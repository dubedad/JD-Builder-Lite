# Roadmap: DND Civilian Careers Site

## Overview

Eight phases take this project from raw spreadsheet to a fully browsable careers site. The data pipeline (phases 1-3) builds and enriches careers.sqlite, including the CAF bridge for related-careers linking. The app foundation (phase 4) stands up the FastAPI server with GC FIP chrome. The three page layers (phases 5-8) deliver the complete visitor experience: browsing job family cards, filtering and searching, exploring a job family, and reading a full career profile with five anchored tabs.

## Phases

**Phase Numbering:**
- Integer phases (1, 2, 3): Planned milestone work
- Decimal phases (2.1, 2.2): Urgent insertions (marked with INSERTED)

Decimal phases appear between their surrounding integers in numeric order.

- [ ] **Phase 1: TBS Ingest** - Parse Job_Architecture_TBS.xlsx into careers.sqlite with slugs
- [ ] **Phase 2: LLM Enrichment** - Generate career content for all 1,989 job titles via Anthropic API
- [ ] **Phase 3: CAF Bridge** - Scrape forces.ca, build caf_bridge in JobForge, populate caf_related in careers.sqlite
- [ ] **Phase 4: App Foundation** - FastAPI app, static assets, GC FIP header and footer on all pages
- [ ] **Phase 5: L1 Card Grid** - Browse page with job family cards matching CAF visual design
- [ ] **Phase 6: L1 Interactivity** - Job Function filter and real-time search bar on the browse page
- [ ] **Phase 7: L2 Job Family Page** - Job title listing within a family with metadata badges and breadcrumb
- [ ] **Phase 8: L3 Job Title Detail** - Five-tab career profile page with action buttons and breadcrumb

## Phase Details

### Phase 1: TBS Ingest
**Goal**: careers.sqlite contains all 1,989 job titles with TBS fields and URL-safe slugs, ready for enrichment
**Depends on**: Nothing (first phase)
**Requirements**: PIPE-01, PIPE-02
**Success Criteria** (what must be TRUE):
  1. Running the ingest script against Job_Architecture_TBS.xlsx produces careers.sqlite with 1,989 rows in the careers table
  2. Every row has all TBS fields populated: jt_id, job_title, job_family, job_function, managerial_level, noc_2021_uid, noc_2021_title, digital
  3. Every job title and job family has a unique, URL-safe slug (lowercase, hyphenated, no special characters)
  4. Re-running the ingest is idempotent — no duplicate rows created
**Plans**: 1 plan

Plans:
- [ ] 01-01-PLAN.md � Create pipeline package, schema, slug utility, and full TBS ingest with upsert and card image seeding

### Phase 2: LLM Enrichment
**Goal**: Every job title in careers.sqlite has AI-generated career content and is flagged as draft
**Depends on**: Phase 1
**Requirements**: PIPE-03, PIPE-04
**Success Criteria** (what must be TRUE):
  1. Every row in careers.sqlite has non-null values for overview, training, entry_plans, and part_time columns
  2. Every enriched row has content_status = 'draft' and a populated enriched_at timestamp
  3. The enrichment script can be resumed after interruption without re-enriching already-completed rows
  4. Enrichment runs against all 1,989 titles without unhandled API errors
**Plans**: TBD

### Phase 3: CAF Bridge
**Goal**: CAF bridge data from JobForge flows into careers.sqlite so each civilian title knows its related military careers
**Depends on**: Phase 1
**Requirements**: PIPE-05, PIPE-06, PIPE-07
**Note**: JobForge Phase 15 already built and tested the CAF scraper, dim_caf_occupation (88 occupations), bridge_caf_ja (880 CAF→TBS mappings), and bridge_caf_noc. The pipeline code exists and passed UAT. Phase 3 runs the JobForge pipeline to generate the parquet files, then reads bridge_caf_ja to populate careers.sqlite. No re-scraping needed.
**Success Criteria** (what must be TRUE):
  1. JobForge gold parquets (dim_caf_occupation, bridge_caf_ja) exist and are populated by running the existing Phase 15 pipeline
  2. The bridge reader script reads bridge_caf_ja and maps caf_slug → jt_ids against careers.sqlite job titles
  3. Job title rows in careers.sqlite that have matching CAF careers show a non-empty caf_related JSON array
  4. Job title rows with no CAF match have caf_related = null or empty array (no false positives)
**Plans**: TBD

