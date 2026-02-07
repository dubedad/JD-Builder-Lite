# Phase 18: Profile Page Overhaul - Research

**Researched:** 2026-02-06
**Domain:** Frontend UI restructuring (HTML/CSS/JavaScript tab navigation and hierarchical filters)
**Confidence:** HIGH

## Summary

This phase restructures the existing Flask-based web application's profile page tabs and enhances data display with dimension-aware labels. The application already uses vanilla JavaScript with W3C ARIA-compliant tab navigation (`TabController` class) and custom CSS with Government of Canada design patterns.

The standard approach for this UI refactoring work is to modify existing HTML templates, update JavaScript rendering functions, enhance CSS for new layouts, and extend data mapping logic to include dimension type metadata from guide.csv. No new libraries are needed - the codebase already has all necessary components (ARIA tabs, filter checkboxes, profile rendering pipeline).

The primary technical challenges are: (1) moving content between tabs while preserving selection state, (2) mapping dimension types from guide.csv categories to individual rating circles, (3) adding hierarchical structure to filter checkboxes, and (4) ensuring tab bar overflow handling works across screen sizes.

**Primary recommendation:** Modify existing `accordion.js` rendering functions to restructure tabs, extend the profile data pipeline to include dimension metadata from guide.csv, update HTML template to add new tab elements, and enhance filter.js to support hierarchical checkbox groups with parent selection logic.

<user_constraints>
## User Constraints (from CONTEXT.md)

### Locked Decisions

**Tab structure & ordering:**
- 8 tabs in this order: Overview, Core Competencies, Key Activities, Skills, Abilities, Knowledge, Effort, Responsibility
- Remove Feeder Group Mobility & Career Progression tab (content moves to Overview)
- Remove Other Job Information tab (content moves to Overview)
- Split current Skills tab into 3 separate tabs: Skills, Abilities, Knowledge
- Promote Core Competencies from inside Overview to its own dedicated tab
- Default selected tab on profile load: Overview
- Claude's discretion on tab bar overflow handling (wrap vs scroll vs label shortening) based on existing CSS and screen width

**Dimension label presentation:**
- Replace the current "L3" label with dimension-aware format: "Proficiency 3/5", "Importance 3/5", etc.
- Position: same spot as current L-number label (after the rating circles)
- Dimension types derived from guide.csv per category (Skills=Proficiency, Abilities=Proficiency, Knowledge=Knowledge Level, Work Activities=Complexity, Personal Attributes=Importance, Work Context=varies)

**Overview tab layout:**
- Navy blue description text moves from above-tabs position INTO the Overview tab
- The NOC icon/badge stays above the tabs in its current position AND is also copied into the Overview tab
- Above-tabs area: icon only (description text removed from there)
- Overview tab: icon + full description + existing reference data + consolidated content from removed tabs

**Filter hierarchy display:**
- Sub-major group and minor group hierarchy headings in occupational category filter
- Sub-major group headings are selectable -- clicking selects/deselects all minor groups underneath
- Hierarchy data sourced from `dim_noc_structure` table in the JobForge 2.0 directory
- Need to load dim_noc_structure data and map it to search results for filter building

### Claude's Discretion

- Tab bar overflow handling (wrap vs scroll vs abbreviation)
- Tooltip behavior on rating circles (keep or remove given new labels)
- Dimension label wording (exact guide.csv names vs shortened single-word variants)
- Mixed dimension type display within categories (inline per-statement vs grouped headers)
- Overview tab section ordering and organization
- Whether Overview sections are collapsible and which start expanded/collapsed
- Filter hierarchy visual style (indented tree, grouped sections, or accordion)
- Item count display on filter hierarchy levels

### Deferred Ideas (OUT OF SCOPE)

None -- discussion stayed within phase scope

</user_constraints>

## Standard Stack

The existing application stack is already in place. No new libraries required for this phase.

### Core (Already in Use)
| Library | Version | Purpose | Why Standard |
|---------|---------|---------|--------------|
| Flask | 2.x+ | Backend web framework | Application is already Flask-based with API routes |
| Vanilla JavaScript | ES6+ | Frontend interactivity | Existing TabController, accordion.js, filters.js use vanilla JS |
| CSS3 | Modern | Styling with GC design tokens | Custom CSS with CSS variables, flexbox, ARIA support |

