# JD Builder — DND Civilian Careers Site

## What This Is

A public-facing careers discovery website for DND's civilian workforce, modelled on the Canadian Armed Forces careers site (forces.ca/en/careers/). Employees and job seekers can browse civilian Public Service job families, view job titles within each family, and read detailed career profiles covering overview, training, entry paths, and flexible work options. The site is powered by the TBS Job Architecture table (1,989 job titles, 209 job families, 22 job functions).

## Core Value

A job seeker can land on the site, find a civilian DND career that fits them, and understand what the job is and how to enter it — without needing to navigate GC Jobs or call an HR advisor.

## Current Milestone: v1.0 DND Civilian Careers Site

**Goal:** Build the full careers site — data pipeline + all three page layers — so job seekers can browse, discover, and read about DND civilian careers.

**Target features:**
- Data pipeline: ingest TBS Job Architecture xlsx → SQLite, LLM-enrich all job titles
- L1 Browse page: 12 MVP job family cards (CAF-mirrored design), Job Function filter
- L2 Job Family page: list of all job titles within a family with NOC badge, level, digital flag, excerpt
- L3 Job Title detail page: 5-tab layout (Overview, Training, Entry Plans, Part-Time, Related Careers)
- Search across job titles and content

## Requirements

### Validated

(None yet — ship to validate)

### Active

- [ ] TBS Job Architecture xlsx ingested into careers.sqlite
- [ ] LLM enrichment populates overview, training, entry_plans, part_time for each job title
- [ ] L1 Browse page renders 12 job family cards matching CAF visual design
- [ ] Job Function filter (22 values) narrows the family grid on L1
- [ ] Search bar filters cards by job title / keyword
- [ ] L2 Job Family page lists all titles in a family with NOC badge, managerial level, digital flag, and overview excerpt
- [ ] L3 Job Title detail page renders 5 anchored tabs: Overview, Training, Entry Plans, Part-Time Options, Related Careers
- [ ] Related Careers tab shows related civilian titles and CAF bridge links (where available)
- [ ] GC FIP header and footer render correctly (Exo 2 + Roboto fonts, Canada wordmark)
- [ ] Responsive layout: 4-col → 3-col → 1-col at Bootstrap 4 breakpoints

### Out of Scope

- JD Builder (Surface B — manager portal) — separate app, separate milestone
- Full bilingual (FR) support — TBS table has French fields but full bilingual is post-MVP
- CAF bridge table scraping — bridge data will be mocked; full scrape is a future phase
- WCAG 2.1 AA full audit — accessible markup yes, formal audit post-MVP
- User accounts / authentication — public read-only site

## Context

- **Spec:** `ps_careers_site/DND-Civilian-Careers-SPEC.md` — full product spec with schema, CSS values, image assets
- **CAF reference:** `ps_careers_site/CAF-CAREERS-SITE-REFERENCE.md` — exact DevTools measurements from forces.ca
- **Data source:** `ps_careers_site/Job_Architecture_TBS.xlsx` — 1,989 job titles, 209 families, 22 functions
- **Image assets:** 12 card background images already present in `ps_careers_site/` (webp, jpg, png)
- **Related project:** `jobforge/` (JobForge 2.0) — provides medallion data pipeline; `job_architecture` gold table at `jobforge/reference/job_architecture.parquet`
- **App location:** `ps_careers_site/` within this repo; runs on its own port (not localhost:8000 which is JD Builder)
- **LLM enrichment:** Uses Anthropic API (claude-sonnet-4-6) to generate overview, training, entry_plans, part_time content per job title

## Constraints

- **Stack:** FastAPI + Jinja2 (server-rendered HTML) — no React, no SPA
- **Data:** No Protected B data — only open TBS Job Architecture data
- **Compliance:** LLM-generated content must be flagged `content_status: draft` until human-reviewed (DADM)
- **Design:** Must visually match forces.ca — exact CSS values documented in CAF reference
- **Dependencies:** Anthropic API key required for LLM enrichment phase

## Key Decisions

| Decision | Rationale | Outcome |
|----------|-----------|---------|
| FastAPI + Jinja2, not React | Spec decision; server-rendered matches CAF's own approach | — Pending |
| Standalone SQLite, not runtime JobForge calls | Simpler ops; pipeline runs once, site reads local DB | — Pending |
| L2 as separate URL (`/careers/{family-slug}`) | Better UX for linking/sharing than same-page filter | — Pending |
| Job Function as L1 filter, not L0 page | 22 functions as filter on the 209-family grid; no extra page layer | — Pending |

---
*Last updated: 2026-03-15 — Milestone v1.0 started*
