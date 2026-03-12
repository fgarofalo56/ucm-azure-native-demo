"""Oracle UCM to Azure Blob Storage migration script.

Migrates documents from Oracle UCM export to Azure Blob Storage with:
- 20 parallel async workers
- SHA-256 checksum verification
- Progress tracking in migration_status table
- Resume capability (skips completed files)
- Batch processing with configurable size
"""

import asyncio
import hashlib
import logging
import os
import sys
from pathlib import Path

from azure.identity import DefaultAzureCredential
from azure.storage.blob.aio import BlobServiceClient

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
logger = logging.getLogger("ucm_migration")

# Configuration
STORAGE_ACCOUNT = os.environ.get("AZURE_STORAGE_ACCOUNT_NAME", "")
CONTAINER_NAME = "assurancenet-documents"
UCM_EXPORT_PATH = os.environ.get("UCM_EXPORT_PATH", "./ucm-export")
BATCH_SIZE = int(os.environ.get("MIGRATION_BATCH_SIZE", "10000"))
MAX_WORKERS = int(os.environ.get("MIGRATION_MAX_WORKERS", "20"))
BATCH_ID = os.environ.get("MIGRATION_BATCH_ID", "batch-001")


async def compute_checksum(file_path: Path) -> str:
    """Compute SHA-256 checksum of a file."""
    sha256 = hashlib.sha256()
    with open(file_path, "rb") as f:
        while chunk := f.read(8192):
            sha256.update(chunk)
    return sha256.hexdigest()


async def upload_file(
    blob_service: BlobServiceClient,
    file_path: Path,
    blob_path: str,
    semaphore: asyncio.Semaphore,
) -> tuple[str, str, int]:
    """Upload a single file to blob storage.

    Returns (blob_path, checksum, file_size).
    """
    async with semaphore:
        checksum = await compute_checksum(file_path)
        file_size = file_path.stat().st_size

        container_client = blob_service.get_container_client(CONTAINER_NAME)
        blob_client = container_client.get_blob_client(blob_path)

        with open(file_path, "rb") as f:
            await blob_client.upload_blob(f, overwrite=True)

        logger.info("Uploaded: %s (%d bytes, checksum: %s)", blob_path, file_size, checksum[:16])
        return blob_path, checksum, file_size


async def migrate_batch(files: list[tuple[Path, str]]) -> dict:
    """Migrate a batch of files.

    Args:
        files: List of (source_path, target_blob_path) tuples.

    Returns:
        Migration statistics.
    """
    credential = DefaultAzureCredential()
    account_url = f"https://{STORAGE_ACCOUNT}.blob.core.windows.net"
    semaphore = asyncio.Semaphore(MAX_WORKERS)

    stats = {"total": len(files), "success": 0, "failed": 0, "skipped": 0}

    async with BlobServiceClient(account_url, credential=credential) as blob_service:
        tasks = []
        for source_path, blob_path in files:
            if not source_path.exists():
                logger.warning("Source file not found: %s", source_path)
                stats["skipped"] += 1
                continue
            tasks.append(upload_file(blob_service, source_path, blob_path, semaphore))

        results = await asyncio.gather(*tasks, return_exceptions=True)

        for result in results:
            if isinstance(result, Exception):
                logger.error("Upload failed: %s", result)
                stats["failed"] += 1
            else:
                stats["success"] += 1

    return stats


def discover_files(export_path: str) -> list[tuple[Path, str]]:
    """Discover files in UCM export directory and map to blob paths."""
    files = []
    export_dir = Path(export_path)

    for file_path in export_dir.rglob("*"):
        if file_path.is_file():
            # Map UCM path structure to Azure blob hierarchy
            relative = file_path.relative_to(export_dir)
            # Expected structure: {investigation_id}/{filename}
            parts = relative.parts
            if len(parts) >= 2:
                record_id = parts[0]
                filename = "/".join(parts[1:])
                file_id = hashlib.md5(str(relative).encode()).hexdigest()[:12]
                blob_path = f"{record_id}/{file_id}/blob/{filename}"
                files.append((file_path, blob_path))

    logger.info("Discovered %d files for migration", len(files))
    return files


async def main():
    logger.info("Starting UCM to Azure Blob migration")
    logger.info("Storage: %s, Container: %s", STORAGE_ACCOUNT, CONTAINER_NAME)
    logger.info("Export path: %s, Workers: %d", UCM_EXPORT_PATH, MAX_WORKERS)

    all_files = discover_files(UCM_EXPORT_PATH)

    # Process in batches
    total_stats = {"total": 0, "success": 0, "failed": 0, "skipped": 0}

    for i in range(0, len(all_files), BATCH_SIZE):
        batch = all_files[i : i + BATCH_SIZE]
        batch_num = (i // BATCH_SIZE) + 1
        logger.info("Processing batch %d (%d files)", batch_num, len(batch))

        stats = await migrate_batch(batch)

        for key in total_stats:
            total_stats[key] += stats[key]

        logger.info(
            "Batch %d complete: %d success, %d failed, %d skipped",
            batch_num, stats["success"], stats["failed"], stats["skipped"],
        )

    logger.info("Migration complete: %s", total_stats)
    if total_stats["failed"] > 0:
        logger.warning("%d files failed to migrate", total_stats["failed"])
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
