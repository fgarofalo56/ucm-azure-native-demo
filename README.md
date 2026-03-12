# AssuranceNet Document Management System

![Status](https://img.shields.io/badge/status-active-green)
![Stack](https://img.shields.io/badge/stack-Python%20%7C%20React%20%7C%20Azure-blue)
![IaC](https://img.shields.io/badge/IaC-Bicep-orange)
![License](https://img.shields.io/badge/license-MIT-yellow)

> **TL;DR** — Azure-native document management system replacing Oracle UCM for FSIS AssuranceNet.
> Upload, convert, merge, and version food safety investigation documents using FastAPI + React + Azure Bicep.
> Run `./scripts/setup/init-dev.sh` to set up locally, or deploy to Azure with `az deployment sub create`.

---

## 📑 Table of Contents

- [Architecture](#-architecture)
- [Quick Start](#-quick-start)
- [FSIS Demo Data](#-fsis-demo-data)
- [Project Structure](#-project-structure)
- [Deployment](#-deployment)
- [CI/CD](#-cicd)
- [Documentation](#-documentation)
- [API Endpoints](#-api-endpoints)
- [Environment Variables](#️-environment-variables)
- [License](#-license)

---

## 🏗️ Architecture

### Live Environment (Dev)

| Service | URL |
|---------|-----|
| **Frontend** | https://yellow-field-05ae8b90f.2.azurestaticapps.net |
| **Backend API** | https://ca-api-assurancenet-dev.reddune-5bb251d3.eastus2.azurecontainerapps.io |
| **API Health** | https://ca-api-assurancenet-dev.reddune-5bb251d3.eastus2.azurecontainerapps.io/api/v1/health |

```mermaid
flowchart LR
    subgraph Client
        FE["React SPA\n(Static Web Apps)"]
    end

    subgraph Azure
        API["FastAPI\n(Container Apps)"]
        GOT["Gotenberg\n(Container Apps)"]
        BLOB["Blob Storage\n(Versioned)"]
        SQL["Azure SQL\n(Metadata + Audit)"]
        KV["Key Vault"]
        ENTRA["Entra ID\n(MSAL Auth)"]
        MI["Managed Identity"]
    end

    FE -->|HTTPS| API
    API --> BLOB
    API --> SQL
    API --> KV
    API -.->|Token Auth| MI
    FE -.->|Auth| ENTRA
    API -.->|Validate JWT| ENTRA

    style FE fill:#61dafb,color:#000
    style API fill:#009688,color:#fff
    style GOT fill:#ff9800,color:#000
    style BLOB fill:#0078d4,color:#fff
    style SQL fill:#0078d4,color:#fff
```

| Component | Technology | Azure Resource | Location |
|-----------|-----------|----------------|----------|
| **Frontend** | React 18 + TypeScript + Vite | Static Web App (`swa-assurancenet-dev`) | `src/frontend/` |
| **Backend API** | Python 3.11+ FastAPI | Container App (`ca-api-assurancenet-dev`) | `src/backend/` |
| **PDF Service** | Gotenberg 8 | Container App (`ca-gotenberg-dev`) | Bicep IaC |
| **Storage** | Azure Blob Storage (versioned) | `stassurancenetdev` | Backend services |
| **Database** | Azure SQL (SQLAlchemy + Alembic) | `sql-assurancenet-dev` / `sqldb-assurancenet-dev` | `src/backend/app/db/` |
| **Auth** | Microsoft Entra ID (MSAL) | App Registrations (API + SPA) | Both frontend and backend |
| **Secrets** | Azure Key Vault | `kv-assurancenet-2-dev` | Infrastructure |
| **IaC** | Bicep modules (19 modules) | 5 resource groups | `infra/` |
| **Monitoring** | Log Analytics + Event Hub | `law-assurancenet-dev` | `rg-assurancenet-monitoring-dev` |

---

## 🚀 Quick Start

### Prerequisites

- Python 3.11+
- Node.js 20+
- Azure CLI
- ODBC Driver 18

```bash
# Initialize development environment
./scripts/setup/init-dev.sh

# Backend
cd src/backend
source .venv/bin/activate
uvicorn app.main:app --reload

# Frontend (separate terminal)
cd src/frontend
npm run dev

# Seed with FSIS demo data (after backend is running)
./scripts/setup/seed-data.sh
```

---

## 🗄️ FSIS Demo Data

The system includes demo data sourced from the [FSIS Science & Data portal](https://www.fsis.usda.gov/science-data):

| Investigation | Content | Source |
|---|---|---|
| FY2025 Annual Sampling Program | Annual sampling plans (FY2024–FY2025) | [Sampling Program](https://www.fsis.usda.gov/science-data/sampling-program) |
| National Residue Program | Red Book, Blue Book, quarterly reports | [Chemical Residues](https://www.fsis.usda.gov/science-data/data-sets-visualizations/chemical-residues-and-contaminants) |
| Microbiology Baseline Data | Sampling summary reports (FY2021, FY2024) | [Microbiology](https://www.fsis.usda.gov/science-data/data-sets-visualizations/microbiology) |
| MPI Directory Audit | Establishment directories (CSV) | [Laboratory Data](https://www.fsis.usda.gov/science-data/data-sets-visualizations/laboratory-sampling-data) |
| STEC Sampling Results | E. coli O157:H7 and non-O157 STEC data | [Sampling Results](https://www.fsis.usda.gov/science-data/sampling-program/sampling-results-fsis-regulated-products) |

Run `./scripts/setup/seed-data.sh` to create investigations and download sample files.
See [`scripts/setup/fsis-demo-data.json`](scripts/setup/fsis-demo-data.json) for the full data configuration.

---

## 📁 Project Structure

```
ucm-azure-native-demo/
├── 📁 infra/                  # Bicep infrastructure-as-code
│   ├── 📁 modules/            # 18 modular Azure resource definitions
│   └── 📁 parameters/         # Environment-specific parameters (dev/staging/prod)
├── 📁 src/
│   ├── 📁 backend/            # FastAPI Python API
│   ├── 📁 frontend/           # React TypeScript SPA
│   └── 📁 functions/          # Azure Functions (PDF conversion)
├── 📁 docs/
│   ├── 📁 architecture/       # Architecture documentation (7 docs)
│   ├── 📁 adr/                # Architecture Decision Records (6 ADRs)
│   ├── 📁 api/                # OpenAPI specification
│   ├── 📁 diagrams/           # Excalidraw interactive diagrams
│   ├── 📁 guides/             # User, deployment, developer, operations guides
│   └── 📁 runbooks/           # Operational runbooks (4 runbooks)
├── 📁 scripts/
│   ├── 📁 migration/          # UCM to Azure migration tooling
│   └── 📁 setup/              # Dev environment setup + FSIS demo data
├── 📁 tests/
│   ├── 📁 backend/            # Python unit + integration tests
│   ├── 📁 functions/          # Azure Functions tests
│   ├── 📁 frontend/           # React component + E2E tests
│   └── 📁 infra/              # Bicep validation tests
├── 📄 CLAUDE.md               # Claude Code project instructions
├── 📄 CONTRIBUTING.md         # Contribution guidelines
├── 📄 SECURITY.md             # Security policy
└── 📄 README.md               # This file
```

---

## 📦 Deployment

Multiple deployment methods are supported. See the [Deployment Guide](docs/guides/deployment-guide.md) for complete instructions.

```mermaid
flowchart LR
    A[Choose Method] --> B{Method?}
    B -->|Recommended| C["Bicep IaC"]
    B -->|Manual| D["Azure CLI"]
    B -->|Automated| E["GitHub Actions"]
    B -->|Explore| F["Azure Portal"]
    C --> G["az deployment sub create"]
    D --> H["Individual az commands"]
    E --> I["Push to main"]
    F --> J["GUI-based"]
    style C fill:#2ea44f,color:#fff
```

| Method | Command | Best For |
|---|---|---|
| **Bicep** (recommended) | `az deployment sub create --template-file infra/main.bicep --parameters infra/parameters/dev.bicepparam` | Full environment deployment |
| **Azure CLI** | Individual `az` commands per resource | Learning, single resource changes |
| **Azure PowerShell** | `New-AzResourceGroup`, `New-AzResourceGroupDeployment` | PowerShell-based workflows |
| **Azure Portal** | GUI-based resource creation | Exploration, manual verification |
| **GitHub Actions** | Push to `main` branch | Automated CI/CD |

### 🚀 Quick Deploy (Bicep)

```bash
# Login
az login
az account set --subscription <your-subscription-id>

# Validate
az deployment sub what-if --location eastus \
  --template-file infra/main.bicep \
  --parameters infra/parameters/dev.bicepparam

# Deploy
az deployment sub create --location eastus \
  --template-file infra/main.bicep \
  --parameters infra/parameters/dev.bicepparam
```

---

## 🔄 CI/CD

| Workflow | Trigger | Purpose | Status |
|---|---|---|---|
| `ci.yml` | Push/PR to main | Lint, test, security scan, Bicep validate | Active |
| `deploy-backend.yml` | Push to main (`src/backend/`) | ACR build + deploy to Container Apps | Active |
| `deploy-frontend.yml` | Push to main (`src/frontend/`) | Vite build + deploy to Static Web App | Active |
| `deploy-infra.yml` | Push to main (`infra/`) | Bicep infrastructure deployment | Active |
| `deploy-functions.yml` | Push to main (`src/functions/`) | Functions build + deploy | Active |
| `db-migrate.yml` | Manual dispatch | Alembic database migrations | Active |
| `security-scan.yml` | Push to main | CodeQL SAST + dependency audit | Active |

---

## 📚 Documentation

### 📖 Guides

| Guide | Audience | Description |
|-------|----------|-------------|
| [User Guide](docs/guides/user-guide.md) | FSIS Staff | End-user documentation |
| [Deployment Guide](docs/guides/deployment-guide.md) | DevOps | Step-by-step deployment (Portal, CLI, Bicep, GitHub Actions) |
| [Developer Guide](docs/guides/developer-guide.md) | Developers | Dev environment setup, coding patterns, testing |
| [Operations Guide](docs/guides/operations-guide.md) | SRE / Ops | Monitoring, alerting, maintenance, backup/recovery |
| [Best Practices](docs/guides/best-practices.md) | All | Security, infrastructure, development best practices |
| [Troubleshooting](docs/guides/troubleshooting.md) | All | Common issues with symptoms, causes, and solutions |

### 🏗️ Architecture

| Document | Description |
|----------|-------------|
| [High-Level Architecture](docs/architecture/high-level-architecture.md) | System overview and component relationships |
| [Detailed Azure Architecture](docs/architecture/azure-architecture-detail.md) | Resource groups, networking, managed identities |
| [User Workflow Diagrams](docs/architecture/workflow-diagrams.md) | Sequence diagrams for all user flows |
| [Blob Hierarchy Specification](docs/architecture/blob-hierarchy.md) | Storage container layout and naming conventions |
| [Security Architecture](docs/architecture/security-architecture.md) | Authentication, authorization, encryption |
| [Monitoring & Telemetry](docs/architecture/monitoring-telemetry.md) | OpenTelemetry, App Insights, Log Analytics |
| [Data Migration Strategy](docs/architecture/data-migration.md) | Oracle UCM to Azure migration approach |

### 📎 Reference

| Resource | Description |
|----------|-------------|
| [Architecture Decision Records](docs/adr/) | ADR-001 through ADR-006 |
| [OpenAPI Specification](docs/api/openapi-spec.yaml) | Full API contract |
| [Deployment Runbook](docs/runbooks/deployment.md) | Step-by-step deployment procedures |
| [Incident Response Runbook](docs/runbooks/incident-response.md) | Incident handling procedures |
| [Data Migration Runbook](docs/runbooks/data-migration-runbook.md) | Migration execution steps |
| [Splunk Integration Runbook](docs/runbooks/splunk-integration.md) | SIEM integration setup |

---

## 🔌 API Endpoints

| Method | Endpoint | Auth | Description |
|---|---|---|---|
| `GET` | `/api/v1/health` | None | Liveness probe |
| `GET` | `/api/v1/health/ready` | None | Readiness probe (DB + storage) |
| `GET` | `/api/v1/investigations/` | `investigations.read` | List investigations (paginated) |
| `POST` | `/api/v1/investigations/` | `investigations.create` | Create investigation |
| `GET` | `/api/v1/investigations/{id}` | `investigations.read` | Get investigation details |
| `PUT` | `/api/v1/investigations/{id}` | `investigations.update` | Update investigation |
| `GET` | `/api/v1/investigations/{id}/documents` | `documents.read` | List documents for investigation |
| `POST` | `/api/v1/documents/upload` | `documents.create` | Upload document (multipart) |
| `POST` | `/api/v1/documents/batch-upload/{id}` | `documents.create` | Batch upload multiple files |
| `GET` | `/api/v1/documents/{id}` | `documents.read` | Get document metadata |
| `GET` | `/api/v1/documents/{id}/download` | `documents.download` | Download original file |
| `GET` | `/api/v1/documents/{id}/pdf` | `documents.download` | Download PDF version |
| `GET` | `/api/v1/documents/{id}/versions` | `documents.read` | List document versions |
| `DELETE` | `/api/v1/documents/{id}` | `documents.delete` | Soft-delete document |
| `POST` | `/api/v1/investigations/{recordId}/merge-pdf` | `documents.merge` | Merge multiple PDFs |
| `POST` | `/api/v1/audit/logs` | `audit.read` | Query audit logs |
| `GET` | `/api/v1/search/?q=` | Authenticated | Search investigations and documents |
| `GET` | `/api/v1/explorer/browse` | `documents.read` | Browse blob storage explorer |
| `DELETE` | `/api/v1/explorer/files` | `documents.delete` | Batch delete blob files |
| `GET` | `/api/v1/admin/me` | Authenticated | Current user + roles + permissions |
| `GET` | `/api/v1/admin/users` | `users.read` | List all users |
| `GET` | `/api/v1/admin/roles` | `roles.manage` | List all roles |
| `PUT` | `/api/v1/admin/users/{id}/roles` | `roles.manage` | Assign roles to user |

---

## ⚙️ Environment Variables

See [`src/backend/.env.example`](src/backend/.env.example) for the complete reference.

| Variable | Description | Default |
|---|---|---|
| `ENVIRONMENT` | Environment name (`dev`/`staging`/`prod`) | `dev` |
| `AZURE_STORAGE_ACCOUNT_NAME` | Storage account name | — |
| `AZURE_SQL_SERVER` | SQL server FQDN | — |
| `AZURE_SQL_DATABASE` | SQL database name | — |
| `AZURE_KEY_VAULT_URI` | Key Vault URI | — |
| `ENTRA_TENANT_ID` | Entra ID tenant | — |
| `ENTRA_CLIENT_ID` | API app registration client ID | — |
| `ENTRA_AUDIENCE` | JWT audience | `api://assurancenet-api` |
| `MAX_UPLOAD_SIZE_MB` | Max file upload size | `500` |
| `MAX_MERGE_FILES` | Max files in PDF merge | `50` |

---

## 📄 License

MIT

---

*Last updated: 2026-03-12*
