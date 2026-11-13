# Daily Word Game Platform

A Dawson College team project that brings Wordle and Spelling Bee into one web app. Players can try daily puzzles as guests or sign in to track streaks and review past games.

## Isabela’s contributions

Isabela co-developed the app in a three-person team. She implemented Flask routes for reading and updating game data, including streaks and game history. She created the PostgreSQL tables and managed database connections.

## Stack

Python, Flask, Flask-Login, PostgreSQL, psycopg2, HTML, CSS, and JavaScript.

## Local setup

Use Python with pip and a local PostgreSQL server. Create a fresh database and run the setup script once from the repository root. Set `PGUSER` to a local PostgreSQL role that can create databases.

```bash
export PGHOST=127.0.0.1
export PGUSER=postgres
createdb word_games
psql -X -v ON_ERROR_STOP=1 -d word_games -f db/setup.sql
```

The script creates the tables and enables both games for all seven weekdays. Open the local app to play as a guest or use its registration form to create your own account.

From the repository root, create and activate a virtual environment:

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
```

Set a fresh session key and supply your local database credentials:

```bash
export FLASK_SECRET_KEY="$(python -c 'import secrets; print(secrets.token_hex(32))')"
export FLASK_DBHOST=127.0.0.1
export FLASK_DBPORT=5432
export FLASK_DBNAME=word_games
export FLASK_DBUSER="$PGUSER"
export FLASK_DBPASS='replace-with-your-local-password'
python -m flask --app App run
```

## Demo data

Both games are available to guests immediately after setup. To preview game history, register a local account named `word-games-demo` with a password you choose, then run:

```bash
psql -X -v ON_ERROR_STOP=1 -d word_games -f db/demo.sql
```

Sign in as that user and open **History** to see a completed Wordle from the previous weekday. Both current puzzles remain available to play.

## Project structure

- `App/__init__.py` contains the Flask application, routes, and database access.
- `App/wordle.py` and `App/spellingBee.py` implement the puzzle rules.
- `App/templates/` and `App/static/` contain the UI.
- `db/setup.sql` initializes the PostgreSQL tables and weekly game schedule.
