// Accordion rendering for JD Element sections
const JD_ELEMENT_LABELS = {
    key_activities: 'Key Activities',
    skills: 'Skills',
    effort: 'Effort',
    responsibility: 'Responsibility',
    working_conditions: 'Working Conditions'
};

// All 8 sections for sidebar/drawer (PITFALL: sectionOrder only has 5 — drawer needs all 8)
const ALL_SECTIONS_LABELS = {
    core_competencies: 'Core Competencies',
    key_activities: 'Key Activities',
    skills: 'Skills',
    abilities: 'Abilities',
    knowledge: 'Knowledge',
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

// v5.1: Level badge color mapping for level-grouped tabs (Abilities, Knowledge, Effort, Responsibility)
const LEVEL_BADGE_COLORS = {
    5: { label: 'Level 5', cssClass: 'level-badge--5' },
    4: { label: 'Level 4', cssClass: 'level-badge--4' },
    3: { label: 'Level 3', cssClass: 'level-badge--3' },
    2: { label: 'Level 2', cssClass: 'level-badge--2' },
    1: { label: 'Level 1', cssClass: 'level-badge--1' },
    0: { label: 'Unrated', cssClass: 'level-badge--unrated' }
};

// Category definitions from guide.csv - displayed beside section titles
const CATEGORY_DEFINITIONS = {
    'Work Activities': 'Work activities are general types of job behaviours occurring on multiple jobs. For each work activity statement a worker indicates the level of the activity that is required to perform a job.',
    'Skills': 'Skills are developed capacities that facilitate learning or the more rapid acquisition of knowledge. Skills can be thought of as the "how to" for accomplishing job tasks.',
    'Abilities': 'Abilities are enduring attributes of the individual that influence performance. Abilities are categorized according to the different kinds of behaviours they influence.',
    'Knowledge': 'Knowledge is organized sets of principles and facts applying in general domains. Knowledge describes what must be learned prior to performing on the job.',
    'Work Context': 'Work context describes the physical and social factors that influence the nature of work. For each work context element, a worker rates how often or to what extent the descriptor applies to the context of work.'
};

// Section descriptions for v5.1 description boxes (one per tab)
const SECTION_DESCRIPTIONS = {
    overview: {
        icon: 'fa-eye',
        title: 'Overview',
        text: 'The Overview provides a high-level summary of the occupation, including the lead statement, definition, and key characteristics from NOC and OaSIS data sources.'
    },
    core_competencies: {
        icon: 'fa-star',
        title: 'Core Competencies',
        text: 'Core competencies represent the fundamental capabilities and personal attributes that are essential for effective performance in this occupation. These include behavioral competencies, work styles, and professional values.'
    },
    activities: {
        icon: 'fa-list-check',
        title: 'Key Activities',
        text: 'Key activities are the main duties and tasks performed in this occupation. They describe what workers in this role typically do on a regular basis.'
    },
    skills: {
        icon: 'fa-lightbulb',
        title: 'Skills (OaSIS Category F)',
        text: '<strong>Developed capabilities</strong> <em>that an individual must have to be effective in a job, role, function, task or duty. Skills are organized into: Foundational Skills (verbal, reading/writing, mathematical), Analytical Skills, Technical Skills, Resource Management Skills, and Interpersonal Skills.</em>'
    },
    abilities: {
        icon: 'fa-brain',
        title: 'Abilities (OaSIS Category A)',
        text: '<strong>Innate and developed aptitudes</strong> <em>that facilitate the acquisition of knowledge and skills to carry out expected work. Abilities include: Cognitive Abilities, Physical Abilities, Psychomotor Abilities, and Sensory Abilities.</em>'
    },
    knowledge: {
        icon: 'fa-book-open',
        title: 'Knowledge (OaSIS Category G)',
        text: '<strong>Organized sets of principles and practices</strong> <em>used for the execution of tasks and activities within a particular domain. Knowledge areas include: Administration &amp; Management, Communication, Education, Health &amp; Wellbeing, Law/Government/Safety, Logistics &amp; Design, Natural Resources, Physical Sciences, Socioeconomic Systems, Technology, and Foundational Knowledge.</em>'
    },
    effort: {
        icon: 'fa-exchange-alt',
        title: 'Effort (OaSIS Work Context J03)',
        text: '<strong>Physical demands</strong> <em>the job requires the worker to perform. This includes body positioning, body exertion, and speaking/seeing requirements.</em>'
    },
    responsibility: {
        icon: 'fa-user',
        title: 'Responsibility (OaSIS Work Context J04)',
        text: '<strong>Interpersonal relations and accountability</strong> <em>required to perform the job. This includes job interactions, communication methods, and interpersonal responsibilities.</em>'
    }
};

/**
 * Render a section description box for a given tab key.
 * Text may contain raw HTML (bold/italic) for Skills/Abilities/etc. — not escaped.
 */
const renderSectionDescriptionBox = (tabKey) => {
    const desc = SECTION_DESCRIPTIONS[tabKey];
    if (!desc) return '';
    return `
        <div class="section-description-box">
            <i class="fas ${desc.icon} section-description-box__icon"></i>
            <div>
                <span class="section-description-box__title"><i class="fas ${desc.icon}"></i> ${desc.title}</span>
                <p class="section-description-box__text">${desc.text}</p>
            </div>
        </div>
    `;
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

    // v5.1: Always show gear icon in header (NOC-specific icons used in Overview tab)
    iconEl.className = 'fas fa-cog';

    // v5.1: ISO date format for Retrieved timestamp
    const isoDate = new Date().toLocaleDateString('en-CA');
    timestampEl.innerHTML = `<i class="fas fa-clock"></i> Retrieved: ${isoDate}`;

    // Show header
    header.classList.remove('hidden');

    // Close button — returns to search (step 1)
    const closeBtn = document.getElementById('profile-header-close');
    if (closeBtn) {
        closeBtn.onclick = () => {
            if (window.jdStepper) {
                window.jdStepper.goToStep(1);
            }
        };
    }

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
                // Also update the Overview tab's rendered definition box if visible
                const overviewDefEl = document.getElementById('overview-definition-display');
                if (overviewDefEl) overviewDefEl.textContent = descResult.description;
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
            { key: 'noc_hierarchy', title: 'NOC Hierarchy', source: 'noc_hierarchy' }
        ]
    },
    core_competencies: {
        sections: [
            { key: 'core_competencies', title: 'Core Competencies', source: 'reference_attributes.core_competencies' }
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
            { key: 'skills', title: 'Skills', filter: s => s.source_attribute === 'Skills' }
        ],
        dataKey: 'skills'
    },
    abilities: {
        sections: [
            { key: 'abilities', title: 'Abilities', filter: s => s.source_attribute === 'Abilities' }
        ],
        dataKey: 'skills'
    },
    knowledge: {
        sections: [
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
    }
};

