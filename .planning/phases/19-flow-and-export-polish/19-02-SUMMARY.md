---
phase: 19
plan: 02
subsystem: ui
tags: [coaching, classification, UX, invalid-combination, blue-amber, multi-group]
requires:
  - phase: 17
    plan: 02
    provides: "Classification recommendation cards with expand/collapse"
provides:
  - "Coaching panel for multi-group results with informational styling"
  - "Blue/amber styling replacing red error display"
  - "Ranked recommendation cards showing duty alignment percentages"
  - "Cache-hit listener for classify.js"
  - "Status badge update: Multiple Groups Identified (coaching style)"
affects:
  - phase: 19
    plan: 03
    note: "Export functionality may need coaching panel awareness"
tech-stack:
  added: []
  patterns:
    - "Coaching panel UX pattern (informational vs error)"
    - "Blue/amber informational styling for multi-group results"
    - "Duty alignment visualization in recommendation cards"
key-files:
  created: []
  modified:
    - static/js/classify.js
    - static/css/classify.css
key-decisions:
  - decision: "Use coaching panel with blue informational styling instead of red error for invalid_combination"
    rationale: "Multi-group results are valid outcomes needing guidance, not errors"
  - decision: "Show ranked cards with duty alignment percentages and key evidence quotes"
    rationale: "Users need to understand WHY each group was recommended to make informed decisions"
  - decision: "No duplicate Return to Builder button in coaching panel"
    rationale: "Plan 19-01 already provides top-level navigation - avoid redundancy"
duration: 7 minutes
completed: 2026-02-07
---

# Phase 19 Plan 02: Multi-Group Coaching UX Summary

**One-liner:** Replace red "Invalid Combination" error with blue coaching panel showing ranked recommendations with duty alignment percentages and key evidence

## What Was Built

Transformed multi-group classification results from error-style display to coaching-style guidance:

1. **Coaching Panel UI (classify.js)**:
   - New `renderCoachingPanel()` function replaces `renderConflictingDutiesWarning()`
   - Lightbulb icon and blue background convey "insight" not "error"
   - Ranked recommendation cards show confidence percentages and duty alignment
   - Extract up to 3 key evidence quotes per recommendation as "key duties"
   - "Accept Top Recommendation" button dismisses panel, leaving full cards visible
   - Fallback rendering when only `conflicting_duties` dict available (no detailed recommendations)

2. **Status Badge Update**:
   - `invalid_combination` now displays "Multiple Groups Identified" with coaching badge class
   - Blue styling (#1565c0) instead of red error

3. **Cache-Hit Listener**:
   - Added listener in `init()` to re-render from cached allocation responses
   - Reconstructs JD data from `window.currentProfile` and store state

4. **Coaching Panel CSS (classify.css)**:
   - `.coaching-panel` with blue background (#e3f2fd) and border (#1565c0)
   - `.coaching-panel--info` and `--warning` variants for future flexibility
   - `.recommendation-card-coaching` for ranked cards within coaching panel
   - Primary card gets blue border (2px) and subtle shadow
   - `.duty-alignment` and `.duty-list` styles for evidence display
   - `.coaching-accept-btn` with blue primary styling
   - `.classify-status-badge.coaching` for status badge variant
   - Confidence badge tier variants (high/medium/low) with color-coded backgrounds
   - `.classify-stale-warning` amber banner styles (for future use)
   - `.classify-nav-actions` for bottom navigation area

## Requirements Satisfied

- **UX-01**: Invalid Combination displays as coaching style (blue), not red error ✓
- **UX-02**: Explains WHY the combination spans multiple groups (duty alignment breakdown) ✓
- **UX-03**: Suggests what to adjust (ranked duties showing which activities drive each group) ✓
- **UX-04**: Return to Builder button exists at classify-section level (via Plan 19-01) ✓

## Task Commits

| Task | Description | Commit | Files |
|------|-------------|--------|-------|
| 1 | Replace invalid_combination error with coaching panel | ac6589a | static/js/classify.js |
| 2 | Add coaching panel CSS with blue/amber styling | da877d0 | static/css/classify.css |

## Decisions Made

**1. Coaching panel replaces error display**
- Multi-group results are valid outcomes requiring user guidance, not system failures
- Blue informational styling conveys "here are your options" instead of "something went wrong"

**2. Duty alignment visualization**
- Show confidence percentage AND key evidence quotes per recommendation
- Users need to understand which duties drove each recommendation to make informed choices

**3. No duplicate navigation**
- Plan 19-01 already provides "Return to Builder" button at classify-section level
- Adding another inside coaching panel would be redundant and confusing

## Integration Notes

**Coordination with Plan 19-01**:
- Plan 19-01 added `classify-complete` event dispatch (line 172 of classify.js)
- This plan OWNS all other classify.js changes (coaching panel, cache-hit listener, status badge update)
- No conflicts - changes are complementary

**Coaching Panel Architecture**:
```
.coaching-panel (blue background, lightbulb icon)
├── .coaching-content
│   ├── .coaching-title ("Your JD spans multiple groups")
│   ├── .coaching-explanation (why multi-group result)
│   ├── .ranked-recommendations
│   │   └── .recommendation-card-coaching (sorted by confidence)
│   │       ├── .recommendation-coaching-header (confidence badge + group code/name)
│   │       └── .duty-alignment (percentage + key duties list)
│   └── .coaching-actions
│       └── .coaching-accept-btn (dismisses panel)
```

## Deviations from Plan

None - plan executed exactly as written.

## Next Phase Readiness

**Blockers**: None

**Recommendations**:
1. UAT verification: Trigger multi-group classification, confirm blue coaching panel appears
2. Verify "Accept Top Recommendation" button removes coaching panel but leaves full cards
3. Confirm status badge shows "Multiple Groups Identified" in blue, not "Invalid Combination" in red
4. Test responsive layout on mobile (coaching cards should stack vertically)

## Verification Checklist

- [x] `renderCoachingPanel()` replaces `renderConflictingDutiesWarning()`
- [x] Status badge shows "Multiple Groups Identified" with coaching class
- [x] Cache-hit listener added to `init()` function
- [x] Blue coaching panel CSS added (no red styling for multi-group)
- [x] Ranked recommendation cards show duty alignment and key evidence
- [x] Accept Top Recommendation button works (dismisses panel)
- [x] No duplicate "Return to Builder" button in coaching panel
- [x] Confidence badge tier variants defined (high/medium/low)
- [x] Both tasks committed atomically

## Self-Check: PASSED

**Files verification:**
- static/js/classify.js: EXISTS (modified)
- static/css/classify.css: EXISTS (modified)

**Commits verification:**
- ac6589a: EXISTS (Task 1)
- da877d0: EXISTS (Task 2)

All claimed files exist and all commits are in git history.
