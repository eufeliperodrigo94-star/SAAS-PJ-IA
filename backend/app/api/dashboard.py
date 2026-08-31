from fastapi import APIRouter, Depends

from app.core.security import AuthenticatedUser, require_organization
from app.core.supabase_client import get_supabase_admin

router = APIRouter(prefix="/dashboard", tags=["dashboard"])


@router.get("/summary")
def summary(user: AuthenticatedUser = Depends(require_organization)) -> dict:
    admin = get_supabase_admin()
    org_id = user.organization_id

    companies = (
        admin.table("companies").select("id", count="exact").eq("organization_id", org_id).execute()
    )
    processes = (
        admin.table("processes").select("id", count="exact").eq("organization_id", org_id).execute()
    )

    return {
        "organization_id": org_id,
        "total_companies": companies.count or 0,
        "processes_in_progress": processes.count or 0,
        # Preenchido a partir do Dia 4 (motor de regras) e Dia 6 (dashboard completo).
        "pending_issues": 0,
        "errors": 0,
        "alerts": 0,
        "ready_for_filing": 0,
    }
