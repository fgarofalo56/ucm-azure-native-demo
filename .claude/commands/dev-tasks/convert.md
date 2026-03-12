---
name: convert
description: Convert code from one language or framework to another
---

# /convert - Convert Code

Convert code between languages, frameworks, or patterns.

## Conversion Guidelines

1. **Preserve Logic** - Maintain the same functionality
2. **Idiomatic Code** - Use target language/framework best practices
3. **Type Safety** - Add types where applicable
4. **Error Handling** - Adapt to target conventions
5. **Dependencies** - Map to equivalent libraries

## Required Information

Please specify:

- **Source**: What language/framework the code is currently in
- **Target**: What language/framework to convert to
- **File or Code**: Path to file or code snippet to convert
- **Constraints**: Any specific patterns or compatibility requirements

## Process

1. Read and understand the source code
2. Identify language-specific constructs
3. Map to equivalent target constructs
4. Apply target language idioms and best practices
5. Add appropriate type annotations
6. Adapt error handling patterns
7. Map dependencies to equivalents

## Output Format

```markdown
## Conversion: [Source] -> [Target]

### Original Code
[Brief summary of what the code does]

### Converted Code
[The converted code]

### Key Changes

- **[Change 1]**: [Why this change was made]
- **[Change 2]**: [Why this change was made]

### Dependencies Mapped

| Source | Target |
|--------|--------|
| [lib1] | [equiv1] |

### Notes

- [Any caveats or considerations]
```

## Arguments

$ARGUMENTS

Specify: `<source_lang> to <target_lang> <file_path>`
Example: `python to typescript ./src/utils.py`
