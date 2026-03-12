// Selection handling with state updates
const initSelection = () => {
    console.log('[DEBUG selection.js] initSelection called');

    // Event delegation for checkbox changes - use document-level delegation
    // to capture checkboxes in both old accordion (.jd-sections) AND new tab panels
    document.addEventListener('change', (e) => {
        if (e.target.classList.contains('statement__checkbox')) {
            console.log('[DEBUG selection.js] Checkbox changed:', e.target.checked, 'section:', e.target.dataset.section);
            handleSelection(e.target);
        }
        // Handle Select All checkbox
        if (e.target.classList.contains('select-all-checkbox')) {
            console.log('[DEBUG selection.js] Select All changed:', e.target.checked, 'section:', e.target.dataset.section);
            handleSelectAll(e.target);
        }
    });

    console.log('[DEBUG selection.js] Document-level change listener attached');

    // Subscribe to state changes for UI updates
    store.subscribe((state) => {
        Object.keys(state.selections).forEach(sectionId => {
            updateSelectionCount(sectionId);
        });
        updateSidebar(state);
        updateActionBar(state);
    });

    // Trigger initial state update for action bar (in case there are persisted selections)
    updateActionBar(store.getState());
};

const handleSelection = (checkbox) => {
    const sectionId = checkbox.dataset.section;
    const stmtId = checkbox.dataset.id;
    const state = store.getState();

    // Get current selections for this section
    const current = state.selections[sectionId] || [];

    let newSelections;
    if (checkbox.checked) {
        // Add to selections
        if (!current.includes(stmtId)) {
            newSelections = [...current, stmtId];
            // Track selection timestamp for audit trail
            const timestamps = state.selectionTimestamps || {};
            timestamps[stmtId] = new Date().toISOString();
            store.setState({ selectionTimestamps: timestamps });
        } else {
            newSelections = current;
        }
    } else {
        // Remove from selections
        newSelections = current.filter(id => id !== stmtId);
    }

    // Update store (triggers subscribers)
    store.setSelections(sectionId, newSelections);

    // Update visual highlight
    const li = checkbox.closest('.statement');
    if (li) {
        li.classList.toggle('statement--selected', checkbox.checked);
    }
};

/**
 * Handle Select All checkbox - select or deselect all statements in a section
 */
const handleSelectAll = (selectAllCheckbox) => {
    const sectionId = selectAllCheckbox.dataset.section;
    const isChecked = selectAllCheckbox.checked;
    const state = store.getState();

    // Find all statement checkboxes in this section
    const sectionCheckboxes = document.querySelectorAll(
        `input.statement__checkbox[data-section="${sectionId}"]`
    );

    const newSelections = [];
    const now = new Date().toISOString();
    const timestamps = { ...state.selectionTimestamps } || {};

    sectionCheckboxes.forEach(checkbox => {
        const stmtId = checkbox.dataset.id;
        checkbox.checked = isChecked;

        // Update visual highlight
        const li = checkbox.closest('.statement');
        if (li) {
            li.classList.toggle('statement--selected', isChecked);
        }

        if (isChecked) {
            newSelections.push(stmtId);
            timestamps[stmtId] = now;
        }
    });

    // Update store with all selections at once
    store.setSelections(sectionId, newSelections);
    if (isChecked) {
        store.setState({ selectionTimestamps: timestamps });
    }

    console.log('[DEBUG selection.js] Select All:', isChecked ? 'selected' : 'deselected', newSelections.length, 'items in', sectionId);
};

const updateActionBar = (state) => {
    const actionBar = document.getElementById('action-bar');
    const createBtn = document.getElementById('create-btn');
    if (!actionBar || !createBtn) return;

    // Count total selections across ALL sections
    const totalSelections = Object.values(state.selections)
        .reduce((sum, arr) => sum + arr.length, 0);

    console.log('[DEBUG selection.js] updateActionBar called, totalSelections:', totalSelections);

    // Update button text and state based on selection count
    if (totalSelections > 0) {
        actionBar.classList.remove('hidden');
        createBtn.disabled = false;
        createBtn.classList.remove('btn--disabled');
        createBtn.textContent = `Create Job Description (${totalSelections} selected)`;
    } else {
        actionBar.classList.remove('hidden'); // Keep visible but disabled
        createBtn.disabled = true;
        createBtn.classList.add('btn--disabled');
        createBtn.textContent = 'Create Job Description (select statements first)';
    }
};

/**
 * Deselect a single item from the sidebar drawer.
 * Syncs the DOM checkbox state and updates the store.
 * PITFALL: Must also uncheck the DOM checkbox with matching data-section and data-id.
 */
const deselectFromDrawer = (sectionId, stmtId) => {
    const state = store.getState();
    const current = state.selections[sectionId] || [];
    const newSelections = current.filter(id => id !== stmtId);
    store.setSelections(sectionId, newSelections);

    // Sync DOM checkbox
    const checkbox = document.querySelector(
        `input.statement__checkbox[data-section="${sectionId}"][data-id="${stmtId}"]`
    );
    if (checkbox) {
        checkbox.checked = false;
        const li = checkbox.closest('.statement');
        if (li) li.classList.remove('statement--selected');
    }

    // Update select-all checkbox for this section if needed
    const selectAllCb = document.querySelector(
        `input.select-all-checkbox[data-section="${sectionId}"]`
    );
    if (selectAllCb && selectAllCb.checked) {
        selectAllCb.checked = false;
    }
};

/**
 * Clear all selections across all sections.
 * PITFALL: Must also uncheck all DOM checkboxes and all select-all-checkbox inputs.
 */
const clearAllSelections = () => {
    // Clear store
    const emptySelections = {
        core_competencies: [],
        key_activities: [],
        skills: [],
        abilities: [],
        knowledge: [],
        effort: [],
        responsibility: [],
        working_conditions: []
    };
    store.setState({ selections: emptySelections });

    // Uncheck all statement checkboxes
    document.querySelectorAll('input.statement__checkbox:checked').forEach(cb => {
        cb.checked = false;
        const li = cb.closest('.statement');
        if (li) li.classList.remove('statement--selected');
    });

    // Uncheck all select-all checkboxes
    document.querySelectorAll('input.select-all-checkbox:checked').forEach(cb => {
        cb.checked = false;
    });
};

// Export
window.initSelection = initSelection;
window.updateActionBar = updateActionBar;
window.deselectFromDrawer = deselectFromDrawer;
window.clearAllSelections = clearAllSelections;
