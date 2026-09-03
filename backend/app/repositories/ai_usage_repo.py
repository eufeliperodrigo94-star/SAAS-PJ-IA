from app.core.supabase_client import get_supabase_admin


def record_usage(
    organization_id: str,
    task: str,
    provider: str,
    model: str,
    *,
    tokens_input: int | None = None,
    tokens_output: int | None = None,
    latency_ms: int | None = None,
    success: bool = True,
    error_message: str | None = None,
    process_id: str | None = None,
    user_id: str | None = None,
) -> dict:
    record = {
        "organization_id": organization_id,
        "process_id": process_id,
        "user_id": user_id,
        "task": task,
        "provider": provider,
        "model": model,
        "tokens_input": tokens_input,
        "tokens_output": tokens_output,
        "latency_ms": latency_ms,
        "success": success,
        "error_message": error_message,
    }
    result = get_supabase_admin().table("ai_usage").insert(record).execute()
    return result.data[0]


def summary_since(organization_id: str, since_iso: str) -> dict:
    rows = (
        get_supabase_admin()
        .table("ai_usage")
        .select("tokens_input, tokens_output, success")
        .eq("organization_id", organization_id)
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
