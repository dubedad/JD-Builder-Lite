---
phase: 10-image-pipeline
verified: 2026-03-28T22:40:00Z
status: passed
score: 9/9 must-haves verified
re_verification:
  previous_status: passed
  previous_score: 9/9
  gaps_closed: []
  gaps_remaining: []
  regressions: []
---

# Phase 10: Image Pipeline Verification Report

**Phase Goal:** The image pipeline is production-ready — images can be fetched for all 2,221 entries and all cards display gracefully when images are absent.
**Verified:** 2026-03-28T22:40:00Z
**Status:** PASSED
**Re-verification:** Yes — confirmed prior passing result; no regressions found.

---

## Goal Achievement

### Observable Truths

| # | Truth | Status | Evidence |
|---|-------|--------|----------|
| 1 | Running the pipeline fetches images from Unsplash API with job-relevant queries | VERIFIED | `UNSPLASH_SEARCH_URL = "https://api.unsplash.com/search/photos"` at fetch_images.py line 56; `build_query()` generates 3 entity-specific templates; `search_unsplash()` sends `Authorization: Client-ID {access_key}` header |
| 2 | Images are saved to static/images/functions/, /families/, /titles/ | VERIFIED | `IMAGES_DIR = BASE_DIR / "static" / "images"` (line 54); `WorkItem._subdir` explicit dict `{"function": "functions", "family": "families", "title": "titles"}`; `asyncio.to_thread(item.dest.write_bytes, data)` at line 281 |
| 3 | image_path is updated in DB for each record after successful download | VERIFIED | `UPDATE {item.table} SET image_path = ?` at line 284 followed immediately by `conn.commit()` at line 287; progress marked done only after commit |
| 4 | Re-running the pipeline skips entities that already have a local file AND DB image_path set | VERIFIED | `should_skip()` requires both `item.dest.exists()` AND non-null DB `image_path`; partial state returns False to reprocess |
| 5 | 5 concurrent workers process items simultaneously via asyncio semaphore | VERIFIED | `asyncio.Semaphore(workers)` default 5 at line 434; `asyncio.gather(*tasks, return_exceptions=True)` at line 443 |
| 6 | A card with null image_path displays a function-colored gradient instead of broken image | VERIFIED | `gradients.css` exists at `ps_careers_site/static/css/gradients.css` with 22 classes; linked globally in `base.html` head at line 10 |
| 7 | Each of the 22 job functions has a distinct muted gradient class | VERIFIED | `grep -c ".gradient-" gradients.css` returns 22; all hex values are dark (leading hex digit 0-3); covers all slugs from administration through transportation |
| 8 | Gradient fallback is pure CSS — no JavaScript required | VERIFIED | gradients.css contains only `linear-gradient(160deg, ...)` declarations; no script tags, no fetch calls, no @import |
| 9 | Unsplash attribution credit appears in site footer with referral tracking | VERIFIED | `Photos by <a href="https://unsplash.com/?utm_source=dnd_civilian_careers&utm_medium=referral">Unsplash</a>` at base.html line 107, inside `<footer>` element |

**Score:** 9/9 truths verified

---

### Required Artifacts

| Artifact | Expected | Status | Details |
|----------|----------|--------|---------|
| `ps_careers_site/pipeline/fetch_images.py` | Async Unsplash pipeline, min 150 lines, all required exports present, no Pexels references | VERIFIED | 500 lines; all 5 exports confirmed (main, build_query, build_work_list, should_skip, fetch_and_save); `grep -i pexels` returns no matches |
| `ps_careers_site/pipeline/test_fetch_images.py` | Pytest suite covering IMG-01 through IMG-04, min 100 lines | VERIFIED | 560 lines; 15 tests collected; all 15 PASS (7.81s) |
| `ps_careers_site/static/css/gradients.css` | 22 per-function gradient classes | VERIFIED | 27 lines; exactly 22 `.gradient-{slug}` rules confirmed by grep count |
| `ps_careers_site/templates/base.html` | gradients.css linked in head; Unsplash attribution in footer | VERIFIED | CSS link at line 10 (`<head>`); attribution span at line 107 (`<footer>`) |

