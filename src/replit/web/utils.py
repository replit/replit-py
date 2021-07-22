"""Utilities to make development easier."""

from functools import wraps
import time
from typing import Any, Callable, Iterable, Optional, Union

import flask
from werkzeug.local import LocalProxy

from .app import ReplitAuthContext

authentication_snippet = (
    '<script authed="location.reload()" '
    'src="https://auth.turbio.repl.co/script.js"></script>'
)


def whoami() -> flask.Request:
    """Returns the username of the authenticated Replit user, else None."""
    return flask.request.headers.get("X-Replit-User-Name")


def sign_in(title: str = "Please Sign In") -> str:
    """Return a sign-in page.

    Args:
        title (str): The title of the sign in page. Defaults to "Please Sign In".

    Returns:
        str: The sign-in page HTML.
    """
    return (
        f"<!DOCTYPE html><html><head><title>{title}</title></head>"
        f"<body>{authentication_snippet}</body></html>"
    )


sign_in_page = sign_in()


def authenticated(func: Callable = None, login_res: str = sign_in_page) -> Callable:
    """A decorator that enforces that the user is signed in before accessing the page.

    Args:
        func (Callable): The function passed in if used as a decorator. Defaults to
            None.
        login_res (str): The HTML to show when the user needs to sign in. Defaults to
            sign_in_snippet.

    Returns:
        Callable: The new handler.
    """

    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def handler(*args: Any, **kwargs: Any) -> flask.Response:
            if ReplitAuthContext.from_headers(flask.request.headers).is_authed:
                return func(*args, **kwargs)
            else:
                return login_res

        return handler

    if func is not None:  # called with no options @needs_signin
        return decorator(func)
    else:  # called with options, eg @needs_signin(login_html='...')
        return decorator


needs_sign_in = authenticated


def authenticated_template(template: str, **context: Any) -> Callable:
    """A decorator that renders a template if the user is not signed in.

    Args:
        template (str): The template filename to render.
        **context (Any): The context to pass to the template.

    Returns:
        Callable: A decorator to apply to your route.
    """

    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def handler(*args: Any, **kwargs: Any) -> flask.Response:
            if ReplitAuthContext.from_headers(flask.request.headers).is_authed:
                return func(*args, **kwargs)
            else:
                return flask.render_template(template, **context)

        return handler

    return decorator


def params(
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


def per_user_ratelimit(
    max_requests: int,
    period: float,
    login_res: str = sign_in_page,
    get_ratelimited_res: Callable[[float], str] = (
        lambda left: f"Too many requests, wait {left} sec"
    ),
) -> Callable[[Callable], flask.Response]:
    """Require sign in and limit the amount of requests each signed in user can perform.

    This decorator also calls needs_signin for you and passes the login_res kwarg
        directly to it.

    Args:
        max_requests (int): The maximum amount of requests allowed in the period.
        period (float): The length of the period.
        login_res (str): The response to be shown if the user is not signed in, passed
            to needs_sign_in.
        get_ratelimited_res (Callable[[float], str]): A callable which is passed the
            amount of time remaining before the user can request again and returns the
            response that should be sent to the user.

    Returns:
        Callable[[Callable], flask.Response]: A function which decorates the handler.
    """
    last_reset = time.time()
    num_requests = {}

    def decorator(func: Callable) -> flask.Response:
        # Checks for signin first, before checking ratelimit
        @authenticated(login_res=login_res)
        @wraps(func)
        def handler(*args: Any, **kwargs: Any) -> flask.Response:
            nonlocal last_reset
            nonlocal num_requests

            name = ReplitAuthContext.from_headers(flask.request.headers).name
            now = time.time()

            if now - last_reset >= period:
                last_reset = now
                num_requests = {}

            times_requested = num_requests.get(name, 0)
            if times_requested >= max_requests:
                res = get_ratelimited_res(period - (now - last_reset))
                # Make a reponse object so that status can be set
                if not isinstance(res, flask.Response):
                    res = flask.make_response(res)
                res.status = "429"
                return res

            num_requests[name] = times_requested + 1
            return func(*args, **kwargs)

        return handler

    return decorator


def find(
    data: Iterable, cond: Callable[[Any], bool], allow_multiple: bool = False
) -> Optional[Any]:
    """Find an item in an iterable.

    Args:
        data (Iterable): The iterable to search through.
        cond (Callable[[Any], bool]): The function to call for each item to check if it
            is a match.
        allow_multiple (bool): If multiple result are found, return the first one if
            allow_multiple is True, otherwise return None.

    Returns:
        Optional[Any]: The item if exactly one match was found, otherwise None.
    """
    matches = [item for item in data if cond(item)]
    if len(matches) > 1:
        return matches[0] if allow_multiple else None
    return matches[0] if len(matches) == 1 else None


# Syntax sugar.
sign_in_snippet = authentication_snippet
login_snippet = authentication_snippet
