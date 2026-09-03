from fastapi import APIRouter, Depends, Query

from app.core.security import AuthenticatedUser, require_super_admin
from app.schemas.admin import (
    AdminChangePlanRequest,
    OrganizationDetailOut,
    OrganizationSummaryOut,
    PlatformMetricsOut,
    SalesSummaryOut,
)
from app.schemas.billing import PlanCreate, PlanOut, PlanUpdate, SubscriptionOut
from app.schemas.support import MessageCreate, MessageOut, TicketDetailOut, TicketOut, TicketStatusUpdate
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


@router.get("/sales", response_model=SalesSummaryOut)
def get_sales(user: AuthenticatedUser = Depends(require_super_admin)) -> dict:
    return admin_service.get_sales_summary()


@router.get("/support/tickets", response_model=list[TicketOut])
def list_tickets(
    status: str | None = Query(default=None),
    user: AuthenticatedUser = Depends(require_super_admin),
) -> list[dict]:
    return admin_service.list_all_tickets(status=status)


@router.get("/support/tickets/{ticket_id}", response_model=TicketDetailOut)
def get_ticket(ticket_id: str, user: AuthenticatedUser = Depends(require_super_admin)) -> dict:
    return admin_service.get_ticket_detail(ticket_id)


@router.post("/support/tickets/{ticket_id}/messages", response_model=MessageOut)
def reply_ticket(
    ticket_id: str,
    payload: MessageCreate,
    user: AuthenticatedUser = Depends(require_super_admin),
) -> dict:
    return admin_service.reply_ticket(ticket_id, user.id, payload.body)


@router.patch("/support/tickets/{ticket_id}", response_model=TicketOut)
def update_ticket_status(
    ticket_id: str,
    payload: TicketStatusUpdate,
    user: AuthenticatedUser = Depends(require_super_admin),
) -> dict:
    return admin_service.update_ticket_status(ticket_id, payload.status)


@router.get("/plans", response_model=list[PlanOut])
def list_plans(user: AuthenticatedUser = Depends(require_super_admin)) -> list[dict]:
    return admin_service.list_plans()


@router.post("/plans", response_model=PlanOut)
def create_plan(payload: PlanCreate, user: AuthenticatedUser = Depends(require_super_admin)) -> dict:
    return admin_service.create_plan(payload.model_dump())


@router.patch("/plans/{plan_id}", response_model=PlanOut)
def update_plan(
    plan_id: str, payload: PlanUpdate, user: AuthenticatedUser = Depends(require_super_admin)
) -> dict:
    return admin_service.update_plan(plan_id, payload.model_dump())
