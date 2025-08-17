/**
 * CORA Real-time Updates
 * Handles real-time dashboard updates via WebSocket
 */

class RealtimeUpdates {
    constructor() {
        this.ws = null;
        this.reconnectAttempts = 0;
        this.maxReconnectAttempts = 5;
        this.reconnectDelay = 1000;
        this.isConnected = false;
        
        this.init();
    }
    
    init() {
        this.setupWebSocket();
        this.subscribeToEvents();
        this.setupReconnection();
    }
    
    setupWebSocket() {
        try {
            // Use secure WebSocket if on HTTPS, otherwise regular WebSocket
            const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
            const wsUrl = `${protocol}//${window.location.host}/ws`;
            
            this.ws = new WebSocket(wsUrl);
            
            this.ws.onopen = () => {
                // console.log('WebSocket connected');
                this.isConnected = true;
                this.reconnectAttempts = 0;
                this.showConnectionStatus('connected');
            };
            
            this.ws.onmessage = (event) => {
                this.handleMessage(JSON.parse(event.data));
            };
            
            this.ws.onclose = () => {
                // console.log('WebSocket disconnected');
                this.isConnected = false;
                this.showConnectionStatus('disconnected');
                this.attemptReconnection();
            };
            
            this.ws.onerror = (error) => {
                // console.error('WebSocket error:', error);
                this.showConnectionStatus('error');
            };
            
        } catch (error) {
            // console.error('Failed to setup WebSocket:', error);
            this.fallbackToPolling();
        }
    }
    
    setupReconnection() {
        // Listen for online/offline events
        window.addEventListener('online', () => {
            if (!this.isConnected) {
                this.setupWebSocket();
            }
        });
        
        window.addEventListener('offline', () => {
            this.showConnectionStatus('offline');
        });
    }
    
    attemptReconnection() {
        if (this.reconnectAttempts >= this.maxReconnectAttempts) {
            // console.log('Max reconnection attempts reached, falling back to polling');
            this.fallbackToPolling();
            return;
        }
        
        this.reconnectAttempts++;
        const delay = this.reconnectDelay * Math.pow(2, this.reconnectAttempts - 1);
        
        setTimeout(() => {
            // console.log(`Attempting reconnection ${this.reconnectAttempts}/${this.maxReconnectAttempts}`);
            this.setupWebSocket();
        }, delay);
    }
    
    fallbackToPolling() {
        // console.log('Falling back to polling for updates');
        this.setupPolling();
    }
    
    setupPolling() {
        // Poll for updates every 30 seconds
        setInterval(() => {
            this.pollForUpdates();
        }, 30000);
    }
    
    async pollForUpdates() {
        try {
            const response = await fetch('/api/updates/latest');
            if (response.ok) {
                const updates = await response.json();
                this.handleUpdates(updates);
            }
        } catch (error) {
            // console.error('Polling error:', error);
        }
    }
    
    subscribeToEvents() {
        // Subscribe to specific event types
        const subscriptions = [
            'expense.created',
            'expense.updated',
            'job.status_changed',
            'alert.created',
            'system.health_changed'
        ];
        
        if (this.ws && this.isConnected) {
            this.ws.send(JSON.stringify({
                type: 'subscribe',
                events: subscriptions
            }));
        }
    }
    
    handleMessage(data) {
        switch (data.type) {
            case 'expense.created':
                this.handleExpenseCreated(data.payload);
                break;
            case 'expense.updated':
                this.handleExpenseUpdated(data.payload);
                break;
            case 'job.status_changed':
                this.handleJobStatusChanged(data.payload);
                break;
            case 'alert.created':
                this.handleAlertCreated(data.payload);
                break;
            case 'system.health_changed':
                this.handleHealthChanged(data.payload);
                break;
            default:
                // console.log('Unknown message type:', data.type);
        }
    }
    
    handleUpdates(updates) {
        updates.forEach(update => {
            this.handleMessage(update);
        });
    }
    
    handleExpenseCreated(expense) {
        // Update expense list
        this.updateExpenseList(expense);
        
        // Show notification
        this.showNotification('success', `New expense: $${(expense.amount_cents / 100).toFixed(2)} - ${expense.vendor}`);
        
        // Update metrics
        this.updateMetrics();
    }
    
    handleExpenseUpdated(expense) {
        // Update expense in list
        this.updateExpenseInList(expense);
        
        // Show notification
        this.showNotification('info', `Expense updated: ${expense.vendor}`);
        
        // Update metrics
        this.updateMetrics();
    }
    
