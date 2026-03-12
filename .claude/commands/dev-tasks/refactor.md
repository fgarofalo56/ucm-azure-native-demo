---
name: refactor
description: Refactor code for better readability, performance, or maintainability
---

# /refactor - Code Refactoring

Analyze and refactor the specified code for improved quality.

## Focus Areas

1. **Readability** - Clear variable names, logical structure, comments where needed
2. **Performance** - Optimize loops, reduce complexity, improve efficiency
3. **Maintainability** - Extract functions, reduce duplication, improve modularity
4. **Best Practices** - Apply language idioms and modern patterns

## Process

1. Read and understand the code
2. Identify issues and improvement opportunities
3. Apply refactoring patterns
4. Ensure behavior is preserved
5. Document changes made

## Refactoring Patterns

### Extract Function/Method
Break large functions into smaller, focused ones.

### Rename Variables
Use clear, descriptive names that reveal intent.

### Remove Duplication
DRY (Don't Repeat Yourself) - extract common code.

### Simplify Conditionals
Replace complex conditionals with early returns, guard clauses, or strategy pattern.

### Reduce Nesting
Flatten deeply nested code with early returns or extraction.

### Use Modern Syntax
Apply language-specific modern patterns and idioms.

## Output Format

```markdown
## Refactoring Analysis

### Issues Identified
- [Issue 1]: [Location and description]
- [Issue 2]: [Location and description]

### Changes Made

#### [Change 1]: [Description]
- **Pattern**: [e.g., Extract Function]
- **Reason**: [Why this improves the code]

### Refactored Code
[The refactored code]

### Trade-offs
- [Any trade-offs or considerations]

### Testing Notes
- [Suggestions for verifying the refactoring]
```

## Arguments

$ARGUMENTS

If a file path is provided, refactor that file.
If specific functions or a focus area is mentioned, prioritize those.
