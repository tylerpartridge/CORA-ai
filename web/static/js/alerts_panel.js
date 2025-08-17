/**
 * CORA Alerts Panel
 * Manages and displays job alerts and notifications
 */

class AlertsPanel {
    constructor(options = {}) {
        this.options = {
            endpoint: '/api/alerts',
            containerId: 'alerts-panel',
            checkInterval: 60000, // 1 minute
            ...options
        };
        
        this.alerts = [];
        this.isOpen = false;
        this.unreadCount = 0;
        
        this.init();
    }
    
    init() {
        this.createAlertsContainer();
        this.loadAlerts();
        this.startPolling();
    }
    
    createAlertsContainer() {
        // Create alerts container if it doesn't exist
        let container = document.getElementById(this.options.containerId);
        if (!container) {
            container = document.createElement('div');
            container.id = this.options.containerId;
            container.className = 'alerts-panel';
            container.innerHTML = `
                <div class="alerts-header">
                    <h3>Job Alerts</h3>
                    <div class="alerts-filters">
                        <select id="severity-filter" onchange="alertsPanel.filterAlerts()">
                            <option value="all">All Severities</option>
                            <option value="critical">Critical</option>
                            <option value="warning">Warning</option>
                            <option value="info">Info</option>
                        </select>
                        <select id="status-filter" onchange="alertsPanel.filterAlerts()">
                            <option value="all">All Status</option>
                            <option value="unread">Unread</option>
                            <option value="read">Read</option>
                        </select>
                    </div>
                    <div class="alerts-actions">
                        <button class="alert-action-btn secondary" onclick="alertsPanel.markAllRead()">
                            Mark All Read
                        </button>
                        <button class="alert-action-btn secondary" onclick="alertsPanel.dismissSelected()">
                            Dismiss Selected
                        </button>
                        <button class="alert-action-btn primary" onclick="alertsPanel.refreshAlerts()">
                            🔄 Refresh
                        </button>
                    </div>
                </div>
                <div class="alerts-content">
                    <div class="alerts-list" id="alerts-list">
                        <div class="loading">Loading alerts...</div>
                    </div>
                </div>
                <div class="alerts-footer">
                    <button class="alert-action-btn secondary" onclick="alertsPanel.close()">
                        Close
                    </button>
                </div>
            `;
            
            document.body.appendChild(container);
        }
        
        this.addAlertsStyles();
    }
    
    addAlertsStyles() {
        const styleId = 'alerts-panel-styles';
        if (document.getElementById(styleId)) return;
        
        const styles = `
            .alerts-panel {
                position: fixed;
                top: 80px;
                right: 20px;
                width: 400px;
                max-height: 600px;
                background: white;
                border-radius: 12px;
                box-shadow: 0 10px 40px rgba(0, 0, 0, 0.15);
                border: 1px solid #e5e7eb;
                z-index: 1000;
                display: none;
                flex-direction: column;
                overflow: hidden;
            }
            
            .alerts-panel.open {
                display: flex;
            }
            
            .alerts-header {
                padding: 16px 20px;
                border-bottom: 1px solid #e5e7eb;
                background: #f9fafb;
                border-radius: 12px 12px 0 0;
            }
            
            .alerts-header h3 {
                margin: 0 0 12px 0;
                font-size: 16px;
                font-weight: 600;
                color: #111827;
            }
            
            .alerts-filters {
                display: flex;
                gap: 8px;
                margin-bottom: 12px;
            }
            
            .alerts-filters select {
                padding: 4px 8px;
                border: 1px solid #d1d5db;
                border-radius: 4px;
                font-size: 12px;
                background: white;
            }
            
            .alerts-actions {
                display: flex;
                gap: 8px;
            }
            
            .alert-action-btn {
                padding: 6px 12px;
                border: 1px solid #d1d5db;
                border-radius: 6px;
                background: white;
                font-size: 12px;
                font-weight: 500;
                cursor: pointer;
                transition: all 0.2s ease;
            }
            
            .alert-action-btn:hover {
                background: #f3f4f6;
            }
            
            .alert-action-btn.primary {
                background: #3b82f6;
                color: white;
                border-color: #3b82f6;
            }
            
            .alert-action-btn.primary:hover {
                background: #2563eb;
            }
            
            .alert-action-btn.secondary {
                background: #f9fafb;
                color: #374151;
            }
            
            .alerts-content {
                flex: 1;
                overflow-y: auto;
                max-height: 400px;
            }
            
            .alerts-list {
                padding: 0;
            }
            
            .alert-item {
                padding: 16px 20px;
                border-bottom: 1px solid #f3f4f6;
                transition: background 0.2s ease;
                cursor: pointer;
            }
            
            .alert-item:hover {
                background: #f9fafb;
            }
            
            .alert-item.unread {
                background: #fef3c7;
                border-left: 4px solid #f59e0b;
            }
            
            .alert-item.critical {
                background: #fef2f2;
                border-left: 4px solid #ef4444;
            }
            
            .alert-item.warning {
                background: #fffbeb;
                border-left: 4px solid #f59e0b;
            }
            
            .alert-header {
                display: flex;
                justify-content: space-between;
                align-items: flex-start;
                margin-bottom: 8px;
            }
            
            .alert-title {
                font-weight: 600;
                font-size: 14px;
                color: #111827;
                margin: 0;
            }
            
            .alert-time {
                font-size: 12px;
                color: #6b7280;
            }
            
            .alert-message {
                font-size: 13px;
                color: #374151;
                line-height: 1.4;
                margin: 0;
            }
            
            .alert-severity {
                display: inline-block;
                padding: 2px 8px;
                border-radius: 12px;
                font-size: 10px;
                font-weight: 600;
                text-transform: uppercase;
                margin-top: 8px;
            }
            
            .alert-severity.critical {
                background: #fef2f2;
                color: #dc2626;
            }
            
            .alert-severity.warning {
                background: #fffbeb;
                color: #d97706;
            }
            
            .alert-severity.info {
                background: #eff6ff;
                color: #2563eb;
            }
            
            .alerts-footer {
                padding: 16px 20px;
                border-top: 1px solid #e5e7eb;
                background: #f9fafb;
                border-radius: 0 0 12px 12px;
                text-align: right;
            }
            
            .no-alerts {
                padding: 40px 20px;
                text-align: center;
                color: #6b7280;
            }
            
            .no-alerts-icon {
                font-size: 48px;
                margin-bottom: 16px;
                opacity: 0.5;
            }
            
            .loading {
                padding: 20px;
                text-align: center;
                color: #6b7280;
            }
            
            @media (max-width: 768px) {
                .alerts-panel {
                    position: fixed;
                    top: 0;
                    left: 0;
                    right: 0;
                    bottom: 0;
                    width: 100%;
                    max-height: 100%;
                    border-radius: 0;
                }
                
                .alerts-content {
                    max-height: none;
                    flex: 1;
                }
            }
        `;
        
        const styleElement = document.createElement('style');
        styleElement.id = styleId;
        styleElement.textContent = styles;
        document.head.appendChild(styleElement);
    }
    
