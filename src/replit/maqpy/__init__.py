"""Make apps quickly in python."""
import os

import flask
from werkzeug.local import LocalProxy

from . import html
from .app import App
from .html import HTMLElement, Paragraph, Link, Page
from .utils import sign_in_snippet, signin
from ..database import db

auth = LocalProxy(lambda: flask.request.auth)
signed_in = LocalProxy(lambda: flask.request.signed_in)

# TODO: signinwall(exclude=['/a', '/b'])
# TODO: @need_signin
# TODO: Param checking with @needs_params
