---
name: sync
description: Sync with remote repository
---

Synchronize local repository with remote - push, pull, or fetch.

## Arguments

$ARGUMENTS

Parse arguments to determine the action:
- No args: Smart sync (fetch, show status, suggest action)
- "push": Push current branch to remote
- "pull": Pull current branch from remote
- "fetch": Fetch all remotes without merging
- "force" or "push force": Force push (with safety checks)

## Smart Sync (Default)

When no arguments provided:

1. Fetch from all remotes
```bash
git fetch --all --prune
```

2. Check current branch status
```bash
git status -sb
```

3. Show ahead/behind count
```bash
git rev-list --left-right --count HEAD...@{upstream}
```

4. Recommend action based on status:
   - Behind only: Suggest pull
   - Ahead only: Suggest push
   - Diverged: Suggest pull --rebase or merge strategy
   - Up to date: Report clean state

## Push

```bash
# Normal push
git push origin <current-branch>

# Push and set upstream (for new branches)
git push -u origin <current-branch>
```

If push is rejected, explain why and suggest:
- Pull first if behind
- Force push if intentional (with warnings)

## Pull

```bash
# Standard pull (fetch + merge)
git pull origin <current-branch>

# Pull with rebase (cleaner history)
git pull --rebase origin <current-branch>
```

If conflicts occur:
1. List conflicted files
2. Explain resolution options
3. Offer to help resolve

## Force Push

**DANGEROUS** - Only use when:
- Rebased local commits
- Amending pushed commits
- Cleaning up PR branch

```bash
# Safer force push (fails if remote has new commits)
git push --force-with-lease origin <current-branch>
```

**NEVER force push to main/master without explicit confirmation**

## Fetch

```bash
# Fetch all remotes and prune deleted branches
git fetch --all --prune

# Show what was fetched
git log --oneline HEAD..@{upstream}
```

## Output

Show:
1. Current branch and tracking branch
2. Commits ahead/behind
3. Action taken and result
4. Any warnings about diverged branches or conflicts
