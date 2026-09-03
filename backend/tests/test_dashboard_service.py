from app.services import dashboard_service


def test_get_summary_aggregates_all_sources(monkeypatch):
    monkeypatch.setattr("app.repositories.companies_repo.count_companies", lambda org_id: 5)

    def fake_count_by_status(org_id, statuses):
        if statuses == dashboard_service.IN_PROGRESS_STATUSES:
            return 3
        if statuses == dashboard_service.PENDING_CORRECTION_STATUSES:
            return 1
        if statuses == dashboard_service.READY_STATUSES:
            return 2
        raise AssertionError(f"unexpected statuses {statuses}")

    monkeypatch.setattr("app.repositories.processes_repo.count_by_status", fake_count_by_status)

    def fake_count_by_result(org_id, result):
        return {"erro": 4, "atencao": 7}[result]

    monkeypatch.setattr("app.repositories.validations_repo.count_by_result", fake_count_by_result)
    monkeypatch.setattr(
        "app.repositories.ai_usage_repo.summary_since",
        lambda org_id, since: {"calls": 12, "successful_calls": 11, "tokens_input": 100, "tokens_output": 50},
    )
    monkeypatch.setattr(
        "app.services.billing_service.get_current_subscription",
        lambda org_id: {"plan": {"code": "starter", "name": "Starter"}},
    )

    summary = dashboard_service.get_summary("org-1")

    assert summary["total_companies"] == 5
    assert summary["processes_in_progress"] == 3
    assert summary["pending_issues"] == 1
    assert summary["ready_for_filing"] == 2
    assert summary["errors"] == 4
    assert summary["alerts"] == 7
    assert summary["ai_usage_last_30_days"]["calls"] == 12
    assert summary["current_plan"]["code"] == "starter"


def test_get_summary_handles_no_subscription(monkeypatch):
    monkeypatch.setattr("app.repositories.companies_repo.count_companies", lambda org_id: 0)
    monkeypatch.setattr("app.repositories.processes_repo.count_by_status", lambda org_id, s: 0)
    monkeypatch.setattr("app.repositories.validations_repo.count_by_result", lambda org_id, r: 0)
    monkeypatch.setattr(
        "app.repositories.ai_usage_repo.summary_since",
        lambda org_id, since: {"calls": 0, "successful_calls": 0, "tokens_input": 0, "tokens_output": 0},
    )
    monkeypatch.setattr(
        "app.services.billing_service.get_current_subscription", lambda org_id: None
    )

    summary = dashboard_service.get_summary("org-1")

    assert summary["current_plan"] is None
