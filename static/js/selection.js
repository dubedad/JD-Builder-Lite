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

// Export
window.initSelection = initSelection;
window.updateActionBar = updateActionBar;
