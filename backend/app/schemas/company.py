from datetime import date

from pydantic import BaseModel, Field


class CompanyCreate(BaseModel):
    cnpj: str | None = None
    razao_social: str = Field(min_length=2, max_length=200)
    nome_fantasia: str | None = None
    natureza_juridica: str | None = None
    uf: str | None = None
    municipio: str | None = None
    capital_social: float | None = None


class CompanyUpdate(BaseModel):
    cnpj: str | None = None
    razao_social: str | None = None
    nome_fantasia: str | None = None
    natureza_juridica: str | None = None
    uf: str | None = None
    municipio: str | None = None
    capital_social: float | None = None


class CompanyOut(BaseModel):
    id: str
    organization_id: str
    cnpj: str | None
    razao_social: str
    nome_fantasia: str | None
    natureza_juridica: str | None
    uf: str | None
    municipio: str | None
    capital_social: float | None
    created_at: str
    updated_at: str


class PartnerCreate(BaseModel):
    nome: str = Field(min_length=2, max_length=200)
    cpf_cnpj: str | None = None
    qualificacao: str | None = None
    percentual_capital: float | None = None
    data_entrada: date | None = None
    data_saida: date | None = None


class PartnerOut(PartnerCreate):
    id: str
    company_id: str


class AddressCreate(BaseModel):
    tipo: str = "sede"
    logradouro: str | None = None
    numero: str | None = None
    complemento: str | None = None
    bairro: str | None = None
    municipio: str | None = None
    uf: str | None = None
    cep: str | None = None
    atual: bool = True


class AddressOut(AddressCreate):
    id: str
    company_id: str


class ActivityCreate(BaseModel):
    cnae_code: str = Field(min_length=1, max_length=20)
    description: str | None = None
    is_primary: bool = False


class ActivityOut(ActivityCreate):
    id: str
    company_id: str
