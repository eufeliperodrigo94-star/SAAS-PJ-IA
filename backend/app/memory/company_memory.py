"""Memória empresarial (camadas 1 e 3 — ver docs/ARCHITECTURE.md).

Agrega dados estruturados (empresa, sócios, endereços, CNAEs) e o histórico
recente de uma empresa para reutilização em novos processos, sem depender da
LLM para "lembrar" nada. Nada aqui chama IA: é puro acesso a dados.
"""

from app.repositories import companies_repo, company_events_repo, processes_repo
from app.services.company_service import get_company_or_404

CLOSED_STATUSES = {"protocolado", "arquivado"}
RECENT_EVENTS_LIMIT = 10


def get_company_memory(organization_id: str, company_id: str) -> dict:
    company = get_company_or_404(organization_id, company_id)
    partners = companies_repo.list_partners(organization_id, company_id)
    addresses = companies_repo.list_addresses(organization_id, company_id)
    activities = companies_repo.list_activities(organization_id, company_id)
    recent_events = company_events_repo.list_events(
        organization_id, company_id, limit=RECENT_EVENTS_LIMIT
    )
    processes = processes_repo.list_processes(organization_id, company_id)
    open_processes = sum(1 for p in processes if p["status"] not in CLOSED_STATUSES)

    return {
        "company": company,
        "partners": partners,
        "addresses": addresses,
        "activities": activities,
        "recent_events": recent_events,
        "open_processes": open_processes,
    }
