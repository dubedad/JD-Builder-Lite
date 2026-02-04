# Phase 14: Data Layer - Context

**Gathered:** 2026-02-04
**Status:** Ready for planning

<domain>
## Phase Boundary

Scrape DIM_OCCUPATIONAL table from TBS authoritative sources with definitions, inclusions, exclusions. Build a reference data lookup table for occupational group allocation matching. This is data acquisition only — matching logic, API, and UI are separate phases.

**Authoritative Sources:**
- Occupational groups table: https://www.canada.ca/en/treasury-board-secretariat/services/collective-agreements/occupational-groups.html
- Definition pages: Linked from each group in the table
- Allocation guide: https://www.canada.ca/en/treasury-board-secretariat/services/classification/job-evaluation/guide-allocating-positions-using-occupational-group-definitions.html

</domain>

<decisions>
## Implementation Decisions

### Storage Format
- SQLite database (relational, easy joins between groups/inclusions/exclusions)
- Database file location: `data/` directory
- Archive raw HTML from all scraped pages (full audit trail, can re-parse if extraction logic changes)
- Append-only with effective dates (never overwrite, track when each version was valid)

### Provenance for DADM/TBS Compliance
- Full provenance chain including HTTP headers (URL, timestamp, content hash, status, headers)
- Paragraph-level provenance — each inclusion/exclusion statement links to exact source location
- Label and store TBS allocation guide paragraphs as P1, P2, P3... for direct citation in provenance map
- Track human verification events (when a human verified scraped data is correct)

### Refresh Policy
- Manual trigger only (admin/developer runs refresh command — government data changes rarely)
- Content hash comparison (hash each page, only process pages that actually changed)
- Fail explicitly, keep existing data (log error, don't update that group, alert operator)
- Rate limiting: 1 request per second (polite scraping, don't overwhelm government servers)

### Content Scope
- From occupational groups table: Group, Subgroup, Definition link, Qualification standard, Rates of pay (both represented and unrepresented)
- Skip: Job evaluation standard column, Bargaining update column
- From definition pages: Everything available (definition statement, inclusions, exclusions, plus any additional sections/notes/examples)
- Table of Concordance: Scrape (links groups to evaluation standards — needed for DATA-05)
- TBS Allocation Guide: Scrape and label paragraphs (P1, P2, P3...) for provenance map

### DAMA-DMBOK 2.0 Alignment
Per DAMA evaluation, this is a **Master & Reference Data** use case:
- Treat as reference data with stable identifiers (group codes)
- Normalize into master (groups) + child (inclusions/exclusions) entities
- Full lineage from URL to parsed fields
- Validate completeness, accuracy, consistency on every scrape
- Never insert partial or corrupt data

### Claude's Discretion
- Exact SQLite schema design (table names, column types, indexes)
- HTML parsing strategy (BeautifulSoup selectors, error handling)
- Raw HTML archive file organization and naming
- Temp file handling during scrape
- Exact retry logic parameters (count, backoff)

</decisions>

<specifics>
## Specific Ideas

- "I want the provenance to be traceable to DADM and TBS Classification Policy"
- Paragraph labels (P1, P2, P3...) should match the format specified in the requirements for provenance mapping
- Human verification events support DADM human-in-loop requirements
- Content hash enables detecting when TBS updates their pages without notification

</specifics>

<deferred>
## Deferred Ideas

None — discussion stayed within phase scope

</deferred>

---

*Phase: 14-data-layer*
*Context gathered: 2026-02-04*
