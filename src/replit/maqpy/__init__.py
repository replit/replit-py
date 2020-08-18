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
    authed_ratelimit,
    chain_decorators,
    find,
    local_redirect,
    needs_params,
    needs_sign_in,
    sign_in,
    sign_in_page,
    sign_in_snippet,
)
from ..database import AsyncDatabase, AsyncJSONKey, Database, db, JSONKey

auth = LocalProxy(lambda: flask.request.auth)
signed_in = LocalProxy(lambda: flask.request.signed_in)
request = LocalProxy(lambda: flask.request)
render_template = flask.render_template
redirect = flask.redirect


def user_data(username: str) -> JSONKey:
    """Shorthand for db.jsonkey(username, dict).

    Args:
        username (str): The key to use for the JSONKey.

    Returns:
        JSONKey: An initialized JSONKey.
    """
    return db.jsonkey(username, dict)


current_user_data = LocalProxy(lambda: user_data(flask.request.auth.name))
