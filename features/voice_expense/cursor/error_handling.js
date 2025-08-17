/**
 * Enhanced Error Handling for Voice Expense Entry
 * Provides construction-specific error messages and recovery options
 */

class VoiceErrorHandler {
    constructor() {
        this.errorTypes = {
            NO_AMOUNT: 'no_amount',
            NO_VENDOR: 'no_vendor',
            NO_JOB: 'no_job',
            NETWORK_ERROR: 'network_error',
            SPEECH_ERROR: 'speech_error',
            UNKNOWN: 'unknown'
        };
        
        this.errorMessages = {
            [this.errorTypes.NO_AMOUNT]: {
                title: 'Amount Not Detected',
                message: 'I couldn\'t hear the amount clearly. Please try again or enter it manually.',
                suggestion: 'Try saying: "Home Depot receipt for $47.50"',
                action: 'retry_or_manual'
            },
            [this.errorTypes.NO_VENDOR]: {
                title: 'Vendor Not Recognized',
                message: 'I didn\'t recognize the vendor name. Please try again or select from common vendors.',
                suggestion: 'Try saying: "receipt from Home Depot" or "purchase at Lowe\'s"',
                action: 'retry_or_select'
            },
            [this.errorTypes.NO_JOB]: {
                title: 'Job Not Specified',
                message: 'No job was mentioned. This expense will be added without a job assignment.',
                suggestion: 'Try saying: "for the Johnson bathroom job" or "on the Smith kitchen"',
                action: 'continue_or_add_job'
            },
            [this.errorTypes.NETWORK_ERROR]: {
                title: 'Connection Error',
                message: 'Unable to connect to the server. Please check your internet connection.',
                suggestion: 'Try again in a moment or use manual entry',
                action: 'retry'
            },
            [this.errorTypes.SPEECH_ERROR]: {
                title: 'Voice Recognition Error',
                message: 'I couldn\'t understand what you said. Please try again in a quieter environment.',
                suggestion: 'Speak clearly and avoid background noise',
                action: 'retry'
            },
            [this.errorTypes.UNKNOWN]: {
                title: 'Something Went Wrong',
                message: 'An unexpected error occurred. Please try again or use manual entry.',
                suggestion: 'If this continues, try refreshing the page',
                action: 'retry_or_manual'
            }
        };
    }
    
    /**
     * Determine error type from API response
     */
    classifyError(error, parsed = null) {
        if (error.includes('amount') || error.includes('Could not detect amount')) {
            return this.errorTypes.NO_AMOUNT;
        }
        
        if (error.includes('vendor') || error.includes('No vendor detected')) {
            return this.errorTypes.NO_VENDOR;
        }
        
        if (error.includes('job') || error.includes('No job detected')) {
            return this.errorTypes.NO_JOB;
        }
        
        if (error.includes('network') || error.includes('fetch') || error.includes('connection')) {
            return this.errorTypes.NETWORK_ERROR;
        }
        
        if (error.includes('speech') || error.includes('recognition')) {
            return this.errorTypes.SPEECH_ERROR;
        }
        
        return this.errorTypes.UNKNOWN;
    }
    
    /**
     * Show error modal with recovery options
     */
    showErrorModal(error, parsed = null, onRetry = null, onManual = null) {
        const errorType = this.classifyError(error, parsed);
        const errorInfo = this.errorMessages[errorType];
        
        // Create error modal
        const modal = document.createElement('div');
        modal.className = 'voice-error-modal-overlay';
        modal.innerHTML = `
            <div class="voice-error-modal">
                <div class="error-modal-header">
                    <div class="error-icon">⚠️</div>
                    <h3>${errorInfo.title}</h3>
                    <button class="error-modal-close" aria-label="Close">×</button>
                </div>
                
                <div class="error-modal-content">
                    <p class="error-message">${errorInfo.message}</p>
                    
                    <div class="error-suggestion">
                        <strong>💡 Tip:</strong> ${errorInfo.suggestion}
                    </div>
                    
                    ${parsed ? this.renderParsedInfo(parsed) : ''}
                    
                    <div class="error-actions">
                        ${this.renderActionButtons(errorType, onRetry, onManual)}
                    </div>
                </div>
            </div>
        `;
        
        // Add modal styles
        this.addErrorModalStyles();
        
        // Add to page
        document.body.appendChild(modal);
        
        // Bind events
        this.bindErrorModalEvents(modal, onRetry, onManual);
        
        return modal;
    }
    
    /**
     * Render parsed information if available
     */
    renderParsedInfo(parsed) {
        let info = '<div class="parsed-info"><h4>What I detected:</h4><ul>';
        
        if (parsed.vendor && parsed.vendor !== 'Unknown') {
            info += `<li><strong>Vendor:</strong> ${parsed.vendor}</li>`;
        }
        
        if (parsed.job_name) {
            info += `<li><strong>Job:</strong> ${parsed.job_name}</li>`;
        }
        
        if (parsed.category) {
            info += `<li><strong>Category:</strong> ${parsed.category}</li>`;
        }
        
        info += '</ul></div>';
        return info;
    }
    
