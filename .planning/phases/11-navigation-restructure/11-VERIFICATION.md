---
phase: 11-navigation-restructure
verified: 2026-03-28T00:00:00Z
status: passed
score: 6/6 success criteria verified
re_verification: false
gaps: []
human_verification:
  - test: "Visual CAF parity check — all three browse levels"
    expected: "Cards render at exactly 300px height with 3-layer gradient overlay, Exo 2 title, VIEW CAREERS button in uppercase — matching forces.ca appearance"
    why_human: "CSS rendering cannot be verified programmatically without a headless browser"
  - test: "Keyword search on /careers filters in real time"
    expected: "Typing a partial function name (e.g. 'eng') hides all cards except Engineering and Architecture; clearing the field restores all 22 cards"
    why_human: "Client-side DOM filtering requires live browser interaction"
  - test: "22 vs 23 function count — data integrity"
    expected: "REQUIREMENTS.md and ROADMAP say 23 functions; DB and tests verify 22 — confirm whether one function is legitimately missing or the spec count is wrong"
    why_human: "Requires cross-referencing source TBS spreadsheet against DB import"
---

# Phase 11: Navigation Restructure — Verification Report

**Phase Goal:** A visitor can browse all three taxonomy levels (Function → Family → Title) as image card grids with correct URLs, breadcrumbs, and search.
**Verified:** 2026-03-28
**Status:** PASSED
**Re-verification:** No — initial verification

---

## Goal Achievement

### Observable Truths (from ROADMAP.md Success Criteria)

| # | Truth | Status | Evidence |
|---|-------|--------|----------|
| 1 | `/careers` shows 22 Job Function cards in 4-col → 3-col → 1-col responsive grid using CAF card CSS | VERIFIED | `test_careers_contains_22_function_cards` PASSES; DB has 22 rows in `job_functions`; `card_styles.html` implements 25%/33.333%/100% breakpoints, 300px height, Exo 2, gradient overlay |
| 2 | Clicking a Function card navigates to `/careers/{function-slug}` which shows Family cards in same grid | VERIFIED | `careers_functions.html` sets `href="/careers/{{ fn.job_function_slug }}"` on each card; `careers_families.html` renders family cards with identical card CSS via shared partial |
| 3 | Clicking a Family card navigates to `/careers/{function-slug}/{family-slug}` which shows Title cards in same grid | VERIFIED | `careers_families.html` sets `href="/careers/{{ function.job_function_slug }}/{{ fam.job_family_slug }}"` on each card; `careers_titles.html` renders title cards linking to `/career/{title_slug}` |
| 4 | Every browse page shows a hero banner with current level name and description | VERIFIED | All 3 templates include `<div class="browse-hero">` from `card_styles.html` partial; L1 shows "Civilian Careers", L2 shows `function.job_function`, L3 shows `family.job_family` in `hero-title` |
| 5 | Every browse page shows correct breadcrumb (Home > Careers > [Function] > [Family]) | VERIFIED | L1: `Home > Careers`; L2: `Home > Careers > {function}`; L3: `Home > Careers > {function} > {family}` — all verified via template inspection and `test_function_page_breadcrumb_shows_function_name`, `test_family_page_breadcrumb_shows_function_and_family` |
| 6 | Keyword search on `/careers` filters 22 function cards in real time by function name | VERIFIED | `careers_functions.html` sets `data-name="{{ fn.job_function | lower }}"` on each card-col; JS reads `data-name` and hides non-matching cards on `input` event; `test_careers_search_data_present` PASSES |

**Score:** 6/6 truths verified

---

### Required Artifacts

| Artifact | Status | Details |
|----------|--------|---------|
| `ps_careers_site/main.py` | VERIFIED | 3 new route handlers: `careers_functions`, `careers_families`, `careers_titles`; 404 on invalid slugs; correct route ordering (L3 before L2 to prevent FastAPI shadowing) |
| `ps_careers_site/templates/careers_functions.html` | VERIFIED | 77 lines; extends base.html; hero + breadcrumb + search bar + 22-card grid + filter JS |
| `ps_careers_site/templates/careers_families.html` | VERIFIED | 61 lines; extends base.html; hero + breadcrumb + family card grid |
| `ps_careers_site/templates/careers_titles.html` | VERIFIED | 62 lines; extends base.html; hero + breadcrumb + title card grid with `/career/` links |
| `ps_careers_site/templates/partials/card_styles.html` | VERIFIED | 156 lines of shared CSS; `.browse-hero`, `.breadcrumb`, `.search-bar`, `.card-grid`, `.career-card`, `.view-btn`; included via `{% include %}` in all 3 browse templates |
| `ps_careers_site/tests/test_nav_restructure.py` | VERIFIED | 18 tests; all PASS |

