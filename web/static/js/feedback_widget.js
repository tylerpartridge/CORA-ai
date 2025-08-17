/**
 * Feedback Widget for Beta Contractors
 * Quick, easy way to collect feedback while using the app
 */

class FeedbackWidget {
    constructor() {
        this.isOpen = false;
        this.feedbackType = 'general';
        this.init();
    }

    init() {
        // Create the widget HTML
        this.createWidget();
        
        // Add event listeners
        this.setupEventListeners();
        
        // Load any pending feedback
        this.loadPendingFeedback();
    }

    createWidget() {
        // Create widget container
        const widgetHTML = `
            <div id="feedback-widget" class="feedback-widget">
                <!-- Floating button -->
                <button id="feedback-toggle" class="feedback-toggle">
                    <span class="feedback-icon">💬</span>
                    <span class="feedback-text">Feedback</span>
                </button>
                
                <!-- Feedback panel -->
                <div id="feedback-panel" class="feedback-panel hidden">
                    <div class="feedback-header">
                        <h3>Share Your Feedback</h3>
                        <button id="feedback-close" class="feedback-close">&times;</button>
                    </div>
                    
                    <div class="feedback-body">
                        <!-- Quick feedback types -->
                        <div class="feedback-types">
                            <button class="feedback-type-btn active" data-type="praise">
                                😊 What's Working
                            </button>
                            <button class="feedback-type-btn" data-type="improvement">
                                💡 Improvement Idea
                            </button>
                            <button class="feedback-type-btn" data-type="bug">
                                🐛 Report Bug
                            </button>
                            <button class="feedback-type-btn" data-type="feature">
                                ✨ Feature Request
                            </button>
                        </div>
                        
                        <!-- Feedback form -->
                        <form id="feedback-form" class="feedback-form">
                            <div id="feedback-questions" class="feedback-questions">
                                <!-- Dynamic questions based on type -->
                            </div>
                            
                            <textarea 
                                id="feedback-message" 
                                class="feedback-message" 
                                placeholder="Tell us more..."
                                rows="4"
                                required
                            ></textarea>
                            
                            <div class="feedback-actions">
                                <button type="submit" class="btn-submit-feedback">
                                    Send Feedback
                                </button>
                                <span class="feedback-status"></span>
                            </div>
                        </form>
                        
                        <!-- Success message -->
                        <div id="feedback-success" class="feedback-success hidden">
                            <div class="success-icon">✅</div>
                            <h4>Thanks for your feedback!</h4>
                            <p>We read every message and use your input to improve CORA.</p>
                            <button id="feedback-another" class="btn-another">
                                Send Another
                            </button>
                        </div>
                    </div>
                </div>
            </div>
        `;
        
        // Add to page
        document.body.insertAdjacentHTML('beforeend', widgetHTML);
        
        // Add styles
        this.addStyles();
    }

