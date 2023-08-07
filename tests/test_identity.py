"""Tests for replit.identity."""

import json
import os
import unittest

import pyseto
import replit.identity

PUBLIC_KEY = "on0FkSmEC+ce40V9Vc4QABXSx6TXo+lhp99b6Ka0gro="


class TestIdentity(unittest.TestCase):
    """Tests for replit.identity."""

    def setUp(self) -> None:
        """Set up the public keys."""
        if "REPL_PUBKEYS" not in os.environ:
            os.environ["REPL_PUBKEYS"] = json.dumps({"dev:1": PUBLIC_KEY})

    def test_read_public_key_from_env(self) -> None:
        """Test read_public_key_from_env."""
        pubkey = replit.identity.read_public_key_from_env("dev:1", "goval")
        self.assertIsInstance(pubkey, pyseto.versions.v2.V2Public)

    def test_verify_ghostwriter(self) -> None:
        """Test verify_ghostwriter."""
        # This token should be valid for 100y.
        # Generated with `go run ./cmd/goval_keypairgen/ -eternal -sample-token -ghostwriter -gen-prefix dev -gen-id ghostwriter -issuer ghostwriter` in goval.
        replit.identity.verify_ghostwriter(
            "v2.public.Q2d3SXpwSEZwZ1lRdS9uS2hnSVNEQWlPeE1tbUJoQ1QrOHFHQWhvRWRHVnpkQT09Cupv8UwpdFsrAj8U_lAZXxYaBL3jL-tMHkhpveBEHqNpTGehlN-oWlEYcvyUwQq9JKxvNSblReAdElDxGXrkBQ.R0FFaUMyZG9iM04wZDNKcGRHVnlFcVlDZGpJdWNIVmliR2xqTGxFeVpETlRXRmt4VTBWYWQxb3hiRkprVkdoUVRqSm9ibE5XVGtWUlYyeFFaVVV4ZEdKVlNtOVNSM0ExV1c1V1NGRlhhSFpSTUdSQ1YxZHNUMVl6VGpWVVJ6VkRUVlpzZEdWSVFscGxWRlp6VmtaYWIxbFhWbGhXYlhSVlZteEtUMVJWVFhkTmJVWkhZMGhXYW1KVWJIWmFWVlY0VkVkR1JWVnVWbFppYlhONFdURm9iMVpzYjNsT1dFSmhZa1ZhYlZkSWNGTlViRloxVjIwMWNWZFFRVVUwZDNNdFltaGFaMGxPV2xGRlMwRjFOa3B0V1dVeVRYcHZabXBEYkZwaWJVWjRVbXBzZUhnMGVXMWlkazloTjJOM1ZuZzJZemR0YUhsaFpVaGtlamwyT0c5Rk1XRmxhekZsYlZVNU9XTlJUaTVTTUVaR1lWVk5lVnBIT1dsTk1EUjNXa1JPUzJOSFVraFdibXhFV2pGYWNsZHNhRnBPYXpGU1VGUXc"  # noqa: E501,B950 # line too long
        )
