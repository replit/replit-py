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

import aiohttp
import requests


def to_primitive(o: Any) -> Any:
    """If object is an observed object, converts to primitve, otherwise returns it.

    Args:
        o (Any): Any object.

    Returns:
        Any: The primitive equivalent if o is an ObservedList or ObservedDict,
            otherwise o.
    """
    if isinstance(o, ObservedList) or isinstance(o, ObservedDict):
        return o.value
    return o


class DBJSONEncoder(json.JSONEncoder):
    """A JSON encoder that uses to_primitive on passed objects."""

    def default(self, o: Any) -> Any:
        """Runs to_primitive on the passed object."""
        return to_primitive(o)


def dumps(val: Any) -> str:
    """JSON encode a value in the smallest way possible.

    Also handles ObservedList and ObservedDict by using a custom encoder.

    Args:
        val (Any): The value to be encoded.

    Returns:
        str: The JSON string.
    """
    return json.dumps(val, separators=(",", ":"), cls=DBJSONEncoder)


_dumps = dumps


class AsyncDatabase:
    """Async interface for Repl.it Database."""

    __slots__ = ("db_url", "sess")

    def __init__(self, db_url: str) -> None:
        """Initialize database. You shouldn't have to do this manually.

        Args:
            db_url (str): Database url to use.
        """
        self.db_url = db_url
        self.sess = aiohttp.ClientSession()

    async def __aenter__(self) -> "AsyncDatabase":
        return self

    async def __aexit__(self, exc_type: Any, exc_value: Any, traceback: Any) -> None:
        self.sess.close()

    async def get(self, key: str) -> str:
        """Return the value for key if key is in the database.

        This method will JSON decode the value. To disable this behavior, use the
        `get_raw` method instead.

        Args:
            key (str): The key to retreive

        Returns:
            str: The the value for key if key is in the database.
        """
        return json.loads(await self.get_raw(key))

    async def get_raw(self, key: str) -> str:
        """Get the value of an item from the database.

        Args:
            key (str): The key to retreive

        Raises:
            KeyError: Key is not set

        Returns:
            str: The value of the key
        """
        async with self.sess.get(
            self.db_url + "/" + urllib.parse.quote(key)
        ) as response:
            if response.status == 404:
                raise KeyError(key)
            response.raise_for_status()
            return await response.text()

    async def set(self, key: str, value: Any) -> None:
        """Set a key in the database to the result of JSON encoding value.

        Args:
            key (str): The key to set
            value (Any): The value to set it to. Must be JSON-serializable.
        """
        await self.set_raw(key, _dumps(value))

    async def set_raw(self, key: str, value: str) -> None:
        """Set a key in the database to value.

        Args:
            key (str): The key to set
            value (str): The value to set it to
        """
        await self.set_bulk_raw({key: value})

    async def set_bulk(self, values: Dict[str, Any]) -> None:
        """Set multiple values in the database, JSON encoding them.

        Args:
            values (Dict[str, Any]): A dictionary of values to put into the dictionary.
                Values must be JSON serializeable.
        """
        await self.set_bulk_raw({k: _dumps(v) for k, v in values.items()})

    async def set_bulk_raw(self, values: Dict[str, str]) -> None:
        """Set multiple values in the database.

        Args:
            values (Dict[str, str]): The key-value pairs to set.
        """
        async with self.sess.post(self.db_url, data=values) as response:
            response.raise_for_status()

    async def delete(self, key: str) -> None:
        """Delete a key from the database.

        Args:
            key (str): The key to delete

        Raises:
            KeyError: Key does not exist
        """
        async with self.sess.delete(
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
        async with self.sess.get(self.db_url, params=params) as response:
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
    """A list that calls a function every time it is mutated.

    Attributes:
        value (List): The underlying list.
    """

    __slots__ = ("_on_mutate_handler", "value")

    def __init__(
        self, on_mutate: Callable[[List], None], value: Optional[List] = None
    ) -> None:
        self._on_mutate_handler = on_mutate
        if value is None:
            self.value = []
        else:
            self.value = value

    def on_mutate(self) -> None:
        """Calls the mutation handler with the underlying list as an argument."""
        self._on_mutate_handler(self.value)

    def __getitem__(self, i: Union[int, slice]) -> Any:
        return self.value[i]

    def __setitem__(self, i: Union[int, slice], val: Any) -> None:
        self.value[i] = val
        self.on_mutate()

    def __delitem__(self, i: Union[int, slice]) -> None:
        del self.value[i]
        self.on_mutate()

    def __len__(self) -> int:
        return len(self.value)

    def __iter__(self) -> Iterator[Any]:
        return iter(self.value)

    def __imul__(self, rhs: Any) -> Any:
        self.value *= rhs
        self.on_mutate()
        return self.value

    def __eq__(self, rhs: Any) -> bool:
        return self.value == rhs

    def insert(self, i: int, elem: Any) -> None:
        """Inserts a value into the underlying list."""
        self.value.insert(i, elem)
        self.on_mutate()

    def set_value(self, value: List) -> None:
        """Sets the value attribute and triggers the mutation function."""
        self.value = value
        self.on_mutate()

    def __repr__(self) -> str:
        return f"{type(self).__name__}(value={self.value!r})"


class ObservedDict(abc.MutableMapping):
    """A list that calls a function every time it is mutated.

    Attributes:
        value (Dict): The underlying dict.
    """

    __slots__ = ("_on_mutate_handler", "value")

    def __init__(
        self, on_mutate: Callable[[Dict], None], value: Optional[Dict] = None
    ) -> None:
        self._on_mutate_handler = on_mutate
        if value is None:
            self.value = {}
        else:
            self.value = value

    def on_mutate(self) -> None:
        """Calls the mutation handler with the underlying dict as an argument."""
        self._on_mutate_handler(self.value)

    def __contains__(self, k: Any) -> bool:
        return k in self.value

    def __getitem__(self, k: Any) -> Any:
        return self.value[k]

    # This should be posititional only but flake8 doesn't like that
    def get(self, key: str, default: Any = None) -> Any:
        """Return the value for key if key is in the dictionary, else default."""
        return self.value.get(
            key, item_to_observed(_get_set_cb(db=self, k=key), default)
        )

    def __setitem__(self, k: Any, v: Any) -> None:
        self.value[k] = v
        self.on_mutate()

    def __delitem__(self, k: Any) -> None:
        del self.value[k]
        self.on_mutate()

    def __iter__(self) -> Iterator[Any]:
        return iter(self.value)

    def __len__(self) -> int:
        return len(self.value)

    def __eq__(self, rhs: Any) -> bool:
        return self.value == rhs

    def __imul__(self, rhs: Any) -> Any:
        self.value *= rhs
        self.on_mutate()
        return self.value

    def set_value(self, value: Dict) -> None:
        """Sets the value attribute and triggers the mutation function."""
        self.value = value
        self.on_mutate()

    def __repr__(self) -> str:
        return f"{type(self).__name__}(value={self.value!r})"


# By putting these outside we save some memory
def _get_on_mutate_cb(d: Any) -> Callable[[Any], None]:
    def cb(_: Any) -> None:
        d.on_mutate()

    return cb


def _get_set_cb(db: Any, k: str) -> Callable[[Any], None]:
    def cb(val: Any) -> None:
        db[k] = val

    return cb


def item_to_observed(on_mutate: Callable[[Any], None], item: Any) -> Any:
    """Takes a JSON value and recursively converts it into an Observed value."""
    if isinstance(item, dict):
        # no-op handler so we don't call on_mutate in the loop below
        observed_dict = ObservedDict((lambda _: None), item)
        cb = _get_on_mutate_cb(observed_dict)

        for k, v in item.items():
            observed_dict[k] = item_to_observed(cb, v)

        observed_dict._on_mutate_handler = on_mutate
        return observed_dict
    elif isinstance(item, list):
        # no-op handler so we don't call on_mutate in the loop below
        observed_list = ObservedList((lambda _: None), item)
        cb = _get_on_mutate_cb(observed_list)

        for i, v in enumerate(item):
            observed_list[i] = item_to_observed(cb, v)

        observed_list._on_mutate_handler = on_mutate
        return observed_list
    else:
        return item


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

        Will replace the mutable JSON types of dict and list with subclasses that
        enable nested setting. These classes will block to request the DB on every
        mutation, which can have performance implications. To disable this, use the
        `get_raw` method instead.

        This method will JSON decode the value. To disable this behavior, use the
        `get_raw` method instead.

        Args:
            key (str): The key to retreive

        Returns:
            Any: The value of the key
        """
        raw_val = self.get_raw(key)
        val = json.loads(raw_val)
        return item_to_observed(_get_set_cb(self, key), val)

    # This should be posititional only but flake8 doesn't like that
    def get(self, key: str, default: Any = None) -> Any:
        """Return the value for key if key is in the database, else default.

        Will replace the mutable JSON types of dict and list with subclasses that
        enable nested setting. These classes will block to request the DB on every
        mutation, which can have performance implications. To disable this, use the
        `get_raw` method instead.

        This method will JSON decode the value. To disable this behavior, use the
        `get_raw` method instead.

        Args:
            key (str): The key to retreive
            default (Any): The default to return if the key is not the database.
                Defaults to None.

        Returns:
            Any: The the value for key if key is in the database, else default.
        """
        return super().get(key, item_to_observed(_get_set_cb(self, key), default))

    def get_raw(self, key: str) -> str:
        """Look up the given key in the database and return the corresponding value.

        Args:
            key (str): The key to look up

        Raises:
            KeyError: The key is not in the database.

        Returns:
            str: The value of the key in the database.
        """
        r = self.sess.get(self.db_url + "/" + urllib.parse.quote(key))
        if r.status_code == 404:
            raise KeyError(key)

        r.raise_for_status()
        return r.text

    def __setitem__(self, key: str, value: Any) -> None:
        """Set a key in the database to the result of JSON encoding value.

        Args:
            key (str): The key to set
            value (Any): The value to set it to. Must be JSON-serializable.
        """
        self.set(key, value)

    def set(self, key: str, value: Any) -> None:
        """Set a key in the database to value, JSON encoding it.

        Args:
            key (str): The key to set
            value (Any): The value to set.
        """
        self.set_raw(key, _dumps(value))

    def set_raw(self, key: str, value: str) -> None:
        """Set a key in the database to value.

        Args:
            key (str): The key to set
            value (str): The value to set.
        """
        self.set_bulk_raw({key: value})

    def set_bulk(self, values: Dict[str, Any]) -> None:
        """Set multiple values in the database, JSON encoding them.

        Args:
            values (Dict[str, Any]): A dictionary of values to put into the dictionary.
                Values must be JSON serializeable.
        """
        self.set_bulk_raw({k: _dumps(v) for k, v in values.items()})

    def set_bulk_raw(self, values: Dict[str, str]) -> None:
        """Set multiple values in the database.

        Args:
            values (Dict[str, str]): The key-value pairs to set.
        """
        r = self.sess.post(self.db_url, data=values)
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

    def dumps(self, val: Any) -> str:
        """JSON encodes a value that can be a special DB object."""
        return _dumps(val)

    def __repr__(self) -> str:
        """A representation of the database.

        Returns:
            A string representation of the database object.
        """
        return f"<{self.__class__.__name__}(db_url={self.db_url!r})>"

    def close(self) -> None:
        """Closes the database client connection."""
        self.sess.close()
