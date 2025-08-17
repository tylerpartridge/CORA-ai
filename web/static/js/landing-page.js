/**
 * 🧭 LOCATION: /CORA/web/static/js/landing-page.js
 * 🎯 PURPOSE: Landing page functionality - voice capture, email capture, plan selection
 * 🔗 IMPORTS: CORASecurity (from security.js)
 * 📤 EXPORTS: Landing page functions
 * 🔄 PATTERN: External script to avoid CSP inline script issues
 * 📝 STATUS: Production ready for enhanced landing page
 */

// Voice Capture Demo
function demoVoiceCapture() {
    const btn = event.currentTarget;
    const micIcon = btn.querySelector('.mic-icon');
    
    // Add listening animation
    btn.classList.add('listening');
    micIcon.textContent = '🔴';
    
    // Simulate voice capture
    setTimeout(() => {
        // Show sample transcription
        const demoText = document.createElement('div');
        demoText.className = 'alert alert-success mt-3 mx-auto';
        demoText.style.maxWidth = '400px';
        demoText.innerHTML = `
            <strong>Heard:</strong> "Just spent $47 at Office Depot for printer paper"<br>
            <small class="text-muted">Automatically categorized as: Office Supplies</small>
        `;
        btn.parentElement.appendChild(demoText);
        
        // Reset button
        btn.classList.remove('listening');
        micIcon.textContent = '🎤';
        
        // Remove demo after 5 seconds
        setTimeout(() => demoText.remove(), 5000);
    }, 2000);
}

// Wellness Score Animation
function initWellnessScoreAnimation() {
    const scores = document.querySelectorAll('.wellness-score-demo');
    scores.forEach(score => {
        const target = parseInt(score.textContent);
        let current = 0;
        const increment = target / 50;
        
        const timer = setInterval(() => {
            current += increment;
            if (current >= target) {
                current = target;
                clearInterval(timer);
            }
            score.textContent = Math.round(current);
        }, 30);
    });
}

// Plan selection
function selectPlan(planName) {
    // Store selected plan and redirect to checkout
    sessionStorage.setItem('selectedPlan', planName);
    window.location.href = '/pricing/' + planName;
}

// Quick email capture in hero
async function quickCapture(e) {
    e.preventDefault();
    const form = e.target;
    const emailInput = form.querySelector('#emailInput');
    const submitBtn = form.querySelector('#submitBtn');
    const btnText = submitBtn.querySelector('.btn-text');
    const btnLoading = submitBtn.querySelector('.btn-loading');
    
    // Validate email
    if (!emailInput.checkValidity()) {
        emailInput.classList.add('is-invalid');
        return;
    }
    
    emailInput.classList.remove('is-invalid');
    
    // Show loading state
    btnText.classList.add('d-none');
    btnLoading.classList.remove('d-none');
    submitBtn.disabled = true;
    
    // Store email and redirect to signup with email pre-filled
    const email = emailInput.value;
    sessionStorage.setItem('signupEmail', email);
    
    // Capture email first, then redirect
    try {
        const formData = new FormData();
        formData.append('email', email);
        
        // Fire and forget - don't wait for response
        fetch('/api/v1/capture-email', {
            method: 'POST',
            body: formData
        });
    } catch (error) {
        // console.log('Email capture error:', error);
    }
    
    // Redirect to signup with email in query string
    window.location.href = '/signup?email=' + encodeURIComponent(email);
    
    // TODO: Enable when server is running
    // try {
    //     const formData = new FormData();
    //     formData.append('email', emailInput.value);
    //     
    //     const response = await fetch('/api/v1/capture-email', {
    //         method: 'POST',
    //         body: formData
    //     });
    //     
    //     if (response.ok) {
    //         // Show success message using secure function
    //         form.innerHTML = CORASecurity.sanitizeHtml('<div class="text-center text-white"><i class="fas fa-check-circle me-2"></i>You\'re on the list! Check your email for early access.</div>');
    //     } else {
    //         throw new Error('Failed to capture email');
    //     }
    // } catch (error) {
    //     // console.error('Email capture error:', error);
    //     // Show error message using secure function
    //     form.innerHTML = CORASecurity.sanitizeHtml('<div class="text-center text-white"><i class="fas fa-exclamation-triangle me-2"></i>Something went wrong. Please try again.</div>');
    //     
    //     // Reset form after 3 seconds
    //     setTimeout(() => {
    //         location.reload();
    //     }, 3000);
    // }
}

// Open CORA chat
function openCoraChat() {
    // Check if CORA chat instance exists
    if (window.coraChat && window.coraChat.openChat) {
        window.coraChat.openChat();
    } else {
        // Fallback - try to find and click the chat bubble
        const chatBubble = document.querySelector('.cora-chat-bubble');
        if (chatBubble) {
            chatBubble.click();
        } else {
            // console.log('CORA chat not initialized yet');
        }
    }
}

// Footer subscribe functionality
function initFooterSubscribe() {
    const subscribeBtn = document.querySelector('footer .btn-primary');
    const subscribeInput = document.querySelector('footer input[type="email"]');
    
    if (subscribeBtn && subscribeInput) {
        subscribeBtn.addEventListener('click', function() {
            const email = subscribeInput.value;
            if (email) {
                subscribeBtn.textContent = 'Subscribed!';
                subscribeBtn.disabled = true;
                subscribeInput.value = '';
                setTimeout(() => {
                    subscribeBtn.textContent = 'Subscribe';
                    subscribeBtn.disabled = false;
                }, 2000);
            }
        });
    }
}

