from app.services import validation_service


def _patch_common(monkeypatch, *, results, saved):
    monkeypatch.setattr(
        "app.services.validation_service.get_process_or_404",
        lambda org_id, process_id: {"id": process_id, "company_id": "c1", "type": "abertura"},
    )
    monkeypatch.setattr("app.rules.engine.evaluate_process", lambda org_id, process: results)
    monkeypatch.setattr(
        "app.services.validation_service.evaluate_process", lambda org_id, process: results
    )
    monkeypatch.setattr(
        "app.repositories.validations_repo.replace_validations",
        lambda org_id, process_id, r: saved,
    )
    monkeypatch.setattr(
        "app.repositories.company_events_repo.create_event", lambda *a, **k: {"id": "event-1"}
    )

    updated = {}

    def fake_update_status(org_id, process_id, status):
        updated["status"] = status
        return {"id": process_id, "status": status}

    monkeypatch.setattr("app.repositories.processes_repo.update_status", fake_update_status)
    return updated


def test_run_validation_marks_pendente_correcao_on_error(monkeypatch):
    results = [{"result": "erro"}, {"result": "ok"}]
    updated = _patch_common(monkeypatch, results=results, saved=results)

    outcome = validation_service.run_validation("org-1", "p1", "user-1")

    assert updated["status"] == "pendente_correcao"
    assert outcome["process"]["status"] == "pendente_correcao"


def test_run_validation_marks_pronto_when_no_errors(monkeypatch):
    results = [{"result": "ok"}, {"result": "atencao"}]
    updated = _patch_common(monkeypatch, results=results, saved=results)

    validation_service.run_validation("org-1", "p1", "user-1")

    assert updated["status"] == "pronto_para_protocolo"


def test_run_validation_keeps_em_validacao_when_no_rules_apply(monkeypatch):
    updated = _patch_common(monkeypatch, results=[], saved=[])

    validation_service.run_validation("org-1", "p1", "user-1")

    assert updated["status"] == "em_validacao"
