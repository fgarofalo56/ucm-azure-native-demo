---
name: validate
description: Validate Claude Code configuration and project setup
---

# /validate - Validate Configuration

Run validation checks on the Claude Code configuration to ensure everything is properly set up.

## Steps to Execute

### Step 1: Check Configuration File

Validate `.claude/config.yaml` exists and has required fields:

```bash
cat .claude/config.yaml
```

Required fields to check:
- `archon_project_id` - Must not be placeholder `[ARCHON_PROJECT_ID]`
- `project_title` - Must not be placeholder `[PROJECT_TITLE]`
- `github_repo` - Should be a valid URL or empty
- `local_path` - Should match current directory

### Step 2: Validate Directory Structure

Check that required directories and files exist:

```bash
# Required directories
ls -la .claude/ 2>/dev/null || echo "MISSING: .claude/"
ls -la .claude/commands/ 2>/dev/null || echo "MISSING: .claude/commands/"
ls -la .claude/skills/ 2>/dev/null || echo "MISSING: .claude/skills/"
ls -la .claude/context/ 2>/dev/null || echo "MISSING: .claude/context/"
ls -la PRPs/ 2>/dev/null || echo "MISSING: PRPs/"
ls -la PRPs/prds/ 2>/dev/null || echo "MISSING: PRPs/prds/"
ls -la PRPs/plans/ 2>/dev/null || echo "MISSING: PRPs/plans/"

# Required files
ls -la CLAUDE.md 2>/dev/null || echo "MISSING: CLAUDE.md"
ls -la .claude/SESSION_KNOWLEDGE.md 2>/dev/null || echo "MISSING: .claude/SESSION_KNOWLEDGE.md"
ls -la .claude/DEVELOPMENT_LOG.md 2>/dev/null || echo "MISSING: .claude/DEVELOPMENT_LOG.md"
ls -la .claude/settings.json 2>/dev/null || echo "MISSING: .claude/settings.json"
```

### Step 3: Validate Archon Connection

Test connection to Archon with the configured project ID:

```python
# Read project ID from config
# Then test connection

find_projects(project_id="[archon_project_id]")

# Check if project exists and is accessible
# If not found, report as validation failure
```

### Step 4: Validate Git Setup

```bash
# Check git is initialized
git status 2>/dev/null || echo "FAIL: Not a git repository"

# Check remote is configured (optional)
git remote -v 2>/dev/null || echo "INFO: No git remote configured"

# Check .gitignore includes necessary entries
grep -q "\.env" .gitignore 2>/dev/null || echo "WARN: .env not in .gitignore"
grep -q "\.claude-backup" .gitignore 2>/dev/null || echo "WARN: .claude-backup not in .gitignore"
```

### Step 5: Validate CLAUDE.md

Check CLAUDE.md for required sections:

```bash
# Check for key sections
grep -q "STARTUP PROTOCOL" CLAUDE.md 2>/dev/null || echo "WARN: Missing STARTUP PROTOCOL section"
grep -q "PROJECT REFERENCE" CLAUDE.md 2>/dev/null || echo "WARN: Missing PROJECT REFERENCE section"
grep -q "archon_project_id" CLAUDE.md 2>/dev/null || echo "WARN: Missing Archon project ID reference"
```

### Step 6: Run Validation Script (if available)

```powershell
# If validate script exists
pwsh -File scripts/validate-claude-code.ps1 2>/dev/null || echo "Validation script not found"
```

### Step 7: Output Validation Report

```
VALIDATION REPORT
=================
Project: [project_title]
Path:    [current directory]

CONFIGURATION
-------------
[PASS/FAIL] config.yaml exists
[PASS/FAIL] archon_project_id configured
[PASS/FAIL] project_title configured
[PASS/FAIL] github_repo configured
[PASS/WARN] local_path matches current directory

DIRECTORY STRUCTURE
-------------------
[PASS/FAIL] .claude/ directory
[PASS/FAIL] .claude/commands/
[PASS/FAIL] .claude/skills/
[PASS/FAIL] .claude/context/
[PASS/FAIL] PRPs/
[PASS/FAIL] PRPs/prds/
[PASS/FAIL] PRPs/plans/

REQUIRED FILES
--------------
[PASS/FAIL] CLAUDE.md
[PASS/FAIL] .claude/SESSION_KNOWLEDGE.md
[PASS/FAIL] .claude/DEVELOPMENT_LOG.md
[PASS/FAIL] .claude/settings.json

ARCHON CONNECTION
-----------------
[PASS/FAIL] Project found in Archon
[INFO] Project has [X] tasks
[INFO] Project has [X] documents

GIT STATUS
----------
[PASS/FAIL] Git repository initialized
[PASS/WARN] Remote configured
[PASS/WARN] .gitignore properly configured

CLAUDE.MD SECTIONS
------------------
[PASS/WARN] STARTUP PROTOCOL section
[PASS/WARN] PROJECT REFERENCE section
[PASS/WARN] Archon project ID documented

OVERALL STATUS
--------------
Validation: [PASSED/FAILED/WARNINGS]
Issues:     [count of failures]
Warnings:   [count of warnings]

RECOMMENDED ACTIONS
-------------------
[List any actions needed to fix failures or address warnings]
```

## Validation Levels

- **PASS**: Requirement met
- **FAIL**: Critical requirement not met - must fix
- **WARN**: Recommended but not required
- **INFO**: Informational only
