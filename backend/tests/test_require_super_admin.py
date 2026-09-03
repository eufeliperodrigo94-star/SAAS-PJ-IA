import pytest

from app.core.exceptions import NotAuthorizedError
from app.core.security import AuthenticatedUser, require_super_admin


def _user(is_super_admin: bool) -> AuthenticatedUser:
    return AuthenticatedUser(
        id="user-1", email="a@b.com", organization_id=None, role=None, is_super_admin=is_super_admin
    )


def test_require_super_admin_allows_super_admin():
    assert require_super_admin(_user(True)).is_super_admin is True


def test_require_super_admin_blocks_regular_user():
    with pytest.raises(NotAuthorizedError):
        require_super_admin(_user(False))
