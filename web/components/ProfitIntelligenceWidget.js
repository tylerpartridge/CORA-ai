// Profit Intelligence Widget Component
// Displays intelligence score, key metrics, and quick actions

class ProfitIntelligenceWidget {
    constructor(containerId) {
        this.container = document.getElementById(containerId);
        this.data = null;
        this.init();
    }

    async init() {
        await this.loadData();
        this.render();
        this.attachEventListeners();
    }

    async loadData() {
        try {
            const response = await fetch('/api/profit-intelligence/profit-intelligence-summary');
            this.data = await response.json();
        } catch (error) {
            // console.error('Error loading profit intelligence data:', error);
            this.data = this.getMockData();
        }
    }

    getMockData() {
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

    getScoreColor(score) {
        if (score >= 90) return '#00FF88'; // A grade - green
        if (score >= 80) return '#FFD700'; // B grade - gold
        if (score >= 70) return '#FFA500'; // C grade - orange
        return '#FF4444'; // D grade - red
    }

    getScoreGradient(score) {
        const color = this.getScoreColor(score);
        return `linear-gradient(135deg, ${color}20, ${color}40)`;
    }

    render() {
        if (!this.container) return;

        this.container.innerHTML = `
            <div class="profit-intelligence-widget">
                <div class="widget-header">
                    <div class="header-left">
                        <i class="fas fa-brain" style="color: #8B00FF; font-size: 1.5rem;"></i>
                        <h3>Profit Intelligence</h3>
                    </div>
                    <div class="header-right">
                        <span class="last-updated">Updated 2 min ago</span>
                    </div>
                </div>

                <div class="widget-content">
                    <!-- Intelligence Score Section -->
                    <div class="score-section">
                        <div class="score-display" style="background: ${this.getScoreGradient(this.data.intelligenceScore)}">
                            <div class="score-circle" style="border-color: ${this.getScoreColor(this.data.intelligenceScore)}">
                                <span class="score-number">${this.data.intelligenceScore}</span>
                                <span class="score-grade">${this.data.letterGrade}</span>
                            </div>
                            <div class="score-label">
                                <h4>Intelligence Score</h4>
                                <p>Overall business health</p>
                            </div>
                        </div>
                    </div>

                    <!-- Key Metrics Section -->
                    <div class="metrics-section">
                        <div class="metric-card">
                            <div class="metric-icon">
                                <i class="fas fa-dollar-sign"></i>
                            </div>
                            <div class="metric-content">
                                <span class="metric-value">$${(this.data.monthlySavingsPotential / 1000).toFixed(1)}k</span>
                                <span class="metric-label">Monthly Savings Potential</span>
                            </div>
                        </div>

                        <div class="metric-card">
                            <div class="metric-icon ${this.data.costTrend < 0 ? 'positive' : 'negative'}">
                                <i class="fas fa-chart-line"></i>
                            </div>
                            <div class="metric-content">
                                <span class="metric-value ${this.data.costTrend < 0 ? 'positive' : 'negative'}">
                                    ${this.data.costTrend > 0 ? '+' : ''}${this.data.costTrend}%
                                </span>
                                <span class="metric-label">Cost Trend</span>
                            </div>
                        </div>

                        <div class="metric-card">
                            <div class="metric-icon">
                                <i class="fas fa-users"></i>
                            </div>
                            <div class="metric-content">
                                <span class="metric-value">${this.data.vendorCount}</span>
                                <span class="metric-label">Active Vendors</span>
                            </div>
                        </div>
                    </div>

                    <!-- Alerts Section -->
                    <div class="alerts-section">
                        <h4>Intelligence Alerts</h4>
                        <div class="alerts-list">
                            ${this.data.alerts.map(alert => `
                                <div class="alert-item ${alert.type}">
                                    <i class="fas fa-${alert.type === 'warning' ? 'exclamation-triangle' : 'check-circle'}"></i>
                                    <span>${alert.message}</span>
                                </div>
                            `).join('')}
                        </div>
                    </div>

                    <!-- Quick Actions -->
                    <div class="actions-section">
                        <button class="action-btn primary" data-action="view-details">
                            <i class="fas fa-chart-bar"></i>
                            View Details
                        </button>
                        <button class="action-btn secondary" data-action="export-report">
                            <i class="fas fa-download"></i>
                            Export Report
                        </button>
                    </div>
                </div>
            </div>
        `;
    }

    attachEventListeners() {
        const viewDetailsBtn = this.container.querySelector('[data-action="view-details"]');
        const exportReportBtn = this.container.querySelector('[data-action="export-report"]');

        if (viewDetailsBtn) {
            viewDetailsBtn.addEventListener('click', () => {
                window.location.href = '/profit-intelligence';
            });
        }

        if (exportReportBtn) {
            exportReportBtn.addEventListener('click', () => {
                this.exportReport();
            });
        }
    }

    async exportReport() {
        try {
            const response = await fetch('/api/profit-intelligence/export-report', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                }
            });
            
            if (response.ok) {
                const blob = await response.blob();
                const url = window.URL.createObjectURL(blob);
                const a = document.createElement('a');
                a.href = url;
                a.download = `profit-intelligence-report-${new Date().toISOString().split('T')[0]}.pdf`;
                a.click();
                window.URL.revokeObjectURL(url);
            }
        } catch (error) {
            // console.error('Error exporting report:', error);
            alert('Failed to export report. Please try again.');
        }
    }

    updateData(newData) {
        this.data = { ...this.data, ...newData };
        this.render();
    }
}

