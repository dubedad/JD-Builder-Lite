# Phase 08-D: Statement Selection - Research

**Researched:** 2026-01-24
**Domain:** Checkbox selection patterns, accessible tooltips, dynamic button updates, provenance display
**Confidence:** HIGH

## Summary

Phase 08-D implements the final piece of the v2.0 UI redesign by adding statement selection capabilities across all Job Header tabs. The technical challenge involves four key components: (1) implementing checkboxes on existing statement rows without breaking current accordion functionality, (2) displaying proficiency circles that already exist but ensuring consistency across tabs, (3) making provenance labels permanently visible instead of hidden, and (4) implementing accessible tooltips for statement descriptions on hover.

The application already has robust infrastructure for this phase. The `accordion.js` module renders statements with checkboxes, proficiency circles, and source labels. The `selection.js` module handles checkbox state management with a reactive store pattern. The `state.js` store provides centralized selection tracking across sections. This phase extends existing patterns rather than introducing new architecture.

**Primary recommendation:** Extend existing accordion rendering to support tab context, implement accessible CSS-only tooltips with ARIA attributes, ensure provenance labels are always visible, consolidate action buttons into single "Create Job Description (X selected)" button that updates dynamically.

## Standard Stack

### Core (Already in Application)

| Library | Version | Purpose | Why Standard |
|---------|---------|---------|--------------|
| Vanilla JavaScript | ES6+ | Event delegation for checkboxes | Already used throughout app; no new dependencies |
| CSS Custom Properties | Modern | Tooltip styling | Already used for theming; simple tooltip implementation |
| Proxy-based Store | Custom | State management | Already implemented in state.js for selections |
| SortableJS | Current | Drag-and-drop reordering | Already integrated for section reordering |

### Supporting

| Library | Version | Purpose | When to Use |
|---------|---------|---------|-------------|
| localStorage | Browser API | Selection persistence | Already used for state persistence |
| Event delegation | Native | Checkbox change handlers | Already implemented in selection.js |
| CSS ::after pseudo-elements | Modern CSS | Tooltip rendering | Standard accessible tooltip pattern |

### Alternatives Considered

| Instead of | Could Use | Tradeoff |
|------------|-----------|----------|
| CSS ::after tooltips | Bootstrap Tooltip (requires Popper.js) | Would add 40KB dependency; CSS-only is sufficient and accessible |
| HTML title attribute | Custom JS tooltip library | title attribute isn't keyboard accessible; CSS pseudo-elements provide keyboard support via :focus |
| Separate buttons | Single unified button | Requirements explicitly specify single button; matches OaSIS UX |

**Installation:**
No new packages required. All capabilities already present in codebase.

## Architecture Patterns

### Recommended Project Structure

```
static/js/
├── accordion.js          # EXTEND: Support tab context, ensure provenance visible
├── selection.js          # EXTEND: Update button text with total count
├── state.js              # NO CHANGE: Already handles selections correctly
└── main.js              # MINIMAL: Update button consolidation logic

static/css/
└── accordion.css         # EXTEND: Add tooltip styles, ensure provenance always visible

templates/
└── index.html           # MODIFY: Consolidate action bar buttons
```

### Pattern 1: Accessible CSS-Only Tooltips

**What:** Pure CSS tooltips using ::after pseudo-elements with ARIA for keyboard accessibility
**When to use:** Statement descriptions need to appear on hover for items with proficiency levels

