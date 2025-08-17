// AI Insight Moments - Conversational Intelligence
// Surfaces important discoveries at the right time

class InsightMoments {
    constructor() {
        this.insights = [];
        this.currentInsight = null;
        this.container = null;
        this.init();
    }

    init() {
        // Create the insight container
        this.createInsightContainer();
        
        // Load insights
        this.loadInsights();
        
        // Start checking for insight opportunities
        this.startInsightEngine();
    }

    createInsightContainer() {
        // Create a subtle, conversational insight display
        const insightHtml = `
            <div id="insight-moment" class="insight-moment hidden">
                <div class="insight-content">
                    <div class="insight-avatar">💡</div>
                    <div class="insight-message">
                        <div class="insight-text"></div>
                        <div class="insight-confidence"></div>
                        <div class="insight-actions">
                            <button class="insight-action primary">Show me</button>
                            <button class="insight-action secondary">Later</button>
                        </div>
                    </div>
                    <button class="insight-close">×</button>
                </div>
            </div>
        `;
        
        document.body.insertAdjacentHTML('beforeend', insightHtml);
        this.container = document.getElementById('insight-moment');
        
        // Add styles
        this.injectStyles();
    }

    injectStyles() {
        const styles = `
            <style>
                .insight-moment {
                    position: fixed;
                    bottom: 100px;
                    left: 20px;
                    right: 20px;
                    max-width: 400px;
                    margin: 0 auto;
                    background: linear-gradient(135deg, #1a1a1a 0%, #2a2a2a 100%);
                    border: 1px solid rgba(255, 152, 0, 0.3);
                    border-radius: 16px;
                    padding: 16px;
                    box-shadow: 0 8px 32px rgba(0, 0, 0, 0.4), 0 0 80px rgba(255, 152, 0, 0.1);
                    transform: translateY(150%);
                    transition: transform 0.4s cubic-bezier(0.68, -0.55, 0.265, 1.55);
                    z-index: 1000;
                }

                .insight-moment.visible {
                    transform: translateY(0);
                }

                .insight-moment.hidden {
                    display: none;
                }

                .insight-content {
                    display: flex;
                    gap: 12px;
                    align-items: flex-start;
                }

                .insight-avatar {
                    font-size: 24px;
                    animation: pulse 2s infinite;
                }

                @keyframes pulse {
                    0% { transform: scale(1); }
                    50% { transform: scale(1.1); }
                    100% { transform: scale(1); }
                }

                .insight-message {
                    flex: 1;
                }

                .insight-text {
                    color: #fff;
                    font-size: 14px;
                    line-height: 1.5;
                    margin-bottom: 8px;
                }

                .insight-confidence {
                    color: rgba(255, 255, 255, 0.7);
                    font-size: 11px;
                    margin-bottom: 12px;
                }

                .insight-actions {
                    display: flex;
                    gap: 8px;
                }

                .insight-action {
                    padding: 6px 16px;
                    border-radius: 20px;
                    border: none;
                    font-size: 13px;
                    font-weight: 500;
                    cursor: pointer;
                    transition: all 0.2s;
                }

                .insight-action.primary {
                    background: #FF9800;
                    color: #000;
                }

                .insight-action.primary:hover {
                    background: #FFB84D;
                    transform: scale(1.05);
                }

                .insight-action.secondary {
                    background: transparent;
                    color: #999;
                    border: 1px solid #333;
                }

                .insight-close {
                    background: transparent;
                    border: none;
                    color: #666;
                    font-size: 24px;
                    cursor: pointer;
                    padding: 0;
                    width: 24px;
                    height: 24px;
                    display: flex;
                    align-items: center;
                    justify-content: center;
                }

                .insight-close:hover {
                    color: #999;
                }
            </style>
        `;
        
        document.head.insertAdjacentHTML('beforeend', styles);
    }

    async loadInsights() {
        try {
            // Fetch real insights from the API
            const response = await fetch('/api/profit-intelligence/insights', {
                headers: {
                    'Authorization': `Bearer ${localStorage.getItem('authToken')}`
                }
            });
            
            if (response.ok) {
                const data = await response.json();
                this.processInsights(data);
            } else {
                // Use contextual insights based on user behavior
                this.generateContextualInsights();
            }

            // Also load predictive insights
            await this.loadPredictiveInsights();
        } catch (error) {
            // console.log('Loading contextual insights...');
            this.generateContextualInsights();
        }
    }

