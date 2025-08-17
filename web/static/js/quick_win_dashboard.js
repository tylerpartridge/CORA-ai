/**
 * Quick Win Dashboard Component
 * Shows tax deduction opportunities and celebrates savings
 */

class QuickWinDashboard {
    constructor(container) {
        this.container = container;
        this.quickWins = [];
        this.totalSavings = 0;
        this.init();
    }
    
    async init() {
        this.render();
        await this.loadQuickWins();
        this.startAutoRefresh();
    }
    
    render() {
        this.container.innerHTML = `
            <div class="quick-win-section">
                <div class="section-header">
                    <h3 class="section-title">
                        <span class="trophy-icon">🏆</span>
                        Tax Savings Discovered
                    </h3>
                    <button class="analyze-btn" id="analyze-expenses">
                        <i class="fas fa-search-dollar"></i> Find More Savings
                    </button>
                </div>
                
                <div class="savings-summary">
                    <div class="savings-card total-savings">
                        <div class="savings-label">This Month</div>
                        <div class="savings-amount" id="monthly-savings">$0</div>
                        <div class="savings-sublabel">in tax savings</div>
                    </div>
                    <div class="savings-card annual-projection">
                        <div class="savings-label">Annual Projection</div>
                        <div class="savings-amount" id="annual-savings">$0</div>
                        <div class="savings-sublabel">potential savings</div>
                    </div>
                    <div class="savings-card deduction-rate">
                        <div class="savings-label">Deduction Rate</div>
                        <div class="savings-amount" id="deduction-rate">0%</div>
                        <div class="savings-sublabel">of expenses</div>
                    </div>
                </div>
                
                <div class="quick-wins-list" id="quick-wins-list">
                    <div class="loading-wins">
                        <div class="spinner"></div>
                        <p>Analyzing your expenses for tax savings...</p>
                    </div>
                </div>
                
                <div class="tips-section">
                    <h4 class="tips-title">💡 Pro Tips</h4>
                    <div class="tips-carousel" id="tips-carousel"></div>
                </div>
            </div>
        `;
        
        this.addStyles();
        this.bindEvents();
    }
    
