/**
 * CORA Export Manager
 * Handles CSV and PDF export functionality
 */

class ExportManager {
    constructor() {
        this.exportQueue = [];
        this.isExporting = false;
        this.init();
    }
    
    init() {
        this.createExportButton();
        this.addExportStyles();
    }
    
    createExportButton() {
        // Add export button to dashboard header
        const header = document.querySelector('.header-actions');
        if (header) {
            const exportBtn = document.createElement('button');
            exportBtn.className = 'export-btn';
            exportBtn.innerHTML = '📊 Export';
            exportBtn.title = 'Export data to CSV or PDF';
            exportBtn.onclick = () => this.showExportModal();
            
            header.appendChild(exportBtn);
        }
    }
    
    showExportModal() {
        const modal = this.createExportModal();
        document.body.appendChild(modal);
        
        setTimeout(() => {
            modal.classList.add('open');
        }, 10);
    }
    
    createExportModal() {
        const modal = document.createElement('div');
        modal.className = 'export-modal';
        modal.innerHTML = `
            <div class="modal-overlay" onclick="exportManager.closeModal()"></div>
            <div class="modal-content">
                <div class="modal-header">
                    <h3>📊 Export Data</h3>
                    <button class="close-btn" onclick="exportManager.closeModal()">×</button>
                </div>
                <div class="modal-body">
                    <div class="export-section">
                        <h4>Export Type</h4>
                        <div class="export-options">
                            <label class="export-option">
                                <input type="radio" name="exportType" value="expenses" checked>
                                <span class="option-content">
                                    <div class="option-icon">💰</div>
                                    <div class="option-text">
                                        <strong>Expenses</strong>
                                        <small>All expense records with details</small>
                                    </div>
                                </span>
                            </label>
                            <label class="export-option">
                                <input type="radio" name="exportType" value="jobs">
                                <span class="option-content">
                                    <div class="option-icon">🏗️</div>
                                    <div class="option-text">
                                        <strong>Jobs</strong>
                                        <small>Job profitability and status</small>
                                    </div>
                                </span>
                            </label>
                            <label class="export-option">
                                <input type="radio" name="exportType" value="summary">
                                <span class="option-content">
                                    <div class="option-icon">📈</div>
                                    <div class="option-text">
                                        <strong>Summary Report</strong>
                                        <small>Monthly summary and metrics</small>
                                    </div>
                                </span>
                            </label>
                        </div>
                    </div>
                    
                    <div class="export-section">
                        <h4>Date Range</h4>
                        <div class="date-filters">
                            <div class="date-input">
                                <label>From:</label>
                                <input type="date" id="exportFromDate" value="${this.getDefaultFromDate()}">
                            </div>
                            <div class="date-input">
                                <label>To:</label>
                                <input type="date" id="exportToDate" value="${this.getDefaultToDate()}">
                            </div>
                        </div>
                    </div>
                    
                    <div class="export-section">
                        <h4>Format</h4>
                        <div class="format-options">
                            <label class="format-option">
                                <input type="radio" name="exportFormat" value="csv" checked>
                                <span class="option-content">
                                    <div class="option-icon">📄</div>
                                    <div class="option-text">
                                        <strong>CSV</strong>
                                        <small>Excel compatible spreadsheet</small>
                                    </div>
                                </span>
                            </label>
                            <label class="format-option">
                                <input type="radio" name="exportFormat" value="pdf">
                                <span class="option-content">
                                    <div class="option-icon">📋</div>
                                    <div class="option-text">
                                        <strong>PDF</strong>
                                        <small>Professional report format</small>
                                    </div>
                                </span>
                            </label>
                        </div>
                    </div>
                    
                    <div class="export-section" id="csvOptions" style="display: none;">
                        <h4>CSV Options</h4>
                        <div class="csv-options">
                            <label class="checkbox-option">
                                <input type="checkbox" id="includeHeaders" checked>
                                <span>Include column headers</span>
                            </label>
                            <label class="checkbox-option">
                                <input type="checkbox" id="includeTotals">
                                <span>Include totals row</span>
                            </label>
                        </div>
                    </div>
                </div>
                <div class="modal-footer">
                    <button class="btn-secondary" onclick="exportManager.closeModal()">Cancel</button>
                    <button class="btn-primary" onclick="exportManager.startExport()">
                        <span class="btn-text">Export Data</span>
                        <span class="btn-loading" style="display: none;">Exporting...</span>
                    </button>
                </div>
            </div>
        `;
        
        // Add event listeners
        this.addModalEventListeners(modal);
        
        return modal;
    }
    
