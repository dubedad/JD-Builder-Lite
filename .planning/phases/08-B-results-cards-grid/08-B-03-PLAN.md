---
phase: 08-B-results-cards-grid
plan: 03
type: execute
wave: 2
depends_on: ["08-B-01"]
files_modified:
  - templates/index.html
  - static/css/filters.css
  - static/js/filters.js
  - static/js/main.js
autonomous: true

must_haves:
  truths:
    - "Filter panel visible with Minor Unit Group section"
    - "Minor Unit Group filter checkboxes populated from search results"
    - "Selecting Minor Unit Group checkbox narrows displayed results"
    - "Clearing filters restores all results"
    - "Multiple Minor Unit Group filters can be combined (OR logic within group)"
    - "Feeder Group Mobility filter section visible with placeholder message indicating profile data required"
    - "Career Progression filter section visible with placeholder message indicating profile data required"
  artifacts:
    - path: "static/css/filters.css"
      provides: "Filter panel styles"
      contains: ".filter-panel"
    - path: "static/js/filters.js"
      provides: "Filter logic and state management"
      contains: "applyFilters"
    - path: "templates/index.html"
      provides: "Filter panel HTML container"
      contains: "filter-panel"
  key_links:
    - from: "static/js/filters.js"
      to: "static/js/main.js"
      via: "calls renderSearchResults with filtered results"
      pattern: "renderSearchResults"
    - from: "templates/index.html"
      to: "static/css/filters.css"
      via: "stylesheet link"
      pattern: "filters.css"
    - from: "templates/index.html"
      to: "static/js/filters.js"
      via: "script tag"
      pattern: "filters.js"
---

<objective>
Implement custom filter panel for search results with Minor Unit Group filter (functional) and Feeder Group Mobility / Career Progression filters (UI structure with placeholders).

Purpose: Enable users to narrow search results by NOC minor group (DISP-22). The Minor Unit Group filter is fully functional using data derived from search results. Feeder Group Mobility and Career Progression filters are scaffolded as UI placeholders since they require profile data not available from search results.

Output: New filter panel CSS, filter logic JavaScript module, filter UI integrated into search results page.

**Scope note (DISP-22 partial):** This plan delivers:
- Minor Unit Group filter: FULLY FUNCTIONAL (uses minor_group from search results)
- Feeder Group Mobility filter: UI ONLY with placeholder "Select a profile to enable mobility filtering"
- Career Progression filter: UI ONLY with placeholder "Select a profile to enable progression filtering"

Full Feeder/Career filtering requires profile data and is deferred to Phase 08-C or future enhancement.
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
@static/js/main.js
</context>

<tasks>

<task type="auto">
  <name>Task 1: Create filter panel styles</name>
  <files>static/css/filters.css, templates/index.html</files>
  <action>
1. Create new file static/css/filters.css:

```css
/* Filter Panel Styles
   Based on OASIS-HTML-REFERENCE.md filter patterns
*/

/* Results Layout with Filter Panel */
.results-layout {
    display: flex;
    gap: 1.5rem;
    align-items: flex-start;
}

.results-main {
    flex: 1;
    min-width: 0;
}

/* Filter Panel */
.filter-panel {
    width: 280px;
    flex-shrink: 0;
    background: var(--bg);
    border: 1px solid var(--border);
    border-radius: 4px;
    padding: 1rem;
}

.filter-panel h3 {
    font-size: 1rem;
    font-weight: 600;
    margin: 0 0 1rem 0;
    padding-bottom: 0.5rem;
    border-bottom: 1px solid var(--border);
}

/* Filter Groups (collapsible details) */
.filter-group {
    margin-bottom: 0.75rem;
    border: 1px solid var(--border);
    border-radius: 4px;
}

.filter-group summary {
    padding: 0.75rem;
    font-weight: 500;
    cursor: pointer;
    background: var(--highlight);
    list-style: none;
    display: flex;
    justify-content: space-between;
    align-items: center;
}

.filter-group summary::-webkit-details-marker {
    display: none;
}

.filter-group summary::after {
    content: '+';
    font-weight: bold;
    font-size: 1.25rem;
    color: var(--text-light);
}

.filter-group[open] summary::after {
    content: '-';
}

.filter-group summary:hover {
    background: var(--border-light, #f0f0f0);
}

.filter-group summary:focus {
    outline: 2px solid var(--accent);
    outline-offset: -2px;
}

/* Filter Fieldset */
.filter-group fieldset {
    border: none;
    margin: 0;
    padding: 0.5rem 0.75rem;
    max-height: 200px;
    overflow-y: auto;
}

.filter-group legend {
    display: none;
}

/* Filter Checkboxes */
.filter-checkbox {
    display: flex;
    align-items: flex-start;
    gap: 0.5rem;
    padding: 0.25rem 0;
    font-size: 0.875rem;
    cursor: pointer;
}

.filter-checkbox input[type="checkbox"] {
    margin-top: 0.25rem;
    flex-shrink: 0;
}

.filter-checkbox-label {
    line-height: 1.4;
    word-break: break-word;
}

.filter-checkbox-count {
    color: var(--text-light);
    font-size: 0.75rem;
    margin-left: 0.25rem;
}

/* Clear Filters Button */
.filter-clear {
    width: 100%;
    padding: 0.5rem;
    margin-top: 1rem;
    background: var(--bg);
    border: 1px solid var(--border);
    border-radius: 4px;
    cursor: pointer;
    font-size: 0.875rem;
}

.filter-clear:hover {
    background: var(--highlight);
}

.filter-clear:disabled {
    opacity: 0.5;
    cursor: not-allowed;
}

/* Active Filter Badge */
.filter-active-count {
    background: var(--accent);
    color: white;
    font-size: 0.75rem;
    padding: 0.125rem 0.5rem;
    border-radius: 10px;
    margin-left: 0.5rem;
}

/* Empty Filter State */
.filter-empty {
    padding: 0.75rem;
    color: var(--text-light);
    font-size: 0.875rem;
    font-style: italic;
    text-align: center;
}

/* Responsive: Hide filter panel on mobile */
@media (max-width: 768px) {
    .results-layout {
        flex-direction: column;
    }

    .filter-panel {
        width: 100%;
        order: -1; /* Filters above results on mobile */
    }

    /* Collapse all filter groups by default on mobile */
    .filter-group:not([open]) {
        /* Default closed on mobile for space */
    }
}

/* Filter Panel Toggle (for mobile) */
.filter-toggle {
    display: none;
    width: 100%;
    padding: 0.75rem;
    background: var(--bg);
    border: 1px solid var(--border);
    border-radius: 4px;
    cursor: pointer;
    margin-bottom: 1rem;
}

@media (max-width: 768px) {
    .filter-toggle {
        display: flex;
        justify-content: space-between;
        align-items: center;
    }

    .filter-panel.collapsed {
        display: none;
    }
}
```

2. Add CSS link to templates/index.html after results-cards.css (around line 12):
```html
<link rel="stylesheet" href="/static/css/filters.css">
```
  </action>
  <verify>
Check CSS file exists:
```bash
ls -la static/css/filters.css
grep "filters.css" templates/index.html
```
  </verify>
  <done>
Filter panel CSS created with collapsible groups, checkbox styles, responsive layout. CSS linked in index.html.
  </done>
</task>

<task type="auto">
  <name>Task 2: Add filter panel HTML structure</name>
  <files>templates/index.html</files>
  <action>
Update the search-results section in templates/index.html to add filter panel.

