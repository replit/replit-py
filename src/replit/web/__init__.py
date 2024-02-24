# flake8: noqa
"""Make apps quickly using Python."""

import os

import flask
from werkzeug.local import LocalProxy

from .app import debug, ReplitAuthContext, run
from .user import User, UserStore
from .utils import *
from .. import database
from ..database import AsyncDatabase, Database

auth = LocalProxy(lambda: ReplitAuthContext.from_headers(flask.request.headers))


# Previous versions of this library would just have side-effects and always set
# up a database unconditionally. That is very undesirable, so instead of doing
# that, we are using this egregious hack to get the database / database URL
# lazily.
def __getattr__(name: str) -> Any:
    if name == "db":
        return database.db
    raise AttributeError(name)
