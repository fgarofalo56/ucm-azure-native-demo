[Home](../../README.md) > **Guides**

# AssuranceNet Documentation Guides

> **TL;DR:** Comprehensive documentation for the AssuranceNet Document Management System -- an Azure-native replacement for Oracle UCM used by FSIS (Food Safety and Inspection Service). Start with the User Guide or Developer Guide if you are new.

---

## ✨ Available Guides

| Guide | Audience | Description |
|---|---|---|
| [User Guide](user-guide.md) | FSIS end users | How to use the application: investigations, documents, PDF operations, audit logs |
| [Deployment Guide](deployment-guide.md) | DevOps / Platform | Step-by-step deployment via Portal, CLI, PowerShell, Bicep, and GitHub Actions |
| [Developer Guide](developer-guide.md) | Developers | Development environment setup, coding patterns, testing, FSIS demo data |
| [Operations Guide](operations-guide.md) | SRE / Operations | Monitoring, alerting, maintenance, backup/recovery, Splunk integration |
| [Best Practices Guide](best-practices.md) | All technical staff | Security, infrastructure, development, and operational best practices |
| [Troubleshooting Guide](troubleshooting.md) | All technical staff | Common issues organized by symptoms, causes, and solutions |

---

## 🚀 Quick Reference

- **New to the project?** Start with the [User Guide](user-guide.md) or [Developer Guide](developer-guide.md)
- **Deploying?** See the [Deployment Guide](deployment-guide.md)
- **Something broken?** Check the [Troubleshooting Guide](troubleshooting.md)
- **Setting up monitoring?** See the [Operations Guide](operations-guide.md)
- **Code review?** Reference the [Best Practices Guide](best-practices.md)

---

## 🔗 Related Documentation

- [Architecture Documentation](../architecture/) - System design and diagrams
- [Architecture Decision Records](../adr/) - Key design decisions
- [Operational Runbooks](../runbooks/) - Step-by-step operational procedures
- [OpenAPI Specification](../api/openapi-spec.yaml) - API reference
- [FSIS Demo Data Configuration](../../scripts/setup/fsis-demo-data.json) - Sample data from FSIS Science & Data

---

## 🗄️ FSIS Data Source

Demo data and document types are sourced from the
[FSIS Science & Data portal](https://www.fsis.usda.gov/science-data), including:

| Dataset | Link |
|---------|------|
| Sampling Program | [Annual sampling plans](https://www.fsis.usda.gov/science-data/sampling-program) |
| Laboratory Sampling Data | [Quarterly/annual datasets](https://www.fsis.usda.gov/science-data/data-sets-visualizations/laboratory-sampling-data) |
| Chemical Residues | [National Residue Program](https://www.fsis.usda.gov/science-data/data-sets-visualizations/chemical-residues-and-contaminants) |
| Microbiology | [Baseline reports](https://www.fsis.usda.gov/science-data/data-sets-visualizations/microbiology) |
| Inspection Task Data | [Inspection datasets](https://www.fsis.usda.gov/science-data/data-sets-visualizations/inspection-task-data) |
| Humane Handling Data | [Enforcement data](https://www.fsis.usda.gov/science-data/data-sets-visualizations/humane-handling-data) |

---

> **Navigation:** [User Guide](user-guide.md) | [Deployment Guide](deployment-guide.md) | [Developer Guide](developer-guide.md) | [Operations Guide](operations-guide.md) | [Best Practices](best-practices.md) | [Troubleshooting](troubleshooting.md) | [Runbooks](../runbooks/)
