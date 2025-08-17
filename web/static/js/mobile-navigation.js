/**
 * CORA Mobile Navigation System
 * Provides consistent mobile navigation across all pages
 * Enhanced for accessibility, performance, and user experience
 */

class MobileNavigation {
    constructor() {
        this.isOpen = false;
        this.menuElement = null;
        this.toggleButton = null;
        this.overlay = null;
        this.focusTrap = null;
        this.lastFocusedElement = null;
        
        // Initialize on DOM ready
        if (document.readyState === 'loading') {
            document.addEventListener('DOMContentLoaded', () => this.init());
        } else {
            this.init();
        }
    }

    /**
     * Initialize mobile navigation
     */
    init() {
        // Find navigation container
        const navContainer = document.querySelector('#mobile-nav-container, .mobile-nav-container, nav');
        if (!navContainer) {
            // console.warn('Mobile navigation container not found');
            return;
        }

        // Inject mobile navigation HTML
        this.injectNavigationHTML(navContainer);
        
        // Set up event listeners
        this.setupEventListeners();
        
        // Set up keyboard navigation
        this.setupKeyboardNavigation();
        
        // Set up resize observer
        this.setupResizeObserver();
        
        // console.log('📱 CORA Mobile Navigation initialized');
    }

    /**
     * Inject mobile navigation HTML
     */
    injectNavigationHTML(container) {
        // Check if mobile nav already exists
        if (document.querySelector('.mobile-menu-toggle')) {
            return;
        }

        // Determine if user is authenticated
        const isAuthenticated = this.checkAuthentication();
        
        // Create hamburger button
        const hamburgerHTML = `
            <button class="mobile-menu-toggle" 
                    aria-label="Toggle mobile menu" 
                    aria-expanded="false"
                    aria-controls="mobile-menu">
                <span class="hamburger-line"></span>
                <span class="hamburger-line"></span>
                <span class="hamburger-line"></span>
            </button>
        `;

        // Create mobile menu
        const mobileMenuHTML = `
            <div class="mobile-menu-overlay" aria-hidden="true"></div>
            <div class="mobile-menu" 
                 id="mobile-menu" 
                 role="navigation" 
                 aria-label="Mobile navigation">
                <div class="mobile-menu-header">
                    <h2 class="mobile-menu-title">Menu</h2>
                    <button class="mobile-menu-close" 
                            aria-label="Close mobile menu">
                        <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"/>
                        </svg>
                    </button>
                </div>
                <nav class="mobile-menu-nav">
                    ${this.getNavigationLinks(isAuthenticated)}
                </nav>
                <div class="mobile-menu-footer">
                    ${this.getFooterContent(isAuthenticated)}
                </div>
            </div>
        `;

        // Add hamburger to container
        const navEnd = container.querySelector('.navbar-nav, .nav-end, .ml-auto, .ms-auto');
        if (navEnd) {
            navEnd.insertAdjacentHTML('beforeend', hamburgerHTML);
        } else {
            container.insertAdjacentHTML('beforeend', hamburgerHTML);
        }

        // Add mobile menu to body
        document.body.insertAdjacentHTML('beforeend', mobileMenuHTML);

        // Store references
        this.toggleButton = document.querySelector('.mobile-menu-toggle');
        this.menuElement = document.querySelector('.mobile-menu');
        this.overlay = document.querySelector('.mobile-menu-overlay');
    }

    /**
     * Check if user is authenticated
     */
    checkAuthentication() {
        // Check various indicators of authentication
        return !!(
            document.querySelector('[data-authenticated="true"]') ||
            document.querySelector('.user-menu') ||
            document.querySelector('.logout-link') ||
            window.location.pathname.includes('/dashboard') ||
            window.location.pathname.includes('/expenses')
        );
    }

