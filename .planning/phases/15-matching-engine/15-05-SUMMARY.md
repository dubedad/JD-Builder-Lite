---
phase: 15-matching-engine
plan: 05
subsystem: matching-engine
tags: [llm, openai, instructor, pydantic, semantic-search, edge-cases, confidence-scoring]

# Dependency graph
requires:
  - phase: 15-01
    provides: "Data contracts and Pydantic models for structured LLM outputs"
  - phase: 15-02
    provides: "Shortlisting with semantic similarity and labels boost"
  - phase: 15-03
    provides: "Multi-factor confidence scoring without inclusion weight"
  - phase: 15-04
    provides: "LLM classification with structured outputs and fallback"
  - phase: 14-data-layer
    provides: "Database schema and repository for occupational groups"

provides:
  - "OccupationalGroupAllocator orchestrating full allocation pipeline"
  - "allocate_jd() convenience function for single allocation call"
  - "Edge case detection: AP/TC ambiguity, split duties, vague JD, invalid combinations"
  - "Evidence linking with field references and character positions"
  - "Clean public API exports for Phase 16 (API layer)"

affects: [16-api-layer, 17-ui-integration]

# Tech tracking
tech-stack:
  added: []
  patterns:
    - "Pipeline orchestration: load -> shortlist -> classify -> enhance -> link -> check -> filter"
    - "Edge case handling with actionable warnings and guidance"
    - "Empty recommendations allowed for edge cases (no viable candidates)"

key-files:
  created:
    - "src/matching/allocator.py"
    - "src/matching/edge_cases.py"
  modified:
    - "src/matching/__init__.py"
    - "src/matching/models.py"

key-decisions:
  - "NO inclusion weight in final confidence (inclusions for shortlisting only)"
  - "Empty top_recommendations allowed for edge cases where no groups meet threshold"
  - "Edge case detection surfaces issues with actionable guidance, not silent failures"
  - "Evidence linking uses fuzzy matching to handle LLM paraphrasing"

patterns-established:
  - "Edge case handler pattern: detect -> analyze -> guide (not just flag)"
  - "Pipeline orchestration: each component focused, orchestrator integrates"
  - "Graceful degradation: empty results with warnings, not exceptions"

# Metrics
duration: 7min
completed: 2026-02-04
---

# Phase 15 Plan 05: Allocator Assembly Summary

**Main OccupationalGroupAllocator orchestrating full pipeline with edge case detection, multi-factor confidence scoring, and evidence linking**

## Performance

- **Duration:** 7 min
- **Started:** 2026-02-04T07:14:19Z
- **Completed:** 2026-02-04T07:21:11Z
- **Tasks:** 3
- **Files modified:** 4

## Accomplishments

- OccupationalGroupAllocator orchestrates full allocation pipeline (load -> shortlist -> classify -> enhance confidence -> link evidence -> edge cases -> filter)
- Edge case detection for AP/TC ambiguity, split duties, vague JD, invalid combinations, and specialized groups
- Multi-factor confidence WITHOUT inclusion weight (inclusions used for shortlisting only per CONTEXT.md)
- Evidence linking with field references and character positions using fuzzy matching
- Clean public API exports (OccupationalGroupAllocator, allocate_jd, AllocationResult) for Phase 16

## Task Commits

Each task was committed atomically:

1. **Task 1: Create edge case handlers** - `00eee1a` (feat)
2. **Task 2: Create main OccupationalGroupAllocator orchestrator** - `25422a4` (feat)
3. **Task 3: Update package exports** - `e117e73` (feat)

## Files Created/Modified

- `src/matching/edge_cases.py` - Edge case detection and handling with TBS guidance for AP/TC disambiguation, split duties, vague JD, invalid combinations
- `src/matching/allocator.py` - Main allocation orchestrator integrating all components into coherent pipeline
- `src/matching/__init__.py` - Public API exports for Phase 16 (API layer)
- `src/matching/models.py` - Fixed validation to allow empty top_recommendations for edge cases

## Decisions Made

**Edge case handling approach:**
- AP/TC disambiguation uses TBS-based indicators (theoretical vs practical)
- Split duties detected when multiple groups within 15% confidence margin
- Invalid combinations detect fundamentally incompatible work types
- Vague JD detection returns specific clarification questions, not generic errors
- Specialized groups (EX, LC, MD) flagged with separate classification process note

**Empty recommendations handling:**
- Fixed AllocationResult model to allow empty top_recommendations
- Necessary for edge cases: no database groups, no candidates above threshold, database empty
- Returns warnings explaining why no recommendations instead of validation error

**Confidence scoring integration:**
- CRITICAL: NO inclusion weight in final confidence (per CONTEXT.md decision from Plan 15-03)
- Inclusions used ONLY for shortlisting candidates (Plan 15-02)
- Multi-factor confidence: 60% definition fit, 30% semantic similarity, 10% labels boost

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 1 - Bug] Fixed AllocationResult model validation for empty recommendations**
- **Found during:** Task 2 (Testing empty result structure)
- **Issue:** Model validation required at least 1 top_recommendation, but edge cases (no database groups, no candidates above threshold) need empty list support
- **Fix:** Removed minimum length validation, kept maximum 3 entries validation
- **Files modified:** src/matching/models.py
- **Verification:** Empty result creation succeeds, allocator instantiation works
- **Committed in:** 25422a4 (Task 2 commit)

---

**Total deviations:** 1 auto-fixed (1 bug)
**Impact on plan:** Bug fix essential for correct edge case handling. No scope creep.

## Issues Encountered

None - plan executed as specified with one necessary bug fix for edge case support.

## User Setup Required

None - no external service configuration required.

## Next Phase Readiness

**Ready for Phase 16 (API Layer):**
- Clean public API: `from src.matching import OccupationalGroupAllocator, allocate_jd`
- AllocationResult with full provenance, evidence, and confidence breakdown
- Edge cases surfaced with actionable warnings and guidance
- Multi-factor confidence scores calibrated for classification advisor role

**Integration points:**
- allocate_jd(jd_data) -> AllocationResult (single function call)
- JD data format: {position_title, client_service_results, key_activities}
- Result format: {top_recommendations, rejected_groups, borderline_flag, match_context, warnings}

**Known edge cases handled:**
- Empty database (no occupational groups loaded)
- No candidates above similarity threshold
- All candidates below confidence threshold
- AP/TC ambiguity, split duties, vague JD, invalid combinations
- Specialized groups requiring separate classification

**Provenance complete:**
- Each recommendation includes provenance_url to TBS source
- Evidence linked to JD field references with character positions
- Confidence breakdown shows component contributions
- Archive path available via group_id for audit verification

---
*Phase: 15-matching-engine*
*Completed: 2026-02-04*
