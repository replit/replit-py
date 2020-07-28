"""Utitilities to make development easier."""
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
