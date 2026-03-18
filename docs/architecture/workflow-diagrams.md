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
    participant Blob as Azure Blob Storage
    participant EG as Event Grid
    participant Func as Azure Function
    participant Got as Gotenberg
    participant SQL as Azure SQL DB
    participant Audit as Audit Log

    Blob->>EG: BlobCreated event (filtered: /blob/ path, non-PDF)
    EG->>Func: Trigger pdf_converter function
    Func->>Blob: Download original file
    Blob-->>Func: File binary
    alt Image file (JPEG, PNG, TIFF, BMP)
        Func->>Func: Convert with Pillow + img2pdf
    else Office document (DOCX, XLSX, PPTX)
        Func->>Got: POST /forms/libreoffice/convert
        Got-->>Func: PDF binary
    else Plain text (TXT, RTF)
        Func->>Func: Convert with fpdf2
    end
    Func->>Blob: Upload PDF to .../{FileId}/pdf/{filename}.pdf
    Func->>SQL: UPDATE pdf_conversion_status='completed'
    Func->>Audit: Log: document.pdf_converted
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

**Related Architecture Docs:**
[High-Level Architecture](high-level-architecture.md) | [Azure Architecture Detail](azure-architecture-detail.md) | [Blob Hierarchy](blob-hierarchy.md) | [Security Architecture](security-architecture.md) | [Monitoring & Telemetry](monitoring-telemetry.md) | [Data Migration](data-migration.md)
