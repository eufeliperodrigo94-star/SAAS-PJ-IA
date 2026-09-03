from pydantic import BaseModel, Field


class PlanOut(BaseModel):
    id: str
    code: str
    name: str
    max_companies: int | None
    price_cents: int | None
    active: bool = True


class PlanCreate(BaseModel):
    code: str = Field(min_length=2, max_length=50)
    name: str = Field(min_length=2, max_length=100)
    max_companies: int | None = None
    price_cents: int | None = None


class PlanUpdate(BaseModel):
    name: str | None = None
    max_companies: int | None = None
    price_cents: int | None = None
    active: bool | None = None


class SubscriptionOut(BaseModel):
    id: str
    organization_id: str
    status: str
    plan: PlanOut
    current_period_start: str | None = None
    current_period_end: str | None = None


class ChangePlanRequest(BaseModel):
    plan_code: str = Field(min_length=1)
