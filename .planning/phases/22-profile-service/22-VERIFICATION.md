---
phase: 22-profile-service
verified: 2026-03-09T00:00:00Z
status: conditional_pass
score: 3.5/4 must-haves verified
notes: "Criterion 3 partially met at Phase 22 completion (working_conditions key missing in frontend export.js); gap closed by Phase 24 TD-1"
---

# Phase 22: Profile Service Verification Report

**Phase Goal:** Profile page tabs for Skills, Abilities, Knowledge, Work Activities, and Work Context are served from parquet for all 900 profiles, with automatic OASIS fallback for uncovered sections and provenance metadata that distinguishes the two sources.
**Verified:** 2026-03-09T00:00:00Z
**Status:** conditional_pass
**Notes:** 3/4 criteria fully met at Phase 22 completion. Criterion 3 (export provenance) partially met — backend wired correctly, frontend export.js missing `working_conditions` key. Gap closed by Phase 24 TD-1 (commit 83cce6c).

---

## Goal Achievement

### Observable Truths

| # | Truth | Status | Evidence |
|---|-------|--------|----------|
| 1 | 5 profile tabs (Skills, Abilities, Knowledge, Work Activities, Work Context) are served from parquet for covered profiles with automatic OASIS fallback | VERIFIED | 22-01-SUMMARY.md: ProfileParquetReader.get_all_profile_tabs() reads 5 oasis_* parquet files. Mapper wired parquet-first. Verified NOC 21211 returns 25/28/7/35/39 ratings from jobforge for all 5 tabs. Unknown NOC codes fall back gracefully. |
| 2 | key_activities / Main Duties always uses OASIS fallback (parquet ETL incomplete) | VERIFIED | 22-01-SUMMARY.md decision: "key_activities data_source always 'oasis' (Main Duties anchors it to OASIS)". element_main_duties.parquet has only 8 rows / 3 profiles (ETL incomplete per GAP-ANALYSIS.md). OASIS fallback is unconditional for this tab. |
| 3 | Exported JD provenance metadata records each section's data source in the compliance block | CONDITIONAL PASS | 22-02-SUMMARY.md: SourceMetadataExport.section_sources added to export_models.py; build_compliance_sections() in export_service.py includes per-section provenance when section_sources present. Frontend export.js builds section_sources dict with 4 keys (key_activities, skills, effort, responsibility) — missing working_conditions key at Phase 22 completion. Gap closed by Phase 24 TD-1. |
| 4 | Parquet column names with whitespace contamination are stripped at read time | VERIFIED | Phase 21 read_parquet_safe() applies df.columns.str.strip() at read time (21-VERIFICATION.md, Criterion 3). Phase 22 ProfileParquetReader calls read_parquet_safe() for all 5 oasis_* files, inheriting this behaviour. All callers receive clean column names. |

**Score:** 3.5/4 truths verified (Criterion 3 partially met at Phase 22; gap fully closed by Phase 24 TD-1)

---

## Required Artifacts

