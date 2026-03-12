---
name: diff
description: Show git diff summary
---

View differences between commits, branches, or working directory.

## Arguments

$ARGUMENTS

Parse arguments to determine what to diff:
- No args: Show unstaged changes
- "staged": Show staged changes
- "all": Show both staged and unstaged
- "commit <hash>": Diff against specific commit
- "branch <name>": Diff against branch
- "<ref1> <ref2>": Diff between two refs
- "file <path>": Diff specific file
- "stat": Show only statistics

## Views

### Unstaged Changes (Default)
```bash
git diff
```
Shows changes in working directory not yet staged.

### Staged Changes
```bash
git diff --staged
# or
git diff --cached
```
Shows what will be committed.

### All Changes (Staged + Unstaged)
```bash
git diff HEAD
```
Shows all changes since last commit.

### Between Commits
```bash
# Specific commits
git diff <commit1> <commit2>

# Last n commits
git diff HEAD~<n> HEAD
```

### Between Branches
```bash
# What's in feature that's not in main
git diff main..feature

# What's different between branches
git diff main...feature
```

### Specific File
```bash
git diff -- <file-path>
git diff --staged -- <file-path>
git diff <commit> -- <file-path>
```

## Output Formats

### Statistics Only
```bash
git diff --stat
```
Shows files changed and lines added/removed.

### Name Only
```bash
git diff --name-only
```
Just the file paths.

### Name with Status
```bash
git diff --name-status
```
Shows A (added), M (modified), D (deleted), R (renamed).

### Word Diff
```bash
git diff --word-diff
```
Highlights word-level changes instead of lines.

### Compact Summary
```bash
git diff --compact-summary
```
One line per file with change indicators.

## Advanced Options

### Ignore Whitespace
```bash
git diff -w  # Ignore all whitespace
git diff -b  # Ignore whitespace changes
git diff --ignore-blank-lines
```

### Context Lines
```bash
git diff -U5  # Show 5 lines of context (default 3)
```

### Binary Files
```bash
git diff --binary  # Include binary diff
```

### Color Options
```bash
git diff --color-words  # Color at word level
```

## Interpreting Diff Output

Explain the diff format:
- Lines starting with `-` are removed (red)
- Lines starting with `+` are added (green)
- Lines starting with `@@` show location (hunk header)
- Context lines have no prefix

## Output

1. Show the diff with syntax highlighting
2. Summarize: X files changed, Y insertions, Z deletions
3. For large diffs, offer to show specific files or summary only
