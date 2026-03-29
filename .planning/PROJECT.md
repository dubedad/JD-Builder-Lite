# JD Builder — DND Civilian Careers Site

## What This Is

A public-facing careers discovery website for DND's civilian workforce, structured as a full mirror of the Canadian Armed Forces careers site (forces.ca/en/careers/). The civilian site uses the same format, card dimensions, CSS values, and layouts as the CAF site — only the images and words differ. Job seekers browse through 22 job functions → 209 job families → 1,989 job titles → career detail pages. Powered by the TBS Job Architecture table enriched via `enriched_job_architecture.csv`.

Note: Research docs cited 23 functions/210 families from the xlsx; direct CSV inspection confirmed 22/209 distinct non-blank values.

## Current Milestone: v1.1 — Full Browse Experience

**Goal:** Restructure the site to mirror the CAF careers site format across all 3 taxonomy levels — every level uses the same image card grid. Content differs, format is identical.

**Target features:**
- 4-level navigation: Function → Family → Title → Detail (image cards at every browse level)
- Data migration from `enriched_job_architecture.csv`: function descriptions, family descriptions, title enrichments (Key Responsibilities, Required Skills, Typical Education)
- Image pipeline: ~2,200 images sourced via Unsplash API for all functions, families, and job titles
- Enhanced detail page: Key Responsibilities, Required Skills, Typical Education sections

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

- [x] Fix DB_PATH divergence (main.py reads pipeline/careers.sqlite; pipeline writes root careers.sqlite) — fixed 2026-03-18
- [x] Fix blank Job Function dropdown option — Horticulture Specialist assigned to Environmental Services 2026-03-18
- [x] Remove non-functional footer quick-links (/careers?function=...) — removed 2026-03-18
- [ ] Data quality audit: review job_function assignments across all 1,989 titles for purpose-vs-function misclassification (job_function must reflect work performed, not organizational purpose of the role within DND)
- [ ] Horticulture Specialist missing job_family — orphaned row; does not surface in card grid
- [ ] **v1.1: Navigation restructure** — 4-level hierarchy (Function → Family → Title → Detail); `/careers` shows 23 Function cards; `/careers/{function-slug}` shows Family cards; `/careers/{function-slug}/{family-slug}` shows Title cards; `/career/{title-slug}` is detail
- [x] **v1.1: Data migration** — import `enriched_job_architecture.csv` into new `job_functions` and `job_families` tables; add `key_responsibilities`, `required_skills`, `typical_education`, `job_title_description` columns to `careers` table — Validated in Phase 09: data-migration
- [x] **v1.1: Image pipeline** — async Unsplash pipeline with 5-worker concurrency, resume logic, 22 per-function gradient CSS fallbacks, and attribution footer — Validated in Phase 10: image-pipeline
- [ ] **v1.1: Enhanced detail page** — add Key Responsibilities, Required Skills, Typical Education tabs/sections to L4 career detail
- [ ] **CAF pixel-parity audit** — re-analyze forces.ca live site (L1, L2/filter, L3) in real-time; update CAF-CAREERS-SITE-REFERENCE.md with any deltas; treat every measurable value (spacing, font sizes, card dimensions, gap between images, border radii, colours) as a binding constraint that must persist across both sites
- [ ] **Unified Job Taxonomy** — build a single normalized table combining CAF Careers taxonomy + TBS Job Architecture; requirements:
  - Contains all existing Job Architecture fields (jt_id, job_title, job_family, job_function, noc_2021_uid, managerial_level, digital, etc.)
  - Contains all existing CAF Careers site fields (CAF title, CAF slug, CAF category, CAF description fields, etc.)
  - Job Architecture rows enriched via LLM to fill in CAF-style fields where absent
  - CAF rows enriched via LLM to fill in Job Architecture-style fields where absent
  - Bridge columns capturing CAF↔civilian connections: sourced from "Related Civilian..." fields on CAF site + semantic/ontological mapping pipeline (embeddings + similarity scoring) to match CAF occupations to Job Architecture titles
  - Semantic mapping pipeline likely requires ChromaDB embeddings (already in JobForge 2.0) + Claude scoring pass
  - **Architectural note:** This unified taxonomy is canonical data — belongs in JobForge 2.0, not ps_careers_site; ps_careers_site pipeline reads from it
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

## Product Vision — Manager vs Employee Routing

The careers site is **Step 0** of a two-surface product. On entry, users are asked:
> "Are you a manager or an employee?"

**Employee path:** Browse careers site as a job seeker — current experience, Job Architecture only.

**Manager path — two entry points into JD Builder Step 1:**
1. **Via careers site (Step 0):** Browse Job Architecture card grid → select job title → title passed into JD Builder Step 1. Image-driven UI, Job Architecture universe only.
2. **Via JD Builder direct search:** Open text search spanning MULTIPLE taxonomies — NOC 2021, O*NET, CAF Careers, Job Descriptions, TBS OG. Broader universe, different UX.

Both paths converge at **JD Builder Step 1** with a selected job title. Integration point: passing selected title + source taxonomy metadata from either entry into the JD Builder workflow.

**Critical constraint:** The careers site does NOT cover the full manager search universe. The JD Builder's multi-taxonomy search is NOT replaced by the careers site — it remains essential. The careers site is an additional softer entry point only.

**Required integration work (future milestone):**
- "Manager or employee?" routing gate at careers site entry
- "Use this title / Build JD" CTA on L3 page (manager context only)
- JD Builder must accept a pre-selected job title passed from careers site (with source taxonomy metadata)
- Both entry paths (careers site browse + JD Builder open text search) must coexist in the UX

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
| Job Function as L1 filter, not L0 page | 22 functions as filter on 209-family grid; no extra page layer | Superseded by v1.1 — functions become L1 browse pages |
| CARD_IMAGE_STATIC dict in route handler | Explicit mapping prevents normalization edge cases | ✓ Good — prevents subtle 404 bugs |
| data-titles attribute over `/api/families` endpoint | Simpler for v1, no extra HTTP round-trip | ✓ Good for v1 — revisit if title count grows |
| Confidence threshold ≥ 0.70 for CAF bridge | Drops 54 low-confidence mappings from 880 total | ✓ Good — avoids false CAF career links |
| Claude Haiku for LLM enrichment | Cost-effective at ~2,000 calls, sufficient quality | ✓ Good — 0 empty rows, quality acceptable |
| CAF format parity as design principle | "Whatever CAF shows, civilian site shows the same format" | Established v1.1 — all levels use same card grid CSS as CAF |
| Unsplash API for image pipeline | Free, keyword-searchable, high-quality stock matching existing 12 card images | v1.1 decision — 2,200 images, concurrent/resumable pipeline |

## Evolution

This document evolves at phase transitions and milestone boundaries.

**After each phase transition** (via `/gsd:transition`):
1. Requirements invalidated? → Move to Out of Scope with reason
2. Requirements validated? → Move to Validated with phase reference
3. New requirements emerged? → Add to Active
4. Decisions to log? → Add to Key Decisions
5. "What This Is" still accurate? → Update if drifted

**After each milestone** (via `/gsd:complete-milestone`):
1. Full review of all sections
2. Core Value check — still the right priority?
3. Audit Out of Scope — reasons still valid?
4. Update Context with current state

---
*Last updated: 2026-03-29 — Phase 10 complete: async Unsplash image pipeline (fetch_images.py, 15-test TDD suite), 22 per-function gradient CSS fallback classes, Unsplash attribution in footer*
