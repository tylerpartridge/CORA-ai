/**
 * CORA Health Monitor
 * Monitors system health and provides real-time status updates
 */

class HealthMonitor {
    constructor(options = {}) {
        this.options = {
            checkInterval: 30000, // 30 seconds
            endpoint: '/api/status',
            indicatorId: 'system-health',
            ...options
        };
        
        this.isMonitoring = false;
        this.healthStatus = 'unknown';
        this.lastCheck = null;
        
        this.init();
    }
    
    init() {
        this.createHealthIndicator();
        this.startMonitoring();
    }
    
    createHealthIndicator() {
        // Create health indicator if it doesn't exist
        let indicator = document.getElementById(this.options.indicatorId);
        if (!indicator) {
            indicator = document.createElement('div');
            indicator.id = this.options.indicatorId;
            indicator.className = 'health-indicator';
            indicator.innerHTML = `
                <div class="health-dot"></div>
                <span class="health-text">System Status</span>
                <div class="health-tooltip">System Status</div>
            `;
            
            // Add to header if available
            const header = document.querySelector('.header-actions');
            if (header) {
                header.appendChild(indicator);
            } else {
                document.body.appendChild(indicator);
            }
        }
        
        this.addHealthStyles();
    }
    
    addHealthStyles() {
        const styleId = 'health-monitor-styles';
        if (document.getElementById(styleId)) return;
        
        const styles = `
            .health-indicator {
                display: flex;
                align-items: center;
                gap: 8px;
                padding: 8px 12px;
                border-radius: 20px;
                background: rgba(255, 255, 255, 0.1);
                backdrop-filter: blur(10px);
                border: 1px solid rgba(255, 255, 255, 0.2);
                font-size: 12px;
                font-weight: 500;
                color: #fff;
                transition: all 0.3s ease;
            }
            
            .health-dot {
                width: 8px;
                height: 8px;
                border-radius: 50%;
                background: #6b7280;
                transition: background 0.3s ease;
            }
            
            .health-indicator.healthy .health-dot {
                background: #10b981;
                box-shadow: 0 0 8px rgba(16, 185, 129, 0.5);
            }
            
            .health-indicator.degraded .health-dot {
                background: #f59e0b;
                box-shadow: 0 0 8px rgba(245, 158, 11, 0.5);
            }
            
            .health-indicator.error .health-dot {
                background: #ef4444;
                box-shadow: 0 0 8px rgba(239, 68, 68, 0.5);
                animation: pulse-error 2s infinite;
            }
            
            .health-indicator.checking .health-dot {
                background: #3b82f6;
                animation: pulse-checking 1s infinite;
            }
            
            @keyframes pulse-error {
                0%, 100% { opacity: 1; }
                50% { opacity: 0.5; }
            }
            
            @keyframes pulse-checking {
                0%, 100% { transform: scale(1); }
                50% { transform: scale(1.2); }
            }
            
            .health-text {
                font-size: 11px;
                opacity: 0.8;
            }
            
            .health-tooltip {
                position: absolute;
                bottom: 100%;
                left: 50%;
                transform: translateX(-50%);
                background: #1f2937;
                color: white;
                padding: 8px 12px;
                border-radius: 6px;
                font-size: 12px;
                white-space: nowrap;
                opacity: 0;
                pointer-events: none;
                transition: opacity 0.2s ease;
                z-index: 1000;
            }
            
            .health-tooltip::after {
                content: '';
                position: absolute;
                top: 100%;
                left: 50%;
                transform: translateX(-50%);
                border: 4px solid transparent;
                border-top-color: #1f2937;
            }
            
            .health-indicator:hover .health-tooltip {
                opacity: 1;
            }
            
            @media (max-width: 768px) {
                .health-indicator {
                    padding: 6px 8px;
                    font-size: 10px;
                }
                
                .health-text {
                    display: none;
                }
            }
        `;
        
        const styleElement = document.createElement('style');
        styleElement.id = styleId;
        styleElement.textContent = styles;
        document.head.appendChild(styleElement);
    }
    
    async checkSystemHealth() {
        try {
            this.setStatus('checking');
            
            const response = await fetch(this.options.endpoint, {
                method: 'GET',
                headers: {
                    'Accept': 'application/json'
                }
            });
            
            if (!response.ok) {
                throw new Error(`HTTP ${response.status}`);
            }
            
            const health = await response.json();
            this.lastCheck = new Date();
            
            // Determine health status
            let status = 'healthy';
            if (health.status !== 'healthy') {
                status = 'error';
            } else if (health.uptime) {
                // Check if uptime indicates recent restart
                const uptimeMinutes = this.parseUptime(health.uptime);
                if (uptimeMinutes < 5) {
                    status = 'degraded';
                }
            }
            
            this.setStatus(status);
            this.updateHealthIndicator(health);
            
            return health;
            
        } catch (error) {
            // console.error('Health check failed:', error);
            this.setStatus('error');
            return null;
        }
    }
    
    parseUptime(uptimeString) {
        // Parse uptime string like "24m 43s" to minutes
        const match = uptimeString.match(/(\d+)m\s*(\d+)s/);
        if (match) {
            return parseInt(match[1]) + parseInt(match[2]) / 60;
        }
        return 0;
    }
    
    setStatus(status) {
        this.healthStatus = status;
        const indicator = document.getElementById(this.options.indicatorId);
        if (indicator) {
            indicator.className = `health-indicator ${status}`;
        }
    }
    
    updateHealthIndicator(health) {
        const indicator = document.getElementById(this.options.indicatorId);
        if (!indicator) return;
        
        const textElement = indicator.querySelector('.health-text');
        if (textElement) {
            if (health.uptime) {
                textElement.textContent = `Uptime: ${health.uptime}`;
            } else {
                textElement.textContent = `Status: ${health.status}`;
            }
        }
    }
    
    startMonitoring() {
        if (this.isMonitoring) return;
        
        this.isMonitoring = true;
        
        // Initial check
        this.checkSystemHealth();
        
        // Set up periodic checks
        this.monitoringInterval = setInterval(() => {
            this.checkSystemHealth();
        }, this.options.checkInterval);
        
        // Listen for online/offline events
        window.addEventListener('online', () => {
            this.checkSystemHealth();
        });
        
        window.addEventListener('offline', () => {
            this.setStatus('error');
        });
    }
    
    stopMonitoring() {
        this.isMonitoring = false;
        if (this.monitoringInterval) {
            clearInterval(this.monitoringInterval);
            this.monitoringInterval = null;
        }
    }
    
    getStatus() {
        return {
            status: this.healthStatus,
            lastCheck: this.lastCheck,
            isMonitoring: this.isMonitoring
        };
    }
}

// Auto-initialize when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
    window.coraHealthMonitor = new HealthMonitor();
});

// Export for use in other modules
if (typeof module !== 'undefined' && module.exports) {
    module.exports = HealthMonitor;
} 