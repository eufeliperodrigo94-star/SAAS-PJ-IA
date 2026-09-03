from pydantic import BaseModel


class DocumentOut(BaseModel):
    id: str
    process_id: str
    file_name: str
    content_type: str | None
    extracted_data: dict | None = None
    extracted_at: str | None = None
    created_at: str


class DocumentExtractRequest(BaseModel):
    text: str


class DivergenceOut(BaseModel):
    campo: str
    cadastro: str
    documento: str
    divergente: bool


class DocumentExtractResult(BaseModel):
    document_id: str
    extracted_data: dict
    divergences: list[DivergenceOut]
