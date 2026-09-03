from datetime import datetime, timedelta, timezone

from app.core.exceptions import DomainError
from app.repositories import admin_repo, companies_repo, processes_repo
from app.services import billing_service


class OrganizationNotFoundError(DomainError):
    def __init__(self) -> None:
        super().__init__("Organização não encontrada.", status_code=404)


def list_organizations() -> list[dict]:
    organizations = admin_repo.list_organizations()
    return [_with_summary(org) for org in organizations]


def get_organization_detail(organization_id: str) -> dict:
    organization = admin_repo.get_organization(organization_id)
    if organization is None:
        raise OrganizationNotFoundError()
    return {
        **_with_summary(organization),
        "users": admin_repo.list_organization_users(organization_id),
    }


def change_organization_plan(organization_id: str, plan_code: str) -> dict:
    if admin_repo.get_organization(organization_id) is None:
        raise OrganizationNotFoundError()
    return billing_service.change_plan(organization_id, plan_code)


def get_platform_metrics() -> dict:
    since = (datetime.now(timezone.utc) - timedelta(days=30)).isoformat()
    return {
        "total_organizations": admin_repo.count_all("organizations"),
        "total_companies": admin_repo.count_all("companies"),
        "total_processes": admin_repo.count_all("processes"),
        "ai_usage_last_30_days": admin_repo.ai_usage_summary_since(since),
    }


def _with_summary(organization: dict) -> dict:
    organization_id = organization["id"]
    subscription = billing_service.get_current_subscription(organization_id)
    return {
        **organization,
        "plan": subscription["plan"] if subscription else None,
        "user_count": admin_repo.count_users(organization_id),
        "company_count": companies_repo.count_companies(organization_id),
        "process_count": processes_repo.count_total(organization_id),
    }
