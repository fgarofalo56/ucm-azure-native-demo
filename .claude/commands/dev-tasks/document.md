---
name: document
description: Add documentation and comments to code
---

# /document - Document Code

Add comprehensive documentation to the code.

## Documentation Standards

1. **File/Module Level** - Purpose and overview
2. **Function/Method Level** - JSDoc/docstring with params, returns, throws
3. **Inline Comments** - Complex logic explanation (sparingly)
4. **Type Annotations** - Clear type definitions
5. **Examples** - Usage examples where helpful

## Output Format

Match the project's existing documentation style. Include:

- Parameter descriptions
- Return value descriptions
- Exception/error documentation
- Usage examples for public APIs

## Process

1. Read the target file
2. Analyze existing documentation style in the project
3. Add appropriate documentation following language conventions:
   - **Python**: Docstrings (Google, NumPy, or Sphinx style)
   - **TypeScript/JavaScript**: JSDoc comments
   - **Go**: Go doc comments
   - **Rust**: Rustdoc comments
   - **Java/C#**: XML doc or Javadoc
4. Add type annotations where missing
5. Add inline comments for complex logic only

## Documentation Templates

### Python (Google Style)
```python
def function_name(param1: str, param2: int) -> bool:
    """Brief description of function.

    Longer description if needed.

    Args:
        param1: Description of param1.
        param2: Description of param2.

    Returns:
        Description of return value.

    Raises:
        ValueError: When param1 is empty.
    """
```

### TypeScript/JavaScript (JSDoc)
```typescript
/**
 * Brief description of function.
 *
 * @param param1 - Description of param1
 * @param param2 - Description of param2
 * @returns Description of return value
 * @throws {Error} When param1 is empty
 * @example
 * const result = functionName("test", 42);
 */
```

## Arguments

$ARGUMENTS

If a file path is provided, document that file.
If specific functions are mentioned, focus on those.
