/**
 * Voice Modal Component for Detailed Voice Expense Entry
 * Provides real-time transcript display and editing capabilities
 */

class VoiceModal {
    constructor(options = {}) {
        this.options = {
            apiEndpoint: '/api/voice/expense',
            onSuccess: null,
            onError: null,
            onClose: null,
            ...options
        };
        
        this.isRecording = false;
        this.recognition = null;
        this.modal = null;
        this.transcript = '';
        this.parsedData = null;
        
        this.init();
    }
    
    init() {
        this.createModal();
        this.setupSpeechRecognition();
        this.bindEvents();
    }
    
    createModal() {
        // Create modal HTML
        this.modal = document.createElement('div');
        this.modal.className = 'voice-modal-overlay';
        this.modal.innerHTML = `
            <div class="voice-modal">
                <div class="voice-modal-header">
                    <h3>Voice Expense Entry</h3>
                    <button class="voice-modal-close" aria-label="Close">×</button>
                </div>
                
                <div class="voice-modal-content">
                    <div class="voice-status-section">
                        <div class="voice-status-indicator">
                            <div class="voice-status-icon">🎤</div>
                            <div class="voice-status-text">Click to start recording</div>
                        </div>
                        <button class="voice-record-btn" type="button">
                            Start Recording
                        </button>
                    </div>
                    
                    <div class="voice-transcript-section" style="display: none;">
                        <h4>What you said:</h4>
                        <div class="voice-transcript-display"></div>
                        <button class="voice-retry-btn" type="button">Try Again</button>
                    </div>
                    
                    <div class="voice-preview-section" style="display: none;">
                        <h4>Expense Details:</h4>
                        <div class="voice-preview-form">
                            <div class="form-group">
                                <label>Amount:</label>
                                <input type="number" class="voice-amount-input" step="0.01" min="0">
                            </div>
                            <div class="form-group">
                                <label>Vendor:</label>
                                <input type="text" class="voice-vendor-input">
                            </div>
                            <div class="form-group">
                                <label>Job (optional):</label>
                                <input type="text" class="voice-job-input" placeholder="e.g., Johnson Bathroom">
                            </div>
                            <div class="form-group">
                                <label>Category:</label>
                                <select class="voice-category-select">
                                    <option value="">Auto-detected</option>
                                    <option value="Materials - Hardware">Materials - Hardware</option>
                                    <option value="Materials - Lumber">Materials - Lumber</option>
                                    <option value="Materials - Electrical">Materials - Electrical</option>
                                    <option value="Materials - Plumbing">Materials - Plumbing</option>
                                    <option value="Equipment - Fuel">Equipment - Fuel</option>
                                    <option value="Equipment - Rental">Equipment - Rental</option>
                                    <option value="Labor - Crew">Labor - Crew</option>
                                    <option value="Labor - Subcontractors">Labor - Subcontractors</option>
                                </select>
                            </div>
                            <div class="form-group">
                                <label>Description:</label>
                                <textarea class="voice-description-input" rows="2"></textarea>
                            </div>
                        </div>
                        
                        <div class="voice-preview-actions">
                            <button class="voice-save-btn" type="button">Save Expense</button>
                            <button class="voice-cancel-btn" type="button">Cancel</button>
                        </div>
                    </div>
                    
                    <div class="voice-error-section" style="display: none;">
                        <div class="voice-error-message"></div>
                        <button class="voice-retry-btn" type="button">Try Again</button>
                    </div>
                </div>
            </div>
        `;
        
        // Add to body
        document.body.appendChild(this.modal);
        
        // Add CSS styles
        this.addStyles();
    }
    
