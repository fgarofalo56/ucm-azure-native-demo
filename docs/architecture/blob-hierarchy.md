[Home](../../README.md) > [Architecture](.) > **Blob Storage Hierarchy**

# Blob Storage Hierarchy

> **TL;DR:** Documents are stored in Azure Blob Storage using a structured hierarchy: `{container}/{record_id}/{file_id}/blob/{filename}` for originals and `.../pdf/{filename}.pdf` for converted PDFs. This design co-locates investigation files, prevents name collisions, and enables Event Grid filtering for the PDF conversion pipeline.

---

## Table of Contents

- [Naming Convention](#naming-convention)
- [Example](#example)
- [FSIS Real-World Examples](#fsis-real-world-examples)
- [Design Rationale](#design-rationale)

---

## 📁 Naming Convention

```text
{container}/
  {record_id}/
    {file_id}/
      blob/
        {original_filename}
      pdf/
        {original_filename_without_ext}.pdf
```

---

## 📁 Example

```text
assurancenet-documents/
  INVESTIGATION-12345/
    a1b2c3d4-e5f6-7890-abcd-ef1234567890/
      blob/
        quarterly-report.docx
      pdf/
        quarterly-report.pdf
    f9e8d7c6-b5a4-3210-fedc-ba9876543210/
      blob/
        photo-evidence.jpg
      pdf/
        photo-evidence.pdf
```

---

## 🗄️ FSIS Real-World Examples

Based on actual FSIS Science & Data document types from [fsis.usda.gov/science-data](https://www.fsis.usda.gov/science-data):

```text
assurancenet-documents/
  INVESTIGATION-10001/                              # FY2025 Annual Sampling Program
    a1b2c3d4-e5f6-7890-abcd-ef1234567890/
      blob/
        FSIS-Annual-Sampling-Plan-FY2025.pdf        # Already PDF - no conversion needed
      pdf/
        FSIS-Annual-Sampling-Plan-FY2025.pdf        # Passthrough copy
    b2c3d4e5-f6a7-8901-bcde-f12345678901/
      blob/
        FSIS-Annual-Sampling-Plan-FY2024.pdf
      pdf/
        FSIS-Annual-Sampling-Plan-FY2024.pdf

  INVESTIGATION-10002/                              # National Residue Program
    c3d4e5f6-a7b8-9012-cdef-123456789012/
      blob/
        fy2019-red-book.pdf                         # Red Book (sampling results)
      pdf/
        fy2019-red-book.pdf
    d4e5f6a7-b8c9-0123-defa-234567890123/
      blob/
        2019-blue-book.pdf                          # Blue Book (sampling plan)
      pdf/
        2019-blue-book.pdf

  INVESTIGATION-10005/                              # MPI Directory Audit
    e5f6a7b8-c9d0-1234-efab-345678901234/
      blob/
        MPI_Directory_by_Establishment_Number.csv   # CSV - converted to PDF
      pdf/
        MPI_Directory_by_Establishment_Number.pdf   # fpdf2-converted text table
    f6a7b8c9-d0e1-2345-fabc-456789012345/
      blob/
        MPI_Directory_by_Establishment_Name.csv
      pdf/
        MPI_Directory_by_Establishment_Name.pdf
```

---

## 🏗️ Design Rationale

| Principle | Implementation | Benefit |
|-----------|---------------|---------|
| **Investigation-scoped** | All files for an investigation are co-located | Maps directly to FSIS investigation records |
| **File ID isolation** | Each upload gets a unique UUID folder | Prevents name collisions across uploads |
| **Blob/PDF separation** | Original and converted files in distinct paths (`blob/` vs `pdf/`) | Clean separation of source and output |
| **Event Grid filtering** | `/blob/` path filter triggers PDF conversion; `/pdf/` is excluded | Prevents infinite conversion loops |
| **Version support** | Azure Blob versioning tracks changes per file | Full history of document revisions |
| **FSIS alignment** | Record IDs follow FSIS naming patterns (`INVESTIGATION-XXXXX`) | Consistent with upstream systems |

> [!WARNING]
> Never upload files directly to the `pdf/` path. Only the PDF conversion pipeline should write to `pdf/` folders. Direct uploads to `pdf/` will bypass audit logging and integrity checks.

---

**Related Architecture Docs:**
[High-Level Architecture](high-level-architecture.md) | [Azure Architecture Detail](azure-architecture-detail.md) | [Workflow Diagrams](workflow-diagrams.md) | [Security Architecture](security-architecture.md) | [Monitoring & Telemetry](monitoring-telemetry.md) | [Data Migration](data-migration.md)
