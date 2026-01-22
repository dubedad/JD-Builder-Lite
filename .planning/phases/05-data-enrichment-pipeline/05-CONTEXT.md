# Phase 5: Data Enrichment Pipeline - Context

**Gathered:** 2026-01-22
**Status:** Ready for planning

<domain>
## Phase Boundary

Backend loads guide.csv at startup and enriches all profile responses with:
- Category definitions (from guide.csv)
- Statement descriptions (OASIS label lookups from guide.csv)
- Proficiency levels with scale meanings
- Work Context filtering (Responsibilities, Effort, Other)
- Reference NOC attributes (example titles, interests, career mobility, job requirements, personal attributes)

This phase handles data transformation/enrichment on the backend. Frontend rendering of enriched data is Phase 6.

</domain>

<decisions>
## Implementation Decisions

### Data Structure & API Response

- **Enrichment organization:** Claude's discretion on nested vs flat structure based on existing codebase patterns
- **Raw + enriched proficiency:** Claude decides whether to include both raw number and display format
- **Reference attributes:** Grouped under single `reference_attributes` object (not flat at profile level)
- **NOC hierarchy structure:** Claude determines nested vs flat based on frontend needs
- **Category definitions:** Return once per JD Element section (not repeated with every statement)
- **Empty reference fields:** Claude determines whether to use empty arrays, null, or omit

### Lookup & Matching

- **Primary lookup key:** OASIS element ID
- **Fallback key:** OASIS attribute text title (alphabetical key, NOT description column)
- **Case sensitivity for title matching:** Claude determines based on data quality observations
- **Missing lookup handling:** LLM imputation with confidence tracking
  - Source indicator distinguishes guide_csv (higher confidence) from llm_imputed
  - Confidence scores use 0.0-1.0 decimal scale
  - Claude decides whether to cache imputations or generate each time

### Timestamps & Logging

- **Include timestamps:** Yes - track when guide.csv loaded and when LLM imputation occurred
- **Match statistics logging:** Yes - log how many ID matches, title fallbacks, and LLM imputations
- **Log destination:** Claude determines (console, file, or API response metadata)

### Proficiency Display Format

- **Star rating scale:** 5 stars maximum
- **Category-specific scales:** Some OASIS categories use 3-point scale - display 3 stars max (not mapped to 5)
- **Scale meanings source:** Hardcode from official OASIS documentation (https://open.canada.ca/data/en/dataset/eeb3e442-9f19-4d12-8b38-c488fe4f6e5e)
- **Missing proficiency:** Display "No rated level" text
- **Include scale max:** Yes - return `{level: X, max: Y, label: '...'}` so frontend knows the scale
- **Return format:** Both numeric level AND scale meaning label
- **Work Context ratings:** Also use star ratings for dimension ratings (Frequency, Duration, etc.)

### Statement Ordering

- **Filter 0-level statements:** Yes - exclude all statements with proficiency level 0
- **Sort order:** Highest to lowest proficiency within each JD Element heading
- **Cross-category sorting:** Sort ALL statements by proficiency regardless of OASIS category within a heading
- **Tiebreaker:** Claude determines secondary sort when proficiency levels equal

### Work Context Classification

- **Responsibilities patterns:** 'responsib', 'decision'
- **Effort patterns:** 'effort'
- **Additional patterns:** Claude may propose semantic matches based on Work Context data analysis
- **Unmatched statements:** Route to "Other Work Context" section (labeled exactly as "Other Work Context")
- **Pattern matching scope:** Check both statement title AND enriched description (from guide.csv)
- **Filter 0-rated:** Yes - exclude Work Context items with rating 0
- **Sorting within sections:** Sort by rating (highest first)
- **Include routing reason:** Yes - add classification_reason field for debugging/transparency
- **Case sensitivity:** Claude determines
- **Conflict resolution (matches both):** Claude determines priority
- **Empty section handling:** Claude determines whether to show or hide

### Reference Attributes Structure

- **Fields to include:** Claude determines useful fields based on JD needs
- **Career mobility format:** Structured with NOC codes: `[{title: '...', noc_code: '...'}, ...]`
- **Interests format:** Name with description: `[{name: '...', description: '...'}]`
- **Job requirements:** Structured by type: `{education: [...], certifications: [...], licenses: [...]}`
- **Example titles format:** Claude determines array vs comma-separated
- **Personal attributes format:** Claude determines simple list vs categorized
- **Timestamps:** Claude determines granularity

### Claude's Discretion

- Nested vs flat enrichment structure
- Whether to include raw proficiency alongside enriched
- Caching strategy for LLM imputations
- Source tracking granularity (per-field vs per-statement)
- Log destination for match statistics
- Case sensitivity for pattern matching
- Conflict resolution when Work Context matches both Responsibilities and Effort
- Empty section handling
- Tiebreaker for equal proficiency levels
- Empty reference attribute handling (empty array, null, or omit)
- Work Context dimension type display (prefix vs suffix vs separate field)
- Whether to include original OASIS question text for Work Context

</decisions>

<specifics>
## Specific Ideas

- Scale meanings must come from official OASIS documentation at https://open.canada.ca/data/en/dataset/eeb3e442-9f19-4d12-8b38-c488fe4f6e5e
- LLM-imputed descriptions must be clearly marked as lower confidence than guide.csv lookups
- Work Context routing should include classification_reason for transparency (e.g., "matched: responsib in title")
- Job requirements should be structured to distinguish education, certifications, and licenses
- Career mobility paths should include NOC codes where available for cross-referencing

</specifics>

<deferred>
## Deferred Ideas

None - discussion stayed within phase scope

</deferred>

---

*Phase: 05-data-enrichment-pipeline*
*Context gathered: 2026-01-22*
