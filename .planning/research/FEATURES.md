# Feature Research: v5.0 JobForge 2.0 Integration

**Domain:** Local-parquet-first NOC search and profile experience
**Researched:** 2026-03-06
**Milestone:** v5.0 JobForge 2.0 Integration
**Confidence:** HIGH (based on codebase analysis, JOBFORGE-DATA-REQUIREMENTS.md, UAT-FINDINGS.md)

---

## Context: What Changes with Local Parquet

The current architecture makes **two live HTTP requests per user action**:

1. `scraper.search(query)` — hits `noc.esdc.gc.ca/OaSIS/OaSISSearchResult`, returns HTML, parsed by BeautifulSoup
2. `scraper.fetch_profile(code)` — hits `noc.esdc.gc.ca/OaSIS/OaSISOccProfile`, returns HTML, parsed again

Both calls have `REQUEST_TIMEOUT = 60` seconds configured. Both go out over the public internet to a government site with no public API, requiring SSL certificate bypassing (`verify=False`). Both return HTML that gets parsed with fragile CSS selectors, with fallback selectors as a safety net.

The v5.0 integration replaces these two live calls with reads from local JobForge 2.0 gold parquet files. The parquet files are already partially used: `labels_loader.py` reads 6 gold parquet files and 2 source CSVs at startup. The `vocabulary/index.py` reads 4 bronze parquet files at startup. The `matching/` service uses the DIM_OCCUPATIONAL SQLite database. v5.0 extends this existing pattern to cover search and profile data.

### Current Hybrid State (What Already Reads Parquet)

| Service | Parquet Source | Data Provided |
|---------|---------------|---------------|
| `labels_loader.py` | gold: element_labels, element_example_titles, element_exclusions, element_employment_requirements, element_workplaces_employers, oasis_workcontext | Labels, titles, exclusions, employment requirements, workplaces, work context |
| `vocabulary/index.py` | bronze: oasis_abilities, oasis_skills, oasis_knowledges, oasis_workactivities | Vocabulary terms for style constraint |
| `matching/` | SQLite: occupational.db | OG allocation (v4.0 classification) |

### What Still Requires Live OASIS Scraping

| Data | Used For | Search | Profile |
|------|----------|--------|---------|
| Search results (NOC codes, titles, lead statements, TEER) | Search result cards | YES | — |
| Skills, Abilities, Knowledge, Work Activities with scores | Profile tabs | — | YES |
| Main Duties | Key Activities tab | — | YES |
| NOC hierarchy (broad category, sub-major, minor group) | Search cards, filters | YES | YES |
| Personal Attributes | Profile reference | — | YES |
| Interests (Holland codes) | Profile reference | — | YES |
| Core Competencies | Profile reference | — | YES |

---

## Feature Landscape

### Table Stakes (Must Have for This Integration Milestone)

Features required to call v5.0 "done." Missing these means OASIS scraping was not meaningfully replaced.

