---
name: project-wizard
description: Unified project planning and code generation wizard. Supports PRP, Autonomous Harness, and SpecKit frameworks for greenfield projects.
---

# /project-wizard - Unified Project Planning Wizard

A comprehensive wizard that guides you through setting up new projects using one of three development frameworks. Supports session persistence for multi-session setup.

## Arguments

`$ARGUMENTS` - Optional: `resume`, `fresh`, or framework name (`prp`, `harness`, `speckit`)

---

## Phase 0: Resume Check

**FIRST: Check for existing wizard sessions**

```python
# Search for wizard state documents
find_documents(
    query="Project Wizard State",
    document_type="note"
)
```

### If Previous Session Found

Display:

```
EXISTING WIZARD SESSION DETECTED
================================

Project: [Project Name]
Framework: [Selected Framework]
Last Updated: [Date]
Progress: Phase [X] of 7

Phases Completed:
[X] Phase 1: Framework Selection
[X] Phase 2: Project Basics
[ ] Phase 3: Technical Stack
[ ] Phase 4: Framework Configuration
[ ] Phase 5: Archon Integration
[ ] Phase 6: Execution
[ ] Phase 7: Save State

OPTIONS
-------
1. RESUME - Continue from Phase [X]
2. FRESH  - Start a new wizard session (previous state archived)

What would you like to do? [resume/fresh]
```

### If No Previous Session

Proceed directly to Phase 1.

---

## Phase 1: Framework Selection

Display framework comparison and gather selection:

```
PROJECT WIZARD - FRAMEWORK SELECTION
====================================

Choose a development framework based on your project needs:

+----------------------+--------------------------------+----------------------------------------+
| Framework            | Best For                       | Key Features                           |
+----------------------+--------------------------------+----------------------------------------+
| PRP                  | Feature development,           | PRD -> Plan -> Implement,              |
| (Product Requirement | enhancements, brownfield       | validation loops, phased               |
| Planning)            | projects, single features      | implementation, stakeholder docs       |
+----------------------+--------------------------------+----------------------------------------+
| HARNESS              | Greenfield projects,           | Multi-agent pipeline, session          |
| (Autonomous Agent    | long-running development,      | handoffs, autonomous iteration,        |
| Harness)             | complex applications           | 20-50 task generation, agent roles     |
+----------------------+--------------------------------+----------------------------------------+
| SPECKIT              | Complex features,              | Spec-driven development, checklist     |
| (Specification Kit)  | detailed specifications,       | validation, Ralph integration,         |
|                      | compliance requirements        | formal verification, traceability      |
+----------------------+--------------------------------+----------------------------------------+

FRAMEWORK DETAILS
-----------------

1. PRP Framework
   - Creates: PRD (requirements) -> Plan (implementation) -> Tasks
   - Workflow: /prp-prd -> /prp-plan -> /prp-implement
   - Best when: You need stakeholder documentation, phased rollout
   - Output: PRPs/prds/*.md, PRPs/plans/*.md, Archon tasks

2. Autonomous Agent Harness
   - Creates: Agent pipeline with Initializer -> Coder -> Tester -> Reviewer
   - Workflow: /harness-setup -> /harness-init -> /harness-next (iterations)
   - Best when: Building from scratch, want autonomous development
   - Output: .harness/ config, 20-50 Archon tasks, agent prompts

3. SpecKit Framework
   - Creates: Formal specifications with validation checklists
   - Workflow: spec-create -> spec-validate -> implement -> verify
   - Best when: Compliance needed, complex business logic, auditing required
   - Output: specs/*.md, checklists/*.md, verification reports

Which framework would you like to use? [prp/harness/speckit]
```

Store selection and update progress:

```python
wizard_state = {
    "current_phase": 1,
    "completed_phases": [0],
    "framework": "[selected]",
    "created_at": "[timestamp]",
    "updated_at": "[timestamp]"
}
```

---

## Phase 2: Project Basics (Common to All Frameworks)

**FIRST: Check if template_profile already exists in `.claude/config.yaml`**

