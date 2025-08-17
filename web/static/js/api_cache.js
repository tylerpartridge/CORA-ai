/**
 * CORA API Cache Layer
 * Provides intelligent caching for API requests with offline support
 */

class APICache {
    constructor() {
        this.cache = new Map();
        this.ttl = new Map();
        this.defaultTTL = 5 * 60 * 1000; // 5 minutes
        this.maxCacheSize = 100; // Maximum number of cached items
        
        this.init();
    }
    
    init() {
        this.loadFromStorage();
        this.setupCleanupInterval();
        this.interceptFetch();
    }
    
    setupCleanupInterval() {
        // Clean up expired cache entries every minute
        setInterval(() => {
            this.cleanup();
        }, 60 * 1000);
    }
    
    interceptFetch() {
        const originalFetch = window.fetch;
        
        window.fetch = async (url, options = {}) => {
            const requestKey = this.createRequestKey(url, options);
            
            // Handle GET requests with caching
            if (options.method === 'GET' || !options.method) {
                return this.handleGetRequest(url, options, requestKey);
            }
            
            // Handle mutation requests (POST, PUT, DELETE)
            if (['POST', 'PUT', 'DELETE', 'PATCH'].includes(options.method)) {
                return this.handleMutationRequest(url, options, requestKey);
            }
            
            // Fallback to original fetch
            return originalFetch(url, options);
        };
    }
    
    async handleGetRequest(url, options, requestKey) {
        // Check if we have a valid cached response
        const cachedResponse = this.get(requestKey);
        if (cachedResponse) {
            // console.log('Serving from cache:', requestKey);
            return cachedResponse.clone();
        }
        
        try {
            // Make the actual request
            const response = await fetch(url, options);
            
            // Cache successful responses
            if (response.ok) {
                const responseToCache = response.clone();
                this.set(requestKey, responseToCache);
                // console.log('Cached response:', requestKey);
            }
            
            return response;
        } catch (error) {
            // console.error('Fetch failed:', error);
            
            // Return cached response if available (even if expired)
            const staleResponse = this.getStale(requestKey);
            if (staleResponse) {
                // console.log('Serving stale cache:', requestKey);
                return staleResponse.clone();
            }
            
            throw error;
        }
    }
    
    async handleMutationRequest(url, options, requestKey) {
        try {
            // Make the actual request
            const response = await fetch(url, options);
            
            if (response.ok) {
                // Invalidate related cache entries
                this.invalidateRelated(url);
                
                // Trigger optimistic updates
                this.handleOptimisticUpdate(url, options);
            }
            
            return response;
        } catch (error) {
            // console.error('Mutation request failed:', error);
            
            // Queue for retry if offline
            if (!navigator.onLine) {
                this.queueForRetry(url, options);
            }
            
            throw error;
        }
    }
    
    set(key, response, ttl = null) {
        const expiryTime = Date.now() + (ttl || this.defaultTTL);
        
        // Check cache size limit
        if (this.cache.size >= this.maxCacheSize) {
            this.evictOldest();
        }
        
        this.cache.set(key, response);
        this.ttl.set(key, expiryTime);
        
        // Save to localStorage for persistence
        this.saveToStorage();
    }
    
    get(key) {
        const expiryTime = this.ttl.get(key);
        
        if (!expiryTime || Date.now() > expiryTime) {
            // Cache entry has expired
            this.delete(key);
            return null;
        }
        
        return this.cache.get(key);
    }
    
    getStale(key) {
        // Get cached response even if expired
        return this.cache.get(key);
    }
    
    delete(key) {
        this.cache.delete(key);
        this.ttl.delete(key);
        this.saveToStorage();
    }
    
    clear() {
        this.cache.clear();
        this.ttl.clear();
        this.saveToStorage();
    }
    
