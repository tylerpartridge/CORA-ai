/**
 * CORA Error Manager
 * Handles errors gracefully with user-friendly messages and retry mechanisms
 * Enhanced for accessibility and user experience
 */

class ErrorManager {
    constructor() {
        this.errorTypes = {
            NETWORK: 'network',
            TIMEOUT: 'timeout',
            VALIDATION: 'validation',
            AUTHENTICATION: 'authentication',
            AUTHORIZATION: 'authorization',
            SERVER: 'server',
            UNKNOWN: 'unknown'
        };
        
        this.errorMessages = {
            [this.errorTypes.NETWORK]: {
                title: 'Connection Issue',
                message: 'Unable to connect to the server. Please check your internet connection and try again.',
                icon: '🌐',
                retry: true,
                duration: 5000
            },
            [this.errorTypes.TIMEOUT]: {
                title: 'Request Timeout',
                message: 'The request took too long to complete. Please try again.',
                icon: '⏱️',
                retry: true,
                duration: 4000
            },
            [this.errorTypes.VALIDATION]: {
                title: 'Invalid Input',
                message: 'Please check your input and try again.',
                icon: '⚠️',
                retry: false,
                duration: 6000
            },
            [this.errorTypes.AUTHENTICATION]: {
                title: 'Authentication Required',
                message: 'Please log in to continue.',
                icon: '🔐',
                retry: false,
                duration: 0
            },
            [this.errorTypes.AUTHORIZATION]: {
                title: 'Access Denied',
                message: 'You don\'t have permission to perform this action.',
                icon: '🚫',
                retry: false,
                duration: 5000
            },
            [this.errorTypes.SERVER]: {
                title: 'Server Error',
                message: 'Something went wrong on our end. We\'re working to fix it.',
                icon: '🔧',
                retry: true,
                duration: 8000
            },
            [this.errorTypes.UNKNOWN]: {
                title: 'Unexpected Error',
                message: 'An unexpected error occurred. Please try again.',
                icon: '❓',
                retry: true,
                duration: 5000
            }
        };
        
        this.retryConfig = {
            maxRetries: 3,
            baseDelay: 1000,
            maxDelay: 10000,
            backoffMultiplier: 2
        };
        
        this.activeErrors = new Map();
        this.retryAttempts = new Map();
        
        this.init();
    }

    /**
     * Initialize error manager
     */
    init() {
        // Skip ALL error handling on landing page
        if (window.location.pathname === '/') {
            // console.log('🔧 CORA Error Manager - Skipped on landing page');
            return;
        }
        
        // Create error container
        this.createErrorContainer();
        
        // Set up global error handlers
        this.setupGlobalHandlers();
        
        // Set up offline detection
        this.setupOfflineDetection();
        
        // console.log('🔧 CORA Error Manager initialized');
    }