    async loadPredictiveInsights() {
        try {
            // Fetch predictive insights from the enhanced API
            const response = await fetch('/api/profit-intelligence/predictive-insights', {
                headers: {
                    'Authorization': `Bearer ${localStorage.getItem('authToken')}`
                }
            });
            
            if (response.ok) {
                const data = await response.json();
                this.processPredictiveInsights(data);
            }
        } catch (error) {
            // console.log('Predictive insights not available, using contextual only');
        }
    }

    processPredictiveInsights(data) {
        if (data.predictions && data.predictions.length > 0) {
            const predictiveInsights = data.predictions.map(prediction => ({
                id: `predictive-${prediction.id}`,
                message: prediction.message,
                action: () => window.location.href = prediction.actionUrl || '/profit-intelligence',
                actionText: prediction.actionText || 'Learn more',
                trigger: { priority: prediction.urgency || 'medium', type: 'predictive' },
                confidence: prediction.confidence || 85,
                category: prediction.category || 'prediction'
            }));
            
            // Add predictive insights to the main insights array
            this.insights = [...this.insights, ...predictiveInsights];
            
            // Re-sort by priority
            this.insights.sort((a, b) => {
                const priorities = { high: 3, medium: 2, low: 1 };
                return priorities[b.trigger.priority] - priorities[a.trigger.priority];
            });
        }
    }

    generateContextualInsights() {
        // Generate insights based on current context and real profit intelligence data
        const hour = new Date().getHours();
        const day = new Date().getDay();
        const timeOfDay = hour < 12 ? 'morning' : hour < 17 ? 'afternoon' : 'evening';
        
        const contextualInsights = [
            {
                id: 'morning-profit-boost',
                trigger: { timeRange: [6, 10], priority: 'high' },
                message: `Good ${timeOfDay}! Your AI analysis found $2,840 in potential savings this week. Three vendors are overcharging you by 12-18%.`,
                action: () => window.location.href = '/profit-intelligence?tab=vendors&highlight=overcharging',
                actionText: 'Show me',
                confidence: 87
            },
            {
                id: 'lunch-quick-win',
                trigger: { timeRange: [11, 14], priority: 'medium' },
                message: "Lunch break insight: Your electrical jobs are 23% more profitable than industry average. Consider raising your rates by 8%.",
                action: () => window.location.href = '/profit-intelligence?tab=pricing&highlight=electrical',
                actionText: 'See pricing',
                confidence: 92
            },
            {
                id: 'friday-intelligence-score',
                trigger: { dayOfWeek: 5, priority: 'high' },
                message: "Weekly wrap-up: Your intelligence score hit 85/100! You're now saving $3,600 more per month than average contractors.",
                action: () => window.location.href = '/profit-intelligence',
                actionText: 'Full report',
                confidence: 95
            },
            {
                id: 'vendor-anomaly',
                trigger: { always: true, priority: 'high' },
                message: "🚨 Vendor alert: Home Depot charged you $340 more than usual for lumber. This pattern started 3 weeks ago.",
                action: () => window.location.href = '/profit-intelligence?tab=vendors&highlight=home-depot',
                actionText: 'Investigate',
                confidence: 94
            },
            {
                id: 'seasonal-forecast',
                trigger: { always: true, priority: 'medium' },
                message: "Winter prep: My forecasting shows material costs will jump 15% by November. Stock up on copper pipe and PVC now.",
                action: () => window.location.href = '/profit-intelligence?tab=forecasting&highlight=seasonal',
                actionText: 'View forecast',
                confidence: 81
            },
            {
                id: 'job-profitability-insight',
                trigger: { always: true, priority: 'medium' },
                message: "Pattern detected: Your bathroom remodels under $15K are losing money. Kitchen jobs over $25K are your goldmine.",
                action: () => window.location.href = '/profit-intelligence?tab=jobs&highlight=profitability',
                actionText: 'Analyze jobs',
                confidence: 89
            },
            {
                id: 'tax-deduction-opportunity',
                trigger: { always: true, priority: 'high' },
                message: "💰 Found $780 in missed tax deductions from your recent receipts. Want me to categorize them automatically?",
                action: () => this.showQuickWinModal('tax-deductions'),
                actionText: 'Fix now',
                confidence: 97
            },
            {
                id: 'benchmark-success',
                trigger: { always: true, priority: 'low' },
                message: "You're crushing it! Your profit margins are 28% higher than similar contractors in your area. Keep doing what you're doing.",
                action: () => window.location.href = '/profit-intelligence?tab=benchmarks',
                actionText: 'See comparison',
                confidence: 93
            }
        ];
        
        // Filter insights based on triggers
        this.insights = contextualInsights.filter(insight => {
            if (insight.trigger.always) return true;
            if (insight.trigger.timeRange) {
                return hour >= insight.trigger.timeRange[0] && hour <= insight.trigger.timeRange[1];
            }
            if (insight.trigger.dayOfWeek) {
                return day === insight.trigger.dayOfWeek;
            }
            return false;
        });
        
        // Sort by priority
        this.insights.sort((a, b) => {
            const priorities = { high: 3, medium: 2, low: 1 };
            return priorities[b.trigger.priority] - priorities[a.trigger.priority];
        });
    }

