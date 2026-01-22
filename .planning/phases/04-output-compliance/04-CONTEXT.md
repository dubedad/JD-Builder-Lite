# Phase 4: Output + Compliance - Context

**Gathered:** 2026-01-22
**Status:** Ready for planning

<domain>
## Phase Boundary

Manager can export a complete, audit-ready job description PDF with compliance metadata that demonstrates conformance with Canada's Directive on Automated Decision-Making. Includes preview before export, Word export option, and full audit trail traced to NOC source and manager decisions.

</domain>

<decisions>
## Implementation Decisions

### PDF Layout & Structure
- Letter portrait page size (standard 8.5x11)
- Style matches OASIS page design (headers, fonts, colors)
- Header: Job title + NOC code (on each page)
- Footer: Page numbers + brief compliance reference (on each page)

### Compliance Metadata Display
- Both footer reference AND detailed appendix
- Footer: Brief compliance citation on each page
- Appendix: Full compliance documentation at end

### Audit Trail Formatting (Directive-Referenced)
- Appendix sections organized by Directive requirement numbers
- Section 6.2.3: Data Sources — ESDC as data steward, NOC as authoritative source, OASIS URLs, retrieval timestamps
- Section 6.2.7: Manager Decisions — Which statements selected under each JD Element, selection timestamps
- Section 6.3.5: Data Quality — NOC version, data currency, direct retrieval from authoritative source

### AI Disclosure
- Inline markers only (small indicator next to AI-generated text)
- No separate "AI-Generated" badges or headers
- AI metadata captured in compliance appendix (model, timestamp, input statements)

### Export Options
- PDF export (primary)
- Word (.docx) export (editable version)

### Create Button Flow
1. Manager clicks "Create"
2. LLM generates General Overview based on selections
3. Preview page displays assembled job description
4. Manager can export to PDF or Word

### Claude's Discretion
- Exact compliance appendix formatting/layout
- PDF generation library choice
- Word document styling details
- Footer compliance citation wording

</decisions>

<specifics>
## Specific Ideas

- PDF must demonstrate compliance with Directive on Automated Decision-Making (TBS Policy ID 32592)
- Reference specific Directive sections (6.2.3, 6.2.7, 6.3.5) to give manager confidence
- Emphasize: ESDC is data steward, NOC data comes DIRECTLY from authoritative source (OASIS)
- Job description must be "auditable" per Directive definition
- Compliance section should address how JD "does not contravene" Directive requirements

## Directive Compliance References
- Section 6.2.3: Input data, source, method of collection, criteria used
- Section 6.2.7: Document decisions made/assisted by automated systems
- Section 6.3.5: Data must be relevant, accurate, up-to-date
- Source URLs:
  - https://www.tbs-sct.canada.ca/pol/doc-eng.aspx?id=32592
  - https://www.canada.ca/en/government/system/digital-government/digital-government-innovations/responsible-use-ai/guide-scope-directive-automated-decision-making.html

</specifics>

<deferred>
## Deferred Ideas

**Note:** Discussion covered UI decisions across multiple phases. The following affect earlier phases and should be incorporated into Phase 2/3 planning updates:

### Phase 2 Updates (Frontend Core UI)
- Search: Keyword only (drop Code/Competency tabs)
- Filters: Job Family, Managerial Level, GC Job Title
- Results: Card + Table view with toggle
- Card content: Example titles (OASIS), GC Example Titles (LLM), Profile name, OASIS code, lead statement, LLM description
- Icons: Simple black icons
- Sort: Matching search criteria only
- Profile header: As OASIS shows (title + NOC code + lead statement + icon)
- Tabs: JD Element tabs (Key Activities, Skills, Effort, Responsibility, Working Conditions)
- Overview content: LLM sentence + all NOC reference data + hierarchy breakdown
- Statement table: All columns (statement, type, title, description, level, provenance)
- Selection: Checkbox per row
- Selections display: Sidebar panel

### Phase 3 Updates (LLM Integration)
- LLM generates GC Example Titles for search result cards
- LLM generates Occupational Profile description for cards
- LLM generates General Overview triggered by "Create" button

</deferred>

---

*Phase: 04-output-compliance*
*Context gathered: 2026-01-22*