| Feature | Why Expected | Complexity | Data Dependency | Current OASIS Equivalent |
|---------|--------------|------------|-----------------|--------------------------|
| **Search from parquet (dim_noc + element_*)** | Core replacement goal — OASIS search is the primary pain point: slow, fragile, network-dependent | MEDIUM | `dim_noc` (must exist in gold) | `scraper.search()` + `parser.parse_search_results_enhanced()` |
| **Profile statements from parquet (oasis_skills, oasis_abilities, oasis_knowledges, oasis_workactivities)** | Profile page is the main user surface; all statement tabs must render | MEDIUM | 4 oasis_* parquet files (already in gold) | `scraper.fetch_profile()` + `parser.parse_profile()` enrichment pipeline |
| **Main Duties / Key Activities from parquet** | First tab users see; must not be empty | LOW | `element_main_duties` (must exist in gold) | Scraped from OASIS HTML main duties section |
| **Lead statement from parquet** | Used in search cards and profile header | LOW | `element_lead_statement` (must exist in gold) | Scraped from OASIS HTML |
| **NOC hierarchy from parquet (dim_noc: TEER, broad_category, title)** | Used in search result filters (sub-major, minor group) and profile header | LOW | `dim_noc` with full hierarchy columns | Scraped from OASIS HTML, derived in `api.py` |
| **Data exploration inventory before replacement** | v5.0 starts with discovery — commit to replacement scope only after confirming what's actually in the parquet files | LOW | Inventory of all gold parquet files | Not applicable — new requirement |
| **Graceful OASIS fallback for missing data** | Some parquet tables may have gaps; users cannot get blank screens | MEDIUM | Conditional: parquet first, OASIS if absent | Not applicable — current state is OASIS-only |
| **Provenance metadata updated for parquet source** | TBS Directive requires source attribution; switching from OASIS URL to parquet file path + version | LOW | Parquet schema includes `_source_file`, `_ingested_at`, `_batch_id` columns | `SourceMetadata` model currently uses `profile_url` pointing to noc.esdc.gc.ca |

### Differentiators (Features Parquet Enables That OASIS Scraping Cannot)

These features are technically impossible or severely degraded with live scraping. Local parquet is the prerequisite.

| Feature | Value Proposition | Complexity | Data Dependency | Why OASIS Cannot Do This |
|---------|-------------------|------------|-----------------|--------------------------|
| **Full-text search across all NOC attributes** | Current OASIS search only matches on unit group titles. "Data engineer" misses "database analysts" entirely (UAT S1-12). Local parquet enables matching across lead statements, main duties, example titles, labels, workplaces — all attributes simultaneously. | MEDIUM | `element_*` tables, `oasis_*` tables all queryable locally | OASIS search algorithm is black-box; JD Builder has no control; search only hits OASIS's own index |
| **Instantaneous search response** | HTTP round-trips to noc.esdc.gc.ca take 3-15 seconds observed in practice. Local parquet + pandas filtering is sub-100ms. Users stop waiting and start trusting the tool. | LOW | Any local parquet with NOC data | Every search requires network round-trip to live government site |
| **Search that matches example titles (NOC level 7)** | "Project manager" should match NOC units where "Project Manager" is an example title under a label, not just a unit group title (UAT S1-03). Parquet has `element_example_titles` queryable as a JOIN. | LOW | `element_example_titles` (already in gold) | OASIS search does not expose hierarchy-level matching to JD Builder |
| **Match rationale specifying NOC hierarchy level** | UAT S1-03 explicitly requests: "Unit Group match", "Unit Group Label match", "Example Title match" — three specificity tiers. Requires knowing which table the match came from. | LOW | `element_labels`, `element_example_titles` queryable separately | With OASIS, JD Builder receives one HTML page; cannot distinguish where in the NOC hierarchy the match occurred |
| **Matching search criteria displayed on cards** | UAT S1-04: Show the actual matched content from each NOC attribute on the result card. Parquet JOIN lets JD Builder retrieve matched text snippets per attribute. | MEDIUM | All `element_*` and `oasis_*` tables | OASIS HTML search results do not return attribute-level match data |
| **Deterministic NOC-to-OG pre-filtering for classification** | UAT S5-04: Classification currently runs semantic matching against all 426 OG groups. Parquet `bridge_noc_og` lets the system instantly narrow to 2-5 candidate OGs via SQL JOIN before any LLM call fires. Eliminates most of the classification latency. | MEDIUM | `bridge_noc_og` (must exist in gold) | Bridge table data does not exist in OASIS HTML |
| **Offline operation** | App works without internet. This matters for demos in government environments with restricted network access. | LOW | All data in local parquet | Impossible — every search and every profile load requires live noc.esdc.gc.ca availability |
| **Resilience to OASIS site outages and HTML restructuring** | The OASIS site has changed HTML structure before, silently breaking CSS selectors. Local parquet is immutable until the next JobForge refresh cycle. | LOW | Any local parquet | Every structural change to noc.esdc.gc.ca HTML breaks the parser |
| **Search across JobForge job_architecture table** | UAT S1-06: Users can search by Job Title, Job Family, Job Function, Managerial Level from the GC-specific job architecture data — not available anywhere in OASIS | MEDIUM | `job_architecture` (must exist in gold) | This data does not exist in OASIS at all |
| **Consistent score filtering (>20% cutoff)** | Search currently filters out results below 20% relevance (UAT S1-01 fix already shipped). With local search, relevance scoring runs against richer attribute data, reducing false positives without needing the cutoff as a crutch. | LOW | All local parquet for richer scoring | OASIS returns all results; JD Builder applies a post-hoc filter; many low-quality results still surface |

