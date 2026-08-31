from app.core.supabase_client import get_supabase_admin


def list_processes(organization_id: str, company_id: str | None = None) -> list[dict]:
    query = (
        get_supabase_admin()
        .table("processes")
        .select("*")
        .eq("organization_id", organization_id)
    )
    if company_id:
        query = query.eq("company_id", company_id)
    result = query.order("created_at", desc=True).execute()
    return result.data


def get_process(organization_id: str, process_id: str) -> dict | None:
    result = (
        get_supabase_admin()
        .table("processes")
        .select("*")
        .eq("organization_id", organization_id)
        .eq("id", process_id)
        .limit(1)
        .execute()
    )
    return result.data[0] if result.data else None


def create_process(organization_id: str, created_by: str, data: dict) -> dict:
    payload = {**data, "organization_id": organization_id, "created_by": created_by}
    result = get_supabase_admin().table("processes").insert(payload).execute()
    return result.data[0]
