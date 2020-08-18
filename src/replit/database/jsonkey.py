# flake8: noqa
from typing import Any, Callable, Dict, Optional, Tuple, Union
import json

JSON_TYPE = Optional[Union[str, int, float, bool, dict, list]]


class AsyncJSONKey:
    """Represents an key in the async database that holds a JSON value.
    db.jsonkey() will initialize an instance for you,
    you don't have to do it manually.
    """

    __slots__ = ("db", "key", "dtype", "get_default", "discard_bad_data", "do_raise")

    def __init__(
        self,
        db: Any,
        key: str,
        dtype: JSON_TYPE,
        get_default: Callable[[], JSON_TYPE] = None,
        discard_bad_data: bool = False,
        do_raise: bool = False,
    ) -> None:
        """Initialize the key.
        Args:
            db (Any): An instance of ReplitDb
            key (str): The key to read
            dtype (JSON_TYPE): The datatype the key should be, can be typing.Any.
            get_default (Callable): A function that returns the default
                value if the key is not set. If it is None (the default) the dtype
                argument is used.
            discard_bad_data (bool): Don't prompt if bad data is read, overwrite it
                with the default. Defaults to False.
            do_raise (bool): Whether to raise exceptions when errors are encountered.
        """
        self.db = db
        self.key = key
        self.dtype = dtype
        self.get_default = get_default
        self.discard_bad_data = discard_bad_data
        self.do_raise = do_raise

    def _default(self) -> JSON_TYPE:
        if self.get_default:
            return self.get_default()
        return self.dtype

    def _is_valid_type(self, data: JSON_TYPE) -> bool:
        return self.dtype is Any or isinstance(data, self.dtype)

    def _type_mismatch_msg(self, data: Any) -> str:
        return (
            f"Type mismatch: Got type {type(data).__name__},"
            f"expected {self.dtype.__name__}"
        )

    async def get(self) -> JSON_TYPE:
        """Get the value of the key.
        If an invalid JSON value is read or the type does not match, it will show a
            prompt asking the user what to do unless discard_bad_data is set.
        Raises:
            KeyError: If do_raise is true and the key does not exist.
            json.JSONDecodeError: If do_raise is true and invalid JSON data is read
                from the key.
        Returns:
            JSON_TYPE: The value read from the database
        """
        try:
            read = await self.db.get(self.key)
        except KeyError:
            if self.do_raise:
                raise
            print(f"Database key {self.key} not set, setting it to default value")
            default = self._default()
            await self.db.set(self.key, default)
            return default

        try:
            data = json.loads(read)
        except json.JSONDecodeError:
            if self.do_raise:
                raise
            return await self._error("Invalid JSON data read", read)

        if not self._is_valid_type(data):
            return await self._error(self._type_mismatch_msg(data), read,)
        return data

    async def _error(self, error: str, read: str) -> JSON_TYPE:
        if self.do_raise:
            raise ValueError(error)

        print(f"Error reading key {self.key!r}: {error}", file=stderr)
        if self.discard_bad_data:
            val = self._default()
            await self.db.set(self.key, json.dumps(val))
            print(f"Wrote default to key {self.key!r}")
            return val
        return await self._should_discard_prompt(error, read)

    async def _should_discard_prompt(self, error: str, read: str) -> bool:
        while True:
            choice = input(
                "d to use default, v to view the invalid data, c to insert custom "
                "value, ^C to exit: "
            )
            if choice.startswith("d"):
                print("Writing default...")
                val = self._default()
                await self.db.set(self.key, val)
                return val
            elif choice.startswith("v"):
                print(f"Data read from key: {read!r}")
            elif choice.startswith("c"):
                toset = input(
                    f"Enter data to write, should be of type {self.dtype.__name__!r}"
                    " (leave blank to return to menu): "
                )
                if not toset:
                    continue
                try:
                    data = json.loads(toset)
                except json.JSONDecodeError:
                    print("Invalid JSON data!")
                else:
                    if not self._is_valid_type(data):
                        print(self._type_mismatch_msg(data))
                        continue

                    await self.db.set(self.key, toset)
                    print("Wrote data to key")
                    return data

    async def set(self, data: JSON_TYPE) -> None:
        """Set the value of the jsonkey.
        Args:
            data (JSON_TYPE): The value to set it to.
        Raises:
            TypeError: The type of the value set does not match the datatype.
        """
        if not self._is_valid_type(data):
            raise TypeError(self._type_mismatch_msg(data))

        await self.db.set(self.key, json.dumps(data))


