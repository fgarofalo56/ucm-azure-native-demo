[Home](../../README.md) > [Architecture Decision Records](.) > **ADR-004**

# ADR-004: Bicep as Infrastructure-as-Code Tool

`🟢 Accepted`

---

## 📋 Status

Accepted

---

## 📋 Context

Need IaC for Azure resource provisioning across dev, staging, and production environments.

---

## ✅ Decision

Use Azure Bicep for all infrastructure definitions.

---

## 🔄 Alternatives Considered

| Alternative | Why Not Chosen |
|-------------|----------------|
| **Terraform** | Cross-cloud but adds HashiCorp dependency; Azure-only project |
| **ARM Templates** | Verbose JSON; Bicep is the improved DSL |
| **Pulumi** | Requires runtime; Bicep is declarative and Azure-native |

---

## ⚡ Consequences

**Positive:**

- ✅ Azure-native, first-class support
- ✅ Modular structure with parameter files per environment
- ✅ Direct `az deployment` integration in CI/CD
- ✅ Available in Azure Government (GovCloud compatible)

---

[← **ADR-003: FastAPI as Backend Framework**](003-fastapi-backend.md) | [**ADR-005: Gotenberg for Office Document PDF Conversion** →](005-gotenberg-pdf-conversion.md)
