---
phase: 09-data-migration
plan: 01
subsystem: database
tags: [sqlite, csv, migration, python, pytest, tdd]

# Dependency graph
requires: []
provides:
  - job_functions table (22 rows, slugs, descriptions) in careers.sqlite
  - job_families table (209 rows, FK to job_functions, slugs, descriptions) in careers.sqlite
  - careers table: 5 new columns (job_title_description, key_responsibilities, required_skills, typical_education, image_path)
  - All 1989 careers rows enriched from enriched_job_architecture.csv
  - Idempotent migration script pipeline/migrate_v11.py
  - Full pytest test suite (10 tests, all passing)
affects: [10-image-pipeline, 11-navigation-restructure, 12-enhanced-detail-page]

# Tech tracking
tech-stack:
  added: [pytest (test runner, already installed)]
  patterns: [TDD red-green cycle, idempotent SQLite migration, lazy pytest import for deferred module loading]

key-files:
  created:
    - ps_careers_site/pipeline/migrate_v11.py
    - ps_careers_site/pipeline/test_migrate_v11.py
    - ps_careers_site/pytest.ini
  modified:
    - ps_careers_site/careers.sqlite (runtime — gitignored, migrated in place)

key-decisions:
  - "Actual CSV has 22 distinct job functions and 209 job families, not 23/210 as stated in research — tests updated to match reality"
  - "Unconditional UPDATE (not conditional on NULL) used for careers enrichment columns — CSV is authoritative source of truth"
  - "Lazy import inside migrated_db fixture allows pytest --co to collect tests before migrate_v11.py exists (TDD RED phase)"
  - "careers.sqlite is gitignored — migration is a runtime operation, not a version-controlled artifact"

patterns-established:
  - "Pattern: lazy import inside pytest fixture for TDD deferred module loading"
  - "Pattern: column_exists() PRAGMA guard for idempotent ALTER TABLE (SQLite < 3.37 compatibility)"
  - "Pattern: INSERT OR IGNORE for reference table idempotency"
  - "Pattern: unconditional UPDATE from CSV for enrichment columns (CSV = source of truth)"

requirements-completed: [DATA-01, DATA-02, DATA-03, DATA-04, DATA-05, DATA-06]

# Metrics
duration: 10min
completed: 2026-03-28
---

# Phase 9 Plan 01: Data Migration Summary

**SQLite extended with job_functions (22 rows) and job_families (209 rows) tables; all 1989 careers rows enriched from enriched_job_architecture.csv via idempotent migration script with full pytest coverage**

## Performance

- **Duration:** 10 min
- **Started:** 2026-03-28T22:16:19Z
- **Completed:** 2026-03-28T22:26:34Z
- **Tasks:** 3
- **Files modified:** 3 created + 1 runtime DB migration

## Accomplishments

- Created `pipeline/migrate_v11.py`: idempotent migration creates job_functions and job_families tables, adds 5 columns to careers, populates all 1989 rows from CSV
- Created `pipeline/test_migrate_v11.py`: 10 tests covering schema, row counts, FK integrity, enrichment completeness, idempotency, and Horticulture Specialist edge case — all passing
- Created `pytest.ini` with testpaths configuration
- Production `careers.sqlite` migrated: 22 functions, 209 families, 1989 enriched careers rows, 0 FK orphans, 0 NULL enrichment values

## Task Commits

Each task was committed atomically:

1. **Task 1: Create pytest config and migration test suite** - `7c31419` (test)
2. **Task 2: Implement migration script and pass all tests** - `eaf009e` (feat)
3. **Task 3: Run migration on production DB** — runtime operation (DB is gitignored); verified via inline queries

_Note: TDD tasks follow red-green cycle: test commit (RED) → implementation commit (GREEN)_

## Files Created/Modified