    /**
     * Render action buttons based on error type
     */
    renderActionButtons(errorType, onRetry, onManual) {
        const actions = {
            [this.errorTypes.NO_AMOUNT]: `
                <button class="error-action-btn primary" onclick="this.closest('.voice-error-modal-overlay').retry()">
                    🎤 Try Again
                </button>
                <button class="error-action-btn secondary" onclick="this.closest('.voice-error-modal-overlay').manual()">
                    ✏️ Enter Manually
                </button>
            `,
            [this.errorTypes.NO_VENDOR]: `
                <button class="error-action-btn primary" onclick="this.closest('.voice-error-modal-overlay').retry()">
                    🎤 Try Again
                </button>
                <button class="error-action-btn secondary" onclick="this.closest('.voice-error-modal-overlay').selectVendor()">
                    📋 Select Vendor
                </button>
            `,
            [this.errorTypes.NO_JOB]: `
                <button class="error-action-btn primary" onclick="this.closest('.voice-error-modal-overlay').continue()">
                    ✅ Continue Without Job
                </button>
                <button class="error-action-btn secondary" onclick="this.closest('.voice-error-modal-overlay').addJob()">
                    🏗️ Add Job
                </button>
            `,
            [this.errorTypes.NETWORK_ERROR]: `
                <button class="error-action-btn primary" onclick="this.closest('.voice-error-modal-overlay').retry()">
                    🔄 Try Again
                </button>
                <button class="error-action-btn secondary" onclick="this.closest('.voice-error-modal-overlay').manual()">
                    ✏️ Manual Entry
                </button>
            `,
            [this.errorTypes.SPEECH_ERROR]: `
                <button class="error-action-btn primary" onclick="this.closest('.voice-error-modal-overlay').retry()">
                    🎤 Try Again
                </button>
                <button class="error-action-btn secondary" onclick="this.closest('.voice-error-modal-overlay').manual()">
                    ✏️ Manual Entry
                </button>
            `,
            [this.errorTypes.UNKNOWN]: `
                <button class="error-action-btn primary" onclick="this.closest('.voice-error-modal-overlay').retry()">
                    🔄 Try Again
                </button>
                <button class="error-action-btn secondary" onclick="this.closest('.voice-error-modal-overlay').manual()">
                    ✏️ Manual Entry
                </button>
            `
        };
        
        return actions[errorType] || actions[this.errorTypes.UNKNOWN];
    }
    
    /**
     * Bind events to error modal
     */
    bindErrorModalEvents(modal, onRetry, onManual) {
        // Close button
        modal.querySelector('.error-modal-close').addEventListener('click', () => {
            modal.remove();
        });
        
        // Close on overlay click
        modal.addEventListener('click', (e) => {
            if (e.target === modal) {
                modal.remove();
            }
        });
        
        // Action buttons
        modal.retry = () => {
            modal.remove();
            if (onRetry) onRetry();
        };
        
        modal.manual = () => {
            modal.remove();
            if (onManual) onManual();
        };
        
        modal.continue = () => {
            modal.remove();
            // Continue with expense without job
        };
        
        modal.addJob = () => {
            modal.remove();
            // Open job selection/creation
            this.showJobSelection();
        };
        
        modal.selectVendor = () => {
            modal.remove();
            // Open vendor selection
            this.showVendorSelection();
        };
    }
    
    /**
     * Show vendor selection modal
     */
    showVendorSelection() {
        const commonVendors = [
            'Home Depot',
            'Lowe\'s',
            'Menards',
            'Ace Hardware',
            'Lumber Yard',
            'Electrical Supply',
            'Plumbing Supply',
            'Gas Station',
            'Equipment Rental'
        ];
        
        const modal = document.createElement('div');
        modal.className = 'vendor-selection-modal';
        modal.innerHTML = `
            <div class="vendor-selection-content">
                <h3>Select Vendor</h3>
                <div class="vendor-grid">
                    ${commonVendors.map(vendor => `
                        <button class="vendor-option" data-vendor="${vendor}">
                            ${vendor}
                        </button>
                    `).join('')}
                </div>
                <button class="vendor-custom">+ Add Custom Vendor</button>
            </div>
        `;
        
        this.addVendorSelectionStyles();
        document.body.appendChild(modal);
        
        // Handle vendor selection
        modal.querySelectorAll('.vendor-option').forEach(btn => {
            btn.addEventListener('click', () => {
                const vendor = btn.dataset.vendor;
                modal.remove();
                // Continue with selected vendor
            });
        });
    }
    
