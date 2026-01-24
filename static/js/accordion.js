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

const renderProfileHeader = async (profile) => {
    const header = document.getElementById('profile-header');
    const titleEl = document.getElementById('profile-title');
    const badgeEl = document.getElementById('profile-code-badge');
    const leadEl = document.getElementById('profile-lead-statement');
    const descEl = document.getElementById('profile-description');
    const iconEl = document.getElementById('profile-icon');
    const linkEl = document.getElementById('profile-link');
    const timestampEl = document.getElementById('profile-timestamp');

    // Set static content immediately
    titleEl.textContent = profile.title;
    badgeEl.textContent = profile.noc_code;
    leadEl.textContent = profile.reference_attributes?.lead_statement || '';
    linkEl.href = profile.metadata?.profile_url || '#';
    timestampEl.textContent = new Date().toLocaleDateString();

    // Show header
    header.classList.remove('hidden');

    // Extract main duties for description generation
    const mainDuties = (profile.key_activities?.statements || [])
        .filter(s => s.source_attribute === 'Main Duties')
        .map(s => s.text)
        .slice(0, 5);

    const leadStatement = profile.reference_attributes?.lead_statement || profile.title;

    // Fetch icon and description in parallel (non-blocking)
    Promise.all([
        api.fetchOccupationIcon(profile.title, leadStatement),
        api.fetchOccupationDescription(profile.title, leadStatement, mainDuties)
    ]).then(([iconResult, descResult]) => {
        // Update icon
        const iconClass = iconResult.icon_class || 'fa-briefcase';
        iconEl.className = `fas ${iconClass}`;

        // Update description
        if (descResult.description) {
            descEl.textContent = descResult.description;
        }
    }).catch(err => {
        console.warn('LLM enrichment failed:', err);
        // Keep defaults - graceful degradation
    });
};

const TAB_CONFIG = {
    overview: {
        sections: [
            { key: 'also_known_as', title: 'Also Known As', source: 'reference_attributes.example_titles' },
            { key: 'core_competencies', title: 'Core Competencies', source: 'reference_attributes.core_competencies' },
            { key: 'noc_hierarchy', title: 'NOC Hierarchy', source: 'noc_hierarchy' }
        ]
    },
    activities: {
        sections: [
            { key: 'main_duties', title: 'Main Duties', filter: s => s.source_attribute === 'Main Duties' },
            { key: 'work_activities', title: 'Work Activities', filter: s => s.source_attribute === 'Work Activities' }
        ],
        dataKey: 'key_activities'
    },
    skills: {
        sections: [
            { key: 'skills', title: 'Skills', filter: s => s.source_attribute === 'Skills' },
            { key: 'abilities', title: 'Abilities', filter: s => s.source_attribute === 'Abilities' },
            { key: 'knowledge', title: 'Knowledge', filter: s => s.source_attribute === 'Knowledge' }
        ],
        dataKey: 'skills'
    },
    effort: {
        sections: [
            { key: 'effort_context', title: 'Work Context - Effort' }
        ],
        dataKey: 'effort'
    },
    responsibility: {
        sections: [
            { key: 'responsibility_context', title: 'Work Context - Responsibility' }
        ],
        dataKey: 'responsibility'
    },
    career: {
        sections: [
            { key: 'career_info', title: 'Career Progression & Mobility' }
        ],
        source: 'reference_attributes.additional_info'
    }
};

const renderOverviewContent = (profile) => {
    const ref = profile.reference_attributes || {};
    const hierarchy = profile.noc_hierarchy || {};

    let html = '';

    // Example titles / Also known as
    if (ref.example_titles?.length) {
        html += `
            <div class="tab-panel__section">
                <h3 class="tab-panel__section-title">Also Known As</h3>
                <p>${ref.example_titles.join(', ')}</p>
            </div>
        `;
    }

    // Core competencies
    if (ref.core_competencies?.length) {
        html += `
            <div class="tab-panel__section">
                <h3 class="tab-panel__section-title">Core Competencies</h3>
                <ul class="tab-panel__list">
                    ${ref.core_competencies.map(c => `<li class="tab-panel__item">${escapeHtml(c)}</li>`).join('')}
                </ul>
            </div>
        `;
    }

    // NOC Hierarchy
    if (hierarchy.broad_category || hierarchy.teer) {
        html += `
            <div class="tab-panel__section">
                <h3 class="tab-panel__section-title">NOC Hierarchy</h3>
                <dl class="noc-hierarchy-list">
                    ${hierarchy.broad_category ? `<dt>Broad Category</dt><dd>${escapeHtml(hierarchy.broad_category)}</dd>` : ''}
                    ${hierarchy.teer ? `<dt>TEER</dt><dd>${escapeHtml(hierarchy.teer)}</dd>` : ''}
                    ${hierarchy.major_group ? `<dt>Major Group</dt><dd>${escapeHtml(hierarchy.major_group)}</dd>` : ''}
                    ${hierarchy.minor_group ? `<dt>Minor Group</dt><dd>${escapeHtml(hierarchy.minor_group)}</dd>` : ''}
                </dl>
            </div>
        `;
    }

    return html || '<p>No overview information available.</p>';
};

