# Product Requirements Planning (PRP)
## AssuranceNet – Oracle UCM to Azure Native Migration: Demo Enhancements & Refactoring

**Version:** 1.1
**Date:** 2026-03-17
**Author:** FSIS Engineering / Cloud Architecture Team
**Status:** Draft

---

## 1. Executive Summary

### 1.1 Problem Statement

The current AssuranceNet demo application proves Azure-native document management as a replacement for Oracle UCM, but it conflates file identity with version identity, allows users to see all document versions (contrary to FSIS requirements), uses UI-driven assumptions that prevent SDK/server-side consumption, and lacks critical federal security controls like malware scanning and deterministic RBAC enforcement.

### 1.2 Proposed Solution

Refactor the demo to implement an explicit document versioning model separated into logical documents and immutable physical versions, enforce latest-only visibility for end users, introduce a two-phase upload pipeline with malware scanning, abstract the PDF conversion engine for future Aspose integration, enforce rule-based merge ordering by document type, and harden RBAC at the API middleware layer — all while ensuring the React UI remains a removable reference client.

### 1.3 Success Metrics

| Metric | Target |
|--------|--------|
| UCM functional parity proven | 100% of FSIS document lifecycle requirements met |
| React UI removable | All APIs fully consumable by SDK/JSP without frontend dependency |
| Explicit versioning | Logical document + immutable physical versions model in place |
| Federal security controls | Malware scanning, RBAC enforcement, private endpoints operational |
| PDF engine swappable | Gotenberg → Aspose swap with zero frontend/API changes |
| Blob + SQL consistency | Zero silent drift between blob storage and metadata |

---

## 2. Background & Context

### 2.1 Current State

AssuranceNet is an Azure-native document management system built to demonstrate Oracle UCM replacement for FSIS. The current POC:

- **Backend**: FastAPI (Python 3.11+) with SQLAlchemy ORM on Azure SQL
- **Frontend**: React 18 + TypeScript SPA on Azure Static Web Apps
- **Storage**: Azure Blob Storage with implicit GUID-based blob versioning
- **PDF Pipeline**: Azure Functions + Event Grid + Gotenberg
- **Auth**: Microsoft Entra ID (MSAL) with basic RBAC
- **Infrastructure**: 16+ Bicep modules on Azure

The demo currently has 8 FSIS investigations seeded with 10 document metadata records. It supports document upload, download, PDF conversion, merge, audit logging, and blob explorer functionality.

### 2.2 Pain Points

1. **Version conflation**: The `Document` model holds both logical identity and physical binary metadata in one record. There is no `DocumentVersion` entity — versioning relies on Azure Blob Storage's built-in blob versioning, which exposes all versions to any user.

2. **All-versions visibility**: Current APIs (`/documents/{id}/versions`) expose every blob version to end users. FSIS requires latest-only visibility with admin-controlled rollback.

3. **Name-based blob discovery**: Blob paths use `{record_id}/{file_id}/blob/{filename}`, allowing filename-based retrieval. FSIS requires structure-driven, metadata-first retrieval.

4. **UI-coupled architecture**: React-specific patterns in API design (explorer, UI-driven merge ordering) prevent SDK and server-side JSP consumption.

5. **No malware scanning**: Uploaded files go directly to the production storage container. No staging or scanning pipeline exists.

6. **Permissive RBAC**: Roles exist (`viewer`, `document_manager`, `admin`) but enforcement is per-endpoint, not centralized. No role-based visibility filtering.

7. **Hardcoded PDF engine**: Gotenberg is directly integrated in Azure Functions. No abstraction layer for swapping to Aspose.

8. **Flat merge logic**: PDF merge accepts arbitrary user-ordered file lists. No rule-based ordering by document type.

### 2.3 FSIS Requirements Source

All requirements derive from the Oracle UCM demo review session where FSIS stakeholders explicitly stated:
- Users should only see the latest version
- Rollback is an admin workflow, not user self-service
- Structure-driven retrieval, not name-based discovery
- React UI will NOT be used in production — architecture must stand alone
- Merge order is rule-based by document type, not user-selected
- Aspose is required in production (Gotenberg for demo only)
- Malware scanning is mandatory for federal document systems

---

## 3. Goals & Objectives

### 3.1 Business Goals

| Goal | Metric | Target | Timeline |
|------|--------|--------|----------|
| Prove UCM parity | FSIS feature checklist | 100% coverage | Phase 7 completion |
| Demonstrate production readiness | Architecture patterns | Federal-grade security defaults | Phase 5 |
| Enable non-React consumers | API contract | SDK-consumable without UI | Phase 2 |
| Prove PDF engine portability | Engine swap test | Zero-downtime swap | Phase 4 |

### 3.2 User Goals

- As an **investigator**, I want to see only the latest version of each document so that I work with current information without confusion from historical revisions.
- As an **investigator**, I want to upload documents knowing they're scanned for malware so that I trust the system handles security automatically.
- As a **document manager**, I want merged PDFs to follow rule-based ordering by document type so that output is consistent regardless of who triggers the merge.
- As an **admin**, I want to roll back a document to a previous version via API so that I can correct mistakes through a controlled ticketed workflow.
- As an **SDK consumer**, I want to retrieve documents by metadata query (not blob listing) so that I can integrate the system without a web UI.

