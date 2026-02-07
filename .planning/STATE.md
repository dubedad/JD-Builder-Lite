# Project State

## Project Reference

See: .planning/PROJECT.md (updated 2026-02-06)

**Core value:** Compliance-focused job description builder demonstrating TBS Directive 32592 compliance with full provenance tracking.
**Current focus:** v4.1 Polish -- Phase 18 complete, Phase 20 partially done, Phase 19 planning in progress

## Current Position

Milestone: v4.1 Polish
Phase: 19 of 20 (Flow and Export Polish) -- IN PROGRESS
Plan: 1 of 3 complete
Status: Executing Phase 19 plans
Last activity: 2026-02-07 -- Completed 19-01-PLAN.md (Navigation Wiring and Classification Caching)

Progress: ███████████████████░ 95%

## Milestone History

| Milestone | Status | Shipped |
|-----------|--------|---------|
| v1.0 MVP | SHIPPED | 2026-01-22 |
| v1.1 Enhanced Data Display + Export | SHIPPED | 2026-01-23 |
| v2.0 UI Redesign | SHIPPED | 2026-01-25 |
| v3.0 Style-Enhanced Writing | SHIPPED | 2026-02-03 |
| v4.0 Occupational Group Allocation | SHIPPED | 2026-02-04 |

## v4.1 Scope

**19+ requirements across 3 phases:**

| Phase | Focus | Requirements |
|-------|-------|--------------|
| 18 | Profile Page Overhaul | TAB-01..06, DISP-01..03 (9 reqs) |
| 19 | Flow and Export Polish | NAV-01..03, UX-01..04, EXP-01..02, DOC-01 (10 reqs) |
| 20 | Evidence & Provenance Display | EVD-01..05 (carried from v4.0 17-03) |

## Phase 20 Status (Partial)

**Plan 20-01: COMPLETE** -- Provenance tree upgrade (expandable 3-level tree)
**Plan 20-02: DEFERRED** -- Human verification of evidence/provenance

### What was done (20-02 attempt):
- Card sorting by confidence descending (IT 54% now ranks above DA 46%)
- "Highlight in JD" buttons render for all evidence spans (removed start_char null guard)
- Classification Complete section shows when recommendations exist
- Fuzzy text matching upgraded to word-overlap algorithm
- "Not found" indicator made persistent with clearer message

### Why UAT failed:
Evidence highlighting depends on LLM returning exact JD quotes in evidence_spans. Currently the LLM returns paraphrased/analysis text that doesn't match the JD viewer content. Proper fix requires:
1. Allocator prompt changes to enforce verbatim quoting
2. Or: the PuMP comparison grid (v5.0+ SEED S5-11) which replaces text-matching with structured column comparison

### Decision: Execute Phase 19 first, revisit 20-02 after

## Accumulated Context

### Decisions

| Decision | Phase | Rationale |
|----------|-------|-----------|
| Use inline onclick for aria-expanded toggle | 20-01 | Simpler than additional event binding for expandable sections |
| Display scraped_at date in provenance tree | 20-01 | Transparency about data freshness |
| Fallback to group name when definition unavailable | 20-01 | Graceful degradation for missing provenance data |
| Sort recommendation cards client-side by confidence | 20-02 | LLM doesn't guarantee sort order |
| Show complete section on any recommendations | 20-02 | API may return needs_clarification with recommendations present |
| Defer 20-02 UAT to after Phase 19 | 20-02 | Evidence highlighting needs allocator prompt fixes or v5.0+ grid |
| Use sessionStorage flags for navigation intent | 19-01 | Preserves existing localStorage state while controlling screen to show |
| Cache classification results with JD hash | 19-01 | Avoid redundant API calls, detect stale cache when selections change |
| Use CustomEvent for classify-complete | 19-01 | Decouples cache write from classification logic, maintains separation of concerns |
| Show stale warning banner instead of auto-invalidating | 19-01 | Preserves user's classification results while alerting to potential staleness |
| Use coaching panel with blue styling for invalid_combination | 19-02 | Multi-group results are valid outcomes needing guidance, not errors |
| Show duty alignment percentages and key evidence in coaching panel | 19-02 | Users need to understand WHY each group was recommended |
| No duplicate Return to Builder button in coaching panel | 19-02 | Plan 19-01 already provides top-level navigation |

Additional decisions logged in PROJECT.md Key Decisions table.

### Blockers/Concerns

- Evidence_spans from LLM contain paraphrased analysis, not verbatim JD quotes
- "Data Engineer" keyword search returns no OaSIS results (external data issue, not code regression)

## Session Continuity

Last session: 2026-02-07 16:19 UTC
Stopped at: Completed 19-01-PLAN.md (Navigation Wiring and Classification Caching)
Resume file: None

---
*Last updated: 2026-02-07 -- Completed Phase 19 Plan 01 (Navigation Wiring and Classification Caching)*