class JSONKey(AsyncJSONKey):
    """Represents a key in the database that holds a JSON value.

    db.jsonkey() will initialize an instance for you,
    you don't have to do it manually.
    """

    __slots__ = ("db", "key", "dtype", "get_default", "discard_bad_data", "do_raise")

    def __init__(
        self,
        db: Any,
        key: str,
        dtype: JSON_TYPE,
        get_default: Callable = None,
        discard_bad_data: bool = False,
        do_raise: bool = False,
    ) -> None:
        """Initialize the key.

        Args:
            db (Any): An instance of ReplitDb
            key (str): The key to read
            dtype (JSON_TYPE): The datatype the key should be, can be typing.Any.
            get_default (Callable): A function that returns the default
                value if the key is not set. If it is None (the default) the dtype
                argument is used.
            discard_bad_data (bool): Don't prompt if bad data is read, overwrite it
                with the default. Defaults to False.
            do_raise (bool): Whether to raise exceptions when errors are encountered.
        """
        self.db = db
        self.key = key
        self.dtype = dtype
        self.get_default = get_default
        self.discard_bad_data = discard_bad_data
        self.do_raise = do_raise

    def get(self) -> JSON_TYPE:
        """Get the value of the key.

        If an invalid JSON value is read or the type does not match, it will show a
            prompt asking the user what to do unless discard_bad_data is set.

        Returns:
            JSON_TYPE: The value read from the database
        """
        try:
            read = self.db[self.key]
        except KeyError:
            print(f"Database key {self.key} not set, setting it to default value")
            default = self._default()
            self.db[self.key] = default
            return default

        if isinstance(self.db, ReplitDb):
            try:
                data = json.loads(read)
            except json.JSONDecodeError:
                return self._error("Invalid JSON data read", read)
        else:
            data = read

        if not self._is_valid_type(data):
            return self._error(self._type_mismatch_msg(data), read,)
        return data

    def _error(self, error: str, read: str) -> JSON_TYPE:
        print(f"Error reading key {self.key!r}: {error}", file=stderr)
        if self.discard_bad_data:
            val = self._default()
            self.db[self.key] = json.dumps(val)
            print(f"Wrote default to key {self.key!r}")
            return val
        return self._should_discard_prompt(error, read)

    def _should_discard_prompt(self, error: str, read: str) -> bool:
        while True:
            choice = input(
                "d to use default, v to view the invalid data, c to insert custom "
                "value, ^C to exit: "
            )
            if choice.startswith("d"):
                print("Writing default...")
                val = self._default()
                self.db[self.key] = val
                return val
            elif choice.startswith("v"):
                print(f"Data read from key: {read!r}")
            elif choice.startswith("c"):
                toset = input(
                    f"Enter data to write, should be of type {self.dtype.__name__!r}"
                    " (leave blank to return to menu): "
                )
                if not toset:
                    continue
                try:
                    data = json.loads(toset)
                except json.JSONDecodeError:
                    print("Invalid JSON data!")
                else:
                    if not self._is_valid_type(data):
                        print(self._type_mismatch_msg(data))
                        continue

                    self.db[self.key] = toset
                    print("Wrote data to key")
                    return data

    def set(self, data: JSON_TYPE) -> None:
        """Set the value of the jsonkey.

        Args:
            data (JSON_TYPE): The value to set it to.

        Raises:
            TypeError: The type of the value set does not match the datatype.
        """
        if not self._is_valid_type(data):
            raise TypeError(self._type_mismatch_msg(data))
        if isinstance(self.db, ReplitDb):
            data = json.dumps(data)
        self.db[self.key] = data

    def read(self, key: str, default: Any = None) -> Any:
        """Shorthand for self.get().get(name, default) if datatype is dict.

        Args:
            key (str): The name to get.
            default (Any): The default if the key doesn't exist. Defaults to None.

        Returns:
            Any: The value read or the default.
        """
        data = self.get()
        if not isinstance(data, dict):
            raise TypeError
        return data.get(key, default)

    def keys(self, *keys: str) -> Any:
        """Reads multiple keys from the key's value and allows setting.

        Args:
            *keys (str): The keys to read from the data.

        Returns:
            Any: The value accessed from self.get()[k1][k2][kn]
        """
        data = self
        for key in keys[:-1]:
            data = type(self)(db=data, key=key, dtype=Any)
        check = data[keys[-1]]
        if type(check) is dict:
            return type(self)(db=data, key=keys[-1], dtype=dict)
        else:
            return check

    def __getitem__(self, name: str) -> JSON_TYPE:
        """Retrieve a key from the JSONKey's value if it is a dict.

        Args:
            name (str): The name to retrieve.

        Returns:
            JSON_TYPE: The value of the key.
        """
        return self.keys(name)

    def __setitem__(self, name: str, value: JSON_TYPE) -> None:
        """Sets a key inside the JSONKey's value if it is a dict.

        Args:
            name (str): The key to set.
            value (JSON_TYPE): The value to set it to.
        """
        data = self.get()
        if not isinstance(data, dict):
            raise TypeError
        data[name] = value
        self.set(data)

    def append(self, item: JSON_TYPE) -> None:
        """Append to the JSONKey's value if it is a list.

        Args:
            item (JSON_TYPE): The item to append.
        """
        data = self.get()
        if not isinstance(data, list):
            raise TypeError
        self.set(data + [item])

    def __add__(self, item: Any) -> Any:
        """Add to the JSONKey's value and return the result.

        Args:
            item (Any): The item to add.

        Returns:
            Any: The result of adding.
        """
        return self.get() + item

    def __iadd__(self, item: Any) -> Any:
        """Add to the JSONKey's value and set the result.

        Args:
            item (Any): The item to add.

        Returns:
            Any: self
        """
        r = self.get() + item
        self.set(r)
        return self
