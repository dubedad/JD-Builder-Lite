---
phase: 08-A-search-bar-redesign
plan: 01
type: execute
wave: 1
depends_on: []
files_modified:
  - templates/index.html
  - static/css/main.css
  - static/js/main.js
  - static/js/api.js
  - src/routes/api.py
  - src/services/scraper.py
autonomous: true

must_haves:
  truths:
    - "User sees pill toggle with Keyword and Code buttons above search input"
    - "User can switch between Keyword and Code search modes by clicking pills"
    - "Active pill is visually highlighted with accent color"
    - "Search placeholder updates based on selected mode"
    - "Authoritative sources footnote displays below search bar"
    - "Search API accepts and honors search type parameter"
  artifacts:
    - path: "templates/index.html"
      provides: "Pill toggle markup, authoritative sources footnote"
      contains: "search-type-toggle"
    - path: "static/css/main.css"
      provides: "Pill button styles, footnote styles"
      contains: ".pill-btn"
    - path: "static/js/main.js"
      provides: "Toggle handler, placeholder update, searchType state"
      contains: "currentSearchType"
    - path: "static/js/api.js"
      provides: "searchType parameter in API call"
      contains: "type:"
    - path: "src/routes/api.py"
      provides: "Search type query param handling"
      contains: "search_type"
    - path: "src/services/scraper.py"
      provides: "Dynamic searchType in OASIS request"
      contains: "search_type"
  key_links:
    - from: "templates/index.html"
      to: "static/js/main.js"
      via: "pill-btn click handler"
      pattern: "querySelectorAll.*pill-btn"
    - from: "static/js/main.js"
      to: "static/js/api.js"
      via: "api.search(query, currentSearchType)"
      pattern: "api\\.search.*currentSearchType"
    - from: "static/js/api.js"
      to: "src/routes/api.py"
      via: "fetch with type param"
      pattern: "type.*searchType"
    - from: "src/routes/api.py"
      to: "src/services/scraper.py"
      via: "scraper.search(query, search_type)"
      pattern: "scraper\\.search.*search_type"
---

<objective>
Redesign the Step 1 search interface with a Keyword/Code pill toggle and authoritative sources footnote.

Purpose: Enable users to search by NOC code (not just keywords) and show clear data source attribution per SRCH-10, SRCH-11, SRCH-12 requirements.

Output: Updated search UI with pill toggle, dynamic placeholders, and footnote. Full stack support for search type parameter.
</objective>

<execution_context>
@~/.claude/get-shit-done/workflows/execute-plan.md
@~/.claude/get-shit-done/templates/summary.md
</execution_context>

<context>
@.planning/PROJECT.md
@.planning/ROADMAP.md
@.planning/STATE.md
@.planning/phases/08-A-search-bar-redesign/08-A-RESEARCH.md
@templates/index.html
@static/css/main.css
@static/js/main.js
@static/js/api.js
@src/routes/api.py
@src/services/scraper.py
</context>

<tasks>

<task type="auto">
  <name>Task 1: Add pill toggle and footnote to HTML/CSS</name>
  <files>templates/index.html, static/css/main.css</files>
  <action>
Update templates/index.html search-container section (lines 22-30):

1. Add pill toggle BEFORE the search input:
```html
<section class="search-container">
    <div class="search-type-toggle" role="tablist">
        <button role="tab" class="pill-btn active" data-search-type="Keyword" aria-selected="true">
            Keyword
        </button>
        <button role="tab" class="pill-btn" data-search-type="Code" aria-selected="false">
            Code
        </button>
    </div>
    <input
        type="search"
        id="search-input"
        placeholder="Search job titles..."
        aria-label="Search job titles"
    >
    <button id="search-button" type="button">Search</button>
</section>
```

2. Add authoritative sources footnote AFTER search-container (new element):
```html
<p class="authoritative-sources">
    Authoritative Sources: ESDC OaSIS 2025 NOC v1.0 / ONET (R) 27.2 Database (USDOL/ETA)
</p>
```

Update static/css/main.css - add these styles after the existing .search-container rules (around line 106):

