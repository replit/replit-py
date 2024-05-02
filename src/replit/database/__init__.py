"""Interface with the Replit Database."""

from typing import Any

from . import default_db
from .database import AsyncDatabase, Database, DBJSONEncoder, dumps, to_primitive
from .server import make_database_proxy_blueprint, start_database_proxy

__all__ = [
    "AsyncDatabase",
    "Database",
    "db",
    "DBJSONEncoder",
    "db_url",
    "dumps",
    "make_database_proxy_blueprint",
    "start_database_proxy",
    "to_primitive",
]


# Previous versions of this library would just have side-effects and always set
# up a database unconditionally. That is very undesirable, so instead of doing
# that, we are using this egregious hack to get the database / database URL
# lazily.
def __getattr__(name: str) -> Any:
    if name == "db":
        return default_db.db
    if name == "db_url":
        return default_db.db_url
    raise AttributeError(name)