    /**
     * Get navigation links based on authentication status
     */
    getNavigationLinks(isAuthenticated) {
        if (isAuthenticated) {
            return `
                <a href="/dashboard" class="mobile-menu-link ${this.isCurrentPage('/dashboard') ? 'active' : ''}">
                    <svg class="mobile-menu-icon" width="20" height="20" viewBox="0 0 20 20" fill="currentColor">
                        <path d="M10.707 2.293a1 1 0 00-1.414 0l-7 7a1 1 0 001.414 1.414L4 10.414V17a1 1 0 001 1h2a1 1 0 001-1v-2a1 1 0 011-1h2a1 1 0 011 1v2a1 1 0 001 1h2a1 1 0 001-1v-6.586l.293.293a1 1 0 001.414-1.414l-7-7z"/>
                    </svg>
                    Dashboard
                </a>
                <a href="/expenses" class="mobile-menu-link ${this.isCurrentPage('/expenses') ? 'active' : ''}">
                    <svg class="mobile-menu-icon" width="20" height="20" viewBox="0 0 20 20" fill="currentColor">
                        <path d="M8.433 7.418c.155-.103.346-.196.567-.267v1.698a2.305 2.305 0 01-.567-.267C8.07 8.34 8 8.114 8 8c0-.114.07-.34.433-.582zM11 12.849v-1.698c.22.071.412.164.567.267.364.243.433.468.433.582 0 .114-.07.34-.433.582a2.305 2.305 0 01-.567.267z"/>
                        <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm1-13a1 1 0 10-2 0v.092a4.535 4.535 0 00-1.676.662C6.602 6.234 6 7.009 6 8c0 .99.602 1.765 1.324 2.246.48.32 1.054.545 1.676.662v1.941c-.391-.127-.68-.317-.843-.504a1 1 0 10-1.51 1.31c.562.649 1.413 1.076 2.353 1.253V15a1 1 0 102 0v-.092a4.535 4.535 0 001.676-.662C13.398 13.766 14 12.991 14 12c0-.99-.602-1.765-1.324-2.246A4.535 4.535 0 0011 9.092V7.151c.391.127.68.317.843.504a1 1 0 101.511-1.31c-.563-.649-1.413-1.076-2.354-1.253V5z" clip-rule="evenodd"/>
                    </svg>
                    Expenses
                </a>
                <a href="/settings" class="mobile-menu-link ${this.isCurrentPage('/settings') ? 'active' : ''}">
                    <svg class="mobile-menu-icon" width="20" height="20" viewBox="0 0 20 20" fill="currentColor">
                        <path fill-rule="evenodd" d="M11.49 3.17c-.38-1.56-2.6-1.56-2.98 0a1.532 1.532 0 01-2.286.948c-1.372-.836-2.942.734-2.106 2.106.54.886.061 2.042-.947 2.287-1.561.379-1.561 2.6 0 2.978a1.532 1.532 0 01.947 2.287c-.836 1.372.734 2.942 2.106 2.106a1.532 1.532 0 012.287.947c.379 1.561 2.6 1.561 2.978 0a1.533 1.533 0 012.287-.947c1.372.836 2.942-.734 2.106-2.106a1.533 1.533 0 01.947-2.287c1.561-.379 1.561-2.6 0-2.978a1.532 1.532 0 01-.947-2.287c.836-1.372-.734-2.942-2.106-2.106a1.532 1.532 0 01-2.287-.947zM10 13a3 3 0 100-6 3 3 0 000 6z" clip-rule="evenodd"/>
                    </svg>
                    Settings
                </a>
                <a href="/profile" class="mobile-menu-link ${this.isCurrentPage('/profile') ? 'active' : ''}">
                    <svg class="mobile-menu-icon" width="20" height="20" viewBox="0 0 20 20" fill="currentColor">
                        <path fill-rule="evenodd" d="M10 9a3 3 0 100-6 3 3 0 000 6zm-7 9a7 7 0 1114 0H3z" clip-rule="evenodd"/>
                    </svg>
                    Profile
                </a>
                <a href="/help" class="mobile-menu-link ${this.isCurrentPage('/help') ? 'active' : ''}">
                    <svg class="mobile-menu-icon" width="20" height="20" viewBox="0 0 20 20" fill="currentColor">
                        <path fill-rule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-8-3a1 1 0 00-.867.5 1 1 0 11-1.731-1A3 3 0 0113 8a3.001 3.001 0 01-2 2.83V11a1 1 0 11-2 0v-1a1 1 0 011-1 1 1 0 100-2zm0 8a1 1 0 100-2 1 1 0 000 2z" clip-rule="evenodd"/>
                    </svg>
                    Help
                </a>
                <div class="mobile-menu-divider"></div>
                <a href="/logout" class="mobile-menu-link mobile-menu-link-danger">
                    <svg class="mobile-menu-icon" width="20" height="20" viewBox="0 0 20 20" fill="currentColor">
                        <path fill-rule="evenodd" d="M3 3a1 1 0 00-1 1v12a1 1 0 102 0V4a1 1 0 00-1-1zm10.293 9.293a1 1 0 001.414 1.414l3-3a1 1 0 000-1.414l-3-3a1 1 0 10-1.414 1.414L14.586 9H7a1 1 0 100 2h7.586l-1.293 1.293z" clip-rule="evenodd"/>
                    </svg>
                    Logout
                </a>
            `;
        } else {
            return `
                <a href="/" class="mobile-menu-link ${this.isCurrentPage('/') ? 'active' : ''}">
                    <svg class="mobile-menu-icon" width="20" height="20" viewBox="0 0 20 20" fill="currentColor">
                        <path d="M10.707 2.293a1 1 0 00-1.414 0l-7 7a1 1 0 001.414 1.414L4 10.414V17a1 1 0 001 1h2a1 1 0 001-1v-2a1 1 0 011-1h2a1 1 0 011 1v2a1 1 0 001 1h2a1 1 0 001-1v-6.586l.293.293a1 1 0 001.414-1.414l-7-7z"/>
                    </svg>
                    Home
                </a>
                <a href="/features" class="mobile-menu-link ${this.isCurrentPage('/features') ? 'active' : ''}">
                    <svg class="mobile-menu-icon" width="20" height="20" viewBox="0 0 20 20" fill="currentColor">
                        <path d="M9 4.804A7.968 7.968 0 005.5 4c-1.255 0-2.443.29-3.5.804v10A7.969 7.969 0 015.5 14c1.669 0 3.218.51 4.5 1.385A7.962 7.962 0 0114.5 14c1.255 0 2.443.29 3.5.804v-10A7.968 7.968 0 0014.5 4c-1.255 0-2.443.29-3.5.804V12a1 1 0 11-2 0V4.804z"/>
                    </svg>
                    Features
                </a>
                <a href="/pricing" class="mobile-menu-link ${this.isCurrentPage('/pricing') ? 'active' : ''}">
                    <svg class="mobile-menu-icon" width="20" height="20" viewBox="0 0 20 20" fill="currentColor">
                        <path d="M8.433 7.418c.155-.103.346-.196.567-.267v1.698a2.305 2.305 0 01-.567-.267C8.07 8.34 8 8.114 8 8c0-.114.07-.34.433-.582zM11 12.849v-1.698c.22.071.412.164.567.267.364.243.433.468.433.582 0 .114-.07.34-.433.582a2.305 2.305 0 01-.567.267z"/>
                        <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm1-13a1 1 0 10-2 0v.092a4.535 4.535 0 00-1.676.662C6.602 6.234 6 7.009 6 8c0 .99.602 1.765 1.324 2.246.48.32 1.054.545 1.676.662v1.941c-.391-.127-.68-.317-.843-.504a1 1 0 10-1.51 1.31c.562.649 1.413 1.076 2.353 1.253V15a1 1 0 102 0v-.092a4.535 4.535 0 001.676-.662C13.398 13.766 14 12.991 14 12c0-.99-.602-1.765-1.324-2.246A4.535 4.535 0 0011 9.092V7.151c.391.127.68.317.843.504a1 1 0 101.511-1.31c-.563-.649-1.413-1.076-2.354-1.253V5z" clip-rule="evenodd"/>
                    </svg>
                    Pricing
                </a>
                <a href="/demo" class="mobile-menu-link ${this.isCurrentPage('/demo') ? 'active' : ''}">
                    <svg class="mobile-menu-icon" width="20" height="20" viewBox="0 0 20 20" fill="currentColor">
                        <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM9.555 7.168A1 1 0 008 8v4a1 1 0 001.555.832l3-2a1 1 0 000-1.664l-3-2z" clip-rule="evenodd"/>
                    </svg>
                    Demo
                </a>
                <a href="/contact" class="mobile-menu-link ${this.isCurrentPage('/contact') ? 'active' : ''}">
                    <svg class="mobile-menu-icon" width="20" height="20" viewBox="0 0 20 20" fill="currentColor">
                        <path d="M2.003 5.884L10 9.882l7.997-3.998A2 2 0 0016 4H4a2 2 0 00-1.997 1.884z"/>
                        <path d="M18 8.118l-8 4-8-4V14a2 2 0 002 2h12a2 2 0 002-2V8.118z"/>
                    </svg>
                    Contact
                </a>
                <div class="mobile-menu-divider"></div>
                <a href="/login" class="mobile-menu-link mobile-menu-link-primary">
                    <svg class="mobile-menu-icon" width="20" height="20" viewBox="0 0 20 20" fill="currentColor">
                        <path fill-rule="evenodd" d="M3 3a1 1 0 011 1v12a1 1 0 11-2 0V4a1 1 0 011-1zm7.707 3.293a1 1 0 010 1.414L9.414 9H17a1 1 0 110 2H9.414l1.293 1.293a1 1 0 01-1.414 1.414l-3-3a1 1 0 010-1.414l3-3a1 1 0 011.414 0z" clip-rule="evenodd"/>
                    </svg>
                    Login
                </a>
                <a href="/register" class="mobile-menu-link mobile-menu-link-success">
                    <svg class="mobile-menu-icon" width="20" height="20" viewBox="0 0 20 20" fill="currentColor">
                        <path d="M8 9a3 3 0 100-6 3 3 0 000 6zM8 11a6 6 0 016 6H2a6 6 0 016-6zM16 7a1 1 0 10-2 0v1h-1a1 1 0 100 2h1v1a1 1 0 102 0v-1h1a1 1 0 100-2h-1V7z"/>
                    </svg>
                    Get Started
                </a>
            `;
        }
    }

