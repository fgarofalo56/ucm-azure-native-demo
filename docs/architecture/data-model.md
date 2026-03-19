[Home](../../README.md) > [Architecture](.) > **Data Model & RBAC**

# Data Model & RBAC

> **TL;DR:** AssuranceNet uses Azure SQL with explicit document versioning (Document + DocumentVersion), admin-configurable system settings, and a granular RBAC model with 5 roles and 15 permissions.

---

## Table of Contents

- [Database Schema (ERD)](#database-schema-erd)
- [RBAC Model](#rbac-model)
- [Document Type Taxonomy](#document-type-taxonomy)

---

## Database Schema (ERD)

The schema follows an explicit versioning pattern: a `documents` row is the logical document, while each `document_versions` row is an immutable snapshot. The `current_version_id` foreign key on `documents` points back to the latest version — this is the only mutable pointer and is updated atomically on every upload or rollback.

```mermaid
erDiagram
    investigations {
        UUID id PK
        string record_id UK "INVESTIGATION-XXXXX"
        string title
        text description
        enum status "active|closed|archived"
        string created_by
        datetime created_at
        datetime updated_at
    }

    documents {
        UUID id PK
        UUID investigation_id FK
        enum document_type "investigation_report|inspection_form|laboratory_result|correspondence|supporting_evidence|legal_document|other"
        string title
        UUID current_version_id FK
        string created_by
        datetime created_at
        boolean is_deleted
    }

    document_versions {
        UUID id PK
        UUID document_id FK
        int version_number
        string original_filename
        string mime_type
        bigint file_size_bytes
        string blob_path_original
        string blob_path_pdf
        string checksum
        boolean is_latest
        enum pdf_conversion_status
        enum scan_status "pending|scanning|clean|infected|error"
        string uploaded_by
        datetime uploaded_at
    }

    system_settings {
        string key PK
        text value
        string description
        datetime updated_at
        string updated_by
    }

    app_users {
        string id PK
        string entra_oid UK
        string display_name
        string email
        boolean is_active
    }

    roles {
        int id PK
        string name UK
        string display_name
        boolean is_system
    }

    permissions {
        int id PK
        string resource
        string action
    }

    audit_log {
        bigint id PK
        string event_type
        datetime event_timestamp
        string user_id
        string action
        string result
        string resource_type
        string resource_id
        string correlation_id
    }

    migration_status {
        string azure_document_id FK
    }

    investigations ||--o{ documents : "has many"
    documents ||--o{ document_versions : "has many"
    documents }o--|| document_versions : "current_version_id"
    documents }o--|| investigations : "belongs to"
    app_users }o--o{ roles : "user_roles (M:N)"
    roles }o--o{ permissions : "role_permissions (M:N)"
    migration_status }o--o| documents : "azure_document_id"
```

---

## RBAC Model

Five roles span a least-privilege hierarchy from `viewer` (read-only) up to `admin` (full control). Permissions are stored as `resource:action` pairs in the `permissions` table and assigned to roles via the `role_permissions` junction table.

```mermaid
graph LR
    %% ── Nodes ───────────────────────────────────────────────
    subgraph Roles
        A[admin]
        CM[case_manager]
        DM[document_manager]
        RV[reviewer]
        VI[viewer]
    end

    subgraph investigations
        INV_C[create]
        INV_R[read]
        INV_U[update]
        INV_D[delete]
    end

    subgraph documents
        DOC_C[create]
        DOC_R[read]
        DOC_DL[download]
        DOC_D[delete]
        DOC_M[merge]
        DOC_RB[rollback]
        DOC_VER[versions]
    end

    subgraph audit
        AUD_R[read]
    end

    subgraph users
        USR_R[read]
        USR_M[manage]
    end

    subgraph roles_mgmt["roles"]
        ROL_M[manage]
    end

    %% ── admin: all 15 permissions ───────────────────────────
    A --> INV_C
    A --> INV_R
    A --> INV_U
    A --> INV_D
    A --> DOC_C
    A --> DOC_R
    A --> DOC_DL
    A --> DOC_D
    A --> DOC_M
    A --> DOC_RB
    A --> DOC_VER
    A --> AUD_R
    A --> USR_R
    A --> USR_M
    A --> ROL_M

    %% ── case_manager ────────────────────────────────────────
    CM --> INV_C
    CM --> INV_R
    CM --> INV_U
    CM --> INV_D
    CM --> DOC_C
    CM --> DOC_R
    CM --> DOC_DL

    %% ── document_manager ────────────────────────────────────
    DM --> INV_R
    DM --> DOC_C
    DM --> DOC_R
    DM --> DOC_DL
    DM --> DOC_D
    DM --> DOC_M

    %% ── reviewer ────────────────────────────────────────────
    RV --> INV_R
    RV --> DOC_R
    RV --> DOC_DL
    RV --> AUD_R

    %% ── viewer ──────────────────────────────────────────────
    VI --> INV_R
    VI --> DOC_R

    %% ── Styling ─────────────────────────────────────────────
    classDef roleNode fill:#1f4e79,color:#ffffff,stroke:#0d2f4f,font-weight:bold
    classDef permNode fill:#e8f0fe,color:#1a1a2e,stroke:#4a90d9
    classDef subgraphLabel fill:#f0f4ff

    class A,CM,DM,RV,VI roleNode
    class INV_C,INV_R,INV_U,INV_D permNode
    class DOC_C,DOC_R,DOC_DL,DOC_D,DOC_M,DOC_RB,DOC_VER permNode
    class AUD_R,USR_R,USR_M,ROL_M permNode
```

### Permission Matrix

| Permission | admin | case_manager | document_manager | reviewer | viewer |
|---|:---:|:---:|:---:|:---:|:---:|
| investigations:create | Y | Y | | | |
| investigations:read | Y | Y | Y | Y | Y |
| investigations:update | Y | Y | | | |
| investigations:delete | Y | Y | | | |
| documents:create | Y | Y | Y | | |
| documents:read | Y | Y | Y | Y | Y |
| documents:download | Y | Y | Y | Y | |
| documents:delete | Y | | Y | | |
| documents:merge | Y | | Y | | |
| documents:rollback | Y | | | | |
| documents:versions | Y | | | | |
| audit:read | Y | | | Y | |
| users:read | Y | | | | |
| users:manage | Y | | | | |
| roles:manage | Y | | | | |

---

## Document Type Taxonomy

Document types control both classification and PDF merge ordering. When an investigation package is merged, documents are sorted by `merge_order` so the output PDF flows logically from overview down to supporting material.

```mermaid
graph TD
    ROOT([Investigation Package])

    ROOT --> IR[investigation_report\nmerge order: 10]
    ROOT --> IF[inspection_form\nmerge order: 20]
    ROOT --> LR[laboratory_result\nmerge order: 30]
    ROOT --> LD[legal_document\nmerge order: 40]
    ROOT --> CO[correspondence\nmerge order: 50]
    ROOT --> SE[supporting_evidence\nmerge order: 60]
    ROOT --> OT[other\nmerge order: 99]

    classDef typeNode fill:#d4edda,color:#155724,stroke:#28a745,rx:6,ry:6
    classDef rootNode fill:#1f4e79,color:#ffffff,stroke:#0d2f4f,font-weight:bold

    class ROOT rootNode
    class IR,IF,LR,LD,CO,SE,OT typeNode
```

The `merge_order` values are stored in application code (`document_type_config` in `src/backend/app/models/document.py`) rather than in the database so they can be updated via deployment without a schema migration.

---

## Related Docs

- [High-Level Architecture](./high-level-architecture.md) — system component overview
- [Blob Hierarchy](./blob-hierarchy.md) — how blob paths map to `document_versions` rows
- [Security Architecture](./security-architecture.md) — Managed Identity and Key Vault integration
- [Data Migration](./data-migration.md) — Oracle UCM to Azure SQL migration strategy
- [Workflow Diagrams](./workflow-diagrams.md) — upload, merge, and rollback sequence diagrams
