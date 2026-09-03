from pydantic import BaseModel, Field


class TicketCreate(BaseModel):
    subject: str = Field(min_length=3, max_length=200)
    body: str = Field(min_length=1)


class MessageCreate(BaseModel):
    body: str = Field(min_length=1)


class MessageOut(BaseModel):
    id: str
    author_id: str | None
    author_is_admin: bool
    body: str
    created_at: str


class TicketOut(BaseModel):
    id: str
    organization_id: str
    created_by: str | None
    subject: str
    status: str
    priority: str
    created_at: str
    updated_at: str
    organizations: dict | None = None


class TicketDetailOut(TicketOut):
    messages: list[MessageOut]


class TicketStatusUpdate(BaseModel):
    status: str = Field(pattern="^(aberto|em_andamento|resolvido|fechado)$")
