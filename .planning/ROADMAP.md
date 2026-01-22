# Roadmap: JD Builder Lite

## Overview

JD Builder Lite delivers a compliance-focused job description builder in 4 phases following the natural data flow: search and scrape NOC data, display and select content, generate AI overview, and export with full provenance. Each phase builds on the previous, delivering a working capability that can be verified before proceeding. The emphasis throughout is on audit-ready traceability that demonstrates compliance with Canada's Directive on Automated Decision-Making.

## Phases

**Phase Numbering:**
- Integer phases (1, 2, 3, 4): Planned milestone work
- Decimal phases (e.g., 2.1): Urgent insertions (marked with INSERTED)

- [x] **Phase 1: Backend + Scraping** - Flask server that searches OASIS and returns parsed, mapped NOC data
- [x] **Phase 2: Frontend Core UI** - Interactive display of NOC data organized by JD elements with selection
- [ ] **Phase 3: LLM Integration** - AI-generated General Overview with full provenance tracking
- [ ] **Phase 4: Output + Compliance** - PDF export with compliance metadata and audit trail

## Phase Details

### Phase 1: Backend + Scraping
**Goal**: Manager can search OASIS and receive structured NOC data ready for display
**Depends on**: Nothing (first phase)
**Requirements**: SRCH-01, SRCH-02, SRCH-03, DATA-01, DATA-02
**Success Criteria** (what must be TRUE):
  1. Manager can enter a job title and see matching Occupational Profiles from OASIS
  2. Manager can select a profile and receive all NOC data (Overview, Work Characteristics, Skills & Abilities, Interests, Employment Requirements, Skills for Success)
  3. Backend returns data with source metadata (NOC code, profile URL, retrieval timestamp)
  4. Data is organized by JD element mapping (Key Activities, Skills, Effort, Responsibility, Working Conditions)
**Plans**: 3 plans

Plans:
- [x] 01-01-PLAN.md — Project foundation: dependencies, Pydantic models, OASIS scraper service
- [x] 01-02-PLAN.md — HTML parsing: CSS selectors, BeautifulSoup parser, NOC-to-JD mapper
- [x] 01-03-PLAN.md — Flask integration: API routes, app entry point, live verification

### Phase 2: Frontend Core UI
**Goal**: Manager can view NOC data organized by JD elements and select statements for the job description
**Depends on**: Phase 1
**Requirements**: DISP-01, DISP-02, DISP-03
**Success Criteria** (what must be TRUE):
  1. Manager sees NOC data organized under JD Element headers (Key Activities, Skills, Effort, Responsibility, Working Conditions)
  2. Manager can select multiple statements under each JD Element using checkboxes
  3. Selected statements show their NOC source attribution
  4. Selections persist as manager moves between JD Element sections
**Plans**: 2 plans

Plans:
- [x] 02-01-PLAN.md — Page structure, CSS styling, search-to-profile flow
- [x] 02-02-PLAN.md — Accordion display, selection system, drag-reorder, filtering, sidebar

### Phase 3: LLM Integration
**Goal**: App generates a compliant AI overview based on manager's selections
**Depends on**: Phase 2
**Requirements**: AI-01, AI-02
**Success Criteria** (what must be TRUE):
  1. Manager can trigger General Overview generation after making selections
  2. Generated overview is informed by all selected statements (visible in prompt/input)
  3. AI generation metadata is recorded (model used, timestamp, input statements)
  4. Overview is clearly marked as AI-generated in the UI
**Plans**: 2 plans

Plans:
- [ ] 03-01-PLAN.md — Backend: OpenAI SDK, LLM service, SSE streaming endpoint, provenance tracking
- [ ] 03-02-PLAN.md — Frontend: overview section, streaming textarea, AI badge, modification tracking

### Phase 4: Output + Compliance
**Goal**: Manager can export a complete, audit-ready job description PDF
**Depends on**: Phase 3
**Requirements**: OUT-01, OUT-02, OUT-03, OUT-04, OUT-05
**Success Criteria** (what must be TRUE):
  1. Manager can preview the assembled job description before export
  2. Manager can export the final JD to PDF
  3. PDF includes compliance metadata block (NOC code, source URLs, retrieval timestamp)
  4. PDF includes full audit trail (manager's selections per JD Element, traced to NOC source)
  5. PDF includes AI disclosure (General Overview marked as AI-generated, inputs listed, model and timestamp)
**Plans**: TBD

Plans:
- [ ] 04-01: TBD
- [ ] 04-02: TBD

## Progress

**Execution Order:**
Phases execute in numeric order: 1 -> 2 -> 3 -> 4

| Phase | Plans Complete | Status | Completed |
|-------|----------------|--------|-----------|
| 1. Backend + Scraping | 3/3 | ✓ Complete | 2026-01-21 |
| 2. Frontend Core UI | 2/2 | ✓ Complete | 2026-01-22 |
| 3. LLM Integration | 0/2 | Ready | - |
| 4. Output + Compliance | 0/2 | Not started | - |

---
*Roadmap created: 2026-01-21*
*Phase 1 planned: 2026-01-21*
*Phase 2 planned: 2026-01-21*
*Phase 3 planned: 2026-01-21*
