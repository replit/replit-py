"""A module containing the default database."""
from os import environ, path
import threading
from typing import Optional


from .database import Database


def get_db_url() -> str:
    """Fetches the most up-to-date db url from the Repl environment."""
    # todo look into the security warning ignored below
    tmpdir = "/tmp/replitdb"  # noqa: S108
    if path.exists(tmpdir):
        with open(tmpdir, "r") as file:
            db_url = file.read()
    else:
        db_url = environ.get("REPLIT_DB_URL")

    return db_url


def refresh_db() -> None:
    """Refresh the DB URL every hour."""
    global db
    db_url = get_db_url()
    db.update_db_url(db_url)
    threading.Timer(3600, refresh_db).start()


db: Optional[Database]
db_url = get_db_url()
if db_url:
    db = Database(db_url)
else:
    # The user will see errors if they try to use the database.
    print("Warning: error initializing database. Replit DB is not configured.")
    db = None

if db:
    refresh_db()