    handleJobStatusChanged(job) {
        // Update job status in dashboard
        this.updateJobStatus(job);
        
        // Show notification
        this.showNotification('info', `Job status changed: ${job.name} - ${job.status}`);
        
        // Update job profitability
        this.updateJobProfitability();
    }
    
    handleAlertCreated(alert) {
        // Add to alerts panel
        if (window.alertsPanel) {
            window.alertsPanel.addAlert(alert);
        }
        
        // Show notification
        this.showNotification('warning', alert.message);
        
        // Play sound for critical alerts
        if (alert.severity === 'critical') {
            this.playAlertSound();
        }
    }
    
    handleHealthChanged(health) {
        // Update health indicator
        if (window.coraHealthMonitor) {
            window.coraHealthMonitor.setStatus(health.status);
        }
        
        // Show notification for degraded health
        if (health.status === 'degraded') {
            this.showNotification('warning', 'System performance degraded');
        }
    }
    
    updateExpenseList(expense) {
        // Find expense list and add new expense
        const expenseList = document.querySelector('.transactions-list');
        if (expenseList) {
            const expenseElement = this.createExpenseElement(expense);
            expenseList.insertBefore(expenseElement, expenseList.firstChild);
        }
    }
    
    updateExpenseInList(expense) {
        // Find and update existing expense
        const expenseElement = document.querySelector(`[data-expense-id="${expense.id}"]`);
        if (expenseElement) {
            expenseElement.innerHTML = this.createExpenseHTML(expense);
        }
    }
    
    updateJobStatus(job) {
        // Find and update job status
        const jobElement = document.querySelector(`[data-job-id="${job.id}"]`);
        if (jobElement) {
            const statusElement = jobElement.querySelector('.job-status');
            if (statusElement) {
                statusElement.textContent = job.status;
                statusElement.className = `job-status status-${job.status.toLowerCase()}`;
            }
        }
    }
    
    updateMetrics() {
        // Refresh dashboard metrics
        if (typeof initDashboard === 'function') {
            initDashboard();
        }
    }
    
    updateJobProfitability() {
        // Refresh job profitability section
        const jobProfitabilityGrid = document.getElementById('jobProfitabilityGrid');
        if (jobProfitabilityGrid) {
            // Trigger job profitability refresh
            this.loadJobProfitability();
        }
    }
    
    async loadJobProfitability() {
        try {
            const response = await fetch('/api/jobs/profitability');
            if (response.ok) {
                const jobs = await response.json();
                this.renderJobProfitability(jobs);
            }
        } catch (error) {
            // console.error('Failed to load job profitability:', error);
        }
    }
    
    renderJobProfitability(jobs) {
        const grid = document.getElementById('jobProfitabilityGrid');
        if (!grid) return;
        
        // Render job profitability cards
        // This would be implemented based on existing job profitability rendering
    }
    
    createExpenseElement(expense) {
        const element = document.createElement('div');
        element.className = 'transaction-item';
        element.setAttribute('data-expense-id', expense.id);
        element.innerHTML = this.createExpenseHTML(expense);
        return element;
    }
    
    createExpenseHTML(expense) {
        return `
            <div class="transaction-amount">$${(expense.amount_cents / 100).toFixed(2)}</div>
            <div class="transaction-details">
                <div class="transaction-vendor">${expense.vendor}</div>
                <div class="transaction-category">${expense.category}</div>
            </div>
            <div class="transaction-date">${new Date(expense.created_at).toLocaleDateString()}</div>
        `;
    }
    
    showNotification(type, message) {
        const notification = document.createElement('div');
        notification.className = `realtime-notification ${type}`;
        notification.innerHTML = `
            <div class="notification-content">
                <div class="notification-icon">${this.getNotificationIcon(type)}</div>
                <div class="notification-text">${message}</div>
            </div>
        `;
        
        document.body.appendChild(notification);
        
        setTimeout(() => {
            notification.remove();
        }, 5000);
        
        this.addNotificationStyles();
    }
    
    getNotificationIcon(type) {
        const icons = {
            success: '✅',
            info: 'ℹ️',
            warning: '⚠️',
            error: '❌'
        };
        return icons[type] || 'ℹ️';
    }
    
