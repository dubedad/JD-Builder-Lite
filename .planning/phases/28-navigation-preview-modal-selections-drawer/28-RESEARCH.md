# Phase 28: Navigation, Preview Modal & Selections Drawer - Research

**Researched:** 2026-03-12
**Domain:** Vanilla JS / HTML / CSS — navigation bar, modal overlay, slide-out drawer, state management
**Confidence:** HIGH (all findings from direct codebase inspection)

---

## Summary

Phase 28 adds three UI features on top of Phases 26 and 27: (1) a 3-button bottom navigation bar on every Build tab, (2) a modal overlay that assembles and shows a JD preview, and (3) a redesigned Selections drawer replacing the old sidebar. All work happens in vanilla JS and CSS with no new dependencies.

The codebase already has the foundational pieces: `store` manages selections via `state.selections`, `resetSelectionsForProfile` handles the same-vs-different card logic (already implemented in state.js), the `#action-bar` footer is a fixed-bottom element that will be replaced/extended by the new 3-button nav bar, and `sidebar.js` has the raw selections data that needs to be repackaged into the new drawer design. The current `export.js` handles preview by replacing the entire page body — Phase 28 replaces that with an in-page modal instead.

The key architectural decision is that the new bottom nav bar replaces the old `#action-bar` (the "Create Job Description" footer). The old action-bar becomes redundant in v5.1 because navigation to Classification IS the "next step" from Build. The Preview modal is completely new HTML injected into a `<div class="modal-overlay">` appended to `<body>`. The Selections drawer is a redesign of the existing `#sidebar` / `#selection-summary` system.

**Primary recommendation:** Reuse `resetSelectionsForProfile` exactly as-is for card-click logic. Replace `#action-bar` with a `.build-nav-bar` fixed footer containing 3 buttons. Build the Preview modal as a client-side overlay using the same data that `export.js` already assembles (no new API call needed for the preview content). Redesign the sidebar content (`updateSidebar`) to match the new v5.1 drawer spec.

---

## Standard Stack

This phase is pure in-project code — no new npm packages or CDN libraries needed.

### Core
| Component | Location | Purpose | Why Used |
|-----------|----------|---------|----------|
| `store` (state.js) | `static/js/state.js` | Reactive state with localStorage persistence | Already drives all selection state |
| `resetSelectionsForProfile` | `static/js/state.js` | Same-vs-different card logic | Already implemented and correct |
| `updateSidebar` | `static/js/sidebar.js` | Renders sidebar content from state | Needs redesign but logic is sound |
| `exportModule.buildExportRequest()` | `static/js/export.js` | Assembles all selected statements into export payload | Can be reused for preview content |
| Font Awesome 6.5.1 | CDN in index.html | Icon library | Already loaded |

### No New Dependencies Needed
All modal, drawer, and nav-bar functionality can be implemented with vanilla JS, CSS transitions, and the existing store. No animation library, no dialog polyfill, no new packages.

---

## Architecture Patterns

### Recommended Project Structure Changes

```
static/
├── js/
│   ├── main.js          # Add bottom nav bar init, wire "Back to Search" + "Continue to Classification"
│   ├── sidebar.js       # Redesign updateSidebar() for v5.1 drawer spec (deselect button, Clear All, total count)
│   └── export.js        # Wire "Preview Job Description" button; open modal instead of replacing page
├── css/
│   └── main.css         # Add .build-nav-bar, .jd-preview-modal, .selections-drawer styles
templates/
└── index.html           # Add modal HTML skeleton; update #action-bar to .build-nav-bar
```

### Pattern 1: Bottom Navigation Bar

**What:** A fixed `<footer>` element with 3 buttons replacing the current `#action-bar`. Shown only when the Build tabs (`#profile-tabs-container`) are visible. Hidden on Search, Classify, Generate, Export.

**HTML structure (in index.html, replacing `#action-bar`):**

