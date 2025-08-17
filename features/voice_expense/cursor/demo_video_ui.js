/**
 * Demo Video UI Component
 * Creates an interactive demo interface for showcasing features to beta contractors
 */

class DemoVideoUI {
    constructor() {
        this.currentStep = 0;
        this.isPlaying = false;
        this.demoSteps = [
            {
                title: "Welcome to CORA",
                subtitle: "Construction Financial Intelligence",
                description: "Track jobs, manage expenses, and monitor profitability with voice-powered expense entry.",
                action: "show_welcome",
                duration: 3000
            },
            {
                title: "Voice Expense Entry",
                subtitle: "Just speak your expenses",
                description: "Say 'Home Depot receipt Johnson bathroom three forty seven' and watch the magic happen.",
                action: "highlight_voice_button",
                duration: 4000
            },
            {
                title: "Job Profitability Dashboard",
                subtitle: "See your profits at a glance",
                description: "Real-time job profitability tracking with visual indicators and progress bars.",
                action: "highlight_profitability",
                duration: 4000
            },
            {
                title: "Construction Categories",
                subtitle: "Built for contractors",
                description: "Smart categorization for materials, labor, equipment, and permits.",
                action: "show_categories",
                duration: 3000
            },
            {
                title: "Mobile Optimized",
                subtitle: "Perfect for the job site",
                description: "Works seamlessly on phones and tablets - no more paper receipts!",
                action: "show_mobile",
                duration: 3000
            },
            {
                title: "Ready to Get Started?",
                subtitle: "Join the beta program",
                description: "Be among the first contractors to experience the future of construction financial management.",
                action: "show_cta",
                duration: 5000
            }
        ];
        
        this.init();
    }
    
    init() {
        this.createDemoInterface();
        this.bindEvents();
    }
    
    createDemoInterface() {
        // Create demo overlay
        this.demoOverlay = document.createElement('div');
        this.demoOverlay.className = 'demo-overlay';
        this.demoOverlay.innerHTML = `
            <div class="demo-container">
                <div class="demo-header">
                    <div class="demo-controls">
                        <button class="demo-btn demo-play" id="demoPlayBtn">▶️ Play Demo</button>
                        <button class="demo-btn demo-pause" id="demoPauseBtn" style="display: none;">⏸️ Pause</button>
                        <button class="demo-btn demo-restart" id="demoRestartBtn">🔄 Restart</button>
                        <button class="demo-btn demo-close" id="demoCloseBtn">✕ Close</button>
                    </div>
                    <div class="demo-progress">
                        <div class="demo-progress-bar">
                            <div class="demo-progress-fill" id="demoProgressFill"></div>
                        </div>
                        <div class="demo-step-indicator">
                            <span id="demoStepNumber">1</span> / <span id="demoTotalSteps">6</span>
                        </div>
                    </div>
                </div>
                
                <div class="demo-content">
                    <div class="demo-step" id="demoStep">
                        <h2 class="demo-title">Welcome to CORA</h2>
                        <h3 class="demo-subtitle">Construction Financial Intelligence</h3>
                        <p class="demo-description">Track jobs, manage expenses, and monitor profitability with voice-powered expense entry.</p>
                    </div>
                </div>
                
                <div class="demo-highlight" id="demoHighlight"></div>
            </div>
        `;
        
        // Add demo styles
        this.addDemoStyles();
        
        // Add to page
        document.body.appendChild(this.demoOverlay);
        
        // Initially hidden
        this.demoOverlay.style.display = 'none';
    }
    
