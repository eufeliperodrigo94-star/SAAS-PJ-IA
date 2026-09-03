import pytest

from app.services import support_service


def test_create_ticket_creates_ticket_and_first_message(monkeypatch):
    created_tickets = []
    created_messages = []

    monkeypatch.setattr(
        "app.repositories.support_repo.create_ticket",
        lambda org_id, created_by, subject: created_tickets.append((org_id, created_by, subject))
        or {"id": "ticket-1", "organization_id": org_id, "subject": subject},
    )
    monkeypatch.setattr(
        "app.repositories.support_repo.create_message",
        lambda ticket_id, org_id, author_id, is_admin, body: created_messages.append(
            (ticket_id, org_id, author_id, is_admin, body)
        ),
    )

    ticket = support_service.create_ticket("org-1", "user-1", "Dúvida", "Como funciona X?")

    assert ticket["id"] == "ticket-1"
    assert created_tickets == [("org-1", "user-1", "Dúvida")]
    assert created_messages == [("ticket-1", "org-1", "user-1", False, "Como funciona X?")]


def test_get_ticket_or_404_raises_when_missing(monkeypatch):
    monkeypatch.setattr("app.repositories.support_repo.get_ticket", lambda ticket_id, organization_id=None: None)

    with pytest.raises(support_service.TicketNotFoundError):
        support_service.get_ticket_or_404("missing")


def test_add_message_scopes_to_organization(monkeypatch):
    monkeypatch.setattr(
        "app.repositories.support_repo.get_ticket",
        lambda ticket_id, organization_id=None: {"id": ticket_id, "organization_id": "org-1"}
        if organization_id in (None, "org-1")
        else None,
    )
    monkeypatch.setattr(
        "app.repositories.support_repo.create_message",
        lambda ticket_id, org_id, author_id, is_admin, body: {
            "ticket_id": ticket_id,
            "organization_id": org_id,
            "is_admin": is_admin,
            "body": body,
        },
    )

    result = support_service.add_message("ticket-1", "user-1", "Obrigado", organization_id="org-1")
    assert result["organization_id"] == "org-1"
    assert result["is_admin"] is False

    with pytest.raises(support_service.TicketNotFoundError):
        support_service.add_message("ticket-1", "user-2", "oi", organization_id="org-2")


def test_update_status_raises_when_missing(monkeypatch):
    monkeypatch.setattr(
        "app.repositories.support_repo.get_ticket", lambda ticket_id, organization_id=None: {"id": ticket_id}
    )
    monkeypatch.setattr("app.repositories.support_repo.update_status", lambda ticket_id, status: None)

    with pytest.raises(support_service.TicketNotFoundError):
        support_service.update_status("ticket-1", "resolvido")
