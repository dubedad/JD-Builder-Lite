---
phase: 05-data-enrichment-pipeline
plan: 03
subsystem: data-enrichment
tags: [pydantic, csv-lookup, llm-imputation, openai, work-context-classification]

# Dependency graph
requires:
  - phase: 05-01
    provides: CSV loader with O(1) lookups and scale meanings
  - phase: 05-02
    provides: Enhanced parser with proficiency levels
provides:
  - Enrichment service combining CSV lookups with parsed data
  - EnrichedNOCStatement model with full metadata
  - Work Context classification (responsibilities/effort/other)
  - LLM imputation fallback for missing descriptions
affects: [06-enhanced-ui-display, 07-export-extensions, api-integration]

# Tech tracking
tech-stack:
  added: [openai (optional)]
  patterns: [enrichment-service-singleton, llm-fallback-with-graceful-degradation, classification-with-reasoning]

key-files:
  created:
    - src/services/enrichment_service.py
  modified:
    - src/models/noc.py

key-decisions:
  - "LLM imputation is optional with graceful degradation (no crash if OpenAI not installed)"
  - "Confidence tracking distinguishes CSV data (1.0) from LLM-imputed data (0.7)"
  - "Work Context classification uses pattern matching with conflict resolution (responsibilities wins)"
  - "Classification reason tracked for transparency"
  - "Level 0 statements filtered during enrichment, not parsing"
  - "Sorting by proficiency (highest first) with alphabetical tiebreaker"

patterns-established:
  - "EnrichmentService as module-level singleton for zero-latency enrichment"
  - "Try/except ImportError pattern for optional OpenAI dependency"
  - "LLM imputation caching to avoid redundant API calls"
  - "EnrichmentSource enum to track data provenance"

# Metrics
duration: 34min
completed: 2026-01-23
---

# Phase 5 Plan 3: Statement Enrichment Service Summary

**Enrichment service combining CSV lookups with LLM imputation fallback, Work Context classification with pattern matching, and proficiency-based filtering/sorting**

## Performance

- **Duration:** 34 min
- **Started:** 2026-01-23T02:19:43Z
- **Completed:** 2026-01-23T02:54:44Z
- **Tasks:** 3
- **Files modified:** 2

## Accomplishments
- EnrichedNOCStatement model with full enrichment metadata (description, proficiency, classification)
- Statement enrichment adds descriptions from guide_csv with LLM imputation fallback
- Proficiency levels include scale meanings (level, max, label, dimension)
- Work Context classification into responsibilities/effort/other_work_context with reasoning
- Level 0 statement filtering and proficiency-based sorting (highest first)
- Graceful degradation when OpenAI not installed or not configured

## Task Commits

Each task was committed atomically:

1. **Task 1: Add enrichment models to noc.py** - `5f03a24` (feat)
2. **Task 2: Create enrichment_service.py** - `ce5fce0` (feat)
3. **Task 3: Add LLM imputation fallback** - `789fb4b` (feat)

## Files Created/Modified
- `src/models/noc.py` - Added EnrichmentSource enum, ProficiencyLevel model, EnrichedNOCStatement model with enrichment fields
- `src/services/enrichment_service.py` - Enrichment service with CSV lookups, LLM imputation, Work Context classification, filtering, and sorting

## Decisions Made

**1. LLM imputation is optional with graceful degradation**
- Rationale: Not all users will have OpenAI configured, service must work without it
- Implementation: Try/except ImportError, check OPENAI_API_KEY env var, catch API failures
- Result: Service works in three modes: CSV-only, CSV+LLM, CSV+LLM with cache

**2. Confidence tracking distinguishes data sources**
- Rationale: LLM-generated descriptions are lower confidence than official CSV data
- Implementation: confidence=1.0 for CSV, confidence=0.7 for LLM-imputed
- Result: API responses can indicate data provenance and confidence

**3. Work Context classification uses pattern matching**
- Rationale: Responsibilities and Effort need to be separated for JD structure
- Patterns: responsibilities=['responsib', 'decision'], effort=['effort']
- Conflict resolution: responsibilities wins if item matches both patterns
- Result: Three categories with classification_reason for transparency

**4. Level 0 filtering during enrichment, not parsing**
- Rationale: Parser includes all data, enrichment service applies business rules
- Implementation: enrich_statements and enrich_work_context filter level=0 items
- Result: Clean separation of concerns (parsing vs business logic)

**5. Proficiency-based sorting with alphabetical tiebreaker**
- Rationale: Most important statements (highest proficiency) appear first
- Implementation: Sort by -proficiency.level (descending), then text.lower() (ascending)
- Result: Consistent ordering for user experience

## Deviations from Plan

None - plan executed exactly as written.

## Issues Encountered

None - all tasks completed as planned.

## User Setup Required

**Optional: LLM imputation for missing descriptions**

If you want the enrichment service to use OpenAI to generate descriptions for OASIS attributes not found in guide.csv:

1. Install OpenAI Python library:
   ```bash
   pip install openai
   ```

2. Set environment variable:
   ```bash
   export OPENAI_API_KEY=sk-...your-key-here...
   ```

3. Verify LLM imputation is enabled:
   ```python
   from src.services.enrichment_service import enrichment_service
   print(enrichment_service._llm_enabled)  # Should print True
   ```

**If you skip this setup:** Enrichment service will work normally, but missing descriptions will remain None instead of being imputed.

## Next Phase Readiness

**Ready for Phase 6 (Enhanced UI Display):**
- EnrichedNOCStatement model provides all data needed for frontend rendering
- Proficiency levels include display-ready labels
- Work Context classification ready for section grouping
- Sorting ensures best content appears first

**Ready for API integration:**
- enrichment_service singleton can be imported and called from any route
- Model serialization via Pydantic ensures JSON-safe responses
- Confidence tracking enables conditional rendering (e.g., italicize LLM-imputed data)

**No blockers or concerns.**

---
*Phase: 05-data-enrichment-pipeline*
*Completed: 2026-01-23*
