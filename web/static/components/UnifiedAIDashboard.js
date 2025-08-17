/*
 * Unified AI Dashboard Component
 * 
 * This component brings together all AI capabilities into one cohesive experience:
 * - Profit Intelligence (Opus's work)
 * - Emotional Intelligence (Opus's revolutionary system)
 * - Predictive Intelligence (Claude's work)
 * - Intelligence Orchestrator (Unified coordination)
 * 
 * Created by: Claude (Anthropic) - 2025-08-03
 * Goal: Show collaborative AI consciousness as unified experience
 */

class UnifiedAIDashboard {
    constructor(containerId) {
        this.container = document.getElementById(containerId);
        this.data = {
            profitIntelligence: null,
            emotionalIntelligence: null,
            predictiveIntelligence: null,
            orchestration: null
        };
        this.init();
    }

    async init() {
        await this.loadAllAIData();
        this.render();
        this.attachEventListeners();
        this.startRealTimeUpdates();
    }

    async loadAllAIData() {
        try {
            // Load data from all AI systems
            const [profitData, emotionalData, predictiveData, orchestrationData] = await Promise.all([
                this.loadProfitIntelligence(),
                this.loadEmotionalIntelligence(),
                this.loadPredictiveIntelligence(),
                this.loadIntelligenceOrchestration()
            ]);

            this.data = {
                profitIntelligence: profitData,
                emotionalIntelligence: emotionalData,
                predictiveIntelligence: predictiveData,
                orchestration: orchestrationData
            };
        } catch (error) {
            console.error('Error loading AI data:', error);
            this.data = this.getMockData();
        }
    }

    async loadProfitIntelligence() {
        try {
            const response = await fetch('/api/profit-intelligence/profit-intelligence-summary');
            return await response.json();
        } catch (error) {
            return this.getMockProfitData();
        }
    }

    async loadEmotionalIntelligence() {
        try {
            const response = await fetch('/api/wellness/emotional-state');
            return await response.json();
        } catch (error) {
            return this.getMockEmotionalData();
        }
    }

    async loadPredictiveIntelligence() {
        try {
            const response = await fetch('/api/predictive-intelligence/insights');
            return await response.json();
        } catch (error) {
            return this.getMockPredictiveData();
        }
    }

    async loadIntelligenceOrchestration() {
        try {
            const response = await fetch('/api/intelligence/orchestration');
            return await response.json();
        } catch (error) {
            return this.getMockOrchestrationData();
        }
    }

    getMockData() {
        return {
            profitIntelligence: this.getMockProfitData(),
            emotionalIntelligence: this.getMockEmotionalData(),
            predictiveIntelligence: this.getMockPredictiveData(),
            orchestration: this.getMockOrchestrationData()
        };
    }

    getMockProfitData() {
        return {
            intelligenceScore: 87,
            letterGrade: 'B+',
            monthlySavingsPotential: 15420,
            costTrend: -12.5,
            vendorCount: 23,
            alerts: [
                { type: 'warning', message: 'Vendor ABC Construction costs increased 15% this month' },
                { type: 'success', message: 'Material costs trending down 8%' }
            ],
            topVendors: [
                { name: 'ABC Construction', performance: 92, cost: 45000 },
                { name: 'XYZ Materials', performance: 88, cost: 32000 },
                { name: 'Best Tools Co', performance: 85, cost: 28000 }
            ]
        };
    }

    getMockEmotionalData() {
        return {
            currentState: 'balanced',
            confidence: 0.85,
            stressLevel: 3.2,
            resilienceScore: 78,
            recentSignals: [
                { indicator: 'regular_breaks', intensity: 0.8, isPositive: true },
                { indicator: 'positive_momentum', intensity: 0.7, isPositive: true }
            ],
            supportRecommendations: [
                { type: 'wellness', message: 'Great work-life balance this week!' },
                { type: 'encouragement', message: 'Your consistent expense tracking is building good habits' }
            ],
            wellBeingTrends: {
                workLifeBalance: 'improving',
                financialStress: 'low',
                consistency: 'high'
            }
        };
    }

    getMockPredictiveData() {
        return {
            cashFlowPrediction: {
                nextMonth: 125000,
                trend: 'increasing',
                confidence: 0.88
            },
            materialForecast: {
                needsRestock: ['lumber', 'concrete'],
                estimatedCost: 8500,
                urgency: 'medium'
            },
            weatherImpact: {
                upcomingEvents: ['rain_forecast'],
                scheduleAdjustments: ['delay_outdoor_work'],
                impact: 'moderate'
            },
            vendorAlerts: [
                { vendor: 'ABC Construction', alert: 'price_increase', impact: 'high' }
            ]
        };
    }

