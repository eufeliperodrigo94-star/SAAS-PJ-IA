from dataclasses import dataclass

from fastapi import Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import JWTError, jwt

from app.core.config import get_settings
from app.core.exceptions import NotAuthenticatedError
from app.core.supabase_client import get_supabase_admin

bearer_scheme = HTTPBearer(auto_error=False)


@dataclass
class AuthenticatedUser:
    id: str
    email: str | None
    organization_id: str | None
    role: str | None


def _decode_supabase_jwt(token: str) -> dict:
    settings = get_settings()
    try:
        return jwt.decode(
            token,
            settings.supabase_jwt_secret,
            algorithms=["HS256"],
            audience="authenticated",
        )
    except JWTError as exc:
        raise NotAuthenticatedError("Token inválido ou expirado.") from exc


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
