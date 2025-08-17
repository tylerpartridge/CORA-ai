/**
 * CORA Loading States Utility
 * 
 * Provides standardized loading indicators and skeleton screens across the application
 * for consistent user experience during async operations.
 */

class CORALoadingStates {
    constructor() {
        this.loadingOverlays = new Map();
        this.skeletonScreens = new Map();
        this.progressBars = new Map();
        
        this.init();
    }
    
    init() {
        // Create global loading overlay
        this.createGlobalLoadingOverlay();
        
        // Setup skeleton screen templates
        this.setupSkeletonTemplates();
        
        // Setup progress bar templates
        this.setupProgressBarTemplates();
    }
    
    /**
     * Global Loading Overlay
     */
    createGlobalLoadingOverlay() {
        const overlay = document.createElement('div');
        overlay.id = 'cora-global-loading-overlay';
        overlay.className = 'cora-loading-overlay hidden';
        overlay.innerHTML = `
            <div class="cora-loading-content">
                <div class="cora-loading-spinner"></div>
                <div class="cora-loading-text">Loading...</div>
                <div class="cora-loading-progress">
                    <div class="cora-progress-bar">
                        <div class="cora-progress-fill"></div>
                    </div>
                </div>
            </div>
        `;
        
        document.body.appendChild(overlay);
        this.loadingOverlays.set('global', overlay);
    }
    
    /**
     * Show Global Loading Overlay
     */
    showGlobalLoading(message = 'Loading...', showProgress = false) {
        const overlay = this.loadingOverlays.get('global');
        if (overlay) {
            const textElement = overlay.querySelector('.cora-loading-text');
            const progressElement = overlay.querySelector('.cora-loading-progress');
            
            textElement.textContent = message;
            progressElement.style.display = showProgress ? 'block' : 'none';
            
            overlay.classList.remove('hidden');
            document.body.style.overflow = 'hidden';
        }
    }
    
    /**
     * Hide Global Loading Overlay
     */
    hideGlobalLoading() {
        const overlay = this.loadingOverlays.get('global');
        if (overlay) {
            overlay.classList.add('hidden');
            document.body.style.overflow = '';
        }
    }
    
    /**
     * Update Global Loading Progress
     */
    updateGlobalProgress(percentage) {
        const overlay = this.loadingOverlays.get('global');
        if (overlay) {
            const progressFill = overlay.querySelector('.cora-progress-fill');
            progressFill.style.width = `${percentage}%`;
        }
    }
    
    /**
     * Button Loading State
     */
    setButtonLoading(button, loading = true, text = 'Loading...') {
        if (!button) return;
        
        if (loading) {
            button.disabled = true;
            button.dataset.originalText = button.innerHTML;
            button.innerHTML = `
                <i class="fas fa-spinner fa-spin me-2"></i>
                ${text}
            `;
        } else {
            button.disabled = false;
            button.innerHTML = button.dataset.originalText || button.innerHTML;
        }
    }
    
    /**
     * Form Loading State
     */
    setFormLoading(form, loading = true) {
        if (!form) return;
        
        const inputs = form.querySelectorAll('input, select, textarea, button');
        const submitBtn = form.querySelector('button[type="submit"]');
        
        inputs.forEach(input => {
            input.disabled = loading;
        });
        
        if (submitBtn) {
            this.setButtonLoading(submitBtn, loading, 'Processing...');
        }
    }
    
    /**
     * Skeleton Screen Management
     */
    setupSkeletonTemplates() {
        // Card skeleton template
        this.skeletonTemplates = {
            card: `
                <div class="cora-skeleton-card">
                    <div class="cora-skeleton-line long"></div>
                    <div class="cora-skeleton-line medium"></div>
                    <div class="cora-skeleton-line short"></div>
                </div>
            `,
            table: `
                <div class="cora-skeleton-table">
                    <div class="cora-skeleton-row">
                        <div class="cora-skeleton-cell"></div>
                        <div class="cora-skeleton-cell"></div>
                        <div class="cora-skeleton-cell"></div>
                    </div>
                    <div class="cora-skeleton-row">
                        <div class="cora-skeleton-cell"></div>
                        <div class="cora-skeleton-cell"></div>
                        <div class="cora-skeleton-cell"></div>
                    </div>
                </div>
            `,
            list: `
                <div class="cora-skeleton-list">
                    <div class="cora-skeleton-item"></div>
                    <div class="cora-skeleton-item"></div>
                    <div class="cora-skeleton-item"></div>
                </div>
            `
        };
    }
    
