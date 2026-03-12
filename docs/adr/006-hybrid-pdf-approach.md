[Home](../../README.md) > [Architecture Decision Records](.) > **ADR-006**

# ADR-006: Hybrid PDF Conversion Approach

`🟢 Accepted`

---

## 📋 Status

Accepted

---

## 📋 Context

Different file types benefit from different conversion methods. A single tool doesn't optimally handle all formats.

---

## ✅ Decision

Use a hybrid approach:
- **Gotenberg** (Container Apps): Office documents via LibreOffice
- **Pillow + img2pdf** (in-process): Images - lossless, no external call
- **fpdf2** (in-process): Plain text and RTF
- **pypdf** (backend): PDF merging

---

### Routing Logic

```
image/*           -> Pillow + img2pdf (in Azure Function)
text/plain, RTF   -> fpdf2 (in Azure Function)
application/pdf   -> Passthrough
Office formats    -> Gotenberg API (Container Apps)
Unknown           -> Gotenberg fallback
```

---

### FSIS Document Type Mapping

Based on document types from [FSIS Science & Data](https://www.fsis.usda.gov/science-data):

| FSIS Document | Format | Converter | Notes |
|---|---|---|---|
| Annual Sampling Plans | PDF | Passthrough | Already PDF |
| National Residue Reports | PDF | Passthrough | Red Book, Blue Book |
| MPI Establishment Directory | CSV | fpdf2 | Text-to-PDF conversion |
| Laboratory Sampling Data | CSV | fpdf2 | Tabular data rendering |
| Quarterly Enforcement Tables | PDF | Passthrough | Already PDF |
| Investigation Reports | DOCX | Gotenberg | Office format conversion |
| Inspection Photos | JPEG/PNG | Pillow + img2pdf | Lossless image embedding |
| Compliance Spreadsheets | XLSX | Gotenberg | Office format conversion |

---

## 🔄 Alternatives Considered

> No single-tool alternative was evaluated for ADR-006. This decision builds on [ADR-005](005-gotenberg-pdf-conversion.md) by adding format-specific converters to complement Gotenberg. The individual tool choices are documented in ADR-005.

---

## ⚡ Consequences

**Positive:**

- ✅ Optimal conversion quality per format
- ✅ Images don't require external service call (faster, cheaper)
- ✅ Reduced Gotenberg load (only Office documents)
- ✅ CSV files (common in FSIS data) handled efficiently by fpdf2 in-process

**Risks:**

- ⚠️ Multiple code paths require comprehensive testing

---

[← **ADR-005: Gotenberg for Office Document PDF Conversion**](005-gotenberg-pdf-conversion.md)
