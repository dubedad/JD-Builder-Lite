# Phase 08-A: Search Bar Redesign - Research

**Researched:** 2026-01-24
**Domain:** Frontend UI (HTML/CSS/JavaScript), Flask templating
**Confidence:** HIGH

## Summary

This phase involves redesigning the Step 1 search interface to match the OaSIS website pattern. The current implementation has a simple search bar with a text input and button. The redesign requires:

1. Adding a Keyword/Code pill toggle to switch search modes
2. Replacing the version dropdown with an authoritative sources footnote
3. Removing advanced search and A-Z links (which do not exist in the current implementation)

The implementation is straightforward as the codebase uses a clean Flask + vanilla JavaScript architecture with minimal dependencies. The OaSIS HTML reference provides exact patterns to follow.

**Primary recommendation:** Implement pill toggle as pure CSS/HTML component using existing color variables, update API route to accept search type parameter.

## Standard Stack

The established libraries/tools for this domain:

### Core
| Library | Version | Purpose | Why Standard |
|---------|---------|---------|--------------|
| Flask | 2.x | Backend templating | Already in use |
| Jinja2 | 3.x | HTML templates | Built into Flask |
| Vanilla JS | ES6+ | Frontend logic | Already in use, no framework |
| CSS Custom Properties | Native | Color/style variables | Already defined in main.css |

### Supporting
| Library | Version | Purpose | When to Use |
|---------|---------|---------|-------------|
| Font Awesome | CDN | Icons (optional) | If pill toggle needs icons |

### Alternatives Considered
| Instead of | Could Use | Tradeoff |
|------------|-----------|----------|
| Vanilla JS toggle | Alpine.js | Overkill for simple state |
| CSS Pills | Bootstrap | Would add dependency |

**Installation:**
No new dependencies required. All functionality can be achieved with existing stack.

## Architecture Patterns

### Current File Structure (Relevant)
```
templates/
  index.html         # Main template - contains search form
static/
  css/
    main.css         # Contains search-container styles
  js/
    main.js          # Contains handleSearch(), search logic
    api.js           # Contains api.search() method
src/
  routes/
    api.py           # Contains /api/search route
  services/
    scraper.py       # Contains search() method with searchType param
```

### Pattern 1: Pill Toggle Component
**What:** Two-button toggle where only one is active at a time
**When to use:** Binary choice between search modes
**Example:**
```html
<!-- Based on OASIS-HTML-REFERENCE.md -->
<div class="search-type-toggle" role="tablist">
    <button role="tab" class="pill-btn active" data-search-type="Keyword" aria-selected="true">
        Keyword
    </button>
    <button role="tab" class="pill-btn" data-search-type="Code" aria-selected="false">
        Code
    </button>
</div>
```

### Pattern 2: Authoritative Sources Footnote
**What:** Small text below search controls showing data sources
**When to use:** Replace version dropdown with static attribution
**Example:**
```html
<p class="authoritative-sources">
    Authoritative Sources: ESDC OaSIS 2025 NOC v1.0 / ONET (R) 27.2 Database (USDOL/ETA)
</p>
```

### Anti-Patterns to Avoid
- **Radio buttons for toggle:** Pills are more intuitive for this use case
- **Hidden form fields:** Use data attributes instead for cleaner code
- **Separate search forms:** Keep single form, toggle affects searchType param only

## Don't Hand-Roll

Problems that look simple but have existing solutions:

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| Pill styling | Custom from scratch | Copy OaSIS patterns | Already have HTML reference |
| Toggle state | Complex state machine | Simple class toggle | Only 2 states, active/inactive |
| ARIA attributes | Invent patterns | Use role="tablist" | Matches OaSIS implementation |

**Key insight:** The OaSIS-HTML-REFERENCE.md already provides the exact HTML structure and classes to use. Replicate rather than reinvent.

## Common Pitfalls

### Pitfall 1: Breaking Existing Search Functionality
**What goes wrong:** Changing API breaks current keyword-only search
**Why it happens:** Forgetting to default searchType to "Keyword"
**How to avoid:** Backend defaults to "Keyword" if no searchType provided
**Warning signs:** Existing searches stop working after deployment

