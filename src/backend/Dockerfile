# ============================================================
# AssuranceNet FastAPI Backend - Multi-stage build
# ============================================================

# Stage 1: Build dependencies
FROM python:3.11-slim-bookworm AS builder

WORKDIR /build

COPY pyproject.toml ./
RUN pip install --no-cache-dir --upgrade pip \
    && mkdir -p app && touch app/__init__.py \
    && pip install --no-cache-dir --prefix=/install .

# Stage 2: Runtime
FROM python:3.11-slim-bookworm

ENV DEBIAN_FRONTEND=noninteractive \
    PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1

WORKDIR /app

# Install ODBC driver for Azure SQL
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc g++ unixodbc-dev curl gnupg2 \
    && curl -fsSL https://packages.microsoft.com/keys/microsoft.asc | gpg --dearmor -o /usr/share/keyrings/microsoft-prod.gpg \
    && curl -fsSL https://packages.microsoft.com/config/debian/12/prod.list > /etc/apt/sources.list.d/mssql-release.list \
    && apt-get update \
    && ACCEPT_EULA=Y apt-get install -y --no-install-recommends msodbcsql18 \
    && apt-get purge -y gcc g++ curl gnupg2 \
    && apt-get autoremove -y \
    && rm -rf /var/lib/apt/lists/*

# Copy installed packages from builder
COPY --from=builder /install /usr/local

# Create non-root user
RUN groupadd -r appuser && useradd -r -g appuser -s /bin/false appuser

# Copy application code
COPY app/ ./app/

# Set ownership
RUN chown -R appuser:appuser /app

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=15s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/api/v1/health')" || exit 1

USER appuser

EXPOSE 8000

CMD ["gunicorn", "app.main:app", "-k", "uvicorn.workers.UvicornWorker", "--bind", "0.0.0.0:8000", "--workers", "2", "--timeout", "120", "--graceful-timeout", "30"]
