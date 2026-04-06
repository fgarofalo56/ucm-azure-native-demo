Notes and specs gathered from demo of current codebase, below is requested changes and refactoring asked:

A. New Feature Changes (Incremental, Demo‑Safe)
1. Document Versioning Model Aligned to FSIS Requirements
What to change

Move from “implicit GUID-based versions” to an explicit versioning abstraction:

One logical document record
Multiple immutable binary versions underneath
Only latest version returned by default APIs


Track:

logicalDocumentId
versionNumber
isLatest
uploadedAt
uploadedBy



Why

FSIS explicitly stated users should only see the latest version, with rollback handled administratively, not via UI.
Current POC allows all versions to be visible and mergeable, which does not match production expectations.
 [Oracle UCM...Recording | Video]

Testing

Upload same filename multiple times → only latest returned
Admin deletes version N → version N‑1 promoted automatically
Audit log remains immutable across all versions


2. Deterministic Blob Storage Layout (Container + Virtual Directories)
What to change
Implement the agreed structure:
/INVESTIGATION-{ID}/
  /{LogicalDocumentId}/
    /original/
      /v1/
      /v2/
    /pdf/
      /v1/
      /v2/


Logical document identity stored in metadata, not filename
PDFs stored as siblings, not overwrites

Why

FSIS explicitly requested structure-driven retrieval, not name-based discovery.
Supports SDK-based retrieval and future non-React consumers.
 [Oracle UCM...Recording | Video]

Testing

SDK retrieval returns only latest version
Older versions remain addressable by admin tooling
PDF and source always remain paired


3. PDF Merge Rules Based on Document Type (Not User Order)
What to change

Remove free‑form merge ordering
Introduce merge policy:

Document Type → Predefined order


Enforce “latest version only” during merge

Why

FSIS stated merge order is rule-based, not user-selected.
Current POC allows invalid merges (cross-version, arbitrary order).
 [Oracle UCM...Recording | Video]

Testing

Merge ignores older versions
Merge order consistent regardless of selection order
Invalid document combinations rejected


4. Pluggable PDF Conversion Engine
What to change

Abstract PDF conversion behind an interface:

Current: Gotenberg
Future: Aspose (licensed)


Engine selected via configuration

Why

FSIS confirmed Aspose is required in production.
Demo must prove engine replacement without architecture change.
 [Oracle UCM...Recording | Video]

Testing

Swap engine without redeploying frontend
MIME-based routing works identically
PDF output parity validated


5. Malware Scanning (Two‑Phase Upload)
What to change

Introduce staging blob container
Upload → scan → promote to production container
Block downstream processing until clean

Why

FSIS raised explicit concern about untrusted uploads.
This is a mandatory control for federal document systems.
 [Oracle UCM...Recording | Video]

Testing

Infected file never reaches production container
Clean file auto-promoted
User experience remains async/non-blocking


6. Admin‑Only Version Rollback Capability
What to change

No UI for end users
Admin API:

Delete latest version
Promote prior version
Update metadata atomically



Why

FSIS wants rollback via ticketed admin workflow, not user self‑service.
 [Oracle UCM...Recording | Video]

Testing

Rollback preserves audit trail
“Latest” pointer updates correctly
No binary mutation occurs


B. Required Refactoring & Technical Debt Cleanup
1. API Contract Refactor (Version‑Aware)
Change

Separate:

Document (logical)
DocumentVersion (binary)


All read APIs default to latest=true

Why

Current API conflates file identity and version identity.
Required to support FSIS visibility rules.
 [Oracle UCM...Recording | Video]


2. Remove UI‑Driven Assumptions
Change

Treat React app as reference client only
APIs must be fully consumable by:

Server‑side JSP
SDK consumers



Why

FSIS explicitly stated React UI will not be used in production.
Architecture must stand alone.
 [Oracle UCM...Recording | Video]


3. Metadata‑First Retrieval Model
Change

No blob listing for discovery
All retrieval driven by Azure SQL metadata

Why

Required for scale, governance, and auditability.
Matches FSIS integration model.
 [Oracle UCM...Recording | Video]


4. Hardened RBAC Enforcement in Middleware
Change

Centralize role enforcement:

Investigator
Document Manager
Reviewer
Admin


Enforce at API layer, not UI

Why

FSIS emphasized read‑only vs mutable separation.
Current demo is permissive.
 [Oracle UCM...Recording | Video]


