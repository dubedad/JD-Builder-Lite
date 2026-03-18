---
phase: 05-l1-card-grid
verified: 2026-03-17T00:00:00Z
status: human_needed
score: 6/6 must-haves verified
re_verification:
  previous_status: gaps_found
  previous_score: 4/6
  gaps_closed:
    - "CARD_IMAGE_STATIC dict added to main.py — all 12 entries present, CARD_IMAGE_STATIC.get() used on line 94, all 12 normalized static files exist in static/images/"
  gaps_remaining: []
  regressions: []
human_verification:
  - test: "Load /careers in a browser and confirm all 12 card background images render"
    expected: "All 12 cards show their background image (no blank/dark cards)"
    why_human: "Static file serving and URL generation require a live browser check"
  - test: "Confirm GC FIP chrome (header + footer) renders correctly on /careers"
    expected: "GC FIP header with Canada wordmark and nav, and 5-column footer on dark background are visible"
    why_human: "Visual layout requires visual inspection"
---

# Phase 5: L1 Card Grid Verification Report

**Phase Goal:** Build the L1 Browse Careers page — a full-width card grid of job families styled to match the CAF site, where each card links to the L2 family page
**Verified:** 2026-03-17
**Status:** human_needed (all automated checks pass; image rendering and chrome require live browser)
**Re-verification:** Yes — after gap closure (previous: gaps_found 4/6)

## Goal Achievement

### Observable Truths

| # | Truth | Status | Evidence |
|---|-------|--------|----------|
| 1 | GET /careers returns HTTP 200 | VERIFIED | `@app.get("/careers")` route exists in main.py line 56; returns `TemplateResponse("careers.html", ...)` |
| 2 | GET /careers response body contains at least 12 card elements | VERIFIED | SQL `WHERE card_image_key IS NOT NULL AND card_image_key != ''` returns exactly 12 families; all 12 are appended to `families` list; template loops over `families` with no-image guard retained as fallback |
| 3 | Each card has a VIEW CAREERS button with correct CSS (transparent bg, solid border) | VERIFIED | `.view-btn` in careers.html: `background: transparent; border: 1.33px solid rgb(245,245,245); text-transform: uppercase; letter-spacing: 2.4px; padding: 6.53px 30.4px` — exact spec match. Source text "View Careers" renders visually as "VIEW CAREERS" via `text-transform: uppercase` |
| 4 | Card titles use Exo 2 font at 23.2px | VERIFIED | `.card-inner h3` in careers.html: `font-family: 'Exo 2', sans-serif; font-size: 23.2px; font-weight: 600; line-height: 27.84px` — exact spec match |
| 5 | Grid is full-width with 4 columns at >=1200px, 3 at >=768px, 1 on mobile | VERIFIED | `.card-col { width: 25% }` + `@media (max-width: 1199px) { width: 33.333% }` + `@media (max-width: 767px) { width: 100% }` — exact spec match |
| 6 | Clicking a card link navigates to /careers/{family-slug} | VERIFIED | Template line 186: `<a href="/careers/{{ family.slug }}" class="view-btn">` — slug from `job_family_slug` column; `/careers/{family_slug}` route exists in main.py line 104 |

**Score:** 6/6 truths verified

### Required Artifacts

| Artifact | Expected | Status | Details |
|----------|----------|--------|---------|
| `ps_careers_site/templates/careers.html` | L1 Browse Careers page template extending base.html | VERIFIED | Exists, 230 lines; extends base.html; hero banner 306px; card grid with responsive CSS; 3-layer gradient overlay; Exo 2 23.2px titles; VIEW CAREERS button; slug-based hrefs |
| `ps_careers_site/main.py` | GET /careers route and CARD_IMAGE_STATIC mapping | VERIFIED | CARD_IMAGE_STATIC dict present lines 21-34 (12 entries); get_db() helper lines 37-40; GET /careers route lines 56-101; uses `CARD_IMAGE_STATIC.get(row["card_image_key"])` on line 94 |

### Key Link Verification

