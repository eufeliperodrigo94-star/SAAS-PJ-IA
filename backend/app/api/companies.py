from fastapi import APIRouter, Depends

from app.core.security import AuthenticatedUser, require_organization
from app.memory.company_memory import get_company_memory
from app.schemas.company import (
    ActivityCreate,
    ActivityOut,
    AddressCreate,
    AddressOut,
    CompanyCreate,
    CompanyMemoryOut,
    CompanyOut,
    CompanyUpdate,
    PartnerCreate,
    PartnerOut,
    TimelineEventOut,
)
from app.services import company_service

router = APIRouter(prefix="/companies", tags=["companies"])


@router.get("", response_model=list[CompanyOut])
def list_companies(user: AuthenticatedUser = Depends(require_organization)) -> list[dict]:
    return company_service.list_companies(user.organization_id)


@router.post("", response_model=CompanyOut)
def create_company(
    payload: CompanyCreate, user: AuthenticatedUser = Depends(require_organization)
) -> dict:
    return company_service.create_company(user.organization_id, payload.model_dump(), user.id)


@router.get("/{company_id}", response_model=CompanyOut)
def get_company(
    company_id: str, user: AuthenticatedUser = Depends(require_organization)
) -> dict:
    return company_service.get_company_or_404(user.organization_id, company_id)


@router.patch("/{company_id}", response_model=CompanyOut)
def update_company(
    company_id: str,
    payload: CompanyUpdate,
    user: AuthenticatedUser = Depends(require_organization),
) -> dict:
    data = {k: v for k, v in payload.model_dump().items() if v is not None}
    return company_service.update_company(user.organization_id, company_id, data, user.id)


@router.get("/{company_id}/partners", response_model=list[PartnerOut])
def list_partners(
    company_id: str, user: AuthenticatedUser = Depends(require_organization)
) -> list[dict]:
    return company_service.list_partners(user.organization_id, company_id)


@router.post("/{company_id}/partners", response_model=PartnerOut)
def create_partner(
    company_id: str,
    payload: PartnerCreate,
    user: AuthenticatedUser = Depends(require_organization),
) -> dict:
    data = payload.model_dump(mode="json")
    return company_service.add_partner(user.organization_id, company_id, data, user.id)


@router.get("/{company_id}/addresses", response_model=list[AddressOut])
def list_addresses(
    company_id: str, user: AuthenticatedUser = Depends(require_organization)
) -> list[dict]:
    return company_service.list_addresses(user.organization_id, company_id)


@router.post("/{company_id}/addresses", response_model=AddressOut)
def create_address(
    company_id: str,
    payload: AddressCreate,
    user: AuthenticatedUser = Depends(require_organization),
) -> dict:
    return company_service.add_address(
        user.organization_id, company_id, payload.model_dump(), user.id
    )


@router.get("/{company_id}/activities", response_model=list[ActivityOut])
def list_activities(
    company_id: str, user: AuthenticatedUser = Depends(require_organization)
) -> list[dict]:
    return company_service.list_activities(user.organization_id, company_id)


@router.post("/{company_id}/activities", response_model=ActivityOut)
def create_activity(
    company_id: str,
    payload: ActivityCreate,
    user: AuthenticatedUser = Depends(require_organization),
) -> dict:
    return company_service.add_activity(
        user.organization_id, company_id, payload.model_dump(), user.id
    )


@router.get("/{company_id}/timeline", response_model=list[TimelineEventOut])
def get_timeline(
    company_id: str, user: AuthenticatedUser = Depends(require_organization)
) -> list[dict]:
    return company_service.list_timeline(user.organization_id, company_id)


@router.get("/{company_id}/memory", response_model=CompanyMemoryOut)
def get_memory(
    company_id: str, user: AuthenticatedUser = Depends(require_organization)
) -> dict:
    return get_company_memory(user.organization_id, company_id)
