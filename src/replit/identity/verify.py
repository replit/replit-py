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
    user_ids: Set[int] = dataclasses.field(default_factory=set)
    clusters: Set[str] = dataclasses.field(default_factory=set)
    subclusters: Set[str] = dataclasses.field(default_factory=set)
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
            claims.repls.add(claim.replid)
        elif claim.WhichOneof("claim") == "user":
            claims.users.add(claim.user)
        elif claim.WhichOneof("claim") == "user_id":
            claims.user_ids.add(claim.user_id)
        elif claim.WhichOneof("claim") == "cluster":
            claims.clusters.add(claim.cluster)
        elif claim.WhichOneof("claim") == "subcluster":
            claims.subclusters.add(claim.subcluster)
        elif claim.WhichOneof("claim") == "flag":
            claims.flags.add(claim.flag)

    return claims


def get_signing_authority(token: str) -> signing_pb2.GovalSigningAuthority:
    """Gets the signing authority from a token.

    Args:
        token: The token in a PASETO format.

    Returns:
        The parsed GovalSigningAuthority.

    Raises:
        VerifyError: If there's any problem verifying the token.
    """
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
    user_id: Optional[int] = None,
    cluster: Optional[str] = None,
    subcluster: Optional[str] = None,
    claims: Optional[_MessageClaims] = None,
    deployment: bool = False,
) -> None:
    if claims is None:
        return

    any_replid = signing_pb2.FlagClaim.ANY_REPLID in claims.flags
    any_user = signing_pb2.FlagClaim.ANY_USER in claims.flags
    any_user_id = signing_pb2.FlagClaim.ANY_USER_ID in claims.flags
    any_cluster = signing_pb2.FlagClaim.ANY_CLUSTER in claims.flags
    any_subcluster = signing_pb2.FlagClaim.ANY_SUBCLUSTER in claims.flags
    deployments = signing_pb2.FlagClaim.DEPLOYMENTS in claims.flags

    if not any_replid and replid is not None and replid not in claims.repls:
        raise VerifyError(
            f"not authorized (replid), got {replid!r}, want {claims.repls!r}"
        )
    if not any_user and user is not None and user not in claims.users:
        raise VerifyError(f"not authorized (user), got {user!r}, want {claims.users!r}")
    if not any_user_id and user_id is not None and user_id not in claims.user_ids:
        raise VerifyError(
            f"not authorized (user_id), got {user_id!r}, want {claims.user_ids!r}"
        )
    if not any_cluster and cluster is not None and cluster not in claims.clusters:
        raise VerifyError(
            f"not authorized (cluster), got {cluster!r}, want {claims.clusters!r}"
        )
    if (
        not any_subcluster
        and subcluster is not None
        and subcluster not in claims.subclusters
    ):
        raise VerifyError(
            f"not authorized (subcluster), "
            f"got {subcluster!r}, want {claims.subclusters!r}"
        )
    if not deployments and deployment:
        raise VerifyError("not authorized (deployment)")


def _verify_claims(
    iat: datetime.datetime,
    exp: datetime.datetime,
    replid: Optional[str] = None,
    user: Optional[str] = None,
    user_id: Optional[int] = None,
    cluster: Optional[str] = None,
    subcluster: Optional[str] = None,
    deployment: bool = False,
    claims: Optional[_MessageClaims] = None,
) -> None:
    now = datetime.datetime.utcnow()
    if iat > now:
        raise VerifyError(f"not valid for {iat - now}")
    if exp < now:
        raise VerifyError(f"expired {now - exp} ago")

    _verify_raw_claims(
        replid=replid,
        user=user,
        user_id=user_id,
        cluster=cluster,
        subcluster=subcluster,
        claims=claims,
    )