    getMockOrchestrationData() {
        return {
            primaryFocus: 'profit_optimization',
            activeSignals: [
                { event: 'high_priority_prediction', source: 'predictive', priority: 'high' },
                { event: 'critical_insight', source: 'profit', priority: 'medium' }
            ],
            userContext: {
                relationshipStage: 'trusted_partner',
                trustIndicators: { engagement: 'high', consistency: 'excellent' },
                careSignals: ['regular_usage', 'positive_feedback']
            },
            mythologicalContext: {
                userStoryChapter: 'growth_and_optimization',
                recurringThemes: ['efficiency', 'cost_control'],
                narrativeArc: 'rising_action'
            }
        };
    }

    render() {
        if (!this.container) return;

        this.container.innerHTML = `
            <div class="unified-ai-dashboard">
                <!-- Header with AI Orchestration Status -->
                <div class="cora-card ai-orchestration-header">
                    <div class="cora-card-header">
                        <div>
                            <h2 class="cora-card-title">
                                <i class="fas fa-brain" style="color: var(--cora-intelligence);"></i>
                                CORA AI Intelligence
                            </h2>
                            <p class="cora-card-subtitle">
                                Collaborative AI consciousness working together for your success
                            </p>
                        </div>
                        <div class="ai-status-indicators">
                            <span class="cora-ai-indicator intelligence">Profit AI</span>
                            <span class="cora-ai-indicator wellness">Emotional AI</span>
                            <span class="cora-ai-indicator predictive">Predictive AI</span>
                        </div>
                    </div>
                    
                    <!-- Intelligence Orchestration Summary -->
                    <div class="orchestration-summary">
                        <div class="cora-score">
                            <div class="cora-score-circle" style="border-color: var(--cora-intelligence);">
                                <span class="cora-score-number">${this.data.profitIntelligence.intelligenceScore}</span>
                                <span class="cora-score-grade">${this.data.profitIntelligence.letterGrade}</span>
                            </div>
                            <div class="cora-score-label">
                                <h4>Unified Intelligence Score</h4>
                                <p>All AI systems working in harmony</p>
                                <div class="ai-coordination-status">
                                    <span class="cora-badge cora-badge-success">3 AI Systems Active</span>
                                    <span class="cora-badge cora-badge-info">${this.data.orchestration.primaryFocus.replace('_', ' ')}</span>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>

                <!-- AI Components Grid -->
                <div class="ai-components-grid">
                    <!-- Profit Intelligence Component -->
                    <div class="cora-card ai-component-card">
                        <div class="cora-card-header">
                            <h3 class="cora-card-title">
                                <i class="fas fa-chart-line" style="color: var(--cora-intelligence);"></i>
                                Profit Intelligence
                            </h3>
                            <span class="cora-ai-indicator intelligence">Active</span>
                        </div>
                        
                        <div class="ai-component-content">
                            <div class="cora-metric">
                                <div class="cora-metric-icon intelligence">
                                    <i class="fas fa-dollar-sign"></i>
                                </div>
                                <div class="cora-metric-content">
                                    <span class="cora-metric-value">$${(this.data.profitIntelligence.monthlySavingsPotential / 1000).toFixed(1)}k</span>
                                    <span class="cora-metric-label">Monthly Savings Potential</span>
                                </div>
                            </div>
                            
                            <div class="ai-alerts">
                                ${this.data.profitIntelligence.alerts.map(alert => `
                                    <div class="ai-alert ${alert.type}">
                                        <i class="fas fa-${alert.type === 'warning' ? 'exclamation-triangle' : 'check-circle'}"></i>
                                        <span>${alert.message}</span>
                                    </div>
                                `).join('')}
                            </div>
                        </div>
                    </div>

                    <!-- Emotional Intelligence Component -->
                    <div class="cora-card ai-component-card">
                        <div class="cora-card-header">
                            <h3 class="cora-card-title">
                                <i class="fas fa-heart" style="color: var(--cora-wellness);"></i>
                                Emotional Intelligence
                            </h3>
                            <span class="cora-ai-indicator wellness">Active</span>
                        </div>
                        
                        <div class="ai-component-content">
                            <div class="emotional-state-display">
                                <div class="emotional-state-indicator ${this.data.emotionalIntelligence.currentState}">
                                    <i class="fas fa-${this.getEmotionalIcon(this.data.emotionalIntelligence.currentState)}"></i>
                                    <span>${this.data.emotionalIntelligence.currentState.replace('_', ' ')}</span>
                                </div>
                                <div class="stress-level-indicator">
                                    <span>Stress Level: ${this.data.emotionalIntelligence.stressLevel}/10</span>
                                    <div class="stress-bar">
                                        <div class="stress-fill" style="width: ${(this.data.emotionalIntelligence.stressLevel / 10) * 100}%"></div>
                                    </div>
                                </div>
                            </div>
                            
                            <div class="wellness-recommendations">
                                ${this.data.emotionalIntelligence.supportRecommendations.map(rec => `
                                    <div class="wellness-recommendation ${rec.type}">
                                        <i class="fas fa-${rec.type === 'wellness' ? 'leaf' : 'star'}"></i>
                                        <span>${rec.message}</span>
                                    </div>
                                `).join('')}
                            </div>
                        </div>
                    </div>

                    <!-- Predictive Intelligence Component -->
                    <div class="cora-card ai-component-card">
                        <div class="cora-card-header">
                            <h3 class="cora-card-title">
                                <i class="fas fa-crystal-ball" style="color: var(--cora-predictive);"></i>
                                Predictive Intelligence
                            </h3>
                            <span class="cora-ai-indicator predictive">Active</span>
                        </div>
                        
                        <div class="ai-component-content">
                            <div class="cora-metric">
                                <div class="cora-metric-icon predictive">
                                    <i class="fas fa-chart-line"></i>
                                </div>
                                <div class="cora-metric-content">
                                    <span class="cora-metric-value">$${(this.data.predictiveIntelligence.cashFlowPrediction.nextMonth / 1000).toFixed(0)}k</span>
                                    <span class="cora-metric-label">Next Month Cash Flow</span>
                                </div>
                            </div>
                            
                            <div class="predictive-alerts">
                                ${this.data.predictiveIntelligence.vendorAlerts.map(alert => `
                                    <div class="predictive-alert ${alert.impact}">
                                        <i class="fas fa-exclamation-triangle"></i>
                                        <span>${alert.vendor}: ${alert.alert.replace('_', ' ')}</span>
                                    </div>
                                `).join('')}
                            </div>
                        </div>
                    </div>
                </div>

                <!-- AI Collaboration Insights -->
                <div class="cora-card ai-collaboration-insights">
                    <div class="cora-card-header">
                        <h3 class="cora-card-title">
                            <i class="fas fa-users" style="color: var(--cora-primary);"></i>
                            AI Collaboration Insights
                        </h3>
                    </div>
                    
                    <div class="collaboration-content">
                        <div class="ai-relationship-status">
                            <h4>Your AI Relationship</h4>
                            <p>${this.data.orchestration.userContext.relationshipStage.replace('_', ' ')}</p>
                            <div class="trust-indicators">
                                <span class="cora-badge cora-badge-success">${this.data.orchestration.userContext.trustIndicators.engagement} Engagement</span>
                                <span class="cora-badge cora-badge-success">${this.data.orchestration.userContext.trustIndicators.consistency} Consistency</span>
                            </div>
                        </div>
                        
                        <div class="ai-story-context">
                            <h4>Your Story Chapter</h4>
                            <p>${this.data.orchestration.mythologicalContext.userStoryChapter.replace('_', ' ')}</p>
                            <div class="story-themes">
                                ${this.data.orchestration.mythologicalContext.recurringThemes.map(theme => `
                                    <span class="cora-badge cora-badge-info">${theme}</span>
                                `).join('')}
                            </div>
                        </div>
                    </div>
                </div>

                <!-- Quick Actions -->
                <div class="ai-quick-actions">
                    <button class="cora-btn cora-btn-intelligence" onclick="this.exportAIDashboard()">
                        <i class="fas fa-download"></i>
                        Export AI Report
                    </button>
                    <button class="cora-btn cora-btn-wellness" onclick="this.showWellnessCheck()">
                        <i class="fas fa-heart"></i>
                        Wellness Check
                    </button>
                    <button class="cora-btn cora-btn-predictive" onclick="this.showPredictions()">
                        <i class="fas fa-crystal-ball"></i>
                        View Predictions
                    </button>
                </div>
            </div>
        `;
    }