    addModalEventListeners(modal) {
        // Show/hide CSV options based on format selection
        const formatOptions = modal.querySelectorAll('input[name="exportFormat"]');
        const csvOptions = modal.querySelector('#csvOptions');
        
        formatOptions.forEach(option => {
            option.addEventListener('change', () => {
                if (option.value === 'csv') {
                    csvOptions.style.display = 'block';
                } else {
                    csvOptions.style.display = 'none';
                }
            });
        });
    }
    
    getDefaultFromDate() {
        const date = new Date();
        date.setMonth(date.getMonth() - 1);
        return date.toISOString().split('T')[0];
    }
    
    getDefaultToDate() {
        return new Date().toISOString().split('T')[0];
    }
    
    async startExport() {
        if (this.isExporting) return;
        
        this.isExporting = true;
        this.updateExportButton(true);
        
        try {
            const exportType = document.querySelector('input[name="exportType"]:checked').value;
            const exportFormat = document.querySelector('input[name="exportFormat"]:checked').value;
            const fromDate = document.getElementById('exportFromDate').value;
            const toDate = document.getElementById('exportToDate').value;
            
            // console.log('Starting export:', { exportType, exportFormat, fromDate, toDate });
            
            if (exportFormat === 'csv') {
                await this.exportToCSV(exportType, fromDate, toDate);
            } else {
                await this.exportToPDF(exportType, fromDate, toDate);
            }
            
            this.showSuccessMessage(exportType, exportFormat);
            
        } catch (error) {
            // console.error('Export failed:', error);
            this.showErrorMessage(error.message);
        } finally {
            this.isExporting = false;
            this.updateExportButton(false);
        }
    }
    
    async exportToCSV(exportType, fromDate, toDate) {
        const data = await this.fetchExportData(exportType, fromDate, toDate);
        const csv = this.convertToCSV(data, exportType);
        this.downloadCSV(csv, `${exportType}_${fromDate}_to_${toDate}.csv`);
    }
    
    async exportToPDF(exportType, fromDate, toDate) {
        const data = await this.fetchExportData(exportType, fromDate, toDate);
        
        // For PDF, we'll create a simple HTML report and use browser print
        const html = this.generatePDFHTML(data, exportType, fromDate, toDate);
        this.downloadPDF(html, `${exportType}_report_${fromDate}_to_${toDate}.html`);
    }
    
    async fetchExportData(exportType, fromDate, toDate) {
        let endpoint = '';
        let params = new URLSearchParams({
            from_date: fromDate,
            to_date: toDate
        });
        
        switch (exportType) {
            case 'expenses':
                endpoint = '/api/expenses';
                break;
            case 'jobs':
                endpoint = '/api/jobs';
                break;
            case 'summary':
                endpoint = '/api/dashboard/summary';
                break;
            default:
                throw new Error('Invalid export type');
        }
        
        const response = await fetch(`${endpoint}?${params}`);
        if (!response.ok) {
            throw new Error('Failed to fetch data for export');
        }
        
        return await response.json();
    }
    
