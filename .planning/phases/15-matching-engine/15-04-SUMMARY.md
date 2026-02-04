---
phase: 15-matching-engine
plan: 04
subsystem: matching-engine
tags: [llm, openai, instructor, pydantic, structured-outputs, classification]

# Dependency graph
requires:
  - phase: 15-01
    provides: AllocationResult and supporting Pydantic models for structured outputs
provides:
  - LLM classifier using instructor library for type-safe structured outputs
  - Prompt templates encoding TBS allocation method with chain-of-thought reasoning
  - Graceful fallback handling for LLM errors
affects: [15-05-allocator, matching-api, classification-ui]

# Tech tracking
tech-stack:
  added: [instructor>=1.0.0]
  patterns: [instructor.from_openai wrapper for structured outputs, temperature=0 for classification, chain-of-thought prompts with evidence extraction]

key-files:
  created: [src/matching/prompts.py, src/matching/classifier.py]
  modified: [requirements.txt]

key-decisions:
  - "Temperature=0 for deterministic classification (no randomness in occupational group matching)"
  - "Fallback creates minimal 0.0-confidence recommendation when LLM fails but candidates exist"
  - "Chain-of-thought prompts explicitly request quoted evidence with quotation marks"
  - "PROMPT_VERSION tracking for provenance and prompt evolution monitoring"

patterns-established:
  - "Prompt structure: system encodes method, user provides JD+candidates, explicit reasoning steps"
  - "Graceful degradation: fallback raises exception only when no valid result possible"
  - "Evidence extraction: prompt instructs for exact quotes to support recommendations"

# Metrics
duration: 13min
completed: 2026-02-04
---

# Phase 15 Plan 04: LLM Classification Summary

**OpenAI structured outputs via instructor library with temperature=0 deterministic classification and TBS allocation method encoded in chain-of-thought prompts**

## Performance

- **Duration:** 13 min
- **Started:** 2026-02-04T06:57:50Z
- **Completed:** 2026-02-04T07:10:37Z
- **Tasks:** 2
- **Files modified:** 3

## Accomplishments
- LLM classifier using instructor library for type-safe Pydantic integration
- System prompt encodes complete TBS allocation method (primary purpose extraction, holistic definition matching, inclusion support, exclusion hard gate)
- Temperature=0 ensures deterministic classification decisions
- Graceful fallback with minimal valid recommendation on LLM errors

## Task Commits

Each task was committed atomically:

1. **Task 1: Add instructor library and create prompt templates** - `718bcb4` (feat)
   - Added instructor>=1.0.0 to requirements.txt
   - Created src/matching/prompts.py with build_system_prompt() and build_user_prompt()
   - System prompt encodes holistic definition matching, chain-of-thought reasoning
   - PROMPT_VERSION="v1.0-allocation" for provenance tracking

2. **Task 2: Create LLM classifier with structured outputs** - `6d0e35b` (feat)
   - Created src/matching/classifier.py with LLMClassifier class
   - instructor.from_openai() wraps OpenAI client for structured outputs
   - response_model=AllocationResult enforces Pydantic validation
   - Verified with real API call (EC recommendation at 0.90 confidence)

3. **Bug fix: Ensure fallback returns valid AllocationResult** - `dc427f6` (fix)
   - Fixed fallback returning empty top_recommendations (violated validator)
   - Now creates minimal recommendation with 0.0 confidence on error
   - Raises exception if no candidates (can't create valid result)

## Files Created/Modified
- `src/matching/prompts.py` - Prompt templates encoding TBS allocation method
- `src/matching/classifier.py` - LLM classifier using instructor for structured outputs
- `requirements.txt` - Added instructor>=1.0.0

## Decisions Made
- **Temperature=0 for deterministic classification:** Classification decisions should be consistent for identical inputs (not creative text generation)
- **PROMPT_VERSION tracking:** Track prompt versions for provenance and monitoring prompt evolution
- **Fallback strategy:** Create minimal 0.0-confidence recommendation when LLM fails but candidates exist; raise exception when no candidates (can't meet AllocationResult schema requirements)
- **Evidence extraction in prompts:** Explicitly instruct LLM to use quotation marks for exact quotes from JD

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 1 - Bug] Fixed fallback violating AllocationResult validator**
- **Found during:** Task 2 verification
- **Issue:** classify_with_fallback() returned empty top_recommendations list, but AllocationResult validator requires at least 1 entry
- **Fix:** Changed fallback to create minimal GroupRecommendation with 0.0 confidence and error details. Raises exception if no candidates available (can't create valid result).
- **Files modified:** src/matching/classifier.py
- **Verification:** Tested both fallback paths (with/without candidates), both work correctly
- **Committed in:** dc427f6

---

**Total deviations:** 1 auto-fixed (1 bug)
**Impact on plan:** Bug fix necessary for correct error handling. No scope creep.

## Issues Encountered
None - all tasks executed as planned after bug fix

## User Setup Required
None - no external service configuration required.

**Note:** OpenAI API key must be set in environment (OPENAI_API_KEY) for LLM classifier to work. Fallback handles missing/invalid keys gracefully.

## Next Phase Readiness
- LLM classifier complete and verified with real API calls
- Ready for allocator assembly (15-05) to integrate shortlisting, confidence scoring, and LLM classification
- Prompt templates encode complete TBS allocation method per CONTEXT.md
- Structured outputs guarantee valid AllocationResult schema

---
*Phase: 15-matching-engine*
*Completed: 2026-02-04*
