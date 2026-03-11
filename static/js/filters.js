/**
 * Filter Panel Module (v5.1)
 * Handles filtering of search results by NOC Broad/Major group.
 *
 * v5.1 changes: Updated DOM references from filter-minor-group-options
 * to filter-noc-broad-options to match the new 6-accordion filter panel.
 */

(function() {
    'use strict';

    // Filter state
    const filters = {
        minorGroup: new Set()
    };

    // Store all results for filtering
    let allResults = [];
    let renderCallback = null;

    // DOM references
    let minorGroupOptions = null;
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

        // Cache DOM references (v5.1: updated to filter-noc-broad-options)
        minorGroupOptions = document.getElementById('filter-noc-broad-options');
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

        // Build hierarchical structure: sub-major groups with unit group children
        const hierarchy = new Map();

        results.forEach(r => {
            if (!r.sub_major_group || !r.unit_group || !r.broad_category_name) {
                return; // Skip results without hierarchy data
            }

            // Get or create sub-major group
            if (!hierarchy.has(r.sub_major_group)) {
                hierarchy.set(r.sub_major_group, {
                    code: r.sub_major_group,
                    name: r.broad_category_name, // Use broad category name as parent heading
                    children: new Map(),
                    totalCount: 0
                });
            }

            const subMajor = hierarchy.get(r.sub_major_group);

            // Get or create unit group child
            if (!subMajor.children.has(r.unit_group)) {
                subMajor.children.set(r.unit_group, {
                    code: r.unit_group,
                    name: r.title, // Use job title as child label
                    count: 0
                });
            }

            // Increment counts
            subMajor.children.get(r.unit_group).count++;
            subMajor.totalCount++;
        });

        // Render hierarchical checkboxes
        if (minorGroupOptions) {
            if (hierarchy.size === 0) {
                minorGroupOptions.innerHTML = '<p class="filter-empty">No categories in results</p>';
            } else {
                let html = '';

                // Sort parent groups alphabetically
                const sorted = Array.from(hierarchy.values()).sort((a, b) => a.name.localeCompare(b.name));

                sorted.forEach(subMajor => {
                    // Sort children by name
                    const sortedChildren = Array.from(subMajor.children.values()).sort((a, b) =>
                        a.name.localeCompare(b.name)
                    );

                    html += `
                        <div class="filter-group">
                            <label class="filter-checkbox filter-checkbox--parent">
                                <input type="checkbox" class="parent-checkbox" data-group="${escapeHtml(subMajor.code)}">
                                <strong>${escapeHtml(subMajor.name)}</strong>
                                <span class="filter-checkbox-count">(${subMajor.totalCount})</span>
                            </label>
                            <div class="filter-group__children">
                                ${sortedChildren.map(child => `
                                    <label class="filter-checkbox filter-checkbox--child">
                                        <input type="checkbox" class="child-checkbox"
                                               name="minorGroup"
                                               value="${escapeHtml(child.code)}"
                                               data-parent="${escapeHtml(subMajor.code)}"
                                               ${filters.minorGroup.has(child.code) ? 'checked' : ''}>
                                        <span class="filter-checkbox-label">
                                            ${escapeHtml(child.name)}
                                            <span class="filter-checkbox-count">(${child.count})</span>
                                        </span>
                                    </label>
                                `).join('')}
                            </div>
                        </div>
                    `;
                });

                minorGroupOptions.innerHTML = html;

                // Update parent checkbox states after rendering
                updateParentStates();
            }
        }

        // Clear existing filters that no longer apply
        const validUnitGroups = new Set();
        results.forEach(r => {
            if (r.unit_group) {
                validUnitGroups.add(r.unit_group);
            }
        });
        filters.minorGroup.forEach(code => {
            if (!validUnitGroups.has(code)) {
                filters.minorGroup.delete(code);
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

        // Handle parent checkbox
        if (checkbox.classList.contains('parent-checkbox')) {
            handleParentCheckboxChange(checkbox);
            return;
        }

        // Handle child checkbox
        if (checkbox.classList.contains('child-checkbox')) {
            handleChildCheckboxChange(checkbox);
            return;
        }

        // Fallback for legacy checkboxes (non-hierarchical)
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
     * Handle parent checkbox change - select/deselect all children
     * @param {HTMLInputElement} parentCheckbox
     */
    function handleParentCheckboxChange(parentCheckbox) {
        const groupCode = parentCheckbox.dataset.group;
        const children = document.querySelectorAll(
            `input.child-checkbox[data-parent="${groupCode}"]`
        );

        children.forEach(child => {
            child.checked = parentCheckbox.checked;
            // Update filter state
            if (parentCheckbox.checked) {
                filters.minorGroup.add(child.value);
            } else {
                filters.minorGroup.delete(child.value);
            }
        });

        applyFilters();
        updateClearButton();
    }

    /**
     * Handle child checkbox change - update parent indeterminate state
     * @param {HTMLInputElement} childCheckbox
     */
    function handleChildCheckboxChange(childCheckbox) {
        const parentCode = childCheckbox.dataset.parent;
        const parent = document.querySelector(
            `input.parent-checkbox[data-group="${parentCode}"]`
        );

        // Update filter state
        if (childCheckbox.checked) {
            filters.minorGroup.add(childCheckbox.value);
        } else {
            filters.minorGroup.delete(childCheckbox.value);
        }

        // Update parent checkbox state
        if (parent) {
            const siblings = document.querySelectorAll(
                `input.child-checkbox[data-parent="${parentCode}"]`
            );
            const checkedCount = Array.from(siblings).filter(s => s.checked).length;

            parent.checked = checkedCount === siblings.length;
            parent.indeterminate = checkedCount > 0 && checkedCount < siblings.length;
        }

        applyFilters();
        updateClearButton();
    }

    /**
     * Update parent checkbox states (checked/indeterminate) based on children
     */
    function updateParentStates() {
        const parents = document.querySelectorAll('input.parent-checkbox');
        parents.forEach(parent => {
            const groupCode = parent.dataset.group;
            const children = document.querySelectorAll(
                `input.child-checkbox[data-parent="${groupCode}"]`
            );

            if (children.length === 0) return;

            const checkedCount = Array.from(children).filter(c => c.checked).length;

            parent.checked = checkedCount === children.length;
            parent.indeterminate = checkedCount > 0 && checkedCount < children.length;
        });
    }

    /**
     * Apply current filters and trigger callback
     */
    function applyFilters() {
        const filtered = allResults.filter(result => {
            // Check unit group filter (OR logic - any checked unit group matches)
            if (filters.minorGroup.size > 0) {
                if (!result.unit_group || !filters.minorGroup.has(result.unit_group)) {
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

        // Uncheck all checkboxes and reset indeterminate states
        const checkboxes = document.querySelectorAll('#filter-panel input[type="checkbox"]');
        checkboxes.forEach(cb => {
            cb.checked = false;
            cb.indeterminate = false;
        });

        applyFilters();
        updateClearButton();
    }

    /**
     * Update clear button state
     */
    function updateClearButton() {
        const activeCount = filters.minorGroup.size;

        if (clearButton) {
            clearButton.disabled = activeCount === 0;
        }

        if (activeIndicator) {
            if (activeCount > 0) {
                activeIndicator.innerHTML = '<span class="filter-active-count">' + activeCount + '</span>';
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
            minorGroup: Array.from(filters.minorGroup)
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
