---
phase: 09-data-migration
plan: "02"
subsystem: pipeline
tags: [sqlite, pytest, sys-exit, guard-clause, tdd]

# Dependency graph
requires:
  - phase: 09-data-migration-01
    provides: migrate_v11.py with idempotent migration logic
provides:
  - Pre-flight guard in migrate_v11.py that exits cleanly on missing DB or missing careers table
  - Two regression tests (test_guard_missing_db, test_guard_empty_db) covering the UAT gap
affects: [09-data-migration, ci-pipelines, developer-onboarding]

# Tech tracking
tech-stack:
  added: []
  patterns: [pre-flight guard pattern using sys.exit(1) before any DB connection]

key-files:
  created: []
  modified:
    - ps_careers_site/pipeline/migrate_v11.py
    - ps_careers_site/pipeline/test_migrate_v11.py

key-decisions:
  - "Pre-flight guard placed before sqlite3.connect so missing-file case never opens a DB connection"
  - "Old RuntimeError guard inside try block removed — superseded by pre-flight; removal keeps code clean"

patterns-established:
  - "Pre-flight pattern: validate file existence + table existence before opening main connection"

requirements-completed: [DATA-01]

# Metrics
duration: 8min
completed: 2026-03-29
---

# Phase 09 Plan 02: migrate_v11 Guard Clause Summary

**Pre-flight sys.exit(1) guard in migrate_v11.py eliminates raw traceback when running on a fresh machine with no careers.sqlite**

## Performance

- **Duration:** ~8 min
- **Started:** 2026-03-29T05:58:25Z
- **Completed:** 2026-03-29T06:06:XX Z
- **Tasks:** 2 (TDD RED + GREEN)
- **Files modified:** 2

## Accomplishments

- Replaced bare `RuntimeError` guard with a pre-flight check that fires before any `sqlite3.connect` call
- Missing DB file now prints a one-line actionable message ("Run ingest.py first") and exits with code 1 — no traceback
- Missing `careers` table in an existing DB also exits cleanly with code 1
- Two new regression tests (`test_guard_missing_db`, `test_guard_empty_db`) lock in this behaviour
- All 12 tests pass (10 original + 2 new guard tests)

## Task Commits

Each task was committed atomically:

1. **Task 1: Add pre-flight guard test (RED)** - `7a6256b` (test)
2. **Task 2: Replace RuntimeError guard with sys.exit pre-flight check (GREEN)** - `4b5d091` (fix)

**Plan metadata:** _(docs commit follows)_

_Note: TDD tasks have two commits — failing test (RED) then implementation (GREEN)_

## Files Created/Modified

- `ps_careers_site/pipeline/test_migrate_v11.py` — Added `test_guard_missing_db` and `test_guard_empty_db` (lines 216-244)
- `ps_careers_site/pipeline/migrate_v11.py` — Added `import sys`; added pre-flight block after print statements; removed old `RuntimeError` guard inside `try` block

## Decisions Made

- Pre-flight guard placed before `sqlite3.connect` so the missing-file case never tries to open a connection (avoids sqlite3 auto-creating an empty file on some platforms)
- Old `RuntimeError` guard inside the `try` block removed entirely — it can never fire now and removing it keeps the code readable

## Deviations from Plan

None - plan executed exactly as written.

## Issues Encountered

None.

## User Setup Required

None - no external service configuration required.

## Next Phase Readiness

- Phase 09 gap closure complete — `migrate_v11.py` now behaves correctly on a fresh machine
- DATA-01 requirement fully satisfied: both guard conditions covered by tests
- No blockers for downstream phases

---
*Phase: 09-data-migration*
*Completed: 2026-03-29*
