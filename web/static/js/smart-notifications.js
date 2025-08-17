/**
 * CORA Smart Notifications System
 * 
 * Features:
 * - Context-aware notifications
 * - Intelligent timing and frequency
 * - User preference management
 * - Integration with CORA chat
 * - Performance and engagement tracking
 * - Accessibility support
 */

class SmartNotifications {
    constructor() {
        this.notifications = [];
        this.userPreferences = this.loadPreferences();
        this.notificationQueue = [];
        this.isProcessing = false;
        this.lastNotificationTime = 0;
        this.dailyNotificationCount = 0;
        this.engagementMetrics = {
            totalShown: 0,
            totalClicked: 0,
            totalDismissed: 0,
            averageResponseTime: 0
        };
        
        this.init();
    }

    init() {
        this.setupEventListeners();
        this.startNotificationScheduler();
        this.loadEngagementMetrics();
        
        // Reset daily count at midnight
        this.scheduleDailyReset();
        
        // console.log('🔔 Smart Notifications initialized');
    }

    setupEventListeners() {
        // Listen for system events
        document.addEventListener('expense-created', (e) => {
            this.handleExpenseCreated(e.detail);
        });

        document.addEventListener('profit-alert', (e) => {
            this.handleProfitAlert(e.detail);
        });

        document.addEventListener('system-error', (e) => {
            this.handleSystemError(e.detail);
        });

        document.addEventListener('user-inactive', (e) => {
            this.handleUserInactive(e.detail);
        });

        document.addEventListener('goal-achieved', (e) => {
            this.handleGoalAchieved(e.detail);
        });

        // Listen for page visibility changes
        document.addEventListener('visibilitychange', () => {
            if (document.hidden) {
                this.handlePageHidden();
            } else {
                this.handlePageVisible();
            }
        });

        // Listen for user interactions
        document.addEventListener('click', () => {
            this.recordUserActivity();
        });

        document.addEventListener('keydown', () => {
            this.recordUserActivity();
        });
    }

    handleExpenseCreated(expenseData) {
        const notification = {
            id: this.generateId(),
            type: 'success',
            category: 'expense',
            title: 'Expense Recorded',
            message: `Successfully recorded $${expenseData.amount} for ${expenseData.description}`,
            icon: '💰',
            priority: 'medium',
            actions: [
                {
                    label: 'View Details',
                    action: 'view-expense',
                    data: expenseData.id
                },
                {
                    label: 'Add Receipt',
                    action: 'add-receipt',
                    data: expenseData.id
                }
            ],
            metadata: {
                expenseId: expenseData.id,
                amount: expenseData.amount,
                category: expenseData.category
            }
        };

        this.queueNotification(notification);
    }

    handleProfitAlert(alertData) {
        const notification = {
            id: this.generateId(),
            type: 'warning',
            category: 'profit',
            title: 'Profit Alert',
            message: alertData.message,
            icon: '📈',
            priority: 'high',
            actions: [
                {
                    label: 'View Analysis',
                    action: 'view-profit-analysis',
                    data: alertData.jobId
                },
                {
                    label: 'Optimize',
                    action: 'optimize-profit',
                    data: alertData.jobId
                }
            ],
            metadata: {
                jobId: alertData.jobId,
                profitMargin: alertData.profitMargin,
                threshold: alertData.threshold
            }
        };

        this.queueNotification(notification);
    }

    handleSystemError(errorData) {
        const notification = {
            id: this.generateId(),
            type: 'error',
            category: 'system',
            title: 'System Issue Detected',
            message: 'We detected an issue. CORA is here to help!',
            icon: '🔧',
            priority: 'critical',
            actions: [
                {
                    label: 'Get Help',
                    action: 'get-help',
                    data: errorData.errorCode
                },
                {
                    label: 'Report Issue',
                    action: 'report-issue',
                    data: errorData
                }
            ],
            metadata: {
                errorCode: errorData.errorCode,
                severity: errorData.severity,
                timestamp: new Date()
            }
        };

        this.queueNotification(notification);
    }

