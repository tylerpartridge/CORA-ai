/**
 * CORA Virtual Scrolling
 * Handles large lists efficiently with virtual scrolling
 */

class VirtualScroll {
    constructor(container, options = {}) {
        this.container = container;
        this.options = {
            itemHeight: 60,
            bufferSize: 5,
            threshold: 50,
            ...options
        };
        
        this.items = [];
        this.visibleItems = [];
        this.scrollTop = 0;
        this.containerHeight = 0;
        this.totalHeight = 0;
        this.startIndex = 0;
        this.endIndex = 0;
        
        this.init();
    }
    
    init() {
        this.setupContainer();
        this.bindEvents();
        this.render();
    }
    
    setupContainer() {
        // Set container styles
        this.container.style.position = 'relative';
        this.container.style.overflow = 'auto';
        
        // Create content wrapper
        this.contentWrapper = document.createElement('div');
        this.contentWrapper.className = 'virtual-scroll-content';
        this.contentWrapper.style.position = 'relative';
        
        // Create spacer for total height
        this.spacer = document.createElement('div');
        this.spacer.className = 'virtual-scroll-spacer';
        this.spacer.style.height = '0px';
        
        this.contentWrapper.appendChild(this.spacer);
        this.container.appendChild(this.contentWrapper);
        
        // Calculate container height
        this.updateContainerHeight();
    }
    
    bindEvents() {
        // Handle scroll events
        this.container.addEventListener('scroll', (e) => {
            this.handleScroll(e);
        });
        
        // Handle resize events
        window.addEventListener('resize', () => {
            this.updateContainerHeight();
            this.render();
        });
        
        // Handle orientation change on mobile
        window.addEventListener('orientationchange', () => {
            setTimeout(() => {
                this.updateContainerHeight();
                this.render();
            }, 100);
        });
    }
    
    handleScroll(e) {
        const newScrollTop = e.target.scrollTop;
        
        // Check if we need to re-render
        if (Math.abs(newScrollTop - this.scrollTop) > this.options.threshold) {
            this.scrollTop = newScrollTop;
            this.render();
        }
    }
    
    updateContainerHeight() {
        this.containerHeight = this.container.clientHeight;
    }
    
    setItems(items) {
        this.items = items;
        this.totalHeight = items.length * this.options.itemHeight;
        this.spacer.style.height = `${this.totalHeight}px`;
        this.render();
    }
    
    render() {
        if (this.items.length === 0) {
            this.clearContent();
            return;
        }
        
        // Calculate visible range
        this.calculateVisibleRange();
        
        // Get items to render
        const itemsToRender = this.items.slice(this.startIndex, this.endIndex + 1);
        
        // Render items
        this.renderItems(itemsToRender);
    }
    
    calculateVisibleRange() {
        const bufferHeight = this.options.bufferSize * this.options.itemHeight;
        const startOffset = Math.max(0, this.scrollTop - bufferHeight);
        const endOffset = this.scrollTop + this.containerHeight + bufferHeight;
        
        this.startIndex = Math.floor(startOffset / this.options.itemHeight);
        this.endIndex = Math.min(
            this.items.length - 1,
            Math.floor(endOffset / this.options.itemHeight)
        );
    }
    
    renderItems(items) {
        // Clear existing content
        this.clearContent();
        
        // Create and position items
        items.forEach((item, index) => {
            const actualIndex = this.startIndex + index;
            const itemElement = this.createItemElement(item, actualIndex);
            
            // Position item
            itemElement.style.position = 'absolute';
            itemElement.style.top = `${actualIndex * this.options.itemHeight}px`;
            itemElement.style.left = '0';
            itemElement.style.right = '0';
            itemElement.style.height = `${this.options.itemHeight}px`;
            
            this.contentWrapper.appendChild(itemElement);
        });
    }
    
    createItemElement(item, index) {
        const element = document.createElement('div');
        element.className = 'virtual-scroll-item';
        element.setAttribute('data-index', index);
        
        // Use custom render function if provided
        if (this.options.renderItem) {
            element.innerHTML = this.options.renderItem(item, index);
        } else {
            // Default rendering
            element.textContent = item.text || item.name || item.toString();
        }
        
        // Add click handler if provided
        if (this.options.onItemClick) {
            element.addEventListener('click', () => {
                this.options.onItemClick(item, index);
            });
        }
        
        return element;
    }
    
    clearContent() {
        // Remove all items except spacer
        const items = this.contentWrapper.querySelectorAll('.virtual-scroll-item');
        items.forEach(item => item.remove());
    }
    
    scrollToIndex(index) {
        const targetScrollTop = index * this.options.itemHeight;
        this.container.scrollTop = targetScrollTop;
    }
    
    scrollToItem(item) {
        const index = this.items.findIndex(i => i === item);
        if (index !== -1) {
            this.scrollToIndex(index);
        }
    }
    
    getVisibleItems() {
        return this.items.slice(this.startIndex, this.endIndex + 1);
    }
    
    getVisibleIndices() {
        return {
            start: this.startIndex,
            end: this.endIndex
        };
    }
    