    /**
     * Get footer content based on authentication status
     */
    getFooterContent(isAuthenticated) {
        if (isAuthenticated) {
            const userEmail = document.querySelector('.user-email')?.textContent || 'user@example.com';
            return `
                <div class="mobile-menu-user">
                    <div class="mobile-menu-avatar">
                        ${userEmail.charAt(0).toUpperCase()}
                    </div>
                    <div class="mobile-menu-user-info">
                        <div class="mobile-menu-user-name">Welcome back!</div>
                        <div class="mobile-menu-user-email">${userEmail}</div>
                    </div>
                </div>
            `;
        } else {
            return `
                <div class="mobile-menu-cta">
                    <p class="mobile-menu-cta-text">Start your financial wellness journey today</p>
                    <a href="/register" class="mobile-menu-cta-button">Get Started Free</a>
                </div>
            `;
        }
    }

    /**
     * Check if current page matches path
     */
    isCurrentPage(path) {
        return window.location.pathname === path || 
               window.location.pathname.startsWith(path + '/');
    }

    /**
     * Set up event listeners
     */
    setupEventListeners() {
        // Toggle button click
        this.toggleButton?.addEventListener('click', () => this.toggleMenu());

        // Close button click
        const closeButton = document.querySelector('.mobile-menu-close');
        closeButton?.addEventListener('click', () => this.closeMenu());

        // Overlay click
        this.overlay?.addEventListener('click', () => this.closeMenu());

        // Window resize
        window.addEventListener('resize', () => this.handleResize());

        // Escape key
        document.addEventListener('keydown', (e) => {
            if (e.key === 'Escape' && this.isOpen) {
                this.closeMenu();
            }
        });

        // Prevent body scroll when menu is open
        document.addEventListener('touchmove', (e) => {
            if (this.isOpen && !this.menuElement.contains(e.target)) {
                e.preventDefault();
            }
        }, { passive: false });
    }

