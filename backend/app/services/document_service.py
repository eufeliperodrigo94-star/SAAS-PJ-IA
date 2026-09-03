import json

from app.ai.router import get_ai_router
from app.core.exceptions import DomainError
from app.documents.cross_check import compare_company_data
from app.repositories import companies_repo, company_events_repo, documents_repo
from app.services.process_service import get_process_or_404

EXTRACTION_SCHEMA = (
    '{"razao_social": string|null, "cnpj": string|null, '
    '"socios": [{"nome": string, "percentual_capital": number|null}]|null, '
    '"endereco": {"municipio": string|null, "uf": string|null}|null}'
)


class DocumentNotFoundError(DomainError):
    def __init__(self) -> None:
        super().__init__("Documento não encontrado.", status_code=404)


def upload_document(
    organization_id: str,
    process_id: str,
    user_id: str | None,
    filename: str,
    content: bytes,
    content_type: str | None,
) -> dict:
    process = get_process_or_404(organization_id, process_id)
    storage_path = documents_repo.upload_file(organization_id, process_id, filename, content, content_type)
    document = documents_repo.create_document(
        organization_id,
        process_id,
        {"file_name": filename, "storage_path": storage_path, "content_type": content_type, "uploaded_by": user_id},
    )
    company_events_repo.create_event(
        organization_id,
        process["company_id"],
        event_type="document.uploaded",
        description=f"Documento '{filename}' enviado.",
        payload={"document_id": document["id"]},
        process_id=process_id,
        created_by=user_id,
    )
    return document


def list_documents(organization_id: str, process_id: str) -> list[dict]:
    get_process_or_404(organization_id, process_id)
    return documents_repo.list_documents(organization_id, process_id)


def get_document_or_404(organization_id: str, document_id: str) -> dict:
    document = documents_repo.get_document(organization_id, document_id)
    if not document:
        raise DocumentNotFoundError()
    return document


def extract_document(organization_id: str, document_id: str, text: str, user_id: str | None) -> dict:
    document = get_document_or_404(organization_id, document_id)
    process = get_process_or_404(organization_id, document["process_id"])
    company = companies_repo.get_company(organization_id, process["company_id"])
    partners = companies_repo.list_partners(organization_id, process["company_id"])

    raw = get_ai_router().extract(
        task="document_extraction",
        text=text,
        schema_description=EXTRACTION_SCHEMA,
        organization_id=organization_id,
        process_id=process["id"],
        user_id=user_id,
    )
    try:
        extracted = json.loads(raw)
    except json.JSONDecodeError as exc:
        raise DomainError("Não foi possível interpretar a resposta da IA como JSON.") from exc

    documents_repo.save_extraction(organization_id, document_id, extracted)
    divergences = compare_company_data(company, partners, extracted)

    company_events_repo.create_event(
        organization_id,
        process["company_id"],
        event_type="document.extracted",
        description=(
            f"Documento '{document['file_name']}' analisado "
            f"({sum(1 for d in divergences if d['divergente'])} divergência(s) encontrada(s))."
        ),
        payload={"document_id": document_id},
        process_id=process["id"],
        created_by=user_id,
    )

    return {"document_id": document_id, "extracted_data": extracted, "divergences": divergences}
