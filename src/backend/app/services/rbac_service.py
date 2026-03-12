"""RBAC service for user and role management."""

from datetime import datetime

import structlog
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import AppUser, Role

logger = structlog.get_logger()


class RBACService:
    """Manages users, roles, and permission checks."""

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def get_or_create_user(
        self,
        oid: str,
        name: str,
        email: str | None = None,
    ) -> AppUser:
        """Get existing user or create on first login with viewer role."""
        result = await self._session.execute(select(AppUser).where(AppUser.entra_oid == oid))
        user = result.scalar_one_or_none()

        if user:
            user.last_login_at = datetime.utcnow()
            user.display_name = name
            if email:
                user.email = email
            await self._session.flush()
            return user

        # New user - assign viewer role
        viewer_result = await self._session.execute(select(Role).where(Role.name == "viewer"))
        viewer_role = viewer_result.scalar_one_or_none()

        user = AppUser(
            entra_oid=oid,
            display_name=name,
            email=email,
            last_login_at=datetime.utcnow(),
        )
        if viewer_role:
            user.roles.append(viewer_role)
        self._session.add(user)
        await self._session.flush()

        logger.info("user_auto_provisioned", entra_oid=oid, display_name=name)
        return user

    async def user_has_permission(self, user: AppUser, resource: str, action: str) -> bool:
        """Check if user has a specific permission via any of their roles."""
        for role in user.roles:
            for perm in role.permissions:
                if perm.resource == resource and perm.action == action:
                    return True
        return False

    async def list_users(self, page: int = 1, page_size: int = 20) -> tuple[list[AppUser], int]:
        """List all users with pagination."""
        count_query = select(func.count()).select_from(AppUser)
        total = (await self._session.execute(count_query)).scalar() or 0

        result = await self._session.execute(
            select(AppUser).order_by(AppUser.display_name).offset((page - 1) * page_size).limit(page_size)
        )
        return list(result.scalars().all()), total

    async def list_roles(self) -> list[Role]:
        """List all available roles."""
        result = await self._session.execute(select(Role).order_by(Role.id))
        return list(result.scalars().all())

    async def assign_roles(self, user_id: str, role_names: list[str]) -> AppUser | None:
        """Replace user's roles with the specified roles."""
        result = await self._session.execute(select(AppUser).where(AppUser.id == user_id))
        user = result.scalar_one_or_none()
        if not user:
            return None

        roles_result = await self._session.execute(select(Role).where(Role.name.in_(role_names)))
        new_roles = list(roles_result.scalars().all())

        user.roles = new_roles
        await self._session.flush()

        logger.info(
            "user_roles_updated",
            user_id=user_id,
            roles=[r.name for r in new_roles],
        )
        return user
