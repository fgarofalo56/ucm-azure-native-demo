---
name: prp-implement
description: Execute an implementation plan with guided phases and validation
---

# /prp-implement - Execute Implementation Plan

Execute an existing implementation plan with phase-by-phase guidance, validation gates, and progress tracking.

## Arguments

`$ARGUMENTS` - Path to plan file or feature name (optional, will list available plans if not provided)

## Steps to Execute

### Step 1: Locate Implementation Plan

If `$ARGUMENTS` is not provided, list available plans:

```bash
ls -la PRPs/plans/*.md 2>/dev/null | grep -v completed
```

Ask user to select which plan to implement.

If `$ARGUMENTS` is provided:
- If it's a file path, read that file
- If it's a feature name, look for `PRPs/plans/[feature-name]-plan.md`

### Step 2: Load and Parse Plan

Read the implementation plan:

```bash
cat PRPs/plans/[feature-name]-plan.md
```

Extract:
- Prerequisites checklist
- Phase definitions
- Tasks per phase
- Validation criteria
- Success metrics

### Step 3: Verify Prerequisites

Before starting implementation, verify all prerequisites:

```
PREREQUISITE CHECK
==================

Checking prerequisites from implementation plan...

[ ] PRD approved by stakeholders
[ ] Development environment set up
[ ] Required access/permissions obtained
[ ] Dependencies available

[Run checks and report status]

All prerequisites met? (yes/no/skip)
```

If prerequisites not met, provide guidance on resolving them.

### Step 4: Implementation Loop

For each phase in the plan, execute the following cycle:

```
=================================================
PHASE [N]: [Phase Name]
=================================================

Objective: [Phase objective from plan]

TASKS FOR THIS PHASE
--------------------
```

#### For Each Task:

**4a. Display Task Details**
```
TASK [N.M]: [Task Name]
-----------------------
Description: [Task description]
Files:       [Files to create/modify]
Estimated:   [Time estimate]
Dependencies: [Any dependencies]

Implementation Notes:
[Notes from plan]

Ready to implement this task? (yes/skip/help)
```

**4b. Execute Task**

If user confirms:
1. Load relevant context (files, patterns mentioned in plan)
2. Implement according to plan specifications
3. Follow project conventions

**4c. Task Validation**
```
TASK VALIDATION
---------------
[ ] [Check 1 from plan]
[ ] [Check 2 from plan]

Running validation...
[Execute validation commands]

Task [N.M] Status: [PASS/FAIL]
```

**4d. Update Progress**

```python
# Update task status in Archon
manage_task("update", task_id="[task_id]", status="done")
```

#### Phase Validation Gate

After all tasks in a phase:

```
=================================================
PHASE [N] VALIDATION GATE
=================================================

Running phase validation...

[Execute phase validation commands from plan]

Phase Validation Results:
[ ] [Validation 1]: PASS/FAIL
[ ] [Validation 2]: PASS/FAIL

Phase [N] Status: [COMPLETE/BLOCKED]

Proceed to Phase [N+1]? (yes/fix/stop)
```

### Step 5: Progress Tracking

Throughout implementation, maintain progress state:

```python
# Update Archon task for current phase
manage_task("update", task_id="[phase_task_id]", status="doing")

# Log progress to development log
# Append to .claude/DEVELOPMENT_LOG.md
```

### Step 6: Handle Blockers

If validation fails or implementation hits a blocker:

```
BLOCKER DETECTED
================

Issue: [Description of blocker]

Options:
1. Attempt to fix the issue
2. Document and skip (with risk acknowledgment)
3. Stop implementation and investigate
4. Seek help / escalate

Select option (1/2/3/4):
```

Document all blockers in `.claude/FAILED_ATTEMPTS.md` for future reference.

### Step 7: Final Validation

After all phases complete:

```
=================================================
FINAL VALIDATION
=================================================

Running complete validation suite...

Code Quality:
[ ] Linting passes
[ ] Type checking passes
[ ] No security issues

Testing:
[ ] Unit tests pass
[ ] Integration tests pass
[ ] Coverage target met

Documentation:
[ ] Code documented
[ ] User docs updated (if applicable)
[ ] API docs updated (if applicable)

PRD Success Criteria:
[ ] [Metric 1 from PRD]
[ ] [Metric 2 from PRD]
[ ] [Metric 3 from PRD]

OVERALL STATUS: [COMPLETE/INCOMPLETE]
```

### Step 8: Completion Actions

When implementation is complete:

**8a. Update Archon**
```python
# Mark all phase tasks as done
for task_id in phase_tasks:
    manage_task("update", task_id=task_id, status="done")

# Create completion summary in Archon documents
manage_document(
    "update",
    project_id="[archon_project_id]",
    document_id="[session_context_doc_id]",
    content={
        "last_completed": "[feature name]",
        "completion_date": "[date]",
        "notes": "[any important notes]"
    }
)
```

**8b. Move Plan to Completed**
```bash
mv PRPs/plans/[feature-name]-plan.md PRPs/plans/completed/
```

**8c. Update Development Log**
```markdown
## [Date] - [Feature Name] Implementation Complete

### Summary
- Completed all [X] phases
- [Y] tasks implemented
- All validations passing

### Notes
[Any important implementation notes]

### Follow-up Items
- [Any items for future work]
```

### Step 9: Output Completion Summary

```
IMPLEMENTATION COMPLETE
=======================

Feature:     [Feature Name]
PRD:         PRPs/prds/[feature-name]-prd.md
Plan:        PRPs/plans/completed/[feature-name]-plan.md
Duration:    [Actual time taken]

PHASES COMPLETED
----------------
Phase 1: Foundation      - COMPLETE
Phase 2: Core           - COMPLETE
Phase 3: Integration    - COMPLETE
Phase 4: Testing & Docs - COMPLETE

VALIDATION STATUS
-----------------
Code Quality:     PASS
Unit Tests:       PASS ([X] tests)
Integration:      PASS
Documentation:    COMPLETE

SUCCESS CRITERIA
----------------
[X] [Metric 1] - Achieved
[X] [Metric 2] - Achieved
[X] [Metric 3] - Achieved

ARTIFACTS
---------
- New files created: [list]
- Files modified: [list]
- Tests added: [count]
- Documentation: [list]

NEXT STEPS
----------
1. Code review (if not done)
2. Merge to main branch
3. Deploy to staging
4. Update stakeholders

Congratulations! The feature is ready for deployment.
```

## Interruption Handling

If implementation is interrupted (session end, context reset, etc.):

1. Save current phase/task progress to SESSION_KNOWLEDGE.md
2. Update Archon tasks with current status
3. On resume, `/prp-implement` will detect partial completion and offer to continue

```
RESUMING IMPLEMENTATION
=======================

Detected partial implementation of: [Feature Name]

Progress:
- Phase 1: COMPLETE
- Phase 2: IN PROGRESS (Task 2.3)
- Phase 3: NOT STARTED
- Phase 4: NOT STARTED

Resume from Task 2.3? (yes/restart/cancel)
```

## Emergency Stop

At any point, user can type `stop` or `pause` to:
1. Save all current progress
2. Update task statuses
3. Document current state
4. Exit implementation mode gracefully
