from app.core.supabase_client import get_supabase_admin


def get_organization(organization_id: str) -> dict | None:
    result = (
        get_supabase_admin()
        .table("organizations")
        .select("id, name, created_at")
        .eq("id", organization_id)
        .limit(1)
        .execute()
    )
    return result.data[0] if result.data else None


def update_organization_name(organization_id: str, name: str) -> dict:
    result = (
        get_supabase_admin()
        .table("organizations")
        .update({"name": name})
        .eq("id", organization_id)
        .execute()
    )
    return result.data[0]


def list_members(organization_id: str) -> list[dict]:
    result = (
        get_supabase_admin()
        .table("organization_users")
        .select("user_id, role, created_at, users(id, email, full_name)")
        .eq("organization_id", organization_id)
        .order("created_at")
        .execute()
    )
    return result.data


def count_owners(organization_id: str) -> int:
    result = (
        get_supabase_admin()
        .table("organization_users")
        .select("id", count="exact")
        .eq("organization_id", organization_id)
        .eq("role", "owner")
        .execute()
    )
    return result.count or 0


def get_membership(organization_id: str, user_id: str) -> dict | None:
    result = (
        get_supabase_admin()
        .table("organization_users")
        .select("user_id, role")
        .eq("organization_id", organization_id)
        .eq("user_id", user_id)
        .limit(1)
        .execute()
    )
    return result.data[0] if result.data else None


def insert_membership(organization_id: str, user_id: str, role: str) -> dict:
    result = (
        get_supabase_admin()
        .table("organization_users")
        .insert({"organization_id": organization_id, "user_id": user_id, "role": role})
        .execute()
    )
    return result.data[0]


def update_membership_role(organization_id: str, user_id: str, role: str) -> dict:
    result = (
        get_supabase_admin()
        .table("organization_users")
        .update({"role": role})
        .eq("organization_id", organization_id)
        .eq("user_id", user_id)
        .execute()
    )
    return result.data[0]


def delete_membership(organization_id: str, user_id: str) -> None:
    get_supabase_admin().table("organization_users").delete().eq(
        "organization_id", organization_id
    ).eq("user_id", user_id).execute()


def upsert_user_profile(user_id: str, email: str | None, full_name: str | None) -> dict:
    result = (
        get_supabase_admin()
        .table("users")
        .upsert({"id": user_id, "email": email, "full_name": full_name})
        .execute()
    )
    return result.data[0]


def insert_audit_log(
    organization_id: str, user_id: str, action: str, entity_type: str, entity_id: str
) -> None:
    get_supabase_admin().table("audit_logs").insert(
        {
            "organization_id": organization_id,
            "user_id": user_id,
            "action": action,
            "entity_type": entity_type,
            "entity_id": entity_id,
        }
    ).execute()