    cleanup() {
        const now = Date.now();
        const expiredKeys = [];
        
        for (const [key, expiryTime] of this.ttl.entries()) {
            if (now > expiryTime) {
                expiredKeys.push(key);
            }
        }
        
        expiredKeys.forEach(key => this.delete(key));
        
        if (expiredKeys.length > 0) {
            // console.log(`Cleaned up ${expiredKeys.length} expired cache entries`);
        }
    }
    
    evictOldest() {
        let oldestKey = null;
        let oldestTime = Infinity;
        
        for (const [key, expiryTime] of this.ttl.entries()) {
            if (expiryTime < oldestTime) {
                oldestTime = expiryTime;
                oldestKey = key;
            }
        }
        
        if (oldestKey) {
            this.delete(oldestKey);
            // console.log('Evicted oldest cache entry:', oldestKey);
        }
    }
    
    createRequestKey(url, options) {
        const urlObj = new URL(url, window.location.origin);
        const params = new URLSearchParams(urlObj.search);
        
        // Sort parameters for consistent keys
        const sortedParams = Array.from(params.entries())
            .sort(([a], [b]) => a.localeCompare(b))
            .map(([key, value]) => `${key}=${value}`)
            .join('&');
        
        return `${urlObj.pathname}?${sortedParams}`;
    }
    
    invalidateRelated(url) {
        const urlObj = new URL(url, window.location.origin);
        const path = urlObj.pathname;
        
        // Invalidate cache entries that match the path
        const keysToInvalidate = [];
        
        for (const key of this.cache.keys()) {
            if (key.startsWith(path)) {
                keysToInvalidate.push(key);
            }
        }
        
        keysToInvalidate.forEach(key => {
            // console.log('Invalidating cache:', key);
            this.delete(key);
        });
    }
    
    handleOptimisticUpdate(url, options) {
        const urlObj = new URL(url, window.location.origin);
        
        // Handle specific optimistic updates
        if (urlObj.pathname === '/api/expenses' && options.method === 'POST') {
            this.handleExpenseCreated(options.body);
        } else if (urlObj.pathname.startsWith('/api/expenses/') && options.method === 'PUT') {
            this.handleExpenseUpdated(urlObj.pathname, options.body);
        }
    }
    
    async handleExpenseCreated(body) {
        try {
            const expenseData = JSON.parse(body);
            
            // Get current expenses cache
            const expensesKey = '/api/expenses';
            const cachedResponse = this.get(expensesKey);
            
            if (cachedResponse) {
                const expenses = await cachedResponse.json();
                expenses.unshift(expenseData);
                
                // Update cache with new expense
                const newResponse = new Response(JSON.stringify(expenses), {
                    headers: { 'Content-Type': 'application/json' }
                });
                
                this.set(expensesKey, newResponse);
                // console.log('Optimistically updated expenses cache');
            }
        } catch (error) {
            // console.error('Failed to handle optimistic update:', error);
        }
    }
    
    async handleExpenseUpdated(path, body) {
        try {
            const expenseData = JSON.parse(body);
            const expenseId = path.split('/').pop();
            
            // Get current expenses cache
            const expensesKey = '/api/expenses';
            const cachedResponse = this.get(expensesKey);
            
            if (cachedResponse) {
                const expenses = await cachedResponse.json();
                const index = expenses.findIndex(e => e.id == expenseId);
                
                if (index !== -1) {
                    expenses[index] = { ...expenses[index], ...expenseData };
                    
                    // Update cache
                    const newResponse = new Response(JSON.stringify(expenses), {
                        headers: { 'Content-Type': 'application/json' }
                    });
                    
                    this.set(expensesKey, newResponse);
                    // console.log('Optimistically updated expense in cache');
                }
            }
        } catch (error) {
            // console.error('Failed to handle optimistic update:', error);
        }
    }
    
    queueForRetry(url, options) {
        const retryQueue = this.getRetryQueue();
        retryQueue.push({
            url,
            options,
            timestamp: Date.now(),
            retryCount: 0
        });
        
        this.saveRetryQueue(retryQueue);
        // console.log('Queued request for retry:', url);
    }
    
