from pydantic import BaseModel, Field

PROCESS_TYPES = (
    "abertura",
    "alteracao_qsa",
    "alteracao_endereco",
    "alteracao_cnae",
    "alteracao_capital",
    "alteracao_administrador",
    "alteracao_nome_objeto",
    "alteracao_porte",
    "transferencia_uf",
)


class ProcessCreate(BaseModel):
    company_id: str
    type: str = Field(pattern="^(" + "|".join(PROCESS_TYPES) + ")$")
    description: str | None = None


class ProcessOut(BaseModel):
    id: str
    organization_id: str
    company_id: str
    type: str
    status: str
    description: str | None
    created_at: str
    updated_at: str