    convertToCSV(data, exportType) {
        let headers = [];
        let rows = [];
        
        switch (exportType) {
            case 'expenses':
                headers = ['Date', 'Vendor', 'Amount', 'Category', 'Job', 'Description'];
                rows = data.map(expense => [
                    new Date(expense.date).toLocaleDateString(),
                    expense.vendor,
                    `$${(expense.amount_cents / 100).toFixed(2)}`,
                    expense.category,
                    expense.job_name || 'N/A',
                    expense.description || ''
                ]);
                break;
                
            case 'jobs':
                headers = ['Job Name', 'Status', 'Budget', 'Spent', 'Profit', 'Margin %', 'Start Date'];
                rows = data.map(job => [
                    job.job_name,
                    job.status,
                    `$${(job.budget_cents / 100).toFixed(2)}`,
                    `$${(job.spent_cents / 100).toFixed(2)}`,
                    `$${(job.profit_cents / 100).toFixed(2)}`,
                    `${job.profit_margin_percent.toFixed(1)}%`,
                    new Date(job.start_date).toLocaleDateString()
                ]);
                break;
                
            case 'summary':
                headers = ['Metric', 'Value', 'Period'];
                rows = [
                    ['Total Revenue', `$${(data.total_revenue || 0).toFixed(2)}`, 'Monthly'],
                    ['Total Expenses', `$${(data.total_expenses || 0).toFixed(2)}`, 'Monthly'],
                    ['Net Profit', `$${(data.net_profit || 0).toFixed(2)}`, 'Monthly'],
                    ['Active Jobs', data.active_jobs || 0, 'Current'],
                    ['Average Margin', `${(data.avg_margin || 0).toFixed(1)}%`, 'Current']
                ];
                break;
        }
        
        // Add totals row if requested
        const includeTotals = document.getElementById('includeTotals')?.checked;
        if (includeTotals && exportType === 'expenses') {
            const totalAmount = data.reduce((sum, expense) => sum + expense.amount_cents, 0);
            rows.push(['TOTAL', '', `$${(totalAmount / 100).toFixed(2)}`, '', '', '']);
        }
        
        // Convert to CSV format
        const csvContent = [
            headers.join(','),
            ...rows.map(row => row.map(cell => `"${cell}"`).join(','))
        ].join('\n');
        
        return csvContent;
    }
    
    generatePDFHTML(data, exportType, fromDate, toDate) {
        const title = this.getExportTitle(exportType);
        const dateRange = `${fromDate} to ${toDate}`;
        
        let content = '';
        
        switch (exportType) {
            case 'expenses':
                content = this.generateExpensesHTML(data);
                break;
            case 'jobs':
                content = this.generateJobsHTML(data);
                break;
            case 'summary':
                content = this.generateSummaryHTML(data);
                break;
        }
        
        return `
            <!DOCTYPE html>
            <html>
            <head>
                <title>${title}</title>
                <style>
                    body { font-family: Arial, sans-serif; margin: 20px; }
                    .header { text-align: center; margin-bottom: 30px; }
                    .title { font-size: 24px; font-weight: bold; color: #9B6EC8; }
                    .subtitle { font-size: 14px; color: #666; margin-top: 5px; }
                    table { width: 100%; border-collapse: collapse; margin-top: 20px; }
                    th, td { border: 1px solid #ddd; padding: 8px; text-align: left; }
                    th { background-color: #f5f5f5; font-weight: bold; }
                    .total-row { background-color: #f0f0f0; font-weight: bold; }
                    @media print { body { margin: 0; } }
                </style>
            </head>
            <body>
                <div class="header">
                    <div class="title">${title}</div>
                    <div class="subtitle">Generated on ${new Date().toLocaleDateString()} | Period: ${dateRange}</div>
                </div>
                ${content}
            </body>
            </html>
        `;
    }
    
