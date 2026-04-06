# Changelog

All notable changes to the AssuranceNet Document Management System are documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).

---

## [Unreleased]

### Added

**Backend**
- Rate limiting middleware using slowapi (200 requests/minute per client IP, X-Forwarded-For aware for reverse proxy support)
- `DELETE /api/v1/investigations/{id}` endpoint with soft-delete pattern (sets status to "archived", cascades to all documents)
- Pydantic field validators for `Settings` configuration: environment validation (dev/staging/prod/test), upload size bounds (1-2048 MB), log level normalization
- Search pagination with `page` and `page_size` query parameters on `/api/v1/search`

**Frontend**
- `ErrorBoundary` component with styled fallback UI, expandable error details, and "Try again" button
- Global toast notification system (`ToastProvider` + `useToast` hook) with success/error/info variants and 5-second auto-dismiss
- `useDebounce` hook for generic value debouncing (used in search with 500ms delay)
- Modal accessibility: `role="dialog"`, `aria-modal="true"`, `aria-labelledby`, focus trap with Tab/Shift+Tab cycling
- Debounced search-as-you-type in the Header component (navigates to `/search?q=...` after 500ms)

**Infrastructure**
- Multi-stage Dockerfile (builder + runtime stages) with non-root `appuser`, HEALTHCHECK directive, and ODBC driver installation
- `.dockerignore` file to reduce build context size

**Testing**
- 144 backend unit tests covering: Settings validation (21), Pydantic schemas (42), enums (21), rate limiting (8), RBAC service (12), settings service (17), plus existing service tests
- 26 new frontend tests: ErrorBoundary (8), ToastContext (10), useDebounce (8)
- Total test count: 225 (144 backend + 81 frontend)

### Changed

- Search endpoint now returns `page` and `page_size` fields in `SearchResponse` schema
- Backend Docker image reduced in size via multi-stage build (only runtime dependencies in final image)
- `App.tsx` wraps routes with `ErrorBoundary` for graceful error handling
- `main.tsx` wraps app with `ToastProvider` for global notification support

### Fixed

- Search pagination: replaced hardcoded `.limit(20)` with proper OFFSET/LIMIT using query parameters
- Modal focus trap: auto-focus gated to initial open only (prevents focus stealing during form input)

---

## [1.0.0] - 2026-03-19

### Added

- Initial release of AssuranceNet Document Management System
- FastAPI backend with document upload, download, versioning, and PDF conversion
- React 18 + TypeScript frontend with MSAL authentication
- Azure Bicep infrastructure (19 modules, 5 resource groups)
- FSIS demo data seeding (8 investigations, 10 document records)
- OpenTelemetry + Azure Monitor instrumentation
- RBAC system with 5 roles and 15 permissions
- PDF merge with FSIS type-based ordering
- Audit logging (NIST 800-53 AU-2/AU-3 compliant)
- Server-side search across investigations and documents
