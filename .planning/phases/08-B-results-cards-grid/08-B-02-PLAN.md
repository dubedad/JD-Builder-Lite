---
phase: 08-B-results-cards-grid
plan: 02
type: execute
wave: 2
depends_on: ["08-B-01"]
files_modified:
  - templates/index.html
  - static/css/main.css
  - static/css/results-cards.css
  - static/js/main.js
autonomous: true

must_haves:
  truths:
    - "Card view displays OaSIS-style cards matching reference HTML"
    - "Each card shows lead statement with book icon"
    - "Each card shows TEER description with bookmark icon"
    - "Each card shows broad category with appropriate icon"
    - "Each card shows matching criteria with search icon"
    - "Cards are clickable and navigate to profile details"
    - "Sort dropdown allows sorting by label, code, or match"
    - "Grid view shows placeholder message for skills/abilities/knowledge columns (profile data required)"
  artifacts:
    - path: "static/css/results-cards.css"
      provides: "OaSIS card styles matching reference"
      contains: ".oasis-card"
    - path: "static/js/main.js"
      provides: "renderCardView function with enriched data"
      contains: "renderCardView"
    - path: "templates/index.html"
      provides: "Card view container and sort controls"
      contains: "sort-controls"
  key_links:
    - from: "static/js/main.js"
      to: "static/css/results-cards.css"
      via: "card element classes"
      pattern: "oasis-card|card-row"
    - from: "static/js/main.js"
      to: "templates/index.html"
      via: "results-list container"
      pattern: "results-list"
    - from: "templates/index.html"
      to: "static/css/results-cards.css"
      via: "stylesheet link"
      pattern: "results-cards.css"
---

<objective>
Implement OaSIS-style card view for search results with 6 data points.

Purpose: Render search results as rich cards matching OaSIS design (DISP-20). Display lead statement, TEER, broad category, and matching criteria with appropriate icons. Add sort controls per OaSIS pattern.

Output: New CSS file for card styles, updated renderSearchResults() to use enriched data, sort dropdown, clickable cards navigating to profile.

**Scope note (DISP-21 Grid View):** Grid view displays columns for Skills, Abilities, and Knowledge with placeholder text "Load profile for [X]". These columns require profile data which is not available from search results. Full grid population deferred to Phase 08-C profile integration or future enhancement.
</objective>

<execution_context>
@~/.claude/get-shit-done/workflows/execute-plan.md
@~/.claude/get-shit-done/templates/summary.md
</execution_context>

<context>
@.planning/PROJECT.md
@.planning/ROADMAP.md
@.planning/phases/08-B-results-cards-grid/08-B-RESEARCH.md
@.planning/phases/06-enhanced-ui-display/OASIS-HTML-REFERENCE.md
@templates/index.html
@static/css/main.css
@static/js/main.js
</context>

<tasks>

<task type="auto">
  <name>Task 1: Create OaSIS card styles CSS</name>
  <files>static/css/results-cards.css, templates/index.html</files>
  <action>
1. Create new file static/css/results-cards.css with OaSIS-inspired card styles:

