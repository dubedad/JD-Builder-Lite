# Roadmap: JD Builder Lite v4.0

## Overview

v4.0 implements Classification Step 1: Occupational Group Allocation. The milestone delivers a matching engine that compares job descriptions against TBS occupational group definitions using the prescribed allocation method with full policy provenance. The journey starts with scraping authoritative data (DIM_OCCUPATIONAL table), proceeds through the OccupationalGroupAllocator matching engine, then exposes the allocation API, and concludes with a recommendations UI.

**Authoritative Source:** https://www.canada.ca/en/treasury-board-secretariat/services/classification/job-evaluation/guide-allocating-positions-using-occupational-group-definitions.html

## Milestones

- **v4.0 Occupational Group Allocation** - Phases 14-17 (in progress)

## Phases

**Phase Numbering:**
- Integer phases (14, 15, 16...): Planned milestone work
- Decimal phases (14.1, 14.2): Urgent insertions (marked with INSERTED)

Decimal phases appear between their surrounding integers in numeric order.

- [x] **Phase 14: Data Layer** - Scrape DIM_OCCUPATIONAL table from TBS with definitions, inclusions, exclusions
- [x] **Phase 15: Matching Engine** - OccupationalGroupAllocator with holistic definition matching
- [x] **Phase 16: API Layer** - POST /api/allocate endpoint with provenance response
- [ ] **Phase 17: UI Layer** - Recommendations display with rationale and evidence links

## Phase Details

### Phase 14: Data Layer
**Goal**: DIM_OCCUPATIONAL table populated with all occupational group definitions
**Depends on**: Nothing (first phase of v4.0)
**Requirements**: DATA-01, DATA-02, DATA-03, DATA-04, DATA-05
**Success Criteria** (what must be TRUE):
  1. TBS occupational groups table scraped from authoritative source
  2. For each group, definition page scraped with: definition statement, inclusion statements, exclusion statements
  3. Group metadata extracted: Group code, Subgroup, Definition, Qualification standard, Rates of pay links
  4. DIM_OCCUPATIONAL lookup table built with all scraped data
  5. Table of Concordance links group definitions to job evaluation standards
**Plans**: 3 plans
Plans:
- [x] 14-01-PLAN.md - Database foundation with SQLite schema, connection manager, repository
- [x] 14-02-PLAN.md - HTTP client with rate limiting, HTML archiver, TBS page parsers
- [x] 14-03-PLAN.md - ETL orchestrator with validation and CLI refresh command

### Phase 15: Matching Engine
**Goal**: OccupationalGroupAllocator produces ranked recommendations with provenance
**Depends on**: Phase 14 (data layer)
**Requirements**: MATCH-01 through MATCH-08, OUT-01 through OUT-07, EDGE-01 through EDGE-04
**Success Criteria** (what must be TRUE):
  1. System extracts primary purpose from JD using Client-Service Results and Key Activities
  2. System shortlists candidate groups based on semantic similarity + labels boost
  3. System evaluates definition fit holistically (not keyword matching)
  4. System checks inclusion statements and links to definition when used
  5. System checks exclusion statements to confirm they don't reflect primary purpose
  6. System produces ranked top-3 recommendations with confidence scores (0.0-1.0)
  7. System handles edge cases: AP vs TC disambiguation, multiple groups plausible, invalid combination
**Plans**: 5 plans
Plans:
- [x] 15-01-PLAN.md - Pydantic output models and repository extensions for statements
- [x] 15-02-PLAN.md - Semantic shortlisting with sentence-transformers and labels boost
- [x] 15-03-PLAN.md - Multi-factor confidence scoring and evidence linking
- [x] 15-04-PLAN.md - LLM classifier with structured outputs and instructor library
- [x] 15-05-PLAN.md - Main allocator orchestration and edge case handling

### Phase 16: API Layer
**Goal**: Allocation endpoint returns recommendations with full provenance map
**Depends on**: Phase 15 (matching engine)
**Requirements**: API-01, API-02, API-03, API-04
**Success Criteria** (what must be TRUE):
  1. POST /api/allocate accepts JD data and returns allocation recommendations
  2. Response includes full provenance map linking decisions to authoritative source paragraphs
  3. Response includes confidence scores and rationale for each recommendation
  4. API handles edge cases: "Needs Work Description Clarification", "Invalid Combination of Work"
**Plans**: 2 plans
Plans:
- [x] 16-01-PLAN.md - Request/response Pydantic models with JD validation and provenance structure
- [x] 16-02-PLAN.md - POST /api/allocate endpoint with provenance builder and caching

### Phase 17: UI Layer
**Goal**: User can view allocation recommendations with evidence and provenance
**Depends on**: Phase 16 (API layer)
**Requirements**: UI-01, UI-02, UI-03, UI-04, UI-05
**Success Criteria** (what must be TRUE):
  1. UI displays top-3 ranked group recommendations with confidence bars
  2. UI shows rationale for each recommendation (expandable)
  3. UI shows evidence links to JD text spans (highlight on click)
  4. UI shows provenance chain to authoritative source
  5. UI displays "Classification Step 1 Complete" status with next steps
**Plans**: 3 plans
Plans:
- [ ] 17-01-PLAN.md - Step 5 stepper navigation and API client method
- [ ] 17-02-PLAN.md - Recommendation cards with confidence visualization
- [ ] 17-03-PLAN.md - Evidence highlighting and provenance display

## Progress

**Execution Order:**
Phases execute in numeric order: 14 -> 15 -> 16 -> 17
Note: Phase 15 requires Phase 14; Phases 16-17 are sequential.

| Phase | Plans Complete | Status | Completed |
|-------|----------------|--------|-----------|
| 14. Data Layer | 3/3 | Complete | 2026-02-04 |
| 15. Matching Engine | 5/5 | Complete | 2026-02-04 |
| 16. API Layer | 2/2 | Complete | 2026-02-04 |
| 17. UI Layer | 0/3 | Planned | - |

---
*Roadmap created: 2026-02-04*
*Last updated: 2026-02-04 - Phase 17 plans created*
*Milestone: v4.0 Occupational Group Allocation*