    /**
     * Set up keyboard navigation
     */
    setupKeyboardNavigation() {
        // Get all focusable elements
        this.focusableElements = this.menuElement?.querySelectorAll(
            'a, button, input, select, textarea, [tabindex]:not([tabindex="-1"])'
        );

        if (!this.focusableElements || this.focusableElements.length === 0) return;

        // Set up focus trap
        this.menuElement?.addEventListener('keydown', (e) => {
            if (e.key === 'Tab') {
                this.handleTabKey(e);
            }
        });
    }

    /**
     * Handle tab key for focus trap
     */
    handleTabKey(e) {
        const firstFocusable = this.focusableElements[0];
        const lastFocusable = this.focusableElements[this.focusableElements.length - 1];

        if (e.shiftKey) {
            // Shift + Tab
            if (document.activeElement === firstFocusable) {
                e.preventDefault();
                lastFocusable.focus();
            }
        } else {
            // Tab
            if (document.activeElement === lastFocusable) {
                e.preventDefault();
                firstFocusable.focus();
            }
        }
    }

    /**
     * Toggle menu open/close
     */
    toggleMenu() {
        if (this.isOpen) {
            this.closeMenu();
        } else {
            this.openMenu();
        }
    }

    /**
     * Open menu
     */
    openMenu() {
        if (!this.menuElement || !this.overlay) return;

        // Store last focused element
        this.lastFocusedElement = document.activeElement;

        // Open menu
        this.isOpen = true;
        this.menuElement.classList.add('open');
        this.overlay.classList.add('show');
        this.toggleButton?.classList.add('open');

        // Update ARIA attributes
        this.toggleButton?.setAttribute('aria-expanded', 'true');
        this.menuElement.setAttribute('aria-hidden', 'false');
        this.overlay.setAttribute('aria-hidden', 'false');

        // Prevent body scroll
        document.body.style.overflow = 'hidden';

        // Focus first focusable element
        setTimeout(() => {
            const firstLink = this.menuElement.querySelector('a, button');
            firstLink?.focus();
        }, 100);

        // Announce to screen readers
        this.announce('Mobile menu opened');
    }