If the project was created by `setup-claude-code-project.ps1`, a `template_profile` section will exist with `project_type`, `primary_language`, and `framework` already set. In this case:
- Skip language/framework questions (already answered during setup)
- Read values from `template_profile` and display them
- Continue to Phase 3 with pre-filled values

If no `template_profile` exists, ask all questions:

```
PROJECT WIZARD - PROJECT BASICS
===============================

Framework Selected: [FRAMEWORK]

Please provide the following information:

PROJECT IDENTITY
----------------
1. Project Name:
   (lowercase, hyphens allowed, e.g., "my-awesome-app")

2. Project Description:
   (1-3 sentences describing the project's purpose)

3. Project Type:
   [ ] web-frontend    - Browser-based UI application
   [ ] backend-api     - REST/GraphQL API service
   [ ] fullstack       - Combined frontend + backend
   [ ] cli-tool        - Command-line application
   [ ] library         - Reusable package/module
   [ ] infrastructure  - IaC, DevOps tooling

REPOSITORY SETUP
----------------
4. Repository Location:
   [ ] Create new directory at: [default: ./project-name]
   [ ] Use existing directory: [path]
   [ ] Use current directory

5. GitHub Organization (optional):
   (Leave blank for personal repo, or enter org name)

6. Repository Visibility:
   [ ] public
   [ ] private

7. Initialize with:
   [ ] README.md
   [ ] .gitignore (based on project type)
   [ ] LICENSE (MIT/Apache/proprietary)
   [ ] CI/CD workflow (GitHub Actions)
```

Validate inputs:

```bash
# Check if directory exists
ls -la "[provided-path]" 2>/dev/null || echo "Will create new directory"

# Check if git repo exists
git -C "[provided-path]" status 2>/dev/null && echo "Existing git repo detected"
```

Store in wizard state:

```python
wizard_state["project"] = {
    "name": "[name]",
    "description": "[description]",
    "type": "[type]",
    "path": "[path]",
    "github_org": "[org or null]",
    "visibility": "[public/private]",
    "init_options": ["readme", "gitignore", "license", "ci"]
}
```

---

## Phase 3: Technical Stack

```
PROJECT WIZARD - TECHNICAL STACK
================================

Project: [Project Name]
Type: [Project Type]

PRIMARY LANGUAGE
----------------
1. Language:
   [ ] TypeScript  - Modern JavaScript with types
   [ ] Python      - Versatile, great for APIs and ML
   [ ] Go          - Fast, simple, great for services
   [ ] Rust        - Performance-critical applications
   [ ] Java        - Enterprise applications
   [ ] C#          - .NET ecosystem

FRAMEWORK (based on project type and language)
----------------------------------------------
```

**For web-frontend:**
```
2. Frontend Framework:
   [ ] React + Vite      - Component library + fast bundler
   [ ] Next.js           - React with SSR/SSG
   [ ] Vue + Vite        - Progressive framework
   [ ] Svelte + SvelteKit - Compiled framework
   [ ] Astro             - Content-focused sites
```

**For backend-api:**
```
2. Backend Framework:
   [ ] FastAPI (Python)    - Modern async Python API
   [ ] Express (Node)      - Minimal Node.js framework
   [ ] Hono (TypeScript)   - Ultrafast edge-ready
   [ ] Gin (Go)            - High-performance Go
   [ ] Actix (Rust)        - Powerful Rust framework
   [ ] ASP.NET Core (C#)   - Enterprise .NET
```

**For fullstack:**
```
2. Fullstack Framework:
   [ ] Next.js             - React fullstack
   [ ] Nuxt                - Vue fullstack
   [ ] SvelteKit           - Svelte fullstack
   [ ] Remix               - React with loaders
   [ ] T3 Stack            - TypeScript + tRPC + Prisma
```

