---
phase: 27-build-page-redesign
plan: 01
subsystem: ui
tags: [font-awesome, css-grid, dark-navy-header, tab-icons, section-description-box, position-title, state]

# Dependency graph
requires:
  - phase: 26-global-chrome-and-search
    provides: stepper (jdStepper.goToStep), profile-tabs-container, tab panel HTML structure
provides:
  - Dark navy v5.1 occupation header card with gear icon, NOC badge, lead statement, metadata row, close button
  - FA icons on all 8 tab buttons
  - Section description boxes injected at top of all 8 tab panels
  - Editable Position Title input on Overview tab (persisted in store)
  - Two-column Lead Statement + Definition layout on Overview tab
affects:
  - 27-02 (subsequent Build page plans building on this layout)
  - 27-03 and later plans reading positionTitle from store

# Tech tracking
tech-stack:
  added: []
  patterns:
    - "BEM modifier .profile-header--v51 for dark navy card variant"
    - "SECTION_DESCRIPTIONS constant drives description box content + icons"
    - "renderSectionDescriptionBox() helper injects boxes before any panel content"
    - "positionTitle in store enables cross-tab title persistence"

key-files:
  created: []
  modified:
    - templates/index.html
    - static/css/main.css
    - static/js/accordion.js
    - static/js/state.js

key-decisions:
  - "Header always shows fa-cog gear icon regardless of NOC category (NOC-specific icons stay in Overview content only)"
  - "Section description box text for Skills/Abilities/Knowledge/Effort/Responsibility uses raw HTML (bold+italic) — not escaped"
  - "positionTitle stored at top level of defaultState (not inside selections) so it resets with profile but survives tab switches"
  - "CSS for overview-position-title and overview-two-col added in Task 2 commit alongside section-description-box CSS"

patterns-established:
  - "SECTION_DESCRIPTIONS constant: icon + title + text per tab key — extend for new tabs"
  - "renderSectionDescriptionBox(tabKey) always prepended before panel innerHTML assignment"
  - "positionTitle reset in resetSelectionsForProfile alongside selections clear"

# Metrics
duration: 4min
completed: 2026-03-12
---

# Phase 27 Plan 01: Build Page Redesign — Header, Tab Icons, Section Boxes, Overview Redesign Summary

**Dark navy v5.1 header card with gear icon + NOC badge + metadata row replaces blue banner; FA icons on all 8 tabs; blue-grey description boxes at top of every panel; Overview tab adds editable Position Title input and two-column Lead Statement/Definition layout**

## Performance

- **Duration:** 4 min
- **Started:** 2026-03-12T10:44:39Z
- **Completed:** 2026-03-12T10:48:39Z
- **Tasks:** 3
- **Files modified:** 4

## Accomplishments
- Replaced old `blueBG` blue banner with `profile-header--v51` dark navy card including gear icon wrap, NOC badge, lead statement, metadata row (NOC 2021 v1.0 | Retrieved ISO date | Quality Verified | View Provenance Graph), OASIS link, and close button that calls `jdStepper.goToStep(1)`
- Added Font Awesome icons to all 8 tab buttons (fa-eye, fa-star, fa-list-check, fa-lightbulb, fa-brain, fa-book-open, fa-exchange-alt, fa-user) and blue-grey `.section-description-box` panels injected at the top of every tab panel
- Redesigned Overview tab top section: editable Position Title input pre-filled from store/profile title, two-column grid showing Lead Statement (left) and Definition (right); all existing panels (Also Known As, NOC Hierarchy, Feeder Group, Other Job Info) render unchanged below

## Task Commits

Each task was committed atomically:

1. **Task 1: Redesign occupation header card** - `740ea3c` (feat)
2. **Task 2: Add tab icons and section description boxes** - `6aec993` (feat)
3. **Task 3: Redesign Overview tab with Position Title and two-column layout** - `124aa53` (feat)

## Files Created/Modified
- `templates/index.html` - New v5.1 `#profile-header` structure with close button, icon-wrap, NOC badge, metadata row; FA icons in all 8 tab buttons
- `static/css/main.css` - Added `.profile-header--v51` dark navy card styles, `.section-description-box` styles, `.tab-icon` styles, `.overview-position-title` and `.overview-two-col` grid styles, mobile responsive overrides
- `static/js/accordion.js` - `renderProfileHeader` updated (fa-cog icon, ISO date, close button handler); added `SECTION_DESCRIPTIONS` constant and `renderSectionDescriptionBox()` helper; `renderTabContent` prepends description boxes to all 8 panels; `renderOverviewContent` rewritten top section with Position Title input and two-column layout
- `static/js/state.js` - Added `positionTitle: ''` to `defaultState`; `resetSelectionsForProfile` now resets `positionTitle` on profile change

## Decisions Made
- Header always shows `fa-cog` gear icon regardless of NOC category — NOC-specific icons (`getNocIcon()`) are still used in Overview tab content, not the header
- Section description box text for Skills/Abilities/Knowledge/Effort/Responsibility contains intentional raw HTML (bold+italic) injected via innerHTML — safe since it's authored constants, not user data
- `positionTitle` stored at top level of defaultState (not inside `selections`) so it resets on profile change but survives tab switches within the same profile
- No separate CSS file added — all v5.1 styles added to `main.css` keeping the single-file pattern already established

## Deviations from Plan

None — plan executed exactly as written.

## Issues Encountered
None.

## User Setup Required
None - no external service configuration required.

## Next Phase Readiness
- Dark navy header card, tab icons, description boxes, and Overview redesign are all in place
- `positionTitle` in store is available for 27-02 and later plans that use the position title in JD generation
- Existing tab content (statements, checkboxes, proficiency ratings, source badges) all render unchanged below description boxes
- No blockers for 27-02

---
*Phase: 27-build-page-redesign*
*Completed: 2026-03-12*
