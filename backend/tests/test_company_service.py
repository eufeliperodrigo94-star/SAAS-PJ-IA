import pytest

from app.services import company_service
from app.services.billing_service import CompanyLimitReachedError
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


def test_create_company_blocked_when_plan_limit_reached(monkeypatch):
    def fake_check_limit(org_id):
        raise CompanyLimitReachedError(10)

    monkeypatch.setattr("app.services.billing_service.check_company_limit", fake_check_limit)

    with pytest.raises(CompanyLimitReachedError):
        company_service.create_company("org-1", {"razao_social": "Acme LTDA"})


def test_create_company_succeeds_within_limit(monkeypatch):
    monkeypatch.setattr("app.services.billing_service.check_company_limit", lambda org_id: None)
    monkeypatch.setattr(
        "app.repositories.companies_repo.create_company",
        lambda org_id, data: {"id": "company-1", "razao_social": data["razao_social"]},
    )
    monkeypatch.setattr(
        "app.repositories.company_events_repo.create_event", lambda *a, **k: {"id": "event-1"}
    )

    company = company_service.create_company("org-1", {"razao_social": "Acme LTDA"})

    assert company["id"] == "company-1"
