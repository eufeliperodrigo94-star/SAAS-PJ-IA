from fastapi import APIRouter, Depends, File, Form, UploadFile

from app.core.exceptions import DomainError
from app.core.security import AuthenticatedUser, require_organization
from app.schemas.document import DocumentExtractRequest, DocumentExtractResult, DocumentOut
from app.services import document_service

router = APIRouter(prefix="/documents", tags=["documents"])

MAX_UPLOAD_BYTES = 10 * 1024 * 1024  # 10 MB — proteção básica de upload (ver docs/PROJECT.md).


@router.post("/upload", response_model=DocumentOut)
async def upload_document(
    process_id: str = Form(...),
    file: UploadFile = File(...),
    user: AuthenticatedUser = Depends(require_organization),
) -> dict:
    content = await file.read()
    if len(content) > MAX_UPLOAD_BYTES:
        raise DomainError("Arquivo excede o limite de 10 MB.", status_code=413)

    return document_service.upload_document(
        user.organization_id, process_id, user.id, file.filename, content, file.content_type
    )


@router.post("/{document_id}/extract", response_model=DocumentExtractResult)
def extract_document(
    document_id: str,
    payload: DocumentExtractRequest,
    user: AuthenticatedUser = Depends(require_organization),
) -> dict:
    return document_service.extract_document(user.organization_id, document_id, payload.text, user.id)