    /**
     * Close menu
     */
    closeMenu() {
        if (!this.menuElement || !this.overlay) return;

        // Close menu
        this.isOpen = false;
        this.menuElement.classList.remove('open');
        this.overlay.classList.remove('show');
        this.toggleButton?.classList.remove('open');

        // Update ARIA attributes
        this.toggleButton?.setAttribute('aria-expanded', 'false');
        this.menuElement.setAttribute('aria-hidden', 'true');
        this.overlay.setAttribute('aria-hidden', 'true');

        // Restore body scroll
        document.body.style.overflow = '';

        // Restore focus
        this.lastFocusedElement?.focus();

        // Announce to screen readers
        this.announce('Mobile menu closed');
    }

    /**
     * Handle window resize
     */
    handleResize() {
        // Close menu if window is resized to desktop breakpoint
        if (window.innerWidth > 768 && this.isOpen) {
            this.closeMenu();
        }
    }

    /**
     * Set up resize observer for performance
     */
    setupResizeObserver() {
        if (!window.ResizeObserver) return;

        const observer = new ResizeObserver((entries) => {
            for (const entry of entries) {
                if (entry.contentRect.width > 768 && this.isOpen) {
                    this.closeMenu();
                }
            }
        });

        observer.observe(document.body);
    }

    /**
     * Announce to screen readers
     */
    announce(message) {
        const announcement = document.createElement('div');
        announcement.className = 'sr-only';
        announcement.setAttribute('aria-live', 'polite');
        announcement.setAttribute('aria-atomic', 'true');
        announcement.textContent = message;
        
        document.body.appendChild(announcement);
        
        setTimeout(() => {
            document.body.removeChild(announcement);
        }, 1000);
    }

    /**
     * Destroy mobile navigation
     */
    destroy() {
        // Remove event listeners
        this.toggleButton?.removeEventListener('click', this.toggleMenu);
        
        // Remove elements
        this.menuElement?.remove();
        this.overlay?.remove();
        this.toggleButton?.remove();
        
        // Restore body scroll
        document.body.style.overflow = '';
        
        this.isOpen = false;
    }
}

// Initialize mobile navigation
const mobileNav = new MobileNavigation();

// Export for use in other modules
window.MobileNavigation = MobileNavigation;
window.mobileNav = mobileNav;

// Console helpers for debugging
if (typeof console !== 'undefined') {
    // console.log('📱 CORA Mobile Navigation loaded');
    // console.log('Available commands:');
    // console.log('- mobileNav.openMenu()');
    // console.log('- mobileNav.closeMenu()');
    // console.log('- mobileNav.destroy()');
}