    addStyles() {
        const styleId = 'quick-win-dashboard-styles';
        if (document.getElementById(styleId)) return;
        
        const styles = `
            .quick-win-section {
                background: white;
                border-radius: 12px;
                padding: 24px;
                box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
                margin-bottom: 24px;
            }
            
            .section-header {
                display: flex;
                justify-content: space-between;
                align-items: center;
                margin-bottom: 24px;
            }
            
            .section-title {
                font-size: 20px;
                font-weight: 600;
                color: #1a1a1a;
                display: flex;
                align-items: center;
                gap: 8px;
                margin: 0;
            }
            
            .trophy-icon {
                font-size: 24px;
                animation: bounce 2s infinite;
            }
            
            @keyframes bounce {
                0%, 100% { transform: translateY(0); }
                50% { transform: translateY(-5px); }
            }
            
            .analyze-btn {
                background: linear-gradient(135deg, #22c55e, #16a34a);
                color: white;
                border: none;
                padding: 10px 20px;
                border-radius: 8px;
                font-weight: 500;
                cursor: pointer;
                display: flex;
                align-items: center;
                gap: 8px;
                transition: all 0.3s ease;
            }
            
            .analyze-btn:hover {
                transform: translateY(-2px);
                box-shadow: 0 4px 12px rgba(34, 197, 94, 0.3);
            }
            
            .savings-summary {
                display: grid;
                grid-template-columns: repeat(3, 1fr);
                gap: 16px;
                margin-bottom: 32px;
            }
            
            .savings-card {
                background: linear-gradient(135deg, #f0f9ff, #e0f2fe);
                padding: 20px;
                border-radius: 12px;
                text-align: center;
                position: relative;
                overflow: hidden;
            }
            
            .savings-card.total-savings {
                background: linear-gradient(135deg, #dcfce7, #bbf7d0);
            }
            
            .savings-card.annual-projection {
                background: linear-gradient(135deg, #fef3c7, #fde68a);
            }
            
            .savings-card.deduction-rate {
                background: linear-gradient(135deg, #ede9fe, #ddd6fe);
            }
            
            .savings-label {
                font-size: 14px;
                color: #666;
                margin-bottom: 8px;
                font-weight: 500;
            }
            
            .savings-amount {
                font-size: 32px;
                font-weight: 700;
                color: #1a1a1a;
                margin-bottom: 4px;
            }
            
            .savings-sublabel {
                font-size: 12px;
                color: #666;
            }
            
            .quick-wins-list {
                margin-bottom: 24px;
            }
            
            .loading-wins {
                text-align: center;
                padding: 40px;
                color: #666;
            }
            
            .spinner {
                width: 40px;
                height: 40px;
                margin: 0 auto 16px;
                border: 3px solid #f0f0f0;
                border-top: 3px solid #9B6EC8;
                border-radius: 50%;
                animation: spin 1s linear infinite;
            }
            
            @keyframes spin {
                0% { transform: rotate(0deg); }
                100% { transform: rotate(360deg); }
            }
            
            .win-item {
                background: #f8f9fa;
                border: 1px solid #e5e5e5;
                border-radius: 8px;
                padding: 16px;
                margin-bottom: 12px;
                display: flex;
                align-items: center;
                gap: 16px;
                transition: all 0.3s ease;
                cursor: pointer;
            }
            
            .win-item:hover {
                border-color: #22c55e;
                box-shadow: 0 2px 8px rgba(34, 197, 94, 0.1);
            }
            
            .win-icon {
                font-size: 32px;
                width: 48px;
                height: 48px;
                display: flex;
                align-items: center;
                justify-content: center;
                background: white;
                border-radius: 50%;
                flex-shrink: 0;
            }
            
            .win-details {
                flex: 1;
            }
            
            .win-expense {
                font-weight: 600;
                color: #1a1a1a;
                margin-bottom: 4px;
            }
            
            .win-savings {
                color: #22c55e;
                font-size: 14px;
                font-weight: 500;
            }
            
            .win-tip {
                color: #666;
                font-size: 12px;
                margin-top: 4px;
            }
            
            .win-celebration {
                background: #22c55e;
                color: white;
                padding: 4px 12px;
                border-radius: 20px;
                font-size: 12px;
                font-weight: 600;
                animation: pulse 2s infinite;
            }
            
            @keyframes pulse {
                0% { opacity: 1; }
                50% { opacity: 0.8; }
                100% { opacity: 1; }
            }
            
            .tips-section {
                background: #f0f9ff;
                padding: 20px;
                border-radius: 8px;
            }
            
            .tips-title {
                margin: 0 0 12px 0;
                color: #1a1a1a;
                font-size: 16px;
            }
            
            .tips-carousel {
                display: flex;
                gap: 12px;
                overflow-x: auto;
                scrollbar-width: thin;
            }
            
            .tip-card {
                background: white;
                padding: 12px 16px;
                border-radius: 6px;
                min-width: 250px;
                font-size: 14px;
                color: #666;
                border: 1px solid #e0f2fe;
            }
            
            .celebration-modal {
                position: fixed;
                top: 50%;
                left: 50%;
                transform: translate(-50%, -50%);
                background: white;
                padding: 32px;
                border-radius: 16px;
                box-shadow: 0 20px 40px rgba(0, 0, 0, 0.2);
                z-index: 10000;
                text-align: center;
                animation: celebrateIn 0.5s ease;
            }
            
            @keyframes celebrateIn {
                0% { transform: translate(-50%, -50%) scale(0.8); opacity: 0; }
                100% { transform: translate(-50%, -50%) scale(1); opacity: 1; }
            }
            
            .celebration-emoji {
                font-size: 64px;
                margin-bottom: 16px;
            }
            
            .celebration-message {
                font-size: 24px;
                font-weight: 700;
                color: #1a1a1a;
                margin-bottom: 8px;
            }
            
            .celebration-details {
                font-size: 16px;
                color: #666;
                margin-bottom: 24px;
            }
            
            .celebration-close {
                background: #9B6EC8;
                color: white;
                border: none;
                padding: 12px 32px;
                border-radius: 8px;
                font-weight: 600;
                cursor: pointer;
            }
            
            @media (max-width: 768px) {
                .savings-summary {
                    grid-template-columns: 1fr;
                }
                
                .section-header {
                    flex-direction: column;
                    gap: 16px;
                    align-items: stretch;
                }
                
                .analyze-btn {
                    justify-content: center;
                }
            }
        `;
        
        const styleSheet = document.createElement('style');
        styleSheet.id = styleId;
        styleSheet.textContent = styles;
        document.head.appendChild(styleSheet);
    }
    
