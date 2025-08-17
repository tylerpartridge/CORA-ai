/**
 * CORA Dark Mode Manager
 * Handles theme switching, system preference detection, and persistence
 * Enhanced for performance and accessibility
 */

class DarkModeManager {
    constructor() {
        this.theme = 'light';
        this.systemPreference = 'light';
        this.isInitialized = false;
        this.transitionDuration = 300;
        
        // Theme storage key
        this.storageKey = 'cora-theme-preference';
        
        // Initialize on DOM ready
        if (document.readyState === 'loading') {
            document.addEventListener('DOMContentLoaded', () => this.init());
        } else {
            this.init();
        }
    }

    /**
     * Initialize dark mode manager
     */
    init() {
        if (this.isInitialized) return;
        
        // Detect system preference
        this.detectSystemPreference();
        
        // Load saved preference or use system preference
        this.loadThemePreference();
        
        // Apply theme
        this.applyTheme();
        
        // Set up event listeners
        this.setupEventListeners();
        
        // Create theme toggle if it doesn't exist - DISABLED
        // this.createThemeToggle();
        
        this.isInitialized = true;
        
        // Dispatch custom event for other modules
        document.dispatchEvent(new CustomEvent('themeChanged', {
            detail: { theme: this.theme }
        }));
    }

    /**
     * Detect system color scheme preference
     */
    detectSystemPreference() {
        if (window.matchMedia) {
            const mediaQuery = window.matchMedia('(prefers-color-scheme: dark)');
            this.systemPreference = mediaQuery.matches ? 'dark' : 'light';
            
            // Listen for system preference changes
            mediaQuery.addEventListener('change', (e) => {
                this.systemPreference = e.matches ? 'dark' : 'light';
                
                // Only update if user hasn't set a manual preference
                if (!this.hasManualPreference()) {
                    this.setTheme(this.systemPreference);
                }
            });
        }
    }

    /**
     * Load theme preference from localStorage
     */
    loadThemePreference() {
        try {
            const saved = localStorage.getItem(this.storageKey);
            if (saved && (saved === 'light' || saved === 'dark')) {
                this.theme = saved;
            } else {
                // No saved preference, use system preference
                this.theme = this.systemPreference;
            }
        } catch (error) {
            // console.warn('Could not load theme preference:', error);
            this.theme = this.systemPreference;
        }
    }

    /**
     * Save theme preference to localStorage
     */
    saveThemePreference() {
        try {
            localStorage.setItem(this.storageKey, this.theme);
        } catch (error) {
            // console.warn('Could not save theme preference:', error);
        }
    }

    /**
     * Check if user has set a manual preference
     */
    hasManualPreference() {
        try {
            return localStorage.getItem(this.storageKey) !== null;
        } catch (error) {
            return false;
        }
    }

    /**
     * Apply current theme to document
     */
    applyTheme() {
        // Add transition class for smooth theme switching
        document.documentElement.classList.add('theme-transitioning');
        
        // Set data attribute for CSS targeting
        document.documentElement.setAttribute('data-theme', this.theme);
        
        // Update meta theme-color for mobile browsers
        this.updateMetaThemeColor();
        
        // Update theme toggle state
        this.updateThemeToggle();
        
        // Remove transition class after animation
        setTimeout(() => {
            document.documentElement.classList.remove('theme-transitioning');
        }, this.transitionDuration);
        
        // Dispatch custom event
        document.dispatchEvent(new CustomEvent('themeApplied', {
            detail: { theme: this.theme }
        }));
    }

    /**
     * Update meta theme-color for mobile browsers
     */
    updateMetaThemeColor() {
        let metaThemeColor = document.querySelector('meta[name="theme-color"]');
        
        if (!metaThemeColor) {
            metaThemeColor = document.createElement('meta');
            metaThemeColor.name = 'theme-color';
            document.head.appendChild(metaThemeColor);
        }
        
        // Set appropriate theme color based on current theme
        if (this.theme === 'dark') {
            metaThemeColor.content = '#1A202C';
        } else {
            metaThemeColor.content = '#9B6EC8';
        }
    }

    /**
     * Set theme and apply changes
     */
    setTheme(theme) {
        if (theme !== 'light' && theme !== 'dark') {
            // console.warn('Invalid theme:', theme);
            return;
        }
        
        if (this.theme === theme) return;
        
        this.theme = theme;
        this.saveThemePreference();
        this.applyTheme();
        
        // Analytics tracking (if available)
        this.trackThemeChange(theme);
    }

