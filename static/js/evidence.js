// Evidence highlighting module for Classification Step 1
// Manages side-by-side JD text view with highlighted evidence quotes

const evidenceModule = (function() {
    'use strict';

    // DOM element cache
    let elements = {};

    // Active highlights state
    let activeHighlights = [];

    /**
     * Initialize the module
     */
    function init() {
        elements = {
            evidencePanel: document.getElementById('evidence-panel'),
            jdTextViewer: document.getElementById('jd-text-viewer'),
            evidenceClose: document.getElementById('evidence-close')
        };

        // Listen for highlight requests from classify.js
        document.addEventListener('evidence-highlight-requested', handleHighlightRequest);

        // Bind close button
        elements.evidenceClose?.addEventListener('click', closePanel);

        console.log('[evidence.js] Module initialized');
    }

    /**
     * Handle evidence-highlight-requested event
     * @param {CustomEvent} event - Contains startChar, endChar, text
     */
    function handleHighlightRequest(event) {
        const { startChar, endChar, text } = event.detail;

        // Ensure JD text is rendered
        if (!elements.jdTextViewer?.innerHTML || elements.jdTextViewer.innerHTML.trim() === '') {
            renderJdText();
        }

        // Show panel
        elements.evidencePanel?.classList.remove('hidden');

        // Apply highlight
        highlightEvidence(text, startChar, endChar);
    }

    /**
     * Render JD text from currentJdText (set by classify.js)
     */
    function renderJdText() {
        const jdData = window.currentJdText;
        if (!jdData || !elements.jdTextViewer) return;

        let html = '';

        // Client-Service Results section
        if (jdData.client_service_results) {
            html += `
                <div class="jd-text-section">
                    <h4>Client-Service Results</h4>
                    <p class="jd-text-content" data-field="client_service_results">
                        ${escapeHtml(jdData.client_service_results)}
                    </p>
                </div>
            `;
        }

        // Key Activities section
        if (jdData.key_activities && jdData.key_activities.length > 0) {
            html += `
                <div class="jd-text-section">
                    <h4>Key Activities</h4>
                    <ul class="jd-activity-list">
                        ${jdData.key_activities.map((activity, idx) => `
                            <li data-field="key_activity_${idx}">${escapeHtml(activity)}</li>
                        `).join('')}
                    </ul>
                </div>
            `;
        }

        elements.jdTextViewer.innerHTML = html;
    }

    /**
     * Highlight evidence text in the JD viewer
     * Uses fuzzy matching if exact match fails
     * @param {string} evidenceText - Text to highlight
     * @param {number|null} startChar - Character offset (may be null)
     * @param {number|null} endChar - End character offset (may be null)
     */
    function highlightEvidence(evidenceText, startChar, endChar) {
        if (!elements.jdTextViewer || !evidenceText) return;

        // Clear previous active states (but keep highlights)
        clearActiveState();

        // Try to find the text in the rendered content
        const searchResult = findTextInViewer(evidenceText, startChar, endChar);

        if (searchResult.found) {
            insertHighlight(searchResult.node, searchResult.start, searchResult.end, evidenceText);
        } else {
            // Try fuzzy match
            const fuzzyResult = fuzzyFindText(evidenceText);
            if (fuzzyResult.found) {
                insertHighlight(fuzzyResult.node, fuzzyResult.start, fuzzyResult.end, evidenceText, true);
            } else {
                // Show "evidence not found" indicator
                showNotFoundIndicator(evidenceText);
            }
        }
    }

    /**
     * Find exact text match in viewer
     * @param {string} text - Text to find
     * @param {number|null} startChar - Character offset hint
     * @param {number|null} endChar - End character offset hint
     * @returns {Object} - {found: boolean, node: Node, start: number, end: number}
     */
    function findTextInViewer(text, startChar, endChar) {
        const walker = document.createTreeWalker(
            elements.jdTextViewer,
            NodeFilter.SHOW_TEXT,
            null,
            false
        );

        const normalizedSearch = normalizeText(text);

        while (walker.nextNode()) {
            const node = walker.currentNode;
            const normalizedContent = normalizeText(node.textContent);
            const idx = normalizedContent.indexOf(normalizedSearch);

            if (idx !== -1) {
                // Map back to original text position
                const originalIdx = mapNormalizedToOriginal(node.textContent, idx);
                const originalEnd = mapNormalizedToOriginal(node.textContent, idx + normalizedSearch.length);

                return {
                    found: true,
                    node: node,
                    start: originalIdx,
                    end: originalEnd
                };
            }
        }

        return { found: false };
    }

    /**
     * Fuzzy find text using similarity matching
     * @param {string} text - Text to find
     * @returns {Object} - {found: boolean, node: Node, start: number, end: number}
     */
    function fuzzyFindText(text) {
        const walker = document.createTreeWalker(
            elements.jdTextViewer,
            NodeFilter.SHOW_TEXT,
            null,
            false
        );

        const normalizedSearch = normalizeText(text);
        const minLength = Math.min(normalizedSearch.length, 20);
        let bestMatch = { found: false, similarity: 0 };

        while (walker.nextNode()) {
            const node = walker.currentNode;
            const normalizedContent = normalizeText(node.textContent);

            // Try sliding window for partial matches
            for (let i = 0; i <= normalizedContent.length - minLength; i++) {
                const window = normalizedContent.substring(i, i + normalizedSearch.length);
                const similarity = calculateSimilarity(normalizedSearch, window);

                if (similarity > 0.7 && similarity > bestMatch.similarity) {
                    const originalIdx = mapNormalizedToOriginal(node.textContent, i);
                    const originalEnd = mapNormalizedToOriginal(node.textContent, i + normalizedSearch.length);

                    bestMatch = {
                        found: true,
                        node: node,
                        start: originalIdx,
                        end: originalEnd,
                        similarity: similarity
                    };
                }
            }
        }

        return bestMatch;
    }

    /**
     * Normalize text for comparison (lowercase, remove extra whitespace)
     * @param {string} text - Text to normalize
     * @returns {string} - Normalized text
     */
    function normalizeText(text) {
        return text.toLowerCase().replace(/\s+/g, ' ').trim();
    }

    /**
     * Map normalized text position back to original position
     * @param {string} original - Original text
     * @param {number} normalizedIdx - Position in normalized text
     * @returns {number} - Position in original text
     */
    function mapNormalizedToOriginal(original, normalizedIdx) {
        let normalizedPos = 0;
        let originalPos = 0;

        while (normalizedPos < normalizedIdx && originalPos < original.length) {
            if (/\s/.test(original[originalPos])) {
                // Skip consecutive whitespace in original
                while (originalPos < original.length && /\s/.test(original[originalPos])) {
                    originalPos++;
                }
                normalizedPos++; // One space in normalized
            } else {
                originalPos++;
                normalizedPos++;
            }
        }

        return Math.min(originalPos, original.length);
    }

    /**
     * Calculate similarity between two strings (0-1)
     * Simple character-based similarity
     * @param {string} a - First string
     * @param {string} b - Second string
     * @returns {number} - Similarity score 0-1
     */
    function calculateSimilarity(a, b) {
        if (a === b) return 1;
        if (a.length === 0 || b.length === 0) return 0;

        const longer = a.length > b.length ? a : b;
        const shorter = a.length > b.length ? b : a;

        let matches = 0;
        for (let i = 0; i < shorter.length; i++) {
            if (shorter[i] === longer[i]) {
                matches++;
            }
        }

        return matches / longer.length;
    }

    /**
     * Insert highlight mark into text node
     * @param {Node} textNode - Text node to modify
     * @param {number} start - Start position
     * @param {number} end - End position
     * @param {string} evidenceText - Original evidence text (for aria-label)
     * @param {boolean} isFuzzy - Whether this is a fuzzy match
     */
    function insertHighlight(textNode, start, end, evidenceText, isFuzzy = false) {
        const text = textNode.textContent;

        // Clamp positions to valid range
        start = Math.max(0, Math.min(start, text.length));
        end = Math.max(start, Math.min(end, text.length));

        const before = text.substring(0, start);
        const highlighted = text.substring(start, end);
        const after = text.substring(end);

        // Create highlight mark element
        const mark = document.createElement('mark');
        mark.className = `evidence-highlight active scroll-target${isFuzzy ? ' evidence-fuzzy-match' : ''}`;
        mark.setAttribute('role', 'mark');
        mark.setAttribute('aria-label', `Evidence: ${evidenceText}`);
        mark.textContent = highlighted;

        // Replace text node with before + mark + after
        const fragment = document.createDocumentFragment();
        if (before) fragment.appendChild(document.createTextNode(before));
        fragment.appendChild(mark);
        if (after) fragment.appendChild(document.createTextNode(after));

        textNode.parentNode.replaceChild(fragment, textNode);

        // Track highlight
        activeHighlights.push(mark);

        // Scroll into view
        setTimeout(() => {
            mark.scrollIntoView({ behavior: 'smooth', block: 'center' });
            // Remove scroll animation class after animation completes
            setTimeout(() => mark.classList.remove('scroll-target'), 500);
        }, 100);
    }

    /**
     * Show indicator when evidence quote not found in JD
     * @param {string} evidenceText - The quote that wasn't found
     */
    function showNotFoundIndicator(evidenceText) {
        const indicator = document.createElement('div');
        indicator.className = 'evidence-not-found-banner';
        indicator.innerHTML = `
            <i class="fas fa-exclamation-triangle"></i>
            <span>Evidence quote not found in exact form: "${escapeHtml(truncateText(evidenceText, 50))}"</span>
        `;

        // Insert at top of viewer
        elements.jdTextViewer?.prepend(indicator);

        // Remove after 5 seconds
        setTimeout(() => indicator.remove(), 5000);
    }

    /**
     * Clear active state from highlights (keep the marks)
     */
    function clearActiveState() {
        document.querySelectorAll('.evidence-highlight.active').forEach(el => {
            el.classList.remove('active', 'scroll-target');
        });
    }

    /**
     * Clear all highlights and reset viewer
     */
    function clearAllHighlights() {
        activeHighlights = [];
        // Re-render JD text to remove all marks
        renderJdText();
    }

    /**
     * Close the evidence panel
     */
    function closePanel() {
        elements.evidencePanel?.classList.add('hidden');
        clearActiveState();
    }

    /**
     * Escape HTML special characters
     * @param {string} text - Text to escape
     * @returns {string} - Escaped text
     */
    function escapeHtml(text) {
        if (!text) return '';
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }

    /**
     * Truncate text with ellipsis
     * @param {string} text - Text to truncate
     * @param {number} maxLength - Max length
     * @returns {string} - Truncated text
     */
    function truncateText(text, maxLength) {
        if (!text || text.length <= maxLength) return text;
        return text.substring(0, maxLength - 3) + '...';
    }

    // Expose public API
    return {
        init,
        highlightEvidence,
        clearAllHighlights,
        closePanel,
        renderJdText
    };
})();

// Initialize on DOM ready
document.addEventListener('DOMContentLoaded', evidenceModule.init);
