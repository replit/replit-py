"""Make apps quickly in python."""
import os

import flask
from werkzeug.local import LocalProxy

from . import html
from .app import App
from .html import Page, Paragraph
from .utils import sign_in_snippet, signin

# TODO: import new db package package name

db = ReplitDb(os.environ["REPLIT_DB_URL"])
auth = LocalProxy(lambda: flask.request.auth)
signed_in = LocalProxy(lambda: flask.request.signed_in)

# TODO: signinwall(exclude=['/a', '/b'])
# TODO: @need_signin
# TODO: Param checking with @needs_params