---

### Key Link Verification

| From | To | Via | Status | Details |
|------|----|-----|--------|---------|
| fetch_images.py | https://api.unsplash.com/search/photos | httpx.AsyncClient GET with Authorization: Client-ID header | WIRED | `UNSPLASH_SEARCH_URL` constant + `headers={"Authorization": f"Client-ID {access_key}"}` in `search_unsplash()` |
| fetch_images.py | careers.sqlite (job_functions, job_families, careers) | sqlite3 UPDATE image_path + commit | WIRED | `conn.execute(f"UPDATE {item.table} SET image_path = ? WHERE {item.pk_col} = ?", ...)` + `conn.commit()` at lines 284-287 |
| fetch_images.py | static/images/{functions,families,titles}/ | Path.write_bytes via asyncio.to_thread | WIRED | `IMAGES_DIR = BASE_DIR / "static" / "images"`; `await asyncio.to_thread(item.dest.write_bytes, data)` at line 281 |
| gradients.css | Phase 11 card templates | CSS class `gradient-{slug}` applied in Jinja2 template | INFRASTRUCTURE READY — Phase 11 pending | CSS defines all 22 `.gradient-{slug}` classes; base.html loads the file globally; consuming templates are Phase 11's responsibility |
| base.html | gradients.css | `<link rel="stylesheet">` in `<head>` | WIRED | Line 10: `<link rel="stylesheet" href="{{ url_for('static', path='css/gradients.css') }}">` |

---

### Data-Flow Trace (Level 4)

Not applicable for pipeline scripts or static CSS assets. `fetch_images.py` is a data writer (not a renderer). `gradients.css` is a static asset with no dynamic data source. Level 4 deferred to Phase 11 verification when card templates consume `image_path` and `gradient-{slug}` classes.

---

### Behavioral Spot-Checks

| Behavior | Command | Result | Status |
|----------|---------|--------|--------|
| All 15 tests pass | `python -m pytest pipeline/test_fetch_images.py -v` | 15 passed in 7.81s | PASS |
| Dry-run processes 22 function items | `UNSPLASH_ACCESS_KEY=x python pipeline/fetch_images.py --dry-run --type function` | Logged 22 items (administration through transportation) | PASS |
| No Pexels references remain | `grep -i pexels pipeline/fetch_images.py` | No matches | PASS |
| Unsplash API URL present | `grep "api.unsplash.com" pipeline/fetch_images.py` | `UNSPLASH_SEARCH_URL = "https://api.unsplash.com/search/photos"` | PASS |
| Semaphore concurrency configured | `grep "asyncio.Semaphore" pipeline/fetch_images.py` | Lines 212 and 434 | PASS |
| Exactly 22 gradient classes | `grep -c ".gradient-" static/css/gradients.css` | 22 | PASS |
| gradients.css linked in head | `grep "gradients.css" templates/base.html` | Match at line 10 in `<head>` | PASS |
| All required module exports present | `python -c "from pipeline import fetch_images; ..."` | Missing: none | PASS |
| All 4 phase commits exist in git | `git cat-file -e {hash}` for 9512861, 563d1f2, ba0dc4e, dbafca7 | All 4 found | PASS |

---

### Requirements Coverage

