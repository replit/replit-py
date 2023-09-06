"""This library allows signing identity tokens from Replit."""

import base64

import pyseto

from . import verify
from ..goval.api import signing_pb2


class SigningAuthority:
    """A class to generate tokens that prove identity.

    This class proves the identity of one repl (your own) against another repl
    (the audience). Use this to prevent the target repl from spoofing your own
    identity by forwarding the token.
    """

    def __init__(
        self,
        marshaled_private_key: str,
        marshaled_identity: str,
        replid: str,
        pubkey_source: verify.PubKeySource = verify.read_public_key_from_env,
    ) -> None:
        """Creates a new SigningAuthority.

        Args:
            marshaled_private_key: The private key, in PASERK format.
            marshaled_identity: The PASETO of the Repl identity.
            replid: The ID of the source Repl.
            pubkey_source: The PubKeySource to get the public key.
        """
        self.identity = verify.verify_identity_token(
            marshaled_identity, replid, pubkey_source
        )
        self.signing_authority = verify.get_signing_authority(marshaled_identity)
        self.private_key = pyseto.Key.from_paserk(marshaled_private_key)

    def sign(self, audience: str) -> str:
        """Generates a new token that can be given to the provided audience.

        This is resistant against forwarding, so that the recipient cannot
        forward this token to another repl and claim it came directly from you.

        Args:
            audience: The audience that the token will be signed for.

        Returns:
            The encoded token in PASETO format.
        """
        identity = signing_pb2.GovalReplIdentity()
        identity.CopyFrom(self.identity)
        identity.aud = audience

        encoded_identity = identity.SerializeToString()
        encoded_cert = self.signing_authority.SerializeToString()

        return pyseto.encode(
            self.private_key,
            base64.b64encode(encoded_identity),
            base64.b64encode(encoded_cert),
        ).decode("utf-8")
