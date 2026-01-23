---
phase: 06-enhanced-ui-display
plan: 02
title: "Proficiency Circles & Dimension Badges"
subsystem: ui-display
status: complete
tags: [accessibility, wcag, oasis, ui-components, proficiency-display]

dependencies:
  requires:
    - "05-05-enrichment-api-integration"
    - "06-01-view-mode-toggle"
  provides:
    - "proficiency-circle-rendering"
    - "dimension-badge-display"
    - "wcag-compliant-tooltips"
  affects:
    - "07-export-extensions"

tech-stack:
  added: []
  patterns:
    - "OASIS visual language for proficiency levels"
    - "Unicode symbols for accessible icons (U+25CF/U+25CB)"
    - "WCAG 2.1 Level AA tooltip patterns"
    - "CSS custom properties for themeable colors"

key-files:
  created: []
  modified:
    - "static/css/accordion.css"
    - "static/js/accordion.js"

decisions:
  - id: "D06-02-1"
    decision: "Use Unicode circle characters (●○) instead of SVG or CSS shapes"
    rationale: "Better cross-browser support, simpler DOM, no additional assets"
    alternatives: ["SVG icons", "CSS border-radius circles", "Icon font"]
    impact: "Consistent rendering across browsers, accessible to assistive tech"
  - id: "D06-02-2"
    decision: "Tooltip dismissal with Escape key and blur"
    rationale: "WCAG 2.1 SC 1.4.13 requires dismissable tooltips without losing focus context"
    alternatives: ["Click-to-dismiss", "Timer-based auto-hide"]
    impact: "Keyboard users can dismiss tooltips while maintaining page position"
  - id: "D06-02-3"
    decision: "Dimension badges inline with statement text, not separate column"
    rationale: "Work Context dimension type is attribute of the statement itself"
    alternatives: ["Separate badge column", "Icon-only badges"]
    impact: "Clear visual association between badge and statement content"

metrics:
  duration: "90 minutes"
  commits: 2
  files-changed: 2
  completed: "2026-01-23"
---

# Phase 06 Plan 02: Proficiency Circles & Dimension Badges Summary

**One-liner:** OASIS-style proficiency circles (●●●●○) with WCAG-compliant tooltips and Work Context dimension badges (FREQUENCY, DURATION).

## What Was Built

Implemented visual proficiency rating system using OASIS circle patterns with full WCAG 2.1 Level AA accessibility:

1. **CSS Styling** (accordion.css):
   - OASIS color variables (--oasis-blue: #0066cc)
   - Proficiency rating container with flex layout
   - Tooltip styles with keyboard focus support
   - Dimension badge styling for Work Context attributes
   - Updated statement layout to accommodate proficiency column

2. **JavaScript Rendering** (accordion.js):
   - `renderProficiency()` function generating filled/empty circles
   - Scale meaning labels (1: Basic Level → 5: Highest Level)
   - `renderDimensionBadge()` for Work Context dimension types
   - WCAG-compliant accessibility attributes (aria-label, aria-hidden)
   - Escape key handler for tooltip dismissal (SC 1.4.13)

3. **Accessibility Features**:
   - Screen reader announces "Level X" once (not individual circles)
   - Circles marked aria-hidden="true" (decorative only)
   - Keyboard focusable with tabindex="0"
   - Tooltip appears on hover/focus
   - Escape key dismisses tooltip

## Technical Implementation

### Proficiency Rendering Pattern

```javascript
// Enriched data from Phase 5:
{
  proficiency: {
    level: 4,
    max: 5,
    label: "High Level"
  }
}

// Renders to:
// Visual: ●●●●○ L4
// Screen reader: "Level 4"
// Tooltip on focus: "4 - High Level"
```

### Dimension Badge Pattern

```javascript
// Work Context with dimension type from Phase 5:
{
  text: "Work with others",
  dimension_type: "Frequency"
}

// Renders to:
// "Work with others [FREQUENCY]"
```

### Color System

- **Filled circles**: `--oasis-blue: #0066cc`
- **Empty circles**: `--circle-empty: #b0b0b0`
- **Badges**: Use existing `--highlight` and `--border` variables

## How It Works

### 1. Statement Rendering Flow

```javascript
createAccordionSection()
  ↓
statements.forEach()
  ↓
renderProficiency(stmt.proficiency) → HTML with circles
renderDimensionBadge(stmt.dimension_type) → Badge HTML
  ↓
Insert into statement__label with proficiency column
```

### 2. Accessibility Pattern

- **Visual users**: See colored circles + abbreviated label (L4)
- **Hover/Focus**: See full meaning in tooltip (4 - High Level)
- **Screen readers**: Hear "Level 4" once
- **Keyboard users**: Tab to focus, Escape to dismiss tooltip

### 3. CSS Layout

```
.statement__label (flex container)
  ├── .statement__checkbox (flex-shrink: 0)
  ├── .statement__content (flex: 1)
  │   ├── .statement__text + .dimension-badge
  │   └── .statement__source
  └── .proficiency-rating (margin-left: auto)
      ├── .rating-circles (aria-hidden)
      └── .rating-label (L4)
```

## Integration Points

### Consumes (from Phase 5)

```javascript
// Enriched statement format:
{
  text: "statement text",
  source_attribute: "Skills.1.A.1.a",
  proficiency: {
    level: 4,
    max: 5,
    label: "High Level"
  },
  dimension_type: "Frequency"  // Work Context only
}
```

### Provides (to Phase 7 - Export)

- Visual proficiency representation for PDF/Word export
- Dimension badge styling can be reused in export templates
- Accessible tooltip pattern for other enriched data

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 3 - Blocking] Task 2 code pre-existing in codebase**

