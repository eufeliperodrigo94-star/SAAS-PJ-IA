from fastapi import APIRouter, Depends, Query

from app.core.security import AuthenticatedUser, require_organization
from app.schemas.document import DocumentOut
from app.schemas.process import ProcessCreate, ProcessOut
from app.schemas.validation import ValidationOut, ValidationRunOut
from app.services import document_service, process_service, validation_service

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


@router.post("/{process_id}/validate", response_model=ValidationRunOut)
def validate_process(
    process_id: str, user: AuthenticatedUser = Depends(require_organization)
) -> dict:
    return validation_service.run_validation(user.organization_id, process_id, user.id)


@router.get("/{process_id}/validations", response_model=list[ValidationOut])
def list_validations(
    process_id: str, user: AuthenticatedUser = Depends(require_organization)
) -> list[dict]:
    return validation_service.list_validations(user.organization_id, process_id)


@router.get("/{process_id}/documents", response_model=list[DocumentOut])
def list_documents(
    process_id: str, user: AuthenticatedUser = Depends(require_organization)
) -> list[dict]:
    return document_service.list_documents(user.organization_id, process_id)