### Supporting (Already in Use)
| Library | Version | Purpose | When to Use |
|---------|---------|---------|-------------|
| Font Awesome | 6.5.1 | Icon library | Already used for NOC icons, UI elements |
| W3C ARIA | 1.2 | Accessibility markup | Existing TabController follows ARIA Authoring Practices |

### Current Architecture
- **Backend:** Flask application serving HTML templates + JSON API endpoints
- **Frontend:** Vanilla JavaScript modules (accordion.js, filters.js, profile_tabs.js, etc.)
- **Data:** CSV files (guide.csv) loaded server-side, parquet files from JobForge Bronze directory
- **Templates:** Jinja2 HTML templates in `/templates` directory
- **Static Assets:** `/static/js`, `/static/css` for organized client-side code

**No installation needed** - this phase only modifies existing code.

## Architecture Patterns

### Existing Profile Rendering Pipeline

The codebase follows a clear separation of concerns:

```
1. API fetch (/api/profile) → profile JSON with statements
2. accordion.js renders profile header + tab content
3. TabController manages tab switching (ARIA-compliant)
4. State management via store.js for selections
5. CSS classes control visibility/styling
```

**Key files in rendering flow:**
- `templates/index.html` - Static HTML structure with tab skeleton
- `static/js/accordion.js` - `renderProfileHeader()`, `renderTabContent()`, `renderOverviewContent()`, etc.
- `static/js/profile_tabs.js` - `TabController` class for tab navigation
- `static/css/main.css` - Tab bar styling, panel layout, responsive rules

### Pattern 1: Tab Content Rendering

**What:** Each tab renders by populating a `<div role="tabpanel">` element with HTML via innerHTML

**Current implementation:**
```javascript
// From accordion.js line 596+
const renderTabContent = (profile) => {
    const state = store.getState();

    // Overview tab - special handling for reference data
    const overviewPanel = document.getElementById('panel-overview');
    if (overviewPanel) {
        overviewPanel.innerHTML = renderOverviewContent(profile);
    }

    // Skills tab
    const skillsPanel = document.getElementById('panel-skills');
    if (skillsPanel) {
        skillsPanel.innerHTML = renderStatementsPanel(
            profile.skills?.statements || [],
            TAB_CONFIG.skills.sections,
            'skills',
            state.selections.skills || []
        );
    }
    // ... similar for other tabs
};
```

**For this phase:** Add new tabs (Core Competencies, Abilities, Knowledge), remove old tabs (career, other), move content into Overview.

### Pattern 2: Statement Proficiency Display

**Current implementation (line 935-962 in accordion.js):**
```javascript
const renderProficiency = (proficiency) => {
    const level = proficiency.level;
    const max = proficiency.max || 5;
    const label = proficiency.label || PROFICIENCY_LABELS[level] || `Level ${level}`;

    const filledCircles = '<span class="filled">●</span>'.repeat(level);
    const emptyCircles = '<span class="empty">○</span>'.repeat(max - level);

    return `
        <div class="proficiency-rating"
             aria-label="Level ${level}"
             data-full-label="${level} - ${escapeHtml(label)}"
             tabindex="0">
            <span class="rating-circles">${filledCircles}${emptyCircles}</span>
            <span class="rating-label">L${level}</span>
        </div>
    `;
};
```

**For this phase:** Replace `<span class="rating-label">L${level}</span>` with dimension-aware format like `<span class="rating-label">${dimensionType} ${level}/${max}</span>`.

**Dimension metadata source:** guide.csv has category-level dimension definitions. Map statement's `source_attribute` to category to get dimension type:
- Skills → Proficiency
- Abilities → Proficiency
- Knowledge → Knowledge Level
- Work Activities → Complexity
- Personal Attributes → Importance
- Work Context → varies (multiple dimension types)

### Pattern 3: Filter Checkbox Groups

