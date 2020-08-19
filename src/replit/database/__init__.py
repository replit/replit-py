"""Interface with the Replit Database."""
import os
from sys import stderr
from typing import Optional

from .database import AsyncDatabase, Database
from .jsonkey import AsyncJSONKey, JSONKey

__all__ = ["AsyncDatabase", "Database", "AsyncJSONKey", "JSONKey"]


db: Optional[Database]
db_url = os.environ.get("REPLIT_DB_URL")
if db_url:
    db = Database(db_url)
else:
    print(
        "Warning: REPLIT_DB_URL does not exist, are we running on repl.it? "
        "Database will not function.",
        file=stderr,
    )
    db = None
