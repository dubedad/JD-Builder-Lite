---
phase: 16
plan: 02
subsystem: api-layer
tags: [rest-api, provenance, caching, allocation]
depends_on:
  requires: ["16-01", "15-05"]
  provides: ["POST /api/allocate endpoint", "provenance map builder", "allocation cache"]
  affects: ["17-ui"]
tech-stack:
  added: []
  patterns: ["content-based cache invalidation", "flat provenance map structure"]
key-files:
  created:
    - src/matching/provenance_builder.py
  modified:
    - src/routes/api.py
decisions:
  - id: "16-02-cache"
    choice: "In-memory dict cache with SHA256 content hash key"
    rationale: "Simple, no external deps, cache invalidates when JD changes"
metrics:
  duration: "11min"
  completed: "2026-02-04"
---

# Phase 16 Plan 02: API Allocation Endpoint Summary

**One-liner:** POST /api/allocate endpoint with provenance map builder and content-based caching

## What Was Built

### 1. Provenance Map Builder (`src/matching/provenance_builder.py`)

New module that extracts TBS source metadata from AllocationResult:

- `extract_paragraph_labels(text)` - Regex extraction of I1/I2/E1/E2 paragraph references from LLM reasoning
- `build_provenance_map(result)` - Converts AllocationResult to Dict[group_code, ProvenanceDetail]
- `build_confidence_summary(result)` - Quick lookup dict {group_code: confidence}

Structure kept to 2 levels per RESEARCH.md to avoid deep nesting in JSON responses.

### 2. POST /api/allocate Endpoint (`src/routes/api.py`)

Complete allocation endpoint implementing API-01 through API-04:

```
POST /api/allocate
Content-Type: application/json

{
  "position_title": "Policy Analyst",
  "client_service_results": "Provides policy analysis...",
  "key_activities": ["Research", "Brief preparation"],
  "skills": ["Analysis", "Communication"],  // optional
  "labels": ["11201"],  // optional NOC labels
  "minimum_confidence": 0.3  // optional, default 0.3
}
```

Response (HTTP 200 for all cases):
```json
{
  "status": "success | needs_clarification | invalid_combination",
  "recommendations": [...GroupRecommendation],
  "provenance_map": {"CS": ProvenanceDetail, ...},
  "confidence_summary": {"CS": 0.75, ...},
  "primary_purpose_summary": "...",
  "match_context": "dominant match",
  "borderline_flag": false,
  "clarification_needed": null,
  "conflicting_duties": null,
  "warnings": null,
  "constraints_compliance": "..."
}
```

### 3. Allocation Caching

Simple in-memory cache with content-based invalidation:

- `_cache_key(data)` - SHA256 hash of JSON-normalized request
- Cache invalidates automatically when JD content changes
- `clear_allocation_cache()` - Manual invalidation for testing

## Key Integration Points

| Component | Integration |
|-----------|-------------|
| `OccupationalGroupAllocator` | Called to get AllocationResult |
| `OccupationalGroupRepository.get_group_provenance()` | Fetches scrape metadata |
| `AllocationRequest` (16-01) | Validates incoming requests |
| `AllocationResponse` (16-01) | Structures outgoing responses |
| `GroupRecommendation` (15-01) | Passed through in recommendations array |

## Error Handling

| Condition | HTTP Status | Response |
|-----------|-------------|----------|
| Missing request body | 400 | `{"error": "Request body required"}` |
| Pydantic validation error | 400 | `{"error": "Invalid request data", "detail": [...]}` |
| Allocator import error | 503 | `{"error": "Allocation engine not available"}` |
| Internal error | 500 | `{"error": "Allocation failed"}` |
| Edge cases | 200 | Status field indicates condition |

## Deviations from Plan

None - plan executed exactly as written.

## Verification Results

1. POST /api/allocate returns 400 for missing request body - PASS
2. POST /api/allocate returns 400 with field details for validation errors - PASS
3. provenance_builder extracts I1, E2 style labels from reasoning text - PASS
4. Cache key changes when JD content changes - PASS
5. Response structure matches AllocationResponse model - PASS
6. Requirements API-01, API-02, API-03, API-04 addressed - PASS

## Files Changed

| File | Change Type | Lines |
|------|-------------|-------|
| `src/matching/provenance_builder.py` | Created | 96 |
| `src/routes/api.py` | Modified | +164 |

## Commits

| Hash | Message |
|------|---------|
| dbd9cb5 | feat(16-02): create provenance map builder |
| f5f67d2 | feat(16-02): implement POST /api/allocate endpoint |

## Next Phase Readiness

Phase 16 Plan 02 complete. The POST /api/allocate endpoint is ready for UI integration in Phase 17.

**Ready for:**
- UI can call POST /api/allocate with JD data
- Response includes full provenance for display
- Edge cases return 200 with status flag for graceful UI handling