/**
 * Render a source badge indicating whether tab data comes from JobForge parquet or OASIS.
 * @param {string} dataSource - "jobforge" or "oasis"
 * @param {string} [tooltip] - Optional tooltip text for hover
 * @returns {string} HTML string for the badge container
 */
const renderSourceBadge = (dataSource, tooltip) => {
    const label = dataSource === 'jobforge' ? 'Source: JobForge' : 'Source: OASIS';
    const cssClass = dataSource === 'jobforge'
        ? 'source-badge source-badge--jobforge'
        : 'source-badge source-badge--oasis';
    const titleAttr = tooltip ? ` title="${escapeHtml(tooltip)}"` : '';
    return `<div class="source-badge-container">
        <span class="${cssClass}"${titleAttr}>${label}</span>
    </div>`;
};

const renderOverviewContent = (profile) => {
    const ref = profile.reference_attributes || {};
    const hierarchy = profile.noc_hierarchy || {};
    const state = store.getState();

    let html = '';

    // Position Title — editable input (BUILD-03)
    const currentTitle = state.positionTitle || profile.title || '';
    html += `
        <div class="overview-position-title">
            <label class="overview-position-title__label" for="position-title-input">Position Title</label>
            <input type="text" id="position-title-input" class="overview-position-title__input"
                   value="${escapeHtml(currentTitle)}"
                   placeholder="Enter position title...">
        </div>
    `;

    // Two-column: Lead Statement (left) + Definition (right)
    const leadStatement = ref.lead_statement || '';
    const descEl = document.getElementById('profile-description');
    const definition = descEl ? descEl.textContent : '';

    html += `
        <div class="overview-two-col">
            <div class="overview-two-col__panel">
                <h4 class="overview-two-col__heading">Lead Statement</h4>
                <p class="overview-two-col__text">${leadStatement ? escapeHtml(leadStatement) : '<em>No lead statement available.</em>'}</p>
            </div>
            <div class="overview-two-col__panel">
                <h4 class="overview-two-col__heading">Definition</h4>
                <p id="overview-definition-display" class="overview-two-col__text">${definition ? escapeHtml(definition) : '<em>Loading definition...</em>'}</p>
            </div>
        </div>
    `;

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

    // Feeder Group Mobility & Career Progression (moved from removed career tab)
    const additionalInfo = ref.additional_info;
    if (additionalInfo) {
        html += `
            <div class="oasis-panel">
                <div class="oasis-panel__heading">
                    <span class="fas fa-route oasis-panel__icon"></span>
                    <h3 class="oasis-panel__title">Feeder Group Mobility & Career Progression</h3>
                </div>
                <div class="oasis-panel__body">
                    <div class="career-content">${escapeHtml(additionalInfo)}</div>
                </div>
            </div>
        `;
    }

    // Other Job Information sections (moved from removed other tab)
    html += renderOtherJobInfoContent(profile);

    return html || '<p>No overview information available.</p>';
};

