// Profit Intelligence Dashboard JavaScript
// Handles data fetching, chart rendering, and interactive functionality

class ProfitIntelligenceDashboard {
    constructor() {
        this.charts = {};
        this.data = null;
        this.currentTab = 'forecasting';
        this.init();
    }

    async init() {
        await this.loadData();
        this.initializeCharts();
        this.setupEventListeners();
        this.startRealTimeUpdates();
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
            forecast: {
                months: ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun'],
                actual: [45000, 52000, 48000, 55000, 58000, 62000],
                predicted: [null, null, null, 61000, 65000, 68000]
            },
            vendors: [
                { name: 'ABC Construction', performance: 92, cost: 45000, trend: 5.2 },
                { name: 'XYZ Materials', performance: 88, cost: 32000, trend: -2.1 },
                { name: 'Best Tools Co', performance: 85, cost: 28000, trend: 1.8 },
                { name: 'Quality Lumber', performance: 82, cost: 22000, trend: -1.5 },
                { name: 'Pro Electric', performance: 79, cost: 18000, trend: 3.2 }
            ],
            jobs: [
                { name: 'Kitchen Remodel - Smith', risk: 'high', potential: 25000, completion: 65 },
                { name: 'Bathroom Addition - Johnson', risk: 'low', potential: 18000, completion: 85 },
                { name: 'Deck Construction - Davis', risk: 'medium', potential: 12000, completion: 45 }
            ],
            pricing: {
                marketAverage: 118,
                yourAverage: 125,
                recommendations: [
                    { service: 'Kitchen Remodel', currentPrice: 125, suggestedPrice: 135, confidence: 85 },
                    { service: 'Bathroom Remodel', currentPrice: 95, suggestedPrice: 102, confidence: 78 },
                    { service: 'Deck Construction', currentPrice: 45, suggestedPrice: 48, confidence: 92 }
                ]
            },
            benchmarks: {
                profitMargin: { your: 18.5, industry: 15.2 },
                completionRate: { your: 94, industry: 87 },
                satisfaction: { your: 4.2, industry: 3.8 },
                efficiency: { your: 78, industry: 72 }
            }
        };
    }

    initializeCharts() {
        this.createForecastChart();
        this.createVendorChart();
        this.createJobChart();
        this.createPricingChart();
        this.createBenchmarkChart();
        this.populateVendorList();
        this.populateJobAlerts();
    }

    createForecastChart() {
        const ctx = document.getElementById('forecastChart');
        if (!ctx) return;

        this.charts.forecast = new Chart(ctx, {
            type: 'line',
            data: {
                labels: this.data.forecast.months,
                datasets: [
                    {
                        label: 'Actual Costs',
                        data: this.data.forecast.actual,
                        borderColor: '#8B00FF',
                        backgroundColor: 'rgba(139, 0, 255, 0.1)',
                        borderWidth: 3,
                        fill: false,
                        tension: 0.4
                    },
                    {
                        label: 'Predicted Costs',
                        data: this.data.forecast.predicted,
                        borderColor: '#00FF88',
                        backgroundColor: 'rgba(0, 255, 136, 0.1)',
                        borderWidth: 3,
                        fill: false,
                        tension: 0.4,
                        borderDash: [5, 5]
                    }
                ]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        labels: {
                            color: '#e2e8f0'
                        }
                    }
                },
                scales: {
                    x: {
                        ticks: {
                            color: '#a0aec0'
                        },
                        grid: {
                            color: 'rgba(160, 174, 192, 0.1)'
                        }
                    },
                    y: {
                        ticks: {
                            color: '#a0aec0',
                            callback: function(value) {
                                return '$' + (value / 1000) + 'k';
                            }
                        },
                        grid: {
                            color: 'rgba(160, 174, 192, 0.1)'
                        }
                    }
                }
            }
        });
    }

    createVendorChart() {
        const ctx = document.getElementById('vendorChart');
        if (!ctx) return;

        const vendorData = this.data.vendors.slice(0, 5);
        
        this.charts.vendor = new Chart(ctx, {
            type: 'bar',
            data: {
                labels: vendorData.map(v => v.name),
                datasets: [{
                    label: 'Performance Score',
                    data: vendorData.map(v => v.performance),
                    backgroundColor: [
                        'rgba(139, 0, 255, 0.8)',
                        'rgba(160, 32, 240, 0.8)',
                        'rgba(0, 255, 136, 0.8)',
                        'rgba(255, 165, 0, 0.8)',
                        'rgba(255, 68, 68, 0.8)'
                    ],
                    borderColor: [
                        '#8B00FF',
                        '#A020F0',
                        '#00FF88',
                        '#FFA500',
                        '#FF4444'
                    ],
                    borderWidth: 2,
                    borderRadius: 8
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        display: false
                    }
                },
                scales: {
                    x: {
                        ticks: {
                            color: '#a0aec0',
                            maxRotation: 45
                        },
                        grid: {
                            color: 'rgba(160, 174, 192, 0.1)'
                        }
                    },
                    y: {
                        ticks: {
                            color: '#a0aec0'
                        },
                        grid: {
                            color: 'rgba(160, 174, 192, 0.1)'
                        }
                    }
                }
            }
        });
    }

    createJobChart() {
        const ctx = document.getElementById('jobChart');
        if (!ctx) return;

        const jobData = this.data.jobs;
        
        this.charts.job = new Chart(ctx, {
            type: 'doughnut',
            data: {
                labels: jobData.map(j => j.name),
                datasets: [{
                    data: jobData.map(j => j.potential),
                    backgroundColor: [
                        'rgba(255, 68, 68, 0.8)',
                        'rgba(0, 255, 136, 0.8)',
                        'rgba(255, 165, 0, 0.8)'
                    ],
                    borderColor: [
                        '#FF4444',
                        '#00FF88',
                        '#FFA500'
                    ],
                    borderWidth: 2
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        position: 'bottom',
                        labels: {
                            color: '#e2e8f0',
                            padding: 20
                        }
                    }
                }
            }
        });
    }

    createPricingChart() {
        const ctx = document.getElementById('pricingChart');
        if (!ctx) return;

        const pricingData = this.data.pricing.recommendations;
        
        this.charts.pricing = new Chart(ctx, {
            type: 'bar',
            data: {
                labels: pricingData.map(p => p.service),
                datasets: [
                    {
                        label: 'Current Price',
                        data: pricingData.map(p => p.currentPrice),
                        backgroundColor: 'rgba(139, 0, 255, 0.6)',
                        borderColor: '#8B00FF',
                        borderWidth: 2
                    },
                    {
                        label: 'Suggested Price',
                        data: pricingData.map(p => p.suggestedPrice),
                        backgroundColor: 'rgba(0, 255, 136, 0.6)',
                        borderColor: '#00FF88',
                        borderWidth: 2
                    }
                ]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        labels: {
                            color: '#e2e8f0'
                        }
                    }
                },
                scales: {
                    x: {
                        ticks: {
                            color: '#a0aec0'
                        },
                        grid: {
                            color: 'rgba(160, 174, 192, 0.1)'
                        }
                    },
                    y: {
                        ticks: {
                            color: '#a0aec0'
                        },
                        grid: {
                            color: 'rgba(160, 174, 192, 0.1)'
                        }
                    }
                }
            }
        });
    }

    createBenchmarkChart() {
        const ctx = document.getElementById('benchmarkChart');
        if (!ctx) return;

        const benchmarkData = this.data.benchmarks;
        
        this.charts.benchmark = new Chart(ctx, {
            type: 'radar',
            data: {
                labels: ['Profit Margin', 'Completion Rate', 'Customer Satisfaction', 'Efficiency'],
                datasets: [
                    {
                        label: 'Your Performance',
                        data: [
                            benchmarkData.profitMargin.your,
                            benchmarkData.completionRate.your,
                            benchmarkData.satisfaction.your * 20, // Scale to 0-100
                            benchmarkData.efficiency.your
                        ],
                        backgroundColor: 'rgba(139, 0, 255, 0.2)',
                        borderColor: '#8B00FF',
                        borderWidth: 3,
                        pointBackgroundColor: '#8B00FF'
                    },
                    {
                        label: 'Industry Average',
                        data: [
                            benchmarkData.profitMargin.industry,
                            benchmarkData.completionRate.industry,
                            benchmarkData.satisfaction.industry * 20, // Scale to 0-100
                            benchmarkData.efficiency.industry
                        ],
                        backgroundColor: 'rgba(160, 174, 192, 0.2)',
                        borderColor: '#a0aec0',
                        borderWidth: 2,
                        pointBackgroundColor: '#a0aec0'
                    }
                ]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        labels: {
                            color: '#e2e8f0'
                        }
                    }
                },
                scales: {
                    r: {
                        ticks: {
                            color: '#a0aec0',
                            backdropColor: 'transparent'
                        },
                        grid: {
                            color: 'rgba(160, 174, 192, 0.1)'
                        },
                        pointLabels: {
                            color: '#e2e8f0'
                        }
                    }
                }
            }
        });
    }

    populateVendorList() {
        const vendorList = document.getElementById('vendorList');
        if (!vendorList) return;

        vendorList.innerHTML = this.data.vendors.map(vendor => `
            <div class="vendor-card">
                <div class="vendor-info">
                    <h5>${vendor.name}</h5>
                    <p>$${(vendor.cost / 1000).toFixed(1)}k • ${vendor.trend > 0 ? '+' : ''}${vendor.trend}% trend</p>
                </div>
                <div class="vendor-score">
                    ${vendor.performance}
                </div>
            </div>
        `).join('');
    }

    populateJobAlerts() {
        const highRiskJobs = document.getElementById('highRiskJobs');
        const highPotentialJobs = document.getElementById('highPotentialJobs');
        
        if (highRiskJobs) {
            const highRisk = this.data.jobs.filter(job => job.risk === 'high');
            highRiskJobs.innerHTML = highRisk.map(job => `
                <div class="alert-card">
                    <div class="alert-icon">
                        <i class="fas fa-exclamation-triangle"></i>
                    </div>
                    <div>
                        <h6>${job.name}</h6>
                        <p>${job.completion}% complete • Potential: $${(job.potential / 1000).toFixed(1)}k</p>
                    </div>
                </div>
            `).join('');
        }
        
        if (highPotentialJobs) {
            const highPotential = this.data.jobs.filter(job => job.risk === 'low');
            highPotentialJobs.innerHTML = highPotential.map(job => `
                <div class="alert-card" style="background: rgba(0, 255, 136, 0.1); border-color: rgba(0, 255, 136, 0.3);">
                    <div class="alert-icon" style="background: rgba(0, 255, 136, 0.2); color: #00FF88;">
                        <i class="fas fa-check-circle"></i>
                    </div>
                    <div>
                        <h6>${job.name}</h6>
                        <p>${job.completion}% complete • Potential: $${(job.potential / 1000).toFixed(1)}k</p>
                    </div>
                </div>
            `).join('');
        }
    }

    setupEventListeners() {
        // Tab switching
        const tabs = document.querySelectorAll('[data-bs-toggle="tab"]');
        tabs.forEach(tab => {
            tab.addEventListener('shown.bs.tab', (event) => {
                this.currentTab = event.target.id.replace('-tab', '');
                this.resizeCharts();
            });
        });

        // Export buttons
        document.addEventListener('click', (event) => {
            if (event.target.classList.contains('export-btn')) {
                const action = event.target.getAttribute('onclick');
                if (action) {
                    eval(action);
                }
            }
        });
    }

    resizeCharts() {
        // Resize charts when tab changes
        Object.values(this.charts).forEach(chart => {
            if (chart && chart.resize) {
                chart.resize();
            }
        });
    }

    startRealTimeUpdates() {
        // Update data every 5 minutes
        setInterval(async () => {
            await this.loadData();
            this.updateCharts();
        }, 5 * 60 * 1000);
    }

    updateCharts() {
        // Update chart data with new information
        if (this.charts.forecast) {
            this.charts.forecast.data.datasets[0].data = this.data.forecast.actual;
            this.charts.forecast.data.datasets[1].data = this.data.forecast.predicted;
            this.charts.forecast.update();
        }

        // Update main score
        const mainScore = document.getElementById('mainScore');
        const mainGrade = document.getElementById('mainGrade');
        if (mainScore) mainScore.textContent = this.data.intelligenceScore;
        if (mainGrade) mainGrade.textContent = this.data.letterGrade;
    }
}

