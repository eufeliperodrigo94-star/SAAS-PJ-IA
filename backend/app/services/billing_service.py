from app.core.exceptions import DomainError
from app.repositories import billing_repo, companies_repo

DEFAULT_PLAN_CODE = "starter"


class PlanNotFoundError(DomainError):
    def __init__(self) -> None:
        super().__init__("Plano não encontrado.", status_code=404)


class CompanyLimitReachedError(DomainError):
    def __init__(self, max_companies: int) -> None:
        super().__init__(
            f"Limite de {max_companies} empresas do plano atual atingido. "
            "Troque de plano para cadastrar mais empresas.",
            status_code=403,
        )


def list_plans() -> list[dict]:
    return billing_repo.list_plans()


def ensure_default_subscription(organization_id: str) -> dict:
    existing = billing_repo.get_subscription(organization_id)
    if existing:
        return existing

    plan = billing_repo.get_plan_by_code(DEFAULT_PLAN_CODE)
    if plan is None:
        raise PlanNotFoundError()
    return billing_repo.create_subscription(organization_id, plan["id"], status="trialing")


def get_current_subscription(organization_id: str) -> dict | None:
    subscription = billing_repo.get_subscription(organization_id)
    if subscription is None:
        return None
    plan = billing_repo.get_plan(subscription["plan_id"])
    return {**subscription, "plan": plan}


def change_plan(organization_id: str, plan_code: str) -> dict:
    plan = billing_repo.get_plan_by_code(plan_code)
    if plan is None:
        raise PlanNotFoundError()

    subscription = billing_repo.get_subscription(organization_id) or ensure_default_subscription(
        organization_id
    )
    updated = billing_repo.update_subscription_plan(subscription["id"], plan["id"])
    return {**updated, "plan": plan}


def check_company_limit(organization_id: str) -> None:
    subscription = get_current_subscription(organization_id)
    max_companies = subscription["plan"]["max_companies"] if subscription else None
    if max_companies is None:
        return  # sem plano definido ou limite ilimitado (ex.: Enterprise).

    current_count = companies_repo.count_companies(organization_id)
    if current_count >= max_companies:
        raise CompanyLimitReachedError(max_companies)
