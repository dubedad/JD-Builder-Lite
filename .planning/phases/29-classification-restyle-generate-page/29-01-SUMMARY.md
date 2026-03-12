---
phase: 29-classification-restyle-generate-page
plan: 01
subsystem: ui
tags: [html, css, classification, v5.1, chrome, badges, tbs]

# Dependency graph
requires:
  - phase: 28-navigation-preview-modal-selections-drawer
    provides: nav buttons (classify-back-to-edit-2, classify-continue-generate-2, classify-nav-always) wired in main.js
provides:
  - Restyled #classify-section in index.html with v5.1 occupation header card
  - classify.css v5.1 section: header card, badges, TBS card, CTA button, post-analysis containers
  - Empty DOM containers (classify-top-result, classify-alignment, classify-key-evidence, classify-caveats, classify-alternatives, classify-next-step) ready for JS population in 29-03
affects:
  - 29-03 (classify.js wiring — targets new container IDs and analyze button)

# Tech tracking
tech-stack:
  added: []
  patterns:
    - "Occupation header card pattern: dark navy flex card with icon + title/subtitle + badge strip (matches Build page header)"
    - "Badge component: .badge base class + modifier variants (dadm-compliant green, full-provenance purple)"
    - "TBS reference card: 3-column dark navy grid with step label/title/desc pattern"
    - "Orange CTA button: .btn--cta-orange for primary action prompting user to trigger async analysis"

key-files:
  created: []
  modified:
    - templates/index.html
    - static/css/classify.css

key-decisions:
  - "classify-status-badge starts hidden in v5.1 (was visible by default) — user sees TBS card + CTA first, not loading state"
  - "Legacy panels (recommendations-panel, evidence-panel) kept in hidden .classify-layout div — backward compat for classify.js renderRecommendationCards()"
  - "classify-back-to-edit and classify-continue-generate (no -2 suffix) placed in hidden div inside classify-complete — main.js uses null guard (if btn) so safe, but preserved for completeness"

patterns-established:
  - "Post-analysis containers pattern: empty div with ID + .hidden class, populated by JS in later plan"

# Metrics
duration: 2min
completed: 2026-03-12
---

# Phase 29 Plan 01: Classification Restyle Summary

**#classify-section replaced with v5.1 chrome: dark navy occupation header card with gear icon + DADM Compliant (green) + Full Provenance (purple) badges, TBS 3-step dark navy card (§4.1.1/§4.1.2/§4.1.3), orange Analyze CTA button, and empty post-analysis containers ready for 29-03 JS wiring**

## Performance

- **Duration:** ~2 min
- **Started:** 2026-03-12T21:12:03Z
- **Completed:** 2026-03-12T21:14:20Z
- **Tasks:** 2
- **Files modified:** 2

## Accomplishments

- Replaced 83-line old classify-section HTML with 137-line v5.1 structure preserving all 17 existing element IDs
- Added 326 lines of new v5.1 CSS (header card, badge component, TBS card, orange CTA, top result card, alignment/evidence/caveats/alternatives/next-step containers) prepended to classify.css
- All post-analysis DOM containers exist with correct IDs for plan 29-03 to populate via classify.js

## Task Commits

Each task was committed atomically:

1. **Task 1: Replace #classify-section HTML with v5.1 layout** - `8edfae6` (feat)
2. **Task 2: Add CSS for header card, badges, TBS card, and post-analysis section containers** - `0a2a859` (feat)

**Plan metadata:** (see final commit below)

## Files Created/Modified

- `templates/index.html` - #classify-section replaced: occupation header card, TBS 3-step card, CTA button, post-analysis containers, all existing IDs preserved
- `static/css/classify.css` - v5.1 styles prepended: 16 new CSS rule sets covering header card, badge variants, TBS card, CTA, result card, alignment, evidence/caveat bullets, alternatives, next-step, responsive breakpoints

## Decisions Made

- `classify-status-badge` starts with `hidden` class in v5.1 (was visible/without hidden in old HTML). The classify.js `showLoading()` removes `hidden` — correct behavior since user sees TBS card first, then clicks Analyze.
- Legacy `recommendations-panel` / `evidence-panel` kept inside a `hidden` div (`.classify-layout.hidden`) for backward compatibility with existing `renderRecommendationCards()` in classify.js. Plan 29-03 transitions to new containers.
- `classify-back-to-edit` and `classify-continue-generate` (no `-2` suffix) preserved in a `hidden` div inside `classify-complete`. Main.js NAV-04 uses null guards so absence would be safe, but presence maintains full spec compliance.

## Deviations from Plan

None - plan executed exactly as written.

## Issues Encountered

None.

## User Setup Required

None - no external service configuration required.

## Next Phase Readiness

- Plan 29-02 (Generate page restyle) can proceed independently — no dependency on 29-01 output
- Plan 29-03 (classify.js wiring) requires 29-01 DOM containers — all containers now exist with correct IDs
- `classify-analyze-btn` (#classify-analyze-btn) ready for click handler in 29-03
- All post-analysis container IDs confirmed: classify-top-result, classify-alignment, classify-key-evidence, classify-caveats, classify-alternatives, classify-next-step

---
*Phase: 29-classification-restyle-generate-page*
*Completed: 2026-03-12*
