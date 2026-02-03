/**
 * Simple Tab Controller - click to switch tabs
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

        // Bind click handlers to each tab
        this.tabs.forEach((tab, i) => {
            tab.addEventListener('click', () => this.activateTab(i));
        });

        // Set initial state - first tab active
        this.activateTab(0);
    }

    activateTab(index) {
        // Update aria-selected on all tabs
        this.tabs.forEach((tab, i) => {
            const isActive = i === index;
            tab.setAttribute('aria-selected', isActive);
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
