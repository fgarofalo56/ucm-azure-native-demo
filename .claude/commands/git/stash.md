---
name: stash
description: Manage git stashes
---

Manage git stash - save, apply, list, or drop stashed changes.

## Arguments

$ARGUMENTS

Parse arguments to determine the action:
- No args or "save": Stash current changes
- "save <message>": Stash with descriptive message
- "list": List all stashes
- "show" or "show <n>": Show stash contents
- "apply" or "apply <n>": Apply stash (keep in list)
- "pop" or "pop <n>": Apply and remove stash
- "drop <n>": Delete a stash
- "clear": Delete ALL stashes (with confirmation)

## Actions

### Save/Push (Default)
```bash
# Stash tracked files
git stash push -m "<message>"

# Include untracked files
git stash push -u -m "<message>"

# Include ignored files too
git stash push -a -m "<message>"
```

Auto-generate descriptive message if not provided:
`WIP on <branch>: <last-commit-subject>`

### List Stashes
```bash
git stash list --format="%gd: %s (%cr)"
```
Shows stash index, message, and relative time.

### Show Stash Contents
```bash
# Show diff summary
git stash show stash@{n}

# Show full diff
git stash show -p stash@{n}

# Show file list
git stash show --stat stash@{n}
```

### Apply Stash
```bash
# Apply most recent
git stash apply

# Apply specific stash
git stash apply stash@{n}
```
Keeps the stash in the list for potential reuse.

### Pop Stash
```bash
# Pop most recent
git stash pop

# Pop specific stash
git stash pop stash@{n}
```
Removes the stash after successful apply.

### Drop Stash
```bash
git stash drop stash@{n}
```
Ask for confirmation before dropping.

### Clear All Stashes
```bash
git stash clear
```
**DANGEROUS** - Require explicit confirmation. Show count of stashes that will be deleted.

## Handling Conflicts

If apply/pop causes conflicts:
1. List conflicted files
2. Explain that stash is NOT dropped on conflict (even with pop)
3. Guide through resolution:
   ```bash
   # After resolving conflicts
   git add <resolved-files>
   git stash drop  # if was using pop
   ```

## Output

Show:
1. Action taken
2. Current stash list (abbreviated)
3. Branch context
4. Any conflict warnings
