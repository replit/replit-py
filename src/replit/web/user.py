"""Utilities for working with user mappings."""
from collections.abc import Mapping, MutableMapping
from typing import Any, Iterator, Optional

from flask import request as real_request

from .app import ReplitRequest
from ..database import Database, db as real_db

db: Database = real_db  # type: ignore
request: ReplitRequest = real_request  # type: ignore


class User(MutableMapping):
    """A user in the database, usually initialized by UserStore."""

    __slots__ = ("username", "prefix", "_value")

    def __init__(self, username: str, prefix: str = "") -> None:
        self.username = username
        self.prefix = prefix

    def db_key(self) -> str:
        """Returns the database key for this user."""
        return self.prefix + self.username

    def set_value(self, value: str) -> None:
        """Sets the raw value of this user in the database.

        See set() and get() for a simpler dict based API.
        Will set the key `prefix + username`.

        Args:
            value (str): The value to set in the database
        """
        db[self.db_key()] = value

    def _ensure_value(self) -> Any:
        try:
            return db[self.db_key()]
        except KeyError:
            db[self.db_key()] = {}
            return db[self.db_key()]

    def set(self, key: str, val: Any) -> None:
        """Sets a key to a value for this user's entry in the database.

        Args:
            key (str): The key to set
            val (Any): The value to set it to
        """
        self[key] = val

    def get(self, key: str, default: Any = None) -> Any:
        """Gets a value from the database if it exists, otherwise returns default.

        Args:
            key (str): The key to retrieve
            default (Any): The value to return if the key does not exist

        Returns:
            Any: The value of the key or default
        """
        # We can't let MutableMapping implement this method because if it does it will
        #  return default directly instead of wrapping it in a special database method
        return self._ensure_value().get(key, default)

    def __getitem__(self, k: str) -> Any:
        return self._ensure_value()[k]

    def __setitem__(self, k: str, v: Any) -> None:
        self._ensure_value()[k] = v

    def __delitem__(self, k: str) -> None:
        del self._ensure_value()[k]

    def __iter__(self) -> Iterator[Any]:
        return iter(self._ensure_value())

    def __len__(self) -> int:
        return sum(1 for _ in self)


class UserStore(Mapping):
    """A mapping of username to keys in the replit database."""

    __slots__ = ("prefix",)

    def __init__(self, prefix: str = "") -> None:
        self.prefix = prefix

    @property
    def current(self) -> Optional[User]:
        """The user currently logged in with repl auth, None if not logged in."""
        if request.is_authenticated:
            return self[request.auth.name]
        return None

    def _strip_prefix(self, k: str) -> str:
        return k[len(self.prefix) :]

    def __getitem__(self, name: str) -> User:
        return User(username=name, prefix=self.prefix)

    def __iter__(self) -> Iterator[str]:
        for k in db.keys():
            if k.startswith(self.prefix):
                yield self._strip_prefix(k)

    def __len__(self) -> int:
        return sum(1 for _ in self)
