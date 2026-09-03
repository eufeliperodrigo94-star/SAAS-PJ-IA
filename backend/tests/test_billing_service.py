import pytest

from app.services import billing_service
from app.services.billing_service import CompanyLimitReachedError, PlanNotFoundError

STARTER_PLAN = {"id": "plan-starter", "code": "starter", "name": "Starter", "max_companies": 10, "price_cents": 9900}
ENTERPRISE_PLAN = {"id": "plan-ent", "code": "enterprise", "name": "Enterprise", "max_companies": None, "price_cents": None}


def test_ensure_default_subscription_creates_when_missing(monkeypatch):
    monkeypatch.setattr("app.repositories.billing_repo.get_subscription", lambda org_id: None)
    monkeypatch.setattr(
        "app.repositories.billing_repo.get_plan_by_code", lambda code: STARTER_PLAN
    )
    created = {}
    monkeypatch.setattr(
        "app.repositories.billing_repo.create_subscription",
        lambda org_id, plan_id, status="trialing": created.update(
            id="sub-1", organization_id=org_id, plan_id=plan_id, status=status
        )
        or created,
    )

    result = billing_service.ensure_default_subscription("org-1")

    assert result["plan_id"] == "plan-starter"
    assert result["status"] == "trialing"


def test_ensure_default_subscription_returns_existing(monkeypatch):
    existing = {"id": "sub-1", "organization_id": "org-1", "plan_id": "plan-starter"}
    monkeypatch.setattr("app.repositories.billing_repo.get_subscription", lambda org_id: existing)

    result = billing_service.ensure_default_subscription("org-1")

    assert result == existing


def test_ensure_default_subscription_raises_when_plan_missing(monkeypatch):
    monkeypatch.setattr("app.repositories.billing_repo.get_subscription", lambda org_id: None)
    monkeypatch.setattr("app.repositories.billing_repo.get_plan_by_code", lambda code: None)

    with pytest.raises(PlanNotFoundError):
        billing_service.ensure_default_subscription("org-1")


def test_get_current_subscription_merges_plan(monkeypatch):
    subscription = {"id": "sub-1", "organization_id": "org-1", "plan_id": "plan-starter"}
    monkeypatch.setattr(
        "app.repositories.billing_repo.get_subscription", lambda org_id: subscription
    )
    monkeypatch.setattr("app.repositories.billing_repo.get_plan", lambda plan_id: STARTER_PLAN)

    result = billing_service.get_current_subscription("org-1")

    assert result["plan"]["code"] == "starter"


def test_get_current_subscription_returns_none_without_subscription(monkeypatch):
    monkeypatch.setattr("app.repositories.billing_repo.get_subscription", lambda org_id: None)

    assert billing_service.get_current_subscription("org-1") is None


def test_change_plan_updates_subscription(monkeypatch):
    subscription = {"id": "sub-1", "organization_id": "org-1", "plan_id": "plan-starter"}
    monkeypatch.setattr(
        "app.repositories.billing_repo.get_plan_by_code", lambda code: ENTERPRISE_PLAN
    )
    monkeypatch.setattr(
        "app.repositories.billing_repo.get_subscription", lambda org_id: subscription
    )
    updated = {}
    monkeypatch.setattr(
        "app.repositories.billing_repo.update_subscription_plan",
        lambda sub_id, plan_id: updated.update(
            id=sub_id, organization_id="org-1", plan_id=plan_id
        )
        or updated,
    )

    result = billing_service.change_plan("org-1", "enterprise")

    assert result["plan"]["code"] == "enterprise"
    assert updated["plan_id"] == "plan-ent"


def test_change_plan_raises_for_unknown_plan(monkeypatch):
    monkeypatch.setattr("app.repositories.billing_repo.get_plan_by_code", lambda code: None)

    with pytest.raises(PlanNotFoundError):
        billing_service.change_plan("org-1", "nao-existe")


def test_check_company_limit_raises_when_reached(monkeypatch):
    subscription = {"id": "sub-1", "organization_id": "org-1", "plan_id": "plan-starter"}
    monkeypatch.setattr(
        "app.repositories.billing_repo.get_subscription", lambda org_id: subscription
    )
    monkeypatch.setattr("app.repositories.billing_repo.get_plan", lambda plan_id: STARTER_PLAN)
    monkeypatch.setattr("app.repositories.companies_repo.count_companies", lambda org_id: 10)

    with pytest.raises(CompanyLimitReachedError):
        billing_service.check_company_limit("org-1")


def test_check_company_limit_passes_under_limit(monkeypatch):
    subscription = {"id": "sub-1", "organization_id": "org-1", "plan_id": "plan-starter"}
    monkeypatch.setattr(
        "app.repositories.billing_repo.get_subscription", lambda org_id: subscription
    )
    monkeypatch.setattr("app.repositories.billing_repo.get_plan", lambda plan_id: STARTER_PLAN)
    monkeypatch.setattr("app.repositories.companies_repo.count_companies", lambda org_id: 3)

    billing_service.check_company_limit("org-1")  # não deve levantar


def test_check_company_limit_passes_when_unlimited(monkeypatch):
    subscription = {"id": "sub-1", "organization_id": "org-1", "plan_id": "plan-ent"}
    monkeypatch.setattr(
        "app.repositories.billing_repo.get_subscription", lambda org_id: subscription
    )
    monkeypatch.setattr("app.repositories.billing_repo.get_plan", lambda plan_id: ENTERPRISE_PLAN)
    monkeypatch.setattr(
        "app.repositories.companies_repo.count_companies", lambda org_id: 1000
    )

    billing_service.check_company_limit("org-1")  # não deve levantar
