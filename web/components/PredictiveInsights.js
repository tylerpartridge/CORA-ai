/**
 * Predictive Insights Component
 * 
 * Displays proactive predictions and anticipatory insights to help contractors
 * stay ahead of their business needs.
 * 
 * Philosophy: Show the future, not just the present
 */

class PredictiveInsights {
    constructor() {
        this.predictions = [];
        this.container = null;
        this.updateInterval = null;
        this.displayedPredictions = new Set();
        this.init();
    }

    async init() {
        await this.loadPredictions();
        this.createPredictiveUI();
        this.startPredictiveEngine();
    }

    async loadPredictions() {
        try {
            const response = await fetch('/api/predictions?days_ahead=7');
            if (response.ok) {
                const data = await response.json();
                this.predictions = data.predictions || [];
            }
        } catch (error) {
            // console.log('Using demo predictions for development');
            this.predictions = this.getDemoPredictions();
        }
    }

    getDemoPredictions() {
        return [
            {
                id: 'cash_flow_alert_20',
                type: 'cash_flow_prediction',
                urgency: 'high',
                confidence: 87,
                days_ahead: 3,
                message: '💰 Cash flow heads up: You typically spend $3,200 around the 20th. That\'s in 3 days - consider preparing.',
                predicted_amount: 3200,
                action: {
                    type: 'prepare_cash_flow',
                    suggestions: [
                        'Review current cash position',
                        'Send invoice reminders to clients',
                        'Consider delaying non-essential purchases'
                    ]
                }
            },
            {
                id: 'material_restock_lumber',
                type: 'material_prediction',
                urgency: 'medium',
                confidence: 82,
                days_ahead: 5,
                message: '🔧 Lumber restock: Based on your pattern, you typically reorder every 14 days. It\'s been 12 days since your last purchase.',
                category: 'Lumber',
                action: {
                    type: 'plan_purchase',
                    suggestions: [
                        'Review current lumber inventory',
                        'Check with preferred vendors for pricing',
                        'Consider bulk purchases for better rates'
                    ]
                }
            },
            {
                id: 'weather_rain_2',
                type: 'weather_prediction',
                urgency: 'medium',
                confidence: 85,
                days_ahead: 2,
                message: '🌧️ Weather alert: 85% chance of rain in 2 days. Consider adjusting outdoor work schedules.',
                weather_type: 'rain',
                action: {
                    type: 'schedule_adjustment',
                    suggestions: [
                        'Move outdoor work to earlier in week',
                        'Notify clients of potential delays',
                        'Prepare indoor alternatives'
                    ]
                }
            },
            {
                id: 'vendor_price_increase_home_depot',
                type: 'vendor_prediction',
                urgency: 'high',
                confidence: 90,
                days_ahead: 0,
                message: '📈 Vendor alert: Home Depot prices are trending up 18.5%. Consider stocking up or finding alternatives before further increases.',
                vendor: 'Home Depot',
                price_trend: 18.5,
                action: {
                    type: 'vendor_optimization',
                    suggestions: [
                        'Stock up on essentials from Home Depot',
                        'Research alternative suppliers',
                        'Negotiate volume discounts'
                    ]
                }
            },
            {
                id: 'seasonal_trend_9',
                type: 'seasonal_prediction',
                urgency: 'medium',
                confidence: 75,
                days_ahead: 7,
                message: '🍂 Winter prep: Indoor project demand increases in October. Pivot marketing toward interior work.',
                action: {
                    type: 'seasonal_opportunity',
                    suggestions: [
                        'Review historical seasonal patterns',
                        'Adjust marketing and pricing strategies',
                        'Plan material procurement timing'
                    ]
                }
            }
        ];
    }

