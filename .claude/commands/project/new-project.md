---
name: new-project
description: Create and configure a new Claude Code project
---

# /new-project - Create New Project

Initialize a new project with Claude Code configuration, either in the current directory or by setting up Archon integration for an existing codebase.

## Steps to Execute

### Step 1: Gather Project Information

Ask the user for the following information:

```
NEW PROJECT SETUP
=================

Please provide the following information:

1. Project Title: [human-readable name]
2. Project Description: [brief description of the project]
3. Project Type: [web-frontend, backend-api, fullstack, cli-library, infrastructure, power-platform]
4. Primary Language: [typescript, python, csharp, go, java, rust]
5. Framework: [react, fastapi, nextjs, express, etc. - based on type + language]
6. GitHub Repository URL: [optional - leave blank if not on GitHub]
7. Default Assignee: [Claude Code / User / specific name]
```

### Step 2: Check Current State

Determine if this is:
- A new project in an existing codebase (config.yaml has placeholders)
- A fresh setup needing full initialization

```bash
# Check if config exists and has placeholders
cat .claude/config.yaml 2>/dev/null | grep -q "\[ARCHON_PROJECT_ID\]" && echo "Config needs initialization"

# Check if Archon project might already exist
# Will search in Step 3
```

### Step 3: Create or Link Archon Project

**Option A: Create new Archon project**

```python
result = manage_project(
    "create",
    title="[Project Title]",
    description="[Project Description]",
    github_repo="[GitHub URL if provided]"
)
# Extract project_id from result
```

**Option B: Link to existing Archon project**

If user indicates a project already exists:

```python
# Search for existing project
results = find_projects(query="[Project Title]")
# Let user select if multiple matches
```

### Step 4: Update Configuration File

Update `.claude/config.yaml` with actual values:

```yaml
archon_project_id: "[actual project ID from Archon]"
project_title: "[Project Title]"
github_repo: "[GitHub URL]"
local_path: "[current directory path]"
default_branch: "main"
created_at: "[current date]"
updated_at: "[current date]"
default_assignee: "[selected assignee]"

languages:
  - [language1]

feature_labels:
  - core
  - documentation
  - testing
  - infrastructure
  - bugfix

template_profile:
  template_version: "2.0.0"
  project_type: "[project type]"
  primary_language: "[language]"
  framework: "[framework]"
  skill_groups: ["core", "[other groups based on project type]"]
  command_groups: ["core"]
  dev_frameworks: []
  created_with: "new-project-command"
```

### Step 5: Initialize Context Files

Ensure all context files are initialized:

**SESSION_KNOWLEDGE.md:**
```markdown
# Session Knowledge

## Project Overview
[Project Title] - [Brief description]

## Current State
Project initialized on [date].

## Key Information
- Archon Project ID: [id]
- Primary Languages: [languages]

## Session Notes
[To be updated during sessions]
```

**DEVELOPMENT_LOG.md:**
```markdown
# Development Log

## [Current Date] - Project Initialization

### Setup Complete
- Created Archon project: [project_id]
- Configured Claude Code settings
- Initialized context files

### Next Steps
- [First task or focus area]
```

### Step 6: Create Initial Archon Documents (Optional)

Offer to create standard Archon documents:

```python
# Architecture document
manage_document(
    "create",
    project_id="[project_id]",
    title="Architecture",
    document_type="spec",
    content={"overview": "To be documented", "components": [], "decisions": []}
)

# Session Context document
manage_document(
    "create",
    project_id="[project_id]",
    title="Session Context",
    document_type="note",
    content={"current_work": "", "recent_decisions": [], "next_steps": []}
)
```

### Step 7: Create Initial Tasks (Optional)

Ask if user wants to create initial tasks:

```python
# Example initial tasks
manage_task(
    "create",
    project_id="[project_id]",
    title="Document project architecture",
    description="Create comprehensive architecture documentation",
    feature="documentation"
)

manage_task(
    "create",
    project_id="[project_id]",
    title="Set up development environment",
    description="Configure local development environment and dependencies",
    feature="infrastructure"
)
```

### Step 8: Output Setup Summary

```
PROJECT SETUP COMPLETE
======================

PROJECT DETAILS
---------------
Title:          [Project Title]
Archon ID:      [project_id]
GitHub:         [URL or "Not configured"]
Local Path:     [directory]
Languages:      [language list]

CONFIGURATION FILES
-------------------
[OK] .claude/config.yaml - Updated with project values
[OK] .claude/SESSION_KNOWLEDGE.md - Initialized
[OK] .claude/DEVELOPMENT_LOG.md - Initialized

ARCHON INTEGRATION
------------------
[OK] Project created/linked in Archon
[OK/SKIP] Architecture document created
[OK/SKIP] Session Context document created
[OK/SKIP] Initial tasks created

NEXT STEPS
----------
1. Review and customize CLAUDE.md for project-specific instructions
2. Run /validate to confirm setup
3. Run /start to begin your first session
4. Consider creating a PRD for your first feature: /prp-prd

QUICK START
-----------
Type /start to begin working on this project.
```

## Error Handling

- If Archon is unavailable, create config with placeholder and note for later
- If git is not initialized, offer to run `git init`
- If files already exist with content, ask before overwriting
