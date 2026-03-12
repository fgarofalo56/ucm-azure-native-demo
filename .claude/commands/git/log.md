---
name: log
description: Show git log
---

View git history with various formats and filters.

## Arguments

$ARGUMENTS

Parse arguments to determine the view:
- No args: Show recent commits (default 10)
- "<n>": Show last n commits
- "all": Show all commits (paginated)
- "graph": Show branch graph
- "oneline": Compact one-line format
- "file <path>": History of specific file
- "author <name>": Commits by author
- "since <date>": Commits since date
- "search <term>": Search commit messages
- "between <ref1> <ref2>": Commits between two refs

## Views

### Default View (Pretty)
```bash
git log -n 10 --pretty=format:"%C(yellow)%h%C(reset) %C(blue)%ad%C(reset) %C(green)%an%C(reset)%C(red)%d%C(reset)%n%s%n" --date=short
```

### One-Line Compact
```bash
git log --oneline -n 20
```

### Graph View
```bash
git log --graph --oneline --all --decorate -n 30
```
Shows branch structure visually.

### Detailed View
```bash
git log -n 5 --stat
```
Includes file change statistics.

### Full Diff View
```bash
git log -n 3 -p
```
Shows actual code changes.

## Filters

### By File
```bash
git log --follow -- <file-path>
```
`--follow` tracks file through renames.

### By Author
```bash
git log --author="<name>" -n 10
```

### By Date
```bash
# Since a date
git log --since="2024-01-01" -n 20

# Date range
git log --since="2024-01-01" --until="2024-06-30"

# Relative
git log --since="2 weeks ago"
```

### By Message Content
```bash
git log --grep="<search-term>" -i -n 10
```
`-i` for case-insensitive.

### By Code Content
```bash
git log -S "<code-string>" -n 10
```
Finds commits that added/removed the string.

### Between Refs
```bash
# Commits in feature not in main
git log main..feature

# Commits in either but not both
git log main...feature
```

## Output Formats

### For Review
```
<hash> <date> <author>
  <subject>

  Files: <changed-file-count>
```

### For Release Notes
```bash
git log --pretty=format:"- %s (%h)" v1.0.0..HEAD
```

### For Statistics
```bash
git shortlog -sn --since="1 month ago"
```
Shows commit count by author.

## Output

Display the requested log view. If output is long:
1. Show first portion
2. Indicate total count
3. Offer to show more or export to file
