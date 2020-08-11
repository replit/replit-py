import os
import unittest

import requests

from replit.database import AsyncReplitDb


class TestDatabase(unittest.IsolatedAsyncioTestCase):
    def setUp(self):
        password = os.environ["PASSWORD"]
        req = requests.get(
            "https://database-test-jwt.kochman.repl.co", auth=("test", password)
        )
        url = req.text
        self.db = AsyncReplitDb(url)

    async def test_get_set_delete(self):
        await self.db.set("test-key", "value")

        val = await self.db.get("test-key")
        self.assertEqual(val, "value")

        await self.db.delete("test-key")
        with self.assertRaises(KeyError):
            await self.db.get("test-key")

    async def test_list_keys(self):
        key = "test-list-keys-with\nnewline"
        await self.db.set(key, "value")

        val = await self.db.get(key)
        self.assertEqual(val, "value")

        keys = await self.db.list(key)
        self.assertEqual(keys, (key,))

        await self.db.delete(key)
        with self.assertRaises(KeyError):
            await self.db.get(key)
