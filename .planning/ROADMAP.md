# Roadmap: JD Builder Lite

## Milestones

- **v4.1 Polish** -- Phases 18-20 (in progress)
- ✅ **v4.0 Occupational Group Allocation** -- Phases 14-17 (shipped 2026-02-04)
- ✅ **v3.0 Style-Enhanced Writing** -- Phases 09-13 (shipped 2026-02-03)
- ✅ **v2.0 UI Redesign** -- Phases 08-A through 08-D (shipped 2026-01-25)
- ✅ **v1.1 Enhanced Data Display + Export** -- Phases 05-07 (shipped 2026-01-23)
- ✅ **v1.0 MVP** -- Phases 01-04 (shipped 2026-01-22)

## Current: v4.1 Polish

**Milestone Goal:** Exec-ready demo polish -- restructure profile tabs, improve navigation flow between screens, add coaching tone to classification, make results exportable, and update documentation.

- [x] **Phase 18: Profile Page Overhaul** - Restructure tabs and enhance data display on the profile page (completed 2026-02-07)
- [x] **Phase 19: Flow and Export Polish** - Fix navigation between screens, add coaching UX, extend export, update docs (completed 2026-02-07)
- [ ] **Phase 20: Evidence & Provenance Display** - Evidence highlighting with fuzzy matching, provenance tree, completion guidance (carried from v4.0 17-03)

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
**Plans**: 3 plans

Plans:
- [x] 19-01-PLAN.md -- Navigation wiring: split nav layout, breadcrumb, Return to Builder, Classify from preview, classification caching
- [x] 19-02-PLAN.md -- Multi-group coaching UX: replace error-style invalid_combination with ranked coaching panel
- [x] 19-03-PLAN.md -- Classification export with hyperlinked provenance, export checkboxes, README creation

### Phase 20: Evidence & Provenance Display
**Goal**: Users can verify classification recommendations by seeing evidence quotes highlighted in context within their JD text, trace provenance from recommendation back to TBS source, and receive completion guidance for next steps
**Depends on**: Nothing (independent of Phases 18-19)
**Requirements**: EVD-01, EVD-02, EVD-03, EVD-04, EVD-05
**Success Criteria** (what must be TRUE):
  1. User can click evidence link to see side-by-side JD text view with evidence quote highlighted (EVD-01)
  2. Evidence quote is highlighted in the JD text panel using fuzzy matching when exact match fails (EVD-02)
  3. Multiple evidence quotes can be highlighted simultaneously (EVD-03)
  4. User can see expandable provenance tree from recommendation to TBS source (EVD-04)
  5. User sees Classification Step 1 Complete with next steps guidance (EVD-05)
**Plans**: 2 plans

Plans:
- [ ] 20-01-PLAN.md -- Upgrade provenance rendering from flat to expandable tree (closes gap between existing CSS and JS)
- [ ] 20-02-PLAN.md -- Human verification of complete evidence, provenance, and completion flow (carried from 17-03 Task 3)

## Progress

| Phase | Milestone | Plans Complete | Status | Completed |
|-------|-----------|----------------|--------|-----------|
| 18. Profile Page Overhaul | v4.1 | 2/2 | ✓ Complete | 2026-02-07 |
| 19. Flow and Export Polish | v4.1 | 3/3 | ✓ Complete | 2026-02-07 |
| 20. Evidence & Provenance Display | v4.1 | 0/2 | Not started | - |

---
*Roadmap updated: 2026-02-07 -- Phase 19 complete (3 plans executed, goal verified)*
