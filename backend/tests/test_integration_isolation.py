"""Testes de integração via API (TestClient) cobrindo autenticação e
isolamento multi-tenant real (através das rotas, não só das funções de
serviço isoladas). Toda interação com o Supabase é substituída por dublês
em memória — nenhum destes testes toca um banco real.
"""

import pytest
from fastapi.testclient import TestClient

from app.core.security import AuthenticatedUser, get_current_user
from app.main import app

client = TestClient(app)


def _override_user(
    organization_id: str, role: str = "owner", user_id: str = "user-1", is_super_admin: bool = False
):
    def _fake_user() -> AuthenticatedUser:
        return AuthenticatedUser(
            id=user_id,
            email="a@b.com",
            organization_id=organization_id,
            role=role,
            is_super_admin=is_super_admin,
        )

    return _fake_user


@pytest.fixture(autouse=True)
def _clear_overrides():
    yield
    app.dependency_overrides.clear()


def test_health_check_is_public():
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_protected_route_without_token_is_rejected():
    response = client.get("/companies")

    assert response.status_code == 401


def _company(company_id: str, organization_id: str, razao_social: str) -> dict:
    return {
        "id": company_id,
        "organization_id": organization_id,
        "cnpj": None,
        "razao_social": razao_social,
        "nome_fantasia": None,
        "natureza_juridica": None,
        "uf": None,
        "municipio": None,
        "capital_social": None,
        "created_at": "2026-01-01T00:00:00Z",
        "updated_at": "2026-01-01T00:00:00Z",
    }


def test_companies_are_isolated_per_organization(monkeypatch):
    fake_db = {
        "org-a": [_company("company-a1", "org-a", "Empresa A")],
        "org-b": [_company("company-b1", "org-b", "Empresa B")],
    }

    def fake_list_companies(organization_id: str) -> list[dict]:
        return fake_db.get(organization_id, [])

    monkeypatch.setattr("app.services.company_service.companies_repo.list_companies", fake_list_companies)

    app.dependency_overrides[get_current_user] = _override_user("org-a")
    response_a = client.get("/companies")
    assert response_a.status_code == 200
    assert [c["id"] for c in response_a.json()] == ["company-a1"]

    app.dependency_overrides[get_current_user] = _override_user("org-b")
    response_b = client.get("/companies")
    assert response_b.status_code == 200
    assert [c["id"] for c in response_b.json()] == ["company-b1"]


def test_cannot_fetch_company_belonging_to_another_organization(monkeypatch):
    companies_by_org = {
        "org-a": {"company-a1": _company("company-a1", "org-a", "Empresa A")},
    }

    def fake_get_company(organization_id: str, company_id: str):
        return companies_by_org.get(organization_id, {}).get(company_id)

    monkeypatch.setattr("app.services.company_service.companies_repo.get_company", fake_get_company)

    # Usuário da org-b tentando acessar uma empresa que pertence à org-a.
    app.dependency_overrides[get_current_user] = _override_user("org-b")
    response = client.get("/companies/company-a1")

    assert response.status_code == 404


def test_document_upload_rejects_files_over_size_limit():
    app.dependency_overrides[get_current_user] = _override_user("org-a")

    oversized_content = b"0" * (10 * 1024 * 1024 + 1)
    response = client.post(
        "/documents/upload",
        data={"process_id": "process-1"},
        files={"file": ("grande.pdf", oversized_content, "application/pdf")},
    )

    assert response.status_code == 413


def test_change_plan_requires_owner_or_admin_role(monkeypatch):
    monkeypatch.setattr(
        "app.api.billing.billing_service.change_plan",
        lambda organization_id, plan_code: {"id": "sub-1", "plan_code": plan_code},
    )

    app.dependency_overrides[get_current_user] = _override_user("org-a", role="viewer")
    response = client.post("/subscriptions/change-plan", json={"plan_code": "pro"})

    assert response.status_code == 403


def test_change_plan_allows_owner(monkeypatch):
    def fake_change_plan(organization_id: str, plan_code: str) -> dict:
        return {
            "id": "sub-1",
            "organization_id": organization_id,
            "status": "active",
            "plan": {
                "id": "plan-pro",
                "code": plan_code,
                "name": "Pro",
                "max_companies": None,
                "price_cents": 9900,
            },
        }

    monkeypatch.setattr("app.api.billing.billing_service.change_plan", fake_change_plan)

    app.dependency_overrides[get_current_user] = _override_user("org-a", role="owner")
    response = client.post("/subscriptions/change-plan", json={"plan_code": "pro"})

    assert response.status_code == 200
    assert response.json()["plan"]["code"] == "pro"


def test_admin_routes_are_blocked_for_regular_users():
    app.dependency_overrides[get_current_user] = _override_user("org-a", role="owner")

    response = client.get("/admin/organizations")

    assert response.status_code == 403


def test_admin_can_list_organizations(monkeypatch):
    monkeypatch.setattr(
        "app.services.admin_service.list_organizations",
        lambda: [
            {
                "id": "org-a",
                "name": "Escritório A",
                "created_at": "2026-01-01T00:00:00Z",
                "plan": None,
                "user_count": 1,
                "company_count": 0,
                "process_count": 0,
            }
        ],
    )

    app.dependency_overrides[get_current_user] = _override_user("org-a", is_super_admin=True)
    response = client.get("/admin/organizations")

    assert response.status_code == 200
    assert response.json()[0]["id"] == "org-a"
