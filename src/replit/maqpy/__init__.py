"""Make apps quickly in python."""
import os

import flask
from werkzeug.local import LocalProxy

from . import files
from . import html
from .app import App
from .files import File
from .html import HTMLElement, Link, Page, Paragraph
from .utils import needs_params, needs_signin, sign_in_snippet, signin
from ..database import db

auth = LocalProxy(lambda: flask.request.auth)
signed_in = LocalProxy(lambda: flask.request.signed_in)
request = LocalProxy(lambda: flask.request)
render_template = flask.render_template
redirect = flask.redirect


def local_redirect(location: str, code: int = 302) -> flask.Response:
    """Perform a redirection to a local path without downgrading to HTTP.

    Args:
        location (str): The path to redirect to.
        code (int): The code to use for the redirect. Defaults to 302.

    Returns:
        flask.Response: The redirect response.
    """
    # Use a LocalProxy so that it can be called before the request context is available
    return LocalProxy(
        lambda: redirect("https://" + request.headers["host"] + location, code)
    )
