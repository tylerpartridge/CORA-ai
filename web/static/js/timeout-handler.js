/**
 * CORA Timeout Handler
 * Manages request timeouts with user feedback and retry mechanisms
 * Enhanced for performance and user experience
 */

class TimeoutHandler {
    constructor() {
        this.defaultTimeout = 30000; // 30 seconds
        this.timeoutConfig = {
            short: 5000,    // 5 seconds for quick operations
            medium: 15000,  // 15 seconds for normal operations
            long: 30000,    // 30 seconds for complex operations
            upload: 60000   // 60 seconds for file uploads
        };
        
        this.activeRequests = new Map();
        this.retryConfig = {
            maxRetries: 3,
            baseDelay: 1000,
            maxDelay: 10000,
            backoffMultiplier: 2
        };
        
        this.timeoutIndicators = new Map();
        
        this.init();
    }

    /**
     * Initialize timeout handler
     */
    init() {
        // Skip ALL timeout handling on landing page
        if (window.location.pathname === '/') {
            // console.log('⏱️ CORA Timeout Handler - Skipped on landing page');
            return;
        }
        
        // Create timeout indicator container
        this.createTimeoutContainer();
        
        // Set up global timeout handling
        this.setupGlobalHandlers();
        
        // console.log('⏱️ CORA Timeout Handler initialized');
    }

    /**
     * Create timeout indicator container
     */
    createTimeoutContainer() {
        const container = document.createElement('div');
        container.id = 'cora-timeout-container';
        container.className = 'cora-timeout-container';
        container.setAttribute('aria-live', 'polite');
        
        // Add styles
        const style = document.createElement('style');
        style.textContent = `
            .cora-timeout-container {
                position: fixed;
                top: 50%;
                left: 50%;
                transform: translate(-50%, -50%);
                z-index: 10001;
                pointer-events: none;
            }
            
            .cora-timeout-indicator {
                background: var(--wellness-bg-card);
                border: 2px solid var(--wellness-border-primary);
                border-radius: var(--wellness-radius-lg);
                padding: var(--wellness-space-lg);
                box-shadow: var(--wellness-shadow-xl);
                pointer-events: auto;
                text-align: center;
                min-width: 300px;
                max-width: 400px;
                transform: scale(0.8);
                opacity: 0;
                transition: all 300ms ease;
            }
            
            .cora-timeout-indicator.show {
                transform: scale(1);
                opacity: 1;
            }
            
            .cora-timeout-indicator.hide {
                transform: scale(0.8);
                opacity: 0;
            }
            
            .cora-timeout-icon {
                font-size: 2rem;
                margin-bottom: var(--wellness-space-md);
                animation: pulse 2s ease-in-out infinite;
            }
            
            .cora-timeout-title {
                font-weight: 600;
                color: var(--wellness-text-primary);
                font-size: var(--wellness-font-size-lg);
                margin-bottom: var(--wellness-space-sm);
            }
            
            .cora-timeout-message {
                color: var(--wellness-text-secondary);
                font-size: var(--wellness-font-size-base);
                line-height: 1.5;
                margin-bottom: var(--wellness-space-lg);
            }
            
            .cora-timeout-progress {
                width: 100%;
                height: 6px;
                background: var(--wellness-bg-tertiary);
                border-radius: var(--wellness-radius-full);
                overflow: hidden;
                margin-bottom: var(--wellness-space-md);
            }
            
            .cora-timeout-progress-bar {
                height: 100%;
                background: linear-gradient(90deg, var(--wellness-primary), var(--wellness-peace));
                border-radius: var(--wellness-radius-full);
                transition: width linear;
                position: relative;
            }
            
            .cora-timeout-progress-bar::after {
                content: '';
                position: absolute;
                top: 0;
                left: 0;
                right: 0;
                bottom: 0;
                background: linear-gradient(90deg, 
                    transparent 0%, 
                    rgba(255, 255, 255, 0.3) 50%, 
                    transparent 100%);
                animation: shimmer 2s ease-in-out infinite;
            }
            
            .cora-timeout-actions {
                display: flex;
                gap: var(--wellness-space-sm);
                justify-content: center;
            }
            
            .cora-timeout-btn {
                padding: var(--wellness-space-sm) var(--wellness-space-md);
                border: 1px solid var(--wellness-border-primary);
                background: var(--wellness-bg-secondary);
                color: var(--wellness-text-primary);
                border-radius: var(--wellness-radius-md);
                font-size: var(--wellness-font-size-sm);
                cursor: pointer;
                transition: all 200ms ease;
            }
            
            .cora-timeout-btn:hover {
                background: var(--wellness-bg-tertiary);
                border-color: var(--wellness-border-secondary);
            }
            
            .cora-timeout-btn.primary {
                background: var(--wellness-primary);
                color: white;
                border-color: var(--wellness-primary);
            }
            
            .cora-timeout-btn.primary:hover {
                background: var(--wellness-primary-hover);
            }
            
            .cora-timeout-time {
                font-size: var(--wellness-font-size-sm);
                color: var(--wellness-text-muted);
                margin-top: var(--wellness-space-sm);
            }
            
            @keyframes pulse {
                0%, 100% { transform: scale(1); }
                50% { transform: scale(1.1); }
            }
            
            @keyframes shimmer {
                0% { transform: translateX(-100%); }
                100% { transform: translateX(100%); }
            }
            
            @media (max-width: 768px) {
                .cora-timeout-indicator {
                    min-width: 280px;
                    margin: 0 var(--wellness-space-md);
                }
            }
        `;
        
        document.head.appendChild(style);
        document.body.appendChild(container);
    }

