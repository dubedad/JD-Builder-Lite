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

    // Profile info elements
    const profileTitle = document.getElementById('profile-title');
    const profileNoc = document.getElementById('profile-noc');
    const profileLink = document.getElementById('profile-link');
    const profileTimestamp = document.getElementById('profile-timestamp');

    // Global profile data storage
    window.currentProfile = null;

    // Initialize modules (from Plan 02)
    initSidebar();
    initSelection();
    initSectionSearch();
    initGenerate();
    initExport();

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
        resultsList.innerHTML = '';

        if (results.length === 0) {
            resultsList.innerHTML = '<li class="empty-state">No results found</li>';
            return;
        }

        results.forEach(function(result) {
            const li = document.createElement('li');
            li.setAttribute('data-code', result.noc_code);
            li.innerHTML = `
                <span class="result-title">${escapeHtml(result.title)}</span>
                <span class="result-code">(${escapeHtml(result.noc_code)})</span>
            `;
            resultsList.appendChild(li);
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
            const response = await api.search(query);
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

    // Event delegation for result clicks
    resultsList.addEventListener('click', function(e) {
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
});
