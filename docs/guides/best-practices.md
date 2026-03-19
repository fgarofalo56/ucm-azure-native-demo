[Home](../../README.md) > [Guides](.) > **Best Practices Guide**

# AssuranceNet Best Practices Guide

> **TL;DR:** Engineering standards for security, infrastructure, development, and operations across the AssuranceNet platform. Covers Managed Identity usage, Private Endpoints, structured logging, testing requirements, CI/CD pipelines, and cost optimization. Every team member contributing to the platform should follow these practices.

---

## Table of Contents

1. [Security](#1-security)
2. [Infrastructure (Bicep/IaC)](#2-infrastructure-bicepiac)
3. [Backend Development (Python/FastAPI)](#3-backend-development-pythonfastapi)
4. [Frontend Development (React/TypeScript)](#4-frontend-development-reacttypescript)
5. [PDF Conversion](#5-pdf-conversion)
6. [Data Migration](#6-data-migration)
7. [Monitoring & Observability](#7-monitoring--observability)
8. [CI/CD](#8-cicd)
9. [Testing](#9-testing)
10. [Cost Optimization](#10-cost-optimization)

---

## 1. Security

Security is non-negotiable in a federal system handling FSIS documents. Every design decision must default to the most restrictive option and open up only what is explicitly required.

### 🔒 Identity and Authentication

- **Use Managed Identities everywhere.** Every Azure resource that supports Managed Identity must use one. Never store credentials in code, configuration files, environment variables, or App Settings when a Managed Identity can be used instead.
- **Entra ID for all user authentication.** Use MSAL.js with the redirect flow (not popup) for the React frontend. Popup flows are blocked by many federal browser policies and ad blockers.
- **App Roles for RBAC.** Define and enforce the following roles through Entra ID App Registrations:

  | Role | Access Level |
  |------|-------------|
  | `Documents.Reader` | Read-only access to documents |
  | `Documents.Contributor` | Upload, update, and manage documents |
  | `Investigations.Manager` | Manage investigation workflows and merge operations |
  | `Admin` | Full administrative access including user management and system configuration |

- **JWT validation must check all claims.** Every API endpoint must validate `aud` (audience), `iss` (issuer), `exp` (expiration), and `roles`. Never trust a token without verifying all four. Use the FastAPI dependency injection pattern to enforce this consistently.

### 🔒 Network Security

> [!IMPORTANT]
> All data services must be accessible only through Private Endpoints within the VNet. Public network access must be disabled.

- **Private Endpoints for all data services.** Azure Blob Storage, Azure SQL, Key Vault, and Event Hub must be accessible only through Private Endpoints within the VNet. Disable public network access on each resource.
- **Never expose backend services directly.** Azure Front Door is the only public entry point. App Services, Functions, and all other backend components sit behind the VNet and are reachable only through Front Door's origin configuration.
- **WAF on Front Door.** Enable the Web Application Firewall with the OWASP 3.2 managed rule set. Add custom rules for any application-specific patterns.
- **NSG rules follow least privilege.** Each subnet's Network Security Group should allow only the traffic required for that subnet's purpose. Default-deny everything else. Document every rule with a description explaining why it exists.
- **HTTPS-only on all services.** Disable HTTP on every App Service and Function App. Set `httpsOnly: true` in Bicep templates.
- **TLS 1.2 minimum.** Configure `minTlsVersion: '1.2'` on all services. TLS 1.0 and 1.1 are prohibited.

### 🔒 Secrets Management

- **Key Vault for any secrets that cannot use Managed Identity.** Third-party API keys, connection strings to external systems, and similar values belong in Key Vault with access policies scoped to the specific Managed Identity that needs them.
- **Never commit secrets.** Use `gitleaks` in CI to catch accidental commits. Add `.env` files and credential patterns to `.gitignore`.

### 🔒 Input Validation

- **Pydantic models on all API endpoints.** Every request body, query parameter, and path parameter must be validated through a Pydantic model. Never access raw request data directly.
- **File upload validation.** Enforce size limits (configurable per environment, default 100 MB) and verify content-type headers against the actual file content. Do not rely solely on the file extension.

---

## 2. Infrastructure (Bicep/IaC)

All infrastructure is defined in Bicep and deployed through CI/CD pipelines. No manual Azure Portal changes in any environment.

### 🏗️ Module Structure

- **Use Bicep modules for reusable components.** Each Azure resource type (App Service, Storage Account, SQL Database, etc.) should have a dedicated module that encapsulates its configuration, diagnostic settings, and Private Endpoint setup.
- **Parameter files per environment.** Maintain separate parameter files:

  | File | Purpose |
  |------|---------|
  | `dev.bicepparam` | Development settings with cost-optimized SKUs |
  | `staging.bicepparam` | Production-like configuration for validation |
  | `prod.bicepparam` | Production configuration with full redundancy and scale |

### ⚙️ Resource Standards

- **Tag all resources.** Every resource must include at minimum:

  | Tag | Values |
  |-----|--------|
  | `Environment` | `dev`, `staging`, or `prod` |
  | `Project` | `AssuranceNet` |
  | `ManagedBy` | `Bicep` |

- **Enable diagnostic settings on every resource.** Route logs and metrics to the central Log Analytics workspace. This is not optional; resources without diagnostics are invisible to operations.
- **Use Private Endpoints and disable public access.** This applies to Storage Accounts, SQL Servers, Key Vaults, and Event Hubs. Set `publicNetworkAccess: 'Disabled'` in every Bicep definition.

### 🗄️ Data Protection

- **Enable soft delete on Storage Accounts.** Set blob soft delete to 30 days and container soft delete to 30 days. This provides recovery capability for accidental deletions.
- **Enable soft delete on Key Vault.** Set purge protection with a 90-day retention. Key Vault soft delete is enabled by default but purge protection must be explicitly set.
- **Enable blob versioning and change feed.** Versioning provides point-in-time recovery for individual blobs. Change feed enables auditing of all blob operations.

### 📦 Deployment Safety

> [!WARNING]
> Never deploy without running `what-if` first. Understanding what will change prevents accidental resource deletions or modifications.

- **Use what-if before every deployment.** The CI/CD pipeline must run `az deployment group what-if` and present the results for review before applying changes.
- **Budget alerts at 80% and 100%.** Configure Azure Budget resources with action groups that notify the team at 80% (warning) and 100% (critical) of the monthly budget.

### 🔒 Compliance

- **NIST 800-53 policy assignments.** Assign the NIST 800-53 Rev 5 policy initiative to all resource groups. Remediate any non-compliant resources before they reach production.
- **Microsoft Defender for Cloud on all resource types.** Enable Defender plans for App Service, Storage, SQL, Key Vault, and Containers. Review the Secure Score weekly.

---

## 3. Backend Development (Python/FastAPI)

The backend is a FastAPI application serving the REST API for document management, investigation workflows, and system administration.

### ⚙️ Configuration and Dependencies

- **Use `pydantic-settings` for configuration.** Define a `Settings` class that reads from environment variables with sensible defaults for local development. Never hardcode configuration values.
- **Dependency injection via `Depends()`.** Database sessions, authenticated users, Azure SDK clients, and configuration should all flow through FastAPI's dependency injection system. This keeps endpoint functions clean and makes testing straightforward.

### 📊 Logging and Observability

- **Use `structlog` for structured logging.** Never use `print()` or the standard `logging` module directly. Structlog produces JSON-formatted logs that integrate cleanly with Application Insights and Log Analytics.
- **Correlation IDs on every request.** Generate or propagate a correlation ID for each incoming request. Include it in all log entries and pass it to downstream service calls. This is essential for tracing requests across the distributed system.
- **Audit logging for all state-changing operations.** Every create, update, delete, upload, merge, and status change must produce an audit log entry that records who did what, when, and to which resource.

### ⚡ Performance

- **Use `async`/`await` for I/O-bound operations.** Database queries, Azure SDK calls, and HTTP requests to other services should all use async patterns. FastAPI is built on Starlette's async runtime; blocking the event loop degrades throughput for all users.
- **Stream large files.** Never load an entire file into memory for upload or download. Use streaming upload with `azure-storage-blob`'s `upload_blob` (which accepts streams) and streaming download with `StorageStreamDownloader`. This keeps memory usage constant regardless of file size.

### 🔒 Data Integrity

- **SHA-256 checksums for file integrity.** Compute a SHA-256 hash for every file at upload time and store it alongside the metadata. Verify the checksum on download and after migration operations.
- **Use Alembic for database migrations.** All schema changes go through Alembic migration scripts checked into source control. Never run manual SQL against production. Every migration must have a corresponding downgrade path.

### 🧪 Code Quality

- **Type hints everywhere.** Run `mypy` in strict mode. Every function signature, variable declaration, and return type should be annotated. This catches entire categories of bugs before runtime.
- **Ruff for linting.** Configure Ruff to include the `S` (bandit) rule set for security checks alongside standard Python linting. Run it in CI and block merges on violations.
- **Test with `pytest`.** Mock Azure SDK clients using `unittest.mock` or `pytest-mock`. Test business logic in isolation from Azure infrastructure.

---

## 4. Frontend Development (React/TypeScript)

The frontend is a React single-page application built with TypeScript, served through Azure Front Door.

### 🧪 TypeScript and Code Quality

- **TypeScript strict mode.** Enable `strict: true` in `tsconfig.json`. This includes `strictNullChecks`, `noImplicitAny`, and all other strict checks. Loose typing defeats the purpose of using TypeScript.

### 🔒 Authentication

- **MSAL React for authentication.** Use the `@azure/msal-react` library with the `useMsal` hook pattern. Wrap the app in `MsalProvider` and use `AuthenticatedTemplate` / `UnauthenticatedTemplate` for conditional rendering.
- **Axios interceptor for auth token injection.** Configure an Axios request interceptor that acquires a token silently (falling back to redirect) and attaches it as a Bearer token on every API request. Never manually attach tokens to individual requests.

### ⚙️ Data Fetching and State

- **TanStack React Query for server state.** All API data fetching, caching, and synchronization should go through React Query. It handles loading states, error states, caching, background refetching, and optimistic updates out of the box.
- **Handle loading and error states explicitly.** Every component that fetches data must render appropriate loading indicators and error messages. Never show a blank screen or stale data without indication.

### 💡 File Handling

- **React Dropzone for file uploads.** Use `react-dropzone` for drag-and-drop file uploads with progress tracking. Show upload progress, validate file types and sizes on the client side before sending to the API, and handle failures gracefully.

### ⚡ Styling and Performance

- **Tailwind CSS for styling.** Use the utility-first approach. Avoid writing custom CSS unless Tailwind utilities genuinely cannot express the design. Keep the design system consistent by defining custom theme values in `tailwind.config.ts`.
- **Lazy load routes for performance.** Use `React.lazy()` and `Suspense` for route-level code splitting. The initial bundle should contain only the authentication flow and the shell layout.

### 🧪 Testing

- **Vitest for unit tests.** Test components, hooks, and utility functions with Vitest and React Testing Library. Focus on user-visible behavior, not implementation details.
- **Playwright for E2E tests.** End-to-end tests cover critical user workflows: login, document upload, search, investigation creation, PDF merge, and download.

---

## 5. PDF Conversion

The PDF conversion pipeline transforms Office documents, images, and text files into PDF format for standardized storage and FOIA response compilation.

### 🏗️ Architecture

- **Event-driven architecture.** Use Azure Event Grid to trigger conversions when new documents are uploaded. Never poll a queue or database table for new work.
- **Hybrid conversion approach.** Use the right tool for each file type:

  | File Type | Converter |
  |-----------|-----------|
  | Office documents (Word, Excel, PowerPoint) | Aspose SDK (licensed) or Gotenberg HTTP API (optional opensource fallback) |
  | Images (JPEG, PNG, TIFF, BMP) | Pillow -- PIL-based in-process conversion |
  | Plain text / CSV / RTF | fpdf2 -- in-process text rendering |

### ⚙️ Reliability

- **120-second timeout for conversions.** Set this as the maximum duration for any single conversion operation. If a file cannot convert within this window, it should fail rather than block the pipeline.
- **3 retries with exponential backoff.** Failed conversions retry at intervals of approximately 1 second, 4 seconds, and 16 seconds. After three failures, the event moves to the dead-letter container.
- **Dead-letter container for failed events.** Store failed conversion events in a dedicated blob container with the original file reference, error details, and timestamps. Monitor this container and alert on growth.
- **Track conversion status in the database.** Every document has a conversion status field (`pending`, `processing`, `completed`, `failed`) that the frontend queries to show progress.

### 💡 Merged PDFs

> [!NOTE]
> Do not persist merged PDFs. Investigation packet merges should be generated on demand and streamed directly to the client. Storing merged PDFs creates data duplication, staleness problems, and storage cost bloat.

---

## 6. Data Migration

Migration from Oracle UCM to AssuranceNet must preserve every document, every piece of metadata, and every relationship without data loss.

### ⚙️ Processing Strategy

- **Batch processing in groups of 10,000 files.** This keeps each batch manageable for monitoring, error handling, and potential re-runs. Log batch start, progress, and completion.
- **20 concurrent async workers.** Use `asyncio.Semaphore(20)` to limit concurrency. This balances throughput against Azure throttling limits and network saturation.
- **Resume capability.** Track the status of every file in the migration status table. On restart, skip files marked as `completed` and retry files marked as `failed` or `in_progress`. The migration must be safely restartable at any point.

### 🔒 Data Integrity

- **SHA-256 checksum verification for every file.** Compute the checksum from Oracle UCM, store it, transfer the file, compute the checksum from Azure Blob Storage, and compare. Any mismatch is a hard failure for that file.
- **Validate 100% of checksums post-migration.** After the full migration run, execute a separate validation pass that reads every blob and verifies its checksum against the source record. This is the final quality gate before cutover.

### 📊 Migration Tracking

- **Migration status tracking table.** Maintain a dedicated table with columns for source ID, target blob path, status, checksum (source), checksum (target), error message, and timestamps. This table is the single source of truth for migration progress.
- **30-day parallel run.** After migration completes, keep Oracle UCM running in read-only mode for 30 days. During this period, validate that all workflows function correctly against AssuranceNet. This provides a safety net for any issues discovered post-migration.
- **Rollback scripts ready before starting.** Prepare and test rollback procedures that can revert the migration and redirect traffic back to Oracle UCM. Never begin a migration without a tested fallback plan.

---

## 7. Monitoring & Observability

Comprehensive observability is required for a system handling federal documents. Every component must be instrumented, and the team must have clear visibility into system health at all times.

### 📊 Instrumentation

- **Application Insights on all components.** The FastAPI backend, Azure Functions, and the React frontend must all report telemetry to Application Insights. Use the OpenTelemetry SDK for backend instrumentation and the Application Insights JavaScript SDK for the frontend.
- **Log Analytics as the central workspace.** All logs, metrics, and diagnostic data flow to a single Log Analytics workspace. This enables cross-resource queries and unified alerting.
- **Diagnostic settings on every Azure resource.** This is enforced at the infrastructure level (see Section 2) but bears repeating: a resource without diagnostic settings is invisible.

### 📊 Metrics and Alerting

- **Custom metrics for business KPIs.** Track and surface the following:

  | Metric | Granularity |
  |--------|------------|
  | Document upload count and size | Daily, weekly |
  | PDF conversion duration | P50, P95, P99 |
  | PDF merge duration | P50, P95, P99 |
  | Investigation creation and completion rates | Weekly |
  | Failed conversion and upload counts | Daily |

- **4-tier alert strategy.** Configure alerts at four severity levels:

  | Tier | Response | Notification |
  |------|----------|-------------|
  | **Critical** | Service down, data loss risk, security incident | Pages on-call immediately |
  | **Error** | Elevated failure rates, degraded performance | Notifies team within 15 minutes |
  | **Warning** | Approaching thresholds, unusual patterns | Email notification |
  | **Info** | Notable events for awareness | Logged, no notification |

### 📊 Dashboards and Retention

- **Azure Dashboards for operational visibility.** Build dashboards covering system health (App Service metrics, SQL DTU, storage capacity), pipeline status (conversion queue depth, failure rates), and business metrics (documents processed, investigations active).
- **Splunk forwarding via Event Hub.** Stream security-relevant logs to Event Hub for consumption by the FSIS Splunk SIEM instance. This satisfies the centralized security monitoring requirement.
- **90-day interactive retention plus 3-year archive.** Keep logs queryable in Log Analytics for 90 days. Archive to Storage Account (cool tier) for 3 years to satisfy NIST AU-11 audit log retention requirements.

---

## 8. CI/CD

The CI/CD pipeline enforces quality gates and automates deployment across all environments. No manual deployments.

### 🔒 Authentication

- **OIDC federated credentials.** GitHub Actions authenticates to Azure using OpenID Connect workload identity federation. No client secrets or certificates are stored in GitHub. Configure a federated credential for each environment (dev, staging, prod) with appropriate subject claims.

### 🔄 Pipeline Structure

- **Separate workflows per component.** The backend, frontend, infrastructure, and Azure Functions each have their own workflow file. Changes to one component do not trigger unnecessary builds of others. Use `paths` filters in workflow triggers.
- **PR validation runs on every pull request.** The PR validation workflow must pass before merge is allowed. It includes:
  - Linting (Ruff for Python, ESLint for TypeScript)
  - Unit tests (pytest, Vitest)
  - Security scanning (CodeQL SAST)
  - Bicep build validation (`az bicep build`)
  - Dependency scanning (`pip-audit`, `npm audit`)
  - Secret scanning (`gitleaks`)

### 📦 Deployment Strategy

- **Blue/green deployment via staging slots.** Deploy to the staging slot of each App Service, validate health endpoints and smoke tests, then swap to production. If the swap fails or health checks degrade, swap back immediately.
- **Approval gates for staging and production.** GitHub Environments with required reviewers gate deployments to staging (1 reviewer) and production (2 reviewers). No automated deployment to production without human approval.

### 🧪 Quality Thresholds

- **Coverage threshold: 80% minimum.** Both the Python backend and TypeScript frontend must maintain at least 80% code coverage. The CI pipeline fails if coverage drops below this threshold.

---

## 9. Testing

A robust testing strategy ensures reliability across the full stack.

### 🧪 Unit Tests

- **Mock Azure SDK clients.** Unit tests must not call real Azure services. Use `unittest.mock.patch` or `pytest-mock` to replace `BlobServiceClient`, `SecretClient`, and similar SDK clients with fakes that return controlled responses.
- **Test business logic in isolation.** Separate business rules from framework and infrastructure code. The core logic for document validation, metadata extraction, checksum computation, and status transitions should be testable without FastAPI or Azure dependencies.
- **AAA pattern: Arrange, Act, Assert.** Structure every test in three clear sections. This makes tests readable and ensures each test verifies one behavior.

### 🧪 Integration Tests

- **Test API endpoints with test fixtures.** Use FastAPI's `TestClient` (or the async equivalent `httpx.AsyncClient`) to test full request/response cycles. Set up test data in `conftest.py` fixtures and clean up after each test.
- **Use `conftest.py` for shared fixtures.** Database sessions, authenticated test users, sample documents, and common setup belong in `conftest.py` files at the appropriate directory level. Avoid duplicating fixture code across test files.

### 🧪 End-to-End Tests

- **Playwright for full user workflows.** E2E tests exercise the system as a user would: log in, upload a document, search for it, create an investigation, add documents, merge PDFs, and download the result. These tests run against a deployed environment (typically staging).

### 🧪 Infrastructure Tests

- **Bicep build validation.** Run `az bicep build` on all Bicep files in CI to catch syntax errors, type mismatches, and invalid resource configurations before deployment.

### 📊 Coverage

- **80% minimum, enforced in CI.** The pipeline fails if coverage drops below 80%. Coverage reports are generated and uploaded as build artifacts for review.

---

## 10. Cost Optimization

Federal cloud budgets are finite. Use the right SKU for each environment and avoid paying for idle resources.

### ⚙️ Environment-Appropriate SKUs

| Resource | Dev | Staging | Production |
|---|---|---|---|
| Azure SQL | Serverless (auto-pause) | Standard S1 | Standard S2+ |
| App Service Plan | B1 (Basic) | P1v3 | P1v3 |
| Storage Account | LRS (locally redundant) | GRS (geo-redundant) | GRS (geo-redundant) |
| PDF Engine | OpenSource (in-process) | OpenSource or Aspose | Aspose (licensed) |

### ⚡ Compute Optimization

- **Serverless SQL for dev.** Configure auto-pause with a 1-hour delay. Development databases sit idle most of the time; serverless billing stops during idle periods.
- **In-process PDF conversion.** PDF conversion runs inside the FastAPI backend container — no separate compute needed. This eliminates idle costs from dedicated conversion services. The engine (opensource or Aspose) is configurable via the Admin Settings UI.

### 📊 Storage and Logging

- **Log Analytics commitment tier for production.** If production ingests more than 100 GB/day, switch from pay-as-you-go to a commitment tier for significant savings. Review ingestion volume monthly.
- **Review cost reports monthly.** Use Azure Cost Management to review spending by resource group, resource type, and tag. Identify any resources that have drifted from expected costs.

### 💡 Budget Controls

- **Budget alerts at 80% and 100%.** Configured at the infrastructure level (see Section 2). The 80% alert triggers investigation; the 100% alert triggers immediate action. Both notify the team lead and the cloud operations channel.

---

## 📌 Quick Reference Checklist

Use this checklist when starting new work or conducting code reviews.

### Before Committing Code

- [ ] No secrets, credentials, or connection strings in code or config files
- [ ] All new API endpoints have Pydantic request/response models
- [ ] All new endpoints validate JWT claims (aud, iss, exp, roles)
- [ ] Structured logging with correlation ID on new code paths
- [ ] Audit log entries for state-changing operations
- [ ] Type hints on all new functions and methods
- [ ] Unit tests for new business logic (80% coverage maintained)
- [ ] Ruff and mypy pass without errors

### Before Deploying Infrastructure

- [ ] Bicep `what-if` reviewed and approved
- [ ] Diagnostic settings included on new resources
- [ ] Private Endpoints configured, public access disabled
- [ ] Resource tags (Environment, Project, ManagedBy) applied
- [ ] Soft delete and versioning enabled on storage resources

### Before Production Release

- [ ] All PR checks passing (lint, test, security scan, coverage)
- [ ] Staging deployment validated with smoke tests
- [ ] Approval gates satisfied (2 reviewers for production)
- [ ] Rollback plan documented and tested
- [ ] Monitoring dashboards updated for new features
- [ ] Alert rules configured for new failure modes

---

> **Navigation:** [Guides Home](README.md) | [User Guide](user-guide.md) | [Deployment Guide](deployment-guide.md) | [Developer Guide](developer-guide.md) | [Operations Guide](operations-guide.md) | [Troubleshooting](troubleshooting.md)
