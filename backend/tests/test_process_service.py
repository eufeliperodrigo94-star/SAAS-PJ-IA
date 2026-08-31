import pytest

from app.services import process_service
from app.services.company_service import CompanyNotFoundError


def test_create_process_requires_company_in_same_organization(monkeypatch):
    monkeypatch.setattr(
        "app.repositories.companies_repo.get_company", lambda org_id, company_id: None
    )

    with pytest.raises(CompanyNotFoundError):
        process_service.create_process(
            "org-1", "user-1", {"company_id": "company-x", "type": "abertura", "description": None}
        )


def test_create_process_delegates_to_repository(monkeypatch):
    monkeypatch.setattr(
        "app.repositories.companies_repo.get_company",
        lambda org_id, company_id: {"id": company_id, "organization_id": org_id},
    )

    created = {}

    def fake_create_process(organization_id, created_by, data):
        created.update(organization_id=organization_id, created_by=created_by, data=data)
        return {"id": "process-1", **data}

    monkeypatch.setattr("app.repositories.processes_repo.create_process", fake_create_process)

    result = process_service.create_process(
        "org-1", "user-1", {"company_id": "company-1", "type": "abertura", "description": None}
    )

    assert result["id"] == "process-1"
    assert created["organization_id"] == "org-1"
    assert created["created_by"] == "user-1"
