/**
 * API Error Handler for CORA
 * Gracefully handles API failures without showing error popups
 */

(function() {
    // Store original fetch
    const originalFetch = window.fetch;
    
    // Override fetch to handle errors gracefully on landing page
    window.fetch = async function(...args) {
        try {
            const response = await originalFetch(...args);
            return response;
        } catch (error) {
            // On landing page, silently log errors instead of showing popups
            if (window.location.pathname === '/') {
                // console.log('API request failed (silent on landing page):', error.message);
                // Return a mock response to prevent further errors
                return {
                    ok: false,
                    status: 0,
                    statusText: 'Network Error',
                    json: async () => ({ error: 'Network unavailable' }),
                    text: async () => 'Network unavailable'
                };
            }
            // Re-throw for other pages
            throw error;
        }
    };
})();