// API client for Flask backend
const api = {
    baseUrl: '/api',

    async search(query) {
        const response = await fetch(`${this.baseUrl}/search?q=${encodeURIComponent(query)}`);
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
    }
};
