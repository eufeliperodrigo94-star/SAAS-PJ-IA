import time

import pytest
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import ec
from jose import jwk, jwt

from app.core.exceptions import NotAuthenticatedError
from app.core.security import _decode_supabase_jwt


@pytest.fixture
def es256_keypair():
    private_key = ec.generate_private_key(ec.SECP256R1())
    pem = private_key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=serialization.NoEncryption(),
    )
    public_jwk = jwk.construct(pem, algorithm="ES256").to_dict()
    public_jwk.pop("d", None)
    public_jwk["kid"] = "test-key-1"
    return pem, public_jwk


def _make_token(pem: bytes, kid: str, **extra_claims) -> str:
    claims = {
        "sub": "user-1",
        "email": "user@example.com",
        "aud": "authenticated",
        "exp": int(time.time()) + 3600,
        **extra_claims,
    }
    return jwt.encode(claims, pem, algorithm="ES256", headers={"kid": kid})


def test_decode_es256_token_via_jwks(monkeypatch, es256_keypair):
    pem, public_jwk = es256_keypair
    monkeypatch.setattr(
        "app.core.security._fetch_jwks", lambda force_refresh=False: {"keys": [public_jwk]}
    )

    token = _make_token(pem, public_jwk["kid"])
    payload = _decode_supabase_jwt(token)

    assert payload["sub"] == "user-1"
    assert payload["email"] == "user@example.com"


def test_decode_es256_token_refetches_jwks_on_unknown_kid(monkeypatch, es256_keypair):
    pem, public_jwk = es256_keypair
    calls = []

    def fake_fetch(force_refresh=False):
        calls.append(force_refresh)
        # Simula uma JWKS desatualizada em cache (chave ainda não vista);
        # só aparece depois que o backend força um refresh.
        return {"keys": [public_jwk]} if force_refresh else {"keys": []}

    monkeypatch.setattr("app.core.security._fetch_jwks", fake_fetch)

    token = _make_token(pem, public_jwk["kid"])
    payload = _decode_supabase_jwt(token)

    assert payload["sub"] == "user-1"
    assert True in calls  # buscou de novo com force_refresh


def test_decode_es256_token_unknown_key_raises(monkeypatch, es256_keypair):
    pem, public_jwk = es256_keypair
    monkeypatch.setattr("app.core.security._fetch_jwks", lambda force_refresh=False: {"keys": []})

    token = _make_token(pem, public_jwk["kid"])
    with pytest.raises(NotAuthenticatedError):
        _decode_supabase_jwt(token)


def test_decode_hs256_token_uses_shared_secret(monkeypatch):
    monkeypatch.setattr(
        "app.core.security.get_settings",
        lambda: type("S", (), {"supabase_jwt_secret": "shared-secret", "supabase_url": ""})(),
    )
    token = jwt.encode(
        {"sub": "user-2", "aud": "authenticated", "exp": int(time.time()) + 3600},
        "shared-secret",
        algorithm="HS256",
    )

    payload = _decode_supabase_jwt(token)

    assert payload["sub"] == "user-2"


def test_decode_invalid_token_raises():
    with pytest.raises(NotAuthenticatedError):
        _decode_supabase_jwt("not-a-jwt")
