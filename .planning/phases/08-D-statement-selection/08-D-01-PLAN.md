---
phase: 08-D-statement-selection
plan: 01
type: execute
wave: 1
depends_on: []
files_modified:
  - static/js/accordion.js
  - static/css/accordion.css
  - static/js/selection.js
  - templates/index.html
autonomous: true

must_haves:
  truths:
    - "Every statement row has a checkbox for selection"
    - "Proficiency circles display correctly (1-5 scale with filled/empty circles)"
    - "Provenance labels are always visible below each statement in small italics"
    - "Hovering over statement text shows description as tooltip for items with proficiency"
    - "Single 'Create Job Description (X selected)' button visible, count updates with selections"
    - "Tooltip is keyboard accessible via focus"
  artifacts:
    - path: "static/js/accordion.js"
      provides: "Statement rendering with data-tooltip and tabindex for description tooltips"
      contains: "data-tooltip"
    - path: "static/css/accordion.css"
      provides: "CSS tooltip styles using ::after pseudo-element"
      contains: ".statement__text[data-tooltip]::after"
    - path: "static/js/selection.js"
      provides: "Single button text update with selection count"
      contains: "Create Job Description"
    - path: "templates/index.html"
      provides: "Single create button in action bar"
      contains: "id=\"create-btn\""
  key_links:
    - from: "static/js/accordion.js"
      to: "EnrichedNOCStatement.description"
      via: "data-tooltip attribute populated from stmt.description"
      pattern: "data-tooltip.*stmt\\.description"
    - from: "static/js/selection.js"
      to: "templates/index.html"
      via: "updateActionBar updates create-btn textContent"
      pattern: "create-btn.*textContent"
---

<objective>
Implement statement selection UI with accessible tooltips, always-visible provenance, and consolidated action button.

Purpose: Complete the v2.0 UI redesign by adding the statement selection layer (Step 10) that enables users to select statements across all Job Header tabs with clear provenance and proficiency display.

Output: Statement rows with checkboxes, tooltips showing descriptions on hover/focus, visible provenance labels, and single "Create Job Description (X selected)" button.
</objective>

<execution_context>
@C:\Users\Administrator\.claude/get-shit-done/workflows/execute-plan.md
@C:\Users\Administrator\.claude/get-shit-done/templates/summary.md
</execution_context>

<context>
@.planning/PROJECT.md
@.planning/ROADMAP.md
@.planning/phases/08-D-statement-selection/08-D-RESEARCH.md
@.planning/phases/06-enhanced-ui-display/06-CONTEXT.md
@static/js/accordion.js
@static/js/selection.js
@static/css/accordion.css
@templates/index.html
</context>

<tasks>

<task type="auto">
  <name>Task 1: Add tooltip data attribute and keyboard accessibility to statements</name>
  <files>static/js/accordion.js</files>
  <action>
    Modify the statement rendering in `createAccordionSection()` function to:

    1. Add `data-tooltip` attribute to `.statement__text` span ONLY when `stmt.description` exists
    2. Add `tabindex="0"` to make statement text keyboard focusable for tooltip access
    3. Ensure provenance is always visible (already is, but verify no display:none)

    **Update the li.innerHTML template in createAccordionSection():**

    Change from:
    ```javascript
    li.innerHTML = `
        <label class="statement__label">
            <input type="checkbox" class="statement__checkbox"
                   data-section="${sectionId}"
                   data-id="${stmtId}"
                   ${isSelected ? 'checked' : ''}>
            <span class="statement__content">
                <span class="statement__text">${escapeHtml(stmt.text)}${dimensionBadgeHtml}</span>
                <span class="statement__source">from ${escapeHtml(sourceText)}</span>
            </span>
            ${proficiencyHtml}
        </label>
    `;
    ```

    To:
    ```javascript
    // Build tooltip attribute if description exists
    const tooltipAttr = stmt.description
        ? `data-tooltip="${escapeHtml(stmt.description)}" tabindex="0"`
        : '';

    li.innerHTML = `
        <label class="statement__label">
            <input type="checkbox" class="statement__checkbox"
                   data-section="${sectionId}"
                   data-id="${stmtId}"
                   ${isSelected ? 'checked' : ''}>
            <span class="statement__content">
                <span class="statement__text" ${tooltipAttr}>${escapeHtml(stmt.text)}${dimensionBadgeHtml}</span>
                <span class="statement__source">from ${escapeHtml(sourceText)}</span>
            </span>
            ${proficiencyHtml}
        </label>
    `;
    ```

    **Key notes:**
    - Only add `data-tooltip` and `tabindex` when `stmt.description` is truthy
    - Use `escapeHtml()` on description to prevent XSS from HTML special chars
    - `.statement__source` already has `display: block` in CSS, no changes needed there
    - This pattern allows CSS to style tooltips only when data-tooltip exists
  </action>
  <verify>
    1. Open browser DevTools on profile page
    2. Inspect a statement row (e.g., "Analyzing Data or Information")
    3. Confirm `.statement__text` span has `data-tooltip` attribute with description text
    4. Confirm `tabindex="0"` is present on statements with descriptions
    5. Confirm statements without descriptions do NOT have data-tooltip attribute
    6. Confirm provenance label ("from Work Activities") is visible without hovering
  </verify>
  <done>
    Statement text elements have data-tooltip with description content and are keyboard focusable. Provenance labels visible by default.
  </done>
