# Phase 9: Vocabulary Foundation - Context

**Gathered:** 2026-02-03
**Status:** Ready for planning

<domain>
## Phase Boundary

Build a term index from JobForge parquet files (abilities, skills, knowledges, work activities) that enables validating any text against NOC vocabulary. This phase delivers the vocabulary index and validation function — it does NOT implement the generation or retry logic that consumes it (that's Phase 12).

</domain>

<decisions>
## Implementation Decisions

### Data Sources
- Reference JobForge parquet files directly at `C:\Users\Administrator\Dropbox\++ Results Kit\JobForge 2.0\data\bronze\`
- Do NOT copy files into JD Builder Lite — demonstrates "goose and golden eggs" architecture (JobForge = gold model, JD Builder Lite = value module)
- Relevant parquet files: `oasis_abilities.parquet`, `oasis_skills.parquet`, `oasis_knowledges.parquet`, `oasis_workactivities.parquet`
- Start with bronze layer (authoritative source), but Claude can evaluate silver/gold layers if metadata quality is better
- GitHub reference: https://github.com/dubedad/JobForge-2.0

### Index Granularity
- Case-insensitive matching (locked — "Coordinate" matches "coordinate")
- Claude's discretion: whether to index full phrases, individual words, or both
- Claude's discretion: stemming vs lemmatization vs exact matching
- Claude's discretion: stop word handling (skip common words like "the", "and", "of")

### Validation Reporting
- MUST return vocabulary coverage percentage (e.g., "85% of words are NOC vocabulary")
- Claude's discretion: whether to list specific non-NOC words
- Claude's discretion: whether to include character positions
- Claude's discretion: whether to suggest replacement words
- Claude's discretion: API endpoint vs Python module only

### Loading Strategy
- Hot reload when parquet files change (locked — useful during development)
- Memory footprint: no concern — demo app, keep it simple, in-memory is fine
- Claude's discretion: eager vs lazy vs background loading
- Claude's discretion: error handling when parquet files unavailable

### Claude's Discretion
- Index granularity (words, phrases, stems)
- Stop word handling
- Replacement suggestions
- API exposure
- Load timing
- Missing file behavior

</decisions>

<specifics>
## Specific Ideas

- "The model is the goose, and the value are the golden eggs which represent workflows that automate HR tasks" — architecture should demonstrate this relationship
- JD Builder Lite consuming JobForge data proves the pattern works

</specifics>

<deferred>
## Deferred Ideas

None — discussion stayed within phase scope

</deferred>

---

*Phase: 09-vocabulary-foundation*
*Context gathered: 2026-02-03*
