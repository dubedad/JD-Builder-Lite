# Roadmap: JD Builder Lite

## Milestones

- **v5.0 JobForge 2.0 Integration** -- Phases 21-25 (current)
- ✅ **v4.1 Polish** -- Phases 18-20 (shipped 2026-02-07; Phase 20 deferred indefinitely)
- ✅ **v4.0 Occupational Group Allocation** -- Phases 14-17 (shipped 2026-02-04)
- ✅ **v3.0 Style-Enhanced Writing** -- Phases 09-13 (shipped 2026-02-03)
- ✅ **v2.0 UI Redesign** -- Phases 08-A through 08-D (shipped 2026-01-25)
- ✅ **v1.1 Enhanced Data Display + Export** -- Phases 05-07 (shipped 2026-01-23)
- ✅ **v1.0 MVP** -- Phases 01-04 (shipped 2026-01-22)

## Current: v5.0 JobForge 2.0 Integration

**Milestone Goal:** Replace live OASIS scraping with JobForge 2.0 gold parquet as the primary data source for search and profile data. OASIS scraping is retained as an explicit fallback for data not yet covered by parquet. TBS Directive compliance is extended to distinguish parquet-sourced content from OASIS-scraped content in provenance metadata.

- [x] **Phase 21: Data Exploration** - Inventory JobForge parquet files, map schema and row counts, produce gap analysis against OASIS, and establish the CoverageStatus type used by all subsequent phases (completed 2026-03-07)
- [x] **Phase 22: Profile Service** - Serve profile tab content (Skills, Abilities, Knowledge, Work Activities, Work Context) from parquet with automatic OASIS fallback and full provenance distinction in exports (completed 2026-03-08)
- [x] **Phase 23: Search Service** - Serve search results from parquet with tiered relevance scoring, sub-second response, and automatic OASIS fallback when parquet is unavailable (completed 2026-03-09)
- [x] **Phase 24: Compliance Hardening** - Close three tech debt items from v5.0 audit: add working_conditions provenance to frontend export (fully satisfies PROF-03), add route-level OASIS-down fallback to /api/profile, and create Phase 22 VERIFICATION.md (completed 2026-03-09)
- [x] **Phase 25: Tech Debt Cleanup** - Close non-blocking tech debt identified in v5.0 milestone audit: replace print() with logger.info() in labels_loader.py, fix bare except clauses, resolve search scoring inconsistency between OASIS and parquet paths, and fix structural inconsistency in _map_working_conditions_enriched() (completed 2026-03-10)

## Phase Details

### Phase 21: Data Exploration
**Goal**: Developers know exactly which JobForge parquet files exist, what they contain, and where OASIS scraping must remain as the primary source
**Depends on**: Nothing (first phase of milestone)
**Requirements**: DATA-01, DATA-02, DATA-03, DATA-04
**Success Criteria** (what must be TRUE):
  1. A structured inventory document exists listing every gold parquet file with schema (column names), row counts, and the OASIS data element each file replaces or supplements
  2. A gap analysis document explicitly lists which OASIS data fields have no parquet equivalent and must continue using live scraping -- gaps are named, not inferred
  3. The `CoverageStatus` type exists in the codebase with three distinct states: load error, record not found, and empty-but-valid result -- each state is handled differently, not collapsed into a single failure case
  4. Any parquet file that fails to load or returns unexpected data produces a visible warning log entry -- no failure is silently swallowed
**Plans**: 3 plans

Plans:
- [x] 21-01-PLAN.md -- Parquet inventory and gap analysis documents
- [x] 21-02-PLAN.md -- CoverageStatus type and ParquetReader service with warning logging
- [x] 21-03-PLAN.md -- Gap closure: wire logger.warning() into labels_loader.py and vocabulary/index.py

### Phase 22: Profile Service
**Goal**: Profile page tabs for Skills, Abilities, Knowledge, Work Activities, and Work Context are served from parquet for all 900 profiles, with automatic OASIS fallback for uncovered sections and provenance metadata that distinguishes the two sources
**Depends on**: Phase 21 (gap analysis determines which tabs use parquet vs OASIS; CoverageStatus type required)
**Requirements**: PROF-01, PROF-02, PROF-03, PROF-04
**Success Criteria** (what must be TRUE):
  1. Skills, Abilities, Knowledge, Work Activities, and Work Context tabs on the profile page load their statement data from parquet (not live OASIS scraping) for any of the 900 profiles covered in the gold files
  2. Main Duties / Key Activities, Interests, Personal Attributes, and Core Competencies tabs automatically fall back to OASIS scraping without any user-visible error or empty state -- the fallback is transparent
  3. Exported JD provenance metadata records each section's source as either "JobForge parquet (version X, path Y)" or "OASIS (URL, scrape timestamp)" -- the distinction is present and readable in the compliance block
  4. All parquet column names displayed as UI labels are stripped of leading and trailing whitespace before rendering -- no label shows a leading space or trailing space regardless of raw column name in the file
