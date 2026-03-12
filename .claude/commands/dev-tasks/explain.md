---
name: explain
description: Explain code in detail with documentation
---

# /explain - Explain Code

Provide a detailed explanation of the code.

## Explanation Format

1. **Overview** - What does this code do at a high level?
2. **Step-by-Step** - Walk through the logic
3. **Key Concepts** - Explain any patterns, algorithms, or techniques used
4. **Dependencies** - What does it rely on?
5. **Usage** - How would you use this code?

Keep explanations clear and accessible for developers of varying experience levels.

## Code Context

If a file path is provided, read and explain that file.
If specific functions or classes are mentioned, focus on those.
Otherwise, ask what code to explain.

## Process

1. Read the relevant file(s)
2. Analyze the structure and purpose
3. Explain each major component
4. Highlight important patterns or concepts
5. Provide usage examples if helpful

## Output Format

```markdown
## Overview

[High-level description of what the code does]

## Step-by-Step Breakdown

### [Component 1]
[Explanation]

### [Component 2]
[Explanation]

## Key Concepts

- **[Concept 1]**: [Explanation]
- **[Concept 2]**: [Explanation]

## Dependencies

- [External dependency]: [Purpose]

## Usage Example

[How to use this code]
```

## Arguments

$ARGUMENTS

If a file path is provided, explain that file.
If a topic or function name is provided, focus on that.