- `ps_careers_site/pipeline/migrate_v11.py` — v1.1 migration script: creates tables, adds columns, loads CSV data
- `ps_careers_site/pipeline/test_migrate_v11.py` — 10 pytest tests covering all DATA-* requirements
- `ps_careers_site/pytest.ini` — pytest configuration with testpaths = pipeline
- `ps_careers_site/careers.sqlite` — runtime: 22 job_functions, 209 job_families, 1989 enriched careers rows (gitignored)

## Decisions Made

- **Actual counts are 22 functions and 209 families** — research doc stated 23/210 but direct CSV inspection revealed 22/209. Tests and script updated to match actual data. The Horticulture family exists under Environmental Services (from other rows); only JT_ID=1933 itself has blank function/family.
- **Unconditional UPDATE** chosen over conditional-on-NULL — ensures CSV is always authoritative, avoids partial-update edge cases on re-runs
- **Lazy import in fixture** — `from pipeline.migrate_v11 import run_migration` placed inside fixture body so pytest `--co` can collect tests before the implementation file exists (TDD RED phase requirement)
- **DB is gitignored** — migration is a runtime operation; production state verified via queries, not committed

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 1 - Bug] Corrected function/family row counts from research**
- **Found during:** Task 2 (GREEN phase, first test run)
- **Issue:** Research document stated 23 job functions and 210 job families. Direct CSV inspection confirmed 22 distinct non-blank Job_Function values and 209 distinct job families. The plan's must_haves and test assertions used the incorrect research values.
- **Fix:** Updated test assertions from 23/210 to 22/209. Updated migration script verification messages accordingly.
- **Files modified:** `pipeline/test_migrate_v11.py`, `pipeline/migrate_v11.py`
- **Verification:** All 10 tests pass. Production DB confirms 22 functions, 209 families.
- **Committed in:** `eaf009e` (Task 2 commit)

**2. [Rule 1 - Bug] Fixed Horticulture test assertion**
- **Found during:** Task 2 (GREEN phase, second test run)
- **Issue:** `test_horticulture_specialist` checked `job_families WHERE job_family LIKE '%Horticulture%'` expecting 0. But "Horticulture" is a legitimate family (under Environmental Services, from JT_IDs 421–472 etc.). The test was asserting the wrong thing — the intent was to verify blank-function rows don't create entries, not that the word "Horticulture" doesn't appear.
- **Fix:** Rewrote test to assert: (1) JT_ID=1933 has key_responsibilities populated, (2) no job_functions rows with blank slug, (3) no job_families rows with blank function FK.
- **Files modified:** `pipeline/test_migrate_v11.py`
- **Verification:** Test passes. Behavior verified correct.
- **Committed in:** `eaf009e` (Task 2 commit)

---

**Total deviations:** 2 auto-fixed (both Rule 1 - Bug)
**Impact on plan:** Both fixes correct inaccurate research assertions. Actual data structure is correct and complete. No scope creep.

## Issues Encountered

None beyond the two auto-fixed deviations above.

## User Setup Required

None — no external service configuration required. The migration reads from `C:\Users\Administrator\Projects\jobforge\data\reference\enriched_job_architecture.csv` which was confirmed present at research time.

To re-run migration against production DB:
```bash
cd ps_careers_site && python pipeline/migrate_v11.py
```

To run tests:
```bash
cd ps_careers_site && python -m pytest pipeline/test_migrate_v11.py -v
```

## Next Phase Readiness

- **Phase 10 (Image Pipeline):** Ready. `job_functions` and `job_families` tables exist with slugs. `image_path` columns are NULL on all rows (Phase 10 fills them).
- **Phase 11 (Navigation Restructure):** Ready. 22 functions and 209 families with slugs and descriptions available for L1/L2 card grids.
- **Phase 12 (Enhanced Detail Page):** Ready. `key_responsibilities`, `required_skills`, `typical_education` populated on all 1989 rows.
- **Blockers:** None.

---
*Phase: 09-data-migration*
*Completed: 2026-03-28*