    addStyles() {
        const styleId = 'voice-modal-styles';
        if (document.getElementById(styleId)) return;
        
        const styles = `
            .voice-modal-overlay {
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
            
            .voice-modal {
                background: white;
                border-radius: 12px;
                box-shadow: 0 20px 40px rgba(0, 0, 0, 0.15);
                width: 90%;
                max-width: 500px;
                max-height: 90vh;
                overflow-y: auto;
                animation: slideUp 0.3s ease;
            }
            
            .voice-modal-header {
                display: flex;
                justify-content: space-between;
                align-items: center;
                padding: 20px 24px;
                border-bottom: 1px solid #e5e7eb;
            }
            
            .voice-modal-header h3 {
                margin: 0;
                font-size: 18px;
                font-weight: 600;
                color: #1f2937;
            }
            
            .voice-modal-close {
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
            
            .voice-modal-close:hover {
                background: #f3f4f6;
                color: #374151;
            }
            
            .voice-modal-content {
                padding: 24px;
            }
            
            .voice-status-section {
                text-align: center;
                padding: 40px 20px;
            }
            
            .voice-status-indicator {
                margin-bottom: 24px;
            }
            
            .voice-status-icon {
                font-size: 48px;
                margin-bottom: 12px;
                transition: all 0.3s ease;
            }
            
            .voice-status-text {
                font-size: 16px;
                color: #6b7280;
                margin-bottom: 8px;
            }
            
            .voice-record-btn {
                background: linear-gradient(135deg, #9B6EC8, #7C3AED);
                color: white;
                border: none;
                border-radius: 8px;
                padding: 12px 24px;
                font-size: 16px;
                font-weight: 600;
                cursor: pointer;
                transition: all 0.3s ease;
            }
            
            .voice-record-btn:hover {
                transform: translateY(-1px);
                box-shadow: 0 4px 12px rgba(155, 110, 200, 0.3);
            }
            
            .voice-record-btn.recording {
                background: linear-gradient(135deg, #ef4444, #dc2626);
                animation: pulse 1.5s infinite;
            }
            
            .voice-transcript-section {
                margin-bottom: 24px;
            }
            
            .voice-transcript-section h4 {
                margin: 0 0 12px 0;
                font-size: 16px;
                color: #374151;
            }
            
            .voice-transcript-display {
                background: #f9fafb;
                border: 1px solid #e5e7eb;
                border-radius: 8px;
                padding: 16px;
                font-size: 16px;
                line-height: 1.5;
                color: #1f2937;
                margin-bottom: 16px;
                min-height: 60px;
            }
            
            .voice-preview-section h4 {
                margin: 0 0 16px 0;
                font-size: 16px;
                color: #374151;
            }
            
            .voice-preview-form {
                display: grid;
                gap: 16px;
                margin-bottom: 24px;
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
            .form-group select,
            .form-group textarea {
                padding: 10px 12px;
                border: 1px solid #d1d5db;
                border-radius: 6px;
                font-size: 14px;
                transition: border-color 0.2s ease;
            }
            
            .form-group input:focus,
            .form-group select:focus,
            .form-group textarea:focus {
                outline: none;
                border-color: #9B6EC8;
                box-shadow: 0 0 0 3px rgba(155, 110, 200, 0.1);
            }
            
            .voice-preview-actions {
                display: flex;
                gap: 12px;
                justify-content: flex-end;
            }
            
            .voice-save-btn {
                background: linear-gradient(135deg, #22c55e, #16a34a);
                color: white;
                border: none;
                border-radius: 6px;
                padding: 10px 20px;
                font-size: 14px;
                font-weight: 600;
                cursor: pointer;
                transition: all 0.2s ease;
            }
            
            .voice-save-btn:hover {
                transform: translateY(-1px);
                box-shadow: 0 4px 12px rgba(34, 197, 94, 0.3);
            }
            
            .voice-cancel-btn,
            .voice-retry-btn {
                background: #f3f4f6;
                color: #374151;
                border: 1px solid #d1d5db;
                border-radius: 6px;
                padding: 10px 20px;
                font-size: 14px;
                font-weight: 500;
                cursor: pointer;
                transition: all 0.2s ease;
            }
            
            .voice-cancel-btn:hover,
            .voice-retry-btn:hover {
                background: #e5e7eb;
            }
            
            .voice-error-section {
                text-align: center;
                padding: 40px 20px;
            }
            
            .voice-error-message {
                background: #fef2f2;
                border: 1px solid #fecaca;
                border-radius: 8px;
                padding: 16px;
                color: #dc2626;
                margin-bottom: 16px;
            }
            
            @keyframes fadeIn {
                from { opacity: 0; }
                to { opacity: 1; }
            }
            
            @keyframes slideUp {
                from { transform: translateY(20px); opacity: 0; }
                to { transform: translateY(0); opacity: 1; }
            }
            
            @keyframes pulse {
                0% { transform: scale(1); }
                50% { transform: scale(1.05); }
                100% { transform: scale(1); }
            }
            
            @media (max-width: 640px) {
                .voice-modal {
                    width: 95%;
                    margin: 20px;
                }
                
                .voice-modal-content {
                    padding: 20px;
                }
                
                .voice-preview-actions {
                    flex-direction: column;
                }
            }
        `;
        
        const styleSheet = document.createElement('style');
        styleSheet.id = styleId;
        styleSheet.textContent = styles;
        document.head.appendChild(styleSheet);
    }
    
