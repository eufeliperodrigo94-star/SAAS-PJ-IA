from app.rules.engine import evaluate_process

RULE_CNAE = {
    "id": "rule-cnae",
    "codigo": "PE-CNAE-001",
    "uf": "PE",
    "tipo_processo": None,
    "condicao": {"check": "company_has_activity"},
    "severidade": "erro",
    "mensagem": "A empresa não possui nenhum CNAE cadastrado.",
    "acao_sugerida": "Cadastre um CNAE.",
    "vigencia_inicio": None,
    "vigencia_fim": None,
}

RULE_QSA_OTHER_STATE = {**RULE_CNAE, "id": "rule-other", "codigo": "SP-X", "uf": "SP"}


def _patch_context(monkeypatch, *, company, partners=None, addresses=None, activities=None):
    monkeypatch.setattr("app.repositories.companies_repo.get_company", lambda org, cid: company)
    monkeypatch.setattr(
        "app.repositories.companies_repo.list_partners", lambda org, cid: partners or []
    )
    monkeypatch.setattr(
        "app.repositories.companies_repo.list_addresses", lambda org, cid: addresses or []
    )
    monkeypatch.setattr(
        "app.repositories.companies_repo.list_activities", lambda org, cid: activities or []
    )


def test_evaluate_process_flags_missing_cnae(monkeypatch):
    _patch_context(monkeypatch, company={"id": "c1", "uf": "PE"}, activities=[])
    monkeypatch.setattr("app.repositories.rules_repo.list_active_rules", lambda: [RULE_CNAE])

    process = {"id": "p1", "company_id": "c1", "type": "abertura"}
    results = evaluate_process("org-1", process)

    assert len(results) == 1
    assert results[0]["result"] == "erro"
    assert results[0]["rule_id"] == "rule-cnae"


def test_evaluate_process_passes_when_activity_present(monkeypatch):
    _patch_context(
        monkeypatch,
        company={"id": "c1", "uf": "PE"},
        activities=[{"cnae_code": "0000-0/00"}],
    )
    monkeypatch.setattr("app.repositories.rules_repo.list_active_rules", lambda: [RULE_CNAE])

    results = evaluate_process("org-1", {"id": "p1", "company_id": "c1", "type": "abertura"})

    assert results[0]["result"] == "ok"


def test_evaluate_process_ignores_rules_from_other_uf(monkeypatch):
    _patch_context(monkeypatch, company={"id": "c1", "uf": "PE"}, activities=[])
    monkeypatch.setattr(
        "app.repositories.rules_repo.list_active_rules", lambda: [RULE_QSA_OTHER_STATE]
    )

    results = evaluate_process("org-1", {"id": "p1", "company_id": "c1", "type": "abertura"})

    assert results == []
