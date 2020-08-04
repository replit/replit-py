"""Make apps quickly in python."""
import os

import flask
from werkzeug.local import LocalProxy

from . import files
from . import html
from .app import App
from .files import File
from .html import HTMLElement, Link, Page, Paragraph
from .utils import (
    needs_params,
    needs_sign_in,
    sign_in_snippet,
    sign_in_page,
    sign_in,
    local_redirect,
    authed_ratelimit,
)
from ..database import db

auth = LocalProxy(lambda: flask.request.auth)
signed_in = LocalProxy(lambda: flask.request.signed_in)
request = LocalProxy(lambda: flask.request)
render_template = flask.render_template
redirect = flask.redirect
