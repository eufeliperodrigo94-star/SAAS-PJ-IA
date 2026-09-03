from app.core.supabase_client import get_supabase_admin


def list_plans() -> list[dict]:
    result = get_supabase_admin().table("plans").select("*").order("price_cents").execute()
    return result.data


def get_plan_by_code(code: str) -> dict | None:
    result = get_supabase_admin().table("plans").select("*").eq("code", code).limit(1).execute()
    return result.data[0] if result.data else None


def get_plan(plan_id: str) -> dict | None:
    result = get_supabase_admin().table("plans").select("*").eq("id", plan_id).limit(1).execute()
    return result.data[0] if result.data else None


def get_subscription(organization_id: str) -> dict | None:
    result = (
        get_supabase_admin()
        .table("subscriptions")
        .select("*")
        .eq("organization_id", organization_id)
        .limit(1)
        .execute()
    )
    return result.data[0] if result.data else None


def create_subscription(organization_id: str, plan_id: str, status: str = "trialing") -> dict:
    result = (
        get_supabase_admin()
        .table("subscriptions")
        .insert({"organization_id": organization_id, "plan_id": plan_id, "status": status})
        .execute()
    )
    return result.data[0]


def update_subscription_plan(subscription_id: str, plan_id: str) -> dict:
    result = (
        get_supabase_admin()
        .table("subscriptions")
        .update({"plan_id": plan_id})
        .eq("id", subscription_id)
        .execute()
    )
    return result.data[0]