// Smooth scrolling for anchor links
function initSmoothScrolling() {
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function (e) {
            e.preventDefault();
            const target = document.querySelector(this.getAttribute('href'));
            if (target) {
                target.scrollIntoView({
                    behavior: 'smooth',
                    block: 'start'
                });
            }
        });
    });
}

// Lead form submission - now full signup
function initLeadForm() {
    const leadForm = document.getElementById('leadForm');
    if (leadForm) {
        leadForm.addEventListener('submit', async function(e) {
            e.preventDefault();
            
            if (!leadForm.checkValidity()) {
                e.stopPropagation();
                leadForm.classList.add('was-validated');
                return;
            }
            
            const formData = new FormData(this);
            const submitBtn = this.querySelector('button[type="submit"]');
            const originalText = submitBtn.textContent;
            
            // Check passwords match - use the correct field IDs
            const password = document.getElementById('landing_password').value;
            const confirmPassword = document.getElementById('landing_confirm_password').value;
            if (password !== confirmPassword) {
                alert('Passwords do not match');
                return;
            }
            
            submitBtn.textContent = 'Creating Account...';
            submitBtn.disabled = true;
            
            try {
                // Create the account directly
                const signupData = {
                    email: formData.get('email'),
                    password: password,
                    confirm_password: confirmPassword
                };
                
                const response = await fetch('/api/auth/register', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify(signupData)
                });
                
                const result = await response.json();
                
                if (response.ok) {
                    // Store email for later
                    localStorage.setItem('signupEmail', formData.get('email'));
                    
                    // Check if we should auto-login and redirect to onboarding
                    if (result.next_action === 'auto_login' && result.redirect) {
                        // User is auto-verified (dev mode), redirect to onboarding
                        this.innerHTML = `
                            <div class="text-center" style="padding: 2rem;">
                                <div style="color: #69F0AE; font-size: 3rem; margin-bottom: 1rem;">✓</div>
                                <h3 style="color: #ffffff; margin-bottom: 1rem;">Welcome to CORA!</h3>
                                <p style="color: #a0aec0;">Taking you to personalize your experience...</p>
                            </div>
                        `;
                        setTimeout(() => {
                            window.location.href = result.redirect;  // Should be /onboarding
                        }, 1500);
                    } else if (result.next_action === 'verify_email') {
                        // Show email verification message
                        this.innerHTML = `
                            <div class="text-center" style="padding: 2rem;">
                                <div style="color: #69F0AE; font-size: 3rem; margin-bottom: 1rem;">✓</div>
                                <h3 style="color: #ffffff; margin-bottom: 1rem;">Account Created!</h3>
                                <div style="background: rgba(255,152,0,0.1); border: 2px solid #FF9800; border-radius: 8px; padding: 1.5rem; margin: 1.5rem 0;">
                                    <h4 style="color: #FF9800; margin-bottom: 1rem;">📧 CHECK YOUR EMAIL NOW</h4>
                                    <p style="color: #ffffff; margin-bottom: 0.5rem;">We sent a verification email to:</p>
                                    <p style="color: #69F0AE; font-weight: bold; margin-bottom: 1rem;">${formData.get('email')}</p>
                                    <p style="color: #a0aec0; font-size: 0.9rem;">
                                        ⚠️ Check your SPAM/JUNK folder if you don't see it<br>
                                        Click the verification link to activate your account
                                    </p>
                                </div>
                                <div style="color: #a0aec0; font-size: 0.9rem;">Redirecting to login page...</div>
                            </div>
                        `;
                        
                        // Go to login after showing message
                        setTimeout(() => {
                            window.location.href = '/login';
                        }, 5000);  // Give them time to read
                    }
                } else {
                    // Don't throw error if response was actually successful
                    console.error('Unexpected response:', result);
                    throw new Error(result.message || result.detail || 'Signup failed');
                }
            } catch (error) {
                // Log full error for debugging
                console.error('Signup error details:', error);
                
                // Always restore button state
                if (submitBtn) {
                    submitBtn.textContent = originalText || 'Create Free Account →';
                    submitBtn.disabled = false;
                }
                
                // Show error message
                alert(`Signup failed: ${error.message || 'Unknown error. Please check console.'}`);
            }
        });
    }
}

// Initialize all landing page functionality
document.addEventListener('DOMContentLoaded', function() {
    // console.log('🎯 CORA Landing Page initialized');
    
    // Initialize all features
    initWellnessScoreAnimation();
    initFooterSubscribe();
    initSmoothScrolling();
    initLeadForm();
    
    // Add event listeners for buttons with data-plan attributes
    document.querySelectorAll('[data-plan]').forEach(element => {
        const plan = element.getAttribute('data-plan');
        element.addEventListener('click', () => selectPlan(plan));
    });
    
    // Add event listener for voice capture button
    const voiceCaptureBtn = document.getElementById('voiceCaptureBtn');
    if (voiceCaptureBtn) {
        voiceCaptureBtn.addEventListener('click', demoVoiceCapture);
    }
    
    // Add event listener for email form
    const emailForm = document.getElementById('emailForm');
    if (emailForm) {
        emailForm.addEventListener('submit', quickCapture);
    }
    
    // Service Worker registration disabled on landing page
    // Uncomment when server is running
    // if ('serviceWorker' in navigator) {
    //     window.addEventListener('load', () => {
    //         navigator.serviceWorker.register('/static/service-worker.js')
    //             .then(reg => // console.log('🔧 Service Worker registered'))
    //             .catch(err => // console.error('Service Worker registration failed:', err));
    //     });
    // }
});

// Export functions for global access
window.demoVoiceCapture = demoVoiceCapture;
window.selectPlan = selectPlan;
window.quickCapture = quickCapture; 