    generateExpensesHTML(data) {
        const totalAmount = data.reduce((sum, expense) => sum + expense.amount_cents, 0);
        
        return `
            <table>
                <thead>
                    <tr>
                        <th>Date</th>
                        <th>Vendor</th>
                        <th>Amount</th>
                        <th>Category</th>
                        <th>Job</th>
                        <th>Description</th>
                    </tr>
                </thead>
                <tbody>
                    ${data.map(expense => `
                        <tr>
                            <td>${new Date(expense.date).toLocaleDateString()}</td>
                            <td>${expense.vendor}</td>
                            <td>$${(expense.amount_cents / 100).toFixed(2)}</td>
                            <td>${expense.category}</td>
                            <td>${expense.job_name || 'N/A'}</td>
                            <td>${expense.description || ''}</td>
                        </tr>
                    `).join('')}
                    <tr class="total-row">
                        <td colspan="2"><strong>TOTAL</strong></td>
                        <td><strong>$${(totalAmount / 100).toFixed(2)}</strong></td>
                        <td colspan="3"></td>
                    </tr>
                </tbody>
            </table>
        `;
    }
    
    generateJobsHTML(data) {
        return `
            <table>
                <thead>
                    <tr>
                        <th>Job Name</th>
                        <th>Status</th>
                        <th>Budget</th>
                        <th>Spent</th>
                        <th>Profit</th>
                        <th>Margin %</th>
                    </tr>
                </thead>
                <tbody>
                    ${data.map(job => `
                        <tr>
                            <td>${job.job_name}</td>
                            <td>${job.status}</td>
                            <td>$${(job.budget_cents / 100).toFixed(2)}</td>
                            <td>$${(job.spent_cents / 100).toFixed(2)}</td>
                            <td>$${(job.profit_cents / 100).toFixed(2)}</td>
                            <td>${job.profit_margin_percent.toFixed(1)}%</td>
                        </tr>
                    `).join('')}
                </tbody>
            </table>
        `;
    }
    
    generateSummaryHTML(data) {
        return `
            <table>
                <thead>
                    <tr>
                        <th>Metric</th>
                        <th>Value</th>
                        <th>Period</th>
                    </tr>
                </thead>
                <tbody>
                    <tr>
                        <td>Total Revenue</td>
                        <td>$${(data.total_revenue || 0).toFixed(2)}</td>
                        <td>Monthly</td>
                    </tr>
                    <tr>
                        <td>Total Expenses</td>
                        <td>$${(data.total_expenses || 0).toFixed(2)}</td>
                        <td>Monthly</td>
                    </tr>
                    <tr>
                        <td>Net Profit</td>
                        <td>$${(data.net_profit || 0).toFixed(2)}</td>
                        <td>Monthly</td>
                    </tr>
                    <tr>
                        <td>Active Jobs</td>
                        <td>${data.active_jobs || 0}</td>
                        <td>Current</td>
                    </tr>
                    <tr>
                        <td>Average Margin</td>
                        <td>${(data.avg_margin || 0).toFixed(1)}%</td>
                        <td>Current</td>
                    </tr>
                </tbody>
            </table>
        `;
    }
    
    getExportTitle(exportType) {
        switch (exportType) {
            case 'expenses': return 'CORA Expenses Report';
            case 'jobs': return 'CORA Jobs Report';
            case 'summary': return 'CORA Summary Report';
            default: return 'CORA Export';
        }
    }
    
    downloadCSV(csvContent, filename) {
        const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' });
        const link = document.createElement('a');
        link.href = URL.createObjectURL(blob);
        link.download = filename;
        link.click();
        URL.revokeObjectURL(link.href);
    }
    
    downloadPDF(htmlContent, filename) {
        // Create a new window with the HTML content
        const newWindow = window.open('', '_blank');
        newWindow.document.write(htmlContent);
        newWindow.document.close();
        
        // Trigger print dialog
        setTimeout(() => {
            newWindow.print();
        }, 500);
    }
    