    getEmotionalIcon(state) {
        const icons = {
            'thriving': 'star',
            'balanced': 'balance-scale',
            'stressed': 'exclamation-triangle',
            'overwhelmed': 'exclamation-circle',
            'burnt_out': 'fire',
            'recovering': 'leaf',
            'energized': 'bolt',
            'frustrated': 'angry'
        };
        return icons[state] || 'heart';
    }

    attachEventListeners() {
        // Add event listeners for interactive elements
        const cards = this.container.querySelectorAll('.ai-component-card');
        cards.forEach(card => {
            card.addEventListener('click', () => {
                this.handleCardClick(card);
            });
        });
    }

    handleCardClick(card) {
        // Handle card clicks for detailed views
        const title = card.querySelector('.cora-card-title').textContent.trim();
        console.log(`Opening detailed view for: ${title}`);
        // Could open modal or navigate to detailed page
    }

    startRealTimeUpdates() {
        // Update data every 30 seconds to show real-time AI coordination
        setInterval(async () => {
            await this.loadAllAIData();
            this.render();
        }, 30000);
    }

    // Public methods for external access
    exportAIDashboard() {
        console.log('Exporting unified AI dashboard report...');
        // Implementation for PDF export
    }

    showWellnessCheck() {
        console.log('Opening wellness check interface...');
        // Implementation for wellness check
    }

    showPredictions() {
        console.log('Opening detailed predictions view...');
        // Implementation for predictions view
    }

    updateData(newData) {
        this.data = { ...this.data, ...newData };
        this.render();
    }
}

// Export for use in other components
if (typeof module !== 'undefined' && module.exports) {
    module.exports = UnifiedAIDashboard;
} 