    bindEvents() {
        document.getElementById('analyze-expenses').addEventListener('click', () => {
            this.analyzeMoreExpenses();
        });
    }
    
    async loadQuickWins() {
        try {
            const response = await fetch('/api/expenses/quick-wins');
            const data = await response.json();
            
            if (data.success) {
                this.quickWins = data.quick_wins;
                this.totalSavings = data.total_savings;
                this.updateDisplay();
                
                // Celebrate if significant savings found
                if (data.total_savings > 100) {
                    this.celebrateSavings(data.total_savings);
                }
            }
        } catch (error) {
            // console.error('Failed to load quick wins:', error);
            this.showError();
        }
    }
    
    updateDisplay() {
        // Update summary cards
        document.getElementById('monthly-savings').textContent = 
            `$${this.totalSavings.toFixed(2)}`;
        document.getElementById('annual-savings').textContent = 
            `$${(this.totalSavings * 12).toFixed(0)}`;
        document.getElementById('deduction-rate').textContent = 
            `${this.calculateDeductionRate()}%`;
        
        // Update wins list
        const listContainer = document.getElementById('quick-wins-list');
        
        if (this.quickWins.length === 0) {
            listContainer.innerHTML = `
                <div class="no-wins">
                    <p>No tax deductions found yet. Add more expenses to discover savings!</p>
                </div>
            `;
            return;
        }
        
        listContainer.innerHTML = this.quickWins.map(win => `
            <div class="win-item" data-expense-id="${win.expense_id}">
                <div class="win-icon">${this.getCategoryIcon(win.category)}</div>
                <div class="win-details">
                    <div class="win-expense">
                        ${win.vendor} - $${win.amount.toFixed(2)}
                    </div>
                    <div class="win-savings">
                        Save $${win.tax_savings.toFixed(2)} (${win.deduction_rate}% deductible)
                    </div>
                    <div class="win-tip">${win.tip}</div>
                </div>
                ${win.celebration_level === 'large' ? 
                    '<div class="win-celebration">BIG WIN!</div>' : ''}
            </div>
        `).join('');
        
        // Update tips
        this.updateTips();
    }
    
    getCategoryIcon(category) {
        const icons = {
            'Meals & Entertainment': '🍽️',
            'Transportation': '🚗',
            'Office Supplies': '📎',
            'Technology & Equipment': '💻',
            'Professional Development': '📚',
            'Marketing & Advertising': '📢',
            'Professional Services': '💼',
            'Home Office': '🏠'
        };
        return icons[category] || '💰';
    }
    
    calculateDeductionRate() {
        if (!this.quickWins.length) return 0;
        
        const totalExpenses = this.quickWins.reduce((sum, win) => sum + win.amount, 0);
        const totalDeductions = this.quickWins.reduce((sum, win) => 
            sum + (win.amount * win.deduction_rate / 100), 0);
        
        return Math.round((totalDeductions / totalExpenses) * 100);
    }
    
    updateTips() {
        const tipsContainer = document.getElementById('tips-carousel');
        const tips = [
            "Track mileage for client visits - $0.655 per mile adds up fast!",
            "Home office deduction can save thousands annually",
            "Business meals are 50% deductible when discussing work",
            "Keep all receipts - digital photos count!",
            "Software subscriptions for work are 100% deductible"
        ];
        
        tipsContainer.innerHTML = tips.map(tip => 
            `<div class="tip-card">${tip}</div>`
        ).join('');
    }
    
