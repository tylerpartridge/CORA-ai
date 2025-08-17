// Dashboard Controller
class Dashboard {
    constructor() {
        this.currentPeriod = 'today';
        this.data = {};
        
        // Cookie-based authentication - no token check needed here
        // If user reaches dashboard, they're already authenticated
        
        // Initialize
        this.init();
    }
    
    async init() {
        // Set up event listeners
        this.setupEventListeners();
        
        // Load initial data
        await this.loadDashboardData();
        
        // Set up real-time updates (every 30 seconds)
        setInterval(() => this.refreshData(), 30000);
    }
    
    setupEventListeners() {
        // Time filter buttons
        document.querySelectorAll('.time-filter').forEach(btn => {
            btn.addEventListener('click', (e) => this.handleTimeFilterChange(e));
        });
        
        // FAB button
        document.getElementById('fabButton').addEventListener('click', () => this.showAddOptions());
        
        // Summary cards
        document.querySelectorAll('.summary-card').forEach(card => {
            card.addEventListener('click', (e) => this.handleSummaryCardClick(e));
        });
    }
    
    handleTimeFilterChange(e) {
        // Update active state
        document.querySelectorAll('.time-filter').forEach(btn => {
            btn.classList.remove('active');
            btn.setAttribute('aria-pressed', 'false');
        });
        e.target.classList.add('active');
        e.target.setAttribute('aria-pressed', 'true');
        
        // Update period and reload data
        this.currentPeriod = e.target.dataset.period;
        this.loadDashboardData();
    }
    
    async loadDashboardData() {
        try {
            // Fetch summary data (using cookie-based authentication)
            const summaryResponse = await fetch('/api/dashboard/summary', {
                credentials: 'same-origin'  // Include cookies for authentication
            });
            
            if (!summaryResponse.ok) {
                if (summaryResponse.status === 401) {
                    // Redirect to login if authentication fails
                    window.location.href = '/login';
                    return;
                }
                throw new Error('Failed to load dashboard data');
            }
            
            const summaryData = await summaryResponse.json();
            
            // Fetch metrics data
            const metricsResponse = await fetch(`/api/dashboard/metrics?period=${this.currentPeriod}`, {
                credentials: 'same-origin'  // Include cookies for authentication
            });
            
            const metricsData = await metricsResponse.json();
            
            // Fetch insights
            const insightsResponse = await fetch('/api/dashboard/insights', {
                credentials: 'same-origin'  // Include cookies for authentication
            });
            
            const insightsData = await insightsResponse.json();
            
            // Update UI with data
            this.updateCashPosition(summaryData.summary, metricsData.metrics);
            this.updateMonthlySummary(summaryData.summary);
            this.updateActivityFeed(summaryData.summary.recent_expenses);
            this.updateInsights(insightsData.insights);
            
        } catch (error) {
            // console.error('Dashboard error:', error);
            this.showError('Unable to load dashboard data');
        }
    }
    
    updateCashPosition(summary, metrics) {
        const cashAmount = document.getElementById('cashAmount');
        const cashChange = document.getElementById('cashChange');
        
        // For now, use a calculated value (would come from bank integration)
        const estimatedCash = 15000; // This would be from Plaid
        const todayChange = summary.total_expenses_this_month ? 
            (summary.total_expenses_this_month / 30) : 0;
        
        // Animate number change
        this.animateValue(cashAmount, estimatedCash, '$');
        
        // Update change indicator
        cashChange.innerHTML = todayChange > 0 ? 
            `<span class="negative">↓ $${Math.abs(todayChange).toFixed(2)} today</span>` :
            `<span>→ $0.00 today</span>`;
    }
    
    updateMonthlySummary(summary) {
        // Money In (placeholder until income tracking is added)
        const moneyIn = document.getElementById('moneyIn');
        const monthlyIncome = summary.total_income_this_month || 0; // real value from API summary
        moneyIn.textContent = `$${monthlyIncome.toFixed(2)}`;
        
        // Money Out
        const moneyOut = document.getElementById('moneyOut');
        const monthlyExpenses = summary.total_expenses_this_month || 0;
        moneyOut.textContent = `$${monthlyExpenses.toFixed(2)}`;
        
        // Net
        const netAmount = document.getElementById('netAmount');
        const net = monthlyIncome - monthlyExpenses;
        netAmount.textContent = `${net >= 0 ? '+' : ''}$${Math.abs(net).toFixed(2)}`;
        netAmount.className = `summary-amount ${net >= 0 ? 'amount-positive' : 'amount-negative'}`;
    }
    