    addStyles() {
        const styles = `
            <style>
            .feedback-widget {
                position: fixed;
                bottom: 20px;
                right: 20px;
                z-index: 9999;
            }
            
            .feedback-toggle {
                background: #9B6EC8;
                color: white;
                border: none;
                border-radius: 25px;
                padding: 12px 24px;
                font-size: 16px;
                font-weight: 500;
                cursor: pointer;
                box-shadow: 0 4px 12px rgba(0,0,0,0.15);
                display: flex;
                align-items: center;
                gap: 8px;
                transition: all 0.3s ease;
            }
            
            .feedback-toggle:hover {
                background: #8B5CB8;
                transform: translateY(-2px);
                box-shadow: 0 6px 16px rgba(0,0,0,0.2);
            }
            
            .feedback-panel {
                position: absolute;
                bottom: 70px;
                right: 0;
                width: 380px;
                background: white;
                border-radius: 12px;
                box-shadow: 0 10px 40px rgba(0,0,0,0.15);
                transform-origin: bottom right;
                transition: all 0.3s ease;
            }
            
            .feedback-panel.hidden {
                opacity: 0;
                transform: scale(0.8);
                pointer-events: none;
            }
            
            .feedback-header {
                padding: 20px;
                border-bottom: 1px solid #e5e7eb;
                display: flex;
                justify-content: space-between;
                align-items: center;
            }
            
            .feedback-header h3 {
                margin: 0;
                font-size: 18px;
                color: #1f2937;
            }
            
            .feedback-close {
                background: none;
                border: none;
                font-size: 24px;
                color: #6b7280;
                cursor: pointer;
                width: 32px;
                height: 32px;
                display: flex;
                align-items: center;
                justify-content: center;
                border-radius: 6px;
                transition: all 0.2s;
            }
            
            .feedback-close:hover {
                background: #f3f4f6;
                color: #1f2937;
            }
            
            .feedback-body {
                padding: 20px;
            }
            
            .feedback-types {
                display: grid;
                grid-template-columns: 1fr 1fr;
                gap: 8px;
                margin-bottom: 20px;
            }
            
            .feedback-type-btn {
                background: #f3f4f6;
                border: 2px solid transparent;
                border-radius: 8px;
                padding: 10px 12px;
                font-size: 14px;
                cursor: pointer;
                transition: all 0.2s;
                text-align: left;
            }
            
            .feedback-type-btn:hover {
                background: #e5e7eb;
            }
            
            .feedback-type-btn.active {
                background: #f3f4fb;
                border-color: #9B6EC8;
                color: #9B6EC8;
            }
            
            .feedback-questions {
                margin-bottom: 16px;
            }
            
            .feedback-question {
                margin-bottom: 12px;
            }
            
            .feedback-question label {
                display: block;
                font-size: 14px;
                color: #374151;
                margin-bottom: 4px;
            }
            
            .feedback-question select,
            .feedback-question input {
                width: 100%;
                padding: 8px 12px;
                border: 1px solid #d1d5db;
                border-radius: 6px;
                font-size: 14px;
            }
            
            .feedback-message {
                width: 100%;
                padding: 12px;
                border: 1px solid #d1d5db;
                border-radius: 8px;
                font-size: 14px;
                resize: none;
                font-family: inherit;
            }
            
            .feedback-message:focus {
                outline: none;
                border-color: #9B6EC8;
                box-shadow: 0 0 0 3px rgba(155, 110, 200, 0.1);
            }
            
            .feedback-actions {
                margin-top: 16px;
                display: flex;
                align-items: center;
                justify-content: space-between;
            }
            
            .btn-submit-feedback {
                background: #9B6EC8;
                color: white;
                border: none;
                border-radius: 6px;
                padding: 10px 20px;
                font-size: 14px;
                font-weight: 500;
                cursor: pointer;
                transition: all 0.2s;
            }
            
            .btn-submit-feedback:hover {
                background: #8B5CB8;
            }
            
            .btn-submit-feedback:disabled {
                opacity: 0.5;
                cursor: not-allowed;
            }
            
            .feedback-status {
                font-size: 13px;
                color: #6b7280;
            }
            
            .feedback-success {
                text-align: center;
                padding: 20px;
            }
            
            .success-icon {
                font-size: 48px;
                margin-bottom: 16px;
            }
            
            .feedback-success h4 {
                margin: 0 0 8px 0;
                font-size: 18px;
                color: #1f2937;
            }
            
            .feedback-success p {
                margin: 0 0 20px 0;
                color: #6b7280;
            }
            
            .btn-another {
                background: #f3f4f6;
                border: none;
                border-radius: 6px;
                padding: 8px 16px;
                font-size: 14px;
                cursor: pointer;
                transition: all 0.2s;
            }
            
            .btn-another:hover {
                background: #e5e7eb;
            }
            
            /* Mobile responsiveness */
            @media (max-width: 640px) {
                .feedback-panel {
                    width: calc(100vw - 40px);
                    max-width: 380px;
                }
                
                .feedback-types {
                    grid-template-columns: 1fr;
                }
            }
            
            /* Rating stars */
            .star-rating {
                display: flex;
                gap: 4px;
                margin-top: 4px;
            }
            
            .star {
                font-size: 24px;
                color: #d1d5db;
                cursor: pointer;
                transition: color 0.2s;
            }
            
            .star:hover,
            .star.active {
                color: #fbbf24;
            }
            </style>
        `;
        
        document.head.insertAdjacentHTML('beforeend', styles);
    }

    setupEventListeners() {
        // Toggle button
        document.getElementById('feedback-toggle').addEventListener('click', () => {
            this.togglePanel();
        });
        
        // Close button
        document.getElementById('feedback-close').addEventListener('click', () => {
            this.closePanel();
        });
        
        // Feedback type buttons
        document.querySelectorAll('.feedback-type-btn').forEach(btn => {
            btn.addEventListener('click', (e) => {
                this.selectFeedbackType(e.target.dataset.type);
            });
        });
        
        // Form submission
        document.getElementById('feedback-form').addEventListener('submit', (e) => {
            e.preventDefault();
            this.submitFeedback();
        });
        
        // Another feedback button
        document.getElementById('feedback-another').addEventListener('click', () => {
            this.resetForm();
        });
        
        // Close on escape
        document.addEventListener('keydown', (e) => {
            if (e.key === 'Escape' && this.isOpen) {
                this.closePanel();
            }
        });
    }

