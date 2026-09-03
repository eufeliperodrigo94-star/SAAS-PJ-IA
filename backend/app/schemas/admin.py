from pydantic import BaseModel, Field

from app.schemas.billing import PlanOut


class OrganizationSummaryOut(BaseModel):
    id: str
    name: str
    created_at: str
    plan: PlanOut | None
    user_count: int
    company_count: int
    process_count: int


class OrganizationUserOut(BaseModel):
    id: str
    role: str
    created_at: str
    users: dict | None = None


class OrganizationDetailOut(OrganizationSummaryOut):
    users: list[OrganizationUserOut]


class AdminChangePlanRequest(BaseModel):
    plan_code: str = Field(min_length=1)


class AiUsageSummaryOut(BaseModel):
    calls: int
    successful_calls: int
    tokens_input: int
    tokens_output: int


class PlatformMetricsOut(BaseModel):
    total_organizations: int
    total_companies: int
    total_processes: int
    ai_usage_last_30_days: AiUsageSummaryOut
