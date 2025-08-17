/**
 * CORA Error Recovery
 * Provides smart error recovery for voice expense entry
 */

class ErrorRecovery {
    constructor() {
        this.modal = null;
        this.currentData = null;
        this.offlineQueue = [];
        this.retryAttempts = 0;
        this.maxRetries = 3;
        this.init();
        this.loadOfflineQueue();
    }
    
    init() {
        this.createModal();
    }
    
    createModal() {
        this.modal = document.createElement('div');
        this.modal.id = 'error-recovery-modal';
        this.modal.className = 'error-recovery-modal';
        this.modal.innerHTML = `
            <div class="modal-overlay"></div>
            <div class="modal-content">
                <div class="modal-header">
                    <h3>Voice Entry Error</h3>
                    <button class="close-btn" onclick="errorRecovery.close()">×</button>
                </div>
                <div class="modal-body">
                    <div class="error-message" id="error-message"></div>
                    <div class="recovery-form" id="recovery-form">
                        <div class="form-group">
                            <label for="vendor-input">Vendor</label>
                            <input type="text" id="vendor-input" placeholder="Enter vendor name">
                        </div>
                        <div class="form-group">
                            <label for="amount-input">Amount</label>
                            <input type="number" id="amount-input" placeholder="0.00" step="0.01">
                        </div>
                        <div class="form-group">
                            <label for="job-select">Job (Optional)</label>
                            <select id="job-select">
                                <option value="">Select a job</option>
                            </select>
                        </div>
                        <div class="form-group">
                            <label for="category-select">Category</label>
                            <select id="category-select">
                                <option value="materials">Materials</option>
                                <option value="labor">Labor</option>
                                <option value="equipment">Equipment</option>
                                <option value="subcontractor">Subcontractor</option>
                                <option value="other">Other</option>
                            </select>
                        </div>
                    </div>
                </div>
                <div class="modal-footer">
                    <button class="btn-secondary" onclick="errorRecovery.close()">Cancel</button>
                    <button class="btn-primary" onclick="errorRecovery.saveExpense()">Save Expense</button>
                </div>
            </div>
        `;
        
        document.body.appendChild(this.modal);
        this.addModalStyles();
    }
    
    addModalStyles() {
        const styleId = 'error-recovery-modal-styles';
        if (document.getElementById(styleId)) return;
        
        const styles = `
            .error-recovery-modal {
                position: fixed;
                top: 0;
                left: 0;
                width: 100%;
                height: 100%;
                z-index: 10000;
                display: none;
                align-items: center;
                justify-content: center;
            }
            
            .error-recovery-modal.open {
                display: flex;
            }
            
            .modal-overlay {
                position: absolute;
                top: 0;
                left: 0;
                width: 100%;
                height: 100%;
                background: rgba(0, 0, 0, 0.5);
                backdrop-filter: blur(4px);
            }
            
            .modal-content {
                position: relative;
                background: white;
                border-radius: 12px;
                box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
                width: 90%;
                max-width: 500px;
                max-height: 90vh;
                overflow-y: auto;
                animation: modalSlideIn 0.3s ease;
            }
            
            @keyframes modalSlideIn {
                from {
                    transform: translateY(-20px);
                    opacity: 0;
                }
                to {
                    transform: translateY(0);
                    opacity: 1;
                }
            }
            
            .modal-header {
                padding: 20px 24px;
                border-bottom: 1px solid #e5e7eb;
                display: flex;
                justify-content: space-between;
                align-items: center;
            }
            
            .modal-header h3 {
                margin: 0;
                font-size: 18px;
                font-weight: 600;
                color: #111827;
            }
            
            .close-btn {
                background: none;
                border: none;
                font-size: 24px;
                color: #6b7280;
                cursor: pointer;
                padding: 4px;
                border-radius: 4px;
                transition: all 0.2s ease;
            }
            
            .close-btn:hover {
                background: #f3f4f6;
                color: #374151;
            }
            
            .modal-body {
                padding: 24px;
            }
            
            .error-message {
                background: #fef2f2;
                border: 1px solid #fecaca;
                border-radius: 8px;
                padding: 12px 16px;
                margin-bottom: 20px;
                color: #dc2626;
                font-size: 14px;
            }
            
            .recovery-form {
                display: flex;
                flex-direction: column;
                gap: 16px;
            }
            
            .form-group {
                display: flex;
                flex-direction: column;
                gap: 6px;
            }
            
            .form-group label {
                font-size: 14px;
                font-weight: 500;
                color: #374151;
            }
            
            .form-group input,
            .form-group select {
                padding: 10px 12px;
                border: 1px solid #d1d5db;
                border-radius: 6px;
                font-size: 14px;
                transition: border-color 0.2s ease;
            }
            
            .form-group input:focus,
            .form-group select:focus {
                outline: none;
                border-color: #9B6EC8;
                box-shadow: 0 0 0 3px rgba(155, 110, 200, 0.1);
            }
            
            .modal-footer {
                padding: 20px 24px;
                border-top: 1px solid #e5e7eb;
                display: flex;
                justify-content: flex-end;
                gap: 12px;
            }
            
            .btn-primary,
            .btn-secondary {
                padding: 10px 20px;
                border-radius: 6px;
                font-size: 14px;
                font-weight: 500;
                cursor: pointer;
                transition: all 0.2s ease;
                border: none;
            }
            
            .btn-primary {
                background: #9B6EC8;
                color: white;
            }
            
            .btn-primary:hover {
                background: #7C3AED;
            }
            
            .btn-secondary {
                background: #f3f4f6;
                color: #374151;
                border: 1px solid #d1d5db;
            }
            
            .btn-secondary:hover {
                background: #e5e7eb;
            }
            
            @media (max-width: 768px) {
                .modal-content {
                    width: 95%;
                    margin: 20px;
                }
                
                .modal-header,
                .modal-body,
                .modal-footer {
                    padding: 16px;
                }
            }
        `;
        
        const styleElement = document.createElement('style');
        styleElement.id = styleId;
        styleElement.textContent = styles;
        document.head.appendChild(styleElement);
    }
    
