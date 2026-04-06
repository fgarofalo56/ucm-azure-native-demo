# Session Knowledge - AssuranceNet Document Management System

## Project Context

- **Project**: Azure-native document management replacing Oracle UCM for FSIS AssuranceNet
- **Status**: Early development - infrastructure and architecture defined, core backend/frontend scaffolded
- **Tech Stack**: Python FastAPI + React TypeScript + Azure Bicep IaC

## Key Architecture Decisions

- Event-driven PDF conversion pipeline (Event Grid + Functions + Gotenberg)
- Azure Blob Storage with versioning for document storage
- Azure SQL for metadata and audit trails
- Microsoft Entra ID (MSAL) for authentication
- OpenTelemetry for distributed tracing

## Current Focus Areas

- Backend API development (FastAPI)
- Frontend SPA scaffolding (React + Vite)
- Infrastructure-as-code (Bicep modules)
- CI/CD pipeline configuration

## Important Paths

- Backend: src/backend/app/
- Frontend: src/frontend/src/
- Infrastructure: infra/modules/
- Tests: tests/
- Documentation: docs/

## Last Updated

2026-03-10 - Initial onboarding