```html
<!-- Bottom Navigation Bar (NAV-01) -->
<footer id="build-nav-bar" class="build-nav-bar hidden">
    <button id="nav-back-to-search" class="btn btn--secondary build-nav-bar__btn build-nav-bar__btn--left" type="button">
        <i class="fas fa-arrow-left"></i> Back to Search
    </button>
    <button id="nav-preview-jd" class="btn btn--primary build-nav-bar__btn build-nav-bar__btn--center" type="button">
        <i class="fas fa-eye"></i> Preview Job Description
    </button>
    <button id="nav-continue-classify" class="btn btn--primary build-nav-bar__btn build-nav-bar__btn--right" type="button">
        Continue to Classification <i class="fas fa-arrow-right"></i>
    </button>
</footer>
```

**Key CSS (in main.css):**

```css
.build-nav-bar {
    position: fixed;
    bottom: 0;
    left: 0;
    right: 0;
    background: var(--bg);
    border-top: 1px solid var(--border);
    padding: 1rem 2rem;
    box-shadow: 0 -2px 10px rgba(0, 0, 0, 0.1);
    z-index: 40;
    display: flex;
    justify-content: space-between;
    align-items: center;
    transition: right 0.3s ease;
}
body.sidebar-open .build-nav-bar {
    right: 300px;
}
```

**JS wiring (in main.js, inside `initStepper` or a new `initBuildNav` function):**

```javascript
// Show/hide build-nav-bar based on current section
function updateBuildNavVisibility() {
    const buildNav = document.getElementById('build-nav-bar');
    if (!buildNav) return;
    const isBuilding = window.currentProfile
        && !document.getElementById('profile-tabs-container').classList.contains('hidden');
    buildNav.classList.toggle('hidden', !isBuilding);
}

// Back to Search (NAV-02)
document.getElementById('nav-back-to-search').addEventListener('click', () => {
    window.jdStepper.goToStep(1);
    // Selections are NOT cleared — resetSelectionsForProfile handles this on next card click
});

// Continue to Classification (NAV-01)
document.getElementById('nav-continue-classify').addEventListener('click', () => {
    window.jdStepper.goToStep(3);
});
```

**Visibility management:** Call `updateBuildNavVisibility()` from the `profile-loaded` event listener and from each `navigateToStep` case. The `#action-bar` (old footer) should be hidden permanently — it is superseded by `#build-nav-bar`.

### Pattern 2: Same-vs-Different Card Click Logic

**What:** When the user clicks "Back to Search" and then clicks a card, existing `resetSelectionsForProfile` already implements this correctly. No new logic needed.

**Existing implementation (state.js lines 81-107):**

```javascript
const resetSelectionsForProfile = (nocCode) => {
    const state = store.getState();
    if (state.currentProfileCode !== nocCode) {
        // Different profile — clears ALL selections
        store.setState({ positionTitle: '', selections: { ... }, currentProfileCode: nocCode });
    } else {
        // Same profile — preserves all selections
        console.log('[DEBUG state.js] Same profile', nocCode, '- preserving selections');
    }
};
```

`handleResultClick` in main.js calls `resetSelectionsForProfile(profile.noc_code)` before rendering. This is the correct hook.

**Verification:** When "Back to Search" is clicked, `goToStep(1)` shows search results but does NOT call `resetSelectionsForProfile`. Only a new card click triggers the reset check. This means selections survive the Back-to-Search navigation correctly.

### Pattern 3: Preview Modal

**What:** An in-page modal overlay (NOT page replacement) that assembles the JD content from current state and renders it inline. Opened by "Preview Job Description" button. Does NOT call `/api/preview` — assembles content client-side.

**Why not use the existing `/api/preview`?** The current `export.js` `showPreview()` replaces the entire page body and requires `sessionStorage` flags + page reload to navigate back. The v5.1 spec says "modal" with a "Return to Builder" button — this must be in-page, not a page navigation. The modal assembles content from `state.selections` and `window.currentProfile` directly.

**HTML structure (added to index.html before `</body>`):**

