/**
 * Quick Tour Feature
 * Interactive tour for new contractors
 */

class QuickTour {
    constructor() {
        this.currentStep = 0;
        this.isActive = false;
        this.tourSteps = [
            {
                title: "Welcome to CORA!",
                description: "Let's take a quick tour of your new construction financial dashboard.",
                target: null,
                position: "center",
                action: "welcome"
            },
            {
                title: "Voice Expense Entry",
                description: "Try saying 'Home Depot receipt Johnson bathroom three forty seven' - it's that easy!",
                target: ".voice-btn",
                position: "bottom",
                action: "highlight_voice"
            },
            {
                title: "Job Profitability at a Glance",
                description: "See which jobs are making money instantly. Green = profitable, red = needs attention.",
                target: ".job-profitability-section",
                position: "top",
                action: "highlight_profitability"
            },
            {
                title: "Stay Informed with Alerts",
                description: "Get notified when job margins drop or budgets are exceeded.",
                target: ".alert-dropdown",
                position: "left",
                action: "highlight_alerts"
            },
            {
                title: "Track Your Success",
                description: "See how much time and money you're saving with CORA.",
                target: ".success-metrics-section",
                position: "top",
                action: "highlight_success"
            },
            {
                title: "You're All Set!",
                description: "Start by adding your first expense using the voice button or quick expense form.",
                target: null,
                position: "center",
                action: "complete"
            }
        ];
        
        this.init();
    }
    
    init() {
        this.createTourInterface();
        this.bindEvents();
    }
    
    createTourInterface() {
        // Create tour overlay
        this.tourOverlay = document.createElement('div');
        this.tourOverlay.className = 'quick-tour-overlay';
        this.tourOverlay.innerHTML = `
            <div class="tour-highlight" id="tourHighlight"></div>
            <div class="tour-tooltip" id="tourTooltip">
                <div class="tour-header">
                    <h3 id="tourTitle">Welcome to CORA!</h3>
                    <button class="tour-close" id="tourClose">✕</button>
                </div>
                <div class="tour-content">
                    <p id="tourDescription">Let's take a quick tour of your new construction financial dashboard.</p>
                </div>
                <div class="tour-actions">
                    <button class="tour-btn secondary" id="tourSkip">Skip Tour</button>
                    <button class="tour-btn primary" id="tourNext">Next</button>
                </div>
                <div class="tour-progress">
                    <div class="tour-progress-bar">
                        <div class="tour-progress-fill" id="tourProgressFill"></div>
                    </div>
                    <span class="tour-step-indicator">
                        <span id="tourStepNumber">1</span> / <span id="tourTotalSteps">6</span>
                    </span>
                </div>
            </div>
        `;
        
        // Add tour styles
        this.addTourStyles();
        
        // Add to page
        document.body.appendChild(this.tourOverlay);
        
        // Initially hidden
        this.tourOverlay.style.display = 'none';
    }
    
