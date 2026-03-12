[Home](../../README.md) > [Architecture](.) > **Data Migration Strategy**

# Data Migration Strategy

> **TL;DR:** Migration of ~700,000 files (~1.7TB) from Oracle UCM to Azure Blob Storage + SQL, executed over 8 weeks in six phases: assessment, infrastructure, pilot (10K files), full migration (20 async workers), validation (100% checksum), and cutover with 30-day parallel run.

---

## Table of Contents

- [Overview](#overview)
- [Phases](#phases)
- [FSIS Document Types for Migration](#fsis-document-types-for-migration)
- [Rollback](#rollback)

---

## 📋 Overview

Migration of ~700,000 files (~1.7TB) from Oracle UCM to Azure Blob Storage + SQL.

---

## 🏗️ Phases

### 🏗️ Phase 1: Assessment (Week 1-2)

- Inventory UCM content: types, sizes, metadata
- Map UCM fields to Azure SQL schema
- Identify duplicates via checksum dedup

### 🏗️ Phase 2: Infrastructure (Week 2-3)

- Deploy Azure resources via Bicep (dev first)
- Validate networking, Private Endpoints, MI access

### 🏗️ Phase 3: Pilot (Week 3-4)

- Migrate 10,000 representative files
- Validate integrity (SHA-256), metadata, PDF conversion
- Target: >=1,000 files/hour throughput

### 📦 Phase 4: Full Migration (Week 4-6)

| Parameter | Value |
|-----------|-------|
| Script | `migrate_ucm_to_blob.py` |
| Workers | 20 async workers |
| Batch size | 10,000 files |
| Estimated duration | ~35 hours for 700K files |
| Resume capability | Via `migration_status` table |

> [!IMPORTANT]
> The migration script supports resume from the last successful batch. If interrupted, re-running the script will skip already-migrated files based on the `migration_status` table.

### ✨ Phase 5: Validation (Week 6-7)

- `validate_migration.py` for 100% checksum verification
- 1% spot-check (7,000 files)
- Metadata completeness report

### 📦 Phase 6: Cutover (Week 7-8)

- Switch to Azure backend
- 30-day parallel run with UCM read-only
- Final sign-off and UCM decommission

> [!WARNING]
> UCM must remain read-only (not decommissioned) during the 30-day parallel run period. This is the rollback window.

---

## 🗄️ FSIS Document Types for Migration

Based on the FSIS Science & Data portal ([fsis.usda.gov/science-data](https://www.fsis.usda.gov/science-data)),
the following document categories are expected in the UCM migration:

| Category | Est. Volume | Formats | Notes |
|---|---|---|---|
| Annual Sampling Plans | ~20/year | PDF | FY2014-FY2025+ |
| Laboratory Sampling Data | ~50 datasets | CSV | Updated quarterly/annually |
| National Residue Program | ~100 reports | PDF | Red Book, Blue Book, quarterly |
| Microbiology Baseline Reports | ~50 reports | PDF | Per species/commodity |
| Quarterly Sampling Reports | ~200 reports | PDF, CSV | Salmonella, Campylobacter, AMR, STEC |
| MPI Establishment Directories | ~10 files | CSV | Updated periodically |
| Inspection Task Data | ~100 datasets | CSV | Humane handling, enforcement |
| Chemical Residue Tolerances | ~100 reports | PDF | Quarterly summaries |
| Enforcement Reports | ~50 reports | PDF | Quarterly tables |
| Investigation Documents | ~700,000 files | Mixed | Primary migration volume |

### ✨ Demo Data for Validation

For pilot migration validation, use sample files from the FSIS public data portal:

| File Type | Document | URL |
|-----------|----------|-----|
| CSV | MPI Directory by Establishment Number | [Download](https://www.fsis.usda.gov/sites/default/files/media_file/documents/MPI_Directory_by_Establishment_Number.csv) |
| CSV | MPI Directory by Establishment Name | [Download](https://www.fsis.usda.gov/sites/default/files/media_file/documents/MPI_Directory_by_Establishment_Name.csv) |
| PDF | Annual Sampling Plan FY2025 | [Download](https://www.fsis.usda.gov/sites/default/files/media_file/documents/FSIS-Annual-Sampling-Plan-FY2025.pdf) |
| PDF | Sampling Summary Report FY2024 | [Download](https://www.fsis.usda.gov/sites/default/files/media_file/documents/FY2024A_Sampling%20Summary%20Report.pdf) |

---

## 📦 Rollback

| Mechanism | Details |
|-----------|---------|
| Blob soft delete | 30-day retention window |
| SQL restore | Point-in-time restore capability |
| Batch removal | `rollback_migration.py` for bulk cleanup |
| Parallel run | UCM remains read-only during cutover period |

> [!NOTE]
> The rollback strategy ensures zero data loss. Blob soft delete and SQL point-in-time restore provide independent recovery paths for storage and metadata respectively.

---

**Related Architecture Docs:**
[High-Level Architecture](high-level-architecture.md) | [Azure Architecture Detail](azure-architecture-detail.md) | [Workflow Diagrams](workflow-diagrams.md) | [Blob Hierarchy](blob-hierarchy.md) | [Security Architecture](security-architecture.md) | [Monitoring & Telemetry](monitoring-telemetry.md)
