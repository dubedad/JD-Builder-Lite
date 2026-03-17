---
phase: 08-l3-job-title
plan: 01
subsystem: ui
tags: [fastapi, jinja2, sqlite, html, css, sticky-nav, caf-bridge]

# Dependency graph
requires:
  - phase: 07-l2-job-family
    provides: GET /careers/{family_slug} route and family.html L2 listing page
provides:
  - GET /career/{title_slug} route returning full career profile with 404 on unknown slug
  - career_detail.html L3 template with sticky 5-tab nav, 5 content sections, action buttons, breadcrumb
  - CAF bridge link rendering (caf_related JSON array → forces.ca career links)
affects: [navigation-chain, end-to-end-flow]

# Tech tracking
tech-stack:
  added: []
  patterns:
    - "Defensive JSON parsing with try/except (json.JSONDecodeError, TypeError) for nullable JSON columns"
    - "Jinja2 | safe filter for LLM-generated HTML content"
    - "position:sticky tab nav at top:64px (below GC header) with z-index:900"
    - "Empty section fallback: 'Content coming soon.' when LLM field is null"

key-files:
  created:
    - ps_careers_site/templates/career_detail.html
  modified:
    - ps_careers_site/main.py (route was pre-existing from prior session)

key-decisions:
  - "Route GET /career/{title_slug} was already implemented in main.py from a prior session — committed as-is after verification"
  - "CSS property written as position:sticky (no space) to match plan verification script literal check"
  - "CAF bridge links use slug | replace('-', ' ') | title for display names — no lookup table needed"

patterns-established:
  - "Pattern 1: L3 page header uses Exo 2 26px h1 on #222 background — consistent with CAF site"
  - "Pattern 2: Tab nav sticky at top:64px (GC header height) with z-index:900 — below GC header at 1020"
  - "Pattern 3: Action buttons Discover/Prepare scroll to named section anchors; Apply links externally to GC Jobs"

requirements-completed: [L3-01, L3-02, L3-03, L3-04, L3-05, L3-06, L3-07, L3-08, L3-09]

# Metrics
duration: 3min
completed: 2026-03-17
---

# Phase 8 Plan 01: L3 Job Title Detail Summary

**Jinja2 career_detail.html with sticky 5-tab nav, Exo 2 header, CAF bridge links, and LLM content sections at /career/{title_slug}**

## Performance

- **Duration:** 3 min
- **Started:** 2026-03-17T22:10:04Z
- **Completed:** 2026-03-17T22:12:54Z
- **Tasks:** 2 (1 pre-existing, 1 created)
- **Files modified:** 1 (career_detail.html created)

## Accomplishments
- Created career_detail.html covering all 9 L3 requirements (L3-01 through L3-09)
- Verified GET /career/{title_slug} returns HTTP 200 for valid slug, HTTP 404 for unknown slug
- CAF bridge links confirmed rendering: administrative-assistant shows dental-technician and medical-laboratory-technologist links to forces.ca
- All 5 content sections (sec-overview, sec-training, sec-entry, sec-parttime, sec-related) confirmed in live curl tests
- Full navigation chain confirmed: /careers -> /careers/{family} -> /career/{title} all HTTP 200

## Test Record Details

- **Slug tested end-to-end:** `administrative-assistant` (Administrative Assistant, administrative-support family)
- **LLM content present:** overview=YES, training=YES, entry_plans=YES, part_time=YES (9/9 titles in administrative-support family have all LLM fields populated)
- **CAF bridge coverage (administrative-support family):** 7/9 titles have caf_related populated
- **CAF bridge coverage (overall):** 433/1989 titles have caf_related populated (~21.8%)

## Task Commits

Each task was committed atomically:

1. **Task 1: GET /career/{title_slug} route** — pre-existing in main.py (committed in prior session `709d731`)
2. **Task 2: career_detail.html** — `53b6e28` (feat)

## Files Created/Modified
- `ps_careers_site/templates/career_detail.html` — L3 job title detail page: breadcrumb, header with NOC/family/level/digital badges, Discover/Prepare/Apply action buttons, sticky 5-tab nav, 5 content sections with LLM content rendered via | safe, CAF bridge links section
- `ps_careers_site/main.py` — GET /career/{title_slug} route (pre-existing, verified passing)

## Decisions Made
- The /career/{title_slug} route was already fully implemented in main.py from the phase 07 session. Confirmed it matched the plan spec exactly and proceeded without re-committing.
- Used `position:sticky` (no space) rather than `position: sticky` to match the exact string the plan verification script checks for.

## Deviations from Plan

### Pre-existing Work

**Task 1: GET /career/{title_slug} route pre-existed in main.py**
- **Found during:** Task 1 verification
- **Issue:** Route was already added to main.py in a prior session (visible in phase 07 session context)
- **Fix:** Ran the verification check — it passed. No changes needed. Noted as pre-existing.
- **Impact:** Zero — route matches the plan spec exactly

---

**Total deviations:** 1 (pre-existing route — no corrective action needed)
**Impact on plan:** None — all plan requirements met.

## Issues Encountered
- Minor: Jinja2 template `position: sticky` (with space) failed the plan verification script which checks for `position:sticky` (no space). Fixed by removing the space in the CSS property value. No functional impact.

## User Setup Required
None - no external service configuration required.

## Next Phase Readiness
- Full 3-level navigation chain is complete: /careers (L1) → /careers/{family} (L2) → /career/{title} (L3)
- All 9 L3 requirements are satisfied
- LLM content is already populated in the database for all test records
- CAF bridge data covers ~21.8% of titles overall; 77.8% of administrative-support family
- Site is functionally complete for the DND Civilian Careers v1.0 milestone

---
*Phase: 08-l3-job-title*
*Completed: 2026-03-17*