```css
/* OaSIS-style Card View Styles
   Based on OASIS-HTML-REFERENCE.md patterns
*/

/* Card Container */
.results-cards-container {
    display: flex;
    flex-direction: column;
    gap: 1rem;
}

/* Individual Card */
.oasis-card {
    border: 1px solid var(--border);
    border-radius: 4px;
    background: var(--bg);
    cursor: pointer;
    transition: box-shadow 0.15s, border-color 0.15s;
}

.oasis-card:hover {
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
    border-color: var(--accent);
}

.oasis-card:focus {
    outline: 2px solid var(--accent);
    outline-offset: 2px;
}

/* Card Header (NOC code + title link) */
.card-header {
    padding: 0.75rem 1rem;
    border-bottom: 1px solid var(--border);
    background: var(--highlight);
}

.card-title-link {
    font-weight: 600;
    color: var(--accent);
    text-decoration: none;
    font-size: 1rem;
}

.card-title-link:hover {
    text-decoration: underline;
}

/* Card Content Rows */
.card-row {
    padding: 0.5rem 1rem;
    display: flex;
    align-items: flex-start;
    gap: 0.75rem;
    border-bottom: 1px solid var(--border-light, #f0f0f0);
}

.card-row:last-of-type {
    border-bottom: none;
}

/* Card Icons (Font Awesome style) */
.card-icon {
    flex-shrink: 0;
    width: 1.25rem;
    color: var(--text-light);
    margin-top: 0.125rem;
}

/* Card Text Content */
.card-text {
    flex: 1;
    font-size: 0.875rem;
    line-height: 1.5;
    color: var(--text);
}

.card-text.empty {
    color: var(--text-light);
    font-style: italic;
}

/* Card Footer (Matching Criteria) */
.card-footer {
    padding: 0.5rem 1rem;
    border-top: 2px solid var(--border);
    background: var(--highlight);
    display: flex;
    align-items: center;
    gap: 0.75rem;
}

.card-footer .card-text {
    font-size: 0.8rem;
}

.matching-label {
    font-weight: 500;
    color: var(--text);
}

.matching-value {
    color: var(--text-light);
    font-size: 0.75rem;
}

/* Sort Controls */
.sort-controls {
    display: flex;
    align-items: center;
    gap: 1rem;
    margin-bottom: 1rem;
    flex-wrap: wrap;
}

.sort-controls label {
    font-weight: 500;
    font-size: 0.875rem;
}

.sort-select {
    padding: 0.5rem 0.75rem;
    border: 1px solid var(--border);
    border-radius: 4px;
    background: var(--bg);
    font-size: 0.875rem;
    min-width: 180px;
}

.sort-select:focus {
    outline: 2px solid var(--accent);
    outline-offset: 1px;
}

/* Results Count */
.results-count {
    font-size: 0.875rem;
    color: var(--text-light);
    margin-left: auto;
}

/* Responsive: Stack on mobile */
@media (max-width: 768px) {
    .sort-controls {
        flex-direction: column;
        align-items: flex-start;
        gap: 0.5rem;
    }

    .sort-select {
        width: 100%;
    }

    .results-count {
        margin-left: 0;
    }

    .card-row {
        flex-direction: column;
        gap: 0.25rem;
    }

    .card-icon {
        margin-top: 0;
    }
}

/* Font Awesome icon sizing */
.oasis-card .fa,
.oasis-card .fas,
.oasis-card .far {
    font-size: 1rem;
}

/* Grid View placeholder text */
.loading-text {
    color: var(--text-light);
    font-style: italic;
    font-size: 0.8rem;
}
```

2. Add CSS link to templates/index.html after the existing CSS links (around line 11):
```html
<link rel="stylesheet" href="/static/css/results-cards.css">
```

3. Add Font Awesome CDN link if not present (in <head>):
```html
<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.5.1/css/all.min.css">
```
  </action>
  <verify>
Check CSS file exists and is properly linked:
```bash
ls -la static/css/results-cards.css
grep "results-cards.css" templates/index.html
grep "fontawesome\|font-awesome" templates/index.html
```
  </verify>
  <done>
OaSIS card CSS file created with card, icon, sort control styles. CSS linked in index.html. Font Awesome linked for icons.
  </done>
</task>

<task type="auto">
  <name>Task 2: Update HTML with sort controls and container</name>
  <files>templates/index.html</files>
  <action>
Update the search-results section in templates/index.html (around lines 55-63):

Replace the current section:
```html
<!-- Search Results (initially hidden) -->
<section id="search-results" class="search-results hidden">
    <div class="view-controls">
        <button id="view-toggle" class="view-toggle" aria-label="Switch to grid view" title="Grid view">
            <span aria-hidden="true">&#x2630;</span>
        </button>
    </div>
    <h2>Search Results</h2>
    <ul id="results-list" class="results-list card-view"></ul>
</section>
```