    handleUserInactive(inactivityData) {
        // Only show if user has been inactive for more than 5 minutes
        if (inactivityData.duration > 300000) {
            const notification = {
                id: this.generateId(),
                type: 'info',
                category: 'engagement',
                title: 'Need Help?',
                message: 'I\'m here if you need assistance with anything!',
                icon: '🤖',
                priority: 'low',
                actions: [
                    {
                        label: 'Ask CORA',
                        action: 'open-chat',
                        data: null
                    },
                    {
                        label: 'View Tips',
                        action: 'view-tips',
                        data: null
                    }
                ],
                metadata: {
                    inactivityDuration: inactivityData.duration,
                    lastActivity: inactivityData.lastActivity
                }
            };

            this.queueNotification(notification);
        }
    }

    handleGoalAchieved(goalData) {
        const notification = {
            id: this.generateId(),
            type: 'success',
            category: 'achievement',
            title: 'Goal Achieved! 🎉',
            message: `Congratulations! You've achieved: ${goalData.goalName}`,
            icon: '🏆',
            priority: 'high',
            actions: [
                {
                    label: 'View Details',
                    action: 'view-goal',
                    data: goalData.goalId
                },
                {
                    label: 'Set New Goal',
                    action: 'set-new-goal',
                    data: null
                }
            ],
            metadata: {
                goalId: goalData.goalId,
                goalName: goalData.goalName,
                achievementDate: new Date()
            }
        };

        this.queueNotification(notification);
    }

    handlePageHidden() {
        // Store current state for when page becomes visible again
        this.pageHiddenTime = Date.now();
    }

    handlePageVisible() {
        if (this.pageHiddenTime) {
            const hiddenDuration = Date.now() - this.pageHiddenTime;
            
            // If user was away for more than 10 minutes, show welcome back notification
            if (hiddenDuration > 600000) {
                const notification = {
                    id: this.generateId(),
                    type: 'info',
                    category: 'welcome',
                    title: 'Welcome Back!',
                    message: 'Great to see you again. How can I help you today?',
                    icon: '👋',
                    priority: 'low',
                    actions: [
                        {
                            label: 'Chat with CORA',
                            action: 'open-chat',
                            data: null
                        },
                        {
                            label: 'View Updates',
                            action: 'view-updates',
                            data: null
                        }
                    ],
                    metadata: {
                        awayDuration: hiddenDuration,
                        returnTime: new Date()
                    }
                };

                this.queueNotification(notification);
            }
            
            this.pageHiddenTime = null;
        }
    }

    queueNotification(notification) {
        // Check user preferences
        if (!this.shouldShowNotification(notification)) {
            return;
        }

        // Add to queue
        this.notificationQueue.push(notification);
        
        // Process queue if not already processing
        if (!this.isProcessing) {
            this.processQueue();
        }
    }

    shouldShowNotification(notification) {
        const prefs = this.userPreferences;
        
        // Check if notifications are enabled
        if (!prefs.enabled) {
            return false;
        }
        
        // Check category preferences
        if (prefs.disabledCategories.includes(notification.category)) {
            return false;
        }
        
        // Check priority preferences
        if (notification.priority === 'low' && !prefs.showLowPriority) {
            return false;
        }
        
        // Check daily limit
        if (this.dailyNotificationCount >= prefs.dailyLimit) {
            return false;
        }
        
        // Check frequency limits
        const timeSinceLastNotification = Date.now() - this.lastNotificationTime;
        if (timeSinceLastNotification < prefs.minInterval) {
            return false;
        }
        
        return true;
    }

    async processQueue() {
        if (this.isProcessing || this.notificationQueue.length === 0) {
            return;
        }

        this.isProcessing = true;

        while (this.notificationQueue.length > 0) {
            const notification = this.notificationQueue.shift();
            
            // Check if we should still show this notification
            if (this.shouldShowNotification(notification)) {
                await this.showNotification(notification);
                
                // Add delay between notifications
                await this.delay(2000);
            }
        }

        this.isProcessing = false;
    }

