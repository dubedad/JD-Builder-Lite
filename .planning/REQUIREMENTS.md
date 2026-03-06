# Requirements: JD Builder Lite v5.0 JobForge 2.0 Integration

**Defined:** 2026-03-06
**Core Value:** Every piece of content in the final job description can be traced back to its authoritative source (NOC/OASIS or JobForge parquet), with clear documentation of human decisions and AI involvement.

## v5.0 Requirements

Requirements for JobForge 2.0 integration. Each maps to roadmap phases.

### Data Exploration

- [ ] **DATA-01**: Developer can access a structured document listing every JobForge parquet file with schema, row counts, and the OASIS data each file replaces
- [ ] **DATA-02**: Developer can see which data fields are not covered by parquet and must continue to use OASIS (explicit gap analysis, not inferred)
- [ ] **DATA-03**: App uses a `CoverageStatus` type to distinguish between three parquet failure modes: load error, record not found, and empty-but-valid result
- [ ] **DATA-04**: App logs a warning when parquet files fail to load or return unexpected data — failures are never silently swallowed

### Profile Service

- [ ] **PROF-01**: Profile page Skills, Abilities, Knowledge, Work Activities, and Work Context tabs are served from JobForge gold parquet (not live OASIS scraping)
- [ ] **PROF-02**: Profile page automatically falls back to OASIS scraping for sections not covered by parquet (Main Duties / Key Activities, Interests, Personal Attributes, Core Competencies)
- [ ] **PROF-03**: Exported JD records in provenance metadata whether each section came from parquet (JobForge version + file path) or OASIS (URL + scrape timestamp) — TBS Directive compliance requires this distinction
- [ ] **PROF-04**: All parquet column names are stripped of leading/trailing whitespace before use as display labels (known contamination in gold parquet confirmed in research)

### Search Service

- [ ] **SRCH-01**: Search results are returned from local JobForge parquet files (not live OASIS scraping) — sub-100ms response vs current 60s timeout ceiling
- [ ] **SRCH-02**: Search uses tiered relevance scoring against parquet: Labels match (95–100), occupation title match (90), example titles match (80), lead statement match (50)
- [ ] **SRCH-03**: Search automatically falls back to live OASIS scraping if the parquet search service is unavailable or returns no results for a query

## Future Requirements

Deferred to v5.1+ milestones.

### Main Duties ETL (v5.1 — JobForge-side dependency)

- **MAIN-01**: Key Activities / Main Duties tab served from parquet once JobForge ETL populates `element_main_duties.parquet` for all 900 profiles (currently 8 rows / 3 profiles only)
- **MAIN-02**: OASIS fallback for Main Duties retired once ETL coverage is confirmed complete

### P2 Features Unlocked by Parquet (v5.1)

- **ENH-01**: Search result cards show which NOC attribute matched the query and at what hierarchy level (UAT S1-03, S1-04)
- **ENH-02**: Search supports filtering by Job Architecture taxonomy from JobForge (UAT S1-06)
- **ENH-03**: NOC-to-OG pre-filtering in classification using `bridge_noc_og.parquet` for faster shortlisting (UAT S5-04)

### Classification Step 2 (v6.0)

- **JES-01**: Job Evaluation Standards scoring per occupational group
- **JES-02**: Benchmark position comparison UI
- **JES-03**: Manager consultation workflow

## Out of Scope

| Feature | Reason |
|---------|--------|
| Main Duties ETL coordination | JobForge-side task; JD Builder cannot unblock it unilaterally; OASIS fallback is acceptable permanently for now |
| Rewrite labels_loader as full replacement | Risky scope; DATA-04 fixes the silent failure; full rewrite is v5.1 hardening |
| Polars migration | Benchmarked on actual gold files — no performance advantage over pandas at 27 MB; adds dependency churn |
| Hot-reload of gold parquet files | watchdog unavailable on Python 3.14; low priority since gold files change infrequently |
| Multi-user / deployment hosting | Out of scope per PROJECT.md — single-user local app |

## Traceability

Phase mapping confirmed during roadmap creation 2026-03-06.

| Requirement | Phase | Status |
|-------------|-------|--------|
| DATA-01 | Phase 21 | Pending |
| DATA-02 | Phase 21 | Pending |
| DATA-03 | Phase 21 | Pending |
| DATA-04 | Phase 21 | Pending |
| PROF-01 | Phase 22 | Pending |
| PROF-02 | Phase 22 | Pending |
| PROF-03 | Phase 22 | Pending |
| PROF-04 | Phase 22 | Pending |
| SRCH-01 | Phase 23 | Pending |
| SRCH-02 | Phase 23 | Pending |
| SRCH-03 | Phase 23 | Pending |

**Coverage:**
- v5.0 requirements: 11 total
- Mapped to phases: 11
- Unmapped: 0 ✓

---
*Requirements defined: 2026-03-06*
*Last updated: 2026-03-06 — traceability confirmed during roadmap creation*
