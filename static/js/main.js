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
            viewToggle.innerHTML = '<span aria-hidden="true">&#x25A6;</span>';
            viewToggle.setAttribute('aria-label', 'Switch to card view');
            viewToggle.setAttribute('title', 'Card view');
        } else {
            viewToggle.innerHTML = '<span aria-hidden="true">&#x2630;</span>';
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

        if (results.length === 0) {
            resultsList.innerHTML = '<li class="empty-state">No results found</li>';
            return;
        }

        if (currentView === 'grid' && !mediaQuery.matches) {
            // Add header row for grid view
            const header = document.createElement('div');
            header.className = 'grid-header';
            header.setAttribute('role', 'row');
            header.innerHTML = `
                <div class="grid-header-cell" data-column="profile" role="columnheader">
                    OASIS Profile<span class="sort-indicator"></span>
                </div>
                <div class="grid-header-cell" data-column="examples" role="columnheader">
                    Example Titles<span class="sort-indicator"></span>
                </div>
                <div class="grid-header-cell" data-column="lead" role="columnheader">
                    Lead Statement<span class="sort-indicator"></span>
                </div>
                <div class="grid-header-cell" data-column="teer" role="columnheader">
                    TEER<span class="sort-indicator"></span>
                </div>
            `;
            resultsList.appendChild(header);

            // Render grid rows
            results.forEach(function(result) {
                const li = document.createElement('li');
                li.setAttribute('data-code', result.noc_code);
                li.setAttribute('role', 'row');
                li.innerHTML = `
                    <div class="grid-cell" data-column="profile" role="cell">
                        <strong>${escapeHtml(result.title)}</strong>
                        <span class="noc-code">(${escapeHtml(result.noc_code)})</span>
                    </div>
                    <div class="grid-cell" data-column="examples" role="cell">
                        ${escapeHtml(result.example_titles || '-')}
                    </div>
                    <div class="grid-cell" data-column="lead" role="cell">
                        ${escapeHtml(result.lead_statement || '-')}
                    </div>
                    <div class="grid-cell" data-column="teer" role="cell">
                        ${escapeHtml(result.teer || '-')}
                    </div>
                `;
                resultsList.appendChild(li);
            });

            updateSortIndicator();
        } else {
            // Card view rendering
            results.forEach(function(result) {
                const li = document.createElement('li');
                li.setAttribute('data-code', result.noc_code);
                li.innerHTML = `
                    <span class="result-title">${escapeHtml(result.title)}</span>
                    <span class="noc-code">(${escapeHtml(result.noc_code)})</span>
                `;
                resultsList.appendChild(li);
            });
        }
    }

    /**
     * Sort results by column
     * @param {string} column - Column name to sort by
     */
    function sortResults(column) {
        if (currentSort.column === column) {
            currentSort.ascending = !currentSort.ascending;
        } else {
            currentSort.column = column;
            currentSort.ascending = true;
        }

        const sortKey = {
            profile: 'title',
            examples: 'example_titles',
            lead: 'lead_statement',
            teer: 'teer'
        }[column] || 'title';

        lastResults.sort((a, b) => {
            const aVal = (a[sortKey] || '').toString();
            const bVal = (b[sortKey] || '').toString();
            const cmp = aVal.localeCompare(bVal);
            return currentSort.ascending ? cmp : -cmp;
        });

        renderSearchResults(lastResults);
    }

    /**
     * Update sort indicator arrows in grid header
     */
    function updateSortIndicator() {
        document.querySelectorAll('.grid-header-cell').forEach(cell => {
            const indicator = cell.querySelector('.sort-indicator');
            if (cell.dataset.column === currentSort.column) {
                indicator.textContent = currentSort.ascending ? ' ▲' : ' ▼';
                indicator.classList.add('active');
            } else {
                indicator.textContent = '';
                indicator.classList.remove('active');
            }
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

    // Event delegation for result clicks and sort header clicks
    resultsList.addEventListener('click', function(e) {
        const headerCell = e.target.closest('.grid-header-cell');
        if (headerCell) {
            sortResults(headerCell.dataset.column);
            return;
        }

        // Existing result click handling
        const li = e.target.closest('li[data-code]');
        if (li) {
            const code = li.getAttribute('data-code');
            handleResultClick(code);
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