const renderCoreCompetenciesContent = (profile) => {
    const ref = profile.reference_attributes || {};
    const state = store.getState();
    const selectedIds = state.selections.core_competencies || [];

    if (!ref.core_competencies?.length) {
        return '<p>No core competencies information available.</p>';
    }

    const items = ref.core_competencies;
    const allSelected = items.length > 0 && items.every((_, idx) =>
        selectedIds.includes(`core_competencies-${idx}`)
    );
    const selectedCount = items.filter((_, idx) =>
        selectedIds.includes(`core_competencies-${idx}`)
    ).length;

    let html = `
        <div class="select-all-row">
            <label class="select-all-label">
                <input type="checkbox" class="select-all-checkbox" data-section="core_competencies"
                       ${allSelected ? 'checked' : ''}>
                Select All (${items.length})
            </label>
            <span class="selection-count" id="count-core_competencies">${selectedCount} selected</span>
        </div>
        <div class="sources-row">
            <span class="sources-label">SOURCES:</span>
            <span class="source-chip">GC Core Competencies</span>
        </div>
        <ul class="tab-panel__list jd-section__list">
    `;

    items.forEach((competency, idx) => {
        const stmtId = `core_competencies-${idx}`;
        const isSelected = selectedIds.includes(stmtId);
        html += `
            <li class="statement tab-panel__item${isSelected ? ' statement--selected' : ''}" data-id="${stmtId}">
                <label class="statement__label">
                    <input type="checkbox" class="statement__checkbox"
                           data-section="core_competencies"
                           data-id="${stmtId}"
                           ${isSelected ? 'checked' : ''}>
                    <span class="statement__content">
                        <span class="statement__text">${escapeHtml(competency)}</span>
                    </span>
                </label>
            </li>
        `;
    });

    html += '</ul>';
    return html;
};

