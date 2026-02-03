# Phase 11: Provenance Architecture - Context

**Gathered:** 2026-02-03
**Status:** Ready for planning

<domain>
## Phase Boundary

Extended audit trail schema for styled content with differentiated AI disclosure. This phase defines how styled variants link to source NOC statements, how AI involvement is disclosed, and what metadata supports compliance. Generation implementation is Phase 12; this phase establishes the schema.

</domain>

<decisions>
## Implementation Decisions

### AI Disclosure Labels
- Styled content labeled: "AI-Styled using Job Description Samples"
- Visual treatment: Subtle indicator only (small icon or footnote marker, no color coding)
- Disclosure location: Inline with each statement
- Fallback statements (when styling fails): Marked as "Original NOC"

### Audit Trail Structure
- Styled content shown with expandable/collapsible original NOC statement
- PDF/DOCX exports: Footnotes per statement linking to original NOC
- Full version history tracked (all generated variants kept for audit)
- Users can revert to any previous styled version from history

### Vocabulary Audit Display
- Each styled statement shows: List of NOC terms used AND coverage percentage
- Non-NOC words (edge cases): Highlighted in warning color
- Terms show their NOC category (skill, ability, knowledge, work activity)
- Audit location: Both per-section summary AND full compliance appendix

### Generation Metadata
- Confidence scores: Visible to users as color-coded dot (green/yellow/red based on thresholds)
- Retry count: Tooltip/details (hidden by default, visible on hover or expand)
- Generation timestamp: Captured and displayed for each styled statement

### Claude's Discretion
- Exact color palette for confidence indicators
- Threshold values for green/yellow/red confidence levels
- Schema field naming conventions
- Version history storage format

</decisions>

<specifics>
## Specific Ideas

- Label explicitly references "Job Description Samples" to show the styling source
- Collapsible original statements keep the UI clean while maintaining full traceability
- Color-coded confidence dots provide at-a-glance quality indication without numeric clutter
- Per-section vocab summaries give quick compliance check; appendix provides full audit trail

</specifics>

<deferred>
## Deferred Ideas

None — discussion stayed within phase scope

</deferred>

---

*Phase: 11-provenance-architecture*
*Context gathered: 2026-02-03*
