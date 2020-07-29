"""Utitilities to make development easier."""
from functools import wraps
from types import FunctionType
from typing import Any, Callable, Tuple

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


def needs_signin(func: Callable = None, login_html: str = sign_in_snippet) -> Callable:
    """A decorator that enforces that the user is signed in before accessing the page.

    Args:
        func (Callable): The function passed in if used as a decorator. Defaults to
            None.
        login_html (str): The HTML to show when the user needs to sign in. Defaults to
            sign_in_snippet.

    Returns:
        Callable: The new handler.
    """

    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def handler(*args: Any, **kwargs: Any) -> flask.Response:
            if flask.request.signed_in:
                return func(*args, **kwargs)
            else:
                return login_html

        return handler

    if func is not None:  # called with no options @needs_signin
        return decorator(func)
    else:  # called with options, eg @needs_signin(login_html='...')
        return decorator


def needs_params(
    *param_names: str, onerror: Callable[[Tuple[str]], flask.Response] = None
) -> Callable:
    """Require paramaters before a handler can be activated.

    Args:
        param_names (str): The paramaters that must be in the request.
        onerror (Callable): A function to handle when a paramater is missing. It will
            be passed a tuple of all of the missing paramaters. If no function is
            specified a handler that returns a descriptive error and 400 Bad Request
            status code will be used.

    Raises:
        TypeError: No paramaters were provided or an invalid one was provided.
        NotImplementedError: If the handler is called.

    Returns:
        Callable: The new handler.
    """
    if len(param_names) < 1:
        raise TypeError("You must specify at least one required paramater name")
    # If function is used as a decorator with no arguments, the first argument will be
    # a function, so type check all of the param names to catch mistakes
    if not all(isinstance(p, str) for p in param_names):
        raise TypeError("All paramater names should be strings.")

    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def handler(*args: Any, **kwargs: Any) -> flask.Response:
            raise NotImplementedError()

        return handler

    return decorator
