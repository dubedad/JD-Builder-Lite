/**
 * Generation module for AI overview with SSE streaming.
 * Handles: trigger generation, stream tokens, track modifications, regenerate.
 */

const generation = {
    isGenerating: false,
    hasGenerated: false,
    isModified: false,
    eventSource: null,

    // DOM references (set in init)
    elements: {
        section: null,
        textarea: null,
        badge: null,
        generateBtn: null,
        regenerateBtn: null,
        errorDiv: null
    },

    init() {
        // Cache DOM elements
        this.elements = {
            section: document.getElementById('overview-section'),
            textarea: document.getElementById('overview-textarea'),
            badge: document.getElementById('ai-badge'),
            generateBtn: document.getElementById('generate-btn'),
            regenerateBtn: document.getElementById('regenerate-btn'),
            errorDiv: document.getElementById('overview-error')
        };

        // Bind event handlers
        this.elements.generateBtn?.addEventListener('click', () => this.startGeneration());
        this.elements.regenerateBtn?.addEventListener('click', () => this.startGeneration());
        this.elements.textarea?.addEventListener('input', () => this.handleEdit());

        // Subscribe to state changes for button updates
        if (window.store) {
            store.subscribe((state) => this.updateButtonState(state));
        }
    },

    /**
     * Update generate button based on selection count
     */
    updateButtonState(state) {
        const totalSelections = Object.values(state.selections)
            .reduce((sum, arr) => sum + arr.length, 0);

        if (this.elements.generateBtn) {
            this.elements.generateBtn.disabled = totalSelections === 0 || this.isGenerating;
            this.elements.generateBtn.textContent = this.isGenerating
                ? 'Generating...'
                : `Generate Overview (${totalSelections} selected)`;
        }
    },

    /**
     * Gather selected statements with full data for API request
     */
    gatherStatements() {
        const state = store.getState();
        const profile = window.currentProfile;
        if (!profile) return [];

        const statements = [];

        Object.entries(state.selections).forEach(([sectionId, selectedIds]) => {
            const sectionData = profile[sectionId];
            if (!sectionData || !sectionData.statements) return;

            selectedIds.forEach(stmtId => {
                const index = parseInt(stmtId.split('-').pop(), 10);
                const stmt = sectionData.statements[index];
                if (stmt) {
                    statements.push({
                        id: stmtId,
                        text: stmt.text,
                        source_attribute: stmt.source_attribute,
                        jd_element: sectionId
                    });
                }
            });
        });

        return statements;
    },

    /**
     * Build job context from current profile
     */
    buildContext() {
        const profile = window.currentProfile;
        if (!profile) return null;

        return {
            job_title: profile.title,
            noc_code: profile.noc_code,
            noc_title: profile.title,
            occupation_code: profile.metadata?.noc_code || null
        };
    },

    /**
     * Start generation (used for both initial and regenerate)
     */
    async startGeneration() {
        if (this.isGenerating) return;

        const statements = this.gatherStatements();
        const context = this.buildContext();

        if (statements.length === 0) {
            this.showError('Select at least one statement first.');
            return;
        }

        if (!context) {
            this.showError('No profile loaded.');
            return;
        }

        // Reset state
        this.isGenerating = true;
        this.isModified = false;
        this.hasGenerated = false;
        this.hideError();

        // Update UI
        this.elements.section.classList.remove('hidden');
        this.elements.textarea.value = '';
        this.elements.textarea.disabled = true;
        this.elements.textarea.classList.add('overview-textarea--streaming');
        this.elements.badge.textContent = 'Generating...';
        this.elements.badge.className = 'ai-badge ai-badge--generating';
        this.elements.regenerateBtn.disabled = true;
        this.updateButtonState(store.getState());

        try {
            // Send POST request to trigger generation
            const response = await fetch('/api/generate', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ statements, context })
            });

            if (!response.ok) {
                const error = await response.json();
                throw new Error(error.detail || error.error || 'Generation failed');
            }

            // Read SSE stream
            await this.consumeStream(response);

        } catch (error) {
            this.showError(error.message);
            this.resetGeneratingState();
        }
    },

    /**
     * Consume SSE stream from fetch response
     */
    async consumeStream(response) {
        const reader = response.body.getReader();
        const decoder = new TextDecoder();
        let buffer = '';

        try {
            while (true) {
                const { done, value } = await reader.read();

                if (done) {
                    // Stream ended without [DONE] signal
                    if (!this.hasGenerated) {
                        this.showError('Stream ended unexpectedly');
                    }
                    break;
                }

                // Decode chunk and add to buffer
                buffer += decoder.decode(value, { stream: true });

                // Process complete SSE messages
                const lines = buffer.split('\n\n');
                buffer = lines.pop() || ''; // Keep incomplete message in buffer

                for (const line of lines) {
                    if (line.startsWith('data: ')) {
                        const data = line.substring(6);
                        this.handleSSEMessage(data);
                    }
                }
            }
        } finally {
            this.resetGeneratingState();
        }
    },

    /**
     * Handle individual SSE message
     */
    handleSSEMessage(data) {
        if (data === '[DONE]') {
            this.hasGenerated = true;
            return;
        }

        if (data.startsWith('[ERROR]')) {
            const errorMsg = data.substring(8).trim();
            this.showError(errorMsg);
            return;
        }

        // Append token to textarea
        this.elements.textarea.value += data;

        // Auto-scroll to bottom
        this.elements.textarea.scrollTop = this.elements.textarea.scrollHeight;
    },

    /**
     * Reset UI after generation completes or fails
     */
    resetGeneratingState() {
        this.isGenerating = false;
        this.elements.textarea.disabled = false;
        this.elements.textarea.classList.remove('overview-textarea--streaming');
        this.elements.regenerateBtn.disabled = false;

        if (this.hasGenerated) {
            this.elements.badge.textContent = 'AI Generated';
            this.elements.badge.className = 'ai-badge';
        }

        this.updateButtonState(store.getState());
    },

    /**
     * Handle user editing the textarea
     */
    handleEdit() {
        if (this.isGenerating || !this.hasGenerated) return;

        if (!this.isModified) {
            this.isModified = true;
            this.elements.badge.textContent = 'AI-Generated (Modified)';
            this.elements.badge.className = 'ai-badge ai-badge--modified';

            // Notify backend for provenance tracking
            fetch('/api/mark-modified', { method: 'POST' })
                .catch(err => console.warn('Failed to mark as modified:', err));
        }
    },

    /**
     * Show error message
     */
    showError(message) {
        this.elements.errorDiv.textContent = message;
        this.elements.errorDiv.classList.remove('hidden');
    },

    /**
     * Hide error message
     */
    hideError() {
        this.elements.errorDiv.classList.add('hidden');
    },

    /**
     * Get current overview text and modified state
     */
    getOverview() {
        return {
            text: this.elements.textarea?.value || '',
            modified: this.isModified,
            generated: this.hasGenerated
        };
    }
};

// Export for other modules
window.generation = generation;

// Initialize function for main.js to call
function initGenerate() {
    generation.init();
}

window.initGenerate = initGenerate;
