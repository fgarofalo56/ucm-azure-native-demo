---
name: commit
description: Create conventional commits
---

Create a well-structured git commit using Conventional Commits format.

## Instructions

1. Run `git status` to see all changes (staged and unstaged)
2. Run `git diff --staged` to review staged changes
3. If nothing is staged, ask user what to stage or suggest `git add -A`
4. Analyze the changes and determine the appropriate commit type
5. Write a commit message following Conventional Commits format
6. Execute the commit

## Conventional Commits Format

```
<type>(<scope>): <description>

[optional body]

[optional footer(s)]
```

### Types
- **feat**: New feature
- **fix**: Bug fix
- **docs**: Documentation only
- **style**: Code style (formatting, semicolons, etc.)
- **refactor**: Code change that neither fixes a bug nor adds a feature
- **perf**: Performance improvement
- **test**: Adding or updating tests
- **build**: Build system or external dependencies
- **ci**: CI configuration
- **chore**: Other changes that don't modify src or test files
- **revert**: Reverts a previous commit

### Scope (optional)
The scope is the module/component affected (e.g., api, ui, auth, db)

### Examples
```
feat(auth): add JWT token refresh endpoint
fix(ui): resolve button alignment on mobile
docs: update API documentation for v2 endpoints
refactor(db): optimize user query performance
```

## Breaking Changes

If the commit introduces a breaking change:
```
feat(api)!: change authentication flow

BREAKING CHANGE: API now requires Bearer token instead of API key
```

## Arguments

$ARGUMENTS

If arguments provided, use them as context for the commit message.
If arguments say "amend", use `git commit --amend` instead.

## Output

After committing, show:
1. The commit hash
2. Files changed summary
3. The full commit message used
