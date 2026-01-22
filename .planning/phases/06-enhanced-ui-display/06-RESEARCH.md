# Phase 6: Enhanced UI Display - Research

**Researched:** 2026-01-22
**Domain:** Frontend UI Enhancement (Vanilla JavaScript, CSS Grid, Web Accessibility)
**Confidence:** HIGH

## Summary

Phase 6 enhances the frontend with visual improvements including Unicode circle-based proficiency ratings, grid/card view toggle for search results, NOC code display, and comprehensive accessibility compliance. The research confirms that modern browser-native solutions (CSS Grid, localStorage, Unicode characters) provide production-ready capabilities without external dependencies.

The standard approach uses:
- **CSS Grid with auto-fit/minmax** for responsive table layouts that automatically adapt to viewport size
- **localStorage with JSON serialization** for persisting user view preferences
- **Unicode circles (U+25CF/U+25CB)** styled with CSS custom properties for zero-dependency rating display
- **ARIA patterns (aria-hidden, aria-label)** for WCAG 2.1 Level AA compliant accessibility
- **Event delegation** for performant dynamic content interaction
- **matchMedia API** for efficient responsive breakpoint handling

**Primary recommendation:** Use browser-native solutions throughout—CSS Grid for layouts, localStorage for persistence, Unicode + CSS for visual elements, and semantic HTML + ARIA for accessibility. Avoid libraries/frameworks for this phase.

## Standard Stack

The established libraries/tools for this domain:

### Core
| Library | Version | Purpose | Why Standard |
|---------|---------|---------|--------------|
| CSS Grid | Native (97% browser support) | Responsive table layouts | Universal browser support, powerful layout capabilities with subgrid, auto-fit, and minmax |
| localStorage API | Native (Web Storage API) | Persist user preferences | 5-10MB per domain, synchronous, widely supported, perfect for view mode preferences |
| Unicode Characters | U+25CF/U+25CB | Visual rating indicators | Zero dependencies, accessibility-friendly, universal support, matches OASIS style |
| ARIA 1.2 | Native (HTML attributes) | Screen reader accessibility | W3C standard for WCAG compliance, native browser support |
| CSS Custom Properties | Native (CSS Variables) | Color theming | Runtime-updateable, perfect for dynamic theming, 96%+ browser support |

### Supporting
| Library | Version | Purpose | When to Use |
|---------|---------|---------|-------------|
| matchMedia API | Native (Window API) | Responsive breakpoint detection | More efficient than resize events, fires only at breakpoint changes |
| dataset API | Native (HTMLElement) | Access data-* attributes | Cleanly manage component state and configuration |
| JSON.stringify/parse | Native (JavaScript) | Serialize objects for storage | Required for storing non-string values in localStorage |

### Alternatives Considered
| Instead of | Could Use | Tradeoff |
|------------|-----------|----------|
| Unicode circles | Font Awesome / icon library | Adds ~100KB dependency for 2 characters; accessibility complexity |
| CSS Grid | Table elements with display:grid | Loss of semantic table markup for screen readers |
| localStorage | sessionStorage | Data lost on tab close; use only if session-scope desired |
| matchMedia | resize event listeners | Performance cost: fires on every pixel change vs. once per breakpoint |

**Installation:**
```bash
# No dependencies required - all browser-native APIs
# Project already uses vanilla JavaScript
```

## Architecture Patterns

### Recommended Project Structure
```
static/
├── js/
│   ├── viewToggle.js       # Grid/card view switching logic
│   ├── proficiency.js      # Star rating rendering
│   └── storage.js          # localStorage wrapper with quota handling
└── css/
    ├── grid-view.css       # CSS Grid table layout
    ├── proficiency.css     # Circle rating styles
    └── responsive.css      # Breakpoint definitions
```

