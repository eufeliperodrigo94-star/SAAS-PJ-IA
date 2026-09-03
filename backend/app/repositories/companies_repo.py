from app.core.supabase_client import get_supabase_admin


def list_companies(organization_id: str) -> list[dict]:
    result = (
        get_supabase_admin()
        .table("companies")
        .select("*")
        .eq("organization_id", organization_id)
        .order("razao_social")
        .execute()
    )
    return result.data


def get_company(organization_id: str, company_id: str) -> dict | None:
    result = (
        get_supabase_admin()
        .table("companies")
        .select("*")
        .eq("organization_id", organization_id)
        .eq("id", company_id)
        .limit(1)
        .execute()
    )
    return result.data[0] if result.data else None


def create_company(organization_id: str, data: dict) -> dict:
    payload = {**data, "organization_id": organization_id}
    result = get_supabase_admin().table("companies").insert(payload).execute()
    return result.data[0]


def update_company(organization_id: str, company_id: str, data: dict) -> dict | None:
    result = (
        get_supabase_admin()
        .table("companies")
        .update(data)
        .eq("organization_id", organization_id)
        .eq("id", company_id)
        .execute()
    )
    return result.data[0] if result.data else None


def list_partners(organization_id: str, company_id: str) -> list[dict]:
    result = (
        get_supabase_admin()
        .table("company_partners")
        .select("*")
        .eq("organization_id", organization_id)
        .eq("company_id", company_id)
        .order("nome")
        .execute()
    )
    return result.data


def create_partner(organization_id: str, company_id: str, data: dict) -> dict:
    payload = {**data, "organization_id": organization_id, "company_id": company_id}
    result = get_supabase_admin().table("company_partners").insert(payload).execute()
    return result.data[0]


def list_addresses(organization_id: str, company_id: str) -> list[dict]:
    result = (
        get_supabase_admin()
        .table("company_addresses")
        .select("*")
        .eq("organization_id", organization_id)
        .eq("company_id", company_id)
        .order("created_at")
        .execute()
    )
    return result.data


def create_address(organization_id: str, company_id: str, data: dict) -> dict:
    payload = {**data, "organization_id": organization_id, "company_id": company_id}
    result = get_supabase_admin().table("company_addresses").insert(payload).execute()
    return result.data[0]


def list_activities(organization_id: str, company_id: str) -> list[dict]:
    result = (
        get_supabase_admin()
        .table("company_activities")
        .select("*")
        .eq("organization_id", organization_id)
        .eq("company_id", company_id)
        .order("is_primary", desc=True)
        .execute()
    )
    return result.data


def create_activity(organization_id: str, company_id: str, data: dict) -> dict:
    payload = {**data, "organization_id": organization_id, "company_id": company_id}
    result = get_supabase_admin().table("company_activities").insert(payload).execute()
    return result.data[0]
