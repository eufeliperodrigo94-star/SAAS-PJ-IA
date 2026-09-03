"""Funções de verificação determinística usadas pelo motor de regras.

Cada check recebe o contexto (empresa, sócios, endereços, CNAEs, processo) e os
parâmetros da regra (vindos de `rules.condicao`, um jsonb) e devolve
`(passou, evidencia)`. Nunca chamam LLM — ver docs/RULES.md ("regra de ouro").
"""

from typing import Callable

CheckFn = Callable[[dict, dict], tuple[bool, dict]]


def company_has_activity(context: dict, params: dict) -> tuple[bool, dict]:
    activities = context["activities"]
    return bool(activities), {"total_cnaes": len(activities)}


def company_has_address(context: dict, params: dict) -> tuple[bool, dict]:
    addresses = context["addresses"]
    return bool(addresses), {"total_addresses": len(addresses)}


def company_has_partners(context: dict, params: dict) -> tuple[bool, dict]:
    partners = context["partners"]
    return bool(partners), {"total_partners": len(partners)}


def partners_percentual_sum(context: dict, params: dict) -> tuple[bool, dict]:
    tolerance = params.get("tolerance", 0.01)
    total = sum(p.get("percentual_capital") or 0 for p in context["partners"])
    passed = abs(total - 100) <= tolerance
    return passed, {"soma_percentual_capital": total}


def required_company_fields(context: dict, params: dict) -> tuple[bool, dict]:
    company = context["company"]
    missing = [field for field in params.get("fields", []) if not company.get(field)]
    return not missing, {"campos_ausentes": missing}


CHECKS: dict[str, CheckFn] = {
    "company_has_activity": company_has_activity,
    "company_has_address": company_has_address,
    "company_has_partners": company_has_partners,
    "partners_percentual_sum": partners_percentual_sum,
    "required_company_fields": required_company_fields,
}
