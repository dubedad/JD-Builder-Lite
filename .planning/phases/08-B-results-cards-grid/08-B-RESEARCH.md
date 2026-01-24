# Phase 08-B: Results Cards & Grid - Research

**Researched:** 2026-01-24
**Domain:** Frontend UI (HTML/CSS/JavaScript), Flask API, OaSIS HTML patterns
**Confidence:** HIGH

## Summary

This phase redesigns the Step 4 occupational profile menu (search results display) with two major components:

1. **Card View** - Replicates OaSIS exactly with 6 data points per card: lead statement, example titles, TEER, mobility/progression, source table, and publication date
2. **Grid View** - Uses CUSTOM columns (different from OaSIS): OaSIS Profile | Top 10 Skills | Top Abilities | Top Knowledge | Matching criteria
3. **Custom Filters** - Replaces OaSIS filters with: Minor Unit Group, Feeder Group Mobility, Career Progression

The implementation requires significant backend changes to return enriched search results (currently only returns `noc_code`, `title`, `url`), plus frontend work to render the new card/grid structures and filter panel.

**Primary recommendation:** Extend backend `/api/search` to return enriched results with all 6 card data points, then implement OaSIS-style HTML structure for cards. Grid view requires profile data (skills/abilities/knowledge) which needs a design decision - either batch fetch or lazy load.

## Standard Stack

The established libraries/tools for this domain:

### Core
| Library | Version | Purpose | Why Standard |
|---------|---------|---------|--------------|
| Flask | 2.x | Backend API routes | Already in use |
| BeautifulSoup4 | 4.x | HTML parsing for search results | Already in use (parser.py) |
| Vanilla JS | ES6+ | Frontend rendering | Already in use, no framework |
| CSS Custom Properties | Native | Color/style variables | Already defined in main.css |

### Supporting
| Library | Version | Purpose | When to Use |
|---------|---------|---------|-------------|
| Font Awesome | CDN | Icons (fa-truck, fa-bookmark, fa-book, fa-search) | OaSIS card icons |

### Alternatives Considered
| Instead of | Could Use | Tradeoff |
|------------|-----------|----------|
| Vanilla filtering | DataTables.js | Adds dependency, overkill for 3 filters |
| CSS Grid for cards | Flexbox | Grid better for responsive card layouts |
| Manual pagination | Library | Manual is simpler for ~50 results max |

**Installation:**
No new dependencies required. Font Awesome may be added via CDN for icons if not already present.

## Architecture Patterns

### Current Search Data Flow
```
User enters query
    |
    v
api.js: search(query) --> /api/search?q={query}
    |
    v
api.py: scraper.search(query) --> OaSIS HTML
    |
    v
parser.py: parse_search_results(html) --> List[SearchResult]
    |
    v
SearchResult: { noc_code, title, url } <-- INSUFFICIENT FOR CARDS
    |
    v
main.js: renderSearchResults(results) --> Display
```

### Required Data Flow (Enhanced)
```
User enters query
    |
    v
api.js: search(query) --> /api/search?q={query}
    |
    v
api.py: scraper.search(query) --> OaSIS HTML
    |
    v
parser.py: parse_search_results_enhanced(html) --> List[EnrichedSearchResult]
    |
    v
EnrichedSearchResult: {
    noc_code,
    title,
    url,
    lead_statement,        # NEW - from OaSIS card
    example_titles,        # NEW - from OaSIS card
    teer_description,      # NEW - from OaSIS card
    mobility_progression,  # NEW - requires profile fetch
    source_table,          # NEW - requires profile fetch
    publication_date,      # NEW - requires profile fetch
    broad_category,        # For filtering
    minor_group            # For filtering
}
    |
    v
main.js: renderSearchResults(results) --> Card/Grid Display
```

### Recommended Project Structure Changes
```
src/
  models/
    noc.py              # Add EnrichedSearchResult model
  services/
    parser.py           # Enhance parse_search_results()
  routes/
    api.py              # Return enriched results

static/
  css/
    main.css            # Add card/filter styles
    results-cards.css   # NEW - OaSIS card styles
  js/
    main.js             # Update renderSearchResults()
    filters.js          # NEW - Filter panel logic
```

