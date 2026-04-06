"""Unit tests for RBACService."""

import pytest
from datetime import datetime
from unittest.mock import AsyncMock, MagicMock
from uuid import uuid4

from app.services.rbac_service import RBACService
from app.db.models import AppUser, Role


@pytest.fixture
def rbac_service(mock_db_session):
    return RBACService(mock_db_session)


@pytest.fixture
def mock_user():
    user = MagicMock(spec=AppUser)
    user.id = str(uuid4())
    user.entra_oid = "test-oid"
    user.display_name = "Test User"
    user.email = "test@example.com"
    user.last_login_at = datetime.utcnow()
    user.roles = []
    return user


@pytest.fixture
def mock_role():
    role = MagicMock(spec=Role)
    role.id = 1
    role.name = "viewer"
    role.display_name = "Viewer"
    role.permissions = []
    return role


class TestRBACService:
    @pytest.mark.asyncio
    async def test_get_or_create_user_existing(self, rbac_service, mock_db_session, mock_user):
        """Should return existing user and update last login."""
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = mock_user
        mock_db_session.execute.return_value = mock_result

        user = await rbac_service.get_or_create_user("test-oid", "Updated Name", "updated@example.com")

        assert user.entra_oid == "test-oid"
        assert user.display_name == "Updated Name"
        assert user.email == "updated@example.com"
        mock_db_session.flush.assert_called_once()

    @pytest.mark.asyncio
    async def test_get_or_create_user_new_with_viewer_role(self, rbac_service, mock_db_session, mock_role):
        """Should create new user with viewer role if not found."""
        # Mock user query - return None (user not found)
        user_result = MagicMock()
        user_result.scalar_one_or_none.return_value = None

        # Mock role query - return viewer role
        role_result = MagicMock()
        role_result.scalar_one_or_none.return_value = mock_role

        mock_db_session.execute.side_effect = [user_result, role_result]

        user = await rbac_service.get_or_create_user("new-oid", "New User", "new@example.com")

        mock_db_session.add.assert_called_once()
        mock_db_session.flush.assert_called_once()
        # Verify the user was created with correct attributes
        added_user = mock_db_session.add.call_args[0][0]
        assert added_user.entra_oid == "new-oid"
        assert added_user.display_name == "New User"
        assert added_user.email == "new@example.com"

    @pytest.mark.asyncio
    async def test_get_or_create_user_new_no_viewer_role(self, rbac_service, mock_db_session):
        """Should create new user even if viewer role doesn't exist."""
        # Mock user query - return None (user not found)
        user_result = MagicMock()
        user_result.scalar_one_or_none.return_value = None

        # Mock role query - return None (viewer role not found)
        role_result = MagicMock()
        role_result.scalar_one_or_none.return_value = None

        mock_db_session.execute.side_effect = [user_result, role_result]

        user = await rbac_service.get_or_create_user("new-oid", "New User")

        mock_db_session.add.assert_called_once()
        mock_db_session.flush.assert_called_once()

    @pytest.mark.asyncio
    async def test_user_has_permission_found(self, rbac_service, mock_user):
        """Should return True when user has required permission."""
        # Mock permission
        mock_permission = MagicMock()
        mock_permission.resource = "documents"
        mock_permission.action = "read"

        # Mock role with permission
        mock_role = MagicMock()
        mock_role.permissions = [mock_permission]

        # User has role with permission
        mock_user.roles = [mock_role]

        result = await rbac_service.user_has_permission(mock_user, "documents", "read")
        assert result is True

    @pytest.mark.asyncio
    async def test_user_has_permission_not_found(self, rbac_service, mock_user):
        """Should return False when user doesn't have required permission."""
        # Mock permission with different resource/action
        mock_permission = MagicMock()
        mock_permission.resource = "documents"
        mock_permission.action = "write"

        # Mock role with different permission
        mock_role = MagicMock()
        mock_role.permissions = [mock_permission]

        # User has role with different permission
        mock_user.roles = [mock_role]

        result = await rbac_service.user_has_permission(mock_user, "documents", "read")
        assert result is False

    @pytest.mark.asyncio
    async def test_user_has_permission_no_roles(self, rbac_service, mock_user):
        """Should return False when user has no roles."""
        mock_user.roles = []

        result = await rbac_service.user_has_permission(mock_user, "documents", "read")
        assert result is False

    @pytest.mark.asyncio
    async def test_list_users(self, rbac_service, mock_db_session):
        """Should list users with pagination."""
        # Mock count query
        mock_count_result = MagicMock()
        mock_count_result.scalar.return_value = 25

        # Mock users query
        mock_users = [MagicMock(spec=AppUser) for _ in range(20)]
        mock_users_result = MagicMock()
        mock_users_result.scalars.return_value.all.return_value = mock_users

        mock_db_session.execute.side_effect = [mock_count_result, mock_users_result]

        users, total = await rbac_service.list_users(page=1, page_size=20)

        assert total == 25
        assert len(users) == 20
        assert all(isinstance(user, MagicMock) for user in users)

    @pytest.mark.asyncio
    async def test_list_users_empty(self, rbac_service, mock_db_session):
        """Should handle empty user list."""
        # Mock count query - return None (handled as 0)
        mock_count_result = MagicMock()
        mock_count_result.scalar.return_value = None

        # Mock users query - return empty list
        mock_users_result = MagicMock()
        mock_users_result.scalars.return_value.all.return_value = []

        mock_db_session.execute.side_effect = [mock_count_result, mock_users_result]

        users, total = await rbac_service.list_users()

        assert total == 0
        assert len(users) == 0

    @pytest.mark.asyncio
    async def test_list_roles(self, rbac_service, mock_db_session):
        """Should return all roles ordered by ID."""
        mock_roles = [MagicMock(spec=Role) for _ in range(3)]
        mock_result = MagicMock()
        mock_result.scalars.return_value.all.return_value = mock_roles
        mock_db_session.execute.return_value = mock_result

        roles = await rbac_service.list_roles()

        assert len(roles) == 3
        assert all(isinstance(role, MagicMock) for role in roles)

    @pytest.mark.asyncio
    async def test_assign_roles_user_found(self, rbac_service, mock_db_session, mock_user):
        """Should assign roles to existing user."""
        # Mock user query
        user_result = MagicMock()
        user_result.scalar_one_or_none.return_value = mock_user

        # Mock roles query
        mock_roles = [MagicMock(spec=Role) for _ in range(2)]
        mock_roles[0].name = "admin"
        mock_roles[1].name = "editor"
        roles_result = MagicMock()
        roles_result.scalars.return_value.all.return_value = mock_roles

        mock_db_session.execute.side_effect = [user_result, roles_result]

        result = await rbac_service.assign_roles("user-123", ["admin", "editor"])

        assert result is mock_user
        assert mock_user.roles == mock_roles
        mock_db_session.flush.assert_called_once()

    @pytest.mark.asyncio
    async def test_assign_roles_user_not_found(self, rbac_service, mock_db_session):
        """Should return None when user doesn't exist."""
        # Mock user query - return None
        user_result = MagicMock()
        user_result.scalar_one_or_none.return_value = None
        mock_db_session.execute.return_value = user_result

        result = await rbac_service.assign_roles("nonexistent-user", ["admin"])

        assert result is None
        # Should only call execute once (for user lookup, not roles lookup)
        assert mock_db_session.execute.call_count == 1

    @pytest.mark.asyncio
    async def test_assign_roles_empty_role_list(self, rbac_service, mock_db_session, mock_user):
        """Should handle empty role assignments."""
        # Mock user query
        user_result = MagicMock()
        user_result.scalar_one_or_none.return_value = mock_user

        # Mock roles query - return empty list
        roles_result = MagicMock()
        roles_result.scalars.return_value.all.return_value = []

        mock_db_session.execute.side_effect = [user_result, roles_result]

        result = await rbac_service.assign_roles("user-123", ["nonexistent-role"])

        assert result is mock_user
        assert mock_user.roles == []
        mock_db_session.flush.assert_called_once()