### 3.3 Non-Goals

- End-user version history UI (explicitly forbidden by FSIS)
- Blob browser / name-based discovery for end users
- Filename-based document identification logic
- UI polish or feature expansion beyond document lifecycle
- Production deployment (this is demo-only, but architecture must be production-correct)

---

## 4. User Stories & Requirements

### 4.1 User Personas

#### Persona 1: FSIS Investigator
- **Role:** Federal food safety investigator
- **Goals:** Upload, view, and download investigation documents quickly
- **Pain Points:** Seeing multiple versions causes confusion; needs only the latest
- **Tech Savviness:** Medium (may use JSP-based UI, not React)

#### Persona 2: Document Manager
- **Role:** Investigation support staff managing document workflows
- **Goals:** Merge documents into case packages, manage document types
- **Pain Points:** Inconsistent merge ordering; no type-based rules
- **Tech Savviness:** Medium

#### Persona 3: System Administrator
- **Role:** IT/ops managing the platform
- **Goals:** Roll back bad uploads, manage user roles, audit activity
- **Pain Points:** No admin rollback API; RBAC is permissive
- **Tech Savviness:** High

#### Persona 4: SDK/Integration Developer
- **Role:** Developer building server-side consumers (JSP, SDK)
- **Goals:** Consume document APIs without any UI dependency
- **Pain Points:** Current API assumes React client; blob listing for discovery
- **Tech Savviness:** High

### 4.2 User Stories

#### Epic 1: Document Versioning Model

**US-001: Explicit Logical Document with Physical Versions**
- **As a** system architect
- **I want to** separate Document (logical identity) from DocumentVersion (physical binary)
- **So that** versioning is explicit, immutable, and aligns with FSIS metadata-first requirements

**Acceptance Criteria:**
- [ ] Given a new upload of a file, when the system creates a record, then both a `Document` (logical) and a `DocumentVersion` (physical) record are created
- [ ] Given a re-upload of an existing document (same logical document), when a new version is uploaded, then a new `DocumentVersion` is created and the previous version's `is_latest` is set to false
- [ ] Given any API call, when no version filter is specified, then only the latest version of each document is returned
- [ ] Given a `DocumentVersion`, when inspecting its record, then it contains `version_id`, `document_id`, `version_number`, `blob_path_original`, `blob_path_pdf`, `uploaded_at`, `uploaded_by`, `is_latest`, `checksum`, and `mime_type`

**Priority:** P0
**Story Points:** 13

---

**US-002: Latest-Only Default Visibility**
- **As an** investigator
- **I want to** see only the latest version of each document
- **So that** I am not confused by historical revisions

**Acceptance Criteria:**
- [ ] Given a document with 3 versions, when an investigator calls `GET /api/investigations/{id}/documents`, then only the latest version data is returned
- [ ] Given an admin, when calling a dedicated admin versions endpoint, then all versions are visible
- [ ] Given a document with versions deleted by admin, when fetching documents, then the promoted prior version is shown

**Priority:** P0
**Story Points:** 5

---

#### Epic 2: Deterministic Blob Storage Layout

**US-003: Versioned Blob Directory Structure**
- **As a** system architect
- **I want to** store documents in `/{INVESTIGATION-ID}/{documentId}/original/v{N}/` and `/{INVESTIGATION-ID}/{documentId}/pdf/v{N}/`
- **So that** blob layout is deterministic, version-aware, and SDK-retrievable

**Acceptance Criteria:**
- [ ] Given a new upload, when the blob is stored, then the path follows `/INVESTIGATION-{ID}/{documentId}/original/v{N}/{filename}`
- [ ] Given a PDF conversion, when the PDF is stored, then the path follows `/INVESTIGATION-{ID}/{documentId}/pdf/v{N}/{filename}.pdf`
- [ ] Given SDK retrieval, when querying by document ID and version, then only the correct version blob is returned
- [ ] Given older versions, when queried by admin tooling, then they remain addressable

**Priority:** P0
**Story Points:** 8

---

#### Epic 3: PDF Merge Rules

**US-004: Rule-Based Merge Ordering by Document Type**
- **As a** document manager
- **I want to** merge PDFs with ordering determined by document type rules
- **So that** output is consistent and compliant regardless of selection order

**Acceptance Criteria:**
- [ ] Given documents of types A, B, C with a predefined order, when merged, then the output follows the type-based order regardless of input sequence
- [ ] Given a merge request with documents from different versions, when the merge executes, then only latest versions are included
- [ ] Given an invalid combination of document types, when a merge is attempted, then the request is rejected with a clear error

**Priority:** P1
**Story Points:** 8

---

#### Epic 4: Pluggable PDF Conversion Engine

**US-005: Abstract PDF Conversion Interface**
- **As an** operations team member
- **I want to** swap the PDF conversion engine from Gotenberg to Aspose via configuration
- **So that** engine replacement requires no code deployment or architecture change

