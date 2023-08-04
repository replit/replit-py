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

    # def test_read_public_key_from_env(self) -> None:
    #     """Test read_public_key_from_env."""
    #     pubkey = replit.identity.read_public_key_from_env("dev:1", "goval")
    #     self.assertIsInstance(pubkey, pyseto.versions.v2.V2Public)

    # def test_verify_ghostwriter(self) -> None:
    #     """Test verify_ghostwriter."""
    #     # This token should be valid for 10y.
    #     replit.identity.verify_ghostwriter(
    #         "v2.public.Q2dzSTc4L0htZ1lRbXB1VmNoSUxDTDZDekpvR0VOQ2RsWEk9S1AmYjDdBvVZjmHFgcYVDD57VvJFKbXF9q-fFYQ0XYu12xG8cMV0EK12qFcD3ihtCdqkNoCbNmFpNByDooKSDA.R0FFaUMyZG9iM04wZDNKcGRHVnlFcndDZGpJdWNIVmliR2xqTGxFeVpIcFRWR00wVERCb2RGb3hiRkpNTURWRVVrZE9iMU5WZUVSVVJGcEVaV3R3ZGxJd1ZrNVpiR3h1VFRCc2FGRlhhRzVTTUdSdVUxWnNRbUZIT1VSU01FWk9XVlZHYjFvd1ZrcGhiRnA1VkZkck1XUXlVbGhUYms1b1ZqQXhNVnBXV2tObGJGcHlZVWhPVTJWck5ERmFSelZyWkZVNVJtVkdWbXROUkdneldsY3hjMU5IU2xobFJFcHJVakJzTUZsVVFrdFZSMFpYV25wQ1lWSkdTbHBhUnpGSFpFVXdlR0ZGY0dGa2VqQTVUbXRKWWpaM1NscG9NRGcyYnpRMGIwaEhVRGhCZG13MWNWaHRaMkUyZFd4R1JGcHhObmRSWTFGU2MyRnVjV2hXVEhsamJsQTRXbTFEUVhOV2JWOVplbmQxZUVreGIwaEVZbmQzYmw4d2QxbzRaakp4UTJjdVVqQkdSbUZWVFhsYVJ6bHBUVEEwZDFwRVRrdGpSMUpJVm01c1JGb3hXbkpYYkdoYVRtc3hVbEJVTUE9PQ"  # noqa: E501,B950 # line too long
    #     )
