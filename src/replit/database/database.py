"""Async and dict-like interfaces for interacting with Repl.it Database."""

from collections import abc
import json
from typing import AbstractSet, Any, Callable, Dict, Iterator, List, Tuple
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

        Raises:
            KeyError: Key does not exist
        """
        async with aiohttp.ClientSession() as session:
            async with session.delete(
                self.db_url + "/" + urllib.parse.quote(key)
            ) as response:
                if response.status == 404:
                    raise KeyError(key)
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


class ObservedList(abc.MutableSequence):
    """A list that calls a function every time it is mutated."""

    __slots__ = ("on_mutate", "value")

    def __init__(self, on_mutate: Callable[[List], None], value: List = []) -> None:
        self.on_mutate = on_mutate
        self.value = value

    def __getitem__(self, i: int) -> Any:
        return self.value[i]

    def __setitem__(self, i: int, val: Any) -> None:
        self.value[i] = val
        self.on_mutate(self.value)

    def __delitem__(self, i: int) -> None:
        del self.value[i]
        self.on_mutate(self.value)

    def __len__(self) -> int:
        return len(self.value)

    def __iter__(self) -> Iterator[Any]:
        return iter(self.value)

    def insert(self, i: int, elem: Any) -> None:
        """Inserts a value into the underlying list."""
        self.value.insert(i, elem)
        self.on_mutate(self.value)

    def set_value(self, value: List) -> None:
        """Sets the value attribute and triggers the mutation function."""
        self.value = value
        self.on_mutate(self.value)

    def __repr__(self) -> str:
        return f"{type(self).__name__}(value={self.value!r})"


class ObservedDict(abc.MutableMapping):
    """A list that calls a function every time it is mutated."""

    __slots__ = ("on_mutate", "value")

    def __init__(self, on_mutate: Callable[[List], None], value: Dict = {}) -> None:
        self.on_mutate = on_mutate
        self.value = value

    def __contains__(self, k: Any) -> bool:
        return k in self.value

    def __getitem__(self, k: Any) -> Any:
        return self.value[k]

    def __setitem__(self, k: Any, v: Any) -> None:
        self.value[k] = v
        self.on_mutate(self.value)

    def __delitem__(self, k: Any) -> None:
        del self.value[k]
        self.on_mutate(self.value)

    def __iter__(self) -> Iterator[Any]:
        return iter(self.value)

    def __len__(self) -> int:
        return len(self.value)

    def set_value(self, value: List) -> None:
        """Sets the value attribute and triggers the mutation function."""
        self.value = value
        self.on_mutate(self.value)

    def __repr__(self) -> str:
        return f"{type(self).__name__}(value={self.value!r})"


def item_to_observed(on_mutate: Callable[[Any], None], item: Any) -> Any:
    """Takes a JSON value and recursively converts it into an Observed value."""
    # Bind on_mutate to the item it was called on.
    # If this is a recursive call, item will be ignored (passed into the _ param)
    cb = lambda _: on_mutate(item)

    if isinstance(item, str) or isinstance(item, int) or item is None:
        return item
    elif isinstance(item, dict):
        for k, v in item.items():
            item[k] = item_to_observed(cb, v)
        return ObservedDict(cb, item)
    elif isinstance(item, list):
        for i, v in enumerate(item):
            item[i] = item_to_observed(cb, v)
        return ObservedList(cb, item)
    else:
        raise TypeError(f"Unexpected type {type(item).__name__!r}")


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
        r = self.sess.get(self.db_url + "/" + urllib.parse.quote(key))
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
        r = self.sess.delete(self.db_url + "/" + urllib.parse.quote(key))
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
        r = self.sess.get(f"{self.db_url}", params={"prefix": prefix, "encode": "true"})
        r.raise_for_status()

        if not r.text:
            return tuple()
        else:
            return tuple(urllib.parse.unquote(k) for k in r.text.split("\n"))

    def keys(self) -> AbstractSet[str]:
        """Returns all of the keys in the database.

        Returns:
            List[str]: The keys.
        """
        # Rationale for this method:
        # This is implemented for free from our superclass using iter, but when you
        #  db.keys() in the console, you should see the keys immediately. Without this,
        #  it will just print an ugly repr that doesn't show the data within.
        # By implementing this method we get pretty output in the console when you
        #  type db.keys() in an interactive prompt.

        # TODO: Return a set from prefix since keys are guaranteed unique
        return set(self.prefix(""))

    def __repr__(self) -> str:
        """A representation of the database.

        Returns:
            A string representation of the database object.
        """
        return f"<{self.__class__.__name__}(db_url={self.db_url!r})>"

    def close(self) -> None:
        """Closes the database client connection."""
        self.sess.close()
