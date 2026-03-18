[Home](../../README.md) > [Architecture](.) > **High-Level Architecture**

# High-Level Architecture

> **TL;DR:** AssuranceNet is an Azure-native document management system replacing Oracle UCM for FSIS. It uses an explicit document versioning model (logical Document + immutable DocumentVersion) with latest-only visibility for end users. Azure Blob Storage holds versioned binaries, FastAPI provides the backend API, React is a removable reference client, and an Event Grid + Functions pipeline handles async PDF conversion via a pluggable engine (Aspose default, Gotenberg fallback). Malware scanning uses a two-phase upload through a staging container. All services authenticate via Managed Identities with zero secrets.

---

## Table of Contents

- [Overview](#overview)
- [Architecture Diagram](#architecture-diagram)
- [Key Design Decisions](#key-design-decisions)
- [FSIS Data Context](#fsis-data-context)

---

## 📋 Overview

AssuranceNet Document Management is an Azure-native system replacing Oracle UCM for FSIS document storage, PDF conversion, and compliance auditing.

---

## 🏗️ Architecture Diagram

```mermaid
graph TB
    subgraph Users
        EU[AssuranceNet End Users]
    end

    subgraph Azure Cloud - eastus2
        subgraph Frontend
            SWA[Azure Static Web Apps<br/>React + TypeScript + Vite]
        end

        subgraph Application - Container Apps
            API[FastAPI Backend<br/>Container App]
        end

        subgraph PDF Pipeline
            FUNC[Azure Functions<br/>PDF Conversion]
            ASPOSE[Aspose SDK<br/>Word + Cells + Slides]
        end

        subgraph Data
            BLOB[Azure Blob Storage<br/>Versioned Documents]
            STAGING[Staging Container<br/>Malware Scanning]
            SQL[Azure SQL Database<br/>Document + DocumentVersion<br/>+ Audit + RBAC]
        end

        subgraph Security
            ENTRA[Microsoft Entra ID<br/>MSAL Auth]
            KV[Azure Key Vault]
            MI[Managed Identities<br/>App + Functions]
        end

        subgraph Monitoring
            LAW[Log Analytics Workspace]
            EH[Azure Event Hub<br/>Splunk Integration]
        end
    end

    EU -->|HTTPS| SWA
    EU -->|HTTPS| API
    SWA -->|MSAL Auth| ENTRA
    API -->|JWT Validation| ENTRA
    API --> BLOB
    API --> SQL
    API --> KV
    FUNC --> ASPOSE
    FUNC --> BLOB
    STAGING -->|scan clean| BLOB
    MI -.-> BLOB
    MI -.-> SQL
    MI -.-> KV
    LAW --> EH
```

### Deployed Resources (Dev Environment)

| Resource Group | Resources |
|---|---|
| `rg-assurancenet-app-dev` | Container App (API), Azure Functions (PDF), 2 CAE, ACR, SWA |
| `rg-assurancenet-data-dev` | Storage Account, SQL Server + Database |
| `rg-assurancenet-security-dev` | Key Vault, 2 Managed Identities |
| `rg-assurancenet-monitoring-dev` | Log Analytics, Event Hub, Dashboard |
| `rg-assurancenet-network-dev` | VNet (4 subnets), NSGs |

---

## ✨ Key Design Decisions

| Decision | Rationale |
|----------|-----------|
| **Azure Blob Storage** over SharePoint | 700K+ files at TB scale |
| **Explicit document versioning** | Logical Document + immutable DocumentVersion; latest-only visibility for end users |
| **Event Grid + Functions** for PDF pipeline | Async, event-driven conversion |
| **Aspose** (pluggable) for Office conversion | Production-grade fidelity; Gotenberg available as fallback via `PDF_ENGINE` config |
| **Two-phase upload** with malware scanning | Staging container → scan → promote to production |
| **Type-based merge ordering** | PDF merge sorted by `document_type`, not user order |
| **Managed Identities** for service auth | Zero-secret service-to-service authentication |
| **Private Endpoints** for data services | Network-level isolation for all data stores |

---

## 🗄️ FSIS Data Context

This system manages document types found across FSIS Science & Data programs
([fsis.usda.gov/science-data](https://www.fsis.usda.gov/science-data)):

| Document Category | Examples | Typical Formats |
|---|---|---|
| Sampling Program Plans | Annual Sampling Plans (FY2024, FY2025) | PDF |
| Laboratory Sampling Data | Quarterly microbiological/chemical results | CSV |
| Residue Program Reports | National Residue Program "Red Book" / "Blue Book", quarterly summaries | PDF |
| Microbiology Reports | Baseline data, Salmonella/Campylobacter quarterly reports | PDF, CSV |
| Establishment Directories | MPI Directory by Establishment Number/Name | CSV |
| Inspection Task Data | Humane handling verification records, enforcement actions | CSV, PDF |
| Chemical Residue Data | Quarterly tolerance/summary reports | PDF |
| Enforcement Reports | Quarterly enforcement tables | PDF |

> [!NOTE]
> These document types inform the investigation structures, blob naming, and PDF conversion pipeline design.

---

**Related Architecture Docs:**
[Azure Architecture Detail](azure-architecture-detail.md) | [Workflow Diagrams](workflow-diagrams.md) | [Blob Hierarchy](blob-hierarchy.md) | [Security Architecture](security-architecture.md) | [Monitoring & Telemetry](monitoring-telemetry.md) | [Data Migration](data-migration.md)