### Pattern 1: OaSIS Card Structure
**What:** Table-based card layout matching OaSIS exactly
**When to use:** Default card view for search results
**Example:**
```html
<!-- Source: OASIS-HTML-REFERENCE.md lines 389-466 -->
<table class="cards wb-tables table">
    <thead class="hideTableHeader"><!-- Hidden headers for accessibility --></thead>
    <tbody>
        <tr class="eqht-trgt cardsTr" data-code="72600.01">
            <!-- OaSIS Profile link -->
            <td class="bottomPadding">
                <span class="cardsheader">
                    <a href="#">72600.01 - Air pilots</a>
                </span>
            </td>
            <!-- Lead Statement -->
            <td class="topPadding">
                <i class="fa fa-book OaSISIconTopCorrected" aria-hidden="true"></i>
                <span class="OaSISCardTDTextStyle">
                    Air pilots fly fixed wing aircraft...
                </span>
            </td>
            <!-- Example Titles (Also Known As) -->
            <td class="topPadding">
                <i class="fa fa-truck OaSISIconTopCorrected" aria-hidden="true"></i>
                <span class="OaSISCardTDTextStyle">
                    Airline pilot, Flight instructor...
                </span>
            </td>
            <!-- TEER -->
            <td class="topPadding">
                <i class="fa fa-bookmark OaSISIconTopCorrected" aria-hidden="true"></i>
                <span class="OaSISCardTDTextStyle">
                    Occupations usually require a college diploma...
                </span>
            </td>
            <!-- Mobility/Progression -->
            <td class="topPadding">
                <span class="OaSISCardTDTextStyle">
                    From: Flight instructors, To: Senior pilots...
                </span>
            </td>
            <!-- Source & Date -->
            <td class="topBorder">
                <span class="OaSISCardTDTextStyle">
                    Source: OaSIS 2025 | Published: 2025-01-15
                </span>
            </td>
        </tr>
    </tbody>
</table>
```

### Pattern 2: Custom Grid View Structure
**What:** CSS Grid table for custom columns
**When to use:** Grid view toggle
**Example:**
```html
<div class="results-grid">
    <div class="grid-header">
        <div class="grid-cell">OaSIS Profile</div>
        <div class="grid-cell">Top 10 Skills</div>
        <div class="grid-cell">Top Abilities</div>
        <div class="grid-cell">Top Knowledge</div>
        <div class="grid-cell">Matching Criteria</div>
    </div>
    <div class="grid-row" data-code="72600.01">
        <div class="grid-cell profile-cell">
            <a href="#">72600.01 - Air pilots</a>
        </div>
        <div class="grid-cell skills-cell">
            Critical thinking, Problem solving...
        </div>
        <div class="grid-cell abilities-cell">
            Deductive reasoning, Oral comprehension...
        </div>
        <div class="grid-cell knowledge-cell">
            Transportation, Mathematics...
        </div>
        <div class="grid-cell matching-cell">
            Label, Job titles
        </div>
    </div>
</div>
```

### Pattern 3: Filter Panel Structure
**What:** Collapsible filter checkboxes
**When to use:** Left sidebar filter panel
**Example:**
```html
<!-- Source: OASIS-HTML-REFERENCE.md lines 339-359 -->
<div class="filter-panel">
    <h2 class="h4">Filter items</h2>

    <details class="filter-group" open>
        <summary>Minor Unit Group</summary>
        <fieldset>
            <div class="checkbox">
                <label>
                    <input type="checkbox" name="minorGroup" value="212">
                    212 - Professional occupations in applied sciences
                </label>
            </div>
            <!-- More checkboxes -->
        </fieldset>
    </details>

    <details class="filter-group">
        <summary>Feeder Group Mobility</summary>
        <!-- Checkboxes for career entry paths -->
    </details>

    <details class="filter-group">
        <summary>Career Progression</summary>
        <!-- Checkboxes for advancement paths -->
    </details>
</div>
```

### Anti-Patterns to Avoid
- **Fetching profile data for every search result:** Would cause N+1 problem. Batch or cache instead.
- **Duplicating card HTML in multiple places:** Create reusable render function.
- **Hardcoding filter options:** Extract from search results dynamically.
- **Using `display:none` for filters:** Use `visibility` or CSS class to maintain layout.