### Anti-Features (Deliberately NOT Build in v5.0)

Features that seem natural next steps but are out of scope or harmful for this milestone.

| Anti-Feature | Why Requested | Why to Avoid in v5.0 | What to Do Instead |
|--------------|---------------|---------------------|-------------------|
| **Remove OASIS scraping entirely** | "We have local data, delete the old code" | Some data still has gaps in gold parquet (Interests, Personal Attributes as CSVs, Core Competencies unresolved). Removing fallback before data exploration confirms 100% coverage would break the profile page for affected fields. | Keep OASIS scraper as fallback. Mark it clearly as legacy. Remove per-field as gold coverage is confirmed during data exploration phase. |
| **Re-implement the full OASIS search algorithm** | Tempting to replicate exactly what OASIS does for backward compatibility | OASIS's algorithm is unknown and its quality is the problem. The point of local search is to do better, not to replicate the same limitations. Attempting parity wastes effort. | Build a better local search: full-text across all attributes, NOC hierarchy-aware scoring, sorted by relevance tiers (100/95/85/60/50). |
| **Build a full-text search engine (Elasticsearch, etc.)** | "We have all this data, let's index it properly" | Scope explosion. This is a local Flask demo. pandas DataFrame filtering with index operations is fast enough for NOC's ~500 unit groups. Adding an external search engine adds a runtime dependency and deployment complexity. | Use pandas + simple string matching + optional TF-IDF scoring. The vocabulary index already demonstrates this pattern at startup. |
| **Real-time JobForge data sync** | "Keep parquet files always current" | JD Builder is a local demo, not a production ETL system. JobForge has its own medallion pipeline. Coupling JD Builder to live ETL processes adds fragility without user-visible benefit. | Set parquet files as static at startup. Document the JobForge version in provenance metadata. Refresh on next JobForge data drop, not continuously. |
| **Multi-source search (NOC + CAF + O*NET simultaneously)** | UAT S1-08 requests CAF taxonomy as an additional search source | This is a v6.0 SEED item (S1-08). Adding multi-taxonomy search in v5.0 before local NOC search is working creates two unsolved problems simultaneously. | v5.0 = NOC search from parquet working reliably. CAF and O*NET in a future milestone once the parquet pattern is proven. |
| **Streaming search results** | "Show results as they load" | With local parquet, results load in <100ms. Streaming is engineering complexity for a non-problem. | Return all results in a single JSON response. |

---

## Feature Dependencies

