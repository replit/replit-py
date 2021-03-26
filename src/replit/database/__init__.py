"""Interface with the Replit Database."""
import os
from typing import Optional

from .database import AsyncDatabase, Database, DBJSONEncoder, dumps, to_primitive
from .default_db import db_url, db
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
