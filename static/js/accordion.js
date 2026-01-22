// Accordion rendering for JD Element sections
const JD_ELEMENT_LABELS = {
    key_activities: 'Key Activities',
    skills: 'Skills',
    effort: 'Effort',
    responsibility: 'Responsibility',
    working_conditions: 'Working Conditions'
};

const renderAccordions = (profile) => {
    const container = document.querySelector('.jd-sections');
    const state = store.getState();

    // Clear existing content
    container.innerHTML = '';

    // Render in order from state
    state.sectionOrder.forEach(sectionId => {
        const data = profile[sectionId];
        if (!data || !data.statements) return;

        const section = createAccordionSection(sectionId, data.statements, state.selections[sectionId] || []);
        container.appendChild(section);
    });

    // Initialize SortableJS on container
    initSortable(container);
};

const createAccordionSection = (sectionId, statements, selectedIds) => {
    const details = document.createElement('details');
    details.className = 'jd-section';
    details.dataset.sectionId = sectionId;
    details.setAttribute('name', 'jd-accordion'); // Exclusive accordion behavior

    const summary = document.createElement('summary');
    summary.className = 'jd-section__header';
    summary.innerHTML = `
        <span class="jd-section__drag-handle" title="Drag to reorder">&#x2630;</span>
        <span class="jd-section__title">${JD_ELEMENT_LABELS[sectionId]}</span>
        <span class="jd-section__count">(${selectedIds.length} selected)</span>
    `;

    const content = document.createElement('div');
    content.className = 'jd-section__content';

    // Search filter input
    const searchInput = document.createElement('input');
    searchInput.type = 'search';
    searchInput.className = 'jd-section__search';
    searchInput.placeholder = 'Filter statements...';
    searchInput.dataset.sectionId = sectionId;
    content.appendChild(searchInput);

    // Statements list
    const list = document.createElement('ul');
    list.className = 'jd-section__list';

    statements.forEach((stmt, index) => {
        const stmtId = `${sectionId}-${index}`;
        const isSelected = selectedIds.includes(stmtId);

        const li = document.createElement('li');
        li.className = 'statement' + (isSelected ? ' statement--selected' : '');
        li.dataset.id = stmtId;

        li.innerHTML = `
            <label class="statement__label">
                <input type="checkbox" class="statement__checkbox"
                       data-section="${sectionId}"
                       data-id="${stmtId}"
                       ${isSelected ? 'checked' : ''}>
                <span class="statement__text">${escapeHtml(stmt.text)}</span>
                <span class="statement__source">from ${escapeHtml(stmt.source_attribute)}</span>
            </label>
        `;

        list.appendChild(li);
    });

    content.appendChild(list);
    details.appendChild(summary);
    details.appendChild(content);

    return details;
};

const initSortable = (container) => {
    if (window.sortableInstance) {
        window.sortableInstance.destroy();
    }

    window.sortableInstance = new Sortable(container, {
        animation: 150,
        ghostClass: 'jd-section--dragging',
        handle: '.jd-section__drag-handle',
        onEnd: (evt) => {
            // Update state with new order
            const newOrder = Array.from(container.children)
                .map(el => el.dataset.sectionId);
            store.getState().sectionOrder = newOrder;
        }
    });
};

const updateSelectionCount = (sectionId) => {
    const section = document.querySelector(`[data-section-id="${sectionId}"]`);
    if (!section) return;

    const state = store.getState();
    const count = (state.selections[sectionId] || []).length;
    const countEl = section.querySelector('.jd-section__count');
    if (countEl) {
        countEl.textContent = `(${count} selected)`;
    }
};

const escapeHtml = (text) => {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
};

// Export for other modules
window.renderAccordions = renderAccordions;
window.updateSelectionCount = updateSelectionCount;
window.JD_ELEMENT_LABELS = JD_ELEMENT_LABELS;