```
[Data Exploration Phase]
  |
  +--inventories--> confirms which gold parquet tables exist and have data
  |
  +--unblocks--> [Search from Parquet]
  |                |
  |                +--requires--> dim_noc, element_lead_statement, element_labels
  |                |              element_example_titles, element_main_duties
  |                |
  |                +--enables--> Full-text search across all attributes
  |                +--enables--> Match rationale with NOC hierarchy level
  |                +--enables--> Matching criteria displayed on cards
  |
  +--unblocks--> [Profile from Parquet]
  |                |
  |                +--requires--> oasis_skills, oasis_abilities, oasis_knowledges,
  |                |              oasis_workactivities, oasis_workcontext
  |                |              (all already in gold per JOBFORGE-DATA-REQUIREMENTS.md)
  |                |
  |                +--enables--> Sub-100ms profile load
  |                +--enables--> Offline operation
  |
  +--unblocks--> [OASIS Fallback Scope Decision]
                   |
                   +--determines--> Which fields still need OASIS as fallback
                   +--determines--> Timeline for removing scraper calls field-by-field

[Provenance Metadata Update]
  |
  +--requires--> parquet schema column inventory (_source_file, _ingested_at, _batch_id)
  +--extends--> existing SourceMetadata model
  +--required-for--> TBS Directive compliance (source attribution must remain valid)

[bridge_noc_og in gold]
  |
  +--unblocks--> Deterministic NOC-to-OG pre-filtering (UAT S5-04)
  +--enables--> Classification speed improvement (2-3x faster)
```

### Dependency Notes

- **Data exploration is Phase 1, not optional.** The milestone description explicitly calls for a data exploration phase before committing to replacement scope. Several features above are conditional on what the exploration finds.
- **oasis_* parquet tables are already confirmed in gold** per JOBFORGE-DATA-REQUIREMENTS.md: skills, abilities, knowledges, workactivities, workcontext. Profile statements (the main user-facing data) can be replaced immediately.
- **element_* tables are confirmed in gold** per JOBFORGE-DATA-REQUIREMENTS.md: lead_statement, main_duties, labels, example_titles, exclusions, employment_requirements, workplaces_employers. Search data can be replaced immediately.
- **Interests and Personal Attributes** exist as source CSVs (not gold parquet). The `labels_loader.py` already reads them. This is a gap in the gold layer but not a blocker — the CSVs work and are loaded today.
- **Core Competencies** has no identified source yet. Remains OASIS fallback or blank until resolved separately.

---

## v5.0 Milestone Scope Definition

### Launch With (v5.0 Done)

What makes v5.0 "complete":

- [ ] Data exploration complete — all gold parquet tables inventoried, columns documented, row counts verified
- [ ] Search reads from parquet (`dim_noc` + `element_*`) instead of live OASIS scraping
- [ ] Search results include lead statement, TEER, broad category from parquet (matches current card data)
- [ ] Full-text search across title + lead statement + example titles (minimum — enables S1-12 fix)
- [ ] Profile tabs read from parquet (`oasis_skills`, `oasis_abilities`, `oasis_knowledges`, `oasis_workactivities`, `oasis_workcontext`)
- [ ] Profile loads in <500ms (down from 3-15s with OASIS scraping)
- [ ] Provenance metadata updated: parquet source file + JobForge version instead of noc.esdc.gc.ca URL
- [ ] OASIS fallback retained for fields not yet in gold (Interests CSVs, Personal Attributes CSVs, Core Competencies)
- [ ] No regression: existing enrichment (labels, example titles, exclusions) still works — it already uses parquet

### Add After v5.0 Core (Post-v5.0 Enhancements)

Features enabled by v5.0 but not required for the milestone to be "done":

- [ ] Match rationale with NOC hierarchy level (UAT S1-03) — requires search indexing which table matched
- [ ] Matching search criteria on cards (UAT S1-04) — requires attribute-level search, not just title search
- [ ] Search from `job_architecture` table (UAT S1-06) — new data source, new UI controls
- [ ] Deterministic NOC-to-OG pre-filtering (UAT S5-04) — requires `bridge_noc_og` + classification wiring
- [ ] Sort by matched NOC attribute (UAT S1-05) — requires attribute-level search first

### Future Consideration (v6.0+)

- [ ] CAF Careers taxonomy search (UAT S1-08) — multi-taxonomy, out of scope for v5.0
- [ ] Bubble matrix classification report (UAT S5-06) — visualization feature, v6.0 scope
- [ ] OG enrichment via Stylize button (UAT S2-06) — RAG architecture, v6.0 scope

---

## Feature Prioritization Matrix

