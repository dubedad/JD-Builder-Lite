---
phase: 08-C-profile-page-tabs
plan: 03
type: execute
wave: 2
depends_on: ["08-C-01"]
files_modified:
  - templates/index.html
  - static/css/main.css
  - static/js/profile_tabs.js
  - static/js/accordion.js
  - src/services/mapper.py
autonomous: true

must_haves:
  truths:
    - "User sees horizontal tabs below profile header"
    - "Tabs show: Overview, Key Activities, Skills, Effort, Responsibility, Feeder Group Mobility & Career Progression"
    - "Clicking a tab shows corresponding panel content"
    - "Arrow keys navigate between tabs per ARIA pattern"
    - "Key Activities tab shows Main Duties + Work Activities"
    - "Skills tab shows Skills + Abilities + Knowledge"
    - "Effort tab shows Work Context items filtered by 'effort'"
    - "Responsibility tab shows Work Context items filtered by 'responsib' or 'decision'"
  artifacts:
    - path: "templates/index.html"
      provides: "Tab navigation HTML structure with role=tablist"
      contains: "role=\"tablist\""
    - path: "static/js/profile_tabs.js"
      provides: "TabController class with ARIA keyboard navigation"
      contains: "class TabController"
    - path: "static/css/main.css"
      provides: "Tab styling with active states"
      contains: ".tabs-bar"
  key_links:
    - from: "static/js/profile_tabs.js"
      to: "templates/index.html"
      via: "querySelector for [role=tablist]"
      pattern: "querySelector.*role.*tablist"
    - from: "static/js/accordion.js"
      to: "static/js/profile_tabs.js"
      via: "window.TabController instantiation"
      pattern: "new TabController"
---

<objective>
Implement horizontal ARIA tabs for the profile page with proper content mapping from OaSIS categories to Job Description headers.

Purpose: Replace the current accordion pattern with a horizontal tab navigation that maps NOC data categories to JD element headers per the requirements.

Output: Fully accessible tab navigation with 6 tabs, proper ARIA attributes, keyboard navigation, and content panels populated from profile data.
</objective>

<execution_context>
@C:\Users\Administrator\.claude/get-shit-done/workflows/execute-plan.md
@C:\Users\Administrator\.claude/get-shit-done/templates/summary.md
</execution_context>

<context>
@.planning/PROJECT.md
@.planning/ROADMAP.md
@.planning/phases/08-C-profile-page-tabs/08-C-RESEARCH.md
@.planning/phases/06-enhanced-ui-display/06-CONTEXT.md
@templates/index.html
@static/css/main.css
@static/js/accordion.js
@src/services/mapper.py
</context>

<tasks>

