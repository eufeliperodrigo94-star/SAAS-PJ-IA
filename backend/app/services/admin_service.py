from datetime import datetime, timedelta, timezone

from app.core.exceptions import DomainError
from app.repositories import admin_repo, billing_repo, companies_repo, processes_repo
from app.services import billing_service, support_service


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


def get_sales_summary() -> dict:
    subscriptions = billing_repo.list_active_subscriptions_with_plans()

    by_plan: dict[str, dict] = {}
    mrr_cents = 0
    active_count = 0
    trialing_count = 0
    other_count = 0

    for sub in subscriptions:
        plan = sub.get("plans")
        status = sub["status"]
        if status == "active":
            active_count += 1
            if plan and plan.get("price_cents"):
                mrr_cents += plan["price_cents"]
        elif status == "trialing":
            trialing_count += 1
        else:
            other_count += 1

        if plan:
            entry = by_plan.setdefault(
                plan["code"], {"plan_code": plan["code"], "plan_name": plan["name"], "count": 0, "mrr_cents": 0}
            )
            entry["count"] += 1
            if status == "active" and plan.get("price_cents"):
                entry["mrr_cents"] += plan["price_cents"]

    total = active_count + trialing_count + other_count
    conversion_rate = (active_count / total) if total else 0.0

    return {
        "mrr_cents": mrr_cents,
        "active_subscriptions": active_count,
        "trialing_subscriptions": trialing_count,
        "other_subscriptions": other_count,
        "conversion_rate": round(conversion_rate, 4),
        "by_plan": sorted(by_plan.values(), key=lambda p: p["mrr_cents"], reverse=True),
    }


def list_all_tickets(status: str | None = None) -> list[dict]:
    return support_service.list_all_tickets(status=status)


def get_ticket_detail(ticket_id: str) -> dict:
    return support_service.get_ticket_with_messages(ticket_id)


def reply_ticket(ticket_id: str, admin_user_id: str, body: str) -> dict:
    return support_service.add_message(ticket_id, admin_user_id, body, is_admin=True)


def update_ticket_status(ticket_id: str, status: str) -> dict:
    return support_service.update_status(ticket_id, status)


def list_plans() -> list[dict]:
    return billing_service.list_plans(active_only=False)


def create_plan(data: dict) -> dict:
    return billing_service.create_plan(data)


def update_plan(plan_id: str, data: dict) -> dict:
    return billing_service.update_plan(plan_id, data)


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
