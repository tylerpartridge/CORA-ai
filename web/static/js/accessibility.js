/**
 * CORA Accessibility Enhancement Suite
 * 
 * This module provides comprehensive accessibility features for the CORA wellness experience:
 * - Screen reader optimization
 * - Keyboard navigation enhancements
 * - High contrast mode support
 * - Focus management
 * - Voice control integration
 * - Cognitive accessibility features
 * - Motion reduction support
 */

class CORAAccessibility {
    constructor() {
        this.currentFocus = null;
        this.focusHistory = [];
        this.voiceControlActive = false;
        this.highContrastMode = false;
        this.reducedMotionMode = false;
        this.darkMode = false;
        this.fontSize = 16; // Base font size in pixels
        
        // Load saved preferences
        this.loadPreferences();
        
        this.init();
    }
    
    init() {
        // Remove any existing voice control button
        const existingVoiceButton = document.getElementById('voice-control-toggle');
        if (existingVoiceButton) {
            existingVoiceButton.remove();
        }
        
        // Setup core accessibility features
        this.setupKeyboardNavigation();
        this.setupScreenReaderSupport();
        this.setupFocusManagement();
        // Voice control temporarily disabled - integrated into CORA chat
        // this.setupVoiceControl();
        this.setupHighContrastMode();
        this.setupReducedMotion();
        this.setupFontSizeControls();
        this.setupCognitiveAccessibility();
        this.setupDarkMode();
        
        // Monitor for accessibility preferences
        this.monitorAccessibilityPreferences();
        
        // Setup accessibility testing
        this.setupAccessibilityTesting();
    }
    
    /**
     * Monitor accessibility preferences and apply them
     */
    monitorAccessibilityPreferences() {
        // Monitor for system preference changes
        if (window.matchMedia) {
            // Reduced motion preference
            const motionQuery = window.matchMedia('(prefers-reduced-motion: reduce)');
            motionQuery.addEventListener('change', (e) => {
                if (e.matches) {
                    this.applyReducedMotion();
                } else {
                    this.removeReducedMotion();
                }
            });
            
            // High contrast preference
            const contrastQuery = window.matchMedia('(prefers-contrast: high)');
            contrastQuery.addEventListener('change', (e) => {
                if (e.matches) {
                    this.applyHighContrastStyles();
                }
            });
            
            // Color scheme preference
            const colorSchemeQuery = window.matchMedia('(prefers-color-scheme: dark)');
            colorSchemeQuery.addEventListener('change', (e) => {
                if (window.darkModeManager) {
                    window.darkModeManager.setTheme(e.matches ? 'dark' : 'light');
                }
            });
        }
        
        // Load saved preferences
        this.loadPreferences();
        
        // Monitor for new elements being added
        this.monitorAccessibilityIssues();
    }
    
    /**
     * Keyboard Navigation
     */
    setupKeyboardNavigation() {
        // Enhanced keyboard navigation
        document.addEventListener('keydown', (e) => {
            this.handleKeyboardNavigation(e);
        });
        
        // Skip to main content link - DISABLED
        // this.createSkipLink();
        
        // Enhanced tab navigation
        this.enhanceTabNavigation();
    }
    
    handleKeyboardNavigation(e) {
        const target = e.target;
        
        // Skip to main content
        if (e.key === 'Tab' && e.shiftKey === false && target.classList.contains('skip-link')) {
            e.preventDefault();
            this.focusMainContent();
        }
        
        // Enhanced arrow key navigation for cards
        if (target.classList.contains('wellness-card') || target.closest('.wellness-card')) {
            this.handleCardNavigation(e, target);
        }
        
        // Voice control shortcuts
        if (e.altKey && e.key === 'v') {
            e.preventDefault();
            this.toggleVoiceControl();
        }
        
        // High contrast toggle
        if (e.altKey && e.key === 'h') {
            e.preventDefault();
            this.toggleHighContrast();
        }
        
        // Font size controls
        if (e.altKey && e.key === '=') {
            e.preventDefault();
            this.increaseFontSize();
        }
        
        if (e.altKey && e.key === '-') {
            e.preventDefault();
            this.decreaseFontSize();
        }
        
        // Reset font size
        if (e.altKey && e.key === '0') {
            e.preventDefault();
            this.resetFontSize();
        }
    }
    
    createSkipLink() {
        const skipLink = document.createElement('a');
        skipLink.href = '#main-content';
        skipLink.className = 'skip-link';
        skipLink.textContent = 'Skip to main content';
        skipLink.style.cssText = `
            position: absolute;
            top: -40px;
            left: 6px;
            background: #FF9800;
            color: white;
            padding: 8px;
            text-decoration: none;
            border-radius: 4px;
            z-index: 10000;
            transition: top 0.3s;
        `;
        
        skipLink.addEventListener('focus', () => {
            skipLink.style.top = '6px';
        });
        
        skipLink.addEventListener('blur', () => {
            skipLink.style.top = '-40px';
        });
        
        document.body.insertBefore(skipLink, document.body.firstChild);
    }
    