```html
<!-- JD Preview Modal (PREV-01) -->
<div id="jd-preview-modal" class="jd-preview-modal hidden" role="dialog" aria-modal="true" aria-labelledby="jd-preview-modal-title">
    <div class="jd-preview-modal__backdrop"></div>
    <div class="jd-preview-modal__panel">
        <header class="jd-preview-modal__header">
            <h2 id="jd-preview-modal-title" class="jd-preview-modal__title">Job Description Preview</h2>
            <button id="jd-preview-return-btn" class="btn btn--secondary" type="button">
                <i class="fas fa-arrow-left"></i> Return to Builder
            </button>
        </header>
        <div id="jd-preview-modal__body" class="jd-preview-modal__body">
            <!-- Assembled JD content rendered here by JS -->
        </div>
        <footer class="jd-preview-modal__footer">
            <button id="jd-preview-classify-btn" class="btn btn--primary" type="button">
                Advance to Classify <i class="fas fa-arrow-right"></i>
            </button>
            <div class="jd-preview-modal__export-btns">
                <button id="jd-preview-export-pdf" class="btn btn--secondary" type="button">
                    <i class="fas fa-file-pdf"></i> Export PDF
                </button>
                <button id="jd-preview-export-word" class="btn btn--secondary" type="button">
                    <i class="fas fa-file-word"></i> Export Word
                </button>
            </div>
        </footer>
    </div>
</div>
```

**JS — assembleJDPreview() function:**

```javascript
function assembleJDPreview() {
    const profile = window.currentProfile;
    const state = store.getState();
    if (!profile) return '<p>No profile loaded.</p>';

    const title = state.positionTitle || profile.title;
    const nocCode = profile.noc_code;

    // Group selections by section
    const SECTION_LABELS = {
        core_competencies: 'Core Competencies',
        key_activities: 'Key Activities',
        skills: 'Skills',
        abilities: 'Abilities',
        knowledge: 'Knowledge',
        effort: 'Effort',
        responsibility: 'Responsibility',
        working_conditions: 'Working Conditions'
    };

    let html = `<h1>${escapeHtml(title)}</h1>`;
    html += `<p class="jd-preview__noc">NOC ${escapeHtml(nocCode)}</p>`;

    const leadStatement = profile.reference_attributes?.lead_statement;
    if (leadStatement) {
        html += `<div class="jd-preview__section"><h2>Key Definition</h2><p>${escapeHtml(leadStatement)}</p></div>`;
    }

    Object.entries(state.selections).forEach(([sectionId, selectedIds]) => {
        if (!selectedIds.length) return;
        // core_competencies use reference_attributes array, not statements
        if (sectionId === 'core_competencies') {
            const items = profile.reference_attributes?.core_competencies || [];
            const selectedItems = selectedIds.map(id => {
                const idx = parseInt(id.split('-').pop(), 10);
                return items[idx];
            }).filter(Boolean);
            if (selectedItems.length) {
                html += `<div class="jd-preview__section"><h2>${SECTION_LABELS[sectionId]}</h2><ul>`;
                selectedItems.forEach(item => { html += `<li>${escapeHtml(item)}</li>`; });
                html += '</ul></div>';
            }
            return;
        }
        const sectionData = profile[sectionId];
        if (!sectionData?.statements) return;
        const selectedStmts = selectedIds.map(id => {
            const idx = parseInt(id.split('-').pop(), 10);
            return sectionData.statements[idx];
        }).filter(Boolean);
        if (selectedStmts.length) {
            html += `<div class="jd-preview__section"><h2>${SECTION_LABELS[sectionId]}</h2><ul>`;
            selectedStmts.forEach(stmt => { html += `<li>${escapeHtml(stmt.text)}</li>`; });
            html += '</ul></div>';
        }
    });

    return html;
}
```

**Opening the modal:**

```javascript
document.getElementById('nav-preview-jd').addEventListener('click', () => {
    const body = document.getElementById('jd-preview-modal__body');
    body.innerHTML = assembleJDPreview();
    document.getElementById('jd-preview-modal').classList.remove('hidden');
    document.body.classList.add('modal-open');
});

document.getElementById('jd-preview-return-btn').addEventListener('click', () => {
    document.getElementById('jd-preview-modal').classList.add('hidden');
    document.body.classList.remove('modal-open');
});

document.getElementById('jd-preview-classify-btn').addEventListener('click', () => {
    document.getElementById('jd-preview-modal').classList.add('hidden');
    document.body.classList.remove('modal-open');
    window.jdStepper.goToStep(3);
});
```

