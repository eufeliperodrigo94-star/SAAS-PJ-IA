from pydantic import BaseModel, Field


class RegisterOrganizationRequest(BaseModel):
    organization_name: str = Field(min_length=2, max_length=200)
    full_name: str | None = None


class OrganizationOut(BaseModel):
    id: str
    name: str
    role: str


class MeResponse(BaseModel):
    id: str
    email: str | None
    organization_id: str | None
    role: str | None
