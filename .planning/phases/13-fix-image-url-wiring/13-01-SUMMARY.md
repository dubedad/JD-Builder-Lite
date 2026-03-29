---
phase: 13-fix-image-url-wiring
plan: 01
subsystem: ui
tags: [jinja2, fastapi, static-files, image-url, url_for]

# Dependency graph
requires:
  - phase: 10-image-pipeline
    provides: Unsplash images downloaded to static/images/functions/ directory
  - phase: 11-navigation-restructure
    provides: careers_functions.html, careers_families.html, careers_titles.html browse templates

provides:
  - Image URL path correctly wired in all 3 browse templates (images/ prefix added)
  - Function cards on /careers display Unsplash photos instead of gradient fallback
  - Family and title templates wired for photos (will resolve once Phase 14 populates those dirs)
  - IMG-03-WIRING gap closed; IMG-05 gradient-always-active side effect resolved

affects: [14-image-pipeline-families-titles, any template using url_for with image_path]

# Tech tracking
tech-stack:
  added: []
  patterns:
    - "url_for('static', path='images/' + var.image_path) — correct pattern for DB-relative image paths under static/images/"

key-files:
  created: []
  modified:
    - ps_careers_site/templates/careers_functions.html
    - ps_careers_site/templates/careers_families.html
    - ps_careers_site/templates/careers_titles.html

key-decisions:
  - "DB stores image_path relative to static/images/ (e.g. 'functions/admin.jpg'), not to static/ root — url_for must prepend 'images/' to bridge the gap"

patterns-established:
  - "image_path in DB is always relative to static/images/, not static/ — all templates must use url_for('static', path='images/' + var.image_path)"

requirements-completed: [IMG-03, IMG-05]

# Metrics
duration: 14min
completed: 2026-03-29
---

# Phase 13 Plan 01: Fix Image URL Wiring Summary

**Added `images/` prefix to url_for path in 3 browse templates so Unsplash function photos resolve to `/static/images/functions/slug.jpg` instead of 404ing at `/static/functions/slug.jpg`**

## Performance

- **Duration:** 14 min
- **Started:** 2026-03-29T14:43:17Z
- **Completed:** 2026-03-29T14:56:43Z
- **Tasks:** 1 of 1
- **Files modified:** 3

## Accomplishments

- careers_functions.html: fixed url_for to `path='images/' + fn.image_path` — function cards now display Unsplash photos
- careers_families.html: fixed url_for to `path='images/' + fam.image_path` — wired for when family images are populated
- careers_titles.html: fixed url_for to `path='images/' + title.image_path` — wired for when title images are populated
- Gradient fallback conditional (`{% if image_path %}` / `{% else %} gradient-{slug}`) left unchanged in all three templates

## Task Commits

Each task was committed atomically:

1. **Task 1: Prepend images/ prefix to url_for path in all 3 browse templates** - `1e8acde` (fix)

**Plan metadata:** (docs commit — see below)

## Files Created/Modified

- `ps_careers_site/templates/careers_functions.html` - url_for path corrected to include `images/` prefix for fn.image_path
- `ps_careers_site/templates/careers_families.html` - url_for path corrected to include `images/` prefix for fam.image_path
- `ps_careers_site/templates/careers_titles.html` - url_for path corrected to include `images/` prefix for title.image_path

## Decisions Made

- DB stores image_path as a value relative to `static/images/` (e.g. `functions/administration.jpg`), not relative to the `static/` mount root. The FastAPI static mount resolves `url_for('static', path='X')` to `/static/X`. Therefore the correct call is `url_for('static', path='images/' + var.image_path)` yielding `/static/images/functions/administration.jpg` which is where the file actually lives on disk.

## Deviations from Plan

None - plan executed exactly as written.

## Issues Encountered

None.

## User Setup Required

None - no external service configuration required.

## Next Phase Readiness

- Function-level cards on /careers now display Unsplash photos correctly (assuming static/images/functions/ populated by Phase 10 pipeline run)
- Family and title template URL wiring is correct; images will display once Phase 14 populates static/images/families/ and static/images/titles/
- No blockers for Phase 14 (image pipeline for families/titles)

---
*Phase: 13-fix-image-url-wiring*
*Completed: 2026-03-29*