### Pitfall 2: Code Search Format Validation
**What goes wrong:** Code search accepts invalid NOC codes
**Why it happens:** Not validating 5-digit or 5.2-digit format
**How to avoid:** Add client-side validation for Code mode (pattern: `^\d{5}(?:\.\d{2})?$`)
**Warning signs:** Confusing error messages from backend

### Pitfall 3: Pill Toggle Accessibility
**What goes wrong:** Keyboard users cannot toggle between modes
**Why it happens:** Using divs instead of buttons, missing ARIA
**How to avoid:** Use `<button>` elements with `role="tab"`, `aria-selected`
**Warning signs:** Tab key skips over toggle, screen reader confusion

### Pitfall 4: Search Input Placeholder Not Updating
**What goes wrong:** Placeholder says "Search job titles..." in Code mode
**Why it happens:** Forgetting to update placeholder on mode switch
**How to avoid:** Update placeholder text when toggle changes
**Warning signs:** User confusion about what to enter

## Code Examples

Verified patterns from codebase and OaSIS reference.

### Current Search Container (index.html lines 22-30)
```html
<!-- Current implementation to modify -->
<section class="search-container">
    <input
        type="search"
        id="search-input"
        placeholder="Search job titles..."
        aria-label="Search job titles"
    >
    <button id="search-button" type="button">Search</button>
</section>
```

### Target Layout (from 06-CONTEXT.md)
```
+----------------------------------------------------------+
| [Keyword] [Code]     Search by keyword  [input] [Search] |
|                                                          |
| Authoritative Sources: ESDC OaSIS 2025 NOC v1.0 / ONET   |
| (R) 27.2 Database (USDOL/ETA)              [small font]  |
+----------------------------------------------------------+
```

### Pill Toggle CSS Pattern (based on OaSIS)
```css
/* Source: OASIS-HTML-REFERENCE.md search bar section */
.search-type-toggle {
    display: flex;
    gap: 0;
}

.pill-btn {
    padding: 7px 16px;
    border: 1px solid var(--border);
    background: var(--bg);
    cursor: pointer;
    font-size: 0.875rem;
    transition: background 0.15s, color 0.15s;
}

.pill-btn:first-child {
    border-radius: 25px 0 0 25px;
}

.pill-btn:last-child {
    border-radius: 0 25px 25px 0;
}

.pill-btn.active {
    background: var(--accent);
    color: white;
    border-color: var(--accent);
}

.pill-btn:focus {
    outline: 2px solid var(--accent);
    outline-offset: 2px;
}
```

### Backend Search Type Parameter (scraper.py line 39-47)
```python
# Current implementation already supports searchType
url = f"{OASIS_BASE_URL}/OaSIS/OaSISSearchResult"
params = {
    "searchType": "Keyword",  # <-- This needs to be dynamic
    "searchText": query,
    "version": version
}
```

### API Route Update Pattern
```python
# api.py /search route modification
@api_bp.route('/search')
def search():
    query = request.args.get('q', '')
    search_type = request.args.get('type', 'Keyword')  # Default to Keyword

    # Validate search_type
    if search_type not in ['Keyword', 'Code']:
        search_type = 'Keyword'

    # Pass to scraper
    html = scraper.search(query, search_type=search_type)
```

### Scraper Update Pattern
```python
# scraper.py search method modification
def search(self, query: str, search_type: str = "Keyword", version: Optional[str] = None) -> str:
    params = {
        "searchType": search_type,  # Now dynamic
        "searchText": query,
        "version": version or OASIS_VERSION
    }
```

