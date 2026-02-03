# Phase 12: Constrained Generation - Context

**Gathered:** 2026-02-03
**Status:** Ready for planning

<domain>
## Phase Boundary

Few-shot styling with vocabulary validation and retry. This phase implements the generation mechanics: triggering styling, validating output against NOC vocabulary, retry logic on failure, fallback to original, and user controls for regeneration. Display format and provenance schema are locked by Phase 11.

</domain>

<decisions>
## Implementation Decisions

### User Controls for Styling
- Per-statement toggle to opt out of styling and use original NOC statement
- Styling trigger, granularity (per-statement/section/whole JD), and manual editing: Claude's discretion

### Retry & Fallback UX
- Progress indicator during styling: Claude's discretion
- Retry visibility (hidden vs visible count): Claude's discretion
- Fallback communication method: Claude's discretion
- Retry limit: Claude's discretion

### Regeneration Workflow
- Regenerate UI pattern (inline icon vs context menu): Claude's discretion
- Version history: Locked by Phase 11 — full version history tracked, user can revert
- Batch regeneration option: Claude's discretion
- Regeneration variation (different examples vs same prompt): Claude's discretion

### Claude's Discretion
- Whether styling is manual trigger or auto-on-add
- Styling granularity (per-statement, per-section, or whole JD)
- Whether styled text is manually editable
- Loading/progress UX during generation
- Retry count and visibility
- Fallback notification method (toast, inline, both)
- Regenerate button placement
- Whether batch regeneration adds value
- How to vary regeneration output

</decisions>

<specifics>
## Specific Ideas

- Phase 11 locked display as expandable/collapsible original with styled primary
- Phase 11 locked confidence as color-coded dots (green/yellow/red)
- Phase 11 locked AI label as "AI-Styled using Job Description Samples"
- User explicitly wants per-statement opt-out toggle to use original NOC statement

</specifics>

<deferred>
## Deferred Ideas

None — discussion stayed within phase scope

</deferred>

---

*Phase: 12-constrained-generation*
*Context gathered: 2026-02-03*