**Export buttons in modal** delegate to `exportModule.downloadPDF()` and `exportModule.downloadDOCX()` — those functions already use `buildExportRequest()` which reads from `store.getState()`. The modal just needs to call them.

### Pattern 4: Selections Drawer Redesign

**What:** The existing `#sidebar` and `updateSidebar()` need visual redesign to match v5.1 spec: title "Selection Summary — Your selected JD elements", items grouped by tab with `×` deselect buttons, "Total Selected: N" count at bottom, red "Clear All" button. The trigger (`#selections-tab-btn`) already works.

**Current sidebar limitations:**
- Items have no `×` deselect button
- No "Total Selected: N" count label at bottom
- No "Clear All" button
- `sectionOrder` only lists 5 sections (`key_activities, skills, effort, responsibility, working_conditions`) — missing `core_competencies`, `abilities`, `knowledge`
- Item lookup uses `sectionData.statements[index]` which breaks for `core_competencies` (which is `reference_attributes.core_competencies[index]`)

**Rewritten updateSidebar logic:**

```javascript
const updateSidebar = (state) => {
    const summaryContainer = document.getElementById('selection-summary');
    if (!summaryContainer) return;

    const profile = window.currentProfile;
    const totalSelections = Object.values(state.selections)
        .reduce((sum, arr) => sum + arr.length, 0);

    if (!profile || totalSelections === 0) {
        summaryContainer.innerHTML = '<p class="sidebar__empty">No selections yet.</p>';
        updateSelectionsTabCount(totalSelections);
        return;
    }

    // All sections in display order
    const ALL_SECTIONS = [
        'core_competencies', 'key_activities', 'skills',
        'abilities', 'knowledge', 'effort', 'responsibility', 'working_conditions'
    ];

    let html = '';
    ALL_SECTIONS.forEach(sectionId => {
        const selectedIds = state.selections[sectionId] || [];
        if (!selectedIds.length) return;

        html += `<div class="sidebar__section">
            <h4 class="sidebar__section-title">${SECTION_LABELS[sectionId]} (${selectedIds.length})</h4>
            <ul class="sidebar__list">`;

        selectedIds.forEach(stmtId => {
            const idx = parseInt(stmtId.split('-').pop(), 10);
            let text = '';
            if (sectionId === 'core_competencies') {
                text = profile.reference_attributes?.core_competencies?.[idx] || stmtId;
            } else {
                text = profile[sectionId]?.statements?.[idx]?.text || stmtId;
            }
            html += `<li class="sidebar__item">
                <span class="sidebar__item-text">${escapeHtmlSidebar(text)}</span>
                <button class="sidebar__deselect-btn" type="button"
                        data-section="${sectionId}" data-id="${stmtId}"
                        aria-label="Remove ${escapeHtmlSidebar(text)} from selection">
                    &times;
                </button>
            </li>`;
        });

        html += '</ul></div>';
    });

    html += `<div class="sidebar__footer">
        <span class="sidebar__total">Total Selected: ${totalSelections}</span>
        <button id="sidebar-clear-all" class="btn btn--danger btn--sm" type="button">
            <i class="fas fa-times"></i> Clear All
        </button>
    </div>`;

    summaryContainer.innerHTML = html;
    updateSelectionsTabCount(totalSelections);

    // Wire deselect buttons (event delegation on summaryContainer)
    summaryContainer.querySelectorAll('.sidebar__deselect-btn').forEach(btn => {
        btn.addEventListener('click', () => {
            const sectionId = btn.dataset.section;
            const stmtId = btn.dataset.id;
            const current = store.getState().selections[sectionId] || [];
            store.setSelections(sectionId, current.filter(id => id !== stmtId));
            // Re-render checkbox in tab panel (DOM update)
            const checkbox = document.querySelector(
                `input.statement__checkbox[data-section="${sectionId}"][data-id="${stmtId}"]`
            );
            if (checkbox) {
                checkbox.checked = false;
                checkbox.closest('.statement')?.classList.remove('statement--selected');
            }
        });
    });

    // Wire Clear All button
    const clearAllBtn = document.getElementById('sidebar-clear-all');
    if (clearAllBtn) {
        clearAllBtn.addEventListener('click', () => {
            const emptySelections = {};
            Object.keys(store.getState().selections).forEach(k => { emptySelections[k] = []; });
            store.setState({ selections: emptySelections });
            // Uncheck all checkboxes in DOM
            document.querySelectorAll('input.statement__checkbox').forEach(cb => {
                cb.checked = false;
                cb.closest('.statement')?.classList.remove('statement--selected');
            });
            // Uncheck select-all checkboxes
            document.querySelectorAll('input.select-all-checkbox').forEach(cb => { cb.checked = false; });
        });
    }
};
```

