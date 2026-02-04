# Phase 16: API Layer - Context

**Gathered:** 2026-02-04
**Status:** Ready for planning

<domain>
## Phase Boundary

POST /api/allocate endpoint that accepts a complete JD and returns ranked occupational group recommendations with confidence scores, rationale, and provenance chains. The endpoint exposes the OccupationalGroupAllocator from Phase 15 to the UI layer.

</domain>

<decisions>
## Implementation Decisions

### Request format
- Accept full JD object including Client-Service Results, Key Activities, labels, and all fields
- Require complete JDs only — Client-Service Results and Key Activities must be filled in
- Single JD per request — no batch support
- No authentication required (internal endpoint, UI and API are same app)

### Response structure
- Return ranked list of top-3 recommendations as array ordered by confidence
- Each recommendation includes: group_code, group_name, confidence (0.0-1.0), rationale
- Full detailed rationale always included (not summary) with all evidence inline
- Provenance links embedded in each recommendation (not separate section)
- Evidence references use both field references (e.g., "Key Activity 3") AND character offsets within that field for precise UI highlighting

### Error responses
- "Needs Work Description Clarification" returns HTTP 200 with status flag + explanation of what's unclear
- "Invalid Combination of Work" returns HTTP 200 with status flag + explanation of why work spans multiple incompatible groups
- Both use consistent pattern: successful response with status flag indicating the issue

### Claude's Discretion
- Whether to include partial recommendations when clarification/invalid status returned
- HTTP status codes for validation errors (400 vs 422)
- Synchronous vs streaming response (based on expected latency)
- REST conventions vs existing app patterns (align with codebase)

### Integration points
- Trigger via explicit "Allocate" button AND auto-suggest when JD reaches complete state
- Cache results with invalidation when JD changes

</decisions>

<specifics>
## Specific Ideas

- Edge case responses (clarification needed, invalid combination) should feel helpful, not like errors
- Evidence highlighting should make it obvious which parts of the JD drove the recommendation

</specifics>

<deferred>
## Deferred Ideas

None — discussion stayed within phase scope

</deferred>

---

*Phase: 16-api-layer*
*Context gathered: 2026-02-04*