**Example:**
```css
/* Source: MDN ARIA tooltip pattern + inclusive-components.design */
.statement__text[data-tooltip] {
    position: relative;
    cursor: help;
}

.statement__text[data-tooltip]::after {
    content: attr(data-tooltip);
    position: absolute;
    bottom: 100%;
    left: 50%;
    transform: translateX(-50%) translateY(-8px);

    /* Styling */
    background: var(--text);
    color: white;
    padding: 0.5rem 0.75rem;
    border-radius: 4px;
    font-size: 0.75rem;
    line-height: 1.4;
    white-space: normal;
    max-width: 300px;
    width: max-content;

    /* Hidden by default */
    opacity: 0;
    pointer-events: none;
    transition: opacity 0.2s ease;
    z-index: 100;
}

/* Show tooltip on hover AND focus (keyboard accessibility) */
.statement__text[data-tooltip]:hover::after,
.statement__text[data-tooltip]:focus::after {
    opacity: 1;
}

/* Tooltip arrow */
.statement__text[data-tooltip]::before {
    content: '';
    position: absolute;
    bottom: 100%;
    left: 50%;
    transform: translateX(-50%) translateY(-2px);
    border: 6px solid transparent;
    border-top-color: var(--text);
    opacity: 0;
    transition: opacity 0.2s ease;
    z-index: 101;
}

.statement__text[data-tooltip]:hover::before,
.statement__text[data-tooltip]:focus::before {
    opacity: 1;
}

/* Make statement text focusable for keyboard users */
.statement__text[data-tooltip] {
    display: inline-block;
    tabindex: 0;
    outline-offset: 2px;
}
```

**Accessibility notes:**
- `tabindex="0"` makes element keyboard focusable so tooltip shows on focus
- `:focus` pseudo-class triggers tooltip for keyboard users
- `cursor: help` indicates additional information available
- `data-tooltip` attribute holds description text (populated from backend)

### Pattern 2: Dynamic Button Text with Selection Count

**What:** Update button text in real-time as checkboxes are selected/deselected
**When to use:** Action bar button needs to show live count of selected statements

**Example:**
```javascript
// Source: Existing selection.js pattern, extended for total count
const updateActionBar = (state) => {
    const actionBar = document.getElementById('action-bar');
    const createBtn = document.getElementById('create-btn');
    if (!actionBar || !createBtn) return;

    // Count total selections across ALL sections
    const totalSelections = Object.values(state.selections)
        .reduce((sum, arr) => sum + arr.length, 0);

    // Show action bar and update button text
    if (totalSelections > 0) {
        actionBar.classList.remove('hidden');
        createBtn.disabled = false;
        createBtn.textContent = `Create Job Description (${totalSelections} selected)`;
    } else {
        actionBar.classList.remove('hidden'); // Keep visible but disabled
        createBtn.disabled = true;
        createBtn.textContent = 'Create Job Description (select statements first)';
    }
};

// Subscribe to state changes (already implemented in selection.js)
store.subscribe((state) => {
    updateActionBar(state);
});
```

**Key insights:**
- `Object.values(state.selections).reduce()` aggregates counts from all sections
- Button remains visible but disabled when count is zero (better UX than hiding)
- Text updates synchronously with state changes via reactive store pattern

### Pattern 3: Always-Visible Provenance Labels

**What:** Ensure source attribution is always displayed below statement text, not on hover
**When to use:** Every statement needs permanent provenance label per requirements

**Example:**
```javascript
// Source: Existing accordion.js createAccordionSection function
// Provenance label HTML structure (already implemented):
li.innerHTML = `
    <label class="statement__label">
        <input type="checkbox" class="statement__checkbox"
               data-section="${sectionId}"
               data-id="${stmtId}"
               ${isSelected ? 'checked' : ''}>
        <span class="statement__content">
            <span class="statement__text"
                  ${stmt.description ? `data-tooltip="${escapeHtml(stmt.description)}"` : ''}>
                ${escapeHtml(stmt.text)}
            </span>
            <span class="statement__source">from ${escapeHtml(sourceText)}</span>
        </span>
        ${proficiencyHtml}
    </label>
`;
```

**CSS for always-visible provenance:**
```css
/* Source: Existing accordion.css */
.statement__source {
    display: block;  /* Always visible, not display:none */
    font-size: 0.75rem;
    color: var(--text-light);
    font-style: italic;
    margin-top: 0.25rem;
}
```

