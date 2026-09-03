import pytest

from app.core.exceptions import DomainError
from app.services import document_service
from app.services.document_service import DocumentNotFoundError


class FakeRouter:
    def __init__(self, raw: str):
        self.raw = raw

    def extract(self, **kwargs):
        return self.raw


def _patch_process_and_company(monkeypatch):
    monkeypatch.setattr(
        "app.services.document_service.get_process_or_404",
        lambda org_id, process_id: {"id": process_id, "company_id": "c1", "type": "abertura"},
    )
    monkeypatch.setattr(
        "app.repositories.companies_repo.get_company",
        lambda org_id, cid: {"id": cid, "razao_social": "Acme LTDA", "cnpj": None},
    )
    monkeypatch.setattr("app.repositories.companies_repo.list_partners", lambda org_id, cid: [])
    monkeypatch.setattr(
        "app.repositories.company_events_repo.create_event", lambda *a, **k: {"id": "event-1"}
    )


def test_extract_document_not_found(monkeypatch):
    monkeypatch.setattr("app.repositories.documents_repo.get_document", lambda org_id, doc_id: None)

    with pytest.raises(DocumentNotFoundError):
        document_service.extract_document("org-1", "missing-doc", "texto", "user-1")


def test_extract_document_saves_and_returns_divergences(monkeypatch):
    _patch_process_and_company(monkeypatch)
    monkeypatch.setattr(
        "app.repositories.documents_repo.get_document",
        lambda org_id, doc_id: {"id": doc_id, "process_id": "p1", "file_name": "contrato.pdf"},
    )
    saved = {}
    monkeypatch.setattr(
        "app.repositories.documents_repo.save_extraction",
        lambda org_id, doc_id, data: saved.update(org_id=org_id, doc_id=doc_id, data=data),
    )
    monkeypatch.setattr(
        "app.services.document_service.get_ai_router",
        lambda: FakeRouter('{"razao_social": "Beta LTDA", "cnpj": null, "socios": null}'),
    )

    result = document_service.extract_document("org-1", "doc-1", "texto do contrato", "user-1")

    assert result["extracted_data"]["razao_social"] == "Beta LTDA"
    assert result["divergences"][0]["divergente"] is True
    assert saved["doc_id"] == "doc-1"


def test_extract_document_invalid_json_raises_domain_error(monkeypatch):
    _patch_process_and_company(monkeypatch)
    monkeypatch.setattr(
        "app.repositories.documents_repo.get_document",
        lambda org_id, doc_id: {"id": doc_id, "process_id": "p1", "file_name": "contrato.pdf"},
    )
    monkeypatch.setattr(
        "app.services.document_service.get_ai_router", lambda: FakeRouter("isso não é json")
    )

    with pytest.raises(DomainError):
        document_service.extract_document("org-1", "doc-1", "texto", "user-1")