**Acceptance Criteria:**
- [ ] Given a `PdfConverter` abstract interface, when Gotenberg is configured, then Gotenberg handles all conversions
- [ ] Given Aspose is configured, when a document is uploaded, then Aspose handles conversion with identical output
- [ ] Given any engine, when a MIME type is provided, then routing works identically
- [ ] Given an engine swap, when no frontend redeployment occurs, then functionality is unaffected

**Priority:** P1
**Story Points:** 8

---

#### Epic 5: Malware Scanning Pipeline

**US-006: Two-Phase Upload with Scanning**
- **As an** investigator
- **I want to** upload documents knowing they are scanned for malware before reaching the production container
- **So that** untrusted files never enter the production storage

**Acceptance Criteria:**
- [ ] Given a file upload, when the file is received, then it is stored in a staging container first
- [ ] Given a staged file, when malware scan completes clean, then the file is automatically promoted to the production container
- [ ] Given a staged file, when malware is detected, then the file is rejected and never reaches production
- [ ] Given the scanning process, when the user uploads, then the experience remains async/non-blocking

**Priority:** P0
**Story Points:** 13

---

#### Epic 6: Admin Version Rollback

**US-007: Admin-Only Version Rollback API**
- **As an** admin
- **I want to** roll back a document to its previous version via API
- **So that** mistakes are corrected through controlled admin workflow

**Acceptance Criteria:**
- [ ] Given a document with versions v1 and v2 (latest), when admin calls `POST /api/admin/documents/{documentId}/rollback`, then v2 is deleted and v1 is promoted to latest
- [ ] Given a rollback, when the audit log is inspected, then the rollback action is immutably recorded
- [ ] Given a rollback, when the binary blobs are inspected, then no binary mutation occurred (v1 blob untouched)
- [ ] Given a document with only one version, when rollback is attempted, then the request is rejected

**Priority:** P1
**Story Points:** 5

---

#### Epic 7: API Contract Refactor

**US-008: Version-Aware API Contract**
- **As an** SDK consumer
- **I want to** interact with separate Document (logical) and DocumentVersion (physical) API resources
- **So that** I can build integrations without UI assumptions

**Acceptance Criteria:**
- [ ] Given a `GET /api/investigations/{id}/documents`, when called, then only logical documents with latest version metadata are returned
- [ ] Given a `GET /api/admin/documents/{id}/versions`, when called by admin, then all versions are returned
- [ ] Given any API, when called without a React frontend, then full functionality is available

**Priority:** P0
**Story Points:** 8

---

#### Epic 8: Hardened RBAC Enforcement

**US-009: Centralized Role Enforcement in Middleware**
- **As a** security architect
- **I want to** enforce RBAC at the API middleware layer with roles: Viewer, DocumentManager, Reviewer, Admin
- **So that** authorization is consistent, centralized, and not dependent on UI

**Acceptance Criteria:**
- [ ] Given a Viewer role, when calling a write endpoint, then the request is denied with 403
- [ ] Given a DocumentManager role, when uploading or merging documents, then the request succeeds
- [ ] Given role enforcement, when bypassing the UI (SDK/curl), then the same rules apply
- [ ] Given an Admin role, when calling rollback or user management, then the request succeeds

**Priority:** P0
**Story Points:** 5

---

#### Epic 9: IaC Refactor

**US-010: Modular Bicep with Feature Flags**
- **As an** infrastructure engineer
- **I want to** deploy core infra separately from optional services (Defender, scanning, Event Grid)
- **So that** I can toggle features cleanly and understand each module

**Acceptance Criteria:**
- [ ] Given a `core-only` deployment, when optional flags are off, then only base resources deploy
- [ ] Given feature flags, when Defender/scanning is enabled, then those modules deploy additively
- [ ] Given any deployment, when run twice, then results are idempotent
- [ ] Given any Bicep module, when inspected, then it has parameter documentation and comments

**Priority:** P2
**Story Points:** 5

---

#### Epic 10: Event-Driven Consistency Checks

**US-011: Blob Event Validation Pipeline**
- **As a** system architect
- **I want to** validate blob events against SQL metadata, version rules, and PDF pairing
- **So that** silent drift between blob storage and database is prevented

**Acceptance Criteria:**
- [ ] Given a blob creation event, when Event Grid fires, then metadata existence is validated
- [ ] Given a blob without a metadata record, when detected, then an alert or compensating action is triggered
- [ ] Given a document upload, when processing completes, then both original and PDF blobs have matching version records

**Priority:** P2
**Story Points:** 8

---

## 5. Functional Requirements

### 5.1 Core Features

#### FR-001: Document Versioning Data Model

**Description:** Refactor the data model to separate logical documents from physical document versions.

**Current State:**
```
Document (single table)
- id, investigation_id, file_id, original_filename
- content_type, file_size_bytes, blob_path, pdf_path
- pdf_conversion_status, blob_version_id, checksum_sha256
- uploaded_by, uploaded_at, is_deleted
```