<task type="auto">
  <name>Task 1: Create ARIA tab controller JavaScript</name>
  <files>static/js/profile_tabs.js</files>
  <action>
    Create new file `static/js/profile_tabs.js` with TabController class implementing W3C ARIA tab pattern:

    ```javascript
    /**
     * ARIA Tab Controller following W3C APG pattern
     * Implements automatic activation with arrow key navigation
     */
    class TabController {
        constructor(tablistEl) {
            this.tablist = tablistEl;
            this.tabs = Array.from(tablistEl.querySelectorAll('[role="tab"]'));
            this.panels = this.tabs.map(tab =>
                document.getElementById(tab.getAttribute('aria-controls'))
            );

            if (this.tabs.length === 0) {
                console.warn('TabController: No tabs found');
                return;
            }

            // Bind event handlers
            this.tablist.addEventListener('keydown', this.onKeydown.bind(this));
            this.tabs.forEach((tab, i) => {
                tab.addEventListener('click', () => this.activateTab(i));
            });

            // Set initial state - first tab active
            this.activateTab(0);
        }

        onKeydown(event) {
            const currentIndex = this.tabs.indexOf(document.activeElement);
            if (currentIndex === -1) return;

            let targetIndex = currentIndex;

            switch (event.key) {
                case 'ArrowRight':
                    targetIndex = (currentIndex + 1) % this.tabs.length;
                    break;
                case 'ArrowLeft':
                    targetIndex = currentIndex === 0 ?
                        this.tabs.length - 1 : currentIndex - 1;
                    break;
                case 'Home':
                    targetIndex = 0;
                    break;
                case 'End':
                    targetIndex = this.tabs.length - 1;
                    break;
                default:
                    return; // Don't prevent default for other keys
            }

            event.preventDefault();
            this.activateTab(targetIndex);
            this.tabs[targetIndex].focus();
        }

        activateTab(index) {
            // Update aria-selected and tabindex on all tabs
            this.tabs.forEach((tab, i) => {
                const isActive = i === index;
                tab.setAttribute('aria-selected', isActive);
                tab.setAttribute('tabindex', isActive ? '0' : '-1');
                tab.classList.toggle('tab-button-active', isActive);
            });

            // Show/hide panels
            this.panels.forEach((panel, i) => {
                if (panel) {
                    panel.hidden = i !== index;
                }
            });
        }

        // Programmatic tab activation by id
        activateTabById(tabId) {
            const index = this.tabs.findIndex(tab => tab.id === tabId);
            if (index !== -1) {
                this.activateTab(index);
            }
        }
    }

    // Export for use
    window.TabController = TabController;
    ```
  </action>
  <verify>
    Add script tag to index.html and verify in browser console:
    ```javascript
    // After DOM loads
    const tablist = document.querySelector('[role="tablist"]');
    const controller = new TabController(tablist);
    console.log('Tabs:', controller.tabs.length);
    controller.activateTab(1); // Should switch to second tab
    ```
  </verify>
  <done>
    TabController class implements full ARIA tab pattern with click and keyboard navigation.
  </done>
</task>

