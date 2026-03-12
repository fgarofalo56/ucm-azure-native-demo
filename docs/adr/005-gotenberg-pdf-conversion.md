[Home](../../README.md) > [Architecture Decision Records](.) > **ADR-005**

# ADR-005: Gotenberg for Office Document PDF Conversion

`🟢 Accepted`

---

## 📋 Status

Accepted

---

## 📋 Context

Need to convert Microsoft Office documents (DOCX, XLSX, PPTX, etc.) to PDF.

---

## ✅ Decision

Use Gotenberg (LibreOffice-based) running in Azure Container Apps.

---

## 🔄 Alternatives Considered

| Alternative | Why Not Chosen |
|-------------|----------------|
| **Aspose** | Commercial license, expensive at scale (~$10K/yr) |
| **Azure Logic Apps PDF connector** | Limited format support |
| **LibreOffice direct** | Complex deployment; Gotenberg provides clean HTTP API |

---

## ⚡ Consequences

**Positive:**

- ✅ Open-source, BSD-licensed, no per-document costs
- ✅ Simple HTTP API for conversion
- ✅ Scale 0-5 replicas based on load
- ✅ Good fidelity for standard Office documents

**Risks:**

- ⚠️ Complex formatting may differ from MS Office rendering

---

[← **ADR-004: Bicep as Infrastructure-as-Code Tool**](004-bicep-iac.md) | [**ADR-006: Hybrid PDF Conversion Approach** →](006-hybrid-pdf-approach.md)