    focusMainContent() {
        const mainContent = document.querySelector('main') || document.querySelector('#main-content');
        if (mainContent) {
            mainContent.setAttribute('tabindex', '-1');
            mainContent.focus();
            this.announceToScreenReader('Main content area');
        }
    }
    
    enhanceTabNavigation() {
        // Ensure all interactive elements are keyboard accessible
        document.querySelectorAll('button, a, input, select, textarea, [tabindex]').forEach(element => {
            if (!element.hasAttribute('tabindex')) {
                element.setAttribute('tabindex', '0');
            }
            
            // Add focus indicators
            element.addEventListener('focus', () => {
                this.addFocusIndicator(element);
            });
            
            element.addEventListener('blur', () => {
                this.removeFocusIndicator(element);
            });
        });
    }
    
    handleCardNavigation(e, target) {
        const card = target.closest('.wellness-card') || target;
        const cards = Array.from(document.querySelectorAll('.wellness-card'));
        const currentIndex = cards.indexOf(card);
        
        switch (e.key) {
            case 'ArrowRight':
                e.preventDefault();
                this.focusNextCard(cards, currentIndex);
                break;
            case 'ArrowLeft':
                e.preventDefault();
                this.focusPreviousCard(cards, currentIndex);
                break;
            case 'Enter':
            case ' ':
                e.preventDefault();
                this.activateCard(card);
                break;
        }
    }
    
    focusNextCard(cards, currentIndex) {
        const nextIndex = (currentIndex + 1) % cards.length;
        cards[nextIndex].focus();
        this.announceToScreenReader(`Card ${nextIndex + 1} of ${cards.length}`);
    }
    
    focusPreviousCard(cards, currentIndex) {
        const prevIndex = currentIndex === 0 ? cards.length - 1 : currentIndex - 1;
        cards[prevIndex].focus();
        this.announceToScreenReader(`Card ${prevIndex + 1} of ${cards.length}`);
    }
    
    activateCard(card) {
        const button = card.querySelector('button') || card;
        if (button && button.click) {
            button.click();
        }
    }
    
    /**
     * Screen Reader Support
     */
    setupScreenReaderSupport() {
        // Create live region for announcements
        this.createLiveRegion();
        
        // Enhance ARIA labels
        this.enhanceARIALabels();
        
        // Add descriptive text for complex interactions
        this.addDescriptiveText();
        
        // Setup heading structure
        this.setupHeadingStructure();
    }
    
    createLiveRegion() {
        const liveRegion = document.createElement('div');
        liveRegion.id = 'screen-reader-announcements';
        liveRegion.setAttribute('aria-live', 'polite');
        liveRegion.setAttribute('aria-atomic', 'true');
        liveRegion.className = 'sr-only';
        liveRegion.style.cssText = `
            position: absolute;
            left: -10000px;
            width: 1px;
            height: 1px;
            overflow: hidden;
        `;
        document.body.appendChild(liveRegion);
    }
    
    announceToScreenReader(message) {
        const liveRegion = document.getElementById('screen-reader-announcements');
        if (liveRegion) {
            liveRegion.textContent = message;
            setTimeout(() => {
                liveRegion.textContent = '';
            }, 1000);
        }
    }
    
    enhanceARIALabels() {
        // Add missing ARIA labels
        document.querySelectorAll('button:not([aria-label]):not([aria-labelledby])').forEach(button => {
            if (!button.textContent.trim()) {
                const icon = button.querySelector('i');
                if (icon) {
                    const iconClass = icon.className;
                    let label = '';
                    
                    if (iconClass.includes('fa-plus')) label = 'Add new item';
                    else if (iconClass.includes('fa-edit')) label = 'Edit';
                    else if (iconClass.includes('fa-delete')) label = 'Delete';
                    else if (iconClass.includes('fa-save')) label = 'Save';
                    else if (iconClass.includes('fa-cancel')) label = 'Cancel';
                    else if (iconClass.includes('fa-search')) label = 'Search';
                    else if (iconClass.includes('fa-filter')) label = 'Filter';
                    else if (iconClass.includes('fa-sort')) label = 'Sort';
                    else label = 'Button';
                    
                    button.setAttribute('aria-label', label);
                }
            }
        });
        
        // Enhance form labels
        document.querySelectorAll('input, select, textarea').forEach(input => {
            if (!input.hasAttribute('aria-label') && !input.hasAttribute('aria-labelledby')) {
                const label = input.closest('label') || document.querySelector(`label[for="${input.id}"]`);
                if (label) {
                    input.setAttribute('aria-labelledby', label.id || this.generateId(label));
                }
            }
        });
    }
    
