/**
 * Client-side error reporting
 * Catches and reports JavaScript errors to the server
 */

(function() {
    'use strict';
    
    // Configuration
    const ERROR_ENDPOINT = '/api/errors/javascript';
    const PERFORMANCE_ENDPOINT = '/api/errors/performance';
    const MAX_ERRORS_PER_SESSION = 10;
    const BATCH_INTERVAL = 5000; // 5 seconds
    
    let errorCount = 0;
    let errorBatch = [];
    
    /**
     * Send error to server
     */
    function reportError(errorData) {
        // Limit errors per session to avoid spam
        if (errorCount >= MAX_ERRORS_PER_SESSION) {
            return;
        }
        
        errorCount++;
        
        // Add timestamp and URL
        errorData.timestamp = new Date().toISOString();
        errorData.url = window.location.href;
        errorData.userAgent = navigator.userAgent;
        
        // Send immediately for critical errors
        if (isCriticalError(errorData)) {
            sendError(errorData);
        } else {
            // Batch non-critical errors
            errorBatch.push(errorData);
        }
    }
    
    /**
     * Send error to server
     */
    function sendError(errorData) {
        try {
            fetch(ERROR_ENDPOINT, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(errorData)
            }).catch(function(err) {
                // console.error('Failed to report error:', err);
            });
        } catch (e) {
            // Silently fail if fetch isn't available
        }
    }
    
    /**
     * Check if error is critical
     */
    function isCriticalError(errorData) {
        const criticalPatterns = [
            /SecurityError/,
            /TypeError.*Cannot read/,
            /ReferenceError/,
            /Failed to fetch/,
            /Network request failed/
        ];
        
        return criticalPatterns.some(pattern => 
            pattern.test(errorData.message)
        );
    }
    
    /**
     * Global error handler
     */
    window.addEventListener('error', function(event) {
        const errorData = {
            message: event.message || 'Unknown error',
            source: event.filename || 'unknown',
            lineno: event.lineno || 0,
            colno: event.colno || 0,
            stack: event.error ? event.error.stack : null,
            errorType: 'javascript'
        };
        
        reportError(errorData);
    });
    
    /**
     * Unhandled promise rejection handler
     */
    window.addEventListener('unhandledrejection', function(event) {
        const errorData = {
            message: event.reason ? event.reason.toString() : 'Unhandled Promise Rejection',
            stack: event.reason && event.reason.stack ? event.reason.stack : null,
            errorType: 'promise'
        };
        
        reportError(errorData);
    });
    
    /**
     * Performance monitoring
     */
    if (window.performance && window.performance.timing) {
        window.addEventListener('load', function() {
            setTimeout(function() {
                const timing = window.performance.timing;
                const pageLoadTime = timing.loadEventEnd - timing.navigationStart;
                const domReadyTime = timing.domContentLoadedEventEnd - timing.navigationStart;
                const responseTime = timing.responseEnd - timing.requestStart;
                
                // Report slow page loads
                if (pageLoadTime > 3000) {
                    fetch(PERFORMANCE_ENDPOINT, {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json',
                        },
                        body: JSON.stringify({
                            metric: 'page_load',
                            value: pageLoadTime,
                            url: window.location.href,
                            metadata: {
                                domReady: domReadyTime,
                                serverResponse: responseTime,
                                userAgent: navigator.userAgent
                            }
                        })
                    }).catch(function() {
                        // Silently fail
                    });
                }
            }, 1000); // Wait for page to fully load
        });
    }
    
    /**
     * Batch send errors periodically
     */
    setInterval(function() {
        if (errorBatch.length > 0) {
            const errors = errorBatch.splice(0, errorBatch.length);
            errors.forEach(sendError);
        }
    }, BATCH_INTERVAL);
    
    /**
     * Send remaining errors before page unload
     */
    window.addEventListener('beforeunload', function() {
        if (errorBatch.length > 0) {
            const errors = errorBatch.splice(0, errorBatch.length);
            errors.forEach(function(errorData) {
                // Use sendBeacon for reliability during unload
                if (navigator.sendBeacon) {
                    navigator.sendBeacon(ERROR_ENDPOINT, JSON.stringify(errorData));
                } else {
                    sendError(errorData);
                }
            });
        }
    });
    
    /**
     * API for manual error reporting
     */
    window.reportError = function(message, details) {
        reportError({
            message: message,
            stack: new Error().stack,
            errorType: 'manual',
            details: details
        });
    };
    
    /**
     * Track specific user actions that might cause errors
     */
    window.trackAction = function(action, metadata) {
        try {
            fetch(PERFORMANCE_ENDPOINT, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    metric: 'user_action',
                    value: 0,
                    url: window.location.href,
                    metadata: Object.assign({
                        action: action
                    }, metadata || {})
                })
            }).catch(function() {
                // Silently fail
            });
        } catch (e) {
            // Silently fail
        }
    };
    
})();