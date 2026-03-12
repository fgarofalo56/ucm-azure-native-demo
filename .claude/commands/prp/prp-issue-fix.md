---
name: prp-issue-fix
description: Execute fix from investigation with validation
---

# PRP Issue Fix

**Issue Number**: $ARGUMENTS

---

## Your Mission

Execute the fix based on investigation findings with rigorous validation.

**Core Principle**: Follow the investigation, validate thoroughly, don't introduce new issues.

---

## Phase 1: LOAD - Review Investigation

### 1.1 Find Investigation Results

Check for previous investigation of this issue:
- Review conversation history
- Check Archon documents
- Check PRPs/issues/ directory if exists

If no investigation found:
```
Error: No investigation found for issue #{number}

Run: /prp-issue-investigate {number}
```

### 1.2 Extract Fix Details

From the investigation, extract:
- Root cause location
- Solution design
- Files to change
- Implementation steps
- Testing strategy

---

## Phase 2: PREPARE - Setup Branch

### 2.1 Create Fix Branch

```bash
git checkout main
git pull origin main
git checkout -b fix/issue-{number}-{short-description}
```

### 2.2 Verify Clean State

```bash
git status --porcelain
```

Must be clean before starting.

---

## Phase 3: IMPLEMENT - Execute Fix

### 3.1 Follow Investigation Steps

Execute each implementation step from the investigation:

1. Read the current problematic code
2. Apply the corrected code from the fix design
3. Validate immediately after each change

### 3.2 Validate Each Change

After each file modification:

**.NET/C#:**
```bash
dotnet build
```

**Python:**
```bash
ruff check {file} && mypy {file}
```

**TypeScript/React:**
```bash
npm run type-check
```

### 3.3 Track Progress

```
Step 1: Update {file} [done]
Step 2: Add {file} [done]
Step 3: Update {tests} [done]
```

---

## Phase 4: TEST - Verify Fix

### 4.1 Reproduction Test

Run the reproduction steps from the investigation.

**Before Fix**: Issue should be reproducible
**After Fix**: Issue should be resolved

### 4.2 Regression Tests

Run existing test suite:

**.NET/C#:**
```bash
dotnet test
```

**Python:**
```bash
pytest -v
```

**TypeScript/React:**
```bash
npm test
```

**All tests must pass.**

### 4.3 Add New Test (if needed)

If the investigation identified a missing test:
1. Create the test
2. Verify it catches the original bug
3. Verify it passes with the fix

---

## Phase 5: COMMIT - Prepare for PR

### 5.1 Stage Changes

```bash
git add -A
```

### 5.2 Create Commit

```bash
git commit -m "fix: {short description} (fixes #{number})

- Root cause: {brief explanation}
- Solution: {what was changed}
- Tests: {added/updated}"
```

### 5.3 Push Branch

```bash
git push -u origin fix/issue-{number}-{description}
```

---

## Phase 6: OUTPUT - Report

```markdown
## Fix Complete

**Issue**: #{number}
**Branch**: `fix/issue-{number}-{description}`
**Status**: Ready for PR

### Summary

{One sentence describing the fix}

### Changes

| File | Change |
|------|--------|
| `{path}` | {description} |

### Validation

| Check | Result |
|-------|--------|
| Build | Pass |
| Tests | Pass ({N} tests) |
| Reproduction | Fixed |

### Next Steps

1. Create PR: `/pr-create`
2. Link to issue #{number}
3. Request review
4. Merge when approved
```

---

## Handling Issues

### Build Fails

1. Check error message
2. Fix the issue
3. Re-run build
4. Don't proceed until clean

### Tests Fail

1. Check if related to fix or pre-existing
2. If related to fix, review the change
3. If pre-existing, document but don't fix (out of scope)
4. Ensure fix doesn't introduce new failures

### Fix Doesn't Work

1. Review investigation analysis
2. Check if root cause was correct
3. If not, re-run investigation
4. If yes, refine the solution approach

---

## Success Criteria

- **INVESTIGATION_FOLLOWED**: Fix matches the documented solution
- **BUILD_PASSES**: No compilation errors
- **TESTS_PASS**: All tests green (including new ones)
- **ISSUE_RESOLVED**: Original problem no longer reproducible
- **NO_REGRESSIONS**: Existing functionality preserved
- **BRANCH_PUSHED**: Ready for PR
