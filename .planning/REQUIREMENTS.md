# v2.0 UI Redesign Requirements

**Milestone:** v2.0 UI Redesign
**Goal:** Redesign UI to mirror OaSIS website interface following swimlane process map
**Created:** 2026-01-24

---

## Milestone Requirements

### Search (Step 1)

- [x] **SRCH-10**: Search bar positioned above results grid with pill toggle for Keyword/Code search ✓
- [x] **SRCH-11**: Authoritative sources footnote replaces version dropdown: "ESDC OaSIS 2025 NOC v1.0 / ONET (R) 27.2 Database (USDOL/ETA)" ✓
- [x] **SRCH-12**: Remove advanced search and View all A-Z links from search interface ✓

### Results Display (Step 4)

- [x] **DISP-20**: Card view replicates OaSIS exactly with 6 data points (lead statement, example titles, TEER, mobility/progression, source table, publication date) ✓
- [x] **DISP-21**: Grid view uses custom columns: OaSIS Profile | Top 10 Skills | Top Abilities | Top Knowledge | Matching criteria ✓
- [x] **DISP-22**: Custom filters replace OaSIS filters: Minor Unit Group, Feeder Group Mobility, Career Progression ✓
- [x] **DISP-23**: Card/grid click navigates to Profile Details page (Step 9) ✓

### Profile Display (Step 9)

- [x] **DISP-30**: Profile header shows occupation title with LLM-driven icon based on minor group ✓
- [x] **DISP-31**: OaSIS code displayed as badge below title ✓
- [x] **DISP-32**: LLM-generated paragraph description above tabs ✓
- [x] **DISP-33**: Horizontal tabs renamed to Job Headers: Overview | Key Activities | Skills | Effort | Responsibility | Feeder Group Mobility & Career Progression ✓
- [x] **DISP-34**: Tab content mapping: Key Activities (Main Duties + Work Activities), Skills (Skills + Abilities + Knowledge), Effort (Work Context "effort"), Responsibility (Work Context "responsib"/"decision") ✓

### Statement Selection (Step 10)

- [ ] **SEL-01**: Checkboxes on all statements in all Job Header tabs
- [ ] **SEL-02**: Proficiency circles display (●●●●○) matching OaSIS style
- [ ] **SEL-03**: Provenance labels always visible (small italics below statement)
- [ ] **SEL-04**: Description tooltip on hover for items with proficiency levels
- [ ] **SEL-05**: Single "Create Job Description (X selected)" button replaces separate Generate Overview

---

## Usability Testing Checkpoints

Each phase will produce a rough prototype for validation before final implementation:

1. **Phase 08-A**: Search bar prototype → test Keyword/Code toggle UX
2. **Phase 08-B**: Results cards prototype → verify 6 data points layout
3. **Phase 08-C**: Profile tabs prototype → validate Job Header structure
4. **Phase 08-D**: Selection prototype → test checkbox + tooltip interaction

---

## Future Requirements (Deferred to v2.1+)

- SRCH-06: Grid view shows columns: Broad category, Training/Education, Lead statement
- SRCH-07: Filter items by Job Family
- SRCH-08: Filter items by Organizational Unit
- SRCH-09: Filter items by Digital Competencies
- DISP-12: Visual scale distinction by category type
- DISP-13: "Learn More" links to OASIS source
- OUT-09: "Include Annex" checkbox toggle
- OUT-10: Custom compliance styling in DOCX

---

## Out of Scope

- User authentication — single user demo only
- Database persistence — no saved history
- Production hosting — runs locally only
- Inline rating editing — breaks provenance
- Custom statement creation — breaks audit trail

---

## Traceability

| REQ-ID | Phase | Validated |
|--------|-------|-----------|
| SRCH-10 | 08-A | ✓ |
| SRCH-11 | 08-A | ✓ |
| SRCH-12 | 08-A | ✓ |
| DISP-20 | 08-B | ✓ |
| DISP-21 | 08-B | ✓ |
| DISP-22 | 08-B | ✓ |
| DISP-23 | 08-B | ✓ |
| DISP-30 | 08-C | ✓ |
| DISP-31 | 08-C | ✓ |
| DISP-32 | 08-C | ✓ |
| DISP-33 | 08-C | ✓ |
| DISP-34 | 08-C | ✓ |
| SEL-01 | 08-D | |
| SEL-02 | 08-D | |
| SEL-03 | 08-D | |
| SEL-04 | 08-D | |
| SEL-05 | 08-D | |

---

## Reference Documents

- `.planning/phases/06-enhanced-ui-display/06-CONTEXT.md` — Full specifications
- `.planning/phases/06-enhanced-ui-display/06-UI-REDESIGN-SUMMARY.md` — Summary
- `.planning/phases/06-enhanced-ui-display/OASIS-HTML-REFERENCE.md` — HTML reference

---
*Created: 2026-01-24*
