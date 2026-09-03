from typing import Literal

from pydantic import BaseModel, Field

OrganizationRole = Literal["owner", "admin", "operator", "viewer"]


class OrganizationDetailOut(BaseModel):
    id: str
    name: str
    created_at: str


class OrganizationRename(BaseModel):
    name: str = Field(min_length=2, max_length=200)


class ProfileUpdate(BaseModel):
    full_name: str = Field(min_length=1, max_length=200)


class MemberUserOut(BaseModel):
    id: str
    email: str | None
    full_name: str | None


class MemberOut(BaseModel):
    user_id: str
    role: OrganizationRole
    created_at: str
    users: MemberUserOut


class MemberInvite(BaseModel):
    email: str = Field(min_length=3, max_length=255)
    role: OrganizationRole = "operator"


class MemberRoleUpdate(BaseModel):
    role: OrganizationRole


class MemberRoleOut(BaseModel):
    user_id: str
    role: OrganizationRole
