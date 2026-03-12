"""NIST 800-53 AU-2/AU-3 compliant audit event middleware."""

import structlog
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.requests import Request
from starlette.responses import Response

logger = structlog.get_logger()

# Paths that trigger audit events
AUDITABLE_METHODS = {"POST", "PUT", "PATCH", "DELETE"}


class AuditMiddleware(BaseHTTPMiddleware):
    """Captures audit events for NIST 800-53 compliance."""

    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        response = await call_next(request)

        # Log audit events for state-changing operations
        if request.method in AUDITABLE_METHODS and request.url.path.startswith("/api/"):
            correlation_id = getattr(request.state, "correlation_id", "unknown")
            user_id = getattr(request.state, "user_id", "anonymous")

            logger.info(
                "audit_event",
                event_type=_derive_event_type(request.url.path, request.method),
                user_id=user_id,
                ip_address=request.client.host if request.client else "unknown",
                user_agent=request.headers.get("user-agent", ""),
                resource_path=request.url.path,
                method=request.method,
                status_code=response.status_code,
                result="success" if response.status_code < 400 else "failure",
                correlation_id=correlation_id,
            )

        return response


def _derive_event_type(path: str, method: str) -> str:
    """Derive audit event type from request path and method."""
    if "/documents/" in path:
        if method == "POST" and "upload" in path:
            return "document.upload"
        if method == "DELETE":
            return "document.delete"
        return "document.update"
    if "/investigations/" in path:
        if method == "POST":
            return "investigation.create"
        return "investigation.update"
    if "/merge-pdf" in path:
        return "document.merge"
    return f"api.{method.lower()}"
