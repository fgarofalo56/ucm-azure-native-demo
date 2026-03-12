---
name: undo
description: Undo git operations safely
---

Undo git operations - reset commits, revert changes, or restore files.

## Arguments

$ARGUMENTS

Parse arguments to determine the action:
- No args: Show undo options based on current state
- "unstage" or "unstage <file>": Unstage files
- "discard" or "discard <file>": Discard working directory changes
- "commit" or "commit <n>": Undo last n commits (default 1)
- "amend": Modify the last commit
- "revert <commit>": Create a new commit that undoes a specific commit
- "reflog": Show reflog for recovery options

## Safety First

Before any destructive operation:
1. Check for uncommitted changes
2. Warn about data loss potential
3. Suggest backup if needed (stash or branch)

## Actions

### Unstage Files
```bash
# Unstage specific file
git restore --staged <file>

# Unstage all files
git restore --staged .

# Legacy (still works)
git reset HEAD <file>
```
Safe operation - only affects staging area.

### Discard Working Directory Changes
```bash
# Discard changes in specific file
git restore <file>

# Discard all changes
git restore .

# Legacy
git checkout -- <file>
```
**WARNING**: Permanently loses uncommitted changes.

### Undo Commits

**Keep changes in working directory (soft):**
```bash
git reset --soft HEAD~<n>
```
Use when: You want to re-commit differently.

**Keep changes staged (mixed - default):**
```bash
git reset HEAD~<n>
```
Use when: You want to review and selectively re-stage.

**Discard changes completely (hard):**
```bash
git reset --hard HEAD~<n>
```
**DANGEROUS**: Permanently loses commit AND changes.

### Amend Last Commit
```bash
# Change message only
git commit --amend -m "new message"

# Add more changes to last commit
git add <files>
git commit --amend --no-edit
```
**WARNING**: Don't amend pushed commits (rewrites history).

### Revert (Safe for Pushed Commits)
```bash
# Revert a specific commit
git revert <commit-hash>

# Revert without auto-commit (to edit or combine)
git revert --no-commit <commit-hash>

# Revert a merge commit
git revert -m 1 <merge-commit-hash>
```
Creates a NEW commit that undoes changes. Safe for shared branches.

### Recovery with Reflog
```bash
# Show reflog
git reflog

# Recover to a previous state
git reset --hard HEAD@{n}
```
Git keeps commits for ~30 days even after reset.

## Decision Tree

Ask clarifying questions if action is ambiguous:
1. "Are these changes pushed to remote?"
   - Yes → Use revert (safe)
   - No → Can use reset
2. "Do you want to keep the changes?"
   - Yes → soft/mixed reset
   - No → hard reset
3. "Which commits to undo?"
   - Show recent commits to help identify

## Output

Show:
1. What was undone
2. Current state (git status summary)
3. How to recover if needed (reflog reference)
4. Warnings about pushed commits if applicable
