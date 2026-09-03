from pydantic import BaseModel


class ReportRuleOut(BaseModel):
    codigo: str
    nome: str
    versao: int
    fonte: str | None


class ReportItemOut(BaseModel):
    result: str
    message: str
    suggested_action: str | None
    evidence: dict
    rule_codigo: str | None


class ProcessReportOut(BaseModel):
    process_id: str
    company_name: str
    process_type: str
    process_status: str
    generated_at: str
    resumo: str
    erros: list[ReportItemOut]
    alertas: list[ReportItemOut]
    itens_ok: list[ReportItemOut]
    documentos_enviados: int
    regras_aplicadas: list[ReportRuleOut]
    acoes_recomendadas: list[str]
    aviso: str
