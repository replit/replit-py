"""Utitilities to make development easier."""
from typing import Any, Callable
from functools import wraps

import flask

from .html import Page


sign_in_snippet = (
    '<script authed="location.reload()" '
    'src="https://auth.turbio.repl.co/script.js"></script>'
)


def signin(title: str = "Please Sign In") -> Page:
    """Return a sign-in page.

    Args:
        title (str): The title of the sign in page. Defaults to "Please Sign In".

    Returns:
        Page: The sign-in page.
    """
    return Page(title=title, body=sign_in_snippet)


def needs_signin(func: Callable = None, loginhtml: str = sign_in_snippet) -> Callable:
    """A decorator that enforces that the user is signed in before accessing the page.

    Args:
        func (Callable): The function passed in if used as a decorator. Defaults to None.
        loginhtml (str): The HTML to show when the user needs to sign in. Defaults to sign_in_snippet.

    Returns:
        Callable: The new handler.
    """

    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def handler(*args: Any, **kwargs: Any) -> flask.Response:
            if flask.request.signed_in:
                return func(*args, **kwargs)
            else:
                return loginhtml

    if func is not None:  # called with no options @needs_signin
        return decorator(func)
    else:  # called with options, eg @needs_signin(loginhtml='...')
        return decorator
