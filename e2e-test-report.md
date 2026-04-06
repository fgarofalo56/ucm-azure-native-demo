# AssuranceNet E2E Test Report

**Date:** 2026-03-13
**Application:** AssuranceNet Document Management System
**URL:** https://yellow-field-05ae8b90f.2.azurestaticapps.net
**Tester:** Claude Code (Playwright MCP)
**Auth:** Microsoft Entra ID SSO (Frank Garofalo, Admin role)

---

## Summary

| Metric | Value |
|--------|-------|
| **Journeys Tested** | 10 |
| **Screenshots Captured** | 31 |
| **Pages Verified** | 10 (Dashboard, Investigations, Investigation Detail, Documents, File Explorer, Search, Audit Log, Administration, Help, Settings) |
| **Viewports Tested** | 3 (Mobile 375x812, Tablet 768x1024, Desktop 1440x900) |
| **UX Issues Found** | 3 |
| **Code Analysis Bugs** | 16 (3 critical, 7 high, 4 medium, 2 low) |
| **Issues Fixed During Testing** | 0 (all are findings for follow-up) |

---

## Per-Journey Breakdown

### 1. Dashboard (`/`)

**Status:** PASS

**Steps Tested:**
- Page load with welcome banner (USDA gradient)
- 4 stat cards: Total Investigations (32), Active (15), Total Documents (212), Pending Conversion (21)
- Bar chart: Documents by Investigation
- Donut chart: Document Status Distribution (Completed, Failed, Pending, Processing)
- Recent Activity section with audit log entries
- Recent Investigations table
- Dark mode rendering

**Screenshots:**
- `dashboard/01-dashboard-loaded.png` — Initial load
- `dashboard/02-dashboard-data-loaded.png` — After data renders
- `dashboard/03-dashboard-scrolled-down.png` — Bottom of page
- `dashboard/04-dashboard-full-page.png` — Full page capture
- `dashboard/05-dashboard-dark-mode.png` — Dark theme
- `dashboard/06-header-search-typing.png` — Search bar interaction

**Console Warnings:** 2 warnings from Recharts about chart dimensions (-1, -1) — non-blocking, occurs during initial render before container has size.

---

### 2. Investigations List & Create (`/investigations`)

**Status:** PASS (with UX findings)

