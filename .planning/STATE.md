# Project State

## Project Reference

See: .planning/PROJECT.md (updated 2026-03-11)

**Core value:** Every piece of content in the JD can be traced to its authoritative source (JobForge parquet or OASIS), with clear documentation of human decisions and AI involvement.
**Current focus:** v5.1 UI Overhaul — Phase 30 (final phase)

## Current Position

Milestone: v5.1 UI Overhaul
Phase: 29 of 30 (Classification Restyle + Generate Page) — COMPLETE
Plan: 29-04 complete (all 4 plans done including gap closure)
Status: Phase 29 complete (gap closure done)
Last activity: 2026-03-12 — Completed 29-04-PLAN.md (additional_context pipeline + multi-paragraph prompt)

Progress: [█████████░] 79% (11/14 plans complete)

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
| classify-status-badge starts hidden in v5.1 | 29-01 | User sees TBS card + Analyze CTA first; showLoading() removes hidden class when analysis begins |
| Legacy classify panels in hidden div for JS compat | 29-01 | recommendations-panel / evidence-panel kept in .classify-layout.hidden; plan 29-03 transitions to new containers |
| overview-textarea ID kept on contenteditable div | 29-02 | ID rename would break all downstream JS (main.js, export.js) calling generation.getOverview() |
| regenerate-btn preserved hidden in DOM | 29-02 | generate.js binds click listener to regenerate-btn; null would throw; visible regenerate is generate-regenerate |
| generate-output starts hidden, revealed by JS on generate | 29-02 | Separates pre-generation form state from post-generation output state visually |
| Analyze button dispatches classify-requested CustomEvent | 29-03 | Reuses handleClassifyRequest exactly; guarantees no double API call vs calling api.allocate() directly |
| showLoading() hides classify-cta (not just button click) | 29-03 | Covers both Analyze button and any programmatic trigger in one place |
| Alignment score computed client-side (evidenceCount/activityCount) | 29-03 | No new API field needed; keeps GroupRecommendation schema stable for backward compat |
| JOB_EVAL_STANDARDS covers 8 common groups only | 29-03 | AS/CS/EC/PM/IT/FI/PE/EX; all others fall back to general TBS job evaluation index |
| additional_context defaults to empty string in GenerationRequest | 29-04 | Backward compatible; existing requests without field are unaffected |
| Additional context block inserted after NOC statements, before closing instruction | 29-04 | LLM sees it as final guidance before writing |
| PROMPT_VERSION bumped to v1.1 after paragraph structure change | 29-04 | Provenance tracking — session metadata records which prompt version generated overview |

## Session Continuity

Last session: 2026-03-12
Stopped at: Completed 29-04-PLAN.md — additional_context pipeline + multi-paragraph prompt (Phase 29 gap closure complete)
Resume file: None
