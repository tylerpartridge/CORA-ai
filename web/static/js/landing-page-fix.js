/**
 * Landing Page Fix - Comprehensive functionality restoration
 * Fixes all buttons, forms, and interactive elements
 */

document.addEventListener('DOMContentLoaded', function() {
    // console.log('Landing page fix script loaded');

    // 1. Fix all buttons with onclick handlers
    function fixButtonClicks() {
        // Fix pricing buttons
        const pricingButtons = document.querySelectorAll('button[onclick*="pricing"]');
        pricingButtons.forEach(button => {
            button.removeAttribute('onclick');
            button.addEventListener('click', function() {
                window.location.href = '/pricing';
            });
        });

        // Fix onboarding buttons to go to signup instead
        const onboardingButtons = document.querySelectorAll('button[onclick*="onboarding"]');
        onboardingButtons.forEach(button => {
            button.removeAttribute('onclick');
            button.addEventListener('click', function() {
                window.location.href = '/signup';
            });
        });

        // Fix any other buttons with onclick
        const allButtons = document.querySelectorAll('button[onclick]');
        allButtons.forEach(button => {
            const onclickValue = button.getAttribute('onclick');
            button.removeAttribute('onclick');
            
            if (onclickValue.includes('window.location.href')) {
                const match = onclickValue.match(/window\.location\.href\s*=\s*['"]([^'"]+)['"]/);
                if (match && match[1]) {
                    button.addEventListener('click', function() {
                        window.location.href = match[1];
                    });
                }
            }
        });
    }

    // 2. Fix email capture forms
    function fixEmailForms() {
        // Main hero email form
        const heroEmailForm = document.getElementById('emailForm');
        if (heroEmailForm) {
            heroEmailForm.addEventListener('submit', async function(e) {
                e.preventDefault();
                const emailInput = this.querySelector('input[type="email"]');
                const submitButton = this.querySelector('button[type="submit"]');
                
                if (!emailInput || !emailInput.value) return;

                const email = emailInput.value.trim();
                const originalButtonText = submitButton.textContent;
                
                // Show loading state
                submitButton.disabled = true;
                submitButton.textContent = 'Capturing...';

                try {
                    // Call the API endpoint
                    const response = await fetch('/api/v1/capture-email', {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/x-www-form-urlencoded',
                        },
                        body: `email=${encodeURIComponent(email)}`
                    });

                    const data = await response.json();

                    if (data.success) {
                        // Success - redirect to signup with email
                        localStorage.setItem('signupEmail', email);
                        submitButton.textContent = '✓ Success!';
                        setTimeout(() => {
                            window.location.href = '/signup';
                        }, 500);
                    } else {
                        // Error - show message
                        submitButton.textContent = 'Try Again';
                        setTimeout(() => {
                            submitButton.disabled = false;
                            submitButton.textContent = originalButtonText;
                        }, 2000);
                    }
                } catch (error) {
                    // console.error('Email capture error:', error);
                    // Fallback - still redirect to signup
                    localStorage.setItem('signupEmail', email);
                    window.location.href = '/signup';
                }
            });
        }

        // Footer email forms
        const footerEmailForms = document.querySelectorAll('form');
        footerEmailForms.forEach(form => {
            // Skip if it's the main hero form or has no email input
            if (form.id === 'emailForm' || !form.querySelector('input[type="email"]')) return;

            form.addEventListener('submit', async function(e) {
                e.preventDefault();
                const emailInput = this.querySelector('input[type="email"]');
                const submitButton = this.querySelector('button[type="submit"]');
                
                if (!emailInput || !emailInput.value) return;

                const email = emailInput.value.trim();
                const originalButtonText = submitButton ? submitButton.textContent : '';
                
                // Show loading state
                if (submitButton) {
                    submitButton.disabled = true;
                    submitButton.textContent = 'Subscribing...';
                }

                try {
                    // Call the API endpoint
                    const response = await fetch('/api/v1/capture-email', {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/x-www-form-urlencoded',
                        },
                        body: `email=${encodeURIComponent(email)}`
                    });

                    const data = await response.json();

                    if (data.success) {
                        // Success
                        emailInput.value = '';
                        if (submitButton) {
                            submitButton.textContent = '✓ Subscribed!';
                            setTimeout(() => {
                                submitButton.disabled = false;
                                submitButton.textContent = originalButtonText;
                            }, 3000);
                        }
                    } else {
                        // Error
                        if (submitButton) {
                            submitButton.textContent = 'Try Again';
                            setTimeout(() => {
                                submitButton.disabled = false;
                                submitButton.textContent = originalButtonText;
                            }, 2000);
                        }
                    }
                } catch (error) {
                    // console.error('Email capture error:', error);
                    if (submitButton) {
                        submitButton.disabled = false;
                        submitButton.textContent = originalButtonText;
                    }
                }
            });
        });
    }

    // 3. Fix lead capture form
    function fixLeadForm() {
        // Try both possible IDs
        const leadForm = document.getElementById('lead-form') || document.getElementById('leadForm');
        if (leadForm) {
            leadForm.addEventListener('submit', async function(e) {
                e.preventDefault();
                
                const formData = new FormData(this);
                const submitButton = this.querySelector('button[type="submit"]');
                const originalButtonText = submitButton.textContent;
                
                // Show loading state
                submitButton.disabled = true;
                submitButton.textContent = 'Submitting...';

                try {
                    const response = await fetch('/api/v1/lead-capture', {
                        method: 'POST',
                        body: formData
                    });

                    const data = await response.json();

                    if (data.success) {
                        // Success - show message and redirect
                        submitButton.textContent = '✓ Success!';
                        
                        // Show success message
                        const alertDiv = document.createElement('div');
                        alertDiv.className = 'alert alert-success mt-3';
                        alertDiv.textContent = data.message || 'Thank you! Redirecting to signup...';
                        this.appendChild(alertDiv);

                        // Redirect after delay
                        setTimeout(() => {
                            if (data.redirect) {
                                window.location.href = data.redirect;
                            } else {
                                window.location.href = '/signup';
                            }
                        }, 1500);
                    } else {
                        // Error - show message
                        submitButton.textContent = 'Try Again';
                        
                        const alertDiv = document.createElement('div');
                        alertDiv.className = 'alert alert-danger mt-3';
                        alertDiv.textContent = data.message || 'An error occurred. Please try again.';
                        this.appendChild(alertDiv);
                        
                        setTimeout(() => {
                            submitButton.disabled = false;
                            submitButton.textContent = originalButtonText;
                            alertDiv.remove();
                        }, 3000);
                    }
                } catch (error) {
                    // console.error('Lead capture error:', error);
                    submitButton.disabled = false;
                    submitButton.textContent = originalButtonText;
                }
            });
        }
    }

    // 4. Fix navigation links
    function fixNavigation() {
        // Fix navbar brand
        const navbarBrand = document.querySelector('.navbar-brand');
        if (navbarBrand) {
            navbarBrand.style.cursor = 'pointer';
            navbarBrand.addEventListener('click', function(e) {
                if (!this.href) {
                    e.preventDefault();
                    window.location.href = '/';
                }
            });
        }

        // Ensure all nav links work
        const navLinks = document.querySelectorAll('.nav-link');
        navLinks.forEach(link => {
            if (!link.href || link.href === '#') {
                const text = link.textContent.trim().toLowerCase();
                if (text.includes('features')) link.href = '/features';
                else if (text.includes('pricing')) link.href = '/pricing';
                else if (text.includes('how it works')) link.href = '/how-it-works';
                else if (text.includes('reviews')) link.href = '/reviews';
                else if (text.includes('contact')) link.href = '/contact';
                else if (text.includes('login')) link.href = '/login';
            }
        });
    }

    // 5. Fix hover effects (move from inline)
    function fixHoverEffects() {
        // Fix button hover effects
        const buttons = document.querySelectorAll('button[onmouseover], button[onmouseout]');
        buttons.forEach(button => {
            button.removeAttribute('onmouseover');
            button.removeAttribute('onmouseout');
            
            button.addEventListener('mouseenter', function() {
                this.style.transform = 'translateY(-2px)';
                this.style.boxShadow = '0 6px 20px rgba(255,152,0,0.5)';
            });
            
            button.addEventListener('mouseleave', function() {
                this.style.transform = 'translateY(0)';
                this.style.boxShadow = '0 4px 15px rgba(255,152,0,0.4)';
            });
        });

        // Fix input focus effects
        const inputs = document.querySelectorAll('input[type="email"], input[type="text"], select');
        inputs.forEach(input => {
            input.addEventListener('focus', function() {
                this.style.borderColor = '#FF9800';
                this.style.boxShadow = '0 0 0 2px rgba(255,152,0,0.1)';
            });
            
            input.addEventListener('blur', function() {
                this.style.borderColor = 'rgba(255,152,0,0.3)';
                this.style.boxShadow = 'none';
            });
        });
    }

    // Execute all fixes
    fixButtonClicks();
    fixEmailForms();
    fixLeadForm();
    fixNavigation();
    fixHoverEffects();

    // console.log('Landing page functionality restored');
});