    addDescriptiveText() {
        // Add descriptive text for complex interactions
        document.querySelectorAll('.wellness-card').forEach((card, index) => {
            const title = card.querySelector('h3, h4')?.textContent || 'Card';
            const description = card.querySelector('p')?.textContent || '';
            
            card.setAttribute('aria-label', `${title}. ${description}. Press Enter to activate.`);
            card.setAttribute('role', 'button');
            card.setAttribute('tabindex', '0');
        });
        
        // Add descriptive text for progress indicators
        document.querySelectorAll('.progress-bar, .progress-ring').forEach(progress => {
            const value = progress.getAttribute('aria-valuenow') || '0';
            const max = progress.getAttribute('aria-valuemax') || '100';
            const label = progress.getAttribute('aria-label') || 'Progress';
            
            progress.setAttribute('aria-label', `${label}: ${value}% complete`);
        });
    }
    
    setupHeadingStructure() {
        // Ensure proper heading hierarchy
        const headings = document.querySelectorAll('h1, h2, h3, h4, h5, h6');
        let currentLevel = 0;
        
        headings.forEach(heading => {
            const level = parseInt(heading.tagName.charAt(1));
            
            if (level > currentLevel + 1) {
                // console.warn('Skipped heading level:', heading);
            }
            
            currentLevel = level;
        });
    }
    
    /**
     * Focus Management
     */
    setupFocusManagement() {
        // Track focus history
        document.addEventListener('focusin', (e) => {
            this.focusHistory.push(e.target);
            if (this.focusHistory.length > 10) {
                this.focusHistory.shift();
            }
        });
        
        // Trap focus in modals
        this.setupFocusTrapping();
        
        // Restore focus after modal close
        this.setupFocusRestoration();
    }
    
    setupFocusTrapping() {
        document.querySelectorAll('[role="dialog"], .modal').forEach(modal => {
            const focusableElements = modal.querySelectorAll(
                'button, [href], input, select, textarea, [tabindex]:not([tabindex="-1"])'
            );
            
            const firstElement = focusableElements[0];
            const lastElement = focusableElements[focusableElements.length - 1];
            
            modal.addEventListener('keydown', (e) => {
                if (e.key === 'Tab') {
                    if (e.shiftKey) {
                        if (document.activeElement === firstElement) {
                            e.preventDefault();
                            lastElement.focus();
                        }
                    } else {
                        if (document.activeElement === lastElement) {
                            e.preventDefault();
                            firstElement.focus();
                        }
                    }
                }
            });
        });
    }
    
    setupFocusRestoration() {
        // Store focus before opening modal
        document.querySelectorAll('[data-modal-trigger]').forEach(trigger => {
            trigger.addEventListener('click', () => {
                this.currentFocus = document.activeElement;
            });
        });
        
        // Restore focus after modal close
        document.querySelectorAll('[data-modal-close]').forEach(closeBtn => {
            closeBtn.addEventListener('click', () => {
                if (this.currentFocus) {
                    setTimeout(() => {
                        this.currentFocus.focus();
                    }, 100);
                }
            });
        });
    }
    
    addFocusIndicator(element) {
        element.style.outline = '2px solid #FF9800';
        element.style.outlineOffset = '2px';
    }
    
    removeFocusIndicator(element) {
        element.style.outline = '';
        element.style.outlineOffset = '';
    }
    
    /**
     * Voice Control Integration
     */
    setupVoiceControl() {
        // Voice control toggle
        this.createVoiceControlToggle();
        
        // Voice commands
        this.setupVoiceCommands();
    }
    
    createVoiceControlToggle() {
        const toggle = document.createElement('button');
        toggle.id = 'voice-control-toggle';
        toggle.className = 'accessibility-toggle';
        toggle.setAttribute('aria-label', 'Toggle voice control');
        toggle.innerHTML = '<i class="fas fa-microphone"></i>';
        toggle.style.cssText = `
            position: fixed;
            bottom: 20px;
            right: 20px;
            width: 50px;
            height: 50px;
            border-radius: 50%;
            background: #FF9800;
            color: white;
            border: none;
            cursor: pointer;
            z-index: 1000;
            display: flex;
            align-items: center;
            justify-content: center;
        `;
        
        toggle.addEventListener('click', () => {
            this.toggleVoiceControl();
        });
        
        document.body.appendChild(toggle);
    }
    
    toggleVoiceControl() {
        this.voiceControlActive = !this.voiceControlActive;
        const toggle = document.getElementById('voice-control-toggle');
        
        if (this.voiceControlActive) {
            toggle.innerHTML = '<i class="fas fa-microphone-slash"></i>';
            toggle.style.background = '#E74C3C';
            this.startVoiceRecognition();
            this.announceToScreenReader('Voice control activated');
        } else {
            toggle.innerHTML = '<i class="fas fa-microphone"></i>';
            toggle.style.background = '#FF9800';
            this.stopVoiceRecognition();
            this.announceToScreenReader('Voice control deactivated');
        }
    }
    
