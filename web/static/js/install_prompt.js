/**
 * CORA PWA Install Prompt
 * Handles app installation prompts and banners
 */

class InstallPrompt {
    constructor() {
        this.deferredPrompt = null;
        this.installBanner = null;
        this.isIOS = this.detectIOS();
        this.isStandalone = window.matchMedia('(display-mode: standalone)').matches;
        
        this.init();
    }
    
    init() {
        this.setupEventListeners();
        this.checkInstallability();
        
        // Show install button in header if eligible
        this.addInstallButton();
    }
    
    setupEventListeners() {
        // Listen for beforeinstallprompt event
        window.addEventListener('beforeinstallprompt', (e) => {
            // console.log('Install prompt available');
            e.preventDefault();
            this.deferredPrompt = e;
            this.showInstallBanner();
        });
        
        // Listen for app installed event
        window.addEventListener('appinstalled', (e) => {
            // console.log('App installed successfully');
            this.hideInstallBanner();
            this.trackInstallEvent();
            this.deferredPrompt = null;
        });
        
        // Listen for display mode changes
        window.matchMedia('(display-mode: standalone)').addEventListener('change', (e) => {
            this.isStandalone = e.matches;
            if (this.isStandalone) {
                this.hideInstallBanner();
            }
        });
    }
    
    detectIOS() {
        return /iPad|iPhone|iPod/.test(navigator.userAgent) && !window.MSStream;
    }
    
    checkInstallability() {
        // Check if already installed
        if (this.isStandalone) {
            // console.log('App already installed');
            return;
        }
        
        // Check if service worker is registered
        if ('serviceWorker' in navigator) {
            navigator.serviceWorker.getRegistration().then((registration) => {
                if (registration) {
                    // console.log('Service Worker registered, app installable');
                }
            });
        }
    }
    
    addInstallButton() {
        // Add install button to header if not already installed
        if (!this.isStandalone) {
            const header = document.querySelector('.header-actions');
            if (header) {
                const installBtn = document.createElement('button');
                installBtn.className = 'install-app-btn';
                installBtn.innerHTML = '📱 Install App';
                installBtn.title = 'Install CORA as an app';
                installBtn.onclick = () => this.showInstallBanner();
                
                header.appendChild(installBtn);
                this.addInstallButtonStyles();
            }
        }
    }
    
    showInstallBanner() {
        if (this.installBanner) {
            return; // Already showing
        }
        
        this.installBanner = this.createInstallBanner();
        document.body.appendChild(this.installBanner);
        
        // Animate in
        setTimeout(() => {
            this.installBanner.classList.add('show');
        }, 100);
    }
    
    createInstallBanner() {
        const banner = document.createElement('div');
        banner.className = 'install-banner';
        
        if (this.isIOS) {
            banner.innerHTML = this.createIOSBannerContent();
        } else {
            banner.innerHTML = this.createStandardBannerContent();
        }
        
        return banner;
    }
    
    createStandardBannerContent() {
        return `
            <div class="install-banner-content">
                <div class="install-banner-icon">📱</div>
                <div class="install-banner-text">
                    <h4>Install CORA</h4>
                    <p>Get quick access to voice expense tracking and job management</p>
                </div>
                <div class="install-banner-actions">
                    <button class="install-btn primary" onclick="installPrompt.installApp()">
                        Install
                    </button>
                    <button class="install-btn secondary" onclick="installPrompt.hideInstallBanner()">
                        Not Now
                    </button>
                </div>
            </div>
        `;
    }
    
    createIOSBannerContent() {
        return `
            <div class="install-banner-content">
                <div class="install-banner-icon">📱</div>
                <div class="install-banner-text">
                    <h4>Install CORA on iOS</h4>
                    <p>Tap the share button <span class="ios-share-icon">⎋</span> then "Add to Home Screen"</p>
                </div>
                <div class="install-banner-actions">
                    <button class="install-btn secondary" onclick="installPrompt.hideInstallBanner()">
                        Got It
                    </button>
                </div>
            </div>
        `;
    }
    
    async installApp() {
        if (!this.deferredPrompt) {
            // console.log('No install prompt available');
            return;
        }
        
        try {
            // Show the install prompt
            this.deferredPrompt.prompt();
            
            // Wait for user response
            const { outcome } = await this.deferredPrompt.userChoice;
            
            // console.log('Install prompt outcome:', outcome);
            
            if (outcome === 'accepted') {
                // console.log('User accepted install prompt');
                this.trackInstallEvent('accepted');
            } else {
                // console.log('User dismissed install prompt');
                this.trackInstallEvent('dismissed');
            }
            
            // Clear the deferred prompt
            this.deferredPrompt = null;
            
        } catch (error) {
            // console.error('Error showing install prompt:', error);
        }
    }
    
