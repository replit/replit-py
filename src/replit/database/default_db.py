"""A module containing the default database."""
import logging
import os
import os.path
import threading
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
    """Deprecated: refresh_db is now located inside the LazyDB singleton instance."""
    pass


class LazyDB:
    """A way to lazily create a database connection."""

    _instance: Optional["LazyDB"] = None

    def __init__(self) -> None:
        self._db: Optional[Database] = None
        self._db_url = get_db_url()
        if self._db_url:
            self._db = Database(self._db_url)
            self.refresh_db()
        else:
            logging.warning(
                "Warning: error initializing database. Replit DB is not configured."
            )

    def refresh_db(self) -> None:
        """Refresh the DB URL every hour."""
        if not self._db:
            return
        self._db_url = get_db_url()
        if self._db_url:
            self._db.update_db_url(self._db_url)
        threading.Timer(3600, self.refresh_db).start()

    @classmethod
    def get_instance(cls) -> "LazyDB":
        """Get the lazy singleton instance."""
        if cls._instance is None:
            cls._instance = LazyDB()
        return cls._instance

    @classmethod
    def get_db(cls) -> Optional[Database]:
        return cls.get_instance()._db

    @classmethod
    def get_db_url(cls) -> Optional[str]:
        return cls.get_instance()._db_url


# Previous versions of this library would just have side-effects and always set
# up a database unconditionally. That is very undesirable, so instead of doing
# that, we are using this egregious hack to get the database / database URL
# lazily.
def __getattr__(name: str) -> Any:
    if name == "db":
        return LazyDB.get_db()
    if name == "db_url":
        return LazyDB.get_db_url()
    raise AttributeError(name)
