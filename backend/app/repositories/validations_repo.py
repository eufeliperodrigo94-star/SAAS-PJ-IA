from app.core.supabase_client import get_supabase_admin


def replace_validations(organization_id: str, process_id: str, results: list[dict]) -> list[dict]:
    admin = get_supabase_admin()
    # Cada execução de pré-validação substitui o resultado anterior do processo.
    admin.table("validations").delete().eq("organization_id", organization_id).eq(
        "process_id", process_id
    ).execute()

    if not results:
        return []

    records = [
        {
            "organization_id": organization_id,
            "process_id": process_id,
            "rule_id": r["rule_id"],
            "result": r["result"],
            "evidence": r["evidence"],
            "message": r["message"],
            "suggested_action": r["suggested_action"],
        }
        for r in results
    ]
    inserted = admin.table("validations").insert(records).execute()
    return inserted.data


def list_validations(organization_id: str, process_id: str) -> list[dict]:
    result = (
        get_supabase_admin()
        .table("validations")
        .select("*")
        .eq("organization_id", organization_id)
        .eq("process_id", process_id)
        .order("created_at")
        .execute()
    )
    return result.data


def count_by_result(organization_id: str, result_value: str) -> int:
    result = (
        get_supabase_admin()
        .table("validations")
        .select("id", count="exact")
        .eq("organization_id", organization_id)
        .eq("result", result_value)
        .execute()
    )
    return result.count or 0
