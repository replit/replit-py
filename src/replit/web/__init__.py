# flake8: noqa
"""Make apps quickly using Python."""

import os

import flask
from werkzeug.local import LocalProxy

from .app import debug, ReplitAuthContext, run
from .user import User, UserStore
from .utils import *
from ..database import AsyncDatabase, Database, db

auth = LocalProxy(lambda: ReplitAuthContext.from_headers(flask.request.headers))
