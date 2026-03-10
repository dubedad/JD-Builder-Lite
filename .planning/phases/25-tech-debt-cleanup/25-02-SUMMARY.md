---
phase: 25-tech-debt-cleanup
plan: 02
subsystem: api
tags: [search, scoring, mapper, parquet, provenance, working-conditions]

# Dependency graph
requires:
  - phase: 24-compliance-hardening
    provides: working_conditions key in export section_sources, OASIS-down fallback
  - phase: 23-search-performance
    provides: search_parquet_reader T3 tier scoring at 90
  - phase: 22-parquet-profile-tabs
    provides: _map_effort_enriched and _map_responsibility_enriched with parquet_tabs pattern
provides:
  - OASIS search stem-in-title tier scores 90 (matches parquet T3 tier)
  - _map_working_conditions_enriched() accepts parquet_tabs and propagates data_source
affects: [future search ranking, working_conditions provenance in JD exports]

# Tech tracking
tech-stack:
  added: []
  patterns:
    - "All three work-context mapper methods (effort, responsibility, working_conditions) share identical parquet_tabs + wc_source extraction pattern"
    - "OASIS and parquet search paths now score identically for equivalent match tiers"

key-files:
  created: []
  modified:
    - src/routes/api.py
    - src/services/mapper.py

key-decisions:
  - "Stem-in-title OASIS score raised to 90 to match search_parquet_reader T3 tier — both paths now rank identically"
  - "wc_source extraction in _map_working_conditions_enriched mirrors effort/responsibility pattern exactly (no deviation from established convention)"

patterns-established:
  - "Work context mapper trio pattern: signature(parquet_tabs=None) -> unpack wc_source from work_context tuple -> pass data_source to EnrichedJDElementData"

# Metrics
duration: 2min
completed: 2026-03-10
---

# Phase 25 Plan 02: Tech Debt Cleanup (Scoring + Mapper Parity) Summary

**Stem-in-title OASIS search score aligned to 90 to match parquet T3 tier; _map_working_conditions_enriched() given parquet_tabs parameter and data_source propagation to match effort/responsibility parity**

## Performance

- **Duration:** 2 min
- **Started:** 2026-03-10T03:06:18Z
- **Completed:** 2026-03-10T03:08:57Z
- **Tasks:** 2/2
- **Files modified:** 2

## Accomplishments

- OASIS fallback search path stem-in-title tier now scores 90 (was 85), matching the T3 tier in `search_parquet_reader.py` so parquet and OASIS search results rank identically for equivalent matches
- `_map_working_conditions_enriched()` signature extended with `parquet_tabs: Optional[dict] = None` and body now extracts `wc_source` via the same `work_context` tuple-unpack used by `_map_effort_enriched()` and `_map_responsibility_enriched()`
- `EnrichedJDElementData` returned from `_map_working_conditions_enriched()` now carries `data_source` — provenance badge will render correctly for working conditions in exported JDs

## Task Commits

Each task was committed atomically:

1. **Task 1: Fix stem-in-title score from 85 to 90 in OASIS search path** - `1ce584c` (fix)
2. **Task 2: Add parquet_tabs parameter and data_source to _map_working_conditions_enriched()** - `dbc3a93` (feat)

**Plan metadata:** (see final commit below)

## Files Created/Modified

- `src/routes/api.py` - stem-in-title relevance_score changed from 85 to 90 (line 163)
- `src/services/mapper.py` - _map_working_conditions_enriched() signature, body, return, and call site updated

## Decisions Made

None - followed plan as specified. Both changes were exact one-to-one alignments with existing patterns already established in the codebase.

## Deviations from Plan

### Minor Plan Documentation Issue (not a code deviation)

The plan's verify step specified `grep -c "data_source=data_source" mapper.py` should return 3. The actual result was 4, because `_map_skills_enriched()` already had `data_source=data_source` before this plan (added in Phase 22). The plan's expectation was based on counting only the work-context trio (effort, responsibility, working_conditions). All 4 occurrences are correct and expected — no code was changed to resolve this; it was a documentation undercount in the plan.

---

**Total deviations:** 0 code deviations — plan executed exactly as written.
**Impact on plan:** None.

## Issues Encountered

- Plan verify step referenced `NOCMapper` as the import name; actual class is `JDMapper`. Used correct class name in verification. Not a code issue — both files import cleanly.

## User Setup Required

None - no external service configuration required.

## Next Phase Readiness

- Phase 25 SC-3 met: OASIS stem-in-title tier scores 90
- Phase 25 SC-4 met: _map_working_conditions_enriched() has parquet_tabs and data_source propagation
- Both files import without errors
- Ready for Phase 25 plan 03 if it exists, or phase complete

---
*Phase: 25-tech-debt-cleanup*
*Completed: 2026-03-10*
