from app.core.exceptions import DomainError
from app.repositories import companies_repo


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


def create_company(organization_id: str, data: dict) -> dict:
    return companies_repo.create_company(organization_id, data)


def update_company(organization_id: str, company_id: str, data: dict) -> dict:
    get_company_or_404(organization_id, company_id)
    updated = companies_repo.update_company(organization_id, company_id, data)
    if not updated:
        raise CompanyNotFoundError()
    return updated


def add_partner(organization_id: str, company_id: str, data: dict) -> dict:
    get_company_or_404(organization_id, company_id)
    return companies_repo.create_partner(organization_id, company_id, data)


def list_partners(organization_id: str, company_id: str) -> list[dict]:
    get_company_or_404(organization_id, company_id)
    return companies_repo.list_partners(organization_id, company_id)


def add_address(organization_id: str, company_id: str, data: dict) -> dict:
    get_company_or_404(organization_id, company_id)
    return companies_repo.create_address(organization_id, company_id, data)


def list_addresses(organization_id: str, company_id: str) -> list[dict]:
    get_company_or_404(organization_id, company_id)
    return companies_repo.list_addresses(organization_id, company_id)


def add_activity(organization_id: str, company_id: str, data: dict) -> dict:
    get_company_or_404(organization_id, company_id)
    return companies_repo.create_activity(organization_id, company_id, data)


def list_activities(organization_id: str, company_id: str) -> list[dict]:
    get_company_or_404(organization_id, company_id)
    return companies_repo.list_activities(organization_id, company_id)
