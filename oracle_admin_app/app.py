"""Flask application exposing Oracle rights management helpers."""
from __future__ import annotations

import os
from dataclasses import dataclass, field
from typing import Dict, List, Mapping

from dotenv import load_dotenv
from flask import Flask, flash, render_template, request

from .db import OracleClientError, QueryResult, build_client

load_dotenv()


def create_app() -> Flask:
    app = Flask(__name__)
    app.secret_key = os.environ.get("FLASK_SECRET_KEY", "change-me")

    @dataclass
    class Operation:
        name: str
        label: str
        sql: str
        parameters: List[str] = field(default_factory=list)
        description: str = ""

    OPERATIONS: Dict[str, Operation] = {
        "create_account": Operation(
            name="create_account",
            label="Créer un compte nominatif",
            description="Crée un compte et définit le mot de passe initial.",
            sql="""
                CREATE USER {username} IDENTIFIED BY "{password}"
                DEFAULT TABLESPACE USERS
                TEMPORARY TABLESPACE TEMP
            """,
            parameters=["username", "password"],
        ),
        "grant_role": Operation(
            name="grant_role",
            label="Attribuer un rôle",
            description="Attribue un rôle métier à un utilisateur existant.",
            sql="GRANT {role} TO {username}",
            parameters=["username", "role"],
        ),
        "revoke_role": Operation(
            name="revoke_role",
            label="Retirer un rôle",
            description="Retire un rôle métier attribué à un utilisateur.",
            sql="REVOKE {role} FROM {username}",
            parameters=["username", "role"],
        ),
        "list_roles": Operation(
            name="list_roles",
            label="Lister les rôles d'un utilisateur",
            description="Affiche les rôles actuellement attribués.",
            sql=(
                "SELECT GRANTEE, GRANTED_ROLE, ADMIN_OPTION, DEFAULT_ROLE "
                "FROM DBA_ROLE_PRIVS WHERE GRANTEE = :username"
            ),
            parameters=["username"],
        ),
    }

    def _build_sql(operation: Operation, form_data: Mapping[str, str]) -> str:
        if ":" in operation.sql:
            # Bind variables are already in place, we simply return the SQL as is.
            return operation.sql
        prepared = operation.sql
        for parameter in operation.parameters:
            value = form_data.get(parameter, "").strip()
            prepared = prepared.replace("{" + parameter + "}", value)
        return prepared

    def _build_binds(operation: Operation, form_data: Mapping[str, str]) -> Mapping[str, str]:
        if ":" not in operation.sql:
            return {}
        return {parameter: form_data.get(parameter, "").strip() for parameter in operation.parameters}

    @app.route("/", methods=["GET", "POST"])
    def index():
        selected = request.form.get("operation", "grant_role")
        operation = OPERATIONS.get(selected) or OPERATIONS["grant_role"]
        result: QueryResult | None = None
        preview_sql: str | None = None

        if request.method == "POST":
            form_data = request.form
            sql = _build_sql(operation, form_data)
            binds = _build_binds(operation, form_data)
            preview_sql = sql if not binds else f"{sql}\nBIND VARIABLES: {binds}"
            client = build_client(
                dsn=os.environ.get("ORACLE_DSN", "PDTM12135"),
                user=os.environ.get("ORACLE_USER", "admin"),
                password=os.environ.get("ORACLE_PASSWORD", "password"),
                use_dummy=os.environ.get("ORACLE_DUMMY", "false").lower() == "true",
            )
            try:
                result = client.execute(sql=sql, binds=binds)
                flash("Requête exécutée avec succès", "success")
            except OracleClientError as exc:
                flash(str(exc), "error")
        else:
            preview_sql = _build_sql(operation, request.form)

        return render_template(
            "index.html",
            operations=OPERATIONS,
            selected_operation=operation,
            result=result,
            preview_sql=preview_sql,
        )

    return app


app = create_app()


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