    async loadAlerts() {
        try {
            const response = await fetch(this.options.endpoint);
            if (!response.ok) {
                throw new Error(`HTTP ${response.status}`);
            }
            
            const alerts = await response.json();
            this.alerts = alerts;
            this.renderAlerts();
            
        } catch (error) {
            // console.error('Failed to load alerts:', error);
            this.showError('Failed to load alerts');
        }
    }
    
    renderAlerts() {
        const listContainer = document.getElementById('alerts-list');
        if (!listContainer) return;
        
        if (this.alerts.length === 0) {
            listContainer.innerHTML = `
                <div class="no-alerts">
                    <div class="no-alerts-icon">🔔</div>
                    <h4>No Alerts</h4>
                    <p>All jobs are running smoothly!</p>
                </div>
            `;
            return;
        }
        
        // Group alerts by severity
        const critical = this.alerts.filter(a => a.severity === 'critical');
        const warning = this.alerts.filter(a => a.severity === 'warning');
        const info = this.alerts.filter(a => a.severity === 'info');
        
        let html = '';
        
        // Render critical alerts first
        if (critical.length > 0) {
            html += this.renderAlertGroup('Critical', critical, 'critical');
        }
        
        // Render warning alerts
        if (warning.length > 0) {
            html += this.renderAlertGroup('Warnings', warning, 'warning');
        }
        
        // Render info alerts
        if (info.length > 0) {
            html += this.renderAlertGroup('Info', info, 'info');
        }
        
        listContainer.innerHTML = html;
        this.updateUnreadCount();
    }
    
    renderAlertGroup(title, alerts, severity) {
        let html = `<div class="alert-group">`;
        
        alerts.forEach(alert => {
            const timeAgo = this.getTimeAgo(alert.created_at);
            const unreadClass = alert.read ? '' : 'unread';
            const severityClass = `alert-severity ${severity}`;
            
            html += `
                <div class="alert-item ${unreadClass} ${severity}" onclick="alertsPanel.markAsRead('${alert.id}')">
                    <div class="alert-header">
                        <h4 class="alert-title">${alert.title}</h4>
                        <span class="alert-time">${timeAgo}</span>
                    </div>
                    <p class="alert-message">${alert.message}</p>
                    <span class="${severityClass}">${severity}</span>
                </div>
            `;
        });
        
        html += `</div>`;
        return html;
    }
    
    getTimeAgo(timestamp) {
        const now = new Date();
        const alertTime = new Date(timestamp);
        const diffMs = now - alertTime;
        const diffMins = Math.floor(diffMs / 60000);
        const diffHours = Math.floor(diffMs / 3600000);
        const diffDays = Math.floor(diffMs / 86400000);
        
        if (diffMins < 1) return 'Just now';
        if (diffMins < 60) return `${diffMins}m ago`;
        if (diffHours < 24) return `${diffHours}h ago`;
        return `${diffDays}d ago`;
    }
    
