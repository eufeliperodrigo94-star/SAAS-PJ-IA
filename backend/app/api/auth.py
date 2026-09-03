from fastapi import APIRouter, Depends

from app.core.security import AuthenticatedUser, get_current_user
from app.schemas.auth import MeResponse, OrganizationOut, RegisterOrganizationRequest
from app.services.organization_service import register_organization

router = APIRouter(prefix="/auth", tags=["auth"])


@router.get("/me", response_model=MeResponse)
def me(user: AuthenticatedUser = Depends(get_current_user)) -> MeResponse:
    return MeResponse(
        id=user.id,
        email=user.email,
        organization_id=user.organization_id,
        role=user.role,
        is_super_admin=user.is_super_admin,
    )


@router.post("/register-organization", response_model=OrganizationOut)
def register_organization_endpoint(
    payload: RegisterOrganizationRequest,
    user: AuthenticatedUser = Depends(get_current_user),
) -> OrganizationOut:
    result = register_organization(user, payload.organization_name, payload.full_name)
    return OrganizationOut(**result)
