// Selection handling with state updates
const initSelection = () => {
    // Event delegation for checkbox changes
    document.querySelector('.jd-sections').addEventListener('change', (e) => {
        if (e.target.classList.contains('statement__checkbox')) {
            handleSelection(e.target);
        }
    });

    // Subscribe to state changes for UI updates
    store.subscribe((state) => {
        Object.keys(state.selections).forEach(sectionId => {
            updateSelectionCount(sectionId);
        });
        updateSidebar(state);
        updateActionBar(state);
    });
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

// Export
window.initSelection = initSelection;