```
DATABASE
--------
3. Database:
   [ ] PostgreSQL   - Relational, feature-rich
   [ ] MySQL        - Relational, widely supported
   [ ] MongoDB      - Document database
   [ ] SQLite       - Embedded, file-based
   [ ] Supabase     - PostgreSQL + realtime + auth
   [ ] Firebase     - NoSQL + realtime + auth
   [ ] None         - No database needed

PACKAGE MANAGER
---------------
4. Package Manager:
   [ ] npm          - Node default
   [ ] pnpm         - Fast, efficient
   [ ] yarn         - Classic alternative
   [ ] bun          - All-in-one toolkit
   [ ] uv           - Fast Python package manager
   [ ] pip          - Python default
   [ ] cargo        - Rust
   [ ] go mod       - Go modules
```

Store in wizard state:

```python
wizard_state["stack"] = {
    "language": "[language]",
    "framework": "[framework]",
    "database": "[database]",
    "package_manager": "[pm]"
}
```

---

## Phase 4: Framework-Specific Configuration

### If PRP Framework Selected:

```
PRP FRAMEWORK CONFIGURATION
===========================

FEATURE COMPLEXITY
------------------
1. Expected Complexity:
   [ ] Low        - Simple CRUD, minor enhancement (1-3 days)
   [ ] Medium     - New feature, moderate scope (1-2 weeks)
   [ ] High       - Major feature, significant scope (2-4 weeks)
   [ ] Very High  - System-level change, extensive (1+ month)

IMPLEMENTATION PHASES
---------------------
2. Number of Phases:
   [ ] 2 - Foundation + Implementation
   [ ] 3 - Foundation + Core + Polish (recommended)
   [ ] 4 - Foundation + Core + Integration + Polish
   [ ] Custom - Define your own phases

TESTING REQUIREMENTS
--------------------
3. Testing Strategy:
   [ ] Minimal    - Manual testing, happy path
   [ ] Standard   - Unit tests for core logic
   [ ] Thorough   - Unit + integration tests
   [ ] Complete   - Unit + integration + E2E + performance

DOCUMENTATION REQUIREMENTS
--------------------------
4. Documentation Level:
   [ ] Minimal    - Code comments only
   [ ] Standard   - README + API docs
   [ ] Thorough   - Full technical docs
   [ ] Complete   - Technical + user docs + diagrams
```

Store PRP config:

```python
wizard_state["framework_config"] = {
    "complexity": "[level]",
    "phases": "[number]",
    "testing": "[strategy]",
    "documentation": "[level]"
}
```

### If Autonomous Harness Selected:

```
AUTONOMOUS HARNESS CONFIGURATION
================================

TASK GENERATION
---------------
1. Max Features/Tasks:
   Default: 30 (recommended for manageable scope)
   Range: 10-100
   Your value: [___]

2. Task Granularity:
   [ ] Coarse    - Large tasks, fewer total (10-20)
   [ ] Medium    - Balanced tasks (20-40)
   [ ] Fine      - Small tasks, more total (40-70)

SESSION CONFIGURATION
---------------------
3. Session Iteration Limit:
   Default: 50 (max iterations per session)
   Your value: [___]

4. Claude Model Preference:
   [ ] claude-sonnet-4-20250514  - Fast, efficient (recommended)
   [ ] claude-opus-4-5-20251101   - Most capable, slower

AGENT PIPELINE
--------------
5. Enable Agent Roles:
   [X] Initializer  - Parses spec, generates tasks
   [X] Coder        - Implements features
   [X] Tester       - Writes and runs tests
   [ ] Reviewer     - Code review (optional)
   [ ] Documenter   - Generates docs (optional)

MCP SERVERS
-----------
6. MCP Servers to Enable:
   [ ] filesystem    - File operations
   [ ] git           - Version control
   [ ] github        - GitHub API
   [ ] playwright    - Browser automation
   [ ] database      - Database operations
   [ ] crawl4ai      - AI-ready web crawling & RAG
   [ ] Custom: [_______________]

TESTING STRATEGY
----------------
7. Testing Approach:
   [ ] Unit only           - Fast feedback
   [ ] Unit + Integration  - Balanced (recommended)
   [ ] Unit + Integration + E2E - Comprehensive

8. Browser Testing Tool:
   [ ] Playwright  - Modern, cross-browser
   [ ] Puppeteer   - Chrome-focused
   [ ] None        - No browser tests

SECURITY BOUNDARIES
-------------------
9. Allowed Bash Commands (comma-separated):
   Default: npm,npx,node,python,pip,git,ls,cat,mkdir,rm,cp,mv
   Additional: [_______________]

10. Filesystem Restrictions:
    [ ] Project directory only (recommended)
    [ ] Project + home directory
    [ ] No restrictions (use with caution)
```

