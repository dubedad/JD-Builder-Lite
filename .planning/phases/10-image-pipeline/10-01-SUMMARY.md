---
phase: 10-image-pipeline
plan: 01
subsystem: pipeline
tags: [unsplash, httpx, asyncio, sqlite, python, tdd]

# Dependency graph
requires:
  - phase: 09-data-migration
    provides: job_functions and job_families tables with image_path columns; careers.image_path column

provides:
  - Async Unsplash image pipeline script (fetch_images.py) with 5-worker concurrency and resume
  - Full pytest suite (15 tests) covering all IMG-01 through IMG-04 behaviors
  - WorkItem dataclass with entity typing and correct subdirectory routing
  - build_query() with entity-specific templates and paren-stripping
  - should_skip() with dual file+DB consistency check for resumable pipeline
  - build_work_list() reading from Phase 9 authoritative tables

affects: [11-navigation-restructure, phase-11, card-grid, image-rendering]

# Tech tracking
tech-stack:
  added: []
  patterns:
    - "Async pipeline: httpx.AsyncClient + asyncio.Semaphore(5) + asyncio.gather(return_exceptions=True)"
    - "Blocking I/O in async context: asyncio.to_thread for file writes"
    - "TDD RED/GREEN: lazy import fixture pattern for test collection before implementation"
    - "Dual-state resume: file exists AND DB image_path set (not either/or)"
    - "Rate-limit safety: 429 not added to done set; zero-result marked done to prevent infinite retry"

key-files:
  created:
    - ps_careers_site/pipeline/fetch_images.py
    - ps_careers_site/pipeline/test_fetch_images.py
  modified: []

key-decisions:
  - "WorkItem._subdir uses explicit dict mapping instead of naive f-string pluralization ('family' → 'families' not 'familys')"
  - "search_unsplash returns the raw response object on 429 so caller can read Retry-After header"
  - "Tests mock search_unsplash/trigger_download directly rather than httpx.AsyncClient to avoid complex async mock chains"
  - "image_rel uses plural subdir names (functions/families/titles) — relative to static/images/ for FastAPI static mount"

patterns-established:
  - "WorkItem pattern: dataclass with entity_type, slug, table, pk_col, pk_val + computed dest/image_rel properties"
  - "Unsplash ToS compliance: trigger_download() fire-and-forget after every successful fetch"
  - "Progress state: JSON file keyed by entity_type:slug, written AFTER DB commit (not before)"

requirements-completed: [IMG-01, IMG-02, IMG-03, IMG-04]

# Metrics
duration: 16min
completed: 2026-03-29
---

# Phase 10 Plan 01: Image Pipeline Summary

**Async Unsplash pipeline with 5-worker semaphore, dual-state resume, and 15-test TDD suite covering all IMG-01 through IMG-04 behaviors**

## Performance

- **Duration:** 16 min
- **Started:** 2026-03-29T01:37:21Z
- **Completed:** 2026-03-29T01:53:22Z
- **Tasks:** 2 (Task 1: RED test suite, Task 2: GREEN implementation)
- **Files modified:** 2

## Accomplishments

- Complete rewrite of `fetch_images.py`: Pexels API fully replaced with Unsplash async pipeline using `httpx.AsyncClient` + `asyncio.Semaphore(5)`
- 15-test pytest suite covering build_query (3 entity types + paren-stripping), fallback query, file storage subdirs, DB update, resume skip logic, partial-state reprocess, concurrency limit, work list ordering, 22+209+1989 counts, 429 rate-limit handling, and zero-result done-marking
- Script is runnable immediately with `UNSPLASH_ACCESS_KEY=your-key python pipeline/fetch_images.py --type function` (22 items, safe for Demo key) or full 2,221-item run with Production key

## Task Commits

Each task was committed atomically:

1. **Task 1: Create test suite (RED phase)** - `9512861` (test)
2. **Task 2: Rewrite fetch_images.py (GREEN phase)** - `563d1f2` (feat)

## Files Created/Modified

- `ps_careers_site/pipeline/fetch_images.py` — Complete async Unsplash pipeline (rewrite of old Pexels script)
- `ps_careers_site/pipeline/test_fetch_images.py` — 15-test TDD suite for all IMG requirements

## Decisions Made

