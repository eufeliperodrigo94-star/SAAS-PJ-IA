from app.core.exceptions import DomainError
from app.repositories import companies_repo, company_events_repo
from app.services import billing_service


class CompanyNotFoundError(DomainError):
    def __init__(self) -> None:
        super().__init__("Empresa não encontrada.", status_code=404)


def list_companies(organization_id: str) -> list[dict]:
    return companies_repo.list_companies(organization_id)


def get_company_or_404(organization_id: str, company_id: str) -> dict:
    company = companies_repo.get_company(organization_id, company_id)
    if not company:
        raise CompanyNotFoundError()
    return company


def create_company(organization_id: str, data: dict, created_by: str | None = None) -> dict:
    billing_service.check_company_limit(organization_id)
    company = companies_repo.create_company(organization_id, data)
    company_events_repo.create_event(
        organization_id,
        company["id"],
        event_type="company.created",
        description=f"Empresa {company['razao_social']} cadastrada.",
        payload={"razao_social": company["razao_social"], "cnpj": company.get("cnpj")},
        created_by=created_by,
    )
    return company


def update_company(
    organization_id: str, company_id: str, data: dict, created_by: str | None = None
) -> dict:
    get_company_or_404(organization_id, company_id)
    updated = companies_repo.update_company(organization_id, company_id, data)
    if not updated:
        raise CompanyNotFoundError()
    company_events_repo.create_event(
        organization_id,
        company_id,
        event_type="company.updated",
        description="Dados cadastrais da empresa atualizados.",
        payload={"changed_fields": list(data.keys())},
        created_by=created_by,
    )
    return updated


def add_partner(
    organization_id: str, company_id: str, data: dict, created_by: str | None = None
) -> dict:
    get_company_or_404(organization_id, company_id)
    partner = companies_repo.create_partner(organization_id, company_id, data)
    company_events_repo.create_event(
        organization_id,
        company_id,
        event_type="partner.added",
        description=f"Sócio {partner['nome']} incluído.",
        payload={"partner_id": partner["id"], "percentual_capital": partner.get("percentual_capital")},
        created_by=created_by,
    )
    return partner


def list_partners(organization_id: str, company_id: str) -> list[dict]:
    get_company_or_404(organization_id, company_id)
    return companies_repo.list_partners(organization_id, company_id)


def add_address(
    organization_id: str, company_id: str, data: dict, created_by: str | None = None
) -> dict:
    get_company_or_404(organization_id, company_id)
    address = companies_repo.create_address(organization_id, company_id, data)
    company_events_repo.create_event(
        organization_id,
        company_id,
        event_type="address.added",
        description=f"Endereço ({address['tipo']}) adicionado.",
        payload={"address_id": address["id"], "municipio": address.get("municipio"), "uf": address.get("uf")},
        created_by=created_by,
    )
    return address


def list_addresses(organization_id: str, company_id: str) -> list[dict]:
    get_company_or_404(organization_id, company_id)
    return companies_repo.list_addresses(organization_id, company_id)


def add_activity(
    organization_id: str, company_id: str, data: dict, created_by: str | None = None
) -> dict:
    get_company_or_404(organization_id, company_id)
    activity = companies_repo.create_activity(organization_id, company_id, data)
    company_events_repo.create_event(
        organization_id,
        company_id,
        event_type="activity.added",
        description=f"CNAE {activity['cnae_code']} adicionado.",
        payload={"activity_id": activity["id"], "is_primary": activity.get("is_primary")},
        created_by=created_by,
    )
    return activity


def list_activities(organization_id: str, company_id: str) -> list[dict]:
    get_company_or_404(organization_id, company_id)
    return companies_repo.list_activities(organization_id, company_id)


def list_timeline(organization_id: str, company_id: str) -> list[dict]:
    get_company_or_404(organization_id, company_id)
    return company_events_repo.list_events(organization_id, company_id)
