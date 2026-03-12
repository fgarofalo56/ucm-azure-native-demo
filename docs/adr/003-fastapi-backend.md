[Home](../../README.md) > [Architecture Decision Records](.) > **ADR-003**

# ADR-003: FastAPI as Backend Framework

`🟢 Accepted`

---

## 📋 Status

Accepted

---

## 📋 Context

Need a Python web framework for the document management API with async support, type safety, and Azure SDK compatibility.

---

## ✅ Decision

Use FastAPI with Pydantic v2 for the backend API.

---

## 🔄 Alternatives Considered

| Alternative | Why Not Chosen |
|-------------|----------------|
| **Django REST Framework** | Heavier, less async-native |
| **Flask** | Lacks built-in validation, async support requires extensions |
| **.NET 8** | Team's primary expertise is Python; faster iteration with FastAPI |

---

## ⚡ Consequences

**Positive:**

- ✅ Auto-generated OpenAPI 3.1 documentation
- ✅ Native async/await for Azure SDK calls
- ✅ Pydantic v2 for request/response validation
- ✅ Excellent Azure SDK ecosystem in Python

---

[← **ADR-002: Event Grid for PDF Conversion Triggering**](002-event-grid-for-pdf-trigger.md) | [**ADR-004: Bicep as Infrastructure-as-Code Tool** →](004-bicep-iac.md)
