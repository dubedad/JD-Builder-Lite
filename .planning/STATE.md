# Project State

## Project Reference

See: .planning/PROJECT.md (updated 2026-03-06)

**Core value:** Compliance-focused job description builder demonstrating TBS Directive 32592 compliance with full provenance tracking.
**Current focus:** v5.0 Tech Debt Cleanup -- Phase 25 complete, all tech debt closed

## Current Position

Milestone: v5.0 Tech Debt Cleanup
Phase: 25 complete (2/2 plans done)
Plan: 25-02 complete
Status: Phase complete
Last activity: 2026-03-10 -- Completed 25-02 (search scoring symmetry + working_conditions mapper consistency)

Progress: [████████████] 100% (12/12 plans complete)

## Milestone History

| Milestone | Status | Shipped |
|-----------|--------|---------|
| v1.0 MVP | SHIPPED | 2026-01-22 |
| v1.1 Enhanced Data Display + Export | SHIPPED | 2026-01-23 |
| v2.0 UI Redesign | SHIPPED | 2026-01-25 |
| v3.0 Style-Enhanced Writing | SHIPPED | 2026-02-03 |
| v4.0 Occupational Group Allocation | SHIPPED | 2026-02-04 |
| v4.1 Polish | SHIPPED | 2026-02-07 (Phases 18-19; Phase 20 deferred indefinitely) |

## Accumulated Context

### Decisions

| Decision | Phase | Rationale |
|----------|-------|-----------|
| TF-IDF fallback for semantic matching | Compat fix 2026-03-05 | torch has no Python 3.14 wheels; TF-IDF keeps classifier functional with reduced accuracy. See .planning/accuracy-notes/tfidf-fallback-2025-03-05.md |
| Defer Phase 20 (evidence highlighting) | v4.1 | LLM returns paraphrased analysis, not verbatim quotes; proper fix requires allocator prompt changes or v6+ PuMP grid |
| JobForge-first exploration before integration | v5.0 | JobForge gold parquet contents are unknown; Phase 21 inventories before committing to replacement scope |
| OASIS kept as explicit fallback | v5.0 | Parquet may not cover all profiles or all data fields; fallback ensures nothing breaks and is reflected in provenance |
| CoverageStatus is cross-cutting | v5.0 | Defined in Phase 21, used in Phase 22 (profile tabs) and Phase 23 (search); three distinct failure modes must not be collapsed |
| str,Enum (not StrEnum) for CoverageStatus | 21-02 | Matches EnrichmentSource pattern in src/models/noc.py -- consistent with codebase convention |
| Column stripping in read_parquet_safe (not lookup_profile) | 21-02 | Strip once at read time; all callers get clean columns regardless of which function they use |
| oasis_skills.parquet uses unit_group_id not oasis_profile_code | 21-02 | oasis_profile_code column exists only in element_labels.parquet; Phase 22 must use correct column per file |
| element_main_duties.parquet must not be queried in Phase 22 | 21-01 | ETL incomplete: only 8 rows / 3 profiles vs 4,991 rows / 900 profiles in source CSV; OASIS fallback is unconditional until JobForge ETL runs |
| Interests and Personal Attributes need no Phase 22 change | 21-01 | Source CSV via existing LabelsLoader already handles these -- no gold parquet gap requires intervention |
| Core Competencies and Career Mobility OASIS-only | 21-01 | No data in any tier (no parquet, no CSV); Phase 22 must use OASIS live scraping only |
| logger.warning() additive-only alongside self._load_error | 21-03 | Preserves runtime error inspection via get_error() while adding log-stream observability; neither replaces the other |
| vocabulary/index.py uses log-and-reraise not log-and-suppress | 21-03 | FileNotFoundError and read exceptions must propagate to callers; warning logged before raise, original traceback preserved |
| unit_group_id is join key for all element_* parquet files | 23-01 | Confirmed via parquet inspection: element_labels, element_lead_statement, element_example_titles all use unit_group_id |
| Auto-detect code search by pattern match | 23-01 | Queries matching ^\d{5}$ treated as code search regardless of search_type parameter |
| OASIS profile URL changed to /OASIS/OASISOccProfile with .00 suffix | 23-02 | Pre-existing breakage: old /OaSIS/OaSISSOccProfile returned 404; fix applied in scraper.py, mapper.py, selectors.py, search_parquet_reader.py |
| Two-block try/except in /api/profile for OASIS-down resilience | 24-01 | Block 1: OASIS fetch+parse (fallback to stub on any exception); Block 2: mapper+response (always runs); 502 eliminated |
| working_conditions key added to export.js section_sources | 24-01 | Fully satisfies PROF-03 -- all 5 JD element sections now record provenance in exported compliance appendix |
| logger.info() for success paths in _load_labels/_load_example_titles | 25-01 | info level appropriate for successful startup events; matches existing _load_* warning-on-failure pattern |
| %-style format strings in logger calls | 25-01 | Matches every existing logger.warning() call in labels_loader.py -- codebase-consistent |
| Stem-in-title OASIS search score raised to 90 | 25-02 | Matches T3 tier in search_parquet_reader.py so both paths rank identically for equivalent matches |
| wc_source extraction in _map_working_conditions_enriched mirrors effort/responsibility | 25-02 | Established trio pattern: all three work-context mappers share identical parquet_tabs + wc_source unpack |

### Blockers/Concerns

- TF-IDF semantic matching fallback active (sentence-transformers incompatible with Python 3.14) -- accuracy impact documented in .planning/accuracy-notes/tfidf-fallback-2025-03-05.md
- element_main_duties.parquet ETL gap: 8 rows / 3 profiles only (source has 900 profiles) -- OASIS fallback unconditional for Main Duties; see .planning/phases/21-data-exploration/GAP-ANALYSIS.md

## Session Continuity

Last session: 2026-03-10
Stopped at: Completed 25-02-PLAN.md (search scoring symmetry + working_conditions mapper consistency)
Resume file: None