**Target State:**
```
Document (logical identity)
- document_id (UUID, PK)
- investigation_id (FK)
- document_type (enum)
- title (string)
- created_at, created_by
- current_version_id (FK → DocumentVersion)

DocumentVersion (physical binary)
- version_id (UUID, PK)
- document_id (FK → Document)
- version_number (int, auto-incrementing per document)
- blob_path_original (string)
- blob_path_pdf (string, nullable)
- uploaded_at, uploaded_by
- is_latest (bool)
- checksum (SHA-256)
- mime_type (string)
- file_size_bytes (bigint)
- original_filename (string)
- pdf_conversion_status (enum)
```

**Business Rules:**
- Only one version per document can have `is_latest = true`
- `Document.current_version_id` must always point to the `is_latest` version
- Version numbers auto-increment per logical document (v1, v2, v3...)
- Versions are immutable once created (no updates to binary data)
- Soft-delete on `Document` cascades to all versions
- `original_filename` moves to `DocumentVersion` (same logical doc may have different filenames per version)

**Dependencies:** Alembic migration, all API endpoints, blob service

---

#### FR-002: Deterministic Blob Storage Layout

**Description:** Restructure blob paths to use versioned virtual directories.

**Current Layout:**
```
{record_id}/{file_id}/blob/{filename}
{record_id}/{file_id}/pdf/{filename}.pdf
```

**Target Layout:**
```
/INVESTIGATION-{ID}/{documentId}/original/v{N}/{filename}
/INVESTIGATION-{ID}/{documentId}/pdf/v{N}/{filename}.pdf
```

**Business Rules:**
- New upload = new version directory (v1, v2, ...)
- PDFs are siblings of originals at the same version level
- Filenames are stored as metadata, not used for identity
- Old versions remain addressable by full path
- No blob listing for discovery — all retrieval is metadata-driven

**Dependencies:** FR-001 (versioning model), blob_service.py refactor

---

#### FR-003: PDF Merge with Type-Based Ordering

**Description:** Replace free-form user-ordered merge with document-type-driven rules.

**Current Behavior:** `PdfMergeRequest` accepts `file_ids: list[str]` in user-specified order.

**Target Behavior:**
- Define `MERGE_ORDER_CONFIG: dict[DocumentType, int]` mapping document types to sort positions
- Merge service queries documents, sorts by type order, uses latest versions only
- User-provided ordering is ignored
- Invalid document type combinations raise validation errors

**Business Rules:**
- Only latest versions included in merge
- Order driven by `document_type`, not user selection
- Cross-investigation merges prohibited
- Configuration-driven ordering (not hardcoded)

**Dependencies:** FR-001 (document_type field), pdf_merge_service.py

---

#### FR-004: Pluggable PDF Conversion Engine

**Description:** Abstract PDF conversion behind an interface to support engine swapping.

**Target Interface:**
```python
class PdfConverter(Protocol):
    def supports(self, mime_type: str) -> bool: ...
    async def convert(self, input_data: bytes, mime_type: str) -> bytes: ...
```

**Implementations:**
- `GotenbergConverter` — current engine, wraps HTTP calls to Gotenberg
- `AsposeConverter` — future engine, wraps Aspose SDK calls

**Engine Selection:**
- Environment variable `PDF_ENGINE=gotenberg|aspose`
- Factory pattern at startup: `get_pdf_converter(engine: str) -> PdfConverter`
- Hot-swap via config change + restart (no redeploy)

**Business Rules:**
- MIME-based routing works identically across engines
- Output PDF quality/fidelity must pass comparison validation
- Unsupported MIME types return clear error

**Dependencies:** Azure Functions (`pdf_converter.py`, `conversion_service.py`), `gotenberg_client.py`

---

#### FR-005: Two-Phase Upload with Malware Scanning

**Description:** Introduce a staging container and scan pipeline before production persistence.

**Upload Flow:**
1. User uploads file → stored in `staging` blob container
2. Event Grid triggers malware scan (Microsoft Defender for Storage or custom scanner)
3. **Clean:** File promoted to `production` container, metadata created
4. **Infected:** File deleted from staging, user notified, audit logged
5. Downstream processing (PDF conversion) only triggers after promotion

**Infrastructure:**
- New staging blob container: `assurancenet-staging`
- Event Grid subscription for blob created events on staging
- Azure Function or Logic App for scan orchestration
- Defender for Storage integration (or EICAR test harness for demo)

**Business Rules:**
- Infected files NEVER reach the production container
- Clean files auto-promoted with no user action required
- Upload response returns `202 Accepted` with status polling endpoint
- Audit log records scan results for all uploads

**Dependencies:** Bicep (new staging container, Event Grid), blob_service.py, documents.py

---

#### FR-006: Admin-Only Version Rollback API

**Description:** Provide admin API to delete latest version and promote the prior version.

**Endpoint:** `POST /api/admin/documents/{documentId}/rollback`

**Behavior:**
1. Validate caller has Admin role
2. Fetch latest version for document
3. If only 1 version exists, reject with 400
4. Mark latest version `is_latest = false`
5. Promote version N-1 to `is_latest = true`
6. Update `Document.current_version_id`
7. Audit log the rollback (immutable)
8. Optionally soft-delete the rolled-back version blob