    showConnectionStatus(status) {
        const statusElement = document.getElementById('connection-status');
        if (!statusElement) {
            this.createConnectionStatusIndicator();
        }
        
        const indicator = document.getElementById('connection-status');
        if (indicator) {
            indicator.className = `connection-status ${status}`;
            indicator.title = `Connection: ${status}`;
        }
    }
    
    createConnectionStatusIndicator() {
        const indicator = document.createElement('div');
        indicator.id = 'connection-status';
        indicator.className = 'connection-status';
        indicator.innerHTML = '●';
        
        // Add to header
        const header = document.querySelector('.header-actions');
        if (header) {
            header.appendChild(indicator);
        }
        
        this.addConnectionStatusStyles();
    }
    
    addConnectionStatusStyles() {
        const styleId = 'connection-status-styles';
        if (document.getElementById(styleId)) return;
        
        const styles = `
            .connection-status {
                width: 8px;
                height: 8px;
                border-radius: 50%;
                margin-left: 8px;
                transition: background 0.3s ease;
            }
            
            .connection-status.connected {
                background: #10b981;
                box-shadow: 0 0 8px rgba(16, 185, 129, 0.5);
            }
            
            .connection-status.disconnected {
                background: #6b7280;
            }
            
            .connection-status.error {
                background: #ef4444;
                animation: pulse-error 2s infinite;
            }
            
            .connection-status.offline {
                background: #f59e0b;
            }
            
            .realtime-notification {
                position: fixed;
                top: 20px;
                right: 20px;
                background: white;
                border-radius: 8px;
                box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
                padding: 12px 16px;
                z-index: 10000;
                animation: slideInRight 0.3s ease;
            }
            
            @keyframes slideInRight {
                from {
                    transform: translateX(100%);
                    opacity: 0;
                }
                to {
                    transform: translateX(0);
                    opacity: 1;
                }
            }
        `;
        
        const styleElement = document.createElement('style');
        styleElement.id = styleId;
        styleElement.textContent = styles;
        document.head.appendChild(styleElement);
    }
    
    addNotificationStyles() {
        const styleId = 'realtime-notification-styles';
        if (document.getElementById(styleId)) return;
        
        const styles = `
            .realtime-notification {
                position: fixed;
                top: 20px;
                right: 20px;
                background: white;
                border-radius: 8px;
                box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
                padding: 12px 16px;
                z-index: 10000;
                animation: slideInRight 0.3s ease;
                max-width: 300px;
            }
            
            .realtime-notification.success {
                border-left: 4px solid #10b981;
            }
            
            .realtime-notification.info {
                border-left: 4px solid #3b82f6;
            }
            
            .realtime-notification.warning {
                border-left: 4px solid #f59e0b;
            }
            
            .realtime-notification.error {
                border-left: 4px solid #ef4444;
            }
            
            .realtime-notification .notification-content {
                display: flex;
                align-items: center;
                gap: 8px;
            }
            
            .realtime-notification .notification-icon {
                font-size: 16px;
            }
            
            .realtime-notification .notification-text {
                font-size: 14px;
                color: #374151;
            }
        `;
        
        const styleElement = document.createElement('style');
        styleElement.id = styleId;
        styleElement.textContent = styles;
        document.head.appendChild(styleElement);
    }
    
    playAlertSound() {
        // Create audio context for alert sound
        try {
            const audioContext = new (window.AudioContext || window.webkitAudioContext)();
            const oscillator = audioContext.createOscillator();
            const gainNode = audioContext.createGain();
            
            oscillator.connect(gainNode);
            gainNode.connect(audioContext.destination);
            
            oscillator.frequency.setValueAtTime(800, audioContext.currentTime);
            oscillator.frequency.setValueAtTime(600, audioContext.currentTime + 0.1);
            
            gainNode.gain.setValueAtTime(0.1, audioContext.currentTime);
            gainNode.gain.exponentialRampToValueAtTime(0.01, audioContext.currentTime + 0.2);
            
            oscillator.start(audioContext.currentTime);
            oscillator.stop(audioContext.currentTime + 0.2);
        } catch (error) {
            // console.log('Audio not supported, skipping alert sound');
        }
    }
    
    disconnect() {
        if (this.ws) {
            this.ws.close();
        }
    }
}

// Auto-initialize when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
    window.realtimeUpdates = new RealtimeUpdates();
});

// Export for use in other modules
if (typeof module !== 'undefined' && module.exports) {
    module.exports = RealtimeUpdates;
} 