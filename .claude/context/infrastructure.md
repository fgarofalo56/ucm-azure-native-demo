---
applyTo:
  - "**/terraform/**"
  - "**/*.tf"
  - "**/*.tfvars"
  - "**/bicep/**"
  - "**/*.bicep"
  - "**/pulumi/**"
  - "**/cdk/**"
  - "**/docker/**"
  - "**/Dockerfile*"
  - "**/docker-compose*.yml"
  - "**/kubernetes/**"
  - "**/helm/**"
---

# Infrastructure as Code Standards

## Core Principles
- Infrastructure should be version controlled
- Environments should be reproducible
- Use immutable infrastructure patterns
- Separate configuration from code
- Document all infrastructure decisions

## Terraform

### File Organization
```
infrastructure/
├── environments/
│   ├── dev/
│   │   ├── main.tf
│   │   ├── variables.tf
│   │   └── terraform.tfvars
│   ├── staging/
│   └── prod/
├── modules/
│   ├── networking/
│   ├── database/
│   └── compute/
└── shared/
    └── backend.tf
```

### Naming Conventions

| Element | Convention | Example |
|---------|-----------|---------|
| Resources | lowercase with underscores | `aws_instance.web_server` |
| Variables | lowercase with underscores | `instance_count` |
| Modules | lowercase with hyphens | `networking`, `database-cluster` |
| Tags | PascalCase | `Name`, `Environment` |

### Resource Naming
```hcl
locals {
  common_tags = {
    Project     = var.project_name
    Environment = var.environment
    ManagedBy   = "terraform"
  }
}

resource "aws_instance" "web" {
  ami           = var.ami_id
  instance_type = var.instance_type

  tags = merge(local.common_tags, {
    Name = "${var.project_name}-${var.environment}-web"
  })
}
```

### Variable Definitions
```hcl
variable "environment" {
  description = "Deployment environment (dev, staging, prod)"
  type        = string

  validation {
    condition     = contains(["dev", "staging", "prod"], var.environment)
    error_message = "Environment must be dev, staging, or prod."
  }
}
```

## Docker

### Dockerfile Best Practices
```dockerfile
# Use specific version tags
FROM node:20-alpine AS builder

WORKDIR /app

# Copy dependency files first (leverage cache)
COPY package.json package-lock.json ./
RUN npm ci --only=production

COPY src/ ./src/
RUN npm run build

# Production stage
FROM node:20-alpine AS production

# Run as non-root user
RUN addgroup -g 1001 -S nodejs && \
    adduser -S nodejs -u 1001

WORKDIR /app

COPY --from=builder --chown=nodejs:nodejs /app/dist ./dist
COPY --from=builder --chown=nodejs:nodejs /app/node_modules ./node_modules

USER nodejs

HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
  CMD wget --no-verbose --tries=1 --spider http://localhost:3000/health || exit 1

EXPOSE 3000
CMD ["node", "dist/server.js"]
```

### Docker Compose
```yaml
services:
  api:
    build:
      context: .
      target: production
    ports:
      - "3000:3000"
    environment:
      - NODE_ENV=production
    depends_on:
      db:
        condition: service_healthy
    healthcheck:
      test: ["CMD", "wget", "--spider", "http://localhost:3000/health"]
      interval: 30s
      timeout: 10s
      retries: 3
    restart: unless-stopped

  db:
    image: postgres:16-alpine
    volumes:
      - postgres_data:/var/lib/postgresql/data
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U user -d app"]
      interval: 10s
      timeout: 5s
      retries: 5

volumes:
  postgres_data:
```

## Kubernetes

### Deployment Configuration
```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: api
  labels:
    app: myapp
    component: api
spec:
  replicas: 3
  selector:
    matchLabels:
      app: myapp
      component: api
  template:
    spec:
      containers:
        - name: api
          image: myapp/api:1.0.0
          ports:
            - containerPort: 3000
          resources:
            requests:
              memory: "256Mi"
              cpu: "250m"
            limits:
              memory: "512Mi"
              cpu: "500m"
          livenessProbe:
            httpGet:
              path: /health
              port: 3000
            initialDelaySeconds: 10
            periodSeconds: 10
          readinessProbe:
            httpGet:
              path: /health/ready
              port: 3000
            initialDelaySeconds: 5
            periodSeconds: 5
          env:
            - name: DATABASE_URL
              valueFrom:
                secretKeyRef:
                  name: api-secrets
                  key: database-url
```

## Azure Bicep

### Module Structure
```bicep
targetScope = 'subscription'

param environment string
param location string = 'eastus'

resource rg 'Microsoft.Resources/resourceGroups@2023-07-01' = {
  name: 'rg-myapp-${environment}'
  location: location
  tags: {
    Environment: environment
    ManagedBy: 'bicep'
  }
}

module networking 'modules/networking.bicep' = {
  name: 'networking'
  scope: rg
  params: {
    environment: environment
    location: location
  }
}
```

## Security

### Secrets Management
- Never commit secrets to version control
- Use secret management tools (Vault, AWS Secrets Manager, Azure Key Vault)
- Rotate secrets regularly
- Use least-privilege access

### Network Security
- Use private subnets for databases and internal services
- Implement security groups with minimal required access
- Enable VPC flow logs
- Use WAF for public-facing applications
