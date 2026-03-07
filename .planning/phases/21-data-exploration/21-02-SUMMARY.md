---
phase: 21-data-exploration
plan: 02
subsystem: database
tags: [parquet, pandas, enum, dataclass, coverage-status, jobforge, error-handling]

# Dependency graph
requires:
  - phase: 21-data-exploration/21-01
    provides: DATA-INVENTORY.md and GAP-ANALYSIS.md identifying which parquet files exist and their schemas
provides:
  - CoverageStatus enum (LOAD_ERROR / NOT_FOUND / FOUND) in src/models/parquet.py
  - ParquetResult generic dataclass in src/models/parquet.py
  - read_parquet_safe() function with caching and column stripping in src/services/parquet_reader.py
  - lookup_profile() function with three-state error returns in src/services/parquet_reader.py
affects:
  - phase 22 (profile service -- imports CoverageStatus and lookup_profile)
  - phase 23 (search service -- imports CoverageStatus and read_parquet_safe)

# Tech tracking
tech-stack:
  added: []
  patterns:
    - "CoverageStatus(str, Enum) three-state pattern for typed parquet error handling"
    - "ParquetResult(Generic[T]) dataclass wraps status + optional data + error"
    - "Module-level _cache dict for once-per-process parquet loading"
    - "logger.warning() on EVERY non-FOUND path (DATA-04 contract)"

key-files:
  created:
    - src/models/parquet.py
    - src/services/parquet_reader.py
  modified: []

key-decisions:
  - "Used str,Enum (not StrEnum) for CoverageStatus -- matches EnrichmentSource pattern in src/models/noc.py"
  - "Column whitespace stripping at read_parquet_safe time, not at lookup time -- strips once, consistent for all callers"
  - "Cache keyed by str(path) -- consistent with pathlib Path usage throughout codebase"
  - "lookup_profile propagates LOAD_ERROR transparently (no double-logging) -- warning already emitted by read_parquet_safe"
  - "Verification tests adapted to actual parquet column names (oasis_skills uses unit_group_id not oasis_profile_code)"

patterns-established:
  - "ParquetResult pattern: always check result.status == CoverageStatus.FOUND before accessing result.data"
  - "Parquet service functions never raise -- always return ParquetResult with appropriate status"
  - "Every non-FOUND return path must call logger.warning() before returning"

# Metrics
duration: 5min
completed: 2026-03-07
---

# Phase 21 Plan 02: CoverageStatus and ParquetReader Summary

**CoverageStatus(str, Enum) with three distinct failure states and read_parquet_safe/lookup_profile service functions with mandatory warning logging on all failure paths**

## Performance

- **Duration:** 5 min
- **Started:** 2026-03-07T16:35:05Z
- **Completed:** 2026-03-07T16:40:05Z
- **Tasks:** 2
- **Files modified:** 2

## Accomplishments

- Created `CoverageStatus(str, Enum)` with LOAD_ERROR, NOT_FOUND, FOUND -- three distinct states never collapsed (DATA-03)
- Created `ParquetResult(Generic[T])` dataclass -- typed result wrapper for all parquet operations
- Created `read_parquet_safe()` -- loads parquet with module-level cache, strips column whitespace at read time, logs warning on every failure
- Created `lookup_profile()` -- filters by any profile code column, returns NOT_FOUND with warning when no rows match, propagates LOAD_ERROR transparently
- All 5 integration tests passing against real JobForge gold parquet files

## Task Commits

Each task was committed atomically:

1. **Task 1: Create CoverageStatus enum and ParquetResult dataclass** - `72067b5` (feat)
2. **Task 2: Create ParquetReader service with warning logging** - `7b78d17` (feat)

## Files Created/Modified

- `src/models/parquet.py` - CoverageStatus enum and ParquetResult generic dataclass
- `src/services/parquet_reader.py` - read_parquet_safe() and lookup_profile() with caching, column stripping, and warning logging

## Decisions Made

- Used `str, Enum` (not `StrEnum`) for `CoverageStatus` to match the `EnrichmentSource` pattern established in `src/models/noc.py`.
- Column whitespace stripping applied inside `read_parquet_safe` at read time (not in `lookup_profile`) so all callers receive clean column names regardless of which function they use.
- `lookup_profile` propagates LOAD_ERROR without double-logging -- `read_parquet_safe` already emitted the warning.
- Cache keyed by `str(path)` for pathlib consistency.

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 1 - Bug] Verification tests adapted to actual parquet column names**

- **Found during:** Task 2 verification
- **Issue:** Plan verification script used `oasis_profile_code` as the column name in `oasis_skills.parquet`. Actual column in that file is `unit_group_id`. The column `oasis_profile_code` exists only in `element_labels.parquet`.
- **Fix:** Ran verification against `element_labels.parquet` using `oasis_profile_code` column and profile code `21211.00` (correct file/column/value combination). The `lookup_profile` function is correctly parameterized -- this was only a verification script issue, not a code issue.
- **Files modified:** No source files modified (verification script corrected in-session only)
- **Verification:** All 5 tests pass with correct parameters
- **Committed in:** 7b78d17 (Task 2 commit)

---

**Total deviations:** 1 auto-fixed (Rule 1 - Bug in verification parameters)
**Impact on plan:** No scope creep. The `lookup_profile` function's parameterized design (`code_col` argument) already handles all column name variations correctly. Verification adapted to match reality.

## Issues Encountered

The plan's verification script assumed `oasis_skills.parquet` contains an `oasis_profile_code` column with values like `'21211.00'`. The actual schema uses `unit_group_id` with numeric-string values like `'21211'`. The `lookup_profile` function is correctly parameterized and unaffected -- callers provide `code_col` explicitly. Verified against `element_labels.parquet` which does have `oasis_profile_code` with `'21211.00'` format values.

## User Setup Required

None - no external service configuration required.

## Next Phase Readiness

- Phase 22 (Profile Service) can import `CoverageStatus`, `ParquetResult`, `read_parquet_safe`, and `lookup_profile` directly
- Phase 23 (Search Service) can use the same imports
- Column names for each parquet file documented in `DATA-INVENTORY.md` (from plan 21-01)
- The `oasis_skills.parquet` uses `unit_group_id` (not `oasis_profile_code`) -- Phase 22 must use correct column name when calling `lookup_profile`

---
*Phase: 21-data-exploration*
*Completed: 2026-03-07*
