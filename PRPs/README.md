# PRP Framework for Claude Code

> **PRP = PRD + curated codebase intelligence + agent/runbook**

The minimum viable packet an AI needs to ship production-ready code on the first pass.

## What is PRP?

**Product Requirement Prompt (PRP)** is a methodology designed to enable AI agents to ship production-ready code on the first pass. It differs from traditional PRDs by adding AI-critical layers:

- **Context**: Precise file paths, library versions, code snippet examples
- **Patterns**: Existing codebase conventions to follow
- **Validation**: Executable commands the AI can run to verify its work
- **Integration**: Archon task management for tracking and persistence

## Quick Start

### For Large Features (PRD -> Plan -> Implement)

```
1. /prp-prd "user authentication system"
   -> Creates PRD with Implementation Phases

2. /prp-plan PRPs/prds/user-auth.prd.md
   -> Creates implementation plan for next phase

3. /prp-implement PRPs/plans/user-auth-phase-1.plan.md
   -> Executes plan with validation loops

4. Repeat /prp-plan for remaining phases
```

### For Medium Features (Direct to Plan)

```
1. /prp-plan "add pagination to the API"
   -> Creates implementation plan directly

2. /prp-implement PRPs/plans/add-pagination.plan.md
   -> Executes the plan
```

### For Bug Fixes (Issue Workflow)

```
1. /prp-issue-investigate 123
   -> Analyzes issue, finds root cause

2. /prp-issue-fix 123
   -> Implements fix from investigation
```

## Available Commands

| Command | Description | Input |
|---------|-------------|-------|
| `/prp-prd` | Interactive PRD generator | Feature description |
| `/prp-plan` | Create implementation plan | PRD path or description |
| `/prp-implement` | Execute plan with validation | Plan file path |
| `/prp-review` | Comprehensive code review | Diff scope |
| `/prp-issue-investigate` | Analyze GitHub issue | Issue number |
| `/prp-issue-fix` | Execute fix from investigation | Issue number |
| `/prp-debug` | Deep root cause analysis | Problem description |
| `/prp-report` | Generate implementation report | Plan file path |

## Directory Structure

```
PRPs/
├── README.md              # This file
├── prds/                  # Product Requirement Documents
│   └── .gitkeep
├── plans/                 # Implementation Plans
│   ├── .gitkeep
│   └── completed/         # Archived completed plans
│       └── .gitkeep
├── issues/                # Issue Investigations
│   ├── .gitkeep
│   └── completed/         # Archived investigations
│       └── .gitkeep
├── reports/               # Implementation Reports
│   └── .gitkeep
└── templates/             # Reusable Templates
    ├── prd-template.md                    # PRD template
    ├── plan-template.md                   # Implementation plan template
    ├── issue-investigation-template.md    # Issue investigation template
    └── implementation-report-template.md  # Post-implementation report template
```

## Workflow Selection Guide

### When to Use Each Workflow

| Scenario | Workflow | Artifacts |
|----------|----------|-----------|
| New feature (1+ week effort) | PRD -> Plan -> Implement | PRD, Plan(s), Report |
| Enhancement (2-5 days) | Plan -> Implement | Plan, Report |
| Bug fix | Issue Investigation -> Fix | Investigation, Report |
| Urgent hotfix | Direct fix with validation | Report only |
| Refactoring | Plan -> Implement | Plan, Report |

### Effort Estimation Guide

| Complexity | Estimated Effort | Recommended Workflow |
|------------|------------------|----------------------|
| Low | < 1 day | Direct implementation |
| Medium | 1-5 days | Plan -> Implement |
| High | 1-2 weeks | PRD -> Plan -> Implement |
| Very High | 2+ weeks | PRD with multiple phases |

## Core Principles

### 1. Context is King

Every PRP must include comprehensive context:
- Documentation URLs with specific sections
- Code examples from the actual codebase
- Known gotchas and pitfalls
- File:line references for every pattern

### 2. Validation Loops

Every task must have executable validation:
- Build commands
- Lint commands
- Test commands
- Integration verification

### 3. Information Dense

Use specific references from the codebase:
- Actual function names
- Real type definitions
- Existing error patterns
- Current naming conventions

### 4. Bounded Scope

Each plan should be completable in one session:
- Clear start and end points
- Explicit out-of-scope items
- Dependencies listed and checked

### 5. Archon Integration

All PRPs integrate with Archon for:
- Task tracking and status updates
- Project context persistence
- Cross-session knowledge retention
- Team coordination

## Workflow Overview

```
Feature Idea
    |
    v
+-------------------+
|     PRD Phase     |  <- Problem definition, user stories, phases
+--------+----------+
         |
         v
+-------------------+
|    Plan Phase     |  <- Codebase exploration, pattern extraction
+--------+----------+
         |
         v
+-------------------+
| Implement Phase   |  <- Task execution, validation loops
+--------+----------+
         |
         v
+-------------------+
|   Report Phase    |  <- Documentation, lessons learned
+--------+----------+
         |
         v
+-------------------+
|   Review Phase    |  <- Code review, quality gates
+--------+----------+
         |
         v
    PR & Merge
```