With this enhanced structure:
```html
<!-- Search Results (initially hidden) -->
<section id="search-results" class="search-results hidden">
    <h2>Search Results</h2>

    <!-- Sort and View Controls -->
    <div class="sort-controls">
        <label for="sort-select">Sort by:</label>
        <select id="sort-select" class="sort-select">
            <option value="match" selected>Matching search criteria</option>
            <option value="title-asc">Label - A to Z</option>
            <option value="title-desc">Label - Z to A</option>
            <option value="code-asc">Code - Ascending</option>
            <option value="code-desc">Code - Descending</option>
        </select>

        <button id="view-toggle" class="view-toggle btn btn--secondary" aria-label="Switch to grid view" title="Grid view">
            <span id="view-toggle-label">Grid view</span>
            <i class="fa fa-th-list" aria-hidden="true"></i>
        </button>

        <span id="results-count" class="results-count"></span>
    </div>

    <!-- Results Container (card or grid view) -->
    <div id="results-list" class="results-cards-container" role="list"></div>
</section>
```

Note: Changed from <ul> to <div> for more flexible card layout. Added sort dropdown and results count.
  </action>
  <verify>
Verify HTML structure contains required elements:
```bash
grep "sort-select" templates/index.html
grep "results-cards-container" templates/index.html
grep "view-toggle" templates/index.html
```
  </verify>
  <done>
Search results section has sort dropdown, view toggle with icon, results count placeholder, and flexible container div.
  </done>
</task>

<task type="auto">
  <name>Task 3: Update JavaScript for card rendering and sorting</name>
  <files>static/js/main.js</files>
  <action>
Update static/js/main.js to render OaSIS-style cards with enriched data.

1. Update DOM references at the top (around line 13) to include new elements:
```javascript
const sortSelect = document.getElementById('sort-select');
const resultsCount = document.getElementById('results-count');
const viewToggleLabel = document.getElementById('view-toggle-label');
```

2. Replace the existing renderSearchResults function (around line 163) with this enhanced version:

```javascript
/**
 * Render search results in card or grid view
 * @param {Array} results - Array of EnrichedSearchResult objects
 */
function renderSearchResults(results) {
    lastResults = results; // Store for re-rendering
    resultsList.innerHTML = '';

    // Update results count
    resultsCount.textContent = `Showing ${results.length} ${results.length === 1 ? 'result' : 'results'}`;

    if (results.length === 0) {
        resultsList.innerHTML = '<div class="empty-state" role="listitem">No results found</div>';
        return;
    }

    if (currentView === 'grid' && !mediaQuery.matches) {
        renderGridView(results);
    } else {
        renderCardView(results);
    }
}

/**
 * Render OaSIS-style card view
 * @param {Array} results - Array of EnrichedSearchResult objects
 */
function renderCardView(results) {
    resultsList.className = 'results-cards-container';

    results.forEach(function(result) {
        const card = document.createElement('div');
        card.className = 'oasis-card';
        card.setAttribute('data-code', result.noc_code);
        card.setAttribute('role', 'listitem');
        card.setAttribute('tabindex', '0');

        // Build card HTML with available data
        card.innerHTML = `
            <div class="card-header">
                <a href="#" class="card-title-link" data-code="${escapeHtml(result.noc_code)}">
                    ${escapeHtml(result.noc_code)} - ${escapeHtml(result.title)}
                </a>
            </div>

            ${result.broad_category_name ? `
            <div class="card-row">
                <i class="fa fa-truck card-icon" aria-hidden="true"></i>
                <span class="card-text">${escapeHtml(result.broad_category_name)}</span>
            </div>
            ` : ''}

            ${result.teer_description ? `
            <div class="card-row">
                <i class="fa fa-bookmark card-icon" aria-hidden="true"></i>
                <span class="card-text">${escapeHtml(result.teer_description)}</span>
            </div>
            ` : ''}

            ${result.lead_statement ? `
            <div class="card-row">
                <i class="fa fa-book card-icon" aria-hidden="true"></i>
                <span class="card-text">${escapeHtml(result.lead_statement)}</span>
            </div>
            ` : ''}

            <div class="card-footer">
                <i class="fa fa-search card-icon" aria-hidden="true"></i>
                <span class="card-text">
                    <span class="matching-label">Matching search criteria</span>
                    ${result.matching_criteria ? `<br><span class="matching-value">${escapeHtml(result.matching_criteria)}</span>` : ''}
                </span>
            </div>
        `;

        resultsList.appendChild(card);
    });
}

/**
 * Render grid view with placeholder for profile-dependent columns
 * Note: Skills/Abilities/Knowledge require profile fetch - shows placeholder
 * @param {Array} results - Array of EnrichedSearchResult objects
 */
function renderGridView(results) {
    resultsList.className = 'results-list grid-view';

    // Grid header
    const header = document.createElement('div');
    header.className = 'grid-header';
    header.setAttribute('role', 'row');
    header.innerHTML = `
        <div class="grid-header-cell" role="columnheader">OaSIS Profile</div>
        <div class="grid-header-cell" role="columnheader">Top Skills</div>
        <div class="grid-header-cell" role="columnheader">Top Abilities</div>
        <div class="grid-header-cell" role="columnheader">Top Knowledge</div>
        <div class="grid-header-cell" role="columnheader">Matching Criteria</div>
    `;
    resultsList.appendChild(header);

    // Grid rows (skills/abilities/knowledge require profile fetch - show placeholder)
    results.forEach(function(result) {
        const row = document.createElement('div');
        row.className = 'grid-row';
        row.setAttribute('data-code', result.noc_code);
        row.setAttribute('role', 'row');
        row.setAttribute('tabindex', '0');
        row.innerHTML = `
            <div class="grid-cell" role="cell">
                <a href="#" class="grid-profile-link">${escapeHtml(result.noc_code)} - ${escapeHtml(result.title)}</a>
            </div>
            <div class="grid-cell" role="cell">${result.top_skills ? result.top_skills.slice(0, 3).join(', ') : '<span class="loading-text">Load profile for skills</span>'}</div>
            <div class="grid-cell" role="cell">${result.top_abilities ? result.top_abilities.slice(0, 3).join(', ') : '<span class="loading-text">Load profile for abilities</span>'}</div>
            <div class="grid-cell" role="cell">${result.top_knowledge ? result.top_knowledge.slice(0, 3).join(', ') : '<span class="loading-text">Load profile for knowledge</span>'}</div>
            <div class="grid-cell" role="cell">${escapeHtml(result.matching_criteria || '-')}</div>
        `;
        resultsList.appendChild(row);
    });
}
```

3. Add sort handler after the view toggle handler (around line 384):

```javascript
// Sort dropdown handler
sortSelect.addEventListener('change', function() {
    const sortValue = sortSelect.value;
    let sorted = [...lastResults];

    switch (sortValue) {
        case 'title-asc':
            sorted.sort((a, b) => a.title.localeCompare(b.title));
            break;
        case 'title-desc':
            sorted.sort((a, b) => b.title.localeCompare(a.title));
            break;
        case 'code-asc':
            sorted.sort((a, b) => a.noc_code.localeCompare(b.noc_code));
            break;
        case 'code-desc':
            sorted.sort((a, b) => b.noc_code.localeCompare(a.noc_code));
            break;
        case 'match':
        default:
            // Keep original order (API returns by match relevance)
            sorted = [...lastResults];
            break;
    }

    renderSearchResults(sorted);
});
```

4. Update the view toggle switch to update label text (in switchView function, around line 63):