    setupVoiceCommands() {
        if ('webkitSpeechRecognition' in window || 'SpeechRecognition' in window) {
            const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
            this.recognition = new SpeechRecognition();
            
            this.recognition.continuous = true;
            this.recognition.interimResults = false;
            this.recognition.lang = navigator.language || 'en-US';
            
            this.recognition.onresult = (event) => {
                const command = event.results[event.results.length - 1][0].transcript.toLowerCase();
                this.processVoiceCommand(command);
            };
            
            this.recognition.onerror = (event) => {
                // console.error('Voice recognition error:', event.error);
                if (event.error === 'no-speech') {
                    this.announceToScreenReader('No speech detected. Please try again.');
                } else {
                    this.announceToScreenReader('Voice recognition error. Please check your microphone.');
                }
            };
            
            this.recognition.onend = () => {
                if (this.voiceControlActive) {
                    // Restart if still active
                    setTimeout(() => {
                        if (this.voiceControlActive) {
                            this.startVoiceRecognition();
                        }
                    }, 1000);
                }
            };
        }
    }
    
    startVoiceRecognition() {
        if (this.recognition) {
            this.recognition.start();
        }
    }
    
    stopVoiceRecognition() {
        if (this.recognition) {
            this.recognition.stop();
        }
    }
    
    processVoiceCommand(command) {
        // Announce the command for confirmation
        this.announceToScreenReader(`Processing command: ${command}`);
        
        if (command.includes('go to dashboard') || command.includes('dashboard')) {
            window.location.href = '/dashboard';
        } else if (command.includes('go to expenses') || command.includes('expenses')) {
            window.location.href = '/expenses';
        } else if (command.includes('add expense') || command.includes('new expense')) {
            document.querySelector('#quickAddBtn')?.click();
        } else if (command.includes('search')) {
            document.querySelector('input[type="search"]')?.focus();
        } else if (command.includes('help')) {
            this.showHelp();
        } else if (command.includes('close') || command.includes('cancel')) {
            document.querySelector('.modal .close')?.click();
        } else if (command.includes('next')) {
            this.navigateNext();
        } else if (command.includes('previous') || command.includes('back')) {
            this.navigatePrevious();
        } else if (command.includes('save')) {
            document.querySelector('button[type="submit"]')?.click();
        } else if (command.includes('logout') || command.includes('sign out')) {
            window.location.href = '/logout';
        } else if (command.includes('settings')) {
            window.location.href = '/settings';
        } else {
            this.announceToScreenReader('Command not recognized. Say "help" for available commands.');
        }
    }
    
    navigateNext() {
        // Navigate to next focusable element
        const focusable = document.querySelectorAll('button, [href], input, select, textarea, [tabindex]:not([tabindex="-1"])');
        const current = document.activeElement;
        const currentIndex = Array.from(focusable).indexOf(current);
        if (currentIndex < focusable.length - 1) {
            focusable[currentIndex + 1].focus();
        }
    }
    
    navigatePrevious() {
        // Navigate to previous focusable element
        const focusable = document.querySelectorAll('button, [href], input, select, textarea, [tabindex]:not([tabindex="-1"])');
        const current = document.activeElement;
        const currentIndex = Array.from(focusable).indexOf(current);
        if (currentIndex > 0) {
            focusable[currentIndex - 1].focus();
        }
    }
    
    /**
     * High Contrast Mode
     */
    setupHighContrastMode() {
        // Hide toggle on all pages; keep styles for compatibility
        this.applyHighContrastStyles();
    }
    
    createHighContrastToggle() {
        const toggle = document.createElement('button');
        toggle.id = 'high-contrast-toggle';
        toggle.className = 'accessibility-toggle';
        toggle.setAttribute('aria-label', 'Toggle high contrast mode');
        toggle.innerHTML = '<i class="fas fa-adjust"></i>';
        toggle.style.cssText = `
            position: fixed;
            bottom: 20px;
            right: 80px;
            width: 50px;
            height: 50px;
            border-radius: 50%;
            background: #333;
            color: white;
            border: 2px solid white;
            cursor: pointer;
            z-index: 1000;
            display: flex;
            align-items: center;
            justify-content: center;
        `;
        
        toggle.addEventListener('click', () => {
            this.toggleHighContrast();
        });
        
        document.body.appendChild(toggle);
    }
    
    toggleHighContrast() {
        this.highContrastMode = !this.highContrastMode;
        document.body.classList.toggle('high-contrast', this.highContrastMode);
        
        const toggle = document.getElementById('high-contrast-toggle');
        if (this.highContrastMode) {
            toggle.style.background = '#fff';
            toggle.style.color = '#000';
            this.announceToScreenReader('High contrast mode activated');
        } else {
            toggle.style.background = '#333';
            toggle.style.color = '#fff';
            this.announceToScreenReader('High contrast mode deactivated');
        }
        
        this.savePreferences();
    }
    