    hideInstallBanner() {
        if (this.installBanner) {
            this.installBanner.classList.remove('show');
            setTimeout(() => {
                if (this.installBanner && this.installBanner.parentNode) {
                    this.installBanner.parentNode.removeChild(this.installBanner);
                }
                this.installBanner = null;
            }, 300);
        }
    }
    
    trackInstallEvent(action = 'installed') {
        // Track install events for analytics
        if (typeof gtag !== 'undefined') {
            gtag('event', 'pwa_install', {
                event_category: 'engagement',
                event_label: action,
                value: 1
            });
        }
        
        // Send to our analytics endpoint
        fetch('/api/analytics/pwa-install', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                action: action,
                timestamp: new Date().toISOString(),
                userAgent: navigator.userAgent,
                platform: this.isIOS ? 'ios' : 'android'
            })
        }).catch(error => {
            // console.error('Failed to track install event:', error);
        });
    }
    
    addInstallButtonStyles() {
        const styleId = 'install-button-styles';
        if (document.getElementById(styleId)) return;
        
        const styles = `
            .install-app-btn {
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
            
            .install-app-btn:hover {
                background: #7C3AED;
                transform: translateY(-1px);
            }
            
            .install-banner {
                position: fixed;
                bottom: 0;
                left: 0;
                right: 0;
                background: white;
                border-top: 1px solid #e5e7eb;
                box-shadow: 0 -4px 12px rgba(0, 0, 0, 0.1);
                z-index: 10000;
                transform: translateY(100%);
                transition: transform 0.3s ease;
            }
            
            .install-banner.show {
                transform: translateY(0);
            }
            
            .install-banner-content {
                display: flex;
                align-items: center;
                padding: 16px;
                max-width: 1200px;
                margin: 0 auto;
                gap: 16px;
            }
            
            .install-banner-icon {
                font-size: 24px;
                flex-shrink: 0;
            }
            
            .install-banner-text {
                flex: 1;
            }
            
            .install-banner-text h4 {
                margin: 0 0 4px 0;
                font-size: 16px;
                font-weight: 600;
                color: #111827;
            }
            
            .install-banner-text p {
                margin: 0;
                font-size: 14px;
                color: #6b7280;
            }
            
            .install-banner-actions {
                display: flex;
                gap: 8px;
                flex-shrink: 0;
            }
            
            .install-btn {
                padding: 8px 16px;
                border-radius: 6px;
                font-size: 14px;
                font-weight: 500;
                cursor: pointer;
                transition: all 0.2s ease;
                border: none;
            }
            
            .install-btn.primary {
                background: #9B6EC8;
                color: white;
            }
            
            .install-btn.primary:hover {
                background: #7C3AED;
            }
            
            .install-btn.secondary {
                background: #f3f4f6;
                color: #374151;
                border: 1px solid #d1d5db;
            }
            
            .install-btn.secondary:hover {
                background: #e5e7eb;
            }
            
            .ios-share-icon {
                font-size: 18px;
                font-weight: bold;
                color: #9B6EC8;
            }
            
            @media (max-width: 768px) {
                .install-banner-content {
                    flex-direction: column;
                    text-align: center;
                    gap: 12px;
                }
                
                .install-banner-actions {
                    width: 100%;
                    justify-content: center;
                }
                
                .install-app-btn {
                    display: none; /* Hide on mobile to avoid clutter */
                }
            }
        `;
        
        const styleElement = document.createElement('style');
        styleElement.id = styleId;
        styleElement.textContent = styles;
        document.head.appendChild(styleElement);
    }
    
    // Check if app is installed
    isAppInstalled() {
        return this.isStandalone;
    }
    
    // Get install eligibility
    getInstallEligibility() {
        return {
            isIOS: this.isIOS,
            isStandalone: this.isStandalone,
            hasServiceWorker: 'serviceWorker' in navigator,
            hasInstallPrompt: !!this.deferredPrompt
        };
    }
}

// Auto-initialize when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
    window.installPrompt = new InstallPrompt();
});

// Export for use in other modules
if (typeof module !== 'undefined' && module.exports) {
    module.exports = InstallPrompt;
} 