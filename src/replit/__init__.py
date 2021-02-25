# flake8: noqa

"""The Replit Python module."""

from . import web
from .audio import Audio
from .database import db, Database

# Backwards compatibility.
def clear() -> None:
    """Clear the terminal."""
    print("\033[H\033[2J", end="", flush=True)


audio = Audio()