    updateExportButton(isExporting) {
        const exportBtn = document.querySelector('.export-btn');
        if (exportBtn) {
            if (isExporting) {
                exportBtn.innerHTML = '⏳ Exporting...';
                exportBtn.disabled = true;
            } else {
                exportBtn.innerHTML = '📊 Export';
                exportBtn.disabled = false;
            }
        }
    }
    
    showSuccessMessage(exportType, format) {
        const message = `Successfully exported ${exportType} data as ${format.toUpperCase()}`;
        this.showNotification('success', message);
    }
    
    showErrorMessage(message) {
        this.showNotification('error', `Export failed: ${message}`);
    }
    
    showNotification(type, message) {
        const notification = document.createElement('div');
        notification.className = `export-notification ${type}`;
        notification.innerHTML = `
            <div class="notification-content">
                <div class="notification-icon">${type === 'success' ? '✅' : '❌'}</div>
                <div class="notification-text">${message}</div>
            </div>
        `;
        
        document.body.appendChild(notification);
        
        setTimeout(() => {
            notification.remove();
        }, 5000);
    }
    
    closeModal() {
        const modal = document.querySelector('.export-modal');
        if (modal) {
            modal.classList.remove('open');
            setTimeout(() => {
                modal.remove();
            }, 300);
        }
    }
    