    addDemoStyles() {
        const styleId = 'demo-video-styles';
        if (document.getElementById(styleId)) return;
        
        const styles = `
            .demo-overlay {
                position: fixed;
                top: 0;
                left: 0;
                right: 0;
                bottom: 0;
                background: rgba(0, 0, 0, 0.8);
                z-index: 9999;
                display: flex;
                align-items: center;
                justify-content: center;
                animation: fadeIn 0.3s ease;
            }
            
            .demo-container {
                background: white;
                border-radius: 16px;
                box-shadow: 0 25px 50px rgba(0, 0, 0, 0.25);
                width: 90%;
                max-width: 800px;
                max-height: 90vh;
                overflow: hidden;
                position: relative;
            }
            
            .demo-header {
                background: linear-gradient(135deg, #9B6EC8, #7C3AED);
                color: white;
                padding: 20px;
            }
            
            .demo-controls {
                display: flex;
                gap: 12px;
                margin-bottom: 16px;
                flex-wrap: wrap;
            }
            
            .demo-btn {
                background: rgba(255, 255, 255, 0.2);
                color: white;
                border: 1px solid rgba(255, 255, 255, 0.3);
                border-radius: 8px;
                padding: 8px 16px;
                font-size: 14px;
                font-weight: 500;
                cursor: pointer;
                transition: all 0.2s ease;
                backdrop-filter: blur(10px);
            }
            
            .demo-btn:hover {
                background: rgba(255, 255, 255, 0.3);
                transform: translateY(-1px);
            }
            
            .demo-progress {
                display: flex;
                align-items: center;
                gap: 16px;
            }
            
            .demo-progress-bar {
                flex: 1;
                height: 6px;
                background: rgba(255, 255, 255, 0.3);
                border-radius: 3px;
                overflow: hidden;
            }
            
            .demo-progress-fill {
                height: 100%;
                background: white;
                border-radius: 3px;
                transition: width 0.3s ease;
                width: 0%;
            }
            
            .demo-step-indicator {
                font-size: 14px;
                font-weight: 500;
                min-width: 40px;
                text-align: center;
            }
            
            .demo-content {
                padding: 40px;
                text-align: center;
                min-height: 300px;
                display: flex;
                align-items: center;
                justify-content: center;
            }
            
            .demo-step {
                max-width: 600px;
            }
            
            .demo-title {
                font-size: 2.5rem;
                font-weight: 700;
                color: #1f2937;
                margin: 0 0 8px 0;
                line-height: 1.2;
            }
            
            .demo-subtitle {
                font-size: 1.25rem;
                font-weight: 600;
                color: #9B6EC8;
                margin: 0 0 16px 0;
            }
            
            .demo-description {
                font-size: 1.125rem;
                line-height: 1.6;
                color: #6b7280;
                margin: 0;
            }
            
            .demo-highlight {
                position: absolute;
                border: 3px solid #9B6EC8;
                border-radius: 8px;
                box-shadow: 0 0 0 9999px rgba(0, 0, 0, 0.5);
                pointer-events: none;
                z-index: 10000;
                animation: highlight-pulse 2s infinite;
            }
            
            @keyframes highlight-pulse {
                0%, 100% { box-shadow: 0 0 0 9999px rgba(0, 0, 0, 0.5), 0 0 0 0 rgba(155, 110, 200, 0.7); }
                50% { box-shadow: 0 0 0 9999px rgba(0, 0, 0, 0.5), 0 0 0 10px rgba(155, 110, 200, 0); }
            }
            
            @keyframes fadeIn {
                from { opacity: 0; }
                to { opacity: 1; }
            }
            
            /* Demo trigger button */
            .demo-trigger-btn {
                position: fixed;
                bottom: 20px;
                right: 20px;
                background: linear-gradient(135deg, #9B6EC8, #7C3AED);
                color: white;
                border: none;
                border-radius: 50px;
                padding: 12px 20px;
                font-size: 14px;
                font-weight: 600;
                cursor: pointer;
                box-shadow: 0 4px 12px rgba(155, 110, 200, 0.3);
                transition: all 0.3s ease;
                z-index: 1000;
            }
            
            .demo-trigger-btn:hover {
                transform: translateY(-2px);
                box-shadow: 0 6px 20px rgba(155, 110, 200, 0.4);
            }
            
            @media (max-width: 768px) {
                .demo-container {
                    width: 95%;
                    margin: 20px;
                }
                
                .demo-content {
                    padding: 30px 20px;
                    min-height: 250px;
                }
                
                .demo-title {
                    font-size: 2rem;
                }
                
                .demo-subtitle {
                    font-size: 1.125rem;
                }
                
                .demo-description {
                    font-size: 1rem;
                }
                
                .demo-controls {
                    justify-content: center;
                }
                
                .demo-btn {
                    padding: 10px 14px;
                    font-size: 13px;
                }
            }
        `;
        
        const styleSheet = document.createElement('style');
        styleSheet.id = styleId;
        styleSheet.textContent = styles;
        document.head.appendChild(styleSheet);
    }
    
    bindEvents() {
        // Play button
        document.getElementById('demoPlayBtn').addEventListener('click', () => {
            this.playDemo();
        });
        
        // Pause button
        document.getElementById('demoPauseBtn').addEventListener('click', () => {
            this.pauseDemo();
        });
        
        // Restart button
        document.getElementById('demoRestartBtn').addEventListener('click', () => {
            this.restartDemo();
        });
        
        // Close button
        document.getElementById('demoCloseBtn').addEventListener('click', () => {
            this.closeDemo();
        });
    }
    
