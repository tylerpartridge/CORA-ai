// Minimal Export Manager module
// Exports a class that binds export buttons to backend endpoints

export class ExportManager {
    constructor(options = {}) {
        this.options = options;
        this.bound = false;
        this.init();
    }

    init() {
        if (this.bound) return;
        this.bindExpenseExport();
        this.bindDashboardExport();
        this.bound = true;
    }

    bindExpenseExport() {
        const buttons = document.querySelectorAll('[data-export="expenses"]');
        buttons.forEach((btn) => {
            btn.addEventListener('click', (e) => {
                e.preventDefault();
                // Simple navigation triggers CSV download from backend
                window.location.href = '/api/expenses/export';
            });
        });
    }

    bindDashboardExport() {
        const buttons = document.querySelectorAll('[data-export="dashboard"]');
        buttons.forEach((btn) => {
            btn.addEventListener('click', (e) => {
                e.preventDefault();
                window.location.href = '/api/dashboard/export?format=csv';
            });
        });
    }
}


