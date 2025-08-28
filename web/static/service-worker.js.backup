/**
 * CORA Service Worker
 * Progressive Web App functionality with offline support
 */

const CACHE_NAME = 'cora-v1.0.1';
const STATIC_CACHE = 'cora-static-v1.0.1';
const API_CACHE = 'cora-api-v1.0.1';
const OFFLINE_CACHE = 'cora-offline-v1.0.1';

// Static assets to cache
const STATIC_ASSETS = [
    '/',
    '/dashboard',
    '/static/css/cora-chat-consolidated.css',
    '/static/css/mobile-navigation.css',
    '/static/css/onboarding.css',
    // Removed legacy chat script from precache to avoid caching outdated widget
    '/static/js/health_monitor.js',
    '/static/js/alerts_panel.js',
    '/static/js/error_recovery.js',
    '/static/js/realtime_updates.js',
    '/static/js/voice_help.js',
    '/static/js/feedback_widget.js',
    '/static/images/logos/cora-logo.png',
    '/static/images/logos/integrations/quickbooks-logo.svg',
    '/static/images/logos/integrations/shopify-logo.svg',
    '/static/images/logos/integrations/square-logo.svg',
    '/static/images/profiles/lisa-park.png',
    '/static/images/profiles/marcus-johnson.png',
    '/static/images/logos/cora-logo.png'
];

// API endpoints to cache
const API_ENDPOINTS = [
    '/api/status',
    '/api/jobs',
    '/api/expenses',
    '/api/alerts'
];

// Install event - cache static assets
self.addEventListener('install', (event) => {
    console.log('Service Worker installing...');
    
    event.waitUntil(
        Promise.all([
            // Cache static assets
            caches.open(STATIC_CACHE).then((cache) => {
                console.log('Caching static assets...');
                return cache.addAll(STATIC_ASSETS);
            }),
            
            // Cache offline page
            caches.open(OFFLINE_CACHE).then((cache) => {
                return cache.add('/offline.html');
            })
        ]).then(() => {
            console.log('Service Worker installed successfully');
            return self.skipWaiting();
        })
    );
});

// Activate event - clean up old caches
self.addEventListener('activate', (event) => {
    console.log('Service Worker activating...');
    
    event.waitUntil(
        caches.keys().then((cacheNames) => {
            return Promise.all(
                cacheNames.map((cacheName) => {
                    if (cacheName !== STATIC_CACHE && 
                        cacheName !== API_CACHE && 
                        cacheName !== OFFLINE_CACHE) {
                        console.log('Deleting old cache:', cacheName);
                        return caches.delete(cacheName);
                    }
                })
            );
        }).then(() => {
            console.log('Service Worker activated');
            return self.clients.claim();
        })
    );
});

// Fetch event - serve from cache or network
self.addEventListener('fetch', (event) => {
    const { request } = event;
    const url = new URL(request.url);
    
    // Skip non-GET requests
    if (request.method !== 'GET') {
        return;
    }
    
    // Handle different types of requests
    if (isStaticAsset(request)) {
        event.respondWith(handleStaticAsset(request));
    } else if (isAPIRequest(request)) {
        event.respondWith(handleAPIRequest(request));
    } else {
        event.respondWith(handleNavigationRequest(request));
    }
});

// Background sync for offline expenses
self.addEventListener('sync', (event) => {
    console.log('Background sync triggered:', event.tag);
    
    if (event.tag === 'sync-expenses') {
        event.waitUntil(syncOfflineExpenses());
    }
});

// Push notification handling
self.addEventListener('push', (event) => {
    console.log('Push notification received');
    
    const options = {
        body: event.data ? event.data.text() : 'New update available',
        icon: '/static/images/logos/cora-logo.png',
        badge: '/static/images/logos/cora-logo.png',
        vibrate: [100, 50, 100],
        data: {
            dateOfArrival: Date.now(),
            primaryKey: 1
        },
        actions: [
            {
                action: 'explore',
                title: 'View Dashboard',
                icon: '/static/images/logos/cora-logo.png'
            },
            {
                action: 'close',
                title: 'Close',
                icon: '/static/images/logos/cora-logo.png'
            }
        ]
    };
    
    event.waitUntil(
        self.registration.showNotification('CORA', options)
    );
});

// Notification click handling
self.addEventListener('notificationclick', (event) => {
    console.log('Notification clicked:', event.action);
    
    event.notification.close();
    
    if (event.action === 'explore') {
        event.waitUntil(
            clients.openWindow('/dashboard')
        );
    }
});

