[Home](../../README.md) > [Architecture Decision Records](.) > **ADR-005**

# ADR-005: Aspose for Office Document PDF Conversion

`🟡 Superseded` — Originally Gotenberg; updated to Aspose as primary engine.

---

## 📋 Status

Superseded — Aspose is now the default production engine. Gotenberg remains as a configurable fallback for environments without Aspose licenses.

---

## 📋 Context

Need to convert Microsoft Office documents (DOCX, XLSX, PPTX, etc.) to PDF for the FSIS document management pipeline. FSIS confirmed Aspose is the required engine for production use due to superior Office format fidelity.

---

## ✅ Decision (Updated)

Use **Aspose** (aspose.words, aspose.cells, aspose.slides) as the default PDF conversion engine, with **Gotenberg** (LibreOffice-based) available as a configurable fallback.

Engine selection is controlled via the `PDF_ENGINE` environment variable:
- `aspose` (default) — Production-grade, licensed
- `gotenberg` — Demo/OSS fallback, requires running container

The engine swap requires zero code changes — only a config update and restart.

### Engine Routing

| MIME Type | Aspose Engine | Gotenberg Engine |
|-----------|--------------|-----------------|
| Word (DOC/DOCX) | aspose.words | Gotenberg (LibreOffice) |
| Excel (XLS/XLSX) | aspose.cells | Gotenberg (LibreOffice) |
| PowerPoint (PPT/PPTX) | aspose.slides | Gotenberg (LibreOffice) |
| Images (JPEG/PNG/TIFF) | Pillow + img2pdf | Pillow + img2pdf |
| Text/RTF | fpdf2 | fpdf2 |
| PDF | Passthrough | Passthrough |

---

## 🔄 Original Decision (Historical)

Gotenberg was the original choice (LibreOffice-based, OSS, running in Azure Container Apps). This was appropriate for the demo phase but FSIS explicitly stated Aspose is required for production due to:
- Higher fidelity Office format rendering
- Better handling of complex formatting, macros, and embedded objects
- Established use within USDA/FSIS toolchain

---

## 🔄 Alternatives Considered

| Alternative | Why Not Primary |
|-------------|----------------|
| **Gotenberg** (original) | Good for demo but lower fidelity for complex Office documents; retained as fallback |
| **Azure Logic Apps PDF connector** | Limited format support |
| **LibreOffice direct** | Complex deployment; Gotenberg provides cleaner API wrapper |

---

## ⚡ Consequences

**Positive:**

- Highest fidelity Office format conversion (matches MS Office rendering)
- Dedicated SDK per format (Words, Cells, Slides) — optimal for each type
- No external container dependency (runs in-process in Azure Functions)
- Pluggable engine architecture allows zero-downtime swap back to Gotenberg
- Images and text still use lightweight in-process converters (no license needed)

**Risks:**

- Commercial license required (~$10K/yr per SDK)
- Aspose SDKs add to deployment package size
- License management needed for production environments

---

[← **ADR-004: Bicep as Infrastructure-as-Code Tool**](004-bicep-iac.md) | [**ADR-006: Hybrid PDF Conversion Approach** →](006-hybrid-pdf-approach.md)
