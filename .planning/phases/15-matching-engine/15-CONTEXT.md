# Phase 15: Matching Engine - Context

**Gathered:** 2026-02-04
**Status:** Ready for planning

<domain>
## Phase Boundary

OccupationalGroupAllocator that compares job descriptions against TBS occupational group definitions using the prescribed allocation method. Produces ranked top-3 recommendations with confidence scores, rationales, and full policy provenance. Uses Phase 14 data layer (DIM_OCCUPATIONAL). API and UI exposure are separate phases.

</domain>

<decisions>
## Implementation Decisions

### Matching approach
- **Primary purpose extraction:** Combined analysis using Client-Service Results + Key Activities together for fuller picture
- **Definition matching:** Holistic match — compare purpose to full definition as semantic whole (mirrors how classifiers think)
- **Inclusion statements:** Use for shortlisting candidates only, not for scoring or evidence
- **Exclusion statements:** Hard gate — if primary purpose matches an exclusion, group is eliminated entirely
- **Candidate shortlisting:** Hybrid approach — match all groups but boost confidence if labels.csv supports the match
- **Multi-group duties:** Surface the split — show distribution and recommend based on primary, but flag the split (e.g., "40% AS, 35% PM, 25% CS")
- **Threshold:** Minimum 0.3 confidence to appear in top-3 recommendations
- **Borderline positions:** Flag for expert review when top scores are within 10% of each other
- **Current groups only:** Match against active TBS groups only, not legacy/historical
- **Disambiguation rules:** Hybrid — start definition-driven, add explicit rules for documented edge cases (e.g., AP vs TC)
- **Title-duty mismatch:** Use duties for matching, but surface title mismatch as observation (e.g., "Clerk" title with PM-like duties)

### Confidence scoring
- **High confidence (0.85+):** Multi-factor match — definition alignment + inclusions + no exclusion conflicts + labels.csv support
- **Relative scoring:** Show both absolute confidence AND margin indicator showing gap to next best group
- **Match context:** Include contextual indicator — "dominant match" vs "competitive field" vs "only viable option"
- **Component breakdown:** Yes — show transparent breakdown (definition fit, inclusion support, exclusion status)
- **Low confidence warning:** Explicit warning for recommendations scoring 0.3-0.4 (borderline inclusion threshold)
- **Calibration:** Aspirational human alignment — aim for scores reflecting how classifiers would assess, but don't formally calibrate in v4.0

### Rationale generation
- **Explanation format:** Both narrative summary + expandable quotes and evidence
  - Narrative: "This position primarily delivers X, which aligns with Y group"
  - Evidence: Quoted excerpts with context
- **Evidence linking:** All three approaches — text spans, field references (e.g., "Key Activity 3"), and highlighted excerpts
- **Rejected groups:** Full explanation — same detail as positive recommendations, explaining why group was not recommended
- **Provenance:** Full provenance with links to specific TBS page/paragraph where definition comes from

### Edge case handling
- **AP vs TC:** Explicit rules encoding TBS guidance on this specific disambiguation
- **Invalid Combination of Work:** Split recommendation — suggest the JD may need to be split into multiple positions
- **Vague JD content:** Return "Needs Work Description Clarification" with specific questions about what's missing
- **Specialized groups (EX, LC, MD):** Match normally but flag if recommending — these have separate classification processes

### Claude's Discretion
- Subgroup handling (top-level only vs include subgroups) — based on TBS data availability
- Language handling (English only vs bilingual) — based on data availability
- Operational vs admin lens — use TBS guidance to determine approach
- JD field weighting — determine appropriate weights based on classification practice
- labels.csv usage — determine best use of existing duty mappings beyond shortlisting
- Exclusion statement interpretation — determine severity based on statement strength

</decisions>

<specifics>
## Specific Ideas

- "Borderline positions" should trigger human classifier review when scores are within 10%
- Engine should feel like a classification advisor — transparent about its reasoning, not a black box
- Provenance is critical: every decision must trace back to authoritative TBS source
- Split recommendations should be actionable: "This JD describes work that should be 2 positions: [Group A] for X duties, [Group B] for Y duties"

</specifics>

<deferred>
## Deferred Ideas

None — discussion stayed within phase scope

</deferred>

---

*Phase: 15-matching-engine*
*Context gathered: 2026-02-04*
