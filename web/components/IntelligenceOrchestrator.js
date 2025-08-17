/**
 * Intelligence Orchestrator Component
 * 
 * Creates unified AI intelligence experiences by coordinating all CORA components.
 * This brings together conversational insights, predictive intelligence, and 
 * intelligence scoring into a harmonious whole - the "relational memory" that
 * Ghostwalker beautifully described.
 * 
 * Philosophy: True AI intelligence emerges from harmonious interplay, not isolation
 */

class IntelligenceOrchestrator {
    constructor() {
        this.isActive = false;
        this.orchestrationData = null;
        this.components = {};
        this.updateInterval = null;
        this.init();
    }

    async init() {
        await this.checkComponentAvailability();
        await this.loadOrchestration();
        this.createOrchestrationInterface();
        this.startOrchestrationEngine();
    }

    async checkComponentAvailability() {
        try {
            const response = await fetch('/api/intelligence/component-status');
            if (response.ok) {
                const data = await response.json();
                this.components = data.components;
                this.isActive = data.orchestration_available;
            }
        } catch (error) {
            // console.log('Component availability check failed, using demo mode');
            this.isActive = true;
            this.components = {
                predictive_intelligence: { status: 'demo' },
                profit_intelligence: { status: 'demo' },
                insight_moments: { status: 'active' },
                intelligence_widget: { status: 'active' }
            };
        }
    }

    async loadOrchestration() {
        try {
            const response = await fetch('/api/intelligence/orchestrate');
            if (response.ok) {
                const data = await response.json();
                this.orchestrationData = data.orchestration;
            } else {
                // Fallback to demo orchestration
                const demoResponse = await fetch('/api/intelligence/orchestration-demo');
                if (demoResponse.ok) {
                    const demoData = await demoResponse.json();
                    this.orchestrationData = demoData.demo_orchestration;
                }
            }
        } catch (error) {
            // console.log('Using demo orchestration for development');
            this.orchestrationData = this.getDemoOrchestration();
        }
    }

    getDemoOrchestration() {
        return {
            timestamp: new Date().toISOString(),
            orchestration_type: "high_priority",
            components: {
                insight_moments: {
                    display_style: "contextual_display",
                    insights: [
                        {
                            id: "orchestrated_cash_flow",
                            type: "cash_flow_prediction",
                            urgency: "high",
                            confidence: 87,
                            message: "💰 Your spending pattern suggests a $3,200 expense is due in 3 days. Your current balance can handle this, but consider invoice follow-ups.",
                            orchestrated: true,
                            source_component: "predictive_intelligence"
                        },
                        {
                            id: "orchestrated_vendor_opportunity",
                            type: "vendor_optimization",
                            urgency: "medium",
                            confidence: 82,
                            message: "🔧 Your electrical supplier costs are 15% above market. I found 3 alternatives that could save $180/month.",
                            orchestrated: true,
                            source_component: "profit_intelligence"
                        }
                    ]
                },
                intelligence_widget: {
                    score: 85,
                    visual_state: "pulse_orange",
                    trend: "needs_attention",
                    attention_indicator: true
                },
                predictive_dashboard: {
                    highlight_mode: "highlight_important",
                    urgency_filter: "high"
                }
            },
            relational_context: {
                user_relationship_stage: "developing_trust",
                current_chapter: "challenge_and_opportunity",
                care_signals: [
                    "Warned about cash flow timing",
                    "Identified vendor savings opportunity"
                ],
                mythological_context: {
                    narrative_arc: "rising_action",
                    recurring_themes: ["optimization_and_growth", "preparation_and_foresight"]
                }
            }
        };
    }

