from app.core.exceptions import DomainError
from app.repositories import support_repo


class TicketNotFoundError(DomainError):
    def __init__(self) -> None:
        super().__init__("Chamado não encontrado.", status_code=404)


def create_ticket(organization_id: str, created_by: str, subject: str, body: str) -> dict:
    ticket = support_repo.create_ticket(organization_id, created_by, subject)
    support_repo.create_message(ticket["id"], organization_id, created_by, False, body)
    return ticket


def list_tickets(organization_id: str) -> list[dict]:
    return support_repo.list_tickets(organization_id=organization_id)


def get_ticket_or_404(ticket_id: str, organization_id: str | None = None) -> dict:
    ticket = support_repo.get_ticket(ticket_id, organization_id=organization_id)
    if ticket is None:
        raise TicketNotFoundError()
    return ticket


def get_ticket_with_messages(ticket_id: str, organization_id: str | None = None) -> dict:
    ticket = get_ticket_or_404(ticket_id, organization_id=organization_id)
    return {**ticket, "messages": support_repo.list_messages(ticket_id)}


def add_message(
    ticket_id: str, author_id: str | None, body: str, *, organization_id: str | None = None, is_admin: bool = False
) -> dict:
    ticket = get_ticket_or_404(ticket_id, organization_id=organization_id)
    return support_repo.create_message(ticket_id, ticket["organization_id"], author_id, is_admin, body)


def update_status(ticket_id: str, status: str) -> dict:
    get_ticket_or_404(ticket_id)
    updated = support_repo.update_status(ticket_id, status)
    if updated is None:
        raise TicketNotFoundError()
    return updated


def list_all_tickets(status: str | None = None) -> list[dict]:
    return support_repo.list_tickets(status=status)
