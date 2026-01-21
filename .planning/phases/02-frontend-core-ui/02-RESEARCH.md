# Phase 2: Frontend Core UI - Research

**Researched:** 2026-01-21
**Domain:** Vanilla JavaScript UI with accordion, drag-and-drop, and state management
**Confidence:** HIGH

## Summary

This phase implements the interactive frontend for displaying NOC data organized by JD elements with selection capabilities. The project constraint is vanilla HTML/CSS/JS (no frameworks), which aligns well with modern browser capabilities in 2026.

Research confirms that all required UI patterns (accordion, drag-and-drop reordering, collapsible sidebar, sticky action bar, checkbox selection with highlighting) can be implemented effectively without frameworks using native browser APIs and minimal external libraries.

**Primary recommendation:** Use native HTML5 `<details>`/`<summary>` elements for accordions (accessibility built-in), SortableJS library for drag-and-drop reordering, and a simple Proxy-based state management pattern for selection tracking and persistence.

## Standard Stack

The established libraries/tools for this domain:

### Core
| Library | Version | Purpose | Why Standard |
|---------|---------|---------|--------------|
| Native HTML5 | - | `<details>`/`<summary>` for accordion | Built-in accessibility, no JS required for basic behavior |
| SortableJS | 1.15+ | Drag-and-drop reordering | De facto standard for sortable lists, framework-agnostic, touch support |
| Native localStorage | - | State persistence | Built into all browsers, no dependencies |
| Native CSS | - | Transitions, sticky positioning, flexbox layout | Modern CSS handles all layout requirements natively |

### Supporting
| Library | Version | Purpose | When to Use |
|---------|---------|---------|-------------|
| DragDropTouch polyfill | - | Touch support for drag-and-drop | Only if mobile support needed (not required per CONTEXT.md - desktop only) |

### Alternatives Considered
| Instead of | Could Use | Tradeoff |
|------------|-----------|----------|
| SortableJS | html5sortable | Smaller but less maintained; SortableJS has better docs |
| Native `<details>` | ARIA accordion pattern | Custom JS accordion offers more control but adds complexity |
| localStorage | sessionStorage | sessionStorage clears on tab close; localStorage persists across sessions |

**Installation:**
```html
<!-- CDN approach (recommended for demo simplicity) -->
<script src="https://cdn.jsdelivr.net/npm/sortablejs@1.15.0/Sortable.min.js"></script>
```

Or via npm if build tooling is added later:
```bash
npm install sortablejs
```

## Architecture Patterns

### Recommended Project Structure
```
static/
├── css/
│   ├── main.css          # Core layout and typography
│   ├── accordion.css     # Accordion-specific styles
│   ├── sidebar.css       # Collapsible sidebar styles
│   └── skeleton.css      # Loading state styles
├── js/
│   ├── main.js           # Entry point, initialization
│   ├── state.js          # State management (Proxy-based)
│   ├── api.js            # API client for Flask backend
│   ├── accordion.js      # Accordion behavior enhancement
│   ├── selection.js      # Checkbox selection logic
│   ├── search.js         # Per-section text filtering
│   └── sidebar.js        # Sidebar toggle logic
└── index.html            # Single page application
templates/
└── index.html            # Flask-served HTML (alternative to static)
```

### Pattern 1: Proxy-Based Reactive State
**What:** Use JavaScript Proxy to intercept state changes and trigger UI updates automatically
**When to use:** Managing selection state across multiple accordion sections
**Example:**
```javascript
// Source: Modern state management pattern (2026 trend)
const createStore = (initialState) => {
    const listeners = new Set();

    const state = new Proxy(initialState, {
        set(target, key, value) {
            target[key] = value;
            listeners.forEach(fn => fn(state));
            // Persist to localStorage
            localStorage.setItem('jdBuilderState', JSON.stringify(target));
            return true;
        }
    });

    return {
        getState: () => state,
        subscribe: (fn) => {
            listeners.add(fn);
            return () => listeners.delete(fn);
        }
    };
};

// Initialize with persisted state or defaults
const savedState = JSON.parse(localStorage.getItem('jdBuilderState')) || {
    selections: {
        key_activities: [],
        skills: [],
        effort: [],
        responsibility: [],
        working_conditions: []
    },
    sectionOrder: ['key_activities', 'skills', 'effort', 'responsibility', 'working_conditions']
};

const store = createStore(savedState);
```