const renderKeyActivitiesContent = (profile, state) => {
    const allStatements = profile.key_activities?.statements || [];
    const selectedIds = state.selections.key_activities || [];

    if (allStatements.length === 0) {
        return '<p>No key activities available.</p>';
    }

    const mainDuties = allStatements.filter(s => s.source_attribute === 'Main Duties');
    const workActivities = allStatements.filter(s => s.source_attribute === 'Work Activities');

    // Single Select All for combined list
    const allSelected = allStatements.length > 0 && allStatements.every((_, idx) =>
        selectedIds.includes(`key_activities-${idx}`)
    );
    const selectedCount = allStatements.filter((_, idx) =>
        selectedIds.includes(`key_activities-${idx}`)
    ).length;

    let html = `
        <div class="select-all-row">
            <label class="select-all-label">
                <input type="checkbox" class="select-all-checkbox" data-section="key_activities"
                       ${allSelected ? 'checked' : ''}>
                Select All (${allStatements.length})
            </label>
            <span class="selection-count" id="count-key_activities">${selectedCount} selected</span>
        </div>
    `;

    // Render Main Duties section
    if (mainDuties.length > 0) {
        html += `<h4 class="activity-section-heading">Main Duties</h4>`;
        html += '<ul class="tab-panel__list jd-section__list">';
        mainDuties.forEach(stmt => {
            const idx = allStatements.indexOf(stmt);
            const stmtId = `key_activities-${idx}`;
            const isSelected = selectedIds.includes(stmtId);
            const descriptionHtml = stmt.description
                ? `<span class="statement__description">${escapeHtml(stmt.description)}</span>`
                : '';
            html += `
                <li class="statement tab-panel__item${isSelected ? ' statement--selected' : ''}" data-id="${stmtId}">
                    <label class="statement__label">
                        <input type="checkbox" class="statement__checkbox"
                               data-section="key_activities"
                               data-id="${stmtId}"
                               ${isSelected ? 'checked' : ''}>
                        <span class="statement__content">
                            <span class="statement__text">${escapeHtml(stmt.text)}</span>
                            ${descriptionHtml}
                        </span>
                    </label>
                </li>
            `;
        });
        html += '</ul>';
    }

    // Render Work Activities section
    if (workActivities.length > 0) {
        html += `<h4 class="activity-section-heading">Work Activities</h4>`;
        html += '<ul class="tab-panel__list jd-section__list">';
        workActivities.forEach(stmt => {
            const idx = allStatements.indexOf(stmt);
            const stmtId = `key_activities-${idx}`;
            const isSelected = selectedIds.includes(stmtId);
            const descriptionHtml = stmt.description
                ? `<span class="statement__description">${escapeHtml(stmt.description)}</span>`
                : '';
            html += `
                <li class="statement tab-panel__item${isSelected ? ' statement--selected' : ''}" data-id="${stmtId}">
                    <label class="statement__label">
                        <input type="checkbox" class="statement__checkbox"
                               data-section="key_activities"
                               data-id="${stmtId}"
                               ${isSelected ? 'checked' : ''}>
                        <span class="statement__content">
                            <span class="statement__text">${escapeHtml(stmt.text)}</span>
                            ${descriptionHtml}
                        </span>
                    </label>
                </li>
            `;
        });
        html += '</ul>';
    }

    return html + renderSourceBadge(
        profile.key_activities?.data_source || 'oasis',
        'Main Duties always served from OASIS (ETL pending)'
    );
};

/**
 * v5.1: Render level-grouped tab content with colored badges and proficiency dot ratings.
 * Used for Abilities, Knowledge, Effort, and Responsibility tabs.
 * Statements are grouped by stmt.proficiency.level (descending: 5, 4, 3, 2, 1, unrated).
 */
