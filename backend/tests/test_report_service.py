from app.services import report_service

RULE_CNAE = {"id": "rule-1", "codigo": "PE-CNAE-001", "nome": "Empresa sem CNAE", "versao": 1, "fonte": "Interna"}


def _patch_common(monkeypatch, validations, documents=None):
    monkeypatch.setattr(
        "app.services.report_service.get_process_or_404",
        lambda org_id, process_id: {
            "id": process_id,
            "company_id": "c1",
            "type": "abertura",
            "status": "pendente_correcao",
        },
    )
    monkeypatch.setattr(
        "app.repositories.companies_repo.get_company",
        lambda org_id, cid: {"id": cid, "razao_social": "Acme LTDA"},
    )
    monkeypatch.setattr(
        "app.repositories.validations_repo.list_validations", lambda org_id, pid: validations
    )
    monkeypatch.setattr(
        "app.repositories.documents_repo.list_documents", lambda org_id, pid: documents or []
    )
    monkeypatch.setattr(
        "app.repositories.rules_repo.get_rules_by_ids", lambda ids: [RULE_CNAE] if ids else []
    )


def test_build_report_splits_by_result(monkeypatch):
    validations = [
        {
            "rule_id": "rule-1",
            "result": "erro",
            "message": "A empresa não possui nenhum CNAE cadastrado.",
            "suggested_action": "Cadastre um CNAE.",
            "evidence": {},
        },
        {
            "rule_id": None,
            "result": "ok",
            "message": "Regra atendida.",
            "suggested_action": None,
            "evidence": {},
        },
    ]
    _patch_common(monkeypatch, validations)

    report = report_service.build_report("org-1", "p1")

    assert report["company_name"] == "Acme LTDA"
    assert len(report["erros"]) == 1
    assert len(report["itens_ok"]) == 1
    assert report["erros"][0]["rule_codigo"] == "PE-CNAE-001"
    assert "Cadastre um CNAE." in report["acoes_recomendadas"]
    assert report["regras_aplicadas"][0]["codigo"] == "PE-CNAE-001"
    assert "pré-análise" in report["aviso"]


def test_build_report_without_validations(monkeypatch):
    _patch_common(monkeypatch, [])

    report = report_service.build_report("org-1", "p1")

    assert report["resumo"] == "Pré-validação ainda não executada para este processo."
    assert report["erros"] == []
    assert report["regras_aplicadas"] == []


def test_build_report_deduplicates_recommended_actions(monkeypatch):
    validations = [
        {"rule_id": "rule-1", "result": "erro", "message": "m1", "suggested_action": "Ação X", "evidence": {}},
        {"rule_id": "rule-1", "result": "atencao", "message": "m2", "suggested_action": "Ação X", "evidence": {}},
    ]
    _patch_common(monkeypatch, validations)

    report = report_service.build_report("org-1", "p1")

    assert report["acoes_recomendadas"] == ["Ação X"]
