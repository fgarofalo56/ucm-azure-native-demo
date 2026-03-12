"""FastAPI dependency injection - Azure SDK clients and services."""

from functools import lru_cache

from azure.identity import DefaultAzureCredential, ManagedIdentityCredential
from azure.keyvault.secrets import SecretClient
from azure.storage.blob import BlobServiceClient

from app.config import Settings, settings


@lru_cache
def get_settings() -> Settings:
    return settings


def get_azure_credential() -> DefaultAzureCredential | ManagedIdentityCredential:
    """Get Azure credential based on environment.

    Uses ManagedIdentityCredential in production (faster),
    DefaultAzureCredential in dev (supports local dev auth).
    """
    if settings.is_production and settings.azure_client_id:
        return ManagedIdentityCredential(client_id=settings.azure_client_id)
    return DefaultAzureCredential()


def get_blob_service_client() -> BlobServiceClient:
    """Get Azure Blob Storage client."""
    credential = get_azure_credential()
    account_url = f"https://{settings.azure_storage_account_name}.blob.core.windows.net"
    return BlobServiceClient(account_url=account_url, credential=credential)


def get_key_vault_client() -> SecretClient:
    """Get Azure Key Vault client."""
    credential = get_azure_credential()
    return SecretClient(vault_url=settings.azure_key_vault_uri, credential=credential)
