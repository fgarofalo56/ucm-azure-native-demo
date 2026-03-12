---
name: security-review
description: Perform security review and identify vulnerabilities in code
---

# /security-review - Security Review

Analyze code for security vulnerabilities and provide fixes.

## Security Checklist

1. **Injection** - SQL, XSS, command injection
2. **Authentication** - Proper auth checks, session handling
3. **Authorization** - Access control, privilege escalation
4. **Data Exposure** - Sensitive data in logs, responses, URLs
5. **Input Validation** - All user input validated and sanitized
6. **Dependencies** - Known vulnerabilities in packages
7. **Cryptography** - Secure algorithms, proper key management
8. **Error Handling** - No sensitive info in errors

## OWASP Top 10 Coverage

| Risk | Check For |
|------|-----------|
| Injection | SQL, NoSQL, LDAP, OS command injection |
| Broken Auth | Weak passwords, session fixation, credential exposure |
| Sensitive Data | Encryption at rest/transit, PII handling |
| XML External Entities | XXE attacks in XML parsers |
| Broken Access Control | IDOR, missing function-level access control |
| Misconfiguration | Default configs, unnecessary features, verbose errors |
| XSS | Reflected, stored, DOM-based XSS |
| Insecure Deserialization | Object injection, type confusion |
| Known Vulnerabilities | Outdated dependencies with CVEs |
| Insufficient Logging | Missing audit trails, log injection |

## Process

1. Read the target code
2. Check against security checklist
3. Identify vulnerabilities
4. Assess severity
5. Provide secure alternatives

## Vulnerability Report Format

For each issue found:

```markdown
### [Vulnerability Name]

**Severity**: Critical / High / Medium / Low

**Location**: `file.ts:42`

**Description**: [What's the vulnerability?]

**Risk**: [What could an attacker do?]

**Affected Code**:
[The vulnerable code]

**Fix**:
[Secure code replacement]

**References**:
- [OWASP link or CVE]
```

## Output Format

```markdown
# Security Review Report

## Summary

- **Files Reviewed**: [count]
- **Critical Issues**: [count]
- **High Issues**: [count]
- **Medium Issues**: [count]
- **Low Issues**: [count]

## Findings

### Critical

[Critical vulnerabilities]

### High

[High severity issues]

### Medium

[Medium severity issues]

### Low

[Low severity suggestions]

## Recommendations

1. [Priority action 1]
2. [Priority action 2]

## Dependency Check

```bash
# Check for known vulnerabilities
npm audit
# or
pip-audit
# or
go mod verify
```
```

## Arguments

$ARGUMENTS

If a file path is provided, review that file.
If no file specified, review current changes or ask what to review.
