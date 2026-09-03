import pytest

from app.services import admin_service, billing_service


def test_get_sales_summary_computes_mrr_and_conversion(monkeypatch):
    monkeypatch.setattr(
        "app.repositories.billing_repo.list_active_subscriptions_with_plans",
        lambda: [
            {"status": "active", "plans": {"code": "starter", "name": "Starter", "price_cents": 9900}},
            {"status": "active", "plans": {"code": "starter", "name": "Starter", "price_cents": 9900}},
            {"status": "trialing", "plans": {"code": "pro", "name": "Profissional", "price_cents": 19900}},
            {"status": "canceled", "plans": {"code": "starter", "name": "Starter", "price_cents": 9900}},
        ],
    )

    summary = admin_service.get_sales_summary()

    assert summary["mrr_cents"] == 19800
    assert summary["active_subscriptions"] == 2
    assert summary["trialing_subscriptions"] == 1
    assert summary["other_subscriptions"] == 1
    assert summary["conversion_rate"] == 0.5
    starter_entry = next(p for p in summary["by_plan"] if p["plan_code"] == "starter")
    assert starter_entry["count"] == 3
    assert starter_entry["mrr_cents"] == 19800


def test_get_sales_summary_handles_no_subscriptions(monkeypatch):
    monkeypatch.setattr("app.repositories.billing_repo.list_active_subscriptions_with_plans", lambda: [])

    summary = admin_service.get_sales_summary()

    assert summary["mrr_cents"] == 0
    assert summary["conversion_rate"] == 0.0
    assert summary["by_plan"] == []


def test_create_plan_rejects_duplicate_code(monkeypatch):
    monkeypatch.setattr(
        "app.repositories.billing_repo.get_plan_by_code", lambda code: {"id": "plan-1", "code": code}
    )

    with pytest.raises(billing_service.PlanCodeAlreadyExistsError):
        billing_service.create_plan({"code": "starter", "name": "Starter"})


def test_create_plan_succeeds_for_new_code(monkeypatch):
    monkeypatch.setattr("app.repositories.billing_repo.get_plan_by_code", lambda code: None)
    monkeypatch.setattr(
        "app.repositories.billing_repo.create_plan", lambda data: {"id": "plan-new", **data}
    )

    plan = billing_service.create_plan({"code": "enterprise", "name": "Enterprise"})
    assert plan["id"] == "plan-new"


def test_update_plan_raises_when_missing(monkeypatch):
    monkeypatch.setattr("app.repositories.billing_repo.get_plan", lambda plan_id: None)

    with pytest.raises(billing_service.PlanNotFoundError):
        billing_service.update_plan("missing", {"active": False})


def test_update_plan_filters_none_values(monkeypatch):
    monkeypatch.setattr("app.repositories.billing_repo.get_plan", lambda plan_id: {"id": plan_id})
    captured = {}

    def fake_update(plan_id, data):
        captured["data"] = data
        return {"id": plan_id, **data}

    monkeypatch.setattr("app.repositories.billing_repo.update_plan", fake_update)

    billing_service.update_plan("plan-1", {"name": None, "active": False, "price_cents": None})

    assert captured["data"] == {"active": False}