| Artifact | Expected | Status | Details |
|----------|----------|--------|---------|
| `src/services/profile_parquet_reader.py` | ProfileParquetReader reading 5 oasis_* parquet files with OASIS fallback | VERIFIED | Created in Plan 22-01 (commit 88c0468). get_all_profile_tabs(), get_profile_tab(), extract_dimension_ratings(), noc_to_oasis_code() all implemented. OASIS_CODE_COL = 'oasis_code' confirmed correct for all 5 files. |
| `src/services/mapper.py` | Parquet-first wiring; all 5 tab methods accept parquet_tabs parameter | VERIFIED | Plan 22-01 (commit d6ce242). _map_skills_enriched(), _map_abilities_enriched(), _map_knowledge_enriched(), _map_work_activities_enriched(), _map_effort_enriched(), _map_responsibility_enriched() all accept parquet_tabs. |
| `src/models/responses.py` | data_source field on EnrichedJDElementData | VERIFIED | Plan 22-01 (commit d6ce242). data_source: str = "oasis" added to EnrichedJDElementData. Field propagates to API response JSON for all profile tabs. |
| `static/css/main.css` | Source badge CSS classes for JobForge/OASIS distinction | VERIFIED | Plan 22-02 (commit fb3e398). .source-badge, .source-badge--jobforge (green, #e8f5e9), .source-badge--oasis (grey, #f5f5f5) present. |
| `static/js/accordion.js` | renderSourceBadge() injected in all 6 statement tabs | VERIFIED | Plan 22-02 (commit fb3e398). renderSourceBadge() function added. Badge injected for Skills, Abilities, Knowledge, Key Activities, Effort, Responsibility tabs. Key Activities badge includes hover tooltip. |
| `src/models/export_models.py` | section_sources Optional field on SourceMetadataExport | VERIFIED | Plan 22-02 (commit 9befc12). section_sources: Optional[dict[str, str]] = None added. Backward compatible — None default preserves existing export behaviour. |
| `src/services/export_service.py` | build_compliance_sections() includes per-section provenance when section_sources present | VERIFIED | Plan 22-02 (commit 9befc12). Conditional block reads section_sources and builds per-section detail entries in Section 6.2.3. access_method text updated to reflect both sources when present. |
| `static/js/export.js` | section_sources dict with all 5 JD element keys | PARTIAL | 4 keys present at Phase 22 completion (key_activities, skills, effort, responsibility). working_conditions missing. Gap closed by Phase 24 TD-1 (commit 83cce6c, 2026-03-09). |

---

## Key Link Verification

| From | To | Via | Status | Details |
|------|----|-----|--------|---------|
| `profile_parquet_reader.py` | `5 oasis_* parquet files` | `read_parquet_safe(JOBFORGE_GOLD_PATH / filename)` | WIRED | get_all_profile_tabs() reads oasis_skills, oasis_abilities, oasis_knowledge, oasis_work_activities, oasis_work_context. Strips columns via read_parquet_safe(). |
| `mapper.py` | `profile_parquet_reader.py` | `from src.services.profile_parquet_reader import get_all_profile_tabs` | WIRED | to_jd_elements() calls get_all_profile_tabs(noc_code) and passes result to all _map_*_enriched() methods as parquet_tabs. |
| `accordion.js` | `API response data_source field` | `profile[section].data_source` | WIRED | renderSourceBadge() reads data_source from each tab's API response and renders appropriate badge class (jobforge = green, oasis = grey). |
| `export.js` | `src/services/export_service.py` | `section_sources dict in export request body` | PARTIAL | 4/5 keys wired at Phase 22 completion. working_conditions key added by Phase 24 TD-1. Build path: profile[tab].data_source -> section_sources dict -> export request body -> SourceMetadataExport -> build_compliance_sections(). |

---

## Requirements Coverage

| Requirement | Status | Notes |
|-------------|--------|-------|
| PROF-01: Profile page tabs served from parquet for covered profiles | SATISFIED | 5 tabs (Skills, Abilities, Knowledge, Work Activities, Work Context) served from parquet for NOC 21211 and other covered profiles. Verified via parquet inspection: 25/28/7/35/39 ratings returned from jobforge. |
| PROF-02: Automatic OASIS fallback when parquet lookup fails | SATISFIED | CoverageStatus LOAD_ERROR and NOT_FOUND both trigger OASIS fallback transparently. Unknown NOC codes return gracefully with OASIS data. key_activities uses OASIS unconditionally. |
| PROF-03: Provenance metadata distinguishes parquet-sourced from OASIS-sourced content in exports | PARTIALLY SATISFIED at Phase 22 | Backend wired: SourceMetadataExport.section_sources + build_compliance_sections() both implemented. Frontend partially wired: 4/5 keys in export.js section_sources dict. working_conditions key missing. Fully satisfied after Phase 24 TD-1. |
| PROF-04: Whitespace-contaminated parquet column names handled correctly | SATISFIED | Inherited from Phase 21 infrastructure: read_parquet_safe() calls df.columns.str.strip() at read time. Phase 22 ProfileParquetReader uses read_parquet_safe() exclusively. |

---

## Conditional Status Explanation

Phase 22 is assessed as **CONDITIONAL PASS** for the following reason:

**Criterion 3 (PROF-03 provenance):** The backend implementation is complete and correct. The gap is limited to the frontend `static/js/export.js` file, which assembles the `section_sources` dict from the profile API response before sending the export request. At Phase 22 completion, `working_conditions` was not included in this dict (4 of 5 section keys present). As a result, exported JDs would not record provenance for Working Conditions statements in the compliance appendix.

This gap was identified during the v5.0 milestone audit and documented as TD-1. It was closed by Phase 24 Plan 01 Task 1 (commit `83cce6c`, 2026-03-09), which added the `working_conditions` key to the `section_sources` dict. The backend requires no further changes.

The three other criteria are fully met and have no known gaps.

---

## Anti-Patterns Found

| File | Line | Pattern | Severity | Impact |
|------|------|---------|----------|--------|
| `static/js/export.js` | 113-118 | Missing `working_conditions` key in section_sources dict | Warning | PROF-03 partially unsatisfied at Phase 22 completion; working_conditions provenance not recorded in exports. Closed by Phase 24 TD-1. |

No blocker anti-patterns in backend implementation. Frontend gap is isolated to a single missing dict key.

---

## Human Verification Required

User verified source badges in browser (2026-03-08):
- Skills, Abilities, Knowledge, Effort, Responsibility tabs: green "Source: JobForge" badge confirmed
- Key Activities tab: grey "Source: OASIS" badge with tooltip confirmed
- Overview, Core Competencies: no badge confirmed
- Badges visually distinct (green vs grey) confirmed

---

_Verified: 2026-03-09T00:00:00Z_
_Verifier: Claude (gsd-executor Phase 24 Plan 01)_
