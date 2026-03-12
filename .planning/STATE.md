# Project State

## Project Reference

See: .planning/PROJECT.md (updated 2026-03-11)

**Core value:** Every piece of content in the JD can be traced to its authoritative source (JobForge parquet or OASIS), with clear documentation of human decisions and AI involvement.
**Current focus:** v5.1 UI Overhaul — Phase 28: Navigation, Preview Modal & Selections Drawer

## Current Position

Milestone: v5.1 UI Overhaul
Phase: 28 of 30 (Navigation, Preview & Selections)
Plan: Not started
Status: Ready to plan
Last activity: 2026-03-12 — Phase 27 complete (2/2 plans, verified 5/5 must-haves)

Progress: [████░░░░░░] 33% (4/12 plans complete)

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

## Session Continuity

Last session: 2026-03-12
Stopped at: Phase 27 complete — verified 5/5 must-haves, ROADMAP updated, ready to plan Phase 28
Resume file: None