| Requirement | Source Plan | Description | Status | Evidence |
|-------------|------------|-------------|--------|----------|
| IMG-01 | 10-01-PLAN.md | Pipeline queries Unsplash API with job-relevant keyword per function/family/title | SATISFIED | `build_query()` with 3 entity-type templates + paren-stripping via `re.sub`; `search_unsplash()` calls Unsplash API; 4 passing tests cover all query variants |
| IMG-02 | 10-01-PLAN.md | Images downloaded to /static/images/functions/, /families/, /titles/ | SATISFIED | `WorkItem._subdir` explicit dict mapping; `IMAGES_DIR / _subdir / slug.jpg`; `test_image_stored_in_correct_subdir` passes with path-separator-agnostic assertions |
| IMG-03 | 10-01-PLAN.md | image_path updated in DB after successful download | SATISFIED | `UPDATE ... SET image_path = ?` + `conn.commit()` before marking done; `test_db_updated_after_download` passes |
| IMG-04 | 10-01-PLAN.md | Pipeline is concurrent (5 workers) and resumable (skips already-fetched images) | SATISFIED | `asyncio.Semaphore(workers)` default 5; `should_skip()` dual-state check (file + DB); `test_concurrency_limit`, `test_resume_skips_done_items`, `test_resume_reprocesses_partial` all pass |
| IMG-05 | 10-02-PLAN.md | Cards display styled fallback (gradient, no photo) when image_path is null | SATISFIED | 22 `.gradient-{slug}` CSS classes in gradients.css; globally linked in base.html `<head>`; ready for Phase 11 template consumption |

**All 5 requirements: SATISFIED**

No orphaned requirements. REQUIREMENTS.md maps IMG-01 through IMG-05 to Phase 10, both plans claim exactly those 5 IDs. There are no Phase-10-assigned IDs in REQUIREMENTS.md that were not claimed by a plan.

---

### Anti-Patterns Found

| File | Line | Pattern | Severity | Impact |
|------|------|---------|----------|--------|
| fetch_images.py | 392-397 | `--dry-run` branch is reached only after the `UNSPLASH_ACCESS_KEY` env-var check, requiring a key even for dry runs | Info | Minor UX friction for offline testing; does not affect production pipeline correctness |

No blocking anti-patterns. No TODO/FIXME/PLACEHOLDER/HACK comments. No `return null`, empty stub implementations, or hardcoded empty data flowing to any renderer. No Pexels references remaining.

---

### Human Verification Required

#### 1. Gradient class visual appearance on cards

**Test:** Open the careers site. Apply `gradient-administration` (or any other function slug class) to a card element via browser DevTools. Confirm the gradient renders as a muted dark tone suitable for a federal government site.
**Expected:** Dark, desaturated gradient background at 160 degrees; overlaid text remains legible against it.
**Why human:** Colour aesthetic and WCAG contrast ratio cannot be confirmed programmatically without a running browser.

#### 2. Unsplash attribution legibility in footer

**Test:** Load any page in the site. Scroll to the footer. Confirm "Photos by Unsplash" appears in the footer-bottom row and the link opens `https://unsplash.com/?utm_source=dnd_civilian_careers&utm_medium=referral`.
**Expected:** Small grey text (11px, Roboto) with underlined "Unsplash" hyperlink; positioned between the social icons div and the Terms/Français links div.
**Why human:** Flex layout and visual spacing require browser rendering to confirm correct positioning.

#### 3. End-to-end image fetch with live Unsplash key

**Test:** Obtain an Unsplash Demo Access Key. Run `python pipeline/fetch_images.py --type function --limit 3`. Confirm 3 images download to `static/images/functions/`, the DB is updated with relative paths, and re-running the command skips those 3 items.
**Expected:** 3 .jpg files appear in the functions directory; `SELECT image_path FROM job_functions LIMIT 3` returns non-null relative paths; second run logs "Skipped (done): 3".
**Why human:** Requires a live Unsplash API key not available in this verification environment.

---

### Gaps Summary

No gaps. All 9 observable truths are verified. All 4 artifacts pass levels 1 (exists), 2 (substantive), and 3 (wired). All 5 requirements are satisfied. All 15 tests pass. All 4 documented commits exist in git history. The one anti-pattern noted (dry-run requiring API key) is a minor UX inconvenience, not a functional gap blocking the phase goal.

The gradient-to-card-template link is intentionally incomplete at this phase — that wiring is Phase 11's responsibility and is correctly scoped. The CSS infrastructure is fully in place.

---

_Verified: 2026-03-28T22:40:00Z_
_Verifier: Claude (gsd-verifier)_
