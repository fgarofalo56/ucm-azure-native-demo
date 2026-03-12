[Home](../../README.md) > [Architecture](.) > **Monitoring & Telemetry Architecture**

# Monitoring & Telemetry Architecture

> **TL;DR:** Monitoring is centralized through a Log Analytics Workspace with three Application Insights instances (backend, functions, frontend). Alerts follow a 4-tier severity model. All logs are forwarded to Splunk via Event Hub for SIEM integration. FSIS-specific business metrics track document operations, conversion success rates, and data freshness.

---

## Table of Contents

- [Overview](#overview)
- [Components](#components)
- [Alert Strategy](#alert-strategy)
- [Custom Metrics](#custom-metrics)
- [FSIS-Specific Monitoring](#fsis-specific-monitoring)
- [Diagnostic Settings Coverage](#diagnostic-settings-coverage)

---

## 📋 Overview

Centralized monitoring via Log Analytics Workspace with three Application Insights instances and Splunk forwarding via Event Hub.

---

## 📊 Components

### 📊 Log Analytics Workspace

| Property | Value |
|----------|-------|
| Name | `law-assurancenet-{env}` |
| Interactive retention | 90 days |
| Archive retention | 3 years (NIST AU-11) |
| Scope | All Azure resource diagnostics |

### 📊 Application Insights (3 instances)

| Instance | Target | SDK |
|----------|--------|-----|
| `appi-backend-{env}` | FastAPI | OpenTelemetry SDK |
| `appi-functions-{env}` | Azure Functions | Built-in integration |
| `appi-frontend-{env}` | React SPA | Application Insights JS SDK |

### 🌐 Splunk Integration

```text
Azure Resources -> Diagnostic Settings -> Log Analytics
                                              |
                                    Data Export Rules
                                              |
                              Event Hub Namespace
                              |- evh-audit-logs
                              |- evh-diagnostic-logs
                                              |
                              Splunk Add-on for Microsoft Cloud
```

---

## 📊 Alert Strategy

The alert system follows a 4-tier severity model:

| Severity | Trigger | Action |
|----------|---------|--------|
| **Critical (Sev 0)** | 5xx rate > 5%, DLQ > 100 | Email + SMS + Teams |
| **Error (Sev 1)** | p95 > 3s, PDF timeout | Email + Teams |
| **Warning (Sev 2)** | p95 > 2s, capacity > 80% | Email |
| **Info (Sev 3)** | Daily counts, trends | Email digest |

> [!IMPORTANT]
> Critical (Sev 0) alerts require acknowledgment within 15 minutes during business hours. See the [Operations Guide](../guides/operations-guide.md) for escalation procedures.

---

## 📊 Custom Metrics

| Metric | Description |
|--------|-------------|
| `documents.uploaded` | Count of document uploads |
| `documents.downloaded` | Count of document downloads |
| `pdf.conversion.duration` | Time taken for PDF conversion |
| `pdf.conversion.status` | Success/failure status of conversions |
| `pdf.merge.duration` | Time taken for PDF merge operations |
| `pdf.merge.file_count` | Number of files in each merge request |
| `audit.events` | Audit event counts by type/action/result |

---

## 🗄️ FSIS-Specific Monitoring

### 📊 Key Business Metrics

| Metric | Description | Alert Threshold |
|---|---|---|
| Sampling Plan uploads/day | Annual sampling plan document uploads | None (informational) |
| CSV file conversions | MPI Directory and laboratory data CSV-to-PDF | Failure rate > 5% |
| Establishment data updates | MPI Directory refresh frequency | Stale > 30 days |
| Investigation document volume | Total docs per investigation type | > 10,000 per investigation |
| Merge operations/day | PDF merge requests for report compilation | > 100/day triggers review |

### 📊 FSIS Data Source Monitoring

Monitor availability and freshness of data sourced from [FSIS Science & Data](https://www.fsis.usda.gov/science-data):

| Data Source | Update Frequency |
|-------------|-----------------|
| Laboratory Sampling Data | Quarterly (current FY), annually (prior FYs in April) |
| Chemical Residue Reports | Quarterly |
| MPI Directory | Regularly (CSV files) |
| Inspection Task Data | Periodically |

### 📊 KQL Queries for FSIS Operations

**Documents uploaded by investigation type (last 7 days):**

```kql
AppRequests
| where TimeGenerated > ago(7d)
| where Name startswith "POST /api/v1/documents/upload"
| summarize UploadCount = count() by bin(TimeGenerated, 1d)
| render timechart
```

**PDF conversion results for CSV files (FSIS data imports):**

```kql
FunctionAppLogs
| where TimeGenerated > ago(24h)
| where Message contains "csv" or Message contains "CSV"
| summarize count() by Level
| render piechart
```

**Audit events for FSIS document operations:**

```kql
customEvents
| where TimeGenerated > ago(7d)
| where name == "audit.event"
| extend event_type = tostring(customDimensions.event_type)
| summarize count() by event_type
| order by count_ desc
```

### 🌐 Splunk Indexes for FSIS Data

| Splunk Index | Content | FSIS Relevance |
|---|---|---|
| `main` | Application audit events | Document operations, user actions |
| `azure_activity` | Azure Activity Logs | Resource changes, deployments |
| `azure_storage` | Blob Storage access logs | Document access patterns |
| `azure_sql` | SQL security audit | Database query audit |
| `azure_security` | Key Vault audit | Secret access monitoring |
| `azure_waf` | Front Door WAF logs | Attack detection |

---

## ⚙️ Diagnostic Settings Coverage

Every Azure resource has diagnostic settings configured to send logs and metrics to the
Log Analytics Workspace. See [Operations Guide](../guides/operations-guide.md) for
detailed KQL queries and dashboard usage.

> [!NOTE]
> Diagnostic settings are deployed via Bicep modules alongside each resource. Adding a new Azure resource requires a corresponding diagnostic settings configuration in its Bicep module.

---

**Related Architecture Docs:**
[High-Level Architecture](high-level-architecture.md) | [Azure Architecture Detail](azure-architecture-detail.md) | [Workflow Diagrams](workflow-diagrams.md) | [Blob Hierarchy](blob-hierarchy.md) | [Security Architecture](security-architecture.md) | [Data Migration](data-migration.md)
