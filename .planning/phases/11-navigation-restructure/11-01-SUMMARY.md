---
phase: 11
plan: "01"
subsystem: ps_careers_site
tags: [navigation, routing, templates, tdd, card-grid, caf-parity]
dependency_graph:
  requires: [phase-09, phase-10]
  provides: [4-level-browse-hierarchy, function-cards, family-cards, title-cards]
  affects: [main.py, careers_functions.html, careers_families.html, careers_titles.html]
tech_stack:
  added: []
  patterns: [TDD-RED-GREEN, Jinja2-partials, FastAPI-route-ordering]
key_files:
  created:
    - ps_careers_site/main.py (routes rewritten)
    - ps_careers_site/templates/careers_functions.html
    - ps_careers_site/templates/careers_families.html
    - ps_careers_site/templates/careers_titles.html
    - ps_careers_site/templates/partials/card_styles.html
    - ps_careers_site/tests/test_nav_restructure.py
  modified:
    - ps_careers_site/pytest.ini (added tests/ to testpaths)
decisions:
  - "Route ordering: /careers/{function_slug}/{family_slug} declared BEFORE /careers/{function_slug} in FastAPI to prevent L2 URL shadowing L3"
  - "Schema adaptation: DB uses job_function_slug/job_family_slug as PKs (not id); plan SQL adapted to match reality"
  - "Gradient fallback at L2/L3: family and title cards inherit function gradient since families/titles have no images yet"
  - "Shared card CSS in partials/card_styles.html avoids duplication across all 3 browse templates"
metrics:
  duration: "~25 minutes"
  completed: "2026-03-29"
  tasks_completed: 3
  files_changed: 8
  tests_added: 18
  tests_passing: 43
---

# Phase 11 Plan 01: 4-Level Browse Hierarchy with Image Card Grids — Summary

**One-liner:** Three-level Function → Family → Title card grid browse with CAF-parity CSS, breadcrumbs, and keyword search, implemented via TDD (18 tests GREEN).

## What Was Built

A complete navigation restructure replacing the old flat family card grid with a proper 3-level browse hierarchy:

- `/careers` → 22 Job Function image cards with real-time keyword search
- `/careers/{function-slug}` → Job Family cards within that function + breadcrumb + hero
- `/careers/{function-slug}/{family-slug}` → Job Title cards within that family + breadcrumb + hero
- `/career/{title-slug}` → Detail page (unchanged, Phase 12 enhances)

All browse levels use identical CAF card CSS: 300px height, 3-layer gradient overlay, Exo 2 title, "VIEW CAREERS" button, 4→3→1 responsive columns. Per-function gradient fallback classes from Phase 10 handle cards without images.

## Implementation Details

### Route Implementation

`main.py` routes were replaced with 3 new handlers. The key ordering constraint: `/{function_slug}/{family_slug}` must be declared before `/{function_slug}` in FastAPI to prevent the 2-segment path from matching the 1-segment route.

DB schema uses `job_function_slug` as PK (not `id`/`slug` as the plan assumed). All SQL adapted accordingly.

### Templates

Three new browse templates share a `partials/card_styles.html` include for the ~130 lines of card CSS. Each template:
- Extends `base.html`
- Renders hero banner (306px, white Exo 2 heading)
- Renders breadcrumb trail
- Renders CAF-format card grid using per-row div approach

### Search

L1 keyword search filters function cards client-side using `data-name` attributes set to lowercase function name. Works via DOM traversal, no data-attribute JSON blob needed for the simpler 22-item list.

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 1 - Schema Mismatch] DB column names differ from plan SQL**
- **Found during:** Task implementation (Step 2)
- **Issue:** Plan showed `SELECT f.id, f.function_name, f.slug` but actual DB has `job_function_slug, job_function, job_function_description`; similarly `job_families` uses `job_family_slug, job_function_slug` (no `function_id`)
- **Fix:** All SQL queries and template variable references adapted to actual schema
- **Files modified:** main.py, all 3 templates

**2. [Rule 1 - Route Order] FastAPI route shadowing**
- **Found during:** Step 2 analysis
- **Issue:** If `/careers/{function_slug}` is declared before `/{function_slug}/{family_slug}`, FastAPI would match the 2-segment URL incorrectly
- **Fix:** Declared L3 route (`/{function_slug}/{family_slug}`) before L2 route (`/{function_slug}`) in main.py
- **Files modified:** main.py

## Known Stubs

- Family image_path: All 209 job families have `image_path = NULL` in the DB. The Phase 10 image pipeline ran for functions (3 images fetched), but family and title images were not yet fetched. The gradient fallback classes ensure cards render correctly — this is expected behavior, not a broken stub.
- Title image_path: Same as above. All titles fall back to per-function gradient.

These fallbacks are intentional and render correctly. No data is missing from the user experience — cards display with styled gradients and correct labels.

## Test Results

```
18/18 nav restructure tests PASS
25/25 pipeline tests PASS (no regressions)
43 total tests passing
```

## Self-Check: PASSED

All 6 key files verified present. Commits be03f36 and 70c88ae confirmed in git log. 43 tests passing.
