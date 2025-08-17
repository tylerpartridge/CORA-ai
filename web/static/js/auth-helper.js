// Authentication helper to add auth headers to all requests
(function() {
    // Store the original fetch
    const originalFetch = window.fetch;
    
    // Override fetch to add auth headers
    window.fetch = function(...args) {
        let [url, options = {}] = args;
        
        // Get auth token from localStorage
        const authToken = localStorage.getItem('authToken');
        
        // Add auth header if we have a token and it's an API call
        if (authToken && (url.startsWith('/api/') || url.startsWith('/dashboard'))) {
            options.headers = options.headers || {};
            if (!options.headers['Authorization']) {
                options.headers['Authorization'] = `Bearer ${authToken}`;
            }
        }
        
        // Call original fetch
        return originalFetch(url, options);
    };
    
    // Also handle direct navigation to authenticated pages
    if (window.location.pathname === '/dashboard') {
        const authToken = localStorage.getItem('authToken');
        if (!authToken) {
            // Redirect to login if no token
            window.location.href = '/login';
        }
    }
})();