Store Harness config:

```python
wizard_state["framework_config"] = {
    "max_tasks": 30,
    "granularity": "[level]",
    "iteration_limit": 50,
    "model": "[model]",
    "agents": ["initializer", "coder", "tester"],
    "mcp_servers": ["filesystem", "git"],
    "testing": "[strategy]",
    "browser_tool": "[tool]",
    "allowed_commands": ["npm", "git", "..."],
    "fs_restrictions": "[level]"
}
```

### If SpecKit Selected:

```
SPECKIT CONFIGURATION
=====================

SPECIFICATION DETAIL
--------------------
1. Specification Detail Level:
   [ ] Minimal       - High-level requirements only
   [ ] Standard      - Requirements + acceptance criteria
   [ ] Comprehensive - Full formal specification

CLARIFICATION HANDLING
----------------------
2. Clarification Tolerance:
   [ ] Ask Many      - Pause for unclear requirements
   [ ] Balanced      - Ask for critical items only
   [ ] Make Assumptions - Document assumptions, proceed

CHECKLIST GRANULARITY
---------------------
3. Verification Checklist:
   [ ] Coarse     - Major milestones only
   [ ] Standard   - Feature-level checks
   [ ] Fine       - Task-level verification

RALPH INTEGRATION
-----------------
4. Enable Ralph Loop:
   [ ] Yes  - Iterative refinement with Ralph methodology
   [ ] No   - Standard spec-driven development

   If Yes:
   4a. Ralph Iteration Limit: [default: 5]
   4b. Convergence Threshold: [default: 90%]

TRACEABILITY
------------
5. Requirement Traceability:
   [ ] None       - No formal tracing
   [ ] Basic      - Req -> Implementation mapping
   [ ] Full       - Req -> Design -> Code -> Test mapping

COMPLIANCE
----------
6. Compliance Framework (optional):
   [ ] None
   [ ] SOC2
   [ ] HIPAA
   [ ] GDPR
   [ ] Custom: [_______________]
```

Store SpecKit config:

```python
wizard_state["framework_config"] = {
    "detail_level": "[level]",
    "clarification": "[tolerance]",
    "checklist_granularity": "[level]",
    "ralph_enabled": True,
    "ralph_iterations": 5,
    "ralph_threshold": 0.9,
    "traceability": "[level]",
    "compliance": "[framework or null]"
}
```

---

## Phase 5: Archon Integration

```
PROJECT WIZARD - ARCHON INTEGRATION
===================================

ARCHON PROJECT
--------------
1. Archon Project:
   [ ] Create new Archon project
   [ ] Link to existing project: [search or ID]

2. Project Hierarchy:
   [ ] Standalone project
   [ ] Sub-project of: [parent project ID]

TASK CONFIGURATION
------------------
3. Initial Task Breakdown:
   [ ] Generate from description     - AI creates initial tasks
   [ ] Import from specification     - Provide spec document
   [ ] Manual creation              - Create tasks yourself
   [ ] Skip                         - Set up tasks later

4. Default Task Assignee:
   [ ] Claude Code
   [ ] Unassigned
   [ ] Custom: [_______________]

DOCUMENT TEMPLATES
------------------
5. Create Archon Documents:
   [X] Session Context     - Track current work state
   [X] Architecture        - System design documentation
   [ ] Deployment          - Deployment procedures
   [ ] API Documentation   - API reference
   [ ] Codebase Overview   - Code organization guide
```

Execute Archon integration:

```python
# Create or link project
if create_new:
    project_result = manage_project(
        "create",
        title=wizard_state["project"]["name"],
        description=wizard_state["project"]["description"],
        github_repo=f"https://github.com/{org}/{name}" if org else None
    )
    project_id = project_result["project_id"]
else:
    project_id = selected_project_id

# Create requested documents
if "session_context" in selected_docs:
    manage_document(
        "create",
        project_id=project_id,
        title="Session Context",
        document_type="note",
        content={
            "created": "[timestamp]",
            "wizard_framework": wizard_state["framework"],
            "current_work": "",
            "decisions": [],
            "blockers": [],
            "next_steps": []
        }
    )

if "architecture" in selected_docs:
    manage_document(
        "create",
        project_id=project_id,
        title="Architecture",
        document_type="spec",
        content={
            "overview": wizard_state["project"]["description"],
            "stack": wizard_state["stack"],
            "components": [],
            "decisions": []
        }
    )
```

Store Archon config:

```python
wizard_state["archon"] = {
    "project_id": "[id]",
    "is_new": True,
    "parent_id": None,
    "task_breakdown": "[method]",
    "default_assignee": "[assignee]",
    "documents": ["session_context", "architecture"]
}
```

---

## Phase 6: Confirmation & Execution

Display complete configuration summary:

```
PROJECT WIZARD - CONFIRMATION
=============================

CONFIGURATION SUMMARY
---------------------

PROJECT
  Name:        [project-name]
  Description: [description]
  Type:        [project-type]
  Path:        [/path/to/project]
  GitHub:      [org/repo or N/A]
  Visibility:  [public/private]

TECHNICAL STACK
  Language:    [language]
  Framework:   [framework]
  Database:    [database]
  Package Mgr: [pm]

FRAMEWORK: [PRP/HARNESS/SPECKIT]
  [Framework-specific config displayed]

ARCHON
  Project ID:  [id or "Will create"]
  Documents:   [list of documents to create]
  Task Method: [method]

EXECUTION PLAN
--------------
The wizard will now:

1. [ ] Create repository directory structure
2. [ ] Initialize git repository
3. [ ] Create GitHub repository (if requested)
4. [ ] Create/link Archon project
5. [ ] Generate Archon documents
6. [ ] Create framework-specific artifacts:
   [Framework-specific items listed]
7. [ ] Set up pre-commit hooks
8. [ ] Configure MCP servers (if applicable)
9. [ ] Run initial setup commands

Estimated time: 2-5 minutes

Proceed with project creation? [yes/no/back]
```

### Execute Project Creation

```bash
# Step 1: Create directory structure
mkdir -p "[project-path]"
cd "[project-path]"

# Create standard directories based on project type
mkdir -p src tests docs .claude/commands .claude/skills

# For specific types:
# fullstack: mkdir -p frontend backend shared
# monorepo: mkdir -p packages apps libs
```

```bash
# Step 2: Initialize git
git init
git branch -M main
```

```bash
# Step 3: Create GitHub repo (if requested)
gh repo create "[org/name]" --[visibility] --source=. --remote=origin
```

```python
# Step 4: Create Archon project (already done in Phase 5 if create_new)

# Step 5: Create remaining documents
# [Execute document creation from Phase 5]
```

### Framework-Specific Artifact Generation

**For PRP Framework:**

```bash
# Create PRPs directory structure
mkdir -p PRPs/prds PRPs/plans PRPs/reviews
```

```markdown
# Create initial PRD template at PRPs/prds/initial-setup-prd.md
# PRD: Initial Project Setup

**Created:** [Date]
**Author:** Project Wizard
**Status:** Draft

## Goal
Set up the foundational project structure and development environment.

## Requirements
[Generated based on wizard configuration]

## Success Criteria
- [ ] Development environment running
- [ ] CI/CD pipeline operational
- [ ] Initial tests passing
```

**For Autonomous Harness:**

```bash
# Create harness directory
mkdir -p .harness
```

