---
phase: 23-search-service
plan: 02
subsystem: api
tags: [parquet, oasis, search, flask, route, fallback, scoring]

# Dependency graph
requires:
  - phase: 23-01
    provides: SearchParquetReader service with five-tier relevance scoring
  - phase: 22-search-service
    provides: existing /api/search route with OASIS scraping and scoring block
provides:
  - Parquet-first search route in src/routes/api.py (SRCH-01, SRCH-02, SRCH-03)
  - Transparent OASIS fallback when parquet returns None or []
  - OASIS profile URL corrected in scraper.py, mapper.py, selectors.py, search_parquet_reader.py
affects: []

# Tech tracking
tech-stack:
  added: []
  patterns:
    - "Parquet-first with transparent OASIS fallback: try parquet, skip OASIS on hit, fall back silently on None/[]"
    - "Conditional scoring: scoring block executes only in OASIS branch; parquet results arrive pre-scored"
    - "Common post-processing path: hierarchy population, sort, filter, SearchResponse construction run regardless of source"

key-files:
  created: []
  modified:
    - src/routes/api.py
    - src/services/scraper.py
    - src/services/mapper.py
    - src/utils/selectors.py
    - src/services/search_parquet_reader.py

key-decisions:
  - "OASIS profile URL changed from /OaSIS/OaSISSOccProfile to /OASIS/OASISOccProfile with .00 NOC suffix — fix applied in scraper.py, mapper.py, selectors.py, search_parquet_reader.py"
  - "Scoring block kept in OASIS-only branch — parquet results are pre-scored by SearchParquetReader; executing the scoring block again would corrupt scores"
  - "Hierarchy population runs after if/else block — single execution point for both sources; no duplication"

patterns-established:
  - "Fallback pattern: if parquet_results: use them; else: log reason and fall back to live scraping"
  - "OASIS URL convention: /OASIS/OASISOccProfile/{code}.00 (verified 2026-03-09)"

# Metrics
duration: ~45min
completed: 2026-03-09
---

# Phase 23 Plan 02: OASIS Fallback and Route Integration Summary

**Parquet-first /api/search route wired with transparent OASIS fallback, reducing keyword search latency from 5-60s to under 1s; pre-existing OASIS profile URL breakage discovered and fixed.**

## Performance

- **Duration:** ~45 min
- **Started:** 2026-03-09
- **Completed:** 2026-03-09
- **Tasks:** 2 (1 auto + 1 checkpoint, human-approved)
- **Files modified:** 5

## Accomplishments

- Wired `SearchParquetReader` into `/api/search` as the primary path — parquet serves results in under 1 second vs. 5-60 seconds via OASIS scraping
- OASIS fallback path preserved intact: when parquet returns `None` (load error) or `[]` (no matches), the existing OASIS scraping and scoring block executes transparently
- Hierarchy population, sort/filter, and `SearchResponse` construction run on a single shared code path regardless of result source
- Discovered and fixed a pre-existing OASIS profile URL breakage (`/OaSIS/OaSISSOccProfile` → `/OASIS/OASISOccProfile` with `.00` NOC suffix) that was silently preventing profile loads
- Human verified: search for "web designer" returned fast results (parquet path); profile for NOC code 21233 loaded successfully with 200 status

## Task Commits

Each task was committed atomically:

1. **Task 1: Wire parquet search into route with OASIS fallback** - `d05d4da` (feat)
2. **Deviation: OASIS profile URL fix** - `8d868e8` (fix)
3. **Checkpoint: human-verify** - approved by user (no commit — checkpoint gate)

**Plan metadata:** (this commit) (docs: complete plan)

## Files Created/Modified

- `src/routes/api.py` - Added `search_parquet_reader` import; restructured search route body to try parquet first, fall back to OASIS scraping when parquet returns `None` or `[]`; OASIS scoring block preserved but now executes only in the fallback branch; hierarchy population moved to shared post-processing path
- `src/services/scraper.py` - Updated OASIS profile URL from `/OaSIS/OaSISSOccProfile/{code}` to `/OASIS/OASISOccProfile/{code}.00`
- `src/services/mapper.py` - Same OASIS profile URL correction
- `src/utils/selectors.py` - Same OASIS profile URL correction
- `src/services/search_parquet_reader.py` - Same OASIS profile URL correction (used for code-search profile lookups)

## Decisions Made

- **OASIS URL corrected to `/OASIS/OASISOccProfile/{code}.00`:** The previous URL pattern (`/OaSIS/OaSISSOccProfile/{code}`) returned 404s. The correct path uses mixed-case OASIS (not OaSIS), OASISOccProfile (not OaSISSOccProfile), and appends `.00` to the NOC code. Fix applied in all four files that construct profile URLs.
- **Scoring block stays in OASIS branch only:** Parquet results arrive pre-scored by `SearchParquetReader` with the five-tier scoring system (100/95/90/80/50). Re-scoring would overwrite those values incorrectly. The existing scoring block is left untouched but now executes only for OASIS fallback results.
- **Hierarchy population after if/else:** Moving the hierarchy block to after the source-selection block means it executes once for both paths rather than duplicating it in each branch.

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 1 - Bug] OASIS profile URL was broken — /OaSIS/OaSISSOccProfile returning 404**

- **Found during:** Task 1 (route wiring verification — profile load for NOC 21233)
- **Issue:** OASIS had changed its URL scheme. The old pattern `/OaSIS/OaSISSOccProfile/{code}` returned 404. Correct URL is `/OASIS/OASISOccProfile/{code}.00` (case-corrected path, double-letter removed, `.00` suffix added).
- **Fix:** Updated URL construction in all four files that reference OASIS profile URLs: `scraper.py`, `mapper.py`, `selectors.py`, `search_parquet_reader.py`.
- **Files modified:** `src/services/scraper.py`, `src/services/mapper.py`, `src/utils/selectors.py`, `src/services/search_parquet_reader.py`
- **Verification:** `curl http://127.0.0.1:5000/api/profile/21233` returned HTTP 200; profile data loaded successfully.
- **Committed in:** `8d868e8` (separate fix commit)

---

**Total deviations:** 1 auto-fixed (Rule 1 - Bug)
**Impact on plan:** Auto-fix was necessary for correct operation — profile loads were silently broken before this fix. No scope creep; fix applied only to the pre-existing breakage.

## Issues Encountered

- **InsecureRequestWarning in logs:** `urllib3` emits InsecureRequestWarning when making HTTPS requests without SSL verification. This is pre-existing behaviour (not introduced by this plan) — scraper uses `verify=False` to handle self-signed OASIS certificates. No action taken.

## User Setup Required

None - no external service configuration required.

## Next Phase Readiness

- Phase 23 is complete. All three SRCH requirements are satisfied:
  - SRCH-01: Sub-second keyword search via parquet confirmed by human
  - SRCH-02: Tiered scoring (100/95/90/80/50) delivered by SearchParquetReader in Plan 01
  - SRCH-03: Transparent OASIS fallback implemented in route with no user-visible error
- v5.0 JobForge 2.0 Integration milestone (Phases 21-23) is complete
- No blockers for future work. The OASIS URL fix resolves a previously silent breakage that would have affected any phase relying on profile loads.

---
*Phase: 23-search-service*
*Completed: 2026-03-09*
