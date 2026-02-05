/**
 * Tab Controller - click and keyboard navigation per W3C ARIA Authoring Practices
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

        // Bind keyboard navigation to tablist
        this.tablist.addEventListener('keydown', this.onKeydown.bind(this));

        // Set initial state - first tab active
        this.activateTab(0);
    }

    /**
     * Handle keyboard navigation within tablist
     * - ArrowRight: next tab with wrap-around
     * - ArrowLeft: previous tab with wrap-around
     * - Home: first tab
     * - End: last tab
     */
    onKeydown(event) {
        const currentIndex = this.tabs.indexOf(document.activeElement);
        if (currentIndex === -1) return;

        let targetIndex = currentIndex;

        switch (event.key) {
            case 'ArrowRight':
                targetIndex = (currentIndex + 1) % this.tabs.length;
                break;
            case 'ArrowLeft':
                targetIndex = (currentIndex - 1 + this.tabs.length) % this.tabs.length;
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
