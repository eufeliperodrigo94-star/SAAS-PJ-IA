from app.memory.company_memory import get_company_memory


def _fake_company(organization_id: str, company_id: str):
    return {"id": company_id, "organization_id": organization_id, "razao_social": "Acme LTDA"}


def test_get_company_memory_aggregates_structured_data_and_history(monkeypatch):
    monkeypatch.setattr("app.repositories.companies_repo.get_company", _fake_company)
    monkeypatch.setattr(
        "app.repositories.companies_repo.list_partners",
        lambda org_id, company_id: [{"id": "p1", "nome": "Maria"}],
    )
    monkeypatch.setattr(
        "app.repositories.companies_repo.list_addresses",
        lambda org_id, company_id: [{"id": "a1", "tipo": "sede"}],
    )
    monkeypatch.setattr(
        "app.repositories.companies_repo.list_activities",
        lambda org_id, company_id: [{"id": "c1", "cnae_code": "0000-0/00"}],
    )
    monkeypatch.setattr(
        "app.repositories.company_events_repo.list_events",
        lambda org_id, company_id, limit=10: [{"id": "e1", "event_type": "company.created"}],
    )
    monkeypatch.setattr(
        "app.repositories.processes_repo.list_processes",
        lambda org_id, company_id=None: [
            {"id": "proc-1", "status": "rascunho"},
            {"id": "proc-2", "status": "protocolado"},
        ],
    )

    memory = get_company_memory("org-1", "company-1")

    assert memory["company"]["razao_social"] == "Acme LTDA"
    assert len(memory["partners"]) == 1
    assert len(memory["addresses"]) == 1
    assert len(memory["activities"]) == 1
    assert len(memory["recent_events"]) == 1
    # Só o processo "rascunho" está em aberto; "protocolado" não conta.
    assert memory["open_processes"] == 1