## Don't Hand-Roll

Problems that look simple but have existing solutions:

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| Card layout | Custom CSS grid | OaSIS table structure | Already have exact HTML reference |
| Icon styling | Custom icons | Font Awesome classes | OaSIS uses fa-truck, fa-bookmark, fa-book, fa-search |
| Filter state | Complex state management | Simple object + localStorage | Only 3 filters, low complexity |
| Pagination | Custom pagination | Simple slice + render | OaSIS uses "Show X entries" dropdown |
| Sort dropdown | Custom select | Native HTML select | Matches OaSIS pattern |

**Key insight:** The OASIS-HTML-REFERENCE.md provides exact HTML for cards, filters, and sort controls. Replicate rather than reinvent.

## Common Pitfalls

### Pitfall 1: N+1 Query Problem for Grid View
**What goes wrong:** Grid view needs skills/abilities/knowledge which requires profile fetch for each result
**Why it happens:** Search results from OaSIS only contain card data, not full profile
**How to avoid:**
- Option A: Lazy load grid data on view switch (user experience tradeoff)
- Option B: Return partial profile data from search (requires scraping optimization)
- Option C: Cache profile data client-side after first fetch
**Warning signs:** Grid view takes 5+ seconds to load with many results

### Pitfall 2: Missing Data in OaSIS Search Results
**What goes wrong:** Not all card data points are in OaSIS search results HTML
**Why it happens:** OaSIS search results have limited data; mobility/progression requires profile fetch
**How to avoid:** For cards, show what's available immediately; fetch remaining on click or lazy load
**Warning signs:** Cards display "N/A" for most fields

### Pitfall 3: Filter Options Explosion
**What goes wrong:** Too many filter options make panel overwhelming
**Why it happens:** NOC has hundreds of minor groups, many mobility paths
**How to avoid:** Only show filter options that appear in current search results
**Warning signs:** Filter panel longer than search results

### Pitfall 4: View Toggle State Loss
**What goes wrong:** User toggles to grid, searches again, view resets to card
**Why it happens:** Not persisting view preference or re-applying after search
**How to avoid:** Store view preference in localStorage, apply on every render
**Warning signs:** User must toggle twice after each search

### Pitfall 5: Inconsistent Click Behavior
**What goes wrong:** Clicking card goes to profile details but doesn't work consistently
**Why it happens:** Event delegation not handling both table rows and grid rows
**How to avoid:** Use consistent `data-code` attribute, single click handler
**Warning signs:** Some cards clickable, others not

## Code Examples

Verified patterns from codebase and OaSIS reference.

### Current SearchResult Model (noc.py lines 19-25)
```python
class SearchResult(BaseModel):
    """Single search result from OASIS."""
    noc_code: str
    title: str
    url: str
    # ONLY 3 FIELDS - Needs extension for card view
```

### Enhanced SearchResult Model (proposed)
```python
class EnrichedSearchResult(BaseModel):
    """Enhanced search result with card data."""
    # Core (existing)
    noc_code: str
    title: str
    url: str

    # Card View Data (DISP-20)
    lead_statement: Optional[str] = None
    example_titles: Optional[str] = None  # Comma-separated
    teer_description: Optional[str] = None
    mobility_progression: Optional[str] = None  # May need profile fetch
    source_table: Optional[str] = None
    publication_date: Optional[str] = None

    # For Filtering (DISP-22)
    broad_category: Optional[int] = None  # First digit of NOC code
    broad_category_name: Optional[str] = None
    minor_group: Optional[str] = None  # First 3 digits
    minor_group_name: Optional[str] = None

    # For Grid View (DISP-21)
    top_skills: Optional[List[str]] = None  # Requires profile fetch
    top_abilities: Optional[List[str]] = None  # Requires profile fetch
    top_knowledge: Optional[List[str]] = None  # Requires profile fetch
    matching_criteria: Optional[str] = None  # From search match
```

### Current parse_search_results (parser.py lines 23-76)
```python
def parse_search_results(self, html: str) -> List[SearchResult]:
    """Parse search results HTML into SearchResult models."""
    soup = BeautifulSoup(html, 'lxml')
    results = []

    # Current: only extracts noc_code, title, url
    for element in elements:
        link = element.select_one(link_primary)
        text = link.get_text(strip=True)
        href = link.get('href', '')
        code_match = self.NOC_CODE_PATTERN.search(text)

        results.append(SearchResult(
            noc_code=noc_code,
            title=title,
            url=href
        ))
    return results
```

