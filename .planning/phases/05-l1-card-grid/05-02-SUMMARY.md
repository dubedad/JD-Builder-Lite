---
phase: 05-l1-card-grid
plan: 02
subsystem: ui
tags: [fastapi, jinja2, sqlite, static-files, card-images]

# Dependency graph
requires:
  - phase: 05-01
    provides: careers.html template with card grid and CARD_IMAGE_STATIC structure needed

provides:
  - CARD_IMAGE_STATIC dict in main.py mapping 12 raw DB keys to hyphenated static filenames
  - SQL WHERE clause restricts /careers query to 12 card-image families only
  - image_file assignment uses CARD_IMAGE_STATIC.get() for normalized URL resolution

affects: [05-l1-card-grid, 06-l1-interactivity]

# Tech tracking
tech-stack:
  added: []
  patterns:
    - "CARD_IMAGE_STATIC normalization dict: maps raw DB values (with spaces/special chars) to filesystem-safe hyphenated filenames"
    - "SQL WHERE on card_image_key IS NOT NULL to scope grid to families with images"

key-files:
  created: []
  modified:
    - ps_careers_site/main.py

key-decisions:
  - "CARD_IMAGE_STATIC.get() used over string replacement — explicit mapping prevents accidental normalization errors"
  - "SQL WHERE scoped to card_image_key IS NOT NULL AND card_image_key != '' — intent is explicit; no silent row drops"

patterns-established:
  - "Static asset key normalization: raw DB key -> normalized filename via explicit dict lookup in route handler"

requirements-completed: [L1-01, L1-02, L1-03]

# Metrics
duration: 5min
completed: 2026-03-18
---

# Phase 05 Plan 02: L1 Card Grid Gap Closure Summary

**CARD_IMAGE_STATIC dict added to main.py with 12 raw-to-hyphenated filename mappings, fixing all 11 broken card background image 404 URLs on /careers**

## Performance

- **Duration:** ~5 min
- **Started:** 2026-03-18T00:38:00Z
- **Completed:** 2026-03-18T00:41:32Z
- **Tasks:** 1
- **Files modified:** 1

## Accomplishments

- Added CARD_IMAGE_STATIC dict (12 entries) after DB_PATH assignment in main.py
- Updated SQL WHERE clause from `job_family != ''` to `card_image_key IS NOT NULL AND card_image_key != ''` — scopes query explicitly to the 12 card-image families
- Replaced raw `row["card_image_key"] or None` assignment with `CARD_IMAGE_STATIC.get(row["card_image_key"])` for all 12 card image URLs
- All 5 plan verification checks pass: syntax, 12-entry count, no spaces in values, WHERE clause, dict lookup

## Task Commits

Each task was committed atomically:

1. **Task 1: Add CARD_IMAGE_STATIC dict and fix image_file mapping in main.py** - `3368ca2` (fix)

**Plan metadata:** (docs commit follows)

## Files Created/Modified

- `ps_careers_site/main.py` - Added CARD_IMAGE_STATIC dict, tightened SQL WHERE, replaced raw key assignment with dict lookup

## Decisions Made

- Used CARD_IMAGE_STATIC.get() (explicit dict) over string replacement to prevent accidental normalization errors (e.g., "nursing.jpg" maps to itself unchanged)
- SQL WHERE scoped to card_image_key IS NOT NULL AND card_image_key != '' makes intent clear and eliminates 197 silently-dropped families

## Deviations from Plan

None — plan executed exactly as written. Three targeted changes applied to main.py without altering any surrounding code.

## Gap Closure Confirmation

This plan closes the gap identified in 05-VERIFICATION.md: "CARD_IMAGE_STATIC dict missing from main.py". The 11 broken card background images were caused by raw DB values containing spaces (e.g. "administrative support.webp") being served as static URLs against hyphenated filenames on disk (e.g. "administrative-support.webp"). The normalization dict resolves all 12 mappings explicitly.

## Issues Encountered

None.

## User Setup Required

None — no external service configuration required.

## Next Phase Readiness

- /careers page card images are now fully functional for all 12 families
- Phase 05 gap fully closed; Phase 06 (L1 Interactivity) can proceed without this blocker

---
*Phase: 05-l1-card-grid*
*Completed: 2026-03-18*
