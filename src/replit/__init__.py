"""The replit python module."""
import sys
import types

from . import maqpy
from . import termutils
from .audio import Audio
from .database import db


def clear() -> None:
    """Clear the terminal."""
    print("\033[H\033[2J", end="", flush=True)

    
def imported() -> list:
    i = []

    for name, value in globals().items():
        if isinstance(value, types.ModuleType):
            i.append(value.__name__)
    
    return sorted(i)


def importable() -> list:
    return sorted([i.__name__ for i in sys.modules.values() if i])


audio = Audio()

# TODO: DB convience methods like nuke and a CLI to interact with it?