### Enhanced parse_search_results (proposed)
```python
def parse_search_results_enhanced(self, html: str) -> List[EnrichedSearchResult]:
    """Parse search results with all card data points."""
    soup = BeautifulSoup(html, 'lxml')
    results = []

    # Find card rows in OaSIS structure
    rows = soup.select('tr.cardsTr')  # From OASIS-HTML-REFERENCE.md

    for row in rows:
        # Extract NOC code and title from link
        link = row.select_one('.cardsheader a')
        if not link:
            continue

        href = link.get('href', '')
        code_match = self.NOC_CODE_PATTERN.search(href)
        noc_code = code_match.group(0) if code_match else None
        title = link.get_text(strip=True).split(' - ', 1)[-1] if ' - ' in link.get_text() else link.get_text(strip=True)

        # Extract lead statement (fa-book icon cell)
        lead_cell = row.select_one('td:has(.fa-book) .OaSISCardTDTextStyle')
        lead_statement = lead_cell.get_text(strip=True) if lead_cell else None

        # Extract TEER (fa-bookmark icon cell)
        teer_cell = row.select_one('td:has(.fa-bookmark) .OaSISCardTDTextStyle')
        teer_description = teer_cell.get_text(strip=True) if teer_cell else None

        # Extract broad category (fa-truck or similar icon cell)
        boc_cell = row.select_one('td:has(.fa-truck) .OaSISCardTDTextStyle, td:has(.fa-pen-alt) .OaSISCardTDTextStyle')
        broad_category_name = boc_cell.get_text(strip=True) if boc_cell else None

        # Extract matching criteria
        match_cell = row.select_one('td:has(.fa-search) .OaSISCardTDTextStyle')
        matching_criteria = match_cell.get_text(strip=True) if match_cell else None

        # Derive minor group from NOC code
        base_code = noc_code.split('.')[0] if noc_code else ''
        minor_group = base_code[:3] if len(base_code) >= 3 else None
        broad_category = int(base_code[0]) if base_code else None

        results.append(EnrichedSearchResult(
            noc_code=noc_code,
            title=title,
            url=href,
            lead_statement=lead_statement,
            teer_description=teer_description,
            broad_category=broad_category,
            broad_category_name=broad_category_name,
            minor_group=minor_group,
            matching_criteria=matching_criteria
            # Note: example_titles, mobility_progression, source_table,
            # publication_date, skills, abilities, knowledge require profile fetch
        ))

    return results
```

### Card Rendering JavaScript (proposed)
```javascript
// Add to main.js or new results-cards.js

function renderCardView(results) {
    const container = document.getElementById('results-list');
    container.innerHTML = '';
    container.className = 'cards-container';

    results.forEach(result => {
        const card = document.createElement('div');
        card.className = 'oasis-card';
        card.dataset.code = result.noc_code;

        card.innerHTML = `
            <div class="card-header">
                <a href="#" class="card-title">${escapeHtml(result.noc_code)} - ${escapeHtml(result.title)}</a>
            </div>
            <div class="card-row">
                <i class="fa fa-book card-icon" aria-hidden="true"></i>
                <span class="card-text">${escapeHtml(result.lead_statement || 'No lead statement')}</span>
            </div>
            <div class="card-row">
                <i class="fa fa-users card-icon" aria-hidden="true"></i>
                <span class="card-text">${escapeHtml(result.example_titles || 'No example titles')}</span>
            </div>
            <div class="card-row">
                <i class="fa fa-bookmark card-icon" aria-hidden="true"></i>
                <span class="card-text">${escapeHtml(result.teer_description || 'No TEER info')}</span>
            </div>
            <div class="card-row">
                <i class="fa fa-arrows-alt card-icon" aria-hidden="true"></i>
                <span class="card-text">${escapeHtml(result.mobility_progression || 'No mobility info')}</span>
            </div>
            <div class="card-footer">
                <span class="card-source">Source: ${escapeHtml(result.source_table || 'OaSIS')}</span>
                <span class="card-date">${escapeHtml(result.publication_date || '')}</span>
            </div>
        `;

        container.appendChild(card);
    });
}
```

