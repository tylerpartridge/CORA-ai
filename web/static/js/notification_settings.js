/**
 * Notification Settings Component
 * Manages email and SMS notification preferences
 */

class NotificationSettings {
    constructor(container) {
        this.container = container;
        this.preferences = {
            email_notifications: true,
            sms_notifications: false,
            phone_number: null,
            alert_thresholds: {
                margin_warning: 20,  // Alert when margin drops below 20%
                margin_critical: 10, // Critical alert below 10%
                budget_warning: 90,  // Alert when 90% of budget used
                budget_critical: 100 // Critical when over budget
            }
        };
        this.init();
    }
    
    async init() {
        await this.loadPreferences();
        this.render();
        this.bindEvents();
    }
    
    async loadPreferences() {
        try {
            const response = await fetch('/api/user/preferences');
            if (response.ok) {
                const data = await response.json();
                this.preferences = { ...this.preferences, ...data };
            }
        } catch (error) {
            // console.error('Failed to load preferences:', error);
        }
    }
    
    render() {
        this.container.innerHTML = `
            <div class="notification-settings">
                <h3 class="settings-title">Notification Settings</h3>
                
                <div class="notification-channels">
                    <div class="channel-card email-channel">
                        <div class="channel-header">
                            <div class="channel-icon">📧</div>
                            <div class="channel-info">
                                <h4>Email Notifications</h4>
                                <p class="channel-status">Receive alerts via email</p>
                            </div>
                            <label class="toggle-switch">
                                <input type="checkbox" id="email-toggle" 
                                    ${this.preferences.email_notifications ? 'checked' : ''}>
                                <span class="toggle-slider"></span>
                            </label>
                        </div>
                        <div class="channel-details ${this.preferences.email_notifications ? 'active' : ''}">
                            <p class="verified-badge">✅ Email verified</p>
                        </div>
                    </div>
                    
                    <div class="channel-card sms-channel">
                        <div class="channel-header">
                            <div class="channel-icon">📱</div>
                            <div class="channel-info">
                                <h4>SMS Notifications</h4>
                                <p class="channel-status">Get urgent alerts via text</p>
                            </div>
                            <label class="toggle-switch">
                                <input type="checkbox" id="sms-toggle" 
                                    ${this.preferences.sms_notifications ? 'checked' : ''}>
                                <span class="toggle-slider"></span>
                            </label>
                        </div>
                        <div class="channel-details ${this.preferences.sms_notifications ? 'active' : ''}">
                            <div class="phone-input-group">
                                <input type="tel" 
                                    id="phone-number" 
                                    placeholder="+1 (555) 123-4567"
                                    value="${this.preferences.phone_number || ''}"
                                    class="phone-input">
                                <button class="verify-btn" id="verify-phone">Verify</button>
                            </div>
                        </div>
                    </div>
                </div>
                
                <div class="alert-thresholds">
                    <h4>Alert Thresholds</h4>
                    <div class="threshold-grid">
                        <div class="threshold-item">
                            <label>Margin Warning</label>
                            <div class="threshold-control">
                                <input type="range" 
                                    id="margin-warning" 
                                    min="10" max="30" 
                                    value="${this.preferences.alert_thresholds.margin_warning}">
                                <span class="threshold-value">${this.preferences.alert_thresholds.margin_warning}%</span>
                            </div>
                        </div>
                        <div class="threshold-item">
                            <label>Budget Warning</label>
                            <div class="threshold-control">
                                <input type="range" 
                                    id="budget-warning" 
                                    min="70" max="100" 
                                    value="${this.preferences.alert_thresholds.budget_warning}">
                                <span class="threshold-value">${this.preferences.alert_thresholds.budget_warning}%</span>
                            </div>
                        </div>
                    </div>
                </div>
                
                <div class="test-notifications">
                    <h4>Test Notifications</h4>
                    <button class="test-btn" id="test-email">
                        <i class="fas fa-envelope"></i> Send Test Email
                    </button>
                    <button class="test-btn" id="test-sms" ${!this.preferences.phone_number ? 'disabled' : ''}>
                        <i class="fas fa-sms"></i> Send Test SMS
                    </button>
                </div>
                
                <div class="save-section">
                    <button class="save-btn" id="save-preferences">Save Preferences</button>
                </div>
            </div>
        `;
        
        this.addStyles();
    }
    
