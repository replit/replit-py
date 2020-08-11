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