class Verifier:
    """Provides verification of tokens."""

    def __init__(self) -> None:
        pass

    def verify_chain(
        self,
        token: str,
        pubkey_source: PubKeySource,
    ) -> Tuple[bytes, Optional[signing_pb2.GovalCert]]:
        """Verifies that the token and its signing chain are valid."""
        gsa = get_signing_authority(token)

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
        self,
        token: str,
        key_id: str,
        issuer: str,
        pubkey_source: PubKeySource,
    ) -> bytes:
        """Verifies that the token is valid and signed by the keyid."""
        pubkey = pubkey_source(key_id, issuer)
        return self.verify_token(token, pubkey)

    def verify_token_with_cert(
        self,
        token: str,
        cert: signing_pb2.GovalCert,
    ) -> bytes:
        """Verifies that the token is valid and signed by the cert."""
        pubkey = pyseto.Key.from_paserk(cert.publicKey)
        return self.verify_token(token, pubkey)

    def verify_cert(
        self, encoded_cert: bytes, signing_cert: Optional[signing_pb2.GovalCert]
    ) -> signing_pb2.GovalCert:
        """Verifies that the certificate is valid."""
        cert = signing_pb2.GovalCert.FromString(encoded_cert)

        # Verify that the cert is valid.
        _verify_claims(
            iat=cert.iat.ToDatetime(),
            exp=cert.exp.ToDatetime(),
            claims=_parse_claims(cert),
        )

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
            any_user_id = False
            any_cluster = False
            any_subcluster = False
            for claim in signing_cert.claims:
                authorized_claims.add(str(claim))
                if claim.WhichOneof("claim") == "flag":
                    if claim.flag == signing_pb2.FlagClaim.ANY_REPLID:
                        any_replid = True
                    elif claim.flag == signing_pb2.FlagClaim.ANY_USER:
                        any_user = True
                    elif claim.flag == signing_pb2.FlagClaim.ANY_USER_ID:
                        any_user_id = True
                    elif claim.flag == signing_pb2.FlagClaim.ANY_CLUSTER:
                        any_cluster = True
                    elif claim.flag == signing_pb2.FlagClaim.ANY_SUBCLUSTER:
                        any_subcluster = True

            for claim in signing_cert.claims:
                if claim.WhichOneof("claim") == "replid" and any_replid:
                    continue
                if claim.WhichOneof("claim") == "user" and any_user:
                    continue
                if claim.WhichOneof("claim") == "user_id" and any_user_id:
                    continue
                if claim.WhichOneof("claim") == "cluster" and any_cluster:
                    continue
                if claim.WhichOneof("claim") == "subcluster" and any_subcluster:
                    continue
                if str(claim) not in authorized_claims:
                    raise VerifyError(f"signing cert does not authorize claim {claim}")

        return cert

    def verify_token(
        self,
        token: str,
        pubkey: pyseto.KeyInterface,
    ) -> bytes:
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


def verify_identity_token(
    identity_token: str,
    audience: str,
    pubkey_source: PubKeySource = read_public_key_from_env,
) -> signing_pb2.GovalReplIdentity:
    """Verifies a Repl Identity token.

    Args:
        identity_token: The Identity token.
        audience: The audience that the token was signed for.
        pubkey_source: The PubKeySource to get the public key.

    Returns:
        The parsed and verified signing_pb2.GovalReplIdentity.

    Raises:
        VerifyError: If there's any problem verifying the token.
    """
    v = Verifier()
    raw_goval_token, goval_cert = v.verify_chain(identity_token, pubkey_source)
    repl_identity = signing_pb2.GovalReplIdentity.FromString(raw_goval_token)

    # Verify that the cert is valid.
    if repl_identity.aud != audience:
        raise VerifyError(
            f"not authorized (audience), got {repl_identity.aud!r}, want {audience!r}"
        )
    deployment: bool = False
    cluster: Optional[str] = None
    subcluster: Optional[str] = None
    if repl_identity.WhichOneof("runtime") == "deployment":
        deployment = True
    elif repl_identity.WhichOneof("runtime") == "interactive":
        cluster = repl_identity.interactive.cluster
        subcluster = repl_identity.interactive.subcluster
    _verify_claims(
        iat=goval_cert.iat.ToDatetime(),
        exp=goval_cert.exp.ToDatetime(),
        cluster=cluster,
        subcluster=subcluster,
        deployment=deployment,
        claims=_parse_claims(goval_cert) if goval_cert else None,
    )
    return repl_identity


def verify_ghostwriter(
    ghostwriter_token: str,
    pubkey_source: PubKeySource = read_public_key_from_env,
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
            claims=_parse_claims(goval_cert),
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
