# flake8: noqa
"""Make apps quickly using Python."""

import os

import flask
from werkzeug.local import LocalProxy

from .app import ReplitApp
from .user import User, UserStore
from .utils import *
from ..database import AsyncDatabase, Database, db

auth = LocalProxy(lambda: flask.request.auth)
signed_in = LocalProxy(lambda: flask.request.signed_in)
request = LocalProxy(lambda: flask.request)
render_template = flask.render_template
redirect = flask.redirect

# Syntax sugar.
App = ReplitApp
