from app.core.exceptions import DomainError
from app.core.security import AuthenticatedUser
from app.core.supabase_client import get_supabase_admin
from app.repositories import organization_repo
from app.services import billing_service

ORGANIZATION_ROLES = ("owner", "admin", "operator", "viewer")


class OrganizationNotFoundError(DomainError):
    def __init__(self) -> None:
        super().__init__("Organização não encontrada.", status_code=404)


class MemberNotFoundError(DomainError):
    def __init__(self) -> None:
        super().__init__("Membro não encontrado nesta organização.", status_code=404)


class LastOwnerError(DomainError):
    def __init__(self) -> None:
        super().__init__(
            "A organização precisa ter ao menos um owner — promova outro membro antes."
        )


def register_organization(user: AuthenticatedUser, organization_name: str, full_name: str | None) -> dict:
    if user.organization_id:
        raise DomainError("Usuário já pertence a uma organização.")

    admin = get_supabase_admin()

    admin.table("users").upsert(
        {"id": user.id, "email": user.email, "full_name": full_name}
    ).execute()

    org = (
        admin.table("organizations")
        .insert({"name": organization_name})
        .execute()
    )
    organization = org.data[0]

    admin.table("organization_users").insert(
        {"organization_id": organization["id"], "user_id": user.id, "role": "owner"}
    ).execute()

    admin.table("audit_logs").insert(
        {
            "organization_id": organization["id"],
            "user_id": user.id,
            "action": "organization.created",
            "entity_type": "organization",
            "entity_id": organization["id"],
        }
    ).execute()

    billing_service.ensure_default_subscription(organization["id"])

    return {"id": organization["id"], "name": organization["name"], "role": "owner"}


def get_my_organization(organization_id: str) -> dict:
    organization = organization_repo.get_organization(organization_id)
    if organization is None:
        raise OrganizationNotFoundError()
    return organization


def rename_organization(organization_id: str, name: str, actor_user_id: str) -> dict:
    organization = organization_repo.update_organization_name(organization_id, name)
    organization_repo.insert_audit_log(
        organization_id, actor_user_id, "organization.renamed", "organization", organization_id
    )
    return organization


def update_my_profile(user: AuthenticatedUser, full_name: str) -> dict:
    return organization_repo.upsert_user_profile(user.id, user.email, full_name)


def list_members(organization_id: str) -> list[dict]:
    return organization_repo.list_members(organization_id)


def invite_member(organization_id: str, email: str, role: str, actor_user_id: str) -> dict:
    admin = get_supabase_admin()
    try:
        response = admin.auth.admin.invite_user_by_email(email)
    except Exception as exc:  # a API do GoTrue não expõe um tipo de exceção dedicado aqui
        raise DomainError(
            "Não foi possível convidar este e-mail — verifique se ele já não está cadastrado."
        ) from exc

    invited_user = response.user
    organization_repo.upsert_user_profile(invited_user.id, email, None)

    membership = organization_repo.insert_membership(organization_id, invited_user.id, role)
    organization_repo.insert_audit_log(
        organization_id, actor_user_id, "member.invited", "user", invited_user.id
    )
    return {
        "user_id": invited_user.id,
        "role": membership["role"],
        "created_at": membership["created_at"],
        "users": {"id": invited_user.id, "email": email, "full_name": None},
    }


def update_member_role(organization_id: str, target_user_id: str, role: str, actor_user_id: str) -> dict:
    membership = organization_repo.get_membership(organization_id, target_user_id)
    if membership is None:
        raise MemberNotFoundError()

    if membership["role"] == "owner" and role != "owner":
        if organization_repo.count_owners(organization_id) <= 1:
            raise LastOwnerError()

    updated = organization_repo.update_membership_role(organization_id, target_user_id, role)
    organization_repo.insert_audit_log(
        organization_id, actor_user_id, "member.role_updated", "user", target_user_id
    )
    return updated


def remove_member(organization_id: str, target_user_id: str, actor_user_id: str) -> None:
    membership = organization_repo.get_membership(organization_id, target_user_id)
    if membership is None:
        raise MemberNotFoundError()

    if membership["role"] == "owner" and organization_repo.count_owners(organization_id) <= 1:
        raise LastOwnerError()

    organization_repo.delete_membership(organization_id, target_user_id)
    organization_repo.insert_audit_log(
        organization_id, actor_user_id, "member.removed", "user", target_user_id
    )
