/**
 * Intelligence Score Widget
 * 
 * A prominent, always-visible indicator of CORA's AI analysis score
 * that encourages users to explore deeper insights.
 * 
 * Philosophy: Surface the AI's confidence and value immediately
 */

class IntelligenceScoreWidget {
    constructor() {
        this.score = 0;
        this.grade = 'C';
        this.trend = 'stable';
        this.container = null;
        this.updateInterval = null;
        this.init();
    }

    async init() {
        await this.loadScore();
        this.createWidget();
        this.startRealTimeUpdates();
    }

    async loadScore() {
        try {
            const response = await fetch('/api/profit-intelligence/profit-intelligence-summary');
            if (response.ok) {
                const data = await response.json();
                this.score = data.intelligence_score || 75;
                this.grade = this.calculateGrade(this.score);
                this.trend = data.trend || 'stable';
            }
        } catch (error) {
            // console.log('Using demo score for development');
            this.score = 82;
            this.grade = 'B+';
            this.trend = 'improving';
        }
    }

    createWidget() {
        // Find the best location in the dashboard
        const targetLocation = this.findOptimalLocation();
        if (!targetLocation) return;

        // Create the widget HTML
        const widgetHtml = `
            <div id="intelligence-score-widget" class="intelligence-widget">
                <div class="widget-content">
                    <div class="score-section">
                        <div class="score-circle">
                            <div class="score-number">${this.score}</div>
                            <div class="score-grade">${this.grade}</div>
                        </div>
                        <div class="score-trend ${this.trend}">
                            ${this.getTrendIcon()} ${this.getTrendText()}
                        </div>
                    </div>
                    <div class="widget-info">
                        <h4>AI Intelligence</h4>
                        <p>Your profit optimization score</p>
                        <button class="explore-btn" onclick="intelligenceWidget.exploreInsights()">
                            See insights →
                        </button>
                    </div>
                </div>
                <div class="widget-pulse"></div>
            </div>
        `;

        // Insert widget
        targetLocation.insertAdjacentHTML('afterbegin', widgetHtml);
        this.container = document.getElementById('intelligence-score-widget');
        
        // Add styles
        this.injectStyles();
        
        // Animate in
        setTimeout(() => {
            this.container.classList.add('visible');
        }, 500);
    }

    findOptimalLocation() {
        // Try to find dashboard main content area
        const candidates = [
            document.querySelector('.dashboard-main'),
            document.querySelector('.main-content'),
            document.querySelector('.dashboard-content'),
            document.querySelector('main'),
            document.querySelector('.container')
        ];

        for (const candidate of candidates) {
            if (candidate) return candidate;
        }

        // Fallback to body
        return document.body;
    }

    calculateGrade(score) {
        if (score >= 95) return 'A+';
        if (score >= 90) return 'A';
        if (score >= 85) return 'A-';
        if (score >= 80) return 'B+';
        if (score >= 75) return 'B';
        if (score >= 70) return 'B-';
        if (score >= 65) return 'C+';
        if (score >= 60) return 'C';
        if (score >= 55) return 'C-';
        if (score >= 50) return 'D';
        return 'F';
    }

    getTrendIcon() {
        const icons = {
            'improving': '📈',
            'declining': '📉',
            'stable': '➡️',
            'volatile': '📊'
        };
        return icons[this.trend] || '➡️';
    }

    getTrendText() {
        const texts = {
            'improving': 'Improving',
            'declining': 'Needs attention',
            'stable': 'Stable',
            'volatile': 'Fluctuating'
        };
        return texts[this.trend] || 'Stable';
    }

    exploreInsights() {
        // Navigate to profit intelligence with highlight
        window.location.href = '/profit-intelligence?source=widget';
        
        // Track interaction
        this.trackInteraction('explore_clicked');
    }

    async updateScore() {
        await this.loadScore();
        
        if (this.container) {
            // Update score with animation
            const scoreEl = this.container.querySelector('.score-number');
            const gradeEl = this.container.querySelector('.score-grade');
            const trendEl = this.container.querySelector('.score-trend');
            
            if (scoreEl) {
                scoreEl.style.transform = 'scale(1.1)';
                setTimeout(() => {
                    scoreEl.textContent = this.score;
                    scoreEl.style.transform = 'scale(1)';
                }, 200);
            }
            
            if (gradeEl) {
                gradeEl.textContent = this.grade;
            }
            
            if (trendEl) {
                trendEl.className = `score-trend ${this.trend}`;
                trendEl.innerHTML = `${this.getTrendIcon()} ${this.getTrendText()}`;
            }
        }
    }

    startRealTimeUpdates() {
        // Update score every 5 minutes
        this.updateInterval = setInterval(() => {
            this.updateScore();
        }, 5 * 60 * 1000);
    }

