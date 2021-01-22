# flake8: noqa

"""The Replit Python module."""

from . import web
from .audio import Audio
from .database import db, Database
from .users import get_profile, User

# Backwards compatibility.
from ._termutils import clear

audio = Audio()
