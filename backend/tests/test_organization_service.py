import pytest

from app.services import organization_service
from app.services.organization_service import (
    LastOwnerError,
    MemberNotFoundError,
    OrganizationNotFoundError,
)


def test_get_my_organization_raises_when_missing(monkeypatch):
    monkeypatch.setattr(
        "app.repositories.organization_repo.get_organization", lambda org_id: None
    )

    with pytest.raises(OrganizationNotFoundError):
        organization_service.get_my_organization("org-1")


def test_get_my_organization_returns_data(monkeypatch):
    monkeypatch.setattr(
        "app.repositories.organization_repo.get_organization",
        lambda org_id: {"id": org_id, "name": "Acme", "created_at": "2026-01-01T00:00:00Z"},
    )

    organization = organization_service.get_my_organization("org-1")

    assert organization["name"] == "Acme"


def test_update_member_role_raises_when_member_missing(monkeypatch):
    monkeypatch.setattr(
        "app.repositories.organization_repo.get_membership", lambda org_id, user_id: None
    )

    with pytest.raises(MemberNotFoundError):
        organization_service.update_member_role("org-1", "user-1", "admin", "actor-1")


def test_update_member_role_blocks_demoting_last_owner(monkeypatch):
    monkeypatch.setattr(
        "app.repositories.organization_repo.get_membership",
        lambda org_id, user_id: {"user_id": user_id, "role": "owner"},
    )
    monkeypatch.setattr(
        "app.repositories.organization_repo.count_owners", lambda org_id: 1
    )

    with pytest.raises(LastOwnerError):
        organization_service.update_member_role("org-1", "user-1", "admin", "actor-1")


def test_update_member_role_allows_demoting_when_other_owner_exists(monkeypatch):
    monkeypatch.setattr(
        "app.repositories.organization_repo.get_membership",
        lambda org_id, user_id: {"user_id": user_id, "role": "owner"},
    )
    monkeypatch.setattr(
        "app.repositories.organization_repo.count_owners", lambda org_id: 2
    )
    monkeypatch.setattr(
        "app.repositories.organization_repo.update_membership_role",
        lambda org_id, user_id, role: {"user_id": user_id, "role": role},
    )
    monkeypatch.setattr(
        "app.repositories.organization_repo.insert_audit_log", lambda *a, **k: None
    )

    updated = organization_service.update_member_role("org-1", "user-1", "admin", "actor-1")

    assert updated["role"] == "admin"


def test_remove_member_raises_when_missing(monkeypatch):
    monkeypatch.setattr(
        "app.repositories.organization_repo.get_membership", lambda org_id, user_id: None
    )

    with pytest.raises(MemberNotFoundError):
        organization_service.remove_member("org-1", "user-1", "actor-1")


def test_remove_member_blocks_removing_last_owner(monkeypatch):
    monkeypatch.setattr(
        "app.repositories.organization_repo.get_membership",
        lambda org_id, user_id: {"user_id": user_id, "role": "owner"},
    )
    monkeypatch.setattr(
        "app.repositories.organization_repo.count_owners", lambda org_id: 1
    )

    with pytest.raises(LastOwnerError):
        organization_service.remove_member("org-1", "user-1", "actor-1")


def test_remove_member_succeeds_for_non_owner(monkeypatch):
    monkeypatch.setattr(
        "app.repositories.organization_repo.get_membership",
        lambda org_id, user_id: {"user_id": user_id, "role": "operator"},
    )
    removed = {}
    monkeypatch.setattr(
        "app.repositories.organization_repo.delete_membership",
        lambda org_id, user_id: removed.update(org_id=org_id, user_id=user_id),
    )
    monkeypatch.setattr(
        "app.repositories.organization_repo.insert_audit_log", lambda *a, **k: None
    )

    organization_service.remove_member("org-1", "user-1", "actor-1")

    assert removed == {"org_id": "org-1", "user_id": "user-1"}