    addStyles() {
        const styleId = 'notification-settings-styles';
        if (document.getElementById(styleId)) return;
        
        const styles = `
            .notification-settings {
                background: white;
                padding: 24px;
                border-radius: 12px;
                box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
            }
            
            .settings-title {
                font-size: 24px;
                font-weight: 600;
                margin-bottom: 24px;
                color: #1a1a1a;
            }
            
            .notification-channels {
                display: flex;
                flex-direction: column;
                gap: 16px;
                margin-bottom: 32px;
            }
            
            .channel-card {
                border: 1px solid #e5e5e5;
                border-radius: 8px;
                padding: 16px;
                transition: all 0.3s ease;
            }
            
            .channel-card:hover {
                border-color: #9B6EC8;
            }
            
            .channel-header {
                display: flex;
                align-items: center;
                gap: 16px;
            }
            
            .channel-icon {
                font-size: 32px;
            }
            
            .channel-info {
                flex: 1;
            }
            
            .channel-info h4 {
                margin: 0 0 4px 0;
                font-size: 18px;
                color: #1a1a1a;
            }
            
            .channel-status {
                margin: 0;
                color: #666;
                font-size: 14px;
            }
            
            .toggle-switch {
                position: relative;
                display: inline-block;
                width: 50px;
                height: 24px;
            }
            
            .toggle-switch input {
                opacity: 0;
                width: 0;
                height: 0;
            }
            
            .toggle-slider {
                position: absolute;
                cursor: pointer;
                top: 0;
                left: 0;
                right: 0;
                bottom: 0;
                background-color: #ccc;
                transition: .4s;
                border-radius: 24px;
            }
            
            .toggle-slider:before {
                position: absolute;
                content: "";
                height: 18px;
                width: 18px;
                left: 3px;
                bottom: 3px;
                background-color: white;
                transition: .4s;
                border-radius: 50%;
            }
            
            input:checked + .toggle-slider {
                background-color: #22c55e;
            }
            
            input:checked + .toggle-slider:before {
                transform: translateX(26px);
            }
            
            .channel-details {
                margin-top: 16px;
                padding-top: 16px;
                border-top: 1px solid #f0f0f0;
                display: none;
            }
            
            .channel-details.active {
                display: block;
            }
            
            .verified-badge {
                color: #22c55e;
                font-size: 14px;
                margin: 0;
            }
            
            .phone-input-group {
                display: flex;
                gap: 12px;
            }
            
            .phone-input {
                flex: 1;
                padding: 8px 12px;
                border: 1px solid #e5e5e5;
                border-radius: 6px;
                font-size: 16px;
            }
            
            .verify-btn {
                padding: 8px 20px;
                background: #9B6EC8;
                color: white;
                border: none;
                border-radius: 6px;
                cursor: pointer;
                font-weight: 500;
            }
            
            .verify-btn:hover {
                background: #8B5EB8;
            }
            
            .alert-thresholds {
                background: #f8f9fa;
                padding: 20px;
                border-radius: 8px;
                margin-bottom: 24px;
            }
            
            .alert-thresholds h4 {
                margin: 0 0 16px 0;
                color: #1a1a1a;
            }
            
            .threshold-grid {
                display: grid;
                grid-template-columns: 1fr 1fr;
                gap: 20px;
            }
            
            .threshold-item label {
                display: block;
                margin-bottom: 8px;
                color: #666;
                font-size: 14px;
            }
            
            .threshold-control {
                display: flex;
                align-items: center;
                gap: 12px;
            }
            
            .threshold-control input[type="range"] {
                flex: 1;
            }
            
            .threshold-value {
                min-width: 40px;
                font-weight: 600;
                color: #1a1a1a;
            }
            
            .test-notifications {
                margin-bottom: 24px;
            }
            
            .test-notifications h4 {
                margin: 0 0 16px 0;
                color: #1a1a1a;
            }
            
            .test-btn {
                padding: 10px 20px;
                margin-right: 12px;
                background: #f0f0f0;
                border: 1px solid #e5e5e5;
                border-radius: 6px;
                cursor: pointer;
                font-size: 14px;
                transition: all 0.3s ease;
            }
            
            .test-btn:hover:not(:disabled) {
                background: #e5e5e5;
            }
            
            .test-btn:disabled {
                opacity: 0.5;
                cursor: not-allowed;
            }
            
            .save-btn {
                padding: 12px 32px;
                background: #9B6EC8;
                color: white;
                border: none;
                border-radius: 8px;
                cursor: pointer;
                font-size: 16px;
                font-weight: 600;
                width: 100%;
            }
            
            .save-btn:hover {
                background: #8B5EB8;
            }
            
            @media (max-width: 768px) {
                .threshold-grid {
                    grid-template-columns: 1fr;
                }
                
                .test-btn {
                    display: block;
                    width: 100%;
                    margin-bottom: 12px;
                }
            }
        `;
        
        const styleSheet = document.createElement('style');
        styleSheet.id = styleId;
        styleSheet.textContent = styles;
        document.head.appendChild(styleSheet);
    }
    
