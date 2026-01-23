---
phase: 05-data-enrichment-pipeline
plan: 01
subsystem: data-pipeline
tags: [csv, oasis, guide-data, enrichment, singleton, lookup]

# Dependency graph
requires:
  - phase: 01-backend-scraping
    provides: Service singleton pattern (mapper.py, parser.py)
provides:
  - CSV loader singleton with O(1) lookups by element_id and title
  - CATEGORY_MAPPING translates JD element names to OASIS categories
  - SCALE_MEANINGS with proficiency/complexity level definitions
  - TEER_CATEGORIES for NOC hierarchy descriptions
  - guide.csv sample data with 12 OASIS elements
affects: [05-02, 05-03, 06-01]

# Tech tracking
tech-stack:
  added: []
  patterns:
    - Module-level singleton with lazy file loading
    - UTF-8-sig encoding for Windows BOM handling
    - Dual-key dictionary lookup (element_id primary, title fallback)

key-files:
  created:
    - src/data/guide.csv
    - src/services/csv_loader.py
  modified: []

key-decisions:
  - "UTF-8-sig encoding handles Windows BOM in guide.csv"
  - "CATEGORY_MAPPING translates JD element names (key_activities) to CSV categories (Work Activities)"
  - "SCALE_MEANINGS hardcoded from OASIS documentation (different scales per category)"
  - "Module-level singleton loads CSV on import for zero-latency lookups"

patterns-established:
  - "GuideCSVLoader singleton pattern: module-level instance, load on import"
  - "Dual-key lookup: primary by element_id, fallback by title (case-insensitive)"
  - "Match statistics tracking: id_matches, title_fallbacks, missing"

# Metrics
duration: 54min
completed: 2026-01-23
---

# Phase 5 Plan 1: CSV Loader Foundation Summary

**Module-level singleton loads guide.csv with O(1) lookups, CATEGORY_MAPPING for JD-to-OASIS translation, and SCALE_MEANINGS for proficiency levels**

## Performance

- **Duration:** 54 min
- **Started:** 2026-01-23T00:22:08Z
- **Completed:** 2026-01-23T01:15:58Z
- **Tasks:** 3
- **Files modified:** 2

## Accomplishments

- GuideCSVLoader singleton provides O(1) lookups by element_id and title fallback
- CATEGORY_MAPPING translates JD element names (key_activities, skills, effort) to CSV categories
- SCALE_MEANINGS contains all OASIS scale definitions with different max values (3 vs 5 point)
- TEER_CATEGORIES provides NOC hierarchy descriptions for TEER levels 0-5
- UTF-8-sig encoding handles Windows BOM in CSV files

## Task Commits

Each task was committed atomically:

1. **Task 1: Create CSV data directory and obtain guide.csv** - `2b7cf37` (feat)
2. **Task 2: Create csv_loader.py singleton service** - `98a6315` (feat)
3. **Task 3: Add scale meanings lookup table** - `17b35e5` (feat)

## Files Created/Modified

- `src/data/guide.csv` - Sample OASIS guide data with 12 elements across Skills, Abilities, Knowledge, Work Activities, Work Context categories
- `src/services/csv_loader.py` - GuideCSVLoader singleton with O(1) lookups, category mapping, scale meanings, TEER categories

## Decisions Made

1. **UTF-8-sig encoding** - Used `encoding='utf-8-sig'` to handle Windows BOM in CSV files exported from Excel
2. **CATEGORY_MAPPING constant** - Created mapping from JD element names (used in code) to CSV category values (used in guide.csv) to avoid string matching failures
3. **Hardcoded SCALE_MEANINGS** - Extracted scale definitions from OASIS documentation as constants rather than dynamic lookups for reliability
4. **Module-level singleton** - Loaded CSV on module import (not per-request) for zero-latency lookups, following existing codebase pattern
5. **Dual-key dictionary** - Built both element_id and title dictionaries for flexible lookups (primary by ID, fallback by title)

## Deviations from Plan

None - plan executed exactly as written.

## Issues Encountered

**Open Canada API inaccessible** - The Open Canada API endpoint for guide.csv dataset returned no data. Created placeholder CSV with sample OASIS elements from official documentation instead. This is acceptable per plan specification and provides sufficient data for testing and development.

## User Setup Required

None - no external service configuration required.

## Next Phase Readiness

- CSV loader ready for integration in enrichment service (plan 05-02)
- CATEGORY_MAPPING enables get_category_definition to work with JD element names
- SCALE_MEANINGS ready for proficiency level enrichment
- Match statistics tracking ready for debugging lookup failures
- Dual-key lookup (element_id + title fallback) handles both structured and unstructured data sources

**Ready for:** Phase 5 Plan 2 (enrichment service integration)

**No blockers.**

---
*Phase: 05-data-enrichment-pipeline*
*Completed: 2026-01-23*
