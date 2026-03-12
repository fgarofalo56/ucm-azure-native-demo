---
name: generate-tests
description: Generate comprehensive unit tests for code
---

# /generate-tests - Generate Unit Tests

Create thorough unit tests for the specified code.

## Test Requirements

- Use the project's existing test framework
- Follow AAA pattern (Arrange, Act, Assert)
- Cover happy paths and edge cases
- Include error scenarios
- Use descriptive test names

## Test Cases to Include

1. **Happy Path** - Normal expected behavior
2. **Edge Cases** - Boundary values, empty inputs, null/undefined
3. **Error Handling** - Invalid inputs, exceptions
4. **Integration Points** - Mock external dependencies

## Process

1. Read and analyze the code to test
2. Identify the test framework used in the project
3. Determine all test scenarios
4. Generate tests following project conventions
5. Include setup/teardown as needed
6. Add mocks for dependencies

## Test Frameworks by Language

| Language | Frameworks |
|----------|------------|
| Python | pytest, unittest |
| TypeScript/JavaScript | Jest, Vitest, Mocha |
| Go | testing, testify |
| Rust | built-in, mockall |
| Java | JUnit, Mockito |
| C# | xUnit, NUnit, Moq |

## Output Format

```markdown
## Test Plan for [Module/Function]

### Test Scenarios
- [ ] [Scenario 1]: Happy path - [description]
- [ ] [Scenario 2]: Edge case - [description]
- [ ] [Scenario 3]: Error case - [description]

### Generated Tests

[Test code following project conventions]

### Coverage Notes
- Functions covered: [list]
- Lines covered: [estimate]
- Missing scenarios: [if any]

### Mocking Required
- [Dependency 1]: [How to mock]
```

## Arguments

$ARGUMENTS

If a file path is provided, generate tests for that file.
If specific functions are mentioned, focus on those.
Output location should follow project test conventions (e.g., `__tests__/`, `tests/`, `*_test.go`).