**Current implementation (filters.js line 96-113):**
```javascript
// Flat list of checkboxes
minorGroupOptions.innerHTML = sorted.map(cat => `
    <label class="filter-checkbox">
        <input type="checkbox" name="minorGroup" value="${escapeHtml(cat.name)}"
               ${filters.minorGroup.has(cat.name) ? 'checked' : ''}>
        <span class="filter-checkbox-label">
            ${escapeHtml(cat.name)}
            <span class="filter-checkbox-count">(${cat.count})</span>
        </span>
    </label>
`).join('');
```

**For this phase:** Add hierarchy structure with parent groups that select/deselect children. Two-level structure:
1. **Sub-major group heading** (parent checkbox) - selects all minor groups beneath
2. **Minor group items** (child checkboxes) - individual selections

**Hierarchical pattern:**
```javascript
// Pseudocode structure
hierarchyData.forEach(subMajor => {
    html += `<div class="filter-group">
        <label class="filter-checkbox filter-checkbox--parent">
            <input type="checkbox" class="parent-checkbox"
                   data-group-id="${subMajor.code}">
            <strong>${subMajor.name}</strong> (${subMajor.totalCount})
        </label>
        <div class="filter-group__children">
            ${subMajor.minorGroups.map(minor => `
                <label class="filter-checkbox filter-checkbox--child">
                    <input type="checkbox" class="child-checkbox"
                           data-parent="${subMajor.code}"
                           value="${minor.code}">
                    ${minor.name} (${minor.count})
                </label>
            `).join('')}
        </div>
    </div>`;
});
```

### Pattern 4: Content Migration Between Tabs

**Strategy:** Content already rendered in profile object. Just route to different tab panel.

**Example - Core Competencies (currently in Overview):**

Current code (accordion.js line 203-213):
```javascript
// Inside renderOverviewContent()
if (ref.core_competencies?.length) {
    html += `
        <div class="tab-panel__section">
            <h3>Core Competencies</h3>
            <ul>
                ${ref.core_competencies.map(c => `<li>${escapeHtml(c)}</li>`).join('')}
            </ul>
        </div>
    `;
}
```

**For this phase:** Extract this into `renderCoreCompetenciesContent()` function, call from new Core Competencies panel instead of Overview.

### Anti-Patterns to Avoid

- **Don't rebuild TabController** - Existing implementation already follows W3C ARIA Authoring Practices for tabs. Modify tab list in HTML and call `new TabController()` to reinitialize.
- **Don't hard-code dimension labels in JS** - Load from guide.csv category definitions to maintain single source of truth.
- **Don't break selection state** - When moving content between tabs, preserve `state.selections[sectionId]` keys. If renaming section IDs, add migration logic.
- **Don't remove profile header elements** - User wants NOC icon in both header AND Overview tab. Duplicate, don't move.

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| ARIA-compliant tab navigation | Custom tab switching logic | Existing `TabController` class | Already implements W3C ARIA Authoring Practices (keyboard nav, aria-selected, focus management) |
| Hierarchical checkboxes | Custom checkbox tree component | Plain HTML with parent/child event listeners | Simple parent-child relationship doesn't need a tree library. CSS indentation + JS event delegation handles selection logic cleanly. |
| Dimension type mapping | Runtime lookup from guide.csv | Pre-process guide.csv into category → dimension map | Parsing CSV on every statement render is inefficient. Load once into lookup object. |
| Tab overflow | Custom scroll buttons | CSS `overflow-x: auto` with scroll-snap | Modern CSS handles horizontal scrolling well. Mobile browsers have good touch scroll UX. |

**Key insight:** This phase is UI reorganization, not new capability. Existing patterns (tab rendering, filter checkboxes, proficiency display) already work. Extend, don't replace.

## Common Pitfalls

### Pitfall 1: Breaking Selection State When Renaming Section IDs

**What goes wrong:** Current code uses section IDs like `skills`, `key_activities`, etc. as keys in `state.selections` object. If you split `skills` into separate `skills`, `abilities`, `knowledge` sections, existing selections would be lost.

**Why it happens:** Statement IDs include section prefix: `skills-0`, `skills-1`, etc. Changing section name breaks these references.

**How to avoid:**
1. Map existing `skills` section data to new sections by checking `source_attribute` field:
   - Statements with `source_attribute === 'Skills'` → `skills` section
   - Statements with `source_attribute === 'Abilities'` → `abilities` section
   - Statements with `source_attribute === 'Knowledge'` → `knowledge` section