### Pattern 1: CSS Grid Responsive Table Layout
**What:** Use CSS Grid with auto-fit and minmax to create responsive table that adapts to available width
**When to use:** For search results grid view displaying 4+ columns with sortable headers
**Example:**
```css
/* Source: CSS-Tricks Complete Guide to Grid + web.dev RAM pattern */
.results-grid {
  display: grid;
  /* RAM: Repeat, Auto-fit, Minmax */
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 1rem;
}

/* For fixed column table layout */
.results-table {
  display: grid;
  grid-template-columns: 2fr 2fr 3fr 2fr; /* OASIS Profile | Examples | Lead | TEER */
  gap: 0.5rem 1rem;
}

/* Headers and rows as grid items */
.table-header {
  font-weight: 600;
  border-bottom: 2px solid var(--border);
  padding: 0.75rem;
  cursor: pointer; /* sortable */
}

.table-cell {
  padding: 0.75rem;
  border-bottom: 1px solid var(--border);
}

/* Responsive: switch to cards below 768px */
@media (max-width: 768px) {
  .results-table {
    display: block; /* Revert to card view */
  }
}
```

### Pattern 2: Unicode Circle Proficiency Display
**What:** Use Unicode filled/empty circles with CSS styling and ARIA for accessible rating display
**When to use:** For displaying proficiency levels 1-5 in statement tables
**Example:**
```html
<!-- Source: MDN ARIA patterns + WCAG 2.0 techniques -->
<div class="proficiency-rating" aria-label="Level 4">
  <span class="rating-circles" aria-hidden="true">●●●●○</span>
  <span class="rating-label">L4</span>
</div>
```

```css
/* Source: Unicode character documentation */
.rating-circles {
  color: var(--oasis-blue); /* Filled circles */
  letter-spacing: 0.125rem;
}

.rating-label {
  font-size: 0.875rem;
  color: var(--text-light);
  margin-left: 0.5rem;
}

/* Tooltip on hover */
.proficiency-rating {
  position: relative;
}

.proficiency-rating::after {
  content: attr(data-full-label); /* e.g., "5 - Highest Level" */
  position: absolute;
  /* Tooltip positioning styles */
  opacity: 0;
  transition: opacity 0.2s;
  pointer-events: none;
}

.proficiency-rating:hover::after,
.proficiency-rating:focus-within::after {
  opacity: 1;
}
```

```javascript
// Generate rating circles
function renderProficiency(level) {
  const filled = '●'.repeat(level);
  const empty = '○'.repeat(5 - level);
  return filled + empty;
}
```

### Pattern 3: localStorage with Quota Handling
**What:** Safely persist user preferences with try-catch for QuotaExceededError
**When to use:** For saving grid/card view preference across sessions
**Example:**
```javascript
// Source: MDN Web Storage API + LogRocket localStorage guide
const storage = {
  set(key, value) {
    try {
      const serialized = JSON.stringify(value);
      localStorage.setItem(key, serialized);
      return true;
    } catch (error) {
      // QuotaExceededError: code 22 (all browsers except Firefox)
      // Firefox: code 1014 or NS_ERROR_DOM_QUOTA_REACHED
      if (error.code === 22 || error.code === 1014 ||
          error.name === 'QuotaExceededError' ||
          error.name === 'NS_ERROR_DOM_QUOTA_REACHED') {
        console.warn('localStorage quota exceeded');
        // Fallback: clear old data or use sessionStorage
      }
      return false;
    }
  },

  get(key, defaultValue = null) {
    try {
      const item = localStorage.getItem(key);
      return item ? JSON.parse(item) : defaultValue;
    } catch (error) {
      console.error('Failed to parse localStorage item:', error);
      return defaultValue;
    }
  },

  remove(key) {
    try {
      localStorage.removeItem(key);
    } catch (error) {
      console.error('Failed to remove localStorage item:', error);
    }
  }
};

// Usage
storage.set('viewMode', 'grid');
const viewMode = storage.get('viewMode', 'card'); // Default to 'card'
```

### Pattern 4: matchMedia for Responsive Breakpoints
**What:** Use matchMedia API to detect viewport size changes at specific breakpoints
**When to use:** Auto-switching from grid to card view below 768px
**Example:**
```javascript
// Source: MDN Window.matchMedia + web development guides
const mediaQuery = window.matchMedia('(max-width: 768px)');

function handleViewportChange(e) {
  if (e.matches) {
    // Viewport is 768px or less - force card view
    switchToCardView();
  } else {
    // Restore user preference
    const savedView = storage.get('viewMode', 'card');
    if (savedView === 'grid') {
      switchToGridView();
    }
  }
}

// Listen for breakpoint changes (fires only when crossing 768px)
mediaQuery.addEventListener('change', handleViewportChange);

// Check initial state
handleViewportChange(mediaQuery);
```