**Verification checklist:**
- [ ] `display: block` or `display: inline` (never `display: none`)
- [ ] No `:hover` or `:focus` pseudo-classes controlling visibility
- [ ] No JavaScript toggling visibility based on interaction
- [ ] Visual inspection confirms labels visible at all times

### Pattern 4: Checkbox Selection State Persistence

**What:** Persist selections across page refreshes using localStorage via reactive store
**When to use:** User selections must survive browser refresh (already implemented)

**Example:**
```javascript
// Source: Existing state.js pattern (no changes needed)
const STORAGE_KEY = 'jdBuilderState';

const notify = () => {
    listeners.forEach(fn => fn(state));
    try {
        localStorage.setItem(STORAGE_KEY, JSON.stringify(state));
    } catch (e) {
        console.warn('localStorage save failed:', e);
    }
};

// Automatically persists on every state change via Proxy pattern
store.setSelections(sectionId, newSelections); // triggers notify() → saves to localStorage
```

**Already implemented correctly** - no changes required for this phase.

### Anti-Patterns to Avoid

- **Using `title` attribute for tooltips:** Not keyboard accessible; doesn't work on mobile; can't be styled
- **Hiding provenance on hover:** Requirements specify "always visible" - must be permanently displayed
- **Separate "Generate Overview" and "Create JD" buttons:** Requirements specify single button only
- **jQuery for DOM manipulation:** App uses vanilla JavaScript throughout; don't introduce jQuery dependency
- **Bootstrap tooltip component:** Requires Popper.js dependency; CSS-only solution is lighter and sufficient

## Don't Hand-Roll

Problems that look simple but have existing solutions:

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| Tooltip positioning logic | Custom JavaScript tooltip engine | CSS ::after with transform | Built-in browser positioning; no JS overhead; accessible by default |
| Selection count aggregation | Manual loop through checkboxes | Reactive store with subscription pattern | Already implemented; centralized state prevents bugs |
| Checkbox state persistence | Custom localStorage wrapper | Existing state.js Proxy pattern | Already handles serialization, quota errors, validation |
| Statement rendering | Manual DOM construction per tab | Extend existing accordion.js pattern | Consistent with current implementation; tested and working |

**Key insight:** This phase extends existing, working patterns rather than building new infrastructure. The accordion, selection, and state management systems already handle 90% of requirements. Focus on incremental enhancements, not rewrites.

## Common Pitfalls

### Pitfall 1: Tooltip Overflow/Clipping

**What goes wrong:** Tooltips appear cut off at container edges or viewport boundaries
**Why it happens:** Fixed positioning without boundary detection; long descriptions exceed max-width
**How to avoid:**
- Set reasonable `max-width: 300px` on tooltip
- Use `white-space: normal` to allow wrapping
- Position tooltips `bottom: 100%` (above element) to avoid lower viewport clipping
- For elements near screen edges, accept minor clipping over complex repositioning logic
**Warning signs:** Tooltip text truncated; tooltip extends beyond visible area; horizontal scrollbar appears

### Pitfall 2: Tooltip Flickering on Hover Transition

**What goes wrong:** Tooltip flickers or disappears when mouse moves from element to tooltip
**Why it happens:** Gap between element and tooltip breaks hover state
**How to avoid:**
- Use `transform: translateY(-8px)` to position tooltip close to element
- Set `pointer-events: none` on tooltip so mouse events pass through
- Add small `transition-delay` on opacity fade-out (0.1s) to reduce flickering perception
**Warning signs:** Tooltip disappears when hovering near element edge; tooltip flashes rapidly

### Pitfall 3: Missing Description Data for Tooltips

**What goes wrong:** Tooltips don't appear because backend doesn't provide description text
**Why it happens:** Assuming all proficiency items have descriptions; not handling missing data gracefully
**How to avoid:**
- Conditionally add `data-tooltip` attribute only when `stmt.description` exists
- Don't apply tooltip styles to elements without `data-tooltip` attribute
- Backend must populate `description` field for Work Activities, Skills, Abilities, Knowledge
- Log warning in console if proficiency item lacks description (helps debugging)
**Warning signs:** No tooltip appears on hover; empty tooltip shows; undefined/null appears in tooltip