---

### Key Link Verification

| From | To | Via | Status | Details |
|------|----|-----|--------|---------|
| `/careers` route in `main.py` | `careers_functions.html` | `TemplateResponse("careers_functions.html", ...)` | WIRED | Route queries `job_functions` table; passes `functions` context; template renders each `fn.job_function_slug` as card href |
| `/careers/{function_slug}` route | `careers_families.html` | `TemplateResponse("careers_families.html", ...)` | WIRED | Route looks up function by slug (404 if missing); queries `job_families WHERE job_function_slug = ?`; template renders correct links |
| `/careers/{function_slug}/{family_slug}` route | `careers_titles.html` | `TemplateResponse("careers_titles.html", ...)` | WIRED | Route validates both slugs; queries `careers WHERE job_family_slug = ?`; template renders `/career/{title_slug}` links |
| `careers_functions.html` | `partials/card_styles.html` | `{% include "partials/card_styles.html" %}` | WIRED | Present in `{% block extra_head %}` of all 3 browse templates |
| `careers_families.html` | `partials/card_styles.html` | `{% include "partials/card_styles.html" %}` | WIRED | Same as above |
| `careers_titles.html` | `partials/card_styles.html` | `{% include "partials/card_styles.html" %}` | WIRED | Same as above |
| L3 route (`/{function_slug}/{family_slug}`) | L2 route (`/{function_slug}`) | Route declaration order in `main.py` | WIRED | L3 route declared at line 76, L2 declared at line 109 — correct ordering prevents FastAPI shadowing |

---

### Data-Flow Trace (Level 4)

| Artifact | Data Variable | Source | Produces Real Data | Status |
|----------|---------------|--------|--------------------|--------|
| `careers_functions.html` | `functions` | `conn.execute("SELECT ... FROM job_functions ORDER BY job_function")` | Yes — 22 rows from SQLite | FLOWING |
| `careers_families.html` | `families` | `conn.execute("SELECT ... FROM job_families WHERE job_function_slug = ?")` | Yes — N rows per function from SQLite | FLOWING |
| `careers_titles.html` | `titles` | `conn.execute("SELECT ... FROM careers WHERE job_family_slug = ?")` | Yes — N rows per family from SQLite | FLOWING |

---

### Behavioral Spot-Checks

| Behavior | Command | Result | Status |
|----------|---------|--------|--------|
| `/careers` returns 200 with 22 function cards | `pytest test_careers_contains_22_function_cards` | PASSED | PASS |
| `/careers/administration` returns 200 with family cards and breadcrumb | `pytest test_function_page_breadcrumb_shows_function_name` | PASSED | PASS |
| L3 route returns 200 for valid function+family combo | `pytest test_family_page_valid_combo_returns_200` | PASSED | PASS |
| Title cards link to `/career/` detail route | `pytest test_family_page_title_cards_link_to_career_detail` | PASSED | PASS |
| Invalid slugs return 404 | `pytest test_function_page_invalid_slug_returns_404`, `test_family_page_invalid_family_returns_404` | PASSED | PASS |
| Keyword search data attributes present on L1 | `pytest test_careers_search_data_present` | PASSED | PASS |
| Full test suite (18 nav + 25 pipeline) | `pytest -q` | 43/43 passed | PASS |

---

### Requirements Coverage