```javascript
if (view === 'grid') {
    viewToggleLabel.textContent = 'Card view';
    viewToggle.setAttribute('aria-label', 'Switch to card view');
    viewToggle.setAttribute('title', 'Card view');
} else {
    viewToggleLabel.textContent = 'Grid view';
    viewToggle.setAttribute('aria-label', 'Switch to grid view');
    viewToggle.setAttribute('title', 'Grid view');
}
```

5. Update click handler for cards (in resultsList event listener, around line 387):

```javascript
// Event delegation for result clicks
resultsList.addEventListener('click', function(e) {
    // Handle card clicks (prevent link default, use data-code)
    const card = e.target.closest('.oasis-card, .grid-row');
    if (card) {
        e.preventDefault();
        const code = card.getAttribute('data-code');
        if (code) {
            handleResultClick(code);
        }
        return;
    }

    // Fallback for direct li clicks (legacy)
    const li = e.target.closest('li[data-code]');
    if (li) {
        const code = li.getAttribute('data-code');
        handleResultClick(code);
    }
});

// Keyboard navigation for cards
resultsList.addEventListener('keydown', function(e) {
    if (e.key === 'Enter' || e.key === ' ') {
        const card = e.target.closest('.oasis-card, .grid-row');
        if (card) {
            e.preventDefault();
            const code = card.getAttribute('data-code');
            if (code) {
                handleResultClick(code);
            }
        }
    }
});
```
  </action>
  <verify>
Run the app and test:
1. Search for "pilot" - should show OaSIS-style cards with icons
2. Cards should display: header with code/title, broad category, TEER, lead statement, matching criteria
3. Sort dropdown should reorder cards
4. Clicking a card should navigate to profile
5. View toggle should switch between card and grid views
6. Grid view shows "Load profile for skills/abilities/knowledge" placeholders
  </verify>
  <done>
Card view renders with OaSIS styling and icons. Sort dropdown works. Cards are clickable with keyboard support. View toggle switches views. Grid view shows placeholder text for profile-dependent columns.
  </done>
</task>

</tasks>

<verification>
After all tasks complete:

1. **Visual verification:**
   - Open http://localhost:5000
   - Search for "pilot"
   - Cards display with OaSIS styling:
     - Header with NOC code and title (clickable)
     - Broad category with truck icon
     - TEER with bookmark icon
     - Lead statement with book icon
     - Footer with matching criteria and search icon

2. **Sort verification:**
   - Change sort to "Label - A to Z" - cards reorder alphabetically
   - Change sort to "Code - Ascending" - cards reorder by NOC code
   - Change sort to "Matching search criteria" - returns to original order

3. **Click verification:**
   - Click on a card - navigates to profile details
   - Press Enter on focused card - navigates to profile details

4. **View toggle verification:**
   - Click "Grid view" - switches to grid layout
   - Grid shows "Load profile for skills/abilities/knowledge" in respective columns
   - Click "Card view" - switches back to cards

5. **Responsive verification:**
   - Resize to mobile width - cards stack properly
   - Sort controls stack vertically
</verification>

<success_criteria>
- [ ] results-cards.css file exists with OaSIS-inspired styles
- [ ] Font Awesome linked for icons
- [ ] Sort dropdown visible with 5 sort options
- [ ] Cards render with enriched data (lead_statement, teer_description, etc.)
- [ ] Cards show icons: truck/bookmark/book/search
- [ ] Sort dropdown reorders cards correctly
- [ ] Clicking card navigates to profile
- [ ] Keyboard Enter on card navigates to profile
- [ ] View toggle switches between card/grid
- [ ] Grid view shows placeholder text for skills/abilities/knowledge columns
- [ ] Results count displays correctly
- [ ] Responsive layout works on mobile
</success_criteria>

<output>
After completion, create `.planning/phases/08-B-results-cards-grid/08-B-02-SUMMARY.md`
</output>