    async showNotification(notification) {
        // Update metrics
        this.engagementMetrics.totalShown++;
        this.dailyNotificationCount++;
        this.lastNotificationTime = Date.now();

        // Create notification element
        const notificationElement = this.createNotificationElement(notification);
        
        // Add to DOM
        document.body.appendChild(notificationElement);
        
        // Animate in
        requestAnimationFrame(() => {
            notificationElement.classList.add('show');
        });

        // Auto-dismiss after delay
        const dismissDelay = this.getDismissDelay(notification);
        if (dismissDelay > 0) {
            setTimeout(() => {
                this.dismissNotification(notification.id);
            }, dismissDelay);
        }

        // Track engagement
        this.trackEngagement(notification);

        // Send to CORA chat if available
        if (window.coraChatEnhanced) {
            window.coraChatEnhanced.addSmartNotification(notification);
        }

        // Store notification
        this.notifications.push(notification);
        
        // Announce to screen readers
        this.announceToScreenReader(notification.message);
    }

    createNotificationElement(notification) {
        const element = document.createElement('div');
        element.className = `smart-notification ${notification.type} ${notification.category}`;
        element.id = `notification-${notification.id}`;
        element.setAttribute('role', 'alert');
        element.setAttribute('aria-live', 'polite');

        element.innerHTML = `
            <div class="notification-content">
                <div class="notification-header">
                    <div class="notification-icon">${notification.icon}</div>
                    <div class="notification-text">
                        <div class="notification-title">${notification.title}</div>
                        <div class="notification-message">${notification.message}</div>
                    </div>
                    <button class="notification-close" aria-label="Close notification">
                        <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                            <line x1="18" y1="6" x2="6" y2="18"></line>
                            <line x1="6" y1="6" x2="18" y2="18"></line>
                        </svg>
                    </button>
                </div>
                ${this.renderActions(notification.actions)}
                <div class="notification-progress"></div>
            </div>
        `;

        // Add event listeners
        element.querySelector('.notification-close').addEventListener('click', () => {
            this.dismissNotification(notification.id);
        });

        // Add action listeners
        element.querySelectorAll('.notification-action').forEach(btn => {
            btn.addEventListener('click', (e) => {
                const action = e.target.dataset.action;
                const data = e.target.dataset.data;
                this.handleNotificationAction(notification, action, data);
            });
        });

        return element;
    }

    renderActions(actions) {
        if (!actions || actions.length === 0) {
            return '';
        }

        const actionsHtml = actions.map(action => `
            <button class="notification-action" 
                    data-action="${action.action}" 
                    data-data="${action.data || ''}">
                ${action.label}
            </button>
        `).join('');

        return `<div class="notification-actions">${actionsHtml}</div>`;
    }

    dismissNotification(notificationId) {
        const element = document.getElementById(`notification-${notificationId}`);
        if (element) {
            element.classList.add('dismissing');
            
            setTimeout(() => {
                if (element.parentNode) {
                    element.parentNode.removeChild(element);
                }
            }, 300);

            // Update metrics
            this.engagementMetrics.totalDismissed++;
        }
    }

    handleNotificationAction(notification, action, data) {
        // Update metrics
        this.engagementMetrics.totalClicked++;
        
        // Record response time
        const responseTime = Date.now() - notification.timestamp;
        this.updateAverageResponseTime(responseTime);

        // Handle different actions
        switch (action) {
            case 'open-chat':
                if (window.coraChatEnhanced) {
                    window.coraChatEnhanced.openChat();
                }
                break;
                
            case 'view-expense':
                window.location.href = `/expenses/${data}`;
                break;
                
            case 'view-profit-analysis':
                window.location.href = `/profit-analysis/${data}`;
                break;
                
            case 'get-help':
                this.showHelpModal(data);
                break;
                
            case 'view-goal':
                window.location.href = `/goals/${data}`;
                break;
                
            case 'set-new-goal':
                window.location.href = '/goals/new';
                break;
                
            default:
                // console.log('Unknown notification action:', action, data);
        }

        // Dismiss notification after action
        this.dismissNotification(notification.id);
    }