### Pattern 5: Classification and Generate Page Navigation (NAV-04, NAV-05)

**What:** Add bottom nav buttons to Classify and Generate sections.

**Classify section (NAV-04):** Add `← Back to Edit` (goes to step 2) and `Continue to Generate →` (goes to step 4) inside `#classify-section`. These replace or join the existing "Return to Builder" button in `#classify-complete`.

**Generate section (NAV-05):** Add `↺ Regenerate` and `Continue →` buttons inside `#overview-section`. The Regenerate button calls the existing `generation.startGeneration()`.

**Approach:** Inject via JS when navigating to those steps, OR add static HTML to index.html inside the respective `<section>` elements. Static HTML is simpler and more reliable.

---

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| Modal focus trap | Custom focus management | `inert` attribute on background, or simple `tabindex` management | Not needed for a single-level app with no deep focus trees |
| Deselect-from-drawer causing stale DOM | Custom two-way binding | Direct DOM query for matching checkbox by `data-section` + `data-id` | Checkbox DOM is always present (accordion renders on profile load) |
| Preview content assembly | `/api/preview` endpoint | Client-side assembly from `store.getState()` + `window.currentProfile` | The API call does page replacement; modal needs inline content |
| Section labels map | Redefine in each file | Add `SECTION_LABELS` to `accordion.js` (already has `JD_ELEMENT_LABELS`) or expand sidebar.js | `JD_ELEMENT_LABELS` in accordion.js currently only has 5 sections |

**Key insight:** The existing `resetSelectionsForProfile` in state.js already handles the "same card preserves, different card clears" logic correctly. Do not reimplement it.

---

## Common Pitfalls

### Pitfall 1: core_competencies item lookup in sidebar

**What goes wrong:** `updateSidebar` looks up items as `profile[sectionId].statements[index]`. For `core_competencies`, the data is at `profile.reference_attributes.core_competencies[index]` (a plain string array, not objects with `.text`). Looking up `profile.core_competencies` returns `undefined`.

**Why it happens:** core_competencies was added in Phase 27-02 with a different data path than all other sections.

**How to avoid:** Add a special-case branch in sidebar item lookup: if `sectionId === 'core_competencies'`, use `profile.reference_attributes?.core_competencies?.[idx]` directly.

**Warning signs:** Sidebar shows item IDs (e.g., "core_competencies-2") instead of text when core competencies are selected.

### Pitfall 2: sectionOrder missing core_competencies / abilities / knowledge

**What goes wrong:** `sidebar.js` iterates `state.sectionOrder` which is `['key_activities', 'skills', 'effort', 'responsibility', 'working_conditions']`. Items selected in Core Competencies, Abilities, or Knowledge tabs never appear in the drawer.

**Why it happens:** `sectionOrder` was defined before Phase 27-02 added these sections.

**How to avoid:** In the rewritten `updateSidebar`, iterate a hardcoded `ALL_SECTIONS` array covering all 8 sections, not `state.sectionOrder`.

### Pitfall 3: Deselect from drawer doesn't uncheck DOM checkbox

**What goes wrong:** Clicking `×` in the drawer calls `store.setSelections(...)` which triggers a store notification and re-renders the sidebar. But the checkbox in the tab panel DOM is not updated — it stays checked visually even though the item is removed from state.

