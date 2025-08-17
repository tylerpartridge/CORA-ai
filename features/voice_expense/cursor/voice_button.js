/**
 * Voice Button Component for Dashboard
 * Provides quick voice expense entry functionality
 */

class VoiceButton {
    constructor(container, options = {}) {
        this.container = container;
        this.options = {
            apiEndpoint: '/api/expenses/voice',
            onSuccess: null,
            onError: null,
            ...options
        };
        
        this.isRecording = false;
        this.recognition = null;
        this.init();
    }
    
    init() {
        this.createButton();
        this.setupSpeechRecognition();
        this.bindEvents();
    }
    
    createButton() {
        // Create voice button HTML
        this.button = document.createElement('button');
        this.button.className = 'voice-btn';
        this.button.innerHTML = `
            <div class="voice-btn-content">
                <div class="voice-icon">🎤</div>
                <div class="voice-label">Quick Voice Entry</div>
            </div>
            <div class="voice-pulse" style="display: none;"></div>
        `;
        
        // Add to container
        this.container.appendChild(this.button);
        
        // Add CSS styles
        this.addStyles();
    }
    
    addStyles() {
        const styleId = 'voice-button-styles';
        if (document.getElementById(styleId)) return;
        
        const styles = `
            .voice-btn {
                position: relative;
                background: linear-gradient(135deg, #9B6EC8, #7C3AED);
                color: white;
                border: none;
                border-radius: 50px;
                padding: 12px 20px;
                font-weight: 600;
                cursor: pointer;
                transition: all 0.3s ease;
                box-shadow: 0 4px 12px rgba(155, 110, 200, 0.3);
                display: flex;
                align-items: center;
                gap: 8px;
                font-family: 'Inter', sans-serif;
            }
            
            .voice-btn:hover {
                transform: translateY(-2px);
                box-shadow: 0 6px 20px rgba(155, 110, 200, 0.4);
            }
            
            .voice-btn.recording {
                background: linear-gradient(135deg, #ef4444, #dc2626);
                animation: voice-pulse 1.5s infinite;
            }
            
            .voice-btn-content {
                display: flex;
                align-items: center;
                gap: 8px;
            }
            
            .voice-icon {
                font-size: 18px;
                transition: transform 0.3s ease;
            }
            
            .voice-btn.recording .voice-icon {
                transform: scale(1.2);
            }
            
            .voice-label {
                font-size: 14px;
                white-space: nowrap;
            }
            
            .voice-pulse {
                position: absolute;
                top: 50%;
                left: 50%;
                transform: translate(-50%, -50%);
                width: 100%;
                height: 100%;
                border-radius: 50px;
                background: rgba(239, 68, 68, 0.3);
                animation: pulse 1.5s infinite;
            }
            
            @keyframes voice-pulse {
                0% { transform: translate(-50%, -50%) scale(1); opacity: 1; }
                100% { transform: translate(-50%, -50%) scale(1.5); opacity: 0; }
            }
            
            @keyframes pulse {
                0% { transform: translate(-50%, -50%) scale(1); opacity: 0.7; }
                100% { transform: translate(-50%, -50%) scale(1.3); opacity: 0; }
            }
            
            @media (max-width: 768px) {
                .voice-btn {
                    padding: 10px 16px;
                }
                
                .voice-label {
                    display: none;
                }
                
                .voice-btn::after {
                    content: "🎤";
                    font-size: 18px;
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
            console.warn('Speech recognition not supported');
            this.button.disabled = true;
            this.button.title = 'Speech recognition not supported in this browser';
            return;
        }
        
        const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
        this.recognition = new SpeechRecognition();
        
        this.recognition.continuous = false;
        this.recognition.interimResults = false;
        this.recognition.lang = 'en-US';
        
        this.recognition.onstart = () => {
            this.isRecording = true;
            this.button.classList.add('recording');
            this.button.querySelector('.voice-label').textContent = 'Listening...';
        };
        
        this.recognition.onresult = (event) => {
            const transcript = event.results[0][0].transcript;
            this.processTranscript(transcript);
        };
        
        this.recognition.onerror = (event) => {
            console.error('Speech recognition error:', event.error);
            this.stopRecording();
            this.showError('Voice recognition failed. Please try again.');
        };
        
        this.recognition.onend = () => {
            this.stopRecording();
        };
    }
    
    bindEvents() {
        this.button.addEventListener('click', () => {
            if (this.isRecording) {
                this.stopRecording();
            } else {
                this.startRecording();
            }
        });
    }
    
    startRecording() {
        if (this.recognition) {
            this.recognition.start();
        }
    }
    
    stopRecording() {
        if (this.recognition) {
            this.recognition.stop();
        }
        this.isRecording = false;
        this.button.classList.remove('recording');
        this.button.querySelector('.voice-label').textContent = 'Quick Voice Entry';
    }
    
    async processTranscript(transcript) {
        try {
            // Show processing state
            this.button.querySelector('.voice-label').textContent = 'Processing...';
            
            // Send to API
            const response = await fetch(this.options.apiEndpoint, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    transcript: transcript,
                    source: 'dashboard_voice'
                })
            });
            
            const result = await response.json();
            
            if (result.success) {
                this.showSuccess(result.expense);
            } else {
                this.showError(result.error, result.parsed);
            }
            
        } catch (error) {
            console.error('Voice processing error:', error);
            this.showError('Failed to process voice input. Please try again.');
        } finally {
            this.button.querySelector('.voice-label').textContent = 'Quick Voice Entry';
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
                    <strong>Expense Added!</strong><br>
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
    }
    
    showError(message, parsed = null) {
        // Create error notification
        const notification = document.createElement('div');
        notification.className = 'voice-error-notification';
        notification.innerHTML = `
            <div class="notification-content">
                <div class="notification-icon">❌</div>
                <div class="notification-text">
                    <strong>Voice Error</strong><br>
                    ${message}
                    ${parsed ? `<br><small>Detected: ${parsed.vendor || 'Unknown vendor'}</small>` : ''}
                </div>
            </div>
        `;
        
        // Add notification styles
        this.addNotificationStyles();
        
        // Show notification
        document.body.appendChild(notification);
        
        // Auto-remove after 5 seconds
        setTimeout(() => {
            notification.remove();
        }, 5000);
        
        // Call error callback
        if (this.options.onError) {
            this.options.onError(message, parsed);
        }
    }
    
    addNotificationStyles() {
        const styleId = 'voice-notification-styles';
        if (document.getElementById(styleId)) return;
        
        const styles = `
            .voice-success-notification,
            .voice-error-notification {
                position: fixed;
                top: 20px;
                right: 20px;
                background: white;
                border-radius: 8px;
                box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
                padding: 16px;
                z-index: 1000;
                animation: slideIn 0.3s ease;
                max-width: 300px;
            }
            
            .voice-success-notification {
                border-left: 4px solid #22c55e;
            }
            
            .voice-error-notification {
                border-left: 4px solid #ef4444;
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
        if (this.recognition) {
            this.recognition.stop();
        }
        if (this.button && this.button.parentNode) {
            this.button.parentNode.removeChild(this.button);
        }
    }
}

// Export for use
if (typeof module !== 'undefined' && module.exports) {
    module.exports = VoiceButton;
} 