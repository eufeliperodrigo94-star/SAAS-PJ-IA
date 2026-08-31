import pytest

from app.services import company_service
from app.services.company_service import CompanyNotFoundError


def test_get_company_or_404_raises_when_missing(monkeypatch):
    monkeypatch.setattr(
        "app.repositories.companies_repo.get_company", lambda org_id, company_id: None
    )

    with pytest.raises(CompanyNotFoundError):
        company_service.get_company_or_404("org-1", "missing-company")


def test_get_company_or_404_ignores_other_organizations(monkeypatch):
    # A empresa só é retornada quando organization_id bate — simula isolamento
    # multi-tenant: o repositório nunca deve devolver dados de outro escritório.
    def fake_get_company(organization_id: str, company_id: str):
        return {"id": company_id, "organization_id": organization_id} if organization_id == "org-1" else None

    monkeypatch.setattr("app.repositories.companies_repo.get_company", fake_get_company)

    company = company_service.get_company_or_404("org-1", "company-1")
    assert company["organization_id"] == "org-1"

    with pytest.raises(CompanyNotFoundError):
        company_service.get_company_or_404("org-2", "company-1")


def test_add_partner_requires_existing_company(monkeypatch):
    monkeypatch.setattr(
        "app.repositories.companies_repo.get_company", lambda org_id, company_id: None
    )

    with pytest.raises(CompanyNotFoundError):
        company_service.add_partner("org-1", "missing-company", {"nome": "Maria"})
