from fastapi import APIRouter, Depends

from app.core.security import AuthenticatedUser, require_organization
from app.schemas.assistant import AssistantMessageRequest, AssistantProposalOut
from app.services import assistant_service

router = APIRouter(prefix="/assistant", tags=["assistant"])


@router.post("/message", response_model=AssistantProposalOut)
def send_message(
    payload: AssistantMessageRequest, user: AuthenticatedUser = Depends(require_organization)
) -> dict:
    return assistant_service.interpret_message(
        user.organization_id, payload.process_id, payload.message, user.id
    )
