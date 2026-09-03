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


def at_most_one_primary_cnae(context: dict, params: dict) -> tuple[bool, dict]:
    """No Requerimento Eletrônico da JUCEPE só é possível marcar uma atividade
    como principal ("Pode-se escolher apenas uma atividade principal e várias
    atividades secundárias, sem limite" — Passo a Passo Constituição/JUCEPE)."""
    primary_count = sum(1 for a in context["activities"] if a.get("is_primary"))
    return primary_count <= 1, {"total_cnaes_principais": primary_count}


ADDRESS_REQUIRED_FIELDS = ["logradouro", "numero", "bairro", "municipio", "uf", "cep"]


def address_fields_complete(context: dict, params: dict) -> tuple[bool, dict]:
    """O DREI (Manual de Registro de Sociedade Limitada, Anexo IV da IN DREI
    nº 81/2020) exige o endereço completo — logradouro, número, bairro,
    município, UF e CEP — no ato de inscrição ou de alteração de endereço.
    Verifica o endereço do tipo informado (padrão "sede")."""
    tipo = params.get("tipo", "sede")
    addresses = [a for a in context["addresses"] if a.get("tipo") == tipo]
    if not addresses:
        return False, {"tipo": tipo, "motivo": "endereço não cadastrado"}

    address = addresses[0]
    missing = [field for field in ADDRESS_REQUIRED_FIELDS if not address.get(field)]
    return not missing, {"tipo": tipo, "campos_ausentes": missing}


def company_capital_minimum(context: dict, params: dict) -> tuple[bool, dict]:
    """Não há piso legal de capital social para LTDA no Brasil, mas a prática
    de mercado e a orientação do Redesim recomendam um capital compatível com
    o objeto social — na ausência de outro valor, R$ 1.000,00 é a referência
    usual. Por isso esta regra é sempre 'atencao', nunca 'erro'."""
    minimo = params.get("minimo", 1000)
    capital = context["company"].get("capital_social")
    passed = capital is not None and capital >= minimo
    return passed, {"capital_social": capital, "minimo_recomendado": minimo}


CHECKS: dict[str, CheckFn] = {
    "company_has_activity": company_has_activity,
    "company_has_address": company_has_address,
    "company_has_partners": company_has_partners,
    "partners_percentual_sum": partners_percentual_sum,
    "required_company_fields": required_company_fields,
    "address_fields_complete": address_fields_complete,
    "company_capital_minimum": company_capital_minimum,
    "at_most_one_primary_cnae": at_most_one_primary_cnae,
}
