const CACHE_NAME = 'expense-manager-v1';
const urlsToCache = [
    '/',
    '/static/css/style.css',
    '/static/js/app.js',
    '/static/manifest.json',
    '/dashboard',
    '/add_expense',
    '/expenses',
    '/reports',
    '/settings',
    'https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css',
    'https://cdn.jsdelivr.net/npm/bootstrap-icons@1.7.2/font/bootstrap-icons.css',
    'https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js',
    'https://cdn.jsdelivr.net/npm/chart.js'
];

// Install event - cache resources
self.addEventListener('install', function(event) {
    console.log('Service Worker installing...');
    event.waitUntil(
        caches.open(CACHE_NAME)
            .then(function(cache) {
                console.log('Opened cache');
                return cache.addAll(urlsToCache);
            })
            .catch(function(error) {
                console.log('Error caching resources:', error);
            })
    );
});

// Activate event - clean up old caches
self.addEventListener('activate', function(event) {
    console.log('Service Worker activating...');
    event.waitUntil(
        caches.keys().then(function(cacheNames) {
            return Promise.all(
                cacheNames.map(function(cacheName) {
                    if (cacheName !== CACHE_NAME) {
                        console.log('Deleting old cache:', cacheName);
                        return caches.delete(cacheName);
                    }
                })
            );
        })
    );
});

// Fetch event - serve from cache, fallback to network
self.addEventListener('fetch', function(event) {
    // Skip non-GET requests
    if (event.request.method !== 'GET') {
        return;
    }
    
    // Skip requests to external domains (except CDN resources)
    const url = new URL(event.request.url);
    if (url.origin !== location.origin && 
        !url.hostname.includes('cdn.jsdelivr.net') && 
        !url.hostname.includes('fonts.googleapis.com') &&
        !url.hostname.includes('fonts.gstatic.com')) {
        return;
    }

    event.respondWith(
        caches.match(event.request)
            .then(function(response) {
                // Return cached version if available
                if (response) {
                    console.log('Serving from cache:', event.request.url);
                    return response;
                }
                
                // Clone the request because it's a one-time use stream
                const fetchRequest = event.request.clone();
                
                return fetch(fetchRequest)
                    .then(function(response) {
                        // Check if valid response
                        if (!response || response.status !== 200 || response.type !== 'basic') {
                            return response;
                        }
                        
                        // Clone the response because it's a one-time use stream
                        const responseToCache = response.clone();
                        
                        // Cache the fetched response
                        caches.open(CACHE_NAME)
                            .then(function(cache) {
                                cache.put(event.request, responseToCache);
                            });
                        
                        return response;
                    })
                    .catch(function(error) {
                        console.log('Fetch failed, serving offline page:', error);
                        
                        // Return a basic offline page for navigation requests
                        if (event.request.destination === 'document') {
                            return caches.match('/');
                        }
                        
                        // For other requests, you might want to return a default response
                        return new Response('Offline', {
                            status: 200,
                            statusText: 'Offline',
                            headers: new Headers({
                                'Content-Type': 'text/plain'
                            })
                        });
                    });
            })
    );
});

// Background sync for offline form submissions
self.addEventListener('sync', function(event) {
    if (event.tag === 'expense-sync') {
        event.waitUntil(syncExpenses());
    }
});

function syncExpenses() {
    // Get pending expenses from IndexedDB and sync them
    return new Promise((resolve, reject) => {
        // This would be implemented with IndexedDB to store offline expenses
        // For now, just resolve
        console.log('Syncing offline expenses...');
        resolve();
    });
}

// Push notifications (future enhancement)
self.addEventListener('push', function(event) {
    const options = {
        body: event.data ? event.data.text() : 'You have a new notification!',
        icon: '/static/icons/icon-192x192.png',
        badge: '/static/icons/icon-96x96.png',
        vibrate: [200, 100, 200],
        tag: 'expense-notification',
        actions: [
            {
                action: 'view',
                title: 'View',
                icon: '/static/icons/icon-96x96.png'
            },
            {
                action: 'dismiss',
                title: 'Dismiss',
                icon: '/static/icons/icon-96x96.png'
            }
        ]
    };
    
    event.waitUntil(
        self.registration.showNotification('Expense Manager', options)
    );
});

// Handle notification clicks
self.addEventListener('notificationclick', function(event) {
    event.notification.close();
    
    if (event.action === 'view') {
        event.waitUntil(
            clients.openWindow('/dashboard')
        );
    }
    // Dismiss action does nothing (just closes notification)
});

// Handle message events from the main thread
self.addEventListener('message', function(event) {
    if (event.data && event.data.type === 'SKIP_WAITING') {
        self.skipWaiting();
    }
});

// Periodic background sync (future enhancement)
self.addEventListener('periodicsync', function(event) {
    if (event.tag === 'expense-backup') {
        event.waitUntil(backupExpenses());
    }
});

function backupExpenses() {
    // Implement expense backup logic
    console.log('Backing up expenses...');
    return Promise.resolve();
}
