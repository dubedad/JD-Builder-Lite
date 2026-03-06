# Project State

## Project Reference

See: .planning/PROJECT.md (updated 2026-03-06)

**Core value:** Compliance-focused job description builder demonstrating TBS Directive 32592 compliance with full provenance tracking.
**Current focus:** v5.0 JobForge 2.0 Integration — defining requirements

## Current Position

Milestone: v5.0 JobForge 2.0 Integration
Phase: Not started (defining requirements)
Plan: —
Status: Defining requirements
Last activity: 2026-03-06 — Milestone v5.0 started

## Milestone History

| Milestone | Status | Shipped |
|-----------|--------|---------|
| v1.0 MVP | SHIPPED | 2026-01-22 |
| v1.1 Enhanced Data Display + Export | SHIPPED | 2026-01-23 |
| v2.0 UI Redesign | SHIPPED | 2026-01-25 |
| v3.0 Style-Enhanced Writing | SHIPPED | 2026-02-03 |
| v4.0 Occupational Group Allocation | SHIPPED | 2026-02-04 |
| v4.1 Polish | SHIPPED | 2026-02-07 (Phases 18-19; Phase 20 deferred indefinitely) |

## Accumulated Context

### Decisions

| Decision | Phase | Rationale |
|----------|-------|-----------|
| TF-IDF fallback for semantic matching | Compat fix 2026-03-05 | torch has no Python 3.14 wheels; TF-IDF keeps classifier functional with reduced accuracy. See .planning/accuracy-notes/tfidf-fallback-2025-03-05.md |
| Defer Phase 20 (evidence highlighting) | v4.1 | LLM returns paraphrased analysis, not verbatim quotes; proper fix requires allocator prompt changes or v6+ PuMP grid |
| JobForge-first exploration before integration | v5.0 | JobForge gold parquet contents are unknown; build phase 1 to inventory before committing to replacement scope |
| OASIS kept as fallback | v5.0 | JobForge may not have complete coverage for all profiles; fallback ensures nothing breaks |

### Blockers/Concerns

- JobForge 2.0 gold parquet actual contents unknown — Phase 21 (data exploration) resolves this
- TF-IDF semantic matching fallback active (sentence-transformers incompatible with Python 3.14) — accuracy impact documented in .planning/accuracy-notes/tfidf-fallback-2025-03-05.md

---
*Last updated: 2026-03-06 — Milestone v5.0 JobForge 2.0 Integration started*
