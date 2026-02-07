# Phase 19: Flow and Export Polish - Context

**Gathered:** 2026-02-07
**Status:** Ready for planning

<domain>
## Phase Boundary

Smooth navigation between Builder, Preview, and Classification screens with step indicator, coaching-toned guidance for multi-group classification results, classification data in PDF/DOCX exports, and README update reflecting v4.0 architecture. Creating new screens or adding new classification capabilities are out of scope.

</domain>

<decisions>
## Implementation Decisions

### Navigation flow
- Split layout: "Return to Builder" at top-left, "Classify" and "Export" in a bottom/footer action bar
- Step indicator / breadcrumb showing Builder > Preview > Classify with current step highlighted
- Rename existing "Back to Edit" to "Return to Builder" and reposition to match new nav layout
- Classification results cached until JD changes — user doesn't have to re-classify after navigating away
- When JD is edited after classifying, show stale warning: "JD changed — re-classify for updated results"
- Export available from both Preview and Classification screens
- When exporting from Classification, user can choose what to include (checkboxes: Include JD, Include Classification)

### Multi-group coaching (replaces "Invalid Combination")
- Reframe from "invalid" to "Your JD spans multiple groups — here's how we ranked them by confidence"
- Show both duty alignment percentages AND key duties driving each ranking
- Offer both paths: "Accept the top recommendation" or "Return to Builder to adjust your JD"
- No red styling — coaching tone, not error tone

### Classification in export
- Full detail: recommendations, confidence scores, rationale, evidence quotes, and provenance chain
- Provenance entries hyperlinked to actual TBS directive URLs (clickable in both PDF and DOCX)
- Full audit footer: tool name, version, date generated, data sources used

### README
- Dual audience: quick overview + value proposition for reviewers, then technical details for developers
- Screenshots of key screens (Builder, Preview, Classification, Export)
- Detailed architecture: component diagram, data pipeline, file structure, classification algorithm overview

### Claude's Discretion
- Return-to-Builder state handling (preserve selections, scroll position decisions)
- Button hierarchy (Classify primary vs equal weight with Export)
- Whether step indicator steps are clickable or visual-only
- Whether Export appears as a step in the breadcrumb or stays a side action
- Color scheme for multi-group coaching (replacing red — likely blue/amber informational tones)
- Classification placement in export document (after JD vs separate page)
- How to position compliance context in README

</decisions>

<specifics>
## Specific Ideas

- "It's not even necessarily 'invalid' when a JD spans multiple occ groups — it's just an observation that requires looking at other attributes. The ranking does that with confidence scoring KPIs." — This reframing is central to the coaching UX.
- The confidence scoring already exists — coaching just needs to surface the ranking explanation more clearly.

</specifics>

<deferred>
## Deferred Ideas

None — discussion stayed within phase scope

</deferred>

---

*Phase: 19-flow-and-export-polish*
*Context gathered: 2026-02-07*