// Helper functions
function isStaticAsset(request) {
    const url = new URL(request.url);
    return url.pathname.startsWith('/static/') || 
           url.pathname === '/' ||
           url.pathname === '/dashboard' ||
           url.pathname.endsWith('.css') ||
           url.pathname.endsWith('.js') ||
           url.pathname.endsWith('.png') ||
           url.pathname.endsWith('.svg') ||
           url.pathname.endsWith('.jpg') ||
           url.pathname.endsWith('.webp');
}

function isAPIRequest(request) {
    const url = new URL(request.url);
    return url.pathname.startsWith('/api/');
}

function handleStaticAsset(request) {
    return caches.match(request).then((response) => {
        if (response) {
            return response;
        }
        
        return fetch(request).then((response) => {
            if (!response || response.status !== 200 || response.type !== 'basic') {
                return response;
            }
            
            const responseToCache = response.clone();
            caches.open(STATIC_CACHE).then((cache) => {
                cache.put(request, responseToCache);
            });
            
            return response;
        });
    });
}

function handleAPIRequest(request) {
    return fetch(request).then((response) => {
        if (response.status === 200) {
            const responseToCache = response.clone();
            caches.open(API_CACHE).then((cache) => {
                cache.put(request, responseToCache);
            });
        }
        return response;
    }).catch(() => {
        // Return cached response if available
        return caches.match(request).then((response) => {
            if (response) {
                return response;
            }
            
            // Return offline data if available
            return getOfflineData(request);
        });
    });
}

function handleNavigationRequest(request) {
    // Always prefer network for HTML navigations; fall back to offline page
    return fetch(request).catch(() => caches.match('/offline.html'));
}

async function syncOfflineExpenses() {
    try {
        const db = await openOfflineDB();
        const offlineExpenses = await db.getAll('offlineExpenses');
        
        for (const expense of offlineExpenses) {
            try {
                const response = await fetch('/api/expenses', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify(expense.data)
                });
                
                if (response.ok) {
                    // Remove from offline storage
                    await db.delete('offlineExpenses', expense.id);
                    console.log('Synced offline expense:', expense.id);
                }
            } catch (error) {
                console.error('Failed to sync expense:', expense.id, error);
            }
        }
        
        // Notify clients of sync completion
        const clients = await self.clients.matchAll();
        clients.forEach((client) => {
            client.postMessage({
                type: 'SYNC_COMPLETE',
                syncedCount: offlineExpenses.length
            });
        });
        
    } catch (error) {
        console.error('Background sync failed:', error);
    }
}

function getOfflineData(request) {
    const url = new URL(request.url);
    
    // Return mock data for common API endpoints
    if (url.pathname === '/api/expenses') {
        return new Response(JSON.stringify([]), {
            headers: { 'Content-Type': 'application/json' }
        });
    }
    
    if (url.pathname === '/api/jobs') {
        return new Response(JSON.stringify([]), {
            headers: { 'Content-Type': 'application/json' }
        });
    }
    
    if (url.pathname === '/api/alerts') {
        return new Response(JSON.stringify([]), {
            headers: { 'Content-Type': 'application/json' }
        });
    }
    
    return new Response('Offline', { status: 503 });
}

async function openOfflineDB() {
    return new Promise((resolve, reject) => {
        const request = indexedDB.open('CORAOfflineDB', 1);
        
        request.onerror = () => reject(request.error);
        request.onsuccess = () => resolve(request.result);
        
        request.onupgradeneeded = (event) => {
            const db = event.target.result;
            
            if (!db.objectStoreNames.contains('offlineExpenses')) {
                const store = db.createObjectStore('offlineExpenses', { keyPath: 'id', autoIncrement: true });
                store.createIndex('timestamp', 'timestamp', { unique: false });
            }
        };
    });
}

// Message handling for client communication
self.addEventListener('message', (event) => {
    console.log('Service Worker received message:', event.data);
    
    if (event.data.type === 'SKIP_WAITING') {
        self.skipWaiting();
    }
    
    if (event.data.type === 'GET_VERSION') {
        event.ports[0].postMessage({ version: CACHE_NAME });
    }
    
    if (event.data.type === 'CACHE_URL') {
        event.waitUntil(
            caches.open(STATIC_CACHE).then((cache) => {
                return cache.add(event.data.url);
            })
        );
    }
});

// Error handling
self.addEventListener('error', (event) => {
    console.error('Service Worker error:', event.error);
});

self.addEventListener('unhandledrejection', (event) => {
    console.error('Service Worker unhandled rejection:', event.reason);
}); 