**Why it happens:** The accordion tab panels are rendered once on profile load and not re-rendered on every state change (they use the initial `selectedIds` at render time for the `checked` attribute).

**How to avoid:** After calling `store.setSelections`, immediately find the matching DOM checkbox with `document.querySelector('input.statement__checkbox[data-section="X"][data-id="Y"]')` and set `checkbox.checked = false` and remove `statement--selected` from the parent `<li>`.

**Warning signs:** Unchecking from sidebar shows lower count but tab panels still show items as checked.

### Pitfall 4: Clear All doesn't uncheck select-all checkboxes

**What goes wrong:** "Clear All" resets all `state.selections` arrays but doesn't update the "Select All" checkboxes in each tab panel, which stay in their checked state.

**How to avoid:** After clearing state, also run `document.querySelectorAll('input.select-all-checkbox').forEach(cb => { cb.checked = false; })`.

### Pitfall 5: Modal scroll blocked by fixed body

**What goes wrong:** Adding `overflow: hidden` to `<body>` when modal opens prevents scroll on the modal body too, making long JD previews unscrollable.

**How to avoid:** Apply `overflow: hidden` only to `body` (or use `pointer-events: none` on the backdrop). The `.jd-preview-modal__body` div must have its own `overflow-y: auto` and `max-height` (e.g., `calc(100vh - 180px)`).

### Pitfall 6: #action-bar vs #build-nav-bar coexistence

**What goes wrong:** If `#action-bar` is not hidden when `#build-nav-bar` is shown, two fixed bottom bars overlap.

**How to avoid:** When introducing `#build-nav-bar`, ensure `#action-bar` is permanently hidden (remove from HTML or set `display: none` always). The old "Create Job Description" button functionality is superseded by the new 3-button bar. `updateActionBar` in `selection.js` references `#action-bar` — either keep it pointing to a hidden element (safe, no visible effect) or update it to not affect the new bar.

### Pitfall 7: Export buttons in modal use stale export data

**What goes wrong:** `exportModule.downloadPDF()` uses `exportModule.currentExportData` which is set by `buildExportRequest()`. If the user opens the preview modal and clicks Export without having called `showPreview()` first, `currentExportData` is null.

**How to avoid:** When opening the preview modal, immediately call `exportModule.currentExportData = exportModule.buildExportRequest()` to ensure the export data is fresh. This is a one-liner before assembling the preview content.

### Pitfall 8: Abilities/Knowledge ID lookups in sidebar

**What goes wrong:** Abilities and Knowledge use `renderLevelGroupedContent` with IDs `abilities-0`, `abilities-1`, etc. based on the filtered-array index (not the global statements array index). The sidebar lookup must use `profile.skills.statements` filtered to `source_attribute === 'Abilities'` or `'Knowledge'` to find the correct item at `[idx]`.

**Why it happens:** Per the Phase 27-02 decision: "Abilities/Knowledge IDs use filtered-array positions" — IDs are `abilities-0..N` where 0 is the first item in the filtered-by-source-attribute sub-array, not the full statements array.

**How to avoid:** In the sidebar, for `abilities` and `knowledge` sections, look up items from the filtered sub-array:
```javascript
const filtered = (profile.skills?.statements || [])
    .filter(s => s.source_attribute === (sectionId === 'abilities' ? 'Abilities' : 'Knowledge'));
text = filtered[idx]?.text || stmtId;
```

---

## Code Examples

### Current State Structure (state.js)

```javascript
// Source: static/js/state.js lines 58-72
const defaultState = {
    positionTitle: '',
    selections: {
        core_competencies: [],   // IDs: "core_competencies-0", "core_competencies-1"
        key_activities: [],      // IDs: "key_activities-N" (global index in profile.key_activities.statements)
        skills: [],              // IDs: "skills-N" (global index in profile.skills.statements)
        abilities: [],           // IDs: "abilities-N" (filtered-array index, source_attribute='Abilities')
        knowledge: [],           // IDs: "knowledge-N" (filtered-array index, source_attribute='Knowledge')
        effort: [],              // IDs: "effort-N" (global index in profile.effort.statements)
        responsibility: [],      // IDs: "responsibility-N" (global index)
        working_conditions: []   // IDs: "working_conditions-N" (global index)
    },
    sectionOrder: ['key_activities', 'skills', 'effort', 'responsibility', 'working_conditions'],
    currentProfileCode: null
};
```

