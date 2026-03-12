---
name: review
description: Perform comprehensive code review on changes or specified files
---

# /review - Code Review

Perform a comprehensive code review of the current changes or specified files.

## Process

### 1. Understand Changes

```bash
# If reviewing staged changes
git diff --staged

# If reviewing all changes
git diff HEAD

# If reviewing specific files
# Read the specified files
```

### 2. Review Checklist

#### Code Quality
- [ ] Clear naming conventions
- [ ] Functions are small and focused
- [ ] No magic numbers/strings (use constants)
- [ ] Proper error handling
- [ ] Type annotations where applicable
- [ ] Appropriate comments for complex logic

#### Architecture
- [ ] Single Responsibility Principle
- [ ] Proper separation of concerns
- [ ] No circular dependencies
- [ ] Consistent patterns with codebase

#### Security
- [ ] Input validation on all user input
- [ ] No SQL injection vulnerabilities
- [ ] No hardcoded secrets
- [ ] Proper authentication/authorization

#### Testing
- [ ] New code has tests
- [ ] Edge cases covered
- [ ] Tests are meaningful (not just for coverage)

#### Performance
- [ ] No N+1 queries
- [ ] Efficient algorithms
- [ ] Proper async usage

#### Documentation
- [ ] Public APIs documented
- [ ] README updated if needed
- [ ] Breaking changes documented

## Output Format

```markdown
# Code Review

## Summary

[2-3 sentence overview]

## Issues Found

### Critical (Must Fix)

| File:Line | Issue | Suggested Fix |
|-----------|-------|---------------|
| `file.ts:42` | [Issue] | [Fix] |

### Important (Should Fix)

| File:Line | Issue | Suggested Fix |
|-----------|-------|---------------|
| `file.ts:85` | [Issue] | [Fix] |

### Minor (Consider)

- [Improvement suggestions]

## Good Practices Observed

- [What was done well]

## Test Coverage

- Current: [X%]
- Missing tests: [list]

## Recommendation

[ ] Ready to merge
[ ] Needs changes (see above)
[ ] Needs discussion
```

## Arguments

$ARGUMENTS

- No args: Review staged changes or current branch changes
- `<file>`: Review specific file
- `all`: Review all uncommitted changes
