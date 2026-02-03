# Phase 13: Export Enhancement - Context

**Gathered:** 2026-02-03
**Status:** Ready for planning

<domain>
## Phase Boundary

PDF/DOCX exports include styled statements with dual-format display and compliance metadata. This phase extends existing export infrastructure (Phase 7) to render styled content using display patterns locked by Phase 11. Export format, file naming, and error handling carry forward from Phase 7.

</domain>

<decisions>
## Implementation Decisions

### Inherited from Phase 7
- Export dropdown menu pattern (single button → PDF/Word options)
- Exact visual match between PDF and DOCX
- File naming format: `{NOC code} - {Title} - {date} - Job Description.{ext}`
- Compliance appendix structure with source attribution
- Page setup: Letter, 1" margins, matching headers/footers

### Inherited from Phase 11
- Dual-format display: styled statement primary, original collapsible
- Confidence indicator: color-coded dots (green/yellow/red)
- AI disclosure label: "AI-Styled using Job Description Samples"
- Vocabulary audit content: NOC terms used, vocabulary coverage
- Generation metadata: confidence scores, retry counts

### Claude's Discretion
- Static document representation of expandable/collapsible original (stacked, footnote, or appendix)
- Vocabulary audit format (summary stats vs detailed breakdown)
- Placement of vocabulary audit and generation metadata (existing appendix vs new section)
- How confidence dots translate to static format (colored circles, text labels, or symbols)

</decisions>

<specifics>
## Specific Ideas

No specific requirements — open to standard approaches that match existing export quality.

</specifics>

<deferred>
## Deferred Ideas

None — discussion stayed within phase scope

</deferred>

---

*Phase: 13-export-enhancement*
*Context gathered: 2026-02-03*
