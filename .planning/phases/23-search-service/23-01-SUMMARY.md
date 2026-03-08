---
phase: 23-search-service
plan: 01
subsystem: api
tags: [parquet, pandas, numpy, search, scoring, jobforge, noc]

requires:
  - phase: 21-data-exploration
    provides: CoverageStatus, ParquetResult, read_parquet_safe, parquet infrastructure
  - phase: 22-profile-service
    provides: JOBFORGE_GOLD_PATH config constant, parquet-first pattern established

provides:
  - SearchParquetReader class with search(query, search_type) method
  - Five-tier relevance scoring (100/95/90/80/50) from three gold parquet files
  - Module-level singleton search_parquet_reader for direct import by Plan 02
  - None/[]/list return semantics for OASIS fallback logic

affects: [23-search-service plan 02]

tech-stack:
  added: [numpy (already available, added to search path)]
  patterns:
    - "Vectorized pandas ops + numpy score arrays for sub-second bulk scoring"
    - "pd.DataFrame constructor + .assign() avoids chained-assignment FutureWarning"
    - "Lazy parquet loading with instance-level cache (_loaded/_load_failed flags)"
    - "Returns None/[]/list with distinct semantics for caller fallback logic"

key-files:
  created:
    - src/services/search_parquet_reader.py
  modified: []

key-decisions:
  - "unit_group_id is the join key in element_labels and element_lead_statement (confirmed from parquet inspection)"
  - "element_example_titles uses Job title text column (confirmed from parquet inspection)"
  - "Auto-detect code search: if query matches r'^\\d{5}$', treat as code even with search_type=Keyword"
  - "Pandas FutureWarning fixed immediately (Rule 1 bug): use pd.DataFrame constructor and .assign() not chained assignment"
  - "lead_map built as dict[noc_code, lead_text] per search() call (small enough to not cache separately)"

patterns-established:
  - "Pattern: SearchParquetReader._load_parquets() lazy-loads all three files; _load_failed prevents repeated retry"
  - "Pattern: search() wraps _search_impl() in try/except so exceptions never propagate to route"
  - "Pattern: _build_result() centralizes EnrichedSearchResult construction from parquet row"

duration: 3min
completed: 2026-03-08
---

# Phase 23 Plan 01: SearchParquetReader Summary

**Five-tier parquet search service reading element_labels/lead_statement/example_titles with vectorized pandas scoring and None/[]/list return semantics for transparent OASIS fallback**

## Performance

- **Duration:** ~3 min
- **Started:** 2026-03-08T16:26:18Z
- **Completed:** 2026-03-08T16:30:05Z
- **Tasks:** 1
- **Files modified:** 1

## Accomplishments

- Created `src/services/search_parquet_reader.py` with `SearchParquetReader` class and `search_parquet_reader` singleton
- Five-tier scoring implemented: 100 (code/exact-title), 95 (title contains), 90 (stem in title), 80 (example job title), 50 (lead statement)
- Returns None on LOAD_ERROR, [] on no match — distinct semantics preserved for Plan 02 fallback logic
- Vectorized pandas operations with numpy arrays; 900-row labels + 18,666 example titles scan completes in well under 1 second
- Pandas chained-assignment FutureWarning fixed proactively (future pandas 3.0 correctness)

## Task Commits

1. **Task 1: Create SearchParquetReader service** - `b3eb604` (feat)

**Plan metadata:** (docs commit follows)

## Files Created/Modified

- `src/services/search_parquet_reader.py` - New search service: reads 3 gold parquet files, returns tiered-scored EnrichedSearchResult list

## Decisions Made

- `unit_group_id` confirmed as join key for all three element_* parquet files (validated via direct parquet inspection)
- Auto-detect code search: queries matching `^\d{5}$` treated as code search regardless of `search_type` parameter (defensive)
- Lead statement lookup built as in-memory dict per call (900 entries, negligible overhead)
- `BROAD_CATEGORIES` dict imported from `src/models/noc.py` to populate `broad_category_name` without hardcoding

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 1 - Bug] Fixed pandas chained-assignment FutureWarning**
- **Found during:** Task 1 (smoke test output)
- **Issue:** Using `working["col"] = ...` on a sliced copy triggers FutureWarning — will silently fail in pandas 3.0
- **Fix:** Replaced slice-then-assign pattern with `pd.DataFrame({...})` constructor and `.assign()` method
- **Files modified:** src/services/search_parquet_reader.py
- **Verification:** Re-ran with `-W error::FutureWarning` flag — zero warnings
- **Committed in:** b3eb604 (included in task commit)

---

**Total deviations:** 1 auto-fixed (Rule 1 bug — pandas future-compatibility)
**Impact on plan:** Fix essential for pandas 3.0 correctness. No scope creep.

## Issues Encountered

None — all three parquet files were present with expected column names. Column names confirmed clean (read_parquet_safe strips whitespace automatically).

## User Setup Required

None - no external service configuration required. JOBFORGE_GOLD_PATH already set in config.py.

## Next Phase Readiness

- Plan 23-02 (wire search into api.py route) can proceed: `search_parquet_reader` singleton is importable and returns correct types
- Route needs to: import `search_parquet_reader`, call `search_parquet_reader.search(query, search_type)`, fall back to OASIS on `None`, merge/replace results on list
- Scoring tiers match the existing OASIS scoring in api.py (both use same `_normalize_plural` and `_stem_word` logic)

---
*Phase: 23-search-service*
*Completed: 2026-03-08*