    setupSpeechRecognition() {
        if (!('webkitSpeechRecognition' in window) && !('SpeechRecognition' in window)) {
            this.showError('Speech recognition is not supported in this browser.');
            return;
        }
        
        const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
        this.recognition = new SpeechRecognition();
        
        this.recognition.continuous = false;
        this.recognition.interimResults = true;
        this.recognition.lang = 'en-US';
        
        this.recognition.onstart = () => {
            this.isRecording = true;
            this.updateStatus('Listening...', 'recording');
            this.showTranscriptSection();
        };
        
        this.recognition.onresult = (event) => {
            let interimTranscript = '';
            let finalTranscript = '';
            
            for (let i = event.resultIndex; i < event.results.length; i++) {
                const transcript = event.results[i][0].transcript;
                if (event.results[i].isFinal) {
                    finalTranscript += transcript;
                } else {
                    interimTranscript += transcript;
                }
            }
            
            this.transcript = finalTranscript || interimTranscript;
            this.updateTranscriptDisplay();
        };
        
        this.recognition.onerror = (event) => {
            console.error('Speech recognition error:', event.error);
            this.stopRecording();
            this.showError('Voice recognition failed. Please try again.');
        };
        
        this.recognition.onend = () => {
            this.stopRecording();
            if (this.transcript) {
                this.processTranscript();
            }
        };
    }
    
    bindEvents() {
        // Close button
        this.modal.querySelector('.voice-modal-close').addEventListener('click', () => {
            this.close();
        });
        
        // Record button
        this.modal.querySelector('.voice-record-btn').addEventListener('click', () => {
            if (this.isRecording) {
                this.stopRecording();
            } else {
                this.startRecording();
            }
        });
        
        // Retry button
        this.modal.querySelectorAll('.voice-retry-btn').forEach(btn => {
            btn.addEventListener('click', () => {
                this.reset();
            });
        });
        
        // Save button
        this.modal.querySelector('.voice-save-btn').addEventListener('click', () => {
            this.saveExpense();
        });
        
        // Cancel button
        this.modal.querySelector('.voice-cancel-btn').addEventListener('click', () => {
            this.close();
        });
        
        // Close on overlay click
        this.modal.addEventListener('click', (e) => {
            if (e.target === this.modal) {
                this.close();
            }
        });
    }
    
    startRecording() {
        this.transcript = '';
        this.parsedData = null;
        this.reset();
        
        if (this.recognition) {
            this.recognition.start();
        }
    }
    
    stopRecording() {
        if (this.recognition) {
            this.recognition.stop();
        }
        this.isRecording = false;
        this.updateStatus('Click to start recording', 'idle');
    }
    
    updateStatus(text, state = 'idle') {
        const statusText = this.modal.querySelector('.voice-status-text');
        const recordBtn = this.modal.querySelector('.voice-record-btn');
        const statusIcon = this.modal.querySelector('.voice-status-icon');
        
        statusText.textContent = text;
        
        if (state === 'recording') {
            recordBtn.textContent = 'Stop Recording';
            recordBtn.classList.add('recording');
            statusIcon.style.animation = 'pulse 1.5s infinite';
        } else {
            recordBtn.textContent = 'Start Recording';
            recordBtn.classList.remove('recording');
            statusIcon.style.animation = 'none';
        }
    }
    
    showTranscriptSection() {
        this.modal.querySelector('.voice-transcript-section').style.display = 'block';
        this.modal.querySelector('.voice-preview-section').style.display = 'none';
        this.modal.querySelector('.voice-error-section').style.display = 'none';
    }
    
    showPreviewSection() {
        this.modal.querySelector('.voice-transcript-section').style.display = 'none';
        this.modal.querySelector('.voice-preview-section').style.display = 'block';
        this.modal.querySelector('.voice-error-section').style.display = 'none';
    }
    
    showErrorSection() {
        this.modal.querySelector('.voice-transcript-section').style.display = 'none';
        this.modal.querySelector('.voice-preview-section').style.display = 'none';
        this.modal.querySelector('.voice-error-section').style.display = 'block';
    }
    
    updateTranscriptDisplay() {
        const display = this.modal.querySelector('.voice-transcript-display');
        display.textContent = this.transcript;
    }
    
