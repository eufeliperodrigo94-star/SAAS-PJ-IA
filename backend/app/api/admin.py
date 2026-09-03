from fastapi import APIRouter, Depends

from app.core.security import AuthenticatedUser, require_super_admin
from app.schemas.admin import (
    AdminChangePlanRequest,
    OrganizationDetailOut,
    OrganizationSummaryOut,
    PlatformMetricsOut,
)
from app.schemas.billing import SubscriptionOut
from app.services import admin_service

router = APIRouter(prefix="/admin", tags=["admin"])


@router.get("/organizations", response_model=list[OrganizationSummaryOut])
def list_organizations(user: AuthenticatedUser = Depends(require_super_admin)) -> list[dict]:
    return admin_service.list_organizations()


@router.get("/organizations/{organization_id}", response_model=OrganizationDetailOut)
def get_organization(
    organization_id: str, user: AuthenticatedUser = Depends(require_super_admin)
) -> dict:
    return admin_service.get_organization_detail(organization_id)


@router.post("/organizations/{organization_id}/change-plan", response_model=SubscriptionOut)
def change_organization_plan(
    organization_id: str,
    payload: AdminChangePlanRequest,
    user: AuthenticatedUser = Depends(require_super_admin),
) -> dict:
    return admin_service.change_organization_plan(organization_id, payload.plan_code)


@router.get("/metrics", response_model=PlatformMetricsOut)
def get_metrics(user: AuthenticatedUser = Depends(require_super_admin)) -> dict:
    return admin_service.get_platform_metrics()
