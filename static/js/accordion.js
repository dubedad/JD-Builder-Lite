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

// Category definitions from guide.csv - displayed beside section titles
const CATEGORY_DEFINITIONS = {
    'Work Activities': 'Work activities are general types of job behaviours occurring on multiple jobs. For each work activity statement a worker indicates the level of the activity that is required to perform a job.',
    'Skills': 'Skills are developed capacities that facilitate learning or the more rapid acquisition of knowledge. Skills can be thought of as the "how to" for accomplishing job tasks.',
    'Abilities': 'Abilities are enduring attributes of the individual that influence performance. Abilities are categorized according to the different kinds of behaviours they influence.',
    'Knowledge': 'Knowledge is organized sets of principles and facts applying in general domains. Knowledge describes what must be learned prior to performing on the job.',
    'Work Context': 'Work context describes the physical and social factors that influence the nature of work. For each work context element, a worker rates how often or to what extent the descriptor applies to the context of work.'
};

// NOC Minor Group (3-digit) to Icon mapping for specific occupations
const NOC_MINOR_GROUP_ICONS = {
    // Transport occupations (72x) - more specific than broad category
    '726': 'fa-plane',      // Air pilots, flight engineers, flying instructors
    '727': 'fa-ship',       // Marine/ship officers and crew
    '728': 'fa-train',      // Rail transport
    '721': 'fa-truck',      // Truck drivers, bus drivers
    '722': 'fa-truck',      // Heavy equipment operators
    // Construction trades
    '731': 'fa-hard-hat',   // Construction trades helpers
    '732': 'fa-hard-hat',   // Construction labourers
    // Health sub-categories
    '301': 'fa-user-md',    // Physicians, dentists
    '302': 'fa-user-nurse', // Nursing
    '311': 'fa-user-nurse', // Nursing coordinators
    '321': 'fa-stethoscope',// Medical technologists
    // Tech/IT
    '217': 'fa-laptop-code',// Computer and information systems
    '212': 'fa-laptop-code',// Software engineers, designers
};

// NOC Broad Category (1-digit) fallback mapping
const NOC_BROAD_ICONS = {
    0: 'fa-landmark',       // Legislative and senior management
    1: 'fa-briefcase',      // Business, finance and administration
    2: 'fa-atom',           // Natural and applied sciences
    3: 'fa-heartbeat',      // Health
    4: 'fa-graduation-cap', // Education, law, social, community, government
    5: 'fa-palette',        // Art, culture, recreation, sport
    6: 'fa-handshake',      // Sales and service
    7: 'fa-tools',          // Trades, transport, equipment operators (fallback)
    8: 'fa-tractor',        // Natural resources, agriculture
    9: 'fa-industry'        // Manufacturing and utilities
};

/**
 * Get icon class based on NOC code - checks minor group first, then broad category
 */
