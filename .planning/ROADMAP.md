# Roadmap: JD Builder Lite

## Milestones

- **v4.1 Polish** -- Phases 18-19 (in progress)
- ✅ **v4.0 Occupational Group Allocation** -- Phases 14-17 (shipped 2026-02-04)
- ✅ **v3.0 Style-Enhanced Writing** -- Phases 09-13 (shipped 2026-02-03)
- ✅ **v2.0 UI Redesign** -- Phases 08-A through 08-D (shipped 2026-01-25)
- ✅ **v1.1 Enhanced Data Display + Export** -- Phases 05-07 (shipped 2026-01-23)
- ✅ **v1.0 MVP** -- Phases 01-04 (shipped 2026-01-22)

## Current: v4.1 Polish

**Milestone Goal:** Exec-ready demo polish -- restructure profile tabs, improve navigation flow between screens, add coaching tone to classification, make results exportable, and update documentation.

- [x] **Phase 18: Profile Page Overhaul** - Restructure tabs and enhance data display on the profile page (completed 2026-02-07)
- [ ] **Phase 19: Flow and Export Polish** - Fix navigation between screens, add coaching UX, extend export, update docs

## Phase Details

### Phase 18: Profile Page Overhaul
**Goal**: Profile page presents NOC data in a clean, logical tab structure with meaningful dimension labels on all ratings
**Depends on**: Nothing (no dependency on Phase 19)
**Requirements**: TAB-01, TAB-02, TAB-03, TAB-04, TAB-05, TAB-06, DISP-01, DISP-02, DISP-03
**Success Criteria** (what must be TRUE):
  1. Skills, Abilities, and Knowledge each appear as separate tabs on the profile page (not lumped together)
  2. Core Competencies has its own dedicated tab separate from Overview
  3. Navy blue description, Feeder Group Mobility, Career Progression, and Other Job Information content all live inside the Overview tab with no leftover empty tabs
  4. Every level circle on every statement shows its dimension type (e.g., "Proficiency: 4/5", "Importance: 3/5") derived from guide.csv
  5. Occupational category filter displays sub-major group and minor group hierarchy headings
**Plans**: 2 plans

Plans:
- [x] 18-01-PLAN.md -- Tab restructure + dimension labels (split Skills into 3 tabs, promote Core Competencies, consolidate Overview, dimension-aware proficiency labels)
- [x] 18-02-PLAN.md -- Filter hierarchy headings (hierarchical sub-major/minor group checkboxes with parent selection)

### Phase 19: Flow and Export Polish
**Goal**: Users can navigate fluidly between builder, preview, and classification screens with coaching guidance on invalid results, export classification alongside JD, and README reflects shipped state
**Depends on**: Nothing (independent of Phase 18; can execute in either order)
**Requirements**: NAV-01, NAV-02, NAV-03, UX-01, UX-02, UX-03, UX-04, EXP-01, EXP-02, DOC-01
**Success Criteria** (what must be TRUE):
  1. Preview screen shows Classify, Export, and Return to Builder as navigation options -- Return to Builder preserves all selections
  2. Classification results screen has Return to Builder button that goes back to profile page with selections intact
  3. Invalid Combination result displays in coaching style (blue/amber, not red) with explanation of why and what to adjust, plus Return to Builder button
  4. Classification results (recommendations, confidence, rationale, evidence, provenance) appear in exported PDF/DOCX
  5. GitHub README accurately describes v4.0 architecture, setup instructions, and shipped features
**Plans**: TBD

Plans:
- [ ] 19-01: Navigation wiring (Classify from preview, Return to Builder from classification, fix Back to Edit)
- [ ] 19-02: Invalid Combination coaching UX (restyle, add explanation and suggestions)
- [ ] 19-03: Classification export and README update

## Progress

| Phase | Milestone | Plans Complete | Status | Completed |
|-------|-----------|----------------|--------|-----------|
| 18. Profile Page Overhaul | v4.1 | 2/2 | ✓ Complete | 2026-02-07 |
| 19. Flow and Export Polish | v4.1 | 0/3 | Not started | - |

---
*Roadmap updated: 2026-02-07 -- Phase 18 complete (2/2 plans, verified)*
