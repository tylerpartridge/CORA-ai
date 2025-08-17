/**
 * Voice Button Activation Fix
 * Ensures voice button is properly initialized on dashboard
 */

(function() {
    'use strict';
    
    // Wait for DOM and ensure voice button initializes
    const ensureVoiceButton = () => {
        const container = document.querySelector('.voice-button-container');
        
        if (container && !container.querySelector('.voice-btn')) {
            // console.log('[Voice Fix] Container found but no button, initializing...');
            
            // Check if VoiceButton class exists
            if (typeof VoiceButton !== 'undefined') {
                // Initialize the voice button
                const voiceButton = new VoiceButton(container, {
                    onSuccess: (expense) => {
                        // console.log('[Voice Fix] Expense created:', expense);
                        // Refresh dashboard data
                        if (typeof loadTransactions === 'function') {
                            loadTransactions();
                        }
                        if (typeof updateDashboardMetrics === 'function') {
                            updateDashboardMetrics();
                        }
                    },
                    onError: (message, parsed) => {
                        // console.error('[Voice Fix] Error:', message, parsed);
                    }
                });
                
                // console.log('[Voice Fix] Voice button initialized successfully!');
                
                // Add visual confirmation
                container.style.border = '2px solid #22c55e';
                setTimeout(() => {
                    container.style.border = 'none';
                }, 2000);
                
            } else if (typeof initVoiceButton === 'function') {
                // Use existing initialization function
                initVoiceButton();
                // console.log('[Voice Fix] Called initVoiceButton()');
            } else {
                // console.error('[Voice Fix] VoiceButton class not found, retrying in 1 second...');
                setTimeout(ensureVoiceButton, 1000);
            }
        } else if (container && container.querySelector('.voice-btn')) {
            // console.log('[Voice Fix] Voice button already initialized');
        } else {
            // console.log('[Voice Fix] Container not found, retrying in 500ms...');
            setTimeout(ensureVoiceButton, 500);
        }
    };
    
    // Start checking when DOM is ready
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', ensureVoiceButton);
    } else {
        // DOM already loaded, check immediately
        setTimeout(ensureVoiceButton, 100);
    }
    
    // Also check when window fully loads (in case of async scripts)
    window.addEventListener('load', () => {
        setTimeout(ensureVoiceButton, 500);
    });
    
    // Expose for debugging
    window.voiceButtonFix = {
        check: ensureVoiceButton,
        status: () => {
            const container = document.querySelector('.voice-button-container');
            const button = document.querySelector('.voice-btn');
            // console.log('Container:', container ? 'Found' : 'Not Found');
            // console.log('Button:', button ? 'Found' : 'Not Found');
            // console.log('VoiceButton class:', typeof VoiceButton !== 'undefined' ? 'Available' : 'Not Available');
            // console.log('initVoiceButton function:', typeof initVoiceButton !== 'undefined' ? 'Available' : 'Not Available');
        }
    };
    
})();

// console.log('[Voice Fix] Voice button activation fix loaded. Use voiceButtonFix.status() to check status.');