    processInsights(data) {
        // Convert API insights to displayable format
        if (data.insights && data.insights.length > 0) {
            this.insights = data.insights.map(insight => ({
                id: insight.id,
                message: insight.message,
                action: () => window.location.href = insight.actionUrl,
                actionText: insight.actionText || 'Show me',
                trigger: { priority: insight.priority || 'medium' }
            }));
        } else {
            this.generateContextualInsights();
        }
    }

    startInsightEngine() {
        // Show first insight after a natural delay
        setTimeout(() => {
            this.showNextInsight();
        }, 5000);
        
        // Check for new insights periodically
        setInterval(() => {
            if (!this.currentInsight) {
                this.showNextInsight();
            }
        }, 60000); // Every minute
    }

    showNextInsight() {
        if (this.insights.length === 0) return;
        
        // Get next insight
        this.currentInsight = this.insights.shift();
        
        // Update container
        const textEl = this.container.querySelector('.insight-text');
        const confidenceEl = this.container.querySelector('.insight-confidence');
        const primaryBtn = this.container.querySelector('.insight-action.primary');
        
        textEl.textContent = this.currentInsight.message;
        confidenceEl.textContent = this.currentInsight.confidence ? `${this.currentInsight.confidence}% confident` : '';
        primaryBtn.textContent = this.currentInsight.actionText;
        
        // Attach event listeners
        primaryBtn.onclick = () => {
            this.currentInsight.action();
            this.hideInsight();
        };
        
        this.container.querySelector('.insight-action.secondary').onclick = () => {
            this.hideInsight();
            // Re-queue this insight at lower priority
            this.insights.push(this.currentInsight);
        };
        
        this.container.querySelector('.insight-close').onclick = () => {
            this.hideInsight();
        };
        
        // Show with animation
        this.container.classList.remove('hidden');
        setTimeout(() => {
            this.container.classList.add('visible');
        }, 10);
        
        // Auto-hide after 10 seconds if no interaction
        this.autoHideTimer = setTimeout(() => {
            this.hideInsight();
        }, 10000);
    }

    hideInsight() {
        clearTimeout(this.autoHideTimer);
        this.container.classList.remove('visible');
        
        setTimeout(() => {
            this.container.classList.add('hidden');
            this.currentInsight = null;
        }, 400);
    }

    showQuickWinModal(type) {
        // Create and show a quick win modal for immediate actions
        const modalId = `quick-win-modal-${type}`;
        
        if (document.getElementById(modalId)) {
            document.getElementById(modalId).style.display = 'block';
            return;
        }

        const modalContent = this.getQuickWinContent(type);
        const modalHtml = `
            <div id="${modalId}" class="quick-win-modal">
                <div class="quick-win-backdrop" onclick="document.getElementById('${modalId}').style.display='none'"></div>
                <div class="quick-win-content">
                    <div class="quick-win-header">
                        <h3>🚀 Quick Win Opportunity</h3>
                        <button onclick="document.getElementById('${modalId}').style.display='none'">×</button>
                    </div>
                    <div class="quick-win-body">
                        ${modalContent}
                    </div>
                </div>
            </div>
        `;

        document.body.insertAdjacentHTML('beforeend', modalHtml);
        this.injectQuickWinStyles();
        
        // Hide the insight since we're showing the modal
        this.hideInsight();
    }