    bindEvents() {
        // Toggle switches
        document.getElementById('email-toggle').addEventListener('change', (e) => {
            this.preferences.email_notifications = e.target.checked;
            this.updateChannelVisibility();
        });
        
        document.getElementById('sms-toggle').addEventListener('change', (e) => {
            this.preferences.sms_notifications = e.target.checked;
            this.updateChannelVisibility();
        });
        
        // Phone number input
        document.getElementById('phone-number').addEventListener('input', (e) => {
            this.preferences.phone_number = e.target.value;
            document.getElementById('test-sms').disabled = !e.target.value;
        });
        
        // Threshold sliders
        ['margin-warning', 'budget-warning'].forEach(id => {
            const slider = document.getElementById(id);
            slider.addEventListener('input', (e) => {
                const key = id.replace('-', '_');
                this.preferences.alert_thresholds[key] = parseInt(e.target.value);
                e.target.nextElementSibling.textContent = `${e.target.value}%`;
            });
        });
        
        // Test buttons
        document.getElementById('test-email').addEventListener('click', () => this.testEmail());
        document.getElementById('test-sms').addEventListener('click', () => this.testSMS());
        
        // Save button
        document.getElementById('save-preferences').addEventListener('click', () => this.savePreferences());
        
        // Verify phone
        document.getElementById('verify-phone').addEventListener('click', () => this.verifyPhone());
    }
    
    updateChannelVisibility() {
        const emailDetails = document.querySelector('.email-channel .channel-details');
        const smsDetails = document.querySelector('.sms-channel .channel-details');
        
        emailDetails.classList.toggle('active', this.preferences.email_notifications);
        smsDetails.classList.toggle('active', this.preferences.sms_notifications);
    }
    
    async testEmail() {
        try {
            const response = await fetch('/api/test-notifications', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ email: true })
            });
            
            if (response.ok) {
                this.showNotification('Test email sent! Check your inbox.', 'success');
            } else {
                this.showNotification('Failed to send test email', 'error');
            }
        } catch (error) {
            this.showNotification('Error sending test email', 'error');
        }
    }
    
    async testSMS() {
        if (!this.preferences.phone_number) return;
        
        try {
            const response = await fetch('/api/test-notifications', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ 
                    sms: true,
                    phone: this.preferences.phone_number 
                })
            });
            
            if (response.ok) {
                this.showNotification('Test SMS sent!', 'success');
            } else {
                this.showNotification('Failed to send test SMS', 'error');
            }
        } catch (error) {
            this.showNotification('Error sending test SMS', 'error');
        }
    }
    
    async verifyPhone() {
        // Implement phone verification logic
        this.showNotification('Phone verification coming soon!', 'info');
    }
    
    async savePreferences() {
        try {
            const response = await fetch('/api/user/preferences', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(this.preferences)
            });
            
            if (response.ok) {
                this.showNotification('Preferences saved successfully!', 'success');
            } else {
                this.showNotification('Failed to save preferences', 'error');
            }
        } catch (error) {
            this.showNotification('Error saving preferences', 'error');
        }
    }
    
    showNotification(message, type) {
        const notification = document.createElement('div');
        notification.className = `notification-toast ${type}`;
        notification.textContent = message;
        notification.style.cssText = `
            position: fixed;
            top: 20px;
            right: 20px;
            padding: 16px 24px;
            background: ${type === 'success' ? '#22c55e' : type === 'error' ? '#ef4444' : '#3b82f6'};
            color: white;
            border-radius: 8px;
            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
            z-index: 10000;
            animation: slideIn 0.3s ease;
        `;
        
        document.body.appendChild(notification);
        
        setTimeout(() => notification.remove(), 3000);
    }
}

// Initialize when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
    const container = document.querySelector('.notification-settings-container');
    if (container) {
        new NotificationSettings(container);
    }
});

// Export for use in other modules
window.NotificationSettings = NotificationSettings;