    showHelpModal(errorCode) {
        // Create help modal
        const modal = document.createElement('div');
        modal.className = 'help-modal';
        modal.innerHTML = `
            <div class="help-content">
                <h3>Need Help?</h3>
                <p>I'm here to help you resolve this issue. Let me connect you with the right resources.</p>
                <div class="help-actions">
                    <button class="help-action" onclick="window.coraChatEnhanced.openChat()">
                        Chat with CORA
                    </button>
                    <button class="help-action" onclick="window.location.href='/support'">
                        Contact Support
                    </button>
                </div>
                <button class="help-close">×</button>
            </div>
        `;

        document.body.appendChild(modal);

        // Close handlers
        modal.querySelector('.help-close').addEventListener('click', () => {
            modal.remove();
        });

        modal.addEventListener('click', (e) => {
            if (e.target === modal) {
                modal.remove();
            }
        });
    }

    getDismissDelay(notification) {
        const baseDelays = {
            critical: 0, // No auto-dismiss
            high: 10000, // 10 seconds
            medium: 8000, // 8 seconds
            low: 5000 // 5 seconds
        };

        return baseDelays[notification.priority] || 5000;
    }

    trackEngagement(notification) {
        // Store engagement data
        const engagement = {
            notificationId: notification.id,
            type: notification.type,
            category: notification.category,
            priority: notification.priority,
            timestamp: new Date(),
            shown: true,
            clicked: false,
            dismissed: false
        };

        // Store in localStorage for analytics
        this.storeEngagementData(engagement);
    }

    updateAverageResponseTime(newResponseTime) {
        const currentAvg = this.engagementMetrics.averageResponseTime;
        const totalClicked = this.engagementMetrics.totalClicked;
        
        this.engagementMetrics.averageResponseTime = 
            (currentAvg * (totalClicked - 1) + newResponseTime) / totalClicked;
    }

    recordUserActivity() {
        this.lastUserActivity = Date.now();
    }

    startNotificationScheduler() {
        // Check for scheduled notifications every minute
        setInterval(() => {
            this.checkScheduledNotifications();
        }, 60000);
    }

    checkScheduledNotifications() {
        // Check for time-based notifications
        const now = new Date();
        const hour = now.getHours();
        
        // Morning motivation (9 AM)
        if (hour === 9 && this.shouldShowDailyNotification('morning')) {
            this.showMorningMotivation();
        }
        
        // Afternoon check-in (2 PM)
        if (hour === 14 && this.shouldShowDailyNotification('afternoon')) {
            this.showAfternoonCheckin();
        }
        
        // End of day summary (6 PM)
        if (hour === 18 && this.shouldShowDailyNotification('evening')) {
            this.showEndOfDaySummary();
        }
    }

    shouldShowDailyNotification(type) {
        const today = new Date().toDateString();
        const lastShown = this.userPreferences.lastDailyNotifications?.[type];
        
        return lastShown !== today;
    }

    showMorningMotivation() {
        const notification = {
            id: this.generateId(),
            type: 'info',
            category: 'motivation',
            title: 'Good Morning! ☀️',
            message: 'Ready to make today productive? Let\'s track those expenses and boost your profits!',
            icon: '🌅',
            priority: 'low',
            actions: [
                {
                    label: 'Start Tracking',
                    action: 'open-expense-tracker',
                    data: null
                },
                {
                    label: 'View Goals',
                    action: 'view-goals',
                    data: null
                }
            ]
        };

        this.queueNotification(notification);
        this.updateDailyNotificationShown('morning');
    }

    showAfternoonCheckin() {
        const notification = {
            id: this.generateId(),
            type: 'info',
            category: 'checkin',
            title: 'Afternoon Check-in',
            message: 'How\'s your day going? Don\'t forget to log any expenses you\'ve had!',
            icon: '☕',
            priority: 'low',
            actions: [
                {
                    label: 'Log Expenses',
                    action: 'open-expense-tracker',
                    data: null
                },
                {
                    label: 'View Progress',
                    action: 'view-progress',
                    data: null
                }
            ]
        };

        this.queueNotification(notification);
        this.updateDailyNotificationShown('afternoon');
    }

    showEndOfDaySummary() {
        const notification = {
            id: this.generateId(),
            type: 'info',
            category: 'summary',
            title: 'End of Day Summary',
            message: 'Great work today! Let\'s review your progress and plan for tomorrow.',
            icon: '📊',
            priority: 'medium',
            actions: [
                {
                    label: 'View Summary',
                    action: 'view-daily-summary',
                    data: null
                },
                {
                    label: 'Plan Tomorrow',
                    action: 'plan-tomorrow',
                    data: null
                }
            ]
        };

        this.queueNotification(notification);
        this.updateDailyNotificationShown('evening');
    }