2. Migrate selection state keys on profile load or provide backward compatibility

**Warning signs:** After tab restructure, previously selected statements are no longer checked.

### Pitfall 2: Dimension Type Mapping Confusion for Work Context

**What goes wrong:** Work Context has multiple dimension types (Frequency, Importance, Context) unlike Skills/Abilities which have single dimension type (Proficiency). Hard-coding "Work Context = Frequency" will be wrong for some statements.

**Why it happens:** guide.csv has category-level definitions, but Work Context is heterogeneous. Individual statements may have different scale types.

**How to avoid:**
1. Check guide.csv for actual dimension type per element_id, not just category
2. If guide.csv doesn't specify per-element, use the `description` field which mentions scale type
3. For Effort/Responsibility tabs, most are Context/Frequency based - verify with actual data

**Warning signs:** Some Work Context statements show "Frequency 3/5" when they should show "Importance 3/5" or "Context 3/5".

### Pitfall 3: NOC Hierarchy Data Not Available from dim_noc_structure

**What goes wrong:** CONTEXT.md states hierarchy data comes from `dim_noc_structure` table in JobForge 2.0 directory, but this data may not be pre-loaded into search results.

**Why it happens:** Search results API (`/api/search`) returns profile metadata, but may not include full NOC hierarchy structure from Bronze layer parquet files.

**How to avoid:**
1. Check if search results already include hierarchy fields (broad_category_name, minor_group_name, etc.)
2. If not available, load `dim_noc_structure` parquet file server-side and join with search results
3. Add hierarchy fields to SearchResult model/JSON response
4. Alternatively, load hierarchy data separately and join client-side (less efficient)

**Warning signs:** Filter hierarchy shows no sub-major/minor group names, or all results appear under single group.

### Pitfall 4: Tab Bar Overflow Not Handling 8 Tabs on Mobile

**What goes wrong:** 8 tab labels ("Overview", "Core Competencies", "Key Activities", etc.) don't fit horizontally on mobile screens. Tabs wrap messily or get cut off.

**Why it happens:** Current CSS has `flex-wrap: wrap` on `.tabs-bar` which causes multi-row wrapping. Long labels like "Core Competencies" and "Feeder Group Mobility & Career Progression" consume significant width.

**How to avoid:**
- **Option A (current):** Keep `flex-wrap: wrap` - tabs wrap to multiple rows on narrow screens
- **Option B (scroll):** Change to `flex-wrap: nowrap; overflow-x: auto` with scroll-snap for horizontal scrolling
- **Option C (abbreviate):** Shorten labels on mobile with CSS (`tab-button::after` content swap) or `title` attribute

**Recommendation:** Use Option B (horizontal scroll) with scroll-snap. Mobile users are accustomed to horizontal scroll for tabs. Ensures consistent single-row layout.

**Warning signs:** Tab bar is 3-4 rows tall on mobile, making navigation awkward.

## Code Examples

### Example 1: Dimension-Aware Proficiency Label

**Source:** Modification of existing `renderProficiency()` in accordion.js

```javascript
// New function: map category to dimension type
const getDimensionType = (sourceAttribute) => {
    const dimensionMap = {
        'Skills': 'Proficiency',
        'Abilities': 'Proficiency',
        'Knowledge': 'Knowledge Level',
        'Work Activities': 'Complexity',
        'Personal Attributes': 'Importance',
        // Work Context varies - would need element-level lookup
    };
    return dimensionMap[sourceAttribute] || 'Level';
};

// Modified renderProficiency function
const renderProficiency = (proficiency, sourceAttribute) => {
    if (!proficiency || proficiency.level == null) {
        return `<div class="proficiency-rating no-rating">
            <span class="rating-label">No rating</span>
        </div>`;
    }

    const level = proficiency.level;
    const max = proficiency.max || 5;
    const dimensionType = getDimensionType(sourceAttribute);

    const filledCircles = '<span class="filled">●</span>'.repeat(level);
    const emptyCircles = '<span class="empty">○</span>'.repeat(max - level);

    return `
        <div class="proficiency-rating"
             aria-label="${dimensionType} ${level} of ${max}"
             tabindex="0">
            <span class="rating-circles">${filledCircles}${emptyCircles}</span>
            <span class="rating-label">${dimensionType} ${level}/${max}</span>
        </div>
    `;
};

// Usage in statement rendering (pass sourceAttribute)
const proficiencyHtml = stmt.proficiency
    ? renderProficiency(stmt.proficiency, stmt.source_attribute)
    : '';
```