### Filter Panel JavaScript (proposed)
```javascript
// New file: static/js/filters.js

const filters = {
    minorGroup: new Set(),
    feederMobility: new Set(),
    careerProgression: new Set()
};

let allResults = []; // Unfiltered results

function buildFilterOptions(results) {
    // Extract unique filter values from results
    const minorGroups = new Map();
    const mobilityPaths = new Set();
    const progressionPaths = new Set();

    results.forEach(r => {
        if (r.minor_group) {
            minorGroups.set(r.minor_group, r.minor_group_name || r.minor_group);
        }
        // Parse mobility/progression if available
        // These would need to be parsed from profile data
    });

    return { minorGroups, mobilityPaths, progressionPaths };
}

function renderFilterPanel(options) {
    const panel = document.getElementById('filter-panel');
    panel.innerHTML = `
        <h2 class="h4">Filter items</h2>

        <details class="filter-group" open>
            <summary>Minor Unit Group</summary>
            <fieldset>
                ${Array.from(options.minorGroups).map(([code, name]) => `
                    <div class="checkbox">
                        <label>
                            <input type="checkbox" name="minorGroup" value="${code}">
                            ${escapeHtml(code)} - ${escapeHtml(name)}
                        </label>
                    </div>
                `).join('')}
            </fieldset>
        </details>

        <!-- Similar for other filters -->
    `;
}

function applyFilters() {
    const filtered = allResults.filter(r => {
        // Check minor group filter
        if (filters.minorGroup.size > 0 && !filters.minorGroup.has(r.minor_group)) {
            return false;
        }
        // Check other filters...
        return true;
    });

    renderSearchResults(filtered);
}

function initFilters() {
    document.getElementById('filter-panel').addEventListener('change', (e) => {
        const checkbox = e.target;
        if (checkbox.type !== 'checkbox') return;

        const filterType = checkbox.name;
        const value = checkbox.value;

        if (checkbox.checked) {
            filters[filterType].add(value);
        } else {
            filters[filterType].delete(value);
        }

        applyFilters();
    });
}
```

### Sort Dropdown (from OASIS-HTML-REFERENCE.md)
```html
<div class="sort-controls">
    <label for="sortingOptionsSelect" class="h4">Sort by:</label>
    <select id="sortingOptionsSelect" class="form-control">
        <option value="match" selected>Matching search criteria</option>
        <option value="title-asc">Label - A to Z</option>
        <option value="title-desc">Label - Z to A</option>
        <option value="code-asc">Code - Ascending</option>
        <option value="code-desc">Code - Descending</option>
    </select>

    <button id="viewToggle" class="btn btn-default" title="Grid view">
        <span id="viewToggleLabel">Grid view</span>
        <i class="fa fa-th-list" aria-hidden="true"></i>
    </button>
</div>
```

## State of the Art

| Old Approach | Current Approach | When Changed | Impact |
|--------------|------------------|--------------|--------|
| Simple list results | OaSIS-style cards with 6 data points | v2.0 design | Richer information at glance |
| Single column grid | Custom 5-column grid (profile/skills/abilities/knowledge/match) | v2.0 design | More data visible in grid mode |
| OaSIS filters | Custom filters (Minor Group, Mobility, Progression) | v2.0 design | More relevant filtering options |

**Deprecated/outdated:**
- Simple `title (noc_code)` list items: Replaced by rich cards
- OaSIS filter categories (Broad category, TEER, Alphabetical): Removed per DISP-22
- Grid columns from 06-CONTEXT.md initial spec: Updated to custom columns per requirement

## Open Questions

Things that couldn't be fully resolved:

1. **Grid View Data Source for Skills/Abilities/Knowledge**
   - What we know: Grid view needs top 10 skills, top abilities, top knowledge per result
   - What's unclear: This data requires profile fetch - do we lazy load on grid toggle, batch fetch all, or fetch on demand?
   - Recommendation: Lazy load on grid toggle with loading spinner per row; cache results