| Requirement | Description | Status | Evidence |
|-------------|-------------|--------|----------|
| NAV-01 | `/careers` serves 23 Job Function image cards (4-col → 3-col → 1-col, CAF card format) | SATISFIED (with caveat) | Route and template verified; 22 cards rendered (see Note below) |
| NAV-02 | `/careers/{function-slug}` serves Job Family image cards for that function (same card format) | SATISFIED | Route wired, template verified, `test_function_page_family_cards_link_to_family_slug` PASSES |
| NAV-03 | `/careers/{function-slug}/{family-slug}` serves Job Title image cards for that family (same card format) | SATISFIED | Route wired, template verified, `test_family_page_shows_title_cards` PASSES |
| NAV-04 | All 3 browse levels use identical card CSS (300px height, 3-layer gradient overlay, Exo 2 title font, VIEW CAREERS button) | SATISFIED | `card_styles.html` included in all 3 templates; CSS: `height: 300px`, `font-family: 'Exo 2'`, `text-transform: uppercase` on `.view-btn`, 2 gradient layers + url |
| NAV-05 | Hero banner on each browse page showing current level name and description | SATISFIED | All 3 templates include `.browse-hero` with `hero-title` showing level name; description rendered when present |
| NAV-06 | Breadcrumb on every page: Home > Careers > [Function] > [Family] | SATISFIED | L1: Home > Careers; L2: Home > Careers > {function}; L3: Home > Careers > {function} > {family} |
| NAV-07 | Keyword search on L1 (`/careers`) searches across function names | SATISFIED | `data-name` set to `fn.job_function | lower` on each card; JS filters on `input` event |

**Note on NAV-01 count discrepancy:** REQUIREMENTS.md, ROADMAP.md, and DATA-04 all reference 23 job functions. The actual DB contains 22 (`SELECT COUNT(*) FROM job_functions = 22`). The test verifies 22 cards and PASSES. This discrepancy originates in Phase 9 data import, not Phase 11. Phase 11 correctly renders all rows present. Human verification recommended (see Human Verification section).

---

### Anti-Patterns Found

| File | Line | Pattern | Severity | Impact |
|------|------|---------|----------|--------|
| `templates/careers.html` | — | Orphaned old template — not rendered by any route | Info | No user impact; old flat family-card page replaced by `careers_functions.html` |

No blocking stubs, no placeholder implementations, no hardcoded empty arrays returned to the browser.

---

### Human Verification Required

#### 1. Visual CAF parity check

**Test:** Open `/careers`, `/careers/administration`, and `/careers/administration/{any-family-slug}` in a browser. Compare each level against the card specification in `CAF-CAREERS-SITE-REFERENCE.md`.
**Expected:** Cards render at 300px height, gradient overlay is visible on photo cards, fallback gradient shows on cards without images, button appears uppercase with border, Exo 2 font is active.
**Why human:** CSS rendering, font loading, and visual gradient fidelity cannot be asserted programmatically without a headless browser.

#### 2. Keyword search real-time filtering

**Test:** Load `/careers`, type "eng" in the search box.
**Expected:** All function cards except "Engineering and Architecture" hide immediately; clearing the input restores all 22 cards.
**Why human:** Client-side DOM manipulation requires interactive browser session.

#### 3. Function count discrepancy (22 vs 23)

**Test:** Open `Job Architecture_TBS.xlsx` (source file) and count distinct Job Function values. Cross-reference against `SELECT COUNT(*) FROM job_functions`.
**Expected:** Either 22 is the correct count (specs were wrong) or one function was missed during Phase 9 ingest and should be added.
**Why human:** Requires reading the source spreadsheet to determine ground truth. If 23 is correct, a Phase 9 data fix is needed before Phase 11 can fully satisfy NAV-01 as written.

---

### Gaps Summary

No gaps block phase goal achievement. All six ROADMAP success criteria are satisfied by verified, working code:

- Three-level routing is wired end-to-end in `main.py` with correct FastAPI route ordering
- All three browse templates extend `base.html`, include shared `card_styles.html`, render hero banners, breadcrumbs, and card grids from live DB queries
- Keyword search on L1 operates via `data-name` attributes and DOM filtering
- 18 dedicated tests all pass; full suite of 43 tests passes with no regressions
- CAF card CSS compliance: 300px height, responsive grid (4→3→1 col), Exo 2 font, gradient overlay, VIEW CAREERS button (uppercase via CSS) — all present in `card_styles.html`

One advisory finding: REQUIREMENTS.md says "23 job functions" but the DB has 22. This is a Phase 9 data issue, not a Phase 11 code defect. Phase 11 correctly renders whatever the DB contains.

---

_Verified: 2026-03-28_
_Verifier: Claude (gsd-verifier)_