    /**
     * Create error notification container
     */
    createErrorContainer() {
        const container = document.createElement('div');
        container.id = 'cora-error-container';
        container.className = 'cora-error-container';
        container.setAttribute('aria-live', 'polite');
        container.setAttribute('aria-atomic', 'true');
        
        // Add styles
        const style = document.createElement('style');
        style.textContent = `
            .cora-error-container {
                position: fixed;
                top: 20px;
                right: 20px;
                z-index: 10000;
                max-width: 400px;
                pointer-events: none;
            }
            
            .cora-error-notification {
                background: var(--wellness-bg-card);
                border: 2px solid var(--wellness-border-primary);
                border-left: 4px solid var(--wellness-danger);
                border-radius: var(--wellness-radius-lg);
                padding: var(--wellness-space-md);
                margin-bottom: var(--wellness-space-sm);
                box-shadow: var(--wellness-shadow-lg);
                pointer-events: auto;
                transform: translateX(100%);
                opacity: 0;
                transition: all 300ms ease;
                max-width: 100%;
            }
            
            .cora-error-notification.show {
                transform: translateX(0);
                opacity: 1;
            }
            
            .cora-error-notification.hide {
                transform: translateX(100%);
                opacity: 0;
            }
            
            .cora-error-header {
                display: flex;
                align-items: center;
                justify-content: space-between;
                margin-bottom: var(--wellness-space-sm);
            }
            
            .cora-error-title {
                font-weight: 600;
                color: var(--wellness-text-primary);
                font-size: var(--wellness-font-size-base);
                display: flex;
                align-items: center;
                gap: var(--wellness-space-sm);
            }
            
            .cora-error-close {
                background: none;
                border: none;
                color: var(--wellness-text-muted);
                cursor: pointer;
                padding: 4px;
                border-radius: var(--wellness-radius-sm);
                transition: all 200ms ease;
                font-size: 18px;
                line-height: 1;
            }
            
            .cora-error-close:hover {
                background: var(--wellness-bg-tertiary);
                color: var(--wellness-text-primary);
            }
            
            .cora-error-message {
                color: var(--wellness-text-secondary);
                font-size: var(--wellness-font-size-sm);
                line-height: 1.5;
                margin-bottom: var(--wellness-space-sm);
            }
            
            .cora-error-actions {
                display: flex;
                gap: var(--wellness-space-sm);
                justify-content: flex-end;
            }
            
            .cora-error-btn {
                padding: var(--wellness-space-xs) var(--wellness-space-sm);
                border: 1px solid var(--wellness-border-primary);
                background: var(--wellness-bg-secondary);
                color: var(--wellness-text-primary);
                border-radius: var(--wellness-radius-sm);
                font-size: var(--wellness-font-size-xs);
                cursor: pointer;
                transition: all 200ms ease;
            }
            
            .cora-error-btn:hover {
                background: var(--wellness-bg-tertiary);
                border-color: var(--wellness-border-secondary);
            }
            
            .cora-error-btn.primary {
                background: var(--wellness-primary);
                color: white;
                border-color: var(--wellness-primary);
            }
            
            .cora-error-btn.primary:hover {
                background: var(--wellness-primary-hover);
            }
            
            .cora-error-progress {
                height: 3px;
                background: var(--wellness-bg-tertiary);
                border-radius: var(--wellness-radius-full);
                overflow: hidden;
                margin-top: var(--wellness-space-sm);
            }
            
            .cora-error-progress-bar {
                height: 100%;
                background: var(--wellness-danger);
                transition: width linear;
            }
            
            @media (max-width: 768px) {
                .cora-error-container {
                    top: 10px;
                    right: 10px;
                    left: 10px;
                    max-width: none;
                }
                
                .cora-error-notification {
                    max-width: none;
                }
            }
        `;
        
        document.head.appendChild(style);
        document.body.appendChild(container);
    }

    /**
     * Set up global error handlers
     */
    setupGlobalHandlers() {
        // Handle unhandled promise rejections
        window.addEventListener('unhandledrejection', (event) => {
            event.preventDefault();
            // Skip all error popups on landing page
            if (window.location.pathname === '/') {
                // console.log('Skipping error popup for landing page');
                return;
            }
            this.handleError(event.reason, this.errorTypes.UNKNOWN);
        });

        // Handle global errors
        window.addEventListener('error', (event) => {
            event.preventDefault();
            // Skip all error popups on landing page
            if (window.location.pathname === '/') {
                // console.log('Skipping error popup for landing page');
                return;
            }
            this.handleError(event.error, this.errorTypes.UNKNOWN);
        });

        // Handle fetch errors
        this.interceptFetch();
    }

    /**
     * Intercept fetch requests for error handling
     */
    interceptFetch() {
        // Skip error handling on landing page to prevent popups
        if (window.location.pathname === '/') {
            return;
        }
        
        const originalFetch = window.fetch;
        
        window.fetch = async (...args) => {
            try {
                const response = await originalFetch(...args);
                
                // Handle HTTP errors
                if (!response.ok) {
                    const errorType = this.getErrorTypeFromStatus(response.status);
                    const error = new Error(`HTTP ${response.status}: ${response.statusText}`);
                    error.status = response.status;
                    error.response = response;
                    
                    this.handleError(error, errorType);
                    throw error;
                }
                
                return response;
            } catch (error) {
                // Handle network errors
                if (error.name === 'TypeError' && error.message.includes('fetch')) {
                    this.handleError(error, this.errorTypes.NETWORK);
                } else if (error.name === 'AbortError') {
                    this.handleError(error, this.errorTypes.TIMEOUT);
                } else {
                    this.handleError(error, this.errorTypes.UNKNOWN);
                }
                
                throw error;
            }
        };
    }

    /**
     * Set up offline detection
     */
    setupOfflineDetection() {
        window.addEventListener('online', () => {
            this.showNotification({
                type: 'success',
                title: 'Connection Restored',
                message: 'You\'re back online!',
                icon: '✅',
                duration: 3000
            });
        });

        window.addEventListener('offline', () => {
            this.handleError(new Error('No internet connection'), this.errorTypes.NETWORK);
        });
    }

    /**
     * Get error type from HTTP status code
     */
    getErrorTypeFromStatus(status) {
        if (status >= 500) return this.errorTypes.SERVER;
        if (status === 401) return this.errorTypes.AUTHENTICATION;
        if (status === 403) return this.errorTypes.AUTHORIZATION;
        if (status === 408 || status === 504) return this.errorTypes.TIMEOUT;
        if (status >= 400) return this.errorTypes.VALIDATION;
        return this.errorTypes.UNKNOWN;
    }

