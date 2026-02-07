# Phase 18: Profile Page Overhaul - Context

**Gathered:** 2026-02-06
**Status:** Ready for planning

<domain>
## Phase Boundary

Restructure profile page tabs and enhance data display. Split Skills/Abilities/Knowledge into separate tabs, promote Core Competencies to its own tab, consolidate Feeder Group Mobility/Career Progression/Other Job Information into Overview, add dimension type labels to all rating circles, and add hierarchy headings to the occupational category filter. No new capabilities -- this reorganizes and labels existing content.

</domain>

<decisions>
## Implementation Decisions

### Tab structure & ordering
- 8 tabs in this order: Overview, Core Competencies, Key Activities, Skills, Abilities, Knowledge, Effort, Responsibility
- Remove Feeder Group Mobility & Career Progression tab (content moves to Overview)
- Remove Other Job Information tab (content moves to Overview)
- Split current Skills tab into 3 separate tabs: Skills, Abilities, Knowledge
- Promote Core Competencies from inside Overview to its own dedicated tab
- Default selected tab on profile load: Overview
- Claude's discretion on tab bar overflow handling (wrap vs scroll vs label shortening) based on existing CSS and screen width

### Dimension label presentation
- Replace the current "L3" label with dimension-aware format: "Proficiency 3/5", "Importance 3/5", etc.
- Position: same spot as current L-number label (after the rating circles)
- Dimension types derived from guide.csv per category (Skills=Proficiency, Abilities=Proficiency, Knowledge=Knowledge Level, Work Activities=Complexity, Personal Attributes=Importance, Work Context=varies)

### Overview tab layout
- Navy blue description text moves from above-tabs position INTO the Overview tab
- The NOC icon/badge stays above the tabs in its current position AND is also copied into the Overview tab
- Above-tabs area: icon only (description text removed from there)
- Overview tab: icon + full description + existing reference data + consolidated content from removed tabs

### Filter hierarchy display
- Sub-major group and minor group hierarchy headings in occupational category filter
- Sub-major group headings are selectable -- clicking selects/deselects all minor groups underneath
- Hierarchy data sourced from `dim_noc_structure` table in the JobForge 2.0 directory
- Need to load dim_noc_structure data and map it to search results for filter building

### Claude's Discretion
- Tab bar overflow handling (wrap vs scroll vs abbreviation)
- Tooltip behavior on rating circles (keep or remove given new labels)
- Dimension label wording (exact guide.csv names vs shortened single-word variants)
- Mixed dimension type display within categories (inline per-statement vs grouped headers)
- Overview tab section ordering and organization
- Whether Overview sections are collapsible and which start expanded/collapsed
- Filter hierarchy visual style (indented tree, grouped sections, or accordion)
- Item count display on filter hierarchy levels

</decisions>

<specifics>
## Specific Ideas

- User wants the NOC icon visible in both the header area and the Overview tab -- it's a recognizable element that anchors the profile
- Navy blue description is a distinctive visual treatment that should be preserved when moved into Overview tab
- Filter parent groups must be selectable (not just labels) to enable "select all in this category" behavior
- Hierarchy data lives in `dim_noc_structure` table in JobForge 2.0 directory -- needs to be loaded and joined with search results

</specifics>

<deferred>
## Deferred Ideas

None -- discussion stayed within phase scope

</deferred>

---

*Phase: 18-profile-page-overhaul*
*Context gathered: 2026-02-06*