    /**
     * Set up global timeout handling
     */
    setupGlobalHandlers() {
        // Intercept fetch requests for timeout handling
        this.interceptFetch();
        
        // Handle page visibility changes
        document.addEventListener('visibilitychange', () => {
            if (document.hidden) {
                this.pauseActiveTimeouts();
            } else {
                this.resumeActiveTimeouts();
            }
        });
    }

    /**
     * Intercept fetch requests for timeout handling
     */
    interceptFetch() {
        // Skip timeout handling on landing page to prevent errors
        if (window.location.pathname === '/') {
            return;
        }
        
        const originalFetch = window.fetch;
        
        window.fetch = async (...args) => {
            const [url, options = {}] = args;
            const timeout = options.timeout || this.defaultTimeout;
            
            // Create abort controller for timeout
            const controller = new AbortController();
            const timeoutId = setTimeout(() => {
                controller.abort();
            }, timeout);
            
            // Add signal to options
            const fetchOptions = {
                ...options,
                signal: controller.signal
            };
            
            // Create request ID
            const requestId = this.generateRequestId();
            
            // Show timeout indicator
            this.showTimeoutIndicator(requestId, timeout);
            
            try {
                const response = await originalFetch(url, fetchOptions);
                clearTimeout(timeoutId);
                this.hideTimeoutIndicator(requestId);
                return response;
            } catch (error) {
                clearTimeout(timeoutId);
                this.hideTimeoutIndicator(requestId);
                
                if (error.name === 'AbortError') {
                    this.handleTimeout(requestId, url, timeout);
                }
                
                throw error;
            }
        };
    }

    /**
     * Show timeout indicator
     */
    showTimeoutIndicator(requestId, timeout) {
        const container = document.getElementById('cora-timeout-container');
        if (!container) return;

        const indicator = document.createElement('div');
        indicator.className = 'cora-timeout-indicator';
        indicator.id = `timeout-${requestId}`;

        const icon = document.createElement('div');
        icon.className = 'cora-timeout-icon';
        icon.innerHTML = '⏱️';

        const title = document.createElement('div');
        title.className = 'cora-timeout-title';
        title.textContent = 'Processing Request';

        const message = document.createElement('div');
        message.className = 'cora-timeout-message';
        message.textContent = 'Please wait while we process your request...';

        const progress = document.createElement('div');
        progress.className = 'cora-timeout-progress';
        
        const progressBar = document.createElement('div');
        progressBar.className = 'cora-timeout-progress-bar';
        progressBar.style.width = '100%';
        
        progress.appendChild(progressBar);

        const time = document.createElement('div');
        time.className = 'cora-timeout-time';
        time.textContent = `Timeout: ${timeout / 1000}s`;

        indicator.appendChild(icon);
        indicator.appendChild(title);
        indicator.appendChild(message);
        indicator.appendChild(progress);
        indicator.appendChild(time);

        container.appendChild(indicator);

        // Animate in
        setTimeout(() => {
            indicator.classList.add('show');
        }, 100);

        // Animate progress bar
        setTimeout(() => {
            progressBar.style.width = '0%';
        }, 100);

        // Store indicator reference
        this.timeoutIndicators.set(requestId, {
            element: indicator,
            startTime: Date.now(),
            timeout: timeout,
            progressBar: progressBar
        });

        // Update progress
        this.updateProgress(requestId);
    }

    /**
     * Update progress bar
     */
    updateProgress(requestId) {
        const indicator = this.timeoutIndicators.get(requestId);
        if (!indicator) return;

        const elapsed = Date.now() - indicator.startTime;
        const progress = Math.max(0, 100 - (elapsed / indicator.timeout) * 100);
        
        if (indicator.progressBar) {
            indicator.progressBar.style.width = `${progress}%`;
        }

        // Continue updating if not complete
        if (progress > 0) {
            requestAnimationFrame(() => this.updateProgress(requestId));
        }
    }

    /**
     * Hide timeout indicator
     */
    hideTimeoutIndicator(requestId) {
        const indicator = this.timeoutIndicators.get(requestId);
        if (!indicator) return;

        indicator.element.classList.add('hide');
        setTimeout(() => {
            indicator.element.remove();
            this.timeoutIndicators.delete(requestId);
        }, 300);
    }

