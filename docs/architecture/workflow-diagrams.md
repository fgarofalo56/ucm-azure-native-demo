[Home](../../README.md) > [Architecture](.) > **User Workflow Diagrams**

# User Workflow Diagrams

> **TL;DR:** This document illustrates the six core workflows of AssuranceNet: document upload, async PDF conversion, document download, PDF merge, version history retrieval, and authentication. Each flow is shown as a sequence diagram with all participants and interactions.

---

## Table of Contents

- [Document Upload Flow](#document-upload-flow)
- [Async PDF Conversion Flow](#async-pdf-conversion-flow)
- [Document Download Flow](#document-download-flow)
- [PDF Merge Flow](#pdf-merge-flow)
- [Version History Flow](#version-history-flow)
- [Authentication Flow](#authentication-flow)

---

## 🏗️ Document Upload Flow

```mermaid
sequenceDiagram
    actor User as AssuranceNet User
    participant FE as React Frontend
    participant Auth as Entra ID
    participant API as FastAPI Backend
    participant Blob as Azure Blob Storage
    participant SQL as Azure SQL DB
    participant Audit as Audit Log

    User->>FE: Select file & upload
    FE->>Auth: Acquire token (MSAL)
    Auth-->>FE: JWT access token
    FE->>API: POST /api/v1/documents/upload (multipart/form-data + JWT)
    API->>API: Validate JWT, extract user claims
    API->>API: Generate FileId, compute SHA-256
    API->>Blob: Upload to INVESTIGATION-{RecordId}/{FileId}/blob/{filename}
    Blob-->>API: Blob URL + version ID
    API->>SQL: INSERT document metadata
    SQL-->>API: Document record created
    API->>Audit: Log: document.upload
    API-->>FE: 201 Created {document_id, status: "pending_conversion"}
    FE-->>User: Upload successful
```

---

## ⚙️ Async PDF Conversion Flow

```mermaid
sequenceDiagram
    participant API as FastAPI Backend
    participant Settings as system_settings DB
    participant Staging as Staging Container
    participant Blob as Production Blob Storage
    participant SQL as Azure SQL DB

    API->>Settings: Read pdf_engine + malware_scanning_enabled
    alt Malware scanning enabled
        API->>Staging: Upload to staging container
        Note over Staging: Defender for Storage scans
        API->>Blob: Promote clean file to production
    else Scanning disabled
        API->>Blob: Upload directly to production
    end
    API->>Blob: Upload to .../{documentId}/original/v{N}/{filename}
    alt Image file (JPEG, PNG, TIFF, BMP)
        API->>API: Convert with Pillow (in-process)
    else Text/CSV file
        API->>API: Convert with fpdf2 (in-process)
    else Office document (DOCX, XLSX, PPTX)
        alt Engine = aspose
            API->>API: Convert with Aspose SDK (licensed)
        else Engine = opensource + Gotenberg URL set
            API->>API: Convert via Gotenberg HTTP API
        end
    end
    API->>Blob: Upload PDF to .../{documentId}/pdf/v{N}/{basename}.pdf
    API->>SQL: UPDATE document_versions SET pdf_conversion_status='completed'
```

> [!NOTE]
> Files already in PDF format are passed through without conversion. The Event Grid filter on the `/blob/` path ensures only new uploads (not PDF outputs) trigger conversion.

---

## 🗄️ Document Download Flow

```mermaid
sequenceDiagram
    actor User as AssuranceNet User
    participant FE as React Frontend
    participant API as FastAPI Backend
    participant SQL as Azure SQL DB
    participant Blob as Azure Blob Storage
    participant Audit as Audit Log

    User->>FE: Click download (original or PDF)
    FE->>API: GET /api/v1/documents/{id}/download
    API->>API: Validate JWT + authorization
    API->>SQL: GET document metadata
    API->>Blob: Download file
    Blob-->>API: File stream
    API->>Audit: Log: document.download
    API-->>FE: StreamingResponse
    FE-->>User: File download
```

---

## ✨ PDF Merge Flow

```mermaid
sequenceDiagram
    actor User as AssuranceNet User
    participant FE as React Frontend
    participant API as FastAPI Backend
    participant SQL as Azure SQL DB
    participant Blob as Azure Blob Storage
    participant Audit as Audit Log

    User->>FE: Select multiple documents, click "Merge PDFs"
    FE->>API: POST /api/v1/investigations/{recordId}/merge-pdf
    API->>API: Validate JWT + authorization
    loop For each document_id (sorted by document_type)
        API->>SQL: Resolve latest version, GET blob_path_pdf for document_id
        API->>Blob: Download PDF
        Blob-->>API: PDF binary
    end
    API->>API: Merge PDFs with pypdf (in-memory)
    API->>Audit: Log: document.merge
    API-->>FE: StreamingResponse (merged PDF)
    Note right of API: Merged PDF is NOT persisted
    FE-->>User: Download merged PDF
```

> [!IMPORTANT]
> Merged PDFs are generated on-the-fly and are **not** persisted to Blob Storage. Each merge request re-downloads and re-merges the source PDFs.

---

## 🗄️ Version History Flow

```mermaid
sequenceDiagram
    actor User as AssuranceNet User
    participant FE as React Frontend
    participant API as FastAPI Backend
    participant SQL as Azure SQL DB
    participant Blob as Azure Blob Storage

    User->>FE: View document versions
    FE->>API: GET /api/v1/documents/{id}/versions
    API->>SQL: GET version history
    API->>Blob: List blob versions
    API-->>FE: Version list with timestamps, users, sizes
    User->>FE: Select specific version
    FE->>API: GET /api/v1/documents/{id}/download?version={versionId}
    API->>Blob: Download specific blob version
    API-->>FE: StreamingResponse (versioned file)
    FE-->>User: File download
```

---

## 🔒 Authentication Flow

```mermaid
sequenceDiagram
    actor User
    participant FE as React SPA
    participant MSAL as MSAL.js
    participant Entra as Entra ID
    participant API as FastAPI Backend

    User->>FE: Navigate to app
    FE->>MSAL: Check for cached session
    alt No cached session
        FE->>MSAL: loginRedirect()
        MSAL->>Entra: Redirect to login page
        User->>Entra: Enter credentials + MFA
        Entra-->>MSAL: Authorization code
        MSAL->>Entra: Exchange code for tokens (PKCE)
        Entra-->>MSAL: ID token + access token
        MSAL-->>FE: User authenticated
    else Cached session exists
        MSAL-->>FE: User already authenticated
    end
    FE->>MSAL: acquireTokenSilent()
    MSAL-->>FE: Access token (JWT)
    FE->>API: API request + Bearer token
    API->>API: Validate JWT (signature, aud, iss, exp)
    API->>API: Extract claims (oid, name, roles)
    API-->>FE: API response
```

---

## PDF Conversion Engine Selection

```mermaid
flowchart TD
    Upload[File Uploaded] --> CheckType{Check MIME Type}
    CheckType -->|application/pdf| Pass[Passthrough - no conversion]
    CheckType -->|image/*| Pillow[Pillow + img2pdf]
    CheckType -->|text/plain, text/csv, text/rtf| Fpdf2[fpdf2 text renderer]
    CheckType -->|Office: DOCX, XLSX, PPTX| ReadSettings{Read system_settings}
    ReadSettings -->|pdf_engine = aspose| Aspose[Aspose SDK]
    ReadSettings -->|pdf_engine = opensource| CheckGotenberg{gotenberg_url set?}
    CheckGotenberg -->|Yes| Gotenberg[Gotenberg HTTP API]
    CheckGotenberg -->|No| Skip[Skip - mark pending]
    Pillow --> StorePDF[Upload PDF to /pdf/v{N}/]
    Fpdf2 --> StorePDF
    Aspose --> StorePDF
    Gotenberg --> StorePDF
    StorePDF --> UpdateDB[UPDATE pdf_conversion_status = completed]
```

---

## Malware Scanning Pipeline

```mermaid
sequenceDiagram
    participant User
    participant API as FastAPI API
    participant Settings as system_settings
    participant Staging as assurancenet-staging
    participant Defender as Defender for Storage
    participant Prod as assurancenet-documents
    participant SQL as Azure SQL

    User->>API: Upload file
    API->>Settings: Read malware_scanning_enabled
    alt Scanning Enabled
        API->>Staging: Upload to staging container
        Defender->>Staging: Scan for malware
        alt Clean
            API->>Prod: promote_from_staging()
            API->>Staging: Delete staging copy
            API->>SQL: scan_status = 'clean'
        else Infected
            API->>SQL: scan_status = 'infected'
            Note over Staging: File quarantined
        end
    else Scanning Disabled
        API->>Prod: Upload directly
        API->>SQL: scan_status = 'clean'
    end
    API->>SQL: Create DocumentVersion record
```

---

## Admin Version Rollback

```mermaid
sequenceDiagram
    participant Admin
    participant API as POST /admin/documents/{id}/rollback
    participant SQL as Azure SQL
    participant Audit as Audit Log

    Admin->>API: Rollback request
    API->>SQL: Get all versions (ordered by version_number DESC)
    SQL-->>API: [v3 (latest), v2, v1]

    alt Only 1 version exists
        API-->>Admin: 400 Bad Request - cannot rollback
    else 2+ versions exist
        API->>SQL: UPDATE v3 SET is_latest = false
        API->>SQL: UPDATE v2 SET is_latest = true
        API->>SQL: UPDATE document SET current_version_id = v2.id
        API->>Audit: Log rollback event
        API-->>Admin: {rolled_back: v3, promoted: v2}
    end
    Note over SQL: No binary data modified - only metadata pointers
```

---

## Request Correlation & Tracing

```mermaid
flowchart LR
    subgraph Client
        React[React SPA]
    end

    subgraph API["FastAPI Backend"]
        MW[Auth Middleware] --> Route[Route Handler]
        Route --> Service[Service Layer]
    end

    subgraph Data
        Blob[Blob Storage]
        SQL[Azure SQL]
        AuditTbl[Audit Log]
    end

    subgraph Monitoring
        AI[App Insights]
        LAW[Log Analytics]
    end

    React -->|"correlation_id in header"| MW
    Service --> Blob
    Service --> SQL
    Service --> AuditTbl
    Route -->|"structlog with correlation_id"| AI
    AI --> LAW

    style React fill:#61dafb,color:#000
    style MW fill:#009688,color:#fff
    style AuditTbl fill:#ffd8a8,color:#000
```

---

**Related Architecture Docs:**
[High-Level Architecture](high-level-architecture.md) | [Azure Architecture Detail](azure-architecture-detail.md) | [Blob Hierarchy](blob-hierarchy.md) | [Security Architecture](security-architecture.md) | [Monitoring & Telemetry](monitoring-telemetry.md) | [Data Migration](data-migration.md)