**Business Rules:**
- No UI for end users — admin API only
- Audit trail preserved immutably across all operations
- No binary mutation — only metadata pointer changes
- Rollback is single-step (one version back)

**Dependencies:** FR-001 (versioning model), admin.py, audit_service.py

---

#### FR-007: Hardened RBAC Enforcement

**Description:** Centralize and harden role enforcement at the API middleware layer.

**Roles:**
| Role | Permissions |
|------|------------|
| **Viewer** | Read documents, download, view investigations |
| **DocumentManager** | All Viewer + upload, merge, batch operations |
| **Reviewer** | All Viewer + annotate, comment (future) |
| **Admin** | All permissions + rollback, user management, version access |

**Implementation:**
- Centralized middleware decorator/dependency that maps role → allowed endpoints
- Remove per-endpoint permission string checks in favor of role-based policy
- Enforce at API layer, not UI — SDK/curl calls get identical enforcement
- `Reviewer` role added to existing RBAC tables

**Business Rules:**
- Read-only vs mutable operations strictly separated
- No permission escalation through API crafting
- Audit log all denied access attempts
- Default new users to Viewer role (already implemented)

**Dependencies:** rbac_service.py, auth middleware, Alembic migration for Reviewer role

---

#### FR-008: Metadata-First Retrieval Model

**Description:** Remove all blob-listing-based discovery. All retrieval driven by Azure SQL metadata.

**Changes:**
- Remove or restrict blob explorer endpoint to admin-only
- Remove `list_blob_versions()` for end users — version info comes from `DocumentVersion` table
- Search endpoint queries SQL, not blob storage
- Document listing uses SQL with joins, not blob enumeration

**Business Rules:**
- No blob listing for discovery by end users
- Blob storage is an opaque binary store
- All queries go through Azure SQL indexes
- Explorer remains admin-only diagnostic tool

**Dependencies:** FR-001, documents.py, explorer.py, search.py

---

### 5.2 Feature Matrix

| Feature | Phase 1 | Phase 2 | Phase 3 | Phase 4 | Phase 5 | Phase 6 | Phase 7 | Priority |
|---------|---------|---------|---------|---------|---------|---------|---------|----------|
| Versioning data model | ✓ | | | | | | | P0 |
| Blob layout normalization | | ✓ | | | | | | P0 |
| Merge rule enforcement | | | ✓ | | | | | P1 |
| PDF engine abstraction | | | | ✓ | | | | P1 |
| Malware scanning pipeline | | | | | ✓ | | | P0 |
| Admin rollback APIs | | | | | | ✓ | | P1 |
| IaC cleanup & documentation | | | | | | | ✓ | P2 |
| API contract refactor | ✓ | | | | | | | P0 |
| Metadata-first retrieval | ✓ | ✓ | | | | | | P0 |
| Hardened RBAC | ✓ | | | | | | | P0 |
| Event-driven consistency | | | | | | | ✓ | P2 |

---

## 6. Non-Functional Requirements

### 6.1 Performance

| Metric | Target |
|--------|--------|
| Document upload response (to staging) | < 2s for files ≤ 50MB |
| Document list API (latest-only) | < 200ms for 95th percentile |
| PDF merge (10 documents) | < 30s |
| Malware scan + promote pipeline | < 60s end-to-end |
| Metadata query by investigation | < 100ms |

### 6.2 Security

| Control | Implementation |
|---------|---------------|
| Authentication | Microsoft Entra ID (MSAL) — already in place |
| Authorization | Centralized RBAC middleware (FR-007) |
| Data at rest | Azure Storage encryption (platform-managed keys) |
| Data in transit | TLS 1.2+ everywhere |
| Malware scanning | Two-phase upload (FR-005) |
| Audit logging | Immutable audit trail (already in place) |
| Private endpoints | Azure networking (Bicep modules exist) |
| Managed identities | DefaultAzureCredential (already in place) |

### 6.3 Scalability

| Dimension | Current | Target |
|-----------|---------|--------|
| Concurrent users | Demo (< 10) | Architecture supports 500+ |
| Documents per investigation | ~10 demo records | 10,000+ per investigation |
| Total documents | ~10 demo records | 1M+ documents |
| Blob storage growth | Minimal | 10TB+ capacity |

### 6.4 Reliability

| Metric | Target |
|--------|--------|
| Data consistency (blob + SQL) | Zero silent drift |
| Version pointer accuracy | Always consistent after any operation |
| Audit log completeness | 100% of operations logged |
| Rollback safety | Zero binary mutation |

---

## 7. Technical Specifications

### 7.1 Architecture Overview

