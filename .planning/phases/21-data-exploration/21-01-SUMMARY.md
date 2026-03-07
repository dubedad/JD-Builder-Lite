---
phase: 21-data-exploration
plan: 01
subsystem: database
tags: [pandas, parquet, jobforge, oasis, data-exploration, documentation]

# Dependency graph
requires: []
provides:
  - "DATA-INVENTORY.md: structured inventory of all 25 gold parquet files with schema, row counts, profile counts, and OASIS mapping"
  - "GAP-ANALYSIS.md: explicit named gap table (5 gaps) and covered fields table (13 fields) for Phase 22 and Phase 23 implementers"
affects:
  - 21-02 (CoverageStatus implementation references these gap findings)
  - 22-profile-service (profile tab implementation uses inventory to choose parquet vs OASIS per field)
  - 23-search-service (search uses parquet files confirmed in inventory)

# Tech tracking
tech-stack:
  added: []
  patterns:
    - "oasis_profile_code format: '21211.00' (not '21211') for element_* and oasis_* file lookups"
    - "column whitespace strip: df.columns = df.columns.str.strip() required after reading oasis_* files"

key-files:
  created:
    - .planning/phases/21-data-exploration/DATA-INVENTORY.md
    - .planning/phases/21-data-exploration/GAP-ANALYSIS.md
  modified: []

key-decisions:
  - "element_main_duties.parquet must never be queried in Phase 22 -- only 8 rows / 3 profiles; OASIS fallback is unconditional"
  - "Interests and Personal Attributes are covered by source CSV via LabelsLoader -- no Phase 22 change needed"
  - "Core Competencies and Career Mobility have no data in any tier -- OASIS scraping only"

patterns-established:
  - "DATA-INVENTORY.md format: Profile Data / Reference / Labour Market sections with per-file schema blocks"
  - "GAP-ANALYSIS.md format: Gap Table + Covered Fields Table + profile code format note + whitespace warning + decision summary"

# Metrics
duration: 6min
completed: 2026-03-07
---

# Phase 21 Plan 01: Data Inventory and Gap Analysis Summary

**Two developer-facing reference documents produced from direct pandas inspection of all 25 gold parquet files: inventory (schema/rows/profiles/OASIS mapping) and explicit named gap table (5 gaps, 13 covered fields, whitespace warnings, profile code format)**

## Performance

- **Duration:** 6 min
- **Started:** 2026-03-07T16:34:12Z
- **Completed:** 2026-03-07T16:40:04Z
- **Tasks:** 2
- **Files modified:** 2 created

## Accomplishments

- Inspected all 25 gold parquet files with pandas, recording schema, row counts, and profile key counts
- Confirmed 5 OASIS fields have no adequate parquet equivalent (Main Duties, Interests, Personal Attributes, Core Competencies, Career Mobility)
- Confirmed 13 OASIS fields are fully covered by gold parquet (Skills, Abilities, Knowledge, Work Activities, Work Context, Label, Lead Statement, Example Titles, Employment Requirements, Workplaces, Exclusions, Additional Info, NOC Definition)
- Documented critical `element_main_duties.parquet` ETL gap: 8 rows / 3 profiles vs expected 4,991 rows / 900 profiles
- Documented column whitespace contamination in 5 oasis_* files (14 + 6 + 3 + 3 + 1 affected columns)
- Documented profile code format distinction: `oasis_profile_code` ('21211.00') vs `noc_code` ('21211')

## Task Commits

Each task was committed atomically:

1. **Task 1: Create DATA-INVENTORY.md from gold parquet files** - `5c89419` (docs)
2. **Task 2: Create GAP-ANALYSIS.md from inventory findings** - `c576fd5` (docs)

**Plan metadata:** (committed with this summary)

## Files Created/Modified

- `.planning/phases/21-data-exploration/DATA-INVENTORY.md` - Structured inventory of all 25 gold parquet files (345 lines); three sections: Profile Data Files, Reference/Dimensional Files, Labour Market Files; per-file schema blocks with columns, row counts, profile counts, OASIS mapping, and notes
- `.planning/phases/21-data-exploration/GAP-ANALYSIS.md` - Explicit gap analysis (178 lines); gap table with 5 entries, covered fields table with 13 entries, profile code format note, column whitespace warning table with per-file counts and fix pattern, decision summary for Phase 22 implementers

## Decisions Made

- `element_main_duties.parquet` must not be queried in Phase 22: the file loads without error and returns `CoverageStatus.FOUND` on open, but covers only 3 of 900 profiles. The OASIS fallback is unconditional until JobForge ETL completes. A code comment in Phase 22 must reference GAP-ANALYSIS.md.
- Interests and Personal Attributes require no Phase 22 changes: the existing LabelsLoader correctly serves these from source CSVs already. There is no regression risk from the gold parquet gap.
- Core Competencies and Career Mobility have no data in any tier: no parquet, no CSV. Phase 22 must use OASIS live scraping for these fields and document whether the OASIS scraper currently parses them.

## Deviations from Plan

None -- plan executed exactly as written. All 25 parquet files read successfully with no read errors. The data confirmed the research findings without surprises.

## Issues Encountered

None. All 25 gold parquet files were readable by pandas. The `element_main_duties.parquet` gap was expected from prior research and confirmed as documented.

## User Setup Required

None -- no external service configuration required. Both outputs are developer-facing planning documents.

## Next Phase Readiness

- DATA-01 satisfied: DATA-INVENTORY.md lists all 25 gold parquet files with schema, row counts, profile counts, and OASIS mapping
- DATA-02 satisfied: GAP-ANALYSIS.md explicitly names 5 gaps with evidence and fallback strategy
- Phase 21 plan 02 (CoverageStatus implementation) can proceed using these documents as input
- Phase 22 (Profile Service) implementers have a clear decision table: which fields to read from parquet vs OASIS
- Phase 23 (Search Service) implementers know which parquet files are available for search queries
- Blocker for Phase 22: `element_main_duties.parquet` ETL gap means Main Duties requires unconditional OASIS fallback; this is documented and no code workaround is needed

---
*Phase: 21-data-exploration*
*Completed: 2026-03-07*