    addExportStyles() {
        const styleId = 'export-manager-styles';
        if (document.getElementById(styleId)) return;
        
        const styles = `
            .export-btn {
                background: #9B6EC8;
                color: white;
                border: none;
                border-radius: 6px;
                padding: 8px 12px;
                font-size: 12px;
                font-weight: 500;
                cursor: pointer;
                transition: all 0.2s ease;
                margin-left: 8px;
            }
            
            .export-btn:hover:not(:disabled) {
                background: #7C3AED;
                transform: translateY(-1px);
            }
            
            .export-btn:disabled {
                opacity: 0.6;
                cursor: not-allowed;
            }
            
            .export-modal {
                position: fixed;
                top: 0;
                left: 0;
                width: 100%;
                height: 100%;
                z-index: 10000;
                display: none;
                align-items: center;
                justify-content: center;
            }
            
            .export-modal.open {
                display: flex;
            }
            
            .export-modal .modal-overlay {
                position: absolute;
                top: 0;
                left: 0;
                width: 100%;
                height: 100%;
                background: rgba(0, 0, 0, 0.5);
                backdrop-filter: blur(4px);
            }
            
            .export-modal .modal-content {
                position: relative;
                background: white;
                border-radius: 12px;
                box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
                width: 90%;
                max-width: 600px;
                max-height: 90vh;
                overflow-y: auto;
                animation: modalSlideIn 0.3s ease;
            }
            
            @keyframes modalSlideIn {
                from {
                    transform: translateY(-20px);
                    opacity: 0;
                }
                to {
                    transform: translateY(0);
                    opacity: 1;
                }
            }
            
            .export-modal .modal-header {
                padding: 20px 24px;
                border-bottom: 1px solid #e5e7eb;
                display: flex;
                justify-content: space-between;
                align-items: center;
            }
            
            .export-modal .modal-header h3 {
                margin: 0;
                font-size: 18px;
                font-weight: 600;
                color: #111827;
            }
            
            .export-modal .close-btn {
                background: none;
                border: none;
                font-size: 24px;
                color: #6b7280;
                cursor: pointer;
                padding: 4px;
                border-radius: 4px;
                transition: all 0.2s ease;
            }
            
            .export-modal .close-btn:hover {
                background: #f3f4f6;
                color: #374151;
            }
            
            .export-modal .modal-body {
                padding: 24px;
            }
            
            .export-section {
                margin-bottom: 24px;
            }
            
            .export-section h4 {
                margin: 0 0 12px 0;
                font-size: 14px;
                font-weight: 600;
                color: #374151;
            }
            
            .export-options, .format-options {
                display: flex;
                flex-direction: column;
                gap: 8px;
            }
            
            .export-option, .format-option {
                display: flex;
                align-items: center;
                cursor: pointer;
            }
            
            .export-option input, .format-option input {
                margin-right: 12px;
            }
            
            .option-content {
                display: flex;
                align-items: center;
                gap: 12px;
                padding: 12px;
                border: 1px solid #e5e7eb;
                border-radius: 8px;
                flex: 1;
                transition: all 0.2s ease;
            }
            
            .export-option input:checked + .option-content,
            .format-option input:checked + .option-content {
                border-color: #9B6EC8;
                background: #f8f7ff;
            }
            
            .option-icon {
                font-size: 20px;
            }
            
            .option-text strong {
                display: block;
                font-size: 14px;
                color: #111827;
            }
            
            .option-text small {
                display: block;
                font-size: 12px;
                color: #6b7280;
                margin-top: 2px;
            }
            
            .date-filters {
                display: flex;
                gap: 16px;
            }
            
            .date-input {
                flex: 1;
            }
            
            .date-input label {
                display: block;
                font-size: 12px;
                color: #374151;
                margin-bottom: 4px;
            }
            
            .date-input input {
                width: 100%;
                padding: 8px 12px;
                border: 1px solid #d1d5db;
                border-radius: 6px;
                font-size: 14px;
            }
            
            .csv-options {
                display: flex;
                flex-direction: column;
                gap: 8px;
            }
            
            .checkbox-option {
                display: flex;
                align-items: center;
                gap: 8px;
                cursor: pointer;
            }
            
            .checkbox-option input {
                margin: 0;
            }
            
            .export-modal .modal-footer {
                padding: 20px 24px;
                border-top: 1px solid #e5e7eb;
                display: flex;
                justify-content: flex-end;
                gap: 12px;
            }
            
            .btn-primary, .btn-secondary {
                padding: 10px 20px;
                border-radius: 6px;
                font-size: 14px;
                font-weight: 500;
                cursor: pointer;
                transition: all 0.2s ease;
                border: none;
            }
            
            .btn-primary {
                background: #9B6EC8;
                color: white;
            }
            
            .btn-primary:hover:not(:disabled) {
                background: #7C3AED;
            }
            
            .btn-secondary {
                background: #f3f4f6;
                color: #374151;
                border: 1px solid #d1d5db;
            }
            
            .btn-secondary:hover {
                background: #e5e7eb;
            }
            
            .export-notification {
                position: fixed;
                top: 20px;
                right: 20px;
                background: white;
                border-radius: 8px;
                box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
                padding: 12px 16px;
                z-index: 10001;
                animation: slideInRight 0.3s ease;
                max-width: 300px;
            }
            
            .export-notification.success {
                border-left: 4px solid #10b981;
            }
            
            .export-notification.error {
                border-left: 4px solid #ef4444;
            }
            
            .export-notification .notification-content {
                display: flex;
                align-items: center;
                gap: 8px;
            }
            
            .export-notification .notification-icon {
                font-size: 16px;
            }
            
            .export-notification .notification-text {
                font-size: 14px;
                color: #374151;
            }
            
            @keyframes slideInRight {
                from {
                    transform: translateX(100%);
                    opacity: 0;
                }
                to {
                    transform: translateX(0);
                    opacity: 1;
                }
            }
            
            @media (max-width: 768px) {
                .export-modal .modal-content {
                    width: 95%;
                    margin: 20px;
                }
                
                .date-filters {
                    flex-direction: column;
                }
                
                .export-btn {
                    display: none; /* Hide on mobile to avoid clutter */
                }
            }
        `;
        
        const styleElement = document.createElement('style');
        styleElement.id = styleId;
        styleElement.textContent = styles;
        document.head.appendChild(styleElement);
    }
}

// Auto-initialize when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
    window.exportManager = new ExportManager();
});

// Export for use in other modules
if (typeof module !== 'undefined' && module.exports) {
    module.exports = ExportManager;
} 