<task type="auto">
  <name>Task 2: Add tab navigation HTML and CSS</name>
  <files>templates/index.html, static/css/main.css</files>
  <action>
    **HTML Changes (templates/index.html):**

    Add the tab navigation structure after the profile header section (before jd-sections):

    ```html
    <!-- Profile Tabs Navigation -->
    <nav id="profile-tabs-container" class="profile-tabs-container hidden">
        <ul class="tabs-bar" role="tablist" aria-label="Job description sections">
            <li role="presentation">
                <button role="tab" id="tab-overview" aria-selected="true"
                        aria-controls="panel-overview" tabindex="0" class="tab-button tab-button-active">
                    Overview
                </button>
            </li>
            <li role="presentation">
                <button role="tab" id="tab-activities" aria-selected="false"
                        aria-controls="panel-activities" tabindex="-1" class="tab-button">
                    Key Activities
                </button>
            </li>
            <li role="presentation">
                <button role="tab" id="tab-skills" aria-selected="false"
                        aria-controls="panel-skills" tabindex="-1" class="tab-button">
                    Skills
                </button>
            </li>
            <li role="presentation">
                <button role="tab" id="tab-effort" aria-selected="false"
                        aria-controls="panel-effort" tabindex="-1" class="tab-button">
                    Effort
                </button>
            </li>
            <li role="presentation">
                <button role="tab" id="tab-responsibility" aria-selected="false"
                        aria-controls="panel-responsibility" tabindex="-1" class="tab-button">
                    Responsibility
                </button>
            </li>
            <li role="presentation">
                <button role="tab" id="tab-career" aria-selected="false"
                        aria-controls="panel-career" tabindex="-1" class="tab-button">
                    Feeder Group Mobility & Career Progression
                </button>
            </li>
        </ul>

        <!-- Tab Panels -->
        <div id="panel-overview" role="tabpanel" aria-labelledby="tab-overview" tabindex="0" class="tab-panel">
            <!-- Overview content rendered by JS -->
        </div>
        <div id="panel-activities" role="tabpanel" aria-labelledby="tab-activities" tabindex="0" class="tab-panel" hidden>
            <!-- Key Activities content -->
        </div>
        <div id="panel-skills" role="tabpanel" aria-labelledby="tab-skills" tabindex="0" class="tab-panel" hidden>
            <!-- Skills content -->
        </div>
        <div id="panel-effort" role="tabpanel" aria-labelledby="tab-effort" tabindex="0" class="tab-panel" hidden>
            <!-- Effort content -->
        </div>
        <div id="panel-responsibility" role="tabpanel" aria-labelledby="tab-responsibility" tabindex="0" class="tab-panel" hidden>
            <!-- Responsibility content -->
        </div>
        <div id="panel-career" role="tabpanel" aria-labelledby="tab-career" tabindex="0" class="tab-panel" hidden>
            <!-- Career content -->
        </div>
    </nav>
    ```

    Add script tag before main.js:
    ```html
    <script src="/static/js/profile_tabs.js"></script>
    ```

    **CSS Changes (static/css/main.css):**

    Add tab styling:

    ```css
    /* Profile Tabs Navigation */
    .profile-tabs-container {
        margin-bottom: 1.5rem;
    }

    .tabs-bar {
        list-style: none;
        padding: 0;
        margin: 0;
        display: flex;
        flex-wrap: wrap;
        gap: 0.5rem;
        border-bottom: 2px solid #e0e0e0;
        padding-bottom: 0;
    }

    .tabs-bar li {
        margin-bottom: -2px;
    }

    .tab-button {
        background: transparent;
        border: none;
        border-bottom: 2px solid transparent;
        padding: 0.75rem 1rem;
        font-size: 0.9375rem;
        font-weight: 500;
        color: #555;
        cursor: pointer;
        transition: all 0.2s ease;
        white-space: nowrap;
    }

    .tab-button:hover {
        color: #003366;
        background: rgba(0, 51, 102, 0.05);
    }

    .tab-button:focus {
        outline: 2px solid #003366;
        outline-offset: 2px;
    }

    .tab-button-active {
        color: #003366;
        border-bottom-color: #003366;
        font-weight: 600;
    }

    /* Tab Panels */
    .tab-panel {
        padding: 1.5rem 0;
    }

    .tab-panel[hidden] {
        display: none;
    }

    /* Panel Section Styling */
    .tab-panel__section {
        margin-bottom: 1.5rem;
    }

    .tab-panel__section-title {
        font-size: 1.125rem;
        font-weight: 600;
        color: #333;
        margin-bottom: 0.75rem;
        padding-bottom: 0.5rem;
        border-bottom: 1px solid #e0e0e0;
    }

    .tab-panel__list {
        list-style: none;
        padding: 0;
        margin: 0;
    }

    .tab-panel__item {
        padding: 0.75rem 0;
        border-bottom: 1px solid #f0f0f0;
        display: flex;
        align-items: flex-start;
        gap: 1rem;
    }

    .tab-panel__item:last-child {
        border-bottom: none;
    }

    /* Responsive tabs - scroll on mobile */
    @media (max-width: 768px) {
        .tabs-bar {
            flex-wrap: nowrap;
            overflow-x: auto;
            -webkit-overflow-scrolling: touch;
            scrollbar-width: none;
        }

        .tabs-bar::-webkit-scrollbar {
            display: none;
        }

        .tab-button {
            font-size: 0.875rem;
            padding: 0.625rem 0.875rem;
        }
    }
    ```
  </action>
  <verify>
    1. Reload page - tabs container should be hidden initially
    2. Manually remove 'hidden' class in dev tools
    3. Tab bar displays with 6 tabs
    4. Active tab has blue bottom border
    5. Clicking tabs changes active state
    6. Arrow keys navigate between tabs
    7. Responsive: tabs scroll horizontally on mobile
  </verify>
  <done>
    Tab HTML structure and CSS styling complete with ARIA attributes and responsive design.
  </done>
</task>

