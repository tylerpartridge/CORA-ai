/**
 * Voice Expense Entry System
 * Handles voice-to-text expense entry for contractors
 */

class VoiceExpenseEntry {
    constructor() {
        this.isRecording = false;
        this.recognition = null;
        this.init();
    }

    init() {
        this.setupSpeechRecognition();
        this.bindEvents();
    }

    setupSpeechRecognition() {
        if (!('webkitSpeechRecognition' in window) && !('SpeechRecognition' in window)) {
            // console.warn('Speech recognition not supported');
            return;
        }

        const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
        this.recognition = new SpeechRecognition();
        this.recognition.continuous = false;
        this.recognition.interimResults = false;
        this.recognition.lang = 'en-US';

        this.recognition.onstart = () => {
            this.isRecording = true;
            this.updateUI('listening');
        };

        this.recognition.onresult = (event) => {
            const transcript = event.results[0][0].transcript;
            this.processTranscript(transcript);
        };

        this.recognition.onerror = (event) => {
            // console.error('Speech recognition error:', event.error);
            this.updateUI('error');
        };

        this.recognition.onend = () => {
            this.isRecording = false;
            this.updateUI('ready');
        };
    }

    bindEvents() {
        const voiceBtn = document.querySelector('.voice-btn');
        if (voiceBtn) {
            voiceBtn.addEventListener('click', () => {
                if (this.isRecording) {
                    this.stopRecording();
                } else {
                    this.startRecording();
                }
            });
        }
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
    }

    async processTranscript(transcript) {
        try {
            this.updateUI('processing');
            
            const response = await fetch('/api/expenses/voice', {
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
                this.refreshDashboard();
            } else {
                this.showError(result.error);
            }

        } catch (error) {
            // console.error('Voice processing error:', error);
            this.showError('Failed to process voice input');
        } finally {
            this.updateUI('ready');
        }
    }

    updateUI(state) {
        const voiceBtn = document.querySelector('.voice-btn');
        if (!voiceBtn) return;

        const label = voiceBtn.querySelector('.voice-label');
        if (!label) return;

        switch (state) {
            case 'listening':
                label.textContent = 'Listening...';
                voiceBtn.classList.add('recording');
                break;
            case 'processing':
                label.textContent = 'Processing...';
                voiceBtn.classList.add('processing');
                break;
            case 'ready':
                label.textContent = 'Voice Entry';
                voiceBtn.classList.remove('recording', 'processing');
                break;
            case 'error':
                label.textContent = 'Error';
                voiceBtn.classList.remove('recording', 'processing');
                break;
        }
    }

    showSuccess(expense) {
        this.showNotification(`Expense added: $${(expense.amount_cents / 100).toFixed(2)} - ${expense.vendor}`, 'success');
    }

    showError(message) {
        this.showNotification(`Error: ${message}`, 'error');
    }

    showNotification(message, type) {
        const notification = document.createElement('div');
        notification.className = `voice-notification ${type}`;
        notification.textContent = message;
        notification.style.cssText = `
            position: fixed;
            top: 20px;
            right: 20px;
            background: ${type === 'success' ? '#22c55e' : '#ef4444'};
            color: white;
            padding: 12px 20px;
            border-radius: 8px;
            z-index: 1000;
            animation: slideIn 0.3s ease;
        `;

        document.body.appendChild(notification);

        setTimeout(() => {
            notification.remove();
        }, 3000);
    }

    refreshDashboard() {
        // Refresh dashboard data
        if (typeof loadTransactions === 'function') {
            loadTransactions();
        }
        if (typeof updateDashboardMetrics === 'function') {
            updateDashboardMetrics();
        }
    }
}

// Initialize voice expense entry
document.addEventListener('DOMContentLoaded', () => {
    new VoiceExpenseEntry();
});