### Example 2: Hierarchical Filter Rendering

**Source:** New pattern for filters.js

```javascript
// Load hierarchy structure (from dim_noc_structure or API)
const nocHierarchy = {
    '01': { // Broad category code
        subMajorGroups: {
            '011': {
                code: '011',
                name: 'Administrative services supervisors',
                minorGroups: {
                    '0111': { code: '0111', name: 'Financial managers', count: 5 },
                    '0112': { code: '0112', name: 'Human resources managers', count: 3 }
                }
            }
        }
    }
};

// Render hierarchical checkboxes
function renderHierarchicalFilters(results, hierarchy) {
    let html = '';

    Object.values(hierarchy).forEach(broadCat => {
        Object.values(broadCat.subMajorGroups).forEach(subMajor => {
            const minorGroups = Object.values(subMajor.minorGroups);
            const totalCount = minorGroups.reduce((sum, m) => sum + m.count, 0);

            html += `
                <div class="filter-group">
                    <label class="filter-checkbox filter-checkbox--parent">
                        <input type="checkbox" class="parent-checkbox"
                               data-group="${subMajor.code}"
                               onchange="handleParentCheckboxChange(this)">
                        <strong>${subMajor.name}</strong>
                        <span class="filter-checkbox-count">(${totalCount})</span>
                    </label>
                    <div class="filter-group__children">
                        ${minorGroups.map(minor => `
                            <label class="filter-checkbox filter-checkbox--child">
                                <input type="checkbox"
                                       name="minorGroup"
                                       value="${minor.code}"
                                       data-parent="${subMajor.code}"
                                       onchange="handleChildCheckboxChange(this)">
                                ${minor.name}
                                <span class="filter-checkbox-count">(${minor.count})</span>
                            </label>
                        `).join('')}
                    </div>
                </div>
            `;
        });
    });

    return html;
}

// Parent checkbox handler - select/deselect all children
function handleParentCheckboxChange(parentCheckbox) {
    const groupCode = parentCheckbox.dataset.group;
    const children = document.querySelectorAll(
        `input.child-checkbox[data-parent="${groupCode}"]`
    );

    children.forEach(child => {
        child.checked = parentCheckbox.checked;
        // Trigger filter update
        if (parentCheckbox.checked) {
            filters.minorGroup.add(child.value);
        } else {
            filters.minorGroup.delete(child.value);
        }
    });

    applyFilters();
}

// Child checkbox handler - update parent indeterminate state
function handleChildCheckboxChange(childCheckbox) {
    const parentCode = childCheckbox.dataset.parent;
    const parent = document.querySelector(
        `input.parent-checkbox[data-group="${parentCode}"]`
    );

    const siblings = document.querySelectorAll(
        `input.child-checkbox[data-parent="${parentCode}"]`
    );
    const checkedCount = Array.from(siblings).filter(s => s.checked).length;

    parent.checked = checkedCount === siblings.length;
    parent.indeterminate = checkedCount > 0 && checkedCount < siblings.length;

    // Update filter state
    if (childCheckbox.checked) {
        filters.minorGroup.add(childCheckbox.value);
    } else {
        filters.minorGroup.delete(childCheckbox.value);
    }

    applyFilters();
}
```

**CSS for hierarchy indentation:**
```css
.filter-group {
    margin-bottom: 0.5rem;
}

.filter-checkbox--parent {
    font-weight: 600;
    margin-bottom: 0.25rem;
}

.filter-group__children {
    margin-left: 1.5rem;
    border-left: 2px solid #e0e0e0;
    padding-left: 0.75rem;
}

.filter-checkbox--child {
    font-weight: 400;
    font-size: 0.9375rem;
}
```

### Example 3: Tab Bar Horizontal Scroll (Mobile)

**Source:** CSS modification in main.css