### Same-vs-Different Card Logic (already correct)

```javascript
// Source: static/js/state.js lines 81-107
const resetSelectionsForProfile = (nocCode) => {
    const state = store.getState();
    if (state.currentProfileCode !== nocCode) {
        // DIFFERENT card — clears ALL selections
        store.setState({ positionTitle: '', selections: { ... all empty ... }, currentProfileCode: nocCode });
    } else {
        // SAME card — preserves all selections (no-op)
        console.log('[DEBUG state.js] Same profile', nocCode, '- preserving selections');
    }
};
// Called from handleResultClick in main.js line 490
```

### Navigation Bar Visibility Pattern

```javascript
// Source: main.js navigateToStep() — pattern used in case 2 (Build)
// case 2 shows profile-tabs-container; other cases hide it.
// Build nav bar should track profile-tabs-container visibility.

// On profile-loaded event:
document.addEventListener('profile-loaded', () => {
    document.getElementById('build-nav-bar')?.classList.remove('hidden');
    document.getElementById('action-bar')?.classList.add('hidden');
});

// On navigateToStep(1): hide build-nav-bar
// On navigateToStep(2): show build-nav-bar (if profile loaded)
// On navigateToStep(3+): hide build-nav-bar
```

### Sidebar Deselect + DOM Sync Pattern

```javascript
// After store.setSelections — sync the checkbox DOM:
const checkbox = document.querySelector(
    `input.statement__checkbox[data-section="${sectionId}"][data-id="${stmtId}"]`
);
if (checkbox) {
    checkbox.checked = false;
    checkbox.closest('.statement')?.classList.remove('statement--selected');
}
// Also update select-all checkbox state for that section
const selectAll = document.querySelector(
    `input.select-all-checkbox[data-section="${sectionId}"]`
);
if (selectAll) selectAll.checked = false;
```

### Modal CSS Pattern (prevent background scroll, allow modal scroll)

```css
/* Source: main.css — add new rules */
body.modal-open {
    overflow: hidden;
}
.jd-preview-modal {
    position: fixed;
    inset: 0;
    z-index: 500;
    display: flex;
    align-items: center;
    justify-content: center;
}
.jd-preview-modal__backdrop {
    position: absolute;
    inset: 0;
    background: rgba(0, 0, 0, 0.5);
}
.jd-preview-modal__panel {
    position: relative;
    background: white;
    border-radius: 8px;
    width: 90%;
    max-width: 900px;
    max-height: 90vh;
    display: flex;
    flex-direction: column;
    z-index: 1;
}
.jd-preview-modal__body {
    flex: 1;
    overflow-y: auto;
    padding: 2rem;
}
.jd-preview-modal.hidden {
    display: none;
}
```

---

## State of the Art

| Old Approach | Current Approach | When Changed | Impact on Phase 28 |
|--------------|------------------|--------------|---------------------|
| Preview replaces entire page body | Modal overlay, in-page | Phase 28 introduces this | export.js `showPreview()` is NOT used; new modal function needed |
| Sidebar shows 5 sections only | Drawer shows all 8 sections | Phase 27-02 added 3 new selection types | Must update `updateSidebar` to iterate all 8 sections |
| `#action-bar` with single "Create JD" button | 3-button `#build-nav-bar` | Phase 28 replaces it | `#action-bar` becomes redundant; must hide it |
| No bottom nav on Classify/Generate | NAV-04/05 buttons on those pages | Phase 28 adds them | New static HTML in `#classify-section` and `#overview-section` |

**Still valid from prior phases:**
- `resetSelectionsForProfile` correctly handles same-vs-different card (no change needed)
- `export.js` `buildExportRequest()` already assembles all selections for export (reuse for PDF/Word in modal footer)
- `initSidebar` wiring for `#selections-tab-btn` toggle is correct (no change needed)

