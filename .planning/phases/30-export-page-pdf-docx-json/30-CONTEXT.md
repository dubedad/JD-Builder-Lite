# Phase 30: Export Page + New PDF/DOCX/JSON - Context

**Gathered:** 2026-03-13
**Status:** Ready for planning

<domain>
## Phase Boundary

A new Export page where users download their completed JD as PDF, Word, or JSON — all using a restructured, compliance-first format with provenance tracing. The page displays a scrollable JD preview, three compliance summary cards, optional export options, and three download buttons.

</domain>

<decisions>
## Implementation Decisions

### Export page layout
- JD preview card shows the full JD content, scrollable — all sections rendered as they'll appear in the PDF
- Three compliance summary cards (DAMA DMBOK, TBS Directives, Full Lineage): Claude's discretion on card content — surface whatever data is available from the session
- Export options ("Include provenance annex" / "Include audit trail" checkboxes) sit above the download buttons as a clearly labeled "Export Options" group
- Download buttons (PDF, Word, JSON) sit below the export options group, above the JD preview card — in a toolbar row

### PDF/DOCX section content
- Source tags in "Key Duties and Responsibilities": coloured pill badges next to each item (same visual style as UI pills)
- "Data Provenance & Compliance" section contains all three: Policy Provenance table + DADM compliance attestation paragraph + DAMA DMBOK data quality summary
- Policy Provenance table structure: Claude's discretion — determine columns based on what data is available in the session
- DOCX styling: Claude's discretion — match what's achievable with python-docx (same sections as PDF, native Word styles)

### JSON audit trail structure
- Top-level structure: Claude's discretion — design for clean consumption by downstream HR systems (API payload intent)
- Primary purpose: API payload for downstream systems — clean schema, no UI-specific fields
- Each selected statement includes: full text + source + ID (self-contained, no external lookup needed)
- AI-generated Position Overview included with full AI metadata: model name, prompt version, and generation timestamp

### Compliance checkboxes behavior
- "Include provenance annex": appends full provenance annex pages at the end of the PDF/DOCX (does not affect inline source tags)
- "Include audit trail": appends a chronological action log section to the PDF/DOCX (search performed, profile loaded, AI generation triggered, etc.)
- Checkbox effect on JSON: Claude's discretion — determine whether JSON is always full or respects the checkboxes
- Default state of checkboxes on page load: Claude's discretion — pick the sensible default for a government compliance tool

### Claude's Discretion
- Compliance summary card content (what metrics/badges to show)
- Policy Provenance table column structure
- DOCX styling and formatting approach
- JSON top-level schema design
- Whether JSON respects checkbox state or always exports everything
- Default checkbox state on load
- Inline source tags always present vs. gated by provenance annex checkbox

</decisions>

<specifics>
## Specific Ideas

- Pill badge source tags in PDF: should visually match the UI pills used throughout the app
- JSON is intended as an API payload for HR systems — should be clean, no UI-specific internal state fields
- Provenance annex: extra pages appended at end (not inline modification)
- Audit trail: chronological log of user actions, not a data dump

</specifics>

<deferred>
## Deferred Ideas

None — discussion stayed within phase scope.

</deferred>

---

*Phase: 30-export-page-pdf-docx-json*
*Context gathered: 2026-03-13*