### Pattern 2: Native `<details>`/`<summary>` Accordion
**What:** Use semantic HTML elements with CSS enhancement for accessible accordions
**When to use:** JD Element section accordions
**Example:**
```html
<!-- Source: MDN, W3C APG -->
<details class="jd-section" name="jd-accordion">
    <summary class="jd-section__header">
        <span class="jd-section__title">Key Activities</span>
        <span class="jd-section__count">(0 selected)</span>
    </summary>
    <div class="jd-section__content">
        <input type="search" class="jd-section__search"
               placeholder="Filter statements...">
        <ul class="jd-section__list">
            <!-- Statements rendered here -->
        </ul>
    </div>
</details>
```

```css
/* Exclusive accordion behavior - only one open at a time */
/* Note: name attribute on <details> enables this natively in modern browsers */
details[name="jd-accordion"] {
    border: 1px solid #e0e0e0;
    margin-bottom: 0.5rem;
}

details[name="jd-accordion"] > summary {
    padding: 1rem;
    cursor: pointer;
    list-style: none;
    display: flex;
    justify-content: space-between;
    align-items: center;
}

details[name="jd-accordion"] > summary::-webkit-details-marker {
    display: none;
}

details[name="jd-accordion"][open] > summary {
    border-bottom: 1px solid #e0e0e0;
}
```

### Pattern 3: SortableJS Section Reordering
**What:** Make accordion sections draggable for reordering
**When to use:** Allow managers to customize JD Element order
**Example:**
```javascript
// Source: SortableJS documentation
const accordionContainer = document.querySelector('.jd-sections');

const sortable = new Sortable(accordionContainer, {
    animation: 150,
    ghostClass: 'jd-section--dragging',
    handle: '.jd-section__drag-handle',
    onEnd: (evt) => {
        // Update state with new order
        const newOrder = Array.from(accordionContainer.children)
            .map(el => el.dataset.sectionId);
        store.getState().sectionOrder = newOrder;
    }
});
```

### Pattern 4: Checkbox Selection with Highlighting
**What:** Select statements with visual feedback
**When to use:** All statement items in accordion sections
**Example:**
```html
<li class="statement" data-id="stmt-1">
    <label class="statement__label">
        <input type="checkbox" class="statement__checkbox">
        <span class="statement__text">Analyze user requirements...</span>
        <span class="statement__source">from Main Duties</span>
    </label>
</li>
```

```css
/* Source: Modern CSS checkbox patterns */
.statement__checkbox:checked + .statement__text {
    background-color: #e3f2fd;
}

.statement__label:has(:checked) {
    background-color: #e3f2fd;
    border-left: 3px solid #1976d2;
}
```

### Pattern 5: Collapsible Sidebar
**What:** Sidebar showing selection summary, toggleable
**When to use:** Selection review panel
**Example:**
```css
/* Source: CSS collapsible sidebar patterns */
.sidebar {
    width: 300px;
    transition: width 0.3s ease, transform 0.3s ease;
    position: fixed;
    right: 0;
    top: 0;
    height: 100vh;
    background: #fff;
    box-shadow: -2px 0 5px rgba(0,0,0,0.1);
    overflow-y: auto;
}

.sidebar.collapsed {
    width: 0;
    transform: translateX(100%);
}

.sidebar__toggle {
    position: absolute;
    left: -40px;
    top: 50%;
    transform: translateY(-50%);
}
```

### Pattern 6: Sticky Action Bar
**What:** Bottom bar with "Generate Overview" button always visible
**When to use:** Primary action visibility
**Example:**
```css
/* Source: CSS-Tricks sticky footer patterns */
.action-bar {
    position: fixed;
    bottom: 0;
    left: 0;
    right: 0;
    padding: 1rem;
    background: #fff;
    border-top: 1px solid #e0e0e0;
    box-shadow: 0 -2px 10px rgba(0,0,0,0.1);
    z-index: 100;
}

/* Ensure main content has bottom padding to avoid overlap */
.main-content {
    padding-bottom: 80px;
}
```

### Anti-Patterns to Avoid
- **Don't use alert() for errors:** Use inline error messages with textContent/innerHTML instead
- **Don't attach event listeners to each item:** Use event delegation on the parent container
- **Don't store state in DOM attributes:** Use a centralized state object with localStorage backup
- **Don't use `aria-controls` extensively:** Support is limited to JAWS; rely on DOM proximity instead
- **Don't animate height directly:** Use max-height or the native `<details>` behavior for smooth accordions

## Don't Hand-Roll

Problems that look simple but have existing solutions:

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| Drag-and-drop reordering | Custom drag events | SortableJS | Touch support, edge cases, animation timing, accessibility |
| Accordion animation | Custom height transitions | Native `<details>` | Browser handles accessibility, keyboard nav, state |
| State persistence | Manual localStorage sync | Proxy wrapper pattern | Automatic sync, subscription model, prevents bugs |
| Exclusive accordion | Custom JS open/close tracking | `name` attribute on `<details>` | Native browser support (Chrome 120+, Safari 17.2+, Firefox 130+) |