    /**
     * Show Skeleton Screen
     */
    showSkeleton(container, type = 'card', count = 3) {
        if (!container) return;
        
        const template = this.skeletonTemplates[type];
        if (!template) return;
        
        container.innerHTML = template.repeat(count);
        container.classList.add('cora-skeleton-active');
    }
    
    /**
     * Hide Skeleton Screen
     */
    hideSkeleton(container) {
        if (!container) return;
        
        container.classList.remove('cora-skeleton-active');
    }
    
    /**
     * Progress Bar Management
     */
    setupProgressBarTemplates() {
        this.progressTemplates = {
            linear: `
                <div class="cora-progress-linear">
                    <div class="cora-progress-track">
                        <div class="cora-progress-fill"></div>
                    </div>
                    <div class="cora-progress-text">0%</div>
                </div>
            `,
            circular: `
                <div class="cora-progress-circular">
                    <svg class="cora-progress-svg" viewBox="0 0 36 36">
                        <path class="cora-progress-bg" d="M18 2.0845 a 15.9155 15.9155 0 0 1 0 31.831 a 15.9155 15.9155 0 0 1 0 -31.831"/>
                        <path class="cora-progress-fill" d="M18 2.0845 a 15.9155 15.9155 0 0 1 0 31.831 a 15.9155 15.9155 0 0 1 0 -31.831"/>
                    </svg>
                    <div class="cora-progress-text">0%</div>
                </div>
            `
        };
    }
    
    /**
     * Create Progress Bar
     */
    createProgressBar(container, type = 'linear') {
        if (!container) return;
        
        const template = this.progressTemplates[type];
        if (!template) return;
        
        container.innerHTML = template;
        this.progressBars.set(container.id || 'default', container);
    }
    
    /**
     * Update Progress Bar
     */
    updateProgress(containerId, percentage) {
        const container = this.progressBars.get(containerId);
        if (!container) return;
        
        const fill = container.querySelector('.cora-progress-fill');
        const text = container.querySelector('.cora-progress-text');
        
        if (fill) {
            if (container.querySelector('.cora-progress-svg')) {
                // Circular progress
                const circumference = 2 * Math.PI * 15.9155;
                const offset = circumference - (percentage / 100) * circumference;
                fill.style.strokeDasharray = circumference;
                fill.style.strokeDashoffset = offset;
            } else {
                // Linear progress
                fill.style.width = `${percentage}%`;
            }
        }
        
        if (text) {
            text.textContent = `${Math.round(percentage)}%`;
        }
    }
    
    /**
     * Inline Loading Indicator
     */
    createInlineLoader(text = 'Loading...') {
        const loader = document.createElement('div');
        loader.className = 'cora-inline-loader';
        loader.innerHTML = `
            <i class="fas fa-spinner fa-spin me-2"></i>
            <span>${text}</span>
        `;
        return loader;
    }
    
    /**
     * Replace Content with Loading
     */
    replaceWithLoading(element, text = 'Loading...') {
        if (!element) return;
        
        element.dataset.originalContent = element.innerHTML;
        element.innerHTML = this.createInlineLoader(text).outerHTML;
    }
    
    /**
     * Restore Original Content
     */
    restoreContent(element) {
        if (!element) return;
        
        if (element.dataset.originalContent) {
            element.innerHTML = element.dataset.originalContent;
            delete element.dataset.originalContent;
        }
    }
    