    celebrateSavings(amount) {
        const modal = document.createElement('div');
        modal.className = 'celebration-modal';
        modal.innerHTML = `
            <div class="celebration-emoji">🎉</div>
            <div class="celebration-message">Amazing Tax Savings!</div>
            <div class="celebration-details">
                You've found $${amount.toFixed(2)} in tax deductions this month.
                That's $${(amount * 12).toFixed(0)} per year!
            </div>
            <button class="celebration-close">Awesome!</button>
        `;
        
        document.body.appendChild(modal);
        
        // Add confetti effect
        this.createConfetti();
        
        modal.querySelector('.celebration-close').addEventListener('click', () => {
            modal.remove();
        });
        
        // Auto close after 5 seconds
        setTimeout(() => modal.remove(), 5000);
    }
    
    createConfetti() {
        const colors = ['#22c55e', '#f59e0b', '#3b82f6', '#ef4444', '#9B6EC8'];
        const confettiCount = 50;
        
        for (let i = 0; i < confettiCount; i++) {
            const confetti = document.createElement('div');
            confetti.style.cssText = `
                position: fixed;
                left: ${Math.random() * 100}%;
                top: -10px;
                width: 10px;
                height: 10px;
                background: ${colors[Math.floor(Math.random() * colors.length)]};
                z-index: 9999;
                animation: fall ${3 + Math.random() * 2}s linear;
            `;
            
            document.body.appendChild(confetti);
            
            setTimeout(() => confetti.remove(), 5000);
        }
        
        // Add falling animation
        const styleId = 'confetti-animation';
        if (!document.getElementById(styleId)) {
            const style = document.createElement('style');
            style.id = styleId;
            style.textContent = `
                @keyframes fall {
                    to {
                        transform: translateY(100vh) rotate(360deg);
                    }
                }
            `;
            document.head.appendChild(style);
        }
    }
    
    async analyzeMoreExpenses() {
        const btn = document.getElementById('analyze-expenses');
        btn.disabled = true;
        btn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Analyzing...';
        
        try {
            const response = await fetch('/api/expenses/analyze-deductions', {
                method: 'POST'
            });
            
            const data = await response.json();
            
            if (data.success) {
                this.loadQuickWins();
                
                if (data.new_savings > 0) {
                    this.showNotification(
                        `Found $${data.new_savings.toFixed(2)} in new deductions!`,
                        'success'
                    );
                }
            }
        } catch (error) {
            // console.error('Analysis failed:', error);
            this.showNotification('Failed to analyze expenses', 'error');
        } finally {
            btn.disabled = false;
            btn.innerHTML = '<i class="fas fa-search-dollar"></i> Find More Savings';
        }
    }
    
    showNotification(message, type) {
        const notification = document.createElement('div');
        notification.style.cssText = `
            position: fixed;
            top: 20px;
            right: 20px;
            padding: 16px 24px;
            background: ${type === 'success' ? '#22c55e' : '#ef4444'};
            color: white;
            border-radius: 8px;
            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
            z-index: 10000;
            animation: slideIn 0.3s ease;
        `;
        notification.textContent = message;
        
        document.body.appendChild(notification);
        
        setTimeout(() => notification.remove(), 3000);
    }
    
    showError() {
        const listContainer = document.getElementById('quick-wins-list');
        listContainer.innerHTML = `
            <div class="error-message">
                <p>Unable to load tax savings. Please try again later.</p>
            </div>
        `;
    }
    
    startAutoRefresh() {
        // Refresh every 5 minutes
        setInterval(() => {
            this.loadQuickWins();
        }, 5 * 60 * 1000);
    }
}

// Initialize when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
    const container = document.querySelector('.quick-win-dashboard-container');
    if (container) {
        new QuickWinDashboard(container);
    }
});

// Export for use in other modules
window.QuickWinDashboard = QuickWinDashboard;