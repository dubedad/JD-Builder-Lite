// API client for Flask backend
const api = {
    baseUrl: '/api',

    async search(query, searchType = 'Keyword') {
        const params = new URLSearchParams({
            q: query,
            type: searchType
        });
        const response = await fetch(`${this.baseUrl}/search?${params}`);
        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.detail || error.error || 'Search failed');
        }
        return response.json();
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
    }
};
