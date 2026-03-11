# Phase 27: Build Page Redesign - Context

**Gathered:** 2026-03-11
**Status:** Ready for planning

<domain>
## Phase Boundary

Redesign the Build page UI to match the JobForge v5.1 reference prototype. Covers: occupation header card, tab icons + section description boxes, Core Competencies checkboxes, Key Activities dual-list layout, and level-grouped item display (Abilities, Effort, Responsibility). Navigation bar, Preview modal, and Selections drawer are Phase 28.

</domain>

<decisions>
## Implementation Decisions

### Tab icons + section description boxes
- Icon library: Claude's discretion — use whatever icon library is already present in the app; pick semantically appropriate icons per tab
- Description box content: Extract exact text from v5.1 reference screenshots — screenshots are authoritative spec
- Description box presence per tab: Match screenshots (some tabs may have a box, others may not)
- Description box position within tab: Match screenshots (likely top of tab content area, before items)

### Core Competencies selection behavior
- Select All control: Match screenshots to determine if present and its placement
- Row highlight on selection: Checkbox state only — no background tint on the row when checked
- Inline sub-descriptions: Yes — each competency shows a brief description below its label (label + sub-description layout)
- Selection storage: Claude's discretion — integrate competency selections into the existing selections architecture in whatever way makes the most sense architecturally

### Level badge color scheme (Abilities, Effort, Responsibility tabs)
- Colors: Extract from v5.1 reference screenshots — screenshots are authoritative spec
- Level scheme consistency across tabs: Researcher should verify — check the data structure and screenshots to determine whether Abilities/Effort/Responsibility share a unified level system or each has its own levels
- Item sub-descriptions: Every item has a sub-description shown inline below its label — no items are label-only
- Item selectability: Match screenshots to determine if items in level-grouped tabs are selectable or read-only

### Key Activities tab structure
- Visual separator between Main Duties and Work Activities: Bold section headers (e.g., "Main Duties" heading above first list, "Work Activities" heading above second list), possibly with a horizontal rule
- Selectability: Both Main Duties and Work Activities items are selectable — users can pick individual items from both lists
- Item inline sub-descriptions: Yes — each item shows a brief description below its text (same pattern as other tabs)
- Select All: Per section — separate Select All toggle for Main Duties and a separate one for Work Activities

### Claude's Discretion
- Icon selection (which specific icon per tab) — use semantically appropriate icons from the app's existing library
- Core Competencies selection storage architecture — integrate naturally with existing selections mechanism
- Exact level badge colors if screenshots are ambiguous — use a sensible low/medium/high color gradient (e.g. green/yellow/red or teal/blue/navy)

</decisions>

<specifics>
## Specific Ideas

- The v5.1 reference prototype is the authoritative visual spec. Screenshots are in `.planning/ui-walkthrough-v5.1/` — researcher should read all relevant ones before planning
- "Match screenshots" was the answer for several visual/layout questions — researcher must extract exact layout, text, and colors from those screenshots rather than guessing

</specifics>

<deferred>
## Deferred Ideas

None — discussion stayed within phase scope.

</deferred>

---

*Phase: 27-build-page-redesign*
*Context gathered: 2026-03-11*
