"""Identity verification."""

import base64
import dataclasses
import datetime
import json
import os
from typing import Callable, cast, Dict, Optional, Set, Tuple

import pyseto

from .exceptions import VerifyError
from ..goval.api import signing_pb2

PubKeySource = Callable[[str, str], pyseto.KeyInterface]


@dataclasses.dataclass
class _MessageClaims:
    """Claims from a signing_pb2.GovalCert."""

    repls: Set[str] = dataclasses.field(default_factory=set)
    users: Set[str] = dataclasses.field(default_factory=set)
    clusters: Set[str] = dataclasses.field(default_factory=set)
    flags: Set[int] = dataclasses.field(default_factory=set)


def _parse_claims(cert: signing_pb2.GovalCert) -> _MessageClaims:
    """Parses claims from a signing_pb2.GovalCert.

    Args:
        cert: The certificate

    Returns:
        The parsed _MessageClaims.
    """
    claims = _MessageClaims()

    for claim in cert.claims:
        if claim.WhichOneof("claim") == "replid":
            claims.repls.insert(claim.replid)
        elif claim.WhichOneof("claim") == "user":
            claims.users.insert(claim.user)
        elif claim.WhichOneof("claim") == "cluster":
            claims.clusters.insert(claim.cluster)
        elif claim.WhichOneof("claim") == "flag":
            claims.flags.insert(claim.flag)

    return claims


def _get_signing_authority(token: str) -> signing_pb2.GovalSigningAuthority:
    # The library does not allow just grabbing the footer to know what key to
    # use, so we need to manually extract that.
    token_parts = token.split(".")
    if len(token_parts) != 4:
        raise VerifyError("token is not correctly PASETO-encoded")
    version, purpose, raw_payload, raw_footer = token_parts
    if version != "v2":
        raise VerifyError(f"only v2 is supported: {version}")
    if purpose != "public":
        raise VerifyError(f'only "public" purpose is supported: {purpose}')

    return signing_pb2.GovalSigningAuthority.FromString(
        base64.b64decode(base64.urlsafe_b64decode(raw_footer + "=="))
    )


def _verify_raw_claims(
    replid: Optional[str] = None,
    user: Optional[str] = None,
    cluster: Optional[str] = None,
    claims: Optional[_MessageClaims] = None,
    any_replid: bool = False,
    any_user: bool = False,
    any_cluster: bool = False,
) -> None:
    if claims is None:
        return

    if not any_replid and replid is not None and replid not in claims.repls:
        raise VerifyError("not authorized (replid)")
    if not any_user and user is not None and user not in claims.users:
        raise VerifyError("not authorized (user)")
    if not any_cluster and cluster is not None and cluster not in claims.clusters:
        raise VerifyError("not authorized (cluster)")


def _verify_claims(
    iat: datetime.datetime,
    exp: datetime.datetime,
    replid: Optional[str] = None,
    user: Optional[str] = None,
    cluster: Optional[str] = None,
    claims: Optional[_MessageClaims] = None,
) -> None:
    now = datetime.datetime.utcnow()
    if iat > now:
        raise VerifyError(f"not valid for {iat - now}")
    if exp < now:
        raise VerifyError(f"expired {now - exp} ago")

    _verify_raw_claims(replid=replid, user=user, cluster=cluster, claims=claims)


