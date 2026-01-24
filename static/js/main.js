// Main application initialization
document.addEventListener('DOMContentLoaded', function() {
    // Cache DOM references
    const searchInput = document.getElementById('search-input');
    const searchButton = document.getElementById('search-button');
    const searchResults = document.getElementById('search-results');
    const resultsList = document.getElementById('results-list');
    const profileInfo = document.getElementById('profile-info');
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
    const profileNoc = document.getElementById('profile-noc');
    const profileLink = document.getElementById('profile-link');
    const profileTimestamp = document.getElementById('profile-timestamp');

    // Global profile data storage
    window.currentProfile = null;

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

    // Initialize filter module
    filterModule.init(function(filteredResults) {
        renderSearchResults(filteredResults);
    });

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
                    <i class="fa fa-truck card-icon" aria-hidden="true"></i>
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

    /**
     * Render grid view with placeholder for profile-dependent columns
     * Note: Skills/Abilities/Knowledge require profile fetch - shows placeholder
     * @param {Array} results - Array of EnrichedSearchResult objects
     */
    function renderGridView(results) {
        resultsList.className = 'results-list grid-view';

        // Grid header
        const header = document.createElement('div');
        header.className = 'grid-header';
        header.setAttribute('role', 'row');
        header.innerHTML = `
            <div class="grid-header-cell" role="columnheader">OaSIS Profile</div>
            <div class="grid-header-cell" role="columnheader">Top Skills</div>
            <div class="grid-header-cell" role="columnheader">Top Abilities</div>
            <div class="grid-header-cell" role="columnheader">Top Knowledge</div>
            <div class="grid-header-cell" role="columnheader">Matching Criteria</div>
        `;
        resultsList.appendChild(header);

        // Grid rows (skills/abilities/knowledge require profile fetch - show placeholder)
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
                <div class="grid-cell" role="cell">${result.top_skills ? result.top_skills.slice(0, 3).join(', ') : '<span class="loading-text">Load profile for skills</span>'}</div>
                <div class="grid-cell" role="cell">${result.top_abilities ? result.top_abilities.slice(0, 3).join(', ') : '<span class="loading-text">Load profile for abilities</span>'}</div>
                <div class="grid-cell" role="cell">${result.top_knowledge ? result.top_knowledge.slice(0, 3).join(', ') : '<span class="loading-text">Load profile for knowledge</span>'}</div>
                <div class="grid-cell" role="cell">${escapeHtml(result.matching_criteria || '-')}</div>
            `;
            resultsList.appendChild(row);
        });
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
            const response = await api.search(query, currentSearchType);

            // Update filter options with new results
            filterModule.updateOptions(response.results);

            // Clear any previous filters when doing new search
            filterModule.clear();

            renderSearchResults(response.results);
            searchResults.classList.remove('hidden');
        } catch (error) {
            showError(searchResults.parentElement, error.message);
        } finally {
            searchButton.disabled = false;
            searchButton.textContent = 'Search';
        }
    }

    /**
     * Handle result click to load profile
     * @param {string} code - NOC code to fetch
     */
    async function handleResultClick(code) {
        // Hide search results and show skeleton
        searchResults.classList.add('hidden');
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
                // Keep original order (API returns by match relevance)
                sorted = [...lastResults];
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
});
