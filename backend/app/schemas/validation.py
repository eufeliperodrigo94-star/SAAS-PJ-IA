from pydantic import BaseModel

from app.schemas.process import ProcessOut


class ValidationOut(BaseModel):
    id: str
    process_id: str
    rule_id: str | None
    result: str
    evidence: dict
    message: str
    suggested_action: str | None
    created_at: str


class ValidationRunOut(BaseModel):
    process: ProcessOut
    validations: list[ValidationOut]
