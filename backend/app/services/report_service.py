"""Relatório de pré-validação (ver docs/PROJECT.md, seção Relatório).

Agrega o resultado já persistido da última execução do motor de regras —
não roda nenhuma regra nova nem chama IA. Deixa explícito, sempre, que é
uma pré-análise e não uma decisão do órgão oficial.
"""

from datetime import datetime, timezone

from app.repositories import companies_repo, documents_repo, rules_repo, validations_repo
from app.services.process_service import get_process_or_404

DISCLAIMER = (
    "Este relatório é uma pré-análise automatizada e não substitui a avaliação da Junta "
    "Comercial, da Receita Federal ou de qualquer órgão oficial. Ele não garante aprovação "
    "do processo — apenas identifica possíveis erros e inconsistências antes do protocolo."
)


def _report_item(validation: dict, rules_by_id: dict) -> dict:
    rule = rules_by_id.get(validation["rule_id"])
    return {
        "result": validation["result"],
        "message": validation["message"],
        "suggested_action": validation["suggested_action"],
        "evidence": validation["evidence"],
        "rule_codigo": rule["codigo"] if rule else None,
    }


def build_report(organization_id: str, process_id: str) -> dict:
    process = get_process_or_404(organization_id, process_id)
    company = companies_repo.get_company(organization_id, process["company_id"])
    validations = validations_repo.list_validations(organization_id, process_id)
    documents = documents_repo.list_documents(organization_id, process_id)

    rule_ids = [v["rule_id"] for v in validations if v["rule_id"]]
    rules_by_id = {r["id"]: r for r in rules_repo.get_rules_by_ids(rule_ids)}

    erros = [_report_item(v, rules_by_id) for v in validations if v["result"] == "erro"]
    alertas = [_report_item(v, rules_by_id) for v in validations if v["result"] == "atencao"]
    itens_ok = [_report_item(v, rules_by_id) for v in validations if v["result"] == "ok"]

    acoes = [item["suggested_action"] for item in erros + alertas if item["suggested_action"]]
    acoes_recomendadas = list(dict.fromkeys(acoes))  # remove duplicatas mantendo a ordem

    regras_aplicadas = [
        {"codigo": r["codigo"], "nome": r["nome"], "versao": r["versao"], "fonte": r["fonte"]}
        for r in rules_by_id.values()
    ]

    if not validations:
        resumo = "Pré-validação ainda não executada para este processo."
    else:
        resumo = (
            f"{len(erros)} erro(s), {len(alertas)} alerta(s) e {len(itens_ok)} item(ns) OK "
            f"na última pré-validação."
        )

    return {
        "process_id": process_id,
        "company_name": company["razao_social"] if company else "",
        "process_type": process["type"],
        "process_status": process["status"],
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "resumo": resumo,
        "erros": erros,
        "alertas": alertas,
        "itens_ok": itens_ok,
        "documentos_enviados": len(documents),
        "regras_aplicadas": regras_aplicadas,
        "acoes_recomendadas": acoes_recomendadas,
        "aviso": DISCLAIMER,
    }
