from app.core.supabase_client import get_supabase_admin


def create_event(
    organization_id: str,
    company_id: str,
    event_type: str,
    description: str,
    payload: dict | None = None,
    process_id: str | None = None,
    created_by: str | None = None,
) -> dict:
    record = {
        "organization_id": organization_id,
        "company_id": company_id,
        "process_id": process_id,
        "event_type": event_type,
        "description": description,
        "payload": payload or {},
        "created_by": created_by,
    }
    result = get_supabase_admin().table("company_events").insert(record).execute()
    return result.data[0]


def list_events(organization_id: str, company_id: str, limit: int = 50) -> list[dict]:
    result = (
        get_supabase_admin()
        .table("company_events")
        .select("*")
        .eq("organization_id", organization_id)
        .eq("company_id", company_id)
        .order("created_at", desc=True)
        .limit(limit)
        .execute()
    )
    return result.data
