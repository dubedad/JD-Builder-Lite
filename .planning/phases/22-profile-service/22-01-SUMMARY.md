---
phase: 22-profile-service
plan: 01
subsystem: api
tags: [parquet, pandas, jobforge, oasis, profile, fallback]

requires:
  - phase: 21-data-exploration
    provides: CoverageStatus, ParquetResult, read_parquet_safe, lookup_profile, parquet infrastructure

provides:
  - ProfileParquetReader service reading 5 oasis_* parquet files with OASIS fallback
  - data_source field on EnrichedJDElementData ("jobforge" | "oasis")
  - Parquet-first mapper wiring for Skills, Abilities, Knowledge, Work Activities, Work Context
  - JOBFORGE_GOLD_PATH config constant

affects: [22-profile-service, 23-search-service]

tech-stack:
  added: []
  patterns:
    - "Parquet-first with OASIS fallback: try parquet, fall through on LOAD_ERROR/NOT_FOUND/empty"
    - "noc_to_oasis_code(): NOC '21211' -> ['21211.00', '21211.01'] candidates"
    - "data_source field propagates from service layer to API response JSON"

key-files:
  created:
    - src/services/profile_parquet_reader.py
  modified:
    - src/config.py
    - src/models/responses.py
    - src/services/mapper.py

key-decisions:
  - "OASIS_CODE_COL = 'oasis_code' for all 5 oasis_* files (NOT oasis_profile_code)"
  - "element_main_duties.parquet never queried (8 rows / 3 profiles - ETL incomplete)"
  - "Work Context effort/responsibility: data_source='jobforge' because labels_loader already reads oasis_workcontext.parquet"
  - "key_activities data_source always 'oasis' (Main Duties anchors it to OASIS)"
  - "EMPTY_VALID (parquet FOUND but all ratings zero) falls back to OASIS path"

patterns-established:
  - "Pattern: get_all_profile_tabs(noc_code) returns dict[tab_key, (ratings, source)] for all 5 tabs"
  - "Pattern: parquet_tabs passed as Optional[dict] parameter to all _map_*_enriched() methods"

duration: 45min
completed: 2026-03-08
---

# Plan 22-01: ProfileParquetReader + Mapper Wiring Summary

**ProfileParquetReader service reading 5 oasis_* parquet files wired into mapper as primary data path; all 5 profile tabs now serve from parquet for covered profiles with transparent OASIS fallback and data_source tracking**

## Performance

- **Duration:** ~45 min (split across two sessions)
- **Started:** 2026-03-07
- **Completed:** 2026-03-08T13:13:32Z
- **Tasks:** 2
- **Files modified:** 4

## Accomplishments

- Created `src/services/profile_parquet_reader.py` with `get_all_profile_tabs()`, `get_profile_tab()`, `extract_dimension_ratings()`, `noc_to_oasis_code()`
- Added `data_source: str = "oasis"` field to `EnrichedJDElementData` in responses.py
- Wired `get_all_profile_tabs()` into mapper.py — all 5 tabs (Skills, Abilities, Knowledge, Work Activities, Work Context) now check parquet first
- Verified: NOC 21211 returns 25/28/7/35/39 ratings from jobforge for skills/abilities/knowledge/work_activities/work_context

## Task Commits

1. **Task 1: Create ProfileParquetReader and add JOBFORGE_GOLD_PATH** - `88c0468` (feat)
2. **Task 2: Extend response model and wire mapper** - `d6ce242` (feat)

## Files Created/Modified

- `src/services/profile_parquet_reader.py` - New service: reads 5 oasis_* files, returns (ratings, data_source) per tab
- `src/config.py` - Added JOBFORGE_GOLD_PATH constant
- `src/models/responses.py` - Added data_source field to EnrichedJDElementData
- `src/services/mapper.py` - Parquet-first wiring; all _map_*_enriched() methods accept parquet_tabs

## Decisions Made

- OASIS_CODE_COL hardcoded as `"oasis_code"` (not `oasis_profile_code`) — confirmed correct for all 5 oasis_* files
- Main Duties always OASIS: element_main_duties.parquet has only 8 rows (3 of 900 profiles); code comment references GAP-ANALYSIS.md
- key_activities data_source is always "oasis" because Main Duties anchors the element to OASIS regardless of Work Activities parquet source
- Work Context effort/responsibility use data_source from parquet_tabs["work_context"] — labels_loader already reads oasis_workcontext.parquet, so this is consistent

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 3 - Blocking] Session interruption — effort/responsibility signatures incomplete**
- **Found during:** Task 2 continuation (session resumed after context limit)
- **Issue:** `_map_effort_enriched` and `_map_responsibility_enriched` were called with `parquet_tabs` but method signatures hadn't been updated yet
- **Fix:** Added `parquet_tabs: Optional[dict] = None` parameter and `data_source` to both methods
- **Files modified:** src/services/mapper.py
- **Verification:** `inspect.signature()` confirmed all 4 methods accept parquet_tabs; get_all_profile_tabs('21211') returns jobforge for all 5 tabs
- **Committed in:** d6ce242

---

**Total deviations:** 1 auto-fixed (blocking — incomplete method signatures from interrupted session)
**Impact on plan:** No scope changes, just completion of partially-done work.

## Issues Encountered

None beyond the session interruption handled above.

## Next Phase Readiness

- Plan 22-02 (source badge UI) can proceed: `data_source` field is in the API response JSON for all profile tabs
- `profile.skills.data_source`, `profile.effort.data_source`, `profile.responsibility.data_source`, `profile.key_activities.data_source` all present in API response
- Fallback verified: unknown NOC codes fall back gracefully (no crash)

---
*Phase: 22-profile-service*
*Completed: 2026-03-08*
