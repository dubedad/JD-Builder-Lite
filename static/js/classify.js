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

    // Job Evaluation Standard links by group code
    // Source: TBS classification standards
    const JOB_EVAL_STANDARDS = {
        'AS': { name: 'Administrative Services', url: 'https://www.canada.ca/en/treasury-board-secretariat/services/collective-agreements/job-evaluation/administrative-services-group.html' },
        'CS': { name: 'Computer Systems', url: 'https://www.canada.ca/en/treasury-board-secretariat/services/collective-agreements/job-evaluation/computer-systems-group.html' },
        'EC': { name: 'Economics and Social Science Services', url: 'https://www.canada.ca/en/treasury-board-secretariat/services/collective-agreements/job-evaluation/economics-and-social-science-services-group.html' },
        'PM': { name: 'Programme Administration', url: 'https://www.canada.ca/en/treasury-board-secretariat/services/collective-agreements/job-evaluation/programme-administration-group.html' },
        'IT': { name: 'Information Technology', url: 'https://www.canada.ca/en/treasury-board-secretariat/services/collective-agreements/job-evaluation/information-technology-group.html' },
        'FI': { name: 'Financial Administration', url: 'https://www.canada.ca/en/treasury-board-secretariat/services/collective-agreements/job-evaluation/financial-administration-group.html' },
        'PE': { name: 'Personnel Administration', url: 'https://www.canada.ca/en/treasury-board-secretariat/services/collective-agreements/job-evaluation/personnel-administration-group.html' },
        'EX': { name: 'Executive', url: 'https://www.canada.ca/en/treasury-board-secretariat/services/collective-agreements/job-evaluation/executive-group.html' }
    };
    // Fallback URL for groups not in lookup
    const JOB_EVAL_STANDARD_FALLBACK = 'https://www.canada.ca/en/treasury-board-secretariat/services/collective-agreements/job-evaluation.html';

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

        // Listen for cache-hit event from classify cache
        document.addEventListener('classify-cache-hit', (event) => {
            const cachedResponse = event.detail;
            currentAllocation = cachedResponse;
            // Re-render from cache. We need jdData but can reconstruct minimally.
            const jdData = buildJdDataFromProfile(window.currentProfile, store.getState().selections);
            renderResults(cachedResponse, jdData);
        });

        // Wire the v5.1 Analyze CTA button
        const analyzeBtn = document.getElementById('classify-analyze-btn');
        if (analyzeBtn) {
            analyzeBtn.addEventListener('click', function() {
                // Hide the CTA
                const ctaDiv = document.getElementById('classify-cta');
                if (ctaDiv) ctaDiv.classList.add('hidden');
                // Trigger classification via existing event mechanism (no double-fire)
                const profile = window.currentProfile;
                const selections = store.getState().selections;
                if (profile) {
                    document.dispatchEvent(new CustomEvent('classify-requested', {
                        detail: { profile, selections }
                    }));
                }
            });
        }

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
            document.dispatchEvent(new CustomEvent('classify-complete', { detail: response }));

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
        // Hide the v5.1 Analyze CTA when analysis begins
        const ctaDiv = document.getElementById('classify-cta');
        if (ctaDiv) ctaDiv.classList.add('hidden');
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

        // Reset v5.1 post-analysis sections before re-render
        ['classify-alignment', 'classify-key-evidence', 'classify-caveats', 'classify-alternatives', 'classify-next-step'].forEach(function(id) {
            const el = document.getElementById(id);
            if (el) el.classList.add('hidden');
        });
        const topResultEl = document.getElementById('classify-top-result');
        if (topResultEl) topResultEl.innerHTML = '';

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

                // v5.1 post-analysis sections
                const sorted = [...response.recommendations].sort(function(a, b) { return b.confidence - a.confidence; });
                const topRec = sorted[0];
                renderTopResultCard(topRec, response.provenance_map);
                renderStatementAlignment(topRec, jdData);
                renderKeyEvidence(topRec.evidence_spans);
                renderCaveats(topRec.caveats);
                renderAlternatives(sorted, topRec.group_code);
                renderNextStep(topRec.group_code);
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
            renderCoachingPanel(response.conflicting_duties, response.recommendations);
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

        elements.statusBadge.classList.remove('analyzing', 'success', 'warning', 'error', 'coaching');

        let text = 'Complete';
        let badgeClass = 'success';

        if (status === 'needs_clarification') {
            text = 'Needs Clarification';
            badgeClass = 'warning';
        } else if (status === 'invalid_combination') {
            text = 'Multiple Groups Identified';
            badgeClass = 'coaching';
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

        // Sort by confidence descending so highest-confidence card is #1
        const sorted = [...recommendations].sort((a, b) => b.confidence - a.confidence);

        sorted.forEach((rec, index) => {
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
     * Render the v5.1 top result card into #classify-top-result (CLASS-01 enrichment)
     * @param {Object} topRec - Top GroupRecommendation
     * @param {Object} provenanceMap - Provenance map from API response
     */
    function renderTopResultCard(topRec, provenanceMap) {
        const container = document.getElementById('classify-top-result');
        if (!container || !topRec) return;

        const pct = Math.round(topRec.confidence * 100);
        const groupName = getGroupName(topRec);
        const provenance = provenanceMap ? provenanceMap[topRec.group_code] : null;
        const tbsUrl = (provenance && provenance.url) || topRec.provenance_url || '';
        const barColor = pct >= 70 ? '#43a047' : pct >= 40 ? '#fb8c00' : '#e53935';

        container.innerHTML = `
            <div class="classify-result-card">
                <div class="classify-result-card__header">
                    <div>
                        <h3 class="classify-result-card__title">${pct}% ${escapeHtml(topRec.group_code)} \u2013 ${escapeHtml(groupName)}</h3>
                        <p class="classify-result-card__subtitle">Recommended Occupational Group</p>
                    </div>
                    ${tbsUrl ? `<a href="${escapeHtml(tbsUrl)}" target="_blank" rel="noopener noreferrer" class="classify-result-card__tbs-link"><i class="fas fa-external-link-alt"></i> TBS Definition</a>` : ''}
                </div>
                <div class="classify-result-card__confidence-bar">
                    <div class="classify-result-card__confidence-fill" style="width:${pct}%; background:${barColor}"></div>
                </div>
                <p class="classify-result-card__summary">${escapeHtml(topRec.definition_fit_rationale)}</p>
            </div>
        `;
    }

    /**
     * Render Statement Alignment Comparison (CLASS-02)
     * Two columns: user's key activities vs OG definition statements + overall score
     * @param {Object} topRec - Top GroupRecommendation
     * @param {Object} jdData - JD data sent to API
     */
    function renderStatementAlignment(topRec, jdData) {
        const container = document.getElementById('classify-alignment');
        if (!container) return;

        const userList = document.getElementById('classify-alignment-user');
        const ogList = document.getElementById('classify-alignment-og');
        const scoreDiv = document.getElementById('classify-alignment-score');

        // User's selected key activities
        if (userList && jdData && jdData.key_activities && jdData.key_activities.length > 0) {
            userList.innerHTML = jdData.key_activities.map(function(a) { return '<li>' + escapeHtml(a) + '</li>'; }).join('');
        }

        // OG definition statements from the new model field
        if (ogList && topRec.og_definition_statements && topRec.og_definition_statements.length > 0) {
            ogList.innerHTML = topRec.og_definition_statements.map(function(s) { return '<li>' + escapeHtml(s) + '</li>'; }).join('');
        } else if (ogList) {
            ogList.innerHTML = '<li class="text-muted">No definition statements available</li>';
        }

        // Overall Alignment Score = evidence_spans.length / key_activities.length
        const evidenceCount = (topRec.evidence_spans && topRec.evidence_spans.length) || 0;
        const activityCount = (jdData && jdData.key_activities && jdData.key_activities.length) || 1;
        const alignmentPct = Math.min(100, Math.round((evidenceCount / activityCount) * 100));

        if (scoreDiv) {
            scoreDiv.textContent = 'Overall Alignment Score: ' + alignmentPct + '%';
        }

        container.classList.remove('hidden');
    }

    /**
     * Render Key Evidence green check-circle bullets (CLASS-03)
     * @param {Array} evidenceSpans - EvidenceSpan objects from top recommendation
     */
    function renderKeyEvidence(evidenceSpans) {
        const container = document.getElementById('classify-key-evidence');
        const list = document.getElementById('classify-evidence-list');
        if (!container || !list || !evidenceSpans || evidenceSpans.length === 0) return;

        list.innerHTML = evidenceSpans.map(function(span) {
            var fieldLabel = (span.field && span.field !== 'Unknown') ? ' (' + escapeHtml(span.field) + ')' : '';
            return '<li>' + escapeHtml(span.text) + fieldLabel + '</li>';
        }).join('');

        container.classList.remove('hidden');
    }

    /**
     * Render Caveats amber warning bullets (CLASS-03)
     * @param {Array} caveats - Array of caveat strings from top recommendation
     */
    function renderCaveats(caveats) {
        const container = document.getElementById('classify-caveats');
        const list = document.getElementById('classify-caveats-list');
        if (!container || !list || !caveats || caveats.length === 0) return;

        list.innerHTML = caveats.map(function(c) { return '<li>' + escapeHtml(c) + '</li>'; }).join('');
        container.classList.remove('hidden');
    }

    /**
     * Render Alternative Groups Considered section
     * @param {Array} recommendations - All recommendations sorted by confidence desc
     * @param {string} topGroupCode - Top recommendation's group code to exclude from alternatives
     */
    function renderAlternatives(recommendations, topGroupCode) {
        const container = document.getElementById('classify-alternatives');
        const content = document.getElementById('classify-alternatives-content');
        if (!container || !content) return;

        const alternatives = recommendations.filter(function(r) { return r.group_code !== topGroupCode; });
        if (alternatives.length === 0) return;

        content.innerHTML = alternatives.map(function(rec) {
            var pct = Math.round(rec.confidence * 100);
            var name = OCCUPATIONAL_GROUP_NAMES[rec.group_code] || rec.group_code;
            return '<p><strong>' + escapeHtml(rec.group_code) + '</strong> \u2013 ' + escapeHtml(name) + ': ' + pct + '% confidence</p>';
        }).join('');

        container.classList.remove('hidden');
    }

    /**
     * Render Next Step box with Job Evaluation Standard link (CLASS-04)
     * @param {string} groupCode - Recommended occupational group code
     */
    function renderNextStep(groupCode) {
        const container = document.getElementById('classify-next-step');
        const content = document.getElementById('classify-next-step-content');
        if (!container || !content) return;

        const standard = JOB_EVAL_STANDARDS[groupCode];
        const url = standard ? standard.url : JOB_EVAL_STANDARD_FALLBACK;
        const name = standard ? standard.name : (OCCUPATIONAL_GROUP_NAMES[groupCode] || groupCode);

        content.innerHTML = `
            <p><strong>Step 2:</strong> Apply the Job Evaluation Standard for the <strong>${escapeHtml(groupCode)}</strong> (${escapeHtml(name)}) group.</p>
            <p>Use the standard to determine the appropriate classification level within this occupational group.</p>
            <p><a href="${escapeHtml(url)}" target="_blank" rel="noopener noreferrer"><i class="fas fa-external-link-alt"></i> View ${escapeHtml(groupCode)} Job Evaluation Standard</a></p>
        `;

        container.classList.remove('hidden');
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
     * Render coaching panel for multi-group results (replaces error-style invalid_combination)
     * @param {Object} duties - Duty distribution object (fallback if no recommendations)
     * @param {Array} recommendations - Array of GroupRecommendation objects
     */
    function renderCoachingPanel(duties, recommendations) {
        if (!elements.recommendationsPanel) return;

        // Build coaching panel HTML
        const panel = document.createElement('div');
        panel.className = 'coaching-panel coaching-panel--info';

        // Determine if we have recommendation details to show key duties
        const hasDetailedRecs = recommendations && recommendations.length > 0;

        let rankedCardsHtml = '';
        if (hasDetailedRecs) {
            const sorted = [...recommendations].sort((a, b) => b.confidence - a.confidence);
            rankedCardsHtml = sorted.map((rec, idx) => {
                const isTop = idx === 0;
                const pct = Math.round(rec.confidence * 100);
                const tier = getConfidenceTier(rec.confidence);
                const groupName = getGroupName(rec);
                // Extract up to 3 key evidence quotes as "key duties"
                const keyDuties = (rec.evidence_spans || []).slice(0, 3).map(
                    span => span.text
                );
                return `
                    <div class="recommendation-card-coaching ${isTop ? 'recommendation-card-coaching--primary' : ''}">
                        <div class="recommendation-coaching-header">
                            <div class="confidence-badge confidence-badge--${tier}">${pct}%</div>
                            <h4 class="recommendation-coaching-title">${escapeHtml(rec.group_code)}: ${escapeHtml(groupName)}</h4>
                        </div>
                        <div class="duty-alignment">
                            <p><strong>Duty Alignment:</strong> ${pct}% of your key activities align with this group</p>
                            ${keyDuties.length > 0 ? `
                            <ul class="duty-list">
                                ${keyDuties.map(d => `<li>${escapeHtml(d.length > 100 ? d.substring(0, 97) + '...' : d)}</li>`).join('')}
                            </ul>` : ''}
                        </div>
                    </div>
                `;
            }).join('');
        } else if (duties) {
            // Fallback: render from conflicting_duties dict only
            rankedCardsHtml = Object.entries(duties)
                .sort(([, a], [, b]) => b - a)
                .map(([group, pct], idx) => {
                    const isTop = idx === 0;
                    const groupName = OCCUPATIONAL_GROUP_NAMES[group] || group;
                    return `
                        <div class="recommendation-card-coaching ${isTop ? 'recommendation-card-coaching--primary' : ''}">
                            <div class="recommendation-coaching-header">
                                <div class="confidence-badge confidence-badge--medium">${Math.round(pct * 100)}%</div>
                                <h4 class="recommendation-coaching-title">${escapeHtml(group)}: ${escapeHtml(groupName)}</h4>
                            </div>
                            <div class="duty-alignment">
                                <p><strong>Duty Alignment:</strong> ${Math.round(pct * 100)}% of duties map to this group</p>
                            </div>
                        </div>
                    `;
                }).join('');
        }

        panel.innerHTML = `
            <div class="coaching-icon">
                <i class="fas fa-lightbulb"></i>
            </div>
            <div class="coaching-content">
                <h3 class="coaching-title">Your JD spans multiple occupational groups</h3>
                <p class="coaching-explanation">
                    Based on your key activities, we identified multiple potential groups.
                    Here's how we ranked them by confidence and duty alignment:
                </p>
                <div class="ranked-recommendations">
                    ${rankedCardsHtml}
                </div>
                <div class="coaching-actions">
                    <button class="btn btn--primary coaching-accept-btn" onclick="document.querySelector('.coaching-panel')?.remove()">
                        <i class="fas fa-check"></i> Accept Top Recommendation
                    </button>
                </div>
            </div>
        `;

        elements.recommendationsPanel.prepend(panel);
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
