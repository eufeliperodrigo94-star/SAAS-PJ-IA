from fastapi import APIRouter, Depends

from app.core.security import AuthenticatedUser, require_organization
from app.schemas.support import MessageCreate, MessageOut, TicketCreate, TicketDetailOut, TicketOut
from app.services import support_service

router = APIRouter(prefix="/support", tags=["support"])


@router.get("/tickets", response_model=list[TicketOut])
def list_tickets(user: AuthenticatedUser = Depends(require_organization)) -> list[dict]:
    return support_service.list_tickets(user.organization_id)


@router.post("/tickets", response_model=TicketOut)
def create_ticket(
    payload: TicketCreate, user: AuthenticatedUser = Depends(require_organization)
) -> dict:
    return support_service.create_ticket(user.organization_id, user.id, payload.subject, payload.body)


@router.get("/tickets/{ticket_id}", response_model=TicketDetailOut)
def get_ticket(
    ticket_id: str, user: AuthenticatedUser = Depends(require_organization)
) -> dict:
    return support_service.get_ticket_with_messages(ticket_id, organization_id=user.organization_id)


@router.post("/tickets/{ticket_id}/messages", response_model=MessageOut)
def add_message(
    ticket_id: str,
    payload: MessageCreate,
    user: AuthenticatedUser = Depends(require_organization),
) -> dict:
    return support_service.add_message(
        ticket_id, user.id, payload.body, organization_id=user.organization_id, is_admin=False
    )
