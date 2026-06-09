# Migrated Archon v1 Tasks - AssuranceNet Document Management System

> Frozen export 2026-05-14 during the de-Archon-v1 migration.
> **Archon project ID**: `1669d737-93fd-45de-b38b-ce8d5177dcb7`
> **Total tasks captured**: 13

Archon v1 was archived 2026-04. Going forward use TodoWrite (in-session) +
GitHub Issues on fgarofalo56/ucm-azure-native-demo (cross-session).

## status: todo (5)

### Phase 2: Blob Layout Normalization
_order: 70 . feature: phase-2-blob-layout . id: `a8f5dc85-ab47-4411-8283-d7a59b5767e3`_

Versioned blob paths in BlobService.build_blob_path() and build_pdf_path(). Already implemented as part of Phase 1 BlobService refactor. Path format: /{record_id}/{documentId}/original/v{N}/{filename}

### Phase 3: Merge Rule Enforcement
_order: 64 . feature: phase-3-merge-rules . id: `de352d07-5717-40b2-806f-d07b4887b5dc`_

Type-based merge ordering via MERGE_ORDER_CONFIG. Already implemented in pdf_merge.py refactor. Documents sorted by document_type before merge. Latest versions only.

### Phase 6: Admin Rollback APIs
_order: 58 . feature: phase-6-rollback . id: `fd483e2d-274b-4f08-a65c-35fc53485f53`_

Admin rollback endpoint, version listing, version download. Already implemented in admin.py refactor. POST /api/admin/documents/{id}/rollback, GET versions, GET version download.

### Phase 7: IaC Cleanup & Feature Flags
_order: 46 . feature: phase-7-iac . id: `cfd8d3e2-65d4-45a3-a35e-a4e9ad457596`_

Added enableMalwareScanning and deployDefender feature flags to main.bicep. Added staging container to storage module (conditional). Made Defender module conditional. Added parameter docs.

### Frontend: Update for versioned API contract
_order: 40 . feature: phase-1-versioning . id: `88d4b1e6-0a5a-47a5-8c6b-ce5cd8304b3d`_

Updated all frontend types, API client, components, and pages for the new Document/DocumentVersion model. types.ts, documents.ts, DocumentList, DocumentViewer, VersionHistory, PdfMerge, InvestigationPage all updated. TypeScript compiles clean.

## status: done (8)

### Phase 1.1: DocumentType enum + DocumentVersion ORM model
_order: 105 . feature: phase-1-versioning . id: `71850805-a623-4e04-ab0c-866f6880162d`_

Add DocumentType enum to enums.py. Add DocumentVersion ORM model to db/models.py. Modify Document model to add document_type, title, current_version_id. Add ScanStatus enum for malware scanning.

### Phase 1.2: Alembic migration 003 - versioning schema
_order: 99 . feature: phase-1-versioning . id: `9c4391f0-a6ca-4012-8859-79ccc9852046`_

Create Alembic migration 003 that adds document_versions table, adds document_type/title/current_version_id to documents, adds reviewer role permissions. Fresh seed data with USDA sources.

### Phase 1.3: Version-aware Pydantic schemas
_order: 93 . feature: phase-1-versioning . id: `6833067d-7a16-44f4-b181-b7e3ca9de65b`_

Update schemas.py with version-aware request/response models. Add DocumentVersionResponse with version details. Update DocumentResponse to include latest version info. Add admin-specific schemas.

### Phase 1.4: MetadataService + BlobService refactor
_order: 87 . feature: phase-1-versioning . id: `256c93c0-6222-4cc5-9c06-b593790160f7`_

Refactor MetadataService for version-aware CRUD. Add create_document_version, get_latest_version, list_versions_for_document. Update BlobService with versioned paths. Update config.py with new settings.

### Phase 1.5: Refactor API endpoints for versioning
_order: 81 . feature: phase-1-versioning . id: `106c0661-52fd-4780-8439-bcbe23d3e7a7`_

Refactor documents.py for version-aware upload/download/list. Update admin.py with version listing + rollback. Update investigations.py for latest-only document listing. Restrict explorer.py to admin. Update pdf_merge.py for latest-only.

### Phase 1.6: USDA seed data with actual files
_order: 75 . feature: phase-1-versioning . id: `0e3f7bba-c796-4c88-9a7e-bf2a73fd6a1a`_

Create seed data script using actual USDA/FSIS investigation data. Generate realistic document records for 8 investigations. Include multiple document types per investigation.

### Phase 4: PDF Engine Abstraction (PdfConverter protocol)
_order: 70 . feature: phase-4-pdf-engine . id: `8749e9da-79bc-4fcb-ab5f-635072f40335`_

Create PdfConverter protocol interface. Wrap Gotenberg behind GotenbergConverter adapter. Add config-driven engine selection via PDF_ENGINE env var. Create factory function.

### Phase 5: Malware Scanning Pipeline
_order: 50 . feature: phase-5-malware-scan . id: `037cc5cb-50cf-4aa2-9447-ae3ced35b5d0`_

Add staging container to Bicep storage module. Add scan_status tracking to document versions. Update upload endpoints for two-phase flow. Add upload status polling endpoint. Feature-flag Defender for Storage in Bicep.
