"""Testes de integração via API para as extensões do painel admin: suporte
(cliente + admin), vendas e CRUD de planos. Mesmo padrão de
test_integration_isolation.py — dublês em memória, sem banco real.
"""

import pytest
from fastapi.testclient import TestClient

from app.core.security import AuthenticatedUser, get_current_user
from app.main import app

client = TestClient(app)


def _override_user(organization_id: str, role: str = "owner", is_super_admin: bool = False, user_id: str = "user-1"):
    def _fake_user() -> AuthenticatedUser:
        return AuthenticatedUser(
            id=user_id, email="a@b.com", organization_id=organization_id, role=role, is_super_admin=is_super_admin
        )

    return _fake_user


@pytest.fixture(autouse=True)
def _clear_overrides():
    yield
    app.dependency_overrides.clear()


def _ticket(ticket_id: str, organization_id: str, subject: str = "Dúvida") -> dict:
    return {
        "id": ticket_id,
        "organization_id": organization_id,
        "created_by": "user-1",
        "subject": subject,
        "status": "aberto",
        "priority": "normal",
        "created_at": "2026-01-01T00:00:00Z",
        "updated_at": "2026-01-01T00:00:00Z",
    }


def test_client_can_open_and_list_own_tickets(monkeypatch):
    monkeypatch.setattr(
        "app.services.support_service.support_repo.create_ticket",
        lambda org_id, created_by, subject: _ticket("ticket-1", org_id, subject),
    )
    monkeypatch.setattr("app.services.support_service.support_repo.create_message", lambda *a, **k: {})
    monkeypatch.setattr(
        "app.services.support_service.support_repo.list_tickets",
        lambda organization_id=None, status=None: [_ticket("ticket-1", organization_id)],
    )

    app.dependency_overrides[get_current_user] = _override_user("org-a")

    create_response = client.post("/support/tickets", json={"subject": "Dúvida", "body": "Como funciona?"})
    assert create_response.status_code == 200

    list_response = client.get("/support/tickets")
    assert list_response.status_code == 200
    assert list_response.json()[0]["organization_id"] == "org-a"


def test_client_cannot_reply_to_another_organizations_ticket(monkeypatch):
    monkeypatch.setattr(
        "app.services.support_service.support_repo.get_ticket",
        lambda ticket_id, organization_id=None: {"id": ticket_id, "organization_id": "org-a"}
        if organization_id in (None, "org-a")
        else None,
    )

    app.dependency_overrides[get_current_user] = _override_user("org-b")
    response = client.post("/support/tickets/ticket-1/messages", json={"body": "oi"})

    assert response.status_code == 404


def test_admin_support_routes_blocked_for_regular_user():
    app.dependency_overrides[get_current_user] = _override_user("org-a")
    response = client.get("/admin/support/tickets")
    assert response.status_code == 403


def test_admin_can_list_and_reply_any_ticket(monkeypatch):
    monkeypatch.setattr(
        "app.services.support_service.support_repo.list_tickets",
        lambda organization_id=None, status=None: [
            {
                "id": "ticket-1",
                "organization_id": "org-a",
                "created_by": "user-1",
                "subject": "Dúvida",
                "status": "aberto",
                "priority": "normal",
                "created_at": "2026-01-01T00:00:00Z",
                "updated_at": "2026-01-01T00:00:00Z",
                "organizations": {"name": "Empresa A"},
            }
        ],
    )
    monkeypatch.setattr(
        "app.services.support_service.support_repo.get_ticket",
        lambda ticket_id, organization_id=None: {"id": ticket_id, "organization_id": "org-a"},
    )
    monkeypatch.setattr(
        "app.services.support_service.support_repo.create_message",
        lambda ticket_id, org_id, author_id, is_admin, body: {
            "id": "msg-1",
            "author_id": author_id,
            "author_is_admin": is_admin,
            "body": body,
            "created_at": "2026-01-01T00:00:00Z",
        },
    )

    app.dependency_overrides[get_current_user] = _override_user("org-anything", is_super_admin=True)

    list_response = client.get("/admin/support/tickets")
    assert list_response.status_code == 200
    assert list_response.json()[0]["organizations"]["name"] == "Empresa A"

    reply_response = client.post("/admin/support/tickets/ticket-1/messages", json={"body": "Já estamos vendo."})
    assert reply_response.status_code == 200
    assert reply_response.json()["author_is_admin"] is True


def test_admin_sales_route_requires_super_admin(monkeypatch):
    monkeypatch.setattr("app.repositories.billing_repo.list_active_subscriptions_with_plans", lambda: [])

    app.dependency_overrides[get_current_user] = _override_user("org-a")
    assert client.get("/admin/sales").status_code == 403

    app.dependency_overrides[get_current_user] = _override_user("org-a", is_super_admin=True)
    response = client.get("/admin/sales")
    assert response.status_code == 200
    assert response.json()["mrr_cents"] == 0


def test_admin_can_create_and_update_plan(monkeypatch):
    monkeypatch.setattr("app.repositories.billing_repo.get_plan_by_code", lambda code: None)
    monkeypatch.setattr(
        "app.repositories.billing_repo.create_plan",
        lambda data: {
            "id": "plan-new",
            "code": data["code"],
            "name": data["name"],
            "max_companies": data.get("max_companies"),
            "price_cents": data.get("price_cents"),
            "active": True,
        },
    )
    monkeypatch.setattr("app.repositories.billing_repo.get_plan", lambda plan_id: {"id": plan_id})
    monkeypatch.setattr(
        "app.repositories.billing_repo.update_plan",
        lambda plan_id, data: {
            "id": plan_id,
            "code": "enterprise",
            "name": "Enterprise",
            "max_companies": None,
            "price_cents": None,
            "active": False,
            **data,
        },
    )

    app.dependency_overrides[get_current_user] = _override_user("org-a", is_super_admin=True)

    create_response = client.post(
        "/admin/plans", json={"code": "enterprise", "name": "Enterprise", "max_companies": None, "price_cents": None}
    )
    assert create_response.status_code == 200
    assert create_response.json()["code"] == "enterprise"

    update_response = client.patch("/admin/plans/plan-new", json={"active": False})
    assert update_response.status_code == 200
    assert update_response.json()["active"] is False
