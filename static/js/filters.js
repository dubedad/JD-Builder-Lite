/**
 * Filter Panel Module
 * Handles filtering of search results by Minor Unit Group.
 *
 * Note: Feeder Group Mobility and Career Progression filters are UI placeholders.
 * They require profile data which is not available from search results.
 * Full implementation deferred to Phase 08-C or future enhancement.
 */

(function() {
    'use strict';

    // Filter state
    const filters = {
        minorGroup: new Set(),
        feederMobility: new Set(),      // Placeholder - not functional
        careerProgression: new Set()    // Placeholder - not functional
    };

    // Store all results for filtering
    let allResults = [];
    let renderCallback = null;

    // DOM references
    let minorGroupOptions = null;
    let feederOptions = null;
    let progressionOptions = null;
    let clearButton = null;
    let filterToggle = null;
    let filterPanel = null;
    let activeIndicator = null;

    /**
     * Initialize filter module
     * @param {Function} onFilterChange - Callback when filters change (receives filtered results)
     */
    function initFilters(onFilterChange) {
        renderCallback = onFilterChange;

        // Cache DOM references
        minorGroupOptions = document.getElementById('filter-minor-group-options');
        feederOptions = document.getElementById('filter-feeder-options');
        progressionOptions = document.getElementById('filter-progression-options');
        clearButton = document.getElementById('filter-clear');
        filterToggle = document.getElementById('filter-toggle');
        filterPanel = document.getElementById('filter-panel');
        activeIndicator = document.getElementById('filter-active-indicator');

        if (!minorGroupOptions) {
            console.warn('Filter elements not found, filters disabled');
            return;
        }

        // Bind clear button
        if (clearButton) {
            clearButton.addEventListener('click', clearAllFilters);
        }

        // Bind mobile toggle
        if (filterToggle && filterPanel) {
            filterToggle.addEventListener('click', function() {
                filterPanel.classList.toggle('collapsed');
            });
        }

        // Bind filter change events (event delegation)
        const filterPanelEl = document.getElementById('filter-panel');
        if (filterPanelEl) {
            filterPanelEl.addEventListener('change', handleFilterChange);
        }
    }

    /**
     * Update filter options based on search results
     * @param {Array} results - EnrichedSearchResult objects
     */
    function updateFilterOptions(results) {
        allResults = results;

        // Build Minor Group options from results
        const minorGroups = new Map();
        results.forEach(r => {
            if (r.minor_group) {
                const key = r.minor_group;
                if (!minorGroups.has(key)) {
                    minorGroups.set(key, {
                        code: key,
                        name: r.minor_group_name || `Minor Group ${key}`,
                        count: 0
                    });
                }
                minorGroups.get(key).count++;
            }
        });

        // Render Minor Group checkboxes
        if (minorGroupOptions) {
            if (minorGroups.size === 0) {
                minorGroupOptions.innerHTML = '<p class="filter-empty">No minor groups in results</p>';
            } else {
                const sorted = Array.from(minorGroups.values()).sort((a, b) => a.code.localeCompare(b.code));
                minorGroupOptions.innerHTML = sorted.map(group => `
                    <label class="filter-checkbox">
                        <input type="checkbox" name="minorGroup" value="${escapeHtml(group.code)}"
                               ${filters.minorGroup.has(group.code) ? 'checked' : ''}>
                        <span class="filter-checkbox-label">
                            ${escapeHtml(group.code)} - ${escapeHtml(group.name)}
                            <span class="filter-checkbox-count">(${group.count})</span>
                        </span>
                    </label>
                `).join('');
            }
        }

        // Feeder Mobility and Career Progression: Keep placeholder messages
        // These require profile data which is not available from search results
        if (feederOptions) {
            feederOptions.innerHTML = '<p class="filter-empty">Select a profile to enable mobility filtering</p>';
        }
        if (progressionOptions) {
            progressionOptions.innerHTML = '<p class="filter-empty">Select a profile to enable progression filtering</p>';
        }

        // Clear existing filters that no longer apply
        const validMinorGroups = new Set(minorGroups.keys());
        filters.minorGroup.forEach(mg => {
            if (!validMinorGroups.has(mg)) {
                filters.minorGroup.delete(mg);
            }
        });

        updateClearButton();
    }

    /**
     * Handle filter checkbox change
     * @param {Event} e - Change event
     */
    function handleFilterChange(e) {
        const checkbox = e.target;
        if (checkbox.type !== 'checkbox') return;

        const filterType = checkbox.name;
        const value = checkbox.value;

        if (!filters[filterType]) return;

        if (checkbox.checked) {
            filters[filterType].add(value);
        } else {
            filters[filterType].delete(value);
        }

        applyFilters();
        updateClearButton();
    }

    /**
     * Apply current filters and trigger callback
     */
    function applyFilters() {
        const filtered = allResults.filter(result => {
            // Check minor group filter (OR logic - any checked group matches)
            if (filters.minorGroup.size > 0) {
                if (!result.minor_group || !filters.minorGroup.has(result.minor_group)) {
                    return false;
                }
            }

            // Feeder mobility filter: placeholder, not functional
            // Full implementation requires profile data (Phase 08-C or future)

            // Career progression filter: placeholder, not functional
            // Full implementation requires profile data (Phase 08-C or future)

            return true;
        });

        if (renderCallback) {
            renderCallback(filtered);
        }
    }

    /**
     * Clear all filters
     */
    function clearAllFilters() {
        filters.minorGroup.clear();
        filters.feederMobility.clear();
        filters.careerProgression.clear();

        // Uncheck all checkboxes
        const checkboxes = document.querySelectorAll('#filter-panel input[type="checkbox"]');
        checkboxes.forEach(cb => cb.checked = false);

        applyFilters();
        updateClearButton();
    }

    /**
     * Update clear button state
     */
    function updateClearButton() {
        const activeCount = filters.minorGroup.size + filters.feederMobility.size + filters.careerProgression.size;

        if (clearButton) {
            clearButton.disabled = activeCount === 0;
        }

        if (activeIndicator) {
            if (activeCount > 0) {
                activeIndicator.innerHTML = `<span class="filter-active-count">${activeCount}</span>`;
            } else {
                activeIndicator.innerHTML = '';
            }
        }
    }

    /**
     * Get current filter state
     * @returns {Object} Filter state object
     */
    function getFilterState() {
        return {
            minorGroup: Array.from(filters.minorGroup),
            feederMobility: Array.from(filters.feederMobility),
            careerProgression: Array.from(filters.careerProgression)
        };
    }

    /**
     * Escape HTML special characters
     */
    function escapeHtml(text) {
        if (!text) return '';
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }

    // Export to global scope
    window.filterModule = {
        init: initFilters,
        updateOptions: updateFilterOptions,
        clear: clearAllFilters,
        getState: getFilterState
    };
})();