    applyHighContrastStyles() {
        const style = document.createElement('style');
        style.textContent = `
            .high-contrast {
                background: #000 !important;
                color: #fff !important;
            }
            
            .high-contrast * {
                background: #000 !important;
                color: #fff !important;
                border-color: #fff !important;
            }
            
            .high-contrast .wellness-card {
                background: #000 !important;
                border: 2px solid #fff !important;
                color: #fff !important;
            }
            
            .high-contrast .wellness-btn {
                background: #fff !important;
                color: #000 !important;
                border: 2px solid #fff !important;
            }
            
            .high-contrast input, .high-contrast select, .high-contrast textarea {
                background: #000 !important;
                color: #fff !important;
                border: 2px solid #fff !important;
            }
        `;
        document.head.appendChild(style);
    }
    
    /**
     * Reduced Motion Support
     */
    setupReducedMotion() {
        // Check for reduced motion preference
        if (window.matchMedia('(prefers-reduced-motion: reduce)').matches) {
            this.reducedMotionMode = true;
            this.applyReducedMotion();
        }
        
        // Listen for preference changes
        window.matchMedia('(prefers-reduced-motion: reduce)').addEventListener('change', (e) => {
            this.reducedMotionMode = e.matches;
            if (this.reducedMotionMode) {
                this.applyReducedMotion();
            } else {
                this.removeReducedMotion();
            }
        });
    }
    
    applyReducedMotion() {
        const style = document.createElement('style');
        style.id = 'reduced-motion-styles';
        style.textContent = `
            *, *::before, *::after {
                animation-duration: 0.01ms !important;
                animation-iteration-count: 1 !important;
                transition-duration: 0.01ms !important;
                scroll-behavior: auto !important;
            }
        `;
        document.head.appendChild(style);
    }
    
    removeReducedMotion() {
        const style = document.getElementById('reduced-motion-styles');
        if (style) {
            style.remove();
        }
    }
    
    /**
     * Font Size Controls
     */
    setupFontSizeControls() {
        this.createFontSizeControls();
        this.applyFontSize();
    }
    
    createFontSizeControls() {
        const controls = document.createElement('div');
        controls.id = 'font-size-controls';
        controls.className = 'accessibility-controls';
        controls.style.cssText = `
            position: fixed;
            bottom: 80px;
            left: 20px;
            display: flex;
            gap: 10px;
            z-index: 1000;
            background: rgba(0, 0, 0, 0.85);
            padding: 8px;
            border-radius: 25px;
            box-shadow: 0 2px 10px rgba(0, 0, 0, 0.4);
        `;
        
        const decreaseBtn = document.createElement('button');
        decreaseBtn.innerHTML = 'A-';
        decreaseBtn.setAttribute('aria-label', 'Decrease font size');
        decreaseBtn.addEventListener('click', () => this.decreaseFontSize());
        
        const increaseBtn = document.createElement('button');
        increaseBtn.innerHTML = 'A+';
        increaseBtn.setAttribute('aria-label', 'Increase font size');
        increaseBtn.addEventListener('click', () => this.increaseFontSize());
        
        const resetBtn = document.createElement('button');
        resetBtn.innerHTML = 'A';
        resetBtn.setAttribute('aria-label', 'Reset font size');
        resetBtn.addEventListener('click', () => this.resetFontSize());
        
        // Apply landing-page typography and styling globally
        decreaseBtn.style.cssText = `
            width: 40px;
            height: 40px;
            border-radius: 50%;
            background: #FF9800;
            color: #1a1a1a !important;
            border: none;
            cursor: pointer;
            font-weight: bold;
            transition: all 0.3s ease;
            font-family: 'Inter', system-ui, -apple-system, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif !important;
            font-weight: 700 !important;
            font-size: 16px !important;
            letter-spacing: 0.5px !important;
            display: inline-flex;
            align-items: center;
            justify-content: center;
            text-rendering: optimizeLegibility;
            -webkit-font-smoothing: antialiased;
            -moz-osx-font-smoothing: grayscale;
        `;
        
        increaseBtn.style.cssText = `
            width: 40px;
            height: 40px;
            border-radius: 50%;
            background: #FF9800;
            color: #1a1a1a !important;
            border: none;
            cursor: pointer;
            font-weight: bold;
            transition: all 0.3s ease;
            font-family: 'Inter', system-ui, -apple-system, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif !important;
            font-weight: 700 !important;
            font-size: 16px !important;
            letter-spacing: 0.5px !important;
            display: inline-flex;
            align-items: center;
            justify-content: center;
            text-rendering: optimizeLegibility;
            -webkit-font-smoothing: antialiased;
            -moz-osx-font-smoothing: grayscale;
        `;
        
        resetBtn.style.cssText = `
            width: 40px;
            height: 40px;
            border-radius: 50%;
            background: #FF9800;
            color: #1a1a1a !important;
            border: none;
            cursor: pointer;
            font-weight: bold;
            transition: all 0.3s ease;
            font-family: 'Inter', system-ui, -apple-system, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif !important;
            font-weight: 700 !important;
            font-size: 16px !important;
            letter-spacing: 0.5px !important;
            display: inline-flex;
            align-items: center;
            justify-content: center;
            text-rendering: optimizeLegibility;
            -webkit-font-smoothing: antialiased;
            -moz-osx-font-smoothing: grayscale;
        `;
        
        controls.appendChild(decreaseBtn);
        controls.appendChild(resetBtn);
        controls.appendChild(increaseBtn);
        
        document.body.appendChild(controls);

        // Final normalization to override any late page styles
        const unifyStyles = document.createElement('style');
        unifyStyles.textContent = `
            #font-size-controls {
                background: rgba(0, 0, 0, 0.85) !important;
                box-shadow: 0 2px 10px rgba(0, 0, 0, 0.4) !important;
                border-radius: 25px !important;
                padding: 8px !important;
            }
            #font-size-controls button {
                background: #FF9800 !important;
                color: #1a1a1a !important;
                border: none !important;
                width: 40px !important;
                height: 40px !important;
                border-radius: 50% !important;
                font-family: 'Inter', system-ui, -apple-system, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif !important;
                font-weight: 700 !important;
                font-size: 16px !important;
                letter-spacing: 0.5px !important;
                display: inline-flex !important;
                align-items: center !important;
                justify-content: center !important;
                text-rendering: optimizeLegibility !important;
                -webkit-font-smoothing: antialiased !important;
                -moz-osx-font-smoothing: grayscale !important;
            }
        `;
        document.head.appendChild(unifyStyles);
    }
    