**Steps Tested:**
- Page loads with 32 investigations in paginated table (20 per page)
- Status tabs: All (32), Active (15), Closed (5), Archived (0)
- Tab filtering works — Active tab shows only active investigations
- Search input filters by title/record ID (client-side)
- "New Investigation" button opens modal
- Modal form: Record ID (INVESTIGATION-##### format), Title, Description
- Submit button disabled when fields empty, enabled when filled
- Created INVESTIGATION-99999 "E2E Test Investigation - Automated" successfully
- New investigation appears at top of list

**Screenshots:**
- `investigations/01-investigations-list.png`
- `investigations/02-active-tab-filtered.png`
- `investigations/03-search-ecoli.png`
- `investigations/04-new-investigation-modal.png`
- `investigations/05-new-investigation-filled.png`
- `investigations/06-investigation-created.png`

**Findings:**
- **UX-001**: Tab counts recalculate from filtered results (see Issues section)
- **UX-002**: Client-side search only filters current page (see Issues section)

---

### 3. Investigation Detail & Documents (`/investigations/:id`)

**Status:** PASS

**Steps Tested:**
- Breadcrumb navigation: Dashboard > Investigations > Record ID
- Investigation header with title, status badge, record ID
- Documents tab with document list (14 documents for INVESTIGATION-10001)
- Document table columns: Name, Size, Type, Status, Modified, Actions
- Detail page for newly created INVESTIGATION-99999 (0 documents)

**Screenshots:**
- `investigations/07-investigation-detail.png` — INVESTIGATION-99999 detail
- `investigations/08-investigation-with-documents.png` — INVESTIGATION-10001 with 14 docs

---

### 4. File Explorer (`/explorer`)

**Status:** PASS

**Steps Tested:**
- Root view shows 2 investigation folders
- Breadcrumb shows "Root"
- Click folder navigates into it, shows UUID-based document subfolders
- File/folder icons differentiated
- Checkboxes for file selection
- Download and delete action buttons per file

**Screenshots:**
- `explorer/01-file-explorer-root.png`
- `explorer/02-investigation-folder-contents.png`

---

### 5. Search (`/search`)

**Status:** PASS

**Steps Tested:**
- Search input with autofocus
- Type filter tabs: All, Investigations, Documents
- Searched "E. coli" — returned 2 investigation results
- Results grouped by type with count headers
- Document results have checkboxes for batch operations
- Header search bar navigates to `/search?q=` with query pre-filled

**Screenshots:**
- `search/01-search-results.png` — "E. coli" results
- `search/02-header-search-dark-mode.png` — "salmonella" via header search in dark mode

---

### 6. Audit Log (`/audit`)

**Status:** PASS

**Steps Tested:**
- Page header with "Export" button
- Search input for user/resource/action
- Event type dropdown filter (All Events, auth.logout, document.batch upload, document.download, document.merge, investigation.update)
- Result filter dropdown (All Results, Success, Failure, Denied)
- Table with 1078 entries, 50 per page with pagination
- Filtered by "document.download" — showed 38 matching entries from multiple users
- Timestamps with relative time ("1 day ago", "in 34 minutes")

**Screenshots:**
- `audit/01-audit-log-page.png`
- `audit/02-filtered-by-event-type.png`

---

### 7. Administration (`/admin`)

**Status:** PASS (with finding)

**Steps Tested:**
- User table with columns: User, Roles, Status, Last Login, Actions
- 2 users displayed: one Viewer, one Administrator (Frank Garofalo)
- Both users Active status
- "Edit Roles" button opens modal
- Modal shows 5 roles: Administrator, Case Manager, Document Manager, Reviewer, Viewer
- Current role (Administrator) selected with checkmark
- Cancel and Save Roles buttons

**Screenshots:**
- `admin/01-admin-page.png`
- `admin/02-edit-roles-modal.png`

**Findings:**
- **UX-003**: First user row has blank name/email — only avatar placeholder and "Viewer" role badge visible

---

### 8. Help & Documentation (`/help`)

**Status:** PASS

**Steps Tested:**
- 3 tabs: FAQ, User Guide, Glossary
- **FAQ tab**: 8 accordion questions, expand/collapse works correctly
  - What is AssuranceNet?
  - What is FSIS?
  - How do I create an investigation?
  - How do I upload documents?
  - What is PDF conversion?
  - How do roles and permissions work?
  - How do I search for documents?
  - Where does the demo data come from?
- **User Guide tab**: 7 numbered step cards (Sign In, Dashboard, Investigations, Documents, PDF Merging, File Explorer, Audit Log)
- **Glossary tab**: Table with 10 FSIS terms (FSIS, HACCP, NRTE, STEC, NRP, COA, EST, SSOP, NOIE, SPS)
- FSIS data source disclaimer with link to fsis.usda.gov/science-data

**Screenshots:**
- `help/01-help-page.png` — FAQ tab
- `help/02-user-guide-tab.png` — User Guide tab

---

### 9. Settings (`/settings`)

**Status:** PASS

**Steps Tested:**
- **Appearance section**: Light/Dark/System theme selector with preview cards
- **User Profile section** (read-only): Full Name, Email, Account ID, Roles (Admin badge)
- **Notifications section**: 4 toggles (Document upload complete ON, Investigation updates ON, PDF conversion failures ON, Weekly summary OFF)
- **Application Info section**: App name, Version v0.1.0, Environment "production", API URL

**Screenshots:**
- `settings/01-settings-page.png` — Light mode
- `settings/02-dark-mode.png` — After switching to dark

---

### 10. Dark Mode & Header Search

**Status:** PASS

**Steps Tested:**
- Header dark mode toggle (moon icon) switches to dark theme
- All page elements adapt: sidebar, header, content area, cards, charts, tables
- Button label changes to "Switch to light mode" (sun icon)
- Settings page "Dark" option now selected
- Header search bar accepts text, Enter key navigates to `/search?q=<query>`
- Search results render correctly in dark mode
- Toggle back to light mode works

**Screenshots:**
- `settings/02-dark-mode.png` — Settings in dark mode
- `dashboard/05-dashboard-dark-mode.png` — Dashboard in dark mode
- `search/02-header-search-dark-mode.png` — Search results in dark mode

---

### 11. Responsive Testing

**Status:** PASS

**Viewports tested:**

| Viewport | Size | Sidebar | Layout | Notes |
|----------|------|---------|--------|-------|
| Mobile | 375x812 | Hamburger menu | Single column, stacked cards | All content accessible |
| Tablet | 768x1024 | Icon-only collapsed | 2-column grid for stats | Charts full-width |
| Desktop | 1440x900 | Full expanded with labels | 4-column stats, side-by-side charts | Optimal layout |

**Screenshots:**
- `responsive/01-mobile-dashboard.png` — Full page mobile
- `responsive/02-mobile-investigations.png` — Full page mobile investigations
- `responsive/03-tablet-dashboard.png` — Full page tablet
- `responsive/04-desktop-dashboard.png` — Full page desktop

---

## UX Issues Found During Testing

### UX-001: Tab counts recalculate from filtered results
- **Severity:** Medium
- **Page:** `/investigations`
- **Description:** When "All" tab is selected, counts show All:32, Active:15, Closed:5. When switching to "Active" tab, the counts change (e.g., All:25, Active:20). The counts appear to recalculate from the filtered subset rather than showing consistent global totals.
- **Expected:** Tab counts should remain stable regardless of which tab is selected, always reflecting the true global counts.
- **File:** `src/frontend/src/pages/InvestigationsListPage.tsx`

### UX-002: Client-side search only filters current page
- **Severity:** Medium
- **Page:** `/investigations`
- **Description:** Searching for "Salmonella" on the investigations list returns no results because the Salmonella investigation is on page 2. The client-side search only filters the 20 currently loaded items per page.
- **Expected:** Search should query the backend API with the search term to find results across all pages, or at minimum indicate that results may exist on other pages.
- **File:** `src/frontend/src/pages/InvestigationsListPage.tsx`

### UX-003: Admin user with blank name/email
- **Severity:** Low
- **Page:** `/admin`
- **Description:** The first user row in the Administration user table displays a "Viewer" role badge and "Active" status, but has no name or email — just an empty avatar placeholder. This user was likely auto-provisioned on first API call without proper display name extraction.
- **Expected:** All user rows should display name and email, or show "Unknown User" placeholder text.
- **File:** `src/frontend/src/pages/AdminPage.tsx` (display) / `src/backend/app/services/rbac_service.py` (provisioning)

---

## Code Analysis Findings (from static analysis)

### Critical (3)

| # | Description | File | Line |
|---|-------------|------|------|
| 1 | React list key anti-pattern using array index in DocumentUpload progress tracker | `src/frontend/src/components/documents/DocumentUpload.tsx` | 190 |
| 2 | React list key anti-pattern using array index in FAQ accordion | `src/frontend/src/pages/HelpPage.tsx` | 147 |
| 3 | Race condition in edit form — `editTitle`/`editDesc` initialized as empty string, may show blank on first edit click | `src/frontend/src/pages/InvestigationPage.tsx` | 54-57 |

### High (4 notable)

| # | Description | File | Line |
|---|-------------|------|------|
| 4 | No validation error messages shown to user when create investigation form fails | `src/frontend/src/pages/InvestigationsListPage.tsx` | 68-81 |
| 5 | setTimeout memory leak — timeout not cleared on unmount in copy-to-investigation toast | `src/frontend/src/pages/SearchPage.tsx` | 76,79 |
| 6 | setTimeout memory leak — same issue in FileExplorerPage | `src/frontend/src/pages/FileExplorerPage.tsx` | 94,97 |
| 7 | Missing null check on `investigation` before accessing `.title` in save handler | `src/frontend/src/pages/InvestigationPage.tsx` | 77-79 |

### Medium (4 notable)

| # | Description | File | Line |
|---|-------------|------|------|
| 8 | No loading indicator during title/description edit save — allows double-click submissions | `src/frontend/src/pages/InvestigationPage.tsx` | 77-92 |
| 9 | InvestigationPicker always fetches page 1 only — can't see investigations beyond first 20 | `src/frontend/src/components/ui/InvestigationPicker.tsx` | 25 |
| 10 | Browser `confirm()` for document delete — looks unprofessional, no undo option | `src/frontend/src/components/documents/DocumentList.tsx` | 223 |
| 11 | Selected document state persists when navigating between investigations | `src/frontend/src/pages/InvestigationPage.tsx` | 54-60 |

---

## Test Data Created

| Item | Details |
|------|---------|
| Investigation | INVESTIGATION-99999 "E2E Test Investigation - Automated" (id: `5f9ea097-5d21-4724-baeb-8728669e8bf3`) |
| Audit entries | Multiple `investigation.create` audit log entries from E2E testing |

---

## Screenshots Index

All saved to: `temp/e2e-screenshots/`

```
00-login-page.png

admin/
  01-admin-page.png
  02-edit-roles-modal.png

audit/
  01-audit-log-page.png
  02-filtered-by-event-type.png

dashboard/
  01-dashboard-loaded.png
  02-dashboard-data-loaded.png
  03-dashboard-scrolled-down.png
  04-dashboard-full-page.png
  05-dashboard-dark-mode.png
  06-header-search-typing.png

explorer/
  01-file-explorer-root.png
  02-investigation-folder-contents.png

help/
  01-help-page.png
  02-user-guide-tab.png

investigations/
  01-investigations-list.png
  02-active-tab-filtered.png
  03-search-ecoli.png
  04-new-investigation-modal.png
  05-new-investigation-filled.png
  06-investigation-created.png
  07-investigation-detail.png
  08-investigation-with-documents.png

responsive/
  01-mobile-dashboard.png
  02-mobile-investigations.png
  03-tablet-dashboard.png
  04-desktop-dashboard.png

search/
  01-search-results.png
  02-header-search-dark-mode.png

settings/
  01-settings-page.png
  02-dark-mode.png
```

---

## Recommendations

1. **Fix investigation search** — Make search query the backend API instead of filtering only the current page's 20 items
2. **Fix tab counts** — Ensure status tab counts always reflect global totals, not filtered subsets
3. **Fix React list keys** — Replace `idx` keys with stable IDs (file name/path for uploads, question text for FAQ)
4. **Add InvestigationPicker pagination** — Allow scrolling through all investigations or add search within the picker
5. **Replace browser confirm()** — Use a proper confirmation modal for document deletion
6. **Add form validation feedback** — Show inline error messages when investigation create form validation fails
7. **Clear setTimeout on unmount** — Store timeout IDs and clear in useEffect cleanup

---

*Generated with [Claude Code](https://claude.com/claude-code)*
