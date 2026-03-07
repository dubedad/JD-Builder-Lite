---
phase: 21-data-exploration
plan: 03
subsystem: data
tags: [logging, parquet, csv, python, labels_loader, vocabulary]

# Dependency graph
requires:
  - phase: 21-01
    provides: Gap analysis identifying labels_loader.py and vocabulary/index.py as silent failure sources
  - phase: 21-02
    provides: parquet_reader.py reference implementation with correct logger.warning() pattern
provides:
  - logger.warning() on all parquet/CSV load failure paths in labels_loader.py (24 warnings, 8 methods)
  - logger.warning() on all failure paths in vocabulary/index.py (3 warnings: missing file, read error, empty vocabulary)
  - DATA-04 truth fully satisfied: no data load failure silently swallowed in either file
affects:
  - Phase 22 (profile tabs): failure-path visibility during development and production debugging
  - Phase 23 (search service): same visibility for vocabulary-related failures

# Tech tracking
tech-stack:
  added: []
  patterns:
    - "logger = logging.getLogger(__name__) at module level in every service file that loads external data"
    - "logger.warning() before every return False or raise in data load methods"
    - "except Exception as e: (not bare except Exception:) to capture error details for warning messages"

key-files:
  created: []
  modified:
    - src/services/labels_loader.py
    - src/vocabulary/index.py

key-decisions:
  - "Additive-only approach: logger.warning() added alongside existing self._load_error and return False, not replacing them"
  - "bare except Exception: fixed to except Exception as e: in 6 methods in labels_loader.py to capture error details"
  - "vocabulary/index.py wraps pd.read_parquet() in try/except that logs and re-raises to preserve original exception type and traceback"

patterns-established:
  - "Warning-before-raise pattern: log the warning first, then raise -- both actions happen, warning is never lost"
  - "%-style format strings in logger.warning() (not f-strings) for deferred formatting performance"

# Metrics
duration: 5min
completed: 2026-03-07
---

# Phase 21 Plan 03: Warning Logging Gap Closure Summary

**logger.warning() added to all 24 failure paths across 8 load methods in labels_loader.py and all 3 failure paths in vocabulary/index.py, fully closing DATA-04 Truth 4**

## Performance

- **Duration:** 5 min
- **Started:** 2026-03-07T19:15:30Z
- **Completed:** 2026-03-07T19:20:28Z
- **Tasks:** 2
- **Files modified:** 2

## Accomplishments
- labels_loader.py now emits logger.warning() on every failure path (no-pandas, file-not-found, read-exception) in all 8 `_load_*` methods -- 24 warning calls total
- vocabulary/index.py now logs before FileNotFoundError raise, before pd.read_parquet() exception propagation, and before ValueError raise for empty vocabulary -- 3 warning calls
- Phase 21 Truth 4 (DATA-04) moved from PARTIAL to FULLY SATISFIED: no parquet or CSV load failure is silently swallowed in any service that reads external data files

## Task Commits

Each task was committed atomically:

1. **Task 1: Add logger.warning() to labels_loader.py failure paths** - `eb19b0e` (feat)
2. **Task 2: Add logger.warning() to vocabulary/index.py failure paths** - `3a4df07` (feat)

**Plan metadata:** (docs commit to follow)

## Files Created/Modified
- `src/services/labels_loader.py` - Added `import logging`, `logger = logging.getLogger(__name__)`, and 24 `logger.warning()` calls across all 8 `_load_*` methods; fixed 6 bare `except Exception:` to `except Exception as e:`
- `src/vocabulary/index.py` - Added `import logging`, `logger = logging.getLogger(__name__)`, and 3 `logger.warning()` calls: before FileNotFoundError raise, wrapping pd.read_parquet() with log-and-reraise, and before ValueError raise for empty vocabulary

## Decisions Made
- Additive-only approach: `logger.warning()` calls added alongside existing `self._load_error` assignments and `return False` statements -- neither replaced. This preserves the runtime error inspection path (`get_error()`) while adding observability to the log stream.
- Fixed 6 bare `except Exception:` clauses in labels_loader.py to `except Exception as e:` -- required to capture the exception variable for the warning message. No behavioral change since these already returned False.
- In vocabulary/index.py, wrapped `pd.read_parquet()` in a try/except that logs and re-raises (not silences) -- preserves original exception type and traceback for callers.

## Deviations from Plan

None - plan executed exactly as written.

## Issues Encountered
- macOS system does not have `timeout` as a standalone command (it is a shell builtin in some contexts only). Ran verification commands directly without timeout wrapper; all completed within 1-2 seconds. No functional impact.

## User Setup Required
None - no external service configuration required.

## Next Phase Readiness
- DATA-04 (warning logging) fully satisfied: parquet_reader.py (21-02), labels_loader.py (21-03), and vocabulary/index.py (21-03) all emit logger.warning() on every failure path
- Phase 21 verification truth 4 status: PARTIAL -> FULLY SATISFIED
- Phase 22 (Profile Service) can begin: all Phase 21 data exploration and gap-closure work complete
- No blockers remaining within Phase 21

---
*Phase: 21-data-exploration*
*Completed: 2026-03-07*
