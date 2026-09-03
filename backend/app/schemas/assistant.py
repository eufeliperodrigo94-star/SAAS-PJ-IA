from pydantic import BaseModel, Field


class AssistantMessageRequest(BaseModel):
    process_id: str
    message: str = Field(min_length=1, max_length=2000)


class AssistantProposalOut(BaseModel):
    process_id: str
    proposal: dict
    requires_confirmation: bool
