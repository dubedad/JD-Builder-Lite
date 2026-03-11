# Project State

## Project Reference

See: .planning/PROJECT.md (updated 2026-03-11)

**Core value:** Every piece of content in the JD can be traced to its authoritative source (JobForge parquet or OASIS), with clear documentation of human decisions and AI involvement.
**Current focus:** v5.1 UI Overhaul — Phase 26: Global Chrome & Search

## Current Position

Milestone: v5.1 UI Overhaul
Phase: 26 of 30 (Global Chrome & Search)
Plan: Not started
Status: Ready to plan
Last activity: 2026-03-11 — v5.1 roadmap created (Phases 26-30, 51 requirements mapped)

Progress: [░░░░░░░░░░] 0% (0/12 plans complete)

## Milestone History

| Milestone | Status | Shipped |
|-----------|--------|---------|
| v1.0 MVP | SHIPPED | 2026-01-22 |
| v1.1 Enhanced Data Display + Export | SHIPPED | 2026-01-23 |
| v2.0 UI Redesign | SHIPPED | 2026-01-25 |
| v3.0 Style-Enhanced Writing | SHIPPED | 2026-02-03 |
| v4.0 Occupational Group Allocation | SHIPPED | 2026-02-04 |
| v4.1 Polish | SHIPPED | 2026-02-07 (Phases 18-19; Phase 20 deferred indefinitely) |
| v5.0 JobForge 2.0 Integration | SHIPPED | 2026-03-10 |

## Accumulated Context

### Design Reference
- Full UI walkthrough + 16 screenshots in `.planning/ui-walkthrough-v5.1/`
- Reference prototype based on v4.0 fork (no source code access — screenshots are authoritative spec)
- Français toggle and View Provenance Graph button: cosmetic/non-functional in v5.1
- Generate backend: keep OpenAI (no Anthropic key), update button label to "Generate with AI"

### Open Blockers/Concerns

- TF-IDF semantic matching fallback active (sentence-transformers incompatible with Python 3.14) — accuracy impact documented in .planning/accuracy-notes/tfidf-fallback-2025-03-05.md
- element_main_duties.parquet ETL gap: 8 rows / 3 profiles — OASIS fallback unconditional for Main Duties

## Session Continuity

Last session: 2026-03-11
Stopped at: v5.1 roadmap created — ready to plan Phase 26
Resume file: None