```css
/* Desktop: wrap tabs if needed */
.tabs-bar {
    display: flex;
    flex-wrap: wrap;
    gap: 0.5rem;
    border-bottom: 2px solid #e0e0e0;
}

/* Mobile: horizontal scroll with snap */
@media (max-width: 768px) {
    .tabs-bar {
        flex-wrap: nowrap;
        overflow-x: auto;
        scroll-snap-type: x mandatory;
        -webkit-overflow-scrolling: touch;
        scrollbar-width: thin;
    }

    .tabs-bar li {
        scroll-snap-align: start;
    }

    /* Hide scrollbar on mobile for cleaner look */
    .tabs-bar::-webkit-scrollbar {
        height: 4px;
    }

    .tabs-bar::-webkit-scrollbar-thumb {
        background: #ccc;
        border-radius: 2px;
    }

    .tab-button {
        flex-shrink: 0; /* Prevent tabs from compressing */
        min-width: max-content; /* Ensure full label visible */
    }
}
```

### Example 4: Moving Content to Overview Tab

**Source:** Modification of `renderOverviewContent()` in accordion.js

```javascript
const renderOverviewContent = (profile) => {
    const ref = profile.reference_attributes || {};
    let html = '';

    // NOC Icon (duplicated from header)
    const iconClass = getNocIcon(profile.noc_code);
    html += `
        <div class="overview-header">
            <i class="fas ${iconClass} overview-icon"></i>
            <div class="overview-header__text">
                <h2>${escapeHtml(profile.title)}</h2>
                <span class="noc-badge">${escapeHtml(profile.noc_code)}</span>
            </div>
        </div>
    `;

    // Navy blue description (moved from above-tabs area)
    const description = document.getElementById('profile-description')?.textContent;
    if (description) {
        html += `
            <div class="overview-description">
                <p class="description-text--navy">${escapeHtml(description)}</p>
            </div>
        `;
    }

    // Also Known As
    if (profile.example_titles?.length) {
        html += renderAlsoKnownAsSection(profile.example_titles);
    }

    // NOTE: Core Competencies removed from here - now in separate tab

    // NOC Hierarchy
    html += renderNocHierarchySection(profile);

    // Feeder Group Mobility & Career Progression (moved from removed tab)
    const additionalInfo = ref.additional_info;
    if (additionalInfo) {
        html += `
            <div class="oasis-panel">
                <div class="oasis-panel__heading">
                    <span class="fas fa-route oasis-panel__icon"></span>
                    <h3 class="oasis-panel__title">Feeder Group Mobility & Career Progression</h3>
                </div>
                <div class="oasis-panel__body">
                    ${escapeHtml(additionalInfo)}
                </div>
            </div>
        `;
    }

    // Other Job Information sections (moved from removed tab)
    html += renderOtherJobInfoSections(profile.other_job_info);

    return html;
};
```

**CSS for navy description:**
```css
.overview-description {
    margin: 1.5rem 0;
    padding: 1rem;
    background: #f8f9fa;
    border-radius: 4px;
}

.description-text--navy {
    color: #26374a; /* GC navy blue */
    font-size: 1rem;
    line-height: 1.6;
    font-weight: 500;
}

.overview-icon {
    font-size: 3rem;
    color: #26374a;
    margin-right: 1rem;
}
```

## State of the Art

| Old Approach | Current Approach | When Changed | Impact |
|--------------|------------------|--------------|--------|
| Generic "L3" level labels | Dimension-aware labels ("Proficiency 3/5") | Phase 18 | Users understand what the rating measures, not just numeric level |
| Flat filter checkboxes | Hierarchical filter groups with parent selection | Phase 18 | Users can filter by broader categories or specific groups efficiently |
| Content in 7 tabs | Content in 8 reorganized tabs | Phase 18 | Logical grouping - Skills/Abilities/Knowledge separated, Core Competencies promoted |
| Description above tabs | Description inside Overview tab | Phase 18 | Cleaner header area, Overview tab becomes comprehensive landing page |

**Deprecated/outdated:**
- Old tab structure with combined "Skills" tab containing Skills/Abilities/Knowledge subsections
- Separate "Feeder Group Mobility & Career Progression" and "Other Job Information" tabs
- Generic "L-number" proficiency labels without dimension context