    updateActivityFeed(recentExpenses) {
        const feed = document.getElementById('activityFeed');
        
        if (!recentExpenses || recentExpenses.length === 0) {
            feed.innerHTML = `
                <div class="activity-item" style="text-align: center; color: var(--cora-gray-500);">
                    <div style="padding: var(--space-4);">
                        <p>No recent activity</p>
                        <p style="font-size: var(--text-sm); margin-top: var(--space-1);">
                            Add your first transaction to get started
                        </p>
                    </div>
                </div>
            `;
            return;
        }
        
        feed.innerHTML = recentExpenses.map(expense => `
            <div class="activity-item" tabindex="0" role="button" aria-label="${expense.vendor} expense details">
                <div class="activity-details">
                    <div class="activity-title">${this.escapeHtml(expense.vendor)}</div>
                    <div class="activity-meta">
                        ${this.formatRelativeTime(expense.date)} • ${expense.category}
                    </div>
                </div>
                <div class="activity-amount amount-negative">
                    $${expense.amount.toFixed(2)}
                </div>
            </div>
        `).join('');
    }
    
    updateInsights(insights) {
        const container = document.getElementById('insightsContainer');
        
        if (!insights || insights.length === 0) {
            container.innerHTML = `
                <div class="insight-card">
                    <div class="insight-message">
                        CORA is analyzing your financial patterns...
                    </div>
                </div>
            `;
            return;
        }
        
        container.innerHTML = insights.slice(0, 5).map(insight => `
            <div class="insight-card ${insight.type}" role="alert">
                <div class="insight-title">${this.escapeHtml(insight.title)}</div>
                <div class="insight-message">${this.escapeHtml(insight.message)}</div>
            </div>
        `).join('');
    }
    
    // Utility Methods
    animateValue(element, value, prefix = '') {
        const current = parseFloat(element.textContent.replace(/[^0-9.-]/g, '')) || 0;
        const increment = (value - current) / 20;
        let step = 0;
        
        const timer = setInterval(() => {
            step++;
            const newValue = current + (increment * step);
            element.textContent = `${prefix}${newValue.toLocaleString('en-US', {
                minimumFractionDigits: 2,
                maximumFractionDigits: 2
            })}`;
            
            if (step >= 20) {
                clearInterval(timer);
                element.textContent = `${prefix}${value.toLocaleString('en-US', {
                    minimumFractionDigits: 2,
                    maximumFractionDigits: 2
                })}`;
            }
        }, 30);
    }
    
    formatRelativeTime(dateString) {
        const date = new Date(dateString);
        const now = new Date();
        const diffMs = now - date;
        const diffMins = Math.floor(diffMs / 60000);
        const diffHours = Math.floor(diffMs / 3600000);
        const diffDays = Math.floor(diffMs / 86400000);
        
        if (diffMins < 1) return 'Just now';
        if (diffMins < 60) return `${diffMins} min ago`;
        if (diffHours < 24) return `${diffHours} hour${diffHours > 1 ? 's' : ''} ago`;
        if (diffDays < 7) return `${diffDays} day${diffDays > 1 ? 's' : ''} ago`;
        
        return date.toLocaleDateString();
    }
    
    escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }
    
    showAddOptions() {
        // This would open a modal or action sheet
        // For now, simple alert
        const options = ['Add Expense', 'Add Income', 'Scan Receipt', 'Voice Entry'];
        // console.log('Quick add options:', options);
        // TODO: Implement action sheet
    }
    
    handleSummaryCardClick(e) {
        const card = e.currentTarget;
        // console.log('Drill down into:', card.querySelector('.summary-label').textContent);
        // TODO: Show detailed breakdown
    }
    
    async refreshData() {
        // Only refresh if tab is visible
        if (!document.hidden) {
            await this.loadDashboardData();
        }
    }
    
    showError(message) {
        // TODO: Implement toast notification
        // console.error(message);
    }
}

// Initialize dashboard when DOM is ready
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', () => new Dashboard());
} else {
    new Dashboard();
}