Find the search-results section (around line 55-70) and wrap the content in a layout container. The section should look like:

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

    <!-- Filter Toggle (mobile) -->
    <button id="filter-toggle" class="filter-toggle" type="button">
        <span>Filter Results</span>
        <span id="filter-active-indicator"></span>
    </button>

    <!-- Results Layout with Filter Panel -->
    <div class="results-layout">
        <!-- Filter Panel -->
        <aside id="filter-panel" class="filter-panel">
            <h3>Filter items</h3>

            <!-- Minor Unit Group Filter (FUNCTIONAL) -->
            <details class="filter-group" id="filter-minor-group" open>
                <summary>Minor Unit Group</summary>
                <fieldset>
                    <legend>Filter by Minor Unit Group</legend>
                    <div id="filter-minor-group-options" class="filter-options">
                        <p class="filter-empty">Search to see filter options</p>
                    </div>
                </fieldset>
            </details>

            <!-- Feeder Group Mobility Filter (PLACEHOLDER - requires profile data) -->
            <details class="filter-group" id="filter-feeder-mobility">
                <summary>Feeder Group Mobility</summary>
                <fieldset>
                    <legend>Filter by Feeder Group Mobility</legend>
                    <div id="filter-feeder-options" class="filter-options">
                        <p class="filter-empty">Select a profile to enable mobility filtering</p>
                    </div>
                </fieldset>
            </details>

            <!-- Career Progression Filter (PLACEHOLDER - requires profile data) -->
            <details class="filter-group" id="filter-career-progression">
                <summary>Career Progression</summary>
                <fieldset>
                    <legend>Filter by Career Progression</legend>
                    <div id="filter-progression-options" class="filter-options">
                        <p class="filter-empty">Select a profile to enable progression filtering</p>
                    </div>
                </fieldset>
            </details>

            <button id="filter-clear" class="filter-clear" type="button" disabled>
                Clear all filters
            </button>
        </aside>

        <!-- Results Main Content -->
        <div class="results-main">
            <div id="results-list" class="results-cards-container" role="list"></div>
        </div>
    </div>
</section>
```

Note: The Feeder Group Mobility and Career Progression filters show placeholder text because they require profile data (fetched when user views a profile). The Minor Unit Group filter can be populated from search results immediately.
  </action>
  <verify>
Verify filter panel HTML structure:
```bash
grep "filter-panel" templates/index.html
grep "filter-minor-group" templates/index.html
grep "filter-feeder-mobility" templates/index.html
grep "filter-career-progression" templates/index.html
grep "Select a profile to enable" templates/index.html
```
  </verify>
  <done>
Filter panel HTML added with three filter groups (Minor Unit Group functional, Feeder/Career as placeholders), clear button, and mobile toggle. Integrated into results layout.
  </done>
</task>

<task type="auto">
  <name>Task 3: Create filter JavaScript module</name>
  <files>static/js/filters.js, templates/index.html, static/js/main.js</files>
  <action>
1. Create new file static/js/filters.js:

```javascript
/**
 * Filter Panel Module
 * Handles filtering of search results by Minor Unit Group.
 *
 * Note: Feeder Group Mobility and Career Progression filters are UI placeholders.
 * They require profile data which is not available from search results.
 * Full implementation deferred to Phase 08-C or future enhancement.
 */

