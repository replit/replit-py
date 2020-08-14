"""The replit python module."""
from . import maqpy
from . import termutils
from .audio import Audio
from .database import db


def clear() -> None:
    """Clear the terminal."""
    print("\033[H\033[2J", end="", flush=True)


audio = Audio()

# TODO: DB convience methods like nuke and a CLI to interact with it?
