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
    const pillBtns = document.querySelectorAll('.pill-btn');
    const resultsCount = document.getElementById('results-count');

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

    // Last results storage for re-rendering
    let lastResults = [];

    // Session ID (CHROME-02)
    function getOrCreateSessionId() {
        let id = localStorage.getItem('jdb_session_id');
        if (!id) {
            id = crypto.randomUUID().replace(/-/g, '').substring(0, 12);
            localStorage.setItem('jdb_session_id', id);
        }
        return id;
    }
    const sessionId = getOrCreateSessionId();
    const sessionEl = document.getElementById('app-bar-session');
    if (sessionEl) sessionEl.textContent = 'Session: ' + sessionId.substring(0, 8) + '...';

    // Reset button handler (CHROME-02)
    const resetBtn = document.getElementById('app-bar-reset');
    if (resetBtn) {
        resetBtn.addEventListener('click', () => {
            if (confirm('Reset session? This will clear all selections and cached data.')) {
                localStorage.removeItem('jdb_session_id');
                localStorage.removeItem('classification_cache');
                store.reset();
                window.location.reload();
            }
        });
    }

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
                    setTimeout(() => window.jdStepper.goToStep(3), 200);
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

    // Responsive viewport detection (used for some responsive logic)
    const mediaQuery = window.matchMedia('(max-width: 768px)');

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

        // Update results count in new header format
        if (resultsCount) {
            resultsCount.textContent = `${results.length} result${results.length !== 1 ? 's' : ''}`;
        }

        if (results.length === 0) {
            resultsList.innerHTML = '<div class="empty-state" role="listitem">No results found</div>';
            return;
        }

        renderCardView(results);
    }

    /**
     * Render v5.1 result cards (SRCH-04)
     * @param {Array} results - Array of EnrichedSearchResult objects
     */
    function renderCardView(results) {
        resultsList.className = 'results-cards-container';
        resultsList.innerHTML = '';
        resultsList.setAttribute('role', 'list');

        results.forEach(function(result) {
            const card = document.createElement('div');
            card.className = 'result-card';
            card.setAttribute('data-code', result.noc_code);
            card.setAttribute('role', 'listitem');
            card.setAttribute('tabindex', '0');

            // Determine match tier for badge color
            const score = result.relevance_score || 0;
            let badgeClass, badgeLabel;
            if (score >= 95) {
                badgeClass = 'match-badge-pill--green';
                badgeLabel = 'Title match';
            } else if (score >= 80) {
                badgeClass = 'match-badge-pill--blue';
                badgeLabel = 'Description match';
            } else {
                badgeClass = 'match-badge-pill--grey';
                badgeLabel = 'Related match';
            }

            const sourceLabel = result.source_label || 'O*NET SOC';

            // Build "Also known as:" with keyword highlighting
            let alsoKnownAsHtml = '';
            if (result.example_titles) {
                let titlesText = escapeHtml(result.example_titles);
                // Highlight search query keywords
                const query = searchInput ? searchInput.value.trim() : '';
                if (query) {
                    const queryWords = query.toLowerCase().split(/\s+/);
                    queryWords.forEach(function(word) {
                        if (word.length >= 3) {
                            const regex = new RegExp('(' + word.replace(/[.*+?^${}()|[\]\\]/g, '\\$&') + ')', 'gi');
                            titlesText = titlesText.replace(regex, '<span class="highlight">$1</span>');
                        }
                    });
                }
                alsoKnownAsHtml = '<p class="result-card__also-known-as"><strong>Also known as:</strong> ' + titlesText + '</p>';
            }

            const iconClass = getNocCategoryIcon(result.noc_code);

            card.innerHTML =
                '<div class="result-card__header">' +
                    '<i class="fas ' + iconClass + ' result-card__icon" aria-hidden="true"></i>' +
                    '<h3 class="result-card__title">' + escapeHtml(result.title) + '</h3>' +
                '</div>' +
                '<div class="result-card__badges">' +
                    '<span class="match-badge-pill ' + badgeClass + '">' + score + '% ' + badgeLabel + '</span>' +
                    '<span class="match-badge-pill match-badge-pill--grey">' + escapeHtml(sourceLabel) + '</span>' +
                '</div>' +
                alsoKnownAsHtml +
                (result.lead_statement ? '<p class="result-card__description">' + escapeHtml(result.lead_statement) + '</p>' : '');

            card.addEventListener('click', function() { handleResultClick(result.noc_code); });
            card.addEventListener('keydown', function(e) {
                if (e.key === 'Enter' || e.key === ' ') {
                    e.preventDefault();
                    handleResultClick(result.noc_code);
                }
            });

            resultsList.appendChild(card);
        });
    }

    // Profile cache (kept for potential future use)
    const profileCache = new Map();

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

        // Hide empty state when search starts
        const emptyState = document.getElementById('search-empty-state');
        if (emptyState) emptyState.classList.add('hidden');

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

            // Hide welcome section when showing results
            const welcomeSection = document.getElementById('welcome-section');
            if (welcomeSection) {
                welcomeSection.classList.add('hidden');
            }

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

    // + New Search button handler (SRCH-05)
    const newSearchBtn = document.getElementById('new-search-btn');
    if (newSearchBtn) {
        newSearchBtn.addEventListener('click', function() {
            if (searchInput) searchInput.value = '';
            if (searchResults) searchResults.classList.add('hidden');
            const welcomeSection = document.getElementById('welcome-section');
            if (welcomeSection) welcomeSection.classList.remove('hidden');
            const emptyState = document.getElementById('search-empty-state');
            if (emptyState) emptyState.classList.remove('hidden');
            lastResults = [];
            if (window.jdStepper) window.jdStepper.goToStep(1);
        });
    }

    // Event delegation for result clicks (cards now have direct event listeners added in renderCardView)
    // Fallback delegation for any cards that may not have direct listeners
    resultsList.addEventListener('click', function(e) {
        const card = e.target.closest('.result-card');
        if (card) {
            e.preventDefault();
            const code = card.getAttribute('data-code');
            if (code) {
                handleResultClick(code);
            }
        }
    });

    // Sidebar toggle (legacy - now handled by selections-tab in sidebar.js)
    if (sidebarToggle) {
        sidebarToggle.addEventListener('click', function() {
            sidebar.classList.toggle('open');
            sidebar.classList.toggle('collapsed');
            document.body.classList.toggle('sidebar-open');
        });
    }

    // (view toggle removed in v5.1 — card view is the only view)

    /**
     * Initialize JD Stepper navigation
     * Steps v5.1: 1=Search, 2=Build, 3=Classify, 4=Generate, 5=Export
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
         * Navigate to a specific step (v5.1 mapping)
         * @param {number} step - Target step (1-5)
         */
        function navigateToStep(step) {
            if (step < 1 || step > 5) return;

            // Navigation logic based on target step (v5.1 labels)
            switch (step) {
                case 1: { // Search — show welcome/search results, hide profile
                    searchResults.classList.remove('hidden');
                    profileInfo.classList.add('hidden');
                    document.getElementById('profile-tabs-container')?.classList.add('hidden');
                    document.getElementById('classify-section')?.classList.add('hidden');
                    document.getElementById('overview-section')?.classList.add('hidden');
                    jdSections.innerHTML = '';
                    actionBar.classList.add('hidden');
                    const welcomeSection = document.getElementById('welcome-section');
                    if (welcomeSection && lastResults.length === 0) {
                        welcomeSection.classList.remove('hidden');
                    }
                    break;
                }
                case 2: { // Build — show profile tabs if profile loaded, else search results
                    if (window.currentProfile) {
                        searchResults.classList.add('hidden');
                        document.getElementById('welcome-section')?.classList.add('hidden');
                        document.getElementById('explore-section')?.classList.add('hidden');
                        profileInfo.classList.remove('hidden');
                        document.getElementById('profile-tabs-container')?.classList.remove('hidden');
                        document.getElementById('classify-section')?.classList.add('hidden');
                        document.getElementById('overview-section')?.classList.add('hidden');
                        actionBar.classList.remove('hidden');
                    } else if (lastResults.length > 0) {
                        searchResults.classList.remove('hidden');
                        profileInfo.classList.add('hidden');
                        document.getElementById('profile-tabs-container')?.classList.add('hidden');
                        document.getElementById('classify-section')?.classList.add('hidden');
                        document.getElementById('overview-section')?.classList.add('hidden');
                        jdSections.innerHTML = '';
                        actionBar.classList.add('hidden');
                    }
                    break;
                }
                case 3: { // Classify — show classify section, trigger classification
                    searchResults.classList.add('hidden');
                    profileInfo.classList.add('hidden');
                    document.getElementById('profile-tabs-container')?.classList.add('hidden');
                    document.getElementById('overview-section')?.classList.add('hidden');
                    jdSections.innerHTML = '';
                    actionBar.classList.add('hidden');

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
                                    console.log('[DEBUG main.js] Classification cache hit, using cached result');
                                    document.dispatchEvent(new CustomEvent('classify-cache-hit', { detail: cache.result }));
                                    updateStepperState(step);
                                    return; // Skip API call
                                }
                            } catch (e) {
                                console.error('[DEBUG main.js] Failed to parse classification cache:', e);
                            }
                        }

                        triggerClassification();
                    }
                    break;
                }
                case 4: { // Generate — show overview/generate section
                    if (window.currentProfile) {
                        searchResults.classList.add('hidden');
                        profileInfo.classList.add('hidden');
                        document.getElementById('profile-tabs-container')?.classList.add('hidden');
                        document.getElementById('classify-section')?.classList.add('hidden');
                        jdSections.innerHTML = '';
                        actionBar.classList.add('hidden');
                        document.getElementById('overview-section')?.classList.remove('hidden');
                    }
                    break;
                }
                case 5: { // Export — open sidebar for export
                    if (window.currentProfile) {
                        sidebar.classList.add('open');
                        sidebar.classList.remove('collapsed');
                        document.body.classList.add('sidebar-open');
                    }
                    break;
                }
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
         * Check if a step can be accessed based on app state (v5.1 mapping)
         * @param {number} step - Step to check
         * @returns {boolean}
         */
        function canAccessStep(step) {
            switch (step) {
                case 1: return true; // Always can search
                case 2: return window.currentProfile !== null; // Need profile loaded for Build
                case 3: {
                    // Classify: need profile and some selections or lead statement
                    if (!window.currentProfile) return false;
                    const state = store.getState();
                    const hasSelections = state.selections?.key_activities?.length > 0;
                    const hasLeadStatement = window.currentProfile?.reference_attributes?.lead_statement?.length > 10;
                    return hasSelections || hasLeadStatement;
                }
                case 4: return window.currentProfile !== null; // Need profile for Generate
                case 5: return window.currentProfile !== null; // Need profile for Export
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
        // After search completes - stay on step 1 (search results visible)
        document.addEventListener('search-complete', () => {
            updateStepperState(1);
        });

        // After profile is loaded - move to step 2 (Build)
        document.addEventListener('profile-loaded', () => {
            updateStepperState(2);
        });

        // Re-evaluate step accessibility when selections change
        // This enables Step 3 (Classify) when user selects key activities
        store.subscribe((state) => {
            // Re-run canAccessStep checks without changing current step
            steps.forEach((step, index) => {
                const stepNum = index + 1;
                const btn = step.querySelector('.jd-stepper__btn');
                if (stepNum > currentStep) {
                    btn.disabled = !canAccessStep(stepNum);
                }
            });

            // Update audit count badge (CHROME-02)
            const auditEl = document.getElementById('audit-count');
            if (auditEl) {
                const total = Object.values(state.selections)
                    .reduce((sum, arr) => sum + arr.length, 0);
                auditEl.textContent = total;
            }
        });

        console.log('[DEBUG] JD Stepper initialized with 5 steps (v5.1: Search/Build/Classify/Generate/Export)');
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
