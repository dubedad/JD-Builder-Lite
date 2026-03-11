// Sidebar toggle and selection summary
const initSidebar = () => {
    const sidebar = document.getElementById('sidebar');
    const toggleBtn = document.getElementById('sidebar-toggle');

    // Hide old sidebar-toggle (replaced by selections-tab)
    if (toggleBtn) {
        toggleBtn.style.display = 'none';
    }

    // Wire new selections tab (CHROME-05)
    const selectionsTab = document.getElementById('selections-tab-btn');
    if (selectionsTab) {
        selectionsTab.addEventListener('click', () => {
            sidebar.classList.toggle('open');
            sidebar.classList.toggle('collapsed');
            document.body.classList.toggle('sidebar-open');
        });
    }

    // Subscribe to state changes
    store.subscribe(updateSidebar);
};

const updateSidebar = (state) => {
    const summaryContainer = document.getElementById('selection-summary');
    if (!summaryContainer) return;

    const profile = window.currentProfile;
    if (!profile) {
        summaryContainer.innerHTML = '<p class="sidebar__empty">Load a profile to see selections</p>';
        return;
    }

    const totalSelections = Object.values(state.selections)
        .reduce((sum, arr) => sum + arr.length, 0);

    if (totalSelections === 0) {
        summaryContainer.innerHTML = '<p class="sidebar__empty">No selections yet. Check statements to add them to your job description.</p>';
        return;
    }

    // Build summary HTML grouped by section
    let html = '';
    state.sectionOrder.forEach(sectionId => {
        const selectedIds = state.selections[sectionId] || [];
        if (selectedIds.length === 0) return;

        const sectionData = profile[sectionId];
        if (!sectionData || !sectionData.statements) return;

        html += `<div class="sidebar__section">
            <h4 class="sidebar__section-title">${JD_ELEMENT_LABELS[sectionId]} (${selectedIds.length})</h4>
            <ul class="sidebar__list">`;

        selectedIds.forEach(stmtId => {
            const index = parseInt(stmtId.split('-').pop(), 10);
            const stmt = sectionData.statements[index];
            if (stmt) {
                html += `<li class="sidebar__item">
                    <span class="sidebar__item-text">${escapeHtmlSidebar(stmt.text)}</span>
                    <span class="sidebar__item-source">from ${escapeHtmlSidebar(stmt.source_attribute)}</span>
                </li>`;
            }
        });

        html += '</ul></div>';
    });

    summaryContainer.innerHTML = html;

    // Update selections tab count (CHROME-05)
    const tabCount = document.getElementById('selections-tab-count');
    if (tabCount) {
        tabCount.textContent = totalSelections;
    }
};

const escapeHtmlSidebar = (text) => {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
};

// Export
window.initSidebar = initSidebar;
window.updateSidebar = updateSidebar;