    showDemo() {
        this.demoOverlay.style.display = 'flex';
        this.currentStep = 0;
        this.updateStep();
        this.updateProgress();
    }
    
    closeDemo() {
        this.pauseDemo();
        this.demoOverlay.style.display = 'none';
    }
    
    playDemo() {
        this.isPlaying = true;
        document.getElementById('demoPlayBtn').style.display = 'none';
        document.getElementById('demoPauseBtn').style.display = 'inline-block';
        this.advanceStep();
    }
    
    pauseDemo() {
        this.isPlaying = false;
        document.getElementById('demoPlayBtn').style.display = 'inline-block';
        document.getElementById('demoPauseBtn').style.display = 'none';
        clearTimeout(this.stepTimeout);
    }
    
    restartDemo() {
        this.pauseDemo();
        this.currentStep = 0;
        this.updateStep();
        this.updateProgress();
        this.clearHighlight();
    }
    
    advanceStep() {
        if (!this.isPlaying) return;
        
        this.currentStep++;
        if (this.currentStep >= this.demoSteps.length) {
            this.currentStep = 0; // Loop back to start
        }
        
        this.updateStep();
        this.updateProgress();
        this.executeStepAction();
        
        const step = this.demoSteps[this.currentStep];
        this.stepTimeout = setTimeout(() => {
            this.advanceStep();
        }, step.duration);
    }
    
    updateStep() {
        const step = this.demoSteps[this.currentStep];
        const stepElement = document.getElementById('demoStep');
        
        stepElement.innerHTML = `
            <h2 class="demo-title">${step.title}</h2>
            <h3 class="demo-subtitle">${step.subtitle}</h3>
            <p class="demo-description">${step.description}</p>
        `;
        
        document.getElementById('demoStepNumber').textContent = this.currentStep + 1;
        document.getElementById('demoTotalSteps').textContent = this.demoSteps.length;
    }
    
    updateProgress() {
        const progress = ((this.currentStep + 1) / this.demoSteps.length) * 100;
        document.getElementById('demoProgressFill').style.width = `${progress}%`;
    }
    
    executeStepAction() {
        const step = this.demoSteps[this.currentStep];
        
        switch (step.action) {
            case 'show_welcome':
                this.clearHighlight();
                break;
                
            case 'highlight_voice_button':
                this.highlightElement('.voice-btn', 'Voice expense entry button');
                break;
                
            case 'highlight_profitability':
                this.highlightElement('.job-profitability-section', 'Job profitability dashboard');
                break;
                
            case 'show_categories':
                this.highlightElement('.job-profit-card', 'Construction-specific categories');
                break;
                
            case 'show_mobile':
                this.showMobilePreview();
                break;
                
            case 'show_cta':
                this.showCallToAction();
                break;
        }
    }
    
    highlightElement(selector, description) {
        const element = document.querySelector(selector);
        if (!element) return;
        
        const rect = element.getBoundingClientRect();
        const highlight = document.getElementById('demoHighlight');
        
        highlight.style.left = `${rect.left - 10}px`;
        highlight.style.top = `${rect.top - 10}px`;
        highlight.style.width = `${rect.width + 20}px`;
        highlight.style.height = `${rect.height + 20}px`;
        highlight.style.display = 'block';
    }
    
    clearHighlight() {
        document.getElementById('demoHighlight').style.display = 'none';
    }
    
