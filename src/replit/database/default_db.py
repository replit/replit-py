"""A module containing the default database."""
from os import environ
from typing import Optional

from .database import Database

db: Optional[Database]
db_url = environ.get("REPLIT_DB_URL")
if db_url:
    db = Database(db_url)
else:
    # The user will see errors if they try to use the database.
    db = None
