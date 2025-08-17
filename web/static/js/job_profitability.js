/**
 * Job Profitability Dashboard
 * Shows job profitability metrics and alerts
 */

class JobProfitabilityDashboard {
    constructor() {
        this.jobs = [];
        this.alerts = [];
        this.init();
    }

    async init() {
        await this.loadJobs();
        await this.loadAlerts();
        this.render();
        this.setupEventListeners();
    }

    async loadJobs() {
        try {
            const response = await fetch('/api/jobs');
            if (response.ok) {
                this.jobs = await response.json();
            }
        } catch (error) {
            // console.error('Error loading jobs:', error);
        }
    }

    async loadAlerts() {
        try {
            const response = await fetch('/api/alerts/summary');
            if (response.ok) {
                const summary = await response.json();
                this.alerts = summary.alerts || [];
            }
        } catch (error) {
            // console.error('Error loading alerts:', error);
        }
    }

    render() {
        this.renderJobCards();
        this.renderAlertBadge();
    }

    renderJobCards() {
        const container = document.getElementById('jobProfitabilityGrid');
        if (!container) return;

        if (this.jobs.length === 0) {
            container.innerHTML = '<p>No jobs found. Add your first job to see profitability metrics.</p>';
            return;
        }

        const jobCards = this.jobs.map(job => this.createJobCard(job)).join('');
        container.innerHTML = jobCards;
    }

    createJobCard(job) {
        const profit = job.quoted_amount - (job.total_spent || 0);
        const margin = job.quoted_amount > 0 ? (profit / job.quoted_amount * 100) : 0;
        const alertCount = this.alerts.filter(alert => alert.job_id === job.id).length;
        
        const alertBadge = alertCount > 0 ? `<div class="alert-badge">${alertCount}</div>` : '';
        
        return `
            <div class="job-profit-card ${margin < 20 ? 'low-margin' : ''}">
                ${alertBadge}
                <div class="job-header">
                    <h4>${job.job_name}</h4>
                    <div class="job-status ${job.status}">${job.status}</div>
                </div>
                <div class="job-profit-metrics">
                    <div class="job-metric">
                        <div class="job-metric-label">Quoted</div>
                        <div class="job-metric-value">$${job.quoted_amount?.toFixed(0) || 0}</div>
                    </div>
                    <div class="job-metric">
                        <div class="job-metric-label">Spent</div>
                        <div class="job-metric-value">$${(job.total_spent || 0).toFixed(0)}</div>
                    </div>
                    <div class="job-metric">
                        <div class="job-metric-label">Profit</div>
                        <div class="job-metric-value ${profit >= 0 ? 'positive' : 'negative'}">$${profit.toFixed(0)}</div>
                    </div>
                    <div class="job-metric">
                        <div class="job-metric-label">Margin</div>
                        <div class="job-metric-value ${margin >= 20 ? 'positive' : margin >= 10 ? 'warning' : 'negative'}">${margin.toFixed(1)}%</div>
                    </div>
                </div>
                <div class="job-progress">
                    <div class="progress-bar">
                        <div class="progress-fill" style="width: ${Math.min(100, (job.total_spent || 0) / job.quoted_amount * 100)}%"></div>
                    </div>
                    <div class="progress-label">${((job.total_spent || 0) / job.quoted_amount * 100).toFixed(1)}% of budget used</div>
                </div>
            </div>
        `;
    }

    renderAlertBadge() {
        const alertCount = document.getElementById('alertCount');
        if (!alertCount) return;

        const unreadAlerts = this.alerts.filter(alert => !alert.read).length;
        
        if (unreadAlerts > 0) {
            alertCount.textContent = unreadAlerts;
            alertCount.style.display = 'flex';
        } else {
            alertCount.style.display = 'none';
        }
    }

    setupEventListeners() {
        // Add click handlers for job cards
        document.addEventListener('click', (e) => {
            if (e.target.closest('.job-profit-card')) {
                const jobCard = e.target.closest('.job-profit-card');
                const jobName = jobCard.querySelector('h4').textContent;
                this.showJobDetails(jobName);
            }
        });
    }

    showJobDetails(jobName) {
        // Show job details modal or navigate to job page
        // console.log('Showing details for job:', jobName);
        // Implementation depends on your UI requirements
    }
}

// Initialize job profitability dashboard
document.addEventListener('DOMContentLoaded', () => {
    new JobProfitabilityDashboard();
});
