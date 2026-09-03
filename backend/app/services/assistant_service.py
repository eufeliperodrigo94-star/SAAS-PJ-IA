"""Assistente IA: transforma linguagem natural em proposta estruturada.

Por design, NUNCA aplica a alteração sozinho — apenas devolve um JSON para o
usuário confirmar (ver docs/PROJECT.md, seção "Assistente"). Aplicar a
proposta continua passando pelos endpoints normais de empresas/processos.
"""

import json

from app.ai.router import get_ai_router
from app.core.exceptions import DomainError
from app.repositories import company_events_repo
from app.services.process_service import get_process_or_404

SCHEMAS_BY_PROCESS_TYPE = {
    "alteracao_qsa": (
        '{"acao": "incluir_socio"|"retirar_socio"|"alterar_percentual"|null, '
        '"socio_alvo": string|null, '
        '"novo_socio": {"nome": string, "percentual_capital": number|null}|null, '
        '"novo_percentual": number|null}'
    ),
    "alteracao_endereco": (
        '{"logradouro": string|null, "numero": string|null, "bairro": string|null, '
        '"municipio": string|null, "uf": string|null, "cep": string|null}'
    ),
    "alteracao_cnae": '{"cnae_code": string|null, "description": string|null, "is_primary": boolean|null}',
    "alteracao_capital": '{"novo_capital_social": number|null}',
}
DEFAULT_SCHEMA = '{"resumo": string, "campos_identificados": object}'


def interpret_message(organization_id: str, process_id: str, message: str, user_id: str | None) -> dict:
    process = get_process_or_404(organization_id, process_id)
    schema = SCHEMAS_BY_PROCESS_TYPE.get(process["type"], DEFAULT_SCHEMA)

    raw = get_ai_router().extract(
        task="assistant_interpret",
        text=message,
        schema_description=schema,
        organization_id=organization_id,
        process_id=process_id,
        user_id=user_id,
    )
    try:
        proposal = json.loads(raw)
    except json.JSONDecodeError as exc:
        raise DomainError("Não foi possível interpretar a resposta da IA como JSON.") from exc

    company_events_repo.create_event(
        organization_id,
        process["company_id"],
        event_type="assistant.proposal_generated",
        description="Assistente interpretou uma solicitação em linguagem natural (aguardando confirmação).",
        payload={"message": message, "proposal": proposal},
        process_id=process_id,
        created_by=user_id,
    )

    return {"process_id": process_id, "proposal": proposal, "requires_confirmation": True}