</task>

<task type="auto">
  <name>Task 2: Add CSS tooltip styles with WCAG accessibility</name>
  <files>static/css/accordion.css</files>
  <action>
    Add CSS rules at the end of accordion.css for accessible tooltips using ::after pseudo-element:

    ```css
    /* ============================================
       Statement Description Tooltips (Phase 08-D)
       WCAG 2.1 SC 1.4.13 compliant
       ============================================ */

    /* Make statement text with tooltip focusable and indicate help cursor */
    .statement__text[data-tooltip] {
        position: relative;
        cursor: help;
        display: inline-block;
        outline-offset: 2px;
    }

    /* Tooltip content using ::after pseudo-element */
    .statement__text[data-tooltip]::after {
        content: attr(data-tooltip);

        /* Positioning - above element */
        position: absolute;
        bottom: calc(100% + 8px);
        left: 0;

        /* Box model */
        padding: 0.5rem 0.75rem;
        max-width: 320px;
        min-width: 200px;
        width: max-content;

        /* Typography */
        font-size: 0.75rem;
        font-weight: normal;
        line-height: 1.5;
        white-space: normal;
        text-align: left;

        /* Styling */
        background: #333;
        color: white;
        border-radius: 4px;
        box-shadow: 0 2px 8px rgba(0,0,0,0.2);

        /* Hidden by default */
        opacity: 0;
        pointer-events: none;
        transition: opacity 0.2s ease;
        z-index: 100;
    }

    /* Tooltip arrow */
    .statement__text[data-tooltip]::before {
        content: '';
        position: absolute;
        bottom: calc(100% + 2px);
        left: 16px;
        border: 6px solid transparent;
        border-top-color: #333;
        opacity: 0;
        pointer-events: none;
        transition: opacity 0.2s ease;
        z-index: 101;
    }

    /* Show tooltip on hover AND focus (WCAG 2.1 keyboard accessibility) */
    .statement__text[data-tooltip]:hover::after,
    .statement__text[data-tooltip]:hover::before,
    .statement__text[data-tooltip]:focus::after,
    .statement__text[data-tooltip]:focus::before {
        opacity: 1;
    }

    /* Ensure provenance label is always visible (verify existing styles) */
    .statement__source {
        display: block;
        font-size: 0.75rem;
        color: var(--text-light);
        font-style: italic;
        margin-top: 0.25rem;
    }
    ```

    **Key notes:**
    - Position tooltip above (`bottom: calc(100% + 8px)`) to avoid viewport edge clipping
    - Both `:hover` and `:focus` trigger tooltip for keyboard users
    - `pointer-events: none` prevents tooltip from interfering with mouse events
    - Arrow positioned at 16px from left edge for visual connection
    - `max-width: 320px` prevents overly wide tooltips
    - Existing Escape key handler in accordion.js blurs focused elements to dismiss
  </action>
  <verify>
    1. Hover over a statement with description - tooltip should appear above text
    2. Tab to a statement with description - tooltip should appear on focus
    3. Press Escape - tooltip should disappear (element blurs)
    4. Check contrast - white text on #333 background meets WCAG AA
    5. Verify tooltip doesn't overflow viewport on statements near edges
    6. Confirm provenance label ("from Main Duties") shows in italics below statement
  </verify>
  <done>
    CSS tooltips appear on hover and focus with arrow pointer, styled to match application theme. Provenance labels confirmed always visible in italics.
  </done>
</task>

