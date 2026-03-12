---
applyTo:
  - "**/*"
description: "Security requirements that apply to all code"
---

# Security Standards

## Core Principles
- Security is everyone's responsibility
- Defense in depth - multiple layers of protection
- Least privilege - minimal permissions needed
- Fail securely - errors should not expose vulnerabilities
- Never trust user input

## Input Validation

### Validate all external input
```typescript
const createUserSchema = z.object({
  email: z.string().email().max(255),
  name: z.string().min(1).max(100).regex(/^[\w\s-]+$/),
  age: z.number().int().min(0).max(150),
});

const validatedData = createUserSchema.parse(req.body);
```

### Prevent injection attacks
```typescript
// SQL - Use parameterized queries
const user = await db.query(
  'SELECT * FROM users WHERE id = $1',
  [userId]
);

// NEVER concatenate user input
// BAD: `SELECT * FROM users WHERE id = '${userId}'`
```

### Sanitize output (prevent XSS)
```typescript
// HTML encoding for user content
import { escape } from 'html-escaper';
const safeContent = escape(userContent);

// React automatically escapes
<div>{userContent}</div>  // Safe

// Avoid dangerouslySetInnerHTML
<div dangerouslySetInnerHTML={{ __html: userContent }} />  // Dangerous
```

## Authentication

### Password requirements
```typescript
const passwordSchema = z.string()
  .min(12, 'Minimum 12 characters')
  .regex(/[A-Z]/, 'At least one uppercase letter')
  .regex(/[a-z]/, 'At least one lowercase letter')
  .regex(/[0-9]/, 'At least one number')
  .regex(/[^A-Za-z0-9]/, 'At least one special character');
```

### Secure password storage
```typescript
import { hash, verify } from '@node-rs/argon2';

// Hash with Argon2id (recommended)
const hashedPassword = await hash(password, {
  memoryCost: 65536,
  timeCost: 3,
  parallelism: 4,
});
```

### Token management
```typescript
// JWT with short expiration
const token = jwt.sign(
  { userId, role },
  process.env.JWT_SECRET,
  { expiresIn: '15m', algorithm: 'HS256' }
);
```

## Authorization

### Implement proper access control
```typescript
const PERMISSIONS = {
  admin: ['read', 'write', 'delete', 'manage'],
  editor: ['read', 'write'],
  viewer: ['read'],
};

function authorize(requiredPermission: string) {
  return (req, res, next) => {
    const userPermissions = PERMISSIONS[req.user.role] || [];
    if (!userPermissions.includes(requiredPermission)) {
      return res.status(403).json({ error: 'Forbidden' });
    }
    next();
  };
}
```

## Secrets Management

### Never hardcode secrets
```typescript
// BAD
const API_KEY = 'sk_live_abc123xyz';

// GOOD - Use environment variables
const API_KEY = process.env.API_KEY;

// Validate required secrets at startup
const requiredEnvVars = ['DATABASE_URL', 'JWT_SECRET', 'API_KEY'];
for (const envVar of requiredEnvVars) {
  if (!process.env[envVar]) {
    throw new Error(`Missing required environment variable: ${envVar}`);
  }
}
```

## Data Protection

### Encrypt sensitive data at rest
```typescript
import { createCipheriv, randomBytes } from 'crypto';

function encrypt(text: string, key: Buffer): string {
  const iv = randomBytes(16);
  const cipher = createCipheriv('aes-256-gcm', key, iv);
  let encrypted = cipher.update(text, 'utf8', 'hex');
  encrypted += cipher.final('hex');
  return `${iv.toString('hex')}:${cipher.getAuthTag().toString('hex')}:${encrypted}`;
}
```

### Handle sensitive data carefully
```typescript
// Don't log sensitive data
logger.info('User logged in', {
  userId: user.id,
  // NEVER: password, token, creditCard, etc.
});
```

## HTTP Security Headers

### Configure security headers
```typescript
import helmet from 'helmet';

app.use(helmet());
app.use(helmet.contentSecurityPolicy({
  directives: {
    defaultSrc: ["'self'"],
    scriptSrc: ["'self'"],
    frameSrc: ["'none'"],
    objectSrc: ["'none'"],
  },
}));
```

## Rate Limiting

### Protect against abuse
```typescript
import rateLimit from 'express-rate-limit';

const apiLimiter = rateLimit({
  windowMs: 15 * 60 * 1000,
  max: 100,
});

const authLimiter = rateLimit({
  windowMs: 15 * 60 * 1000,
  max: 5,
  message: { error: 'Too many login attempts' },
});

app.use('/api/', apiLimiter);
app.use('/api/auth/login', authLimiter);
```

## Security Checklist

Before deploying:
- [ ] All user input validated and sanitized
- [ ] Authentication implemented correctly
- [ ] Authorization checked at all levels
- [ ] No secrets in code or logs
- [ ] HTTPS enforced
- [ ] Security headers configured
- [ ] Rate limiting in place
- [ ] Dependencies audited for vulnerabilities
- [ ] Security logging enabled
- [ ] Error messages don't leak sensitive info
