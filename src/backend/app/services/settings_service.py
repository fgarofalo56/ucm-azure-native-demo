"""System settings service — reads/writes admin-configurable settings from DB."""

from datetime import datetime

import structlog
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import SystemSetting

logger = structlog.get_logger()

# Defaults used when DB is unavailable or setting doesn't exist
DEFAULTS = {
    "pdf_engine": "opensource",
    "aspose_words_license": "",
    "aspose_cells_license": "",
    "aspose_slides_license": "",
    "malware_scanning_enabled": "true",
    "gotenberg_url": "",
}

# Settings that should never be returned in API responses (contain secrets)
SENSITIVE_KEYS = {"aspose_words_license", "aspose_cells_license", "aspose_slides_license"}


class SettingsService:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def get_all(self) -> dict[str, dict]:
        """Get all settings as {key: {value, description, updated_at, updated_by}}."""
        result = await self._session.execute(select(SystemSetting))
        settings = {}
        for s in result.scalars().all():
            # Mask sensitive values
            value = s.value
            if s.key in SENSITIVE_KEYS and value:
                value = "••••" + value[-4:] if len(value) > 4 else "••••"
            settings[s.key] = {
                "value": value,
                "description": s.description,
                "updated_at": s.updated_at.isoformat() if s.updated_at else None,
                "updated_by": s.updated_by,
                "is_sensitive": s.key in SENSITIVE_KEYS,
            }
        return settings

    async def get(self, key: str) -> str:
        """Get a single setting value. Returns default if not found."""
        result = await self._session.execute(select(SystemSetting.value).where(SystemSetting.key == key))
        row = result.scalar_one_or_none()
        return row if row is not None else DEFAULTS.get(key, "")

    async def set(self, key: str, value: str, user_id: str | None = None) -> None:
        """Set a setting value. Creates if not exists, updates if exists."""
        existing = await self._session.execute(select(SystemSetting).where(SystemSetting.key == key))
        setting = existing.scalar_one_or_none()

        if setting:
            setting.value = value
            setting.updated_at = datetime.utcnow()
            setting.updated_by = user_id
        else:
            self._session.add(
                SystemSetting(
                    key=key,
                    value=value,
                    updated_by=user_id,
                )
            )
        await self._session.flush()
        logger.info("setting_updated", key=key, user_id=user_id)

    async def set_many(self, updates: dict[str, str], user_id: str | None = None) -> None:
        """Update multiple settings at once."""
        for key, value in updates.items():
            await self.set(key, value, user_id)

    async def is_malware_scanning_enabled(self) -> bool:
        val = await self.get("malware_scanning_enabled")
        return val.lower() in ("true", "1", "yes")

    async def get_pdf_engine(self) -> str:
        return await self.get("pdf_engine")
