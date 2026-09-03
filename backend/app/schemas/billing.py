from pydantic import BaseModel, Field


class PlanOut(BaseModel):
    id: str
    code: str
    name: str
    max_companies: int | None
    price_cents: int | None


class SubscriptionOut(BaseModel):
    id: str
    organization_id: str
    status: str
    plan: PlanOut
    current_period_start: str | None = None
    current_period_end: str | None = None


class ChangePlanRequest(BaseModel):
    plan_code: str = Field(min_length=1)