    trackInteraction(action) {
        // Track user interactions for analytics
        try {
            fetch('/api/insights/interact/intelligence-widget', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    action: action,
                    score: this.score,
                    timestamp: Date.now()
                })
            });
        } catch (error) {
            // console.log('Analytics tracking failed:', error);
        }
    }

    injectStyles() {
        if (document.getElementById('intelligence-widget-styles')) return;

        const styles = `
            <style id="intelligence-widget-styles">
                .intelligence-widget {
                    position: relative;
                    background: linear-gradient(135deg, #9B6EC8 0%, #8856B8 100%);
                    border-radius: 20px;
                    padding: 20px;
                    margin: 20px 0;
                    color: white;
                    box-shadow: 0 10px 30px rgba(139, 0, 255, 0.3);
                    opacity: 0;
                    transform: translateY(20px);
                    transition: all 0.6s cubic-bezier(0.68, -0.55, 0.265, 1.55);
                    overflow: hidden;
                    min-height: 120px;
                }

                .intelligence-widget.visible {
                    opacity: 1;
                    transform: translateY(0);
                }

                .widget-content {
                    display: flex;
                    align-items: center;
                    gap: 20px;
                    position: relative;
                    z-index: 2;
                }

                .score-section {
                    display: flex;
                    flex-direction: column;
                    align-items: center;
                }

                .score-circle {
                    width: 80px;
                    height: 80px;
                    border: 3px solid rgba(255, 255, 255, 0.3);
                    border-radius: 50%;
                    display: flex;
                    flex-direction: column;
                    align-items: center;
                    justify-content: center;
                    background: rgba(255, 255, 255, 0.1);
                    backdrop-filter: blur(10px);
                    margin-bottom: 8px;
                    position: relative;
                }

                .score-circle::before {
                    content: '';
                    position: absolute;
                    top: -3px;
                    left: -3px;
                    right: -3px;
                    bottom: -3px;
                    border-radius: 50%;
                    background: conic-gradient(
                        from 0deg,
                        #00FF88 0deg,
                        #3b82f6 120deg,
                        #8B00FF 240deg,
                        #00FF88 360deg
                    );
                    z-index: -1;
                    animation: rotate 3s linear infinite;
                }

                @keyframes rotate {
                    0% { transform: rotate(0deg); }
                    100% { transform: rotate(360deg); }
                }

                .score-number {
                    font-size: 24px;
                    font-weight: 700;
                    transition: transform 0.3s ease;
                }

                .score-grade {
                    font-size: 12px;
                    font-weight: 600;
                    opacity: 0.9;
                }

                .score-trend {
                    font-size: 11px;
                    padding: 4px 8px;
                    border-radius: 12px;
                    background: rgba(255, 255, 255, 0.2);
                    display: flex;
                    align-items: center;
                    gap: 4px;
                }

                .score-trend.improving {
                    background: rgba(34, 197, 94, 0.3);
                    color: #22c55e;
                }

                .score-trend.declining {
                    background: rgba(239, 68, 68, 0.3);
                    color: #ef4444;
                }

                .widget-info {
                    flex: 1;
                }

                .widget-info h4 {
                    margin: 0 0 4px 0;
                    font-size: 18px;
                    font-weight: 600;
                }

                .widget-info p {
                    margin: 0 0 12px 0;
                    font-size: 13px;
                    opacity: 0.8;
                }

                .explore-btn {
                    background: rgba(255, 255, 255, 0.2);
                    border: 1px solid rgba(255, 255, 255, 0.3);
                    color: white;
                    padding: 8px 16px;
                    border-radius: 20px;
                    font-size: 13px;
                    font-weight: 500;
                    cursor: pointer;
                    transition: all 0.3s ease;
                    backdrop-filter: blur(10px);
                }

                .explore-btn:hover {
                    background: rgba(255, 255, 255, 0.3);
                    transform: translateY(-1px);
                    box-shadow: 0 4px 12px rgba(255, 255, 255, 0.2);
                }

                .widget-pulse {
                    position: absolute;
                    top: 50%;
                    right: 20px;
                    width: 60px;
                    height: 60px;
                    background: radial-gradient(circle, rgba(255, 255, 255, 0.3) 0%, transparent 70%);
                    border-radius: 50%;
                    animation: pulse 4s ease-in-out infinite;
                    opacity: 0.5;
                }

                @keyframes pulse {
                    0%, 100% { 
                        transform: translateY(-50%) scale(1);
                        opacity: 0.5;
                    }
                    50% { 
                        transform: translateY(-50%) scale(1.2);
                        opacity: 0.8;
                    }
                }

                @media (max-width: 768px) {
                    .intelligence-widget {
                        margin: 16px 0;
                        padding: 16px;
                    }

                    .widget-content {
                        gap: 16px;
                    }

                    .score-circle {
                        width: 70px;
                        height: 70px;
                    }

                    .score-number {
                        font-size: 20px;
                    }

                    .widget-info h4 {
                        font-size: 16px;
                    }

                    .widget-pulse {
                        width: 40px;
                        height: 40px;
                        right: 16px;
                    }
                }

                /* Dark mode support */
                @media (prefers-color-scheme: dark) {
                    .intelligence-widget {
                        box-shadow: 0 10px 30px rgba(139, 0, 255, 0.4);
                    }
                }

                /* High contrast mode support */
                @media (prefers-contrast: high) {
                    .intelligence-widget {
                        border: 2px solid white;
                    }
                    
                    .explore-btn {
                        border: 2px solid white;
                    }
                }

                /* Reduced motion support */
                @media (prefers-reduced-motion: reduce) {
                    .intelligence-widget {
                        transition: opacity 0.3s ease;
                    }
                    
                    .score-circle::before {
                        animation: none;
                    }
                    
                    .widget-pulse {
                        animation: none;
                        opacity: 0.3;
                    }
                    
                    .explore-btn:hover {
                        transform: none;
                    }
                }
            </style>
        `;
        
        document.head.insertAdjacentHTML('beforeend', styles);
    }

    destroy() {
        if (this.updateInterval) {
            clearInterval(this.updateInterval);
        }
        
        if (this.container) {
            this.container.remove();
        }
    }
}

// Global instance
let intelligenceWidget;

// Initialize when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
    // Only initialize on dashboard pages
    if (window.location.pathname.includes('/dashboard') || 
        document.querySelector('.dashboard-main')) {
        intelligenceWidget = new IntelligenceScoreWidget();
    }
});

// Export for global access
window.intelligenceWidget = intelligenceWidget;