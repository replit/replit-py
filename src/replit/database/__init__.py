"""Interface with the Replit Database."""
import os
from typing import Optional

from .database import AsyncDatabase, Database

__all__ = ["AsyncDatabase", "Database", "AsyncJSONKey", "JSONKey"]


db: Optional[Database]
db_url = os.environ.get("REPLIT_DB_URL")
if db_url:
    db = Database(db_url)
else:
    # The user will see errors if they try to use the database.
    db = None
