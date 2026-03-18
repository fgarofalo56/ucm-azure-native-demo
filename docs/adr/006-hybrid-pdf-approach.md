[Home](../../README.md) > [Architecture Decision Records](.) > **ADR-006**

# ADR-006: Hybrid PDF Conversion with Pluggable Engine

`🟢 Accepted`

---

## 📋 Status

Accepted (updated to reflect pluggable engine architecture)

---

## 📋 Context

Different file types benefit from different conversion methods. A single tool doesn't optimally handle all formats. Additionally, FSIS requires the ability to swap between PDF engines (Aspose for production, Gotenberg for demo) without code changes.

---

## ✅ Decision

Use a hybrid approach with a **pluggable `PdfConverter` protocol**:

- **Aspose** (default): Word via `aspose.words`, Excel via `aspose.cells`, PowerPoint via `aspose.slides`
- **Gotenberg** (fallback): Office documents via LibreOffice HTTP API
- **Pillow + img2pdf** (in-process): Images — lossless, no external call
- **fpdf2** (in-process): Plain text and RTF
- **pypdf** (backend): PDF merging (type-based ordering)

Engine selection via `PDF_ENGINE` environment variable (`aspose` or `gotenberg`).

---

### Pluggable Architecture

```python
class PdfConverter(Protocol):
    def supports(self, mime_type: str) -> bool: ...
    async def convert(self, input_data: bytes, filename: str, mime_type: str) -> bytes: ...

# Factory selects engine from config
engine = get_pdf_engine()  # Returns AsposeEngine or GotenbergEngine
```

---

### Routing Logic

```
image/*           -> Pillow + img2pdf (in Azure Function, both engines)
text/plain, RTF   -> fpdf2 (in Azure Function, both engines)
application/pdf   -> Passthrough (both engines)
Word (DOC/DOCX)   -> aspose.words (Aspose) | Gotenberg API (Gotenberg)
Excel (XLS/XLSX)  -> aspose.cells (Aspose) | Gotenberg API (Gotenberg)
PowerPoint        -> aspose.slides (Aspose) | Gotenberg API (Gotenberg)
Unknown           -> aspose.words fallback (Aspose) | Gotenberg fallback (Gotenberg)
```

---

### FSIS Document Type Mapping

Based on document types from [FSIS Science & Data](https://www.fsis.usda.gov/science-data):

| FSIS Document | Format | Converter | Document Type |
|---|---|---|---|
| Annual Sampling Plans | PDF | Passthrough | `investigation_report` |
| National Residue Reports | PDF | Passthrough | `laboratory_result` |
| MPI Establishment Directory | CSV | fpdf2 | `supporting_evidence` |
| Laboratory Sampling Data | CSV | fpdf2 | `laboratory_result` |
| Quarterly Enforcement Tables | PDF | Passthrough | `legal_document` |
| Investigation Reports | DOCX | Aspose.Words / Gotenberg | `investigation_report` |
| Inspection Photos | JPEG/PNG | Pillow + img2pdf | `inspection_form` |
| Compliance Spreadsheets | XLSX | Aspose.Cells / Gotenberg | `supporting_evidence` |

---

## 🔄 Alternatives Considered

> No single-tool alternative was evaluated for ADR-006. This decision builds on [ADR-005](005-gotenberg-pdf-conversion.md) by adding format-specific converters and the pluggable engine protocol. The individual tool choices are documented in ADR-005.

---

## ⚡ Consequences

**Positive:**

- Optimal conversion quality per format
- Images and text don't require external service call (faster, cheaper)
- Engine swappable via config — zero code changes for Aspose ↔ Gotenberg
- CSV files (common in FSIS data) handled efficiently by fpdf2 in-process
- Production (Aspose) and demo (Gotenberg) environments use identical routing logic

**Risks:**

- Multiple code paths require comprehensive testing
- Aspose requires commercial license for production

---

[← **ADR-005: Aspose for Office Document PDF Conversion**](005-gotenberg-pdf-conversion.md)
