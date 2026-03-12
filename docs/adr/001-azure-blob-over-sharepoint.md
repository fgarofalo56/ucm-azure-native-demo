[Home](../../README.md) > [Architecture Decision Records](.) > **ADR-001**

# ADR-001: Azure Blob Storage over SharePoint for Document Storage

`🟢 Accepted`

---

## 📋 Status

Accepted

---

## 📋 Context

We need to store ~700,000 files (~1.7TB) from the FSIS UCM system with versioning, programmatic access, and event-driven processing. Document types include FSIS sampling plans (PDF), laboratory data (CSV), National Residue Program reports (PDF), MPI establishment directories (CSV), and general investigation documents in various Office formats. See [FSIS Science & Data](https://www.fsis.usda.gov/science-data) for the types of documents managed.

---

## ✅ Decision

Use Azure Blob Storage with versioning, change feed, and lifecycle management.

---

## 🔄 Alternatives Considered

| Alternative | Why Not Chosen |
|-------------|----------------|
| **SharePoint Online** | Limited API throughput for bulk operations, 250GB site storage limits, not designed for backend document processing |
| **Azure Files** | SMB-oriented, lacks blob versioning and Event Grid integration |

---

## ⚡ Consequences

**Positive:**

- ✅ Full programmatic control via Azure SDK
- ✅ Native Event Grid integration for PDF conversion triggers
- ✅ Cost-effective at TB scale (~$34/mo for 1.7TB Hot LRS)

**Risks:**

- ⚠️ Requires custom UI (no SharePoint document library UX)

---

[**ADR-002: Event Grid for PDF Conversion Triggering** →](002-event-grid-for-pdf-trigger.md)
