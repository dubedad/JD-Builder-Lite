---
phase: 15-matching-engine
plan: 03
subsystem: matching
tags: [confidence-scoring, evidence-extraction, provenance, audit-trail, difflib]

# Dependency graph
requires:
  - phase: 14-data-layer
    provides: OccupationalGroupRepository with provenance tracking
provides:
  - Multi-factor confidence scoring (60% definition fit, 30% semantic, 10% labels, NO inclusion weight)
  - Evidence extraction with field identification and fuzzy matching
  - TBS provenance linking for full audit trail
affects: [15-04-llm-integration, 15-05-allocator-assembly]

# Tech tracking
tech-stack:
  added: []
  patterns:
    - Multi-factor confidence scoring without inclusion weight (per CONTEXT.md)
    - Fuzzy text matching with difflib for evidence extraction
    - Provenance linking to TBS source URLs with archive paths

key-files:
  created:
    - src/matching/confidence.py
    - src/matching/evidence/__init__.py
    - src/matching/evidence/extractor.py
    - src/matching/evidence/provenance.py
  modified: []

key-decisions:
  - "NO inclusion weight in confidence scoring - inclusions for shortlisting only per CONTEXT.md"
  - "Exclusion conflict applies 0.3 multiplier penalty (severe)"
  - "Borderline detection at 10% margin between top scores"
  - "Evidence extraction uses difflib SequenceMatcher for fuzzy matching"
  - "Provenance returns archive_path for audit verification"

patterns-established:
  - "Confidence breakdown transparency: show component contributions"
  - "Evidence spans include field references (not just raw text)"
  - "Graceful degradation: return partial evidence if position mapping fails"

# Metrics
duration: 9min
completed: 2026-02-04
---

# Phase 15 Plan 03: Confidence Scoring and Evidence Linking Summary

**Multi-factor confidence scoring (60/30/10 weighting, NO inclusion) with evidence extraction and TBS provenance for full audit trail**

## Performance

- **Duration:** 9 min
- **Started:** 2026-02-04T01:39:01Z
- **Completed:** 2026-02-04T01:47:46Z
- **Tasks:** 3/3
- **Files modified:** 4 created

## Accomplishments

- Multi-factor confidence calculator with 60% definition fit, 30% semantic similarity, 10% labels boost (NO inclusion weight per CONTEXT.md decision)
- Evidence extractor finds text spans in JD with field identification and fuzzy matching via difflib
- Provenance linker creates TBS audit trail with source URLs, timestamps, content hashes, and archive paths
- Component breakdown for transparency (shows weighted contributions)
- Borderline detection flags when top scores within 10%

## Task Commits

Each task was committed atomically:

1. **Task 1: Create multi-factor confidence calculator** - `7baf9d0` (feat)
   - Multi-factor scoring: 60% definition fit, 30% semantic, 10% labels
   - NO inclusion weight (per CONTEXT.md: inclusions for shortlisting only)
   - Exclusion conflict applies 0.3 multiplier penalty
   - Borderline detection at 10% margin

2. **Task 2: Create evidence extractor for JD text spans** - `a057345` (feat)
   - Exact and fuzzy text matching with difflib SequenceMatcher
   - Field identification (Client-Service Results, Key Activity N)
   - Character position tracking for text spans
   - Graceful handling of LLM paraphrasing

3. **Task 3: Create provenance linker for TBS audit trail** - `95e2ea1` (feat)
   - Links group recommendations to TBS source URLs
   - Returns scraped_at timestamp and archive_path for verification
   - Supports paragraph-level linking (I1, E2, Definition)
   - Uses repository.get_group_provenance() from Phase 14

## Files Created/Modified

- `src/matching/confidence.py` - Multi-factor confidence scoring with component breakdown
- `src/matching/evidence/__init__.py` - Evidence package initialization
- `src/matching/evidence/extractor.py` - Text span extraction with field identification
- `src/matching/evidence/provenance.py` - TBS source provenance linking

## Decisions Made

**Key decision: NO inclusion weight in confidence calculation**

Per CONTEXT.md: "Inclusion statements: Use for shortlisting candidates only, not for scoring or evidence"

This is a critical architectural decision that differs from the RESEARCH.md Pattern 3 example (which showed inclusion as a confidence factor). The user explicitly decided that inclusions help with candidate identification (Plan 15-02) but should NOT boost confidence scores.

**Confidence weighting rationale:**
- 60% definition fit: Primary signal from LLM holistic assessment
- 30% semantic similarity: Independent verification via embeddings
- 10% labels boost: Supporting signal from historical duty mappings
- 0% inclusion: Excluded per user decision

**Other decisions:**
- Exclusion conflict penalty (0.3 multiplier) aligns with CONTEXT.md "hard gate" guidance
- Borderline threshold (10% margin) matches CONTEXT.md requirement for expert review flagging
- Evidence extraction threshold (0.8 similarity) balances accuracy with fuzzy match tolerance
- Provenance includes archive_path to enable audit verification against original HTML

## Deviations from Plan

None - plan executed exactly as written.

The plan explicitly noted "IMPORTANT per CONTEXT.md decision: inclusions are NOT part of confidence calculation" and the implementation correctly excludes inclusion weight from the scoring formula.

## Issues Encountered

None - all implementations worked as expected on first verification.

## User Setup Required

None - no external service configuration required.

## Next Phase Readiness

**Ready for Phase 15-04 (LLM Integration):**
- Confidence calculator available for scoring LLM outputs
- Evidence extractor ready to process LLM reasoning quotes
- Provenance linker ready to attach TBS sources to recommendations

**Ready for Phase 15-05 (Allocator Assembly):**
- All scoring and evidence components in place
- Component breakdown enables transparent explanations
- Borderline detection flags ambiguous cases for review

**Key exports available:**
- `ConfidenceCalculator.calculate_confidence()` - returns (confidence, breakdown)
- `ConfidenceCalculator.check_borderline()` - returns (is_borderline, context)
- `EvidenceExtractor.extract_evidence_spans()` - returns list of span dicts
- `ProvenanceLinker.link_to_tbs_provenance()` - returns provenance dict

**No blockers.** All dependencies from Phase 14 (repository with provenance tracking) are in place.

---
*Phase: 15-matching-engine*
*Completed: 2026-02-04*