```yaml
# Create .harness/config.yaml
harness:
  created: [timestamp]
  project_id: [archon_project_id]

agents:
  initializer:
    enabled: true
    model: [selected_model]
  coder:
    enabled: true
    model: [selected_model]
  tester:
    enabled: true
    model: [selected_model]
  reviewer:
    enabled: [true/false]
    model: [selected_model]

limits:
  max_tasks: [configured_value]
  iteration_limit: [configured_value]

mcp_servers: [list]

security:
  allowed_commands: [list]
  fs_restrictions: [level]
```

```markdown
# Create .harness/INITIALIZER_PROMPT.md
# Harness Initializer Prompt

You are the Initializer agent for [project-name].

## Project Context
[Project description and stack from wizard]

## Your Role
1. Parse the application specification
2. Generate 20-50 detailed tasks in Archon
3. Organize tasks by feature
4. Set priority ordering

## Task Format
[Task template]

## Constraints
[From wizard configuration]
```

**For SpecKit Framework:**

```bash
# Create specs directory structure
mkdir -p specs/requirements specs/design specs/verification
mkdir -p checklists
```

```markdown
# Create specs/SPEC_TEMPLATE.md
# Specification: [Feature Name]

## Metadata
- **ID:** SPEC-[NUMBER]
- **Version:** 1.0
- **Status:** Draft
- **Traceability:** [IDs]

## Requirements
### Functional
[REQ-F-001] ...

### Non-Functional
[REQ-NF-001] ...

## Design
[Design details]

## Verification
[Verification criteria]
```

```markdown
# Create checklists/VERIFICATION_CHECKLIST.md
# Verification Checklist

## Pre-Implementation
- [ ] Specification approved
- [ ] Design reviewed
- [ ] Test plan created

## Implementation
- [ ] Code complete
- [ ] Unit tests passing
- [ ] Integration tests passing

## Post-Implementation
- [ ] Documentation updated
- [ ] Traceability matrix complete
- [ ] Stakeholder sign-off
```

### Finalize Setup

```bash
# Step 7: Set up pre-commit hooks
cat > .pre-commit-config.yaml << 'EOF'
repos:
  - repo: https://github.com/pre-commit/pre-commit-hooks
    rev: v4.5.0
    hooks:
      - id: trailing-whitespace
      - id: end-of-file-fixer
      - id: check-yaml
      - id: check-added-large-files
EOF

# Install pre-commit (if available)
which pre-commit && pre-commit install
```

```bash
# Step 8: Create .claude/config.yaml
cat > .claude/config.yaml << EOF
archon_project_id: "[project_id]"
project_title: "[project_name]"
github_repo: "[repo_url]"
local_path: "[path]"
default_branch: "main"
created_at: "[timestamp]"
updated_at: "[timestamp]"
framework: "[selected_framework]"

stack:
  language: "[language]"
  framework: "[framework]"
  database: "[database]"

framework_config:
  [framework-specific config]
EOF
```

```bash
# Step 9: Initial commit
git add -A
git commit -m "Initial project setup via project-wizard

Framework: [framework]
Stack: [language] + [framework]

Co-Authored-By: Claude Opus 4.5 <noreply@anthropic.com>"
```

---

## Phase 7: Save State & Output

Save final wizard state to Archon:

```python
manage_document(
    "create" if new else "update",
    project_id=project_id,
    title="Project Wizard State",
    document_type="note",
    content={
        "status": "completed",
        "completed_at": "[timestamp]",
        "phases_completed": [0, 1, 2, 3, 4, 5, 6, 7],
        "full_config": wizard_state,
        "artifacts_created": [
            "[list of files/directories created]"
        ],
        "next_commands": [
            "[framework-specific next commands]"
        ]
    }
)
```

Display completion summary:

```
PROJECT WIZARD - COMPLETE
=========================

PROJECT CREATED SUCCESSFULLY

PROJECT DETAILS
---------------
Name:          [project-name]
Path:          [/path/to/project]
Framework:     [PRP/HARNESS/SPECKIT]
Archon ID:     [project_id]
GitHub:        [url or N/A]

FILES CREATED
-------------
[OK] .claude/config.yaml
[OK] .claude/commands/ (empty)
[OK] .claude/skills/ (empty)
[OK] .gitignore
[OK] .pre-commit-config.yaml
```

