---
applyTo:
  - "**/src/api/**"
  - "**/src/controllers/**"
  - "**/src/routes/**"
  - "**/src/services/**"
  - "**/src/middleware/**"
  - "**/api/**"
  - "**/server/**"
---

# Backend API Development Standards

## Core Principles
- RESTful design with consistent conventions
- Proper HTTP status codes and error responses
- Input validation at the API boundary
- Structured logging and observability
- Rate limiting and security headers

## API Design

### URL Structure
```
# Resources (nouns, plural)
GET    /api/v1/users           # List users
POST   /api/v1/users           # Create user
GET    /api/v1/users/:id       # Get user
PATCH  /api/v1/users/:id       # Update user
DELETE /api/v1/users/:id       # Delete user

# Nested resources
GET    /api/v1/users/:id/orders    # User's orders

# Actions (when CRUD doesn't fit)
POST   /api/v1/users/:id/activate
POST   /api/v1/orders/:id/cancel
```

### HTTP Status Codes

| Code | Usage |
|------|-------|
| 200 | Success with body |
| 201 | Created (include Location header) |
| 204 | Success, no content (DELETE) |
| 400 | Bad request (validation error) |
| 401 | Unauthorized (no/invalid auth) |
| 403 | Forbidden (authenticated but not allowed) |
| 404 | Not found |
| 409 | Conflict (duplicate, version mismatch) |
| 422 | Unprocessable entity (semantic error) |
| 429 | Too many requests |
| 500 | Internal server error |

### Response Format

#### Success responses
```json
// Single resource
{
  "data": {
    "id": "usr_123",
    "email": "user@example.com"
  }
}

// Collection with pagination
{
  "data": [...],
  "meta": {
    "page": 1,
    "limit": 20,
    "total": 156
  }
}
```

#### Error responses
```json
{
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Request validation failed",
    "details": [
      { "field": "email", "message": "Invalid email format" }
    ]
  },
  "requestId": "req_abc123"
}
```

## Input Validation

### Validate at the API boundary
```typescript
const createUserSchema = z.object({
  email: z.string().email(),
  name: z.string().min(1).max(100),
  password: z.string().min(8).max(72),
});

app.post('/api/v1/users', validate(createUserSchema), async (req, res) => {
  // req.body is now typed and validated
});
```

## Authentication & Authorization

### Use middleware for auth
```typescript
const authenticate = async (req, res, next) => {
  const token = req.headers.authorization?.replace('Bearer ', '');
  if (!token) {
    return res.status(401).json({
      error: { code: 'UNAUTHORIZED', message: 'Authentication required' }
    });
  }
  req.user = await verifyToken(token);
  next();
};

const authorize = (...roles: string[]) => (req, res, next) => {
  if (!roles.includes(req.user.role)) {
    return res.status(403).json({
      error: { code: 'FORBIDDEN', message: 'Insufficient permissions' }
    });
  }
  next();
};
```

## Error Handling

### Use centralized error handling
```typescript
class AppError extends Error {
  constructor(
    public statusCode: number,
    public code: string,
    message: string,
    public details?: unknown
  ) {
    super(message);
    this.name = 'AppError';
  }
}

app.use((error: Error, req: Request, res: Response, next: NextFunction) => {
  if (error instanceof AppError) {
    return res.status(error.statusCode).json({
      error: { code: error.code, message: error.message }
    });
  }
  res.status(500).json({
    error: { code: 'INTERNAL_ERROR', message: 'An unexpected error occurred' }
  });
});
```

## Logging & Observability

### Use structured logging
```typescript
app.use((req, res, next) => {
  const requestId = req.headers['x-request-id'] || generateId();
  const start = Date.now();

  res.on('finish', () => {
    logger.info({
      type: 'request',
      requestId,
      method: req.method,
      path: req.path,
      statusCode: res.statusCode,
      duration: Date.now() - start,
    });
  });
  next();
});
```

### Add health check endpoints
```typescript
app.get('/health', (req, res) => {
  res.json({ status: 'healthy' });
});

app.get('/health/ready', async (req, res) => {
  const checks = {
    database: await checkDatabase(),
    redis: await checkRedis(),
  };
  const healthy = Object.values(checks).every(Boolean);
  res.status(healthy ? 200 : 503).json({ status: healthy ? 'ready' : 'not_ready', checks });
});
```

## Security

### Required security headers
```typescript
import helmet from 'helmet';
app.use(helmet());
```

### Rate limiting
```typescript
import rateLimit from 'express-rate-limit';

const apiLimiter = rateLimit({
  windowMs: 15 * 60 * 1000,
  max: 100,
});

app.use('/api/', apiLimiter);
```

## Database Patterns

### Use repository pattern
```typescript
interface UserRepository {
  findById(id: string): Promise<User | null>;
  create(data: CreateUserData): Promise<User>;
}
```

### Use transactions for consistency
```typescript
async function createOrder(data: CreateOrderData): Promise<Order> {
  return db.transaction(async (tx) => {
    const order = await tx.orders.create(data.order);
    await tx.orderItems.createMany(data.items);
    return order;
  });
}
```

## File Organization
```
src/
├── api/
│   └── v1/
│       └── users/
│           ├── controller.ts
│           ├── routes.ts
│           ├── schema.ts
│           └── service.ts
├── domain/
├── infrastructure/
└── lib/
```
