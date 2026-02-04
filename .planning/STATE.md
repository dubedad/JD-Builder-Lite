# Project State

## Project Reference

See: .planning/PROJECT.md (updated 2026-02-04)

**Core value:** Classification Step 1 — Match job descriptions to occupational groups using the prescribed TBS allocation method with full policy provenance.
**Current focus:** v4.0 Occupational Group Allocation - Phase 14 COMPLETE

## Current Position

Milestone: v4.0 Occupational Group Allocation
Phase: 15 of 17 (Matching Engine)
Plan: 3 of 5 complete
Status: In progress - Confidence scoring and evidence linking complete
Last activity: 2026-02-04 - Completed 15-03-PLAN.md (Confidence scoring and evidence linking)

Progress: [###        ] 50% (6/12 plans in v4.0)

## Milestone History

| Milestone | Status | Shipped |
|-----------|--------|---------|
| v1.0 MVP | SHIPPED | 2026-01-22 |
| v1.1 Enhanced Data Display + Export | SHIPPED | 2026-01-23 |
| v2.0 UI Redesign | SHIPPED | 2026-01-25 |
| v2.1 OaSIS Provenance | SHIPPED | 2026-02-02 |
| v3.0 Style-Enhanced Writing | SHIPPED | 2026-02-03 |
| v4.0 Occupational Group Allocation | IN PROGRESS | - |

## Performance Metrics

**Velocity:**
- Total plans completed: 17 (v3.0 + v4.0)
- Average duration: 8.4min
- Total execution time: ~3h 46min

**By Phase (v3.0):**

| Phase | Plans | Total | Avg/Plan |
|-------|-------|-------|----------|
| 09-vocabulary-foundation | 1 | 10min | 10min |
| 10-style-analysis-pipeline | 2 | 9min | 4.5min |
| 11-provenance-architecture | 2 | 4.5min | 2.25min |
| 12-constrained-generation | 3 | ~2h | ~40min |
| 13-export-enhancement | 3 | 15min | 5min |

*Updated after each plan completion*

**By Phase (v4.0):**

| Phase | Plans | Total | Avg/Plan |
|-------|-------|-------|----------|
| 14-data-layer | 3/3 | 26min | 8.7min |
| 15-matching-engine | 3/5 | 27min | 9min |

## Accumulated Context

### Decisions

Decisions are logged in PROJECT.md Key Decisions table.
Recent decisions affecting current work:

- [v4.0 Scope]: Classification Step 1 only — job evaluation standards scoring deferred to v5.0
- [v4.0 Data]: Scrape TBS occupational groups table + linked definition pages
- [v4.0 Matching]: Holistic definition matching, not keyword matching
- [v4.0 Provenance]: Traceable to TBS Classification Policy AND DADM
- [14-01]: Append-only temporal design with effective_from/effective_to for all tables
- [14-01]: WAL journal mode for concurrent reads, FK enforcement via pragma
- [14-02]: Rate limit 1 req/sec via time.sleep, retry on 429/5xx with exponential backoff
- [14-02]: Archive filenames use URL slug, timestamp, and hash prefix for provenance
- [14-02]: TBS HTML uses section elements; parsers handle nested structure
- [14-03]: Validation accepts alphanumeric codes (OM2, PR2, SRC, etc.)
- [14-03]: Groups with empty definitions skipped with warning (PM/MCO)
- [14-03]: Definition-centric merge (definitions have content, table has URLs)
- [15-01]: Models use simple types for OpenAI structured output compatibility
- [15-01]: Repository loads statements eagerly (single query pattern)
- [15-01]: Confidence breakdown exposed as dict for transparency
- [15-03]: NO inclusion weight in confidence scoring (inclusions for shortlisting only per CONTEXT.md)
- [15-03]: Exclusion conflict applies 0.3 multiplier penalty
- [15-03]: Borderline detection at 10% margin between top scores
- [15-03]: Evidence extraction uses difflib SequenceMatcher for fuzzy matching
- [15-03]: Provenance returns archive_path for audit verification

### Pending Todos

None yet.

### Blockers/Concerns

None yet.

## Session Continuity

Last session: 2026-02-04
Stopped at: Completed 15-03-PLAN.md
Resume file: None
Next: Continue Phase 15 (15-04: LLM integration, 15-05: Allocator assembly)

---
*Last updated: 2026-02-04 - 15-03 complete*