```
                    ┌─────────────────┐
                    │   React SPA     │  (Reference client only)
                    │  (removable)    │
                    └────────┬────────┘
                             │
                    ┌────────▼────────┐
                    │   FastAPI       │
                    │   Backend API   │
                    │                 │
                    │ ┌─────────────┐ │
                    │ │ RBAC Middle │ │  Centralized enforcement
                    │ │   ware      │ │
                    │ └─────────────┘ │
                    └──┬─────┬─────┬──┘
                       │     │     │
              ┌────────┘     │     └────────┐
              │              │              │
     ┌────────▼──────┐ ┌────▼─────┐ ┌──────▼───────┐
     │  Azure SQL    │ │ Staging  │ │  Production  │
     │  (Metadata)   │ │  Blob    │ │    Blob      │
     │               │ │Container │ │  Container   │
     │ Document      │ └────┬─────┘ └──────────────┘
     │ DocumentVer   │      │              ▲
     │ AuditLog      │      │              │
     └───────────────┘ ┌────▼─────┐        │
                       │ Malware  │ ─ OK ──┘
                       │  Scan    │
                       └────┬─────┘
                            │ FAIL
                       ┌────▼─────┐
                       │ Quarant  │
                       │  ine     │
                       └──────────┘

     ┌──────────────────────────────────┐
     │     Azure Functions              │
     │  ┌──────────┐  ┌──────────────┐  │
     │  │PdfConvert│  │  Event Grid  │  │
     │  │ Engine   │  │  Consistency │  │
     │  │(abstract)│  │   Checks     │  │
     │  └──────────┘  └──────────────┘  │
     └──────────────────────────────────┘
```

### 7.2 API Specifications

#### Document Lifecycle APIs

| Endpoint | Method | Description | Roles |
|----------|--------|-------------|-------|
| `/api/investigations/{id}/documents` | POST | Upload document (staging → scan → promote) | DocumentManager, Admin |
| `/api/investigations/{id}/documents` | GET | List documents (latest versions only) | Viewer, DocumentManager, Reviewer, Admin |
| `/api/documents/{documentId}` | GET | Get single document (latest version metadata) | Viewer, DocumentManager, Reviewer, Admin |
| `/api/documents/{documentId}/download` | GET | Download latest version binary | Viewer, DocumentManager, Reviewer, Admin |
| `/api/documents/{documentId}/pdf` | GET | Download latest PDF version | Viewer, DocumentManager, Reviewer, Admin |
| `/api/investigations/{id}/documents/merge` | POST | Merge documents by type-based rules | DocumentManager, Admin |
| `/api/documents/{documentId}` | DELETE | Soft-delete document (all versions) | DocumentManager, Admin |

#### Admin APIs

| Endpoint | Method | Description | Roles |
|----------|--------|-------------|-------|
| `/api/admin/documents/{documentId}/versions` | GET | List all versions (including non-latest) | Admin |
| `/api/admin/documents/{documentId}/rollback` | POST | Roll back to previous version | Admin |
| `/api/admin/documents/{documentId}/versions/{versionId}/download` | GET | Download specific version | Admin |
| `/api/admin/users` | GET | List users | Admin |
| `/api/admin/users/{id}/roles` | PUT | Assign roles | Admin |
| `/api/admin/roles` | GET | List roles | Admin |

#### Upload Status API (New — for async scanning)

| Endpoint | Method | Description | Roles |
|----------|--------|-------------|-------|
| `/api/uploads/{uploadId}/status` | GET | Poll upload scan status | DocumentManager, Admin |

### 7.3 Data Model (Database Migration)

**New Table: `document_versions`**
```sql
CREATE TABLE document_versions (
    version_id          UNIQUEIDENTIFIER PRIMARY KEY DEFAULT NEWID(),
    document_id         UNIQUEIDENTIFIER NOT NULL REFERENCES documents(id),
    version_number      INT NOT NULL,
    blob_path_original  NVARCHAR(1000) NOT NULL,
    blob_path_pdf       NVARCHAR(1000) NULL,
    uploaded_at         DATETIME2 NOT NULL DEFAULT GETUTCDATE(),
    uploaded_by         NVARCHAR(255) NOT NULL,
    uploaded_by_name    NVARCHAR(255) NULL,
    is_latest           BIT NOT NULL DEFAULT 1,
    checksum            NVARCHAR(64) NOT NULL,
    mime_type           NVARCHAR(255) NULL,
    file_size_bytes     BIGINT NOT NULL,
    original_filename   NVARCHAR(500) NOT NULL,
    pdf_conversion_status NVARCHAR(50) NOT NULL DEFAULT 'pending',
    pdf_conversion_error NVARCHAR(MAX) NULL,
    pdf_converted_at    DATETIME2 NULL,

    CONSTRAINT UQ_document_version UNIQUE (document_id, version_number),
    CONSTRAINT UQ_latest_version UNIQUE (document_id, is_latest)
        -- Note: SQL Server filtered index needed for is_latest=1
);

CREATE INDEX IX_docver_document_id ON document_versions(document_id);
CREATE INDEX IX_docver_is_latest ON document_versions(document_id, is_latest)
    WHERE is_latest = 1;
```

