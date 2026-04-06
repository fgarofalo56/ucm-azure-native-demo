"""AssuranceNet Document Management API - FastAPI entry point."""

from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

import structlog
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded

from app.api.v1.router import api_v1_router
from app.config import settings
from app.middleware.correlation import CorrelationIdMiddleware
from app.middleware.logging import RequestLoggingMiddleware
from app.middleware.rate_limit import limiter
from app.telemetry.setup import configure_telemetry

logger = structlog.get_logger()


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """Application lifespan: startup and shutdown events."""
    configure_telemetry()
    logger.info(
        "application_starting",
        environment=settings.environment,
        version="0.1.0",
    )
    yield
    logger.info("application_shutting_down")


app = FastAPI(
    title="AssuranceNet Document Management API",
    description="Azure-native document management system replacing Oracle UCM",
    version="0.1.0",
    docs_url="/api/docs" if not settings.is_production else None,
    redoc_url="/api/redoc" if not settings.is_production else None,
    openapi_url="/api/openapi.json" if not settings.is_production else None,
    lifespan=lifespan,
)

# Rate limiting setup
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# Middleware (order matters - last added = first executed)
app.add_middleware(RequestLoggingMiddleware)
app.add_middleware(CorrelationIdMiddleware)
app.add_middleware(
    CORSMiddleware,
    allow_origins=[o.strip() for o in settings.cors_origins.split(",") if o.strip()],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Global exception handler — ensures unhandled errors return JSON
# (so CORSMiddleware can attach headers to the response)
@app.exception_handler(Exception)
async def unhandled_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    logger.error("unhandled_exception", error=str(exc), path=request.url.path)
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error"},
    )


# Routes
app.include_router(api_v1_router, prefix="/api/v1")
