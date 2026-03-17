---
phase: 06-l1-interactivity
plan: 01
subsystem: ui
tags: [fastapi, jinja2, sqlite, javascript, html, filter, search]

# Dependency graph
requires:
  - phase: 05-l1-card-grid
    provides: careers.html card grid with .card-col elements and /careers route

provides:
  - Job Function dropdown filter on /careers page (22 functions + All Functions default)
  - Keyword search input filtering by job family name and job title keywords
  - Client-side applyFilters JS (no page reload, intersection logic for both filters)
  - data-function, data-name, data-titles attributes on each .card-col element
  - no-results message when zero cards match

affects: [07-l2-job-family, 08-l3-job-title]

# Tech tracking
tech-stack:
  added: []
  patterns:
    - "Client-side filtering via data attributes + inline IIFE JavaScript"
    - "titles_json: JSON array of lowercase title strings embedded in data-titles attribute"
    - "Filter intersection: both dropdown value AND keyword must match to show a card"

key-files:
  created: []
  modified:
    - ps_careers_site/main.py
    - ps_careers_site/templates/careers.html

key-decisions:
  - "Used data-titles attribute with JSON array over /api/families endpoint — simpler for v1, avoids extra HTTP round-trip"
  - "Filter intersection logic: matchFn AND matchKw — user selecting both controls narrows results"
  - "Titles fetched via GROUP_CONCAT with ||| separator then split server-side — avoids quoting complexity"

patterns-established:
  - "Data-attribute filtering: embed filter keys on DOM elements, JS reads dataset.* properties"
  - "IIFE wrapper for inline filter scripts to avoid global namespace pollution"

requirements-completed: [L1-04, L1-05]

# Metrics
duration: 12min
completed: 2026-03-17
---

# Phase 6 Plan 1: L1 Interactivity Summary

**Client-side Job Function dropdown (22 values) and keyword search bar added to /careers page using data attributes and inline IIFE JavaScript — no page reload, intersection filtering.**

## Performance

- **Duration:** 12 min
- **Started:** 2026-03-17T20:46:42Z
- **Completed:** 2026-03-17T20:58:00Z
- **Tasks:** 2
- **Files modified:** 2

## Accomplishments

- `/careers` route now queries and passes `job_functions` (22 distinct values) and `titles_json` per family to template
- `careers.html` filter bar renders a Job Function `<select>` and keyword `<input>` above the card grid
- Each `.card-col` carries `data-function`, `data-name`, and `data-titles` attributes for client-side matching
- Inline `applyFilters` IIFE hides/shows cards on `change` and `input` events with intersection logic
- `no-results` div surfaces when zero cards match both active filters

## Task Commits

Each task was committed atomically:

1. **Task 1: Update GET /careers route in main.py** - `81b2741` (feat)
2. **Task 2: Add filter bar and JS to careers.html** - `284e883` (feat)

**Plan metadata:** (docs commit — see below)

## Files Created/Modified

- `ps_careers_site/main.py` - Added `job_functions` query, `titles_by_slug` build, `titles_json` field on each family dict, passes `job_functions` to template
- `ps_careers_site/templates/careers.html` - Added filter bar HTML, data attributes on `.card-col`, `no-results` div, inline `applyFilters` IIFE

## Decisions Made

- Used data-titles attribute (JSON array embedded in HTML) over a lightweight `/api/families` endpoint — simpler for v1, no extra HTTP round-trip needed.
- Titles concatenated server-side using GROUP_CONCAT with `|||` separator to avoid JSON quoting complexity at the SQL layer.
- Filter logic uses intersection (matchFn AND matchKw) — selecting a function AND typing a keyword shows only cards satisfying both.

## Deviations from Plan

None — plan executed exactly as written. Task 1's main.py changes were pre-applied in the prior session (main.py was already in the modified state); Task 2 added the missing inline JavaScript and `no-results` div to careers.html.

## Issues Encountered

None. Both automated verification checks passed on first run.

## User Setup Required

None — no external service configuration required.

## Next Phase Readiness

- L1 page fully interactive: filter + search work client-side with no reload
- Ready for Phase 7: L2 job family detail page (`/careers/{family-slug}`)
- No blockers

---
*Phase: 06-l1-interactivity*
*Completed: 2026-03-17*