    async markAsRead(alertId) {
        try {
            const response = await fetch(`/api/alerts/${alertId}/read`, {
                method: 'POST'
            });
            
            if (response.ok) {
                // Update local state
                const alert = this.alerts.find(a => a.id === alertId);
                if (alert) {
                    alert.read = true;
                    this.renderAlerts();
                }
            }
        } catch (error) {
            // console.error('Failed to mark alert as read:', error);
        }
    }
    
    async markAllRead() {
        try {
            const response = await fetch('/api/alerts/mark-all-read', {
                method: 'POST'
            });
            
            if (response.ok) {
                this.alerts.forEach(alert => alert.read = true);
                this.renderAlerts();
            }
        } catch (error) {
            // console.error('Failed to mark all alerts as read:', error);
        }
    }
    
    updateUnreadCount() {
        this.unreadCount = this.alerts.filter(alert => !alert.read).length;
        
        // Update alert count badge
        const countBadge = document.getElementById('alertCount');
        if (countBadge) {
            if (this.unreadCount > 0) {
                countBadge.textContent = this.unreadCount;
                countBadge.style.display = 'block';
            } else {
                countBadge.style.display = 'none';
            }
        }
    }
    
    showError(message) {
        const listContainer = document.getElementById('alerts-list');
        if (listContainer) {
            listContainer.innerHTML = `
                <div class="no-alerts">
                    <div class="no-alerts-icon">❌</div>
                    <h4>Error</h4>
                    <p>${message}</p>
                </div>
            `;
        }
    }
    
    open() {
        const panel = document.getElementById(this.options.containerId);
        if (panel) {
            panel.classList.add('open');
            this.isOpen = true;
        }
    }
    
    close() {
        const panel = document.getElementById(this.options.containerId);
        if (panel) {
            panel.classList.remove('open');
            this.isOpen = false;
        }
    }
    
    toggle() {
        if (this.isOpen) {
            this.close();
        } else {
            this.open();
        }
    }
    
    refreshAlerts() {
        this.loadAlerts();
    }
    
    startPolling() {
        // Check for new alerts every minute
        setInterval(() => {
            this.loadAlerts();
        }, this.options.checkInterval);
    }
    
    getUnreadCount() {
        return this.unreadCount;
    }
    
    filterAlerts() {
        const severityFilter = document.getElementById('severity-filter').value;
        const statusFilter = document.getElementById('status-filter').value;
        
        let filteredAlerts = this.alerts;
        
        // Filter by severity
        if (severityFilter !== 'all') {
            filteredAlerts = filteredAlerts.filter(alert => alert.severity === severityFilter);
        }
        
        // Filter by status
        if (statusFilter !== 'all') {
            filteredAlerts = filteredAlerts.filter(alert => 
                statusFilter === 'unread' ? !alert.read : alert.read
            );
        }
        
        this.renderFilteredAlerts(filteredAlerts);
    }
    
    renderFilteredAlerts(alerts) {
        const listContainer = document.getElementById('alerts-list');
        if (!listContainer) return;
        
        if (alerts.length === 0) {
            listContainer.innerHTML = `
                <div class="no-alerts">
                    <div class="no-alerts-icon">🔍</div>
                    <h4>No Alerts Found</h4>
                    <p>Try adjusting your filters</p>
                </div>
            `;
            return;
        }
        
        // Group alerts by severity
        const critical = alerts.filter(a => a.severity === 'critical');
        const warning = alerts.filter(a => a.severity === 'warning');
        const info = alerts.filter(a => a.severity === 'info');
        
        let html = '';
        
        // Render critical alerts first
        if (critical.length > 0) {
            html += this.renderAlertGroup('Critical', critical, 'critical');
        }
        
        // Render warning alerts
        if (warning.length > 0) {
            html += this.renderAlertGroup('Warnings', warning, 'warning');
        }
        
        // Render info alerts
        if (info.length > 0) {
            html += this.renderAlertGroup('Info', info, 'info');
        }
        
        listContainer.innerHTML = html;
    }
    
    dismissSelected() {
        const selectedAlerts = document.querySelectorAll('.alert-item input[type="checkbox"]:checked');
        const alertIds = Array.from(selectedAlerts).map(checkbox => checkbox.value);
        
        if (alertIds.length === 0) {
            alert('Please select alerts to dismiss');
            return;
        }
        
        // Remove selected alerts from local state
        this.alerts = this.alerts.filter(alert => !alertIds.includes(alert.id));
        this.renderAlerts();
        
        // TODO: Send dismiss request to server
        // console.log('Dismissing alerts:', alertIds);
    }
}

// Global instance
window.alertsPanel = new AlertsPanel();

// Export for use in other modules
if (typeof module !== 'undefined' && module.exports) {
    module.exports = AlertsPanel;
} 