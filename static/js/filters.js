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
        minorGroup: new Set(),
        ochroLevel: new Set(),    // Managerial Level
        ochroFunction: new Set()  // Job Function (parent; selecting function matches any of its families)
    };

    // Store all results for filtering
    let allResults = [];
    let renderCallback = null;

    // DOM references
    let minorGroupOptions = null;
    let ochroLevelOptions = null;
    let ochroFunctionOptions = null;
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
        minorGroupOptions = document.getElementById('filter-noc-broad-options');
        ochroLevelOptions = document.getElementById('filter-ochro-level-options');
        ochroFunctionOptions = document.getElementById('filter-ochro-function-options');
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

        // --- OCHRO: Managerial Level (flat checkboxes) ---
        if (ochroLevelOptions) {
            // Count unique results per level (a result can have multiple levels)
            const levelCounts = new Map();
            results.forEach(r => {
                if (!r.managerial_levels || !r.managerial_levels.length) return;
                // Use a Set to avoid counting the same result twice for the same level
                new Set(r.managerial_levels).forEach(lv => {
                    levelCounts.set(lv, (levelCounts.get(lv) || 0) + 1);
                });
            });

            if (levelCounts.size === 0) {
                ochroLevelOptions.innerHTML = '<p class="filter-empty">No OCHRO data in results</p>';
            } else {
                // Sort by seniority order
                const levelOrder = [
                    'Employee', 'Supervisor', 'Manager', 'Director or equivalent',
                    'Director General, Executive Director or equivalent',
                    'Assistant Deputy Minister or equivalent',
                    'Deputy Minister, Associate Deputy Minister or equivalent'
                ];
                const sortedLevels = Array.from(levelCounts.entries()).sort((a, b) => {
                    const ia = levelOrder.indexOf(a[0]);
                    const ib = levelOrder.indexOf(b[0]);
                    if (ia === -1 && ib === -1) return a[0].localeCompare(b[0]);
                    if (ia === -1) return 1;
                    if (ib === -1) return -1;
                    return ia - ib;
                });

                ochroLevelOptions.innerHTML = sortedLevels.map(([lv, count]) => `
                    <label class="filter-checkbox">
                        <input type="checkbox" class="ochro-level-checkbox"
                               name="ochroLevel" value="${escapeHtml(lv)}"
                               ${filters.ochroLevel.has(lv) ? 'checked' : ''}>
                        <span class="filter-checkbox-label">
                            ${escapeHtml(lv)}
                            <span class="filter-checkbox-count">(${count})</span>
                        </span>
                    </label>
                `).join('');
            }
        }

        // --- OCHRO: Job Function → Job Family (hierarchical) ---
        if (ochroFunctionOptions) {
            // Count unique RESULTS per function/family (not entries — one result can have many)
            const funcMap = new Map();
            results.forEach(r => {
                if (!r.ochro_entries || !r.ochro_entries.length) return;
                // Track which functions/families this result has already been counted in
                const seenFn = new Set();
                const seenFnFam = new Set();
                r.ochro_entries.forEach(entry => {
                    const fn = entry.function || '';
                    const fam = entry.family || '';
                    if (!fn) return;
                    if (!funcMap.has(fn)) {
                        funcMap.set(fn, { families: new Map(), resultCount: 0 });
                    }
                    const fnData = funcMap.get(fn);
                    // Count result once per function
                    if (!seenFn.has(fn)) {
                        fnData.resultCount++;
                        seenFn.add(fn);
                    }
                    // Count result once per function+family
                    if (fam) {
                        const famKey = fn + '||' + fam;
                        if (!seenFnFam.has(famKey)) {
                            fnData.families.set(fam, (fnData.families.get(fam) || 0) + 1);
                            seenFnFam.add(famKey);
                        }
                    }
                });
            });

            if (funcMap.size === 0) {
                ochroFunctionOptions.innerHTML = '<p class="filter-empty">No OCHRO data in results</p>';
            } else {
                const sortedFunctions = Array.from(funcMap.entries()).sort((a, b) => a[0].localeCompare(b[0]));
                ochroFunctionOptions.innerHTML = sortedFunctions.map(([fn, fnData]) => {
                    const sortedFamilies = Array.from(fnData.families.entries()).sort((a, b) => a[0].localeCompare(b[0]));
                    const childrenHtml = sortedFamilies.map(([fam, count]) => `
                        <label class="filter-checkbox filter-checkbox--child">
                            <input type="checkbox" class="ochro-family-checkbox"
                                   name="ochroFunction" value="${escapeHtml(fn + '||' + fam)}"
                                   data-function="${escapeHtml(fn)}"
                                   ${filters.ochroFunction.has(fn + '||' + fam) ? 'checked' : ''}>
                            <span class="filter-checkbox-label">
                                ${escapeHtml(fam)}
                                <span class="filter-checkbox-count">(${count})</span>
                            </span>
                        </label>
                    `).join('');

                    return `
                        <div class="filter-group">
                            <label class="filter-checkbox filter-checkbox--parent">
                                <input type="checkbox" class="ochro-function-checkbox"
                                       data-group="${escapeHtml(fn)}">
                                <strong>${escapeHtml(fn)}</strong>
                                <span class="filter-checkbox-count">(${fnData.resultCount})</span>
                            </label>
                            <div class="filter-group__children">${childrenHtml}</div>
                        </div>
                    `;
                }).join('');

                // Restore parent indeterminate states
                updateOchroParentStates();
            }
        }

        // Clear filters that no longer apply
        const validUnitGroups = new Set();
        const validLevels = new Set();
        const validFunctionFamilies = new Set();
        results.forEach(r => {
            if (r.unit_group) validUnitGroups.add(r.unit_group);
            if (r.managerial_levels) r.managerial_levels.forEach(lv => validLevels.add(lv));
            if (r.ochro_entries) r.ochro_entries.forEach(e => validFunctionFamilies.add((e.function || '') + '||' + (e.family || '')));
        });
        filters.minorGroup.forEach(code => { if (!validUnitGroups.has(code)) filters.minorGroup.delete(code); });
        filters.ochroLevel.forEach(lv => { if (!validLevels.has(lv)) filters.ochroLevel.delete(lv); });
        filters.ochroFunction.forEach(ff => { if (!validFunctionFamilies.has(ff)) filters.ochroFunction.delete(ff); });

        updateClearButton();
    }

    /**
     * Handle filter checkbox change
     * @param {Event} e - Change event
     */
    function handleFilterChange(e) {
        const checkbox = e.target;
        if (checkbox.type !== 'checkbox') return;

        // OCHRO checks must come before generic parent-checkbox to avoid misfiring

        // Handle OCHRO Managerial Level checkbox
        if (checkbox.classList.contains('ochro-level-checkbox')) {
            if (checkbox.checked) {
                filters.ochroLevel.add(checkbox.value);
            } else {
                filters.ochroLevel.delete(checkbox.value);
            }
            applyFilters();
            updateClearButton();
            return;
        }

        // Handle OCHRO Job Function checkbox (parent — select/deselect all families)
        if (checkbox.classList.contains('ochro-function-checkbox')) {
            const fn = checkbox.dataset.group;
            const children = document.querySelectorAll(
                `input.ochro-family-checkbox[data-function="${CSS.escape(fn)}"]`
            );
            children.forEach(child => {
                child.checked = checkbox.checked;
                if (checkbox.checked) {
                    filters.ochroFunction.add(child.value);
                } else {
                    filters.ochroFunction.delete(child.value);
                }
            });
            applyFilters();
            updateClearButton();
            return;
        }

        // Handle OCHRO Job Family checkbox (child)
        if (checkbox.classList.contains('ochro-family-checkbox')) {
            if (checkbox.checked) {
                filters.ochroFunction.add(checkbox.value);
            } else {
                filters.ochroFunction.delete(checkbox.value);
            }
            updateOchroParentStates();
            applyFilters();
            updateClearButton();
            return;
        }

        // Handle NOC parent checkbox
        if (checkbox.classList.contains('parent-checkbox')) {
            handleParentCheckboxChange(checkbox);
            return;
        }

        // Handle NOC child checkbox
        if (checkbox.classList.contains('child-checkbox')) {
            handleChildCheckboxChange(checkbox);
            return;
        }

        // Fallback for any remaining named checkboxes
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
     * Update OCHRO function (parent) checkbox states based on selected families (children)
     */
    function updateOchroParentStates() {
        const parents = document.querySelectorAll('input.ochro-function-checkbox');
        parents.forEach(parent => {
            const fn = parent.dataset.group;
            const children = document.querySelectorAll(`input.ochro-family-checkbox[data-function="${fn}"]`);
            if (!children.length) return;
            const checkedCount = Array.from(children).filter(c => c.checked).length;
            parent.checked = checkedCount === children.length;
            parent.indeterminate = checkedCount > 0 && checkedCount < children.length;
        });
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
            // OCHRO Managerial Level filter — result passes if any of its levels is checked
            if (filters.ochroLevel.size > 0) {
                const hasLevel = result.managerial_levels &&
                    result.managerial_levels.some(lv => filters.ochroLevel.has(lv));
                if (!hasLevel) return false;
            }

            // OCHRO Job Family filter — result passes if any of its function||family pairs is checked
            if (filters.ochroFunction.size > 0) {
                const hasFamily = result.ochro_entries &&
                    result.ochro_entries.some(e =>
                        filters.ochroFunction.has((e.function || '') + '||' + (e.family || ''))
                    );
                if (!hasFamily) return false;
            }

            // NOC unit group filter
            if (filters.minorGroup.size > 0) {
                if (!result.unit_group || !filters.minorGroup.has(result.unit_group)) {
                    return false;
                }
            }

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
        filters.ochroLevel.clear();
        filters.ochroFunction.clear();

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
        const activeCount = filters.minorGroup.size + filters.ochroLevel.size + filters.ochroFunction.size;

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
            minorGroup: Array.from(filters.minorGroup),
            ochroLevel: Array.from(filters.ochroLevel),
            ochroFunction: Array.from(filters.ochroFunction)
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
