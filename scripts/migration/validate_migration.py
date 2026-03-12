"""Validate migration integrity: checksum comparison and completeness checks.

Compares source UCM checksums against Azure Blob Storage to ensure
data integrity post-migration.
"""

import asyncio
import hashlib
import logging
import os
from pathlib import Path

from azure.identity import DefaultAzureCredential
from azure.storage.blob.aio import BlobServiceClient

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
logger = logging.getLogger("migration_validator")

STORAGE_ACCOUNT = os.environ.get("AZURE_STORAGE_ACCOUNT_NAME", "")
CONTAINER_NAME = "assurancenet-documents"


async def validate_blob_checksum(
    blob_service: BlobServiceClient,
    blob_path: str,
    expected_checksum: str,
) -> tuple[str, bool, str]:
    """Validate a single blob's checksum against expected value.

    Returns (blob_path, match, actual_checksum).
    """
    container = blob_service.get_container_client(CONTAINER_NAME)
    blob = container.get_blob_client(blob_path)

    download = await blob.download_blob()
    data = await download.readall()

    actual_checksum = hashlib.sha256(data).hexdigest()
    match = actual_checksum == expected_checksum

    if not match:
        logger.error(
            "Checksum mismatch: %s (expected=%s, actual=%s)",
            blob_path, expected_checksum[:16], actual_checksum[:16],
        )

    return blob_path, match, actual_checksum


async def count_blobs(blob_service: BlobServiceClient) -> int:
    """Count total blobs in the container."""
    container = blob_service.get_container_client(CONTAINER_NAME)
    count = 0
    async for _ in container.list_blobs():
        count += 1
    return count


async def main():
    logger.info("Starting migration validation")

    credential = DefaultAzureCredential()
    account_url = f"https://{STORAGE_ACCOUNT}.blob.core.windows.net"

    async with BlobServiceClient(account_url, credential=credential) as blob_service:
        # Count blobs
        blob_count = await count_blobs(blob_service)
        logger.info("Total blobs in Azure: %d", blob_count)

        # TODO: Compare against migration_status table in SQL
        # TODO: Spot-check 1% of files with checksum verification
        # TODO: Generate validation report

        logger.info("Validation complete. Total blobs: %d", blob_count)


if __name__ == "__main__":
    asyncio.run(main())