    showMobilePreview() {
        // Create mobile preview overlay
        const mobilePreview = document.createElement('div');
        mobilePreview.className = 'mobile-preview';
        mobilePreview.innerHTML = `
            <div class="mobile-device">
                <div class="mobile-screen">
                    <div class="mobile-header">
                        <div class="mobile-voice-btn">🎤</div>
                        <h3>Mobile Dashboard</h3>
                    </div>
                    <div class="mobile-job-card">
                        <h4>Johnson Bathroom</h4>
                        <div class="mobile-metrics">
                            <span>Quoted: $5,000</span>
                            <span>Costs: $3,200</span>
                        </div>
                        <div class="mobile-profit">+$1,800 (36%)</div>
                    </div>
                </div>
            </div>
        `;
        
        // Add mobile preview styles
        const mobileStyles = `
            .mobile-preview {
                position: fixed;
                top: 50%;
                left: 50%;
                transform: translate(-50%, -50%);
                z-index: 10001;
                animation: mobileSlideIn 0.5s ease;
            }
            
            .mobile-device {
                width: 280px;
                height: 500px;
                background: #1f2937;
                border-radius: 20px;
                padding: 8px;
                box-shadow: 0 20px 40px rgba(0, 0, 0, 0.3);
            }
            
            .mobile-screen {
                width: 100%;
                height: 100%;
                background: white;
                border-radius: 12px;
                padding: 20px;
                display: flex;
                flex-direction: column;
                gap: 20px;
            }
            
            .mobile-header {
                display: flex;
                align-items: center;
                gap: 12px;
                padding-bottom: 16px;
                border-bottom: 1px solid #e5e7eb;
            }
            
            .mobile-voice-btn {
                width: 48px;
                height: 48px;
                background: linear-gradient(135deg, #9B6EC8, #7C3AED);
                border-radius: 50%;
                display: flex;
                align-items: center;
                justify-content: center;
                font-size: 20px;
                color: white;
            }
            
            .mobile-job-card {
                background: #f8fafc;
                border-radius: 8px;
                padding: 16px;
                border: 1px solid #e5e7eb;
            }
            
            .mobile-job-card h4 {
                margin: 0 0 8px 0;
                font-size: 16px;
                font-weight: 600;
            }
            
            .mobile-metrics {
                display: flex;
                justify-content: space-between;
                font-size: 14px;
                color: #6b7280;
                margin-bottom: 8px;
            }
            
            .mobile-profit {
                font-size: 16px;
                font-weight: 600;
                color: #22c55e;
                text-align: center;
            }
            
            @keyframes mobileSlideIn {
                from { transform: translate(-50%, -50%) scale(0.8); opacity: 0; }
                to { transform: translate(-50%, -50%) scale(1); opacity: 1; }
            }
        `;
        
        const styleSheet = document.createElement('style');
        styleSheet.textContent = mobileStyles;
        document.head.appendChild(styleSheet);
        
        document.body.appendChild(mobilePreview);
        
        // Remove after 3 seconds
        setTimeout(() => {
            mobilePreview.remove();
        }, 3000);
    }
    
    showCallToAction() {
        const stepElement = document.getElementById('demoStep');
        stepElement.innerHTML = `
            <h2 class="demo-title">Ready to Get Started?</h2>
            <h3 class="demo-subtitle">Join the beta program</h3>
            <p class="demo-description">Be among the first contractors to experience the future of construction financial management.</p>
            <div class="demo-cta-buttons">
                <button class="demo-cta-btn primary" onclick="window.location.href='/onboarding'">Start Free Trial</button>
                <button class="demo-cta-btn secondary" onclick="window.location.href='/contact'">Contact Sales</button>
            </div>
        `;
        
        // Add CTA button styles
        const ctaStyles = `
            .demo-cta-buttons {
                display: flex;
                gap: 16px;
                justify-content: center;
                margin-top: 24px;
                flex-wrap: wrap;
            }
            
            .demo-cta-btn {
                padding: 12px 24px;
                border-radius: 8px;
                font-size: 16px;
                font-weight: 600;
                cursor: pointer;
                transition: all 0.2s ease;
                border: none;
            }
            
            .demo-cta-btn.primary {
                background: #9B6EC8;
                color: white;
            }
            
            .demo-cta-btn.primary:hover {
                background: #7C3AED;
                transform: translateY(-1px);
            }
            
            .demo-cta-btn.secondary {
                background: white;
                color: #9B6EC8;
                border: 2px solid #9B6EC8;
            }
            
            .demo-cta-btn.secondary:hover {
                background: #9B6EC8;
                color: white;
            }
        `;
        
        const styleSheet = document.createElement('style');
        styleSheet.textContent = ctaStyles;
        document.head.appendChild(styleSheet);
    }
    
    // Static method to create demo trigger button
    static createDemoTrigger() {
        const triggerBtn = document.createElement('button');
        triggerBtn.className = 'demo-trigger-btn';
        triggerBtn.textContent = '🎬 Watch Demo';
        triggerBtn.onclick = () => {
            const demo = new DemoVideoUI();
            demo.showDemo();
        };
        
        document.body.appendChild(triggerBtn);
        return triggerBtn;
    }
}

// Export for use
if (typeof module !== 'undefined' && module.exports) {
    module.exports = DemoVideoUI;
} 