    handleVoiceError(error, parsedData) {
        this.currentData = parsedData || {};
        
        // Determine error type and show appropriate recovery UI
        if (error.includes('amount') || error.includes('cost')) {
            this.showAmountInput(parsedData);
        } else if (error.includes('job') || error.includes('project')) {
            this.showJobSelector(parsedData);
        } else if (error.includes('vendor') || error.includes('supplier')) {
            this.showVendorInput(parsedData);
        } else {
            this.showGenericRecovery(parsedData);
        }
    }
    
    showAmountInput(data) {
        this.showModal('Amount not recognized', data);
        this.populateForm(data);
        
        // Focus on amount input
        setTimeout(() => {
            const amountInput = document.getElementById('amount-input');
            if (amountInput) amountInput.focus();
        }, 100);
    }
    
    showJobSelector(data) {
        this.showModal('Job not found', data);
        this.populateForm(data);
        this.loadJobs();
        
        // Focus on job select
        setTimeout(() => {
            const jobSelect = document.getElementById('job-select');
            if (jobSelect) jobSelect.focus();
        }, 100);
    }
    
    showVendorInput(data) {
        this.showModal('Vendor not recognized', data);
        this.populateForm(data);
        
        // Focus on vendor input
        setTimeout(() => {
            const vendorInput = document.getElementById('vendor-input');
            if (vendorInput) vendorInput.focus();
        }, 100);
    }
    
    showGenericRecovery(data) {
        this.showModal('Voice entry needs clarification', data);
        this.populateForm(data);
    }
    
    showModal(errorMessage, data) {
        const messageElement = document.getElementById('error-message');
        if (messageElement) {
            messageElement.textContent = errorMessage;
        }
        
        this.populateForm(data);
        this.modal.classList.add('open');
    }
    
    populateForm(data) {
        if (!data) return;
        
        const vendorInput = document.getElementById('vendor-input');
        const amountInput = document.getElementById('amount-input');
        const categorySelect = document.getElementById('category-select');
        
        if (vendorInput && data.vendor) {
            vendorInput.value = data.vendor;
        }
        
        if (amountInput && data.amount) {
            amountInput.value = data.amount;
        }
        
        if (categorySelect && data.category) {
            categorySelect.value = data.category;
        }
    }
    
    async loadJobs() {
        try {
            const response = await fetch('/api/jobs');
            if (response.ok) {
                const jobs = await response.json();
                const jobSelect = document.getElementById('job-select');
                
                if (jobSelect) {
                    // Clear existing options except the first one
                    jobSelect.innerHTML = '<option value="">Select a job</option>';
                    
                    jobs.forEach(job => {
                        const option = document.createElement('option');
                        option.value = job.id;
                        option.textContent = job.name;
                        jobSelect.appendChild(option);
                    });
                }
            }
        } catch (error) {
            // console.error('Failed to load jobs:', error);
        }
    }
    
