# STATE.md — JD Builder

## Project Reference

See: .planning/PROJECT.md (updated 2026-03-15)

**Core value:** A job seeker can find a DND civilian career, understand it, and know how to enter it — without HR help.
**Current focus:** Defining requirements

## Current Position

Phase: Not started (defining requirements)
Plan: —
Status: Defining requirements
Last activity: 2026-03-15 — Milestone v1.0 started

## Accumulated Context

- Static prototype exists: `ps_careers_site/DND-Civilian-Careers-GC.html` (referenced in spec, not yet extracted)
- 12 card background images already in `ps_careers_site/` — ready to serve as static assets
- JobForge 2.0 gold layer has `job_architecture.parquet` at `jobforge/reference/` — can seed the pipeline
- TBS xlsx is at `ps_careers_site/Job_Architecture_TBS.xlsx` (1,989 rows)
- CAF reference doc has exact CSS pixel values — use these, don't guess
- Anthropic API key needed for enrichment; assume available in environment
