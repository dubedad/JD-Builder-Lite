/**
 * Statement styling with AI-generated text
 * Handles /api/style calls and dual-format display
 */

/**
 * Style a single statement via API
 * @param {string} statementId - Statement ID (e.g., "key_activities-0")
 * @param {string} text - Original NOC statement text
 * @param {string} section - JD element (key_activities, skills, effort, responsibility)
 */
async function styleStatement(statementId, text, section) {
    const container = document.getElementById(`styled-${statementId}`);
    if (!container) return;

    try {
        const response = await fetch('/api/style', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                statement_id: statementId,
                text: text,
                section: section
            })
        });

        const data = await response.json();

        if (data.success) {
            displayStyledStatement(container, data.styled_statement);
        } else {
            console.error('Style generation failed:', data.error);
            // Hide container on failure
            container.style.display = 'none';
        }
    } catch (error) {
        console.error('Style API error:', error);
        container.style.display = 'none';
    }
}

/**
 * Display styled statement in container
 * @param {HTMLElement} container - The styled-statement-container element
 * @param {Object} styledData - API response styled_statement object
 */
function displayStyledStatement(container, styledData) {
    container.style.display = 'block';

    // Set fallback indicator
    if (styledData.is_fallback) {
        container.classList.add('is-fallback');
    } else {
        container.classList.remove('is-fallback');
    }

    // Confidence dot - per CONFIDENCE_THRESHOLDS: 0.8 high, 0.5 medium
    const dot = container.querySelector('.confidence-dot');
    const confidenceInfo = container.querySelector('.confidence-info');
    const score = styledData.confidence_score;

    dot.className = 'confidence-dot';
    if (score >= 0.8) {
        dot.classList.add('high');
        dot.title = `High confidence: ${(score * 100).toFixed(0)}%`;
    } else if (score >= 0.5) {
        dot.classList.add('medium');
        dot.title = `Medium confidence: ${(score * 100).toFixed(0)}%`;
    } else {
        dot.classList.add('low');
        dot.title = `Low confidence: ${(score * 100).toFixed(0)}%`;
    }

    confidenceInfo.textContent = `${(score * 100).toFixed(0)}% confidence`;

    // Styled text
    container.querySelector('.styled-text').textContent = styledData.styled_text;

    // Original text (collapsible)
    container.querySelector('.original-text-content').textContent = styledData.original_noc_text;

    // Update AI label based on content type
    const aiLabel = container.querySelector('.ai-styled-label');
    if (styledData.content_type === 'original_noc') {
        aiLabel.textContent = 'Using original NOC statement (styling not applied)';
    } else {
        aiLabel.textContent = 'AI-Styled using Job Description Samples';
    }

    // Store data for regeneration
    container.dataset.styledData = JSON.stringify(styledData);
}

/**
 * Toggle original text visibility
 * @param {HTMLElement} toggle - The toggle button element
 */
function toggleOriginalText(toggle) {
    const content = toggle.nextElementSibling;
    const icon = toggle.querySelector('i');
    const label = toggle.querySelector('span');

    if (content.classList.contains('show')) {
        content.classList.remove('show');
        icon.className = 'fas fa-chevron-right';
        label.textContent = 'Show original NOC statement';
    } else {
        content.classList.add('show');
        icon.className = 'fas fa-chevron-down';
        label.textContent = 'Hide original NOC statement';
    }
}

/**
 * Regenerate a styled statement
 * @param {HTMLElement} button - The regenerate button element
 */