class Verifier:
    """Provides verification of tokens."""

    def __init__(self) -> None:
        pass

    def verify_chain(
        self, token: str, pubkey_source: PubKeySource,
    ) -> Tuple[bytes, Optional[signing_pb2.GovalCert]]:
        """Verifies that the token and its signing chain are valid."""
        gsa = _get_signing_authority(token)

        if gsa.key_id != "":
            # If it's signed directly with a root key, grab the pubkey and
            # verify it.
            return (
                self.verify_token_with_keyid(
                    token, gsa.key_id, gsa.issuer, pubkey_source
                ),
                None,
            )

        if gsa.signed_cert != "":
            # If it's signed by another token, verify the other token first.
            signing_bytes, skip_level_cert = self.verify_chain(
                gsa.signed_cert, pubkey_source
            )

            # Make sure the two parent certs agree.
            signing_cert = self.verify_cert(signing_bytes, skip_level_cert)

            # Now verify this token using the parent cert.
            return self.verify_token_with_cert(token, signing_cert), signing_cert

        raise VerifyError(f"Invalid signing authority: {gsa}")

    def verify_token_with_keyid(
        self, token: str, key_id: str, issuer: str, pubkey_source: PubKeySource,
    ) -> bytes:
        """Verifies that the token is valid and signed by the keyid."""
        pubkey = pubkey_source(key_id, issuer)
        return self.verify_token(token, pubkey)

    def verify_token_with_cert(self, token: str, cert: signing_pb2.GovalCert,) -> bytes:
        """Verifies that the token is valid and signed by the cert."""
        pubkey = pyseto.Key.from_paserk(cert.publicKey)
        return self.verify_token(token, pubkey)

    def verify_cert(
        self, encoded_cert: bytes, signing_cert: Optional[signing_pb2.GovalCert]
    ) -> signing_pb2.GovalCert:
        """Verifies that the certificate is valid."""
        cert = signing_pb2.GovalCert.FromString(encoded_cert)

        # Verify that the cert is valid.
        _verify_claims(iat=cert.iat.ToDatetime(), exp=cert.exp.ToDatetime())

        # If the parent is the root cert, there's nothing else to verify.
        if signing_cert:
            claims = _parse_claims(signing_cert)
            if signing_pb2.FlagClaim.SIGN_INTERMEDIATE_CERT not in claims.flags:
                raise VerifyError(
                    "signing cert does not have authority to sign intermediate certs"
                )

            # Verify the cert claims agrees with its signer.
            authorized_claims: Set[str] = set()
            any_replid = False
            any_user = False
            any_cluster = False
            for claim in signing_cert.claims:
                authorized_claims.insert(str(claim))
                if claim.WhichOneof("claim") == "flag":
                    if claim.flag == signing_pb2.FlagClaim.ANY_REPLID:
                        any_replid = True
                    elif claim.flag == signing_pb2.FlagClaim.ANY_USER:
                        any_user = True
                    elif claim.flag == signing_pb2.FlagClaim.ANY_CLUSTER:
                        any_cluster = True

            for claim in signing_cert.claims:
                if claim.WhichOneof("claim") == "replid" and any_replid:
                    continue
                if claim.WhichOneof("claim") == "user" and any_user:
                    continue
                if claim.WhichOneof("claim") == "cluster" and any_cluster:
                    continue
                if str(claim) not in authorized_claims:
                    raise VerifyError(f"signing cert does not authorize claim {claim}")

        return cert

    def verify_token(self, token: str, pubkey: pyseto.KeyInterface,) -> bytes:
        """Verifies that the token is valid."""
        decoded = pyseto.decode(pubkey, token)
        return base64.b64decode(decoded.payload)


def read_public_key_from_env(keyid: str, issuer: str) -> pyseto.KeyInterface:
    """Provides a [PubKeySource] that reads public keys from the environment.

    Args:
        keyid: The ID of the public key used to sign a token.
        issuer: The name of the issuer of the certificate.

    Returns:
        The public key corresponding to the key id.
    """
    pubkeys = cast(Dict[str, str], json.loads(os.getenv("REPL_PUBKEYS")))
    key = base64.b64decode(pubkeys[keyid])
    return pyseto.Key.from_asymmetric_key_params(version=2, x=key)


def verify_ghostwriter(
    ghostwriter_token: str, pubkey_source: PubKeySource = read_public_key_from_env,
) -> signing_pb2.GovalToken:
    """Verifies a Ghostwriter token.

    Args:
        ghostwriter_token: The Ghostwriter token.
        pubkey_source: The PubKeySource to get the public key.

    Returns:
        The parsed and verified signing_pb2.GovalToken.

    Raises:
        VerifyError: If there's any problem verifying the token.
    """
    v = Verifier()
    raw_goval_token, goval_cert = v.verify_chain(ghostwriter_token, pubkey_source)
    # TODO: We may need to use a different type.
    goval_token = signing_pb2.GovalToken.FromString(raw_goval_token)

    # Verify that the cert is valid.
    if goval_cert:
        _verify_claims(
            iat=goval_cert.iat.ToDatetime(),
            exp=goval_cert.exp.ToDatetime(),
            replid=goval_token.replid or None,
        )
        # Ensure that the claims include ghostwriter.
        has_ghostwriter_claim = False
        for claim in goval_cert.claims:
            if claim.WhichOneof("claim") != "flag":
                continue
            if claim.flag == signing_pb2.FlagClaim.GHOSTWRITER:
                has_ghostwriter_claim = True
                break
        if not has_ghostwriter_claim:
            raise VerifyError("not authorized (ghostwriter)")
    return goval_token