### Phase 4: App Foundation
**Goal**: A running FastAPI app serves pages from ps_careers_site/ with correct GC FIP chrome on every page
**Depends on**: Phase 1
**Requirements**: FOUND-01, FOUND-02, FOUND-03, FOUND-04
**Success Criteria** (what must be TRUE):
  1. The FastAPI app starts on a configurable port and returns HTTP 200 for its routes
  2. Card background images and the Canada wordmark load from /static/ with no 404 errors
  3. The GC FIP header renders on every page with Canada wordmark, nav links, and Exo 2 font
  4. The footer renders on every page with a 5-column link grid on #1a1a1a, Canada wordmark, and social icons
**Plans**: TBD

### Phase 5: L1 Card Grid
**Goal**: A visitor at /careers sees all available job family cards styled to match the CAF site
**Depends on**: Phase 4
**Requirements**: L1-01, L1-02, L1-03
**Success Criteria** (what must be TRUE):
  1. The /careers page renders a card grid showing all seeded job families
  2. Each card shows the job family name, background image, and a "VIEW CAREERS" button styled with Exo 2 23.2px, gradient overlay, and transparent border
  3. The grid is 4 columns at >=1200px, 3 columns at >=768px, and 1 column on mobile
  4. Clicking any card navigates to /careers/{family-slug} without a 404
**Plans**: TBD

### Phase 6: L1 Interactivity
**Goal**: A visitor can narrow the card grid by job function or keyword without a page reload
**Depends on**: Phase 5
**Requirements**: L1-04, L1-05
**Success Criteria** (what must be TRUE):
  1. The Job Function dropdown lists all 22 functions; selecting one hides cards from other functions and shows only matching families
  2. Typing in the search bar filters visible cards in real time by job family name or job title keyword
  3. Clearing the filter/search restores the full grid without a page reload
**Plans**: TBD

### Phase 7: L2 Job Family Page
**Goal**: A visitor at /careers/{family-slug} sees every job title in that family with metadata and can navigate deeper
**Depends on**: Phase 5
**Requirements**: L2-01, L2-02, L2-03, L2-04
**Success Criteria** (what must be TRUE):
  1. /careers/{family-slug} lists every job title belonging to that family
  2. Each listing shows the job title, NOC 2021 code badge, managerial level tag, Digital/Non-Digital indicator, and the first 150 characters of overview
  3. Clicking a job title navigates to /career/{title-slug} without a 404
  4. The page heading shows the job family name and a breadcrumb reading Home > Careers > [Family Name]
**Plans**: TBD

### Phase 8: L3 Job Title Detail
**Goal**: A visitor at /career/{title-slug} can read a complete career profile across five tabs and take action
**Depends on**: Phase 7, Phase 2, Phase 3
**Requirements**: L3-01, L3-02, L3-03, L3-04, L3-05, L3-06, L3-07, L3-08, L3-09
**Success Criteria** (what must be TRUE):
  1. /career/{title-slug} shows the job title, NOC code, job family, and managerial level in the page header
  2. Five tab labels (Overview, Training, Entry Plans, Part-Time Options, Related Careers) are visible and clicking each scrolls to or reveals its content section; the tab bar sticks to the top on scroll
  3. Each content tab (Overview, Training, Entry Plans, Part-Time Options) renders the corresponding LLM-generated field from careers.sqlite
  4. The Related Careers tab shows any linked civilian titles and any CAF equivalent links drawn from caf_related bridge data
  5. The "Discover", "Prepare", and "Apply" action buttons are present — Discover scrolls to Overview, Prepare scrolls to Training, Apply links to jobs.gc.ca
  6. The breadcrumb reads Home > Careers > [Family Name] > [Job Title]
**Plans**: TBD

## Progress

**Execution Order:**
Phases execute in numeric order: 1 → 2 → 3 → 4 → 5 → 6 → 7 → 8
Note: Phase 3 depends on Phase 1 (not Phase 2); Phase 8 depends on Phases 2, 3, and 7.

| Phase | Plans Complete | Status | Completed |
|-------|----------------|--------|-----------|
| 1. TBS Ingest | 0/TBD | Not started | - |
| 2. LLM Enrichment | 0/TBD | Not started | - |
| 3. CAF Bridge | 0/TBD | Not started | - |
| 4. App Foundation | 0/TBD | Not started | - |
| 5. L1 Card Grid | 0/TBD | Not started | - |
| 6. L1 Interactivity | 0/TBD | Not started | - |
| 7. L2 Job Family Page | 0/TBD | Not started | - |
| 8. L3 Job Title Detail | 0/TBD | Not started | - |
