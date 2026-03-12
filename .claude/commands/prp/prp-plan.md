---
name: prp-plan
description: Create an implementation plan from a PRD
---

# /prp-plan - Create Implementation Plan

Generate a detailed implementation plan from an existing PRD (Product Requirements Document).

## Arguments

`$ARGUMENTS` - Path to PRD file or feature name (optional, will list available PRDs if not provided)

## Steps to Execute

### Step 1: Locate PRD

If `$ARGUMENTS` is not provided, list available PRDs:

```bash
ls -la PRPs/prds/*.md 2>/dev/null
```

Ask user to select which PRD to create a plan for.

If `$ARGUMENTS` is provided:
- If it's a file path, read that file
- If it's a feature name, look for `PRPs/prds/[feature-name]-prd.md`

### Step 2: Analyze PRD

Read and analyze the PRD to extract:
- Requirements (P0, P1, P2)
- Technical considerations
- Dependencies
- Constraints
- Success metrics

```bash
cat PRPs/prds/[feature-name]-prd.md
```

### Step 3: Research Implementation Patterns

Based on PRD requirements, research:

#### 3a. Codebase Patterns
```
Search for:
- Similar implementations in codebase
- Existing patterns to follow
- Test patterns for similar features
- Integration points mentioned in PRD
```

#### 3b. Technical Research
```
Research:
- Best implementation approaches
- Library/framework patterns
- Error handling strategies
- Performance optimization techniques
```

### Step 4: Generate Implementation Plan

Create the plan file at `PRPs/plans/[feature-name]-plan.md`:

```markdown
# Implementation Plan: [Feature Name]

**PRD Reference:** PRPs/prds/[feature-name]-prd.md
**Created:** [Date]
**Author:** [User/Claude Code]
**Status:** Draft
**Estimated Effort:** [X days]

---

## Overview

[Brief summary of what will be implemented]

---

## Prerequisites

### Before Starting
- [ ] PRD approved by stakeholders
- [ ] Development environment set up
- [ ] Required access/permissions obtained
- [ ] Dependencies available

### Required Knowledge
- [Technology/pattern 1]
- [Technology/pattern 2]

### Dependencies
| Dependency | Status | Notes |
|------------|--------|-------|
| [Dep 1] | Available | |
| [Dep 2] | Needs setup | |

---

## Implementation Phases

### Phase 1: Foundation [Day 1-X]

**Objective:** [What this phase accomplishes]

#### Tasks

##### 1.1 [Task Name]
- **Description:** [What to do]
- **Files:** [Files to create/modify]
- **Estimated Time:** [X hours]
- **Dependencies:** None
- **Validation:**
  - [ ] [Check 1]
  - [ ] [Check 2]

**Implementation Notes:**
```python
# Key implementation approach
# Reference: [existing file to follow]
```

##### 1.2 [Task Name]
[Same structure as above]

#### Phase 1 Validation
```bash
# Commands to verify phase 1 is complete
pytest tests/phase1/ -v
```

---

### Phase 2: Core Implementation [Day X-Y]

**Objective:** [What this phase accomplishes]

#### Tasks

##### 2.1 [Task Name]
[Task details]

##### 2.2 [Task Name]
[Task details]

#### Phase 2 Validation
```bash
# Commands to verify phase 2 is complete
```

---

### Phase 3: Integration [Day Y-Z]

**Objective:** [What this phase accomplishes]

#### Tasks
[Integration tasks]

#### Phase 3 Validation
```bash
# Integration test commands
```

---

### Phase 4: Testing & Polish [Day Z-End]

**Objective:** Complete testing and documentation

#### Tasks

##### 4.1 Unit Tests
- Write comprehensive unit tests
- Target coverage: [X]%

##### 4.2 Integration Tests
- End-to-end test scenarios
- Edge case coverage

##### 4.3 Documentation
- Code documentation
- User documentation
- API documentation (if applicable)

#### Final Validation
```bash
# Full test suite
pytest tests/ -v --cov

# Linting
ruff check .
mypy .

