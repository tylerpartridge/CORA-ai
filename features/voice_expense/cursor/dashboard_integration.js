/**
 * Dashboard Integration for Voice Expense Entry
 * Adds voice button to dashboard and integrates with existing functionality
 */

class DashboardVoiceIntegration {
    constructor() {
        this.voiceButton = null;
        this.voiceModal = null;
        this.isInitialized = false;
    }
    
    init() {
        if (this.isInitialized) return;
        
        // Wait for dashboard to load
        this.waitForDashboard().then(() => {
            this.addVoiceButton();
            this.setupVoiceModal();
            this.bindDashboardEvents();
            this.isInitialized = true;
        });
    }
    
    waitForDashboard() {
        return new Promise((resolve) => {
            const checkDashboard = () => {
                const header = document.querySelector('.header-actions');
                if (header) {
                    resolve();
                } else {
                    setTimeout(checkDashboard, 100);
                }
            };
            checkDashboard();
        });
    }
    
    addVoiceButton() {
        const headerActions = document.querySelector('.header-actions');
        if (!headerActions) return;
        
        // Create voice button container
        const voiceContainer = document.createElement('div');
        voiceContainer.className = 'voice-button-container';
        
        // Add voice button
        this.voiceButton = new VoiceButton(voiceContainer, {
            onSuccess: (expense) => {
                this.onExpenseAdded(expense);
            },
            onError: (message, parsed) => {
                console.error('Voice button error:', message, parsed);
            }
        });
        
        // Insert before the existing "Quick Expense" button
        const quickExpenseBtn = headerActions.querySelector('.action-btn');
        if (quickExpenseBtn) {
            headerActions.insertBefore(voiceContainer, quickExpenseBtn);
        } else {
            headerActions.appendChild(voiceContainer);
        }
        
        // Add container styles
        this.addContainerStyles();
    }
    
    setupVoiceModal() {
        this.voiceModal = new VoiceModal({
            onSuccess: (expense) => {
                this.onExpenseAdded(expense);
            },
            onError: (message, parsed) => {
                console.error('Voice modal error:', message, parsed);
            },
            onClose: () => {
                // Modal closed
            }
        });
    }
    
    bindDashboardEvents() {
        // Listen for dashboard updates
        this.observeDashboardChanges();
        
        // Add keyboard shortcut for voice modal
        document.addEventListener('keydown', (e) => {
            // Ctrl/Cmd + V for voice modal
            if ((e.ctrlKey || e.metaKey) && e.key === 'v' && !e.shiftKey) {
                e.preventDefault();
                this.openVoiceModal();
            }
        });
        
        // Add voice button to existing "Quick Expense" functionality
        const quickExpenseBtn = document.querySelector('.action-btn');
        if (quickExpenseBtn) {
            quickExpenseBtn.addEventListener('click', (e) => {
                // Show options: voice or manual entry
                this.showQuickExpenseOptions(e);
            });
        }
    }
    
    showQuickExpenseOptions(event) {
        // Create options popup
        const popup = document.createElement('div');
        popup.className = 'quick-expense-options';
        popup.innerHTML = `
            <div class="options-content">
                <h4>Add Expense</h4>
                <div class="options-buttons">
                    <button class="option-btn voice-option">
                        <span class="option-icon">🎤</span>
                        <span class="option-text">Voice Entry</span>
                        <span class="option-shortcut">Ctrl+V</span>
                    </button>
                    <button class="option-btn manual-option">
                        <span class="option-icon">✏️</span>
                        <span class="option-text">Manual Entry</span>
                    </button>
                </div>
            </div>
        `;
        
        // Add popup styles
        this.addPopupStyles();
        
        // Position popup near the button
        const rect = event.target.getBoundingClientRect();
        popup.style.position = 'absolute';
        popup.style.top = `${rect.bottom + 8}px`;
        popup.style.left = `${rect.left}px`;
        popup.style.zIndex = '1000';
        
        // Add to page
        document.body.appendChild(popup);
        
        // Handle option clicks
        popup.querySelector('.voice-option').addEventListener('click', () => {
            this.openVoiceModal();
            popup.remove();
        });
        
        popup.querySelector('.manual-option').addEventListener('click', () => {
            // Trigger existing manual expense functionality
            this.triggerManualExpense();
            popup.remove();
        });
        
        // Close popup when clicking outside
        setTimeout(() => {
            document.addEventListener('click', function closePopup(e) {
                if (!popup.contains(e.target) && e.target !== event.target) {
                    popup.remove();
                    document.removeEventListener('click', closePopup);
                }
            });
        }, 0);
    }
    
    openVoiceModal() {
        if (this.voiceModal) {
            this.voiceModal.open();
        }
    }
    
    triggerManualExpense() {
        // This would trigger the existing manual expense entry
        // For now, just show a placeholder
        console.log('Manual expense entry triggered');
        // You can implement this to open your existing expense form
    }
    
    onExpenseAdded(expense) {
        // Update dashboard metrics
        this.updateDashboardMetrics(expense);
        
        // Refresh recent activity
        this.refreshRecentActivity();
        
        // Show success message
        this.showDashboardSuccess(expense);
    }
    
    updateDashboardMetrics(expense) {
        // Update total cash (if it's an income)
        const totalCashElement = document.getElementById('totalCash');
        if (totalCashElement && expense.amount_cents > 0) {
            const currentTotal = parseFloat(totalCashElement.textContent.replace('$', '').replace(',', ''));
            const newTotal = currentTotal + (expense.amount_cents / 100);
            totalCashElement.textContent = `$${newTotal.toFixed(0)}`;
        }
        
        // Update monthly profit
        const monthlyProfitElement = document.getElementById('monthlyProfit');
        if (monthlyProfitElement) {
            const currentProfit = parseFloat(monthlyProfitElement.textContent.replace('$', '').replace(',', ''));
            const newProfit = currentProfit - (expense.amount_cents / 100); // Subtract expense
            monthlyProfitElement.textContent = `$${newProfit.toFixed(0)}`;
        }
    }
    
