import pytest

from app.core.exceptions import NotAuthorizedError
from app.core.security import AuthenticatedUser, require_roles


def _user(role: str | None) -> AuthenticatedUser:
    return AuthenticatedUser(id="user-1", email="a@b.com", organization_id="org-1", role=role)


def test_require_roles_allows_matching_roles():
    dependency_fn = require_roles("owner", "admin")

    assert dependency_fn(_user("owner")).role == "owner"
    assert dependency_fn(_user("admin")).role == "admin"


def test_require_roles_blocks_other_roles():
    dependency_fn = require_roles("owner", "admin")

    with pytest.raises(NotAuthorizedError):
        dependency_fn(_user("viewer"))

    with pytest.raises(NotAuthorizedError):
        dependency_fn(_user("operator"))

    with pytest.raises(NotAuthorizedError):
        dependency_fn(_user(None))
