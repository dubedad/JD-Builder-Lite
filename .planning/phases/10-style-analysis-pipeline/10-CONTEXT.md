# Phase 10: Style Analysis Pipeline - Context

**Gathered:** 2026-02-03
**Status:** Ready for planning

<domain>
## Phase Boundary

**REVISED SCOPE:** This phase does NOT include user-facing upload UI or profile management.

Phase 10 delivers **style knowledge preparation**: analyzing provided example JDs to document writing patterns and build few-shot examples for the generation prompts. The style learning happens during development, not at runtime.

**Removes from original roadmap:**
- PDF/DOCX upload UI
- Runtime file parsing
- User-selectable style profiles
- Session persistence for profiles

**Delivers instead:**
- Analysis of example JD corpus → documented style patterns
- Few-shot examples for constrained generation prompts
- Style rules as code constants for runtime use

</domain>

<decisions>
## Implementation Decisions

### Source corpus
- Example JDs located at: `Examples of Job Descriptions/` (18 files, mostly DND PDFs)
- Claude evaluates quality and weights examples accordingly
- No user-provided examples at runtime

### Style characteristics to capture
- Sentence structure: verb-first phrasing, length, complexity patterns
- Vocabulary patterns: recurring words/phrases in professional JDs
- Section formatting: content organization, heading styles, bullet conventions

### Output artifacts
- Style rules documented in `.planning/` for human reference
- Key patterns implemented as code constants in `src/` for runtime use
- Both documentation and code — not one or the other

### Few-shot examples
- Claude determines optimal count based on pattern coverage
- Built from analysis of the example corpus
- Become part of generation prompts in Phase 12

### Claude's Discretion
- Number of few-shot examples (likely 3-10 based on pattern variety)
- Quality weighting of source examples
- Whether to expose style rules in UI (likely hidden — users see styled output, not rules)

</decisions>

<specifics>
## Specific Ideas

- "We are just training you in how to write a more 'real' job description using the most authoritative language possible"
- Style learning is development-time activity, not runtime feature
- Goal is JDs that "sound more like typical 'real' job descriptions"

</specifics>

<deferred>
## Deferred Ideas

None — discussion clarified scope rather than expanding it.

**Note:** Original roadmap requirements (STYLE-01 through STYLE-07) need revision to match the new scope. User upload features should be removed from REQUIREMENTS.md.

</deferred>

---

*Phase: 10-style-analysis-pipeline*
*Context gathered: 2026-02-03*
