---
name: fix
description: Analyze and fix bugs and errors in code
---

# /fix - Fix Bug

Analyze and fix the issue in the code.

## Analysis Steps

1. **Identify** - What's the root cause?
2. **Explain** - Why does this cause the problem?
3. **Fix** - Provide corrected code
4. **Prevent** - How to avoid this in the future?

## Error Context

If error messages or stack traces are provided, use them for better diagnosis.

## Code Context

If a file path or code snippet is provided in the arguments, analyze that specific code.
If working with selected code in the editor, analyze the selection.
Otherwise, ask for the file or code to fix.

## Process

1. Read the relevant file(s)
2. Identify the bug or error
3. Explain the root cause
4. Provide the fix with explanation
5. Suggest preventive measures (tests, validation, etc.)

## Output Format

```markdown
## Bug Analysis

**Root Cause**: [Explanation of what's wrong]

**Why This Happens**: [Technical explanation]

## Fix

[Code with the fix applied]

## Prevention

- [How to prevent this in the future]
- [Suggested tests or validation]
```

## Arguments

$ARGUMENTS

If a file path is provided, analyze that file.
If an error message is provided, use it for context.
