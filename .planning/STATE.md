# Project State

## Project Reference

See: .planning/PROJECT.md (updated 2026-03-15)

**Core value:** A job seeker can find a DND civilian career, understand it, and know how to enter it — without HR help.
**Current focus:** Phase 1: TBS Ingest

## Current Position

Phase: 1 of 8 (TBS Ingest)
Plan: 0 of TBD in current phase
Status: Ready to plan
Last activity: 2026-03-15 — Roadmap created, all 29 v1 requirements mapped across 8 phases

Progress: [░░░░░░░░░░] 0%

## Performance Metrics

**Velocity:**
- Total plans completed: 0
- Average duration: —
- Total execution time: —

**By Phase:**

| Phase | Plans | Total | Avg/Plan |
|-------|-------|-------|----------|
| - | - | - | - |

*Updated after each plan completion*

## Accumulated Context

### Decisions

Decisions are logged in PROJECT.md Key Decisions table.
Recent decisions affecting current work:

- [Setup]: FastAPI + Jinja2, not React — server-rendered matches CAF's own approach
- [Setup]: Standalone SQLite, not runtime JobForge calls — simpler ops; pipeline runs once
- [Setup]: L2 as separate URL (/careers/{family-slug}) — better UX for linking/sharing
- [Setup]: Job Function as L1 filter, not L0 page — 22 functions as filter on 209-family grid

### Pending Todos

None yet.

### Blockers/Concerns

- Phase 2: Anthropic API key required for LLM enrichment — assume available in environment
- Phase 3: CAF bridge writes to JobForge repo (C:\Users\Administrator\projects\jobforge) — confirm schema conventions before planning
- Static prototype exists: ps_careers_site/DND-Civilian-Careers-GC.html — extract CSS values before Phase 4
- CAF reference doc has exact CSS pixel values — use these, don't guess

## Session Continuity

Last session: 2026-03-15
Stopped at: Roadmap created — ready to plan Phase 1
Resume file: None