| From | To | Via | Status | Details |
|------|----|-----|--------|---------|
| `ps_careers_site/main.py` | `ps_careers_site/templates/careers.html` | `templates.TemplateResponse("careers.html", {...})` | VERIFIED | Lines 98-101: returns careers.html with `families` and `job_functions` context |
| `ps_careers_site/templates/careers.html` | `ps_careers_site/static/images/` | `url_for('static', path='images/' + family.image_file)` | VERIFIED | Line 181 uses `family.image_file` which is now the normalized filename from CARD_IMAGE_STATIC. All 12 target files confirmed present in `ps_careers_site/static/images/` |
| `ps_careers_site/main.py` CARD_IMAGE_STATIC | `ps_careers_site/static/images/` | dict keys → normalized filenames | VERIFIED | All 12 CARD_IMAGE_STATIC values match filenames in static/images/ exactly |

### Requirements Coverage

| Requirement | Source Plan | Description | Status | Evidence |
|-------------|------------|-------------|--------|----------|
| L1-01 | 05-01-PLAN.md | Card grid of all job families at /careers (full-width, 4-col / 3-col / 1-col responsive) | SATISFIED | Grid CSS confirmed; 4-col/3-col/1-col breakpoints at 1199px and 767px match spec exactly |
| L1-02 | 05-01-PLAN.md | Each card shows family name, background image, VIEW CAREERS button with exact CAF styling (Exo 2 23.2px, gradient overlay, transparent border button) | SATISFIED | CARD_IMAGE_STATIC gap closed; all 12 normalized filenames exist in static/images/; Exo 2 23.2px and .view-btn CSS verified |
| L1-03 | 05-01-PLAN.md | Clicking a card navigates to /careers/{family-slug} | SATISFIED | `href="/careers/{{ family.slug }}"` present; L2 route exists and is substantive |

No orphaned requirements: REQUIREMENTS.md maps L1-01, L1-02, L1-03 to Phase 5 only. L1-04 and L1-05 are mapped to Phase 6 and are not claimed by this phase's plan.

### Anti-Patterns Found

| File | Line | Pattern | Severity | Impact |
|------|------|---------|----------|--------|
| `ps_careers_site/templates/careers.html` | 186 | Button source text is "View Careers" (not "VIEW CAREERS") | Info | `text-transform: uppercase` in CSS renders it correctly; no visual or functional gap |

No blockers or warnings. The SQL `WHERE card_image_key IS NOT NULL AND card_image_key != ''` (previously flagged as a warning for using `!= ''` instead of `IS NOT NULL` alone) has been refined from the original `WHERE job_family != ''` — this is an improvement and no longer a concern.

### Human Verification Required

#### 1. Card Background Images Render

**Test:** Start the FastAPI server (`uvicorn main:app --reload` from `ps_careers_site/`) and open `http://localhost:8000/careers` in a browser.
**Expected:** All 12 job family cards show their background image. No blank/dark cards.
**Why human:** Static file serving and rendered URL correctness require a live browser check.

#### 2. GC FIP Chrome

**Test:** Same page load — inspect header and footer.
**Expected:** GC FIP header (Canada wordmark, Browse Careers nav, FR toggle) and 5-column dark footer render correctly on the /careers page.
**Why human:** Visual layout cannot be confirmed by grep.

### Re-Verification Summary

**Gap closed:** The single blocker from the initial verification — missing `CARD_IMAGE_STATIC` in `main.py` — has been resolved. The dict is present with all 12 entries, `CARD_IMAGE_STATIC.get()` is used to populate `image_file`, and all 12 normalized static files exist in `ps_careers_site/static/images/`. The image URL link chain is now intact end-to-end.

**No regressions detected.** The careers.html template has been extended with Phase 6 filter bar CSS and JavaScript (not in scope for Phase 5), but all Phase 5 structural elements — hero banner, card grid, responsive CSS, gradient overlay, Exo 2 titles, VIEW CAREERS button, and slug-based hrefs — are present and unchanged.

All 6 must-have truths pass automated verification. Two items require human browser testing (image rendering, visual chrome) before the phase can be marked fully passed.

---

_Verified: 2026-03-17_
_Verifier: Claude (gsd-verifier)_