    refreshRecentActivity() {
        // Trigger dashboard refresh
        const dashboardContent = document.querySelector('.dashboard-content');
        if (dashboardContent) {
            // Dispatch custom event to trigger refresh
            dashboardContent.dispatchEvent(new CustomEvent('expenseAdded'));
        }
    }
    
    showDashboardSuccess(expense) {
        // Create dashboard success notification
        const notification = document.createElement('div');
        notification.className = 'dashboard-success-notification';
        notification.innerHTML = `
            <div class="notification-content">
                <div class="notification-icon">✅</div>
                <div class="notification-text">
                    <strong>Expense Added to Dashboard!</strong><br>
                    $${(expense.amount_cents / 100).toFixed(2)} - ${expense.vendor}
                    ${expense.job_name ? `<br><small>Job: ${expense.job_name}</small>` : ''}
                </div>
            </div>
        `;
        
        // Add notification styles
        this.addDashboardNotificationStyles();
        
        // Show notification
        document.body.appendChild(notification);
        
        // Auto-remove after 4 seconds
        setTimeout(() => {
            notification.remove();
        }, 4000);
    }
    
    observeDashboardChanges() {
        // Watch for dashboard content changes
        const observer = new MutationObserver((mutations) => {
            mutations.forEach((mutation) => {
                if (mutation.type === 'childList') {
                    // Dashboard content changed, refresh if needed
                    this.handleDashboardChange();
                }
            });
        });
        
        const dashboardContent = document.querySelector('.dashboard-content');
        if (dashboardContent) {
            observer.observe(dashboardContent, {
                childList: true,
                subtree: true
            });
        }
    }
    
    handleDashboardChange() {
        // Handle dashboard content changes
        // This could refresh voice button state or update metrics
    }
    
    addContainerStyles() {
        const styleId = 'voice-container-styles';
        if (document.getElementById(styleId)) return;
        
        const styles = `
            .voice-button-container {
                display: flex;
                align-items: center;
            }
        `;
        
        const styleSheet = document.createElement('style');
        styleSheet.id = styleId;
        styleSheet.textContent = styles;
        document.head.appendChild(styleSheet);
    }
    
    addPopupStyles() {
        const styleId = 'quick-expense-popup-styles';
        if (document.getElementById(styleId)) return;
        
        const styles = `
            .quick-expense-options {
                background: white;
                border-radius: 8px;
                box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
                border: 1px solid #e5e7eb;
                animation: slideDown 0.2s ease;
            }
            
            .options-content {
                padding: 16px;
            }
            
            .options-content h4 {
                margin: 0 0 12px 0;
                font-size: 14px;
                color: #374151;
                font-weight: 600;
            }
            
            .options-buttons {
                display: flex;
                flex-direction: column;
                gap: 8px;
            }
            
            .option-btn {
                display: flex;
                align-items: center;
                gap: 12px;
                padding: 12px;
                border: 1px solid #e5e7eb;
                border-radius: 6px;
                background: white;
                cursor: pointer;
                transition: all 0.2s ease;
                text-align: left;
                width: 100%;
            }
            
            .option-btn:hover {
                background: #f9fafb;
                border-color: #9B6EC8;
            }
            
            .option-icon {
                font-size: 18px;
                width: 24px;
                text-align: center;
            }
            
            .option-text {
                flex: 1;
                font-size: 14px;
                font-weight: 500;
                color: #374151;
            }
            
            .option-shortcut {
                font-size: 12px;
                color: #6b7280;
                background: #f3f4f6;
                padding: 2px 6px;
                border-radius: 4px;
            }
            
            @keyframes slideDown {
                from {
                    transform: translateY(-10px);
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
    
    addDashboardNotificationStyles() {
        const styleId = 'dashboard-notification-styles';
        if (document.getElementById(styleId)) return;
        
        const styles = `
            .dashboard-success-notification {
                position: fixed;
                top: 20px;
                right: 20px;
                background: white;
                border-radius: 8px;
                box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
                padding: 16px;
                z-index: 1001;
                animation: slideIn 0.3s ease;
                max-width: 300px;
                border-left: 4px solid #22c55e;
            }
            
            .notification-content {
                display: flex;
                align-items: flex-start;
                gap: 12px;
            }
            
            .notification-icon {
                font-size: 20px;
                flex-shrink: 0;
            }
            
            .notification-text {
                font-size: 14px;
                line-height: 1.4;
            }
            
            .notification-text strong {
                color: #1f2937;
            }
            
            .notification-text small {
                color: #6b7280;
            }
            
            @keyframes slideIn {
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
        
        const styleSheet = document.createElement('style');
        styleSheet.id = styleId;
        styleSheet.textContent = styles;
        document.head.appendChild(styleSheet);
    }
    
    destroy() {
        if (this.voiceButton) {
            this.voiceButton.destroy();
        }
        if (this.voiceModal) {
            this.voiceModal.destroy();
        }
        this.isInitialized = false;
    }
}

// Auto-initialize when DOM is ready
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', () => {
        new DashboardVoiceIntegration().init();
    });
} else {
    new DashboardVoiceIntegration().init();
}

// Export for use
if (typeof module !== 'undefined' && module.exports) {
    module.exports = DashboardVoiceIntegration;
} 