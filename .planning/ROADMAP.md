# Roadmap: DND Civilian Careers Site

## Milestones

- ✅ **v1.0 MVP** — Phases 1–8 (shipped 2026-03-18)
- 🔄 **v1.1 Full Browse Experience** — Phases 9–12 (in progress)

## Phases

<details>
<summary>✅ v1.0 MVP (Phases 1–8) — SHIPPED 2026-03-18</summary>

- [x] Phase 1: TBS Ingest (1/1 plans) — completed 2026-03-15
- [x] Phase 2: LLM Enrichment (1/1 plans) — completed 2026-03-15
- [x] Phase 3: CAF Bridge (1/1 plans) — completed 2026-03-16
- [x] Phase 4: App Foundation (2/2 plans) — completed 2026-03-16
- [x] Phase 5: L1 Card Grid (2/2 plans) — completed 2026-03-18
- [x] Phase 6: L1 Interactivity (1/1 plans) — completed 2026-03-17
- [x] Phase 7: L2 Job Family Page (1/1 plans) — completed 2026-03-17
- [x] Phase 8: L3 Job Title Detail (1/1 plans) — completed 2026-03-17

Full details: `.planning/milestones/v1.0-ROADMAP.md`

</details>

### v1.1 Full Browse Experience

- [x] **Phase 9: Data Migration** — Extend DB schema and import all enriched CSV content (completed 2026-03-28)
- [ ] **Phase 10: Image Pipeline** — Fetch ~2,200 Unsplash images for all functions, families, and titles
- [ ] **Phase 11: Navigation Restructure** — 4-level browse hierarchy with image card grids at every level
- [ ] **Phase 12: Enhanced Detail Page** — Add Key Responsibilities, Required Skills, Typical Education sections

## Phase Details

### Phase 9: Data Migration
**Goal**: The database holds all enriched content for functions, families, and titles needed by v1.1
**Depends on**: Nothing (first phase of v1.1; v1.0 DB is the starting point)
**Requirements**: DATA-01, DATA-02, DATA-03, DATA-04, DATA-05, DATA-06
**Success Criteria** (what must be TRUE):
  1. `careers.sqlite` contains a `job_functions` table with 23 rows, each with a slug and description
  2. `careers.sqlite` contains a `job_families` table with 210 rows, each linked to a function via FK
  3. Every row in the `careers` table has non-null `key_responsibilities`, `required_skills`, `typical_education`, and `job_title_description` values sourced from the CSV
  4. Running the migration script a second time produces no duplicates and no errors (idempotent)
**Plans:** 1/1 plans complete
Plans:
- [x] 09-01-PLAN.md — TDD migration script: tests, implementation, production run

### Phase 10: Image Pipeline
**Goal**: Every function, family, and job title has a matched Unsplash image stored locally and referenced in the DB
**Depends on**: Phase 9 (needs `job_functions` and `job_families` tables with slugs; needs `image_path` columns in `careers`)
**Requirements**: IMG-01, IMG-02, IMG-03, IMG-04, IMG-05
**Success Criteria** (what must be TRUE):
  1. Running the pipeline script downloads images into `/static/images/functions/`, `/static/images/families/`, and `/static/images/titles/` without manual intervention
  2. After a full run, `image_path` is populated in the DB for all records that received a successful Unsplash result
  3. Re-running the pipeline skips records that already have a local image file (resumable; no duplicate downloads)
  4. A card for a record with a null `image_path` still renders — it shows a styled gradient fallback, not a broken image
**Plans:** 1/2 plans executed
Plans:
- [ ] 10-01-PLAN.md — TDD rewrite of fetch_images.py: async Unsplash pipeline with concurrency and resume
- [x] 10-02-PLAN.md — Per-function gradient fallback CSS and Unsplash attribution in footer

### Phase 11: Navigation Restructure
**Goal**: A visitor can browse all three taxonomy levels (Function → Family → Title) as image card grids with correct URLs, breadcrumbs, and search
**Depends on**: Phase 9 (data), Phase 10 (images — cards need image_path; fallback allows partial dependency)
**Requirements**: NAV-01, NAV-02, NAV-03, NAV-04, NAV-05, NAV-06, NAV-07
**Success Criteria** (what must be TRUE):
  1. Visiting `/careers` shows 23 Job Function cards in a 4-col → 3-col → 1-col responsive grid using the CAF card CSS (300px height, 3-layer gradient overlay, Exo 2 title, VIEW CAREERS button)
  2. Clicking a Function card navigates to `/careers/{function-slug}` which shows that function's Job Family cards in the same grid format
  3. Clicking a Family card navigates to `/careers/{function-slug}/{family-slug}` which shows that family's Job Title cards in the same grid format
  4. Every browse page shows a hero banner with the current level name and description
  5. Every browse page shows a correct breadcrumb (e.g., Home > Careers > [Function] > [Family])
  6. The keyword search on `/careers` filters the 23 function cards in real time by function name
**Plans**: TBD
**UI hint**: yes

### Phase 12: Enhanced Detail Page
**Goal**: A visitor reading a career detail page can see structured Key Responsibilities, Required Skills, and Typical Education content, and navigate back through the full hierarchy via breadcrumb
**Depends on**: Phase 9 (data columns), Phase 11 (breadcrumb now includes Function level)
**Requirements**: DETAIL-01, DETAIL-02, DETAIL-03, DETAIL-04
**Success Criteria** (what must be TRUE):
  1. The career detail page displays a Key Responsibilities section with content from the DB
  2. The career detail page displays a Required Skills section with content from the DB
  3. The career detail page displays a Typical Education section with content from the DB
  4. The breadcrumb on the detail page reads: Home > Careers > [Function] > [Family] > [Title]
**Plans**: TBD
**UI hint**: yes

## Progress

| Phase | Milestone | Plans Complete | Status | Completed |
|-------|-----------|----------------|--------|-----------|
| 1. TBS Ingest | v1.0 | 1/1 | Complete | 2026-03-15 |
| 2. LLM Enrichment | v1.0 | 1/1 | Complete | 2026-03-15 |
| 3. CAF Bridge | v1.0 | 1/1 | Complete | 2026-03-16 |
| 4. App Foundation | v1.0 | 2/2 | Complete | 2026-03-16 |
| 5. L1 Card Grid | v1.0 | 2/2 | Complete | 2026-03-18 |
| 6. L1 Interactivity | v1.0 | 1/1 | Complete | 2026-03-17 |
| 7. L2 Job Family Page | v1.0 | 1/1 | Complete | 2026-03-17 |
| 8. L3 Job Title Detail | v1.0 | 1/1 | Complete | 2026-03-17 |
| 9. Data Migration | v1.1 | 1/1 | Complete   | 2026-03-28 |
| 10. Image Pipeline | v1.1 | 1/2 | In Progress|  |
| 11. Navigation Restructure | v1.1 | 0/? | Not started | - |
| 12. Enhanced Detail Page | v1.1 | 0/? | Not started | - |