## Open Questions

### 1. Exact Dimension Type per Work Context Element

**What we know:** guide.csv has category-level dimension definitions. Work Context category description says "worker rates how often or to what extent" which implies multiple scale types.

**What's unclear:** Whether guide.csv element_id rows specify per-element dimension type, or if we need to infer from element title/description.

**Recommendation:**
1. Load guide.csv and check if Work Context elements have distinct dimension types in data
2. If not available, use element title pattern matching (e.g., "How often" → Frequency, "How important" → Importance)
3. Create dimension type lookup map: `{ element_id: dimensionType }`

### 2. NOC Hierarchy Data Structure in dim_noc_structure

**What we know:** CONTEXT.md mentions `dim_noc_structure` table in JobForge 2.0 directory. This likely contains NOC 2021 classification hierarchy.

**What's unclear:**
- Exact schema of dim_noc_structure (column names, structure)
- Whether search results already include this data
- How to join hierarchy with search results (by NOC code? broad category code?)

**Recommendation:**
1. Read dim_noc_structure parquet file to understand schema
2. Check if search API response already includes hierarchy fields
3. If not, load hierarchy data server-side and join before returning search results
4. Ensure hierarchy includes: broad_category, sub_major_group, minor_group names and codes

### 3. Mobile Tab Bar Overflow Strategy

**What we know:** Current CSS uses `flex-wrap: wrap`. 8 tabs with long labels will wrap on mobile.

**What's unclear:** User preference for overflow handling (wrap vs scroll vs abbreviate).

**Recommendation:** Implement horizontal scroll with scroll-snap (Option B from Pitfall 4). Reasons:
- Mobile users familiar with horizontal scroll gesture
- Keeps tab bar height consistent (single row)
- Scroll-snap provides natural "tab stopping points"
- Fallback to wrap on very wide screens (desktop) works fine

## Sources

### Primary (HIGH confidence)

- Existing codebase files (HIGH confidence - direct inspection):
  - `static/js/accordion.js` - Profile rendering, tab content generation, proficiency display
  - `static/js/profile_tabs.js` - TabController class with W3C ARIA implementation
  - `static/js/filters.js` - Current filter checkbox implementation
  - `templates/index.html` - Tab structure HTML
  - `static/css/main.css` - Tab styling, responsive patterns
  - `src/data/guide.csv` - Category and dimension type definitions

### Secondary (MEDIUM confidence)

- [CSS Responsive Tabbed Navigation | CodyHouse](https://codyhouse.co/gem/responsive-tabbed-navigation/) - Tab overflow patterns
- [Container-Adapting Tabs With "More" Button | CSS-Tricks](https://css-tricks.com/container-adapting-tabs-with-more-button/) - Overflow handling strategies
- [Using best practices to create CSS scroll snapping tabs | utilitybend](https://utilitybend.com/blog/using-best-practices-to-create-css-scroll-snapping-tabs) - Scroll-snap implementation
- [Building a Tabs component | Articles | web.dev](https://web.dev/building-a-tabs-component/) - Modern tab component patterns

### Tertiary (MEDIUM confidence - W3C standards)

- [Tree View Pattern | APG | WAI | W3C](https://www.w3.org/WAI/ARIA/apg/patterns/treeview/) - ARIA tree view patterns for hierarchical filters
- [PatternFly • Tree view](https://www.patternfly.org/components/tree-view/design-guidelines/) - Accessibility guidelines for tree views
- [overflow - CSS | MDN](https://developer.mozilla.org/en-US/docs/Web/CSS/overflow) - CSS overflow property reference

## Metadata

**Confidence breakdown:**
- Standard stack: HIGH - All existing libraries already in use, verified by reading codebase
- Architecture: HIGH - Direct inspection of rendering pipeline, tab controller, filter logic
- Pitfalls: HIGH - Based on actual code patterns and state management structure
- Filter hierarchy: MEDIUM - W3C ARIA patterns verified, but dim_noc_structure schema unknown
- Dimension mapping: MEDIUM - guide.csv structure verified, but Work Context per-element types need validation

**Research date:** 2026-02-06
**Valid until:** 2026-03-06 (30 days - stable domain, minimal library changes expected)
