from dataclasses import dataclass

import httpx
from fastapi import Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import JWTError, jwt

from app.core.config import get_settings
from app.core.exceptions import NotAuthenticatedError
from app.core.supabase_client import get_supabase_admin

bearer_scheme = HTTPBearer(auto_error=False)

# Projetos Supabase criados a partir de 2024 assinam o JWT de sessão com uma
# chave assimétrica (ES256/RS256) por padrão, publicada em .well-known/jwks.json —
# não mais com o "JWT Secret" HS256 legado. Suportamos os dois esquemas.
_jwks_cache: dict | None = None


def _fetch_jwks(force_refresh: bool = False) -> dict:
    global _jwks_cache
    if _jwks_cache is None or force_refresh:
        settings = get_settings()
        response = httpx.get(
            f"{settings.supabase_url}/auth/v1/.well-known/jwks.json", timeout=5.0
        )
        response.raise_for_status()
        _jwks_cache = response.json()
    return _jwks_cache


def _find_jwk(kid: str) -> dict | None:
    jwks = _fetch_jwks()
    key = next((k for k in jwks.get("keys", []) if k.get("kid") == kid), None)
    if key is not None:
        return key
    # A chave pode ter rotacionado desde o último cache — busca de novo uma vez.
    jwks = _fetch_jwks(force_refresh=True)
    return next((k for k in jwks.get("keys", []) if k.get("kid") == kid), None)


def _decode_supabase_jwt(token: str) -> dict:
    settings = get_settings()
    try:
        header = jwt.get_unverified_header(token)
    except JWTError as exc:
        raise NotAuthenticatedError("Token inválido ou expirado.") from exc

    algorithm = header.get("alg", "HS256")

    try:
        if algorithm == "HS256":
            # Projetos legados com JWT Secret compartilhado.
            return jwt.decode(
                token,
                settings.supabase_jwt_secret,
                algorithms=["HS256"],
                audience="authenticated",
            )

        # Chave assimétrica (ES256/RS256) — verifica contra a JWKS pública do projeto.
        key = _find_jwk(header.get("kid", ""))
        if key is None:
            raise NotAuthenticatedError("Chave de assinatura do token não reconhecida.")
        return jwt.decode(token, key, algorithms=[algorithm], audience="authenticated")
    except JWTError as exc:
        raise NotAuthenticatedError("Token inválido ou expirado.") from exc


@dataclass
class AuthenticatedUser:
    id: str
    email: str | None
    organization_id: str | None
    role: str | None


def get_current_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(bearer_scheme),
) -> AuthenticatedUser:
    if credentials is None:
        raise NotAuthenticatedError()

    payload = _decode_supabase_jwt(credentials.credentials)
    user_id = payload.get("sub")
    if not user_id:
        raise NotAuthenticatedError("Token sem identificação de usuário.")

    membership = (
        get_supabase_admin()
        .table("organization_users")
        .select("organization_id, role")
        .eq("user_id", user_id)
        .limit(1)
        .execute()
    )
    row = membership.data[0] if membership.data else None

    return AuthenticatedUser(
        id=user_id,
        email=payload.get("email"),
        organization_id=row["organization_id"] if row else None,
        role=row["role"] if row else None,
    )


def require_organization(
    user: AuthenticatedUser = Depends(get_current_user),
) -> AuthenticatedUser:
    if not user.organization_id:
        raise NotAuthenticatedError("Usuário não pertence a nenhuma organização.")
    return user
