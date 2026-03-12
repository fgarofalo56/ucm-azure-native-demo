---
name: wizard-status
description: Check the status of project wizard sessions and generated artifacts
---

# /wizard-status - Project Wizard Status

View the status of wizard sessions, track progress, and see generated artifacts.

## Arguments

`$ARGUMENTS` - Optional: `all`, `active`, `completed`, or project name/session ID

---

## Step 1: Query Wizard Sessions

```python
# Get all wizard state documents
all_sessions = find_documents(
    query="Project Wizard State",
    document_type="note"
)

# Categorize sessions
active_sessions = []
completed_sessions = []
cancelled_sessions = []
error_sessions = []

for session in all_sessions:
    content = session.get("content", {})
    status = content.get("status", "unknown")

    if status == "in-progress":
        active_sessions.append(session)
    elif status == "completed":
        completed_sessions.append(session)
    elif status == "cancelled":
        cancelled_sessions.append(session)
    else:
        error_sessions.append(session)
```

---

## Step 2: Display Summary

### Default View (Overview)

```
PROJECT WIZARD STATUS
=====================

SUMMARY
-------
Active Sessions:    [X]
Completed:          [X]
Cancelled:          [X]
Total Projects:     [X]

ACTIVE SESSIONS
---------------
+----+-----------------------+------------+----------+------------------+
| #  | Project               | Framework  | Progress | Last Updated     |
+----+-----------------------+------------+----------+------------------+
| 1  | my-awesome-app        | PRP        | 4/7 (57%)| 2024-01-15 14:30 |
| 2  | api-service           | HARNESS    | 2/7 (29%)| 2024-01-14 09:15 |
+----+-----------------------+------------+----------+------------------+

RECENTLY COMPLETED
------------------
+----+-----------------------+------------+------------------+
| #  | Project               | Framework  | Completed        |
+----+-----------------------+------------+------------------+
| 1  | web-portal            | PRP        | 2024-01-12 16:00 |
| 2  | data-processor        | SPECKIT    | 2024-01-10 11:30 |
+----+-----------------------+------------+------------------+

QUICK ACTIONS
-------------
  /wizard-resume              - Resume active session
  /wizard-status [project]    - View project details
  /wizard-status completed    - View all completed
  /project-wizard             - Start new wizard
```

---

## Step 3: Detailed Session View

When a specific project/session is requested:

```
PROJECT WIZARD STATUS: my-awesome-app
=====================================

METADATA
--------
Session ID:      abc-123-def-456
Framework:       PRP
Status:          In Progress
Started:         2024-01-15 10:00:00
Last Updated:    2024-01-15 14:30:00
Duration:        4h 30m

PHASE PROGRESS
--------------
[=========>         ] 57% (4 of 7 phases)

  [X] Phase 0: Resume Check           (10:00:15)
  [X] Phase 1: Framework Selection    (10:02:30) - PRP
  [X] Phase 2: Project Basics         (10:15:45) - my-awesome-app
  [X] Phase 3: Technical Stack        (10:25:00) - TypeScript + React
  [ ] Phase 4: Framework Configuration (next)
  [ ] Phase 5: Archon Integration
  [ ] Phase 6: Execution
  [ ] Phase 7: Save State

CONFIGURATION
-------------
Project:
  Name:           my-awesome-app
  Description:    A modern web application
  Type:           fullstack
  Path:           E:/Projects/my-awesome-app
  GitHub:         HouseGarofalo/my-awesome-app (pending)
  Visibility:     private

Technical Stack:
  Language:       TypeScript
  Framework:      React + Vite
  Database:       PostgreSQL
  Package Mgr:    pnpm

Framework Config:
  Complexity:     Medium
  Phases:         3
  Testing:        Standard (unit + integration)
  Documentation:  Standard

GENERATED ARTIFACTS
-------------------
Filesystem:
  [X] E:/Projects/my-awesome-app/
  [X] E:/Projects/my-awesome-app/src/
  [X] E:/Projects/my-awesome-app/tests/
  [X] E:/Projects/my-awesome-app/docs/
  [ ] E:/Projects/my-awesome-app/.claude/config.yaml
  [ ] E:/Projects/my-awesome-app/.gitignore
  [ ] E:/Projects/my-awesome-app/.pre-commit-config.yaml

Git:
  [ ] Repository initialized
  [ ] Initial commit
  [ ] GitHub repo created
  [ ] Remote configured

Archon:
  [ ] Project created
  [ ] Session Context document
  [ ] Architecture document
  [ ] Initial tasks

Framework (PRP):
  [ ] PRPs/prds/initial-setup-prd.md
  [ ] PRPs/plans/
  [ ] PRPs/reviews/

ACTIONS
-------
  /wizard-resume my-awesome-app  - Continue from Phase 4
  /wizard-status my-awesome-app --artifacts  - List all artifacts
  /wizard-status my-awesome-app --log  - View execution log
```

