"""A module containing the default database."""
from os import environ, path
from typing import Optional
import threading

from .database import Database

db: Optional[Database] = None

db_url: str = environ.get("REPLIT_DB_URL")


def reload_db() -> None:
    """
    Reloads the database. The database token expires every 20h.
    """
    global db
    global db_url
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
    reload_db()
    threading.Timer(3600, refresh_db).start()


refresh_db()