(function() {
    'use strict';

    // Filter state
    const filters = {
        minorGroup: new Set(),
        feederMobility: new Set(),      // Placeholder - not functional
        careerProgression: new Set()    // Placeholder - not functional
    };

    // Store all results for filtering
    let allResults = [];
    let renderCallback = null;

    // DOM references
    let minorGroupOptions = null;
    let feederOptions = null;
    let progressionOptions = null;
    let clearButton = null;
    let filterToggle = null;
    let filterPanel = null;
    let activeIndicator = null;

    /**
     * Initialize filter module
     * @param {Function} onFilterChange - Callback when filters change (receives filtered results)
     */
    function initFilters(onFilterChange) {
        renderCallback = onFilterChange;

        // Cache DOM references
        minorGroupOptions = document.getElementById('filter-minor-group-options');
        feederOptions = document.getElementById('filter-feeder-options');
        progressionOptions = document.getElementById('filter-progression-options');
        clearButton = document.getElementById('filter-clear');
        filterToggle = document.getElementById('filter-toggle');
        filterPanel = document.getElementById('filter-panel');
        activeIndicator = document.getElementById('filter-active-indicator');

        if (!minorGroupOptions) {
            console.warn('Filter elements not found, filters disabled');
            return;
        }

        // Bind clear button
        if (clearButton) {
            clearButton.addEventListener('click', clearAllFilters);
        }

        // Bind mobile toggle
        if (filterToggle && filterPanel) {
            filterToggle.addEventListener('click', function() {
                filterPanel.classList.toggle('collapsed');
            });
        }

        // Bind filter change events (event delegation)
        const filterPanelEl = document.getElementById('filter-panel');
        if (filterPanelEl) {
            filterPanelEl.addEventListener('change', handleFilterChange);
        }
    }

    /**
     * Update filter options based on search results
     * @param {Array} results - EnrichedSearchResult objects
     */
    function updateFilterOptions(results) {
        allResults = results;

        // Build Minor Group options from results
        const minorGroups = new Map();
        results.forEach(r => {
            if (r.minor_group) {
                const key = r.minor_group;
                if (!minorGroups.has(key)) {
                    minorGroups.set(key, {
                        code: key,
                        name: r.minor_group_name || `Minor Group ${key}`,
                        count: 0
                    });
                }
                minorGroups.get(key).count++;
            }
        });

        // Render Minor Group checkboxes
        if (minorGroupOptions) {
            if (minorGroups.size === 0) {
                minorGroupOptions.innerHTML = '<p class="filter-empty">No minor groups in results</p>';
            } else {
                const sorted = Array.from(minorGroups.values()).sort((a, b) => a.code.localeCompare(b.code));
                minorGroupOptions.innerHTML = sorted.map(group => `
                    <label class="filter-checkbox">
                        <input type="checkbox" name="minorGroup" value="${escapeHtml(group.code)}"
                               ${filters.minorGroup.has(group.code) ? 'checked' : ''}>
                        <span class="filter-checkbox-label">
                            ${escapeHtml(group.code)} - ${escapeHtml(group.name)}
                            <span class="filter-checkbox-count">(${group.count})</span>
                        </span>
                    </label>
                `).join('');
            }
        }

        // Feeder Mobility and Career Progression: Keep placeholder messages
        // These require profile data which is not available from search results
        if (feederOptions) {
            feederOptions.innerHTML = '<p class="filter-empty">Select a profile to enable mobility filtering</p>';
        }
        if (progressionOptions) {
            progressionOptions.innerHTML = '<p class="filter-empty">Select a profile to enable progression filtering</p>';
        }

        // Clear existing filters that no longer apply
        const validMinorGroups = new Set(minorGroups.keys());
        filters.minorGroup.forEach(mg => {
            if (!validMinorGroups.has(mg)) {
                filters.minorGroup.delete(mg);
            }
        });

        updateClearButton();
    }

    /**
     * Handle filter checkbox change
     * @param {Event} e - Change event
     */
    function handleFilterChange(e) {
        const checkbox = e.target;
        if (checkbox.type !== 'checkbox') return;

        const filterType = checkbox.name;
        const value = checkbox.value;

        if (!filters[filterType]) return;

        if (checkbox.checked) {
            filters[filterType].add(value);
        } else {
            filters[filterType].delete(value);
        }

        applyFilters();
        updateClearButton();
    }

    /**
     * Apply current filters and trigger callback
     */
    function applyFilters() {
        const filtered = allResults.filter(result => {
            // Check minor group filter (OR logic - any checked group matches)
            if (filters.minorGroup.size > 0) {
                if (!result.minor_group || !filters.minorGroup.has(result.minor_group)) {
                    return false;
                }
            }

            // Feeder mobility filter: placeholder, not functional
            // Full implementation requires profile data (Phase 08-C or future)

            // Career progression filter: placeholder, not functional
            // Full implementation requires profile data (Phase 08-C or future)

            return true;
        });

        if (renderCallback) {
            renderCallback(filtered);
        }
    }

    /**
     * Clear all filters
     */
    function clearAllFilters() {
        filters.minorGroup.clear();
        filters.feederMobility.clear();
        filters.careerProgression.clear();

        // Uncheck all checkboxes
        const checkboxes = document.querySelectorAll('#filter-panel input[type="checkbox"]');
        checkboxes.forEach(cb => cb.checked = false);

        applyFilters();
        updateClearButton();
    }

    /**
     * Update clear button state
     */
    function updateClearButton() {
        const activeCount = filters.minorGroup.size + filters.feederMobility.size + filters.careerProgression.size;

        if (clearButton) {
            clearButton.disabled = activeCount === 0;
        }

        if (activeIndicator) {
            if (activeCount > 0) {
                activeIndicator.innerHTML = `<span class="filter-active-count">${activeCount}</span>`;
            } else {
                activeIndicator.innerHTML = '';
            }
        }
    }

    /**
     * Get current filter state
     * @returns {Object} Filter state object
     */
    function getFilterState() {
        return {
            minorGroup: Array.from(filters.minorGroup),
            feederMobility: Array.from(filters.feederMobility),
            careerProgression: Array.from(filters.careerProgression)
        };
    }

    /**
     * Escape HTML special characters
     */
    function escapeHtml(text) {
        if (!text) return '';
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }

    // Export to global scope
    window.filterModule = {
        init: initFilters,
        updateOptions: updateFilterOptions,
        clear: clearAllFilters,
        getState: getFilterState
    };
})();
```

2. Add script tag to templates/index.html BEFORE main.js (around line 133):
```html
<script src="/static/js/filters.js"></script>
```

3. Update static/js/main.js to integrate filters:

Add filter initialization after the existing module initializations (around line 34):
```javascript
// Initialize filter module
filterModule.init(function(filteredResults) {
    renderSearchResults(filteredResults);
});
```

In the handleSearch function, after receiving results (around line 322), add filter update:
```javascript
const response = await api.search(query, currentSearchType);

