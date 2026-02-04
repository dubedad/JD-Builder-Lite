# Phase 17: UI Layer - Context

**Gathered:** 2026-02-04
**Status:** Ready for planning

<domain>
## Phase Boundary

User-facing display of occupational group allocation recommendations with evidence, rationale, and provenance chain to authoritative TBS sources. Includes navigation integration (Step 5: Classify) and results display. Quick allocation bypass without validation is out of scope.

</domain>

<decisions>
## Implementation Decisions

### Navigation Integration
- Add "Step 5: Classify" to the existing navigation stepper (Steps 1-4 exist)
- Structure Phase 17 as multiple plans: navigation update, recommendations display, provenance display
- Step 5 access availability before JD completion: Claude's discretion

### Recommendations Display
- Vertical stacked cards, one per recommendation
- Top recommendation (#1) visually distinguished with larger/highlighted card treatment
- At-a-glance info on each card:
  - Group code + name + confidence percentage
  - One-line rationale summary
  - Inclusion/exclusion status indicators
- Expanded card reveals:
  - Full rationale text
  - Evidence quotes from JD
  - TBS definition excerpt
  - Provenance chain

### Confidence Visualization
- Show both progress bar AND color-coded badge (High/Medium/Low)
- Confidence thresholds: Claude's discretion based on matching engine output patterns
- Low confidence warning/guidance: Claude's discretion
- Expandable confidence breakdown showing semantic similarity, labels boost components

### Evidence Highlighting
- Side-by-side split view: recommendation on left, JD with highlights on right
- Multiple evidence quotes linkable simultaneously (all highlights visible at once)
- Highlight visual treatment: Claude's discretion
- Missing evidence handling (fuzzy match failed): Claude's discretion

### Provenance Presentation
- Expandable tree/breadcrumb: Recommendation → Definition → TBS Page
- TBS source link behavior: Claude's discretion
- Archive snapshot date visibility: Claude's discretion
- "Classification Step 1 Complete" next steps presentation: Claude's discretion

### Claude's Discretion
- Step 5 access behavior when JD validation incomplete
- Confidence tier thresholds (High/Medium/Low cutoffs)
- Low confidence visual warning treatment
- Evidence highlight visual style
- Handling evidence quotes that can't be found in JD
- TBS link behavior (new tab vs preview)
- Archive date visibility in provenance
- Next steps guidance after Step 1 complete

</decisions>

<specifics>
## Specific Ideas

- Navigation stepper should feel cohesive with existing Steps 1-4
- Cards should show enough info at a glance for quick scanning, with details on expand
- Side-by-side evidence view allows user to verify quotes against source JD text
- Provenance tree shows audit trail from recommendation back to authoritative TBS source

</specifics>

<deferred>
## Deferred Ideas

- **Quick allocation button** — "Predict Classified Group" button that bypasses JD validation for automated prediction. Noted as potential future feature but out of scope for Phase 17.

</deferred>

---

*Phase: 17-ui-layer*
*Context gathered: 2026-02-04*