**For PRP:**
```
[OK] PRPs/prds/initial-setup-prd.md
[OK] PRPs/plans/ (empty)
[OK] PRPs/reviews/ (empty)
```

**For Harness:**
```
[OK] .harness/config.yaml
[OK] .harness/INITIALIZER_PROMPT.md
[OK] .harness/CODER_PROMPT.md
[OK] .harness/TESTER_PROMPT.md
```

**For SpecKit:**
```
[OK] specs/SPEC_TEMPLATE.md
[OK] specs/requirements/ (empty)
[OK] checklists/VERIFICATION_CHECKLIST.md
```

```
ARCHON INTEGRATION
------------------
[OK] Project created: [project_id]
[OK] Session Context document
[OK] Architecture document
[OK] Initial tasks: [count] tasks created

NEXT STEPS
----------
```

**For PRP:**
```
1. Review PRPs/prds/initial-setup-prd.md
2. Run /prp-plan to create implementation plan
3. Run /prp-implement to begin development
4. Or use /start to begin a standard session
```

**For Harness:**
```
1. Provide your application specification to the Initializer
2. Run /harness-init to generate tasks from spec
3. Run /harness-status to verify setup
4. Run /harness-next to start first coding session
```

**For SpecKit:**
```
1. Create your first specification using specs/SPEC_TEMPLATE.md
2. Run /spec-validate to verify specification
3. Begin implementation following the spec
4. Use checklists/VERIFICATION_CHECKLIST.md to track progress
```

```
QUICK START
-----------
cd [project-path]
/start

Session initialized. Happy coding!
```

---

## Error Handling

### User Cancellation

If user types `cancel`, `quit`, or `exit` at any phase:

```
WIZARD CANCELLED
================

Your progress has been saved.

Phases Completed: [X] of 7
State Saved: Archon document "[doc_id]"

To resume later, run:
/project-wizard resume

To start fresh:
/project-wizard fresh
```

### Step Failure Recovery

If any execution step fails:

```
EXECUTION ERROR
===============

Step Failed: [step description]
Error: [error message]

RECOVERY OPTIONS
----------------
1. RETRY  - Attempt the failed step again
2. SKIP   - Skip this step and continue
3. BACK   - Return to configuration phase
4. CANCEL - Save progress and exit

What would you like to do? [retry/skip/back/cancel]
```

### Navigation Commands

At any phase, users can type:

- `back` - Return to previous phase
- `restart` - Start over from Phase 1
- `skip` - Skip current phase (where allowed)
- `help` - Show help for current phase
- `status` - Show current wizard progress
- `cancel` - Save and exit

---

## Progress Display

After each phase completion, display:

```
WIZARD PROGRESS
===============

[X] Phase 0: Resume Check - COMPLETE
[X] Phase 1: Framework Selection - COMPLETE
[X] Phase 2: Project Basics - COMPLETE
[*] Phase 3: Technical Stack - IN PROGRESS
[ ] Phase 4: Framework Configuration - PENDING
[ ] Phase 5: Archon Integration - PENDING
[ ] Phase 6: Execution - PENDING
[ ] Phase 7: Save State - PENDING

Progress: 3/7 phases (43%)
```

---

## Shortcuts

Quick start commands:

```bash
# Start fresh with specific framework
/project-wizard prp
/project-wizard harness
/project-wizard speckit

# Resume previous session
/project-wizard resume

# Start completely fresh
/project-wizard fresh
```

---

## Quality Checklist

Before completing the wizard, verify:

- [ ] All required fields have values
- [ ] Directory path is valid and writable
- [ ] Archon connection is available
- [ ] Selected framework config is complete
- [ ] No conflicting options selected
- [ ] Git is available (if repo creation requested)
- [ ] GitHub CLI authenticated (if GitHub repo requested)