5. IaC Refactor: Bicep Modularity & Clarity
Change

Clearly separate:

Core infra
Optional services (Defender, scanning, Event Grid)


Add comments + parameter docs (requested explicitly)

Why

FSIS requested deeper understanding of Bicep/IaC.
Improves handoff and reuse.
 [Oracle UCM...Recording | Video]

Testing

Deploy infra-only
Toggle optional features cleanly
Idempotent redeploys


6. Event‑Driven Consistency Checks
Change

Blob events → validate:

Metadata exists
Version rules enforced
PDF pair created



Why

Prevents silent drift between blob + SQL state.
Required once staging and versioning added.
 [Oracle UCM...Recording | Video]


Recommended Execution Order (Low Risk → High Value)

Metadata + versioning refactor
Blob layout normalization
Merge rule enforcement
PDF engine abstraction
Malware scanning pipeline
Admin rollback APIs
IaC cleanup & documentation

# AssuranceNet – Oracle UCM → Azure Native Migration
## Implementation Specification for Demo Enhancements & Refactoring

**Audience:** Claude Code (primary), senior engineers
**Purpose:** Authoritative build spec for implementing agreed demo changes
**Scope:** Demo app only, but architecture must be production‑correct
**Non‑Goal:** UI polish or feature expansion beyond document lifecycle

---

## 1. Guiding Principles (Non‑Negotiable)

1. **Metadata is the source of truth**
   - Blob storage is never queried for discovery.
   - Azure SQL governs document identity, versioning, and visibility.

2. **Documents are immutable**
   - Binaries are never overwritten.
   - All changes create new versions.

3. **Latest‑only visibility**
   - End users only ever see the latest version of a document.
   - Historical versions are admin‑only.

4. **UI is a reference client**
   - APIs must be consumable by:
     - Server‑side JSP apps
     - SDK consumers
     - Non‑React frontends

5. **Federal‑grade security defaults**
   - Private endpoints
   - Managed identities
   - Explicit RBAC enforcement
   - Malware scanning before persistence

---

## 2. Domain Model

### Investigation
```
Investigation
- investigationId (string)
- createdAt
- createdBy
```

### Document (Logical)
```
Document
- documentId (UUID)
- investigationId
- documentType
- title
- createdAt
- createdBy
- currentVersionId (UUID)
```

### DocumentVersion (Physical)
```
DocumentVersion
- versionId (UUID)
- documentId
- versionNumber (int)
- blobPathOriginal
- blobPathPdf
- uploadedAt
- uploadedBy
- isLatest (bool)
- checksum
- mimeType
```

---

## 3. Blob Storage Layout

```
/INVESTIGATION-{ID}/
  /{documentId}/
    /original/
      /v1/
      /v2/
    /pdf/
      /v1/
      /v2/
```

Rules:
- New upload = new version directory
- PDFs are siblings of originals
- Filenames are not identifiers

---

## 4. API Contract

### Upload Document
```
POST /api/investigations/{id}/documents
```

Behavior:
1. Create logical document if needed
2. Create new document version
3. Mark previous version not latest
4. Store original
5. Trigger async PDF conversion
6. Persist metadata atomically

---

### Retrieve Documents (Default)
```
GET /api/investigations/{id}/documents
```
Returns only latest versions.

---

### Admin Rollback
```
POST /api/admin/documents/{documentId}/rollback
```

---

## 5. PDF Conversion

Pluggable interface:
```
class PdfConverter:
    def supports(mime_type: str) -> bool
    def convert(input_path: str, output_path: str) -> None
```

Implementations:
- Gotenberg (default)
- Aspose (configurable)

---

## 6. Merge Rules

- Only latest versions
- Order driven by documentType
- User order ignored

---

## 7. Malware Scanning

Two‑phase upload:
1. Staging container
2. Scan
3. Promote or reject

---

## 8. RBAC

Roles:
- Viewer
- DocumentManager
- Admin

Enforced at API layer only.

---

## 9. IaC (Bicep)

- Modular
- Feature‑flag driven
- Idempotent

---

## 10. Testing Requirements

- Latest‑only visibility
- Rollback correctness
- Malware never reaches prod
- Blob + SQL consistency

---

## 11. Explicit Non‑Goals

- No end‑user version history UI
- No blob browsing
- No filename logic

---

## 12. Success Criteria

✅ UCM parity proven
✅ React UI removable
✅ Explicit versioning
✅ Federal‑grade security
