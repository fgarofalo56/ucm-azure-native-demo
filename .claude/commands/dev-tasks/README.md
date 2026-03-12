# 🛠️ Dev Tasks Commands

Common development task commands for fixing, refactoring, testing, optimizing, and documenting code. These commands cover the most frequent day-to-day coding activities.

## 📋 Commands

| Command | Description | When to Use |
|---------|-------------|-------------|
| [`/dev-tasks:fix`](./fix.md) | Analyze and fix bugs and errors in code | When you have a bug, error message, or failing test that needs diagnosis and repair |
| [`/dev-tasks:refactor`](./refactor.md) | Refactor code for better readability, performance, or maintainability | When code works but needs structural improvement, deduplication, or pattern updates |
| [`/dev-tasks:optimize`](./optimize.md) | Optimize code for better performance | When you need to improve speed, reduce memory usage, or optimize database queries |
| [`/dev-tasks:review`](./review.md) | Perform comprehensive code review on changes or specified files | Before merging a PR or when you want a thorough quality check on recent changes |
| [`/dev-tasks:security-review`](./security-review.md) | Perform security review and identify vulnerabilities in code | Before deploying to production, after adding auth logic, or during security audits |
| [`/dev-tasks:generate-tests`](./generate-tests.md) | Generate comprehensive unit tests for code | When you need test coverage for new or existing code |
| [`/dev-tasks:document`](./document.md) | Add documentation and comments to code | When code lacks docstrings, inline comments, or README documentation |
| [`/dev-tasks:beautify-docs`](./beautify-docs.md) | Transform markdown docs with icons, diagrams, charts, badges, and rich formatting | When documentation looks plain and needs visual polish, navigation aids, or mermaid diagrams |
| [`/dev-tasks:explain`](./explain.md) | Explain code in detail with documentation | When onboarding to unfamiliar code or need to understand complex logic |
| [`/dev-tasks:convert`](./convert.md) | Convert code from one language or framework to another | When migrating between languages (e.g., JS to TS) or frameworks (e.g., Express to FastAPI) |
| [`/dev-tasks:research`](./research.md) | Search Archon knowledge base for documentation and code examples | When you need to find best practices, patterns, or reference implementations |

## 💡 Usage Examples

### Fixing a bug

```
> /dev-tasks:fix

Paste the error message or describe the bug, and Claude will:
1. Analyze the error and trace it to the root cause
2. Propose a fix with explanation
3. Apply the fix and verify it resolves the issue
```

### Generating tests

```
> /dev-tasks:generate-tests src/services/auth.ts

Claude will:
1. Analyze the module's exports and logic paths
2. Generate unit tests covering happy paths and edge cases
3. Include mocking for external dependencies
```

## 🔄 Common Workflows

```
/dev-tasks:fix           # Fix a bug
/dev-tasks:generate-tests # Add tests for the fix
/dev-tasks:review         # Review the changes
/git:commit               # Commit with conventional message
```

```
/dev-tasks:refactor       # Improve code structure
/dev-tasks:optimize       # Tune performance
/dev-tasks:document       # Update documentation
/dev-tasks:security-review # Verify no new vulnerabilities
```

## 🔗 Related

- [Base Commands](../base_commands/) -- Session lifecycle (start, save, end)
- [Git Commands](../git/) -- Committing and pushing your changes
- [Code Quality Commands](../code-quality/) -- Linting and static analysis
- [PRP Commands](../prp/) -- Full feature delivery workflow
- [Testing Skills](../../skills/testing/) -- Advanced testing frameworks and strategies