    /**
     * Toggle between light and dark themes
     */
    toggleTheme() {
        const newTheme = this.theme === 'light' ? 'dark' : 'light';
        this.setTheme(newTheme);
    }

    /**
     * Reset to system preference
     */
    resetToSystem() {
        this.setTheme(this.systemPreference);
        
        // Remove manual preference from storage
        try {
            localStorage.removeItem(this.storageKey);
        } catch (error) {
            // console.warn('Could not remove theme preference:', error);
        }
    }

    /**
     * Get current theme
     */
    getCurrentTheme() {
        return this.theme;
    }

    /**
     * Get system preference
     */
    getSystemPreference() {
        return this.systemPreference;
    }

    /**
     * Check if current theme is dark
     */
    isDark() {
        return this.theme === 'dark';
    }

    /**
     * Check if current theme is light
     */
    isLight() {
        return this.theme === 'light';
    }

    /**
     * Set up event listeners
     */
    setupEventListeners() {
        // Listen for theme toggle clicks
        document.addEventListener('click', (e) => {
            if (e.target.closest('.theme-toggle')) {
                e.preventDefault();
                this.toggleTheme();
            }
        });

        // Keyboard navigation for theme toggle
        document.addEventListener('keydown', (e) => {
            if (e.target.closest('.theme-toggle') && (e.key === 'Enter' || e.key === ' ')) {
                e.preventDefault();
                this.toggleTheme();
            }
        });

        // Listen for storage changes (other tabs)
        window.addEventListener('storage', (e) => {
            if (e.key === this.storageKey && e.newValue) {
                this.theme = e.newValue;
                this.applyTheme();
            }
        });
    }

    /**
     * Create theme toggle button if it doesn't exist
     */
    createThemeToggle() {
        // Check if toggle already exists
        if (document.querySelector('.theme-toggle')) {
            return;
        }

        // Find a good place to insert the toggle
        const header = document.querySelector('header, .navbar, .nav, .header');
        const nav = document.querySelector('nav');
        const container = header || nav || document.body;

        if (container) {
            const toggle = this.createToggleElement();
            
            // Insert at the beginning of the container
            if (container.firstChild) {
                container.insertBefore(toggle, container.firstChild);
            } else {
                container.appendChild(toggle);
            }
        }
    }

    /**
     * Create theme toggle element
     */
    createToggleElement() {
        const toggle = document.createElement('button');
        toggle.className = 'theme-toggle wellness-focus-visible';
        toggle.setAttribute('aria-label', 'Toggle dark mode');
        toggle.setAttribute('title', 'Switch between light and dark themes');
        toggle.setAttribute('role', 'button');
        toggle.setAttribute('tabindex', '0');

        // Sun icon
        const sunIcon = document.createElement('svg');
        sunIcon.className = 'sun-icon';
        sunIcon.setAttribute('viewBox', '0 0 24 24');
        sunIcon.setAttribute('fill', 'none');
        sunIcon.setAttribute('stroke', 'currentColor');
        sunIcon.setAttribute('stroke-width', '2');
        sunIcon.setAttribute('stroke-linecap', 'round');
        sunIcon.setAttribute('stroke-linejoin', 'round');
        sunIcon.innerHTML = `
            <circle cx="12" cy="12" r="5"/>
            <line x1="12" y1="1" x2="12" y2="3"/>
            <line x1="12" y1="21" x2="12" y2="23"/>
            <line x1="4.22" y1="4.22" x2="5.64" y2="5.64"/>
            <line x1="18.36" y1="18.36" x2="19.78" y2="19.78"/>
            <line x1="1" y1="12" x2="3" y2="12"/>
            <line x1="21" y1="12" x2="23" y2="12"/>
            <line x1="4.22" y1="19.78" x2="5.64" y2="18.36"/>
            <line x1="18.36" y1="5.64" x2="19.78" y2="4.22"/>
        `;

        // Moon icon
        const moonIcon = document.createElement('svg');
        moonIcon.className = 'moon-icon';
        moonIcon.setAttribute('viewBox', '0 0 24 24');
        moonIcon.setAttribute('fill', 'none');
        moonIcon.setAttribute('stroke', 'currentColor');
        moonIcon.setAttribute('stroke-width', '2');
        moonIcon.setAttribute('stroke-linecap', 'round');
        moonIcon.setAttribute('stroke-linejoin', 'round');
        moonIcon.innerHTML = `
            <path d="M21 12.79A9 9 0 1 1 11.21 3 7 7 0 0 0 21 12.79z"/>
        `;

        toggle.appendChild(sunIcon);
        toggle.appendChild(moonIcon);

        return toggle;
    }