// CSS Styles for the widget
const widgetStyles = `
    <style>
        .profit-intelligence-widget {
            background: linear-gradient(135deg, #1a1a1a 0%, #2d3748 100%);
            border: 2px solid rgba(139, 0, 255, 0.3);
            border-radius: 12px;
            padding: 1.5rem;
            box-shadow: 0 8px 32px rgba(139, 0, 255, 0.1);
            transition: all 0.3s ease;
        }

        .profit-intelligence-widget:hover {
            border-color: rgba(139, 0, 255, 0.5);
            box-shadow: 0 12px 40px rgba(139, 0, 255, 0.2);
        }

        .widget-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 1.5rem;
        }

        .header-left {
            display: flex;
            align-items: center;
            gap: 0.75rem;
        }

        .header-left h3 {
            color: #ffffff;
            font-size: 1.25rem;
            font-weight: 600;
            margin: 0;
        }

        .last-updated {
            color: #a0aec0;
            font-size: 0.8rem;
        }

        .score-section {
            margin-bottom: 1.5rem;
        }

        .score-display {
            display: flex;
            align-items: center;
            gap: 1rem;
            padding: 1rem;
            border-radius: 8px;
        }

        .score-circle {
            width: 80px;
            height: 80px;
            border: 4px solid;
            border-radius: 50%;
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            background: rgba(255, 255, 255, 0.1);
        }

        .score-number {
            font-size: 1.5rem;
            font-weight: 700;
            color: #ffffff;
        }

        .score-grade {
            font-size: 0.9rem;
            font-weight: 600;
            color: #ffffff;
        }

        .score-label h4 {
            color: #ffffff;
            margin: 0 0 0.25rem 0;
            font-size: 1.1rem;
        }

        .score-label p {
            color: #a0aec0;
            margin: 0;
            font-size: 0.9rem;
        }

        .metrics-section {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(120px, 1fr));
            gap: 1rem;
            margin-bottom: 1.5rem;
        }

        .metric-card {
            background: rgba(255, 255, 255, 0.05);
            border: 1px solid rgba(139, 0, 255, 0.2);
            border-radius: 8px;
            padding: 1rem;
            display: flex;
            align-items: center;
            gap: 0.75rem;
            transition: all 0.3s ease;
        }

        .metric-card:hover {
            background: rgba(255, 255, 255, 0.1);
            border-color: rgba(139, 0, 255, 0.4);
        }

        .metric-icon {
            width: 40px;
            height: 40px;
            background: linear-gradient(135deg, #8B00FF, #A020F0);
            border-radius: 8px;
            display: flex;
            align-items: center;
            justify-content: center;
            color: #ffffff;
            font-size: 1rem;
        }

        .metric-icon.positive {
            background: linear-gradient(135deg, #00FF88, #00CC6A);
        }

        .metric-icon.negative {
            background: linear-gradient(135deg, #FF4444, #CC3333);
        }

        .metric-content {
            display: flex;
            flex-direction: column;
        }

        .metric-value {
            color: #ffffff;
            font-size: 1.1rem;
            font-weight: 600;
        }

        .metric-value.positive {
            color: #00FF88;
        }

        .metric-value.negative {
            color: #FF4444;
        }

        .metric-label {
            color: #a0aec0;
            font-size: 0.8rem;
        }

        .alerts-section {
            margin-bottom: 1.5rem;
        }

        .alerts-section h4 {
            color: #ffffff;
            margin: 0 0 1rem 0;
            font-size: 1rem;
        }

        .alerts-list {
            display: flex;
            flex-direction: column;
            gap: 0.5rem;
        }

        .alert-item {
            display: flex;
            align-items: center;
            gap: 0.5rem;
            padding: 0.5rem;
            border-radius: 4px;
            font-size: 0.9rem;
        }

        .alert-item.warning {
            background: rgba(255, 193, 7, 0.1);
            color: #FFC107;
            border: 1px solid rgba(255, 193, 7, 0.3);
        }

        .alert-item.success {
            background: rgba(0, 255, 136, 0.1);
            color: #00FF88;
            border: 1px solid rgba(0, 255, 136, 0.3);
        }

        .actions-section {
            display: flex;
            gap: 1rem;
        }

        .action-btn {
            flex: 1;
            padding: 0.75rem 1rem;
            border: none;
            border-radius: 6px;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.3s ease;
            display: flex;
            align-items: center;
            justify-content: center;
            gap: 0.5rem;
        }

        .action-btn.primary {
            background: linear-gradient(135deg, #8B00FF, #A020F0);
            color: #ffffff;
        }

        .action-btn.primary:hover {
            background: linear-gradient(135deg, #A020F0, #8B00FF);
            transform: translateY(-2px);
        }

        .action-btn.secondary {
            background: rgba(255, 255, 255, 0.1);
            color: #ffffff;
            border: 1px solid rgba(139, 0, 255, 0.3);
        }

        .action-btn.secondary:hover {
            background: rgba(255, 255, 255, 0.2);
            border-color: rgba(139, 0, 255, 0.5);
        }

        @media (max-width: 768px) {
            .profit-intelligence-widget {
                padding: 1rem;
            }

            .metrics-section {
                grid-template-columns: 1fr;
            }

            .actions-section {
                flex-direction: column;
            }

            .score-display {
                flex-direction: column;
                text-align: center;
            }
        }
    </style>
`;

// Inject styles into document
if (!document.getElementById('profit-intelligence-styles')) {
    const styleSheet = document.createElement('style');
    styleSheet.id = 'profit-intelligence-styles';
    styleSheet.textContent = widgetStyles;
    document.head.appendChild(styleSheet);
}

// Export for use in other modules
window.ProfitIntelligenceWidget = ProfitIntelligenceWidget; 