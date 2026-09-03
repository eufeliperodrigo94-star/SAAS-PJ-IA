from app.core.exceptions import DomainError
from app.core.security import AuthenticatedUser
from app.core.supabase_client import get_supabase_admin
from app.services import billing_service


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
