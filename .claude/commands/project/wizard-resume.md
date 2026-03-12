---
name: wizard-resume
description: Resume an incomplete project wizard session from Archon
---

# /wizard-resume - Resume Project Wizard Session

Resume a previously saved project wizard session to continue where you left off.

## Arguments

`$ARGUMENTS` - Optional: Session ID or project name to resume

---

## Step 1: Search for Wizard Sessions

Search Archon for incomplete wizard state documents:

```python
# Find all wizard state documents
wizard_docs = find_documents(
    query="Project Wizard State",
    document_type="note"
)

# Filter to incomplete sessions
incomplete_sessions = []
for doc in wizard_docs:
    content = doc.get("content", {})
    if isinstance(content, dict):
        status = content.get("status", "")
        if status not in ["completed", "cancelled"]:
            incomplete_sessions.append(doc)
```

---

## Step 2: Display Available Sessions

If multiple sessions found:

```
WIZARD SESSIONS AVAILABLE
=========================

Found [X] incomplete wizard session(s):

+-----+-----------------------+------------+----------+------------------+
| #   | Project Name          | Framework  | Progress | Last Updated     |
+-----+-----------------------+------------+----------+------------------+
| 1   | my-awesome-app        | PRP        | 4/7      | 2024-01-15 14:30 |
| 2   | api-service           | HARNESS    | 2/7      | 2024-01-14 09:15 |
| 3   | data-pipeline         | SPECKIT    | 5/7      | 2024-01-13 16:45 |
+-----+-----------------------+------------+----------+------------------+

Enter session number to resume, or 'list' for details: [___]
```

If `list` or details requested:

```
SESSION DETAILS: my-awesome-app
===============================

Metadata:
  Session ID:    abc-123-def-456
  Framework:     PRP
  Started:       2024-01-15 10:00
  Last Updated:  2024-01-15 14:30

Progress:
  [X] Phase 0: Resume Check
  [X] Phase 1: Framework Selection - PRP selected
  [X] Phase 2: Project Basics - my-awesome-app
  [X] Phase 3: Technical Stack - TypeScript + React
  [ ] Phase 4: Framework Configuration
  [ ] Phase 5: Archon Integration
  [ ] Phase 6: Execution
  [ ] Phase 7: Save State

Configuration Summary:
  Project: my-awesome-app
  Path: E:/Projects/my-awesome-app
  Stack: TypeScript + React + PostgreSQL
  Package Manager: pnpm

Artifacts Created:
  [X] Directory structure
  [ ] Git initialized
  [ ] GitHub repo
  [ ] Archon project
  [ ] Framework files

Resume from: Phase 4 - Framework Configuration
```

---

## Step 3: Validate Resume Conditions

Before resuming, verify prerequisites:

```bash
# Check if Archon is available
# (Verify MCP server connection)

# Check if target directory still exists
ls -la "[project_path]" 2>/dev/null || echo "Directory not found"

# Check git status if repo was initialized
git -C "[project_path]" status 2>/dev/null || echo "No git repo"

# Check for conflicts
ls -la "[project_path]/.claude/config.yaml" 2>/dev/null
```

### Validation Results

```
RESUME VALIDATION
=================

Prerequisites:
  [OK] Archon MCP server available
  [OK] Target directory exists: E:/Projects/my-awesome-app
  [OK] Git repository initialized
  [--] GitHub repo not created yet (will be created in Phase 6)
  [OK] No conflicting changes detected

Ready to resume from Phase 4: Framework Configuration

Continue? [yes/no]
```

### If Issues Found

```
RESUME VALIDATION - ISSUES DETECTED
====================================

Prerequisites:
  [OK] Archon MCP server available
  [!!] Target directory not found: E:/Projects/my-awesome-app
  [--] Cannot verify git status

RECOVERY OPTIONS
----------------
1. CREATE  - Create missing directory and continue
2. PATH    - Specify new path for project
3. RESTART - Start wizard from beginning (keeps config)
4. CANCEL  - Exit without changes

What would you like to do? [create/path/restart/cancel]
```

---

## Step 4: Load Session State

Load the full wizard state from Archon:

```python
# Get the session document
session_doc = find_documents(
    project_id=selected_session["project_id"],
    title=selected_session["title"]
)

# Parse wizard state
wizard_state = session_doc["content"]

# Extract configuration
project_config = wizard_state.get("project", {})
stack_config = wizard_state.get("stack", {})
framework_config = wizard_state.get("framework_config", {})
archon_config = wizard_state.get("archon", {})

# Determine resume point
current_phase = wizard_state.get("current_phase", 0)
completed_phases = wizard_state.get("completed_phases", [])
```

---

## Step 5: Resume Wizard

Display resume confirmation and continue:

```
RESUMING WIZARD SESSION
=======================

Project: my-awesome-app
Framework: PRP
Resume Point: Phase 4 - Framework Configuration

Loaded Configuration:
  - Project basics: my-awesome-app (TypeScript)
  - Technical stack: React + PostgreSQL + pnpm
  - Repository: E:/Projects/my-awesome-app

Resuming in 3 seconds...
(Press Ctrl+C to cancel)
```

Then invoke the main wizard with the loaded state:

```
[Transition to /project-wizard with pre-loaded state]

PROJECT WIZARD - FRAMEWORK CONFIGURATION
========================================

[Continue from Phase 4 with loaded configuration]
```

---

## Step 6: Update Session Tracking

After each phase completion, update the session state:

```python
# Update the wizard state document
manage_document(
    "update",
    document_id=session_doc["id"],
    content={
        **wizard_state,
        "current_phase": new_phase,
        "completed_phases": completed_phases + [previous_phase],
        "updated_at": current_timestamp
    }
)
```

---

## Error Handling

### No Sessions Found

```
NO WIZARD SESSIONS FOUND
========================

There are no incomplete wizard sessions to resume.

OPTIONS
-------
1. Start new wizard: /project-wizard
2. Check completed sessions: /wizard-status completed
3. Search by project: /wizard-resume [project-name]

Would you like to start a new wizard? [yes/no]
```

### Session ID Not Found

```
SESSION NOT FOUND
=================

Could not find wizard session: [session-id]

Did you mean one of these?
  - my-awesome-app (abc-123...)
  - api-service (def-456...)

Or try:
  /wizard-resume          - List all sessions
  /project-wizard fresh   - Start new wizard
```

### Archon Unavailable

```
ARCHON CONNECTION REQUIRED
==========================

Cannot resume wizard session - Archon MCP server is not available.

Please ensure:
1. Archon MCP server is running
2. Connection is configured in MCP settings
3. Authentication is valid

Check MCP status: /mcp

After fixing, retry: /wizard-resume
```

---

## Quick Commands

```bash
# Resume most recent session
/wizard-resume

# Resume specific session by name
/wizard-resume my-awesome-app

# Resume by session ID
/wizard-resume --session-id abc-123-def-456

# List sessions with details
/wizard-resume list

# Resume and skip validation
/wizard-resume --skip-validation
```

---

## Session States

| State | Description | Action |
|-------|-------------|--------|
| `in-progress` | Active, incomplete session | Can resume |
| `completed` | Successfully finished | View only |
| `cancelled` | User cancelled | Can restart |
| `error` | Failed during execution | Can resume with recovery |

---

*Command Version*: 1.0
*Requires*: Archon MCP server
