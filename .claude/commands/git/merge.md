---
name: merge
description: Merge git branches
---

Merge branches together.

## Arguments

$ARGUMENTS

Parse arguments:
- "<branch>": Merge specified branch into current
- "abort": Abort in-progress merge
- "continue": Continue after resolving conflicts
- "squash <branch>": Squash merge (combine all commits)
- "no-ff <branch>": Force merge commit even if fast-forward possible

## Pre-Merge Checks

Before merging:
1. Check for uncommitted changes
```bash
git status
```
2. Ensure current branch is up to date
```bash
git fetch origin
git status -sb
```
3. Show what will be merged
```bash
git log --oneline HEAD..<branch>
```

## Merge Strategies

### Standard Merge
```bash
git merge <branch>
```
- Fast-forward if possible (linear history)
- Creates merge commit if branches diverged

### No Fast-Forward
```bash
git merge --no-ff <branch>
```
Always creates merge commit. Useful for:
- Preserving feature branch history
- Clear indication of where feature was integrated

### Squash Merge
```bash
git merge --squash <branch>
git commit -m "feat: <description of all changes>"
```
Combines all commits into one. Useful for:
- Clean main branch history
- Feature branches with messy commits

### Fast-Forward Only
```bash
git merge --ff-only <branch>
```
Fails if fast-forward not possible. Ensures linear history.

## Handling Conflicts

If conflicts occur:

1. Show conflicted files
```bash
git status
# or
git diff --name-only --diff-filter=U
```

2. For each conflict:
   - Show the conflict markers
   - Explain the ours/theirs sections
   - Suggest resolution approach

3. After resolving:
```bash
git add <resolved-files>
git merge --continue
# or
git commit
```

### Conflict Resolution Tools
```bash
# Use configured merge tool
git mergetool

# Accept one side entirely
git checkout --ours <file>
git checkout --theirs <file>
```

## Abort Merge
```bash
git merge --abort
```
Returns to pre-merge state. Safe operation.

## Best Practices

1. **Before merging into main/master:**
   - Ensure CI passes on feature branch
   - Get code review approval
   - Update feature branch from main first

2. **Update feature branch first:**
   ```bash
   git checkout feature
   git merge main  # or rebase
   # Resolve any conflicts here
   git checkout main
   git merge feature  # Should be clean now
   ```

3. **Commit message for merge:**
   ```
   Merge branch 'feat/user-auth' into main

   - Adds JWT authentication
   - Implements login/logout endpoints
   - Includes unit tests
   ```

## Output

Show:
1. Merge result (fast-forward, merge commit, or conflicts)
2. Files changed summary
3. If conflicts, list them with guidance
4. New commit hash if successful