---

## Step 4: Artifact Verification

When `--artifacts` flag is used:

```
ARTIFACT VERIFICATION: my-awesome-app
=====================================

Checking filesystem artifacts...

DIRECTORIES
-----------
[OK] E:/Projects/my-awesome-app/
[OK] E:/Projects/my-awesome-app/src/
[OK] E:/Projects/my-awesome-app/tests/
[OK] E:/Projects/my-awesome-app/docs/
[!!] E:/Projects/my-awesome-app/.claude/ (not created)
[!!] E:/Projects/my-awesome-app/PRPs/ (not created)

FILES
-----
[!!] .claude/config.yaml - Not created (Phase 6)
[!!] .gitignore - Not created (Phase 6)
[!!] package.json - Not created (Phase 6)

GIT STATUS
----------
[!!] Not a git repository

ARCHON STATUS
-------------
Project ID: (not created)
Documents: 0
Tasks: 0

VERIFICATION SUMMARY
--------------------
Created:    4 items
Pending:    12 items
Missing:    0 items (expected - Phase 4 not complete)
Errors:     0 items

Next phase will create:
  - Framework configuration
  - Archon project
  - Base documents
```

---

## Step 5: Execution Log View

When `--log` flag is used:

```
EXECUTION LOG: my-awesome-app
=============================

Session: abc-123-def-456
Started: 2024-01-15 10:00:00

+------------------+--------+------------------------------+----------+
| Timestamp        | Phase  | Action                       | Result   |
+------------------+--------+------------------------------+----------+
| 10:00:00.123     | 0      | Resume check started         | OK       |
| 10:00:15.456     | 0      | No previous session found    | OK       |
| 10:02:00.789     | 1      | Framework selection prompt   | OK       |
| 10:02:30.012     | 1      | User selected: PRP           | OK       |
| 10:05:00.345     | 2      | Project basics prompt        | OK       |
| 10:15:45.678     | 2      | Validated project path       | OK       |
| 10:15:46.901     | 2      | Created directory structure  | OK       |
| 10:20:00.234     | 3      | Technical stack prompt       | OK       |
| 10:25:00.567     | 3      | Stack validated              | OK       |
| 14:30:00.890     | 3      | Session paused by user       | PAUSED   |
+------------------+--------+------------------------------+----------+

Total entries: 10
Errors: 0
Warnings: 0

Last action: Session paused by user
Next action: Resume Phase 4 - Framework Configuration
```

---

## Step 6: Filter Views

### Active Sessions Only

```bash
/wizard-status active
```

```
ACTIVE WIZARD SESSIONS
======================

+----+-----------------------+------------+----------+------------------+---------+
| #  | Project               | Framework  | Progress | Last Updated     | Actions |
+----+-----------------------+------------+----------+------------------+---------+
| 1  | my-awesome-app        | PRP        | 4/7      | 2024-01-15 14:30 | resume  |
| 2  | api-service           | HARNESS    | 2/7      | 2024-01-14 09:15 | resume  |
+----+-----------------------+------------+----------+------------------+---------+

Total: 2 active sessions

Quick resume: /wizard-resume [number]
```

### Completed Sessions

```bash
/wizard-status completed
```

```
COMPLETED WIZARD SESSIONS
=========================

+----+-----------------------+------------+------------------+-------------------+
| #  | Project               | Framework  | Completed        | Archon Project    |
+----+-----------------------+------------+------------------+-------------------+
| 1  | web-portal            | PRP        | 2024-01-12 16:00 | proj-abc123       |
| 2  | data-processor        | SPECKIT    | 2024-01-10 11:30 | proj-def456       |
| 3  | mobile-backend        | HARNESS    | 2024-01-08 09:45 | proj-ghi789       |
+----+-----------------------+------------+------------------+-------------------+

Total: 3 completed sessions

View project: /wizard-status [project-name]
Start new: /project-wizard
```

---

## Quick Reference

| Command | Description |
|---------|-------------|
| `/wizard-status` | Show overview of all sessions |
| `/wizard-status active` | Show only active sessions |
| `/wizard-status completed` | Show completed sessions |
| `/wizard-status [name]` | Show specific project details |
| `/wizard-status [name] --artifacts` | Verify created artifacts |
| `/wizard-status [name] --log` | View execution log |
| `/wizard-status --json` | Output as JSON |

---

## Integration with Other Commands

```bash
# Check status then resume
/wizard-status
/wizard-resume my-awesome-app

# Start new after checking existing
/wizard-status completed
/project-wizard

# Verify artifacts after completion
/wizard-status web-portal --artifacts
```

---

*Command Version*: 1.0
*Requires*: Archon MCP server
