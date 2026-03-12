---
applyTo:
  - "**/docs/**"
  - "**/*.md"
  - "**/README*"
  - "**/CHANGELOG*"
  - "**/CONTRIBUTING*"
---

# Documentation Standards

## Core Principles
- Documentation is a first-class deliverable
- Write for your audience (developers, users, operators)
- Keep documentation close to the code it describes
- Use consistent formatting and structure
- Update documentation alongside code changes

## Markdown Formatting

### Headings
```markdown
# Title (H1) - One per document
## Section (H2) - Major sections
### Subsection (H3) - Topics within sections
#### Detail (H4) - Specific items when needed
```

### Code Blocks
Always specify language for syntax highlighting:

```markdown
```typescript
const greeting: string = "Hello, World!";
```

```bash
npm install --save-dev typescript
```
```

### Lists
```markdown
- Unordered list item
- Another item
  - Nested item

1. Ordered list item
2. Another item
   1. Nested item
```

### Tables
```markdown
| Column 1 | Column 2 | Column 3 |
|----------|----------|----------|
| Value 1  | Value 2  | Value 3  |
| Value 4  | Value 5  | Value 6  |
```

## README Structure

Every project README should include:

```markdown
# Project Name

Brief description (1-2 sentences).

## Features

- Feature 1
- Feature 2

## Quick Start

```bash
npm install
npm run dev
```

## Configuration

Environment variables and configuration options.

## Usage

Common usage examples.

## API Reference

Link to detailed API documentation.

## Contributing

How to contribute to the project.

## License

License information.
```

## API Documentation

### Endpoint Documentation
```markdown
### Create User

Creates a new user account.

**Endpoint:** `POST /api/v1/users`

**Authentication:** Required (Bearer token)

**Request Body:**
| Field | Type | Required | Description |
|-------|------|----------|-------------|
| email | string | Yes | User's email address |
| name | string | Yes | User's full name |
| password | string | Yes | Password (min 8 chars) |

**Response:** `201 Created`
```json
{
  "data": {
    "id": "usr_123",
    "email": "user@example.com",
    "name": "John Doe"
  }
}
```

**Errors:**
| Code | Description |
|------|-------------|
| 400 | Invalid request body |
| 409 | Email already exists |
```

## Architecture Documentation

### Decision Records (ADR)
```markdown
# ADR-001: Use PostgreSQL for Primary Database

## Status
Accepted

## Context
We need a reliable, scalable database for our application.

## Decision
We will use PostgreSQL 16.

## Consequences
- Mature ecosystem with excellent tooling
- Strong JSON support for flexible schemas
- Requires operational expertise
```

## Code Comments

### When to Comment
```typescript
// Good: Explain WHY, not WHAT
// Using exponential backoff to avoid overwhelming the API
const delay = Math.pow(2, retryCount) * 1000;

// Good: Document non-obvious behavior
// Returns null if user is soft-deleted (not found in active index)
async function findUser(id: string): Promise<User | null> { ... }

// Avoid: Stating the obvious
// Increment counter
counter++;
```

### JSDoc/TSDoc
```typescript
/**
 * Calculates the total price including tax.
 *
 * @param items - Array of items with prices
 * @param taxRate - Tax rate as decimal (e.g., 0.08 for 8%)
 * @returns Total price with tax applied
 *
 * @example
 * ```typescript
 * const total = calculateTotal([{ price: 100 }], 0.08);
 * // Returns 108
 * ```
 */
function calculateTotal(items: Item[], taxRate: number): number { ... }
```

## Changelog

### Keep a Changelog Format
```markdown
# Changelog

## [Unreleased]

### Added
- New feature description

### Changed
- Modification description

### Deprecated
- Feature to be removed

### Removed
- Removed feature

### Fixed
- Bug fix description

### Security
- Security fix description

## [1.0.0] - 2024-01-15

### Added
- Initial release features
```

## Writing Style

### DO
- Use active voice ("The function returns..." not "A value is returned...")
- Be concise and specific
- Include working code examples
- Use consistent terminology
- Link to related documentation

### DON'T
- Use jargon without explanation
- Assume reader knowledge
- Write walls of text
- Leave TODOs in published docs
- Document implementation details that may change
