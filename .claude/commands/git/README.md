# 🔀 Git & GitHub Commands

Slash commands for common git and GitHub (gh CLI) operations.

## ⌨️ Git Commands

| Command | Description | Usage |
|---------|-------------|-------|
| `/git:commit` | Create commit with Conventional Commits | `/git:commit`, `/git:commit amend` |
| `/git:branch` | Manage branches (create, switch, delete) | `/git:branch`, `/git:branch create feat/new` |
| `/git:sync` | Push, pull, fetch operations | `/git:sync`, `/git:sync push` |
| `/git:stash` | Save and restore work in progress | `/git:stash`, `/git:stash pop` |
| `/git:undo` | Undo operations (reset, revert, restore) | `/git:undo commit`, `/git:undo unstage` |
| `/git:log` | View commit history | `/git:log`, `/git:log graph` |
| `/git:diff` | View changes | `/git:diff`, `/git:diff staged` |
| `/git:merge` | Merge branches | `/git:merge main`, `/git:merge squash feat` |
| `/git:rebase` | Rebase operations | `/git:rebase main`, `/git:rebase interactive` |

## 🐙 GitHub Commands (gh CLI)

| Command | Description | Usage |
|---------|-------------|-------|
| `/git:pr-create` | Create a Pull Request | `/git:pr-create`, `/git:pr-create draft` |
| `/git:pr-review` | Review a Pull Request | `/git:pr-review 123`, `/git:pr-review approve 123` |
| `/git:issue-create` | Create an Issue | `/git:issue-create`, `/git:issue-create bug` |
| `/git:repo-clone` | Clone a repository | `/git:repo-clone owner/repo` |
| `/git:actions-status` | Check CI/CD status | `/git:actions-status`, `/git:actions-status failed` |

## 📜 Commit Message Convention

All commands follow [Conventional Commits](https://www.conventionalcommits.org/):

```
<type>(<scope>): <description>

[body]

[footer]
```

### 🏷️ Types
- `feat` - New feature
- `fix` - Bug fix
- `docs` - Documentation
- `style` - Formatting
- `refactor` - Code restructuring
- `perf` - Performance
- `test` - Tests
- `build` - Build system
- `ci` - CI/CD
- `chore` - Maintenance

## 🔑 Prerequisites

For GitHub commands, ensure gh CLI is authenticated:
```bash
gh auth status
gh auth login  # if needed
```

## 🚀 Quick Reference

```bash
# Daily workflow
/git:sync              # Fetch and check status
/git:branch create feat/my-feature
# ... make changes ...
/git:commit            # Commit with conventional message
/git:sync push         # Push to remote
/git:pr-create         # Create PR

# Code review
/git:pr-review 123     # Review PR
/git:actions-status    # Check CI

# Oops, need to undo
/git:undo commit       # Undo last commit
/git:stash             # Stash changes temporarily
```

## 🔗 Related

- [Base Commands](../base_commands/) -- Session lifecycle management
- [Dev Tasks Commands](../dev-tasks/) -- Code review and quality commands
- [Code Quality Commands](../code-quality/) -- Linting and code analysis
- [Worktree Commands](../worktree/) -- Git worktree management
