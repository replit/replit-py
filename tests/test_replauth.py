"""Tests for replit.auth."""

import unittest

from replit.auth import get_user_info, User

class FakeRequest:
  def __init__(self, headers):
    self.__dict__ = {
      "headers": headers
    }

class TestAuth(unittest.TestCase):
    """Tests for replit.auth."""

    def setUp(self) -> None:
        """Set up two fake request objects - one with auth and one without."""
        self.unauthRequest = FakeRequest({
          "X-Replit-User-Id": "",
          "X-Replit-User-Name": "",
          "X-Replit-User-Profile-Image": "",
          "X-Replit-User-Bio": "",
          "X-Replit-User-Url": "",
          "X-Replit-User-Roles": "",
          "X-Replit-User-Teams": ""
        })
        self.authRequest = FakeRequest({
          "X-Replit-User-Id": "0",
          "X-Replit-User-Name": "mark",
          "X-Replit-User-Profile-Image": "https://replit.com/public/images/mark.png",
          "X-Replit-User-Bio": "ohhi",
          "X-Replit-User-Url": "https://replit.com/@mark",
          "X-Replit-User-Roles": "explorer,moderator,admin",
          "X-Replit-User-Teams": "replit,util,moderation"
        })

    def test_check_proper_auth(self) -> None:
        """Test get_user_info."""
        authed = get_user_info(self.authRequest)
        self.assertIsInstance(authed, User)

        unauthed = get_user_info(self.unauthRequest)
        self.assertIsInstance(unauthed, type(None))

    def test_check_user_data(self) -> None:
        """Test to see if the user data is correct."""
        user = get_user_info(self.authRequest)

        self.assertDictEqual(user.__dict__, {
          "id": 0,
          "name": "mark",
          "profile_image": "https://replit.com/public/images/mark.png",
          "bio": "ohhi",
          "url": "https://replit.com/@mark",
          "roles": ["explorer", "moderator", "admin"],
          "teams": ["replit", "util", "moderation"]
        })
