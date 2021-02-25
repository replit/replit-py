# flake8: noqa

"""The Replit Python module."""

from . import web
from .audio import Audio
from .database import db, Database

# Backwards compatibility.
from ._termutils import clear

audio = Audio()