    /**
     * Show job selection modal
     */
    showJobSelection() {
        // This would load existing jobs and allow selection
        const modal = document.createElement('div');
        modal.className = 'job-selection-modal';
        modal.innerHTML = `
            <div class="job-selection-content">
                <h3>Select Job</h3>
                <div class="job-list">
                    <div class="loading">Loading jobs...</div>
                </div>
                <button class="job-custom">+ Create New Job</button>
            </div>
        `;
        
        this.addJobSelectionStyles();
        document.body.appendChild(modal);
        
        // Load jobs and populate list
        this.loadJobsForSelection(modal);
    }
    
    /**
     * Load jobs for selection
     */
    async loadJobsForSelection(modal) {
        try {
            const response = await fetch('/api/jobs');
            if (response.ok) {
                const jobs = await response.json();
                const jobList = modal.querySelector('.job-list');
                
                if (jobs.length === 0) {
                    jobList.innerHTML = '<p>No jobs found. Create your first job!</p>';
                    return;
                }
                
                jobList.innerHTML = jobs.map(job => `
                    <button class="job-option" data-job-id="${job.id}" data-job-name="${job.job_name}">
                        <div class="job-name">${job.job_name}</div>
                        <div class="job-customer">${job.customer_name || 'No customer'}</div>
                    </button>
                `).join('');
                
                // Handle job selection
                modal.querySelectorAll('.job-option').forEach(btn => {
                    btn.addEventListener('click', () => {
                        const jobId = btn.dataset.jobId;
                        const jobName = btn.dataset.jobName;
                        modal.remove();
                        // Continue with selected job
                    });
                });
            }
        } catch (error) {
            console.error('Error loading jobs:', error);
            modal.querySelector('.job-list').innerHTML = '<p>Error loading jobs. Please try again.</p>';
        }
    }
    
    /**
     * Add error modal styles
     */
    addErrorModalStyles() {
        const styleId = 'voice-error-modal-styles';
        if (document.getElementById(styleId)) return;
        
        const styles = `
            .voice-error-modal-overlay {
                position: fixed;
                top: 0;
                left: 0;
                right: 0;
                bottom: 0;
                background: rgba(0, 0, 0, 0.5);
                display: flex;
                align-items: center;
                justify-content: center;
                z-index: 1000;
                animation: fadeIn 0.3s ease;
            }
            
            .voice-error-modal {
                background: white;
                border-radius: 12px;
                box-shadow: 0 20px 40px rgba(0, 0, 0, 0.15);
                width: 90%;
                max-width: 500px;
                max-height: 90vh;
                overflow-y: auto;
                animation: slideUp 0.3s ease;
            }
            
            .error-modal-header {
                display: flex;
                align-items: center;
                gap: 12px;
                padding: 20px 24px;
                border-bottom: 1px solid #e5e7eb;
            }
            
            .error-icon {
                font-size: 24px;
            }
            
            .error-modal-header h3 {
                margin: 0;
                flex: 1;
                font-size: 18px;
                font-weight: 600;
                color: #1f2937;
            }
            
            .error-modal-close {
                background: none;
                border: none;
                font-size: 24px;
                color: #6b7280;
                cursor: pointer;
                padding: 0;
                width: 32px;
                height: 32px;
                border-radius: 6px;
                display: flex;
                align-items: center;
                justify-content: center;
                transition: all 0.2s ease;
            }
            
            .error-modal-close:hover {
                background: #f3f4f6;
                color: #374151;
            }
            
            .error-modal-content {
                padding: 24px;
            }
            
            .error-message {
                font-size: 16px;
                line-height: 1.5;
                color: #374151;
                margin-bottom: 16px;
            }
            
            .error-suggestion {
                background: #f0f9ff;
                border: 1px solid #bae6fd;
                border-radius: 8px;
                padding: 12px;
                margin-bottom: 20px;
                font-size: 14px;
                line-height: 1.4;
            }
            
            .parsed-info {
                background: #f9fafb;
                border: 1px solid #e5e7eb;
                border-radius: 8px;
                padding: 16px;
                margin-bottom: 20px;
            }
            
            .parsed-info h4 {
                margin: 0 0 8px 0;
                font-size: 14px;
                font-weight: 600;
                color: #374151;
            }
            
            .parsed-info ul {
                margin: 0;
                padding-left: 20px;
                font-size: 14px;
                color: #6b7280;
            }
            
            .error-actions {
                display: flex;
                gap: 12px;
                justify-content: flex-end;
            }
            
            .error-action-btn {
                padding: 10px 20px;
                border-radius: 6px;
                font-size: 14px;
                font-weight: 500;
                cursor: pointer;
                transition: all 0.2s ease;
                border: 1px solid #d1d5db;
            }
            
            .error-action-btn.primary {
                background: #9B6EC8;
                color: white;
                border-color: #9B6EC8;
            }
            
            .error-action-btn.primary:hover {
                background: #7C3AED;
                border-color: #7C3AED;
            }
            
            .error-action-btn.secondary {
                background: white;
                color: #374151;
            }
            
            .error-action-btn.secondary:hover {
                background: #f9fafb;
                border-color: #9B6EC8;
            }
            
            @keyframes fadeIn {
                from { opacity: 0; }
                to { opacity: 1; }
            }
            
            @keyframes slideUp {
                from { transform: translateY(20px); opacity: 0; }
                to { transform: translateY(0); opacity: 1; }
            }
        `;
        
        const styleSheet = document.createElement('style');
        styleSheet.id = styleId;
        styleSheet.textContent = styles;
        document.head.appendChild(styleSheet);
    }
    
