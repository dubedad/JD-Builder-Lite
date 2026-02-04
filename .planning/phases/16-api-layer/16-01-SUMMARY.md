---
phase: 16-api-layer
plan: 01
subsystem: api-models
tags: [pydantic, validation, request-response, allocation-api]

dependency_graph:
  requires: [15-matching-engine]
  provides: [api-request-response-models, allocation-endpoint-contract]
  affects: [16-02-endpoint, 17-ui-integration]

tech_stack:
  added: []
  patterns: [pydantic-field-validators, literal-type-unions, model-dump-json]

key_files:
  created:
    - src/models/allocation.py
  modified: []

decisions:
  - id: allocation-status-literals
    choice: "Use Literal type union for status values"
    rationale: "Type-safe at compile time, auto-documented in OpenAPI"
  - id: provenance-flat-structure
    choice: "ProvenanceDetail at 2 levels max nesting"
    rationale: "RESEARCH.md: >3 levels increases parsing errors by 40%"
  - id: validation-in-model
    choice: "field_validator decorators for CSR and key_activities"
    rationale: "Centralizes validation logic, consistent error messages"

metrics:
  duration: 2min
  completed: 2026-02-04
---

# Phase 16 Plan 01: API Allocation Models Summary

**One-liner:** Pydantic request/response models for POST /api/allocate with JD validation and provenance structure

## What Was Built

Created `src/models/allocation.py` with 4 exports defining the API contract for occupational group allocation:

1. **AllocationRequest** - Validates incoming JD data
   - Required: position_title, client_service_results (min 10 chars), key_activities (min 1 non-empty)
   - Optional: skills, labels, minimum_confidence (default 0.3)
   - Field validators ensure substantive content

2. **AllocationResponse** - Structures allocation results
   - Status literal: "success" | "needs_clarification" | "invalid_combination"
   - Top 1-3 GroupRecommendation objects (reuses Phase 15 model)
   - Provenance map keyed by group_code
   - Edge case fields for clarification_needed and conflicting_duties

3. **ProvenanceDetail** - TBS source provenance for each recommendation
   - URL, scraped_at timestamp, data_source_id for audit trail
   - Inclusion/exclusion paragraph labels referenced
   - Optional archive_path for HTML verification

4. **Status constants** - ALLOCATION_STATUS_SUCCESS, ALLOCATION_STATUS_NEEDS_CLARIFICATION, ALLOCATION_STATUS_INVALID_COMBINATION

## Key Implementation Details

**Validation approach:**
- CSR minimum 10 characters (prevents placeholder text)
- Key activities stripped and filtered for non-empty
- Pydantic v2 field_validator decorators for custom validation

**Type safety:**
- AllocationStatus as Literal type union (not string enum)
- Dict types for provenance_map and confidence_summary
- Optional fields with None defaults for edge cases

**Integration:**
- Imports GroupRecommendation from src.matching.models (Phase 15)
- Compatible with model_dump(mode='json') for Flask jsonify()
- Follows existing ErrorResponse pattern from src.models.responses

## Verification Results

| Check | Result |
|-------|--------|
| AllocationRequest validates required fields | PASS |
| AllocationRequest rejects incomplete JDs | PASS |
| AllocationResponse captures all CONTEXT.md fields | PASS |
| ProvenanceDetail nesting depth <= 2 | PASS |
| All models JSON-serializable | PASS |
| Status type is type-safe literal | PASS |
| Phase 15 GroupRecommendation integration | PASS |

## Deviations from Plan

None - plan executed exactly as written.

## Commits

| Hash | Message |
|------|---------|
| b688b37 | feat(16-01): add AllocationRequest model with JD validation |

## Next Phase Readiness

**Immediately usable:**
- AllocationRequest ready for endpoint validation
- AllocationResponse ready for result serialization
- ProvenanceDetail ready for provenance map construction

**Integration notes for 16-02:**
- Endpoint should catch ValidationError and return 400 with e.errors()
- Use model_dump(mode='json') for jsonify() compatibility
- Status field determines edge case handling (not HTTP status code)

---

*Completed: 2026-02-04 | Duration: 2min | Commit: b688b37*
