# Project State

## Project Reference

See: .planning/PROJECT.md (updated 2026-03-11)

**Core value:** Every piece of content in the JD can be traced to its authoritative source (JobForge parquet or OASIS), with clear documentation of human decisions and AI involvement.
**Current focus:** v5.1 UI Overhaul — Phase 28: Navigation, Preview Modal & Selections Drawer

## Current Position

Milestone: v5.1 UI Overhaul
Phase: 28 of 30 (Navigation, Preview & Selections)
Plan: All 3 plans complete (28-01, 28-02, 28-03)
Status: Phase 28 complete
Last activity: 2026-03-12 — Completed 28-02-PLAN.md (preview modal with client-side JD assembly)

Progress: [██████░░░░] 50% (6/12 plans complete — 28-01, 28-02, 28-03 all done)

## Milestone History

| Milestone | Status | Shipped |
|-----------|--------|---------|
| v1.0 MVP | SHIPPED | 2026-01-22 |
| v1.1 Enhanced Data Display + Export | SHIPPED | 2026-01-23 |
| v2.0 UI Redesign | SHIPPED | 2026-01-25 |
| v3.0 Style-Enhanced Writing | SHIPPED | 2026-02-03 |
| v4.0 Occupational Group Allocation | SHIPPED | 2026-02-04 |
| v4.1 Polish | SHIPPED | 2026-02-07 (Phases 18-19; Phase 20 deferred indefinitely) |
| v5.0 JobForge 2.0 Integration | SHIPPED | 2026-03-10 |

## Accumulated Context

### Design Reference
- Full UI walkthrough + 16 screenshots in `.planning/ui-walkthrough-v5.1/`
- Reference prototype based on v4.0 fork (no source code access — screenshots are authoritative spec)
- Français toggle and View Provenance Graph button: cosmetic/non-functional in v5.1
- Generate backend: keep OpenAI (no Anthropic key), update button label to "Generate with AI"

### Open Blockers/Concerns

- TF-IDF semantic matching fallback active (sentence-transformers incompatible with Python 3.14) — accuracy impact documented in .planning/accuracy-notes/tfidf-fallback-2025-03-05.md
- element_main_duties.parquet ETL gap: 8 rows / 3 profiles — OASIS fallback unconditional for Main Duties

## Accumulated Decisions

| Decision | Phase | Rationale |
|----------|-------|-----------|
| search-complete keeps stepper at step 1 | 26-01 | Search results display IS the Search step in v5.1 |
| profile-loaded advances to step 2 (Build) | 26-01 | Profile view IS the Build step |
| canAccessStep(2=Build) requires currentProfile | 26-01 | You need a profile to be in Build; search results alone don't unlock it |
| selections-tab hides sidebar-toggle via display:none | 26-01 | Preserve DOM element, avoid null-reference errors in main.js |
| Grid view removed entirely | 26-02 | v5.1 spec uses card view only; renderGridView() deleted |
| filter-minor-group-options -> filter-noc-broad-options | 26-02 | v5.1 HTML 6-accordion filter panel uses new element IDs |
| source_label hardcoded to "O*NET SOC" | 26-02 | All parquet results are O*NET-aligned data |
| example_titles from titles_df in _build_result() | 26-02 | Inline lookup avoids extra API calls; max 5, semicolon-separated |
| Header always shows fa-cog gear icon | 27-01 | NOC-specific icons stay in Overview tab content only; header is always a gear |
| Section description box text uses raw HTML | 27-01 | Bold+italic markup is authored constants, not user data; safe for innerHTML |
| positionTitle at top level of defaultState | 27-01 | Resets on profile change but survives tab switches within same profile |
| Abilities/Knowledge IDs use filtered-array positions | 27-02 | Filter from profile.skills.statements before renderLevelGroupedContent so IDs are abilities-0..N, not global indices |
| renderLevelGroupedContent includes renderSourceBadge internally | 27-02 | Callers do not append source badge separately; avoids duplication |
| Style Selected buttons removed entirely | 27-02 | Not in v5.1 spec; removed from renderStatementsPanel and inline Effort/Responsibility rendering |
| ALL_SECTIONS_LABELS lives in accordion.js | 28-03 | Co-located with JD_ELEMENT_LABELS; exported globally so sidebar.js can access without import |
| Drawer event listener re-attached on every render | 28-03 | innerHTML replacement destroys prior listeners; re-attach via summaryContainer.addEventListener each updateSidebar call |
| abilities/knowledge text from filtered sub-array | 28-03 | Filter profile.skills.statements by source_attribute, then index into filtered array — matches IDs from phase 27-02 |
| build-nav-bar visibility managed by navigateToStep | 28-01 | All 5 cases in navigateToStep add/remove hidden class; handleResultClick also shows it on profile load |
| action-bar has style="display:none" not deleted | 28-01 | Keeps actionBar variable refs valid; classList ops on it are now no-ops visually |
| nav-preview-jd dispatches CustomEvent open-preview-modal | 28-01 | Decouples build nav from preview implementation; 28-02 will add the listener |
| classify-nav-actions--always outside #classify-complete | 28-01 | Ensures nav buttons visible even while classification is running or errored |
| assembleJDPreview() is client-side only (no API call) | 28-02 | Fast, instant rendering; no spinner needed for preview |
| downloadPDF/downloadDOCX btn nullable | 28-02 | preview-export-btn only exists on old showPreview() page; modal calls same methods |

## Session Continuity

Last session: 2026-03-12
Stopped at: Completed 28-02-PLAN.md (Preview modal with client-side JD assembly)
Resume file: None
