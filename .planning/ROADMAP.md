# v2.0 UI Redesign Roadmap

**Milestone:** v2.0 UI Redesign
**Phases:** 08-A through 08-D (continues from v1.1 Phase 07)
**Created:** 2026-01-24

---

## Phase Overview

| Phase | Name | Goal | Requirements | Success Criteria |
|-------|------|------|--------------|------------------|
| 08-A | Search Bar Redesign | Step 1 UI - search above results with pill toggle | SRCH-10, SRCH-11, SRCH-12 | 3 |
| 08-B | Results Cards & Grid | Step 4 UI - OaSIS cards, custom grid, custom filters | DISP-20, DISP-21, DISP-22, DISP-23 | 4 |
| 08-C | Profile Page Tabs | Step 9 UI - header with LLM elements, Job Header tabs | DISP-30, DISP-31, DISP-32, DISP-33, DISP-34 | 5 |
| 08-D | Statement Selection | Step 10 UI - checkboxes, tooltips, single Create button | SEL-01, SEL-02, SEL-03, SEL-04, SEL-05 | 5 |

**Total:** 4 phases | 17 requirements | All requirements mapped

---

## Phase Details

### Phase 08-A: Search Bar Redesign

**Goal:** Redesign Step 1 search interface to position search bar above results with Keyword/Code pill toggle and authoritative sources footnote.

**Requirements:**
- SRCH-10: Search bar positioned above results grid with pill toggle for Keyword/Code search
- SRCH-11: Authoritative sources footnote replaces version dropdown
- SRCH-12: Remove advanced search and View all A-Z links

**Success Criteria:**
1. User sees search bar above results (not in sidebar)
2. User can toggle between Keyword and Code search modes via pill buttons
3. Authoritative sources footnote visible below search: "ESDC OaSIS 2025 NOC v1.0 / ONET (R) 27.2 Database (USDOL/ETA)"
4. No version dropdown, advanced search, or A-Z links visible

**Reference:** Slide 4, 06-CONTEXT.md Step 1 section

**Plans:** 1 plan

Plans:
- [x] 08-A-01-PLAN.md — Pill toggle, authoritative sources footnote, full stack search type support ✓

---

### Phase 08-B: Results Cards & Grid

**Goal:** Redesign Step 4 occupational profile menu with OaSIS-style cards showing 6 data points, custom grid columns, and custom filters.

**Requirements:**
- DISP-20: Card view replicates OaSIS exactly with 6 data points
- DISP-21: Grid view uses custom columns (Skills, Abilities, Knowledge)
- DISP-22: Custom filters: Minor Unit Group, Feeder Group Mobility, Career Progression
- DISP-23: Card/grid click navigates to Profile Details page

**Success Criteria:**
1. Card view displays 6 data points: lead statement, example titles, TEER, mobility/progression, source table, publication date
2. Grid view shows columns: OaSIS Profile | Top 10 Skills | Top Abilities | Top Knowledge | Matching criteria
3. Filter panel shows: Minor Unit Group, Feeder Group Mobility, Career Progression (not OaSIS filters)
4. Clicking any result navigates to profile details page

**Reference:** Slides 5-8, 13, 06-CONTEXT.md Step 4 section, OASIS-HTML-REFERENCE.md

**Plans:** 3 plans

Plans:
- [ ] 08-B-01-PLAN.md — Backend: EnrichedSearchResult model, enhanced parser, API update
- [ ] 08-B-02-PLAN.md — Card View: OaSIS-style cards HTML/CSS/JS, sort controls
- [ ] 08-B-03-PLAN.md — Filters: Filter panel with Minor Unit Group, Feeder Mobility, Career Progression

---

### Phase 08-C: Profile Page Tabs

**Goal:** Redesign Step 9 profile page with LLM-driven header elements and Job Header tab structure mapping OaSIS categories to JD elements.

**Requirements:**
- DISP-30: Profile header shows occupation title with LLM-driven icon
- DISP-31: OaSIS code displayed as badge below title
- DISP-32: LLM-generated paragraph description above tabs
- DISP-33: Horizontal tabs renamed to Job Headers
- DISP-34: Tab content mapping to OaSIS categories

**Success Criteria:**
1. Profile header displays occupation title with icon generated based on minor group
2. OaSIS code appears as styled badge below title
3. LLM-generated paragraph describing occupation visible above tabs
4. Tabs show: Overview | Key Activities | Skills | Effort | Responsibility | Feeder Group Mobility & Career Progression
5. Key Activities tab contains Main Duties + Work Activities; Skills tab contains Skills + Abilities + Knowledge; Effort/Responsibility tabs filter Work Context appropriately

**Reference:** Slides 9-10, 06-CONTEXT.md Step 9 section

**Plans:** 3 plans

Plans:
- [ ] 08-C-01-PLAN.md — Backend: LLM endpoints for icon selection and occupation description
- [ ] 08-C-02-PLAN.md — Profile Header: Blue banner with icon, badge, lead statement, LLM description
- [ ] 08-C-03-PLAN.md — Tab Navigation: ARIA tabs with content mapping to JD elements

---

### Phase 08-D: Statement Selection

**Goal:** Implement Step 10 statement selection with checkboxes, proficiency circles, hover tooltips for descriptions, and single Create JD button.

**Requirements:**
- SEL-01: Checkboxes on all statements in all Job Header tabs
- SEL-02: Proficiency circles display (filled/empty) matching OaSIS style
- SEL-03: Provenance labels always visible (small italics)
- SEL-04: Description tooltip on hover for items with proficiency levels
- SEL-05: Single "Create Job Description (X selected)" button

**Success Criteria:**
1. Every statement row has a checkbox for selection
2. Proficiency circles display correctly (1-5 scale with filled/empty circles)
3. Provenance labels ("from Main Duties", "from Work Activities") visible in small italics below each statement
4. Hovering over statement text shows OaSIS attribute description as tooltip
5. Single "Create Job Description (X selected)" button visible, count updates with selections

**Reference:** Slide 12, 06-CONTEXT.md Step 9/10 section

**Plans:** (created by /gsd:plan-phase)

---

## Execution Order

1. **08-A** (Search Bar) — Smallest scope, establishes new styling patterns
2. **08-B** (Results) — Builds on search styling, independent of profile page
3. **08-C** (Profile Tabs) — Most complex, restructures tab system
4. **08-D** (Selection) — Adds interaction layer to 08-C tab content

Each phase produces working code. Usability testing follows execution.

---

## Reference Documents

| Document | Location | Purpose |
|----------|----------|---------|
| Full Specifications | `.planning/phases/06-enhanced-ui-display/06-CONTEXT.md` | All decisions and details |
| Summary | `.planning/phases/06-enhanced-ui-display/06-UI-REDESIGN-SUMMARY.md` | Quick reference |
| HTML Reference | `.planning/phases/06-enhanced-ui-display/OASIS-HTML-REFERENCE.md` | OaSIS HTML for replication |
| Slides | `overview for job lite process milestone 2/` | Visual mockups |

---
*Created: 2026-01-24*
*Phase 08-A planned: 2026-01-24*
*Phase 08-B planned: 2026-01-24*
*Phase 08-C planned: 2026-01-24*