    /**
     * Handle timeout
     */
    handleTimeout(requestId, url, timeout) {
        const indicator = this.timeoutIndicators.get(requestId);
        if (!indicator) return;

        // Update indicator for timeout
        const title = indicator.element.querySelector('.cora-timeout-title');
        const message = indicator.element.querySelector('.cora-timeout-message');
        const icon = indicator.element.querySelector('.cora-timeout-icon');
        const actions = indicator.element.querySelector('.cora-timeout-actions');

        if (title) title.textContent = 'Request Timeout';
        if (message) message.textContent = 'The request took too long to complete. Would you like to retry?';
        if (icon) icon.innerHTML = '⏰';

        // Add retry button
        if (!actions) {
            const actionsDiv = document.createElement('div');
            actionsDiv.className = 'cora-timeout-actions';

            const retryBtn = document.createElement('button');
            retryBtn.className = 'cora-timeout-btn primary';
            retryBtn.textContent = 'Retry';
            retryBtn.onclick = () => this.retryRequest(requestId, url, timeout);

            const cancelBtn = document.createElement('button');
            cancelBtn.className = 'cora-timeout-btn';
            cancelBtn.textContent = 'Cancel';
            cancelBtn.onclick = () => this.hideTimeoutIndicator(requestId);

            actionsDiv.appendChild(retryBtn);
            actionsDiv.appendChild(cancelBtn);
            indicator.element.appendChild(actionsDiv);
        }

        // Log timeout
        // console.warn(`[CORA Timeout] Request timed out after ${timeout}ms:`, url);
    }

    /**
     * Retry request
     */
    retryRequest(requestId, url, timeout) {
        // Hide current indicator
        this.hideTimeoutIndicator(requestId);

        // Show retry notification
        if (window.errorManager) {
            window.errorManager.showNotification({
                type: 'info',
                title: 'Retrying Request',
                message: 'Attempting to retry the request...',
                icon: '🔄',
                duration: 2000
            });
        }

        // Retry the request
        setTimeout(() => {
            fetch(url, { timeout: timeout * 1.5 }); // Increase timeout for retry
        }, 1000);
    }

    /**
     * Pause active timeouts when page is hidden
     */
    pauseActiveTimeouts() {
        for (const [requestId, indicator] of this.timeoutIndicators) {
            indicator.paused = true;
            indicator.pauseTime = Date.now();
        }
    }

    /**
     * Resume active timeouts when page is visible
     */
    resumeActiveTimeouts() {
        for (const [requestId, indicator] of this.timeoutIndicators) {
            if (indicator.paused) {
                const pauseDuration = Date.now() - indicator.pauseTime;
                indicator.startTime += pauseDuration;
                indicator.paused = false;
                delete indicator.pauseTime;
            }
        }
    }

    /**
     * Create a fetch wrapper with timeout
     */
    fetchWithTimeout(url, options = {}) {
        const timeout = options.timeout || this.defaultTimeout;
        const controller = new AbortController();
        
        const timeoutId = setTimeout(() => {
            controller.abort();
        }, timeout);
        
        const fetchOptions = {
            ...options,
            signal: controller.signal
        };
        
        return fetch(url, fetchOptions).finally(() => {
            clearTimeout(timeoutId);
        });
    }

    /**
     * Set timeout for a specific request type
     */
    setTimeout(type, duration) {
        if (this.timeoutConfig.hasOwnProperty(type)) {
            this.timeoutConfig[type] = duration;
        }
    }

    /**
     * Get timeout for a specific request type
     */
    getTimeout(type) {
        return this.timeoutConfig[type] || this.defaultTimeout;
    }

    /**
     * Clear all active timeouts
     */
    clearAllTimeouts() {
        for (const [requestId, indicator] of this.timeoutIndicators) {
            this.hideTimeoutIndicator(requestId);
        }
    }

    /**
     * Generate unique request ID
     */
    generateRequestId() {
        return `req_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
    }

    /**
     * Get timeout statistics
     */
    getTimeoutStats() {
        return {
            activeTimeouts: this.timeoutIndicators.size,
            timeoutConfig: this.timeoutConfig,
            retryConfig: this.retryConfig
        };
    }
}

// Initialize timeout handler only if not on landing page
let timeoutHandler;
if (window.location.pathname !== '/') {
    timeoutHandler = new TimeoutHandler();
    window.timeoutHandler = timeoutHandler;
} else {
    // Create a dummy timeout handler for landing page
    timeoutHandler = {
        fetchWithTimeout: fetch,
        setTimeout: () => {},
        getTimeout: () => 30000,
        clearAllTimeouts: () => {},
        getTimeoutStats: () => ({ activeTimeouts: 0, timeoutConfig: {}, retryConfig: {} })
    };
    window.timeoutHandler = timeoutHandler;
    // console.log('⏱️ CORA Timeout Handler - Disabled on landing page');
}

// Export for use in other modules
window.TimeoutHandler = TimeoutHandler;

// Console helpers for debugging
if (typeof console !== 'undefined' && window.location.pathname !== '/') {
    // console.log('⏱️ CORA Timeout Handler initialized');
    // console.log('Available commands:');
    // console.log('- timeoutHandler.fetchWithTimeout(url, options)');
    // console.log('- timeoutHandler.setTimeout(type, duration)');
    // console.log('- timeoutHandler.clearAllTimeouts()');
    // console.log('- timeoutHandler.getTimeoutStats()');
} 