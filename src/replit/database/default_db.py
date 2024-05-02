"""A module containing the default database."""

import os
import os.path
from typing import Any, Optional

from .database import Database


def get_db_url() -> Optional[str]:
    """Fetches the most up-to-date db url from the Repl environment."""
    # todo look into the security warning ignored below
    tmpdir = "/tmp/replitdb"  # noqa: S108
    if os.path.exists(tmpdir):
        with open(tmpdir, "r") as file:
            return file.read()

    return os.environ.get("REPLIT_DB_URL")


def refresh_db() -> None:
    """Deprecated: refresh_db is now the responsibility of the Database instance."""
    pass


def _unbind() -> None:
    global _db
    _db = None


def _get_db() -> Optional[Database]:
    global _db
    if _db is not None:
        return _db

    db_url = get_db_url()

    if db_url:
        _db = Database(db_url, get_db_url=get_db_url, unbind=_unbind)
    else:
        # The user will see errors if they try to use the database.
        print("Warning: error initializing database. Replit DB is not configured.")
        _db = None
    return _db


_db: Optional[Database] = None


# Previous versions of this library would just have side-effects and always set
# up a database unconditionally. That is very undesirable, so instead of doing
# that, we are using this egregious hack to get the database / database URL
# lazily.
def __getattr__(name: str) -> Any:
    if name == "db":
        return _get_db()
    if name == "db_url":
        return get_db_url()
    raise AttributeError(name)
