# Phase 06: UI Redesign - Complete Summary

**Created:** 2026-01-24
**Status:** Context gathering COMPLETE - Ready for planning

---

## MILESTONE 2 SCOPE

Redesign the JD Builder Lite UI to mirror the OaSIS website interface, following the swimlane process map with numbered steps.

---

## FINALIZED SPECIFICATIONS

### STEP 1: Job Search Window
- Search bar appears ABOVE results grid
- Keyword/Code pill toggle (both options)
- Search input + Search button
- Authoritative Sources footnote: "Authoritative Sources: ESDC OaSIS 2025 NOC v1.0 / ONET (R) 27.2 Database (USDOL/ETA)"
- REMOVED: Version dropdown, View all A-Z, Advanced search

### STEP 4: Occupational Profile Menu (Search Results)
- **Card View:** Replicate OaSIS exactly with 6 data points:
  - Leading statement
  - Example titles (Also known as)
  - TEER (educational requirement)
  - Mobility and progression
  - Authoritative table source
  - Publication date
- **Grid View:** CUSTOM columns (NOT OaSIS):
  - OaSIS Profile | Top 10 Skills | Top Abilities | Top Knowledge | Matching search criteria
- **Filters:** CUSTOM (NOT OaSIS):
  - Minor Unit Group
  - Feeder Group Mobility
  - Career Progression
- **Click behavior:** Card → Step 9 (Profile Details)

### STEP 9: Profile Details Page
- **Header:**
  - Occupation title + LLM-driven icon (based on minor group)
  - OaSIS code badge
  - Leading statement
  - LLM-generated paragraph description
- **Tabs (Job Description Headers):**
  1. Overview (Also known as, Core competencies, Main duties, NOC hierarchy)
  2. Key Activities (Main Duties, Work Activities)
  3. Skills (Skills, Abilities, Knowledge)
  4. Effort (Work Context filtered for "effort")
  5. Responsibility (Work Context filtered for "responsib", "decision")
  6. Feeder Group Mobility & Career Progression (Additional Information)

### STEP 10: Statement Selection
- Checkboxes on all statements
- Proficiency circles: ●●●●○ (keep OaSIS style)
- Provenance labels always visible (small italics)
- **Description tooltip on HOVER** - for items with proficiency levels, mouseover shows OaSIS attribute description
- Single button: "Create Job Description (X selected)"

---

## DATA MAPPING (Slide 3)

| Job Header | OaSIS Source |
|------------|--------------|
| Key Activities | Main Duties, Work Activities |
| Skills | Skills, Abilities, Knowledge |
| Effort | Work Context (filter "effort") |
| Responsibility | Work Context (filter "responsib", "decision") |

**NOT in JD (Overview only):** job requirements, career mobility, example titles, labels, leading statements, interests, personal attributes

---

## REFERENCE FILES

1. **06-CONTEXT.md** - Full specifications with all decisions
2. **OASIS-HTML-REFERENCE.md** - Actual HTML from OaSIS site for replication
3. **Slides source:** `overview for job lite process milestone 2/`

---

## RECOMMENDED APPROACH

### Option A: Single Large Phase
- One phase covering all UI changes
- Risk: Large scope, harder to verify

### Option B: Break into Sub-Phases (RECOMMENDED)
1. **Phase 06-A: Search Bar Redesign** - Step 1 UI
2. **Phase 06-B: Results Cards/Grid** - Step 4 UI
3. **Phase 06-C: Profile Page Tabs** - Step 9 UI with Job Headers
4. **Phase 06-D: Statement Selection** - Step 10 checkboxes + button

### Execution Order
1. Start with Step 1 (search bar) - smallest, establishes styling
2. Then Step 4 (results) - builds on search styling
3. Then Step 9 (profile) - most complex, needs tabs restructured
4. Finally Step 10 (selection) - adds checkboxes to Step 9

---

## NEXT STEPS

1. Run `/gsd:plan-phase` for Phase 06 (or first sub-phase)
2. Research agent will analyze current codebase
3. Planner will create detailed PLAN.md
4. Execute with atomic commits
5. Verify each sub-phase before proceeding
