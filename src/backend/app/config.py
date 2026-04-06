"""Application configuration using pydantic-settings."""

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
    )

    # Environment
    environment: str = "dev"

    # Azure Identity
    azure_client_id: str = ""
    azure_tenant_id: str = ""

    # Azure Storage
    azure_storage_account_name: str = ""
    azure_storage_container_name: str = "assurancenet-documents"
    azure_storage_staging_container: str = "assurancenet-staging"

    # PDF conversion engine: "aspose" (default/production) or "gotenberg" (demo fallback)
    pdf_engine: str = "aspose"

    # Azure SQL
    azure_sql_server: str = ""
    azure_sql_database: str = ""

    # Azure Key Vault
    azure_key_vault_uri: str = ""

    # Entra ID Authentication
    entra_tenant_id: str = ""
    entra_client_id: str = ""
    entra_audience: str = "api://4eb00bab-f560-4af0-8116-917abb571891"

    # Application Insights
    applicationinsights_connection_string: str = ""

    # Cloud Environment
    azure_cloud: str = "commercial"
    azure_authority_host: str = "https://login.microsoftonline.com"

    # CORS
    cors_origins: str = (
        "http://localhost:3000,http://localhost:5173,https://yellow-field-05ae8b90f.2.azurestaticapps.net"
    )

    # Application limits
    max_upload_size_mb: int = 500
    max_merge_files: int = 50
    max_merge_size_mb: int = 500
    log_level: str = "INFO"

    @property
    def max_upload_size_bytes(self) -> int:
        return self.max_upload_size_mb * 1024 * 1024

    @property
    def max_merge_size_bytes(self) -> int:
        return self.max_merge_size_mb * 1024 * 1024

    @property
    def is_production(self) -> bool:
        return self.environment == "prod"

    @property
    def azure_authority(self) -> str:
        if self.azure_cloud == "government":
            return "https://login.microsoftonline.us"
        return "https://login.microsoftonline.com"

    @property
    def sql_connection_string(self) -> str:
        """Build ODBC connection string for Azure SQL with Entra ID auth."""
        driver = "{ODBC Driver 18 for SQL Server}"
        uid_part = f"UID={self.azure_client_id};" if self.azure_client_id else ""
        return (
            f"Driver={driver};"
            f"Server=tcp:{self.azure_sql_server},1433;"
            f"Database={self.azure_sql_database};"
            "Encrypt=yes;"
            "TrustServerCertificate=no;"
            "Connection Timeout=30;"
            "Authentication=ActiveDirectoryManagedIdentity;"
            f"{uid_part}"
        )


settings = Settings()
