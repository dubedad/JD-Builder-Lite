# Phase 2: Frontend Core UI - Context

**Gathered:** 2026-01-21
**Status:** Ready for planning

<domain>
## Phase Boundary

Interactive display of NOC data organized by JD elements with selection capabilities. Manager views structured NOC data and selects statements for the job description. Creating the AI overview and export are separate phases.

</domain>

<decisions>
## Implementation Decisions

### Layout Structure
- Accordion layout for JD Elements (Key Activities, Skills, Effort, Responsibility, Working Conditions)
- All accordion sections collapsed on initial load
- Draggable section order — managers can reorder JD Element sections
- Desktop only — no mobile/tablet responsiveness required

### Information Density
- Detailed display: statement text + NOC code + source NOC section (e.g., "from Work Characteristics")
- Full text always shown — no truncation of long statements

### Selection Experience
- Checkbox + highlight — selected statements get subtle background color
- Selection counts in accordion headers (e.g., "Key Activities (3 selected)")
- Search box per section — text filtering within each JD Element accordion

### Page Layout
- Info card header: job title, NOC code, link to OASIS source, retrieval timestamp
- Collapsible sidebar for selection summary (all selections grouped by JD Element)
- Sticky bottom action bar — "Generate Overview" button always visible

### Visual Style
- Clean/minimal aesthetic — white backgrounds, subtle borders, professional government-tool look

### Claude's Discretion
- Statement grouping within sections — flat list vs grouped by NOC source section
- Keyboard support level — basic accessibility vs power-user shortcuts
- Loading skeleton design
- Exact spacing, typography, and color choices within clean/minimal style
- Error state presentation

</decisions>

<specifics>
## Specific Ideas

- Professional, government-tool aesthetic — think internal HR applications, not flashy SaaS
- Sidebar should be collapsible to maximize content area when not reviewing selections
- Selection counts in headers give at-a-glance progress without expanding sections

</specifics>

<deferred>
## Deferred Ideas

None — discussion stayed within phase scope

</deferred>

---

*Phase: 02-frontend-core-ui*
*Context gathered: 2026-01-21*