2. **Card Data Points Not in Search Results**
   - What we know: OaSIS search results have lead statement, TEER, matching criteria. They do NOT have: example titles, mobility/progression, source table, publication date
   - What's unclear: Do we show partial cards or fetch missing data?
   - Recommendation: Show available data; fetch missing data asynchronously after initial render

3. **Filter Option Population**
   - What we know: Filters should be Minor Unit Group, Feeder Group Mobility, Career Progression
   - What's unclear: Mobility and progression data requires profile fetch - do we preload all or show limited options?
   - Recommendation: Minor Group can be derived from NOC code immediately; Mobility/Progression filters either disabled until profile fetched or limited to current page

4. **Click Navigation Behavior**
   - What we know: DISP-23 says "Card/grid click navigates to Profile Details page"
   - What's unclear: Is this the existing profile view in accordions, or a new dedicated page (Step 9)?
   - Recommendation: Navigate to existing profile view (accordions), but this may change in Phase 08-C

## Sources

### Primary (HIGH confidence)
- `static/js/main.js` - Current renderSearchResults() and view toggle (lines 163-274)
- `static/css/main.css` - Current search results and grid view styles (lines 151-417)
- `src/models/noc.py` - Current SearchResult model (lines 19-25)
- `src/services/parser.py` - Current parse_search_results() (lines 23-76)
- `src/routes/api.py` - Current /api/search route (lines 28-83)
- `.planning/phases/06-enhanced-ui-display/06-CONTEXT.md` - UI specifications (lines 195-265)
- `.planning/phases/06-enhanced-ui-display/OASIS-HTML-REFERENCE.md` - HTML patterns (lines 326-492)

### Secondary (MEDIUM confidence)
- OaSIS search results page structure - From HTML reference file

### Tertiary (LOW confidence)
- None - all findings verified against codebase and reference documents

## Metadata

**Confidence breakdown:**
- Standard stack: HIGH - All from existing codebase
- Architecture: HIGH - Data flow analyzed, patterns extracted from OaSIS reference
- Pitfalls: HIGH - Based on analysis of data requirements vs available data

**Research date:** 2026-01-24
**Valid until:** 60 days (stable codebase, OaSIS HTML structure unlikely to change)

---

## Implementation Summary

### Backend Changes Required

| File | Changes |
|------|---------|
| `src/models/noc.py` | Add EnrichedSearchResult model with all 6 card data points + filter fields |
| `src/services/parser.py` | Enhance parse_search_results() to extract card data from OaSIS HTML |
| `src/routes/api.py` | Return EnrichedSearchResult from /api/search |
| `src/models/responses.py` | Update SearchResponse to use EnrichedSearchResult |

### Frontend Changes Required

| File | Changes |
|------|---------|
| `templates/index.html` | Add filter panel container, update results structure |
| `static/css/main.css` | Add OaSIS-style card CSS, filter panel CSS |
| `static/js/main.js` | Update renderSearchResults() for card/grid views |
| `static/js/filters.js` | NEW - Filter panel logic |
| `static/js/api.js` | May need update for batch profile fetches |

### Key Design Decisions Needed

1. **Grid View Data Strategy:**
   - Option A: Lazy load on grid toggle (recommended)
   - Option B: Batch fetch all profiles on search
   - Option C: Grid view disabled until profile selected

2. **Missing Card Data Strategy:**
   - Option A: Show "N/A" for unavailable fields (simple)
   - Option B: Fetch asynchronously after render (better UX)
   - Option C: Only show available fields (cleanest)

3. **Filter Scope:**
   - Option A: Filter current search results only (recommended)
   - Option B: Re-query backend with filter params

### Estimated Effort

- Backend model/parser changes: ~100 lines
- Frontend card rendering: ~150 lines
- Frontend filter panel: ~100 lines
- CSS styles: ~200 lines
- Grid view with data fetch: ~100 lines

Total: ~650 lines across 8 files. Medium complexity due to data enrichment requirements.

### Dependencies

This phase depends on Phase 08-A (Search Bar Redesign) being complete, as both modify the search interface.

### Risk Areas

1. **OaSIS HTML structure changes** - Parser may break if OaSIS updates their HTML
2. **N+1 query performance** - Grid view needs optimization
3. **Partial data display** - UX for cards with missing data needs design consideration
