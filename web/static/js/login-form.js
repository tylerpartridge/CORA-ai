// Login Form Handler
// console.log('🔧 CORA Login Form Script Loading...');
document.addEventListener('DOMContentLoaded', function() {
    // console.log('🔧 DOM Content Loaded - Looking for login form...');
    const loginForm = document.getElementById('loginForm');
    
    if (!loginForm) {
        // console.error('❌ Login form not found! Checking for form elements...');
        // console.log('Available forms:', document.querySelectorAll('form'));
        // console.log('Available elements with loginForm:', document.querySelectorAll('#loginForm, [id*="login"], [class*="login"]'));
        return;
    }
    
    // console.log('✅ Login form found:', loginForm);
    
    loginForm.addEventListener('submit', async function(e) {
        e.preventDefault();
        
        const email = document.getElementById('email').value;
        const password = document.getElementById('password').value;
        const rememberMe = document.getElementById('rememberMe').checked;
        
        // console.log('Login attempt:', email);
        
        // Demo mode check
        if (email === 'demo@cora.com' && password === 'demo123') {
            // console.log('Demo login detected');
            window.location.href = '/dashboard';
            return;
        }
        
        try {
            const response = await fetch('/api/auth/login', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    email: email,
                    password: password,
                    remember_me: rememberMe
                })
            });
            
            const data = await response.json();
            // console.log('Login response:', data);
            
            if (response.ok) {
                // Store token if needed
                if (data.access_token) {
                    localStorage.setItem('access_token', data.access_token);
                }
                
                // Redirect to dashboard
                window.location.href = '/dashboard';
            } else {
                alert(data.detail || 'Login failed');
            }
            
        } catch (error) {
            // console.error('Login error:', error);
            alert('Network error. Please try again.');
        }
    });
    
    // Clear error states on input - moved from inline script
    document.querySelectorAll('.form-control').forEach(input => {
        input.addEventListener('input', function() {
            this.classList.remove('is-invalid');
        });
    });
});