// Accordion rendering for JD Element sections
const JD_ELEMENT_LABELS = {
    key_activities: 'Key Activities',
    skills: 'Skills',
    effort: 'Effort',
    responsibility: 'Responsibility',
    working_conditions: 'Working Conditions'
};

const PROFICIENCY_LABELS = {
    1: 'Basic Level',
    2: 'Low Level',
    3: 'Medium Level',
    4: 'High Level',
    5: 'Highest Level'
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

        // Build proficiency HTML if enriched data present
        const proficiencyHtml = stmt.proficiency ? renderProficiency(stmt.proficiency) : '';

        // Build dimension badge HTML for Work Context statements
        const dimensionBadgeHtml = stmt.dimension_type ? renderDimensionBadge(stmt.dimension_type) : '';

        // Build source text with optional dimension badge
        const sourceText = stmt.source_attribute || 'Unknown source';

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

const renderProficiency = (proficiency) => {
    // Handle missing or invalid proficiency
    if (!proficiency || proficiency.level === null || proficiency.level === undefined) {
        return `
            <div class="proficiency-rating no-rating" aria-label="No rated level">
                <span class="rating-label">No rating</span>
            </div>
        `;
    }

    const level = proficiency.level;
    const max = proficiency.max || 5;
    const label = proficiency.label || PROFICIENCY_LABELS[level] || `Level ${level}`;

    // Build circles string: filled circles then empty circles
    const filledCircles = '<span class="filled">●</span>'.repeat(level);
    const emptyCircles = '<span class="empty">○</span>'.repeat(max - level);

    return `
        <div class="proficiency-rating"
             aria-label="Level ${level}"
             data-full-label="${level} - ${escapeHtml(label)}"
             tabindex="0">
            <span class="rating-circles" aria-hidden="true">${filledCircles}${emptyCircles}</span>
            <span class="rating-label">L${level}</span>
        </div>
    `;
};

const renderDimensionBadge = (dimensionType) => {
    if (!dimensionType) return '';
    return `<span class="dimension-badge">${escapeHtml(dimensionType)}</span>`;
};

// Export for other modules
window.renderAccordions = renderAccordions;
window.updateSelectionCount = updateSelectionCount;
window.JD_ELEMENT_LABELS = JD_ELEMENT_LABELS;
window.renderProficiency = renderProficiency;
window.renderDimensionBadge = renderDimensionBadge;
window.PROFICIENCY_LABELS = PROFICIENCY_LABELS;