    increaseFontSize() {
        this.fontSize = Math.min(this.fontSize + 2, 24);
        this.applyFontSize();
        this.announceToScreenReader(`Font size increased to ${this.fontSize} pixels`);
        this.savePreferences();
    }
    
    decreaseFontSize() {
        this.fontSize = Math.max(this.fontSize - 2, 12);
        this.applyFontSize();
        this.announceToScreenReader(`Font size decreased to ${this.fontSize} pixels`);
        this.savePreferences();
    }
    
    resetFontSize() {
        this.fontSize = 16;
        this.applyFontSize();
        this.announceToScreenReader('Font size reset to default');
        this.savePreferences();
    }
    
    applyFontSize() {
        document.documentElement.style.fontSize = `${this.fontSize}px`;
    }
    
    /**
     * Cognitive Accessibility
     */
    setupCognitiveAccessibility() {
        // Add reading time estimates
        this.addReadingTimeEstimates();
        
        // Simplify complex language
        this.simplifyLanguage();
        
        // Add progress indicators
        this.addProgressIndicators();
        
        // Setup error prevention
        this.setupErrorPrevention();
    }
    
    addReadingTimeEstimates() {
        document.querySelectorAll('article, .content-section').forEach(section => {
            const text = section.textContent;
            const wordCount = text.split(' ').length;
            const readingTime = Math.ceil(wordCount / 200); // Average reading speed
            
            const estimate = document.createElement('div');
            estimate.className = 'reading-time';
            estimate.textContent = `Estimated reading time: ${readingTime} minute${readingTime !== 1 ? 's' : ''}`;
            estimate.style.cssText = `
                font-size: 0.875rem;
                color: #666;
                margin-bottom: 1rem;
            `;
            
            section.insertBefore(estimate, section.firstChild);
        });
    }
    
    simplifyLanguage() {
        // Replace complex terms with simpler alternatives
        const replacements = {
            'utilize': 'use',
            'facilitate': 'help',
            'implement': 'start',
            'optimize': 'improve',
            'leverage': 'use',
            'streamline': 'simplify'
        };
        
        // Only apply to content areas, not technical elements
        document.querySelectorAll('.content p, .content h1, .content h2, .content h3, article p').forEach(element => {
            // Skip if element has code or technical content
            if (element.querySelector('code') || element.classList.contains('technical')) {
                return;
            }
            
            let text = element.textContent;
            Object.entries(replacements).forEach(([complex, simple]) => {
                text = text.replace(new RegExp(`\\b${complex}\\b`, 'gi'), simple);
            });
            element.textContent = text;
        });
    }
    
