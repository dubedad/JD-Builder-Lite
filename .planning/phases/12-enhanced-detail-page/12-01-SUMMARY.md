---
phase: 12
plan: "01"
subsystem: ps_careers_site
tags: [detail-page, tdd, breadcrumb, key-responsibilities, required-skills, typical-education]
dependency_graph:
  requires: [phase-09-data-migration, phase-11-navigation-restructure]
  provides: [enhanced-detail-page, 4-level-breadcrumb-on-detail]
  affects: [career_detail.html, main.py]
tech_stack:
  added: []
  patterns: [TDD RED-GREEN, Jinja2 LEFT JOIN template data, SQLite JOIN query]
key_files:
  created:
    - ps_careers_site/tests/test_detail_page.py
  modified:
    - ps_careers_site/main.py
    - ps_careers_site/templates/career_detail.html
decisions:
  - "LEFT JOIN job_families + job_functions in career_detail route for function_slug/function_name fallback"
  - "Empty string default for new columns (not None) avoids Jinja2 truthiness issues"
  - "Graceful fallback section renders 'Content is being developed' when DB column is NULL"
  - "Family badge link updated from /careers/{family_slug} to /careers/{function_slug}/{family_slug} for v1.1 nav parity"
metrics:
  duration_seconds: 259
  completed_date: "2026-03-29"
  tasks_completed: 2
  files_changed: 3
requirements: [DETAIL-01, DETAIL-02, DETAIL-03, DETAIL-04]
---

# Phase 12 Plan 01: Enhanced Detail Page — Key Responsibilities, Required Skills, Typical Education + 4-Level Breadcrumb

**One-liner:** Career detail page now shows Key Responsibilities, Required Skills, and Typical Education tabs from the DB, with a 4-level breadcrumb (Home > Careers > Function > Family > Title) via LEFT JOIN on job_families and job_functions.

## What Was Built

### Route Enhancement (`main.py`)

The `/career/{title_slug}` route now JOINs `job_families` and `job_functions` to retrieve the function slug and function name for breadcrumb construction. Three new fields are passed to the template context: `key_responsibilities`, `required_skills`, `typical_education`. The `function_slug` and `function_name` fields fall back gracefully if the JOIN returns NULL (orphaned career row).

### Template Enhancement (`career_detail.html`)

**Breadcrumb:** Updated from 3-level (`Home > Careers > Family > Title`) to 4-level (`Home > Careers > Function > Family > Title`). Function link goes to `/careers/{function_slug}`; Family link goes to `/careers/{function_slug}/{family_slug}`. Conditionally renders the old-style breadcrumb if `function_slug` is empty (orphan fallback).

**Tab navigation:** Expanded from 5 tabs to 8 tabs. Three new tabs inserted after Overview: Key Responsibilities, Required Skills, Typical Education.

**Content sections:** Three new `<section>` elements with `id="sec-key-responsibilities"`, `id="sec-required-skills"`, `id="sec-typical-education"`. Each renders DB content via `| safe` filter. NULL values render a draft placeholder message instead of breaking the page.

**Family badge:** Updated href from `/careers/{family_slug}` to `/careers/{function_slug}/{family_slug}` to match v1.1 navigation structure.

### Test Suite (`tests/test_detail_page.py`)

10 tests covering:
- Tab heading presence (tests 1-3)
- DB content matches rendered output (tests 4-6)
- Breadcrumb function link (test 7)
- Breadcrumb family link with function context (test 8)
- Job title as final non-linked breadcrumb element (test 9)
- NULL graceful handling (test 10 — skipped when all rows populated)

## Test Results

```
9 passed, 1 skipped (NULL test skipped — all DB rows have key_responsibilities populated)
18 Phase 11 regression tests: all pass
```

## Commits

| Task | Commit | Files |
|------|--------|-------|
| Step 1 — TDD RED | 6ca36cb | ps_careers_site/tests/test_detail_page.py |
| Steps 2-4 — Route + Template GREEN | cca3e1a | ps_careers_site/main.py, ps_careers_site/templates/career_detail.html |

## Deviations from Plan

**1. [Rule 2 - Enhancement] Family badge link updated to 4-level path**
- **Found during:** Template modification (Step 3)
- **Issue:** The existing `badge-family` link in the page header pointed to `/careers/{family_slug}` — the old 3-level path that no longer exists as a valid route in v1.1. This would produce a 404 when clicked.
- **Fix:** Updated to `/careers/{function_slug}/{family_slug}` to match v1.1 navigation structure.
- **Files modified:** `ps_careers_site/templates/career_detail.html`
- **Commit:** cca3e1a

No other deviations — plan executed as written.

## Known Stubs

None. All three content columns (`key_responsibilities`, `required_skills`, `typical_education`) are populated in the DB via Phase 9 data migration. The graceful fallback message ("Content is being developed for this section.") is intentional for any future rows where columns are NULL — it is not a stub blocking the plan's goal.

## Self-Check: PASSED
