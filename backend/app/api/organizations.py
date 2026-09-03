from fastapi import APIRouter, Depends

from app.core.security import AuthenticatedUser, require_organization, require_roles
from app.schemas.organization import (
    MemberInvite,
    MemberOut,
    MemberRoleOut,
    MemberRoleUpdate,
    OrganizationDetailOut,
    OrganizationRename,
)
from app.services import organization_service

router = APIRouter(prefix="/organizations", tags=["organizations"])


@router.get("/me", response_model=OrganizationDetailOut)
def get_my_organization(user: AuthenticatedUser = Depends(require_organization)) -> dict:
    return organization_service.get_my_organization(user.organization_id)


@router.patch("/me", response_model=OrganizationDetailOut)
def rename_organization(
    payload: OrganizationRename,
    user: AuthenticatedUser = Depends(require_roles("owner", "admin")),
) -> dict:
    return organization_service.rename_organization(user.organization_id, payload.name, user.id)


@router.get("/me/members", response_model=list[MemberOut])
def list_members(user: AuthenticatedUser = Depends(require_organization)) -> list[dict]:
    return organization_service.list_members(user.organization_id)


@router.post("/me/members", response_model=MemberOut)
def invite_member(
    payload: MemberInvite,
    user: AuthenticatedUser = Depends(require_roles("owner", "admin")),
) -> dict:
    return organization_service.invite_member(
        user.organization_id, payload.email, payload.role, user.id
    )


@router.patch("/me/members/{target_user_id}", response_model=MemberRoleOut)
def update_member_role(
    target_user_id: str,
    payload: MemberRoleUpdate,
    user: AuthenticatedUser = Depends(require_roles("owner", "admin")),
) -> dict:
    return organization_service.update_member_role(
        user.organization_id, target_user_id, payload.role, user.id
    )


@router.delete("/me/members/{target_user_id}", status_code=204)
def remove_member(
    target_user_id: str,
    user: AuthenticatedUser = Depends(require_roles("owner", "admin")),
) -> None:
    organization_service.remove_member(user.organization_id, target_user_id, user.id)
