"""Tests for replit.database."""

import os
import unittest

import requests
from replit.database import AsyncDatabase, AsyncJSONKey, Database


class TestAsyncDatabase(unittest.IsolatedAsyncioTestCase):
    """Tests for replit.database.AsyncDatabase."""

    async def asyncSetUp(self) -> None:
        """Grab a JWT for all the tests to share."""
        password = os.environ["PASSWORD"]
        req = requests.get(
            "https://database-test-jwt.kochman.repl.co", auth=("test", password)
        )
        url = req.text
        self.db = AsyncDatabase(url)

        # nuke whatever is already here
        for k in await self.db.keys():
            await self.db.delete(k)

    async def asyncTearDown(self) -> None:
        """Nuke whatever the test added."""
        for k in await self.db.keys():
            await self.db.delete(k)

    async def test_get_set_delete(self) -> None:
        """Test that we can get, set, and delete a key."""
        await self.db.set("test-key", "value")

        val = await self.db.get("test-key")
        self.assertEqual(val, "value")

        await self.db.delete("test-key")
        with self.assertRaises(KeyError):
            await self.db.get("test-key")

    async def test_get_set_delete_newline(self) -> None:
        """Test that we can get, set, and delete a key with newline."""
        key = "test-key-with\nnewline"
        await self.db.set(key, "value")

        val = await self.db.get(key)
        self.assertEqual(val, "value")

        await self.db.delete(key)
        with self.assertRaises(KeyError):
            await self.db.get(key)

    async def test_list_keys(self) -> None:
        """Test that we can list keys."""
        key = "test-list-keys-with\nnewline"
        await self.db.set(key, "value")

        val = await self.db.get(key)
        self.assertEqual(val, "value")

        keys = await self.db.list(key)
        self.assertEqual(keys, (key,))

        keys = await self.db.keys()
        self.assertEqual(keys, (key,))

        # just to make sure...
        self.assertEqual(await self.db.keys(), await self.db.list(""))

        await self.db.delete(key)
        with self.assertRaises(KeyError):
            await self.db.get(key)

    async def test_list_values(self) -> None:
        """Test that we can get all values."""
        key = "test-list-values"
        await self.db.set(key + "1", "value1")
        await self.db.set(key + "2", "value2")

        vals = await self.db.values()
        self.assertTupleEqual(vals, ("value1", "value2"))

    async def test_dict(self) -> None:
        """Test that we can get a dict."""
        await self.db.set("key1", "value")
        await self.db.set("key2", "value")
        d = await self.db.to_dict()
        self.assertDictEqual(d, {"key1": "value", "key2": "value"})

    async def test_jsonkey(self) -> None:
        """Test replit.database.AsyncJSONKey."""
        key = "test-jsonkey"

        jk = AsyncJSONKey(db=self.db, key=key, dtype=str, do_raise=True)
        with self.assertRaises(KeyError):
            await jk.get()
        await jk.set("value")
        val = await jk.get()
        self.assertEqual(val, "value")

    async def test_jsonkey_default(self) -> None:
        """Test replit.database.AsyncJSONKey with a default callable."""
        key = "test-jsonkey"

        jk = AsyncJSONKey(db=self.db, key=key, dtype=str, get_default=lambda: "value")
        val = await jk.get()
        self.assertEqual(val, "value")


class TestDatabase(unittest.TestCase):
    """Tests for replit.database.Database."""

    def setUp(self) -> None:
        """Grab a JWT for all the tests to share."""
        password = os.environ["PASSWORD"]
        req = requests.get(
            "https://database-test-jwt.kochman.repl.co", auth=("test", password)
        )
        url = req.text
        self.db = Database(url)

        # nuke whatever is already here
        for k in self.db.keys():
            del self.db[k]

    def tearDown(self) -> None:
        """Nuke whatever the test added."""
        for k in self.db.keys():
            del self.db[k]

    def test_get_set_delete(self) -> None:
        """Test get, set, and delete."""
        with self.assertRaises(KeyError):
            self.db["key"]

        self.db["key"] = "value"
        val = self.db["key"]
        self.assertEqual(val, "value")

        del self.db["key"]
        with self.assertRaises(KeyError):
            val = self.db["key"]

    def test_list_keys(self) -> None:
        """Test that we can list keys."""
        key = "test-list-keys-with\nnewline"
        self.db[key] = "value"

        val = self.db[key]
        self.assertEqual(val, "value")

        keys = self.db.prefix(key)
        self.assertEqual(keys, (key,))

        keys = self.db.keys()
        self.assertTupleEqual(tuple(keys), (key,))

        # just to make sure...
        self.assertTupleEqual(tuple(self.db.keys()), self.db.prefix(""))

        del self.db[key]
        with self.assertRaises(KeyError):
            val = self.db[key]

    def test_delete_nonexistent_key(self) -> None:
        """Test that deleting a non-existent key returns 404."""
        key = "this-doesn't-exist"
        with self.assertRaises(KeyError):
            self.db[key]

    def test_get_set_fancy_object(self) -> None:
        """Test that we can get/set/delete something that's more than a string."""
        key = "big-ol-list"
        val = ["this", {"is": "a", "complex": "object"}, 1337]

        self.db[key] = val
        act = self.db[key]
        self.assertEqual(act, val)
