---
phase: 15
plan: 01
subsystem: matching-engine
tags: [pydantic, models, repository, data-access, provenance]
requires: [14-01, 14-02, 14-03]
provides:
  - Pydantic output models for LLM structured responses
  - Repository methods for loading groups with inclusions/exclusions
  - Data access layer for matching engine
affects: [15-02, 15-03]
tech-stack:
  added: []
  patterns:
    - Pydantic v2 models with Field constraints for OpenAI structured output
    - Repository pattern with parameterized SQL queries
    - Lazy imports for package initialization
decisions:
  - Models use simple types for OpenAI structured output compatibility (no complex validation logic)
  - Repository loads complete group data (inclusions/exclusions) in single query for efficiency
  - Confidence scores validated at model level (0.0-1.0 range)
  - Provenance tracking includes archive_path for full audit trail
key-files:
  created:
    - src/matching/__init__.py
    - src/matching/models.py
  modified:
    - src/storage/repository.py
metrics:
  duration: 11min
  completed: 2026-02-04
---

# Phase 15 Plan 01: Data Contracts and Access Layer Summary

**One-liner:** Pydantic models for structured LLM allocation output with repository methods loading groups+statements for semantic matching.

## What Was Built

Created the foundational data layer for the matching engine:

1. **Pydantic Output Models** (src/matching/models.py):
   - `AllocationResult`: Complete allocation output with top-3 recommendations, rejected groups, borderline flags
   - `GroupRecommendation`: Single recommendation with confidence breakdown, reasoning chain, evidence spans, provenance
   - `ReasoningStep`: Chain-of-thought reasoning step
   - `EvidenceSpan`: Quoted JD text with field context
   - `RejectedGroup`: Documented elimination rationale

2. **Repository Extensions** (src/storage/repository.py):
   - `get_groups_with_statements()`: Load all groups with inclusions/exclusions in single query
   - `get_group_provenance()`: Full provenance metadata with archive path
   - `get_inclusions_for_group()`: Ordered inclusion statements
   - `get_exclusions_for_group()`: Ordered exclusion statements

3. **Package Structure** (src/matching/__init__.py):
   - Lazy imports pattern matching storage package
   - Clean exports for all models

## Key Features

**Model Design:**
- Simple types for OpenAI structured output compatibility (no complex validators)
- Confidence scores validated 0.0-1.0 with Pydantic Field constraints
- Full provenance tracking (group_id, provenance_url, provenance_paragraph)
- Evidence linking (text spans with field references)
- Reasoning transparency (chain-of-thought steps)
- Match quality indicators (borderline_flag, match_context, duty_split)

**Repository Pattern:**
- Single query loads groups with complete statement lists (efficient)
- Parameterized SQL (? placeholders) prevents injection
- Proper FK joins to scrape_provenance for audit trail
- Ordered statements by order_num preserve TBS structure

## Commits

| Commit | Type | Description |
|--------|------|-------------|
| a13bc1b | feat | Create Pydantic output models for allocation results |
| d5fcfeb | feat | Extend repository with inclusion/exclusion loading |

## Decisions Made

**DECISION: Models use simple types for OpenAI compatibility**
- **Context:** OpenAI structured output has limitations on complex validation
- **Choice:** Keep validation simple (Field constraints only), no complex model_validators
- **Rationale:** Ensures models work with OpenAI function calling
- **Impact:** Validation logic will live in matching engine, not models

**DECISION: Repository loads statements eagerly**
- **Context:** Matching engine needs inclusions/exclusions for every group
- **Choice:** get_groups_with_statements() loads all statements upfront
- **Rationale:** More efficient than N+1 queries, data size manageable (426 groups)
- **Impact:** Single query pattern for semantic matching workflows

**DECISION: Confidence breakdown exposed as dict**
- **Context:** Multiple factors contribute to confidence score
- **Choice:** confidence_breakdown: Dict[str, float] with named components
- **Rationale:** Transparency for expert review, extensible for new factors
- **Impact:** UI can display component scores separately

## Testing Notes

Verification confirmed:
- All models import without error
- GroupRecommendation validates confidence 0.0-1.0 (rejects 1.5)
- Repository loads 426 groups (213 base groups × 2 for subgroups)
- 190 groups have inclusions, 124 have exclusions
- Provenance query returns archive_path and source URL
- Models serialize to JSON (OpenAI structured output compatible)

## Deviations from Plan

None - plan executed exactly as written.

## Dependencies

**Requires:**
- Phase 14-01: SQLite schema with dim_occupational_group, inclusions, exclusions
- Phase 14-02: Scraping infrastructure with provenance tracking
- Phase 14-03: ETL pipeline populating DIM_OCCUPATIONAL tables

**Provides:**
- Data contracts for LLM structured output (AllocationResult)
- Data access methods for matching engine (get_groups_with_statements)
- Foundation for semantic matching (complete group data with statements)

**Affects:**
- Phase 15-02: Will use AllocationResult as return type
- Phase 15-03: Will use get_groups_with_statements() for candidate loading

## Next Phase Readiness

**Ready for 15-02 (Semantic Matching):**
- ✓ Models define expected LLM output structure
- ✓ Repository provides complete group data for comparison
- ✓ Provenance chain ready for rationale generation
- ✓ Evidence structures support JD-to-definition linking

**No blockers identified.**

## Statistics

- Files created: 2
- Files modified: 1
- Lines added: ~320
- Test verifications: 8
- Duration: 11 minutes
- Commits: 2

---

*Completed: 2026-02-04*
*Phase: 15-matching-engine*
*Plan: 01 of 03*