const getNocIcon = (nocCode) => {
    if (!nocCode) return 'fa-briefcase';

    // Remove decimal suffix (72600.01 -> 72600)
    const baseCode = nocCode.split('.')[0];

    // Try minor group (first 3 digits) for specific match
    const minorGroup = baseCode.substring(0, 3);
    if (NOC_MINOR_GROUP_ICONS[minorGroup]) {
        return NOC_MINOR_GROUP_ICONS[minorGroup];
    }

    // Fall back to broad category (first digit)
    const broadCategory = parseInt(baseCode.charAt(0), 10);
    return NOC_BROAD_ICONS[broadCategory] || 'fa-briefcase';
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

    // Set icon immediately based on NOC broad category (semantic, no API call)
    const iconClass = getNocIcon(profile.noc_code);
    iconEl.className = `fas ${iconClass}`;
    console.log('[DEBUG] Icon set from NOC category:', iconClass, 'for code:', profile.noc_code);

    // Show header
    header.classList.remove('hidden');

    // Extract main duties for description generation
    const mainDuties = (profile.key_activities?.statements || [])
        .filter(s => s.source_attribute === 'Main Duties')
        .map(s => s.text)
        .slice(0, 5);

    const leadStatement = profile.reference_attributes?.lead_statement || profile.title;

    // Fetch LLM description asynchronously (non-blocking)
    api.fetchOccupationDescription(profile.title, leadStatement, mainDuties)
        .then(descResult => {
            if (descResult.description) {
                descEl.textContent = descResult.description;
                console.log('[DEBUG] Description generated, length:', descResult.description.length);
            }
        })
        .catch(err => {
            console.warn('LLM description generation failed:', err);
            // Keep lead statement as fallback - graceful degradation
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

    // Also known as - OaSIS panel card format (matches OaSIS welcome page)
    // Display as panel with icon header and bullet list of job titles
    if (profile.example_titles?.length) {
        const titlesToShow = profile.example_titles.slice(0, 8);
        const hasMore = profile.example_titles.length > 8;

        html += `
            <div class="oasis-panel also-known-as-panel">
                <div class="oasis-panel__heading">
                    <span class="fas fa-project-diagram oasis-panel__icon"></span>
                    <h3 class="oasis-panel__title">Also known as</h3>
                </div>
                <div class="oasis-panel__body">
                    <ul class="aka-list">
                        ${titlesToShow.map(t => `<li class="aka-list__item">${escapeHtml(t)}</li>`).join('')}
                    </ul>
                    ${hasMore ? `<button class="aka-see-more btn btn-link" data-expanded="false">See more – Job titles (${profile.example_titles.length - 8} more)</button>` : ''}
                    ${hasMore ? `<ul class="aka-list aka-list--hidden">
                        ${profile.example_titles.slice(8).map(t => `<li class="aka-list__item">${escapeHtml(t)}</li>`).join('')}
                    </ul>` : ''}
                </div>
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

    // NOC Hierarchy - complete structure per NOC 2021 with Level column
    // Structure: Broad Category (1) → TEER → Major Group (2) → Sub-Major Group (3) → Minor Group (4) → Unit Group (5) → Labels (6) → Example Titles (7)
    if (hierarchy.broad_category_name || hierarchy.noc_code) {
        // Get Labels from profile (if available from Labels 2025 CSV)
        const labels = profile.labels || profile.noc_hierarchy?.labels || [];
        const exampleTitles = profile.example_titles || [];

        html += `
            <div class="tab-panel__section">
                <h3 class="tab-panel__section-title">NOC Hierarchy</h3>
                <table class="noc-hierarchy-table">
                    <thead>
                        <tr>
                            <th>Level</th>
                            <th>Type</th>
                            <th>Code</th>
                            <th>Name</th>
                        </tr>
                    </thead>
                    <tbody>
                        ${hierarchy.broad_category_name ? `
                        <tr>
                            <td class="noc-level">1</td>
                            <th>Broad Category</th>
                            <td class="noc-code">${hierarchy.broad_category}</td>
                            <td class="noc-name">${escapeHtml(hierarchy.broad_category_name)}</td>
                        </tr>` : ''}
                        ${hierarchy.teer_description ? `
                        <tr>
                            <td class="noc-level">-</td>
                            <th>TEER</th>
                            <td class="noc-code">${hierarchy.teer_category}</td>
                            <td class="noc-name">${escapeHtml(hierarchy.teer_description)}</td>
                        </tr>` : ''}
                        ${hierarchy.major_group ? `
                        <tr>
                            <td class="noc-level">2</td>
                            <th>Major Group</th>
                            <td class="noc-code">${hierarchy.major_group}</td>
                            <td class="noc-name">${hierarchy.major_group_name ? escapeHtml(hierarchy.major_group_name) : '-'}</td>
                        </tr>` : ''}
                        ${hierarchy.minor_group ? `
                        <tr>
                            <td class="noc-level">3</td>
                            <th>Sub-Major Group</th>
                            <td class="noc-code">${hierarchy.minor_group}</td>
                            <td class="noc-name">${hierarchy.minor_group_name ? escapeHtml(hierarchy.minor_group_name) : '-'}</td>
                        </tr>` : ''}
                        ${hierarchy.unit_group ? `
                        <tr>
                            <td class="noc-level">4</td>
                            <th>Minor Group</th>
                            <td class="noc-code">${hierarchy.unit_group}</td>
                            <td class="noc-name">${hierarchy.unit_group_name ? escapeHtml(hierarchy.unit_group_name) : '-'}</td>
                        </tr>` : ''}
                        ${hierarchy.noc_code ? `
                        <tr>
                            <td class="noc-level">5</td>
                            <th>Unit Group</th>
                            <td class="noc-code">${escapeHtml(hierarchy.noc_code)}</td>
                            <td class="noc-name">${profile.title ? escapeHtml(profile.title) : '-'}</td>
                        </tr>` : ''}
                        ${labels.length > 0 ? `
                        <tr>
                            <td class="noc-level">6</td>
                            <th>Labels</th>
                            <td class="noc-code">-</td>
                            <td class="noc-name">${labels.map(l => escapeHtml(l)).join(', ')}</td>
                        </tr>` : `
                        <tr>
                            <td class="noc-level">6</td>
                            <th>Labels</th>
                            <td class="noc-code">-</td>
                            <td class="noc-name"><em>Available in Labels 2025 v1.0</em></td>
                        </tr>`}
                        ${exampleTitles.length > 0 ? `
                        <tr>
                            <td class="noc-level">7</td>
                            <th>Example Titles</th>
                            <td class="noc-code">-</td>
                            <td class="noc-name">${exampleTitles.slice(0, 5).map(t => escapeHtml(t)).join(', ')}${exampleTitles.length > 5 ? '...' : ''}</td>
                        </tr>` : ''}
                    </tbody>
                </table>
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

        // Get category definition for section title
        const categoryDef = CATEGORY_DEFINITIONS[section.title] || '';
        const definitionHtml = categoryDef
            ? `<p class="tab-panel__section-definition">${escapeHtml(categoryDef)}</p>`
            : '';

        // Count how many are selected in this section
        const sectionSelectedCount = filtered.filter((stmt) => {
            const stmtId = `${sectionId}-${statements.indexOf(stmt)}`;
            return selectedIds.includes(stmtId);
        }).length;
        const allSelected = sectionSelectedCount === filtered.length && filtered.length > 0;

        html += `
            <div class="tab-panel__section" data-section-id="${sectionId}">
                <div class="tab-panel__section-header">
                    <div class="tab-panel__section-title-row">
                        <label class="select-all-label" title="Select/deselect all statements in this section">
                            <input type="checkbox" class="select-all-checkbox"
                                   data-section="${sectionId}"
                                   ${allSelected ? 'checked' : ''}>
                            <span class="select-all-text">Select All</span>
                        </label>
                        <h3 class="tab-panel__section-title">${section.title} (${filtered.length})</h3>
                    </div>
                    <button class="style-selected-btn"
                            onclick="styleSelectedStatements('${sectionId}')"
                            title="Generate styled versions of selected statements">
                        <i class="fas fa-magic"></i> Style Selected
                    </button>
                </div>
                ${definitionHtml}
                <ul class="tab-panel__list jd-section__list">
        `;

        filtered.forEach((stmt, idx) => {
            const stmtId = `${sectionId}-${statements.indexOf(stmt)}`;
            const isSelected = selectedIds.includes(stmtId);
            const proficiencyHtml = stmt.proficiency ? renderProficiency(stmt.proficiency) : '';

            // Build description HTML if description exists (from guide.csv)
            const descriptionHtml = stmt.description
                ? `<span class="statement__description">${escapeHtml(stmt.description)}</span>`
                : '';

            // Build styled statement container HTML (Phase 12 - dual-format display)
            const styledContainerHtml = window.createStyledStatementContainer
                ? window.createStyledStatementContainer(stmtId, sectionId)
                : '';

            // Hide redundant provenance label when source matches section header (S2-01)
            // Keep labels on Effort/Responsibility tabs (mixed work context dimensions)
            const sourceRedundant = (stmt.source_attribute || '') === section.title;
            const sourceHtml = sourceRedundant
                ? ''
                : `<span class="statement__source">from ${escapeHtml(stmt.source_attribute || 'Unknown')}</span>`;

            html += `
                <li class="statement tab-panel__item${isSelected ? ' statement--selected' : ''}" data-id="${stmtId}">
                    <label class="statement__label">
                        <input type="checkbox" class="statement__checkbox"
                               data-section="${sectionId}"
                               data-id="${stmtId}"
                               ${isSelected ? 'checked' : ''}>
                        <span class="statement__content">
                            <span class="statement__text">${escapeHtml(stmt.text)}</span>
                            ${descriptionHtml}
                            ${sourceHtml}
                        </span>
                        ${proficiencyHtml}
                    </label>
                    ${styledContainerHtml}
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

const renderOtherJobInfoContent = (profile) => {
    const otherInfo = profile.other_job_info || {};
    const ref = profile.reference_attributes || {};
    let html = '';

    // Employment Requirements section
    if (otherInfo.employment_requirements?.length) {
        html += `
            <div class="oasis-panel">
                <div class="oasis-panel__heading">
                    <span class="fas fa-graduation-cap oasis-panel__icon"></span>
                    <h3 class="oasis-panel__title">Employment Requirements</h3>
                </div>
                <div class="oasis-panel__body">
                    <ul class="other-info-list">
                        ${otherInfo.employment_requirements.map(r => `<li class="other-info-list__item">${escapeHtml(r)}</li>`).join('')}
                    </ul>
                </div>
            </div>
        `;
    }

    // Workplaces/Employers section
    if (otherInfo.workplaces?.length) {
        html += `
            <div class="oasis-panel">
                <div class="oasis-panel__heading">
                    <span class="fas fa-building oasis-panel__icon"></span>
                    <h3 class="oasis-panel__title">Workplaces & Employers</h3>
                </div>
                <div class="oasis-panel__body">
                    <ul class="other-info-list other-info-list--inline">
                        ${otherInfo.workplaces.map(w => `<li class="other-info-list__item other-info-list__item--tag">${escapeHtml(w)}</li>`).join('')}
                    </ul>
                </div>
            </div>
        `;
    }

    // Interests (Holland Codes) section
    if (otherInfo.interests?.length) {
        html += `
            <div class="oasis-panel">
                <div class="oasis-panel__heading">
                    <span class="fas fa-compass oasis-panel__icon"></span>
                    <h3 class="oasis-panel__title">Interests (Holland Codes)</h3>
                </div>
                <div class="oasis-panel__body">
                    <div class="holland-codes">
                        ${otherInfo.interests.map(i => `
                            <div class="holland-code">
                                <span class="holland-code__badge holland-code__badge--${i.code.toLowerCase()}">${escapeHtml(i.code)}</span>
                                <div class="holland-code__content">
                                    <span class="holland-code__title">${escapeHtml(i.title)}</span>
                                    <span class="holland-code__rank">#${i.rank}</span>
                                    <p class="holland-code__description">${escapeHtml(i.description)}</p>
                                </div>
                            </div>
                        `).join('')}
                    </div>
                </div>
            </div>
        `;
    }

    // Personal Attributes section
    if (otherInfo.personal_attributes?.length) {
        html += `
            <div class="oasis-panel">
                <div class="oasis-panel__heading">
                    <span class="fas fa-user-check oasis-panel__icon"></span>
                    <h3 class="oasis-panel__title">Personal Attributes</h3>
                </div>
                <div class="oasis-panel__body">
                    <div class="attributes-grid">
                        ${otherInfo.personal_attributes.map(a => `
                            <div class="attribute-item">
                                <span class="attribute-item__name">${escapeHtml(a.name)}</span>
                                <span class="attribute-item__level">${renderAttributeLevel(a.level)}</span>
                            </div>
                        `).join('')}
                    </div>
                </div>
            </div>
        `;
    }

    // Exclusions section
    if (otherInfo.exclusions?.length) {
        html += `
            <div class="oasis-panel">
                <div class="oasis-panel__heading">
                    <span class="fas fa-times-circle oasis-panel__icon"></span>
                    <h3 class="oasis-panel__title">Exclusions</h3>
                </div>
                <div class="oasis-panel__body">
                    <p class="exclusions-note">The following job titles are classified elsewhere:</p>
                    <ul class="exclusions-list">
                        ${otherInfo.exclusions.map(e => `
                            <li class="exclusions-list__item">
                                <span class="exclusions-list__title">${escapeHtml(e.title)}</span>
                                <span class="exclusions-list__code">(${escapeHtml(e.code)})</span>
                            </li>
                        `).join('')}
                    </ul>
                </div>
            </div>
        `;
    }

    // Work Context from parquet - Responsibility
    if (otherInfo.work_context_responsibility?.length) {
        html += `
            <div class="oasis-panel">
                <div class="oasis-panel__heading">
                    <span class="fas fa-clipboard-check oasis-panel__icon"></span>
                    <h3 class="oasis-panel__title">Work Context - Decision & Responsibility</h3>
                </div>
                <div class="oasis-panel__body">
                    <div class="work-context-grid">
                        ${otherInfo.work_context_responsibility.map(wc => `
                            <div class="work-context-item">
                                <span class="work-context-item__name">${escapeHtml(wc.name)}</span>
                                <span class="work-context-item__level">${renderAttributeLevel(wc.level)}</span>
                            </div>
                        `).join('')}
                    </div>
                </div>
            </div>
        `;
    }

    // Work Context from parquet - Effort
    if (otherInfo.work_context_effort?.length) {
        html += `
            <div class="oasis-panel">
                <div class="oasis-panel__heading">
                    <span class="fas fa-running oasis-panel__icon"></span>
                    <h3 class="oasis-panel__title">Work Context - Physical Effort</h3>
                </div>
                <div class="oasis-panel__body">
                    <div class="work-context-grid">
                        ${otherInfo.work_context_effort.map(wc => `
                            <div class="work-context-item">
                                <span class="work-context-item__name">${escapeHtml(wc.name)}</span>
                                <span class="work-context-item__level">${renderAttributeLevel(wc.level)}</span>
                            </div>
                        `).join('')}
                    </div>
                </div>
            </div>
        `;
    }

    // Data Sources section
    html += `
        <div class="oasis-panel">
            <div class="oasis-panel__heading">
                <span class="fas fa-database oasis-panel__icon"></span>
                <h3 class="oasis-panel__title">Data Sources</h3>
            </div>
            <div class="oasis-panel__body">
                <p class="tab-panel__text">
                    This occupational profile is sourced from ESDC OaSIS 2025 NOC v1.0 (Published: 2024-11-15)
                    and enriched with O*NET 27.2 Database descriptors from USDOL/ETA.
                </p>
                <p class="tab-panel__text">
                    <strong>NOC Code:</strong> ${profile.noc_code || 'N/A'}<br>
                    <strong>Profile URL:</strong> <a href="${profile.metadata?.profile_url || '#'}" target="_blank" rel="noopener noreferrer">View on OaSIS</a>
                </p>
            </div>
        </div>
    `;

    return html || '<p>No additional job information available.</p>';
};

const renderAttributeLevel = (level) => {
    const max = 5;
    const filledCircles = '<span class="level-filled">●</span>'.repeat(level);
    const emptyCircles = '<span class="level-empty">○</span>'.repeat(max - level);
    return `<span class="attribute-level">${filledCircles}${emptyCircles}</span>`;
};

const renderTabContent = (profile) => {
    const state = store.getState();

    // Overview tab - special handling for reference data
    const overviewPanel = document.getElementById('panel-overview');
    if (overviewPanel) {
        overviewPanel.innerHTML = renderOverviewContent(profile);

        // Attach "See more" button handler for Also Known As section
        const seeMoreBtn = overviewPanel.querySelector('.aka-see-more');
        if (seeMoreBtn) {
            seeMoreBtn.addEventListener('click', function() {
                const hiddenList = overviewPanel.querySelector('.aka-list--hidden');
                const isExpanded = this.getAttribute('data-expanded') === 'true';

                if (hiddenList) {
                    hiddenList.classList.toggle('visible', !isExpanded);
                }
                this.setAttribute('data-expanded', !isExpanded);
                this.textContent = isExpanded
                    ? `See more – Job titles (${profile.example_titles.length - 8} more)`
                    : 'See less – Job titles';
            });
        }
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

    // Effort tab - with Work Context definition
    const effortPanel = document.getElementById('panel-effort');
    if (effortPanel) {
        const effortStatements = profile.effort?.statements || [];
        const workContextDef = CATEGORY_DEFINITIONS['Work Context'];
        const effortSelectedCount = effortStatements.filter((_, idx) =>
            (state.selections.effort || []).includes(`effort-${idx}`)
        ).length;
        const effortAllSelected = effortSelectedCount === effortStatements.length && effortStatements.length > 0;

        let effortHtml = `
            <div class="tab-panel__section" data-section-id="effort">
                <div class="tab-panel__section-header">
                    <div class="tab-panel__section-title-row">
                        <label class="select-all-label" title="Select/deselect all statements in this section">
                            <input type="checkbox" class="select-all-checkbox"
                                   data-section="effort"
                                   ${effortAllSelected ? 'checked' : ''}>
                            <span class="select-all-text">Select All</span>
                        </label>
                        <h3 class="tab-panel__section-title">Effort (${effortStatements.length})</h3>
                    </div>
                    <button class="style-selected-btn"
                            onclick="styleSelectedStatements('effort')"
                            title="Generate styled versions of selected statements">
                        <i class="fas fa-magic"></i> Style Selected
                    </button>
                </div>
                <p class="tab-panel__section-definition">${escapeHtml(workContextDef)}</p>
        `;

        if (effortStatements.length > 0) {
            effortHtml += '<ul class="tab-panel__list jd-section__list">';
            effortStatements.forEach((stmt, idx) => {
                const stmtId = `effort-${idx}`;
                const isSelected = (state.selections.effort || []).includes(stmtId);
                const proficiencyHtml = stmt.proficiency ? renderProficiency(stmt.proficiency) : '';
                const descriptionHtml = stmt.description ? `<span class="statement__description">${escapeHtml(stmt.description)}</span>` : '';
                const styledContainerHtml = window.createStyledStatementContainer
                    ? window.createStyledStatementContainer(stmtId, 'effort')
                    : '';

                effortHtml += `
                    <li class="statement tab-panel__item${isSelected ? ' statement--selected' : ''}" data-id="${stmtId}">
                        <label class="statement__label">
                            <input type="checkbox" class="statement__checkbox"
                                   data-section="effort"
                                   data-id="${stmtId}"
                                   ${isSelected ? 'checked' : ''}>
                            <span class="statement__content">
                                <span class="statement__text">${escapeHtml(stmt.text)}</span>
                                ${descriptionHtml}
                                <span class="statement__source">from ${escapeHtml(stmt.source_attribute || 'Work Context')}</span>
                            </span>
                            ${proficiencyHtml}
                        </label>
                        ${styledContainerHtml}
                    </li>
                `;
            });
            effortHtml += '</ul>';
        } else {
            effortHtml += '<p class="tab-panel__empty">No effort-related Work Context items available for this occupation.</p>';
        }

        effortHtml += '</div>';
        effortPanel.innerHTML = effortHtml;
    }

    // Responsibility tab - with Work Context definition
    const responsibilityPanel = document.getElementById('panel-responsibility');
    if (responsibilityPanel) {
        const respStatements = profile.responsibility?.statements || [];
        const workContextDef = CATEGORY_DEFINITIONS['Work Context'];
        const respSelectedCount = respStatements.filter((_, idx) =>
            (state.selections.responsibility || []).includes(`responsibility-${idx}`)
        ).length;
        const respAllSelected = respSelectedCount === respStatements.length && respStatements.length > 0;

        let respHtml = `
            <div class="tab-panel__section" data-section-id="responsibility">
                <div class="tab-panel__section-header">
                    <div class="tab-panel__section-title-row">
                        <label class="select-all-label" title="Select/deselect all statements in this section">
                            <input type="checkbox" class="select-all-checkbox"
                                   data-section="responsibility"
                                   ${respAllSelected ? 'checked' : ''}>
                            <span class="select-all-text">Select All</span>
                        </label>
                        <h3 class="tab-panel__section-title">Responsibility (${respStatements.length})</h3>
                    </div>
                    <button class="style-selected-btn"
                            onclick="styleSelectedStatements('responsibility')"
                            title="Generate styled versions of selected statements">
                        <i class="fas fa-magic"></i> Style Selected
                    </button>
                </div>
                <p class="tab-panel__section-definition">${escapeHtml(workContextDef)}</p>
        `;

        if (respStatements.length > 0) {
            respHtml += '<ul class="tab-panel__list jd-section__list">';
            respStatements.forEach((stmt, idx) => {
                const stmtId = `responsibility-${idx}`;
                const isSelected = (state.selections.responsibility || []).includes(stmtId);
                const proficiencyHtml = stmt.proficiency ? renderProficiency(stmt.proficiency) : '';
                const descriptionHtml = stmt.description ? `<span class="statement__description">${escapeHtml(stmt.description)}</span>` : '';
                const styledContainerHtml = window.createStyledStatementContainer
                    ? window.createStyledStatementContainer(stmtId, 'responsibility')
                    : '';

                respHtml += `
                    <li class="statement tab-panel__item${isSelected ? ' statement--selected' : ''}" data-id="${stmtId}">
                        <label class="statement__label">
                            <input type="checkbox" class="statement__checkbox"
                                   data-section="responsibility"
                                   data-id="${stmtId}"
                                   ${isSelected ? 'checked' : ''}>
                            <span class="statement__content">
                                <span class="statement__text">${escapeHtml(stmt.text)}</span>
                                ${descriptionHtml}
                                <span class="statement__source">from ${escapeHtml(stmt.source_attribute || 'Work Context')}</span>
                            </span>
                            ${proficiencyHtml}
                        </label>
                        ${styledContainerHtml}
                    </li>
                `;
            });
            respHtml += '</ul>';
        } else {
            respHtml += '<p class="tab-panel__empty">No responsibility-related Work Context items available for this occupation.</p>';
        }

        respHtml += '</div>';
        responsibilityPanel.innerHTML = respHtml;
    }

    // Career tab
    const careerPanel = document.getElementById('panel-career');
    if (careerPanel) {
        careerPanel.innerHTML = renderCareerContent(profile);
    }

    // Other Job Information tab
    const otherPanel = document.getElementById('panel-other');
    if (otherPanel) {
        otherPanel.innerHTML = renderOtherJobInfoContent(profile);
    }

    // Show tabs container
    const tabsContainer = document.getElementById('profile-tabs-container');
    if (tabsContainer) {
        tabsContainer.classList.remove('hidden');
    }

    // Initialize tab controller (reset if exists to handle new profile load)
    const tablist = document.querySelector('.tabs-bar[role="tablist"]');
    if (tablist) {
        // Always recreate TabController for fresh initialization
        window.tabController = new TabController(tablist);
        console.log('[DEBUG] TabController initialized with', window.tabController.tabs.length, 'tabs');
    }

    // Debug: log what content was rendered
    console.log('[DEBUG] Tab content rendered:');
    console.log('  - Overview:', overviewPanel?.innerHTML?.length || 0, 'chars');
    console.log('  - Activities:', activitiesPanel?.innerHTML?.length || 0, 'chars');
    console.log('  - Skills:', skillsPanel?.innerHTML?.length || 0, 'chars');
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
