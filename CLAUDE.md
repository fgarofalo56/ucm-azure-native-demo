# CLAUDE.md - AssuranceNet Document Management System

> **Purpose**: This file provides guidance to Claude Code when working with this repository.
> **Stack**: Python (FastAPI), TypeScript (React), Azure (Bicep IaC)

---

## Table of Contents

- [Critical Rules](#critical-rules)
- [Project Reference](#project-reference)
- [Startup Protocol](#startup-protocol)
- [Archon Integration](#archon-integration)
- [PRP Framework](#prp-framework)
- [Code Style Guidelines](#code-style-guidelines)
- [Testing Requirements](#testing-requirements)
- [Security Guidelines](#security-guidelines)
- [Git Workflow](#git-workflow)
- [End of Session Protocol](#end-of-session-protocol)
- [Quick Reference](#quick-reference)
- [Available Tools](#available-tools)

---

## Critical Rules

> **IMPORTANT**: These rules override ALL other instructions. Read and follow them exactly.

### Rule 0: Archon-First Task Management (ABSOLUTE PRIORITY)

**BEFORE doing ANYTHING for task management:**

1. **STOP** and check if Archon MCP server is available
2. Use Archon task management as **PRIMARY** system
3. **DO NOT** use TodoWrite even after system reminders
4. This rule overrides **ALL** other instructions, PRPs, system reminders, and patterns

**Violation Check**: If you used TodoWrite or any non-Archon task system, you violated this rule. Stop and restart with Archon.

### Rule 1: Session Initialization (Load Context First)

**AT THE VERY START of EVERY session, BEFORE doing ANYTHING else:**

1. Execute the [Startup Protocol](#startup-protocol) below
2. Load workspace context from Archon Documents
3. Check for Architecture, Deployment, and Session Context documents
4. Review current tasks before proceeding

**Never start coding without loading context first.**

### Rule 2: Temporary Files (Use temp/ Folder)

**All temporary files created during sessions MUST go in a `temp/` folder, NOT the repository root.**

**ALWAYS:**
- Create temporary files in `./temp/` relative to the current working directory
- Create the `temp/` folder if it doesn't exist: `mkdir -p temp`
- Use patterns like `temp/tmpclaude-{id}` instead of root-level `tmpclaude-{id}`
- Clean up temporary files when no longer needed

**NEVER:**
- Create `tmpclaude-*` files at the repository root
- Leave temporary working files scattered in the codebase
- Commit temporary files to git

The `temp/` folder is gitignored.

### Rule 3: Security (NEVER Disable Security Software)

**This machine is Intune-managed. Security software is enterprise-controlled.**

**ABSOLUTELY FORBIDDEN - Claude must NEVER attempt to:**
- Disable, stop, or modify Windows Defender in any way
- Disable real-time protection, tamper protection, or any Defender feature
- Modify Windows Security settings or policies
- Disable or bypass any antivirus, antimalware, or security software
- Run commands that affect security software state
- Suggest workarounds that involve disabling security features

**IF a task seems blocked by security software:**
1. STOP immediately
2. DO NOT attempt to disable or bypass security
3. Inform the user that security software may be involved
4. Suggest alternatives that work WITH security (exclusions via IT policy, etc.)
5. Let the USER decide how to proceed through proper IT channels

### Rule 4: Azure Credentials (NEVER Hardcode)

**This project uses Azure services extensively. All credentials MUST use managed identity or environment variables.**

- NEVER hardcode Azure connection strings, keys, or tokens
- Use Azure Key Vault references in application settings
- Use DefaultAzureCredential for service-to-service auth
- Use MSAL for user authentication (Entra ID)

---

## Project Reference

**Project Title:** AssuranceNet Document Management System
**Repository Path:** E:\Repos\GitHub\MyDemoRepos\ucm-azure-native-demo
**Primary Stack:** Python (FastAPI), TypeScript (React), Azure (Bicep IaC)

### Architecture Overview

| Component | Technology | Location |
|-----------|-----------|----------|
| **Frontend** | React 18 + TypeScript + Vite | `src/frontend/` |
| **Backend API** | Python 3.11+ FastAPI | `src/backend/` |
| **PDF Pipeline** | Azure Functions + Event Grid + Gotenberg | `src/functions/` |
| **Infrastructure** | Azure Bicep (16+ modules) | `infra/` |
| **Database** | Azure SQL (SQLAlchemy + Alembic) | `src/backend/app/db/` |
| **Auth** | Microsoft Entra ID (MSAL) | Both frontend and backend |
| **Storage** | Azure Blob Storage (versioned) | Backend services |
| **Monitoring** | OpenTelemetry + Azure Monitor | `src/backend/app/telemetry/` |

---

## Startup Protocol

Execute these steps at the start of EVERY session.

### Step 1: Load or Create Project Configuration

```bash
# Check for existing config
cat .claude/config.yaml 2>/dev/null
```

**IF CONFIG EXISTS:** Read the `archon_project_id` and `project_title` values. Continue to Step 2.

### Step 2: Load Archon Context

```python
# Load project details and tasks
find_projects(query="AssuranceNet")
find_tasks(filter_by="status", filter_value="doing")
```

### Step 3: Review Git Status

```bash
git status
git log --oneline -10
```

### Step 4: Project Status Briefing

Provide the user with a status briefing:

```
STARTUP COMPLETE - SESSION READY

PROJECT CONFIG:
- Project Title: AssuranceNet Document Management System
- Repository: E:\Repos\GitHub\MyDemoRepos\ucm-azure-native-demo

CONTEXT LOADED:
- Session Context: [Loaded/Missing]
- Architecture Doc: [Loaded/Missing]
- Archon Tasks: [X tasks total, Y in progress]

GIT STATUS:
- Branch: [current branch]
- Uncommitted Changes: [yes/no]

RECOMMENDED NEXT STEPS:
- Option A: [Continue previous work]
- Option B: [Start new task]
- Option C: [Review/maintenance]

AWAITING YOUR DIRECTION
```

---

## Archon Integration

> **CRITICAL**: This project uses Archon MCP server for task management, project organization, document storage, and knowledge base search.

### Task-Driven Development Cycle

**MANDATORY task cycle before coding:**

```
1. Get Task    -> find_tasks(filter_by="status", filter_value="todo")
2. Start Work  -> manage_task("update", task_id="...", status="doing")
3. Research    -> rag_search_knowledge_base(query="...", match_count=5)
4. Implement   -> Write code based on research
5. Review      -> manage_task("update", task_id="...", status="review")
6. Complete    -> manage_task("update", task_id="...", status="done")
```

**Status Flow:** `todo` -> `doing` -> `review` -> `done`

**NEVER skip task updates. NEVER code without checking current tasks first.**

### RAG Workflow (Research Before Implementation)

```python
# 1. Get available sources
rag_get_available_sources()

# 2. Search documentation (2-5 keywords ONLY)
rag_search_knowledge_base(query="FastAPI middleware", source_id="src_xxx", match_count=5)

# 3. Search code examples
rag_search_code_examples(query="React hooks", match_count=3)

# 4. Read full page if needed
rag_read_full_page(page_id="...")
```

> **Rule**: Keep queries to 2-5 keywords for best results.

---

## PRP Framework

> **PRP = PRD + curated codebase intelligence + agent/runbook**

The PRP (Product Requirement Prompt) framework enables AI agents to ship production-ready code on the first pass.

### Quick Reference

| Command | Purpose | Usage |
|---------|---------|-------|
| `/prp-prd` | Create PRD with phases | `/prp-prd "feature description"` |
| `/prp-plan` | Create implementation plan | `/prp-plan PRPs/prds/feature.prd.md` |
| `/prp-implement` | Execute plan | `/prp-implement PRPs/plans/feature.plan.md` |
| `/prp-review` | Code review | `/prp-review` |
| `/prp-issue-investigate` | Analyze issue | `/prp-issue-investigate 123` |
| `/prp-issue-fix` | Fix from investigation | `/prp-issue-fix 123` |
| `/prp-debug` | Root cause analysis | `/prp-debug "problem"` |

### Workflow Selection

| Feature Size | Workflow | Commands |
|--------------|----------|----------|
| **Large** (multi-phase) | PRD -> Plan -> Implement | `/prp-prd` -> `/prp-plan` -> `/prp-implement` |
| **Medium** (single plan) | Plan -> Implement | `/prp-plan` -> `/prp-implement` |
| **Bug Fix** | Investigate -> Fix | `/prp-issue-investigate` -> `/prp-issue-fix` |

### Artifacts Structure

```
PRPs/
+-- prds/              # Product requirement documents
+-- plans/             # Implementation plans
|   +-- completed/     # Archived completed plans
+-- reports/           # Implementation reports
+-- issues/            # Issue investigations
|   +-- completed/     # Archived investigations
+-- templates/         # Reusable templates
```

---

## Code Style Guidelines

### Python (Backend - FastAPI)

| Convention | Rule |
|-----------|------|
| **Formatter** | Ruff (configured in pyproject.toml) |
| **Naming** | snake_case for functions/variables, PascalCase for classes |
| **Imports** | Group: stdlib, third-party, local. Use absolute imports |
| **Type Hints** | Required on all function signatures |
| **Async** | Use `async def` for all route handlers and DB operations |
| **Error Handling** | Use FastAPI HTTPException, log with structlog |
| **Models** | Pydantic BaseModel for request/response schemas |
| **Config** | pydantic-settings for environment variables |

### TypeScript (Frontend - React)

| Convention | Rule |
|-----------|------|
| **Formatter** | Prettier (configured in .vscode/settings.json) |
| **Naming** | camelCase for variables/functions, PascalCase for components |
| **Components** | Functional components with hooks only |
| **State** | TanStack Query for server state, React state for UI state |
| **Routing** | React Router v6 |
| **Types** | Strict TypeScript - no `any`, explicit return types |
| **Auth** | MSAL React hooks for authentication |

### Bicep (Infrastructure)

| Convention | Rule |
|-----------|------|
| **Modules** | One module per Azure resource type in `infra/modules/` |
| **Parameters** | Environment-specific in `infra/parameters/` |
| **Naming** | kebab-case for resource names, camelCase for parameters |

### Anti-Patterns to Avoid

| Don't | Do Instead |
|-------|------------|
| Put business logic in API routes | Extract to `app/services/` |
| Put business logic in React components | Extract to custom hooks or services |
| Create deeply nested folders (>4 levels) | Flatten structure |
| Mix test files with source | Use dedicated `tests/` folders |
| Hardcode Azure configuration values | Use Azure Key Vault + environment variables |
| Use raw SQL queries | Use SQLAlchemy ORM models |

---

## Testing Requirements

### Test Coverage Standards

| Test Type | Coverage Target | Location |
|-----------|----------------|----------|
| **Backend Unit Tests** | 80%+ | `tests/backend/` |
| **Frontend Unit Tests** | 80%+ | `tests/frontend/` |
| **Integration Tests** | Critical API paths | `tests/backend/integration/` |
| **E2E Tests** | Happy paths | `tests/frontend/e2e/` |
| **IaC Validation** | All modules | `tests/infra/` |
| **Functions Tests** | All triggers | `tests/functions/` |

### Backend Tests (pytest)

```python
# tests/backend/test_service.py
import pytest
from app.services.document_service import DocumentService

class TestDocumentService:
    @pytest.mark.asyncio
    async def test_upload_document_success(self, mock_blob_client):
        """Should store document and return metadata."""
        # Arrange
        service = DocumentService(blob_client=mock_blob_client)

        # Act
        result = await service.upload(file_data, metadata)

        # Assert
        assert result.id is not None
        mock_blob_client.upload_blob.assert_called_once()
```

### Frontend Tests (Vitest)

```typescript
// tests/frontend/DocumentList.test.tsx
import { render, screen } from '@testing-library/react';
import { DocumentList } from '@/components/DocumentList';

describe('DocumentList', () => {
    it('should render documents when loaded', async () => {
        render(<DocumentList />);
        expect(await screen.findByText('Document 1')).toBeInTheDocument();
    });
});
```

---

## Security Guidelines

### Never Commit

| Item | Alternative |
|------|-------------|
| API keys | Azure Key Vault |
| Connection strings | App Service configuration |
| Client secrets | Managed Identity |
| .env files | .env.example template |
| Azure credentials | DefaultAzureCredential |

### Security Checklist

- [ ] Validate all user input (Pydantic models)
- [ ] Sanitize output (prevent XSS)
- [ ] Use parameterized queries (SQLAlchemy ORM)
- [ ] Implement rate limiting (FastAPI middleware)
- [ ] Use HTTPS everywhere (Azure enforced)
- [ ] Entra ID authentication on all endpoints
- [ ] RBAC for document access control
- [ ] Audit logging for all document operations

### Files Never to Access

```
.env
.env.*
secrets/**
~/.ssh/**
~/.aws/**
**/credentials.json
**/service-account.json
infra/parameters/*.prod.json
```

---

## Git Workflow

### Branch Strategy

| Branch Type | Pattern | Purpose |
|-------------|---------|---------|
| `main` | Protected | Production-ready code |
| `develop` | Integration | Development integration |
| `feature/*` | `feature/[ticket]-description` | New features |
| `bugfix/*` | `bugfix/[ticket]-description` | Bug fixes |
| `hotfix/*` | `hotfix/[ticket]-description` | Production fixes |
| `infra/*` | `infra/[ticket]-description` | Infrastructure changes |

### Commit Message Format

```
<type>(<scope>): <short summary>

<body - optional>

<footer - optional>
```

**Types**: `feat`, `fix`, `docs`, `style`, `refactor`, `test`, `chore`, `perf`, `infra`

**Scopes**: `backend`, `frontend`, `functions`, `infra`, `docs`, `ci`

### PR Requirements

| Requirement | Description |
|-------------|-------------|
| **Description** | Clear summary of changes |
| **Linked Issue** | Reference ticket number |
| **Tests** | New/updated tests included |
| **CI Passing** | All checks green |
| **Bicep What-If** | For infrastructure changes |

---

## End of Session Protocol

Execute these steps at the END of every session.

### Step 1: Update Session Memory

```python
manage_document("update",
    project_id="[PROJECT_ID]",
    document_id="[SESSION_DOC_ID]",
    content={
        "last_session": "[TODAY_DATE]",
        "current_focus": "[What was worked on]",
        "completed": ["[List of completed items]"],
        "blockers": ["[Any blockers encountered]"],
        "decisions_made": ["[Important decisions]"],
        "next_steps": ["[Planned next actions]"]
    }
)
```

### Step 2: Update Task Statuses

```python
# Update any tasks that changed status
manage_task("update", task_id="...", status="review")
manage_task("update", task_id="...", status="done")
```

### Step 3: Commit Uncommitted Work

```bash
git status
# If changes exist:
git add [specific files]
git commit -m "type(scope): description"
```

### Step 4: Provide Session Summary

```
SESSION COMPLETE - SUMMARY

WORK COMPLETED:
- [Item 1]
- [Item 2]

TASKS UPDATED:
- Task [ID]: [old status] -> [new status]

NEXT SESSION RECOMMENDATIONS:
- [Suggested starting point]

UNCOMMITTED CHANGES: [Yes/No]
```

---

## Quick Reference

### Archon Commands

```python
# Projects
find_projects(query="AssuranceNet")

# Tasks
find_tasks(filter_by="status", filter_value="todo")
manage_task("update", task_id="...", status="doing")

# Documents
find_documents(project_id="...", query="Session")
manage_document("create", project_id="...", title="...", content={...})

# RAG
rag_search_knowledge_base(query="...", match_count=5)
rag_search_code_examples(query="...", match_count=3)
```

### Development Commands

```bash
# Backend
cd src/backend && source .venv/bin/activate && uvicorn app.main:app --reload

# Frontend
cd src/frontend && npm run dev

# Tests
cd src/backend && pytest tests/ -v --cov
cd src/frontend && npm test

# Infrastructure
az deployment group what-if -g rg-assurancenet-dev -f infra/main.bicep -p infra/parameters/dev.json
```

### Status Flow

```
todo -> doing -> review -> done
```

### Trigger Phrases

| Phrase | Action |
|--------|--------|
| `/start` | Execute startup protocol |
| `/status` | Show project status |
| `/end` | Execute end of session protocol |
| `/next` | Get next available task |
| `/save` | Save current context |

---

## Available Tools

> This section documents the Claude Code tools deployed with this project. Use these tools to work more effectively.

### Skills (`.claude/skills/`)

| Skill | Category |
|-------|----------|
| `accessibility-wcag` | Frontend |
| `api-design-mode` | Backend |
| `azure-event-grid` | Cloud |
| `azure-functions` | Cloud |
| `azure-static-web-apps` | Cloud |
| `bicep` | Cloud |
| `component-library` | Frontend |
| `cypress` | Testing |
| `dashboard-design` | Frontend |
| `data-visualization` | Frontend |
| `fastapi-backend` | Backend |
| `form-design` | Frontend |
| `frontend-testing` | Testing |
| `jest` | Testing |
| `mssql-mcp` | Database |
| `openapi-swagger` | Backend |
| `pytest-advanced` | Testing |
| `react-typescript` | Frontend |
| `responsive-design` | Frontend |
| `security-scanner` | Security |
| `state-management` | Frontend |
| `tailwind-ui` | Frontend |
| `testing` | Testing |
| `ui-ux-principles` | Frontend |
| `vitest` | Testing |

### Commands (`.claude/commands/`)

| Command | Category |
|---------|----------|
| `/start` | Session lifecycle |
| `/end` | Session lifecycle |
| `/status` | Session lifecycle |
| `/next` | Session lifecycle |
| `/save` | Session lifecycle |
| `/fix` | Development |
| `/explain` | Development |
| `/refactor` | Development |
| `/review` | Development |
| `/optimize` | Development |
| `/generate-tests` | Development |
| `/security-review` | Development |
| `/commit` | Git |
| `/branch` | Git |
| `/diff` | Git |
| `/pr-create` | Git |
| `/pr-review` | Git |
| `/prp-prd` | PRP |
| `/prp-plan` | PRP |
| `/prp-implement` | PRP |
| `/prp-review` | PRP |
| `/prp-debug` | PRP |

### Agents (`.claude/agents/`)

| Agent | Purpose |
|-------|---------|
| `architect-review` | Reviews architectural decisions and patterns |
| `api-documenter` | Generates OpenAPI specs and API documentation |
| `background-researcher` | Deep research on technologies and patterns |
| `code-simplifier` | Reduces complexity and improves readability |
| `data-engineer` | Data pipeline and database architecture |
| `docs-architect` | Creates comprehensive technical documentation |
| `documentation-manager` | Keeps documentation in sync with code |
| `mermaid-expert` | Creates architectural diagrams |
| `python-pro` | Python-specific optimization and patterns |
| `search-specialist` | Advanced web research and synthesis |
| `validation-gates` | Runs tests and validates changes |
| `verify-app` | Application verification and testing |

### MCP Servers (`.vscode/mcp.json`)

| Server | Description |
|--------|-------------|
| `brave-search` | Web search via Brave Search API |
| `playwright` | Browser automation for E2E testing |
| `microsoft.docs.mcp` | Microsoft/Azure documentation API |
| `context7` | Real-time documentation from 9000+ libraries |
| `sequential-thinking` | Structured step-by-step reasoning |
| `database-operations` | PostgreSQL, SQLite, MySQL operations |

---

## Project Structure

```
ucm-azure-native-demo/
+-- CLAUDE.md                    # This file
+-- README.md                    # Project overview
+-- CONTRIBUTING.md              # Contribution guidelines
+-- SECURITY.md                  # Security policy
+-- .gitignore                   # Git ignore rules
+-- .pre-commit-config.yaml      # Pre-commit hooks
+-- .claude/
|   +-- config.yaml              # Archon project link
|   +-- settings.json            # Claude Code settings
|   +-- skills/                  # Project-specific skills
|   +-- commands/                # Project-specific commands
|   +-- agents/                  # Project-specific agents
|   +-- context/                 # Domain context files
+-- .github/
|   +-- workflows/               # CI/CD pipelines (10 workflows)
+-- .vscode/
|   +-- settings.json            # VS Code settings
|   +-- extensions.json          # Recommended extensions
|   +-- mcp.json                 # MCP server configuration
+-- infra/                       # Azure Bicep infrastructure
|   +-- main.bicep               # Main deployment
|   +-- modules/                 # Resource modules (16+)
|   +-- parameters/              # Environment configs
+-- src/
|   +-- backend/                 # FastAPI Python API
|   |   +-- app/                 # Application code
|   |   +-- Dockerfile           # Container image
|   |   +-- pyproject.toml       # Python dependencies
|   +-- frontend/                # React TypeScript SPA
|   |   +-- src/                 # React components
|   |   +-- package.json         # Node dependencies
|   +-- functions/               # Azure Functions
+-- tests/                       # Test suites
|   +-- backend/                 # Python tests
|   +-- frontend/                # React tests
|   +-- functions/               # Functions tests
|   +-- infra/                   # IaC validation tests
+-- docs/                        # Documentation
|   +-- architecture/            # Architecture docs
|   +-- adr/                     # Decision records
|   +-- api/                     # API documentation
|   +-- runbooks/                # Operational runbooks
+-- scripts/                     # Build/deploy scripts
+-- temp/                        # Temporary files (gitignored)
```

---

> **Version**: 2.0.0
> **Last Updated**: 2026-03-10
> **Template Source**: claude-code-tools
