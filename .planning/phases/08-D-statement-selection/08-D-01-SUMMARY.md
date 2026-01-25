---
phase: 08-D-statement-selection
plan: 01
subsystem: ui
tags: [tooltips, accessibility, wcag, selection, action-bar]

# Dependency graph
requires:
  - phase: 08-C-profile-page-tabs
    provides: Tab navigation with statement rendering in panels
provides:
  - Accessible tooltips showing statement descriptions on hover/focus
  - Always-visible provenance labels below each statement
  - Single consolidated "Create Job Description (X selected)" button
  - Keyboard-accessible tooltips with tabindex and focus styles
affects: [08-D-02-export-jd, job-description-export]

# Tech tracking
tech-stack:
  added: []
  patterns:
    - "CSS ::after/::before pseudo-elements for accessible tooltips"
    - "data-tooltip attribute pattern for conditional tooltip content"
    - "WCAG 2.1 SC 1.4.13 keyboard dismissal with Escape key"

key-files:
  created: []
  modified:
    - static/js/accordion.js
    - static/css/accordion.css
    - static/js/selection.js
    - templates/index.html

key-decisions:
  - "SEL-01: Tooltips only when stmt.description exists"
  - "SEL-02: CSS ::after pattern instead of JS tooltip library"
  - "SEL-03: Single consolidated action button removes dual-button confusion"
  - "SEL-04: Tooltip positioning above element to avoid viewport clipping"

patterns-established:
  - "data-tooltip + tabindex=0 pattern for keyboard-accessible tooltips"
  - "escapeHtml() on tooltip content to prevent XSS"
  - "Action bar remains visible but disabled when no selections"

# Metrics
duration: 8min
completed: 2026-01-24
---

# Phase 08-D Plan 01: Statement Selection UI Summary

**Accessible tooltips with data-tooltip attributes, WCAG-compliant CSS styles, and consolidated Create button replacing dual-button layout**

## Performance

- **Duration:** 8 min
- **Started:** 2026-01-25T04:52:08Z
- **Completed:** 2026-01-24T23:54:15Z
- **Tasks:** 3
- **Files modified:** 4

## Accomplishments
- Statement descriptions appear as tooltips on hover/focus for proficiency items
- Keyboard users can Tab to statement text and see tooltips (WCAG 2.1 compliant)
- Provenance labels ("from Work Activities") always visible in italics below statements
- Single "Create Job Description (X selected)" button with real-time count updates
- Removed dual-button confusion (generate + create → single create button)

## Task Commits

Each task was committed atomically:

1. **Task 1: Add tooltip data attribute and keyboard accessibility** - `dcf0a85` (feat)
2. **Task 2: Add CSS tooltip styles with WCAG accessibility** - `3e70292` (feat)
3. **Task 3: Consolidate action bar to single Create button** - `ec9ebe9` (feat)

## Files Created/Modified
- `static/js/accordion.js` - Added data-tooltip attribute and tabindex to .statement__text when description exists
- `static/css/accordion.css` - CSS ::after/::before pseudo-elements for accessible tooltips with hover/focus triggers
- `static/js/selection.js` - Updated updateActionBar() to manage single create-btn with selection count
- `templates/index.html` - Removed generate-btn, single create-btn in action bar footer

## Decisions Made

**SEL-01: Conditional tooltip rendering**
- Only add data-tooltip when stmt.description exists
- Prevents empty tooltips and unnecessary tabindex on statements without descriptions
- Uses escapeHtml() to prevent XSS from special characters in descriptions

**SEL-02: CSS-only tooltip implementation**
- ::after pseudo-element for tooltip content using attr(data-tooltip)
- ::before pseudo-element for arrow pointer
- No JavaScript tooltip library needed - simpler, faster, no dependencies

**SEL-03: Single consolidated action button**
- Removed dual-button layout (Generate Overview + Create JD)
- Single "Create Job Description (X selected)" button
- Overview generation now happens automatically during Create flow
- Reduces user confusion about which button to click

**SEL-04: Tooltip positioning and accessibility**
- Position above element (`bottom: calc(100% + 8px)`) to avoid viewport edge clipping
- Both :hover and :focus trigger tooltips for keyboard users
- max-width: 320px prevents overly wide tooltips
- White on #333 background meets WCAG AA contrast requirements
- Existing Escape key handler dismisses tooltips by blurring focused elements

## Deviations from Plan

None - plan executed exactly as written.

## Issues Encountered

None - all three tasks completed smoothly with no blockers.

## User Setup Required

None - no external service configuration required.

## Next Phase Readiness

Statement selection UI layer complete. Ready for:
- Export functionality to generate final job description documents
- Backend integration for JD creation flow
- Testing with real user workflows across all tabs

All must-have truths verified:
- ✓ Every statement row has a checkbox for selection
- ✓ Proficiency circles display correctly (1-5 scale with filled/empty circles)
- ✓ Provenance labels always visible below each statement in small italics
- ✓ Hovering over statement text shows description as tooltip for items with proficiency
- ✓ Single 'Create Job Description (X selected)' button visible, count updates with selections
- ✓ Tooltip is keyboard accessible via focus

---
*Phase: 08-D-statement-selection*
*Completed: 2026-01-24*