<task type="auto">
  <name>Task 3: Consolidate action bar to single Create button</name>
  <files>templates/index.html, static/js/selection.js</files>
  <action>
    **HTML Changes (templates/index.html):**

    Find the action bar footer (around line 127):
    ```html
    <footer id="action-bar" class="action-bar hidden">
        <button id="generate-btn" disabled>Generate Overview (select statements first)</button>
        <button id="create-btn" class="btn btn--primary" disabled>Create Job Description</button>
    </footer>
    ```

    Replace with single button:
    ```html
    <!-- Sticky Action Bar (Phase 08-D: Single consolidated button) -->
    <footer id="action-bar" class="action-bar hidden">
        <button id="create-btn" class="btn btn--primary" disabled>
            Create Job Description (select statements first)
        </button>
    </footer>
    ```

    **JavaScript Changes (static/js/selection.js):**

    Update `updateActionBar()` function to update only the create button with selection count:

    Change from:
    ```javascript
    const updateActionBar = (state) => {
        const actionBar = document.getElementById('action-bar');
        const generateBtn = document.getElementById('generate-btn');
        const createBtn = document.getElementById('create-btn');
        if (!actionBar || !generateBtn) return;

        // Count total selections
        const totalSelections = Object.values(state.selections)
            .reduce((sum, arr) => sum + arr.length, 0);

        // Show action bar and enable button if selections exist
        if (totalSelections > 0) {
            actionBar.classList.remove('hidden');
            generateBtn.disabled = false;
            generateBtn.textContent = `Generate Overview (${totalSelections} selected)`;
            // Enable Create button when selections exist (doesn't require overview)
            if (createBtn) {
                createBtn.disabled = false;
            }
        } else {
            generateBtn.disabled = true;
            generateBtn.textContent = 'Generate Overview (select statements first)';
            // Disable Create button when no selections
            if (createBtn) {
                createBtn.disabled = true;
            }
        }
    };
    ```

    To:
    ```javascript
    const updateActionBar = (state) => {
        const actionBar = document.getElementById('action-bar');
        const createBtn = document.getElementById('create-btn');
        if (!actionBar || !createBtn) return;

        // Count total selections across ALL sections
        const totalSelections = Object.values(state.selections)
            .reduce((sum, arr) => sum + arr.length, 0);

        // Update button text and state based on selection count
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
    ```

    **Key notes:**
    - Remove all references to `generate-btn` since it no longer exists
    - Action bar remains visible but button disabled when no selections
    - Button text dynamically shows selection count: "Create Job Description (12 selected)"
    - Overview generation now happens automatically during Create flow (handled elsewhere)
  </action>
  <verify>
    1. Load profile page - action bar should show single "Create Job Description" button
    2. Button shows "(select statements first)" and is disabled initially
    3. Select a statement - button enables and shows "(1 selected)"
    4. Select more statements - count updates in real-time: "(5 selected)"
    5. Deselect all - button returns to disabled with "(select statements first)"
    6. Verify no JavaScript errors in console about missing generate-btn
    7. Verify clicking button still triggers the create job description flow
  </verify>
  <done>
    Single "Create Job Description (X selected)" button replaces dual-button layout. Button text updates dynamically with selection count.
  </done>
</task>

</tasks>

<verification>
After all tasks complete:

1. **Visual verification:**
   - Load any occupation profile
   - Confirm checkboxes appear on all statement rows
   - Confirm proficiency circles display (e.g., "●●●●○ L4")
   - Confirm provenance labels visible in italics ("from Work Activities")
   - Hover over statement text - tooltip should show description
   - Tab to statement text - tooltip should show on focus
   - Single "Create Job Description" button in action bar

2. **Functional verification:**
   - Select 5 statements across different sections
   - Button should show "Create Job Description (5 selected)"
   - Deselect 2 statements - count should update to "(3 selected)"
   - Click Create button - should initiate JD creation flow

3. **Accessibility verification:**
   - Tab through statements - tooltips accessible via keyboard
   - Press Escape - tooltips dismiss
   - Screen reader announces checkbox state and label
   - Button text announced with count

4. **No regressions:**
   - Statement search filter still works
   - Drag-and-drop section reordering still works
   - Selections persist across page refresh
</verification>

<success_criteria>
1. Every statement row has a checkbox (SEL-01) - verified by visual inspection
2. Proficiency circles display correctly 1-5 scale (SEL-02) - already working, no changes needed
3. Provenance labels always visible in small italics (SEL-03) - CSS confirms display:block
4. Tooltip shows description on hover/focus for proficiency items (SEL-04) - CSS ::after pattern
5. Single "Create Job Description (X selected)" button (SEL-05) - HTML consolidated, JS updated
6. No console errors, no visual regressions
</success_criteria>

<output>
After completion, create `.planning/phases/08-D-statement-selection/08-D-01-SUMMARY.md`
</output>
