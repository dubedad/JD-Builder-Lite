# Requirements: DND Civilian Careers Site

**Defined:** 2026-03-15
**Core Value:** A job seeker can find a DND civilian career, understand it, and know how to enter it — without HR help.

## v1 Requirements

### Data Pipeline

- [ ] **PIPE-01**: System ingests Job_Architecture_TBS.xlsx into careers.sqlite with all 1,989 job titles and their TBS fields (jt_id, job_title, job_family, job_function, managerial_level, noc_2021_uid, noc_2021_title, digital)
- [ ] **PIPE-02**: System generates a URL-safe slug for each job title and job family
- [ ] **PIPE-03**: System runs LLM enrichment (Anthropic API) to generate overview, training, entry_plans, and part_time content for each job title, storing results in careers.sqlite
- [ ] **PIPE-04**: System sets content_status = 'draft' and enriched_at timestamp on each LLM-enriched record
- [ ] **PIPE-05**: System scrapes forces.ca CAF career pages and stores CAF career data (slug, title, category, overview, training, entry plans, related civilian occupation strings) as a gold table in JobForge (caf_careers)
- [ ] **PIPE-06**: System builds a bridge table in JobForge (caf_bridge) that maps each CAF career slug to one or many TBS job title IDs (jt_ids) by fuzzy-matching the "Related Civilian Occupations" strings from CAF pages against Job_Title values in the job_architecture table — this is the connector between the CAF taxonomy and the TBS Job Architecture taxonomy
- [ ] **PIPE-07**: System reads the JobForge caf_bridge table during the careers.sqlite build step and populates the caf_related column (JSON array of CAF slugs) on matching job title records

### App Foundation

- [ ] **FOUND-01**: FastAPI app starts and serves pages from ps_careers_site/ on a configurable port
- [ ] **FOUND-02**: Static assets (12 card images, GC Canada Logo, hero image) are served from /static/
- [ ] **FOUND-03**: GC FIP header renders on all pages: Canada wordmark, nav links, Exo 2 font
- [ ] **FOUND-04**: Footer renders on all pages: 5-column link grid on #1a1a1a, Canada wordmark, social icons

### L1 Browse Page

- [ ] **L1-01**: Visitor sees a card grid of all available job families at /careers (full-width, 4-col at >=1200px, 3-col at >=768px, 1-col mobile)
- [ ] **L1-02**: Each card shows the job family name, background image, and "VIEW CAREERS" button with exact CAF styling (Exo 2 23.2px, gradient overlay, transparent border button)
- [ ] **L1-03**: Clicking a card navigates to the L2 job family page (/careers/{family-slug})
- [ ] **L1-04**: Visitor can filter the card grid by Job Function (22 values) using a dropdown — only families in the selected function are shown
- [ ] **L1-05**: Visitor can type in the search bar to filter cards by job family name or job title keyword — cards update in real time

### L2 Job Family Page

- [ ] **L2-01**: Visitor sees a list of all job titles within the selected family at /careers/{family-slug}
- [ ] **L2-02**: Each listing shows: job title, NOC 2021 code badge, managerial level tag, Digital/Non-Digital indicator, and first 150 characters of overview
- [ ] **L2-03**: Clicking a job title navigates to the L3 detail page (/career/{title-slug})
- [ ] **L2-04**: Page shows the job family name as heading with breadcrumb: Home > Careers > [Family Name]

### L3 Job Title Detail Page

- [ ] **L3-01**: Visitor sees the job title, NOC code, job family, and managerial level at /career/{title-slug}
- [ ] **L3-02**: Page has a sticky tab nav bar (Overview, Training, Entry Plans, Part-Time Options, Related Careers) that anchors to page sections on click
- [ ] **L3-03**: Overview tab shows: role description, responsibilities list, work environment (from overview column)
- [ ] **L3-04**: Training tab shows: education requirements, certifications, professional development (from training column)
- [ ] **L3-05**: Entry Plans tab shows: how to enter this career in the federal Public Service (from entry_plans column)
- [ ] **L3-06**: Part-Time Options tab shows: flexible work, remote, part-time options (from part_time column)
- [ ] **L3-07**: Related Careers tab shows: related civilian job titles (from related_careers) and linked CAF equivalents (from caf_related bridge data)
- [ ] **L3-08**: Page has "Discover", "Prepare", and "Apply" action buttons — Discover scrolls to Overview, Prepare scrolls to Training, Apply links to jobs.gc.ca
- [ ] **L3-09**: Breadcrumb shows: Home > Careers > [Family Name] > [Job Title]

## v2 Requirements

### Bilingual

- **BILI-01**: All page text available in French (toggle EN/FR)
- **BILI-02**: French job titles (titre_de_poste) displayed when FR mode active
- **BILI-03**: URL routing supports /fr/carrieres and /fr/carriere/{slug}

### Advanced Search & Filter

- **SRCH-01**: Visitor can filter by Managerial Level (Employee / Manager / Executive)
- **SRCH-02**: Visitor can filter by Digital / Non-Digital flag
- **SRCH-03**: Visitor can filter by minimum education level
- **SRCH-04**: Full-text search across all LLM-generated content (overview, training, etc.)

### Accessibility & Compliance

- **A11Y-01**: Formal WCAG 2.1 AA audit completed and issues resolved
- **COMP-01**: Human review workflow for LLM-generated content (draft > reviewed > published status)

## Out of Scope

| Feature | Reason |
|---------|--------|
| JD Builder (Surface B) | Separate app, separate milestone |
| User authentication | Public read-only site, no login needed |
| React / SPA frontend | Spec calls for FastAPI + Jinja2 |
| Protected B data | Only open occupational data (NOC, TBS Job Architecture) |
| Full bilingual (v1) | TBS table has French fields but full bilingual deferred to v2 |

## Traceability

| Requirement | Phase | Status |
|-------------|-------|--------|
| PIPE-01 | Phase 1 | Pending |
| PIPE-02 | Phase 1 | Pending |
| PIPE-03 | Phase 2 | Pending |
| PIPE-04 | Phase 2 | Pending |
| PIPE-05 | Phase 3 | Pending |
| PIPE-06 | Phase 3 | Pending |
| PIPE-07 | Phase 3 | Pending |
| FOUND-01 | Phase 4 | Pending |
| FOUND-02 | Phase 4 | Pending |
| FOUND-03 | Phase 4 | Pending |
| FOUND-04 | Phase 4 | Pending |
| L1-01 | Phase 5 | Pending |
| L1-02 | Phase 5 | Pending |
| L1-03 | Phase 5 | Pending |
| L1-04 | Phase 6 | Pending |
| L1-05 | Phase 6 | Pending |
| L2-01 | Phase 7 | Pending |
| L2-02 | Phase 7 | Pending |
| L2-03 | Phase 7 | Pending |
| L2-04 | Phase 7 | Pending |
| L3-01 | Phase 8 | Pending |
| L3-02 | Phase 8 | Pending |
| L3-03 | Phase 8 | Pending |
| L3-04 | Phase 8 | Pending |
| L3-05 | Phase 8 | Pending |
| L3-06 | Phase 8 | Pending |
| L3-07 | Phase 8 | Pending |
| L3-08 | Phase 8 | Pending |
| L3-09 | Phase 8 | Pending |

**Coverage:**
- v1 requirements: 29 total
- Mapped to phases: 29
- Unmapped: 0 (complete)

---
*Requirements defined: 2026-03-15*
*Last updated: 2026-03-15 — Traceability populated by roadmapper*
