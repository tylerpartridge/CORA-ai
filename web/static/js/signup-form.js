// CORA Signup Form Enhancements: strength meter, show/hide toggle, autosave
(function(){
  function checkPasswordStrength(password){
    let strength = 0;
    const feedback = [];
    if (password.length >= 10) strength++; else feedback.push('At least 10 characters');
    if (/[A-Z]/.test(password)) strength++; else feedback.push('One uppercase letter');
    if (/[0-9]/.test(password)) strength++; else feedback.push('One number');
    if (/[^A-Za-z0-9]/.test(password)) strength++; else feedback.push('One special character');
    const levels = ['weak','medium','strong','strong'];
    return { score: strength, label: levels[Math.min(strength,3)], feedback };
  }

  function addPasswordToggle(){
    const inputs = document.querySelectorAll('input[type="password"]');
    inputs.forEach(input => {
      if (input.parentElement && input.parentElement.classList.contains('password-input-wrapper')) return;
      const wrapper = document.createElement('div');
      wrapper.className = 'password-input-wrapper';
      input.parentNode.insertBefore(wrapper, input);
      wrapper.appendChild(input);
      const toggle = document.createElement('button');
      toggle.type = 'button';
      toggle.className = 'password-toggle';
      toggle.setAttribute('aria-label','Show password');
      toggle.textContent = '👁️';
      toggle.addEventListener('click', ()=>{
        const isPw = input.type === 'password';
        input.type = isPw ? 'text' : 'password';
        toggle.textContent = isPw ? '🙈' : '👁️';
        toggle.setAttribute('aria-label', isPw ? 'Hide password' : 'Show password');
      });
      wrapper.appendChild(toggle);
    });
  }

  class FormAutosave{
    constructor(formId, key){ this.form=document.getElementById(formId); this.key=key; if(this.form) this.init(); }
    init(){
      try{
        const saved = localStorage.getItem(this.key);
        if (saved){
          const data = JSON.parse(saved);
          Object.keys(data).forEach(name=>{ const el=this.form.querySelector(`[name="${name}"]`); if(el && el.type!=='password') el.value=data[name]; });
        }
      }catch(_){/* noop */}
      this.form.addEventListener('input', ()=>this.save());
      this.form.addEventListener('submit', ()=>this.clear());
    }
    save(){
      const data={};
      this.form.querySelectorAll('input, textarea, select').forEach(el=>{ if(el.name && el.type!=='password') data[el.name]=el.value; });
      try{ localStorage.setItem(this.key, JSON.stringify(data)); }catch(_){/* noop */}
    }
    clear(){ try{ localStorage.removeItem(this.key); }catch(_){/* noop */} }
  }

  function wireStrengthMeter(){
    const pw = document.getElementById('password');
    const bar = document.getElementById('passwordStrength');
    if (!pw || !bar) return;
    pw.addEventListener('input', ()=>{
      const {score} = checkPasswordStrength(pw.value);
      bar.className = 'password-strength-bar';
      if (pw.value.length === 0){ bar.style.width='0%'; return; }
      if (score <= 1){ bar.classList.add('strength-weak'); }
      else if (score === 2){ bar.classList.add('strength-medium'); }
      else { bar.classList.add('strength-strong'); }
    });
  }

  function injectStyles(){
    if (document.getElementById('signup-form-enhance-css')) return;
    const s=document.createElement('style'); s.id='signup-form-enhance-css';
    s.textContent = `.password-input-wrapper{position:relative}.password-toggle{position:absolute;right:10px;top:50%;transform:translateY(-50%);background:none;border:none;cursor:pointer;font-size:18px;padding:5px}`;
    document.head.appendChild(s);
  }

  function init(){
    injectStyles();
    addPasswordToggle();
    wireStrengthMeter();
    new FormAutosave('signupForm','cora_signup_autosave');
  }

  if (document.readyState==='loading') document.addEventListener('DOMContentLoaded', init); else init();
})();

