// Main application initialization
console.log('[DEBUG main.js] Script loaded');
console.log('[DEBUG main.js] api object:', typeof api);
console.log('[DEBUG main.js] storage object:', typeof storage);
console.log('[DEBUG main.js] filterModule:', typeof filterModule);

document.addEventListener('DOMContentLoaded', function() {
    console.log('[DEBUG main.js] DOMContentLoaded fired');
    // Cache DOM references
    const searchInput = document.getElementById('search-input');
    const searchButton = document.getElementById('search-button');
    const searchResults = document.getElementById('search-results');
    const resultsList = document.getElementById('results-list');
    const profileInfo = document.getElementById('profile-header');
    const jdSections = document.getElementById('jd-sections');
    const actionBar = document.getElementById('action-bar');
    const sidebar = document.getElementById('sidebar');
    const sidebarToggle = document.getElementById('sidebar-toggle');
    const viewToggle = document.getElementById('view-toggle');
    const pillBtns = document.querySelectorAll('.pill-btn');
    const sortSelect = document.getElementById('sort-select');
    const resultsCount = document.getElementById('results-count');
    const viewToggleLabel = document.getElementById('view-toggle-label');

    // Profile info elements
    const profileTitle = document.getElementById('profile-title');
    const profileNoc = document.getElementById('profile-code-badge');
    const profileLink = document.getElementById('profile-link');
    const profileTimestamp = document.getElementById('profile-timestamp');

    // Global profile data storage
    window.currentProfile = null;

    // NOC Minor Group (3-digit) to Icon mapping for specific occupations
    const NOC_MINOR_GROUP_ICONS = {
        '726': 'fa-plane',      // Air pilots, flight engineers
        '727': 'fa-ship',       // Marine/ship officers
        '728': 'fa-train',      // Rail transport
        '721': 'fa-truck',      // Truck/bus drivers
        '722': 'fa-truck',      // Heavy equipment operators
        '731': 'fa-hard-hat',   // Construction helpers
        '732': 'fa-hard-hat',   // Construction labourers
        '301': 'fa-user-md',    // Physicians
        '302': 'fa-user-nurse', // Nursing
        '311': 'fa-user-nurse', // Nursing coordinators
        '321': 'fa-stethoscope',// Medical technologists
        '217': 'fa-laptop-code',// IT professionals
        '212': 'fa-laptop-code' // Software engineers
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
        7: 'fa-tools',          // Trades (fallback for category 7)
        8: 'fa-tractor',        // Natural resources, agriculture
        9: 'fa-industry'        // Manufacturing and utilities
    };

    /**
     * Get semantic icon based on NOC code - checks minor group first, then broad category
     * @param {number|string} nocCodeOrCategory - NOC code string or broad category number
     * @returns {string} - Font Awesome icon class
     */
    function getNocCategoryIcon(nocCodeOrCategory) {
        if (nocCodeOrCategory == null) return 'fa-briefcase';

        // If passed a number (broad category), use it directly
        if (typeof nocCodeOrCategory === 'number') {
            return NOC_BROAD_ICONS[nocCodeOrCategory] || 'fa-briefcase';
        }

        // Extract base code (remove decimal: 72600.01 -> 72600)
        const baseCode = String(nocCodeOrCategory).split('.')[0];

        // Try minor group (first 3 digits) for specific match
        const minorGroup = baseCode.substring(0, 3);
        if (NOC_MINOR_GROUP_ICONS[minorGroup]) {
            return NOC_MINOR_GROUP_ICONS[minorGroup];
        }

        // Fall back to broad category (first digit)
        const broadCategory = parseInt(baseCode.charAt(0), 10);
        return NOC_BROAD_ICONS[broadCategory] || 'fa-briefcase';
    }

    // View toggle state
    let currentView = storage.get('viewMode', 'card');
    let currentSort = { column: null, ascending: true };
    let lastResults = []; // Store results for re-rendering on view change

    // Initialize modules (from Plan 02)
    initSidebar();
    initSelection();
    initSectionSearch();
    initGenerate();
    initExport();

    // Initialize JD Stepper navigation
    initStepper();

    // Initialize filter module
    filterModule.init(function(filteredResults) {
        renderSearchResults(filteredResults);
    });

    // Auto-load profile only when returning from preview (Back to Edit)
    const returnToProfile = sessionStorage.getItem('jdb_return_to_profile');
    if (returnToProfile) {
        sessionStorage.removeItem('jdb_return_to_profile');
        const savedState = store.getState();
        if (savedState.currentProfileCode) {
            console.log('[DEBUG main.js] Returning from preview, restoring profile:', savedState.currentProfileCode);
            setTimeout(() => {
                handleResultClick(savedState.currentProfileCode);
            }, 100);
        }
    }

    // Check for return to classify flag
    const returnToClassify = sessionStorage.getItem('jdb_return_to_classify');
    if (returnToClassify) {
        sessionStorage.removeItem('jdb_return_to_classify');
        const savedState = store.getState();
        if (savedState.currentProfileCode) {
            setTimeout(() => {
                handleResultClick(savedState.currentProfileCode);
                // After profile loads, navigate to Step 5
                document.addEventListener('profile-loaded', () => {
                    setTimeout(() => window.jdStepper.goToStep(5), 200);
                }, { once: true });
            }, 100);
        }
    }

    // Search type toggle state
    let currentSearchType = 'Keyword';

    // Pill toggle handler
    pillBtns.forEach(btn => {
        btn.addEventListener('click', () => {
            // Update active state
            pillBtns.forEach(b => {
                b.classList.remove('active');
                b.setAttribute('aria-selected', 'false');
            });
            btn.classList.add('active');
            btn.setAttribute('aria-selected', 'true');

            // Update search type
            currentSearchType = btn.dataset.searchType;

            // Update placeholder
            searchInput.placeholder = currentSearchType === 'Keyword'
                ? 'Search job titles...'
                : 'Enter NOC code (e.g., 72600 or 72600.01)';
            searchInput.setAttribute('aria-label',
                currentSearchType === 'Keyword' ? 'Search job titles' : 'Enter NOC code');
        });
    });

    // Responsive view handling
    const mediaQuery = window.matchMedia('(max-width: 768px)');

    function handleViewportChange(e) {
        if (e.matches) {
            // Mobile: force card view, disable toggle
            switchView('card', false);
            viewToggle.disabled = true;
        } else {
            // Desktop: enable toggle, restore preference
            viewToggle.disabled = false;
            switchView(storage.get('viewMode', 'card'), false);
        }
    }

    mediaQuery.addEventListener('change', handleViewportChange);

    /**
     * Switch between card and grid views
     * @param {string} view - 'card' or 'grid'
     * @param {boolean} persist - Whether to save preference to storage
     */
    function switchView(view, persist = true) {
        currentView = view;
        resultsList.className = 'results-list ' + view + '-view';

        if (view === 'grid') {
            viewToggleLabel.textContent = 'Card view';
            viewToggle.setAttribute('aria-label', 'Switch to card view');
            viewToggle.setAttribute('title', 'Card view');
        } else {
            viewToggleLabel.textContent = 'Grid view';
            viewToggle.setAttribute('aria-label', 'Switch to grid view');
            viewToggle.setAttribute('title', 'Grid view');
        }

        if (persist && !mediaQuery.matches) {
            storage.set('viewMode', view);
        }

        // Re-render with current results
        if (lastResults.length > 0) {
            renderSearchResults(lastResults);
        }
    }

    /**
     * Show inline error message
     * @param {HTMLElement} container - Container to prepend error to
     * @param {string} message - Error message to display
     */
    function showError(container, message) {
        // Remove any existing error messages
        const existingError = container.querySelector('.error-message');
        if (existingError) {
            existingError.remove();
        }

        const errorDiv = document.createElement('div');
        errorDiv.className = 'error-message';
        errorDiv.setAttribute('role', 'alert');
        errorDiv.textContent = message;

        container.prepend(errorDiv);

        // Auto-remove after 5 seconds
        setTimeout(function() {
            if (errorDiv.parentNode) {
                errorDiv.remove();
            }
        }, 5000);
    }

    /**
     * Show skeleton loading placeholders
     * @param {HTMLElement} container - Container to fill with skeletons
     */
    function showSkeleton(container) {
        container.innerHTML = '';

        const sections = [
            'Key Activities',
            'Skills',
            'Effort',
            'Responsibility',
            'Working Conditions'
        ];

        sections.forEach(function(sectionName) {
            const skeleton = document.createElement('div');
            skeleton.className = 'skeleton-section';
            skeleton.innerHTML = `
                <div class="skeleton-section-header">
                    <div class="skeleton skeleton-section-title"></div>
                    <div class="skeleton skeleton-section-badge"></div>
                </div>
                <div class="skeleton-section-content">
                    <div class="skeleton-statement">
                        <div class="skeleton skeleton-checkbox"></div>
                        <div class="skeleton-statement-content">
                            <div class="skeleton skeleton-text"></div>
                            <div class="skeleton skeleton-text medium"></div>
                        </div>
                    </div>
                    <div class="skeleton-statement">
                        <div class="skeleton skeleton-checkbox"></div>
                        <div class="skeleton-statement-content">
                            <div class="skeleton skeleton-text"></div>
                            <div class="skeleton skeleton-text short"></div>
                        </div>
                    </div>
                    <div class="skeleton-statement">
                        <div class="skeleton skeleton-checkbox"></div>
                        <div class="skeleton-statement-content">
                            <div class="skeleton skeleton-text medium"></div>
                        </div>
                    </div>
                </div>
            `;
            container.appendChild(skeleton);
        });
    }

    /**
     * Render search results
     * @param {Array} results - Array of search result objects
     */
    function renderSearchResults(results) {
        lastResults = results; // Store for re-rendering
        resultsList.innerHTML = '';

        // Update results count
        resultsCount.textContent = `Showing ${results.length} ${results.length === 1 ? 'result' : 'results'}`;

        if (results.length === 0) {
            resultsList.innerHTML = '<div class="empty-state" role="listitem">No results found</div>';
            return;
        }

        if (currentView === 'grid' && !mediaQuery.matches) {
            renderGridView(results);
        } else {
            renderCardView(results);
        }
    }

    /**
     * Render OaSIS-style card view
     * @param {Array} results - Array of EnrichedSearchResult objects
     */
    function renderCardView(results) {
        resultsList.className = 'results-cards-container';

        results.forEach(function(result) {
            const card = document.createElement('div');
            card.className = 'oasis-card';
            card.setAttribute('data-code', result.noc_code);
            card.setAttribute('role', 'listitem');
            card.setAttribute('tabindex', '0');

            // Build card HTML with available data
            card.innerHTML = `
                <div class="card-header">
                    <a href="#" class="card-title-link" data-code="${escapeHtml(result.noc_code)}">
                        ${escapeHtml(result.noc_code)} - ${escapeHtml(result.title)}
                    </a>
                </div>

                ${result.broad_category_name ? `
                <div class="card-row">
                    <i class="fa ${getNocCategoryIcon(result.noc_code)} card-icon" aria-hidden="true"></i>
                    <span class="card-text">${escapeHtml(result.broad_category_name)}</span>
                </div>
                ` : ''}

                ${result.teer_description ? `
                <div class="card-row">
                    <i class="fa fa-bookmark card-icon" aria-hidden="true"></i>
                    <span class="card-text">${escapeHtml(result.teer_description)}</span>
                </div>
                ` : ''}

                ${result.lead_statement ? `
                <div class="card-row">
                    <i class="fa fa-book card-icon" aria-hidden="true"></i>
                    <span class="card-text">${escapeHtml(result.lead_statement)}</span>
                </div>
                ` : ''}

                <div class="card-footer">
                    ${result.match_reason ? `
                    <span class="match-reason match-reason--${result.relevance_score >= 80 ? 'high' : result.relevance_score >= 40 ? 'medium' : 'low'}">
                        <span class="match-confidence">${result.relevance_score}%</span>
                        ${escapeHtml(result.match_reason)}
                    </span>
                    ` : ''}
                    <i class="fa fa-search card-icon" aria-hidden="true"></i>
                    <span class="card-text">
                        <span class="matching-label">Matching search criteria</span>
                        ${result.matching_criteria ? `<br><span class="matching-value">${escapeHtml(result.matching_criteria)}</span>` : ''}
                    </span>
                </div>
            `;

            resultsList.appendChild(card);
        });
    }

    // Cache for loaded profile summaries
    const profileCache = new Map();

    /**
     * Render grid view with JD category headers and lazy-load content
     * @param {Array} results - Array of EnrichedSearchResult objects
     */
    function renderGridView(results) {
        resultsList.className = 'results-list grid-view';

        // Grid header with JD category names
        const header = document.createElement('div');
        header.className = 'grid-header';
        header.setAttribute('role', 'row');
        header.innerHTML = `
            <div class="grid-header-cell" role="columnheader">OaSIS Profile</div>
            <div class="grid-header-cell" role="columnheader">Key Activities</div>
            <div class="grid-header-cell" role="columnheader">Skills</div>
            <div class="grid-header-cell" role="columnheader">Effort</div>
            <div class="grid-header-cell" role="columnheader">Responsibility</div>
            <div class="grid-header-cell" role="columnheader">Working Conditions</div>
        `;
        resultsList.appendChild(header);

        // Grid rows with loading state
        results.forEach(function(result) {
            const row = document.createElement('div');
            row.className = 'grid-row';
            row.setAttribute('data-code', result.noc_code);
            row.setAttribute('role', 'row');
            row.setAttribute('tabindex', '0');
            row.innerHTML = `
                <div class="grid-cell" role="cell">
                    <a href="#" class="grid-profile-link">${escapeHtml(result.noc_code)} - ${escapeHtml(result.title)}</a>
                </div>
                <div class="grid-cell grid-cell-activities" role="cell"><span class="loading-text">Loading...</span></div>
                <div class="grid-cell grid-cell-skills" role="cell"><span class="loading-text">Loading...</span></div>
                <div class="grid-cell grid-cell-effort" role="cell"><span class="loading-text">Loading...</span></div>
                <div class="grid-cell grid-cell-responsibility" role="cell"><span class="loading-text">Loading...</span></div>
                <div class="grid-cell grid-cell-conditions" role="cell"><span class="loading-text">Loading...</span></div>
            `;
            resultsList.appendChild(row);
        });

        // Lazy load profile data for each result
        loadGridProfileData(results);
    }

    /**
     * Lazy load profile data for grid view cells
     * @param {Array} results - Search results to load profiles for
     */
    async function loadGridProfileData(results) {
        // Process in batches to avoid overwhelming the server
        const batchSize = 3;
        for (let i = 0; i < results.length; i += batchSize) {
            const batch = results.slice(i, i + batchSize);
            await Promise.all(batch.map(result => loadSingleGridProfile(result.noc_code)));
        }
    }

    /**
     * Load a single profile and update grid row
     * @param {string} nocCode - NOC code to fetch
     */
    async function loadSingleGridProfile(nocCode) {
        const row = resultsList.querySelector(`.grid-row[data-code="${nocCode}"]`);
        if (!row) return;

        // Check cache first
        if (profileCache.has(nocCode)) {
            updateGridRow(row, profileCache.get(nocCode));
            return;
        }

        try {
            const profile = await api.getProfile(nocCode);

            // Extract top 2 items from each JD category (statements are in .statements array)
            const summary = {
                example_titles: profile.example_titles || [],
                key_activities: extractTopItems(profile.key_activities?.statements, 2),
                skills: extractTopItems(profile.skills?.statements, 2),
                effort: extractTopItems(profile.effort?.statements, 2),
                responsibility: extractTopItems(profile.responsibility?.statements, 2),
                working_conditions: extractTopItems(profile.working_conditions?.statements, 2)
            };

            // Cache the summary
            profileCache.set(nocCode, summary);

            // Update the row (including the profile cell with example titles)
            updateGridRow(row, summary, profile);
        } catch (error) {
            console.error(`Failed to load profile ${nocCode}:`, error);
            // Show error state
            const cells = row.querySelectorAll('.grid-cell:not(:first-child)');
            cells.forEach(cell => {
                cell.innerHTML = '<span class="loading-text error">Error</span>';
            });
        }
    }

    /**
     * Extract top N items from a JD section
     * @param {Array} section - Array of statement objects
     * @param {number} count - Number of items to extract
     * @returns {Array} - Array of text strings
     */
    function extractTopItems(section, count) {
        if (!section || !Array.isArray(section)) return [];

        // Dimension type labels to filter out (from Work Context parsing issues)
        const dimensionLabels = ['importance', 'frequency', 'duration', 'level', 'proficiency'];

        return section
            .map(stmt => {
                // Handle both string and object formats
                if (typeof stmt === 'string') return stmt;
                return stmt.text || stmt.statement || '';
            })
            .filter(text => {
                if (!text || text.length === 0) return false;
                // Filter out dimension labels that got captured as text
                const lowerText = text.toLowerCase().trim();
                if (dimensionLabels.includes(lowerText)) return false;
                // Filter out very short text (likely parsing errors)
                if (text.length < 10) return false;
                return true;
            })
            .slice(0, count);
    }

    /**
     * Update a grid row with profile summary data
     * @param {HTMLElement} row - Grid row element
     * @param {Object} summary - Summary data object
     * @param {Object} profile - Full profile data (optional, for example titles)
     */
    function updateGridRow(row, summary, profile) {
        const formatCell = (items) => {
            if (!items || items.length === 0) return '<span class="loading-text">None</span>';
            // Truncate long text and join with line break
            return items.map(text => {
                const truncated = text.length > 50 ? text.substring(0, 47) + '...' : text;
                return escapeHtml(truncated);
            }).join('<br>');
        };

        // Update profile cell with example titles if available
        if (profile && summary.example_titles && summary.example_titles.length > 0) {
            const profileCell = row.querySelector('.grid-cell:first-child');
            const link = profileCell.querySelector('.grid-profile-link');
            const exampleTitlesHtml = summary.example_titles.slice(0, 3).map(t => escapeHtml(t)).join(', ');
            profileCell.innerHTML = `
                <div class="grid-profile-info">
                    <a href="#" class="grid-profile-link">${link.textContent}</a>
                    <div class="grid-example-titles">${exampleTitlesHtml}</div>
                </div>
            `;
        }

        row.querySelector('.grid-cell-activities').innerHTML = formatCell(summary.key_activities);
        row.querySelector('.grid-cell-skills').innerHTML = formatCell(summary.skills);
        row.querySelector('.grid-cell-effort').innerHTML = formatCell(summary.effort);
        row.querySelector('.grid-cell-responsibility').innerHTML = formatCell(summary.responsibility);
        row.querySelector('.grid-cell-conditions').innerHTML = formatCell(summary.working_conditions);
    }

    /**
     * Update profile info card
     * @param {Object} profile - Profile data from API
     */
    function updateProfileInfo(profile) {
        profileTitle.textContent = profile.title;
        profileNoc.textContent = profile.noc_code;
        profileLink.href = profile.metadata.profile_url;

        // Format timestamp
        const date = new Date(profile.metadata.scraped_at);
        profileTimestamp.textContent = date.toLocaleString();
    }

    /**
     * Escape HTML special characters
     * @param {string} text - Text to escape
     * @returns {string} - Escaped text
     */
    function escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }

    /**
     * Handle search form submission
     */
    async function handleSearch() {
        console.log('[DEBUG] handleSearch started');
        const query = searchInput.value.trim();

        // Validate minimum length
        if (query.length < 2) {
            showError(searchResults.parentElement, 'Please enter at least 2 characters');
            return;
        }

        // Show loading state
        searchButton.disabled = true;
        searchButton.textContent = 'Searching...';
        searchResults.classList.add('hidden');
        profileInfo.classList.add('hidden');
        jdSections.innerHTML = '';

        try {
            console.log('[DEBUG] Calling api.search...');
            const response = await api.search(query, currentSearchType);
            console.log('[DEBUG] api.search returned:', response?.count, 'results');

            // Update filter options with new results
            console.log('[DEBUG] Updating filter options...');
            filterModule.updateOptions(response.results);

            // Clear any previous filters when doing new search
            console.log('[DEBUG] Clearing filters...');
            filterModule.clear();

            console.log('[DEBUG] Rendering results...');
            renderSearchResults(response.results);
            searchResults.classList.remove('hidden');

            // Show explore section below results
            const exploreSection = document.getElementById('explore-section');
            if (exploreSection) {
                exploreSection.classList.remove('hidden');
            }

            // Dispatch search-complete event for stepper
            document.dispatchEvent(new CustomEvent('search-complete', {
                detail: { count: response.results.length }
            }));

            console.log('[DEBUG] Search complete!');
        } catch (error) {
            console.error('[DEBUG] Search error:', error);
            showError(searchResults.parentElement, error.message);
        } finally {
            console.log('[DEBUG] Finally block - resetting button');
            searchButton.disabled = false;
            searchButton.textContent = 'Search';
        }
    }

    /**
     * Handle result click to load profile
     * @param {string} code - NOC code to fetch
     */
    async function handleResultClick(code) {
        // Hide search results, welcome section, and explore section
        searchResults.classList.add('hidden');
        const welcomeSection = document.getElementById('welcome-section');
        if (welcomeSection) {
            welcomeSection.classList.add('hidden');
        }
        const exploreSection = document.getElementById('explore-section');
        if (exploreSection) {
            exploreSection.classList.add('hidden');
        }
        showSkeleton(jdSections);

        try {
            const profile = await api.getProfile(code);

            // Store globally
            window.currentProfile = profile;

            // Update info card
            updateProfileInfo(profile);
            profileInfo.classList.remove('hidden');

            // Reset selections if different profile
            resetSelectionsForProfile(profile.noc_code);

            // Render accordions with statements
            renderAccordions(profile);

            // Show action bar
            actionBar.classList.remove('hidden');

            // Trigger initial state update for sidebar
            updateSidebar(store.getState());

            // Dispatch custom event for other modules
            const event = new CustomEvent('profile-loaded', { detail: profile });
            document.dispatchEvent(event);
        } catch (error) {
            showError(jdSections, error.message);
        }
    }

    // Bind search button click
    searchButton.addEventListener('click', handleSearch);

    // Bind Enter key in search input
    searchInput.addEventListener('keypress', function(e) {
        if (e.key === 'Enter') {
            handleSearch();
        }
    });

    // View toggle click
    viewToggle.addEventListener('click', function() {
        switchView(currentView === 'card' ? 'grid' : 'card');
    });

    // Sort dropdown handler
    sortSelect.addEventListener('change', function() {
        const sortValue = sortSelect.value;
        let sorted = [...lastResults];

        switch (sortValue) {
            case 'title-asc':
                sorted.sort((a, b) => a.title.localeCompare(b.title));
                break;
            case 'title-desc':
                sorted.sort((a, b) => b.title.localeCompare(a.title));
                break;
            case 'code-asc':
                sorted.sort((a, b) => a.noc_code.localeCompare(b.noc_code));
                break;
            case 'code-desc':
                sorted.sort((a, b) => b.noc_code.localeCompare(a.noc_code));
                break;
            case 'match':
            default:
                // Sort by relevance score (highest first)
                sorted.sort((a, b) => (b.relevance_score || 0) - (a.relevance_score || 0));
                break;
        }

        renderSearchResults(sorted);
    });

    // Event delegation for result clicks
    resultsList.addEventListener('click', function(e) {
        // Handle card clicks (prevent link default, use data-code)
        const card = e.target.closest('.oasis-card, .grid-row');
        if (card) {
            e.preventDefault();
            const code = card.getAttribute('data-code');
            if (code) {
                handleResultClick(code);
            }
            return;
        }

        // Fallback for direct li clicks (legacy)
        const li = e.target.closest('li[data-code]');
        if (li) {
            const code = li.getAttribute('data-code');
            handleResultClick(code);
        }
    });

    // Keyboard navigation for cards
    resultsList.addEventListener('keydown', function(e) {
        if (e.key === 'Enter' || e.key === ' ') {
            const card = e.target.closest('.oasis-card, .grid-row');
            if (card) {
                e.preventDefault();
                const code = card.getAttribute('data-code');
                if (code) {
                    handleResultClick(code);
                }
            }
        }
    });

    // Sidebar toggle
    sidebarToggle.addEventListener('click', function() {
        sidebar.classList.toggle('open');
        sidebar.classList.toggle('collapsed');
        document.body.classList.toggle('sidebar-open');
    });

    // Initialize view state
    handleViewportChange(mediaQuery);

    /**
     * Initialize JD Stepper navigation
     * Steps: 1=Search, 2=Select Profile, 3=Build JD, 4=Export, 5=Classify
     */
    function initStepper() {
        const stepper = document.getElementById('jd-stepper');
        if (!stepper) return;

        const steps = stepper.querySelectorAll('.jd-stepper__step');
        const buttons = stepper.querySelectorAll('.jd-stepper__btn');
        let currentStep = 1;

        // Step navigation handlers
        buttons.forEach(btn => {
            btn.addEventListener('click', () => {
                const targetStep = parseInt(btn.dataset.step, 10);
                navigateToStep(targetStep);
            });
        });

        /**
         * Navigate to a specific step
         * @param {number} step - Target step (1-5)
         */
        function navigateToStep(step) {
            if (step < 1 || step > 5) return;

            // Navigation logic based on target step
            switch (step) {
                case 1: // Search
                    // Show search results, hide profile
                    searchResults.classList.remove('hidden');
                    profileInfo.classList.add('hidden');
                    document.getElementById('profile-tabs-container')?.classList.add('hidden');
                    document.getElementById('classify-section')?.classList.add('hidden');
                    jdSections.innerHTML = '';
                    actionBar.classList.add('hidden');
                    const welcomeSection = document.getElementById('welcome-section');
                    if (welcomeSection && lastResults.length === 0) {
                        welcomeSection.classList.remove('hidden');
                    }
                    break;
                case 2: // Select Profile (show search results)
                    if (lastResults.length > 0) {
                        searchResults.classList.remove('hidden');
                        profileInfo.classList.add('hidden');
                        document.getElementById('profile-tabs-container')?.classList.add('hidden');
                        document.getElementById('classify-section')?.classList.add('hidden');
                        jdSections.innerHTML = '';
                        actionBar.classList.add('hidden');
                    }
                    break;
                case 3: // Build JD
                    // If we have a profile loaded, show it
                    if (window.currentProfile) {
                        searchResults.classList.add('hidden');
                        profileInfo.classList.remove('hidden');
                        document.getElementById('profile-tabs-container')?.classList.remove('hidden');
                        document.getElementById('classify-section')?.classList.add('hidden');
                        actionBar.classList.remove('hidden');
                    }
                    break;
                case 4: // Export
                    // Navigate to export - trigger sidebar or modal
                    if (window.currentProfile) {
                        sidebar.classList.add('open');
                        sidebar.classList.remove('collapsed');
                        document.body.classList.add('sidebar-open');
                    }
                    break;
                case 5: // Classify
                    // Hide other sections, show classify
                    searchResults.classList.add('hidden');
                    profileInfo.classList.add('hidden');
                    document.getElementById('profile-tabs-container')?.classList.add('hidden');
                    jdSections.innerHTML = '';
                    actionBar.classList.add('hidden');

                    // Show classify section
                    const classifySection = document.getElementById('classify-section');
                    if (classifySection) {
                        classifySection.classList.remove('hidden');

                        // Check for cached classification result
                        const cachedClassification = localStorage.getItem('classification_cache');
                        if (cachedClassification) {
                            try {
                                const cache = JSON.parse(cachedClassification);
                                const currentHash = btoa(JSON.stringify(store.getState().selections));
                                if (cache.jdHash === currentHash) {
                                    // Use cached result - dispatch cache-hit event
                                    console.log('[DEBUG main.js] Classification cache hit, using cached result');
                                    document.dispatchEvent(new CustomEvent('classify-cache-hit', { detail: cache.result }));
                                    return; // Skip API call
                                }
                            } catch (e) {
                                console.error('[DEBUG main.js] Failed to parse classification cache:', e);
                            }
                        }

                        // No valid cache - proceed with API call
                        triggerClassification();
                    }
                    break;
            }

            updateStepperState(step);
        }

        /**
         * Update stepper visual state
         * @param {number} activeStep - Current active step
         */
        function updateStepperState(activeStep) {
            currentStep = activeStep;

            steps.forEach((step, index) => {
                const stepNum = index + 1;
                const btn = step.querySelector('.jd-stepper__btn');

                // Remove all states
                step.classList.remove('jd-stepper__step--active', 'jd-stepper__step--completed');

                if (stepNum < activeStep) {
                    // Completed steps
                    step.classList.add('jd-stepper__step--completed');
                    btn.disabled = false;
                } else if (stepNum === activeStep) {
                    // Current step
                    step.classList.add('jd-stepper__step--active');
                    btn.disabled = false;
                } else {
                    // Future steps - enabled if previous step allows
                    btn.disabled = !canAccessStep(stepNum);
                }
            });
        }

        /**
         * Check if a step can be accessed based on app state
         * @param {number} step - Step to check
         * @returns {boolean}
         */
        function canAccessStep(step) {
            switch (step) {
                case 1: return true; // Always can search
                case 2: return lastResults.length > 0; // Need search results
                case 3: return window.currentProfile !== null; // Need profile selected
                case 4: return window.currentProfile !== null; // Need profile for export
                case 5:
                    // Enable when Client-Service Results and Key Activities are filled
                    // Per CONTEXT.md: Step 5 enabled when JD has CSR/Key Activities content
                    if (!window.currentProfile) return false;
                    const state = store.getState();
                    const hasSelections = state.selections?.key_activities?.length > 0;
                    const hasLeadStatement = window.currentProfile?.reference_attributes?.lead_statement?.length > 10;
                    return hasSelections || hasLeadStatement;
                default: return false;
            }
        }

        // Expose stepper API globally for other modules
        window.jdStepper = {
            goToStep: navigateToStep,
            updateState: updateStepperState,
            getCurrentStep: () => currentStep
        };

        // Listen for app events to auto-update stepper
        // After search completes - move to step 2
        document.addEventListener('search-complete', () => {
            updateStepperState(2);
        });

        // After profile is loaded - move to step 3
        document.addEventListener('profile-loaded', () => {
            updateStepperState(3);
        });

        // Re-evaluate step accessibility when selections change
        // This enables Step 5 when user selects key activities
        store.subscribe((state) => {
            // Re-run canAccessStep checks without changing current step
            steps.forEach((step, index) => {
                const stepNum = index + 1;
                const btn = step.querySelector('.jd-stepper__btn');
                if (stepNum > currentStep) {
                    btn.disabled = !canAccessStep(stepNum);
                }
            });
        });

        console.log('[DEBUG] JD Stepper initialized with 5 steps');
    }

    /**
     * Listen for classify-complete event and write to cache
     */
    document.addEventListener('classify-complete', (event) => {
        const result = event.detail;
        const hash = btoa(JSON.stringify(store.getState().selections));
        localStorage.setItem('classification_cache', JSON.stringify({
            result: result,
            jdHash: hash,
            timestamp: Date.now()
        }));
        console.log('[DEBUG main.js] Classification result cached');
    });

    /**
     * Listen for selection changes and mark classification cache as stale
     */
    store.subscribe((state) => {
        const cache = localStorage.getItem('classification_cache');
        if (cache) {
            try {
                const parsed = JSON.parse(cache);
                const currentHash = btoa(JSON.stringify(state.selections));
                if (parsed.jdHash !== currentHash) {
                    // Mark stale - show banner on classify section
                    const banner = document.getElementById('classify-stale-warning');
                    if (banner) {
                        banner.classList.remove('hidden');
                    }
                }
            } catch (e) {
                console.error('[DEBUG main.js] Failed to parse classification cache for stale check:', e);
            }
        }
    });
}

    /**
     * Trigger allocation API call when navigating to Step 5
     * Full implementation in classify.js (Plan 02)
     */
    async function triggerClassification() {
        const classifySection = document.getElementById('classify-section');
        const loadingEl = document.getElementById('classify-loading');
        const resultsEl = document.getElementById('classify-results');
        const errorEl = document.getElementById('classify-error');

        // Show loading state
        loadingEl?.classList.remove('hidden');
        resultsEl?.classList.add('hidden');
        errorEl?.classList.add('hidden');

        // Classification logic implemented in classify.js
        // This function dispatches event for classify.js to handle
        document.dispatchEvent(new CustomEvent('classify-requested', {
            detail: {
                profile: window.currentProfile,
                selections: store.getState().selections
            }
        }));
    }

    // Expose triggerClassification globally for other modules
    window.triggerClassification = triggerClassification;
});