| Feature | User Value | Implementation Cost | Priority |
|---------|------------|---------------------|----------|
| Data exploration inventory | HIGH (gates everything) | LOW | P1 |
| Search from dim_noc + element_* | HIGH (eliminates primary pain point) | MEDIUM | P1 |
| Profile statements from oasis_* | HIGH (core UI surface) | MEDIUM | P1 |
| Main Duties / Key Activities from parquet | HIGH (first tab users see) | LOW | P1 |
| Provenance metadata for parquet source | HIGH (compliance required) | LOW | P1 |
| OASIS fallback for gap fields | HIGH (prevents regressions) | LOW | P1 |
| Full-text search across attributes | HIGH (fixes S1-12 "data engineer" miss) | MEDIUM | P2 |
| Sub-100ms profile load | HIGH (UX quality improvement) | LOW (side effect of P1) | P2 |
| Offline operation | MEDIUM (demo resilience) | LOW (side effect of P1) | P2 |
| Match rationale with hierarchy level (S1-03) | MEDIUM (nice transparency feature) | MEDIUM | P2 |
| Search from job_architecture (S1-06) | MEDIUM (new data source) | MEDIUM | P3 |
| Deterministic NOC-to-OG bridge filtering (S5-04) | HIGH for classification speed | MEDIUM | P2 |

**Priority key:**
- P1: Required for v5.0 milestone to be complete
- P2: Include if data exploration confirms data availability and time permits
- P3: Future milestone

---

## Comparison: Parquet-First vs Live OASIS Scraping

| Dimension | Live OASIS Scraping (Current) | Parquet-First (v5.0) |
|-----------|-------------------------------|----------------------|
| **Search latency** | 3-15 seconds (HTTP + parsing) | <100ms (pandas filter) |
| **Profile load latency** | 3-15 seconds (HTTP + parsing) | <500ms (parquet read + join) |
| **Search algorithm control** | None — OASIS black-box | Full — JD Builder controls matching logic |
| **Search scope** | Unit group titles only (OASIS limitation) | All NOC attributes: titles, labels, example titles, lead statements, main duties, workplaces |
| **Offline operation** | Impossible | Supported |
| **Reliability** | Fragile — government site availability, HTML structure changes, SSL cert issues | Stable — parquet files don't change until next JobForge refresh |
| **Match transparency** | Cannot determine where in NOC hierarchy match occurred | Can identify: Unit Group / Label / Example Title match tier |
| **Attribute-level match evidence** | Not available | Available via JOIN on matched parquet rows |
| **Data freshness** | Always current from live site | Tied to JobForge refresh cycle (acceptable for demo tool) |
| **Network requirement** | Required for every search and profile load | Not required (after parquet files loaded at startup) |
| **Provenance source** | noc.esdc.gc.ca URL | parquet file path + JobForge version + ingestion timestamp |
| **Failure mode** | Blank screen, 502 error, timeout | Graceful — can show partial data, OASIS fallback for gaps |
| **Cost of improvement** | Cannot improve — source is external | Directly improvable by improving pandas query logic |

---

## Sources

- Codebase analysis: `src/services/scraper.py`, `src/services/parser.py`, `src/services/labels_loader.py`, `src/vocabulary/index.py`, `src/routes/api.py`, `src/config.py` (2026-03-06)
- `.planning/JOBFORGE-DATA-REQUIREMENTS.md` — confirmed gold parquet table inventory (2026-02-06)
- `.planning/UAT-FINDINGS.md` — UAT issues S1-03, S1-04, S1-06, S1-07, S1-10, S1-12, S5-04 (2026-02-06)
- `.planning/PROJECT.md` — v5.0 milestone definition, existing architecture decisions (2026-03-06)
- HIGH confidence: all findings based on direct codebase inspection, not inference

---

*Feature research for: v5.0 JobForge 2.0 Integration — local-parquet-first search and profile*
*Researched: 2026-03-06*
