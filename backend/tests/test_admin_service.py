import pytest

from app.services import admin_service


def test_list_organizations_enriches_with_plan_and_counts(monkeypatch):
    monkeypatch.setattr(
        "app.repositories.admin_repo.list_organizations",
        lambda: [{"id": "org-1", "name": "Escritório A", "created_at": "2026-01-01T00:00:00Z"}],
    )
    monkeypatch.setattr(
        "app.services.billing_service.get_current_subscription",
        lambda org_id: {"plan": {"code": "starter", "name": "Starter"}},
    )
    monkeypatch.setattr("app.repositories.admin_repo.count_users", lambda org_id: 2)
    monkeypatch.setattr("app.repositories.companies_repo.count_companies", lambda org_id: 3)
    monkeypatch.setattr("app.repositories.processes_repo.count_total", lambda org_id: 4)

    result = admin_service.list_organizations()

    assert result == [
        {
            "id": "org-1",
            "name": "Escritório A",
            "created_at": "2026-01-01T00:00:00Z",
            "plan": {"code": "starter", "name": "Starter"},
            "user_count": 2,
            "company_count": 3,
            "process_count": 4,
        }
    ]


def test_get_organization_detail_raises_when_missing(monkeypatch):
    monkeypatch.setattr("app.repositories.admin_repo.get_organization", lambda org_id: None)

    with pytest.raises(admin_service.OrganizationNotFoundError):
        admin_service.get_organization_detail("org-missing")


def test_get_organization_detail_includes_users(monkeypatch):
    monkeypatch.setattr(
        "app.repositories.admin_repo.get_organization",
        lambda org_id: {"id": org_id, "name": "Escritório A", "created_at": "2026-01-01T00:00:00Z"},
    )
    monkeypatch.setattr(
        "app.services.billing_service.get_current_subscription", lambda org_id: None
    )
    monkeypatch.setattr("app.repositories.admin_repo.count_users", lambda org_id: 1)
    monkeypatch.setattr("app.repositories.companies_repo.count_companies", lambda org_id: 0)
    monkeypatch.setattr("app.repositories.processes_repo.count_total", lambda org_id: 0)
    monkeypatch.setattr(
        "app.repositories.admin_repo.list_organization_users",
        lambda org_id: [{"id": "ou-1", "role": "owner", "users": {"email": "a@b.com"}}],
    )

    detail = admin_service.get_organization_detail("org-1")

    assert detail["plan"] is None
    assert detail["users"][0]["role"] == "owner"


def test_change_organization_plan_raises_when_missing(monkeypatch):
    monkeypatch.setattr("app.repositories.admin_repo.get_organization", lambda org_id: None)

    with pytest.raises(admin_service.OrganizationNotFoundError):
        admin_service.change_organization_plan("org-missing", "pro")


def test_change_organization_plan_delegates_to_billing_service(monkeypatch):
    monkeypatch.setattr(
        "app.repositories.admin_repo.get_organization", lambda org_id: {"id": org_id}
    )
    monkeypatch.setattr(
        "app.services.billing_service.change_plan",
        lambda org_id, plan_code: {"organization_id": org_id, "plan_code": plan_code},
    )

    result = admin_service.change_organization_plan("org-1", "pro")

    assert result == {"organization_id": "org-1", "plan_code": "pro"}


def test_get_platform_metrics_aggregates_counts(monkeypatch):
    monkeypatch.setattr(
        "app.repositories.admin_repo.count_all",
        lambda table: {"organizations": 10, "companies": 40, "processes": 90}[table],
    )
    monkeypatch.setattr(
        "app.repositories.admin_repo.ai_usage_summary_since",
        lambda since: {"calls": 5, "successful_calls": 5, "tokens_input": 100, "tokens_output": 20},
    )

    metrics = admin_service.get_platform_metrics()

    assert metrics["total_organizations"] == 10
    assert metrics["total_companies"] == 40
    assert metrics["total_processes"] == 90
    assert metrics["ai_usage_last_30_days"]["calls"] == 5
