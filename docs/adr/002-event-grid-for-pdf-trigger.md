[Home](../../README.md) > [Architecture Decision Records](.) > **ADR-002**

# ADR-002: Event Grid for PDF Conversion Triggering

`🟢 Accepted`

---

## 📋 Status

Accepted

---

## 📋 Context

Uploaded documents need automatic PDF conversion without blocking the upload API.

---

## ✅ Decision

Use Azure Event Grid System Topic on Blob Storage to trigger Azure Functions for PDF conversion.

---

## 🔄 Alternatives Considered

| Alternative | Why Not Chosen |
|-------------|----------------|
| **Queue Storage** | Requires explicit enqueue; Event Grid is automatic on blob creation |
| **Service Bus** | Over-engineered for fire-and-forget file processing |
| **Polling** | Inefficient and adds latency |

---

## ⚡ Consequences

**Positive:**

- ✅ Zero-code event routing from blob uploads to Functions
- ✅ Built-in retry and dead-letter support
- ✅ Subject filtering prevents infinite loops (exclude `/pdf/` path)
- ✅ Near real-time triggering (~seconds latency)

---

[← **ADR-001: Azure Blob Storage over SharePoint**](001-azure-blob-over-sharepoint.md) | [**ADR-003: FastAPI as Backend Framework** →](003-fastapi-backend.md)