---

## Open Questions

1. **Preview content fidelity vs. export template**
   - What we know: The current `/api/preview` uses `jd_preview.html` Jinja template which renders a full document with Appendix A Compliance Metadata, audit trail, etc. (visible in screenshot 2.8 — the preview is very long).
   - What's unclear: Should the modal preview match the export template exactly (long, with appendices), or be a simplified summary view?
   - Screenshot 2.8 shows the full export preview including "Appendix A: Compliance Metadata" — but this was the OLD full-page preview. The v5.1 modal spec doesn't specify whether appendices are included.
   - Recommendation: Show only selected JD elements (no compliance appendix) in the modal preview. The appendix is for the exported document, not the in-browser preview. This keeps the modal focused and fast.

2. **Export PDF/Word from modal requires active state**
   - What we know: `exportModule.downloadPDF()` uses `exportModule.currentExportData`. When called from the modal (not from the old preview page), `currentExportData` must be freshly set.
   - Recommendation: Call `exportModule.currentExportData = exportModule.buildExportRequest()` when opening the modal, before assembling preview HTML.

3. **#classify-section navigation buttons (NAV-04) placement**
   - What we know: `#classify-section` currently has a "Return to Builder" button inside `#classify-complete` (the success state div, line 355 in index.html). "Continue to Generate" is new.
   - What's unclear: Should nav buttons appear always (even during loading/error states) or only when classify-results are shown?
   - Recommendation: Add a persistent `<div class="classify-nav-bar">` inside `#classify-section` that shows the `← Back to Edit` and `Continue to Generate →` buttons always. This matches the v5.1 spec which doesn't indicate conditional visibility.

4. **generate.js Regenerate button reference**
   - What we know: `generate.js` has a `regenerate-btn` (inside `#overview-section`) and `generation.startGeneration()`.
   - What's unclear: NAV-05 says "Generate page shows Regenerate and Continue buttons". Does "Continue" go to Export (step 5) or is it a new Generate-specific nav?
   - Recommendation: "Continue →" on Generate page goes to `goToStep(5)` (Export). This follows the stepper sequence: Generate is step 4, Export is step 5.

---

## Sources

### Primary (HIGH confidence)
- Direct inspection of `static/js/state.js` — selections shape, resetSelectionsForProfile behavior
- Direct inspection of `static/js/sidebar.js` — current updateSidebar, initSidebar wiring
- Direct inspection of `static/js/main.js` — navigateToStep, handleResultClick, action-bar
- Direct inspection of `static/js/export.js` — buildExportRequest, showPreview, downloadPDF/DOCX
- Direct inspection of `static/js/selection.js` — handleSelection, handleSelectAll, updateActionBar
- Direct inspection of `static/js/accordion.js` — renderLevelGroupedContent (abilities/knowledge indexed by filtered array)
- Direct inspection of `templates/index.html` — full DOM structure, #sidebar, #action-bar, #classify-section
- Direct inspection of `.planning/phases/27-build-page-redesign/27-02-PLAN.md` — confirmed Abilities/Knowledge use filtered-array indices
- Visual inspection of `2.9 Selections drawer.png` — confirmed drawer design: section grouping, × buttons, Total Selected count, Clear All button, right-edge slide-out

### Secondary (MEDIUM confidence)
- Visual inspection of `2.8 Preview.png` — confirmed preview shows full JD with sections; the OLD full-page export preview is what was being shown; v5.1 modal should be simpler

---

## Metadata

**Confidence breakdown:**
- Standard stack: HIGH — pure in-project code, no new dependencies
- Architecture: HIGH — all patterns derived from direct codebase inspection
- Pitfalls: HIGH — all pitfalls found from reading actual code (core_competencies path, sectionOrder gap, filtered array indices)
- Open questions: MEDIUM — 4 ambiguities remain, all with clear recommendations

**Research date:** 2026-03-12
**Valid until:** 2026-04-12 (stable codebase, no fast-moving external dependencies)
