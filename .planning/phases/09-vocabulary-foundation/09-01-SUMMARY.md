---
phase: 09-vocabulary-foundation
plan: 01
subsystem: vocabulary
tags: [pandas, pyarrow, watchdog, parquet, noc, vocabulary]

# Dependency graph
requires:
  - phase: none
    provides: "First phase of v3.0 milestone"
provides:
  - VocabularyIndex class for NOC term lookup
  - VocabularyValidator with coverage percentage calculation
  - Hot-reload file watcher for parquet files
  - Flask startup integration
affects: [12-constrained-generation, 13-generation-pipeline]

# Tech tracking
tech-stack:
  added: [pandas, pyarrow, watchdog]
  patterns: [vocabulary-indexing, hot-reload-file-watching]

key-files:
  created:
    - src/vocabulary/__init__.py
    - src/vocabulary/index.py
    - src/vocabulary/validator.py
    - src/vocabulary/watcher.py
  modified:
    - requirements.txt
    - src/config.py
    - src/app.py

key-decisions:
  - "Index individual words from multi-word phrases for better matching"
  - "Use casefold() for case-insensitive comparison (handles Unicode)"
  - "Load vocabulary synchronously at app startup (fast <200ms)"

patterns-established:
  - "Vocabulary lookup via VocabularyIndex.is_noc_term()"
  - "Text validation via VocabularyValidator.validate_text()"
  - "Module-level vocab_index in app.py for global access"

# Metrics
duration: 10min
completed: 2026-02-03
---

# Phase 9 Plan 01: Vocabulary Foundation Summary

**NOC vocabulary index from JobForge parquet files with 417 terms, case-insensitive lookup, coverage percentage validation, and hot-reload file watching**

## Performance

- **Duration:** 10 min
- **Started:** 2026-02-03T22:17:50Z
- **Completed:** 2026-02-03T22:28:08Z
- **Tasks:** 3
- **Files modified:** 7

## Accomplishments

- VocabularyIndex loads 417 vocabulary terms from 4 OASIS parquet files (abilities, skills, knowledges, workactivities)
- Case-insensitive term lookup using casefold() handles "Active", "active", "ACTIVE" identically
- VocabularyValidator calculates coverage percentage excluding stop words
- Hot-reload file watcher monitors parquet files and reloads vocabulary automatically
- Flask app initializes vocabulary at startup with logged term count

## Task Commits

Each task was committed atomically:

1. **Task 1: Create VocabularyIndex class with parquet loading** - `dae00b4` (feat)
2. **Task 2: Create VocabularyValidator with coverage percentage** - `94953e6` (feat)
3. **Task 3: Add hot-reload watcher and Flask startup integration** - `e73cfa5` (feat)

## Files Created/Modified

- `src/vocabulary/__init__.py` - Module exports (VocabularyIndex, VocabularyValidator, start_vocabulary_watcher)
- `src/vocabulary/index.py` - VocabularyIndex class loading 417 terms from parquet files
- `src/vocabulary/validator.py` - VocabularyValidator with validate_text() returning coverage metrics
- `src/vocabulary/watcher.py` - VocabularyFileHandler and start_vocabulary_watcher() for hot-reload
- `requirements.txt` - Added pandas==2.2.3, pyarrow==19.0.0, watchdog==6.0.0
- `src/config.py` - Added JOBFORGE_BRONZE_PATH configuration
- `src/app.py` - Added initialize_vocabulary() and call in create_app()

## Decisions Made

1. **Index individual words from phrases**: Multi-word column names like "Active Listening" are split so both "active" and "listening" are indexed individually. This improves matching for generated text validation.

2. **Use casefold() instead of lower()**: casefold() provides better Unicode handling for internationalized text.

3. **Synchronous vocabulary loading**: Parquet files are tiny (<200KB total) and load in milliseconds. No async complexity needed.

4. **Stop words set**: Defined 24 common stop words excluded from coverage calculation to focus on content words.

## Deviations from Plan

None - plan executed exactly as written.

## Issues Encountered

None.

## User Setup Required

None - no external service configuration required.

## Next Phase Readiness

- Vocabulary module ready for Phase 12 (Constrained Generation) to validate generated text
- VocabularyValidator.validate_text() returns coverage_percentage and non_noc_words for constraint enforcement
- Module-level vocab_index in app.py available for import by other modules

---
*Phase: 09-vocabulary-foundation*
*Completed: 2026-02-03*