    addTourStyles() {
        const styleId = 'quick-tour-styles';
        if (document.getElementById(styleId)) return;
        
        const styles = `
            .quick-tour-overlay {
                position: fixed;
                top: 0;
                left: 0;
                right: 0;
                bottom: 0;
                z-index: 10000;
                pointer-events: none;
            }
            
            .tour-highlight {
                position: absolute;
                border: 3px solid #9B6EC8;
                border-radius: 8px;
                box-shadow: 0 0 0 9999px rgba(0, 0, 0, 0.5);
                pointer-events: none;
                z-index: 10001;
                animation: tour-pulse 2s infinite;
            }
            
            @keyframes tour-pulse {
                0%, 100% { box-shadow: 0 0 0 9999px rgba(0, 0, 0, 0.5), 0 0 0 0 rgba(155, 110, 200, 0.7); }
                50% { box-shadow: 0 0 0 9999px rgba(0, 0, 0, 0.5), 0 0 0 10px rgba(155, 110, 200, 0); }
            }
            
            .tour-tooltip {
                position: absolute;
                background: white;
                border-radius: 12px;
                box-shadow: 0 10px 25px rgba(0, 0, 0, 0.15);
                border: 1px solid #e5e7eb;
                max-width: 350px;
                pointer-events: auto;
                z-index: 10002;
                animation: tour-slide-in 0.3s ease;
            }
            
            @keyframes tour-slide-in {
                from { opacity: 0; transform: translateY(10px); }
                to { opacity: 1; transform: translateY(0); }
            }
            
            .tour-header {
                padding: 16px 20px 0 20px;
                display: flex;
                justify-content: space-between;
                align-items: flex-start;
            }
            
            .tour-header h3 {
                margin: 0;
                font-size: 1.125rem;
                font-weight: 600;
                color: #374151;
            }
            
            .tour-close {
                background: none;
                border: none;
                font-size: 18px;
                color: #9ca3af;
                cursor: pointer;
                padding: 4px;
                border-radius: 4px;
                transition: all 0.2s ease;
            }
            
            .tour-close:hover {
                background: #f3f4f6;
                color: #6b7280;
            }
            
            .tour-content {
                padding: 0 20px 16px 20px;
            }
            
            .tour-content p {
                margin: 0;
                font-size: 0.875rem;
                line-height: 1.5;
                color: #6b7280;
            }
            
            .tour-actions {
                padding: 0 20px 16px 20px;
                display: flex;
                gap: 12px;
                justify-content: flex-end;
            }
            
            .tour-btn {
                padding: 8px 16px;
                border: none;
                border-radius: 6px;
                font-size: 0.875rem;
                font-weight: 500;
                cursor: pointer;
                transition: all 0.2s ease;
            }
            
            .tour-btn.primary {
                background: #9B6EC8;
                color: white;
            }
            
            .tour-btn.primary:hover {
                background: #7C3AED;
                transform: translateY(-1px);
            }
            
            .tour-btn.secondary {
                background: #f3f4f6;
                color: #374151;
            }
            
            .tour-btn.secondary:hover {
                background: #e5e7eb;
            }
            
            .tour-progress {
                padding: 0 20px 16px 20px;
                display: flex;
                align-items: center;
                gap: 12px;
            }
            
            .tour-progress-bar {
                flex: 1;
                height: 4px;
                background: #e5e7eb;
                border-radius: 2px;
                overflow: hidden;
            }
            
            .tour-progress-fill {
                height: 100%;
                background: #9B6EC8;
                border-radius: 2px;
                transition: width 0.3s ease;
                width: 0%;
            }
            
            .tour-step-indicator {
                font-size: 0.75rem;
                color: #9ca3af;
                font-weight: 500;
                min-width: 30px;
                text-align: center;
            }
            
            /* Tour trigger button */
            .tour-trigger-btn {
                position: fixed;
                bottom: 140px;
                right: 20px;
                background: linear-gradient(135deg, #10b981, #059669);
                color: white;
                border: none;
                border-radius: 50px;
                padding: 12px 20px;
                font-size: 14px;
                font-weight: 600;
                cursor: pointer;
                box-shadow: 0 4px 12px rgba(16, 185, 129, 0.3);
                transition: all 0.3s ease;
                z-index: 1000;
            }
            
            .tour-trigger-btn:hover {
                transform: translateY(-2px);
                box-shadow: 0 6px 20px rgba(16, 185, 129, 0.4);
            }
            
            @media (max-width: 768px) {
                .tour-tooltip {
                    max-width: 300px;
                    margin: 20px;
                }
                
                .tour-header {
                    padding: 12px 16px 0 16px;
                }
                
                .tour-content {
                    padding: 0 16px 12px 16px;
                }
                
                .tour-actions {
                    padding: 0 16px 12px 16px;
                }
                
                .tour-progress {
                    padding: 0 16px 12px 16px;
                }
            }
        `;
        
        const styleSheet = document.createElement('style');
        styleSheet.id = styleId;
        styleSheet.textContent = styles;
        document.head.appendChild(styleSheet);
    }
    
    bindEvents() {
        // Close button
        document.getElementById('tourClose').addEventListener('click', () => {
            this.completeTour();
        });
        
        // Skip button
        document.getElementById('tourSkip').addEventListener('click', () => {
            this.completeTour();
        });
        
        // Next button
        document.getElementById('tourNext').addEventListener('click', () => {
            this.nextStep();
        });
    }
    
    startTour() {
        this.isActive = true;
        this.currentStep = 0;
        this.tourOverlay.style.display = 'block';
        this.showStep();
    }
    
    completeTour() {
        this.isActive = false;
        this.tourOverlay.style.display = 'none';
        this.clearHighlight();
        
        // Mark tour as completed
        localStorage.setItem('cora_tour_completed', 'true');
        
        // Track completion
        this.trackTourCompletion();
    }
    
    nextStep() {
        this.currentStep++;
        
        if (this.currentStep >= this.tourSteps.length) {
            this.completeTour();
            return;
        }
        
        this.showStep();
    }
    