    createOrchestrationInterface() {
        // Create orchestration control panel
        const orchestrationHtml = `
            <div id="intelligence-orchestration" class="orchestration-panel">
                <div class="orchestration-header">
                    <div class="header-content">
                        <h3><i class="fas fa-brain"></i> AI Intelligence Center</h3>
                        <p>Unified intelligence across all CORA systems</p>
                    </div>
                    <div class="orchestration-controls">
                        <div class="status-indicator ${this.isActive ? 'active' : 'inactive'}">
                            <i class="fas fa-circle"></i>
                            <span>${this.isActive ? 'Active' : 'Inactive'}</span>
                        </div>
                        <button class="refresh-orchestration" onclick="intelligenceOrchestrator.refresh()">
                            <i class="fas fa-sync-alt"></i>
                        </button>
                    </div>
                </div>
                
                <div class="orchestration-content">
                    ${this.renderOrchestrationStatus()}
                    ${this.renderComponentCoordination()}
                    ${this.renderRelationalContext()}
                </div>
            </div>
        `;

        // Find the best location for orchestration panel
        const targetLocation = this.findOrchestrationLocation();
        if (targetLocation) {
            targetLocation.insertAdjacentHTML('beforeend', orchestrationHtml);
            this.injectStyles();
            this.setupOrchestrationHandlers();
        }
    }

    findOrchestrationLocation() {
        // Try to find the dashboard main area
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

        return document.body;
    }

    renderOrchestrationStatus() {
        if (!this.orchestrationData) {
            return `
                <div class="orchestration-loading">
                    <div class="loading-spinner"></div>
                    <p>Coordinating AI intelligence...</p>
                </div>
            `;
        }

        const orchestrationType = this.orchestrationData.orchestration_type;
        const typeDisplayMap = {
            'urgent_attention': { icon: '🚨', label: 'Urgent Attention Needed', color: '#ef4444' },
            'celebration': { icon: '🎉', label: 'Celebrating Success', color: '#22c55e' },
            'high_priority': { icon: '⚡', label: 'High Priority Items', color: '#f59e0b' },
            'general_insights': { icon: '💡', label: 'General Insights', color: '#667eea' },
            'steady_state': { icon: '✨', label: 'All Systems Optimal', color: '#22c55e' }
        };

        const typeInfo = typeDisplayMap[orchestrationType] || typeDisplayMap['general_insights'];

        return `
            <div class="orchestration-status">
                <div class="status-card" style="border-left: 4px solid ${typeInfo.color}">
                    <div class="status-icon">${typeInfo.icon}</div>
                    <div class="status-content">
                        <h4>${typeInfo.label}</h4>
                        <p>Current intelligence focus across all AI systems</p>
                        <div class="status-meta">
                            <span>Last updated: ${new Date(this.orchestrationData.timestamp).toLocaleTimeString()}</span>
                        </div>
                    </div>
                </div>
            </div>
        `;
    }

    renderComponentCoordination() {
        if (!this.orchestrationData?.components) return '';

        const components = this.orchestrationData.components;
        
        return `
            <div class="component-coordination">
                <h4>AI Component Coordination</h4>
                <div class="coordination-grid">
                    ${this.renderInsightMomentsCoordination(components.insight_moments)}
                    ${this.renderIntelligenceWidgetCoordination(components.intelligence_widget)}
                    ${this.renderPredictiveDashboardCoordination(components.predictive_dashboard)}
                    ${this.renderNotificationsCoordination(components.notifications)}
                </div>
            </div>
        `;
    }

    renderInsightMomentsCoordination(config) {
        if (!config) return '';

        return `
            <div class="component-card insight-moments-card">
                <div class="component-header">
                    <i class="fas fa-lightbulb"></i>
                    <span>Insight Moments</span>
                </div>
                <div class="component-body">
                    <div class="coordination-info">
                        <span>Display: ${config.display_style}</span>
                        <span>Insights: ${config.insights?.length || 0}</span>
                    </div>
                    ${config.insights && config.insights.length > 0 ? `
                        <div class="active-insights">
                            ${config.insights.slice(0, 2).map(insight => `
                                <div class="mini-insight ${insight.urgency}">
                                    <span class="insight-icon">${this.getInsightIcon(insight.type)}</span>
                                    <span class="insight-preview">${insight.message.substring(0, 50)}...</span>
                                </div>
                            `).join('')}
                        </div>
                    ` : ''}
                </div>
            </div>
        `;
    }

    renderIntelligenceWidgetCoordination(config) {
        if (!config) return '';

        return `
            <div class="component-card widget-card">
                <div class="component-header">
                    <i class="fas fa-tachometer-alt"></i>
                    <span>Intelligence Widget</span>
                </div>
                <div class="component-body">
                    <div class="coordination-info">
                        <span>Score: ${config.score}/100</span>
                        <span>State: ${config.visual_state}</span>
                    </div>
                    <div class="widget-preview">
                        <div class="mini-score-circle ${config.visual_state}">
                            <span class="score-number">${config.score}</span>
                        </div>
                        <div class="trend-indicator ${config.trend}">
                            ${config.attention_indicator ? '🔔' : '✓'}
                        </div>
                    </div>
                </div>
            </div>
        `;
    }