    createPredictiveUI() {
        // Create main predictions dashboard
        const predictionsHtml = `
            <div id="predictive-insights-dashboard" class="predictions-dashboard">
                <div class="predictions-header">
                    <div class="header-content">
                        <h3><i class="fas fa-crystal-ball"></i> Predictive Insights</h3>
                        <p>AI-powered foresight for your business</p>
                    </div>
                    <div class="prediction-controls">
                        <select id="prediction-filter" class="filter-select">
                            <option value="all">All Predictions</option>
                            <option value="cash_flow_prediction">Cash Flow</option>
                            <option value="material_prediction">Materials</option>
                            <option value="weather_prediction">Weather</option>
                            <option value="vendor_prediction">Vendors</option>
                            <option value="seasonal_prediction">Seasonal</option>
                        </select>
                        <button class="refresh-btn" onclick="predictiveInsights.refresh()">
                            <i class="fas fa-sync-alt"></i>
                        </button>
                    </div>
                </div>
                <div class="predictions-timeline">
                    <div class="timeline-header">
                        <span class="timeline-label">Next 7 Days</span>
                        <div class="timeline-indicators">
                            <div class="urgency-legend">
                                <span class="legend-item high">High Priority</span>
                                <span class="legend-item medium">Medium Priority</span>
                                <span class="legend-item low">Low Priority</span>
                            </div>
                        </div>
                    </div>
                    <div id="predictions-list" class="predictions-list">
                        <!-- Predictions will be populated here -->
                    </div>
                </div>
            </div>
        `;

        // Find the best location for predictions dashboard
        const targetLocation = this.findDashboardLocation();
        if (targetLocation) {
            targetLocation.insertAdjacentHTML('beforeend', predictionsHtml);
            this.container = document.getElementById('predictive-insights-dashboard');
            this.injectStyles();
            this.renderPredictions();
            this.setupEventHandlers();
        }
    }

    findDashboardLocation() {
        // Try to find a good spot in the dashboard
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

    renderPredictions() {
        const listContainer = document.getElementById('predictions-list');
        if (!listContainer) return;

        // Group predictions by days ahead
        const groupedPredictions = this.groupPredictionsByTime();
        
        let html = '';
        
        for (const [timeGroup, preds] of Object.entries(groupedPredictions)) {
            if (preds.length === 0) continue;
            
            html += `
                <div class="time-group">
                    <div class="time-group-header">${timeGroup}</div>
                    <div class="time-group-predictions">
                        ${preds.map(pred => this.renderPrediction(pred)).join('')}
                    </div>
                </div>
            `;
        }

        if (html === '') {
            html = `
                <div class="no-predictions">
                    <div class="no-predictions-icon">🔮</div>
                    <h4>All Clear Ahead!</h4>
                    <p>No urgent predictions for the next 7 days. Your business is running smoothly.</p>
                </div>
            `;
        }

        listContainer.innerHTML = html;
    }

    groupPredictionsByTime() {
        const groups = {
            'Today': [],
            'Tomorrow': [],
            'This Week': [],
            'Next Week': []
        };

        for (const prediction of this.predictions) {
            const daysAhead = prediction.days_ahead;
            
            if (daysAhead === 0) {
                groups['Today'].push(prediction);
            } else if (daysAhead === 1) {
                groups['Tomorrow'].push(prediction);
            } else if (daysAhead <= 7) {
                groups['This Week'].push(prediction);
            } else {
                groups['Next Week'].push(prediction);
            }
        }

        return groups;
    }

    renderPrediction(prediction) {
        const urgencyClass = `prediction-${prediction.urgency}`;
        const iconMap = {
            'cash_flow_prediction': '💰',
            'material_prediction': '🔧', 
            'weather_prediction': '🌧️',
            'vendor_prediction': '📈',
            'seasonal_prediction': '🍂'
        };

        const icon = iconMap[prediction.type] || '💡';
        const timeText = this.formatTimeAhead(prediction.days_ahead);

        return `
            <div class="prediction-card ${urgencyClass}" data-prediction-id="${prediction.id}">
                <div class="prediction-header">
                    <div class="prediction-icon">${icon}</div>
                    <div class="prediction-meta">
                        <span class="prediction-time">${timeText}</span>
                        <span class="prediction-confidence">${prediction.confidence}% confident</span>
                    </div>
                    <div class="prediction-urgency">
                        <span class="urgency-badge ${prediction.urgency}">${prediction.urgency}</span>
                    </div>
                </div>
                <div class="prediction-content">
                    <div class="prediction-message">${prediction.message}</div>
                    ${this.renderActionSuggestions(prediction)}
                </div>
                <div class="prediction-actions">
                    <button class="action-btn primary" onclick="predictiveInsights.takeSuggestedAction('${prediction.id}')">
                        Take Action
                    </button>
                    <button class="action-btn secondary" onclick="predictiveInsights.acknowledgePrediction('${prediction.id}')">
                        Acknowledge
                    </button>
                    <button class="action-btn dismiss" onclick="predictiveInsights.dismissPrediction('${prediction.id}')">
                        Dismiss
                    </button>
                </div>
            </div>
        `;
    }

    renderActionSuggestions(prediction) {
        if (!prediction.action || !prediction.action.suggestions) {
            return '';
        }

        return `
            <div class="action-suggestions">
                <div class="suggestions-header">Suggested Actions:</div>
                <ul class="suggestions-list">
                    ${prediction.action.suggestions.map(suggestion => 
                        `<li class="suggestion-item">${suggestion}</li>`
                    ).join('')}
                </ul>
            </div>
        `;
    }

    formatTimeAhead(days) {
        if (days === 0) return 'Today';
        if (days === 1) return 'Tomorrow';
        if (days <= 7) return `In ${days} days`;
        return `In ${days} days`;
    }

    setupEventHandlers() {
        // Filter dropdown
        const filterSelect = document.getElementById('prediction-filter');
        if (filterSelect) {
            filterSelect.addEventListener('change', (e) => {
                this.filterPredictions(e.target.value);
            });
        }
    }

    filterPredictions(filterType) {
        if (filterType === 'all') {
            // Show all predictions
            document.querySelectorAll('.prediction-card').forEach(card => {
                card.style.display = 'block';
            });
        } else {
            // Filter by type
            document.querySelectorAll('.prediction-card').forEach(card => {
                const predictionId = card.dataset.predictionId;
                const prediction = this.predictions.find(p => p.id === predictionId);
                
                if (prediction && prediction.type === filterType) {
                    card.style.display = 'block';
                } else {
                    card.style.display = 'none';
                }
            });
        }
    }

    async takeSuggestedAction(predictionId) {
        const prediction = this.predictions.find(p => p.id === predictionId);
        if (!prediction) return;

        // Show action modal with specific suggestions
        this.showActionModal(prediction);
        
        // Track action
        this.trackPredictionInteraction(predictionId, 'action_taken');
    }

    async acknowledgePrediction(predictionId) {
        try {
            const response = await fetch(`/api/predictions/${predictionId}/acknowledge`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    action_taken: 'acknowledged'
                })
            });