<task type="auto">
  <name>Task 3: Render tab content from profile data</name>
  <files>static/js/accordion.js</files>
  <action>
    Modify `static/js/accordion.js` to populate tab panels instead of accordions.

    Add new function `renderTabContent(profile)`:

    ```javascript
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

    const renderTabContent = (profile) => {
        const state = store.getState();

        // Overview tab - special handling for reference data
        const overviewPanel = document.getElementById('panel-overview');
        overviewPanel.innerHTML = renderOverviewContent(profile);

        // Key Activities tab
        const activitiesPanel = document.getElementById('panel-activities');
        activitiesPanel.innerHTML = renderStatementsPanel(
            profile.key_activities?.statements || [],
            TAB_CONFIG.activities.sections,
            'key_activities',
            state.selections.key_activities || []
        );

        // Skills tab
        const skillsPanel = document.getElementById('panel-skills');
        skillsPanel.innerHTML = renderStatementsPanel(
            profile.skills?.statements || [],
            TAB_CONFIG.skills.sections,
            'skills',
            state.selections.skills || []
        );

        // Effort tab
        const effortPanel = document.getElementById('panel-effort');
        effortPanel.innerHTML = renderStatementsPanel(
            profile.effort?.statements || [],
            [{ key: 'effort', title: 'Work Context - Effort' }],
            'effort',
            state.selections.effort || []
        );

        // Responsibility tab
        const responsibilityPanel = document.getElementById('panel-responsibility');
        responsibilityPanel.innerHTML = renderStatementsPanel(
            profile.responsibility?.statements || [],
            [{ key: 'responsibility', title: 'Work Context - Responsibility' }],
            'responsibility',
            state.selections.responsibility || []
        );

        // Career tab
        const careerPanel = document.getElementById('panel-career');
        careerPanel.innerHTML = renderCareerContent(profile);

        // Show tabs container
        document.getElementById('profile-tabs-container').classList.remove('hidden');

        // Initialize tab controller
        const tablist = document.querySelector('[role="tablist"]');
        if (tablist && !window.tabController) {
            window.tabController = new TabController(tablist);
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

    // Update renderAccordions to use tabs instead
    const renderAccordions = (profile) => {
        // Render profile header
        renderProfileHeader(profile);

        // Render tab content instead of accordions
        renderTabContent(profile);

        // Hide old accordion container
        const accordionContainer = document.querySelector('.jd-sections');
        if (accordionContainer) {
            accordionContainer.classList.add('hidden');
        }
    };

    // Export new functions
    window.renderTabContent = renderTabContent;
    ```
  </action>
  <verify>
    1. Search for "pilot" and select a profile
    2. Tab navigation appears below blue header
    3. Overview tab shows: Also Known As, Core Competencies, NOC Hierarchy
    4. Key Activities tab shows: Main Duties, Work Activities (with checkboxes)
    5. Skills tab shows: Skills, Abilities, Knowledge (with proficiency circles)
    6. Effort tab shows: Work Context items containing "effort"
    7. Responsibility tab shows: Work Context items with "responsib" or "decision"
    8. Career tab shows: Additional information text
    9. Checkboxes work and persist selections
  </verify>
  <done>
    Tab panels render correct content from profile data with proper section grouping and checkbox functionality.
  </done>
</task>

</tasks>

<verification>
1. Profile loads with horizontal tabs visible below blue header
2. Six tabs display: Overview, Key Activities, Skills, Effort, Responsibility, Feeder Group Mobility & Career Progression
3. Tab navigation via click works
4. Arrow key navigation between tabs works
5. Home/End keys navigate to first/last tab
6. Tab content displays correct NOC data per mapping:
   - Overview: Also known as, Core Competencies, NOC Hierarchy
   - Key Activities: Main Duties + Work Activities
   - Skills: Skills + Abilities + Knowledge
   - Effort: Work Context filtered for "effort"
   - Responsibility: Work Context filtered for "responsib"/"decision"
   - Career: Additional Information
7. Checkboxes in statement panels work correctly
8. Proficiency circles display on statements with levels
</verification>

<success_criteria>
- [ ] TabController class implements W3C ARIA tab pattern
- [ ] Arrow keys navigate between tabs with focus management
- [ ] Six tabs render with correct labels
- [ ] Active tab has visual indicator (blue bottom border)
- [ ] Tab panels show/hide correctly on tab switch
- [ ] Overview tab shows reference data (not selectable)
- [ ] Key Activities shows Main Duties + Work Activities with checkboxes
- [ ] Skills shows Skills + Abilities + Knowledge with proficiency circles
- [ ] Effort shows filtered Work Context items
- [ ] Responsibility shows filtered Work Context items
- [ ] Career shows Additional Information content
- [ ] Old accordion container hidden
</success_criteria>

<output>
After completion, create `.planning/phases/08-C-profile-page-tabs/08-C-03-SUMMARY.md`
</output>
