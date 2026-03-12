---
phase: 28-navigation-preview-modal-selections-drawer
plan: 02
subsystem: ui
tags: [modal, preview, export, javascript, css, client-side-assembly]

# Dependency graph
requires:
  - phase: 28-01
    provides: build-nav-bar with nav-preview-jd button that dispatches open-preview-modal CustomEvent
  - phase: 27-02
    provides: abilities/knowledge IDs using filtered-array positions from profile.skills.statements
  - phase: 27-01
    provides: positionTitle in store state; overview section in profile
provides:
  - In-page modal overlay (#jd-preview-modal) that opens over the Build step without page navigation
  - Client-side JD assembly (assembleJDPreview) rendering all 8 sections from store selections
  - Return to Builder, Advance to Classify, Export PDF, Export Word buttons
  - Keyboard (Escape) and overlay-click dismissal
affects:
  - 28-03 (selections drawer — z-index must not conflict with modal z-index 1000)

# Tech tracking
tech-stack:
  added: []
  patterns:
    - Client-side HTML assembly from store selections without API call for preview
    - Modal open/close via classList.add/remove('hidden') with body.modal-open for scroll lock
    - CustomEvent cross-module communication (open-preview-modal dispatched in main.js, listened in export.js)
    - Nullable btn guard pattern: downloadPDF/downloadDOCX work whether called from modal or old preview page

key-files:
  created: []
  modified:
    - templates/index.html
    - static/js/export.js
    - static/css/main.css

key-decisions:
  - "assembleJDPreview() is client-side only — no API call needed for visual preview"
  - "core_competencies text from profile.reference_attributes.core_competencies[idx] (plain strings)"
  - "abilities/knowledge text from filtered profile.skills.statements by source_attribute (matches 27-02 ID scheme)"
  - "downloadPDF/downloadDOCX btn nullable — preview-export-btn only exists on old showPreview() page"
  - "openPreviewModal() caches buildExportRequest() result so PDF/Word downloads work immediately"

patterns-established:
  - "Preview is client-side HTML assembly from store state — fast, no spinner needed"
  - "Modal overlay at z-index 1000; build-nav-bar is z-index 40 — no conflict"

# Metrics
duration: 3min
completed: 2026-03-12
---

# Phase 28 Plan 02: Preview Modal Summary

**In-page JD preview modal with client-side assembly, 4 action buttons, and correct core_competencies/abilities/knowledge data lookups**

## Performance

- **Duration:** 3 min
- **Started:** 2026-03-12T15:57:46Z
- **Completed:** 2026-03-12T16:00:58Z
- **Tasks:** 2
- **Files modified:** 3

## Accomplishments
- Added `#jd-preview-modal` overlay to index.html with header (Return to Builder), scrollable body, footer (Advance to Classify, Export PDF, Export Word)
- Implemented `assembleJDPreview()` in exportModule for client-side JD assembly: title/NOC/lead from profile, positionTitle from store, overview from generation module, all 8 sections with correct data lookups
- Wired `open-preview-modal` event listener in `initExport()` linking the nav bar button (28-01) to the modal
- All 4 buttons functional: Return to Builder closes modal, Advance to Classify calls goToStep(3), Export PDF/Word trigger downloads
- Escape key and overlay click also close the modal
- Body scroll locked (`modal-open` class) while modal is open

## Task Commits

Each task was committed atomically:

1. **Task 1: Add preview modal HTML to index.html** - `1d26f69` (feat)
2. **Task 2: Implement modal open/close logic and JD assembly in export.js, add modal CSS** - `551c635` (feat)

## Files Created/Modified
- `templates/index.html` - Added #jd-preview-modal div with overlay, container, header, body, footer
- `static/js/export.js` - Added assembleJDPreview(), _escapeHtml(), openPreviewModal(), closePreviewModal(); wired event listeners in initExport(); fixed nullable btn in downloadPDF/downloadDOCX
- `static/css/main.css` - Added .jd-preview-modal*, .preview-jd__* styles and body.modal-open

## Decisions Made
- `assembleJDPreview()` is fully client-side: no fetch call, instant rendering, no loading state needed
- `core_competencies` uses `profile.reference_attributes.core_competencies[idx]` (plain strings, not statement objects)
- `abilities` and `knowledge` use filtered sub-array from `profile.skills.statements` by `source_attribute` — consistent with 27-02 ID scheme
- `openPreviewModal()` catches `buildExportRequest()` errors so preview still opens even if export data cannot be prepared (e.g. missing profile fields)

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 1 - Bug] Fixed downloadPDF/downloadDOCX crashing when called from modal**
- **Found during:** Task 2 (wiring Export PDF/Word buttons)
- **Issue:** Both download methods start with `const btn = document.getElementById('preview-export-btn'); if (!btn || !this.currentExportData) return;` — `preview-export-btn` only exists on the old `showPreview()` page, not in the modal. Calling from modal would silently abort downloads.
- **Fix:** Separated the guard: gate only on `!this.currentExportData`, make `btn` nullable, use optional chaining for classList/querySelector, guard `if (btn)` in finally blocks.
- **Files modified:** `static/js/export.js`
- **Committed in:** `551c635` (Task 2 commit)

---

**Total deviations:** 1 auto-fixed (Rule 1 - Bug)
**Impact on plan:** Essential for Export PDF/Word buttons to work from the modal. No scope creep.

## Issues Encountered
None.

## User Setup Required
None - no external service configuration required.

## Next Phase Readiness
- Preview modal is fully wired; `open-preview-modal` event from 28-01 now has a handler
- Export PDF/Word work from modal (requires backend PDF/DOCX endpoints to be available)
- `z-index: 1000` for modal; build-nav-bar is `z-index: 40` — no conflict with 28-03 selections drawer
- No blockers for 28-03

---
*Phase: 28-navigation-preview-modal-selections-drawer*
*Completed: 2026-03-12*
