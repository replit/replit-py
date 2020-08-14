"""Tests for replit.database."""

import os
import unittest

from replit.database import AsyncReplitDb, ReplitDb
import requests


class TestAsyncDatabase(unittest.IsolatedAsyncioTestCase):
    """Tests for replit.database.AsyncReplitDb."""

    async def asyncSetUp(self) -> None:
        """Grab a JWT for all the tests to share."""
        password = os.environ["PASSWORD"]
        req = requests.get(
            "https://database-test-jwt.kochman.repl.co", auth=("test", password)
        )
        url = req.text
        self.db = AsyncReplitDb(url)

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

        jk = self.db.jsonkey(key, dtype=str, do_raise=True)
        with self.assertRaises(KeyError):
            await jk.get()
        await jk.set("value")
        val = await jk.get()
        self.assertEqual(val, "value")

    async def test_jsonkey_default(self) -> None:
        """Test replit.database.AsyncJSONKey with a default callable."""
        key = "test-jsonkey"

        jk = self.db.jsonkey(key, dtype=str, get_default=lambda: "value")
        val = await jk.get()
        self.assertEqual(val, "value")


class TestDatabase(unittest.IsolatedAsyncioTestCase):
    """Tests for replit.database.ReplitDb."""

    def setUp(self) -> None:
        """Grab a JWT for all the tests to share."""
        password = os.environ["PASSWORD"]
        req = requests.get(
            "https://database-test-jwt.kochman.repl.co", auth=("test", password)
        )
        url = req.text
        self.db = ReplitDb(url)

        # nuke whatever is already here
        for k in self.db.keys():
            self.db.delete(k)

    async def tearDown(self) -> None:
        """Nuke whatever the test added."""
        for k in await self.db.keys():
            await self.db.delete(k)

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