**Plans**: 2 plans

Plans:
- [x] 22-01-PLAN.md -- ProfileParquetReader service + response model + mapper wiring with parquet-first fallback
- [x] 22-02-PLAN.md -- Source badge UI (CSS + JS) + export provenance extension for per-section source tracking

### Phase 23: Search Service
**Goal**: Search returns results in under one second from local parquet files with tiered relevance scoring, and falls back transparently to OASIS scraping when parquet is unavailable
**Depends on**: Phase 21 (CoverageStatus type, gap analysis confirms parquet search coverage)
**Requirements**: SRCH-01, SRCH-02, SRCH-03
**Success Criteria** (what must be TRUE):
  1. A search query returns results in under one second (measured from request to first result rendered) -- replacing the current path that can take up to 60 seconds via OASIS scraping
  2. Search results are ranked using tiered relevance scoring: Labels match scores 95-100, occupation title match scores 90, example titles match scores 80, lead statement match scores 50 -- an exact title match ranks above a partial lead statement match
  3. When the parquet search service is unavailable or returns zero results for a query, the search automatically falls back to live OASIS scraping and returns results without requiring any user action
**Plans**: 2 plans

Plans:
- [x] 23-01-PLAN.md -- Parquet search reader and tiered scorer (build search index from parquet, implement four-tier scoring, wire query path to parquet)
- [x] 23-02-PLAN.md -- OASIS fallback and integration (detect parquet unavailability or empty results, fall back to OASIS scraper, integrate new search path into existing search endpoint)

### Phase 24: Compliance Hardening
**Goal**: Close the three tech debt items identified in the v5.0 audit: fully satisfy PROF-03 by adding working_conditions to frontend provenance tracking, add route-level resilience so profile parquet tabs survive OASIS outages, and formally verify Phase 22 via gsd-verifier
**Depends on**: Phase 22, Phase 23 (audit prerequisite; both complete)
**Requirements**: PROF-03 (full satisfaction — currently partial)
**Gap Closure**: Closes TD-1, TD-2, TD-3 from v5.0-MILESTONE-AUDIT.md
**Success Criteria** (what must be TRUE):
  1. `working_conditions` key is present in `export.js` section_sources dict — exported JD compliance appendix records provenance for Working Conditions statements
  2. `/api/profile` route serves Skills, Abilities, Knowledge, Work Activities, and Work Context from parquet even when `scraper.fetch_profile()` raises an exception or times out — OASIS-down no longer causes total profile failure
  3. Phase 22 VERIFICATION.md exists with a formal pass/fail assessment against Phase 22 success criteria
**Plans**: 1 plan

Plans:
- [x] 24-01-PLAN.md -- Frontend provenance fix + profile route OASIS-down fallback + Phase 22 verification

## Previous: v4.1 Polish

**Milestone Goal:** Exec-ready demo polish -- restructure profile tabs, improve navigation flow between screens, add coaching tone to classification, make results exportable, and update documentation.

- [x] **Phase 18: Profile Page Overhaul** - Restructure tabs and enhance data display on the profile page (completed 2026-02-07)
- [x] **Phase 19: Flow and Export Polish** - Fix navigation between screens, add coaching UX, extend export, update docs (completed 2026-02-07)
- [ ] **Phase 20: Evidence & Provenance Display** - Evidence highlighting with fuzzy matching, provenance tree, completion guidance (deferred indefinitely)

### Phase 18: Profile Page Overhaul
**Goal**: Profile page presents NOC data in a clean, logical tab structure with meaningful dimension labels on all ratings
**Depends on**: Nothing (no dependency on Phase 19)
**Requirements**: TAB-01, TAB-02, TAB-03, TAB-04, TAB-05, TAB-06, DISP-01, DISP-02, DISP-03
**Success Criteria** (what must be TRUE):
  1. Skills, Abilities, and Knowledge each appear as separate tabs on the profile page (not lumped together)
  2. Core Competencies has its own dedicated tab separate from Overview
  3. Navy blue description, Feeder Group Mobility, Career Progression, and Other Job Information content all live inside the Overview tab with no leftover empty tabs
  4. Every level circle on every statement shows its dimension type (e.g., "Proficiency: 4/5", "Importance: 3/5") derived from guide.csv
  5. Occupational category filter displays sub-major group and minor group hierarchy headings
**Plans**: 2 plans

Plans:
- [x] 18-01-PLAN.md -- Tab restructure + dimension labels (split Skills into 3 tabs, promote Core Competencies, consolidate Overview, dimension-aware proficiency labels)
- [x] 18-02-PLAN.md -- Filter hierarchy headings (hierarchical sub-major/minor group checkboxes with parent selection)