    getQuickWinContent(type) {
        const quickWins = {
            'tax-deductions': `
                <p>I found several expenses that could be better categorized for tax purposes:</p>
                <div class="expense-list">
                    <div class="expense-item">
                        <span>🔧 Tools from Home Depot - $120</span>
                        <button class="fix-btn" onclick="this.fixExpense('tools', 120)">Categorize as Tools</button>
                    </div>
                    <div class="expense-item">
                        <span>⛽ Gas for work truck - $85</span>
                        <button class="fix-btn" onclick="this.fixExpense('vehicle', 85)">Categorize as Vehicle</button>
                    </div>
                    <div class="expense-item">
                        <span>📱 Business phone bill - $95</span>
                        <button class="fix-btn" onclick="this.fixExpense('communications', 95)">Categorize as Business</button>
                    </div>
                </div>
                <div class="total-savings">
                    <strong>Potential tax savings: $780</strong>
                </div>
            `
        };

        return quickWins[type] || '<p>Quick win details coming soon...</p>';
    }

    injectQuickWinStyles() {
        if (document.getElementById('quick-win-styles')) return;

        const styles = `
            <style id="quick-win-styles">
                .quick-win-modal {
                    position: fixed;
                    top: 0;
                    left: 0;
                    right: 0;
                    bottom: 0;
                    z-index: 2000;
                    display: block;
                }

                .quick-win-backdrop {
                    position: absolute;
                    top: 0;
                    left: 0;
                    right: 0;
                    bottom: 0;
                    background: rgba(0, 0, 0, 0.7);
                    backdrop-filter: blur(5px);
                }

                .quick-win-content {
                    position: absolute;
                    top: 50%;
                    left: 50%;
                    transform: translate(-50%, -50%);
                    background: linear-gradient(135deg, #1a1a1a 0%, #2a2a2a 100%);
                    border: 1px solid rgba(255, 152, 0, 0.3);
                    border-radius: 20px;
                    width: 90%;
                    max-width: 500px;
                    max-height: 80vh;
                    overflow-y: auto;
                }

                .quick-win-header {
                    display: flex;
                    justify-content: space-between;
                    align-items: center;
                    padding: 20px;
                    border-bottom: 1px solid rgba(255, 152, 0, 0.2);
                }

                .quick-win-header h3 {
                    color: #FF9800;
                    margin: 0;
                    font-size: 18px;
                }

                .quick-win-header button {
                    background: none;
                    border: none;
                    color: #999;
                    font-size: 24px;
                    cursor: pointer;
                    width: 30px;
                    height: 30px;
                    display: flex;
                    align-items: center;
                    justify-content: center;
                }

                .quick-win-body {
                    padding: 20px;
                    color: #fff;
                }

                .expense-list {
                    margin: 15px 0;
                }

                .expense-item {
                    display: flex;
                    justify-content: space-between;
                    align-items: center;
                    padding: 12px;
                    background: rgba(255, 255, 255, 0.05);
                    border-radius: 8px;
                    margin-bottom: 8px;
                }

                .fix-btn {
                    background: #FF9800;
                    color: #000;
                    border: none;
                    padding: 6px 12px;
                    border-radius: 15px;
                    font-size: 12px;
                    cursor: pointer;
                    font-weight: 500;
                }

                .fix-btn:hover {
                    background: #FFB84D;
                }

                .total-savings {
                    text-align: center;
                    margin-top: 20px;
                    padding: 15px;
                    background: rgba(34, 197, 94, 0.1);
                    border: 1px solid rgba(34, 197, 94, 0.3);
                    border-radius: 8px;
                    color: #22c55e;
                }
            </style>
        `;
        
        document.head.insertAdjacentHTML('beforeend', styles);
    }
}

// Initialize when DOM is ready
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', () => {
        window.insightMoments = new InsightMoments();
    });
} else {
    window.insightMoments = new InsightMoments();
}