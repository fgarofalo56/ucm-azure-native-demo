---
name: branch
description: Create or switch git branches
---

Manage git branches - create, switch, delete, or list branches.

## Arguments

$ARGUMENTS

Parse arguments to determine the action:
- No args or "list": List all branches
- "create <name>": Create and switch to new branch
- "switch <name>" or "checkout <name>": Switch to existing branch
- "delete <name>": Delete a branch
- "rename <old> <new>": Rename a branch
- "clean" or "cleanup": Delete merged branches

## Actions

### List Branches
```bash
git branch -a --sort=-committerdate
```
Show local and remote branches sorted by recent activity.

### Create Branch
```bash
git checkout -b <branch-name>
```
Create from current HEAD. If user specifies a base branch:
```bash
git checkout -b <branch-name> <base-branch>
```

### Branch Naming Convention
Suggest names following pattern:
- `feat/<description>` - New features
- `fix/<description>` - Bug fixes
- `docs/<description>` - Documentation
- `refactor/<description>` - Refactoring
- `test/<description>` - Test additions
- `chore/<description>` - Maintenance

Example: `feat/add-user-authentication`

### Switch Branch
```bash
git checkout <branch-name>
# or
git switch <branch-name>
```
If there are uncommitted changes, warn the user and suggest stashing.

### Delete Branch
```bash
# Local branch (safe - only if merged)
git branch -d <branch-name>

# Force delete (even if not merged)
git branch -D <branch-name>

# Remote branch
git push origin --delete <branch-name>
```
Ask for confirmation before force delete or remote delete.

### Cleanup Merged Branches
```bash
# List merged branches (excluding main/master/develop)
git branch --merged | grep -v "main\|master\|develop"

# Delete them
git branch --merged | grep -v "main\|master\|develop" | xargs git branch -d
```

## Output

After any action, show:
1. Current branch
2. Recent branches (if listing)
3. Any warnings about uncommitted changes