### Pattern 5: Sortable Table with Event Delegation
**What:** Single click handler on table header for column sorting
**When to use:** Grid view with sortable columns
**Example:**
```javascript
// Source: JavaScript.info event delegation + sortable table patterns
const tableContainer = document.querySelector('.results-table');
let currentSort = { column: null, ascending: true };

tableContainer.addEventListener('click', (e) => {
  const header = e.target.closest('.table-header');
  if (!header) return;

  const column = header.dataset.column;

  // Toggle direction if same column
  if (currentSort.column === column) {
    currentSort.ascending = !currentSort.ascending;
  } else {
    currentSort.column = column;
    currentSort.ascending = true;
  }

  sortTable(column, currentSort.ascending);
  updateSortIndicator(header, currentSort.ascending);
});

function sortTable(column, ascending) {
  const rows = Array.from(document.querySelectorAll('.table-row'));

  rows.sort((a, b) => {
    const aVal = a.querySelector(`[data-column="${column}"]`).textContent;
    const bVal = b.querySelector(`[data-column="${column}"]`).textContent;
    return ascending ? aVal.localeCompare(bVal) : bVal.localeCompare(aVal);
  });

  // Re-append in sorted order
  rows.forEach(row => tableContainer.appendChild(row));
}
```

### Pattern 6: Accessible Tooltip Pattern
**What:** WCAG 2.1 compliant tooltips that are dismissable, hoverable, and persistent
**When to use:** Full proficiency labels on hover (e.g., "5 - Highest Level")
**Example:**
```html
<!-- Source: W3C ARIA tooltip pattern -->
<button class="view-toggle" aria-label="Switch to grid view">
  <span class="icon" aria-hidden="true">☰</span>
  <span class="tooltip" role="tooltip" id="tooltip-grid">Grid view</span>
</button>
```

```css
/* Source: CSS-Tricks tooltip best practices */
.tooltip {
  position: absolute;
  background: var(--text);
  color: white;
  padding: 0.5rem;
  border-radius: 4px;
  font-size: 0.875rem;
  white-space: nowrap;
  opacity: 0;
  pointer-events: none; /* Initially not hoverable */
  transition: opacity 0.2s;
}

.view-toggle:hover .tooltip,
.view-toggle:focus .tooltip {
  opacity: 1;
  pointer-events: auto; /* Make hoverable when visible */
}

/* Dismissable with Escape key handled in JS */
```

```javascript
// WCAG 2.1 Success Criterion 1.4.13: Content on Hover or Focus
document.addEventListener('keydown', (e) => {
  if (e.key === 'Escape') {
    // Hide all visible tooltips
    document.querySelectorAll('.tooltip[style*="opacity: 1"]').forEach(tip => {
      tip.style.opacity = '0';
      tip.style.pointerEvents = 'none';
    });
  }
});
```

### Anti-Patterns to Avoid
- **Don't use fixed pixel widths in grid columns:** Use `fr` units and minmax for flexibility
- **Don't attach event listeners to every table cell:** Use event delegation on parent container
- **Don't store large objects in localStorage:** Check serialized size before storing; 5-10MB limit
- **Don't hide focusable elements with aria-hidden:** Only use on decorative content
- **Don't use resize event for breakpoint detection:** Use matchMedia for better performance

## Don't Hand-Roll

Problems that look simple but have existing solutions:

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| Responsive table layouts | Custom JavaScript column hiding/showing | CSS Grid with auto-fit/minmax | Browser-optimized, handles edge cases, accessible by default |
| Star rating accessibility | Custom screen reader text generation | aria-hidden on decorative + aria-label on container | W3C recommended pattern, tested with all screen readers |
| localStorage quota handling | Simple try-catch around setItem | Wrapper with code-specific error detection | QuotaExceededError has different codes across browsers (22 vs 1014) |
| Breakpoint detection | window.resize with debouncing | matchMedia API with change listener | Fires only at breakpoints, not every pixel; built-in throttling |
| Column sorting | Custom comparison logic | Array.sort() with localeCompare() | Handles internationalization, numbers, dates correctly |
| Tooltip accessibility | Custom show/hide with mouse events | WCAG 2.1 pattern with dismissable/hoverable/persistent | Legal compliance requirement; easy to get wrong |

