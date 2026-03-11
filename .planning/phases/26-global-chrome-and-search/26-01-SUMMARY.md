---
phase: 26-global-chrome-and-search
plan: 01
subsystem: ui
tags: [html, css, javascript, design-tokens, chrome, government-of-canada, stepper, sidebar]

requires:
  - phase: 25-export-and-polish
    provides: Stable v5.0 app shell with index.html, main.css, main.js, sidebar.js baseline

provides:
  - Government of Canada identity header (gc-identity-header) with maple leaf flag and bilingual org name
  - Dark navy app bar with JD Builder 1.0 badge, truncated session ID, Audit Trail count badge, Reset button
  - Row of 5 coloured data source pills linking to NOC, CAF, OCHRO, O*NET SOC, OaSIS
  - v5.1 stepper with correct labels: Search, Build, Classify, Generate, Export
  - Right-edge vertical Selections tab toggling sidebar
  - Compliance framework paragraph above footer
  - Dark footer with JobForge branding and Canada wordmark
  - O*NET attribution below footer
  - v5.1 CSS design tokens (--app-bar-bg, --footer-bg, stepper tokens, pill colours)
  - getOrCreateSessionId() persisting 12-char UUID in localStorage
  - store.subscribe audit-count badge updating in real time
  - Reset button clearing session and reloading

affects:
  - 26-02 (global search panel uses same chrome shell)
  - 27-build-tab (Build step 2 UI lives inside this chrome)
  - 28-classify-tab (Classify step 3 UI lives inside this chrome)
  - 29-generate-tab (Generate step 4 UI lives inside this chrome)
  - 30-export-tab (Export step 5 UI lives inside this chrome)

tech-stack:
  added: []
  patterns:
    - CSS design tokens in :root for all v5.1 chrome colours
    - CHROME-XX annotation comments matching requirement IDs
    - Atomic JS: session ID stored in localStorage with crypto.randomUUID()

key-files:
  created: []
  modified:
    - templates/index.html
    - static/css/main.css
    - static/js/main.js
    - static/js/sidebar.js

key-decisions:
  - "Step mapping: search-complete event stays on step 1 (not step 2) — search results are still on Search screen"
  - "profile-loaded event advances to step 2 (Build) — profile view is the Build screen"
  - "canAccessStep(2) requires currentProfile (not search results) — Build means you have a profile"
  - "Selections tab hides old sidebar-toggle entirely via display:none rather than removing DOM element"
  - "compliance-bar and onet-attribution placed outside <main> to span full width"

patterns-established:
  - "Chrome elements use BEM-style class names with CHROME-XX comments for traceability"
  - "Design tokens prefixed with --app-bar-*, --pill-*, --stepper-*, --footer-* for v5.1 chrome namespace"
  - "goToStep() inline HTML calls use v5.1 step numbers: Re-classify=3, Return to Builder=2"

duration: 5min
completed: 2026-03-11
---

# Phase 26 Plan 01: Global Chrome Layout Summary

**v5.1 GoC identity header + dark navy app bar + 5 coloured data pills + v5.1 stepper (Search/Build/Classify/Generate/Export) + right-edge Selections tab + compliance bar + dark footer wired with live session ID and audit count**

## Performance

- **Duration:** 5 min
- **Started:** 2026-03-11T20:14:18Z
- **Completed:** 2026-03-11T20:19:13Z
- **Tasks:** 2/2
- **Files modified:** 4

## Accomplishments

- Full v5.1 chrome DOM (CHROME-01 through CHROME-08) added to index.html replacing old gc-header and gc-footer
- CSS design tokens added to :root; chrome CSS classes for all 8 elements added to main.css
- Stepper labels updated to v5.1 spec (Search/Build/Classify/Generate/Export) with remapped navigateToStep() switch and canAccessStep() guards
- Live session ID (12-char UUID, truncated to 8 chars) displayed in app bar; persists across reloads
- Audit Trail badge increments via store.subscribe on every selection change
- Selections (N) tab on right edge toggles sidebar and syncs count via updateSidebar()
- All inline goToStep() calls in index.html updated to v5.1 step numbers

## Task Commits

Each task was committed atomically:

1. **Task 1: Replace chrome HTML in index.html and add design tokens + chrome CSS in main.css** - `f95735c` (feat)
2. **Task 2: Wire JS for session ID, audit count, selections count, reset button, and stepper remapping** - `7ebe0f5` (feat)

## Files Created/Modified

- `templates/index.html` - Replaced gc-header with gc-identity-header + app-bar + data-sources-bar; updated stepper labels; added selections-tab, compliance-bar, app-footer, onet-attribution; fixed goToStep() inline calls
- `static/css/main.css` - Added v5.1 design tokens to :root; added chrome CSS (gc-identity-header, app-bar, data-sources-bar, data-source-pill variants, selections-tab, compliance-bar, app-footer, onet-attribution); updated stepper number colours to use design tokens
- `static/js/main.js` - Added getOrCreateSessionId(), Reset button handler, remapped navigateToStep() switch (v5.1), updated canAccessStep(), added audit-count store.subscribe, fixed goToStep(5)->goToStep(3) in returnToClassify handler
- `static/js/sidebar.js` - Hides old sidebar-toggle; wires selections-tab-btn click; adds selections-tab-count update at end of updateSidebar()

## Decisions Made

- search-complete event keeps stepper at step 1 (Search results are still the Search screen in v5.1)
- profile-loaded event advances stepper to step 2 (Build — showing the profile is the Build step)
- canAccessStep(2=Build) requires window.currentProfile (not just having search results)
- canAccessStep(3=Classify) requires profile + selections or lead statement (same logic as old step 5)
- selections-tab replaces sidebar-toggle via hide+new-wire approach (DOM element preserved, display:none)
- compliance-bar text placed both in welcome section (existing, left alone) and as full-width bar above footer

## Deviations from Plan

None - plan executed exactly as written.

## Issues Encountered

None.

## User Setup Required

None - no external service configuration required.

## Next Phase Readiness

- v5.1 chrome shell complete and verified (app loads, Python OK)
- All 8 CHROME requirements (CHROME-01 to CHROME-08) in HTML and CSS
- Stepper navigation remapped to v5.1 — subsequent phases can call goToStep(2) for Build, goToStep(3) for Classify, etc.
- Session ID infrastructure ready for audit trail use in later phases
- No regressions introduced — existing search, profile loading, classify, sidebar all preserved

---
*Phase: 26-global-chrome-and-search*
*Completed: 2026-03-11*
