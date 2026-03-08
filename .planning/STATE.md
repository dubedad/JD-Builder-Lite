# Project State

## Project Reference

See: .planning/PROJECT.md (updated 2026-03-06)

**Core value:** Compliance-focused job description builder demonstrating TBS Directive 32592 compliance with full provenance tracking.
**Current focus:** v5.0 JobForge 2.0 Integration -- Phase 22: Profile Service (Plan 01 complete, Plan 02 at checkpoint)

## Current Position

Milestone: v5.0 JobForge 2.0 Integration
Phase: 22 in progress
Plan: 22-01 complete; 22-02 tasks done, awaiting human verification checkpoint
Status: 22-02 checkpoint — user must verify source badges in browser, then type "approved"
Last activity: 2026-03-08 -- Completed 22-01 (ProfileParquetReader + mapper); completed 22-02 tasks 1+2 (badges + export provenance); at human checkpoint

Progress: [████░░░░░░] ~57% (4/7 plans complete)

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

### Blockers/Concerns

- TF-IDF semantic matching fallback active (sentence-transformers incompatible with Python 3.14) -- accuracy impact documented in .planning/accuracy-notes/tfidf-fallback-2025-03-05.md
- oasis_skills.parquet column is unit_group_id (not oasis_profile_code) -- Phase 22 must use correct column name per parquet file
- element_main_duties.parquet ETL gap: 8 rows / 3 profiles only (source has 900 profiles) -- Phase 22 must use unconditional OASIS fallback for Main Duties; see .planning/phases/21-data-exploration/GAP-ANALYSIS.md
- 5 oasis_* parquet files have whitespace-contaminated column names (14+6+3+3+1 columns) -- Phase 22/23 must call df.columns.str.strip() after reading these files (parquet_reader.py handles this automatically)

## Session Continuity

Last session: 2026-03-08T13:20:00Z
Stopped at: Phase 22, Plan 02 — at human verification checkpoint (tasks 1+2 committed, awaiting browser verify)
Resume file: .planning/.continue-here.md
