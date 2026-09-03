from datetime import datetime, timezone

from app.core.supabase_client import get_supabase_admin


def create_ticket(organization_id: str, created_by: str | None, subject: str) -> dict:
    result = (
        get_supabase_admin()
        .table("support_tickets")
        .insert({"organization_id": organization_id, "created_by": created_by, "subject": subject})
        .execute()
    )
    return result.data[0]


def list_tickets(organization_id: str | None = None, status: str | None = None) -> list[dict]:
    query = get_supabase_admin().table("support_tickets").select("*, organizations(name)")
    if organization_id:
        query = query.eq("organization_id", organization_id)
    if status:
        query = query.eq("status", status)
    result = query.order("updated_at", desc=True).execute()
    return result.data


def get_ticket(ticket_id: str, organization_id: str | None = None) -> dict | None:
    query = get_supabase_admin().table("support_tickets").select("*, organizations(name)").eq("id", ticket_id)
    if organization_id:
        query = query.eq("organization_id", organization_id)
    result = query.limit(1).execute()
    return result.data[0] if result.data else None


def update_status(ticket_id: str, status: str) -> dict | None:
    result = (
        get_supabase_admin()
        .table("support_tickets")
        .update({"status": status})
        .eq("id", ticket_id)
        .execute()
    )
    return result.data[0] if result.data else None


def touch_ticket(ticket_id: str) -> None:
    get_supabase_admin().table("support_tickets").update(
        {"updated_at": datetime.now(timezone.utc).isoformat()}
    ).eq("id", ticket_id).execute()


def create_message(
    ticket_id: str, organization_id: str, author_id: str | None, author_is_admin: bool, body: str
) -> dict:
    result = (
        get_supabase_admin()
        .table("support_ticket_messages")
        .insert(
            {
                "ticket_id": ticket_id,
                "organization_id": organization_id,
                "author_id": author_id,
                "author_is_admin": author_is_admin,
                "body": body,
            }
        )
        .execute()
    )
    touch_ticket(ticket_id)
    return result.data[0]


def list_messages(ticket_id: str) -> list[dict]:
    result = (
        get_supabase_admin()
        .table("support_ticket_messages")
        .select("*")
        .eq("ticket_id", ticket_id)
        .order("created_at")
        .execute()
    )
    return result.data