    /**
     * Loading State for API Calls
     */
    async withLoading(apiCall, options = {}) {
        const {
            showGlobal = false,
            showButton = null,
            showSkeleton = null,
            message = 'Loading...',
            buttonText = 'Processing...'
        } = options;
        
        try {
            // Show loading states
            if (showGlobal) {
                this.showGlobalLoading(message);
            }
            
            if (showButton) {
                this.setButtonLoading(showButton, true, buttonText);
            }
            
            if (showSkeleton) {
                this.showSkeleton(showSkeleton.container, showSkeleton.type, showSkeleton.count);
            }
            
            // Execute API call
            const result = await apiCall();
            
            return result;
            
        } finally {
            // Hide loading states
            if (showGlobal) {
                this.hideGlobalLoading();
            }
            
            if (showButton) {
                this.setButtonLoading(showButton, false);
            }
            
            if (showSkeleton) {
                this.hideSkeleton(showSkeleton.container);
            }
        }
    }
}

// Global instance
window.coraLoading = new CORALoadingStates();

// CSS for loading states
const loadingStyles = `
<style>
/* Loading Overlay */
.cora-loading-overlay {
    position: fixed;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    background: rgba(0, 0, 0, 0.7);
    display: flex;
    align-items: center;
    justify-content: center;
    z-index: 9999;
    backdrop-filter: blur(4px);
}

.cora-loading-overlay.hidden {
    display: none;
}

.cora-loading-content {
    background: white;
    padding: 2rem;
    border-radius: 12px;
    text-align: center;
    box-shadow: 0 20px 40px rgba(0, 0, 0, 0.3);
}

.cora-loading-spinner {
    width: 40px;
    height: 40px;
    border: 4px solid #f3f3f3;
    border-top: 4px solid #FF9800;
    border-radius: 50%;
    animation: cora-spin 1s linear infinite;
    margin: 0 auto 1rem;
}

.cora-loading-text {
    font-size: 1.1rem;
    color: #333;
    margin-bottom: 1rem;
}

.cora-progress-bar {
    width: 200px;
    height: 8px;
    background: #f3f3f3;
    border-radius: 4px;
    overflow: hidden;
}

.cora-progress-fill {
    height: 100%;
    background: linear-gradient(90deg, #FF9800, #F57C00);
    width: 0%;
    transition: width 0.3s ease;
}

/* Skeleton Screens */
.cora-skeleton-card {
    background: white;
    padding: 1.5rem;
    border-radius: 8px;
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
    margin-bottom: 1rem;
}

.cora-skeleton-line {
    height: 16px;
    background: linear-gradient(90deg, #f0f0f0 25%, #e0e0e0 50%, #f0f0f0 75%);
    background-size: 200% 100%;
    animation: cora-shimmer 1.5s infinite;
    border-radius: 4px;
    margin-bottom: 0.75rem;
}

.cora-skeleton-line.long {
    width: 100%;
}

.cora-skeleton-line.medium {
    width: 70%;
}

.cora-skeleton-line.short {
    width: 40%;
}

/* Progress Bars */
.cora-progress-linear {
    display: flex;
    align-items: center;
    gap: 1rem;
}

.cora-progress-track {
    flex: 1;
    height: 8px;
    background: #f3f3f3;
    border-radius: 4px;
    overflow: hidden;
}

.cora-progress-circular {
    position: relative;
    width: 60px;
    height: 60px;
}

.cora-progress-svg {
    width: 100%;
    height: 100%;
    transform: rotate(-90deg);
}

.cora-progress-bg {
    fill: none;
    stroke: #f3f3f3;
    stroke-width: 3;
}

.cora-progress-fill {
    fill: none;
    stroke: #FF9800;
    stroke-width: 3;
    stroke-linecap: round;
    transition: stroke-dashoffset 0.3s ease;
}

.cora-progress-text {
    font-size: 0.9rem;
    color: #666;
    font-weight: 500;
}

/* Inline Loader */
.cora-inline-loader {
    display: inline-flex;
    align-items: center;
    color: #666;
    font-size: 0.9rem;
}

/* Animations */
@keyframes cora-spin {
    0% { transform: rotate(0deg); }
    100% { transform: rotate(360deg); }
}

@keyframes cora-shimmer {
    0% { background-position: -200% 0; }
    100% { background-position: 200% 0; }
}

/* Accessibility */
@media (prefers-reduced-motion: reduce) {
    .cora-loading-spinner,
    .cora-skeleton-line {
        animation: none;
    }
}
</style>
`;

// Inject styles
document.head.insertAdjacentHTML('beforeend', loadingStyles); 