### Pitfall 4: Provenance Label Hidden by Existing CSS

**What goes wrong:** Provenance labels invisible despite being in HTML
**Why it happens:** Inherited `display: none` or `visibility: hidden` from parent/global styles
**How to avoid:**
- Explicit `display: block` on `.statement__source` class
- Check for conflicting rules in accordion.css or main.css
- Use browser DevTools to inspect computed styles
- Visual regression test: compare before/after provenance visibility
**Warning signs:** HTML contains provenance text but nothing renders; DevTools shows `display: none` computed

### Pitfall 5: Button Text Update Race Condition

**What goes wrong:** Button shows incorrect count temporarily or doesn't update
**Why it happens:** Direct DOM manipulation conflicts with reactive store updates
**How to avoid:**
- Only update button text in `updateActionBar()` function subscribed to store
- Never manually set `textContent` outside subscription callbacks
- Store subscription triggers on every `setState()` call automatically
- Use single source of truth (store state) for count calculation
**Warning signs:** Button count lags behind selections; count decreases when checking boxes; count shows 0 when items selected

### Pitfall 6: Checkbox Events Not Firing on Dynamically Rendered Content

**What goes wrong:** Checkboxes added after page load don't trigger selection handlers
**Why it happens:** Event listeners attached to elements before they exist in DOM
**How to avoid:**
- Use event delegation: attach listener to `.jd-sections` container (permanent element)
- Filter for `.statement__checkbox` class in event handler
- Already implemented correctly in selection.js: `document.querySelector('.jd-sections').addEventListener('change', ...)`
**Warning signs:** Checkboxes in new tabs don't respond to clicks; console shows no errors; selections don't persist

## Code Examples

Verified patterns from official sources:

### Accessible Tooltip HTML Structure

```html
<!-- Source: ARIA tooltip role MDN + inclusive-components.design -->
<span class="statement__content">
    <span class="statement__text"
          data-tooltip="Identifying the underlying principles, reasons or facts of information by breaking down information or data into separate parts."
          tabindex="0">
        Analyzing Data or Information
    </span>
    <span class="statement__source">from Work Activities</span>
</span>
```

**Key attributes:**
- `data-tooltip`: Holds description text for CSS ::after content
- `tabindex="0"`: Makes text focusable for keyboard users
- CSS applies `:hover` and `:focus` pseudo-classes to show tooltip

### Complete Statement Row with All Requirements

```html
<!-- Source: Existing accordion.js pattern, extended for tooltips -->
<li class="statement">
    <label class="statement__label">
        <input type="checkbox" class="statement__checkbox"
               data-section="key_activities"
               data-id="key_activities-0"
               checked>
        <span class="statement__content">
            <span class="statement__text"
                  data-tooltip="Description from OaSIS API"
                  tabindex="0">
                Analyzing Data or Information
            </span>
            <span class="statement__source">from Work Activities</span>
        </span>
        <div class="proficiency-rating"
             aria-label="Level 5"
             data-full-label="5 - Highest Level"
             tabindex="0">
            <span class="rating-circles" aria-hidden="true">●●●●●</span>
            <span class="rating-label">L5</span>
        </div>
    </label>
</li>
```

**Meets all requirements:**
- ✅ SEL-01: Checkbox present
- ✅ SEL-02: Proficiency circles display (●●●●●)
- ✅ SEL-03: Provenance label visible ("from Work Activities")
- ✅ SEL-04: Tooltip on hover via `data-tooltip` attribute
- ✅ Accessible: keyboard focusable text and proficiency rating

### Consolidated Action Button HTML

```html
<!-- Source: Requirements SEL-05 single button specification -->
<footer id="action-bar" class="action-bar">
    <button id="create-btn" class="btn btn--primary" disabled>
        Create Job Description (select statements first)
    </button>
</footer>
```

