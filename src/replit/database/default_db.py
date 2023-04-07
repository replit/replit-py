"""A module containing the default database."""
from os import environ
from typing import Optional

from .database import Database

db: Optional[Database]
if os.path.exists("/tmp/replitdb"):
    with open(file_path, 'r') as file:
        db_url = file.read()
else:
    db_url = environ.get("REPLIT_DB_URL")

if db_url:
    db = Database(db_url)
else:
    # The user will see errors if they try to use the database.
    db = None
