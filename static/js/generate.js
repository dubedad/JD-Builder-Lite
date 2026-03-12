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
            errorDiv: document.getElementById('overview-error'),
            additionalContext: document.getElementById('additional-context'),
            outputContainer: document.getElementById('generate-output')
        };

        // Bind event handlers
        this.elements.generateBtn?.addEventListener('click', () => this.startGeneration());
        this.elements.regenerateBtn?.addEventListener('click', () => this.startGeneration());
        this.elements.textarea?.addEventListener('input', () => this.handleEdit());
    },

    /**
     * Update generate button to show generating state
     * (selection.js handles the count display via updateActionBar)
     */
    setGeneratingState(generating) {
        if (this.elements.generateBtn) {
            if (generating) {
                this.elements.generateBtn.disabled = true;
                this.elements.generateBtn.textContent = 'Generating...';
            }
            // When not generating, let selection.js restore the button via store subscription
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
        if (this.elements.outputContainer) this.elements.outputContainer.classList.remove('hidden');
        this.elements.textarea.textContent = '';
        this.elements.textarea.classList.add('generate-output__prose--streaming');
        this.elements.badge.textContent = 'Generating...';
        this.elements.badge.className = 'badge badge--ai-generated ai-badge--generating';
        this.elements.regenerateBtn.disabled = true;
        this.setGeneratingState(true);

        const additionalContext = this.elements.additionalContext?.value?.trim() || '';

        try {
            // Send POST request to trigger generation
            const response = await fetch('/api/generate', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ statements, context, additional_context: additionalContext })
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

        // Append token to contenteditable div
        this.elements.textarea.textContent += data;

        // Auto-scroll to bottom
        this.elements.textarea.scrollIntoView({ block: 'end', behavior: 'smooth' });
    },

    /**
     * Reset UI after generation completes or fails
     */
    resetGeneratingState() {
        this.isGenerating = false;
        this.elements.textarea.classList.remove('generate-output__prose--streaming');
        this.elements.regenerateBtn.disabled = false;

        if (this.hasGenerated) {
            this.elements.badge.textContent = 'AI Generated';
            this.elements.badge.className = 'badge badge--ai-generated';

            // Fetch and store AI metadata for export compliance appendix
            this.fetchAIMetadata();
        }

        // Trigger store notification to restore button state via selection.js
        store.notify();
    },

    /**
     * Fetch AI generation metadata from session for export
     */
    async fetchAIMetadata() {
        try {
            const response = await fetch('/api/generation-metadata');
            if (response.ok) {
                const metadata = await response.json();
                if (metadata) {
                    window.aiGenerationMetadata = metadata;
                }
            }
        } catch (error) {
            console.warn('Failed to fetch AI metadata:', error);
        }
    },

    /**
     * Handle user editing the textarea
     */
    handleEdit() {
        if (this.isGenerating || !this.hasGenerated) return;

        if (!this.isModified) {
            this.isModified = true;
            this.elements.badge.textContent = 'AI-Generated (Modified)';
            this.elements.badge.className = 'badge badge--ai-generated ai-badge--modified';

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
            text: this.elements.textarea?.textContent || '',
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