    showStep() {
        const step = this.tourSteps[this.currentStep];
        
        // Update tooltip content
        document.getElementById('tourTitle').textContent = step.title;
        document.getElementById('tourDescription').textContent = step.description;
        document.getElementById('tourStepNumber').textContent = this.currentStep + 1;
        document.getElementById('tourTotalSteps').textContent = this.tourSteps.length;
        
        // Update progress bar
        const progress = ((this.currentStep + 1) / this.tourSteps.length) * 100;
        document.getElementById('tourProgressFill').style.width = `${progress}%`;
        
        // Update next button text
        const nextBtn = document.getElementById('tourNext');
        if (this.currentStep === this.tourSteps.length - 1) {
            nextBtn.textContent = 'Finish';
        } else {
            nextBtn.textContent = 'Next';
        }
        
        // Position tooltip and highlight
        this.positionTooltip(step);
        this.highlightElement(step);
    }
    
    positionTooltip(step) {
        const tooltip = document.getElementById('tourTooltip');
        
        if (!step.target) {
            // Center tooltip for welcome/complete steps
            tooltip.style.left = '50%';
            tooltip.style.top = '50%';
            tooltip.style.transform = 'translate(-50%, -50%)';
            return;
        }
        
        const targetElement = document.querySelector(step.target);
        if (!targetElement) {
            // Fallback to center if target not found
            tooltip.style.left = '50%';
            tooltip.style.top = '50%';
            tooltip.style.transform = 'translate(-50%, -50%)';
            return;
        }
        
        const rect = targetElement.getBoundingClientRect();
        const tooltipRect = tooltip.getBoundingClientRect();
        
        let left, top;
        
        switch (step.position) {
            case 'top':
                left = rect.left + rect.width / 2 - tooltipRect.width / 2;
                top = rect.top - tooltipRect.height - 20;
                break;
            case 'bottom':
                left = rect.left + rect.width / 2 - tooltipRect.width / 2;
                top = rect.bottom + 20;
                break;
            case 'left':
                left = rect.left - tooltipRect.width - 20;
                top = rect.top + rect.height / 2 - tooltipRect.height / 2;
                break;
            case 'right':
                left = rect.right + 20;
                top = rect.top + rect.height / 2 - tooltipRect.height / 2;
                break;
            default:
                left = rect.left + rect.width / 2 - tooltipRect.width / 2;
                top = rect.top - tooltipRect.height - 20;
        }
        
        // Ensure tooltip stays within viewport
        left = Math.max(20, Math.min(left, window.innerWidth - tooltipRect.width - 20));
        top = Math.max(20, Math.min(top, window.innerHeight - tooltipRect.height - 20));
        
        tooltip.style.left = `${left}px`;
        tooltip.style.top = `${top}px`;
        tooltip.style.transform = 'none';
    }
    
    highlightElement(step) {
        const highlight = document.getElementById('tourHighlight');
        
        if (!step.target) {
            this.clearHighlight();
            return;
        }
        
        const targetElement = document.querySelector(step.target);
        if (!targetElement) {
            this.clearHighlight();
            return;
        }
        
        const rect = targetElement.getBoundingClientRect();
        
        highlight.style.left = `${rect.left - 10}px`;
        highlight.style.top = `${rect.top - 10}px`;
        highlight.style.width = `${rect.width + 20}px`;
        highlight.style.height = `${rect.height + 20}px`;
        highlight.style.display = 'block';
        
        // Execute action if specified
        this.executeAction(step.action);
    }
    
    clearHighlight() {
        const highlight = document.getElementById('tourHighlight');
        highlight.style.display = 'none';
    }
    
    executeAction(action) {
        switch (action) {
            case 'highlight_voice':
                // Could add special animation for voice button
                break;
            case 'highlight_profitability':
                // Could scroll to profitability section
                break;
            case 'highlight_alerts':
                // Could show alert panel briefly
                break;
            case 'highlight_success':
                // Could add success animation
                break;
        }
    }
    
    trackTourCompletion() {
        // Send analytics event
        if (typeof gtag !== 'undefined') {
            gtag('event', 'tour_completed', {
                event_category: 'onboarding',
                event_label: 'quick_tour'
            });
        }
        
        // Could also send to backend
        fetch('/api/onboarding/complete-step/tour', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                step: 'tour_completed',
                timestamp: new Date().toISOString()
            })
        }).catch(error => {
            // console.error('Error tracking tour completion:', error);
        });
    }
    
    // Static method to check if tour should be shown
    static shouldShowTour() {
        return !localStorage.getItem('cora_tour_completed');
    }
    
    // Static method to create tour trigger button
    static createTourTrigger() {
        const triggerBtn = document.createElement('button');
        triggerBtn.className = 'tour-trigger-btn';
        triggerBtn.innerHTML = '🎯 Quick Tour';
        triggerBtn.onclick = () => {
            const tour = new QuickTour();
            tour.startTour();
        };
        
        document.body.appendChild(triggerBtn);
        return triggerBtn;
    }
}

// Export for use
if (typeof module !== 'undefined' && module.exports) {
    module.exports = QuickTour;
} 