// Update filter options with new results
filterModule.updateOptions(response.results);

// Clear any previous filters when doing new search
filterModule.clear();

renderSearchResults(response.results);
```

Note: The filter module stores allResults internally and calls renderSearchResults with filtered results when filters change.
  </action>
  <verify>
Test filter functionality:
1. Search for "software" - Minor Unit Group filter should populate with groups from results
2. Check a minor group checkbox - results should filter down
3. Check another checkbox - further filtering (OR logic within minor group)
4. Click "Clear all filters" - all results return
5. Active filter count badge appears when filters active
6. Feeder/Career filters show placeholder text (not functional)
  </verify>
  <done>
Filter module created with Minor Unit Group filtering functional. Feeder Mobility and Career Progression filters show placeholder messages (require profile data - deferred to Phase 08-C). Filters integrate with main.js. Clear button and active count work.
  </done>
</task>

</tasks>

<verification>
After all tasks complete:

1. **Layout verification:**
   - Open http://localhost:5000
   - Search for "pilot"
   - Filter panel visible on left side of results
   - Three filter groups: Minor Unit Group, Feeder Group Mobility, Career Progression

2. **Minor Group filter verification (FUNCTIONAL):**
   - Minor Unit Group filter populates with groups from results
   - Each group shows count (e.g., "726 - Minor Group 726 (3)")
   - Checking a group filters results to only that group
   - Checking multiple groups shows results from any checked group (OR logic)

3. **Placeholder verification:**
   - Feeder Group Mobility shows "Select a profile to enable mobility filtering"
   - Career Progression shows "Select a profile to enable progression filtering"
   - These are UI placeholders - filtering not functional

4. **Clear filter verification:**
   - With filters active, badge shows count
   - Click "Clear all filters" - all results return
   - Checkboxes are unchecked
   - Badge disappears

5. **New search verification:**
   - Perform new search - filters are cleared
   - Minor Group filter repopulates with new results

6. **Responsive verification:**
   - Resize to mobile - filter toggle button appears
   - Click toggle - panel shows/hides
   - Filters above results on mobile
</verification>

<success_criteria>
- [ ] filters.css file exists with panel, group, checkbox styles
- [ ] Filter panel visible in results layout (left sidebar)
- [ ] Three filter groups render with collapsible details
- [ ] Minor Unit Group filter populates from search results
- [ ] Checking Minor Group checkbox filters results (OR logic)
- [ ] Clear all filters button restores all results
- [ ] Active filter count badge appears when filters active
- [ ] Feeder Group Mobility shows placeholder message
- [ ] Career Progression shows placeholder message
- [ ] filters.js module exports init, updateOptions, clear, getState
- [ ] main.js integrates filter module
- [ ] Responsive layout works (mobile toggle, stacked layout)
</success_criteria>

<output>
After completion, create `.planning/phases/08-B-results-cards-grid/08-B-03-SUMMARY.md`
</output>
