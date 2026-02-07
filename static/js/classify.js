// Classification UI module for Step 5: Occupational Group Allocation
// Handles allocation API calls and renders recommendation cards

const classifyModule = (function() {
    'use strict';

    // Confidence tier thresholds (per CONTEXT.md - Claude's discretion)
    const CONFIDENCE_THRESHOLDS = {
        HIGH: 0.70,
        MEDIUM: 0.40
    };

    // TBS Occupational Group names lookup
    // Source: https://www.canada.ca/en/treasury-board-secretariat/services/collective-agreements/occupational-groups/definitions.html
    const OCCUPATIONAL_GROUP_NAMES = {
        'AC': 'Actuarial Science',
        'AI': 'Air Traffic Control',
        'AO': 'Aircraft Operations',
        'AR': 'Architecture and Town Planning',
        'AS': 'Administrative Services',
        'AU': 'Auditing',
        'BI': 'Biological Sciences',
        'CH': 'Chemistry',
        'CM': 'Communications',
        'CO': 'Commerce',
        'CR': 'Clerical and Regulatory',
        'CS': 'Computer Systems',
        'CX': 'Correctional Services',
        'DA': 'Data Processing',
        'DD': 'Drafting and Illustration',
        'DE': 'Dentistry',
        'DS': 'Defence Scientific Services',
        'EC': 'Economics and Social Science Services',
        'ED': 'Education',
        'EG': 'Engineering and Scientific Support',
        'EL': 'Electronics',
        'EN': 'Engineering',
        'ES': 'Economics, Sociology and Statistics',
        'EU': 'Engineering and Land Survey',
        'EX': 'Executive',
        'FB': 'Border Services',
        'FI': 'Financial Administration',
        'FO': 'Forestry',
        'FR': 'Firefighters',
        'FS': 'Foreign Service',
        'GL': 'General Labour and Trades',
        'GS': 'General Services',
        'GT': 'General Technical',
        'HP': 'Heating, Power and Stationary Plant Operations',
        'HR': 'Historical Research',
        'HS': 'Health Services',
        'IT': 'Information Technology',
        'LA': 'Law',
        'LS': 'Library Science',
        'MA': 'Mathematics',
        'MD': 'Medicine',
        'MT': 'Meteorology',
        'ND': 'Nutrition and Dietetics',
        'NU': 'Nursing',
        'OM': 'Organization and Methods',
        'OP': 'Occupational and Physical Therapy',
        'PC': 'Physical Sciences',
        'PE': 'Personnel Administration',
        'PG': 'Purchasing and Supply',
        'PH': 'Pharmacy',
        'PI': 'Primary Products Inspection',
        'PM': 'Programme Administration',
        'PO': 'Police Operations Support',
        'PR': 'Printing Operations',
        'PS': 'Psychology',
        'RE': 'Research',
        'RO': 'Radio Operations',
        'SC': 'Ships\' Crews',
        'SE': 'Scientific Research',
        'SG': 'Scientific Regulation',
        'SI': 'Social Work',
        'SO': 'Ships\' Officers',
        'SR': 'Scientific Research',
        'ST': 'Secretarial, Stenographic and Typing',
        'SW': 'Social Work',
        'TI': 'Technical Inspection',
        'TR': 'Translation',
        'UT': 'University Teaching',
        'VM': 'Veterinary Medicine',
        'WP': 'Welfare Programmes'
    };

    // DOM element cache
    let elements = {};

    // Current allocation response (for evidence highlighting)
    let currentAllocation = null;

    /**
     * Initialize the module - cache DOM references and bind events
     */
    function init() {
        elements = {
            section: document.getElementById('classify-section'),
            loading: document.getElementById('classify-loading'),
            results: document.getElementById('classify-results'),
            error: document.getElementById('classify-error'),
            statusBadge: document.getElementById('classify-status-badge'),
            recommendationsPanel: document.getElementById('recommendations-panel'),
            evidencePanel: document.getElementById('evidence-panel'),
            jdTextViewer: document.getElementById('jd-text-viewer'),
            evidenceClose: document.getElementById('evidence-close'),
            complete: document.getElementById('classify-complete')
        };

        // Listen for classify-requested event from main.js
        document.addEventListener('classify-requested', handleClassifyRequest);

        // Bind evidence panel close button
        if (elements.evidenceClose) {
            elements.evidenceClose.addEventListener('click', closeEvidencePanel);
        }

        console.log('[classify.js] Module initialized');
    }

    /**
     * Handle classify-requested event - call allocation API
     * @param {CustomEvent} event - Contains profile and selections
     */
    async function handleClassifyRequest(event) {
        const { profile, selections } = event.detail;

        if (!profile) {
            showError('No job profile loaded. Please complete Steps 1-3 first.');
            return;
        }

        // Build JD data from profile and selections
        const jdData = buildJdDataFromProfile(profile, selections);

        if (!jdData.key_activities || jdData.key_activities.length === 0) {
            showError('At least one Key Activity is required. Please select activities in Step 3.');
            return;
        }

        // v4.0: Client-Service Results is optional - use position title as fallback
        if (!jdData.client_service_results || jdData.client_service_results.length < 10) {
            // Construct fallback from position title for classification context
            jdData.client_service_results = `Position: ${jdData.position_title}`;
        }

        // Show loading state
        showLoading();

        try {
            const response = await api.allocate(
                jdData.position_title,
                jdData.client_service_results,
                jdData.key_activities,
                jdData.skills,
                jdData.labels,
                0.3 // minimum_confidence
            );

            currentAllocation = response;
            renderResults(response, jdData);

        } catch (err) {
            console.error('[classify.js] Allocation failed:', err);
            showError(err.message || 'Allocation failed. Please try again.');
        }
    }

    /**
     * Build JD data object from profile and user selections
     * @param {Object} profile - Current OaSIS profile
     * @param {Object} selections - User's statement selections from store
     * @returns {Object} JD data for allocation API
     */
    function buildJdDataFromProfile(profile, selections) {
        // Position title from profile
        const positionTitle = profile.title || 'Untitled Position';

        // Client-Service Results from lead statement + selected statements
        let clientServiceResults = profile.reference_attributes?.lead_statement || '';

        // Key activities from selections
        const keyActivities = [];
        if (selections?.key_activities && Array.isArray(selections.key_activities)) {
            // selections.key_activities is array of statement IDs like "key_activities-0"
            // We need to look up the actual text from profile
            const allStatements = profile.key_activities?.statements || [];
            selections.key_activities.forEach(stmtId => {
                // Parse index from ID like "key_activities-3"
                const match = stmtId.match(/key_activities-(\d+)/);
                if (match) {
                    const idx = parseInt(match[1], 10);
                    const stmt = allStatements[idx];
                    if (stmt) {
                        const text = typeof stmt === 'string' ? stmt : (stmt.text || stmt.statement || '');
                        if (text.trim()) {
                            keyActivities.push(text.trim());
                        }
                    }
                }
            });
        }

        // If no key activities selected, try to use profile's activities
        if (keyActivities.length === 0 && profile.key_activities?.statements) {
            profile.key_activities.statements.slice(0, 5).forEach(stmt => {
                const text = typeof stmt === 'string' ? stmt : (stmt.text || stmt.statement || '');
                if (text.trim()) {
                    keyActivities.push(text.trim());
                }
            });
        }

        // Skills from selections
        const skills = [];
        if (selections?.skills && Array.isArray(selections.skills)) {
            const allSkills = profile.skills?.statements || [];
            selections.skills.forEach(stmtId => {
                const match = stmtId.match(/skills-(\d+)/);
                if (match) {
                    const idx = parseInt(match[1], 10);
                    const stmt = allSkills[idx];
                    if (stmt) {
                        const text = typeof stmt === 'string' ? stmt : (stmt.text || stmt.statement || '');
                        if (text.trim()) {
                            skills.push(text.trim());
                        }
                    }
                }
            });
        }

        // NOC labels from profile
        const labels = profile.noc_code ? [profile.noc_code.split('.')[0]] : null;

        return {
            position_title: positionTitle,
            client_service_results: clientServiceResults,
            key_activities: keyActivities,
            skills: skills.length > 0 ? skills : null,
            labels: labels
        };
    }

    /**
     * Show loading state
     */
    function showLoading() {
        if (elements.loading) elements.loading.classList.remove('hidden');
        if (elements.results) elements.results.classList.add('hidden');
        if (elements.error) elements.error.classList.add('hidden');
        if (elements.complete) elements.complete.classList.add('hidden');
        if (elements.statusBadge) {
            elements.statusBadge.classList.remove('success', 'warning', 'error');
            elements.statusBadge.classList.add('analyzing');
            elements.statusBadge.textContent = 'Analyzing...';
        }
    }

    /**
     * Show error message
     * @param {string} message - Error message to display
     */
    function showError(message) {
        if (elements.loading) elements.loading.classList.add('hidden');
        if (elements.results) elements.results.classList.add('hidden');
        if (elements.error) {
            elements.error.classList.remove('hidden');
            elements.error.textContent = message;
        }
        if (elements.statusBadge) {
            elements.statusBadge.classList.remove('analyzing', 'success', 'warning');
            elements.statusBadge.classList.add('error');
            elements.statusBadge.textContent = 'Error';
        }
    }

    /**
     * Render allocation results
     * @param {Object} response - AllocationResponse from API
     * @param {Object} jdData - Original JD data sent to API
     */
    function renderResults(response, jdData) {
        console.log('[classify.js] renderResults called with:', {
            status: response.status,
            recommendationsCount: response.recommendations?.length || 0,
            borderlineFlag: response.borderline_flag,
            hasProvenanceMap: !!response.provenance_map
        });

        if (elements.loading) elements.loading.classList.add('hidden');
        if (elements.error) elements.error.classList.add('hidden');
        if (elements.results) elements.results.classList.remove('hidden');

        // Show position title being classified
        const positionTitleEl = document.getElementById('classify-position-title');
        if (positionTitleEl && jdData.position_title) {
            positionTitleEl.textContent = `Classifying: ${jdData.position_title}`;
        }

        // Update status badge based on response status
        updateStatusBadge(response.status, response.borderline_flag);

        // Clear and render recommendation cards
        if (elements.recommendationsPanel) {
            elements.recommendationsPanel.innerHTML = '';

            // Show recommendations or "no recommendations" message
            if (response.recommendations && response.recommendations.length > 0) {
                renderRecommendationCards(response.recommendations, response.provenance_map);
            } else {
                // Create no-recommendations message dynamically
                const noRecsMsg = document.createElement('p');
                noRecsMsg.className = 'no-recommendations';
                noRecsMsg.textContent = 'No occupational group recommendations could be determined. Try selecting more activities or skills.';
                elements.recommendationsPanel.appendChild(noRecsMsg);
            }
        }

        // Store JD text for evidence highlighting
        storeJdTextForEvidence(jdData);

        // Show complete section when recommendations are present
        if (response.recommendations && response.recommendations.length > 0 && elements.complete) {
            elements.complete.classList.remove('hidden');
        }

        // Handle edge cases
        if (response.status === 'needs_clarification' && response.clarification_needed) {
            renderClarificationWarning(response.clarification_needed);
        }

        if (response.status === 'invalid_combination' && response.conflicting_duties) {
            renderConflictingDutiesWarning(response.conflicting_duties);
        }

        if (response.warnings && response.warnings.length > 0) {
            renderWarnings(response.warnings);
        }
    }

    /**
     * Update status badge based on allocation result
     * @param {string} status - success | needs_clarification | invalid_combination
     * @param {boolean} borderlineFlag - True if borderline case
     */
    function updateStatusBadge(status, borderlineFlag) {
        if (!elements.statusBadge) return;

        elements.statusBadge.classList.remove('analyzing', 'success', 'warning', 'error');

        let text = 'Complete';
        let badgeClass = 'success';

        if (status === 'needs_clarification') {
            text = 'Needs Clarification';
            badgeClass = 'warning';
        } else if (status === 'invalid_combination') {
            text = 'Invalid Combination';
            badgeClass = 'error';
        } else if (borderlineFlag) {
            text = 'Borderline - Review Recommended';
            badgeClass = 'warning';
        }

        elements.statusBadge.classList.add(badgeClass);
        elements.statusBadge.textContent = text;
    }

    /**
     * Get confidence tier based on score
     * @param {number} confidence - Confidence score 0.0-1.0
     * @returns {string} - 'high' | 'medium' | 'low'
     */
    function getConfidenceTier(confidence) {
        if (confidence >= CONFIDENCE_THRESHOLDS.HIGH) return 'high';
        if (confidence >= CONFIDENCE_THRESHOLDS.MEDIUM) return 'medium';
        return 'low';
    }

    /**
     * Get confidence tier label
     * @param {string} tier - 'high' | 'medium' | 'low'
     * @returns {string} - Human readable label
     */
    function getConfidenceTierLabel(tier) {
        const labels = { high: 'High', medium: 'Medium', low: 'Low' };
        return labels[tier] || 'Unknown';
    }

    /**
     * Render recommendation cards
     * @param {Array} recommendations - Array of GroupRecommendation objects
     * @param {Object} provenanceMap - Dict keyed by group_code
     */
    function renderRecommendationCards(recommendations, provenanceMap) {
        console.log('[classify.js] renderRecommendationCards called with', recommendations?.length, 'recommendations');

        if (!elements.recommendationsPanel) {
            console.error('[classify.js] recommendationsPanel element not found!');
            return;
        }

        if (!recommendations || recommendations.length === 0) {
            elements.recommendationsPanel.innerHTML = `
                <div class="classify-warning">
                    <h4><i class="fas fa-exclamation-triangle"></i> No Recommendations</h4>
                    <p>No occupational groups met the minimum confidence threshold. Consider adding more detail to your job description.</p>
                </div>
            `;
            return;
        }

        recommendations.forEach((rec, index) => {
            const rank = index + 1;
            const isTop = rank === 1;
            const tier = getConfidenceTier(rec.confidence);
            const provenance = provenanceMap ? provenanceMap[rec.group_code] : null;

            // DEBUG: Trace data reaching card rendering
            console.log(`[DEBUG-20] Card ${rank} (${rec.group_code}):`, {
                hasProvenanceMap: !!provenanceMap,
                provenanceMapKeys: provenanceMap ? Object.keys(provenanceMap) : [],
                provenance: provenance,
                provenanceUrl: provenance?.url,
                fallbackUrl: rec.provenance_url,
                evidenceSpansCount: rec.evidence_spans?.length || 0,
                evidenceSpans: rec.evidence_spans,
                reasoningStepsCount: rec.reasoning_steps?.length || 0
            });

            const card = document.createElement('article');
            card.className = `recommendation-card confidence-${tier}${isTop ? ' top-recommendation' : ''}`;
            card.setAttribute('aria-expanded', 'false');
            card.setAttribute('tabindex', '0');

            card.innerHTML = `
                <div class="card-summary" role="button" aria-controls="card-details-${rank}">
                    <span class="card-rank">${rank}</span>
                    <div class="card-main">
                        <div class="card-title">
                            <span class="card-group-code">${escapeHtml(rec.group_code)}</span>
                            <span class="card-group-name">- ${escapeHtml(getGroupName(rec))}</span>
                        </div>
                        <p class="card-rationale-summary">${escapeHtml(truncateText(rec.definition_fit_rationale, 80))}</p>
                    </div>
                    <div class="card-confidence">
                        <span class="confidence-percentage">${Math.round(rec.confidence * 100)}%</span>
                        <div class="confidence-bar">
                            <div class="confidence-bar-fill" style="width: ${rec.confidence * 100}%"></div>
                        </div>
                        <span class="confidence-badge">${getConfidenceTierLabel(tier)}</span>
                    </div>
                    <i class="fas fa-chevron-down card-expand-icon" aria-hidden="true"></i>
                </div>

                <div class="card-details" id="card-details-${rank}">
                    <div class="detail-section">
                        <h4><i class="fas fa-info-circle"></i> Full Rationale</h4>
                        <p>${escapeHtml(rec.definition_fit_rationale)}</p>
                    </div>

                    ${renderEvidenceSection(rec.evidence_spans)}

                    ${renderInclusionExclusionSection(rec)}

                    ${renderConfidenceBreakdown(rec.confidence_breakdown)}

                    ${renderProvenanceSection(provenance, rec.group_code, rec.provenance_url)}
                </div>
            `;

            // Bind expand/collapse
            const summary = card.querySelector('.card-summary');
            summary.addEventListener('click', () => toggleCardExpand(card));
            card.addEventListener('keydown', (e) => {
                if (e.key === 'Enter' || e.key === ' ') {
                    e.preventDefault();
                    toggleCardExpand(card);
                }
            });

            elements.recommendationsPanel.appendChild(card);
        });
    }

    /**
     * Get group name from recommendation
     * @param {Object} rec - GroupRecommendation object
     * @returns {string} - Group name or code as fallback
     */
    function getGroupName(rec) {
        // Look up full group name from TBS definitions
        return OCCUPATIONAL_GROUP_NAMES[rec.group_code] || rec.group_code;
    }

    /**
     * Render evidence section with clickable links
     * @param {Array} evidenceSpans - Array of EvidenceSpan objects
     * @returns {string} - HTML string
     */
    function renderEvidenceSection(evidenceSpans) {
        if (!evidenceSpans || evidenceSpans.length === 0) {
            return '';
        }

        const quotes = evidenceSpans.map((span, idx) => {
            // Format field source - show helpful text instead of "Unknown"
            const fieldSource = span.field && span.field !== 'Unknown'
                ? span.field
                : 'Job Description';

            return `
                <blockquote>
                    "${escapeHtml(span.text)}"
                    <footer>
                        <cite>from ${escapeHtml(fieldSource)}</cite>
                        <button class="evidence-link" data-start="${span.start_char ?? ''}" data-end="${span.end_char ?? ''}" data-text="${escapeHtml(span.text)}">
                            <i class="fas fa-highlight"></i> Highlight in JD
                        </button>
                    </footer>
                </blockquote>
            `;
        }).join('');

        return `
            <div class="detail-section">
                <h4><i class="fas fa-quote-left"></i> Supporting Evidence</h4>
                ${quotes}
            </div>
        `;
    }

    /**
     * Render inclusion/exclusion check section with explanatory context
     * @param {Object} rec - GroupRecommendation object
     * @returns {string} - HTML string
     */
    function renderInclusionExclusionSection(rec) {
        // Format inclusion check with context
        const inclusionText = rec.inclusion_check || 'Not evaluated';
        const inclusionExplanation = inclusionText.toLowerCase().includes('none applies')
            ? 'No specific inclusion statements matched. The job was classified based on definition fit alone.'
            : inclusionText;

        // Format exclusion check with context
        const exclusionText = rec.exclusion_check || 'Not evaluated';
        const exclusionExplanation = exclusionText.toLowerCase().includes('no exclusion')
            ? 'No exclusion criteria conflict with this classification. The job duties are compatible with this group.'
            : exclusionText;

        return `
            <div class="detail-section">
                <h4><i class="fas fa-check-circle"></i> Allocation Checks</h4>
                <div class="allocation-check">
                    <p>
                        <strong title="Inclusion statements describe work that typically belongs to this group">Inclusions:</strong>
                        <span class="allocation-check-text">${escapeHtml(inclusionExplanation)}</span>
                    </p>
                </div>
                <div class="allocation-check">
                    <p>
                        <strong title="Exclusion statements describe work that does NOT belong to this group">Exclusions:</strong>
                        <span class="allocation-check-text">${escapeHtml(exclusionExplanation)}</span>
                    </p>
                </div>
            </div>
        `;
    }

    /**
     * Render confidence breakdown grid with tooltips
     * @param {Object} breakdown - Dict of component scores
     * @returns {string} - HTML string
     */
    function renderConfidenceBreakdown(breakdown) {
        if (!breakdown) return '';

        // Labels and tooltips for each confidence component
        const metrics = {
            definition_fit: {
                label: 'Definition Fit',
                tooltip: 'How well the job duties match the occupational group definition (LLM assessment)'
            },
            semantic_similarity: {
                label: 'Semantic Match',
                tooltip: 'Text similarity between job description and group definition (algorithmic score)'
            },
            labels_boost: {
                label: 'Labels Boost',
                tooltip: 'Additional confidence from matching NOC labels or occupation codes'
            },
            inclusion_support: {
                label: 'Inclusion Support',
                tooltip: 'Whether specific inclusion criteria for this group were met'
            },
            exclusion_clear: {
                label: 'Exclusion Clear',
                tooltip: 'Confirms no exclusion criteria disqualify this classification'
            },
            exclusion_penalty: {
                label: 'Exclusion Penalty',
                tooltip: 'Confidence reduction applied when job duties partially match an exclusion statement'
            }
        };

        const items = Object.entries(breakdown)
            .filter(([key, value]) => value !== undefined && value !== null)
            .map(([key, value]) => {
                const metric = metrics[key] || { label: key, tooltip: '' };
                return `
                    <div class="breakdown-item" title="${escapeHtml(metric.tooltip)}">
                        <span class="breakdown-label">${metric.label}</span>
                        <span class="breakdown-value">${typeof value === 'number' ? (value * 100).toFixed(0) + '%' : value}</span>
                    </div>
                `;
            }).join('');

        if (!items) return '';

        return `
            <div class="detail-section">
                <h4><i class="fas fa-chart-bar"></i> Confidence Breakdown</h4>
                <p class="breakdown-hint">Hover over each metric for explanation</p>
                <div class="confidence-breakdown">
                    ${items}
                </div>
            </div>
        `;
    }

    /**
     * Render provenance section with expandable tree structure
     * @param {Object} provenance - ProvenanceDetail object
     * @param {string} groupCode - Group code for display
     * @param {string} fallbackUrl - Fallback URL from recommendation
     * @returns {string} - HTML string
     */
    function renderProvenanceSection(provenance, groupCode, fallbackUrl) {
        let url = provenance?.url || fallbackUrl;
        if (!url) {
            return '';
        }

        // Add anchor to TBS definitions page for direct navigation to group
        // TBS page uses lowercase group codes as anchors (e.g., #as, #cm)
        if (url.includes('definitions.html') && groupCode && !url.includes('#')) {
            url = `${url}#${groupCode.toLowerCase()}`;
        }

        const groupName = OCCUPATIONAL_GROUP_NAMES[groupCode] || groupCode;
        const sourceType = provenance?.source_type || 'TBS Occupational Group Definition';
        const scrapedAt = provenance?.scraped_at;

        // Get definition text - prefer from provenance, fallback to group description
        const definitionText = provenance?.definition || `${groupCode} - ${groupName}`;

        return `
            <div class="detail-section">
                <h4><i class="fas fa-sitemap"></i> Source Provenance</h4>
                <div class="provenance-tree">
                    <!-- Level 1: Recommendation -->
                    <div class="provenance-tree-item">
                        <span class="provenance-tree-icon"><i class="fas fa-star"></i></span>
                        <div class="provenance-tree-content">
                            <span class="provenance-tree-label">Recommendation:</span>
                            <span class="provenance-tree-value">${escapeHtml(groupCode)} - ${escapeHtml(groupName)}</span>
                        </div>
                    </div>

                    <!-- Level 2: Definition (expandable) -->
                    <div class="provenance-tree-item">
                        <span class="provenance-tree-icon"><i class="fas fa-book"></i></span>
                        <div class="provenance-tree-content">
                            <span class="provenance-tree-label">Definition Source:</span>
                            <span class="provenance-tree-value">${escapeHtml(sourceType)}</span>
                            <div class="provenance-expandable" aria-expanded="false">
                                <button class="provenance-expand-btn" type="button" onclick="this.parentElement.setAttribute('aria-expanded', this.parentElement.getAttribute('aria-expanded') === 'true' ? 'false' : 'true')">
                                    <i class="fas fa-chevron-right"></i> View full definition
                                </button>
                                <div class="provenance-detail-content">
                                    ${escapeHtml(definitionText)}
                                </div>
                            </div>
                        </div>
                    </div>

                    <!-- Level 3: TBS Source Link -->
                    <div class="provenance-tree-item">
                        <span class="provenance-tree-icon"><i class="fas fa-external-link-alt"></i></span>
                        <div class="provenance-tree-content">
                            <span class="provenance-tree-label">Authoritative Source:</span>
                            <a href="${escapeHtml(url)}" target="_blank" rel="noopener noreferrer" class="provenance-tree-link">
                                View TBS Definition for ${escapeHtml(groupCode)}
                            </a>
                            ${scrapedAt ? `
                            <div class="provenance-tree-meta">
                                Data scraped: ${new Date(scrapedAt).toLocaleDateString()}
                            </div>
                            ` : ''}
                        </div>
                    </div>
                </div>
            </div>
        `;
    }

    /**
     * Toggle card expand/collapse state
     * @param {HTMLElement} card - Card element
     */
    function toggleCardExpand(card) {
        const isExpanded = card.getAttribute('aria-expanded') === 'true';
        card.setAttribute('aria-expanded', !isExpanded);

        // Bind evidence link clicks when expanded
        if (!isExpanded) {
            card.querySelectorAll('.evidence-link').forEach(link => {
                link.addEventListener('click', handleEvidenceLinkClick);
            });
        }
    }

    /**
     * Handle evidence link click - show evidence panel with highlight
     * Implemented in Plan 03
     * @param {Event} event - Click event
     */
    function handleEvidenceLinkClick(event) {
        event.preventDefault();
        event.stopPropagation();

        const link = event.currentTarget;
        const startChar = link.dataset.start ? parseInt(link.dataset.start, 10) : null;
        const endChar = link.dataset.end ? parseInt(link.dataset.end, 10) : null;
        const text = link.dataset.text;

        // Dispatch event for Plan 03 evidence highlighting
        document.dispatchEvent(new CustomEvent('evidence-highlight-requested', {
            detail: { startChar, endChar, text }
        }));
    }

    /**
     * Store JD text for evidence panel (used by Plan 03)
     * @param {Object} jdData - JD data object
     */
    function storeJdTextForEvidence(jdData) {
        // Store for evidence highlighting module
        window.currentJdText = {
            client_service_results: jdData.client_service_results,
            key_activities: jdData.key_activities
        };

        console.log('[classify.js] Stored JD text for evidence:', {
            hasCSR: !!jdData.client_service_results,
            csrLen: jdData.client_service_results?.length,
            kaCount: jdData.key_activities?.length
        });

        // Pre-render JD text in evidence panel so it's ready when user clicks highlight
        const viewer = document.getElementById('jd-text-viewer');
        if (viewer && window.currentJdText) {
            let html = '';
            if (window.currentJdText.client_service_results) {
                html += `<div class="jd-text-section"><h4>Client-Service Results</h4><p class="jd-text-content" data-field="client_service_results">${window.currentJdText.client_service_results.replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;')}</p></div>`;
            }
            if (window.currentJdText.key_activities && window.currentJdText.key_activities.length > 0) {
                html += `<div class="jd-text-section"><h4>Key Activities</h4><ul class="jd-activity-list">${window.currentJdText.key_activities.map((a, i) => `<li data-field="key_activity_${i}">${a.replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;')}</li>`).join('')}</ul></div>`;
            }
            if (html) {
                viewer.innerHTML = html;
                console.log('[classify.js] Pre-rendered JD text in evidence panel');
            }
        }
    }

    /**
     * Close evidence panel
     */
    function closeEvidencePanel() {
        if (elements.evidencePanel) {
            elements.evidencePanel.classList.add('hidden');
        }
    }

    /**
     * Render clarification warning for needs_clarification status
     * @param {Array} fields - Fields needing clarification
     */
    function renderClarificationWarning(fields) {
        if (!elements.recommendationsPanel) return;

        const warning = document.createElement('div');
        warning.className = 'classify-warning';
        warning.innerHTML = `
            <h4><i class="fas fa-exclamation-triangle"></i> Clarification Needed</h4>
            <p>The following areas need more detail for accurate classification:</p>
            <ul>
                ${fields.map(f => `<li>${escapeHtml(f)}</li>`).join('')}
            </ul>
        `;
        elements.recommendationsPanel.prepend(warning);
    }

    /**
     * Render conflicting duties warning for invalid_combination status
     * @param {Object} duties - Duty distribution object
     */
    function renderConflictingDutiesWarning(duties) {
        if (!elements.recommendationsPanel) return;

        const warning = document.createElement('div');
        warning.className = 'classify-error-detail';
        warning.innerHTML = `
            <h4><i class="fas fa-times-circle"></i> Invalid Combination of Work</h4>
            <p>This job description contains duties that span multiple incompatible occupational groups:</p>
            <ul>
                ${Object.entries(duties).map(([group, pct]) =>
                    `<li><strong>${escapeHtml(group)}:</strong> ${Math.round(pct * 100)}%</li>`
                ).join('')}
            </ul>
            <p>Consider splitting this position or clarifying primary duties.</p>
        `;
        elements.recommendationsPanel.prepend(warning);
    }

    /**
     * Render general warnings
     * @param {Array} warnings - Array of warning strings
     */
    function renderWarnings(warnings) {
        if (!elements.recommendationsPanel) return;

        warnings.forEach(msg => {
            const warning = document.createElement('div');
            warning.className = 'classify-warning-item';
            warning.innerHTML = `<i class="fas fa-info-circle"></i> ${escapeHtml(msg)}`;
            elements.recommendationsPanel.appendChild(warning);
        });
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
     * @param {number} maxLength - Max characters
     * @returns {string} - Truncated text
     */
    function truncateText(text, maxLength) {
        if (!text || text.length <= maxLength) return text || '';
        return text.substring(0, maxLength - 3) + '...';
    }

    // Expose public API
    return {
        init,
        getCurrentAllocation: () => currentAllocation
    };
})();

// Initialize on DOM ready
document.addEventListener('DOMContentLoaded', classifyModule.init);