### JavaScript Toggle Handler Pattern
```javascript
// main.js addition
const pillBtns = document.querySelectorAll('.pill-btn');
let currentSearchType = 'Keyword';

pillBtns.forEach(btn => {
    btn.addEventListener('click', () => {
        pillBtns.forEach(b => {
            b.classList.remove('active');
            b.setAttribute('aria-selected', 'false');
        });
        btn.classList.add('active');
        btn.setAttribute('aria-selected', 'true');
        currentSearchType = btn.dataset.searchType;

        // Update placeholder
        searchInput.placeholder = currentSearchType === 'Keyword'
            ? 'Search job titles...'
            : 'Enter NOC code (e.g., 72600 or 72600.01)';
    });
});

// Update handleSearch to pass type
async function handleSearch() {
    const query = searchInput.value.trim();
    // ... validation ...
    const response = await api.search(query, currentSearchType);
}
```

### API Client Update Pattern
```javascript
// api.js modification
async search(query, searchType = 'Keyword') {
    const params = new URLSearchParams({
        q: query,
        type: searchType
    });
    const response = await fetch(`${this.baseUrl}/search?${params}`);
    // ... rest unchanged
}
```

## State of the Art

| Old Approach | Current Approach | When Changed | Impact |
|--------------|------------------|--------------|--------|
| Version dropdown | Authoritative sources footnote | v2.0 design | Simpler UI, removes confusion |
| Keyword-only search | Keyword/Code toggle | v2.0 design | Users can search by NOC code |

**Deprecated/outdated:**
- Version dropdown: Replaced by static footnote per 06-CONTEXT.md decision
- Advanced search link: Removed per SRCH-12
- A-Z link: Removed per SRCH-12 (does not exist in current implementation)

## Open Questions

Things that couldn't be fully resolved:

1. **NOC Code validation for Code search**
   - What we know: NOC codes are 5 digits or 5.2 digits (e.g., 72600 or 72600.01)
   - What's unclear: Should validation happen client-side, server-side, or both?
   - Recommendation: Both - client for UX, server for security

2. **Error handling for invalid Code searches**
   - What we know: OaSIS returns empty results for invalid codes
   - What's unclear: Should we show a special message for code-not-found vs keyword-not-found?
   - Recommendation: Same "No results found" message for both, simpler implementation

## Sources

### Primary (HIGH confidence)
- `templates/index.html` - Current search form implementation (lines 22-30)
- `static/css/main.css` - Current search styling (lines 62-105)
- `static/js/main.js` - Current search handler (lines 304-329)
- `src/routes/api.py` - Current API route (lines 28-83)
- `src/services/scraper.py` - Current scraper with searchType param (lines 23-48)
- `.planning/phases/06-enhanced-ui-display/06-CONTEXT.md` - UI decisions (lines 161-192)
- `.planning/phases/06-enhanced-ui-display/OASIS-HTML-REFERENCE.md` - HTML patterns (lines 29-88)

### Secondary (MEDIUM confidence)
- OaSIS search API URL pattern: `https://noc.esdc.gc.ca/OaSIS/OaSISSearchResult?searchType={Keyword|Code}&searchText={query}&version=2025.0`

### Tertiary (LOW confidence)
- None - all findings verified against codebase

## Metadata

**Confidence breakdown:**
- Standard stack: HIGH - All from existing codebase
- Architecture: HIGH - Files identified and patterns extracted
- Pitfalls: HIGH - Based on analysis of current implementation

**Research date:** 2026-01-24
**Valid until:** 60 days (stable codebase, no external API changes expected)

---

## Implementation Summary

### Files to Modify

| File | Changes |
|------|---------|
| `templates/index.html` | Add pill toggle, add authoritative sources footnote |
| `static/css/main.css` | Add pill toggle styles, footnote styles |
| `static/js/main.js` | Add toggle handler, update handleSearch |
| `static/js/api.js` | Add searchType parameter to search() |
| `src/routes/api.py` | Accept and validate 'type' query param |
| `src/services/scraper.py` | Accept search_type parameter |

### No New Files Required

All changes are modifications to existing files.

### No Elements to Remove

The current implementation does not have:
- Advanced search link
- View all A-Z link
- Version dropdown

These were never implemented, so SRCH-12 is satisfied by default.

### Estimated Effort

- HTML changes: ~20 lines
- CSS changes: ~40 lines
- JavaScript changes: ~30 lines
- Python changes: ~15 lines

Total: ~105 lines across 6 files. Straightforward implementation.
