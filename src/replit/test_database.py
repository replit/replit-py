"""Tests for replit.database."""

import os
import unittest

from replit.database import AsyncReplitDb
import requests


class TestDatabase(unittest.IsolatedAsyncioTestCase):
    """Tests for replit.database.AsyncReplitDb."""

    async def asyncSetUp(self) -> None:
        """Grab a JWT for all the tests to share."""
        password = os.environ["PASSWORD"]
        req = requests.get(
            "https://database-test-jwt.kochman.repl.co", auth=("test", password)
        )
        url = req.text
        self.db = AsyncReplitDb(url)

        # nuke whatever's in there
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

        await self.db.delete(key)
        with self.assertRaises(KeyError):
            await self.db.get(key)

    async def test_dict(self) -> None:
        """Test that we can get a dict."""
        await self.db.set("key1", "value")
        await self.db.set("key2", "value")
        d = await self.db.to_dict()
        self.assertDictEqual(d, {"key1": "value", "key2": "value"})