**Modified Table: `documents`**
```sql
ALTER TABLE documents
    ADD document_type    NVARCHAR(50) NULL,
    ADD title            NVARCHAR(500) NULL,
    ADD current_version_id UNIQUEIDENTIFIER NULL
        REFERENCES document_versions(version_id);

-- Remove version-specific columns (migrate data first)
-- ALTER TABLE documents DROP COLUMN blob_path, pdf_path, blob_version_id,
--   checksum_sha256, content_type, file_size_bytes, original_filename,
--   pdf_conversion_status, pdf_conversion_error, pdf_converted_at;
```

**New Enum: `DocumentType`**
```python
class DocumentType(StrEnum):
    INVESTIGATION_REPORT = "investigation_report"
    INSPECTION_FORM = "inspection_form"
    LABORATORY_RESULT = "laboratory_result"
    CORRESPONDENCE = "correspondence"
    SUPPORTING_EVIDENCE = "supporting_evidence"
    LEGAL_DOCUMENT = "legal_document"
    OTHER = "other"
```

### 7.4 Integration Points

| System | Integration | Change Required |
|--------|------------|-----------------|
| Azure Blob Storage | Add staging container, versioned paths | Bicep + blob_service.py |
| Azure SQL | Add document_versions table, modify documents | Alembic migration |
| Azure Event Grid | Blob created events for scan + consistency | Bicep + new function |
| Microsoft Defender for Storage | Malware scan trigger | Bicep (optional feature flag) |
| Azure Functions | PDF converter abstraction | Refactor converter services |
| Gotenberg | Wrap behind PdfConverter interface | New adapter class |

---

## 8. UX/UI Requirements

### 8.1 Design Principles

1. **UI is a reference client** — no UI-specific API patterns
2. **Latest-only visibility** — no version history shown to end users
3. **Async-friendly** — upload returns immediately, scanning status polled

### 8.2 Frontend Changes Required

| Change | Impact |
|--------|--------|
| Remove version list UI for end users | Remove `DocumentVersionResponse` display |
| Update upload flow for async scanning | Show upload status polling |
| Remove free-form merge ordering | Replace with type-based merge button |
| Remove/restrict blob explorer | Admin-only or remove from nav |
| Add document type selection on upload | New dropdown field |
| Update document list to show type | Add column to table |

### 8.3 Frontend Non-Changes

- Dashboard, investigations list, audit log — no changes
- Settings, help pages — no changes
- Admin page — enhanced with version management and rollback

---

## 9. Release Plan

### 9.1 Milestones (Recommended Execution Order)

| Phase | Milestone | Deliverables | Priority |
|-------|-----------|-------------|----------|
| **Phase 1** | Metadata + Versioning Refactor | Domain model, Alembic migration, API contract, RBAC hardening | P0 |
| **Phase 2** | Blob Layout Normalization | Versioned directory structure, metadata-first retrieval | P0 |
| **Phase 3** | Merge Rule Enforcement | Document type ordering, latest-only merge | P1 |
| **Phase 4** | PDF Engine Abstraction | PdfConverter interface, Gotenberg adapter, config-driven selection | P1 |
| **Phase 5** | Malware Scanning Pipeline | Staging container, scan integration, promotion flow | P0 |
| **Phase 6** | Admin Rollback APIs | Rollback endpoint, version management, audit logging | P1 |
| **Phase 7** | IaC Cleanup & Consistency | Bicep modularity, feature flags, Event Grid consistency checks | P2 |

### 9.2 Phase Dependencies

```
Phase 1 (Versioning) ──→ Phase 2 (Blob Layout) ──→ Phase 3 (Merge Rules)
                                                 ──→ Phase 6 (Rollback)
Phase 1 ──→ Phase 5 (Malware Scanning)
Phase 4 (PDF Engine) is independent
Phase 7 (IaC) is independent but benefits from all prior phases
```

### 9.3 Migration Strategy

Each phase must:
1. Include an Alembic migration that is backward-compatible
2. Preserve existing demo data (8 investigations, 10 documents)
3. Include data migration scripts for existing records
4. Pass all existing tests before adding new ones
5. Be deployable independently

---

## 10. Risks & Mitigations

| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|------------|
| Data migration breaks existing demo data | Medium | High | Write reversible Alembic migrations; test with backup first |
| Malware scanning latency degrades UX | Medium | Medium | Async upload with polling; clear status indicators |
| Aspose licensing not available for demo | Low | Low | Gotenberg remains default; Aspose adapter is config-only |
| Blob layout migration of existing files | Medium | Medium | Write one-time migration script; validate checksum parity |
| RBAC hardening breaks existing flows | Medium | High | Comprehensive E2E testing; gradual rollout per endpoint |
| SQL Server filtered unique index complexity | Low | Medium | Use application-level enforcement as fallback |
| Azure subscription quota limits | Medium | Medium | Use Container Apps (already in place); monitor quotas |
| Event Grid consistency checks false positives | Low | Low | Log-only mode first; promote to blocking after validation |

---

## 11. Testing Requirements

### 11.1 Test Matrix

