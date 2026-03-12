---
name: issue-create
description: Create GitHub issues
---

Create a GitHub Issue using the gh CLI.

## Arguments

$ARGUMENTS

Parse arguments:
- No args: Interactive issue creation
- "bug": Create bug report
- "feature": Create feature request
- "list": List open issues
- "<title>": Create with specified title

## Process

### 1. Check for Templates

```bash
# Check if repo has issue templates
ls .github/ISSUE_TEMPLATE/ 2>/dev/null
```

If templates exist, offer to use them.

### 2. Create Issue

```bash
# Interactive mode (uses templates if available)
gh issue create

# With title and body
gh issue create --title "<title>" --body "<body>"

# With labels
gh issue create --title "<title>" --body "<body>" --label "bug,priority:high"

# Assign to user
gh issue create --title "<title>" --body "<body>" --assignee @username

# Add to project
gh issue create --title "<title>" --body "<body>" --project "Backlog"
```

## Issue Templates

### Bug Report
```markdown
---
title: "bug: [Brief description]"
labels: bug
---

## Description
[Clear description of the bug]

## Steps to Reproduce
1. [Step 1]
2. [Step 2]
3. [Step 3]

## Expected Behavior
[What should happen]

## Actual Behavior
[What actually happens]

## Environment
- OS: [e.g., Windows 11, macOS 14]
- Version: [e.g., v1.2.3]
- Browser (if applicable): [e.g., Chrome 120]

## Screenshots
[If applicable]

## Additional Context
[Any other relevant information]
```

### Feature Request
```markdown
---
title: "feat: [Brief description]"
labels: enhancement
---

## Summary
[Brief description of the feature]

## Motivation
[Why is this needed? What problem does it solve?]

## Proposed Solution
[How do you envision this working?]

## Alternatives Considered
[Other approaches you've thought about]

## Additional Context
[Mockups, examples, or references]
```

### Task/Chore
```markdown
---
title: "chore: [Brief description]"
labels: chore
---

## Description
[What needs to be done]

## Acceptance Criteria
- [ ] [Criterion 1]
- [ ] [Criterion 2]
- [ ] [Criterion 3]

## Notes
[Any additional context]
```

## Managing Issues

### List Issues
```bash
# All open issues
gh issue list

# Filter by label
gh issue list --label "bug"

# Filter by assignee
gh issue list --assignee @me

# Search issues
gh issue list --search "authentication"
```

### View Issue
```bash
# View details
gh issue view <number>

# View in browser
gh issue view <number> --web
```

### Update Issue
```bash
# Add comment
gh issue comment <number> --body "Comment text"

# Add label
gh issue edit <number> --add-label "in-progress"

# Assign
gh issue edit <number> --add-assignee @username

# Close issue
gh issue close <number>

# Reopen issue
gh issue reopen <number>
```

### Link to PR
When creating a PR that fixes an issue:
```markdown
Closes #123
Fixes #123
Resolves #123
```

## Output

After creating issue:
1. Show issue number
2. Show issue URL
3. List labels applied
4. Show assignees
