# CLAUDE.md - AssuranceNet Document Management System

> **Note:** This project previously used Archon v1 for task tracking. Archon v1 was archived by its author in April 2026. Historical Archon task records were exported to `.claude/migrated-archon-tasks.md` at migration time. Use TodoWrite + GitHub Issues going forward (see Rule 0).

> **Purpose**: This file provides guidance to Claude Code when working with this repository.
> **Stack**: Python (FastAPI), TypeScript (React), Azure (Bicep IaC)

---

## Critical Rules (Override Everything)

### Rule 0: Task Tracking — Native-First

For tracking work in the current session and across sessions, use **native Claude Code tools**:

| Scope | Tool | When |
|-------|------|------|
| Within-turn / within-session checklist | `TodoWrite` | Multi-step task you'll finish soon |
| Cross-session work | **GitHub Issues** (`gh issue`) | Work that spans days or needs visibility |
| Long-form planning | `PRPs/plans/<name>.plan.md` (if PRP framework selected) | Multi-PR initiatives with phases |
| Recurring backlog item | GitHub Issue with a label | Anything you'll reference more than twice |

`TodoWrite` is the right default. Use it freely. Cross-session durability comes from the **filesystem** (`.claude/reference/`, plan files, this CLAUDE.md) and **GitHub** (Issues, PRs, commit messages) — not from a separate task database.

### Rule 1: Load Context First

At the start of EVERY session, before any code work:

1. Run the [Startup Protocol](#startup-protocol).
2. Read this `CLAUDE.md` and any relevant `.claude/reference/*.md`.
3. Check `git status` and `git log -10` for in-flight work.
4. Check open GitHub Issues / PRs if relevant: `gh pr list` / `gh issue list`.
5. Check `MEMORY.md` if there's per-project auto-memory at `~/.claude/projects/<slug>/memory/`.

Never start coding without orienting first.

### Rule 2: Preserve Context in the Filesystem

Project knowledge that survives context resets lives in **files**, not in your conversation:

| Document | Where | When to update |
|----------|-------|----------------|
| Architecture decisions | `.claude/reference/architecture.md` | After any architectural decision |
| Deployment runbook | `.claude/reference/deployment.md` | After deployment changes |
| Session handoff | `.claude/reference/session-context.md` | End of each significant session, before `/compact` or `/clear` |
| API surface | `.claude/reference/api.md` (or generated OpenAPI) | After API surface changes |
| Non-obvious facts / gotchas | `MEMORY.md` (auto-memory) | When you hit something a future session needs |

If the context window approaches 70%, update `session-context.md` BEFORE compacting. Load specific reference docs on demand with `@.claude/reference/<file>.md` syntax — don't preload everything.

### Rule 3: Skills Discovery

Before implementing anything non-trivial, check available skills (`.claude/skills/` and `~/.claude/skills/`). Skills are tested, opinionated workflows - prefer them over ad-hoc solutions.

### Rule 4: Temporary Files Go in `temp/`

All temp files MUST be created under `./temp/` (gitignored), never the repo root. Create the directory if it doesn't exist. Never commit temp files.

### Rule 5: Never Tamper with Security Software

This machine may be Intune-managed. Claude must NEVER attempt to disable, stop, or modify Windows Defender, antivirus, or any security software. If a task seems blocked by security, STOP and ask the user - do not work around it.

### Rule 6: Never Read Secrets

Forbidden paths: `.env`, `.env.*`, `secrets/**`, `~/.ssh/**`, `~/.aws/**`, `**/credentials.json`, `**/service-account.json`. Use `.env.example` as a template only.

### Rule 7: Automatic Behaviors Live in Hooks, Not Memory

If you want Claude to "always do X when Y happens" (e.g., run a linter after every edit, post to Slack on session end, validate env vars before deploy), that **must** be a hook in `.claude/settings.json` — not a memory entry or a CLAUDE.md instruction.

| Mechanism | Fires when | Best for |
|-----------|-----------|----------|
| **Hooks** (`settings.json`) | Deterministic events: PreToolUse, PostToolUse, UserPromptSubmit, Stop, etc. | "Always run X after Y" |
| **Memory** (`MEMORY.md`) | Recalled by Claude when relevant context appears | Facts, preferences, prior decisions |
| **CLAUDE.md** | Loaded into every session | Project-wide policies and conventions |
| **Skills** | Auto-invoked when description matches user intent | Reusable workflows |

If your rule says "from now on, when X, do Y" — write a hook. Memory cannot enforce; it only informs.

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
| **PDF Pipeline** | In-process (Pillow+fpdf2) + Aspose/Gotenberg (admin-configurable) | `src/backend/app/services/` |
| **Infrastructure** | Azure Bicep (18+ modules) | `infra/` |
| **Database** | Azure SQL (Document + DocumentVersion + SystemSettings + RBAC, via SQLAlchemy + Alembic) | `src/backend/app/db/` |
| **Auth** | Microsoft Entra ID (MSAL) | Both frontend and backend |
| **Storage** | Azure Blob Storage (versioned) | Backend services |
| **Monitoring** | OpenTelemetry + Azure Monitor | `src/backend/app/telemetry/` |

---

## Startup Protocol

Run at the start of EVERY session:

1. **Read this file** + any reference docs the task touches (`@.claude/reference/<topic>.md`).

2. **Check git state**:

   ```bash
   git status
   git log --oneline -10
   ```

3. **Check in-flight GitHub work** (if relevant):

   ```bash
   gh pr list --state open
   gh issue list --state open --assignee @me
   ```

4. **Check `.claude/reference/session-context.md`** if it exists — picks up where the prior session left off.

5. **Brief the user** with: what was being worked on, uncommitted changes, recommended next step.

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

## Project Type: Backend API

| Concern | Guidance |
|---------|----------|
| **Validate at boundaries** | Pydantic / DTO / Zod at request ingress. Trust internal code; don't re-validate between layers. |
| **Error responses** | Generic message to client + `logger.exception(...)` server-side. Never `return {"error": str(exc)}` — leaks stack traces (CodeQL `py/stack-trace-exposure`). |
| **Database access** | Parameterized queries only. Connection pooling at the app boundary, not per-request. |
| **Auth** | At middleware level, not per-route. Never trust client-provided user IDs. |
| **Integration tests** | Hit a real database (testcontainers or ephemeral instance). Mocking the DB hides migration breakage. |
| **API versioning** | URL-versioned (`/v1/`) or header-versioned. Never silently break clients. |

Long-running operations: return a job ID + status endpoint, not a hung connection.
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

## Code Style

| Principle | Apply to |
|-----------|----------|
| Single responsibility | Functions, classes, modules |
| Readable over clever | Default |
| DRY | Extract after the third repetition, not the second |
| Testable | Pure functions where possible |
| Minimal dependencies | Add only when truly needed |

[PRIMARY_LANGUAGE]-specific conventions: customize this section.

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

## Testing

| Type | Target | Location |
|------|--------|----------|
| Unit | 80%+ on changed code | `tests/unit/` |
| Integration | Critical paths | `tests/integration/` |
| E2E | Happy paths + critical flows | `tests/e2e/` |

AAA pattern: Arrange / Act / Assert. Run tests before marking a task `review`.

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

## Security

Never commit: API keys, passwords, private keys, connection strings, `.env` files.
Use environment variables. The `.env.example` in this repo lists required variables.

Validate user input. Parameterize queries. Sanitize output. Keep deps updated.

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

1. Update `.claude/reference/session-context.md` with: what was completed, decisions made, next steps, blockers.
2. Update or close any open `TodoWrite` items (mark completed as you go, don't batch).
3. Commit uncommitted work with a descriptive message.
4. If the work warrants a follow-up GitHub Issue (something you'll want to find later), open it now: `gh issue create`.
5. Brief the user with a session summary.

Always update `session-context.md` BEFORE `/clear` or `/compact` near 70%.

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

## Claude Code Capabilities Quick Reference

Pointers to features that meaningfully change how a task gets done. Use these when the situation matches — don't reach for them by default.

### Sub-agents and isolation

| When | Tool | Notes |
|------|------|-------|
| Need independent research that would bloat main context | `Agent` with `subagent_type: Explore` or `general-purpose` | Returns a single message; main thread stays clean |
| Need 2+ independent investigations | Multiple `Agent` calls in **one** message | Run in parallel |
| Risky refactor that might fail | `Agent` with `isolation: worktree` | Auto-cleanup if no changes made |
| Specialized work matches an agent | `Agent` with the right `subagent_type` | See agent registry in `.claude/agents/` |

### Background tasks

| When | How |
|------|-----|
| Command runs >5 min (CI watch, large build) | `Bash` with `run_in_background: true` |
| Want notification on completion | The harness notifies automatically — **don't poll** |
| Long agent run that doesn't block your next steps | `Agent` with `run_in_background: true` |

### Context management

| Action | Command / Syntax |
|--------|------------------|
| Check token usage | `/cost` |
| Compress conversation (preserves intent) | `/compact` — update Session Context first if near 70% |
| Hard reset | `/clear` — save context to disk first |
| Load a reference doc on demand | `@.claude/reference/<file>.md` in user prompt |
| Switch model mid-session | `/model opus` / `/model sonnet` / `/model haiku` |
| Faster Opus output | `/fast` (Opus 4.6 / 4.7 only — no quality drop) |

### Permission & settings

| Need | Where |
|------|-------|
| Allow specific commands without prompts | `permissions.allow` in `.claude/settings.json` |
| Per-tool restrictions for a skill/agent | `allowed-tools:` frontmatter |
| Auto-accept edits in current session | `/permissions` → accept edits mode |
| Plan-only mode (read, don't write) | `/permissions` → plan mode |

### Model selection heuristic

| Task type | Default model |
|-----------|---------------|
| Heavy reasoning, architecture, audits | Opus (Opus 4.7 has 1M context) |
| Day-to-day coding, refactors | Sonnet |
| Quick lookups, simple edits, batch ops | Haiku |

### Skill & command frontmatter (modern fields)

```yaml
---
name: my-skill
description: When to use it (matters for auto-invocation)
effort: high              # low|medium|high|max — reasoning depth
context: fork             # Run in isolated subagent
allowed-tools: Read, Grep # Restrict tool access
argument-hint: "[file]"   # Shown in autocomplete
hooks:                    # Skill-scoped hooks
  PostToolUse:
    - matcher: "Edit"
      hooks: [{type: command, command: "./format.sh"}]
---
```

### Memory system

Per-project auto-memory lives in `~/.claude/projects/<project-slug>/memory/`. Index is `MEMORY.md`. Save user/feedback/project/reference notes there — never duplicate facts already in code or git history.

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

---

## Quick Reference

| Phrase | Action |
|--------|--------|
| `/start` | Run startup protocol |
| `/status` | Project status (git + open issues + recent commits) |
| `/end` | End-of-session protocol (update session-context, commit, summarize) |
| `@.claude/reference/<file>.md` | Load a specific reference doc into context on demand |

---

> **Template Version**: 4.0.0 | **Generated**: [CREATION_DATE]
> **Source**: claude-code-tools project wizard

## Task & Knowledge Workflow

Mandatory before coding:

```
1. Plan            -> TodoWrite (breaks the work into trackable steps)
2. Research        -> Use the project-kb skill (Context7 for libs, filesystem for project docs)
3. Implement
4. Test            -> Run the project's test command before claiming done
5. Mark complete   -> Update TodoWrite as you finish each step
6. Commit          -> Conventional commit format (see Git Workflow below)
```

For multi-day work: open a GitHub Issue with a clear acceptance bar, link PRs that move it forward, close it when shipped.

Research discipline: 2-5 keyword queries beat one long question. Run multiple focused queries rather than one broad one. See the `project-kb` skill for the full lookup flow.

---

## Optional: Archon RAG

> **Skip this section unless you have a substantial private/internal corpus** that genuinely needs vector search. For library docs (FastAPI, React, Pydantic, etc.), use the `project-kb` skill — it wraps Context7 MCP, which already indexes 1000+ libraries with fresher content than any local corpus.

For projects with extracted internal documentation:

1. Drop markdown files in `.claude/kb/` (gitignored if confidential, committed if public).
2. The `project-kb` skill will grep them automatically.
3. No vector store, no MCP server, no background indexing — just filesystem search with `Grep`.

If you genuinely need vector retrieval (semantic similarity, fuzzy concept matching across a large private corpus), evaluate options like LanceDB-on-disk or a self-hosted Qdrant — but that's a deliberate, scoped infrastructure decision, not a default.

---

