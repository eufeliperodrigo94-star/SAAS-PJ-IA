"""Motor de regras determinístico (ver docs/RULES.md).

Nunca chama LLM: se uma regra pode ser avaliada deterministicamente contra os
dados estruturados da empresa/processo, o resultado sai daqui. Regras são
dados versionados em `rules`, não lógica espalhada pelo código — este módulo
só sabe *como* despachar um `condicao.check` para a função correspondente em
`app/rules/checks.py`.
"""

from datetime import date

from app.repositories import companies_repo, rules_repo
from app.rules.checks import CHECKS


def _rule_applies(rule: dict, uf: str | None, tipo_processo: str, today: date) -> bool:
    if rule["uf"] and rule["uf"] != uf:
        return False
    if rule["tipo_processo"] and rule["tipo_processo"] != tipo_processo:
        return False
    if rule.get("vigencia_inicio") and date.fromisoformat(rule["vigencia_inicio"]) > today:
        return False
    if rule.get("vigencia_fim") and date.fromisoformat(rule["vigencia_fim"]) < today:
        return False
    return True


def build_context(organization_id: str, company_id: str, process: dict) -> dict:
    return {
        "company": companies_repo.get_company(organization_id, company_id),
        "partners": companies_repo.list_partners(organization_id, company_id),
        "addresses": companies_repo.list_addresses(organization_id, company_id),
        "activities": companies_repo.list_activities(organization_id, company_id),
        "process": process,
    }


def evaluate_process(organization_id: str, process: dict) -> list[dict]:
    """Avalia todas as regras ativas aplicáveis ao processo. Não persiste nada —
    ver app/services/validation_service.py para a persistência em `validations`."""
    context = build_context(organization_id, process["company_id"], process)
    company_uf = context["company"]["uf"] if context["company"] else None
    today = date.today()

    results = []
    for rule in rules_repo.list_active_rules():
        if not _rule_applies(rule, company_uf, process["type"], today):
            continue

        check = CHECKS.get(rule["condicao"].get("check"))
        if check is None:
            # Regra cadastrada sem check implementado — não inventamos comportamento;
            # ela fica marcada como "não configurada" (ver docs/RULES.md).
            results.append(
                {
                    "rule_id": rule["id"],
                    "result": "atencao",
                    "message": f"Regra '{rule['codigo']}' não configurada (check desconhecido).",
                    "suggested_action": None,
                    "evidence": {"condicao": rule["condicao"]},
                }
            )
            continue

        passed, evidence = check(context, rule["condicao"])
        results.append(
            {
                "rule_id": rule["id"],
                "result": "ok" if passed else rule["severidade"],
                "message": "Regra atendida." if passed else rule["mensagem"],
                "suggested_action": None if passed else rule.get("acao_sugerida"),
                "evidence": evidence,
            }
        )

    return results