const renderLevelGroupedContent = (statements, sectionId, selectedIds, dataSource) => {
    if (!statements || statements.length === 0) {
        return `<p class="tab-panel__empty">No ${sectionId} items available for this occupation.</p>`;
    }

    // Group by proficiency level (key 0 = unrated)
    const groups = {};
    statements.forEach((stmt, idx) => {
        const level = stmt.proficiency?.level ?? 0;
        if (!groups[level]) groups[level] = [];
        groups[level].push({ stmt, idx });
    });

    // Sort levels descending (5 → 4 → 3 → 2 → 1 → 0)
    const sortedLevels = Object.keys(groups).map(Number).sort((a, b) => b - a);

    // Select All row
    const allSelected = statements.length > 0 && statements.every((_, idx) =>
        selectedIds.includes(`${sectionId}-${idx}`)
    );
    const selectedCount = statements.filter((_, idx) =>
        selectedIds.includes(`${sectionId}-${idx}`)
    ).length;

    let html = `
        <div class="select-all-row">
            <label class="select-all-label">
                <input type="checkbox" class="select-all-checkbox" data-section="${sectionId}"
                       ${allSelected ? 'checked' : ''}>
                Select All (${statements.length})
            </label>
            <span class="selection-count" id="count-${sectionId}">${selectedCount} selected</span>
        </div>
    `;

    // Render each level group
    sortedLevels.forEach(level => {
        const group = groups[level];
        const badgeInfo = LEVEL_BADGE_COLORS[level] || LEVEL_BADGE_COLORS[0];

        html += `
            <div class="level-group">
                <div class="level-group-header">
                    <span class="level-badge ${badgeInfo.cssClass}">${badgeInfo.label}</span>
                    <span class="level-group-count">(${group.length} items)</span>
                </div>
                <ul class="tab-panel__list jd-section__list">
        `;

        group.forEach(({ stmt, idx }) => {
            const stmtId = `${sectionId}-${idx}`;
            const isSelected = selectedIds.includes(stmtId);
            const descriptionHtml = stmt.description
                ? `<span class="statement__description">${escapeHtml(stmt.description)}</span>`
                : '';
            // BUILD-09: Proficiency dot ratings for Abilities, Knowledge, Effort, Responsibility
            const proficiencyHtml = stmt.proficiency ? renderProficiency(stmt.proficiency, stmt.source_attribute) : '';

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
                            ${proficiencyHtml}
                        </span>
                    </label>
                </li>
            `;
        });

        html += '</ul></div>';
    });

    html += renderSourceBadge(dataSource || 'oasis');
    return html;
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
                </div>
                ${definitionHtml}
                <ul class="tab-panel__list jd-section__list">
        `;

        filtered.forEach((stmt, idx) => {
            const stmtId = `${sectionId}-${statements.indexOf(stmt)}`;
            const isSelected = selectedIds.includes(stmtId);
            const proficiencyHtml = stmt.proficiency ? renderProficiency(stmt.proficiency, stmt.source_attribute) : '';

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

const renderAttributeLevel = (level, dimensionType = 'Importance') => {
    const max = 5;
    const filledCircles = '<span class="level-filled">●</span>'.repeat(level);
    const emptyCircles = '<span class="level-empty">○</span>'.repeat(max - level);
    return `<span class="attribute-level" title="${dimensionType} ${level}/${max}">${filledCircles}${emptyCircles} <span class="attribute-dimension">${dimensionType} ${level}/${max}</span></span>`;
};

const renderTabContent = (profile) => {
    const state = store.getState();

    // Overview tab - special handling for reference data
    const overviewPanel = document.getElementById('panel-overview');
    if (overviewPanel) {
        overviewPanel.innerHTML = renderSectionDescriptionBox('overview') + renderOverviewContent(profile);

        // Position Title input — store on change
        const titleInput = document.getElementById('position-title-input');
        if (titleInput) {
            titleInput.addEventListener('input', (e) => {
                store.setState({ positionTitle: e.target.value });
            });
        }

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

    // Core Competencies tab - NEW
    const coreCompPanel = document.getElementById('panel-core-competencies');
    if (coreCompPanel) {
        coreCompPanel.innerHTML = renderSectionDescriptionBox('core_competencies') + renderCoreCompetenciesContent(profile);
    }

    // Key Activities tab — single combined Select All + Main Duties / Work Activities headings (v5.1)
    const activitiesPanel = document.getElementById('panel-activities');
    if (activitiesPanel) {
        activitiesPanel.innerHTML = renderSectionDescriptionBox('activities') + renderKeyActivitiesContent(profile, state);
    }

    // Skills tab - now only Skills statements
    const skillsPanel = document.getElementById('panel-skills');
    if (skillsPanel) {
        skillsPanel.innerHTML = renderSectionDescriptionBox('skills') + renderStatementsPanel(
            profile.skills?.statements || [],
            TAB_CONFIG.skills.sections,
            'skills',
            state.selections.skills || []
        ) + renderSourceBadge(profile.skills?.data_source || 'oasis');
    }

    // Abilities tab — level-grouped with colored badges and proficiency dot ratings (v5.1)
    const abilitiesPanel = document.getElementById('panel-abilities');
    if (abilitiesPanel) {
        const abilitiesStmts = (profile.skills?.statements || []).filter(s => s.source_attribute === 'Abilities');
        abilitiesPanel.innerHTML = renderSectionDescriptionBox('abilities') +
            renderLevelGroupedContent(abilitiesStmts, 'abilities', state.selections.abilities || [], profile.skills?.data_source);
    }

    // Knowledge tab — level-grouped with colored badges and proficiency dot ratings (v5.1)
    const knowledgePanel = document.getElementById('panel-knowledge');
    if (knowledgePanel) {
        const knowledgeStmts = (profile.skills?.statements || []).filter(s => s.source_attribute === 'Knowledge');
        knowledgePanel.innerHTML = renderSectionDescriptionBox('knowledge') +
            renderLevelGroupedContent(knowledgeStmts, 'knowledge', state.selections.knowledge || [], profile.skills?.data_source);
    }

    // Effort tab — level-grouped with colored badges and proficiency dot ratings (v5.1)
    const effortPanel = document.getElementById('panel-effort');
    if (effortPanel) {
        const effortStmts = profile.effort?.statements || [];
        effortPanel.innerHTML = renderSectionDescriptionBox('effort') +
            renderLevelGroupedContent(effortStmts, 'effort', state.selections.effort || [], profile.effort?.data_source);
    }

    // Responsibility tab — level-grouped with colored badges and proficiency dot ratings (v5.1)
    const responsibilityPanel = document.getElementById('panel-responsibility');
    if (responsibilityPanel) {
        const respStmts = profile.responsibility?.statements || [];
        responsibilityPanel.innerHTML = renderSectionDescriptionBox('responsibility') +
            renderLevelGroupedContent(respStmts, 'responsibility', state.selections.responsibility || [], profile.responsibility?.data_source);
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
    const state = store.getState();
    const count = (state.selections[sectionId] || []).length;

    // Update old accordion count (jd-section summary badge)
    const section = document.querySelector(`[data-section-id="${sectionId}"]`);
    if (section) {
        const countEl = section.querySelector('.jd-section__count');
        if (countEl) {
            countEl.textContent = `(${count} selected)`;
        }
    }

    // Update v5.1 selection count span (inside select-all-row)
    const countSpan = document.getElementById(`count-${sectionId}`);
    if (countSpan) {
        countSpan.textContent = `${count} selected`;
    }

    // Update Select All checkbox state
    const selectAllCheckbox = document.querySelector(
        `input.select-all-checkbox[data-section="${sectionId}"]`
    );
    if (selectAllCheckbox) {
        const totalCheckboxes = document.querySelectorAll(
            `input.statement__checkbox[data-section="${sectionId}"]`
        ).length;
        selectAllCheckbox.checked = count > 0 && count === totalCheckboxes;
    }
};

const escapeHtml = (text) => {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
};

// Map source_attribute to dimension type for rating labels
const getDimensionType = (sourceAttribute) => {
    const dimensionMap = {
        'Skills': 'Proficiency',
        'Abilities': 'Proficiency',
        'Knowledge': 'Knowledge Level',
        'Work Activities': 'Complexity',
        'Personal Attributes': 'Importance',
        'Main Duties': 'Proficiency'
    };
    return dimensionMap[sourceAttribute] || 'Level';
};

const renderProficiency = (proficiency, sourceAttribute) => {
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
    const dimensionType = proficiency.dimension || getDimensionType(sourceAttribute);

    // Build circles string: filled circles then empty circles
    const filledCircles = '<span class="filled">●</span>'.repeat(level);
    const emptyCircles = '<span class="empty">○</span>'.repeat(max - level);

    return `
        <div class="proficiency-rating"
             aria-label="${dimensionType} ${level} of ${max}"
             data-full-label="${dimensionType} ${level}/${max}"
             tabindex="0">
            <span class="rating-circles" aria-hidden="true">${filledCircles}${emptyCircles}</span>
            <span class="rating-label">${dimensionType} ${level}/${max}</span>
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
window.ALL_SECTIONS_LABELS = ALL_SECTIONS_LABELS;
window.renderProficiency = renderProficiency;
window.renderDimensionBadge = renderDimensionBadge;
window.PROFICIENCY_LABELS = PROFICIENCY_LABELS;
