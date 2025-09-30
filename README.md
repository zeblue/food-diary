food-diary
==========

This application integrates an authentication with Github. You first need
 to create an OAuth application on the Github website : https://github.com/settings/applications/new.

 ![Creation OAuth app](https://cloud.githubusercontent.com/assets/667519/25222203/1d9ad858-25b8-11e7-8a8c-7980a53c971f.png)


 ![OAuth app created](https://cloud.githubusercontent.com/assets/667519/25222188/08488aae-25b8-11e7-8f5e-b240b28c46ab.png)

 Once you created the OAuth application, you need to get the `client ID` and
 `client secret` to put those information in the `app/config/parameters.yml` file.

Installation
============

First of all you need to run the `$ composer install`.

 This application requires a MySQL database. You need to configure the following parameters in the app/config/parameters.yml
 file :

     database_host
     database_port
     database_name
     database_user
     database_password
Then run the following commands in your favorite command line tool :

`$ bin/console doctrine:database:create`
`$ bin/console doctrine:schema:create`


Oracle rights management interface (Python)
===========================================

The repository now also contains a lightweight Flask application that provides
an interface to manage the rights and habilitations of the private Oracle
instance **PDTM12135**. The UI exposes common tasks such as creating a nominative
account, granting or revoking roles, and listing existing role assignments.

Prerequisites
-------------

* Python 3.10+
* Oracle client libraries compatible with the [`oracledb`](https://python-oracledb.readthedocs.io/en/latest/user_guide/installation.html) package

Getting started
---------------

1. Create and populate a virtual environment:

   ```bash
   cd oracle_admin_app
   python -m venv .venv
   source .venv/bin/activate
   pip install -r requirements.txt
   ```

2. Create a `.env` file next to `app.py` with the Oracle connection parameters:

   ```dotenv
   FLASK_SECRET_KEY=change-me
   ORACLE_DSN=hostname:port/service
   ORACLE_USER=admin
   ORACLE_PASSWORD=********
   # Set to "true" to use the built-in simulator without an Oracle connection
   ORACLE_DUMMY=true
   ```

3. Start the development server:

   ```bash
   flask --app oracle_admin_app.app --debug run
   ```

4. Open http://127.0.0.1:5000 to access the interface and trigger SQL operations.

When `ORACLE_DUMMY=true` the application will not attempt to connect to Oracle
and instead shows a preview of the generated SQL statement together with the
submitted parameters. Disable the flag in order to interact with the real
PDTM12135 database.