const renderStatementsPanel = (statements, sections, sectionId, selectedIds) => {
    let html = '';

    sections.forEach(section => {
        const filtered = section.filter
            ? statements.filter(section.filter)
            : statements;

        if (filtered.length === 0) return;

        html += `
            <div class="tab-panel__section">
                <h3 class="tab-panel__section-title">${section.title}</h3>
                <ul class="tab-panel__list jd-section__list">
        `;

        filtered.forEach((stmt, idx) => {
            const stmtId = `${sectionId}-${statements.indexOf(stmt)}`;
            const isSelected = selectedIds.includes(stmtId);
            const proficiencyHtml = stmt.proficiency ? renderProficiency(stmt.proficiency) : '';

            html += `
                <li class="statement tab-panel__item${isSelected ? ' statement--selected' : ''}" data-id="${stmtId}">
                    <label class="statement__label">
                        <input type="checkbox" class="statement__checkbox"
                               data-section="${sectionId}"
                               data-id="${stmtId}"
                               ${isSelected ? 'checked' : ''}>
                        <span class="statement__content">
                            <span class="statement__text">${escapeHtml(stmt.text)}</span>
                            <span class="statement__source">from ${escapeHtml(stmt.source_attribute || 'Unknown')}</span>
                        </span>
                        ${proficiencyHtml}
                    </label>
                </li>
            `;
        });

        html += '</ul></div>';
    });

    return html || '<p>No items available.</p>';
};

const renderCareerContent = (profile) => {
    const additionalInfo = profile.reference_attributes?.additional_info;
    if (!additionalInfo) {
        return '<p>No career progression information available.</p>';
    }

    return `
        <div class="tab-panel__section">
            <h3 class="tab-panel__section-title">Feeder Group Mobility & Career Progression</h3>
            <div class="career-content">${escapeHtml(additionalInfo)}</div>
        </div>
    `;
};

const renderTabContent = (profile) => {
    const state = store.getState();

    // Overview tab - special handling for reference data
    const overviewPanel = document.getElementById('panel-overview');
    if (overviewPanel) {
        overviewPanel.innerHTML = renderOverviewContent(profile);
    }

    // Key Activities tab
    const activitiesPanel = document.getElementById('panel-activities');
    if (activitiesPanel) {
        activitiesPanel.innerHTML = renderStatementsPanel(
            profile.key_activities?.statements || [],
            TAB_CONFIG.activities.sections,
            'key_activities',
            state.selections.key_activities || []
        );
    }

    // Skills tab
    const skillsPanel = document.getElementById('panel-skills');
    if (skillsPanel) {
        skillsPanel.innerHTML = renderStatementsPanel(
            profile.skills?.statements || [],
            TAB_CONFIG.skills.sections,
            'skills',
            state.selections.skills || []
        );
    }

    // Effort tab
    const effortPanel = document.getElementById('panel-effort');
    if (effortPanel) {
        effortPanel.innerHTML = renderStatementsPanel(
            profile.effort?.statements || [],
            [{ key: 'effort', title: 'Work Context - Effort' }],
            'effort',
            state.selections.effort || []
        );
    }

    // Responsibility tab
    const responsibilityPanel = document.getElementById('panel-responsibility');
    if (responsibilityPanel) {
        responsibilityPanel.innerHTML = renderStatementsPanel(
            profile.responsibility?.statements || [],
            [{ key: 'responsibility', title: 'Work Context - Responsibility' }],
            'responsibility',
            state.selections.responsibility || []
        );
    }

    // Career tab
    const careerPanel = document.getElementById('panel-career');
    if (careerPanel) {
        careerPanel.innerHTML = renderCareerContent(profile);
    }

    // Show tabs container
    const tabsContainer = document.getElementById('profile-tabs-container');
    if (tabsContainer) {
        tabsContainer.classList.remove('hidden');
    }

    // Initialize tab controller
    const tablist = document.querySelector('[role="tablist"]');
    if (tablist && !window.tabController) {
        window.tabController = new TabController(tablist);
    }
};

const renderAccordions = (profile) => {
    // Render profile header with LLM enrichment
    renderProfileHeader(profile);

    // Render tab content instead of accordions
    renderTabContent(profile);

    // Hide old accordion container
    const accordionContainer = document.querySelector('.jd-sections');
    if (accordionContainer) {
        accordionContainer.classList.add('hidden');
    }
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

// WCAG 2.1 SC 1.4.13: Dismiss tooltips with Escape key
document.addEventListener('keydown', (e) => {
    if (e.key === 'Escape') {
        // Remove focus from any proficiency rating to hide tooltip
        const focused = document.activeElement;
        if (focused && focused.classList.contains('proficiency-rating')) {
            focused.blur();
        }
    }
});

// Export for other modules
window.renderProfileHeader = renderProfileHeader;
window.renderAccordions = renderAccordions;
window.renderTabContent = renderTabContent;
window.updateSelectionCount = updateSelectionCount;
window.JD_ELEMENT_LABELS = JD_ELEMENT_LABELS;
window.renderProficiency = renderProficiency;
window.renderDimensionBadge = renderDimensionBadge;
window.PROFICIENCY_LABELS = PROFICIENCY_LABELS;
