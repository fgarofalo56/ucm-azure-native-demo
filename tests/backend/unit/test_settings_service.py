"""Unit tests for SettingsService."""

import pytest
from datetime import datetime
from unittest.mock import AsyncMock, MagicMock

from app.services.settings_service import SettingsService, DEFAULTS, SENSITIVE_KEYS
from app.db.models import SystemSetting


@pytest.fixture
def settings_service(mock_db_session):
    return SettingsService(mock_db_session)


@pytest.fixture
def mock_setting():
    setting = MagicMock(spec=SystemSetting)
    setting.key = "pdf_engine"
    setting.value = "opensource"
    setting.description = "PDF engine configuration"
    setting.updated_at = datetime.utcnow()
    setting.updated_by = "user-123"
    return setting


class TestSettingsService:
    @pytest.mark.asyncio
    async def test_get_all(self, settings_service, mock_db_session):
        """Should return all settings with masked sensitive values."""
        mock_settings = []

        # Regular setting
        regular_setting = MagicMock()
        regular_setting.key = "pdf_engine"
        regular_setting.value = "opensource"
        regular_setting.description = "PDF engine"
        regular_setting.updated_at = datetime.utcnow()
        regular_setting.updated_by = "user-123"
        mock_settings.append(regular_setting)

        # Sensitive setting
        sensitive_setting = MagicMock()
        sensitive_setting.key = "aspose_words_license"
        sensitive_setting.value = "super-secret-license-key-12345"
        sensitive_setting.description = "Aspose Words license"
        sensitive_setting.updated_at = datetime.utcnow()
        sensitive_setting.updated_by = "admin-456"
        mock_settings.append(sensitive_setting)

        mock_result = MagicMock()
        mock_result.scalars.return_value.all.return_value = mock_settings
        mock_db_session.execute.return_value = mock_result

        result = await settings_service.get_all()

        assert "pdf_engine" in result
        assert "aspose_words_license" in result

        # Regular setting should not be masked
        assert result["pdf_engine"]["value"] == "opensource"
        assert result["pdf_engine"]["is_sensitive"] is False

        # Sensitive setting should be masked
        assert result["aspose_words_license"]["value"] == "••••2345"
        assert result["aspose_words_license"]["is_sensitive"] is True

    @pytest.mark.asyncio
    async def test_get_all_short_sensitive_value(self, settings_service, mock_db_session):
        """Should mask short sensitive values completely."""
        mock_setting = MagicMock()
        mock_setting.key = "aspose_words_license"
        mock_setting.value = "abc"  # Short value
        mock_setting.description = "License"
        mock_setting.updated_at = None
        mock_setting.updated_by = None

        mock_result = MagicMock()
        mock_result.scalars.return_value.all.return_value = [mock_setting]
        mock_db_session.execute.return_value = mock_result

        result = await settings_service.get_all()

        assert result["aspose_words_license"]["value"] == "••••"

    @pytest.mark.asyncio
    async def test_get_all_empty_sensitive_value(self, settings_service, mock_db_session):
        """Should handle empty sensitive values."""
        mock_setting = MagicMock()
        mock_setting.key = "aspose_words_license"
        mock_setting.value = ""
        mock_setting.description = "License"
        mock_setting.updated_at = None
        mock_setting.updated_by = None

        mock_result = MagicMock()
        mock_result.scalars.return_value.all.return_value = [mock_setting]
        mock_db_session.execute.return_value = mock_result

        result = await settings_service.get_all()

        # Empty sensitive values should not be masked
        assert result["aspose_words_license"]["value"] == ""

    @pytest.mark.asyncio
    async def test_get_setting_found(self, settings_service, mock_db_session):
        """Should return setting value when found."""
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = "opensource"
        mock_db_session.execute.return_value = mock_result

        value = await settings_service.get("pdf_engine")
        assert value == "opensource"

    @pytest.mark.asyncio
    async def test_get_setting_missing_with_default(self, settings_service, mock_db_session):
        """Should return default value when setting not found and default exists."""
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = None
        mock_db_session.execute.return_value = mock_result

        value = await settings_service.get("pdf_engine")
        assert value == DEFAULTS["pdf_engine"]

    @pytest.mark.asyncio
    async def test_get_setting_missing_no_default(self, settings_service, mock_db_session):
        """Should return empty string when setting not found and no default."""
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = None
        mock_db_session.execute.return_value = mock_result

        value = await settings_service.get("nonexistent_setting")
        assert value == ""

    @pytest.mark.asyncio
    async def test_set_setting_new(self, settings_service, mock_db_session):
        """Should create new setting when it doesn't exist."""
        # Mock existing check - return None (not found)
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = None
        mock_db_session.execute.return_value = mock_result

        await settings_service.set("new_setting", "new_value", "user-123")

        # Should add new setting
        mock_db_session.add.assert_called_once()
        added_setting = mock_db_session.add.call_args[0][0]
        assert added_setting.key == "new_setting"
        assert added_setting.value == "new_value"
        assert added_setting.updated_by == "user-123"
        mock_db_session.flush.assert_called_once()

    @pytest.mark.asyncio
    async def test_set_setting_update_existing(self, settings_service, mock_db_session, mock_setting):
        """Should update existing setting."""
        # Mock existing check - return existing setting
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = mock_setting
        mock_db_session.execute.return_value = mock_result

        await settings_service.set("pdf_engine", "aspose", "user-456")

        # Should update existing setting
        assert mock_setting.value == "aspose"
        assert mock_setting.updated_by == "user-456"
        # updated_at should be set to current time (we can't easily test exact time)
        assert mock_setting.updated_at is not None
        mock_db_session.flush.assert_called_once()
        # Should not call add for existing setting
        mock_db_session.add.assert_not_called()

    @pytest.mark.asyncio
    async def test_set_setting_no_user(self, settings_service, mock_db_session):
        """Should handle setting without user ID."""
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = None
        mock_db_session.execute.return_value = mock_result

        await settings_service.set("setting", "value")

        added_setting = mock_db_session.add.call_args[0][0]
        assert added_setting.updated_by is None

    @pytest.mark.asyncio
    async def test_set_many(self, settings_service, mock_db_session):
        """Should update multiple settings."""
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = None
        mock_db_session.execute.return_value = mock_result

        updates = {
            "pdf_engine": "aspose",
            "malware_scanning_enabled": "false",
            "gotenberg_url": "http://gotenberg:3000"
        }

        await settings_service.set_many(updates, "user-123")

        # Should have called add three times (one for each setting)
        assert mock_db_session.add.call_count == 3
        assert mock_db_session.flush.call_count == 3

    @pytest.mark.asyncio
    async def test_is_malware_scanning_enabled_true(self, settings_service, mock_db_session):
        """Should return True for truthy values."""
        test_cases = ["true", "True", "TRUE", "1", "yes", "YES"]

        for test_value in test_cases:
            mock_result = MagicMock()
            mock_result.scalar_one_or_none.return_value = test_value
            mock_db_session.execute.return_value = mock_result

            result = await settings_service.is_malware_scanning_enabled()
            assert result is True, f"Expected True for value: {test_value}"

    @pytest.mark.asyncio
    async def test_is_malware_scanning_enabled_false(self, settings_service, mock_db_session):
        """Should return False for falsy values."""
        test_cases = ["false", "False", "FALSE", "0", "no", "NO", ""]

        for test_value in test_cases:
            mock_result = MagicMock()
            mock_result.scalar_one_or_none.return_value = test_value
            mock_db_session.execute.return_value = mock_result

            result = await settings_service.is_malware_scanning_enabled()
            assert result is False, f"Expected False for value: {test_value}"

    @pytest.mark.asyncio
    async def test_is_malware_scanning_enabled_default(self, settings_service, mock_db_session):
        """Should use default value when setting not found."""
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = None
        mock_db_session.execute.return_value = mock_result

        result = await settings_service.is_malware_scanning_enabled()
        # Default is "true" so should return True
        expected = DEFAULTS["malware_scanning_enabled"].lower() in ("true", "1", "yes")
        assert result is expected

    @pytest.mark.asyncio
    async def test_get_pdf_engine(self, settings_service, mock_db_session):
        """Should return PDF engine setting."""
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = "aspose"
        mock_db_session.execute.return_value = mock_result

        result = await settings_service.get_pdf_engine()
        assert result == "aspose"

    @pytest.mark.asyncio
    async def test_get_pdf_engine_default(self, settings_service, mock_db_session):
        """Should return default PDF engine when not set."""
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = None
        mock_db_session.execute.return_value = mock_result

        result = await settings_service.get_pdf_engine()
        assert result == DEFAULTS["pdf_engine"]

    def test_defaults_constant(self):
        """Should have expected default values."""
        assert DEFAULTS["pdf_engine"] == "opensource"
        assert DEFAULTS["malware_scanning_enabled"] == "true"
        assert "aspose_words_license" in DEFAULTS
        assert "gotenberg_url" in DEFAULTS

    def test_sensitive_keys_constant(self):
        """Should have expected sensitive keys."""
        assert "aspose_words_license" in SENSITIVE_KEYS
        assert "aspose_cells_license" in SENSITIVE_KEYS
        assert "aspose_slides_license" in SENSITIVE_KEYS
        # Non-sensitive keys should not be included
        assert "pdf_engine" not in SENSITIVE_KEYS