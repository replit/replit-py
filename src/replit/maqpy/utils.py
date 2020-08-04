"""Utitilities to make development easier."""
from functools import wraps
from typing import Any, Callable, Union

import flask
from werkzeug.local import LocalProxy

from .html import Page


sign_in_snippet = (
    '<script authed="location.reload()" '
    'src="https://auth.turbio.repl.co/script.js"></script>'
)


def sign_in(title: str = "Please Sign In") -> Page:
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
    *param_names: str,
    src: Union[str, dict] = "form",
    onerror: Callable[[str], flask.Response] = None,
) -> Callable:
    """Require paramaters before a handler can be activated.

    Args:
        param_names (str): The paramaters that must be in the request.
        src (Union[str, dict]): The source to get the paramaters from. Can be "form"
            to use flask.request.form (POST requests), "query" for flask.request.query
            (GET requests), or a custom dictionary.
        onerror (Callable): A function to handle when a paramater is missing. It will
            be passed the parameter that is missing. If no function is specified a
            handler that returns a descriptive error and 400 Bad Request status code
            will be used.

    Raises:
        TypeError: No paramaters were provided or an invalid one was provided.

    Returns:
        Callable: The new handler.
    """
    if len(param_names) < 1:
        raise TypeError("You must specify at least one required paramater name")
    # If function is used as a decorator with no arguments, the first argument will be
    # a function, so type check all of the param names to catch mistakes
    if not all(isinstance(p, str) for p in param_names):
        raise TypeError("All paramater names should be strings.")

    def default_onerror(missing_param: str) -> flask.Response:
        return flask.Response(
            f"Parameter {missing_param!r} is required but is missing",
            400,
            mimetype="text/plain",
        )

    onerror = default_onerror if onerror is None else onerror

    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def handler(*args: Any, **ignoredkwargs: Any) -> flask.Response:
            if src == "form":
                params = flask.request.form
            elif src == "query":
                params = flask.request.args
            else:
                params = src
            param_kwargs = {}
            for p in param_names:
                if p not in params:
                    return onerror(p)
                param_kwargs[p] = params[p]
            return func(*args, **param_kwargs)

        return handler

    return decorator


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
        lambda: flask.redirect(
            "https://" + flask.request.headers["host"] + location, code
        )
    )