    async processRetryQueue() {
        if (!navigator.onLine) {
            return;
        }
        
        const retryQueue = this.getRetryQueue();
        if (retryQueue.length === 0) {
            return;
        }
        
        // console.log(`Processing ${retryQueue.length} queued requests`);
        
        const newQueue = [];
        
        for (const item of retryQueue) {
            try {
                if (item.retryCount < 3) {
                    const response = await fetch(item.url, item.options);
                    
                    if (response.ok) {
                        // console.log('Retry successful:', item.url);
                        // Don't add back to queue
                    } else {
                        item.retryCount++;
                        newQueue.push(item);
                    }
                } else {
                    // console.log('Max retries reached for:', item.url);
                }
            } catch (error) {
                item.retryCount++;
                newQueue.push(item);
                // console.error('Retry failed:', item.url, error);
            }
        }
        
        this.saveRetryQueue(newQueue);
    }
    
    getRetryQueue() {
        try {
            const stored = localStorage.getItem('cora_retry_queue');
            return stored ? JSON.parse(stored) : [];
        } catch (error) {
            // console.error('Failed to load retry queue:', error);
            return [];
        }
    }
    
    saveRetryQueue(queue) {
        try {
            localStorage.setItem('cora_retry_queue', JSON.stringify(queue));
        } catch (error) {
            // console.error('Failed to save retry queue:', error);
        }
    }
    
    saveToStorage() {
        try {
            // Note: We can't directly serialize Response objects
            // So we store metadata and let the cache rebuild
            const metadata = {
                size: this.cache.size,
                timestamp: Date.now()
            };
            localStorage.setItem('cora_cache_metadata', JSON.stringify(metadata));
        } catch (error) {
            // console.error('Failed to save cache metadata:', error);
        }
    }
    
    loadFromStorage() {
        try {
            const metadata = localStorage.getItem('cora_cache_metadata');
            if (metadata) {
                const data = JSON.parse(metadata);
                // console.log('Loaded cache metadata:', data);
            }
        } catch (error) {
            // console.error('Failed to load cache metadata:', error);
        }
    }
    
    // Cache statistics
    getStats() {
        return {
            size: this.cache.size,
            maxSize: this.maxCacheSize,
            hitRate: this.calculateHitRate(),
            oldestEntry: this.getOldestEntry(),
            newestEntry: this.getNewestEntry()
        };
    }
    
    calculateHitRate() {
        // This would need to be implemented with hit tracking
        return 0;
    }
    
    getOldestEntry() {
        let oldestKey = null;
        let oldestTime = Infinity;
        
        for (const [key, expiryTime] of this.ttl.entries()) {
            if (expiryTime < oldestTime) {
                oldestTime = expiryTime;
                oldestKey = key;
            }
        }
        
        return oldestKey;
    }
    
    getNewestEntry() {
        let newestKey = null;
        let newestTime = 0;
        
        for (const [key, expiryTime] of this.ttl.entries()) {
            if (expiryTime > newestTime) {
                newestTime = expiryTime;
                newestKey = key;
            }
        }
        
        return newestKey;
    }
    
    // Preload important data
    async preloadData() {
        const importantEndpoints = [
            '/api/status',
            '/api/jobs',
            '/api/expenses',
            '/api/alerts'
        ];
        
        // console.log('Preloading important data...');
        
        for (const endpoint of importantEndpoints) {
            try {
                await fetch(endpoint);
            } catch (error) {
                // console.error('Failed to preload:', endpoint, error);
            }
        }
    }
}

// Auto-initialize when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
    window.apiCache = new APICache();
    
    // Process retry queue when coming back online
    window.addEventListener('online', () => {
        window.apiCache.processRetryQueue();
    });
    
    // Preload important data
    setTimeout(() => {
        window.apiCache.preloadData();
    }, 1000);
});

// Export for use in other modules
if (typeof module !== 'undefined' && module.exports) {
    module.exports = APICache;
} 