---
phase: 28-navigation-preview-modal-selections-drawer
plan: 01
subsystem: ui
tags: [navigation, build-nav-bar, fixed-footer, classify, generate, css, javascript]

# Dependency graph
requires:
  - phase: 27-build-page-redesign
    provides: profile tabs container and tab panels that the build nav bar sits beneath
  - phase: 26-global-chrome-and-search
    provides: jdStepper.goToStep() API used by all nav buttons
provides:
  - Fixed-bottom 3-button navigation bar on the Build step (Back to Search / Preview JD / Continue to Classification)
  - Back to Edit + Continue to Generate buttons on the Classify page
  - Regenerate + Continue buttons on the Generate page
  - #action-bar permanently hidden (style="display:none") while keeping DOM refs intact
affects:
  - 28-02 (preview modal — nav-preview-jd dispatches open-preview-modal event)
  - 28-03 (selections drawer — build nav bar z-index must not conflict)

# Tech tracking
tech-stack:
  added: []
  patterns:
    - Fixed-bottom nav bar uses position:fixed + z-index:40, hidden class toggled by navigateToStep
    - Nav buttons dispatch CustomEvents (open-preview-modal) for cross-module communication
    - All nav buttons wired centrally in DOMContentLoaded after initStepper()

key-files:
  created: []
  modified:
    - templates/index.html
    - static/js/main.js
    - static/css/main.css

key-decisions:
  - "build-nav-bar hidden with CSS class, not display:none — so show/hide via classList is clean"
  - "action-bar permanently hidden with style='display:none' — classList ops still work without visual effect"
  - "Back to Search navigates without clearing selections (resetSelectionsForProfile fires only on card click)"
  - "nav-preview-jd dispatches open-preview-modal CustomEvent — preview modal (28-02) listens for it"
  - "classify-nav-actions--always added outside #classify-complete so nav buttons show even before classification finishes"

patterns-established:
  - "navigateToStep manages build-nav-bar visibility for all 5 cases — no other code should toggle it"
  - "handleResultClick also shows build-nav-bar (replaces old actionBar show call)"

# Metrics
duration: 2min
completed: 2026-03-12
---

# Phase 28 Plan 01: Navigation Bar Summary

**Fixed-bottom 3-button build nav bar + classify/generate page nav buttons wired to goToStep() API**

## Performance

- **Duration:** 2 min
- **Started:** 2026-03-12T15:51:16Z
- **Completed:** 2026-03-12T15:54:01Z
- **Tasks:** 2
- **Files modified:** 3

## Accomplishments
- Added `#build-nav-bar` fixed-footer with Back to Search, Preview Job Description, and Continue to Classification buttons visible on every Build tab
- Wired all nav buttons in `main.js`: Back to Search preserves selections, Preview JD dispatches `open-preview-modal` CustomEvent, Continue to Classification calls goToStep(3)
- Added Classify page nav buttons (Back to Edit + Continue to Generate) in two locations: inside `#classify-complete` and always-visible outside it
- Added Generate page nav buttons (Regenerate + Continue) after `.overview-actions`
- `#action-bar` permanently hidden with `style="display:none"` while keeping DOM references intact
- CSS: `.build-nav-bar` fixed-footer, `.classify-nav-actions`, `.generate-nav-actions` layout styles

## Task Commits

Each task was committed atomically:

1. **Task 1: Add navigation bar HTML and nav button HTML to index.html** - `fba5df2` (feat)
2. **Task 2: Wire navigation buttons in main.js and add CSS styles** - `23037c3` (feat)

## Files Created/Modified
- `templates/index.html` - Added #build-nav-bar footer (3 buttons), classify nav buttons (×2 locations), generate nav buttons; #action-bar display:none
- `static/js/main.js` - Wired all nav buttons; navigateToStep cases 1-5 manage build-nav-bar visibility; handleResultClick shows build-nav-bar instead of actionBar
- `static/css/main.css` - Added .build-nav-bar fixed-footer styles, .classify-nav-actions layout, .generate-nav-actions layout

## Decisions Made
- `#action-bar` gets `style="display:none"` rather than being deleted — other JS code holds a reference (`actionBar` variable) and calls `.classList.add/remove('hidden')` on it; those calls are now harmless
- `back to search` navigates without clearing selections because `resetSelectionsForProfile` only fires in `handleResultClick` (card click), not on stepper navigation — this is already the correct behavior
- `nav-preview-jd` dispatches `open-preview-modal` CustomEvent rather than calling export.js directly — keeps nav wiring decoupled from preview implementation (28-02)
- Added `classify-nav-actions--always` outside `#classify-complete` so navigation buttons are visible even while classification is still running or if it errors

## Deviations from Plan

None - plan executed exactly as written.

## Issues Encountered
None.

## User Setup Required
None - no external service configuration required.

## Next Phase Readiness
- Build nav bar is in place; `open-preview-modal` event is dispatched but has no listener yet — 28-02 implements the preview modal that listens for this event
- All goToStep() wiring is correct; stepper navigation from classify/generate pages now works
- No blockers for 28-02 or 28-03

---
*Phase: 28-navigation-preview-modal-selections-drawer*
*Completed: 2026-03-12*