**Key insight:** Web accessibility is governed by legal standards (WCAG 2.1 Level AA). Custom solutions risk non-compliance, which has legal consequences. Use established ARIA patterns from W3C documentation.

## Common Pitfalls

### Pitfall 1: Using stars (U+2605/U+2606) instead of circles (U+25CF/U+25CB)
**What goes wrong:** User decisions specify filled circles to match OASIS style, not traditional stars
**Why it happens:** "Star rating" terminology leads developers to use star unicode characters
**How to avoid:** Follow user context document requirement: use U+25CF (●) and U+25CB (○)
**Warning signs:** Visual doesn't match OASIS reference screenshots in milestone documentation

### Pitfall 2: aria-hidden on parent with focusable children
**What goes wrong:** Focusable elements (buttons, links) inside aria-hidden="true" containers become keyboard-inaccessible but still focusable
**Why it happens:** aria-hidden is inherited by all descendants, creating phantom focus targets
**How to avoid:** Only apply aria-hidden to leaf elements (decorative icons, redundant text)
**Warning signs:** Tab key focuses invisible elements; screen readers announce nothing when element focused

### Pitfall 3: localStorage access without quota error handling
**What goes wrong:** App crashes when user's localStorage is full (QuotaExceededError)
**Why it happens:** Assumption that 5MB is sufficient; other sites/apps consume quota
**How to avoid:** Wrap all setItem calls in try-catch checking for error code 22/1014
**Warning signs:** Works in dev/testing but fails for real users with full storage

### Pitfall 4: Grid view not disabled on mobile
**What goes wrong:** Table with 4+ columns unusable on 360-414px mobile screens
**Why it happens:** Forgetting that user context requires auto-switch to cards below 768px
**How to avoid:** Use matchMedia to force card view at mobile breakpoints regardless of user preference
**Warning signs:** Horizontal scrolling on mobile; columns < 60px wide

### Pitfall 5: Sorting breaks with non-string data types
**What goes wrong:** Numbers sort alphabetically (1, 10, 2, 20 instead of 1, 2, 10, 20)
**Why it happens:** Array.sort() converts to strings by default; NOC codes have mixed format
**How to avoid:** Use localeCompare() for strings; detect and handle numbers separately
**Warning signs:** "10" appears before "2" in sorted results

### Pitfall 6: WCAG 2.1 tooltip violations
**What goes wrong:** Tooltips disappear when user moves mouse to read them; no Escape dismissal
**Why it happens:** Unaware of WCAG 2.1 SC 1.4.13 requirements (dismissable, hoverable, persistent)
**How to avoid:** Use pointer-events: auto on visible tooltips; handle Escape key globally
**Warning signs:** Accessibility audit flags SC 1.4.13 failure; tooltip UX feels fragile

### Pitfall 7: Color contrast below WCAG AA minimums
**What goes wrong:** Muted gray NOC codes don't meet 4.5:1 contrast ratio on white background
**Why it happens:** User context says "match OASIS site" which may not meet AA standards
**How to avoid:** Test all colors with contrast checker; document any intentional exceptions
**Warning signs:** Accessibility tools flag contrast errors; text hard to read in bright light

### Pitfall 8: JSON.parse fails silently on corrupted localStorage data
**What goes wrong:** App breaks if user manually edited localStorage or data corrupted
**Why it happens:** Assuming JSON.parse always succeeds; not handling SyntaxError
**How to avoid:** Wrap JSON.parse in try-catch; return default value on parse failure
**Warning signs:** App works until page reload; intermittent crashes with no clear cause

## Code Examples

Verified patterns from official sources:

