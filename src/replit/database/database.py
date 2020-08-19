"""Async and dict-like interfaces for interacting with Repl.it Database."""
from collections import abc
import json
from typing import Any, Dict, Iterator, Tuple
import urllib

import aiohttp
import requests


class AsyncDatabase:
    """Async interface for Repl.it Database."""

    __slots__ = ("db_url", "sess")

    def __init__(self, db_url: str) -> None:
        """Initialize database. You shouldn't have to do this manually.

        Args:
            db_url (str): Database url to use.
        """
        self.db_url = db_url

    async def get(self, key: str) -> str:
        """Get the value of an item from the database.

        Args:
            key (str): The key to retreive

        Raises:
            KeyError: Key is not set

        Returns:
            str: The value of the key
        """
        async with aiohttp.ClientSession() as session:
            async with session.get(
                self.db_url + "/" + urllib.parse.quote(key)
            ) as response:
                if response.status == 404:
                    raise KeyError(key)
                response.raise_for_status()
                return await response.text()

    async def set(self, key: str, value: str) -> None:
        """Set a key in the database to value.

        Args:
            key (str): The key to set
            value (str): The value to set it to
        """
        async with aiohttp.ClientSession() as session:
            async with session.post(self.db_url, data={key: value}) as response:
                response.raise_for_status()

    async def delete(self, key: str) -> None:
        """Delete a key from the database.

        Args:
            key (str): The key to delete
        """
        async with aiohttp.ClientSession() as session:
            async with session.delete(
                self.db_url + "/" + urllib.parse.quote(key)
            ) as response:
                response.raise_for_status()

    async def list(self, prefix: str) -> Tuple[str, ...]:
        """List keys in the database which start with prefix.

        Args:
            prefix (str): The prefix keys must start with, blank not not check.

        Returns:
            Tuple[str]: The keys found.
        """
        params = {"prefix": prefix, "encode": "true"}
        async with aiohttp.ClientSession() as session:
            async with session.get(self.db_url, params=params) as response:
                response.raise_for_status()
                text = await response.text()
                if not text:
                    return tuple()
                else:
                    return tuple(urllib.parse.unquote(k) for k in text.split("\n"))

    async def to_dict(self, prefix: str = "") -> Dict[str, str]:
        """Dump all data in the database into a dictionary.

        Args:
            prefix (str): The prefix the keys must start with,
                blank means anything. Defaults to "".

        Returns:
            Dict[str, str]: All keys in the database.
        """
        ret = {}
        keys = await self.list(prefix=prefix)
        for i in keys:
            ret[i] = await self.get(i)
        return ret

    async def keys(self) -> Tuple[str, ...]:
        """Get all keys in the database.

        Returns:
            Tuple[str]: The keys in the database.
        """
        return await self.list("")

    async def values(self) -> Tuple[str, ...]:
        """Get every value in the database.

        Returns:
            Tuple[str]: The values in the database.
        """
        data = await self.to_dict()
        return tuple(data.values())

    async def items(self) -> Tuple[Tuple[str, str], ...]:
        """Convert the database to a dict and return the dict's items method.

        Returns:
            Tuple[Tuple[str]]: The items
        """
        return tuple((await self.to_dict()).items())

    def __repr__(self) -> str:
        """A representation of the database.

        Returns:
            A string representation of the database object.
        """
        return f"<{self.__class__.__name__}(db_url={self.db_url!r})>"


class Database(abc.MutableMapping):
    """Dictionary-like interface for Repl.it Database.

    This interface will coerce all values everything to and from JSON. If you
    don't want this, use AsyncDatabase instead.
    """

    __slots__ = ("db_url", "sess")

    def __init__(self, db_url: str) -> None:
        """Initialize database. You shouldn't have to do this manually.

        Args:
            db_url (str): Database url to use.
        """
        self.db_url = db_url
        self.sess = requests.Session()

    def __getitem__(self, key: str) -> Any:
        """Get the value of an item from the database.

        Args:
            key (str): The key to retreive

        Raises:
            KeyError: Key is not set

        Returns:
            Any: The value of the key
        """
        r = self.sess.get(f"{self.db_url}/{key}")
        if r.status_code == 404:
            raise KeyError(key)

        r.raise_for_status()
        return json.loads(r.text)

    def __setitem__(self, key: str, value: Any) -> None:
        """Set a key in the database to value.

        Args:
            key (str): The key to set
            value (Any): The value to set it to. Must be JSON-serializable.
        """
        j = json.dumps(value, separators=(",", ":"))
        r = self.sess.post(self.db_url, data={key: j})
        r.raise_for_status()

    def __delitem__(self, key: str) -> None:
        """Delete a key from the database.

        Args:
            key (str): The key to delete

        Raises:
            KeyError: Key is not set
        """
        r = self.sess.delete(f"{self.db_url}/{key}")
        if r.status_code == 404:
            raise KeyError(key)

        r.raise_for_status()

    def __iter__(self) -> Iterator[str]:
        """Return an iterator for the database."""
        return iter(self.prefix(""))

    def __len__(self) -> int:
        """The number of keys in the database."""
        return len(self.prefix(""))

    def prefix(self, prefix: str) -> Tuple[str, ...]:
        """Return all of the keys in the database that begin with the prefix.

        Args:
            prefix (str): The prefix the keys must start with,
                blank means anything.

        Returns:
            Tuple[str]: The keys found.
        """
        r = requests.get(f"{self.db_url}", params={"prefix": prefix, "encode": "true"})
        r.raise_for_status()

        if not r.text:
            return tuple()
        else:
            return tuple(urllib.parse.unquote(k) for k in r.text.split("\n"))

    def __repr__(self) -> str:
        """A representation of the database.

        Returns:
            A string representation of the database object.
        """
        return f"<{self.__class__.__name__}(db_url={self.db_url!r})>"
