# Phase 3: LLM Integration - Context

**Gathered:** 2026-01-21
**Status:** Ready for planning

<domain>
## Phase Boundary

AI-generated General Overview based on manager's selections. The LLM creates a summary paragraph informed by the selected NOC statements. This phase handles generation, display, and provenance tracking. PDF export is Phase 4.

</domain>

<decisions>
## Implementation Decisions

### Generation Trigger & Flow
- Automatic generation after manager confirms selections
- Review screen shows all selections first, then manager confirms to trigger generation
- Unlimited regeneration attempts allowed
- Streaming text display during generation (word-by-word as it arrives)

### LLM Provider & Prompt Design
- OpenAI API with GPT-4o model
- Input statements grouped by JD Element in prompt (Key Activities: [...], Skills: [...], etc.)
- Include job context: job title, NOC title (5-digit code), full Occupation code (NOC with .XX suffix)
- Target output: medium length (1 paragraph, 4-6 sentences)

### Output Presentation
- Generated text is fully editable by manager (textarea)
- "AI Generated" badge/tag displayed above the overview section
- If manager edits text, mark as "AI-Generated (Modified)" — don't store original separately

### Provenance Tracking
- Full provenance recorded: model name, timestamp, input statement IDs, prompt template version
- Storage: in-memory only (kept in session state until PDF export)
- Only final accepted version recorded (regeneration attempts not tracked)

### Claude's Discretion
- Exact prompt wording and system message
- Streaming implementation details
- Error handling for API failures
- Review screen layout

</decisions>

<specifics>
## Specific Ideas

- Streaming gives immediate feedback that generation is happening
- Full editability means manager has final control over text
- Badge-style AI attribution is visible but not intrusive

</specifics>

<deferred>
## Deferred Ideas

None — discussion stayed within phase scope

</deferred>

---

*Phase: 03-llm-integration*
*Context gathered: 2026-01-21*