**Key insight:** Modern browsers (2026) have native support for most interactive patterns. Building custom solutions adds maintenance burden and accessibility debt.

## Common Pitfalls

### Pitfall 1: Forgetting to Persist State on Every Change
**What goes wrong:** User refreshes page and loses all selections
**Why it happens:** Only persisting on explicit save action
**How to avoid:** Use Proxy pattern to auto-persist on every state mutation
**Warning signs:** User complaints about lost work

### Pitfall 2: Event Listener Memory Leaks
**What goes wrong:** Performance degrades as user interacts with page
**Why it happens:** Adding new listeners when re-rendering without removing old ones
**How to avoid:** Use event delegation on container elements, not individual items
**Warning signs:** Browser dev tools show thousands of event listeners

### Pitfall 3: Blocking UI During API Calls
**What goes wrong:** Page freezes while loading NOC data
**Why it happens:** Not using async/await properly, no loading states
**How to avoid:** Show skeleton loaders immediately, use async/await for API calls
**Warning signs:** White screen or frozen UI during data fetch

### Pitfall 4: Inaccessible Custom Accordions
**What goes wrong:** Screen reader users cannot navigate sections
**Why it happens:** Building custom accordion without ARIA attributes
**How to avoid:** Use native `<details>`/`<summary>` which have built-in accessibility
**Warning signs:** Fails WCAG 2.2 AA audit

### Pitfall 5: Sidebar Covering Content on Toggle
**What goes wrong:** Main content shifts or gets covered unexpectedly
**Why it happens:** Not accounting for sidebar width in layout calculations
**How to avoid:** Use CSS transitions with `transform` rather than `width`, add main content padding
**Warning signs:** Content "jumps" when sidebar toggles

### Pitfall 6: Search Filter Not Resetting
**What goes wrong:** User can't see all items after searching
**Why it happens:** Filtered items not restored when search cleared
**How to avoid:** Filter by toggling CSS class (e.g., `.hidden`) rather than removing DOM elements
**Warning signs:** Items "disappear" permanently after search

## Code Examples

Verified patterns from official sources:

### API Client for Flask Backend
```javascript
// Source: Standard fetch pattern with error handling
const api = {
    baseUrl: '/api',

    async search(query) {
        const response = await fetch(`${this.baseUrl}/search?q=${encodeURIComponent(query)}`);
        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.detail || error.error);
        }
        return response.json();
    },

    async getProfile(code) {
        const response = await fetch(`${this.baseUrl}/profile?code=${encodeURIComponent(code)}`);
        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.detail || error.error);
        }
        return response.json();
    }
};
```

### Skeleton Loading State
```html
<!-- Source: CSS skeleton loading patterns -->
<div class="skeleton-container">
    <div class="skeleton skeleton--header"></div>
    <div class="skeleton skeleton--text"></div>
    <div class="skeleton skeleton--text"></div>
    <div class="skeleton skeleton--text skeleton--short"></div>
</div>
```

```css
/* Source: FreeCodeCamp skeleton loader pattern */
.skeleton {
    background: linear-gradient(90deg, #f0f0f0 25%, #e0e0e0 50%, #f0f0f0 75%);
    background-size: 200% 100%;
    animation: shimmer 1.5s infinite;
    border-radius: 4px;
}

.skeleton--header {
    height: 24px;
    width: 60%;
    margin-bottom: 1rem;
}

.skeleton--text {
    height: 16px;
    width: 100%;
    margin-bottom: 0.5rem;
}

.skeleton--short {
    width: 40%;
}

@keyframes shimmer {
    0% { background-position: 200% 0; }
    100% { background-position: -200% 0; }
}
```

### Real-Time Search Filter
```javascript
// Source: CSS-Tricks, vanilla JS filter patterns
const initSectionSearch = (section) => {
    const searchInput = section.querySelector('.jd-section__search');
    const statements = section.querySelectorAll('.statement');

    searchInput.addEventListener('input', (e) => {
        const term = e.target.value.toLowerCase().trim();

        statements.forEach(stmt => {
            const text = stmt.querySelector('.statement__text').textContent.toLowerCase();
            stmt.classList.toggle('hidden', term && !text.includes(term));
        });
    });
};
```

