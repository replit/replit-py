"""A module containing the default database."""
from os import environ, path
from typing import Optional
import threading

from .database import Database

db: Optional[Database]


def reload_db() -> None:
    """
    Reloads the database. The database token expires every 20h.
    """
    global db
    if path.exists("/tmp/replitdb"):
        with open("/tmp/replitdb", 'r') as file:
            db_url = file.read()
    else:
        db_url = environ.get("REPLIT_DB_URL")

    if db_url:
        db = Database(db_url)
    else:
        # The user will see errors if they try to use the database.
        db = None


def refresh_db() -> None:
    """Refresh the DB URL every hour"""
    threading.Timer(3600, reload_db).start()


refresh_db()