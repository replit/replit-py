"""Async and dict-like interfaces for interacting with Repl.it Database."""

from collections import abc
import json
from typing import (
    AbstractSet,
    Any,
    Callable,
    Dict,
    Iterator,
    List,
    Optional,
    Tuple,
    Union,
)
import urllib
from itertools import chain

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


class ObservedList(list):
    """A list that calls a function every time it is mutated."""

    __slots__ = ("_on_mutate_handler",)

    def __init__(self, on_mutate: Callable[[List], None], *args, **kwargs) -> None:
        self._on_mutate_handler = on_mutate
        super().__init__(*args, **kwargs)

    def on_mutate(self) -> None:
        """Called whenever the list is mutated."""
        self._on_mutate_handler(self)

    def _reinit(self, v: Any) -> Any:
        """Re-initializes the class."""
        # Convert lists into our own class
        if isinstance(v, ObservedList):
            return v
        else:
            return self.__class__(self._on_mutate_handler, v)

    def _try_reinit(self, result) -> Any:
        """Tries to iterate over every element in result, recursing on each item.
        If a type-error is raised, returns result unmodified."""
        try:
            return self._reinit([self._try_reinit(i) for i in result])
        except TypeError:
            return result

    def __getslice__(self, i: Any, j: Any) -> Any:
        return self._reinit(self._on_mutate_handler, super().__getslice__(i, j))

    def __getitem__(self, i: Union[int, slice]) -> Any:
        return self._try_reinit(super().__getitem__(i))

    def __setitem__(self, i: Union[int, slice], val: Any) -> None:
        super().__setitem__(i, val)
        self.on_mutate()

    def __delitem__(self, i: Union[int, slice]) -> None:
        super().__delitem__(i)
        self.on_mutate()

    def __iadd__(self, rhs: Any) -> Any:
        # same as extend
        super().__iadd__(self._try_reinit(rhs))
        self.on_mutate()
        return self

    def __imul__(self, rhs: Any) -> Any:
        super().__imul__(self._try_reinit(rhs))
        self.on_mutate()
        return self

    def append(self, item: Any) -> None:
        super().append(self._try_reinit(item))
        self.on_mutate()

    def clear(self) -> None:
        super().clear()
        self.on_mutate()

    def copy(self) -> Any:
        return self._reinit(self.copy())

    def extend(self, t: Any) -> None:
        # same as __iadd__
        super().extend(self._try_reinit(t))
        self.on_mutate()

    def insert(self, i: Any, x: Any) -> None:
        super().insert(i, self._try_reinit(x))
        self.on_mutate()

    def pop(self, i: Any) -> Any:
        val = super().pop(i)
        self.on_mutate()
        return val

    def remove(self, x: Any) -> None:
        # No need to reinit here because ObservableList([1]) == [1]
        super().remove(x)
        self.on_mutate()

    def reverse(self) -> None:
        super().reverse()
        self.on_mutate()

    def insert(self, i: int, elem: Any) -> None:
        """Inserts a value into the underlying list."""
        self.value.insert(i, self._try_reinit(elem))
        self.on_mutate(self.value)

    def __repr__(self):
        return "{0}({1})".format(type(self).__name__, super().__repr__())


_RaiseKeyError = object()  # singleton for no-default behavior


# Inheriting from dict is far from ideal, but it must be done in order to make the
#  class JSON-serializable. See: https://stackoverflow.com/a/39375731/9196137
class ObservedDict(dict):
    """A dictionary that calls a function every time it is mutated.

    When the method is called, the value may not have actually changed.
    It is the handler's responsible to check this if necessary."""

    __slots__ = ("_on_mutate_handler",)  # no __dict__ - that would be redundant

    def __init__(
        self, on_mutate: Callable[[Dict], None], mapping: Any = (), **kwargs
    ) -> None:
        self._on_mutate_handler = on_mutate
        super().__init__(mapping, **kwargs)

    def on_mutate(self) -> None:
        """Called whenever the dictionary is mutated."""
        self._on_mutate_handler(self)

    def __getitem__(self, k: Any) -> Any:
        return super().__getitem__(k)

    def __setitem__(self, k: Any, v: Any) -> None:
        super().__setitem__(k, v)
        self.on_mutate()

    def __delitem__(self, k: Any) -> None:
        super().__delitem__(k)
        self.on_mutate()

    def get(self, k: Any, default: Any = None) -> None:
        return super().get(k, default)

    def setdefault(self, k: Any, default: Any = None) -> Any:
        val = super().setdefault(k, default)
        self.on_mutate()
        return val

    def pop(self, k, v=_RaiseKeyError):
        if v is _RaiseKeyError:
            val = super().pop(k)
        else:
            val = super().pop(k, v)
        self.on_mutate()
        return val

    def update(self, mapping=(), **kwargs):
        super().update(self._process_args(mapping, **kwargs))
        self.on_mutate()

    def __contains__(self, k):
        return super().__contains__(k)

    def copy(self):  # don't delegate w/ super - dict.copy() -> dict
        return type(self)(self)

    @classmethod
    def fromkeys(cls, keys, v=None):
        return super().fromkeys((k for k in keys), v)

    def __repr__(self):
        return "{0}({1})".format(type(self).__name__, super().__repr__())


# By putting this outside we save some memory
def _get_cb(d: Any) -> Callable[[Any], None]:
    def cb(_: Any) -> None:
        d.on_mutate()

    return cb


def item_to_observed(on_mutate: Callable[[Any], None], item: Any) -> Any:
    """Takes a JSON value and recursively converts it into an Observed value."""

    if isinstance(item, str) or isinstance(item, int) or item is None:
        return item
    elif isinstance(item, dict):
        # no-op handler so we don't call on_mutate in the loop below
        d = ObservedDict((lambda _: None), item)
        cb = _get_cb(d)

        for k, v in item.items():
            d[k] = item_to_observed(cb, v)

        d._on_mutate_handler = on_mutate
        return d
    elif isinstance(item, list):
        # no-op handler so we don't call on_mutate in the loop below
        l = ObservedList((lambda _: None), item)
        cb = _get_cb(l)

        for i, v in enumerate(item):
            l[i] = item_to_observed(cb, v)

        l._on_mutate_handler = on_mutate
        return l
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
