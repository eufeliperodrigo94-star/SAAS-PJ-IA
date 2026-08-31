from fastapi import APIRouter, Depends, Query

from app.core.security import AuthenticatedUser, require_organization
from app.schemas.process import ProcessCreate, ProcessOut
from app.services import process_service

router = APIRouter(prefix="/processes", tags=["processes"])


@router.get("", response_model=list[ProcessOut])
def list_processes(
    company_id: str | None = Query(default=None),
    user: AuthenticatedUser = Depends(require_organization),
) -> list[dict]:
    return process_service.list_processes(user.organization_id, company_id)


@router.post("", response_model=ProcessOut)
def create_process(
    payload: ProcessCreate, user: AuthenticatedUser = Depends(require_organization)
) -> dict:
    return process_service.create_process(user.organization_id, user.id, payload.model_dump())


@router.get("/{process_id}", response_model=ProcessOut)
def get_process(
    process_id: str, user: AuthenticatedUser = Depends(require_organization)
) -> dict:
    return process_service.get_process_or_404(user.organization_id, process_id)