    /**
     * Update theme toggle state
     */
    updateThemeToggle() {
        const toggle = document.querySelector('.theme-toggle');
        if (!toggle) return;

        const sunIcon = toggle.querySelector('.sun-icon');
        const moonIcon = toggle.querySelector('.moon-icon');

        if (this.theme === 'dark') {
            toggle.setAttribute('aria-label', 'Switch to light mode');
            toggle.setAttribute('title', 'Switch to light mode');
            if (sunIcon) sunIcon.style.display = 'none';
            if (moonIcon) moonIcon.style.display = 'block';
        } else {
            toggle.setAttribute('aria-label', 'Switch to dark mode');
            toggle.setAttribute('title', 'Switch to dark mode');
            if (sunIcon) sunIcon.style.display = 'block';
            if (moonIcon) moonIcon.style.display = 'none';
        }
    }

    /**
     * Track theme change for analytics
     */
    trackThemeChange(theme) {
        // Dispatch custom event for analytics
        document.dispatchEvent(new CustomEvent('themeAnalytics', {
            detail: { 
                theme: theme,
                previousTheme: this.theme,
                timestamp: Date.now()
            }
        }));

        // Google Analytics 4 (if available)
        if (typeof gtag !== 'undefined') {
            gtag('event', 'theme_change', {
                theme: theme,
                system_preference: this.systemPreference
            });
        }

        // Custom analytics
        if (window.coraAnalytics && typeof window.coraAnalytics.track === 'function') {
            window.coraAnalytics.track('theme_changed', {
                theme: theme,
                system_preference: this.systemPreference
            });
        }
    }

    /**
     * Get theme information for debugging
     */
    getDebugInfo() {
        return {
            currentTheme: this.theme,
            systemPreference: this.systemPreference,
            hasManualPreference: this.hasManualPreference(),
            isInitialized: this.isInitialized,
            storageKey: this.storageKey
        };
    }

    /**
     * Cleanup method
     */
    destroy() {
        // Remove event listeners
        document.removeEventListener('click', this.handleClick);
        document.removeEventListener('keydown', this.handleKeydown);
        window.removeEventListener('storage', this.handleStorage);
        
        this.isInitialized = false;
    }
}

// Add CSS for smooth transitions
const style = document.createElement('style');
style.textContent = `
    .theme-transitioning,
    .theme-transitioning *,
    .theme-transitioning *::before,
    .theme-transitioning *::after {
        transition: background-color 300ms ease, 
                    color 300ms ease, 
                    border-color 300ms ease, 
                    box-shadow 300ms ease !important;
    }
    
    .theme-toggle {
        position: relative;
        display: inline-flex;
        align-items: center;
        justify-content: center;
        width: 48px;
        height: 48px;
        border-radius: 50%;
        background: var(--wellness-bg-secondary);
        border: 2px solid var(--wellness-border-primary);
        cursor: pointer;
        transition: all 300ms ease;
        color: var(--wellness-text-primary);
    }
    
    .theme-toggle:hover {
        background: var(--wellness-bg-tertiary);
        transform: scale(1.05);
    }
    
    .theme-toggle:focus {
        outline: none;
        border-color: var(--wellness-border-focus);
        box-shadow: 0 0 0 3px rgba(155, 110, 200, 0.2);
    }
    
    .theme-toggle svg {
        width: 20px;
        height: 20px;
        transition: all 300ms ease;
    }
    
    .theme-toggle .sun-icon {
        opacity: 1;
        transform: rotate(0deg);
    }
    
    .theme-toggle .moon-icon {
        opacity: 0;
        transform: rotate(-90deg);
        position: absolute;
    }
    
    [data-theme="dark"] .theme-toggle .sun-icon {
        opacity: 0;
        transform: rotate(90deg);
    }
    
    [data-theme="dark"] .theme-toggle .moon-icon {
        opacity: 1;
        transform: rotate(0deg);
    }
`;
document.head.appendChild(style);

// Initialize dark mode manager
const darkModeManager = new DarkModeManager();

// Export for use in other modules
window.DarkModeManager = DarkModeManager;
window.darkModeManager = darkModeManager;

// Console helpers for debugging
if (typeof console !== 'undefined') {
    // console.log('🌙 CORA Dark Mode Manager initialized');
    // console.log('Available commands:');
    // console.log('- darkModeManager.toggleTheme()');
    // console.log('- darkModeManager.setTheme("dark"|"light")');
    // console.log('- darkModeManager.resetToSystem()');
    // console.log('- darkModeManager.getDebugInfo()');
} 