// Export functions
function exportForecast() {
    downloadReport('forecasting', 'Cost Forecasting Report');
}

function exportVendors() {
    downloadReport('vendors', 'Vendor Performance Report');
}

function exportJobs() {
    downloadReport('jobs', 'Job Predictions Report');
}

function exportPricing() {
    downloadReport('pricing', 'Pricing Intelligence Report');
}

function exportBenchmarks() {
    downloadReport('benchmarks', 'Industry Benchmarks Report');
}

async function downloadReport(type, title) {
    try {
        // Show loading state
        const button = event.target;
        const originalText = button.textContent;
        button.textContent = 'Generating...';
        button.disabled = true;
        
        // Call real PDF export API
        const response = await fetch(`/api/pdf-export/profit-intelligence/section/${type}`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${localStorage.getItem('access_token')}`
            }
        });
        
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        const result = await response.json();
        
        if (result.status === 'success') {
            // Download the generated PDF
            const downloadResponse = await fetch(result.download_url, {
                headers: {
                    'Authorization': `Bearer ${localStorage.getItem('access_token')}`
                }
            });
            
            if (downloadResponse.ok) {
                const blob = await downloadResponse.blob();
                const url = window.URL.createObjectURL(blob);
                const a = document.createElement('a');
                a.href = url;
                a.download = result.filename;
                document.body.appendChild(a);
                a.click();
                document.body.removeChild(a);
                window.URL.revokeObjectURL(url);
                
                // Show success notification
                showNotification('Report generated and downloaded successfully!', 'success');
            } else {
                throw new Error('Failed to download report');
            }
        } else {
            throw new Error(result.message || 'Failed to generate report');
        }
        
    } catch (error) {
        // console.error('Error generating report:', error);
        showNotification('Failed to generate report: ' + error.message, 'error');
    } finally {
        // Reset button
        const button = event.target;
        button.textContent = originalText;
        button.disabled = false;
    }
}

// Helper function to show notifications
function showNotification(message, type = 'info') {
    // Create notification element
    const notification = document.createElement('div');
    notification.className = `alert alert-${type === 'success' ? 'success' : type === 'error' ? 'danger' : 'info'} alert-dismissible fade show`;
    notification.style.position = 'fixed';
    notification.style.top = '20px';
    notification.style.right = '20px';
    notification.style.zIndex = '9999';
    notification.style.minWidth = '300px';
    
    notification.innerHTML = `
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    `;
    
    document.body.appendChild(notification);
    
    // Auto-remove after 5 seconds
    setTimeout(() => {
        if (notification.parentNode) {
            notification.parentNode.removeChild(notification);
        }
    }, 5000);
}

// Initialize dashboard when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    new ProfitIntelligenceDashboard();
});

// WebSocket connection for real-time updates (if available)
function setupWebSocket() {
    try {
        const ws = new WebSocket('ws://localhost:8000/ws/profit-intelligence');
        
        ws.onmessage = (event) => {
            const data = JSON.parse(event.data);
            // Handle real-time updates
            // console.log('Real-time update received:', data);
        };
        
        ws.onerror = (error) => {
            // console.log('WebSocket not available, using polling instead');
        };
    } catch (error) {
        // console.log('WebSocket not available, using polling instead');
    }
}

// Setup WebSocket if available
setupWebSocket(); 