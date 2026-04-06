"""Unit tests for application configuration."""

import pytest
from pydantic import ValidationError

from app.config import Settings


class TestSettings:
    def test_default_settings(self):
        """Should create settings with defaults."""
        s = Settings()
        assert s.environment == "dev"
        assert s.max_upload_size_mb == 500
        assert s.log_level == "INFO"
        assert s.azure_cloud == "commercial"
        assert s.pdf_engine == "aspose"

    def test_valid_environments(self):
        """Should accept valid environments."""
        valid_envs = ["dev", "staging", "prod", "test"]
        for env in valid_envs:
            s = Settings(environment=env)
            assert s.environment == env

    def test_invalid_environment(self):
        """Should reject invalid environment."""
        with pytest.raises(ValidationError) as exc_info:
            Settings(environment="invalid")

        error = exc_info.value.errors()[0]
        assert error["type"] == "value_error"
        assert "environment must be one of" in str(error["ctx"]["error"])

    def test_max_upload_size_valid_ranges(self):
        """Should accept valid upload sizes."""
        valid_sizes = [1, 100, 500, 1024, 2048]
        for size in valid_sizes:
            s = Settings(max_upload_size_mb=size)
            assert s.max_upload_size_mb == size

    def test_max_upload_size_too_large(self):
        """Should reject sizes over 2048."""
        with pytest.raises(ValidationError) as exc_info:
            Settings(max_upload_size_mb=3000)

        error = exc_info.value.errors()[0]
        assert error["type"] == "value_error"
        assert "Size must be between 1 and 2048 MB" in str(error["ctx"]["error"])

    def test_max_upload_size_zero(self):
        """Should reject zero size."""
        with pytest.raises(ValidationError) as exc_info:
            Settings(max_upload_size_mb=0)

        error = exc_info.value.errors()[0]
        assert error["type"] == "value_error"
        assert "Size must be between 1 and 2048 MB" in str(error["ctx"]["error"])

    def test_max_upload_size_negative(self):
        """Should reject negative size."""
        with pytest.raises(ValidationError) as exc_info:
            Settings(max_upload_size_mb=-10)

        error = exc_info.value.errors()[0]
        assert error["type"] == "value_error"

    def test_max_merge_size_valid_ranges(self):
        """Should accept valid merge sizes."""
        valid_sizes = [1, 100, 500, 1024, 2048]
        for size in valid_sizes:
            s = Settings(max_merge_size_mb=size)
            assert s.max_merge_size_mb == size

    def test_max_merge_size_too_large(self):
        """Should reject merge sizes over 2048."""
        with pytest.raises(ValidationError) as exc_info:
            Settings(max_merge_size_mb=3000)

        error = exc_info.value.errors()[0]
        assert error["type"] == "value_error"

    def test_log_level_normalization(self):
        """Should normalize log level to uppercase."""
        test_cases = [
            ("debug", "DEBUG"),
            ("info", "INFO"),
            ("warning", "WARNING"),
            ("error", "ERROR"),
            ("critical", "CRITICAL"),
            ("DEBUG", "DEBUG"),  # Already uppercase
            ("Info", "INFO"),    # Mixed case
        ]

        for input_level, expected in test_cases:
            s = Settings(log_level=input_level)
            assert s.log_level == expected

    def test_invalid_log_level(self):
        """Should reject invalid log level."""
        with pytest.raises(ValidationError) as exc_info:
            Settings(log_level="trace")

        error = exc_info.value.errors()[0]
        assert error["type"] == "value_error"
        assert "log_level must be one of" in str(error["ctx"]["error"])

    def test_is_production_property(self):
        """Should return True only for prod environment."""
        test_cases = [
            ("prod", True),
            ("dev", False),
            ("staging", False),
            ("test", False),
        ]

        for env, expected in test_cases:
            s = Settings(environment=env)
            assert s.is_production is expected

    def test_max_upload_size_bytes_property(self):
        """Should convert MB to bytes correctly."""
        s = Settings(max_upload_size_mb=10)
        assert s.max_upload_size_bytes == 10 * 1024 * 1024

        # Test with default
        s = Settings()
        assert s.max_upload_size_bytes == 500 * 1024 * 1024

    def test_max_merge_size_bytes_property(self):
        """Should convert merge MB to bytes correctly."""
        s = Settings(max_merge_size_mb=100)
        assert s.max_merge_size_bytes == 100 * 1024 * 1024

    def test_sql_connection_string_with_client_id(self):
        """Should build valid connection string with client ID."""
        s = Settings(
            azure_sql_server="test.database.windows.net",
            azure_sql_database="testdb",
            azure_client_id="test-client-id"
        )
        conn = s.sql_connection_string

        assert "test.database.windows.net" in conn
        assert "testdb" in conn
        assert "ODBC Driver 18" in conn
        assert "UID=test-client-id" in conn
        assert "Authentication=ActiveDirectoryManagedIdentity" in conn
        assert "Encrypt=yes" in conn
        assert "TrustServerCertificate=no" in conn

    def test_sql_connection_string_without_client_id(self):
        """Should build connection string without UID when no client ID."""
        s = Settings(
            azure_sql_server="test.database.windows.net",
            azure_sql_database="testdb"
        )
        conn = s.sql_connection_string

        assert "test.database.windows.net" in conn
        assert "testdb" in conn
        assert "ODBC Driver 18" in conn
        assert "UID=" not in conn  # Should not include UID part
        assert "Authentication=ActiveDirectoryManagedIdentity" in conn

    def test_azure_authority_commercial(self):
        """Should return commercial authority for commercial cloud."""
        s = Settings(azure_cloud="commercial")
        assert s.azure_authority == "https://login.microsoftonline.com"

    def test_azure_authority_government(self):
        """Should return government authority for government cloud."""
        s = Settings(azure_cloud="government")
        assert s.azure_authority == "https://login.microsoftonline.us"

    def test_azure_authority_other_cloud(self):
        """Should default to commercial authority for unrecognized cloud."""
        s = Settings(azure_cloud="china")  # Not explicitly handled
        assert s.azure_authority == "https://login.microsoftonline.com"

    def test_container_names_defaults(self):
        """Should have expected container name defaults."""
        s = Settings()
        assert s.azure_storage_container_name == "assurancenet-documents"
        assert s.azure_storage_staging_container == "assurancenet-staging"

    def test_cors_origins_default(self):
        """Should have default CORS origins."""
        s = Settings()
        cors_origins = s.cors_origins
        assert "http://localhost:3000" in cors_origins
        assert "http://localhost:5173" in cors_origins
        assert "https://yellow-field-05ae8b90f.2.azurestaticapps.net" in cors_origins

    def test_entra_audience_default(self):
        """Should have default Entra ID audience."""
        s = Settings()
        assert s.entra_audience == "api://4eb00bab-f560-4af0-8116-917abb571891"

    def test_max_merge_files_default(self):
        """Should have default max merge files limit."""
        s = Settings()
        assert s.max_merge_files == 50

    def test_all_properties_accessible(self):
        """Should be able to access all key properties without error."""
        s = Settings(
            environment="prod",
            azure_sql_server="test.database.windows.net",
            azure_sql_database="testdb",
            azure_client_id="test-client"
        )

        # Should not raise any exceptions
        _ = s.is_production
        _ = s.max_upload_size_bytes
        _ = s.max_merge_size_bytes
        _ = s.azure_authority
        _ = s.sql_connection_string