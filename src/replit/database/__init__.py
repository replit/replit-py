"""Interface with the Replit Database."""
import os
from typing import Optional

from .database import AsyncDatabase, Database, DBJSONEncoder, dumps, to_primitive

__all__ = [
    "AsyncDatabase",
    "Database",
    "DBJSONEncoder",
    "dumps",
    "to_primitive",
    "db",
    "db_url",
]


db: Optional[Database]
db_url = os.environ.get("REPLIT_DB_URL")
if db_url:
    db = Database(db_url)
else:
    # The user will see errors if they try to use the database.
    db = None