// Signup Form Logic
document.addEventListener('DOMContentLoaded', function() {
    // Note: Focus behavior is handled by inline script in signup.html template
    // to avoid timing conflicts. Only handle email pre-filling here.
    const urlParams = new URLSearchParams(window.location.search);
    const emailFromUrl = urlParams.get('email');
    if (emailFromUrl) {
        const emailField = document.getElementById('email');
        if (emailField && !emailField.value) {
            emailField.value = decodeURIComponent(emailFromUrl);
        }
    } else {
        // Also check localStorage for email
        const storedEmail = localStorage.getItem('signupEmail');
        if (storedEmail) {
            const emailField = document.getElementById('email');
            if (emailField && !emailField.value) {
                emailField.value = storedEmail;
            }
        }
    }
    
    // Real-time email validation
    const emailInput = document.getElementById('email');
    if (emailInput) {
        emailInput.addEventListener('blur', function() {
            const email = this.value.trim();
            const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
            
            if (email && !emailRegex.test(email)) {
                this.style.borderColor = '#FF5252';
                this.style.boxShadow = '0 0 0 3px rgba(255, 82, 82, 0.1)';
                
                // Show validation message
                let validationMsg = this.parentElement.querySelector('.validation-message');
                if (!validationMsg) {
                    validationMsg = document.createElement('div');
                    validationMsg.className = 'validation-message';
                    validationMsg.style.color = '#FF5252';
                    validationMsg.style.fontSize = '0.875rem';
                    validationMsg.style.marginTop = '0.5rem';
                    this.parentElement.appendChild(validationMsg);
                }
                validationMsg.textContent = 'Please enter a valid email address';
            } else {
                this.style.borderColor = '';
                this.style.boxShadow = '';
                
                // Remove validation message
                const validationMsg = this.parentElement.querySelector('.validation-message');
                if (validationMsg) {
                    validationMsg.remove();
                }
            }
        });
    }
    
    // Password visibility toggles
    const passwordInput = document.getElementById('password');
    const passwordToggle = document.getElementById('passwordToggle');
    const passwordConfirmInput = document.getElementById('passwordConfirm');
    const passwordConfirmToggle = document.getElementById('passwordConfirmToggle');
    const passwordStrength = document.getElementById('passwordStrength');
    const passwordMatch = document.getElementById('passwordMatch');
    const passwordMatchText = document.getElementById('passwordMatchText');
    
    // Password visibility toggle
    if (passwordToggle && passwordInput) {
        passwordToggle.addEventListener('click', function() {
            const type = passwordInput.type === 'password' ? 'text' : 'password';
            passwordInput.type = type;
            this.textContent = type === 'password' ? '👁️' : '🙈';
        });
    }
    
    // Password confirm visibility toggle
    if (passwordConfirmToggle && passwordConfirmInput) {
        passwordConfirmToggle.addEventListener('click', function() {
            const type = passwordConfirmInput.type === 'password' ? 'text' : 'password';
            passwordConfirmInput.type = type;
            this.textContent = type === 'password' ? '👁️' : '🙈';
        });
    }
    
    // Password matching validation
    function checkPasswordMatch() {
        if (passwordInput && passwordConfirmInput && passwordMatch && passwordMatchText) {
            const password = passwordInput.value;
            const confirmPassword = passwordConfirmInput.value;
            
            if (confirmPassword.length > 0) {
                passwordMatch.style.display = 'block';
                if (password === confirmPassword) {
                    passwordMatchText.textContent = '✓ Passwords match';
                    passwordMatchText.style.color = '#69F0AE';
                } else {
                    passwordMatchText.textContent = '✗ Passwords do not match';
                    passwordMatchText.style.color = '#FF5252';
                }
            } else {
                passwordMatch.style.display = 'none';
            }
        }
    }
    
    if (passwordInput) {
        passwordInput.addEventListener('input', checkPasswordMatch);
    }
    
    if (passwordConfirmInput) {
        passwordConfirmInput.addEventListener('input', checkPasswordMatch);
    }
    
    if (passwordInput && passwordStrength) {
        passwordInput.addEventListener('input', function() {
            const password = this.value;
            let strength = 0;
            
            if (password.length >= 10) strength++;
            if (password.match(/[a-z]/) && password.match(/[A-Z]/)) strength++;
            if (password.match(/[0-9]/)) strength++;
            if (password.match(/[^a-zA-Z0-9]/)) strength++;
            
            passwordStrength.className = 'password-strength-bar';
            
            if (password.length === 0) {
                passwordStrength.style.width = '0%';
            } else if (strength <= 1) {
                passwordStrength.classList.add('strength-weak');
            } else if (strength === 2) {
                passwordStrength.classList.add('strength-medium');
            } else {
                passwordStrength.classList.add('strength-strong');
            }
        });
    }
    
    // Form submission
    const form = document.getElementById('signupForm');
    const submitBtn = document.getElementById('submitBtn');
    
    // Prevent double submission
    let isSubmitting = false;
    
    if (form && submitBtn) {
        form.addEventListener('submit', async function(e) {
            e.preventDefault();
            
            // Prevent double submission
            if (isSubmitting) {
                console.log('Form already submitting, ignoring duplicate');
                return;
            }
            
            // Basic validation
            if (!form.checkValidity()) {
                e.stopPropagation();
                form.classList.add('was-validated');
                // console.log('Form validation failed - check password length (12+ chars) and email format');
                return;
            }
            
            // Set flag and show loading state
            isSubmitting = true;
            submitBtn.classList.add('loading');
            submitBtn.disabled = true;
            
            // Validate passwords match
            const password = document.getElementById('password').value;
            const passwordConfirm = document.getElementById('passwordConfirm').value;
            
            if (password !== passwordConfirm) {
                alert('Passwords do not match. Please check and try again.');
                submitBtn.classList.remove('loading');
                submitBtn.disabled = false;
                return;
            }
            
            // Gather form data
            const formData = new FormData(form);
            const data = {
                email: formData.get('email'),
                password: formData.get('password'),
                confirm_password: formData.get('passwordConfirm')  // Backend expects confirm_password
            };
            
            // Name will be collected during onboarding
            
            try {
                // Debug: Log what we're sending
                // console.log('Sending signup data:', JSON.stringify(data, null, 2));
                
                // Call correct API endpoint
                const response = await fetch('/api/auth/register', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify(data)
                });
                
                const result = await response.json();
                
                if (response.ok) {
                    // Store email for potential future use
                    localStorage.setItem('signupEmail', data.email);
                    
                    // Check if we should auto-login and redirect
                    if (result.next_action === 'auto_login' && result.redirect) {
                        // User is auto-verified (dev mode), redirect to plan selection
                        // Hide form and show success briefly
                        form.style.display = 'none';
                        const successState = document.getElementById('successState');
                        if (successState) {
                            successState.style.display = 'block';
                            const msg = document.getElementById('successMessage');
                            if (msg) {
                                msg.textContent = 'Creating your workspace...';
                            }
                        }
                        // Short delay then redirect
                        setTimeout(() => {
                            window.location.href = result.redirect || '/select-plan';
                        }, 1000);
                    } else if (result.next_action === 'verify_email') {
                        // Show email verification message
                        console.log('Showing email verification message');
                        form.style.display = 'none';  // Hide just the form, not its parent
                        const successState = document.getElementById('successState');
                        if (successState) {
                            successState.style.display = 'block';
                            const msg = document.getElementById('successMessage');
                            if (msg) {
                                msg.textContent = `Check your email (${data.email}) to verify your account.`;
                            }
                            // Show resend button
                            const resendContainer = document.getElementById('resendContainer');
                            if (resendContainer) {
                                resendContainer.style.display = 'block';
                            }
                        }
                    } else {
                        // Default success case - show verification message if no next_action specified
                        console.log('No next_action specified, showing verification message');
                        form.style.display = 'none';
                        const successState = document.getElementById('successState');
                        if (successState) {
                            successState.style.display = 'block';
                            const msg = document.getElementById('successMessage');
                            if (msg) {
                                msg.textContent = `Check your email (${data.email}) to verify your account.`;
                            }
                            const resendContainer = document.getElementById('resendContainer');
                            if (resendContainer) {
                                resendContainer.style.display = 'block';
                            }
                        } else {
                            // Fallback to login if no success element
                            window.location.href = '/login';
                        }
                    }
                } else {
                    // Handle server errors - log full response for debugging
                    // console.log('Server error response:', result);
                    let errorMessage = result.detail || 'Something went wrong. Please try again.';
                    if (response.status === 409) {
                        errorMessage = 'An account with this email already exists. Try logging in instead.';
                    }
                    alert(errorMessage);
                    submitBtn.classList.remove('loading');
                    submitBtn.disabled = false;
                    isSubmitting = false; // Reset flag on error
                }
                
            } catch (error) {
                // console.error('Signup error:', error);
                alert('Network error. Please check your connection and try again.');
                submitBtn.classList.remove('loading');
                submitBtn.disabled = false;
                isSubmitting = false; // Reset flag on error
            }
        });
    }
    
    // Add input animations
    const inputs = document.querySelectorAll('.form-control');
    inputs.forEach(input => {
        input.addEventListener('focus', function() {
            this.parentElement.style.transform = 'scale(1.02)';
            this.parentElement.style.transition = 'transform 0.3s ease';
        });
        
        input.addEventListener('blur', function() {
            this.parentElement.style.transform = 'scale(1)';
        });
    });
});