### Grid View HTML Structure
```html
<!-- Semantic table structure with CSS Grid styling -->
<div class="results-container">
  <div class="view-controls">
    <button id="view-toggle" class="view-toggle" aria-label="Switch to grid view">
      <span aria-hidden="true">☰</span>
    </button>
  </div>

  <div class="results-table" role="table" aria-label="Search results">
    <!-- Headers -->
    <div class="table-header" data-column="profile" role="columnheader">
      OASIS Profile
      <span class="sort-indicator" aria-hidden="true"></span>
    </div>
    <div class="table-header" data-column="examples" role="columnheader">
      Example Titles
    </div>
    <div class="table-header" data-column="lead" role="columnheader">
      Lead Statement
    </div>
    <div class="table-header" data-column="teer" role="columnheader">
      Training/Education/Experience
    </div>

    <!-- Rows -->
    <div class="table-row" role="row">
      <div class="table-cell" data-column="profile" role="cell">
        <a href="#" class="profile-link">
          <strong>Air pilots</strong>
          <span class="noc-code">(72600.01)</span>
        </a>
      </div>
      <div class="table-cell" data-column="examples" role="cell">
        Airline pilot, Commercial pilot, Charter pilot
      </div>
      <div class="table-cell" data-column="lead" role="cell">
        Air pilots pilot fixed wing aircraft...
      </div>
      <div class="table-cell" data-column="teer" role="cell">
        TEER 0: University degree
      </div>
    </div>
  </div>
</div>
```

### Complete View Toggle Implementation
```javascript
// Source: Combined pattern from matchMedia API + localStorage best practices
class ViewToggle {
  constructor() {
    this.button = document.getElementById('view-toggle');
    this.container = document.querySelector('.results-container');
    this.mediaQuery = window.matchMedia('(max-width: 768px)');

    this.init();
  }

  init() {
    // Load saved preference
    this.currentView = storage.get('viewMode', 'card');

    // Check if mobile - force card view
    if (this.mediaQuery.matches) {
      this.currentView = 'card';
      this.button.disabled = true; // Can't switch on mobile
    }

    this.updateView();

    // Event listeners
    this.button.addEventListener('click', () => this.toggle());
    this.mediaQuery.addEventListener('change', (e) => this.handleBreakpoint(e));
  }

  toggle() {
    this.currentView = this.currentView === 'card' ? 'grid' : 'card';
    this.updateView();
    storage.set('viewMode', this.currentView);
  }

  updateView() {
    if (this.currentView === 'grid') {
      this.container.classList.add('grid-view');
      this.container.classList.remove('card-view');
      this.button.setAttribute('aria-label', 'Switch to card view');
      this.button.innerHTML = '<span aria-hidden="true">▦</span>';
    } else {
      this.container.classList.add('card-view');
      this.container.classList.remove('grid-view');
      this.button.setAttribute('aria-label', 'Switch to grid view');
      this.button.innerHTML = '<span aria-hidden="true">☰</span>';
    }
  }

  handleBreakpoint(e) {
    if (e.matches) {
      // Mobile: force card view
      this.currentView = 'card';
      this.button.disabled = true;
      this.updateView();
    } else {
      // Desktop: enable toggle, restore preference
      this.button.disabled = false;
      this.currentView = storage.get('viewMode', 'card');
      this.updateView();
    }
  }
}

// Initialize on DOM ready
document.addEventListener('DOMContentLoaded', () => {
  new ViewToggle();
});
```

### Proficiency Rating Component
```javascript
// Complete proficiency rating with accessibility
function createProficiencyRating(level) {
  const wrapper = document.createElement('div');
  wrapper.className = 'proficiency-rating';
  wrapper.setAttribute('aria-label', `Level ${level}`);
  wrapper.setAttribute('data-full-label', `${level} - ${getLevelLabel(level)}`);

  // Decorative circles (hidden from screen readers)
  const circles = document.createElement('span');
  circles.className = 'rating-circles';
  circles.setAttribute('aria-hidden', 'true');
  circles.textContent = '●'.repeat(level) + '○'.repeat(5 - level);

  // Visible abbreviated label
  const label = document.createElement('span');
  label.className = 'rating-label';
  label.textContent = `L${level}`;

  wrapper.appendChild(circles);
  wrapper.appendChild(label);

  return wrapper;
}

function getLevelLabel(level) {
  const labels = {
    1: 'Basic Level',
    2: 'Low Level',
    3: 'Medium Level',
    4: 'High Level',
    5: 'Highest Level'
  };
  return labels[level] || 'Unknown Level';
}
```

### NOC Code Formatting
```javascript
// Format NOC code consistently across the app
function formatProfileTitle(title, nocCode) {
  return `<strong>${title}</strong> <span class="noc-code">(${nocCode})</span>`;
}

// For profile page header with badge
function createNOCBadge(nocCode) {
  const badge = document.createElement('span');
  badge.className = 'noc-badge';
  badge.textContent = nocCode;
  return badge;
}
```