    updateDailyNotificationShown(type) {
        if (!this.userPreferences.lastDailyNotifications) {
            this.userPreferences.lastDailyNotifications = {};
        }
        
        this.userPreferences.lastDailyNotifications[type] = new Date().toDateString();
        this.savePreferences();
    }

    scheduleDailyReset() {
        const now = new Date();
        const tomorrow = new Date(now);
        tomorrow.setDate(tomorrow.getDate() + 1);
        tomorrow.setHours(0, 0, 0, 0);
        
        const timeUntilMidnight = tomorrow.getTime() - now.getTime();
        
        setTimeout(() => {
            this.dailyNotificationCount = 0;
            this.scheduleDailyReset(); // Schedule next reset
        }, timeUntilMidnight);
    }

    loadPreferences() {
        try {
            const saved = localStorage.getItem('cora-notification-preferences');
            return saved ? JSON.parse(saved) : this.getDefaultPreferences();
        } catch (error) {
            // console.warn('Could not load notification preferences:', error);
            return this.getDefaultPreferences();
        }
    }

    getDefaultPreferences() {
        return {
            enabled: true,
            showLowPriority: true,
            dailyLimit: 10,
            minInterval: 5000, // 5 seconds
            disabledCategories: [],
            soundEnabled: true,
            vibrationEnabled: true
        };
    }

    savePreferences() {
        try {
            localStorage.setItem('cora-notification-preferences', JSON.stringify(this.userPreferences));
        } catch (error) {
            // console.warn('Could not save notification preferences:', error);
        }
    }

    loadEngagementMetrics() {
        try {
            const saved = localStorage.getItem('cora-notification-metrics');
            if (saved) {
                this.engagementMetrics = { ...this.engagementMetrics, ...JSON.parse(saved) };
            }
        } catch (error) {
            // console.warn('Could not load engagement metrics:', error);
        }
    }

    storeEngagementData(engagement) {
        try {
            const existing = JSON.parse(localStorage.getItem('cora-notification-engagement') || '[]');
            existing.push(engagement);
            
            // Keep only last 1000 engagements
            if (existing.length > 1000) {
                existing.splice(0, existing.length - 1000);
            }
            
            localStorage.setItem('cora-notification-engagement', JSON.stringify(existing));
        } catch (error) {
            // console.warn('Could not store engagement data:', error);
        }
    }

    generateId() {
        return 'notif_' + Date.now() + '_' + Math.random().toString(36).substr(2, 9);
    }

    delay(ms) {
        return new Promise(resolve => setTimeout(resolve, ms));
    }

    announceToScreenReader(message) {
        const announcement = document.createElement('div');
        announcement.setAttribute('aria-live', 'polite');
        announcement.setAttribute('aria-atomic', 'true');
        announcement.className = 'sr-only';
        announcement.textContent = message;
        
        document.body.appendChild(announcement);
        
        setTimeout(() => {
            announcement.remove();
        }, 1000);
    }

    // Public API methods
    updatePreferences(newPreferences) {
        this.userPreferences = { ...this.userPreferences, ...newPreferences };
        this.savePreferences();
    }

    getEngagementMetrics() {
        return { ...this.engagementMetrics };
    }

    clearAllNotifications() {
        // Remove all notification elements
        document.querySelectorAll('.smart-notification').forEach(el => {
            el.remove();
        });
        
        // Clear queues
        this.notificationQueue = [];
        this.notifications = [];
    }

    getNotificationStats() {
        return {
            totalNotifications: this.notifications.length,
            queueLength: this.notificationQueue.length,
            dailyCount: this.dailyNotificationCount,
            engagement: this.engagementMetrics,
            preferences: this.userPreferences
        };
    }
}

// Initialize smart notifications when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
    window.smartNotifications = new SmartNotifications();
});

// Export for use in other modules
if (typeof module !== 'undefined' && module.exports) {
    module.exports = SmartNotifications;
} 