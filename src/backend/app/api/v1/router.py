"""API v1 router aggregation."""

from fastapi import APIRouter

from app.api.v1.admin import router as admin_router
from app.api.v1.audit import router as audit_router
from app.api.v1.documents import router as documents_router
from app.api.v1.explorer import router as explorer_router
from app.api.v1.health import router as health_router
from app.api.v1.investigations import router as investigations_router
from app.api.v1.pdf_merge import router as pdf_merge_router
from app.api.v1.search import router as search_router

api_v1_router = APIRouter()

api_v1_router.include_router(health_router, tags=["Health"])
api_v1_router.include_router(investigations_router, prefix="/investigations", tags=["Investigations"])
api_v1_router.include_router(documents_router, prefix="/documents", tags=["Documents"])
api_v1_router.include_router(pdf_merge_router, tags=["PDF Merge"])
api_v1_router.include_router(audit_router, prefix="/audit", tags=["Audit"])
api_v1_router.include_router(admin_router, prefix="/admin", tags=["Admin"])
api_v1_router.include_router(search_router, prefix="/search", tags=["Search"])
api_v1_router.include_router(explorer_router, prefix="/explorer", tags=["Explorer"])