    async saveExpense() {
        const vendorInput = document.getElementById('vendor-input');
        const amountInput = document.getElementById('amount-input');
        const jobSelect = document.getElementById('job-select');
        const categorySelect = document.getElementById('category-select');
        
        const expenseData = {
            vendor: vendorInput.value.trim(),
            amount_cents: Math.round(parseFloat(amountInput.value) * 100),
            job_id: jobSelect.value || null,
            category: categorySelect.value,
            source: 'voice_recovery'
        };
        
        // Validate required fields
        if (!expenseData.vendor || !expenseData.amount_cents) {
            alert('Please fill in vendor and amount');
            return;
        }
        
        try {
            const response = await fetch('/api/expenses', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(expenseData)
            });
            
            if (response.ok) {
                const result = await response.json();
                this.close();
                this.showSuccess(result.expense);
                
                // Refresh dashboard data
                if (typeof initDashboard === 'function') {
                    initDashboard();
                }
            } else {
                throw new Error('Failed to save expense');
            }
        } catch (error) {
            // console.error('Error saving expense:', error);
            alert('Failed to save expense. Please try again.');
        }
    }
    
    showSuccess(expense) {
        const notification = document.createElement('div');
        notification.className = 'voice-success-notification';
        notification.innerHTML = `
            <div class="notification-content">
                <div class="notification-icon">✅</div>
                <div class="notification-text">
                    <strong>Expense Saved!</strong><br>
                    $${(expense.amount_cents / 100).toFixed(2)} - ${expense.vendor}
                </div>
            </div>
        `;
        
        document.body.appendChild(notification);
        
        setTimeout(() => {
            notification.remove();
        }, 3000);
    }
    
    close() {
        this.modal.classList.remove('open');
        this.currentData = null;
        
        // Clear form
        const form = document.getElementById('recovery-form');
        if (form) {
            form.reset();
        }
    }
    
    addToOfflineQueue(expenseData) {
        const queueItem = {
            id: Date.now(),
            data: expenseData,
            timestamp: new Date().toISOString(),
            retryCount: 0
        };
        
        this.offlineQueue.push(queueItem);
        this.saveOfflineQueue();
        this.showOfflineNotification();
    }
    
    saveOfflineQueue() {
        localStorage.setItem('cora_offline_queue', JSON.stringify(this.offlineQueue));
    }
    
    loadOfflineQueue() {
        const saved = localStorage.getItem('cora_offline_queue');
        if (saved) {
            this.offlineQueue = JSON.parse(saved);
        }
    }
    
    async processOfflineQueue() {
        if (this.offlineQueue.length === 0) return;
        
        if (!navigator.onLine) {
            // console.log('Still offline, will retry when connection restored');
            return;
        }
        
        const itemsToProcess = [...this.offlineQueue];
        
        for (const item of itemsToProcess) {
            try {
                await this.retryExpenseSubmission(item.data);
                this.removeFromOfflineQueue(item.id);
            } catch (error) {
                item.retryCount++;
                if (item.retryCount >= this.maxRetries) {
                    this.removeFromOfflineQueue(item.id);
                    // console.error('Max retries reached for item:', item.id);
                }
            }
        }
    }
    
    removeFromOfflineQueue(itemId) {
        this.offlineQueue = this.offlineQueue.filter(item => item.id !== itemId);
        this.saveOfflineQueue();
    }
    
    async retryExpenseSubmission(expenseData) {
        const response = await fetch('/api/expenses', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(expenseData)
        });
        
        if (!response.ok) {
            throw new Error('Failed to submit expense');
        }
        
        return response.json();
    }
    
    showOfflineNotification() {
        const notification = document.createElement('div');
        notification.className = 'offline-notification';
        notification.innerHTML = `
            <div class="notification-content">
                <div class="notification-icon">📱</div>
                <div class="notification-text">
                    <strong>Offline Mode</strong><br>
                    Expense saved locally. Will sync when online.
                </div>
            </div>
        `;
        
        document.body.appendChild(notification);
        
        setTimeout(() => {
            notification.remove();
        }, 3000);
    }
}

// Global instance
window.errorRecovery = new ErrorRecovery();

// Export for use in other modules
if (typeof module !== 'undefined' && module.exports) {
    module.exports = ErrorRecovery;
} 