    renderPredictiveDashboardCoordination(config) {
        if (!config) return '';

        return `
            <div class="component-card predictive-card">
                <div class="component-header">
                    <i class="fas fa-crystal-ball"></i>
                    <span>Predictive Dashboard</span>
                </div>
                <div class="component-body">
                    <div class="coordination-info">
                        <span>Mode: ${config.highlight_mode}</span>
                        <span>Filter: ${config.urgency_filter}</span>
                    </div>
                    <div class="predictive-preview">
                        <div class="prediction-indicator ${config.highlight_mode}">
                            <i class="fas fa-forward"></i>
                        </div>
                    </div>
                </div>
            </div>
        `;
    }

    renderNotificationsCoordination(config) {
        if (!config) return '';

        return `
            <div class="component-card notifications-card">
                <div class="component-header">
                    <i class="fas fa-bell"></i>
                    <span>Notifications</span>
                </div>
                <div class="component-body">
                    <div class="coordination-info">
                        <span>Style: ${config.style}</span>
                        <span>Count: ${config.count}</span>
                    </div>
                    <div class="notification-preview">
                        <div class="preview-message">${config.preview_message}</div>
                    </div>
                </div>
            </div>
        `;
    }

    renderRelationalContext() {
        if (!this.orchestrationData?.relational_context) return '';

        const context = this.orchestrationData.relational_context;
        
        return `
            <div class="relational-context">
                <h4>Relational Memory & User Story</h4>
                <div class="context-grid">
                    <div class="context-card relationship-stage">
                        <div class="context-header">
                            <i class="fas fa-handshake"></i>
                            <span>Relationship Stage</span>
                        </div>
                        <div class="context-content">
                            <div class="stage-indicator ${context.user_relationship_stage}">
                                ${this.getRelationshipStageDisplay(context.user_relationship_stage)}
                            </div>
                        </div>
                    </div>
                    
                    <div class="context-card story-chapter">
                        <div class="context-header">
                            <i class="fas fa-book-open"></i>
                            <span>Current Chapter</span>
                        </div>
                        <div class="context-content">
                            <div class="chapter-display">
                                ${this.getChapterDisplay(context.current_chapter)}
                            </div>
                        </div>
                    </div>

                    ${context.care_signals && context.care_signals.length > 0 ? `
                        <div class="context-card care-signals">
                            <div class="context-header">
                                <i class="fas fa-heart"></i>
                                <span>Care Moments</span>
                            </div>
                            <div class="context-content">
                                <div class="care-list">
                                    ${context.care_signals.slice(0, 3).map(signal => `
                                        <div class="care-item">💙 ${signal}</div>
                                    `).join('')}
                                </div>
                            </div>
                        </div>
                    ` : ''}
                </div>
            </div>
        `;
    }

    getInsightIcon(type) {
        const iconMap = {
            'cash_flow_prediction': '💰',
            'vendor_optimization': '🔧',
            'weather_prediction': '🌧️',
            'material_prediction': '📦',
            'seasonal_prediction': '🍂'
        };
        return iconMap[type] || '💡';
    }

    getRelationshipStageDisplay(stage) {
        const stageMap = {
            'new_user': '👋 Getting Acquainted',
            'developing_trust': '🌱 Building Trust',
            'established_partnership': '🤝 Trusted Partner',
            'deep_collaboration': '💎 Deep Collaboration'
        };
        return stageMap[stage] || '👋 New Partnership';
    }

    getChapterDisplay(chapter) {
        const chapterMap = {
            'beginning': '📖 The Beginning',
            'steady_progress': '📈 Steady Progress',
            'challenge_and_opportunity': '⚡ Challenge & Opportunity',
            'triumph_and_recognition': '🏆 Triumph & Recognition',
            'transformation': '🦋 Transformation'
        };
        return chapterMap[chapter] || '📖 Unfolding Story';
    }