            if (response.ok) {
                // Remove prediction from view
                const predictionCard = document.querySelector(`[data-prediction-id="${predictionId}"]`);
                if (predictionCard) {
                    predictionCard.style.opacity = '0.5';
                    predictionCard.style.pointerEvents = 'none';
                    
                    // Add acknowledgment indicator
                    const ackIndicator = document.createElement('div');
                    ackIndicator.className = 'acknowledgment-indicator';
                    ackIndicator.innerHTML = '✓ Acknowledged';
                    predictionCard.appendChild(ackIndicator);
                }
            }
        } catch (error) {
            // console.error('Error acknowledging prediction:', error);
        }
    }

    dismissPrediction(predictionId) {
        const predictionCard = document.querySelector(`[data-prediction-id="${predictionId}"]`);
        if (predictionCard) {
            predictionCard.style.transform = 'translateX(100%)';
            predictionCard.style.opacity = '0';
            
            setTimeout(() => {
                predictionCard.remove();
            }, 300);
        }
        
        // Remove from predictions array
        this.predictions = this.predictions.filter(p => p.id !== predictionId);
        
        this.trackPredictionInteraction(predictionId, 'dismissed');
    }

    showActionModal(prediction) {
        const modalHtml = `
            <div id="prediction-action-modal" class="prediction-modal">
                <div class="modal-backdrop" onclick="document.getElementById('prediction-action-modal').remove()"></div>
                <div class="modal-content">
                    <div class="modal-header">
                        <h3>Take Action: ${prediction.type.replace('_', ' ')}</h3>
                        <button onclick="document.getElementById('prediction-action-modal').remove()">×</button>
                    </div>
                    <div class="modal-body">
                        <div class="prediction-summary">
                            <p>${prediction.message}</p>
                        </div>
                        <div class="action-checklist">
                            <h4>Recommended Actions:</h4>
                            ${prediction.action.suggestions.map((suggestion, index) => `
                                <div class="checklist-item">
                                    <input type="checkbox" id="action-${index}" />
                                    <label for="action-${index}">${suggestion}</label>
                                </div>
                            `).join('')}
                        </div>
                    </div>
                    <div class="modal-actions">
                        <button class="action-btn primary" onclick="predictiveInsights.completeActionPlan('${prediction.id}')">
                            Mark Complete
                        </button>
                        <button class="action-btn secondary" onclick="document.getElementById('prediction-action-modal').remove()">
                            Close
                        </button>
                    </div>
                </div>
            </div>
        `;

        document.body.insertAdjacentHTML('beforeend', modalHtml);
    }

    completeActionPlan(predictionId) {
        // Get checked items
        const checkedItems = document.querySelectorAll('#prediction-action-modal input[type="checkbox"]:checked');
        const completedActions = Array.from(checkedItems).map(cb => cb.nextElementSibling.textContent);

        // Acknowledge with completed actions
        this.acknowledgePrediction(predictionId);
        
        // Close modal
        document.getElementById('prediction-action-modal').remove();
        
        // Show success message
        this.showSuccessMessage(`Great! You've taken action on this prediction. CORA will learn from your response.`);
    }

    showSuccessMessage(message) {
        const successHtml = `
            <div class="success-toast">
                <div class="toast-icon">✅</div>
                <div class="toast-message">${message}</div>
            </div>
        `;

        document.body.insertAdjacentHTML('beforeend', successHtml);
        
        setTimeout(() => {
            document.querySelector('.success-toast').remove();
        }, 3000);
    }

    trackPredictionInteraction(predictionId, interactionType) {
        try {
            fetch(`/api/predictions/${predictionId}/acknowledge`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    action_taken: interactionType,
                    timestamp: Date.now()
                })
            });
        } catch (error) {
            // console.log('Analytics tracking failed:', error);
        }
    }

    async refresh() {
        const refreshBtn = document.querySelector('.refresh-btn i');
        if (refreshBtn) {
            refreshBtn.style.animation = 'spin 1s linear infinite';
        }

        await this.loadPredictions();
        this.renderPredictions();

        if (refreshBtn) {
            refreshBtn.style.animation = '';
        }
    }

    startPredictiveEngine() {
        // Refresh predictions every 10 minutes
        this.updateInterval = setInterval(() => {
            this.refresh();
        }, 10 * 60 * 1000);
    }

    injectStyles() {
        if (document.getElementById('predictive-insights-styles')) return;

        const styles = `
            <style id="predictive-insights-styles">
                .predictions-dashboard {
                    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                    border-radius: 20px;
                    padding: 24px;
                    margin: 20px 0;
                    color: white;
                    box-shadow: 0 12px 40px rgba(102, 126, 234, 0.3);
                }

                .predictions-header {
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

                .prediction-controls {
                    display: flex;
                    gap: 12px;
                    align-items: center;
                }

                .filter-select {
                    background: rgba(255, 255, 255, 0.2);
                    border: 1px solid rgba(255, 255, 255, 0.3);
                    color: white;
                    padding: 8px 12px;
                    border-radius: 8px;
                    font-size: 14px;
                }

                .filter-select option {
                    background: #667eea;
                    color: white;
                }

                .refresh-btn {
                    background: rgba(255, 255, 255, 0.2);
                    border: 1px solid rgba(255, 255, 255, 0.3);
                    color: white;
                    padding: 8px 12px;
                    border-radius: 8px;
                    cursor: pointer;
                    transition: all 0.3s ease;
                }

                .refresh-btn:hover {
                    background: rgba(255, 255, 255, 0.3);
                }

                @keyframes spin {
                    0% { transform: rotate(0deg); }
                    100% { transform: rotate(360deg); }
                }

                .timeline-header {
                    display: flex;
                    justify-content: space-between;
                    align-items: center;
                    margin-bottom: 16px;
                }

                .timeline-label {
                    font-size: 16px;
                    font-weight: 600;
                    opacity: 0.9;
                }

                .urgency-legend {
                    display: flex;
                    gap: 12px;
                    font-size: 12px;
                }

                .legend-item {
                    padding: 4px 8px;
                    border-radius: 12px;
                    font-weight: 500;
                }

                .legend-item.high {
                    background: rgba(239, 68, 68, 0.3);
                    border: 1px solid rgba(239, 68, 68, 0.5);
                }

                .legend-item.medium {
                    background: rgba(245, 158, 11, 0.3);
                    border: 1px solid rgba(245, 158, 11, 0.5);
                }

                .legend-item.low {
                    background: rgba(34, 197, 94, 0.3);
                    border: 1px solid rgba(34, 197, 94, 0.5);
                }

                .time-group {
                    margin-bottom: 20px;
                }

                .time-group-header {
                    font-size: 14px;
                    font-weight: 600;
                    opacity: 0.8;
                    margin-bottom: 12px;
                    padding-left: 8px;
                }

                .time-group-predictions {
                    display: flex;
                    flex-direction: column;
                    gap: 12px;
                }

                .prediction-card {
                    background: rgba(255, 255, 255, 0.15);
                    border: 1px solid rgba(255, 255, 255, 0.2);
                    border-radius: 12px;
                    padding: 16px;
                    transition: all 0.3s ease;
                    backdrop-filter: blur(10px);
                }

                .prediction-card:hover {
                    background: rgba(255, 255, 255, 0.2);
                    border-color: rgba(255, 255, 255, 0.4);
                }

                .prediction-card.prediction-high {
                    border-left: 4px solid #ef4444;
                }

                .prediction-card.prediction-medium {
                    border-left: 4px solid #f59e0b;
                }

                .prediction-card.prediction-low {
                    border-left: 4px solid #22c55e;
                }

                .prediction-header {
                    display: flex;
                    justify-content: space-between;
                    align-items: center;
                    margin-bottom: 12px;
                }

                .prediction-icon {
                    font-size: 20px;
                }

                .prediction-meta {
                    flex: 1;
                    margin-left: 12px;
                    display: flex;
                    flex-direction: column;
                    gap: 2px;
                }

                .prediction-time {
                    font-size: 13px;
                    font-weight: 600;
                }

                .prediction-confidence {
                    font-size: 11px;
                    opacity: 0.7;
                }

                .urgency-badge {
                    padding: 4px 8px;
                    border-radius: 12px;
                    font-size: 10px;
                    font-weight: 600;
                    text-transform: uppercase;
                }

                .urgency-badge.high {
                    background: rgba(239, 68, 68, 0.3);
                    color: #ef4444;
                }

                .urgency-badge.medium {
                    background: rgba(245, 158, 11, 0.3);
                    color: #f59e0b;
                }

                .urgency-badge.low {
                    background: rgba(34, 197, 94, 0.3);
                    color: #22c55e;
                }

                .prediction-message {
                    font-size: 14px;
                    line-height: 1.5;
                    margin-bottom: 12px;
                }

                .action-suggestions {
                    margin-bottom: 16px;
                }

                .suggestions-header {
                    font-size: 12px;
                    font-weight: 600;
                    opacity: 0.8;
                    margin-bottom: 6px;
                }

                .suggestions-list {
                    list-style: none;
                    padding: 0;
                    margin: 0;
                }

                .suggestion-item {
                    font-size: 12px;
                    padding: 4px 0;
                    opacity: 0.9;
                    position: relative;
                    padding-left: 12px;
                }

                .suggestion-item::before {
                    content: '→';
                    position: absolute;
                    left: 0;
                    opacity: 0.6;
                }

                .prediction-actions {
                    display: flex;
                    gap: 8px;
                    flex-wrap: wrap;
                }

                .action-btn {
                    padding: 6px 12px;
                    border-radius: 6px;
                    border: none;
                    font-size: 11px;
                    font-weight: 600;
                    cursor: pointer;
                    transition: all 0.2s ease;
                }

                .action-btn.primary {
                    background: rgba(34, 197, 94, 0.8);
                    color: white;
                }

                .action-btn.primary:hover {
                    background: rgba(34, 197, 94, 1);
                }

                .action-btn.secondary {
                    background: rgba(255, 255, 255, 0.2);
                    color: white;
                    border: 1px solid rgba(255, 255, 255, 0.3);
                }

                .action-btn.secondary:hover {
                    background: rgba(255, 255, 255, 0.3);
                }

                .action-btn.dismiss {
                    background: rgba(239, 68, 68, 0.2);
                    color: #ef4444;
                    border: 1px solid rgba(239, 68, 68, 0.3);
                }

                .action-btn.dismiss:hover {
                    background: rgba(239, 68, 68, 0.3);
                }

                .no-predictions {
                    text-align: center;
                    padding: 40px 20px;
                    opacity: 0.8;
                }

                .no-predictions-icon {
                    font-size: 48px;
                    margin-bottom: 16px;
                }

                .no-predictions h4 {
                    margin: 0 0 8px 0;
                    font-size: 18px;
                }

                .no-predictions p {
                    margin: 0;
                    font-size: 14px;
                    opacity: 0.8;
                }

                .acknowledgment-indicator {
                    position: absolute;
                    top: 8px;
                    right: 8px;
                    background: rgba(34, 197, 94, 0.8);
                    color: white;
                    padding: 4px 8px;
                    border-radius: 12px;
                    font-size: 10px;
                    font-weight: 600;
                }

                /* Modal Styles */
                .prediction-modal {
                    position: fixed;
                    top: 0;
                    left: 0;
                    right: 0;
                    bottom: 0;
                    z-index: 2000;
                    display: flex;
                    align-items: center;
                    justify-content: center;
                }

                .modal-backdrop {
                    position: absolute;
                    top: 0;
                    left: 0;
                    right: 0;
                    bottom: 0;
                    background: rgba(0, 0, 0, 0.7);
                    backdrop-filter: blur(5px);
                }

                .modal-content {
                    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                    border-radius: 16px;
                    width: 90%;
                    max-width: 500px;
                    max-height: 80vh;
                    overflow-y: auto;
                    position: relative;
                    z-index: 1;
                    color: white;
                }

                .modal-header {
                    display: flex;
                    justify-content: space-between;
                    align-items: center;
                    padding: 20px;
                    border-bottom: 1px solid rgba(255, 255, 255, 0.2);
                }

                .modal-header h3 {
                    margin: 0;
                    font-size: 18px;
                    text-transform: capitalize;
                }

                .modal-header button {
                    background: none;
                    border: none;
                    color: white;
                    font-size: 24px;
                    cursor: pointer;
                    width: 30px;
                    height: 30px;
                    display: flex;
                    align-items: center;
                    justify-content: center;
                    border-radius: 4px;
                }

                .modal-header button:hover {
                    background: rgba(255, 255, 255, 0.1);
                }

                .modal-body {
                    padding: 20px;
                }

                .prediction-summary {
                    margin-bottom: 20px;
                    padding: 16px;
                    background: rgba(255, 255, 255, 0.1);
                    border-radius: 8px;
                }

                .action-checklist h4 {
                    margin: 0 0 12px 0;
                    font-size: 16px;
                }

                .checklist-item {
                    display: flex;
                    align-items: center;
                    gap: 8px;
                    margin-bottom: 8px;
                    padding: 8px;
                    background: rgba(255, 255, 255, 0.05);
                    border-radius: 6px;
                }

                .checklist-item input[type="checkbox"] {
                    width: 16px;
                    height: 16px;
                    accent-color: #22c55e;
                }

                .checklist-item label {
                    font-size: 14px;
                    cursor: pointer;
                    flex: 1;
                }

                .modal-actions {
                    padding: 20px;
                    border-top: 1px solid rgba(255, 255, 255, 0.2);
                    display: flex;
                    gap: 12px;
                    justify-content: flex-end;
                }

                .success-toast {
                    position: fixed;
                    top: 20px;
                    right: 20px;
                    background: rgba(34, 197, 94, 0.9);
                    color: white;
                    padding: 12px 16px;
                    border-radius: 8px;
                    display: flex;
                    align-items: center;
                    gap: 8px;
                    z-index: 3000;
                    backdrop-filter: blur(10px);
                    box-shadow: 0 4px 12px rgba(34, 197, 94, 0.3);
                }

                .toast-icon {
                    font-size: 16px;
                }

                .toast-message {
                    font-size: 14px;
                    font-weight: 500;
                }

                @media (max-width: 768px) {
                    .predictions-dashboard {
                        margin: 16px 0;
                        padding: 16px;
                    }

                    .predictions-header {
                        flex-direction: column;
                        gap: 12px;
                        align-items: flex-start;
                    }

                    .prediction-controls {
                        align-self: stretch;
                    }

                    .filter-select {
                        flex: 1;
                    }

                    .prediction-actions {
                        justify-content: center;
                    }

                    .modal-content {
                        width: 95%;
                        margin: 10px;
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
let predictiveInsights;

// Initialize when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
    // Only initialize on dashboard pages
    if (window.location.pathname.includes('/dashboard') || 
        document.querySelector('.dashboard-main')) {
        predictiveInsights = new PredictiveInsights();
    }
});

// Export for global access
window.predictiveInsights = predictiveInsights;