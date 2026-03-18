// API client for Flask backend
const api = {
    baseUrl: '/api',

    async search(query, searchType = 'Keyword') {
        console.log('[DEBUG api.js] search called with:', query, searchType);
        const params = new URLSearchParams({
            q: query,
            type: searchType
        });
        const url = `${this.baseUrl}/search?${params}`;
        console.log('[DEBUG api.js] Fetching URL:', url);
        try {
            const response = await fetch(url);
            console.log('[DEBUG api.js] Fetch response received, status:', response.status);
            if (!response.ok) {
                const error = await response.json();
                throw new Error(error.detail || error.error || 'Search failed');
            }
            const data = await response.json();
            console.log('[DEBUG api.js] JSON parsed, count:', data?.count);
            return data;
        } catch (err) {
            console.error('[DEBUG api.js] Fetch error:', err);
            throw err;
        }
    },

    async getProfile(code) {
        const response = await fetch(`${this.baseUrl}/profile?code=${encodeURIComponent(code)}`);
        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.detail || error.error || 'Profile fetch failed');
        }
        return response.json();
    },

    async fetchOccupationIcon(occupationTitle, leadStatement) {
        const response = await fetch('/api/occupation-icon', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                occupation_title: occupationTitle,
                lead_statement: leadStatement
            })
        });
        if (!response.ok) return { icon_class: 'fa-briefcase' };
        return response.json();
    },

    async fetchOccupationDescription(occupationTitle, leadStatement, mainDuties) {
        const response = await fetch('/api/occupation-description', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                occupation_title: occupationTitle,
                lead_statement: leadStatement,
                main_duties: mainDuties || []
            })
        });
        if (!response.ok) return { description: '' };
        return response.json();
    },

    /**
     * Call the allocation API for Classification Step 1
     * @param {string} positionTitle - Job title
     * @param {string} clientServiceResults - CSR/lead statement text
     * @param {string[]} keyActivities - Array of key activity statements
     * @param {string[]|null} skills - Optional skills array
     * @param {string[]|null} labels - Optional OaSIS labels for boost
     * @param {number} minimumConfidence - Minimum confidence threshold (default 0.3)
     * @returns {Promise<Object>} AllocationResponse with recommendations and provenance
     */
    async allocate(positionTitle, clientServiceResults, keyActivities, skills = null, labels = null, minimumConfidence = 0.3) {
        const response = await fetch(`${this.baseUrl}/allocate`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                position_title: positionTitle,
                client_service_results: clientServiceResults,
                key_activities: keyActivities,
                skills: skills,
                labels: labels,
                minimum_confidence: minimumConfidence
            })
        });

        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.detail || error.error || 'Allocation failed');
        }

        return response.json();
    }
};
