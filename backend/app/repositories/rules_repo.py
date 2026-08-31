from app.core.supabase_client import get_supabase_admin


def list_active_rules() -> list[dict]:
    """Todas as regras ativas. O motor filtra por UF/tipo de processo em memória —
    o catálogo é pequeno no MVP e isso evita queries OR complexas no Supabase."""
    result = get_supabase_admin().table("rules").select("*").eq("ativo", True).execute()
    return result.data