    async processTranscript() {
        try {
            this.updateStatus('Processing...', 'processing');
            
            const response = await fetch(this.options.apiEndpoint, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    transcript: this.transcript,
                    source: 'dashboard_voice'
                })
            });
            
            const result = await response.json();
            
            if (result.success) {
                this.parsedData = result.expense;
                this.populateForm(result.expense);
                this.showPreviewSection();
            } else {
                this.showError(result.error, result.parsed);
            }
            
        } catch (error) {
            console.error('Voice processing error:', error);
            this.showError('Failed to process voice input. Please try again.');
        }
    }
    
    populateForm(expense) {
        this.modal.querySelector('.voice-amount-input').value = (expense.amount_cents / 100).toFixed(2);
        this.modal.querySelector('.voice-vendor-input').value = expense.vendor || '';
        this.modal.querySelector('.voice-job-input').value = expense.job_name || '';
        this.modal.querySelector('.voice-category-select').value = expense.category_name || '';
        this.modal.querySelector('.voice-description-input').value = expense.description || '';
    }
    
    async saveExpense() {
        try {
            const formData = {
                amount_cents: Math.round(parseFloat(this.modal.querySelector('.voice-amount-input').value) * 100),
                vendor: this.modal.querySelector('.voice-vendor-input').value,
                job_name: this.modal.querySelector('.voice-job-input').value,
                category_name: this.modal.querySelector('.voice-category-select').value,
                description: this.modal.querySelector('.voice-description-input').value
            };
            
            // Validate required fields
            if (!formData.amount_cents || !formData.vendor) {
                this.showError('Please fill in amount and vendor.');
                return;
            }
            
            // Send to API
            const response = await fetch('/api/expenses', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(formData)
            });
            
            const result = await response.json();
            
            if (response.ok) {
                this.showSuccess(result);
            } else {
                this.showError(result.detail || 'Failed to save expense.');
            }
            
        } catch (error) {
            console.error('Save expense error:', error);
            this.showError('Failed to save expense. Please try again.');
        }
    }
    
    showSuccess(expense) {
        // Create success notification
        const notification = document.createElement('div');
        notification.className = 'voice-success-notification';
        notification.innerHTML = `
            <div class="notification-content">
                <div class="notification-icon">✅</div>
                <div class="notification-text">
                    <strong>Expense Saved!</strong><br>
                    $${(expense.amount_cents / 100).toFixed(2)} - ${expense.vendor}
                    ${expense.job_name ? `<br><small>Job: ${expense.job_name}</small>` : ''}
                </div>
            </div>
        `;
        
        // Add notification styles
        this.addNotificationStyles();
        
        // Show notification
        document.body.appendChild(notification);
        
        // Auto-remove after 3 seconds
        setTimeout(() => {
            notification.remove();
        }, 3000);
        
        // Call success callback
        if (this.options.onSuccess) {
            this.options.onSuccess(expense);
        }
        
        // Close modal
        this.close();
    }
    
    showError(message, parsed = null) {
        this.showErrorSection();
        const errorMessage = this.modal.querySelector('.voice-error-message');
        errorMessage.textContent = message;
        
        if (parsed) {
            errorMessage.innerHTML += `<br><small>Detected: ${parsed.vendor || 'Unknown vendor'}</small>`;
        }
        
        // Call error callback
        if (this.options.onError) {
            this.options.onError(message, parsed);
        }
    }
    
    addNotificationStyles() {
        const styleId = 'voice-modal-notification-styles';
        if (document.getElementById(styleId)) return;
        
        const styles = `
            .voice-success-notification {
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
    
    reset() {
        this.transcript = '';
        this.parsedData = null;
        this.updateStatus('Click to start recording', 'idle');
        this.modal.querySelector('.voice-transcript-section').style.display = 'none';
        this.modal.querySelector('.voice-preview-section').style.display = 'none';
        this.modal.querySelector('.voice-error-section').style.display = 'none';
    }
    
    open() {
        this.modal.style.display = 'flex';
        document.body.style.overflow = 'hidden';
    }
    
    close() {
        this.modal.style.display = 'none';
        document.body.style.overflow = '';
        this.reset();
        
        if (this.options.onClose) {
            this.options.onClose();
        }
    }
    
    destroy() {
        if (this.recognition) {
            this.recognition.stop();
        }
        if (this.modal && this.modal.parentNode) {
            this.modal.parentNode.removeChild(this.modal);
        }
    }
}

// Export for use
if (typeof module !== 'undefined' && module.exports) {
    module.exports = VoiceModal;
} 