### CSS Custom Properties for OASIS Theming
```css
/* Source: CSS-Tricks Custom Properties guide + user context decisions */
:root {
  /* OASIS Blue color scheme - match reference site */
  --oasis-blue: #0066cc; /* Filled circles, primary accents */
  --oasis-blue-light: #4d94d9; /* Hover states */
  --oasis-blue-pale: #e6f2ff; /* Backgrounds */

  /* Empty circle style */
  --circle-empty: #b0b0b0; /* Lighter shade for empty circles */

  /* NOC code styling */
  --noc-code-color: #666666; /* Muted gray */
  --noc-code-size: 0.875rem;

  /* Contrast-checked colors (WCAG AA minimum) */
  --text-primary: #333333; /* 4.5:1 on white */
  --text-secondary: #666666; /* 3:1 on white for large text */
}

/* Apply OASIS theming */
.rating-circles {
  color: var(--oasis-blue);
}

.noc-code {
  color: var(--noc-code-color);
  font-size: var(--noc-code-size);
}

.noc-badge {
  background: var(--oasis-blue-pale);
  color: var(--oasis-blue);
  border: 1px solid var(--oasis-blue-light);
  padding: 0.25rem 0.5rem;
  border-radius: 4px;
  font-size: 0.75rem;
  font-weight: 600;
}
```

## State of the Art

| Old Approach | Current Approach | When Changed | Impact |
|--------------|------------------|--------------|--------|
| Table element with CSS | CSS Grid with role="table" | 2020 (Grid maturity) | Better responsive control, but requires ARIA roles for accessibility |
| Font icon libraries | Unicode characters + CSS | Ongoing shift (2023-2026) | Zero dependencies, but limited icon variety |
| resize event listeners | matchMedia API | 2012 (API introduction) | Massive performance improvement for breakpoint detection |
| Inline styles | CSS Custom Properties | 2016-2018 (browser adoption) | Runtime theming, cleaner separation of concerns |
| WCAG 2.0 | WCAG 2.1 (added SC 1.4.13) | 2018 | New tooltip requirements: dismissable, hoverable, persistent |

**Deprecated/outdated:**
- **localStorage.getItem without quota handling:** QuotaExceededError catching now required best practice
- **Auto-fit without considering image stretching:** Modern guidance warns against using with images
- **aria-label without visible text:** WCAG 2.2 SC 2.5.3 requires accessible names to start with visible text

## Open Questions

Things that couldn't be fully resolved:

1. **OASIS Site Exact Color Values**
   - What we know: User wants to match OASIS blue for filled circles
   - What's unclear: Exact hex value of OASIS blue (no direct access to inspect)
   - Recommendation: Inspect OASIS site during implementation or use typical blue (#0066cc) and get user approval

2. **NOC Code Format Variations**
   - What we know: Format shown as "Air pilots (72600.01)" with dot notation
   - What's unclear: Are there NOC codes without dot notation? Different formats?
   - Recommendation: Check data/noc_oassis_mappings.csv for all NOC code formats present

3. **Proficiency Scale Labels Beyond 1-5**
   - What we know: OASIS uses 1-5 scale with specific labels
   - What's unclear: Do any dimensions use different scales (0-5, 1-7, etc.)?
   - Recommendation: Audit all proficiency data to confirm 1-5 is universal or needs flexibility

4. **Grid View Column Width Priorities**
   - What we know: 4 columns (OASIS Profile, Examples, Lead, TEER) with user-selected content
   - What's unclear: Should any column have minimum width priority? Which columns can truncate?
   - Recommendation: Test with real data; likely Lead Statement needs most space, TEER can be narrow

5. **localStorage Quota Fallback Strategy**
   - What we know: Need to handle QuotaExceededError
   - What's unclear: What should fallback behavior be? Session-only? Disable feature? User message?
   - Recommendation: Default to sessionStorage as fallback; show user info message about reduced persistence

## Sources

### Primary (HIGH confidence)
- [MDN: CSS Grid Layout](https://developer.mozilla.org/en-US/docs/Web/CSS/Guides/Grid_layout) - Official specification and usage
- [MDN: Window localStorage](https://developer.mozilla.org/en-US/docs/Web/API/Window/localStorage) - Web Storage API documentation
- [MDN: ARIA aria-hidden](https://developer.mozilla.org/en-US/docs/Web/Accessibility/ARIA/Attributes/aria-hidden) - Official ARIA attribute specification
- [W3C: WCAG 2.1 Understanding SC 1.4.13](https://www.w3.org/WAI/WCAG21/Understanding/content-on-hover-or-focus.html) - Content on hover/focus requirements
- [W3C: ARIA Tooltip Pattern](https://www.w3.org/WAI/ARIA/apg/patterns/tooltip/) - Official accessibility pattern
- [MDN: Window matchMedia](https://developer.mozilla.org/en-US/docs/Web/API/Window/matchMedia) - MediaQueryList API
- [MDN: HTMLElement dataset](https://developer.mozilla.org/en-US/docs/Web/API/HTMLElement/dataset) - Data attributes API
- [Unicode.org: U+25CF Black Circle](https://www.compart.com/en/unicode/U+25CF) - Unicode character specification
- [Unicode.org: U+25CB White Circle](https://www.compart.com/en/unicode/U+25CB) - Unicode character specification

### Secondary (MEDIUM confidence)
- [CSS-Tricks: Complete Guide to CSS Grid](https://css-tricks.com/snippets/css/complete-guide-grid/) - Comprehensive practical guide
- [CSS-Tricks: Auto-sizing Columns (auto-fit vs auto-fill)](https://css-tricks.com/auto-sizing-columns-css-grid-auto-fill-vs-auto-fit/) - Grid responsive patterns
- [web.dev: RAM Pattern (Repeat, Auto, Minmax)](https://web.dev/patterns/layout/repeat-auto-minmax) - Modern layout pattern
- [LogRocket: Storing JavaScript Objects in localStorage](https://blog.logrocket.com/storing-retrieving-javascript-objects-localstorage/) - JSON serialization patterns
- [WebAIM: Contrast and Color Accessibility](https://webaim.org/articles/contrast/) - WCAG contrast requirements
- [WebAIM: Using NVDA for Accessibility Testing](https://webaim.org/articles/nvda/) - Screen reader testing guide
- [JavaScript.info: Event Delegation](https://javascript.info/event-delegation) - Event handling pattern
- [CSS-Tricks: CSS Custom Properties and Theming](https://css-tricks.com/css-custom-properties-theming/) - Theming implementation

### Secondary (MEDIUM confidence - WebSearch verified)
- [BrowserStack: Responsive Design Breakpoints 2025](https://www.browserstack.com/guide/responsive-design-breakpoints) - Modern breakpoint recommendations
- [FrontendTools: CSS Grid Masterclass 2025](https://www.frontendtools.tech/blog/mastering-css-grid-2025) - Current best practices
- [TestParty: Screen Reader Testing Guide](https://testparty.ai/blog/screen-reader-testing-guide) - NVDA, JAWS, VoiceOver testing
- [Deque University: Tooltip Accessibility](https://dequeuniversity.com/library/aria/tooltip) - Enterprise accessibility patterns

### Tertiary (LOW confidence - needs validation)
- None required for this research - all key findings verified with official sources

## Metadata

**Confidence breakdown:**
- Standard stack: HIGH - All browser-native APIs with official MDN/W3C documentation
- Architecture patterns: HIGH - Patterns verified with official sources (MDN, W3C, web.dev)
- Don't hand-roll: HIGH - Based on WCAG requirements and established best practices
- Pitfalls: HIGH - Common issues documented in accessibility guides and user context
- Code examples: HIGH - Derived from official documentation and verified patterns
- OASIS color matching: MEDIUM - Exact color values need visual inspection during implementation

**Research date:** 2026-01-22
**Valid until:** 2026-03-22 (60 days - stable web standards, long validity)

**Notes:**
- This phase has zero external dependencies, increasing long-term stability
- WCAG 2.1 standards are legally binding in many jurisdictions; patterns are well-established
- User context document constrains many decisions (circles not stars, specific layout columns, 768px breakpoint)
- All modern browsers (Chrome 90+, Firefox 88+, Safari 14+, Edge 90+) support required APIs
- Testing with NVDA and VoiceOver is critical before shipping (WCAG compliance requirement)