    updateItem(index, newItem) {
        if (index >= 0 && index < this.items.length) {
            this.items[index] = newItem;
            
            // Re-render if item is visible
            if (index >= this.startIndex && index <= this.endIndex) {
                this.render();
            }
        }
    }
    
    addItem(item) {
        this.items.push(item);
        this.totalHeight = this.items.length * this.options.itemHeight;
        this.spacer.style.height = `${this.totalHeight}px`;
        this.render();
    }
    
    removeItem(index) {
        if (index >= 0 && index < this.items.length) {
            this.items.splice(index, 1);
            this.totalHeight = this.items.length * this.options.itemHeight;
            this.spacer.style.height = `${this.totalHeight}px`;
            this.render();
        }
    }
    
    // Utility methods for specific use cases
    static createExpenseList(container, expenses) {
        return new VirtualScroll(container, {
            itemHeight: 80,
            renderItem: (expense, index) => `
                <div class="expense-item">
                    <div class="expense-header">
                        <div class="expense-vendor">${expense.vendor}</div>
                        <div class="expense-amount">$${(expense.amount_cents / 100).toFixed(2)}</div>
                    </div>
                    <div class="expense-details">
                        <div class="expense-category">${expense.category}</div>
                        <div class="expense-date">${new Date(expense.date).toLocaleDateString()}</div>
                    </div>
                    ${expense.job_name ? `<div class="expense-job">${expense.job_name}</div>` : ''}
                </div>
            `,
            onItemClick: (expense, index) => {
                // console.log('Expense clicked:', expense);
                // Handle expense click
            }
        });
    }
    
    static createJobList(container, jobs) {
        return new VirtualScroll(container, {
            itemHeight: 100,
            renderItem: (job, index) => `
                <div class="job-item">
                    <div class="job-header">
                        <div class="job-name">${job.job_name}</div>
                        <div class="job-status status-${job.status}">${job.status}</div>
                    </div>
                    <div class="job-metrics">
                        <div class="job-budget">Budget: $${(job.budget_cents / 100).toFixed(2)}</div>
                        <div class="job-spent">Spent: $${(job.spent_cents / 100).toFixed(2)}</div>
                        <div class="job-profit">Profit: $${(job.profit_cents / 100).toFixed(2)}</div>
                    </div>
                    <div class="job-margin">
                        Margin: ${job.profit_margin_percent.toFixed(1)}%
                    </div>
                </div>
            `,
            onItemClick: (job, index) => {
                // console.log('Job clicked:', job);
                // Handle job click
            }
        });
    }
    
    static createTransactionList(container, transactions) {
        return new VirtualScroll(container, {
            itemHeight: 70,
            renderItem: (transaction, index) => `
                <div class="transaction-item">
                    <div class="transaction-amount ${transaction.type === 'income' ? 'positive' : 'negative'}">
                        ${transaction.type === 'income' ? '+' : '-'}$${(transaction.amount_cents / 100).toFixed(2)}
                    </div>
                    <div class="transaction-details">
                        <div class="transaction-description">${transaction.description}</div>
                        <div class="transaction-date">${new Date(transaction.date).toLocaleDateString()}</div>
                    </div>
                    <div class="transaction-category">${transaction.category}</div>
                </div>
            `,
            onItemClick: (transaction, index) => {
                // console.log('Transaction clicked:', transaction);
                // Handle transaction click
            }
        });
    }
    
    // Performance monitoring
    getPerformanceStats() {
        return {
            totalItems: this.items.length,
            visibleItems: this.endIndex - this.startIndex + 1,
            renderRatio: (this.endIndex - this.startIndex + 1) / this.items.length,
            scrollTop: this.scrollTop,
            containerHeight: this.containerHeight,
            totalHeight: this.totalHeight
        };
    }
    
    // Cleanup
    destroy() {
        this.container.removeEventListener('scroll', this.handleScroll);
        window.removeEventListener('resize', this.handleResize);
        window.removeEventListener('orientationchange', this.handleOrientationChange);
        
        // Clear content
        this.clearContent();
        
        // Remove wrapper
        if (this.contentWrapper && this.contentWrapper.parentNode) {
            this.contentWrapper.parentNode.removeChild(this.contentWrapper);
        }
    }
}

// Auto-initialize virtual scrolling for common containers
document.addEventListener('DOMContentLoaded', () => {
    // Initialize virtual scrolling for expense lists
    const expenseContainers = document.querySelectorAll('.expenses-list, .transactions-list');
    expenseContainers.forEach(container => {
        if (container.children.length > 20) { // Only use virtual scroll for large lists
            const virtualScroll = VirtualScroll.createExpenseList(container, []);
            
            // Store reference for later use
            container.virtualScroll = virtualScroll;
        }
    });
    
    // Initialize virtual scrolling for job lists
    const jobContainers = document.querySelectorAll('.jobs-list, .job-profitability-grid');
    jobContainers.forEach(container => {
        if (container.children.length > 15) { // Only use virtual scroll for large lists
            const virtualScroll = VirtualScroll.createJobList(container, []);
            
            // Store reference for later use
            container.virtualScroll = virtualScroll;
        }
    });
});

// Export for use in other modules
if (typeof module !== 'undefined' && module.exports) {
    module.exports = VirtualScroll;
} 