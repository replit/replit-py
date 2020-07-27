"""The replit python module."""
from .audio import Audio
from .database import db


def clear() -> None:
    "Clear is used to clear the terminal."
    print("\033[H\033[2J", end="", flush=True)


audio = Audio()