### Selection Count Update
```javascript
// Source: Standard DOM manipulation pattern
const updateSelectionCount = (sectionId, count) => {
    const section = document.querySelector(`[data-section-id="${sectionId}"]`);
    const countEl = section.querySelector('.jd-section__count');
    countEl.textContent = `(${count} selected)`;
};

// Subscribe to state changes
store.subscribe((state) => {
    Object.keys(state.selections).forEach(sectionId => {
        updateSelectionCount(sectionId, state.selections[sectionId].length);
    });
});
```

### Error Display (No Alert)
```javascript
// Source: GeeksforGeeks, best practice error handling
const showError = (container, message) => {
    const errorEl = document.createElement('div');
    errorEl.className = 'error-message';
    errorEl.setAttribute('role', 'alert');
    errorEl.textContent = message;

    container.prepend(errorEl);

    // Auto-dismiss after 5 seconds
    setTimeout(() => errorEl.remove(), 5000);
};
```

```css
.error-message {
    background-color: #ffebee;
    color: #c62828;
    padding: 1rem;
    border-radius: 4px;
    border-left: 4px solid #c62828;
    margin-bottom: 1rem;
}
```

## State of the Art

| Old Approach | Current Approach | When Changed | Impact |
|--------------|------------------|--------------|--------|
| Custom accordion JS | Native `<details>`/`<summary>` with `name` attribute | 2024-2025 (Chrome 120, Safari 17.2, Firefox 130) | No JS needed for exclusive accordion |
| jQuery sortable | SortableJS (vanilla) | 2015+ but matured | Framework-agnostic, better performance |
| Redux-like patterns | Proxy-based reactive state | 2020+ (ES6 Proxies widely supported) | Simpler, no library needed |
| Manual ARIA management | Native semantic HTML | Ongoing | Built-in accessibility |
| JavaScript height animation | CSS transitions on `max-height` or `grid-template-rows` | 2020+ | Smoother, GPU-accelerated |

**Deprecated/outdated:**
- jQuery UI Accordion: Requires jQuery dependency, heavier than vanilla alternatives
- Angular Material CDK: Framework-specific, overkill for vanilla JS project
- Custom `aria-expanded` management: Unnecessary when using native `<details>` elements

## Open Questions

Things that couldn't be fully resolved:

1. **Exact statement count in typical NOC profile**
   - What we know: Profile has multiple sections (Main Duties, Work Activities, Skills, Abilities, etc.)
   - What's unclear: Typical count per section to inform virtualization needs
   - Recommendation: Likely 5-30 statements per section; no virtualization needed. Verify with real data in implementation.

2. **GC Design System integration depth**
   - What we know: GC Design System exists with web components, but is in alpha
   - What's unclear: Whether to use GCDS components or just follow visual style
   - Recommendation: Follow visual style (colors, typography, spacing) but don't add web component dependencies for this demo. Keep vanilla JS approach per PROJECT.md constraints.

3. **Section reorder persistence scope**
   - What we know: User decided on draggable section order
   - What's unclear: Should order persist across browser sessions or reset each time?
   - Recommendation: Persist to localStorage along with selections for consistent UX.

## Sources

### Primary (HIGH confidence)
- [W3C WAI ARIA APG - Accordion Pattern](https://www.w3.org/WAI/ARIA/apg/patterns/accordion/examples/accordion/) - ARIA attributes and keyboard interactions
- [MDN - Exclusive accordions using details element](https://developer.mozilla.org/en-US/blog/html-details-exclusive-accordions/) - Native accordion with `name` attribute
- [SortableJS Official](https://sortablejs.github.io/Sortable/) - Drag-and-drop library documentation

### Secondary (MEDIUM confidence)
- [CSS-Tricks - Sticky Footer](https://css-tricks.com/couple-takes-sticky-footer/) - Verified sticky positioning patterns
- [GC Design System Components](https://design-system.alpha.canada.ca/en/components/) - Government of Canada design patterns
- [Modern CSS Solutions - Custom Checkbox](https://moderncss.dev/pure-css-custom-checkbox-style/) - Accessible checkbox styling

### Tertiary (LOW confidence)
- [Medium - State Management in Vanilla JS 2026 Trends](https://medium.com/@chirag.dave/state-management-in-vanilla-js-2026-trends-f9baed7599de) - Community patterns for state management
- [FreeCodeCamp - Skeleton Screens](https://www.freecodecamp.org/news/how-to-build-skeleton-screens-using-css-for-better-user-experience/) - Loading state patterns

## Metadata

**Confidence breakdown:**
- Standard stack: HIGH - Verified with official documentation and established community patterns
- Architecture: HIGH - Patterns are well-documented and widely used
- Pitfalls: MEDIUM - Based on community experience and best practice guides

**Research date:** 2026-01-21
**Valid until:** 2026-02-21 (30 days - stable technologies, no rapid changes expected)
