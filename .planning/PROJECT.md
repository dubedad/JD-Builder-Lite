# JD Builder — DND Civilian Careers Site

## What This Is

A public-facing careers discovery website for DND's civilian workforce, modelled on the Canadian Armed Forces careers site (forces.ca/en/careers/). Job seekers can browse civilian Public Service job families, view job titles within each family, and read detailed career profiles covering overview, training, entry paths, flexible work options, and related CAF military careers. The site is powered by the TBS Job Architecture table (1,989 job titles, 210 job families, 23 job functions) with all content AI-enriched via Claude Haiku.

## Core Value

A job seeker can land on the site, find a civilian DND career that fits them, and understand what the job is and how to enter it — without needing to navigate GC Jobs or call an HR advisor.

## Current State (v1.0 Shipped — 2026-03-18)

- **Stack:** FastAPI + Jinja2, SQLite (careers.sqlite), Anthropic API (Claude Haiku)
- **Codebase:** ~1,782 LOC (Python + HTML), `ps_careers_site/`
- **Data:** 1,989 job titles, 210 families, 23 functions; all titles LLM-enriched; 433 titles have CAF bridge links
- **Pipeline:** `pipeline/ingest.py` → `pipeline/enrich.py` → `pipeline/bridge.py` → `careers.sqlite`
- **App:** `main.py` (FastAPI) + `templates/` (base.html, careers.html, family.html, career_detail.html)
- **Known debt:** DB_PATH divergence (main.py reads from `pipeline/careers.sqlite`; pipeline writes to root `careers.sqlite`). Fix before next pipeline re-run.

## Requirements

### Validated

- ✓ TBS xlsx ingested into careers.sqlite (1,989 rows, 210 families, 0 slug collisions) — v1.0
- ✓ URL-safe slug generated for each job title and job family — v1.0
- ✓ LLM enrichment populates overview, training, entry_plans, part_time for all 1,989 titles — v1.0
- ✓ content_status = 'draft' and enriched_at set on all enriched rows — v1.0
- ✓ CAF pipeline run; bridge_caf_ja parquet populated (88 occupations, 880 mappings) — v1.0
- ✓ bridge.py reads bridge_caf_ja and populates caf_related on 433 matching titles — v1.0
- ✓ FastAPI app starts and serves pages on configurable port — v1.0
- ✓ Static assets (12 card images, GC Canada Logo, hero image) served from /static/ — v1.0
- ✓ GC FIP header on all pages (Canada wordmark, nav links, Exo 2 font) — v1.0
- ✓ Footer on all pages (5-column link grid, Canada wordmark, social icons) — v1.0
- ✓ L1 card grid at /careers — 12 family cards, 4-col/3-col/1-col responsive — v1.0
- ✓ Cards show family name, background image, "VIEW CAREERS" button (Exo 2, gradient overlay) — v1.0
- ✓ Clicking a card navigates to /careers/{family-slug} — v1.0
- ✓ Job Function dropdown (22 values) filters card grid client-side — v1.0
- ✓ Keyword search bar filters cards by family name or title keyword, real-time — v1.0
- ✓ L2 page at /careers/{family-slug} lists all job titles in that family — v1.0
- ✓ Each listing shows job title, NOC badge, managerial level, digital flag, 150-char excerpt — v1.0
- ✓ Clicking a job title navigates to /career/{title-slug} — v1.0
- ✓ L2 shows family name heading and breadcrumb: Home > Careers > [Family] — v1.0
- ✓ L3 page at /career/{title-slug} shows job title, NOC, family, managerial level — v1.0
- ✓ Sticky 5-tab nav: Overview, Training, Entry Plans, Part-Time Options, Related Careers — v1.0
- ✓ Overview tab renders LLM overview content — v1.0
- ✓ Training tab renders LLM training content — v1.0
- ✓ Entry Plans tab renders LLM entry_plans content — v1.0
- ✓ Part-Time Options tab renders LLM part_time content — v1.0
- ✓ Related Careers tab shows CAF bridge links (forces.ca) where available — v1.0
- ✓ Discover/Prepare/Apply action buttons on L3 — v1.0
- ✓ L3 breadcrumb: Home > Careers > [Family] > [Job Title] — v1.0