    setupOrchestrationHandlers() {
        // Add event listeners for orchestration controls
        const refreshBtn = document.querySelector('.refresh-orchestration');
        if (refreshBtn) {
            refreshBtn.addEventListener('click', () => this.refresh());
        }
    }

    async refresh() {
        const refreshIcon = document.querySelector('.refresh-orchestration i');
        if (refreshIcon) {
            refreshIcon.style.animation = 'spin 1s linear infinite';
        }

        await this.loadOrchestration();
        this.updateOrchestrationDisplay();

        if (refreshIcon) {
            refreshIcon.style.animation = '';
        }
    }

    updateOrchestrationDisplay() {
        const content = document.querySelector('.orchestration-content');
        if (content) {
            content.innerHTML = `
                ${this.renderOrchestrationStatus()}
                ${this.renderComponentCoordination()}
                ${this.renderRelationalContext()}
            `;
        }
    }

    startOrchestrationEngine() {
        // Refresh orchestration every 5 minutes
        this.updateInterval = setInterval(() => {
            this.refresh();
        }, 5 * 60 * 1000);
    }

    injectStyles() {
        if (document.getElementById('intelligence-orchestrator-styles')) return;

        const styles = `
            <style id="intelligence-orchestrator-styles">
                .orchestration-panel {
                    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                    border-radius: 20px;
                    padding: 24px;
                    margin: 20px 0;
                    color: white;
                    box-shadow: 0 12px 40px rgba(102, 126, 234, 0.3);
                }

                .orchestration-header {
                    display: flex;
                    justify-content: space-between;
                    align-items: center;
                    margin-bottom: 24px;
                    padding-bottom: 16px;
                    border-bottom: 1px solid rgba(255, 255, 255, 0.2);
                }

                .header-content h3 {
                    margin: 0 0 4px 0;
                    font-size: 24px;
                    font-weight: 700;
                    display: flex;
                    align-items: center;
                    gap: 8px;
                }

                .header-content p {
                    margin: 0;
                    opacity: 0.8;
                    font-size: 14px;
                }

                .orchestration-controls {
                    display: flex;
                    align-items: center;
                    gap: 12px;
                }

                .status-indicator {
                    display: flex;
                    align-items: center;
                    gap: 6px;
                    padding: 6px 12px;
                    border-radius: 12px;
                    font-size: 12px;
                    font-weight: 600;
                }

                .status-indicator.active {
                    background: rgba(34, 197, 94, 0.3);
                    border: 1px solid rgba(34, 197, 94, 0.5);
                    color: #22c55e;
                }

                .status-indicator.inactive {
                    background: rgba(239, 68, 68, 0.3);
                    border: 1px solid rgba(239, 68, 68, 0.5);
                    color: #ef4444;
                }

                .refresh-orchestration {
                    background: rgba(255, 255, 255, 0.2);
                    border: 1px solid rgba(255, 255, 255, 0.3);
                    color: white;
                    padding: 8px 12px;
                    border-radius: 8px;
                    cursor: pointer;
                    transition: all 0.3s ease;
                }

                .refresh-orchestration:hover {
                    background: rgba(255, 255, 255, 0.3);
                }

                .orchestration-loading {
                    text-align: center;
                    padding: 40px;
                    opacity: 0.8;
                }

                .loading-spinner {
                    width: 32px;
                    height: 32px;
                    border: 3px solid rgba(255, 255, 255, 0.3);
                    border-top: 3px solid white;
                    border-radius: 50%;
                    animation: spin 1s linear infinite;
                    margin: 0 auto 16px;
                }

                .status-card {
                    background: rgba(255, 255, 255, 0.15);
                    border-radius: 12px;
                    padding: 16px;
                    display: flex;
                    align-items: center;
                    gap: 16px;
                    margin-bottom: 20px;
                }

                .status-icon {
                    font-size: 32px;
                }

                .status-content h4 {
                    margin: 0 0 4px 0;
                    font-size: 18px;
                }

                .status-content p {
                    margin: 0 0 8px 0;
                    opacity: 0.8;
                    font-size: 14px;
                }

                .status-meta {
                    font-size: 12px;
                    opacity: 0.6;
                }

                .component-coordination h4,
                .relational-context h4 {
                    margin: 0 0 16px 0;
                    font-size: 16px;
                    font-weight: 600;
                    opacity: 0.9;
                }

                .coordination-grid,
                .context-grid {
                    display: grid;
                    grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
                    gap: 16px;
                    margin-bottom: 24px;
                }

                .component-card,
                .context-card {
                    background: rgba(255, 255, 255, 0.1);
                    border: 1px solid rgba(255, 255, 255, 0.2);
                    border-radius: 8px;
                    padding: 16px;
                    transition: all 0.3s ease;
                }

                .component-card:hover,
                .context-card:hover {
                    background: rgba(255, 255, 255, 0.15);
                    border-color: rgba(255, 255, 255, 0.3);
                }

                .component-header,
                .context-header {
                    display: flex;
                    align-items: center;
                    gap: 8px;
                    margin-bottom: 12px;
                    font-weight: 600;
                    font-size: 14px;
                }

                .coordination-info {
                    display: flex;
                    flex-direction: column;
                    gap: 4px;
                    font-size: 12px;
                    opacity: 0.8;
                    margin-bottom: 8px;
                }

                .active-insights {
                    display: flex;
                    flex-direction: column;
                    gap: 6px;
                }

                .mini-insight {
                    display: flex;
                    align-items: center;
                    gap: 6px;
                    padding: 4px 8px;
                    border-radius: 6px;
                    font-size: 11px;
                    background: rgba(255, 255, 255, 0.1);
                }

                .mini-insight.high {
                    border-left: 2px solid #ef4444;
                }

                .mini-insight.medium {
                    border-left: 2px solid #f59e0b;
                }

                .widget-preview {
                    display: flex;
                    align-items: center;
                    justify-content: space-between;
                    gap: 12px;
                }

                .mini-score-circle {
                    width: 40px;
                    height: 40px;
                    border-radius: 50%;
                    display: flex;
                    align-items: center;
                    justify-content: center;
                    font-weight: 600;
                    font-size: 12px;
                    border: 2px solid rgba(255, 255, 255, 0.3);
                }

                .mini-score-circle.pulse_orange {
                    animation: pulse-orange 2s infinite;
                }

                @keyframes pulse-orange {
                    0%, 100% { border-color: rgba(245, 158, 11, 0.5); }
                    50% { border-color: rgba(245, 158, 11, 1); }
                }

                .predictive-preview,
                .notification-preview {
                    display: flex;
                    align-items: center;
                    justify-content: center;
                    padding: 8px;
                }

                .prediction-indicator {
                    padding: 8px;
                    border-radius: 50%;
                    background: rgba(255, 255, 255, 0.2);
                }

                .preview-message {
                    font-size: 11px;
                    opacity: 0.8;
                    text-align: center;
                }

                .stage-indicator,
                .chapter-display {
                    text-align: center;
                    padding: 8px;
                    background: rgba(255, 255, 255, 0.1);
                    border-radius: 6px;
                    font-size: 13px;
                }

                .care-list {
                    display: flex;
                    flex-direction: column;
                    gap: 4px;
                }

                .care-item {
                    font-size: 11px;
                    opacity: 0.9;
                    padding: 2px 0;
                }

                @keyframes spin {
                    0% { transform: rotate(0deg); }
                    100% { transform: rotate(360deg); }
                }

                @media (max-width: 768px) {
                    .orchestration-panel {
                        margin: 16px 0;
                        padding: 16px;
                    }

                    .orchestration-header {
                        flex-direction: column;
                        gap: 12px;
                        align-items: flex-start;
                    }

                    .orchestration-controls {
                        align-self: stretch;
                        justify-content: space-between;
                    }

                    .coordination-grid,
                    .context-grid {
                        grid-template-columns: 1fr;
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
        
        const panel = document.getElementById('intelligence-orchestration');
        if (panel) {
            panel.remove();
        }
    }
}

// Global instance
let intelligenceOrchestrator;

// Initialize when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
    // Only initialize on dashboard pages
    if (window.location.pathname.includes('/dashboard') || 
        document.querySelector('.dashboard-main')) {
        intelligenceOrchestrator = new IntelligenceOrchestrator();
    }
});

// Export for global access
window.intelligenceOrchestrator = intelligenceOrchestrator;