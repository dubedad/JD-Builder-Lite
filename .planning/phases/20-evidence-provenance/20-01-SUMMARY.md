---
phase: 20-evidence-provenance
plan: 01
subsystem: ui
tags: [javascript, provenance, accessibility, aria, evidence]

# Dependency graph
requires:
  - phase: 17-ui-layer
    provides: CSS classes for provenance tree in evidence.css
provides:
  - Expandable three-level provenance tree (Recommendation -> Definition -> TBS Source)
  - ARIA-compliant expand/collapse interaction
  - Visual hierarchy with connecting lines and icons
affects: [20-02, 20-03, evidence-display, classification-ui]

# Tech tracking
tech-stack:
  added: []
  patterns:
    - "Expandable tree structure with inline onclick handlers for aria-expanded toggling"
    - "Three-level provenance chain display pattern"

key-files:
  created: []
  modified:
    - static/js/classify.js

key-decisions:
  - "Use inline onclick for expand button to avoid additional event binding complexity"
  - "Show full definition text on expand (from provenance.definition or group name fallback)"
  - "Display scraped_at date as metadata under TBS link for transparency"

patterns-established:
  - "Provenance tree uses .provenance-tree-item structure with icon, label, and value pattern"
  - "Expandable sections use aria-expanded attribute toggled by button click"

# Metrics
duration: 4min
completed: 2026-02-07
---

# Phase 20 Plan 01: Provenance Tree Upgrade Summary

**Expandable three-level provenance tree showing Recommendation -> Definition -> TBS Source chain with ARIA-compliant collapse/expand**

## Performance

- **Duration:** 4 min
- **Started:** 2026-02-07T15:47:02Z
- **Completed:** 2026-02-07T15:51:04Z
- **Tasks:** 1
- **Files modified:** 1

## Accomplishments
- Replaced flat provenance section with hierarchical tree structure
- Three-level chain: Recommendation (group + name) -> Definition (expandable) -> TBS Source (external link)
- ARIA-compliant expand/collapse with aria-expanded toggling
- Visual hierarchy using existing CSS classes from evidence.css (17-03)

## Task Commits

Each task was committed atomically:

1. **Task 1: Upgrade renderProvenanceSection to expandable tree (EVD-01)** - `b6db65d` (feat)

## Files Created/Modified
- `static/js/classify.js` - Replaced renderProvenanceSection() function to generate three-level provenance tree HTML using existing .provenance-tree CSS classes

## Decisions Made
- **Inline onclick handler:** Used inline `onclick` attribute for expand button to toggle aria-expanded, avoiding need for additional event listener binding in expandable sections
- **Definition text fallback:** When provenance.definition is unavailable, fallback to "{groupCode} - {groupName}" from OCCUPATIONAL_GROUP_NAMES lookup
- **Scraped date visibility:** Display provenance.scraped_at as metadata below TBS link for data freshness transparency

## Deviations from Plan

None - plan executed exactly as written.

## Issues Encountered

None - implementation was straightforward. The CSS classes were already well-structured from phase 17-03, making the integration seamless.

## User Setup Required

None - no external service configuration required.

## Next Phase Readiness

- Provenance tree rendering complete and functional
- Ready for phase 20-02 (evidence highlighting enhancements if planned)
- CSS from 17-03 proved well-designed for this use case
- No blockers identified

## Self-Check: PASSED

All files and commits verified.

---
*Phase: 20-evidence-provenance*
*Completed: 2026-02-07*