| Test Area | Test Type | Acceptance Criteria |
|-----------|-----------|-------------------|
| Latest-only visibility | Unit + Integration | Upload 3 versions → only latest returned by default API |
| Version rollback | Unit + Integration | Rollback → prior version promoted, audit immutable |
| Malware scanning | Integration | Infected file NEVER reaches production container |
| Blob + SQL consistency | Integration | Event Grid validates metadata exists for every blob |
| Merge ordering | Unit | Type-based order consistent regardless of input order |
| PDF engine swap | Integration | Swap config → identical PDF output |
| RBAC enforcement | Unit + Integration | Viewer cannot write; Admin can rollback |
| Blob layout | Unit | Paths follow `/INVESTIGATION-{ID}/{docId}/original/v{N}/` pattern |
| API contract | Integration | SDK consumer can perform full lifecycle without UI |
| Data migration | Migration | Existing 10 documents migrated to new schema with correct versions |

### 11.2 Test Locations

| Component | Location | Framework |
|-----------|----------|-----------|
| Backend Unit Tests | `tests/backend/unit/` | pytest |
| Backend Integration | `tests/backend/integration/` | pytest + httpx |
| Frontend Unit Tests | `tests/frontend/` | Vitest |
| E2E Tests | `tests/frontend/e2e/` | Playwright |
| IaC Validation | `tests/infra/` | Bicep what-if |
| Functions Tests | `tests/functions/` | pytest |

---

## 12. Open Questions

- [ ] **Document type taxonomy**: What are the exact FSIS document types and their merge ordering? Need final list from FSIS stakeholders. — Owner: Product, Due: Before Phase 3
- [ ] **Malware scanner choice**: Use Microsoft Defender for Storage (built-in) or third-party scanner? — Owner: Security, Due: Before Phase 5
- [ ] **Aspose licensing**: Will Aspose license be available for demo environment testing? — Owner: Procurement, Due: Before Phase 4
- [ ] **Rollback depth**: Can admin roll back multiple versions (v3 → v1) or only one step (v3 → v2)? — Owner: Product, Due: Before Phase 6
- [ ] **Existing data migration**: Should existing 10 demo documents be migrated to new schema or re-seeded fresh? — Owner: Engineering, Due: Before Phase 1
- [ ] **Staging container retention**: How long should scanned/rejected files remain in staging for forensics? — Owner: Security, Due: Before Phase 5

---

## 13. Appendix

### 13.1 Glossary

| Term | Definition |
|------|-----------|
| **Logical Document** | A conceptual document entity with stable identity across versions |
| **Document Version** | An immutable physical binary (original + PDF pair) associated with a logical document |
| **Latest Version** | The most recent version of a logical document; the only one visible to end users |
| **Staging Container** | Temporary blob storage for files awaiting malware scan |
| **Production Container** | Trusted blob storage for scan-approved files |
| **UCM** | Oracle Universal Content Management — the system being replaced |
| **FSIS** | Food Safety and Inspection Service — the federal agency customer |
| **Merge Rules** | Configuration-driven ordering of documents by type for PDF merge operations |

### 13.2 References

- Original UCM demo review notes: `PRPs/specs/ASSURANCENET_UCM_MIGRATION_SPEC.md`
- Current domain model: `src/backend/app/db/models.py`
- Current API schemas: `src/backend/app/models/schemas.py`
- Bicep infrastructure: `infra/modules/`
- PDF conversion pipeline: `src/functions/`

### 13.3 Files Requiring Modification

| File | Changes |
|------|---------|
| `src/backend/app/db/models.py` | Add `DocumentVersion` model, modify `Document` model, add `DocumentType` |
| `src/backend/app/models/schemas.py` | New version-aware request/response schemas |
| `src/backend/app/models/enums.py` | Add `DocumentType` enum |
| `src/backend/app/api/v1/documents.py` | Refactor all endpoints for versioned model |
| `src/backend/app/api/v1/admin.py` | Add rollback, version listing endpoints |
| `src/backend/app/api/v1/pdf_merge.py` | Implement type-based merge ordering |
| `src/backend/app/services/blob_service.py` | Versioned paths, staging container support |
| `src/backend/app/services/pdf_merge_service.py` | Type-based ordering logic |
| `src/backend/app/services/metadata_service.py` | Version-aware CRUD operations |
| `src/backend/app/services/rbac_service.py` | Add Reviewer role, centralized enforcement |
| `src/backend/app/middleware/auth.py` | Role-based policy enforcement |
| `src/backend/app/config.py` | PDF engine selection, staging container config |
| `src/functions/pdf_converter.py` | Abstract converter interface |
| `src/functions/services/conversion_service.py` | Implement PdfConverter protocol |
| `src/functions/services/gotenberg_client.py` | Wrap behind PdfConverter adapter |
| `infra/modules/storage.bicep` | Add staging container |
| `infra/modules/event-grid.bicep` | Add scan trigger, consistency check subscriptions |
| `infra/modules/defender.bicep` | Feature-flag malware scanning |
| `infra/main.bicep` | Feature flag parameters |
| Alembic migration | New migration for document_versions table + document modifications |

### 13.4 Change Log

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0 | 2026-03-17 | Claude Code | Initial PRP generated from FSIS UCM migration spec |