### Active

- [ ] Fix DB_PATH divergence (main.py reads pipeline/careers.sqlite; pipeline writes root careers.sqlite)
- [ ] Fix blank Job Function dropdown option (1 row with empty job_function)
- [ ] Remove or implement non-functional footer quick-links (/careers?function=...)
- [ ] Bilingual support (EN/FR toggle, French job titles, /fr/carrieres routing)
- [ ] Managerial Level and Digital flag filters on L1
- [ ] Full-text search across LLM-generated content
- [ ] WCAG 2.1 AA formal audit
- [ ] Human content review workflow (draft → reviewed → published status)

### Out of Scope

| Feature | Reason |
|---------|--------|
| JD Builder (Surface B) | Separate app, separate milestone |
| User authentication | Public read-only site, no login needed |
| React / SPA frontend | Spec calls for FastAPI + Jinja2 |
| Protected B data | Only open occupational data (NOC, TBS Job Architecture) |
| Full bilingual v1 | TBS table has French fields but full bilingual deferred to v2 |

## Context

- **Spec:** `ps_careers_site/DND-Civilian-Careers-SPEC.md` — product spec with schema, CSS values, image assets
- **CAF reference:** `ps_careers_site/CAF-CAREERS-SITE-REFERENCE.md` — exact DevTools measurements from forces.ca
- **Data source:** `ps_careers_site/Job_Architecture_TBS.xlsx` — 1,989 job titles, 210 families, 23 functions
- **Related project:** `jobforge/` (JobForge 2.0) — provides bridge_caf_ja.parquet (CAF↔TBS mappings)
- **App location:** `ps_careers_site/` within this repo
- **v1.0 milestone:** Shipped 2026-03-18. Archive: `.planning/milestones/v1.0-ROADMAP.md`

## Constraints

- **Stack:** FastAPI + Jinja2 (server-rendered HTML) — no React, no SPA
- **Data:** No Protected B data — only open TBS Job Architecture data
- **Compliance:** LLM-generated content must be flagged `content_status: draft` until human-reviewed (DADM)
- **Design:** Must visually match forces.ca — exact CSS values documented in CAF reference
- **Dependencies:** Anthropic API key required for LLM enrichment re-runs

## Key Decisions

| Decision | Rationale | Outcome |
|----------|-----------|---------|
| FastAPI + Jinja2, not React | Spec decision; server-rendered matches CAF's own approach | ✓ Good — simpler ops, fast to build |
| Standalone SQLite, not runtime JobForge calls | Simpler ops; pipeline runs once, site reads local DB | ✓ Good — fast queries, no dependency at runtime |
| L2 as separate URL (`/careers/{family-slug}`) | Better UX for linking/sharing | ✓ Good — clean navigation hierarchy |
| Job Function as L1 filter, not L0 page | 22 functions as filter on 209-family grid; no extra page layer | ✓ Good — avoids dead-end pages |
| CARD_IMAGE_STATIC dict in route handler | Explicit mapping prevents normalization edge cases | ✓ Good — prevents subtle 404 bugs |
| data-titles attribute over `/api/families` endpoint | Simpler for v1, no extra HTTP round-trip | ✓ Good for v1 — revisit if title count grows |
| Confidence threshold ≥ 0.70 for CAF bridge | Drops 54 low-confidence mappings from 880 total | ✓ Good — avoids false CAF career links |
| Claude Haiku for LLM enrichment | Cost-effective at ~2,000 calls, sufficient quality | ✓ Good — 0 empty rows, quality acceptable |

---
*Last updated: 2026-03-18 after v1.0 milestone*
