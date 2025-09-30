"""Database helpers for the Oracle administration interface."""
from __future__ import annotations

from dataclasses import dataclass
from typing import List, Mapping, Optional, Sequence, Tuple

try:  # pragma: no cover - optional dependency
    import oracledb  # type: ignore
except Exception:  # pragma: no cover - handled gracefully at runtime
    oracledb = None  # type: ignore


class OracleClientError(RuntimeError):
    """Raised when an Oracle client operation cannot be completed."""


@dataclass
class QueryResult:
    """A typed container for SQL query results."""

    columns: Sequence[str]
    rows: Sequence[Sequence[object]]

    def as_dicts(self) -> List[Mapping[str, object]]:
        """Return rows as a list of dictionaries for template consumption."""
        return [dict(zip(self.columns, row)) for row in self.rows]


class OracleClient:
    """Minimal Oracle database client used by the administration UI."""

    def __init__(self, dsn: str, user: str, password: str) -> None:
        self._dsn = dsn
        self._user = user
        self._password = password
        if oracledb is None:
            raise OracleClientError(
                "Le module python 'oracledb' est requis mais n'est pas installé. "
                "Installez-le avec 'pip install oracledb'."
            )

    def execute(
        self, sql: str, binds: Optional[Mapping[str, object]] = None
    ) -> QueryResult:
        """Execute a SQL statement and return the rows (if any)."""
        try:
            connection = oracledb.connect(  # type: ignore[call-arg]
                user=self._user,
                password=self._password,
                dsn=self._dsn,
            )
        except Exception as exc:  # pragma: no cover - requires oracle env
            raise OracleClientError(
                "Impossible d'établir une connexion Oracle : {0}".format(exc)
            ) from exc

        try:
            with connection.cursor() as cursor:  # type: ignore[attr-defined]
                cursor.execute(sql, binds or {})
                description = cursor.description or []
                columns = [column[0] for column in description]
                rows = cursor.fetchall() if description else []
                if not description:
                    connection.commit()
                return QueryResult(columns=columns, rows=rows)
        except Exception as exc:  # pragma: no cover - requires oracle env
            connection.rollback()
            raise OracleClientError(
                "Erreur lors de l'exécution de la requête : {0}".format(exc)
            ) from exc
        finally:
            connection.close()


class DummyOracleClient(OracleClient):
    """Fallback client used during local development without Oracle."""

    def __init__(self, dsn: str, user: str, password: str) -> None:
        self._dsn = dsn
        self._user = user
        self._password = password

    def execute(
        self, sql: str, binds: Optional[Mapping[str, object]] = None
    ) -> QueryResult:
        parameters = binds or {}
        rows: List[Tuple[str, str]] = [
            ("SQL", sql),
            ("Paramètres", str(parameters)),
            ("DSN", self._dsn),
            ("Utilisateur", self._user),
        ]
        columns = ["Clé", "Valeur"]
        return QueryResult(columns=columns, rows=rows)


def build_client(
    dsn: str,
    user: str,
    password: str,
    use_dummy: bool = False,
) -> OracleClient:
    """Instantiate either a real or dummy client depending on the environment."""
    if use_dummy:
        return DummyOracleClient(dsn=dsn, user=user, password=password)

    try:
        return OracleClient(dsn=dsn, user=user, password=password)
    except OracleClientError:
        # Fallback to the dummy client to keep the UI accessible when Oracle is not
        # reachable. The original exception is intentionally swallowed so the
        # interface can still démarrer en mode démo.
        return DummyOracleClient(dsn=dsn, user=user, password=password)
