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
        replit.identity.verify_ghostwriter(
            "v2.public.Q2dzSWo3WEhtZ1lRaFpUNk9SSUxDTjdueTVvR0VJR1grams9_fZqjxwti-9Y3VdGzk98c3ZxY9XaMnHlRptVYfaah-R99LY4yhI1tGfokCaStimfJllYGnegFANHVQSozoM3Cg.R0FFaUMyZG9iM04wZDNKcGRHVnlFcndDZGpJdWNIVmliR2xqTGxFeVpIcFRWMjh6VjBWb2RGb3hiRkpsVm5CWlltczVVMU5WZUVSVWFtUjFaVlJXZGxJd1ZrNWlWMWt4WlcxMGFGRlhhRzVTTUdSdVUxWnNRbUZIT1VSU01FWk9XVlZHYjFvd1ZrcGhiRnA1VkZkck1XUXlVbGhUYms1b1ZqQXhNVmxVVG5kYWJWSTJZVWhhWVZkSGVISldWRXBQVW0xRmVGcEdVbWxpVkd4dFYwUkdiMkpIU2xoaVJrNU9WakprTmxWV1RYaGhWbFpIVm1wV1dsZEdhM2xXYTFwRFVrWmFSbEpyV2xCUlZEQTVTSGh4ZFU1RVN6ZDZOV3g1YWkxbVJrTnBiamRqYWtGTFJVUmpNbWxKTld0bFQyNXZjbHBTVEdsUExUVlFNWFZoUjNSUGVscGZlRzkwT0dGcVgwYzFXVTFWVlRkcVh6ZzVNalpoTFVaQmVtRk9UbnBVUTFFdVVqQkdSbUZWVFhsYVJ6bHBUVEEwZDFwRVRrdGpSMUpJVm01c1JGb3hXbkpYYkdoYVRtc3hVbEJVTUE9PQ"  # noqa: E501,B950 # line too long
        )