    addProgressIndicators() {
        // Add progress indicators for multi-step processes
        document.querySelectorAll('.onboarding-step, .wizard-step').forEach((step, index, steps) => {
            const progress = document.createElement('div');
            progress.className = 'step-progress';
            progress.textContent = `Step ${index + 1} of ${steps.length}`;
            progress.style.cssText = `
                font-size: 0.875rem;
                color: #666;
                margin-bottom: 0.5rem;
            `;
            
            step.insertBefore(progress, step.firstChild);
        });
    }
    
    setupErrorPrevention() {
        // Add confirmation for destructive actions
        document.querySelectorAll('button[data-destructive]').forEach(button => {
            button.addEventListener('click', (e) => {
                if (!confirm('Are you sure you want to perform this action? This cannot be undone.')) {
                    e.preventDefault();
                }
            });
        });
        
        // Add undo functionality
        this.setupUndoFunctionality();
    }
    
    setupUndoFunctionality() {
        const undoStack = [];
        
        // Track user actions
        document.addEventListener('click', (e) => {
            if (e.target.matches('button[data-trackable]')) {
                undoStack.push({
                    action: e.target.textContent,
                    timestamp: Date.now(),
                    element: e.target
                });
            }
        });
        
        // Add undo button
        if (undoStack.length > 0) {
            const undoBtn = document.createElement('button');
            undoBtn.textContent = 'Undo';
            undoBtn.addEventListener('click', () => {
                const lastAction = undoStack.pop();
                if (lastAction) {
                    // Implement undo logic based on action type
                    this.announceToScreenReader(`Undid: ${lastAction.action}`);
                }
            });
        }
    }
    
    /**
     * Accessibility Testing
     */
    setupAccessibilityTesting() {
        // Run accessibility checks
        this.runAccessibilityChecks();
        
        // Monitor for accessibility issues
        this.monitorAccessibilityIssues();
    }
    
    runAccessibilityChecks() {
        // Check for missing alt text
        document.querySelectorAll('img:not([alt])').forEach(img => {
            // console.warn('Image missing alt text:', img);
        });
        
        // Check for missing labels
        document.querySelectorAll('input:not([aria-label]):not([aria-labelledby])').forEach(input => {
            if (!input.closest('label')) {
                // console.warn('Input missing label:', input);
            }
        });
        
        // Check for proper heading structure
        this.validateHeadingStructure();
        
        // Check for sufficient color contrast
        this.checkColorContrast();
    }
    
    validateHeadingStructure() {
        const headings = document.querySelectorAll('h1, h2, h3, h4, h5, h6');
        let previousLevel = 0;
        
        headings.forEach(heading => {
            const currentLevel = parseInt(heading.tagName.charAt(1));
            if (currentLevel > previousLevel + 1) {
                // console.warn('Skipped heading level:', heading);
            }
            previousLevel = currentLevel;
        });
    }
    
    checkColorContrast() {
        // Basic color contrast check
        document.querySelectorAll('*').forEach(element => {
            const style = window.getComputedStyle(element);
            const backgroundColor = style.backgroundColor;
            const color = style.color;
            
            // Simple contrast check (this is a basic implementation)
            if (backgroundColor && color) {
                // In a real implementation, you would calculate the actual contrast ratio
                // For now, we'll just log elements with potential contrast issues
                if (backgroundColor === color) {
                    // console.warn('Potential contrast issue:', element);
                }
            }
        });
    }
    
    monitorAccessibilityIssues() {
        // Monitor for dynamically added content
        this.mutationObserver = new MutationObserver((mutations) => {
            mutations.forEach((mutation) => {
                mutation.addedNodes.forEach((node) => {
                    if (node.nodeType === Node.ELEMENT_NODE) {
                        this.checkNewElement(node);
                    }
                });
            });
        });
        
        this.mutationObserver.observe(document.body, {
            childList: true,
            subtree: true
        });
    }
    
    checkNewElement(element) {
        // Check new elements for accessibility issues
        if (element.tagName === 'IMG' && !element.hasAttribute('alt')) {
            // console.warn('New image missing alt text:', element);
        }
        
        if (element.tagName === 'BUTTON' && !element.textContent.trim() && !element.hasAttribute('aria-label')) {
            // console.warn('New button missing accessible label:', element);
        }
    }
    
    /**
     * Preferences Management
     */
    loadPreferences() {
        const saved = localStorage.getItem('coraAccessibilityPrefs');
        if (saved) {
            try {
                const prefs = JSON.parse(saved);
                this.voiceControlActive = prefs.voiceControlActive || false;
                this.highContrastMode = prefs.highContrastMode || false;
                this.darkMode = prefs.darkMode || false;
                this.fontSize = prefs.fontSize || 16;
                
                // Apply saved preferences
                if (this.highContrastMode) {
                    document.body.classList.add('high-contrast');
                }
                if (this.darkMode) {
                    document.body.classList.add('dark-mode');
                }
                this.applyFontSize();
            } catch (e) {
                // console.error('Error loading accessibility preferences:', e);
            }
        }
        
        // Check system preferences
        if (window.matchMedia('(prefers-color-scheme: dark)').matches) {
            this.darkMode = true;
            document.body.classList.add('dark-mode');
        }
    }
    
