from fastapi import APIRouter, Depends

from app.core.security import AuthenticatedUser, require_organization
from app.services import dashboard_service

router = APIRouter(prefix="/dashboard", tags=["dashboard"])


@router.get("/summary")
def summary(user: AuthenticatedUser = Depends(require_organization)) -> dict:
    return dashboard_service.get_summary(user.organization_id)