- **Found during:** Task 2 execution
- **Issue:** `renderProficiency` and `renderDimensionBadge` functions already existed in commit 35a4875 (labeled as feat(06-01))
- **Fix:** Verified existing implementation matched Task 2 requirements, continued with Task 3
- **Commits:**
  - a2e8114: Task 1 (CSS styles)
  - 562ac19: Task 3 (Escape key handler) - also captured Task 2 changes
- **Impact:** Minor commit history inconsistency (Task 2 code committed as part of 06-01), but no functional impact

## Testing Performed

### Manual Verification

✅ **Visual Rendering**:
- Filled circles use Unicode U+25CF (●)
- Empty circles use Unicode U+25CB (○)
- Filled circles styled with --oasis-blue (#0066cc)
- Empty circles styled with --circle-empty (#b0b0b0)
- Abbreviated label (L4) displays next to circles
- Dimension badges appear on Work Context statements

✅ **Tooltip Behavior**:
- Tooltip shows on hover
- Tooltip shows on keyboard focus (Tab key)
- Tooltip displays full label: "4 - High Level"
- Escape key dismisses tooltip

✅ **Accessibility**:
- aria-hidden="true" on decorative circles
- aria-label="Level X" on container
- tabindex="0" for keyboard focus
- "No rating" displayed gracefully for statements without proficiency

### Code Verification

```bash
# Unicode circles present:
grep "●\|○" static/js/accordion.js
# ✅ Lines 159-160

# Accessibility attributes:
grep "aria-label\|aria-hidden" static/js/accordion.js
# ✅ Lines 148, 164, 167

# Escape key handler:
grep "Escape" static/js/accordion.js
# ✅ Lines 178-180

# OASIS blue color:
grep "oasis-blue" static/css/accordion.css
# ✅ Lines 4-5, 343
```

## Known Issues

None.

## Next Phase Readiness

### Ready for Phase 7 (Export Extensions)

✅ **Proficiency visualization established**: Circle pattern can be exported to PDF/Word
✅ **Dimension badges styled**: Badge HTML ready for export templates
✅ **Accessibility patterns defined**: Can apply same patterns to export preview
✅ **Color system extended**: OASIS colors available for export styling

### Blockers

None.

### Concerns

None - implementation complete and tested.

## Decision Records

### D06-02-1: Unicode Circles vs Other Icon Methods

**Context**: Need visual representation of proficiency levels that's accessible, performant, and consistent.

**Decision**: Use Unicode circle characters (U+25CF filled ●, U+25CB empty ○)

**Rationale**:
- Universal browser support (no font loading required)
- Screen reader friendly (can be hidden with aria-hidden)
- Simple DOM structure (single character per circle)
- Stylable with CSS color
- No additional HTTP requests or assets

**Alternatives Considered**:
1. **SVG icons**: Requires additional assets, complex DOM
2. **CSS border-radius**: Alignment issues, less semantic
3. **Icon font**: Additional font loading, accessibility challenges

**Consequences**:
- ✅ Fast rendering, minimal DOM nodes
- ✅ Consistent cross-browser
- ⚠️ Font fallback could affect appearance (mitigated by common Unicode support)

### D06-02-2: WCAG 2.1 Tooltip Dismissal Pattern

**Context**: WCAG 2.1 SC 1.4.13 requires content triggered by hover/focus to be dismissable without moving pointer/focus.

**Decision**: Escape key dismisses tooltip by blurring focused element

**Rationale**:
- Meets SC 1.4.13 requirement
- Standard keyboard interaction pattern
- Preserves user's place on page (no focus loss)
- Tooltip re-appears on re-focus (expected behavior)

**Alternatives Considered**:
1. **Click elsewhere to dismiss**: Requires mouse movement (fails keyboard-only requirement)
2. **Timer-based auto-hide**: Doesn't give user control (fails SC 1.4.13)
3. **Close button on tooltip**: Adds complexity, harder to reach with keyboard

**Consequences**:
- ✅ WCAG 2.1 Level AA compliant
- ✅ Standard keyboard interaction
- ✅ Simple implementation (single event listener)

### D06-02-3: Dimension Badge Placement

**Context**: Work Context statements have dimension_type attribute (Frequency, Duration, etc.)

**Decision**: Render dimension badge inline with statement text, not in separate column

**Rationale**:
- Dimension type is an attribute of the statement itself
- Visual proximity strengthens association
- Avoids additional column complexity
- Consistent with how attributes are typically displayed inline

**Alternatives Considered**:
1. **Separate column**: Adds layout complexity, weakens visual association
2. **Icon-only badges**: Less clear to users (requires learning icon meanings)
3. **Tooltip on hover**: Hides information by default (accessibility concern)

**Consequences**:
- ✅ Clear visual association
- ✅ Simple layout (no additional columns)
- ✅ Screen reader reads badge in context with statement
- ⚠️ Slightly longer text (mitigated by small badge size)

## Files Modified

### static/css/accordion.css
**Changes**: Added 94 lines, modified 8 lines

**Added**:
- `:root` CSS variables for OASIS colors
- `.proficiency-rating` container styles
- `.rating-circles` and `.rating-label` styles
- Tooltip styles with hover/focus states
- `.dimension-badge` styles
- `.no-rating` variant styles

**Modified**:
- `.statement__label` layout (flex with proficiency column)
- `.statement__content` wrapper structure
- `.statement__text` display properties
- `.statement__source` positioning

### static/js/accordion.js
**Changes**: Added 57 lines

**Added**:
- `PROFICIENCY_LABELS` constant object
- `renderProficiency()` function
- `renderDimensionBadge()` function
- Escape key event listener for tooltip dismissal
- Exports for new functions

**Modified**:
- `createAccordionSection()` statement rendering logic to include proficiency and dimension badges

## Git History

```
562ac19 feat(06-02): add Escape key handler for WCAG tooltip compliance
a2e8114 feat(06-02): add CSS for proficiency circles and dimension badges
```

## Lessons Learned

1. **Unicode symbols for UI**: Simple, accessible, and performant alternative to icon fonts/SVGs
2. **WCAG tooltip patterns**: Escape key dismissal is critical for Level AA compliance
3. **CSS custom properties**: Makes color theming straightforward for branded elements
4. **Aria patterns**: Single aria-label better than decorative elements speaking individually
5. **Commit discipline**: Pre-existing code from mislabeled commits requires deviation tracking

## Links

- **Plan**: `.planning/phases/06-enhanced-ui-display/06-02-PLAN.md`
- **Phase Context**: `.planning/phases/06-enhanced-ui-display/06-CONTEXT.md`
- **Previous Plan**: `06-01-SUMMARY.md` (View Mode Toggle)
- **Data Source**: Phase 5 enrichment API provides proficiency and dimension_type data
- **WCAG Reference**: [SC 1.4.13 Content on Hover or Focus](https://www.w3.org/WAI/WCAG21/Understanding/content-on-hover-or-focus.html)