**Changes from current implementation:**
- **REMOVE:** `<button id="generate-btn">Generate Overview</button>`
- **KEEP:** Single `create-btn` with dynamic text update
- **UPDATE:** Button text includes selection count: `Create Job Description (12 selected)`

### Tooltip CSS with WCAG 2.1 Compliance

```css
/* Source: Inclusive Components tooltips-toggletips pattern */
.statement__text[data-tooltip] {
    position: relative;
    cursor: help;
    display: inline-block;
    outline-offset: 2px;
}

.statement__text[data-tooltip]::after {
    content: attr(data-tooltip);

    /* Positioning */
    position: absolute;
    bottom: calc(100% + 8px);
    left: 50%;
    transform: translateX(-50%);

    /* Box model */
    padding: 0.5rem 0.75rem;
    max-width: 300px;
    width: max-content;

    /* Typography */
    font-size: 0.75rem;
    line-height: 1.4;
    white-space: normal;
    text-align: left;

    /* Styling */
    background: #333;
    color: white;
    border-radius: 4px;
    box-shadow: 0 2px 8px rgba(0,0,0,0.15);

    /* Interaction */
    opacity: 0;
    pointer-events: none;
    transition: opacity 0.2s ease;
    z-index: 100;
}

/* Show on hover AND focus (WCAG 2.1 SC 1.4.13) */
.statement__text[data-tooltip]:hover::after,
.statement__text[data-tooltip]:focus::after {
    opacity: 1;
}

/* Dismiss with Escape key - handled in JavaScript */
document.addEventListener('keydown', (e) => {
    if (e.key === 'Escape') {
        document.activeElement.blur();
    }
});
```

