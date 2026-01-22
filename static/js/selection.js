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
    const generateBtn = document.getElementById('generate-btn');
    if (!actionBar || !generateBtn) return;

    // Count total selections
    const totalSelections = Object.values(state.selections)
        .reduce((sum, arr) => sum + arr.length, 0);

    // Show action bar and enable button if selections exist
    if (totalSelections > 0) {
        actionBar.classList.remove('hidden');
        generateBtn.disabled = false;
        generateBtn.textContent = `Generate Overview (${totalSelections} selected)`;
    } else {
        generateBtn.disabled = true;
        generateBtn.textContent = 'Generate Overview (select statements first)';
    }
};

// Export
window.initSelection = initSelection;
