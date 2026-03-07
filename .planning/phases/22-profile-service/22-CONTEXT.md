# Phase 22: Profile Service - Context

**Gathered:** 2026-03-07
**Status:** Ready for planning

<domain>
## Phase Boundary

Serve profile page tabs (Skills, Abilities, Knowledge, Work Activities, Work Context) from JobForge parquet for all 900 covered profiles, with automatic OASIS fallback for tabs that have no parquet coverage (Main Duties / Key Activities, Interests, Personal Attributes, Core Competencies). Provenance metadata in exports distinguishes parquet-sourced from OASIS-sourced sections. Phase 22 does NOT change the search service (Phase 23) or add new tabs.

</domain>

<decisions>
## Implementation Decisions

### Source indicator in UI
- Each profile tab shows a source badge at the **bottom of the tab content** (below the statement list)
- Badge text: **"Source: JobForge"** for parquet-served content, **"Source: OASIS"** for OASIS-served content
- The two badges are **visually distinct** — different colour or styling so users can tell at a glance which source is active
- Claude's discretion: exact colours and styling (must fit existing badge/chip patterns in the UI)

### Fallback behavior
- The source badge is the **only signal** that a fallback occurred — no other UI indication, no error message, no user-visible disruption
- Fallback is considered transparent when the source badge changes from JobForge to OASIS
- Claude's discretion: loading state treatment (spinner vs skeleton — match existing profile page patterns)
- Claude's discretion: double-failure state (both parquet and OASIS fail) — consistent with existing error handling patterns
- Claude's discretion: Main Duties / Key Activities treatment (unconditional OASIS — Claude decides whether to distinguish permanent vs per-profile fallback in the badge or tooltip)

### Provenance format in export
- All four provenance decisions deferred to Claude's discretion:
  - Detail level for parquet entries (source + file path at minimum to satisfy traceability)
  - Granularity (per-section is the natural fit; per-statement only if existing schema already supports it)
  - OASIS format compatibility (extend only if needed for consistency; don't break existing exports)
  - Per-tab labelling in compliance block (Claude judges based on TBS Directive 32592 compliance requirements)

### Claude's Discretion
- CoverageStatus fallback trigger logic: whether EMPTY_VALID triggers OASIS fallback or shows an empty state (Claude determines based on data semantics — whether an empty-but-valid parquet result means the profile truly has nothing, or the data gap warrants a live scrape)
- LOAD_ERROR visibility: Claude determines appropriate log/warning level vs UI treatment for infrastructure failures vs data-gap fallbacks
- CoverageStatus API surface: whether it is exposed in JSON responses to the frontend or kept internal to the service layer
- CoverageStatus caching strategy: per-request evaluation vs startup cache (Claude picks based on parquet update frequency and observed performance characteristics)

</decisions>

<specifics>
## Specific Ideas

- The source badge should make it immediately obvious without reading — colour differentiation (not just text) is the stated intent
- "Source: JobForge" / "Source: OASIS" is the exact wording chosen — not "JobForge 2.0", not "Live OASIS", exactly those strings

</specifics>

<deferred>
## Deferred Ideas

None — discussion stayed within phase scope.

</deferred>

---

*Phase: 22-profile-service*
*Context gathered: 2026-03-07*
