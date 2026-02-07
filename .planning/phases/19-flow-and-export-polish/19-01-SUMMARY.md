---
phase: 19-flow-and-export-polish
plan: 01
subsystem: ui
tags: [navigation, breadcrumb, caching, localStorage, sessionStorage]
requires:
  - phase: 18
    provides: "Profile page tab restructure"
provides:
  - "Split nav layout on preview page (top: Return to Builder + breadcrumb, bottom: Classify + Export)"
  - "Step indicator breadcrumb showing Builder > Preview > Classify with current step highlighted"
  - "Return to Builder navigation from preview and classification screens"
  - "Classification result caching in localStorage with JD hash invalidation"
  - "Stale warning banner when JD edited after classifying"
  - "classify-complete event dispatched by classify.js for cache write"
affects: [19-02, 19-03]
tech-stack:
  added: []
  patterns: ["sessionStorage navigation flags (jdb_return_to_profile, jdb_return_to_classify)", "localStorage classification cache with JD hash", "CustomEvent for cross-module communication (classify-complete)"]
key-files:
  created: []
  modified: [static/js/export.js, static/js/main.js, static/js/classify.js, templates/index.html, static/css/classify.css]
key-decisions:
  - "Use sessionStorage flags for navigation intent (return to profile vs classify)"
  - "Cache classification results with JD hash to detect stale cache"
  - "Use CustomEvent (classify-complete) to decouple cache write from classification logic"
  - "Show stale warning banner instead of auto-invalidating to preserve user results"
patterns-established:
  - "Navigation via sessionStorage flags + reload preserves state from localStorage"
  - "Hash-based cache invalidation using btoa(JSON.stringify(selections))"
  - "CustomEvent dispatch for cross-module state synchronization"
duration: 18min
completed: 2026-02-07
---

# Phase 19 Plan 01: Navigation Wiring and Classification Caching Summary

**Complete navigation flow between Builder, Preview, and Classification screens with intelligent result caching and stale detection**

## Performance

- **Duration:** 18 min
- **Started:** 2026-02-07T16:01:35Z
- **Completed:** 2026-02-07T16:19:35Z
- **Tasks:** 2
- **Files modified:** 5

## Accomplishments

- Full navigation loop working: Builder → Preview → Classify → Builder with state preservation
- Classification results cached in localStorage to avoid redundant API calls
- Stale detection shows warning when JD changes after classifying
- Return to Builder buttons on both preview and classification screens
- classify-complete event enables cache write without tight coupling

## Task Commits

Each task was committed atomically:

1. **Task 1: Redesign preview page with split nav layout and step indicator breadcrumb** - `f2d2050` (feat) - *completed in prior session*
2. **Task 2: Wire navigation handlers, classification caching, stale detection, and classify-complete event** - `2eb07af` (feat)

**Plan metadata:** *to be committed after SUMMARY.md creation*

## Files Created/Modified

- `static/js/export.js` - Renamed backToEdit to returnToBuilder, added classifyFromPreview method, bound preview navigation buttons
- `static/js/main.js` - Added jdb_return_to_classify handler, classification cache check in Step 5, classify-complete listener, stale detection subscriber
- `static/js/classify.js` - Dispatch classify-complete event after renderResults
- `templates/index.html` - Added classify-stale-warning banner and Return to Builder button in classify section
- `static/css/classify.css` - Added stale warning banner styles

## Decisions Made

**sessionStorage navigation flags:** Used jdb_return_to_profile and jdb_return_to_classify flags to communicate navigation intent across page reloads. This preserves existing localStorage state while controlling which screen to show.

**JD hash for cache invalidation:** Used `btoa(JSON.stringify(selections))` as cache key. When selections change, hash changes, triggering stale warning. Simple and reliable.

**CustomEvent for cache write:** classify-complete event allows main.js to write cache without modifying classify.js internals. Maintains separation of concerns.

**Stale warning vs auto-invalidate:** Chose to show warning banner instead of silently clearing cache. Preserves user's classification results while alerting them to potential staleness.

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 1 - Bug] Fixed export button ID references in export.js**
- **Found during:** Task 2 (updating export.js listeners)
- **Issue:** downloadPDF and downloadDOCX methods referenced old export-btn ID instead of new preview-export-btn
- **Fix:** Updated getElementById calls to use preview-export-btn
- **Files modified:** static/js/export.js
- **Verification:** Export dropdown targets correct button element
- **Committed in:** 2eb07af (part of Task 2 commit)

---

**Total deviations:** 1 auto-fixed (1 bug)
**Impact on plan:** Bug fix necessary for export functionality. No scope creep.

## Issues Encountered

None - plan executed smoothly. Cache-hit listener was already implemented in classify.js from Phase 20 work, which simplified integration.

## User Setup Required

None - no external service configuration required.

## Next Phase Readiness

**Ready for Plan 19-02 (Coaching Panel):** Classification caching infrastructure complete. classify-complete event available for coaching panel to detect classification state changes.

**Ready for Plan 19-03 (Export Classifications):** Classification results stored in currentAllocation and localStorage cache, ready for export integration.

**Note:** Plan 19-02 modifies static/js/classify.js for coaching panel. This plan only added classify-complete event dispatch, no conflicts expected.

---
*Phase: 19-flow-and-export-polish*
*Completed: 2026-02-07*

## Self-Check: PASSED

All key files exist on disk:
- static/js/export.js ✓
- static/js/main.js ✓

All commits present in git log:
- 2eb07af feat(19-01) ✓
- f2d2050 feat(19-01) ✓