    savePreferences() {
        const prefs = {
            voiceControlActive: this.voiceControlActive,
            highContrastMode: this.highContrastMode,
            darkMode: this.darkMode,
            fontSize: this.fontSize
        };
        localStorage.setItem('coraAccessibilityPrefs', JSON.stringify(prefs));
    }
    
    /**
     * Dark Mode Support
     */
    setupDarkMode() {
        // Check system preference
        window.matchMedia('(prefers-color-scheme: dark)').addEventListener('change', (e) => {
            if (!this.highContrastMode) { // Don't override high contrast
                this.darkMode = e.matches;
                document.body.classList.toggle('dark-mode', this.darkMode);
                this.savePreferences();
            }
        });
        
        // Add dark mode styles
        const style = document.createElement('style');
        style.textContent = `
            .dark-mode {
                background: #1a1a1a !important;
                color: #e0e0e0 !important;
            }
            
            .dark-mode .wellness-card {
                background: #2a2a2a !important;
                border-color: #3a3a3a !important;
                color: #e0e0e0 !important;
            }
            
            .dark-mode input, .dark-mode select, .dark-mode textarea {
                background: #2a2a2a !important;
                border-color: #3a3a3a !important;
                color: #e0e0e0 !important;
            }
            
            .dark-mode .wellness-btn {
                background: linear-gradient(135deg, #7B4EA8, #48C87B) !important;
            }
        `;
        document.head.appendChild(style);
    }
    
    /**
     * Utility Methods
     */
    generateId(element) {
        if (!element.id) {
            element.id = 'element-' + Math.random().toString(36).substr(2, 9);
        }
        return element.id;
    }
    
    showHelp() {
        const help = document.createElement('div');
        help.className = 'accessibility-help';
        help.innerHTML = `
            <h2>Accessibility Help</h2>
            <ul>
                <li><strong>Alt + V:</strong> Toggle voice control</li>
                <li><strong>Alt + H:</strong> Toggle high contrast</li>
                <li><strong>Alt + =:</strong> Increase font size</li>
                <li><strong>Alt + -:</strong> Decrease font size</li>
                <li><strong>Alt + 0:</strong> Reset font size</li>
                <li><strong>Tab:</strong> Navigate with keyboard</li>
                <li><strong>Enter/Space:</strong> Activate buttons</li>
            </ul>
        `;
        
        help.style.cssText = `
            position: fixed;
            top: 50%;
            left: 50%;
            transform: translate(-50%, -50%);
            background: white;
            padding: 2rem;
            border-radius: 8px;
            box-shadow: 0 4px 20px rgba(0,0,0,0.3);
            z-index: 10000;
            max-width: 400px;
        `;
        
        // Add close button
        const closeBtn = document.createElement('button');
        closeBtn.innerHTML = '&times;';
        closeBtn.setAttribute('aria-label', 'Close help dialog');
        closeBtn.style.cssText = `
            position: absolute;
            top: 10px;
            right: 10px;
            background: none;
            border: none;
            font-size: 24px;
            cursor: pointer;
            color: #666;
        `;
        closeBtn.addEventListener('click', () => help.remove());
        help.appendChild(closeBtn);
        
        document.body.appendChild(help);
        
        // Close on escape
        document.addEventListener('keydown', (e) => {
            if (e.key === 'Escape') {
                help.remove();
            }
        });
    }
    
    /**
     * Cleanup Method
     */
    cleanup() {
        // Stop voice recognition
        if (this.recognition) {
            this.stopVoiceRecognition();
        }
        
        // Disconnect mutation observer
        if (this.mutationObserver) {
            this.mutationObserver.disconnect();
        }
    }
    
    /**
     * Public API
     */
    getAccessibilityStatus() {
        return {
            voiceControlActive: this.voiceControlActive,
            highContrastMode: this.highContrastMode,
            reducedMotionMode: this.reducedMotionMode,
            fontSize: this.fontSize
        };
    }
    
    enableAccessibility() {
        this.setupKeyboardNavigation();
        this.setupScreenReaderSupport();
        this.setupFocusManagement();
    }
}

// Initialize accessibility features
const coraAccessibility = new CORAAccessibility();

// Export for use in other modules
window.CORAAccessibility = coraAccessibility;

// Auto-enable on DOM ready
document.addEventListener('DOMContentLoaded', () => {
    coraAccessibility.enableAccessibility();
});

// Cleanup on page unload
window.addEventListener('beforeunload', () => {
    coraAccessibility.cleanup();
});

// Export for module systems
if (typeof module !== 'undefined' && module.exports) {
    module.exports = CORAAccessibility;
} 