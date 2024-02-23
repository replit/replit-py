"""Tests for replit.identity."""

import json
import os
import unittest

import pyseto
import replit.identity

PUBLIC_KEY = "on0FkSmEC+ce40V9Vc4QABXSx6TXo+lhp99b6Ka0gro="

# This token should be valid for 100y.
# Generated with:
# ```
# go run ./cmd/goval_keypairgen/ -eternal -sample-token \
#   -identity -gen-prefix dev -gen-id identity -issuer conman \
#   -replid=test -shortlived=false
# ```
# in goval.
IDENTITY_PRIVATE_KEY = "k2.secret.6sHU27WoRIaspIOVaShpuZM33ozpfFyI2THfO8fmSX6xiA_Duh4ac5g76Y5bParclsalaOCTaCs6gZowhYivVQ"  # noqa: E501,B950,S106 # line too long
IDENTITY_TOKEN = "v2.public.Q2dSMFpYTjBJZ1IwWlhOMHDnO17Eg43zucAMSAHnCS4C1wn4QUCCOcr-Pggw5SV1KnbOXq8RcQE5if6pMcbJ6lmRWcdoHq5CV9jqyRrUlwo.R0FFaUJtTnZibTFoYmhLckFuWXlMbkIxWW14cFl5NVJNbVF6VTFkd2VHRnRXbmRrTVd4U1lXMDViRm96YkVKU1ZrNUZVVmRzYTA1VmQzSlRSVlp2VWtaa2RGbFZVa3BSVmtwMlVUQmtRbFpYUmtOYU1qbEdXa1ZrVjJWdFVrUlRWRVpvWld0c01Wa3dhRmRoVjBwSVlrZHdUV0pyTldGWGFrWkRUVEEwZVU5WGVGTk5hbFpSVmpGVk5HUkhTbFpQVm1oc1lXdHdORlJVUW5kaFZrbDZVV3hvYUdKWFVubFVWekZyWlZaUmVVOVZhRnBXVkVaTFZtcENjMlZWTVZkV1ZEQkRUbVpoYkhkMk5EUm9SRkZQTFVKWlJDMURWSEUxYVdJeFQzVlVlamxIWW5WTlFVVnFURFExUVVwclZXNW9kR2hxVFZOVVRtOVZSRVphWDBsaVUyTjFjekoxWW05aVowNU1MV2RRVlRGRmVVOTFUVzlHTGxJd1JrWmhWVXAwVkc1YWFXSlVSbTlaYldSMlVteHdTRlpxU2xCaGExVTU"  # noqa: E501,B950,S106 # line too long


class TestIdentity(unittest.TestCase):
    """Tests for replit.identity."""

    def setUp(self) -> None:
        """Set up the public keys."""
        pubkeys = json.loads(os.getenv("REPL_PUBKEYS", "{}"))
        if "dev:1" not in pubkeys:
            os.environ["REPL_PUBKEYS"] = json.dumps({"dev:1": PUBLIC_KEY})

    def test_read_public_key_from_env(self) -> None:
        """Test read_public_key_from_env."""
        pubkey = replit.identity.read_public_key_from_env("dev:1", "goval")
        self.assertIsInstance(pubkey, pyseto.versions.v2.V2Public)

    def test_signing_authority(self) -> None:
        """Test SigningAuthority."""
        gsa = replit.identity.SigningAuthority(
            marshaled_private_key=IDENTITY_PRIVATE_KEY,
            marshaled_identity=IDENTITY_TOKEN,
            replid="test",
        )
        signed_token = gsa.sign("audience")

        replit.identity.verify_identity_token(
            identity_token=signed_token,
            audience="audience",
        )

    def test_verify_identity_token(self) -> None:
        """Test verify_identity_token."""
        replit.identity.verify_identity_token(
            identity_token=IDENTITY_TOKEN,
            audience="test",
        )

    def test_verify_ghostwriter(self) -> None:
        """Test verify_ghostwriter."""
        # This token should be valid for 100y.
        # Generated with:
        # ```
        # go run ./cmd/goval_keypairgen/ -eternal -sample-token \
        #   -ghostwriter -gen-prefix dev -gen-id ghostwriter \
        #   -issuer ghostwriter -replid=test -shortlived=false
        # ```
        # in goval.
        replit.identity.verify_ghostwriter(
            "v2.public.Q2d3SW12M2Vwd1lRNU9YUCtBRVNEQWlhdWIrSEVoQ042Yy80QVJvRWRHVnpkQT09DdURfbtuhiOQ-2cB_j1YE2pDKOnggxcFUEQsl9601dSTmqApx-6PuJiqGAHVEaMlDJa09zz04gBiYTqH75_SDg.R0FFaUMyZG9iM04wZDNKcGRHVnlFcllDZGpJdWNIVmliR2xqTGxFeVpETlRWMnQyVFRKV2QyUXhiRkpqUkZKWVMzbDBRbEpXVGtWUlYyeG9aRmRKY2xORlZtOVJNVkp4WTJwak1GRldTblpSTUdSQ1YxZEdRMW95T1VaYVJXUlhaVzFTUkZOVVJtaGxhMnd4V1RCb1YyRlhTa2hpUjNCTlltMVNXbFJyVWxkVFIxWkdWbTF3YUZZeWFGRlhiWE14V1ZaS1dGSnJUbWxTYkZWNFYyeGFkMVJXY0hOUldHUnJZWHByTVZkdGNGZFRNVzk0VVcxc1VGSnJXbFJVTUdoVFkwWnZkMUpVTVZoMFF6TktORTVIYW5NMlRubHlMVmhHVFd4blVHb3hUVEpsUzNKWE0zQnZjMmRTTlRGRVRXTk9keTFaVlZGdWRqbFRWbTFoYTNsMU9WbDZlRkEyU25SNk5GQndWMHBwUlMxRFdFZHpSMnN6WjNSSVNVa3VVakJHUm1GVlRYbGFSemxwVFRBMGQxcEVUa3RqUjFKSVZtNXNSRm94V25KWGJHaGFUbXN4VWxCVU1BPT0"  # noqa: E501,B950,S106 # line too long
        )