    /**
     * Handle an error
     */
    handleError(error, type = null) {
        // Skip all error handling on landing page
        if (window.location.pathname === '/') {
            // console.log('Skipping error handling on landing page');
            return;
        }
        
        // Determine error type if not provided
        if (!type) {
            type = this.determineErrorType(error);
        }

        // Get error configuration
        const config = this.errorMessages[type] || this.errorMessages[this.errorTypes.UNKNOWN];
        
        // Create unique error ID
        const errorId = this.generateErrorId();
        
        // Store error information
        this.activeErrors.set(errorId, {
            error,
            type,
            config,
            timestamp: Date.now()
        });

        // Show error notification
        this.showErrorNotification(errorId, config, error);

        // Log error for debugging
        this.logError(error, type);

        // Handle retry logic
        if (config.retry) {
            this.scheduleRetry(errorId, error, type);
        }

        return errorId;
    }

    /**
     * Determine error type from error object
     */
    determineErrorType(error) {
        if (error.name === 'NetworkError' || error.message.includes('network')) {
            return this.errorTypes.NETWORK;
        }
        if (error.name === 'TimeoutError' || error.message.includes('timeout')) {
            return this.errorTypes.TIMEOUT;
        }
        if (error.name === 'ValidationError' || error.message.includes('validation')) {
            return this.errorTypes.VALIDATION;
        }
        if (error.status === 401) {
            return this.errorTypes.AUTHENTICATION;
        }
        if (error.status === 403) {
            return this.errorTypes.AUTHORIZATION;
        }
        if (error.status >= 500) {
            return this.errorTypes.SERVER;
        }
        return this.errorTypes.UNKNOWN;
    }

    /**
     * Show error notification
     */
    showErrorNotification(errorId, config, error) {
        const container = document.getElementById('cora-error-container');
        if (!container) return;

        const notification = document.createElement('div');
        notification.className = 'cora-error-notification';
        notification.id = `error-${errorId}`;
        notification.setAttribute('role', 'alert');

        const header = document.createElement('div');
        header.className = 'cora-error-header';

        const title = document.createElement('div');
        title.className = 'cora-error-title';
        title.innerHTML = `${config.icon} ${config.title}`;

        const closeBtn = document.createElement('button');
        closeBtn.className = 'cora-error-close';
        closeBtn.innerHTML = '×';
        closeBtn.setAttribute('aria-label', 'Close error notification');
        closeBtn.onclick = () => this.dismissError(errorId);

        header.appendChild(title);
        header.appendChild(closeBtn);

        const message = document.createElement('div');
        message.className = 'cora-error-message';
        message.textContent = config.message;

        notification.appendChild(header);
        notification.appendChild(message);

        // Add retry button if applicable
        if (config.retry) {
            const actions = document.createElement('div');
            actions.className = 'cora-error-actions';

            const retryBtn = document.createElement('button');
            retryBtn.className = 'cora-error-btn primary';
            retryBtn.textContent = 'Retry';
            retryBtn.onclick = () => this.retryError(errorId);

            actions.appendChild(retryBtn);
            notification.appendChild(actions);
        }

        // Add progress bar for auto-dismiss
        if (config.duration > 0) {
            const progress = document.createElement('div');
            progress.className = 'cora-error-progress';
            
            const progressBar = document.createElement('div');
            progressBar.className = 'cora-error-progress-bar';
            progressBar.style.width = '100%';
            
            progress.appendChild(progressBar);
            notification.appendChild(progress);

            // Animate progress bar
            setTimeout(() => {
                progressBar.style.width = '0%';
            }, 100);

            // Auto-dismiss
            setTimeout(() => {
                this.dismissError(errorId);
            }, config.duration);
        }

        container.appendChild(notification);

        // Animate in
        setTimeout(() => {
            notification.classList.add('show');
        }, 100);
    }

