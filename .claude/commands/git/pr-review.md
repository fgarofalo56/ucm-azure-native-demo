---
name: pr-review
description: Review GitHub pull requests
---

Review a GitHub Pull Request using the gh CLI.

## Arguments

$ARGUMENTS

Parse arguments:
- No args: Review PR for current branch
- "<number>": Review specific PR by number
- "<url>": Review PR by URL
- "list": List PRs needing review
- "approve <number>": Quick approve
- "request-changes <number>": Request changes

## Review Workflow

### 1. Find PR to Review

```bash
# List PRs requesting your review
gh pr list --search "review-requested:@me"

# List all open PRs
gh pr list

# List PRs by author
gh pr list --author <username>
```

### 2. View PR Details

```bash
# View PR summary
gh pr view <number>

# View in browser
gh pr view <number> --web

# View diff
gh pr diff <number>

# View specific files
gh pr diff <number> -- <file-path>
```

### 3. Checkout PR Locally (Optional)

```bash
# Checkout PR branch
gh pr checkout <number>

# Run tests locally
npm test  # or your test command
```

### 4. Review the Changes

Analyze the PR for:
- **Code Quality**: Style, patterns, best practices
- **Functionality**: Does it work as intended?
- **Tests**: Are there adequate tests?
- **Security**: Any vulnerabilities?
- **Performance**: Any concerns?
- **Documentation**: Updated if needed?

### 5. Submit Review

```bash
# Approve
gh pr review <number> --approve --body "LGTM! Nice work."

# Request changes
gh pr review <number> --request-changes --body "Please address the following:
- Issue 1
- Issue 2"

# Comment only (no approval/rejection)
gh pr review <number> --comment --body "Some thoughts..."
```

### 6. Add Line Comments

```bash
# Add comment on specific line (opens editor)
gh pr review <number>
```

Or use the web interface for line-by-line comments:
```bash
gh pr view <number> --web
```

## Review Templates

### Approval
```
Looks good!

## Summary
- Code follows conventions
- Tests pass and cover changes
- No security concerns
```

### Request Changes
```
Thanks for the PR! A few things to address:

## Required Changes
- [ ] [Specific issue and suggestion]
- [ ] [Specific issue and suggestion]

## Suggestions (Optional)
- [Nice to have improvement]
```

### Questions
```
## Questions
- [ ] Can you explain the approach for [X]?
- [ ] Why did you choose [Y] over [Z]?

Will approve once clarified.
```

## Checking CI Status

```bash
# View checks status
gh pr checks <number>

# Wait for checks to complete
gh pr checks <number> --watch
```

## Merge After Approval

```bash
# Standard merge
gh pr merge <number>

# Squash merge
gh pr merge <number> --squash

# Rebase merge
gh pr merge <number> --rebase

# Delete branch after merge
gh pr merge <number> --delete-branch
```

## Output

Show:
1. PR title and author
2. Changed files summary
3. CI status
4. Current reviews
5. Review action taken