    togglePanel() {
        this.isOpen = !this.isOpen;
        const panel = document.getElementById('feedback-panel');
        
        if (this.isOpen) {
            panel.classList.remove('hidden');
            document.getElementById('feedback-message').focus();
        } else {
            panel.classList.add('hidden');
        }
    }

    closePanel() {
        this.isOpen = false;
        document.getElementById('feedback-panel').classList.add('hidden');
    }

    selectFeedbackType(type) {
        this.feedbackType = type;
        
        // Update active button
        document.querySelectorAll('.feedback-type-btn').forEach(btn => {
            btn.classList.toggle('active', btn.dataset.type === type);
        });
        
        // Update questions based on type
        this.updateQuestions(type);
    }

    updateQuestions(type) {
        const questionsContainer = document.getElementById('feedback-questions');
        let questionsHTML = '';
        
        switch(type) {
            case 'praise':
                questionsHTML = `
                    <div class="feedback-question">
                        <label>What feature do you love most?</label>
                        <select name="favorite_feature">
                            <option value="">Select a feature...</option>
                            <option value="voice_entry">Voice expense entry</option>
                            <option value="job_tracking">Job profitability tracking</option>
                            <option value="dashboard">Dashboard overview</option>
                            <option value="mobile">Mobile experience</option>
                            <option value="other">Other</option>
                        </select>
                    </div>
                    <div class="feedback-question">
                        <label>How much time does CORA save you weekly?</label>
                        <select name="time_saved">
                            <option value="">Select time...</option>
                            <option value="<30min">Less than 30 minutes</option>
                            <option value="30-60min">30-60 minutes</option>
                            <option value="1-2hrs">1-2 hours</option>
                            <option value="2-4hrs">2-4 hours</option>
                            <option value=">4hrs">More than 4 hours</option>
                        </select>
                    </div>
                `;
                break;
                
            case 'improvement':
                questionsHTML = `
                    <div class="feedback-question">
                        <label>Which area needs improvement?</label>
                        <select name="improvement_area">
                            <option value="">Select area...</option>
                            <option value="voice_accuracy">Voice recognition accuracy</option>
                            <option value="speed">App speed</option>
                            <option value="ui">User interface</option>
                            <option value="features">Missing features</option>
                            <option value="mobile">Mobile experience</option>
                        </select>
                    </div>
                `;
                break;
                
            case 'bug':
                questionsHTML = `
                    <div class="feedback-question">
                        <label>Where did you encounter the bug?</label>
                        <input type="text" name="bug_location" placeholder="e.g., Dashboard, Voice entry...">
                    </div>
                    <div class="feedback-question">
                        <label>How often does this happen?</label>
                        <select name="bug_frequency">
                            <option value="">Select frequency...</option>
                            <option value="always">Every time</option>
                            <option value="often">Often</option>
                            <option value="sometimes">Sometimes</option>
                            <option value="once">Just once</option>
                        </select>
                    </div>
                `;
                break;
                
            case 'feature':
                questionsHTML = `
                    <div class="feedback-question">
                        <label>How would this help your business?</label>
                        <input type="text" name="business_impact" placeholder="e.g., Save time on invoicing...">
                    </div>
                    <div class="feedback-question">
                        <label>How important is this feature?</label>
                        <div class="star-rating" data-rating="0">
                            <span class="star" data-value="1">★</span>
                            <span class="star" data-value="2">★</span>
                            <span class="star" data-value="3">★</span>
                            <span class="star" data-value="4">★</span>
                            <span class="star" data-value="5">★</span>
                        </div>
                        <input type="hidden" name="importance" value="0">
                    </div>
                `;
                break;
        }
        
        questionsContainer.innerHTML = questionsHTML;
        
        // Setup star rating if present
        this.setupStarRating();
    }

    setupStarRating() {
        const starContainer = document.querySelector('.star-rating');
        if (!starContainer) return;
        
        const stars = starContainer.querySelectorAll('.star');
        const importanceInput = document.querySelector('input[name="importance"]');
        
        stars.forEach((star, index) => {
            star.addEventListener('click', () => {
                const rating = index + 1;
                starContainer.dataset.rating = rating;
                importanceInput.value = rating;
                
                // Update star appearance
                stars.forEach((s, i) => {
                    s.classList.toggle('active', i < rating);
                });
            });
            
            star.addEventListener('mouseenter', () => {
                stars.forEach((s, i) => {
                    s.classList.toggle('active', i <= index);
                });
            });
        });
        
        starContainer.addEventListener('mouseleave', () => {
            const rating = parseInt(starContainer.dataset.rating);
            stars.forEach((s, i) => {
                s.classList.toggle('active', i < rating);
            });
        });
    }

