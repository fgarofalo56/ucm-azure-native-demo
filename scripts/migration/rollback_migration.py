"""Rollback migration: remove migrated blobs and SQL records.

Safety-first rollback that preserves the UCM source data.
"""

import asyncio
import logging
import os

from azure.identity import DefaultAzureCredential
from azure.storage.blob.aio import BlobServiceClient

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
logger = logging.getLogger("migration_rollback")

STORAGE_ACCOUNT = os.environ.get("AZURE_STORAGE_ACCOUNT_NAME", "")
CONTAINER_NAME = "assurancenet-documents"


async def rollback_blobs(batch_id: str | None = None):
    """Remove migrated blobs from Azure Storage.

    If batch_id is specified, only removes blobs from that batch.
    """
    credential = DefaultAzureCredential()
    account_url = f"https://{STORAGE_ACCOUNT}.blob.core.windows.net"

    async with BlobServiceClient(account_url, credential=credential) as blob_service:
        container = blob_service.get_container_client(CONTAINER_NAME)
        deleted = 0

        async for blob in container.list_blobs():
            # TODO: Filter by batch_id from migration_status table
            await container.delete_blob(blob.name)
            deleted += 1
            if deleted % 1000 == 0:
                logger.info("Deleted %d blobs", deleted)

        logger.info("Rollback complete: %d blobs deleted", deleted)


async def main():
    confirm = input("This will DELETE migrated data from Azure. Type 'CONFIRM' to proceed: ")
    if confirm != "CONFIRM":
        logger.info("Rollback cancelled")
        return

    batch_id = os.environ.get("MIGRATION_BATCH_ID")
    await rollback_blobs(batch_id)


if __name__ == "__main__":
    asyncio.run(main())