    /**
     * Add vendor selection styles
     */
    addVendorSelectionStyles() {
        const styleId = 'vendor-selection-styles';
        if (document.getElementById(styleId)) return;
        
        const styles = `
            .vendor-selection-modal {
                position: fixed;
                top: 0;
                left: 0;
                right: 0;
                bottom: 0;
                background: rgba(0, 0, 0, 0.5);
                display: flex;
                align-items: center;
                justify-content: center;
                z-index: 1000;
            }
            
            .vendor-selection-content {
                background: white;
                border-radius: 12px;
                padding: 24px;
                width: 90%;
                max-width: 400px;
                max-height: 80vh;
                overflow-y: auto;
            }
            
            .vendor-selection-content h3 {
                margin: 0 0 16px 0;
                font-size: 18px;
                font-weight: 600;
                color: #1f2937;
            }
            
            .vendor-grid {
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
                gap: 8px;
                margin-bottom: 16px;
            }
            
            .vendor-option {
                padding: 12px;
                border: 1px solid #e5e7eb;
                border-radius: 6px;
                background: white;
                cursor: pointer;
                transition: all 0.2s ease;
                font-size: 14px;
                text-align: left;
            }
            
            .vendor-option:hover {
                background: #f9fafb;
                border-color: #9B6EC8;
            }
            
            .vendor-custom {
                width: 100%;
                padding: 12px;
                border: 1px solid #d1d5db;
                border-radius: 6px;
                background: white;
                cursor: pointer;
                transition: all 0.2s ease;
                font-size: 14px;
                color: #6b7280;
            }
            
            .vendor-custom:hover {
                background: #f9fafb;
                border-color: #9B6EC8;
            }
        `;
        
        const styleSheet = document.createElement('style');
        styleSheet.id = styleId;
        styleSheet.textContent = styles;
        document.head.appendChild(styleSheet);
    }
    
    /**
     * Add job selection styles
     */
    addJobSelectionStyles() {
        const styleId = 'job-selection-styles';
        if (document.getElementById(styleId)) return;
        
        const styles = `
            .job-selection-modal {
                position: fixed;
                top: 0;
                left: 0;
                right: 0;
                bottom: 0;
                background: rgba(0, 0, 0, 0.5);
                display: flex;
                align-items: center;
                justify-content: center;
                z-index: 1000;
            }
            
            .job-selection-content {
                background: white;
                border-radius: 12px;
                padding: 24px;
                width: 90%;
                max-width: 400px;
                max-height: 80vh;
                overflow-y: auto;
            }
            
            .job-selection-content h3 {
                margin: 0 0 16px 0;
                font-size: 18px;
                font-weight: 600;
                color: #1f2937;
            }
            
            .job-list {
                margin-bottom: 16px;
            }
            
            .job-option {
                width: 100%;
                padding: 12px;
                border: 1px solid #e5e7eb;
                border-radius: 6px;
                background: white;
                cursor: pointer;
                transition: all 0.2s ease;
                text-align: left;
                margin-bottom: 8px;
            }
            
            .job-option:hover {
                background: #f9fafb;
                border-color: #9B6EC8;
            }
            
            .job-name {
                font-size: 14px;
                font-weight: 500;
                color: #1f2937;
            }
            
            .job-customer {
                font-size: 12px;
                color: #6b7280;
                margin-top: 2px;
            }
            
            .job-custom {
                width: 100%;
                padding: 12px;
                border: 1px solid #d1d5db;
                border-radius: 6px;
                background: white;
                cursor: pointer;
                transition: all 0.2s ease;
                font-size: 14px;
                color: #6b7280;
            }
            
            .job-custom:hover {
                background: #f9fafb;
                border-color: #9B6EC8;
            }
        `;
        
        const styleSheet = document.createElement('style');
        styleSheet.id = styleId;
        styleSheet.textContent = styles;
        document.head.appendChild(styleSheet);
    }
}

// Export for use
if (typeof module !== 'undefined' && module.exports) {
    module.exports = VoiceErrorHandler;
} 