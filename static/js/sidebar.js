// Sidebar toggle and selection summary
const initSidebar = () => {
    const sidebar = document.getElementById('sidebar');
    const toggleBtn = document.getElementById('sidebar-toggle');

    // Hide old sidebar-toggle (replaced by selections-tab)
    if (toggleBtn) {
        toggleBtn.style.display = 'none';
    }

    // Remove static h2 (now rendered dynamically in updateSidebar)
    const staticH2 = sidebar?.querySelector('.sidebar-content > h2');
    if (staticH2) staticH2.remove();

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

// Event delegation handler for deselect buttons in the drawer
const handleDrawerClick = (e) => {
    const deselectBtn = e.target.closest('.sidebar__deselect');
    if (!deselectBtn) return;

    const sectionId = deselectBtn.dataset.section;
    const stmtId = deselectBtn.dataset.id;
    if (sectionId && stmtId && window.deselectFromDrawer) {
        window.deselectFromDrawer(sectionId, stmtId);
    }
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

    // Update selections tab count (CHROME-05)
    const tabCount = document.getElementById('selections-tab-count');
    if (tabCount) {
        tabCount.textContent = totalSelections;
    }

    if (totalSelections === 0) {
        summaryContainer.innerHTML = `
            <p class="sidebar__empty">No selections yet. Check statements to add them to your job description.</p>
        `;
        return;
    }

    // Use ALL_SECTIONS_LABELS for all 8 sections (PITFALL: sectionOrder only has 5)
    const labels = window.ALL_SECTIONS_LABELS || {
        core_competencies: 'Core Competencies',
        key_activities: 'Key Activities',
        skills: 'Skills',
        abilities: 'Abilities',
        knowledge: 'Knowledge',
        effort: 'Effort',
        responsibility: 'Responsibility',
        working_conditions: 'Working Conditions'
    };

    let html = '<div class="sidebar__title-bar"><h2>Selection Summary</h2><span class="sidebar__subtitle">Your selected JD elements</span></div>';

    Object.keys(labels).forEach(sectionId => {
        const selectedIds = state.selections[sectionId] || [];
        if (selectedIds.length === 0) return;

        html += `<div class="sidebar__section">
            <h4 class="sidebar__section-title">${labels[sectionId]} (${selectedIds.length})</h4>
            <ul class="sidebar__list">`;

        selectedIds.forEach(stmtId => {
            const index = parseInt(stmtId.split('-').pop(), 10);
            let text = '';

            // PITFALL: core_competencies uses profile.reference_attributes.core_competencies[idx]
            if (sectionId === 'core_competencies') {
                const ccItems = profile.reference_attributes?.core_competencies || [];
                text = ccItems[index] || '';
            }
            // PITFALL: abilities/knowledge use filtered sub-array by source_attribute
            else if (sectionId === 'abilities' || sectionId === 'knowledge') {
                const sourceAttr = sectionId === 'abilities' ? 'Abilities' : 'Knowledge';
                const filtered = (profile.skills?.statements || []).filter(s => s.source_attribute === sourceAttr);
                text = filtered[index]?.text || '';
            } else {
                const sectionData = profile[sectionId];
                if (sectionData?.statements?.[index]) {
                    text = sectionData.statements[index].text;
                }
            }

            if (text) {
                html += `<li class="sidebar__item">
                    <span class="sidebar__item-text">${escapeHtmlSidebar(text)}</span>
                    <button class="sidebar__deselect" type="button"
                        data-section="${sectionId}" data-id="${stmtId}"
                        aria-label="Remove selection"
                        title="Remove from selections">
                        <i class="fas fa-times"></i>
                    </button>
                </li>`;
            }
        });

        html += '</ul></div>';
    });

    // Total count + Clear All footer
    html += `<div class="sidebar__footer">
        <span class="sidebar__total">Total Selected: <strong>${totalSelections}</strong></span>
        <button class="sidebar__clear-all" type="button" id="sidebar-clear-all">
            <i class="fas fa-trash-alt"></i> Clear All
        </button>
    </div>`;

    summaryContainer.innerHTML = html;

    // Wire deselect buttons via event delegation on summary container
    summaryContainer.addEventListener('click', handleDrawerClick);

    // Wire Clear All button
    const clearBtn = document.getElementById('sidebar-clear-all');
    if (clearBtn) {
        clearBtn.addEventListener('click', () => {
            if (window.clearAllSelections) {
                window.clearAllSelections();
            }
        });
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