# Build verification
[build commands]
```

---

## Technical Design

### Data Models

```python
# Key data structures
class FeatureModel:
    """
    [Description]
    """
    field1: type
    field2: type
```

### Architecture

```
[Component diagram or description]

Component A --> Component B --> Component C
     |              |
     v              v
  Database      External API
```

### Key Files

| File | Purpose | Status |
|------|---------|--------|
| src/feature/main.py | Core logic | New |
| src/feature/models.py | Data models | New |
| tests/test_feature.py | Unit tests | New |

---

## Codebase Context

### Patterns to Follow
- **Pattern 1:** [file reference] - [what to follow]
- **Pattern 2:** [file reference] - [what to follow]

### Integration Points
- **[System 1]:** [How to integrate]
- **[System 2]:** [How to integrate]

---

## Risk Mitigation

| Risk | Impact | Mitigation |
|------|--------|------------|
| [Risk 1] | High | [Strategy] |
| [Risk 2] | Medium | [Strategy] |

---

## Validation Checklist

### Pre-Implementation
- [ ] PRD requirements understood
- [ ] Technical approach validated
- [ ] Dependencies available

### During Implementation
- [ ] Each phase validation passes
- [ ] Code follows project conventions
- [ ] Tests written alongside code

### Post-Implementation
- [ ] All P0 requirements complete
- [ ] All tests passing
- [ ] Documentation complete
- [ ] Code reviewed
- [ ] Ready for deployment

---

## Archon Tasks

Tasks to be created in Archon for tracking:

1. **[Feature] - Phase 1: Foundation**
   - Description: Set up foundation for [feature]
   - Estimated: [X hours]

2. **[Feature] - Phase 2: Core Implementation**
   - Description: Implement core functionality
   - Estimated: [X hours]

3. **[Feature] - Phase 3: Integration**
   - Description: Integrate with existing systems
   - Estimated: [X hours]

4. **[Feature] - Phase 4: Testing & Docs**
   - Description: Complete testing and documentation
   - Estimated: [X hours]

---

## Success Criteria

From PRD, implementation is successful when:
- [ ] [Metric 1 from PRD]
- [ ] [Metric 2 from PRD]
- [ ] [Metric 3 from PRD]
```

### Step 5: Create Archon Tasks

Create tasks for each phase:

```python
# Read project ID from config

# Phase 1
manage_task(
    "create",
    project_id="[archon_project_id]",
    title="[Feature] - Phase 1: Foundation",
    description="Set up foundation for [feature]. See PRPs/plans/[feature-name]-plan.md",
    feature="[feature-name]",
    task_order=100
)

# Phase 2
manage_task(
    "create",
    project_id="[archon_project_id]",
    title="[Feature] - Phase 2: Core Implementation",
    description="Implement core functionality for [feature]",
    feature="[feature-name]",
    task_order=90
)

# Continue for other phases...
```

### Step 6: Output Summary

```
IMPLEMENTATION PLAN CREATED
===========================

Feature:     [Feature Name]
PRD:         PRPs/prds/[feature-name]-prd.md
Plan:        PRPs/plans/[feature-name]-plan.md
Phases:      4
Total Tasks: [X]
Estimate:    [X days]

PHASES
------
1. Foundation      - [X tasks] - [X hours]
2. Core           - [X tasks] - [X hours]
3. Integration    - [X tasks] - [X hours]
4. Testing & Docs - [X tasks] - [X hours]

ARCHON TASKS CREATED
--------------------
[List of created tasks with IDs]

NEXT STEPS
----------
1. Review the implementation plan
2. Adjust estimates if needed
3. Run /prp-implement to begin implementation
4. Or manually start with: /start

The plan breaks down the PRD into actionable phases with clear validation gates.
```

## Quality Checklist

Before finalizing:
- [ ] All P0 requirements have corresponding tasks
- [ ] Each phase has clear validation criteria
- [ ] Dependencies are identified and ordered correctly
- [ ] Risk mitigation strategies are defined
- [ ] Success criteria match PRD metrics