## Validation Commands by Stack

### Python

```bash
# Level 1: Static Analysis
ruff check . && mypy .

# Level 2: Unit Tests
pytest tests/unit -v

# Level 3: Full Suite
pytest && python -m build
```

### TypeScript/Node.js

```bash
# Level 1: Static Analysis
npm run lint && npm run type-check

# Level 2: Unit Tests
npm test -- --coverage

# Level 3: Full Suite
npm test && npm run build
```

### .NET/C#

```bash
# Level 1: Static Analysis
dotnet build
dotnet format --verify-no-changes

# Level 2: Unit Tests
dotnet test --filter "Category=Unit"

# Level 3: Full Suite
dotnet test && dotnet build --configuration Release
```

### Multi-Stack (Claude Code Projects)

```bash
# Level 1: Validation scripts exist and pass
./scripts/validate.sh

# Level 2: Component tests
pytest tests/ -v

# Level 3: Integration tests
./scripts/test-integration.sh
```

## Templates

| Template | Purpose | Location |
|----------|---------|----------|
| PRD Template | Large features with phases | `templates/prd-template.md` |
| Plan Template | Implementation plans | `templates/plan-template.md` |
| Issue Investigation | Bug analysis | `templates/issue-investigation-template.md` |
| Implementation Report | Post-implementation docs | `templates/implementation-report-template.md` |

## Best Practices

### DO

- Start with codebase exploration before planning
- Include actual code snippets with file:line references
- Define validation commands for every task
- Mark out-of-scope items explicitly
- Update PRD status after each phase completes
- Create Archon tasks for trackable work
- Archive completed artifacts to `completed/` folders
- Generate implementation reports for significant changes

### DON'T

- Create plans without understanding existing patterns
- Skip validation steps
- Ignore the structured format
- Hardcode values that should be configuration
- Catch all exceptions without specific handling
- Forget to update Archon task status
- Leave completed plans in the active directory

## Archon Integration

### Creating Tasks from Plans

Each plan section maps to Archon tasks:

```python
# Create task for each plan section
manage_task("create",
    project_id="your-project-id",
    title="Implement JWT utilities",
    description="Create src/lib/jwt.ts with token generation and verification",
    feature="auth-system",
    status="todo"
)
```

### Linking Plans to PRDs

Plans reference their parent PRD:

```markdown
> **PRD**: [Feature Name](../prds/feature-name.prd.md)
> **Phase**: 1 of 3 | **Status**: In Progress
```

### Tracking Progress

Update task status as you work:

```python
# Starting work
manage_task("update", task_id="task-123", status="doing")

# Completed
manage_task("update", task_id="task-123", status="done")
```

## Success Metrics

| Metric | Target | Description |
|--------|--------|-------------|
| First-Pass Success | > 80% | Plans implemented without replanning |
| Validation Pass Rate | > 95% | Implementations passing all checks |
| Context Completeness | 100% | All patterns documented with file:line |
| Test Coverage | > 80% | New code covered by tests |
| Archon Task Accuracy | > 90% | Tasks reflect actual work done |

## File Naming Conventions

### PRDs

```
prds/[feature-slug].prd.md
prds/user-authentication.prd.md
prds/api-pagination.prd.md
```

### Plans

```
plans/[feature-slug]-phase-[n].plan.md
plans/user-authentication-phase-1.plan.md
plans/api-pagination.plan.md
```

### Issue Investigations

```
issues/[issue-number]-[brief-description].md
issues/123-login-timeout.md
issues/456-memory-leak.md
```

### Implementation Reports

```
reports/[feature-slug]-report.md
reports/[date]-[feature-slug]-report.md
reports/2026-01-23-user-authentication-report.md
```

## Archiving Completed Work

When work is complete:

1. Move completed plans to `plans/completed/`
2. Move resolved investigations to `issues/completed/`
3. Keep reports in `reports/` for historical reference
4. Update PRD status to reflect completion

```bash
# Example: Archive completed plan
mv PRPs/plans/auth-phase-1.plan.md PRPs/plans/completed/
```

## Related Resources

- **CLAUDE.md**: Project configuration and Claude Code instructions
- **Archon MCP**: Task management and project tracking
- **Skills**: `.claude/skills/` for specialized workflows
- **Commands**: `.claude/commands/` for slash commands

## Credits

This implementation is based on the [PRP Framework by Rasmus Widing](https://github.com/Wirasm/PRPs-agentic-eng), adapted for Claude Code with Archon integration.

---

*Version: 1.0.0 | Last Updated: 2026-01-23*
