---
phase: 29-classification-restyle-generate-page
plan: "03"
subsystem: ui
tags: [classify, pydantic, openai-structured-output, vanilla-js, post-analysis, tbs-classification]

# Dependency graph
requires:
  - phase: 29-01
    provides: Post-analysis container IDs in index.html (classify-top-result, classify-alignment, classify-key-evidence, classify-caveats, classify-alternatives, classify-next-step, classify-analyze-btn)
provides:
  - GroupRecommendation model with caveats and og_definition_statements fields (LLM-populated)
  - renderTopResultCard(): confidence bar + TBS link + summary sentence in classify-top-result
  - renderStatementAlignment(): two-column comparison + alignment score (CLASS-02)
  - renderKeyEvidence(): evidence span bullets in classify-evidence-list (CLASS-03)
  - renderCaveats(): warning bullets in classify-caveats-list (CLASS-03)
  - renderAlternatives(): other group recommendations with confidence percentages
  - renderNextStep(): blue-tinted box with Job Evaluation Standard link (CLASS-04)
  - Analyze button wired via classify-requested CustomEvent (no double-fire)
affects:
  - phase 30 (generate/export) — classification result now available with richer model data
  - future LLM prompt tuning — caveats/og_definition_statements prompt added in section 5

# Tech tracking
tech-stack:
  added: []
  patterns:
    - Post-analysis progressive reveal: sections start hidden, revealed by renderResults() after API response
    - CustomEvent delegation for Analyze button: dispatches classify-requested to leverage existing handleClassifyRequest flow
    - Sorted-copy pattern: const sorted = [...response.recommendations].sort() before all post-analysis renderers

key-files:
  created: []
  modified:
    - src/matching/models.py
    - src/matching/prompts.py
    - static/js/classify.js

key-decisions:
  - "Analyze button dispatches classify-requested CustomEvent — reuses handleClassifyRequest, guarantees no double API call"
  - "showLoading() hides classify-cta to prevent re-trigger while analysis runs"
  - "Alignment score computed client-side as evidence_spans.length / key_activities.length (no new API field)"
  - "JOB_EVAL_STANDARDS covers 8 most common groups; all others fall back to general TBS job evaluation URL"

patterns-established:
  - "Post-analysis reset: forEach over section IDs adding hidden class before re-render"
  - "LLM field population: prompt section 5 instructs caveats + og_definition_statements extraction"

# Metrics
duration: 2min
completed: 2026-03-12
---

# Phase 29 Plan 03: Classification Post-Analysis Rendering Summary

**Six v5.1 post-analysis renderers (top result card, alignment comparison, evidence, caveats, alternatives, next step) wired to GroupRecommendation model extended with LLM-populated caveats and og_definition_statements fields**

## Performance

- **Duration:** 2 min
- **Started:** 2026-03-12T21:19:34Z
- **Completed:** 2026-03-12T21:21:39Z
- **Tasks:** 2
- **Files modified:** 3

## Accomplishments
- Backend: GroupRecommendation model gains `caveats: List[str]` and `og_definition_statements: List[str]` with empty list defaults (backward-compatible for cached responses)
- Backend: LLM system prompt updated in section 5 to instruct 2-4 caveats and 3-5 og_definition_statements per recommendation
- Frontend: JOB_EVAL_STANDARDS lookup table for 8 common occupational groups with direct TBS links
- Frontend: All 6 post-analysis rendering functions added to classify.js (renderTopResultCard, renderStatementAlignment, renderKeyEvidence, renderCaveats, renderAlternatives, renderNextStep)
- Frontend: Analyze button (classify-analyze-btn) wired via classify-requested CustomEvent — single dispatch prevents double-fire
- Frontend: renderResults() now calls all v5.1 renderers after renderRecommendationCards()
- Frontend: showLoading() and Analyze button click both hide the CTA div to prevent re-trigger

## Task Commits

Each task was committed atomically:

1. **Task 1: Add caveats and og_definition_statements to GroupRecommendation model** - `56bc70d` (feat)
2. **Task 2: Add post-analysis rendering and Analyze button wiring in classify.js** - `babfa3c` (feat)

## Files Created/Modified
- `src/matching/models.py` - Added `caveats` and `og_definition_statements` fields to GroupRecommendation with default_factory=list
- `src/matching/prompts.py` - Added two bullet instructions in section 5 of system prompt for LLM field population
- `static/js/classify.js` - Added JOB_EVAL_STANDARDS table, 6 new rendering functions, Analyze button handler, renderResults() v5.1 calls, showLoading() CTA hide, reset logic

## Decisions Made
- Analyze button dispatches the same `classify-requested` CustomEvent that main.js uses — reuses `handleClassifyRequest` exactly, zero risk of duplicate API call
- `showLoading()` responsible for hiding the CTA so both Analyze button click and any programmatic trigger cover this case
- Alignment score computed entirely client-side (evidenceCount / activityCount) — no new API field needed, keeps response schema stable
- JOB_EVAL_STANDARDS covers AS, CS, EC, PM, IT, FI, PE, EX; all others fall back to the general TBS job evaluation index page

## Deviations from Plan

None - plan executed exactly as written.

## Issues Encountered
None — all DOM IDs from 29-01 matched expectations, JS and Python syntax checks passed immediately.

## User Setup Required
None - no external service configuration required.

## Next Phase Readiness
- Classification page is feature-complete for v5.1: CLASS-01 through CLASS-04 all implemented
- Phase 29 overall is complete (29-01, 29-02, 29-03 all done)
- Phase 30 (final phase) can proceed — no blockers from this plan
- LLM will begin populating caveats and og_definition_statements on next live classification run

---
*Phase: 29-classification-restyle-generate-page*
*Completed: 2026-03-12*
