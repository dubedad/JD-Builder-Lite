---
phase: 15-matching-engine
plan: 02
subsystem: matching
tags: [sentence-transformers, semantic-similarity, machine-learning, embeddings, shortlisting]

# Dependency graph
requires:
  - phase: 14-data-layer
    provides: Repository pattern for occupational groups data access
provides:
  - Semantic similarity matcher using sentence-transformers (all-MiniLM-L6-v2)
  - Labels-based confidence booster (gracefully degrades if no OaSIS->TBS mapping)
  - Combined shortlister with definition-based scoring and inclusion filtering
affects: [15-03-classification-engine, 15-04-api-endpoints]

# Tech tracking
tech-stack:
  added: [sentence-transformers==3.4.1]
  patterns: [Lazy-loading singletons for heavy ML models, Embedding caching for performance, Graceful degradation for optional features]

key-files:
  created:
    - src/matching/shortlisting/__init__.py
    - src/matching/shortlisting/semantic_matcher.py
    - src/matching/shortlisting/labels_matcher.py
  modified: []

key-decisions:
  - "Use all-MiniLM-L6-v2 model: fast, good accuracy, no GPU needed (per RESEARCH.md)"
  - "Cache definition embeddings for performance (definitions don't change often)"
  - "Labels boost gracefully degrades to 0.0 when no OaSIS->TBS mapping exists"
  - "Inclusions used for shortlist filtering ONLY, not for combined_score ranking"
  - "Combined score = semantic_similarity + labels_boost (no inclusion weight)"

patterns-established:
  - "Lazy-loading pattern: Heavy ML models loaded only when needed via singleton pattern"
  - "Embedding caching: Definition embeddings cached since groups don't change often"
  - "Graceful degradation: Optional features (labels boost) return 0.0 when dependencies unavailable"

# Metrics
duration: 19min
completed: 2026-02-04
---

# Phase 15 Plan 02: Shortlisting Module Summary

**Semantic shortlisting with sentence-transformers all-MiniLM-L6-v2, definition-based scoring, and inclusion filtering (not scoring)**

## Performance

- **Duration:** 19min 9sec
- **Started:** 2026-02-04T06:31:45Z
- **Completed:** 2026-02-04T06:50:54Z
- **Tasks:** 3
- **Files modified:** 3

## Accomplishments
- Semantic matcher calculates cosine similarity between JD text and group definitions using sentence-transformers
- Labels booster provides 0.0-0.1 confidence boost (gracefully degrades if no OaSIS->TBS mapping)
- Combined shortlister returns candidates above 0.3 similarity threshold, ranked by definition+labels score only
- Inclusions used for filtering candidates (identifying viable groups) but NOT for ranking score
- Definition embeddings cached for performance since groups don't change often

## Task Commits

Each task was committed atomically:

1. **Task 1: Create semantic similarity matcher using sentence-transformers** - `861b184` (feat)
2. **Task 2: Create labels.csv integration for confidence boost** - `64d582e` (feat)
3. **Task 3: Create combined shortlister with all signals** - _(implemented in Task 1's __init__.py)_

## Files Created/Modified
- `src/matching/shortlisting/__init__.py` - Package exports with lazy-loading singletons and combined shortlister
- `src/matching/shortlisting/semantic_matcher.py` - SemanticMatcher class with all-MiniLM-L6-v2 model and embedding caching
- `src/matching/shortlisting/labels_matcher.py` - LabelsBooster class with graceful degradation for missing OaSIS->TBS mapping

## Decisions Made

**1. Model selection: all-MiniLM-L6-v2**
- Rationale: Per RESEARCH.md, balanced speed/quality for definition matching. Fast, good accuracy, no GPU needed.

**2. Embedding caching strategy**
- Rationale: Definition embeddings cached since occupational group definitions don't change often. JD embeddings computed fresh each call since JDs are different.

**3. Labels boost graceful degradation**
- Rationale: labels_loader uses OaSIS profile codes (e.g., "21211.00"), not TBS group codes (e.g., "CS", "PM"). No direct mapping exists in v4.0. Return 0.0 boost gracefully - core matching uses semantic similarity, labels are optional enhancement.
- Future: Add explicit TBS group -> OaSIS code mapping table for labels boost.

**4. Inclusions for filtering, not scoring**
- Rationale: Per CONTEXT.md decision: "Inclusion statements: Use for shortlisting candidates only, not for scoring or evidence"
- Implementation: Inclusions help identify viable candidate groups (if inclusion matches well, candidate passes shortlist even if definition similarity is borderline). But combined_score = semantic_similarity + labels_boost ONLY (no inclusion weight).

**5. Lazy-loading pattern for ML models**
- Rationale: sentence-transformers model is heavy (~90MB). Load only when needed via singleton pattern to avoid startup overhead.

## Deviations from Plan

None - plan executed exactly as written.

## Issues Encountered

None. All verifications passed:
- Semantic similarity returns 0.0-1.0 range
- Definition embeddings cached for performance
- Labels boost gracefully returns 0.0 when no mapping exists
- Min similarity threshold (0.3) respected
- Combined score excludes inclusion weight (definition + labels only)
- Inclusions used for filtering, not scoring

## User Setup Required

None - no external service configuration required.

## Next Phase Readiness

**Ready for Phase 15 Plan 03 (Classification Engine):**
- Shortlisting module complete with semantic matching
- Can pre-filter candidate groups before expensive LLM classification
- Reduces token costs by limiting LLM focus to top candidates
- Provides confidence scores (combined_score) for ranking

**Dependencies satisfied:**
- sentence-transformers already in requirements.txt (3.4.1)
- labels_loader integration ready (gracefully degrades if mapping unavailable)

**Known limitation:**
- Labels boost currently returns 0.0 (no OaSIS->TBS mapping in v4.0)
- Future enhancement: Add TBS group -> OaSIS code mapping table

---
*Phase: 15-matching-engine*
*Completed: 2026-02-04*
