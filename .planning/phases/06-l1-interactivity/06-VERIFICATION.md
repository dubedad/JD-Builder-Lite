---
phase: 06-l1-interactivity
verified: 2026-03-17T21:10:00Z
status: passed
score: 5/5 must-haves verified
re_verification: false
---

# Phase 6: L1 Interactivity Verification Report

**Phase Goal:** A visitor can narrow the card grid by job function or keyword without a page reload
**Verified:** 2026-03-17T21:10:00Z
**Status:** passed
**Re-verification:** No — initial verification

## Goal Achievement

### Observable Truths

| # | Truth | Status | Evidence |
|---|-------|--------|----------|
| 1 | GET /careers response body contains a `<select>` element with job function options | VERIFIED | `<select id="job-function-filter">` present in careers.html; populated via `{% for func in job_functions %}` loop; `job_functions` passed from route |
| 2 | GET /careers response body contains a search `<input>` element | VERIFIED | `<input type="text" id="career-search">` present at line 164 of careers.html |
| 3 | The page includes inline JS that filters cards by job function on dropdown change | VERIFIED | IIFE JS reads `fnFilter.value`, sets `matchFn = !fn \|\| card.dataset.function === fn`; `fnFilter.addEventListener('change', applyFilters)` wired |
| 4 | The page includes inline JS that filters cards by name/title keyword on input event | VERIFIED | IIFE reads `search.value`, matches against `card.dataset.name` and `JSON.parse(card.dataset.titles)`; `search.addEventListener('input', applyFilters)` wired |
| 5 | Clearing filter/search restores all cards without a page reload | VERIFIED | Empty `fn` string evaluates `!fn = true` (all cards pass); empty `kw` skips the `if (kw)` block (matchKw stays true); `card.style.display = show ? '' : 'none'` restores browser default display |

**Score:** 5/5 truths verified

### Required Artifacts

| Artifact | Expected | Status | Details |
|----------|----------|--------|---------|
| `ps_careers_site/templates/careers.html` | Updated L1 page with Job Function dropdown and keyword search bar | VERIFIED — substantive, wired | Contains `job-function-filter`, `career-search`, `data-function`, `data-name`, `data-titles`, `applyFilters` IIFE, `no-results` div, filter bar CSS. 224 lines. |
| `ps_careers_site/main.py` | Updated /careers route passing job_functions list and titles_json to template | VERIFIED — substantive, wired | `import json` present; `SELECT DISTINCT job_function` query; `GROUP_CONCAT` titles query; `titles_by_slug` dict; `titles_json` on each family dict; `job_functions` in `TemplateResponse`. 206 lines. |

### Key Link Verification

| From | To | Via | Status | Details |
|------|----|-----|--------|---------|
| `ps_careers_site/templates/careers.html` | `ps_careers_site/main.py` | `data-function` attribute on `.card-col` elements, populated from `families[].function` | WIRED | `row["job_function"]` in SELECT → `"function": row["job_function"]` in families loop → `"job_functions": job_functions` in TemplateResponse → `data-function="{{ family.function }}"` in template → `card.dataset.function` read in JS |

### Requirements Coverage

| Requirement | Source Plan | Description | Status | Evidence |
|-------------|-------------|-------------|--------|----------|
| L1-04 | 06-01-PLAN.md | Visitor can filter card grid by Job Function (22 values) using a dropdown — only families in the selected function are shown | SATISFIED | `<select id="job-function-filter">` with `{% for func in job_functions %}` loop; JS `matchFn` logic hides non-matching cards |
| L1-05 | 06-01-PLAN.md | Visitor can type in the search bar to filter cards by job family name or job title keyword — cards update in real time | SATISFIED | `<input type="text" id="career-search">`; JS matches `card.dataset.name` and `JSON.parse(card.dataset.titles)`; `data-titles` populated from `titles_json` (GROUP_CONCAT of all job titles per family) |

No orphaned requirements — REQUIREMENTS.md maps only L1-04 and L1-05 to Phase 6, both claimed and satisfied.

### Anti-Patterns Found

| File | Line | Pattern | Severity | Impact |
|------|------|---------|----------|--------|
| `ps_careers_site/templates/careers.html` | 164 | `placeholder="Search by job family..."` | Info — false positive | HTML input placeholder attribute, not an implementation stub. No impact. |

No blockers or warnings found.

### Human Verification Required

#### 1. Job Function Dropdown — 22 Values

**Test:** Start the app (`uvicorn ps_careers_site.main:app`), visit `/careers`, open the dropdown.
**Expected:** Exactly 22 function options plus the "All Functions" default (23 total `<option>` elements).
**Why human:** The query fetches DISTINCT job_function from careers.sqlite. The actual count depends on the DB contents — static analysis cannot confirm 22 vs any other count.

#### 2. Dropdown Filter Hides Correct Cards

**Test:** Select a specific job function (e.g., "Human Resources") from the dropdown.
**Expected:** Only cards whose `data-function` attribute matches "Human Resources" remain visible; all others are hidden with `display: none`. No page reload occurs.
**Why human:** Correct card hiding requires the DB job_function values to exactly match the values embedded in `data-function` attributes — a runtime check.

#### 3. Keyword Search Matches Job Titles Within a Family

**Test:** Type a job title keyword (e.g., "analyst") into the search bar.
**Expected:** Cards whose family contains at least one job title with "analyst" in the name remain visible; cards with no matching title or family name are hidden. Updates in real time as you type.
**Why human:** The `data-titles` attribute must actually contain lowercase title strings from the DB. Verifying non-empty population requires the app running against real data.

#### 4. Intersection Logic

**Test:** Select a job function AND type a keyword simultaneously.
**Expected:** Only cards matching BOTH conditions are shown (intersection, not union).
**Why human:** Requires observing runtime behavior with real data.

#### 5. No-Results Message

**Test:** Type a keyword that matches no family name or title (e.g., "xyzqwerty").
**Expected:** All cards are hidden and "No careers match your search." message appears.
**Why human:** Requires runtime rendering.

### Gaps Summary

No gaps. All five observable truths are verified. Both modified files are substantive and wired. Both requirements (L1-04, L1-05) are satisfied. Commits 81b2741 and 284e883 exist in git history and correspond exactly to the two plan tasks. The only items requiring human verification are runtime behaviors dependent on actual database contents.

---

_Verified: 2026-03-17T21:10:00Z_
_Verifier: Claude (gsd-verifier)_
