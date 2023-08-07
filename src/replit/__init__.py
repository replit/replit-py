# flake8: noqa

"""The Replit Python module."""

from . import web
from .audio import Audio
from .database import (
    db,
    Database,
    AsyncDatabase,
    make_database_proxy_blueprint,
    start_database_proxy,
)
from .info import ReplInfo

info = ReplInfo()


# Backwards compatibility.
def clear() -> None:
    """Clear the terminal."""
    print("\033[H\033[2J", end="", flush=True)


audio = Audio()
