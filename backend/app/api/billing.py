from fastapi import APIRouter, Depends

from app.core.security import AuthenticatedUser, require_organization, require_roles
from app.schemas.billing import ChangePlanRequest, PlanOut, SubscriptionOut
from app.services import billing_service

router = APIRouter(tags=["billing"])


@router.get("/plans", response_model=list[PlanOut])
def list_plans(user: AuthenticatedUser = Depends(require_organization)) -> list[dict]:
    return billing_service.list_plans()


@router.get("/subscriptions", response_model=SubscriptionOut | None)
def get_subscription(user: AuthenticatedUser = Depends(require_organization)) -> dict | None:
    return billing_service.get_current_subscription(user.organization_id)


@router.post("/subscriptions/change-plan", response_model=SubscriptionOut)
def change_plan(
    payload: ChangePlanRequest,
    user: AuthenticatedUser = Depends(require_roles("owner", "admin")),
) -> dict:
    return billing_service.change_plan(user.organization_id, payload.plan_code)
