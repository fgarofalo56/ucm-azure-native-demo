---
name: prp-prd
description: Create a new Product Requirements Document using the PRP framework
---

# /prp-prd - Create Product Requirements Document

Create a comprehensive PRD (Product Requirements Document) using the PRP (Product Requirements Planning) framework.

## Arguments

`$ARGUMENTS` - Feature name or brief description (optional, will prompt if not provided)

## Steps to Execute

### Step 1: Gather Feature Information

If `$ARGUMENTS` is not provided, ask the user:

```
PRP - PRODUCT REQUIREMENTS DOCUMENT
===================================

What feature would you like to document?

Please provide:
1. Feature Name: [short identifier]
2. Feature Description: [what it does in 1-2 sentences]
3. Target Users: [who will use this]
4. Business Value: [why this matters]
```

### Step 2: Research Phase

Execute parallel research to gather comprehensive context:

#### 2a. Codebase Analysis
```
Search the codebase for:
- Similar features or patterns already implemented
- Relevant files and modules
- Existing conventions and architectural patterns
- Related tests and validation approaches
```

#### 2b. External Research
```
Search for:
- Best practices for this type of feature
- Common implementation patterns
- Potential pitfalls and solutions
- Security considerations
```

#### 2c. Documentation Review
```
Check existing project documentation:
- PRPs/prds/ for related PRDs
- Architecture documents in Archon
- README and setup documentation
```

### Step 3: Generate PRD

Create the PRD file at `PRPs/prds/[feature-name]-prd.md`:

```markdown
# PRD: [Feature Name]

**Created:** [Date]
**Author:** [User/Claude Code]
**Status:** Draft
**Version:** 1.0

---

## Executive Summary

[2-3 sentence summary of the feature and its value]

---

## 1. Goal

### Primary Objective
[Specific, measurable outcome this feature achieves]

### Success Metrics
- [ ] [Metric 1 with target]
- [ ] [Metric 2 with target]
- [ ] [Metric 3 with target]

---

## 2. Why

### Business Value
[Why this feature matters to the business]

### User Value
[How this improves the user experience]

### Technical Value
[Any technical debt reduction, performance improvements, etc.]

### Problems Solved
- [Problem 1]: [How it's solved]
- [Problem 2]: [How it's solved]

### Risks of Not Implementing
- [Risk 1]
- [Risk 2]

---

## 3. What

### User-Visible Behavior

**Before:**
[Current state/behavior]

**After:**
[Desired state/behavior with this feature]

### Functional Requirements

#### Must Have (P0)
- [ ] [Requirement 1]
- [ ] [Requirement 2]

#### Should Have (P1)
- [ ] [Requirement 1]
- [ ] [Requirement 2]

#### Nice to Have (P2)
- [ ] [Requirement 1]

### Non-Functional Requirements
- Performance: [targets]
- Security: [requirements]
- Scalability: [requirements]
- Accessibility: [requirements]

---

## 4. Context

### Related Documentation
- url: [External documentation URLs]
- file: [Relevant codebase files]
- docfile: [Related PRDs or docs]

### Codebase Context
[Relevant existing code, patterns, and files]

### Dependencies
- Internal: [Internal systems/services]
- External: [Third-party services/libraries]

### Constraints
- Technical: [Technical limitations]
- Business: [Business constraints]
- Timeline: [Time constraints]

---

## 5. User Stories

### Primary User: [User Type]

**Story 1:**
As a [user type], I want to [action] so that [benefit].

**Acceptance Criteria:**
- [ ] [Criterion 1]
- [ ] [Criterion 2]

**Story 2:**
[Additional stories as needed]

---

## 6. Technical Considerations

### Architecture Impact
[How this affects system architecture]

### Data Model Changes
[New or modified data structures]

### API Changes
[New or modified APIs]

### Integration Points
[Systems this feature integrates with]

### Security Considerations
[Security implications and mitigations]

---

## 7. Out of Scope

Explicitly NOT included in this feature:
- [Item 1]
- [Item 2]

---

## 8. Open Questions

Questions requiring answers before implementation:
1. [Question 1]
2. [Question 2]

---

## 9. Timeline Estimate

| Phase | Duration | Description |
|-------|----------|-------------|
| Planning | [X days] | Finalize requirements, create implementation plan |
| Implementation | [X days] | Core development work |
| Testing | [X days] | QA, bug fixes |
| Documentation | [X days] | User docs, technical docs |
| Deployment | [X days] | Staging, production release |

**Total Estimate:** [X days/weeks]

---

## 10. Approval

| Role | Name | Status | Date |
|------|------|--------|------|
| Product Owner | | Pending | |
| Tech Lead | | Pending | |
| Security | | Pending | |

---

## Appendix

### Research Notes
[Findings from the research phase]

### Mockups/Diagrams
[Links or embedded diagrams]

### References
[External references and resources]
```

### Step 4: Create Archon Task

Create a task in Archon for the PRD review:

```python
manage_task(
    "create",
    project_id="[archon_project_id]",
    title=f"Review PRD: [Feature Name]",
    description="Review and approve the PRD for [Feature Name]. Located at PRPs/prds/[feature-name]-prd.md",
    feature="documentation",
    status="review"
)
```

### Step 5: Output Summary

```
PRD CREATED
===========

Feature:  [Feature Name]
File:     PRPs/prds/[feature-name]-prd.md
Status:   Draft

NEXT STEPS
----------
1. Review the generated PRD
2. Fill in any [PLACEHOLDER] sections
3. Answer open questions
4. Get stakeholder approval
5. Run /prp-plan to create implementation plan

Created Archon task for PRD review.
```

## Quality Checklist

Before finalizing, verify:
- [ ] Goal is specific and measurable
- [ ] User value is clearly articulated
- [ ] Requirements are prioritized (P0/P1/P2)
- [ ] Technical considerations are documented
- [ ] Out of scope is explicitly defined
- [ ] Open questions are captured
