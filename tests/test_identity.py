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

    def test_verify_identity_token(self) -> None:
        """Test verify_identity_token."""
        # This token should be valid for 100y.
        # Generated with `go run ./cmd/goval_keypairgen/ -eternal -sample-token -identity -gen-prefix dev -gen-id identity -issuer conman -replid=test -shortlived=false` in goval.
        replit.identity.verify_identity_token(
            identity_token="v2.public.Q2dSMFpYTjBJZ1IwWlhOMFxmipFrFWTrOkBoOzmSd8l3hYl88GIxsQTq4oueW4d8Lq7mhxYhl3RrZ6Tty24kpkOuIf0b5h582qp98L9iJwI.R0FFaUJtTnZibTFoYmhLbUFuWXlMbkIxWW14cFl5NVJNbVI2VTFkNGJXVnRWbmRrTVd4U1QxaFJNMkp0U2tOVFZYaEVVekZOTUdScVVtcFZNRlpPWVcwd01VMXVaR2hSVjJodVVtdGtibGRWZEVOVFJrcHpXWHBPVW1GVk5WaGpNMnhOWW10SmVGZFhNVFJqUm13MVRsWk9hMDFyV1hoVk1qRnpZVlp3U0dJemFHaGhlbFY1VjFaa2IxVnNaRmxpTTJSaFpWUkZlVlJYY0d0WGJFcDBWMjVLYUZaclZYcGFWbVJyWlVkU1JtUkVXbXRTYkZwV1ZGUktWazVLZVdKaGJsWmlOeTFRTUZsRWJIRnlibkZCV1RaSGMwRTFZbU5rUWtaUmVIRkJNMnRSWkd0NFozSXdYeTFrUVZSUGFtRk9PRGhFUkZVMldVZFJlazlwTkY5WVoyaGlTbWM1WVRodE1GcFlNRGhwTm14QldTNVNNRVpHWVZWS2RGUnVXbWxpVkVadldXMWtkbEpzY0VoV2FrcFFZV3RWT1E9PQ",  # noqa: E501,B950 # line too long
            audience="test",
        )

    def test_verify_ghostwriter(self) -> None:
        """Test verify_ghostwriter."""
        # This token should be valid for 100y.
        # Generated with `go run ./cmd/goval_keypairgen/ -eternal -sample-token -ghostwriter -gen-prefix dev -gen-id ghostwriter -issuer ghostwriter -replid=test -shortlived=false` in goval.
        replit.identity.verify_ghostwriter(
            "v2.public.Q2d3SW12M2Vwd1lRNU9YUCtBRVNEQWlhdWIrSEVoQ042Yy80QVJvRWRHVnpkQT09DdURfbtuhiOQ-2cB_j1YE2pDKOnggxcFUEQsl9601dSTmqApx-6PuJiqGAHVEaMlDJa09zz04gBiYTqH75_SDg.R0FFaUMyZG9iM04wZDNKcGRHVnlFcllDZGpJdWNIVmliR2xqTGxFeVpETlRWMnQyVFRKV2QyUXhiRkpqUkZKWVMzbDBRbEpXVGtWUlYyeG9aRmRKY2xORlZtOVJNVkp4WTJwak1GRldTblpSTUdSQ1YxZEdRMW95T1VaYVJXUlhaVzFTUkZOVVJtaGxhMnd4V1RCb1YyRlhTa2hpUjNCTlltMVNXbFJyVWxkVFIxWkdWbTF3YUZZeWFGRlhiWE14V1ZaS1dGSnJUbWxTYkZWNFYyeGFkMVJXY0hOUldHUnJZWHByTVZkdGNGZFRNVzk0VVcxc1VGSnJXbFJVTUdoVFkwWnZkMUpVTVZoMFF6TktORTVIYW5NMlRubHlMVmhHVFd4blVHb3hUVEpsUzNKWE0zQnZjMmRTTlRGRVRXTk9keTFaVlZGdWRqbFRWbTFoYTNsMU9WbDZlRkEyU25SNk5GQndWMHBwUlMxRFdFZHpSMnN6WjNSSVNVa3VVakJHUm1GVlRYbGFSemxwVFRBMGQxcEVUa3RqUjFKSVZtNXNSRm94V25KWGJHaGFUbXN4VWxCVU1BPT0"  # noqa: E501,B950 # line too long
        )