### Phase 19: Flow and Export Polish
**Goal**: Users can navigate fluidly between builder, preview, and classification screens with coaching guidance on invalid results, export classification alongside JD, and README reflects shipped state
**Depends on**: Nothing (independent of Phase 18; can execute in either order)
**Requirements**: NAV-01, NAV-02, NAV-03, UX-01, UX-02, UX-03, UX-04, EXP-01, EXP-02, DOC-01
**Success Criteria** (what must be TRUE):
  1. Preview screen shows Classify, Export, and Return to Builder as navigation options -- Return to Builder preserves all selections
  2. Classification results screen has Return to Builder button that goes back to profile page with selections intact
  3. Invalid Combination result displays in coaching style (blue/amber, not red) with explanation of why and what to adjust, plus Return to Builder button
  4. Classification results (recommendations, confidence, rationale, evidence, provenance) appear in exported PDF/DOCX
  5. GitHub README accurately describes v4.0 architecture, setup instructions, and shipped features
**Plans**: 3 plans

Plans:
- [x] 19-01-PLAN.md -- Navigation wiring: split nav layout, breadcrumb, Return to Builder, Classify from preview, classification caching
- [x] 19-02-PLAN.md -- Multi-group coaching UX: replace error-style invalid_combination with ranked coaching panel
- [x] 19-03-PLAN.md -- Classification export with hyperlinked provenance, export checkboxes, README creation

### Phase 20: Evidence & Provenance Display
**Goal**: Users can verify classification recommendations by seeing evidence quotes highlighted in context within their JD text, trace provenance from recommendation back to TBS source, and receive completion guidance for next steps
**Depends on**: Nothing (independent of Phases 18-19)
**Requirements**: EVD-01, EVD-02, EVD-03, EVD-04, EVD-05
**Success Criteria** (what must be TRUE):
  1. User can click evidence link to see side-by-side JD text view with evidence quote highlighted (EVD-01)
  2. Evidence quote is highlighted in the JD text panel using fuzzy matching when exact match fails (EVD-02)
  3. Multiple evidence quotes can be highlighted simultaneously (EVD-03)
  4. User can see expandable provenance tree from recommendation to TBS source (EVD-04)
  5. User sees Classification Step 1 Complete with next steps guidance (EVD-05)
**Plans**: 2 plans

Plans:
- [ ] 20-01-PLAN.md -- Upgrade provenance rendering from flat to expandable tree (closes gap between existing CSS and JS)
- [ ] 20-02-PLAN.md -- Human verification of complete evidence, provenance, and completion flow (carried from 17-03 Task 3)

### Phase 25: Tech Debt Cleanup
**Goal**: All non-blocking tech debt from the v5.0 milestone audit is resolved: logging is consistent (no bare print() on success paths), exception handling follows project conventions (no bare except), search scoring is symmetric between OASIS and parquet paths, and working_conditions mapper is structurally consistent with other enriched mappers
**Depends on**: Phase 24 (audit prerequisite complete)
**Requirements**: None (internal code quality)
**Success Criteria** (what must be TRUE):
  1. `labels_loader.py` success paths use `logger.info()` not `print()` — no bare `print()` calls remain on non-error paths
  2. Bare `except Exception:` clauses in `labels_loader.py` query methods are replaced with typed exceptions or explicit re-raises per project conventions
  3. Stem-in-title search tier scores identically via OASIS path and parquet path — the 85 vs 90 discrepancy in `api.py` line 164 is resolved
  4. `_map_working_conditions_enriched()` in `mapper.py` accepts a `parquet_tabs` parameter and propagates `data_source` the same way `_map_effort_enriched()` and `_map_responsibility_enriched()` do
**Plans**:

Plans:
- [x] 25-01-PLAN.md -- labels_loader.py logging and exception cleanup
- [x] 25-02-PLAN.md -- Search scoring symmetry + working_conditions mapper consistency

## Progress

| Phase | Milestone | Plans Complete | Status | Completed |
|-------|-----------|----------------|--------|-----------|
| 21. Data Exploration | v5.0 | 3/3 | Complete | 2026-03-07 |
| 22. Profile Service | v5.0 | 2/2 | Complete | 2026-03-08 |
| 23. Search Service | v5.0 | 2/2 | Complete | 2026-03-09 |
| 24. Compliance Hardening | v5.0 | 1/1 | Complete | 2026-03-09 |
| 25. Tech Debt Cleanup | v5.0 | 2/2 | Complete | 2026-03-10 |
| 18. Profile Page Overhaul | v4.1 | 2/2 | Complete | 2026-02-07 |
| 19. Flow and Export Polish | v4.1 | 3/3 | Complete | 2026-02-07 |
| 20. Evidence & Provenance Display | v4.1 | 0/2 | Deferred | - |

---
*Roadmap updated: 2026-03-10 -- Phase 25 complete (all v5.0 tech debt closed)*