- **WorkItem._subdir uses explicit dict mapping** — naive `f"{entity_type}s"` pluralization gives "familys" not "families"; explicit `{"function": "functions", "family": "families", "title": "titles"}` is correct and self-documenting
- **search_unsplash returns raw response on 429** — lets `fetch_and_save` read the `Retry-After` header value for logging without an extra exception type
- **Tests mock search_unsplash/trigger_download directly** — mocking `httpx.AsyncClient.stream` with `aiter_bytes` requires careful async iterator setup; patching at the module function level is simpler and tests the same behavior
- **image_rel stores relative path from static/images/** — e.g., `functions/administration.jpg`; FastAPI template constructs full URL as `url_for('static', path='images/' + image_path)`

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 1 - Bug] Fixed irregular plural for 'family' entity type**
- **Found during:** Task 2 (GREEN phase) — test_image_stored_in_correct_subdir failed
- **Issue:** `WorkItem.dest` used `f"{self.entity_type}s"` which produced `familys` instead of `families`
- **Fix:** Added `_subdir` property with explicit dict mapping: `{"function": "functions", "family": "families", "title": "titles"}`
- **Files modified:** `ps_careers_site/pipeline/fetch_images.py`
- **Verification:** `test_image_stored_in_correct_subdir` and `test_image_path_is_relative` both pass
- **Committed in:** `563d1f2` (Task 2 commit)

**2. [Rule 1 - Bug] Fixed test mock strategy for async stream context**
- **Found during:** Task 2 (GREEN phase) — `test_fallback_query` and `test_db_updated_after_download` failed with `TypeError: 'async for' requires an object with __aiter__ method`
- **Issue:** `AsyncMock.aiter_bytes` returned a coroutine instead of an async iterable; complex mock chaining through `httpx.AsyncClient.stream` was fragile
- **Fix:** Rewrote tests to mock `search_unsplash` and `trigger_download` at module level rather than mocking the HTTP client internals; stream mock uses a plain `async def async_iter_bytes` generator
- **Files modified:** `ps_careers_site/pipeline/test_fetch_images.py`
- **Verification:** All 15 tests pass
- **Committed in:** `563d1f2` (Task 2 commit)

**3. [Rule 1 - Bug] Fixed test path assertion for Windows backslash compatibility**
- **Found during:** Task 2 (GREEN phase) — `test_image_stored_in_correct_subdir` failed on Windows with `str(path).endswith("functions/administration.jpg")`
- **Issue:** Windows `Path.__str__()` returns backslash-separated paths; `endswith("functions/administration.jpg")` always fails
- **Fix:** Replaced `str(path).endswith(...)` with `path.parts` membership check + `path.name` check — both are path-separator-agnostic
- **Files modified:** `ps_careers_site/pipeline/test_fetch_images.py`
- **Verification:** Test passes on Windows
- **Committed in:** `563d1f2` (Task 2 commit)

---

**Total deviations:** 3 auto-fixed (3× Rule 1 bug fixes)
**Impact on plan:** All auto-fixes were necessary for correctness. No scope creep. Green phase completed in same commit as deviations.

## Issues Encountered

- pytest-asyncio mode is `strict` — `@pytest.mark.asyncio` is required on all async test functions (already done in test file). No action needed.

## User Setup Required

`UNSPLASH_ACCESS_KEY` environment variable must be set before running the pipeline:

```bash
# Get key at: https://unsplash.com/oauth/applications -> Your application -> Access Key
set UNSPLASH_ACCESS_KEY=your-key-here        # Windows
export UNSPLASH_ACCESS_KEY=your-key-here     # Linux/macOS

# Test with Demo key (50 req/hr — 22 function images only):
cd ps_careers_site
python pipeline/fetch_images.py --type function

# Full run with Production key (1,000 req/hr — all 2,221 images):
python pipeline/fetch_images.py

# Dry run (no API calls):
python pipeline/fetch_images.py --dry-run --type function
```

## Next Phase Readiness

- `fetch_images.py` is ready to run when Unsplash key is available — no code changes needed
- Phase 11 (Navigation Restructure) can consume `image_path` from `job_functions`, `job_families`, and `careers` tables
- `image_path` will be NULL until pipeline runs; Phase 10-02 gradient CSS fallback handles null image cards
- `static/images/functions/`, `families/`, and `titles/` directories are created automatically on first run

---
*Phase: 10-image-pipeline*
*Completed: 2026-03-29*

## Self-Check: PASSED

- `ps_careers_site/pipeline/fetch_images.py` — FOUND
- `ps_careers_site/pipeline/test_fetch_images.py` — FOUND
- `.planning/phases/10-image-pipeline/10-01-SUMMARY.md` — FOUND
- Commit `9512861` (RED test suite) — FOUND
- Commit `563d1f2` (GREEN implementation) — FOUND