    /**
     * Show success notification
     */
    showNotification({ type, title, message, icon, duration = 5000 }) {
        const container = document.getElementById('cora-error-container');
        if (!container) return;

        const notification = document.createElement('div');
        notification.className = 'cora-error-notification';
        notification.style.borderLeftColor = type === 'success' ? 'var(--wellness-success)' : 'var(--wellness-primary)';
        notification.setAttribute('role', 'status');

        const header = document.createElement('div');
        header.className = 'cora-error-header';

        const titleEl = document.createElement('div');
        titleEl.className = 'cora-error-title';
        titleEl.innerHTML = `${icon} ${title}`;

        const closeBtn = document.createElement('button');
        closeBtn.className = 'cora-error-close';
        closeBtn.innerHTML = '×';
        closeBtn.setAttribute('aria-label', 'Close notification');
        closeBtn.onclick = () => notification.remove();

        header.appendChild(titleEl);
        header.appendChild(closeBtn);

        const messageEl = document.createElement('div');
        messageEl.className = 'cora-error-message';
        messageEl.textContent = message;

        notification.appendChild(header);
        notification.appendChild(messageEl);

        container.appendChild(notification);

        // Animate in
        setTimeout(() => {
            notification.classList.add('show');
        }, 100);

        // Auto-dismiss
        if (duration > 0) {
            setTimeout(() => {
                notification.classList.add('hide');
                setTimeout(() => notification.remove(), 300);
            }, duration);
        }
    }

    /**
     * Dismiss error notification
     */
    dismissError(errorId) {
        const notification = document.getElementById(`error-${errorId}`);
        if (notification) {
            notification.classList.add('hide');
            setTimeout(() => {
                notification.remove();
                this.activeErrors.delete(errorId);
            }, 300);
        }
    }

    /**
     * Schedule retry for an error
     */
    scheduleRetry(errorId, error, type) {
        const attempts = this.retryAttempts.get(errorId) || 0;
        
        if (attempts >= this.retryConfig.maxRetries) {
            return;
        }

        const delay = Math.min(
            this.retryConfig.baseDelay * Math.pow(this.retryConfig.backoffMultiplier, attempts),
            this.retryConfig.maxDelay
        );

        setTimeout(() => {
            this.retryError(errorId);
        }, delay);
    }

    /**
     * Retry an error
     */
    retryError(errorId) {
        const errorInfo = this.activeErrors.get(errorId);
        if (!errorInfo) return;

        const attempts = this.retryAttempts.get(errorId) || 0;
        this.retryAttempts.set(errorId, attempts + 1);

        // Dismiss current notification
        this.dismissError(errorId);

        // Show retry notification
        this.showNotification({
            type: 'info',
            title: 'Retrying...',
            message: `Attempt ${attempts + 1} of ${this.retryConfig.maxRetries}`,
            icon: '🔄',
            duration: 2000
        });

        // Re-throw the error to trigger retry
        setTimeout(() => {
            this.handleError(errorInfo.error, errorInfo.type);
        }, 1000);
    }

    /**
     * Generate unique error ID
     */
    generateErrorId() {
        return `error_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
    }

    /**
     * Log error for debugging
     */
    logError(error, type) {
        // console.error(`[CORA Error] Type: ${type}`, error);
        
        // Send to analytics if available
        if (window.coraAnalytics && typeof window.coraAnalytics.track === 'function') {
            window.coraAnalytics.track('error_occurred', {
                type,
                message: error.message,
                stack: error.stack,
                timestamp: Date.now()
            });
        }
    }

    /**
     * Clear all errors
     */
    clearAllErrors() {
        this.activeErrors.clear();
        this.retryAttempts.clear();
        
        const container = document.getElementById('cora-error-container');
        if (container) {
            container.innerHTML = '';
        }
    }

    /**
     * Get error statistics
     */
    getErrorStats() {
        const stats = {
            totalErrors: this.activeErrors.size,
            errorTypes: {},
            retryAttempts: this.retryAttempts.size
        };

        for (const [_, errorInfo] of this.activeErrors) {
            const type = errorInfo.type;
            stats.errorTypes[type] = (stats.errorTypes[type] || 0) + 1;
        }

        return stats;
    }
}

// Initialize error manager only if not on landing page
let errorManager;
if (window.location.pathname !== '/') {
    errorManager = new ErrorManager();
    window.errorManager = errorManager;
} else {
    // Create a dummy error manager for landing page
    errorManager = {
        handleError: () => {},
        showNotification: () => {},
        clearAllErrors: () => {},
        getErrorStats: () => ({ totalErrors: 0, errorTypes: {}, retryAttempts: 0 })
    };
    window.errorManager = errorManager;
    // console.log('🔧 CORA Error Manager - Disabled on landing page');
}

// Export for use in other modules
window.ErrorManager = ErrorManager;

// Console helpers for debugging
if (typeof console !== 'undefined' && window.location.pathname !== '/') {
    // console.log('🔧 CORA Error Manager initialized');
    // console.log('Available commands:');
    // console.log('- errorManager.handleError(error, type)');
    // console.log('- errorManager.showNotification(config)');
    // console.log('- errorManager.clearAllErrors()');
    // console.log('- errorManager.getErrorStats()');
} 