```css
/* Pill Toggle Styles */
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
    border-left: none;
}

.pill-btn.active {
    background: var(--accent);
    color: white;
    border-color: var(--accent);
}

.pill-btn:hover:not(.active) {
    background: var(--highlight);
}

.pill-btn:focus {
    outline: 2px solid var(--accent);
    outline-offset: 2px;
    z-index: 1;
}

/* Authoritative Sources Footnote */
.authoritative-sources {
    font-size: 0.75rem;
    color: var(--text-light);
    margin-top: -1rem;
    margin-bottom: 1.5rem;
    text-align: left;
    padding-left: 1rem;
}
```

Also update the responsive section (@media max-width: 768px) to stack the search controls properly:
```css
@media (max-width: 768px) {
    .search-container {
        flex-wrap: wrap;
    }

    .search-type-toggle {
        width: 100%;
        margin-bottom: 0.5rem;
    }
}
```
  </action>
  <verify>
Open http://localhost:5000 in browser. Visually confirm:
- Pill toggle visible with Keyword/Code buttons
- Keyword button has accent color (active state)
- Authoritative sources footnote visible below search
- Layout looks correct on desktop and mobile widths
  </verify>
  <done>
Pill toggle renders with correct styling. Footnote displays below search. Responsive layout works.
  </done>
</task>

<task type="auto">
  <name>Task 2: Add JavaScript toggle handler and API integration</name>
  <files>static/js/main.js, static/js/api.js</files>
  <action>
Update static/js/api.js - modify the search method to accept searchType parameter:

```javascript
async search(query, searchType = 'Keyword') {
    const params = new URLSearchParams({
        q: query,
        type: searchType
    });
    const response = await fetch(`${this.baseUrl}/search?${params}`);
    if (!response.ok) {
        const error = await response.json();
        throw new Error(error.detail || error.error || 'Search failed');
    }
    return response.json();
}
```

Update static/js/main.js - add toggle handler inside DOMContentLoaded:

1. After the existing DOM reference caching (around line 13), add:
```javascript
const pillBtns = document.querySelectorAll('.pill-btn');
```

2. After the module initializations (around line 34), add search type state and handler:
```javascript
// Search type toggle state
let currentSearchType = 'Keyword';

// Pill toggle handler
pillBtns.forEach(btn => {
    btn.addEventListener('click', () => {
        // Update active state
        pillBtns.forEach(b => {
            b.classList.remove('active');
            b.setAttribute('aria-selected', 'false');
        });
        btn.classList.add('active');
        btn.setAttribute('aria-selected', 'true');

        // Update search type
        currentSearchType = btn.dataset.searchType;

        // Update placeholder
        searchInput.placeholder = currentSearchType === 'Keyword'
            ? 'Search job titles...'
            : 'Enter NOC code (e.g., 72600 or 72600.01)';
        searchInput.setAttribute('aria-label',
            currentSearchType === 'Keyword' ? 'Search job titles' : 'Enter NOC code');
    });
});
```

3. Update handleSearch function (around line 321) to pass currentSearchType:
```javascript
const response = await api.search(query, currentSearchType);
```

Note: The handleSearch function currently calls api.search(query) on line 321. Add currentSearchType as second parameter.
  </action>
  <verify>
In browser:
1. Click Code pill - verify it becomes active, Keyword becomes inactive
2. Click Keyword pill - verify it becomes active, Code becomes inactive
3. Check placeholder updates: "Search job titles..." for Keyword, "Enter NOC code..." for Code
4. Open DevTools Network tab, search for something, verify request includes `type=Keyword` or `type=Code`
  </verify>
  <done>
Pill toggle switches active state. Placeholder updates on toggle. Search requests include type parameter.
  </done>
</task>

<task type="auto">
  <name>Task 3: Update backend to handle search type parameter</name>
  <files>src/routes/api.py, src/services/scraper.py</files>
  <action>
Update src/services/scraper.py - modify search method to accept search_type parameter:

Change the method signature and params (around line 23):
```python
def search(self, query: str, search_type: str = "Keyword", version: Optional[str] = None) -> str:
    """Fetch search results HTML from OASIS.

    Args:
        query: Search query string
        search_type: Search type - "Keyword" or "Code" (defaults to "Keyword")
        version: OASIS version (defaults to config.OASIS_VERSION)

    Returns:
        Raw HTML response text

    Raises:
        requests.HTTPError: If request fails
    """
    if version is None:
        version = OASIS_VERSION

    url = f"{OASIS_BASE_URL}/OaSIS/OaSISSearchResult"
    params = {
        "searchType": search_type,  # Now dynamic instead of hardcoded
        "searchText": query,
        "version": version
    }

    response = self.session.get(url, params=params, timeout=self.timeout, verify=False)
    response.raise_for_status()
    return response.text
```

Update src/routes/api.py - modify search route to accept and validate type param:

In the search() function (starting at line 28), after getting query param:
```python
@api_bp.route('/search')
def search():
    """Search OASIS for NOC profiles by query string.

    Query params:
        q: Search query (minimum 2 characters)
        type: Search type - "Keyword" or "Code" (default: "Keyword")

    Returns:
        SearchResponse with results array and metadata
        ErrorResponse with 400/500/502 on error
    """
    query = request.args.get('q', '')
    search_type = request.args.get('type', 'Keyword')

    # Validate search_type
    if search_type not in ['Keyword', 'Code']:
        search_type = 'Keyword'

    # Validate query
    if not query or len(query) < 2:
        error = ErrorResponse(
            error="Invalid query",
            detail="Query parameter 'q' must be at least 2 characters"
        )
        return jsonify(error.model_dump()), 400

    try:
        # Fetch and parse search results - pass search_type
        html = scraper.search(query, search_type=search_type)
        results = parser.parse_search_results(html)
        # ... rest unchanged
```

The key change is passing search_type to scraper.search() on the line that currently reads:
```python
html = scraper.search(query)
```
Change to:
```python
html = scraper.search(query, search_type=search_type)
```
  </action>
  <verify>
Test API directly:
```bash
curl "http://localhost:5000/api/search?q=software&type=Keyword"
curl "http://localhost:5000/api/search?q=21232&type=Code"
```

Verify both return results (assuming valid queries). Verify invalid type defaults to Keyword (test with type=InvalidValue).

Full integration test in browser:
1. Select Keyword, search "software developer" - should return keyword matches
2. Select Code, search "21232" - should return code match
  </verify>
  <done>
Backend accepts type parameter. Scraper passes searchType to OASIS. Invalid types default to Keyword. Full stack search type flow works.
  </done>
</task>

</tasks>

<verification>
After all tasks complete:

1. **Visual verification:**
   - Open http://localhost:5000
   - Pill toggle visible with Keyword active by default
   - Authoritative sources footnote visible: "ESDC OaSIS 2025 NOC v1.0 / ONET (R) 27.2 Database (USDOL/ETA)"
   - No version dropdown, advanced search, or A-Z links visible (SRCH-12 - already absent)

2. **Functional verification:**
   - Click Code pill - becomes active, placeholder changes to NOC code hint
   - Click Keyword pill - becomes active, placeholder changes back
   - Search with Keyword mode - returns keyword-based results
   - Search with Code mode - returns code-based results

3. **Accessibility verification:**
   - Tab through controls - pills are focusable
   - ARIA attributes present (role="tablist", role="tab", aria-selected)
   - Focus outline visible on pills

4. **Responsive verification:**
   - Resize to mobile width - layout stacks appropriately
</verification>

<success_criteria>
- [ ] Pill toggle renders with Keyword/Code options
- [ ] Active pill has accent color styling
- [ ] Clicking pill changes active state and updates placeholder
- [ ] Authoritative sources footnote displays below search
- [ ] Search API accepts `type` parameter (Keyword or Code)
- [ ] Backend passes search type to OASIS scraper
- [ ] Full search flow works with both modes
- [ ] Accessibility: buttons with ARIA, keyboard navigation works
</success_criteria>

<output>
After completion, create `.planning/phases/08-A-search-bar-redesign/08-A-01-SUMMARY.md`
</output>