async function regenerateStatement(button) {
    const statementId = button.dataset.statementId;
    const container = document.getElementById(`styled-${statementId}`);
    if (!container) return;

    // Get original text and section from stored data or DOM
    let text, section;
    try {
        const storedData = JSON.parse(container.dataset.styledData);
        text = storedData.original_noc_text;
    } catch (e) {
        // Fallback: get from original statement element
        const originalElement = document.querySelector(`[data-id="${statementId}"] .statement__text`);
        text = originalElement ? originalElement.textContent : '';
    }
    section = container.dataset.section;

    if (!text || !section) {
        console.error('Cannot regenerate: missing text or section');
        return;
    }

    // Show loading state
    button.classList.add('loading');
    button.disabled = true;

    try {
        await styleStatement(statementId, text, section);
    } finally {
        // Reset loading state
        button.classList.remove('loading');
        button.disabled = false;
    }
}

/**
 * Toggle between styled and original statement
 * @param {HTMLInputElement} checkbox - The use-original checkbox
 */
function toggleUseOriginal(checkbox) {
    const statementId = checkbox.dataset.statementId;
    const container = document.getElementById(`styled-${statementId}`);
    if (!container) return;

    const styledText = container.querySelector('.styled-text');
    const aiLabel = container.querySelector('.ai-styled-label');

    try {
        const storedData = JSON.parse(container.dataset.styledData);

        if (checkbox.checked) {
            // Use original
            styledText.textContent = storedData.original_noc_text;
            aiLabel.textContent = 'Using original NOC statement';
            container.classList.add('is-fallback');
        } else {
            // Use styled
            styledText.textContent = storedData.styled_text;
            if (storedData.content_type === 'original_noc') {
                aiLabel.textContent = 'Using original NOC statement (styling not applied)';
            } else {
                aiLabel.textContent = 'AI-Styled using Job Description Samples';
            }
            container.classList.remove('is-fallback');
        }
    } catch (e) {
        console.error('Cannot toggle: missing stored data');
    }
}

/**
 * Style all selected statements in a section
 * Called when user has selected statements and wants to style them
 * @param {string} section - JD element section
 */
async function styleSelectedStatements(section) {
    const selectedCheckboxes = document.querySelectorAll(
        `input.statement__checkbox[data-section="${section}"]:checked`
    );

    for (const checkbox of selectedCheckboxes) {
        const statementId = checkbox.dataset.id;
        const text = checkbox.closest('.statement')?.querySelector('.statement__text')?.textContent;

        if (statementId && text) {
            await styleStatement(statementId, text, section);
        }
    }
}

/**
 * Create styled statement container HTML
 * @param {string} statementId - Unique statement ID
 * @param {string} section - JD element section
 * @returns {string} HTML for styled statement container
 */
function createStyledStatementContainer(statementId, section) {
    return `
        <div class="styled-statement-container"
             id="styled-${statementId}"
             data-statement-id="${statementId}"
             data-section="${section}"
             style="display: none;">
            <div class="styled-header">
                <span class="confidence-dot" title="Confidence score"></span>
                <span class="confidence-info"></span>
            </div>
            <div class="styled-text"></div>
            <div class="original-text-toggle" onclick="toggleOriginalText(this)">
                <i class="fas fa-chevron-right"></i>
                <span>Show original NOC statement</span>
            </div>
            <div class="original-text-content"></div>
            <div class="ai-styled-label">AI-Styled using Job Description Samples</div>
            <div class="statement-controls">
                <button class="regenerate-btn" onclick="regenerateStatement(this)"
                        data-statement-id="${statementId}">
                    <span class="spinner"></span>
                    <span class="btn-text"><i class="fas fa-sync-alt"></i> Regenerate</span>
                </button>
                <label class="use-original-toggle">
                    <input type="checkbox" onchange="toggleUseOriginal(this)"
                           data-statement-id="${statementId}">
                    Use original
                </label>
            </div>
        </div>
    `;
}

// Export functions for use in other modules
window.styleStatement = styleStatement;
window.displayStyledStatement = displayStyledStatement;
window.toggleOriginalText = toggleOriginalText;
window.regenerateStatement = regenerateStatement;
window.toggleUseOriginal = toggleUseOriginal;
window.styleSelectedStatements = styleSelectedStatements;
window.createStyledStatementContainer = createStyledStatementContainer;