**WCAG compliance:**
- ✅ SC 1.4.13 Content on Hover or Focus: Tooltip dismissible via Escape key
- ✅ SC 2.1.1 Keyboard: Tooltip accessible via focus (tabindex="0")
- ✅ SC 1.4.3 Contrast: Black background (#333) on white text meets AA

## State of the Art

| Old Approach | Current Approach | When Changed | Impact |
|--------------|------------------|--------------|--------|
| HTML `title` attribute | CSS ::after pseudo-elements | WCAG 2.1 (2018) | Keyboard accessible, customizable styling |
| Inline event handlers | Event delegation | Modern JS best practices | Performance, works with dynamic content |
| jQuery `$().text()` updates | Reactive store subscriptions | Modern state management (2020+) | Single source of truth, predictable updates |
| Separate Overview/Create buttons | Single unified Create button | OaSIS UX pattern | Simplified workflow, matches source system |

**Deprecated/outdated:**
- `title` attribute for interactive tooltips: Not keyboard accessible, no mobile support
- Bootstrap 4 Tooltip (requires Popper.js): Heavy dependency for simple use case
- Manual checkbox loop counting: Error-prone, doesn't scale with dynamic content
- Hardcoded button text in HTML: Can't update dynamically, requires JavaScript anyway

## Open Questions

Things that couldn't be fully resolved:

1. **Description Text Source for Tooltips**
   - What we know: OaSIS provides descriptions for Work Activities, Skills, Abilities, Knowledge
   - What's unclear: Whether parser currently extracts description text or just names/levels
   - Recommendation:
     - Verify parser.py extracts description field from OaSIS API response
     - If not present, add extraction in Phase 08-D tasks
     - Map description to statement rows in backend before rendering
     - Example: Work Activity "Analyzing Data or Information" → description from OaSIS element data

2. **Tab Context Adaptation**
   - What we know: Current accordion.js renders Step 10 sections (key_activities, skills, etc.)
   - What's unclear: Whether Phase 08-C creates new tab structure or reuses accordion pattern
   - Recommendation:
     - If Phase 08-C creates separate tab components, extend statement rendering to tab context
     - If tabs contain accordions, no structural changes needed
     - Either way, same checkbox/tooltip/provenance rendering applies

3. **Generate Overview Button Removal**
   - What we know: Requirements specify single "Create JD" button only
   - What's unclear: Whether Overview generation feature is completely removed or just the separate button
   - Recommendation:
     - Remove "Generate Overview" button from action bar
     - Keep Overview generation as automatic step during "Create JD" process
     - Overview still generated, just not triggered by separate button
     - Single button simplifies UX per requirements

## Sources

### Primary (HIGH confidence)

- **Existing codebase:**
  - `static/js/accordion.js` - Statement rendering with checkboxes, proficiency, source labels
  - `static/js/selection.js` - Checkbox event handling, state updates, button text updates
  - `static/js/state.js` - Reactive store pattern, localStorage persistence
  - `static/css/accordion.css` - Statement styling, proficiency circles, tooltip patterns
  - `.planning/phases/06-enhanced-ui-display/06-CONTEXT.md` - Step 9/10 specifications
  - `.planning/phases/06-enhanced-ui-display/OASIS-HTML-REFERENCE.md` - Source system UI patterns

- **Official documentation:**
  - [ARIA: tooltip role - MDN](https://developer.mozilla.org/en-US/docs/Web/Accessibility/ARIA/Roles/tooltip_role) - ARIA tooltip semantics
  - [Tooltips & Toggletips - Inclusive Components](https://inclusive-components.design/tooltips-toggletips/) - Accessible tooltip patterns
  - [HTML title Attribute: Comprehensive Guide - CodeLucky](https://codelucky.com/html-title-attribute/) - Title attribute accessibility issues

### Secondary (MEDIUM confidence)

- [HTML5 Accessibility: title attribute use and abuse - TPGi](https://www.tpgi.com/html5-accessibility-chops-title-attribute-use-and-abuse/) - Why not to use title attribute
- [Tooltips in the time of WCAG 2.1 - Sarah Higley](https://sarahmhigley.com/writing/tooltips-in-wcag-21/) - WCAG compliance for tooltips
- [Accessible simple tooltip using ARIA and Vanilla Javascript - Van11y](https://van11y.net/accessible-simple-tooltip/) - Vanilla JS implementation examples
- Phase 08-C research (08-C-RESEARCH.md) - Tab structure patterns this phase builds upon

### Tertiary (LOW confidence)

- WebSearch results on checkbox counting patterns - General approaches, not library-specific
- WebSearch results on button text updates - Common patterns, needs validation against app's reactive store

## Metadata

**Confidence breakdown:**
- Standard stack: HIGH - No new dependencies; extends existing patterns
- Architecture (tooltips): HIGH - CSS ::after is well-documented, accessible pattern
- Architecture (button updates): HIGH - Already implemented in selection.js, just need to extend
- Architecture (provenance display): HIGH - Simple CSS change, already in HTML
- Pitfalls: HIGH - Based on common accessibility mistakes and existing codebase patterns

**Research date:** 2026-01-24
**Valid until:** 60 days (CSS and JavaScript patterns stable; no framework changes expected)

**Key implementation risks:**
- **LOW RISK:** Checkbox selection state management (already implemented and tested)
- **LOW RISK:** Proficiency circle display (already implemented in Phase 06)
- **LOW RISK:** Provenance label visibility (CSS change only)
- **MEDIUM RISK:** Tooltip implementation (need to populate description data from backend)
- **LOW RISK:** Button consolidation (simple HTML/JS change)

**What to validate during planning:**
- Confirm parser.py extracts description field for Work Activities, Skills, Abilities, Knowledge
- Verify Phase 08-C tab structure to ensure statement rendering adapts correctly
- Test tooltip positioning on statements near viewport edges
- Confirm "Generate Overview" removal aligns with overall workflow expectations
- Validate tooltip content doesn't contain HTML special characters (needs escaping)

**Ready for planning:** Yes - all technical approaches verified, existing patterns identified, risks assessed.
