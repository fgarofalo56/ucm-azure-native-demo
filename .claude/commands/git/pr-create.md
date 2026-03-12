---
name: pr-create
description: Create GitHub pull requests
---

Create a GitHub Pull Request using the gh CLI.

## Prerequisites

Ensure gh CLI is authenticated:
```bash
gh auth status
```

## Arguments

$ARGUMENTS

Parse arguments:
- No args: Interactive PR creation
- "draft": Create as draft PR
- "ready": Create as ready for review
- "<title>": Use as PR title

## Process

### 1. Pre-flight Checks

```bash
# Ensure we're not on main/master
git branch --show-current

# Check for uncommitted changes
git status

# Ensure branch is pushed
git push -u origin HEAD
```

### 2. Gather PR Information

```bash
# Get commits since branching from main
git log --oneline main..HEAD

# Get changed files
git diff --stat main..HEAD
```

### 3. Generate PR Content

**Title:** Use Conventional Commits style
- `feat: Add user authentication`
- `fix: Resolve login timeout issue`
- `docs: Update API documentation`

**Body Template:**
```markdown
## Summary
[Brief description of changes - 2-3 sentences]

## Changes
- [Key change 1]
- [Key change 2]
- [Key change 3]

## Test Plan
- [ ] [How to test this]
- [ ] [Verification step]

## Related Issues
Closes #[issue-number]
```

### 4. Create the PR

```bash
# Standard PR
gh pr create --title "<title>" --body "<body>"

# Draft PR
gh pr create --title "<title>" --body "<body>" --draft

# With reviewers
gh pr create --title "<title>" --body "<body>" --reviewer @user1,@user2

# With labels
gh pr create --title "<title>" --body "<body>" --label "enhancement"

# Against specific base branch
gh pr create --title "<title>" --body "<body>" --base develop
```

### 5. Add Metadata (Optional)

```bash
# Add reviewers after creation
gh pr edit <number> --add-reviewer @user

# Add labels
gh pr edit <number> --add-label "needs-review"

# Add to project
gh pr edit <number> --add-project "Sprint 1"
```

## PR Best Practices

1. **Keep PRs focused** - One feature/fix per PR
2. **Small is better** - Easier to review, faster to merge
3. **Self-review first** - Check your own diff before requesting review
4. **Update description** - Keep it current if changes are made

## Common Options

| Flag | Purpose |
|------|---------|
| `--draft` | Create as draft |
| `--base <branch>` | Target branch (default: main) |
| `--head <branch>` | Source branch (default: current) |
| `--reviewer <users>` | Request reviewers |
| `--assignee <users>` | Assign users |
| `--label <labels>` | Add labels |
| `--milestone <name>` | Add to milestone |
| `--project <name>` | Add to project |

## Output

After creating PR:
1. Show PR URL
2. Show PR number
3. List reviewers requested
4. Show CI status check URL
