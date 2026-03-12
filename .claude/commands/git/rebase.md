---
name: rebase
description: Rebase git branches
---

Rebase commits onto another branch or rewrite history.

## Arguments

$ARGUMENTS

Parse arguments:
- "<branch>": Rebase current branch onto specified branch
- "interactive" or "-i": Interactive rebase for editing commits
- "abort": Abort in-progress rebase
- "continue": Continue after resolving conflicts
- "skip": Skip current commit during rebase
- "onto <new-base> <old-base>": Advanced rebase onto different base

## Warning

**Rebase rewrites history!**
- NEVER rebase commits that have been pushed and shared
- Safe for: local commits, personal feature branches before PR
- Unsafe for: main/master, shared branches, after push

## Standard Rebase

```bash
# Rebase current branch onto main
git rebase main
```

This replays your commits on top of main, creating new commits with new hashes.

**Before:**
```
      A---B---C  (feature)
     /
D---E---F---G  (main)
```

**After:**
```
              A'--B'--C'  (feature)
             /
D---E---F---G  (main)
```

## Interactive Rebase

```bash
# Rebase last n commits
git rebase -i HEAD~<n>

# Rebase onto branch interactively
git rebase -i main
```

### Interactive Commands

In the editor, each commit can be:
- `pick` (p): Keep commit as-is
- `reword` (r): Keep commit, edit message
- `edit` (e): Pause to amend commit
- `squash` (s): Combine with previous commit
- `fixup` (f): Combine with previous, discard message
- `drop` (d): Remove commit entirely
- `reorder`: Change line order to reorder commits

### Common Interactive Tasks

**Squash multiple commits:**
```
pick abc123 First commit
squash def456 Second commit
squash ghi789 Third commit
```

**Reorder commits:**
Move lines to change commit order.

**Edit a commit:**
```
edit abc123 Commit to modify
```
Then: make changes, `git add`, `git commit --amend`, `git rebase --continue`

## Handling Conflicts

During rebase, if conflicts occur:

1. Resolve conflicts in the files
2. Stage resolved files:
   ```bash
   git add <files>
   ```
3. Continue rebase:
   ```bash
   git rebase --continue
   ```

Or abort entirely:
```bash
git rebase --abort
```

Or skip the problematic commit:
```bash
git rebase --skip
```

## Advanced: Rebase Onto

```bash
git rebase --onto <new-base> <old-base> <branch>
```

Example: Move commits from feature that were based on old-branch to main:
```bash
git rebase --onto main old-branch feature
```

## Rebase vs Merge

**Use Rebase when:**
- Cleaning up local commits before PR
- Keeping feature branch updated with main
- You want linear history

**Use Merge when:**
- Integrating completed features
- Working on shared branches
- You want to preserve branch history

## Safety Measures

Before rebasing:
1. Check if branch has been pushed:
   ```bash
   git log origin/<branch>..<branch>
   ```
2. Create backup branch:
   ```bash
   git branch backup-<branch>
   ```

## Output

Show:
1. Rebase progress and result
2. New commit structure (abbreviated)
3. Conflicts if any, with resolution guidance
4. Warning if rebasing pushed commits
