/**
 * Job Query Handler - Natural language job status queries
 */

class JobQueryHandler {
    constructor() {
        this.jobQueryPatterns = [
            /how(?:'s|s| is) (?:the )?(.+?)\s*(?:job|project)?(?:\s+doing)?/i,
            /show (?:me )?(?:the )?(.+?)\s*(?:job|project)?/i,
            /what(?:'s|s| is) (?:my |the )?(?:profit|margin|status) (?:on |for )?(?:the )?(.+)/i,
            /(.+?)\s+(?:status|profit|margin|update)/i
        ];
    }

    /**
     * Check if transcript is a job query
     */
    isJobQuery(transcript) {
        const lower = transcript.toLowerCase();
        
        // Check for job-related keywords
        const jobKeywords = ['job', 'project', 'profit', 'margin', 'status', 'how\'s', 'show me', 'what\'s'];
        const hasJobKeyword = jobKeywords.some(keyword => lower.includes(keyword));
        
        // Check if it matches any job query pattern
        const matchesPattern = this.jobQueryPatterns.some(pattern => pattern.test(lower));
        
        return hasJobKeyword || matchesPattern;
    }

    /**
     * Handle job query
     */
    async handleJobQuery(transcript) {
        try {
            const response = await fetch('/api/chat/job-query', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    query: transcript,
                    context: 'voice'
                })
            });

            const result = await response.json();
            
            if (result.job_found) {
                this.showJobResponse(result);
                
                // If there are alerts, show them
                if (result.alerts && result.alerts.length > 0) {
                    this.showAlerts(result.alerts);
                }
            } else {
                this.showError(result.response);
            }
            
            return result;
            
        } catch (error) {
            // console.error('Job query error:', error);
            this.showError('Failed to process job query. Please try again.');
            throw error;
        }
    }

    /**
     * Show job query response
     */
    showJobResponse(result) {
        const notification = document.createElement('div');
        notification.className = 'job-query-notification';
        
        const marginClass = result.job.margin_percent >= 20 ? 'good' : 
                          result.job.margin_percent >= 10 ? 'warning' : 'urgent';
        
        notification.innerHTML = `
            <div class="notification-content">
                <div class="notification-header">
                    <div class="job-name">${result.job.name}</div>
                    <div class="job-status ${result.job.status}">${result.job.status}</div>
                </div>
                
                <div class="job-metrics">
                    <div class="metric">
                        <span class="label">Quoted:</span>
                        <span class="value">$${result.job.quoted.toFixed(0)}</span>
                    </div>
                    <div class="metric">
                        <span class="label">Spent:</span>
                        <span class="value">$${result.job.spent.toFixed(0)}</span>
                    </div>
                    <div class="metric ${marginClass}">
                        <span class="label">Margin:</span>
                        <span class="value">${result.job.margin_percent.toFixed(1)}%</span>
                    </div>
                </div>
                
                <div class="response-text">
                    ${result.response}
                </div>
                
                <div class="notification-footer">
                    <small>Last expense: ${result.job.last_expense}</small>
                    <button class="view-job-btn" onclick="viewJobDetails('${result.job.name}')">
                        View Details →
                    </button>
                </div>
            </div>
        `;
        
        this.addNotificationStyles();
        document.body.appendChild(notification);
        
        // Auto-remove after 8 seconds (longer for job info)
        setTimeout(() => {
            notification.remove();
        }, 8000);
    }

    /**
     * Show alerts
     */
    showAlerts(alerts) {
        alerts.forEach(alert => {
            const alertNotification = document.createElement('div');
            alertNotification.className = `alert-notification ${alert.severity}`;
            alertNotification.innerHTML = `
                <div class="alert-content">
                    <div class="alert-icon">${alert.severity === 'urgent' ? '⚠️' : '⚡'}</div>
                    <div class="alert-message">${alert.message}</div>
                </div>
            `;
            
            document.body.appendChild(alertNotification);
            
            setTimeout(() => {
                alertNotification.remove();
            }, 5000);
        });
    }

    /**
     * Show error message
     */
    showError(message) {
        const notification = document.createElement('div');
        notification.className = 'job-query-error';
        notification.innerHTML = `
            <div class="notification-content">
                <div class="error-icon">❌</div>
                <div class="error-message">${message}</div>
            </div>
        `;
        
        document.body.appendChild(notification);
        
        setTimeout(() => {
            notification.remove();
        }, 4000);
    }

    /**
     * Add notification styles
     */
    addNotificationStyles() {
        const styleId = 'job-query-styles';
        if (document.getElementById(styleId)) return;
        
        const styles = `
            .job-query-notification {
                position: fixed;
                top: 20px;
                right: 20px;
                background: white;
                border-radius: 12px;
                box-shadow: 0 8px 24px rgba(0, 0, 0, 0.15);
                padding: 20px;
                z-index: 1000;
                animation: slideIn 0.3s ease;
                max-width: 400px;
                border: 1px solid #e5e7eb;
            }
            
            .notification-header {
                display: flex;
                justify-content: space-between;
                align-items: center;
                margin-bottom: 12px;
            }
            
            .job-name {
                font-size: 18px;
                font-weight: 600;
                color: #1f2937;
            }
            
            .job-status {
                font-size: 12px;
                padding: 4px 8px;
                border-radius: 12px;
                font-weight: 500;
            }
            
            .job-status.active {
                background: #dbeafe;
                color: #1d4ed8;
            }
            
            .job-status.completed {
                background: #d1fae5;
                color: #065f46;
            }
            
            .job-metrics {
                display: grid;
                grid-template-columns: repeat(3, 1fr);
                gap: 12px;
                margin: 16px 0;
                padding: 12px;
                background: #f9fafb;
                border-radius: 8px;
            }
            
            .metric {
                text-align: center;
            }
            
            .metric .label {
                display: block;
                font-size: 12px;
                color: #6b7280;
                margin-bottom: 4px;
            }
            
            .metric .value {
                display: block;
                font-size: 16px;
                font-weight: 600;
                color: #1f2937;
            }
            
            .metric.good .value {
                color: #059669;
            }
            
            .metric.warning .value {
                color: #d97706;
            }
            
            .metric.urgent .value {
                color: #dc2626;
            }
            
            .response-text {
                font-size: 14px;
                line-height: 1.5;
                color: #374151;
                margin: 16px 0;
                padding: 12px;
                background: #f3f4f6;
                border-radius: 8px;
            }
            
            .notification-footer {
                display: flex;
                justify-content: space-between;
                align-items: center;
                margin-top: 16px;
            }
            
            .notification-footer small {
                color: #6b7280;
                font-size: 12px;
            }
            
            .view-job-btn {
                background: #9B6EC8;
                color: white;
                border: none;
                padding: 6px 12px;
                border-radius: 6px;
                font-size: 12px;
                font-weight: 500;
                cursor: pointer;
                transition: all 0.2s;
            }
            
            .view-job-btn:hover {
                background: #7C3AED;
                transform: translateY(-1px);
            }
            
            .job-query-error {
                position: fixed;
                top: 20px;
                right: 20px;
                background: #fee2e2;
                border: 1px solid #fecaca;
                border-radius: 8px;
                padding: 16px;
                z-index: 1000;
                animation: slideIn 0.3s ease;
                max-width: 300px;
            }
            
            .alert-notification {
                position: fixed;
                bottom: 20px;
                right: 20px;
                background: white;
                border-radius: 8px;
                box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
                padding: 16px;
                z-index: 1001;
                animation: slideUp 0.3s ease;
                max-width: 300px;
                border-left: 4px solid;
            }
            
            .alert-notification.warning {
                border-left-color: #f59e0b;
            }
            
            .alert-notification.urgent {
                border-left-color: #ef4444;
            }
            
            .alert-content {
                display: flex;
                align-items: center;
                gap: 12px;
            }
            
            .alert-icon {
                font-size: 20px;
            }
            
            .alert-message {
                font-size: 14px;
                color: #374151;
                line-height: 1.4;
            }
            
            @keyframes slideUp {
                from {
                    transform: translateY(100%);
                    opacity: 0;
                }
                to {
                    transform: translateY(0);
                    opacity: 1;
                }
            }
        `;
        
        const styleSheet = document.createElement('style');
        styleSheet.id = styleId;
        styleSheet.textContent = styles;
        document.head.appendChild(styleSheet);
    }
}

// Helper function to view job details
function viewJobDetails(jobName) {
    // Switch to jobs tab
    const jobsTab = document.querySelector('[data-tab="jobs"]');
    if (jobsTab) {
        jobsTab.click();
    }
    
    // Could add logic to highlight the specific job
    // console.log('Viewing job:', jobName);
}

// Export for use in voice button
window.JobQueryHandler = JobQueryHandler;