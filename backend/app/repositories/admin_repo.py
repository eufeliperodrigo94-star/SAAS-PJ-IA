from app.core.supabase_client import get_supabase_admin


def list_organizations() -> list[dict]:
    result = (
        get_supabase_admin()
        .table("organizations")
        .select("*")
        .order("created_at", desc=True)
        .execute()
    )
    return result.data


def get_organization(organization_id: str) -> dict | None:
    result = (
        get_supabase_admin()
        .table("organizations")
        .select("*")
        .eq("id", organization_id)
        .limit(1)
        .execute()
    )
    return result.data[0] if result.data else None


def count_users(organization_id: str) -> int:
    result = (
        get_supabase_admin()
        .table("organization_users")
        .select("id", count="exact")
        .eq("organization_id", organization_id)
        .execute()
    )
    return result.count or 0


def list_organization_users(organization_id: str) -> list[dict]:
    result = (
        get_supabase_admin()
        .table("organization_users")
        .select("id, role, created_at, users(id, email, full_name)")
        .eq("organization_id", organization_id)
        .order("created_at")
        .execute()
    )
    return result.data


def count_all(table: str) -> int:
    result = get_supabase_admin().table(table).select("id", count="exact").execute()
    return result.count or 0


def ai_usage_summary_since(since_iso: str) -> dict:
    rows = (
        get_supabase_admin()
        .table("ai_usage")
        .select("tokens_input, tokens_output, success")
        .gte("created_at", since_iso)
        .execute()
        .data
    )
    return {
        "calls": len(rows),
        "successful_calls": sum(1 for r in rows if r["success"]),
        "tokens_input": sum(r["tokens_input"] or 0 for r in rows),
        "tokens_output": sum(r["tokens_output"] or 0 for r in rows),
    }
