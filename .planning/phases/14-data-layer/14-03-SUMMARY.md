---
phase: 14-data-layer
plan: 03
subsystem: etl-pipeline
tags: [scraper, etl, validation, dama-dmbok, cli, atomic-transactions]

# Dependency graph
requires: [14-01, 14-02]
provides:
  - DAMA-DMBOK 2.0 compliant validation module
  - ETL orchestrator with atomic transactions and rollback
  - CLI command for manual occupational data refresh
  - Full provenance chain from URL to database record
affects: [15-matching-engine]

# Tech tracking
tech-stack:
  added: []
  patterns:
    - "Definition-centric merge (definitions as primary, table for URLs)"
    - "Atomic transactions with rollback on any error"
    - "Validation gates at each ETL stage"
    - "CLI with dry-run mode for safe testing"

key-files:
  created:
    - src/scrapers/validation.py
    - src/scrapers/tbs_scraper.py
    - src/cli/__init__.py
    - src/cli/refresh_occupational.py
  modified: []

key-decisions:
  - "Validation accepts alphanumeric group codes (OM2, PR2, SRC, etc.)"
  - "Groups with empty definitions are skipped with warning (PM/MCO subgroup)"
  - "Definitions page is primary content source; table provides URLs only"
  - "Merge matches definitions to table by group_code, not subgroup"

patterns-established:
  - "validate_or_raise() as gate before database insert"
  - "scrape_all_occupational_groups() convenience function for CLI"
  - "Definition-centric ETL (content from definitions, metadata from table)"

# Metrics
duration: 12min
completed: 2026-02-04
---

# Phase 14 Plan 03: ETL Orchestration and CLI Summary

**DAMA-DMBOK 2.0 compliant validation module, ETL orchestrator with atomic transactions, and CLI command loading 213 groups with 450 inclusions and 165 exclusions**

## Performance

- **Duration:** 12 min
- **Started:** 2026-02-04T05:31:06Z
- **Completed:** 2026-02-04T05:43:08Z
- **Tasks:** 3/3 + 1 fix commit
- **Files created:** 4

## Accomplishments

- Created DAMA-DMBOK 2.0 compliant validation with completeness, consistency, and accuracy checks
- Implemented ETL orchestrator with atomic transactions and rollback on failure
- Built CLI command with --dry-run mode for safe testing without database changes
- Successfully loaded 213 occupational groups with full provenance chain

## Task Commits

Each task was committed atomically:

1. **Task 1: Create DAMA-compliant validation module** - `7737097` (feat)
2. **Task 2: Create ETL orchestrator with atomic transactions** - `a3ac3f2` (feat)
3. **Task 3: Create CLI command for manual refresh** - `e886036` (feat)
4. **Fix: Correct merge logic for definition-centric ETL** - `5bc0a39` (fix)

## Files Created

| File | Purpose | Exports |
|------|---------|---------|
| `src/scrapers/validation.py` | DAMA-DMBOK validation | `validate_completeness`, `validate_consistency`, `validate_accuracy`, `validate_group`, `validate_or_raise`, `ValidationError` |
| `src/scrapers/tbs_scraper.py` | ETL orchestrator | `TBSScraper`, `scrape_all_occupational_groups`, `PARSER_VERSION` |
| `src/cli/__init__.py` | CLI package init | - |
| `src/cli/refresh_occupational.py` | CLI entry point | `main` |

## Data Loaded

| Entity | Count |
|--------|-------|
| Groups | 213 |
| Inclusions | 450 |
| Exclusions | 165 |
| Concordance entries | 90 |
| Provenance records | 2 |
| Skipped (empty definitions) | 1 (PM/MCO) |

## Key Implementation Details

### Validation Module

- **validate_completeness:** Checks required fields exist and are non-empty
- **validate_consistency:** Detects duplicate group_code+subgroup combinations
- **validate_accuracy:** Validates format of codes (alphanumeric), URLs, timestamps
- **validate_or_raise:** Gate function that throws ValidationError if any issues
- Per CONTEXT.md: "Never insert partial or corrupt data"

### ETL Orchestrator

- Single timestamp for entire scrape (per RESEARCH.md Pitfall 6)
- Archives raw HTML before transformation for provenance
- Definition-centric merge: definitions have content, table has URLs
- Atomic transaction with rollback on any error
- Content hash comparison for change detection (though TBS pages have dynamic elements)

### CLI Command

```bash
# Dry run (validate without loading)
python -m src.cli.refresh_occupational --dry-run

# Full scrape with verbose logging
python -m src.cli.refresh_occupational --verbose

# Production refresh
python -m src.cli.refresh_occupational
```

## Decisions Made

| Decision | Rationale |
|----------|-----------|
| Accept alphanumeric codes | TBS uses codes like OM2, PR2, SRC, SRE, SRW |
| Skip empty definitions with warning | PM/MCO subgroup has no definition; warn and continue |
| Definition-centric merge | Table has many subgroup rows with different naming; definitions are canonical |
| Dry-run filters same as full scrape | Consistent behavior between modes |

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 1 - Bug] Fixed validation regex for alphanumeric codes**

- **Found during:** Task 3 verification (dry-run mode)
- **Issue:** Validation rejected valid TBS codes like OM2, PR2, SRC
- **Fix:** Changed regex from `^[A-Z]{2,4}$` to `^[A-Z][A-Z0-9]{1,3}$`
- **Files modified:** `src/scrapers/validation.py`
- **Commit:** e886036

**2. [Rule 1 - Bug] Fixed merge logic for definition-centric ETL**

- **Found during:** Task 3 verification (full scrape)
- **Issue:** Table-centric merge caused duplicate group_code errors; table subgroup names don't match definition subgroup codes
- **Fix:** Rewrote merge to iterate definitions and look up URLs from table by group_code only
- **Files modified:** `src/scrapers/tbs_scraper.py`
- **Commit:** 5bc0a39

**3. [Rule 2 - Missing Critical] Added empty definition filtering**

- **Found during:** Task 3 verification
- **Issue:** PM/MCO subgroup has no definition text on TBS page
- **Fix:** Filter out groups with empty definitions, log warning, continue with valid groups
- **Files modified:** `src/scrapers/tbs_scraper.py`, `src/cli/refresh_occupational.py`
- **Commits:** e886036, 5bc0a39

## Verification Results

| Criterion | Expected | Actual | Status |
|-----------|----------|--------|--------|
| validate_or_raise stops on failure | Raises ValidationError | Raises ValidationError | PASS |
| Transaction rollback on error | No partial data | Implemented | PASS |
| CLI --dry-run shows data | Shows counts | 213 groups, 450 inclusions | PASS |
| Full CLI run populates database | Creates data | data/occupational.db created | PASS |
| Query v_current_occupational_groups | Returns groups | 213 groups | PASS |
| Groups have provenance | provenance_id linked | All groups linked | PASS |
| Inclusions/exclusions have provenance | provenance_id linked | All linked to prov_id=2 | PASS |

## Known Limitations

- **Content hash comparison:** TBS pages have dynamic elements (timestamps, etc.) causing hashes to differ between scrapes even when meaningful data is unchanged. Future improvement could hash only the extracted data.
- **PM/MCO subgroup:** Skipped due to empty definition on TBS page. May be intentional (inherits from PM parent).

## Next Phase Readiness

- Database populated with 213 occupational groups
- Full provenance chain from URL to database record
- Inclusions/exclusions ready for matching engine
- CLI available for manual refresh when TBS updates data
- Ready for Phase 15 (Matching Engine)

---
*Phase: 14-data-layer*
*Completed: 2026-02-04*