    async submitFeedback() {
        const form = document.getElementById('feedback-form');
        const submitBtn = form.querySelector('.btn-submit-feedback');
        const status = form.querySelector('.feedback-status');
        
        // Disable submit button
        submitBtn.disabled = true;
        submitBtn.textContent = 'Sending...';
        status.textContent = '';
        
        // Collect form data
        const formData = new FormData(form);
        const message = document.getElementById('feedback-message').value;
        
        // Build feedback data
        const feedbackData = {
            category: this.feedbackType,
            title: this.getTitleForType(this.feedbackType, message),
            description: this.buildDescription(formData, message),
            priority: this.getPriorityForType(this.feedbackType),
            user_agent: navigator.userAgent,
            page_url: window.location.href,
            browser_info: {
                screen: `${window.screen.width}x${window.screen.height}`,
                viewport: `${window.innerWidth}x${window.innerHeight}`,
                platform: navigator.platform
            }
        };
        
        try {
            const response = await fetch('/api/feedback/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${localStorage.getItem('access_token')}`
                },
                body: JSON.stringify(feedbackData)
            });
            
            if (response.ok) {
                // Show success
                this.showSuccess();
                
                // Track in analytics if available
                if (window.gtag) {
                    window.gtag('event', 'feedback_submitted', {
                        'feedback_type': this.feedbackType
                    });
                }
            } else {
                throw new Error('Failed to submit feedback');
            }
        } catch (error) {
            // console.error('Feedback submission error:', error);
            status.textContent = 'Failed to send. Please try again.';
            status.style.color = '#dc2626';
        } finally {
            submitBtn.disabled = false;
            submitBtn.textContent = 'Send Feedback';
        }
    }

    getTitleForType(type, message) {
        const preview = message.substring(0, 50);
        switch(type) {
            case 'praise':
                return `Positive feedback: ${preview}...`;
            case 'improvement':
                return `Improvement suggestion: ${preview}...`;
            case 'bug':
                return `Bug report: ${preview}...`;
            case 'feature':
                return `Feature request: ${preview}...`;
            default:
                return `Feedback: ${preview}...`;
        }
    }

    buildDescription(formData, message) {
        let description = message + '\n\n';
        
        // Add form fields
        for (let [key, value] of formData.entries()) {
            if (value && key !== 'message') {
                description += `${key.replace(/_/g, ' ')}: ${value}\n`;
            }
        }
        
        return description.trim();
    }

    getPriorityForType(type) {
        switch(type) {
            case 'bug':
                return 'high';
            case 'feature':
                return 'medium';
            default:
                return 'low';
        }
    }

    showSuccess() {
        document.getElementById('feedback-form').classList.add('hidden');
        document.getElementById('feedback-success').classList.remove('hidden');
    }

    resetForm() {
        // Reset form
        document.getElementById('feedback-form').reset();
        document.getElementById('feedback-form').classList.remove('hidden');
        document.getElementById('feedback-success').classList.add('hidden');
        
        // Reset to default type
        this.selectFeedbackType('praise');
    }

    loadPendingFeedback() {
        // Check if there's any unsaved feedback in localStorage
        const pendingFeedback = localStorage.getItem('pending_feedback');
        if (pendingFeedback) {
            const data = JSON.parse(pendingFeedback);
            document.getElementById('feedback-message').value = data.message || '';
            this.selectFeedbackType(data.type || 'general');
            
            // Clear pending feedback
            localStorage.removeItem('pending_feedback');
            
            // Open panel
            this.togglePanel();
        }
    }

    savePendingFeedback() {
        // Save current feedback to localStorage before page unload
        const message = document.getElementById('feedback-message').value;
        if (message && message.trim()) {
            localStorage.setItem('pending_feedback', JSON.stringify({
                type: this.feedbackType,
                message: message
            }));
        }
    }
}

// Initialize widget when DOM is ready
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', () => {
        window.feedbackWidget = new FeedbackWidget();
    });
} else {
    window.feedbackWidget = new FeedbackWidget();
}

// Save pending feedback on page unload
window.addEventListener('beforeunload', () => {
    if (window.feedbackWidget) {
        window.feedbackWidget.savePendingFeedback();
    }
});