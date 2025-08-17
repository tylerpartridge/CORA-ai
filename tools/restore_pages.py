#!/usr/bin/env python3
"""
Restore pages with proper content AND consistent navigation
"""
import os

def restore_signup():
    """Restore the signup page with its original functionality"""
    content = '''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Sign Up - CORA | Start Your Free Trial</title>
    <meta name="description" content="Start your 30-day free trial. Join 500+ contractors saving $12,847/year with CORA.">
    
    <!-- Bootstrap CSS -->
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
    
    <!-- Google Fonts -->
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap" rel="stylesheet">
    
    <!-- Navigation CSS -->
    <link rel="stylesheet" href="/static/css/navigation.css">
    <link rel="stylesheet" href="/static/css/nav-override.css">
    
    <style>
        body {
            font-family: 'Inter', sans-serif;
            background: #1a1a1a;
            color: #e2e8f0;
            padding-top: 80px;
        }
        
        .signup-container {
            max-width: 500px;
            margin: 0 auto;
            padding: 2rem;
        }
        
        .signup-card {
            background: #2d3748;
            border-radius: 8px;
            padding: 2rem;
            box-shadow: 0 4px 20px rgba(0,0,0,0.3);
        }
        
        .form-control {
            background: rgba(26, 26, 26, 0.5);
            border: 1px solid rgba(255, 152, 0, 0.3);
            color: #e2e8f0;
        }
        
        .form-control:focus {
            background: rgba(26, 26, 26, 0.8);
            border-color: #FF9800;
            box-shadow: 0 0 0 3px rgba(255, 152, 0, 0.1);
            color: #e2e8f0;
        }
        
        .btn-signup {
            background: #FF9800;
            color: #1a1a1a;
            font-weight: 700;
            text-transform: uppercase;
            letter-spacing: 0.5px;
            padding: 0.75rem 2rem;
            border: none;
            border-radius: 4px;
            width: 100%;
            transition: all 0.3s ease;
        }
        
        .btn-signup:hover {
            background: #F57C00;
            transform: translateY(-2px);
            box-shadow: 0 6px 20px rgba(255, 152, 0, 0.5);
        }
    </style>
</head>
<body>
    <!-- Navigation -->
    <nav class="navbar navbar-expand-lg navbar-dark" style="background: linear-gradient(180deg, rgba(26, 26, 26, 0.98) 0%, rgba(26, 26, 26, 0.95) 100%); border-bottom: 3px solid #FF9800; position: fixed; width: 100%; top: 0; z-index: 1000;">
        <div class="container">
            <a class="navbar-brand" href="/">
                <img src="/static/images/logos/cora-logo.png" alt="CORA" style="height: 45px;">
            </a>
            
            <button class="navbar-toggler" type="button" data-bs-toggle="collapse" data-bs-target="#navbarNav">
                <span class="navbar-toggler-icon"></span>
            </button>
            
            <div class="collapse navbar-collapse justify-content-end" id="navbarNav">
                <ul class="navbar-nav align-items-center">
                    <li class="nav-item">
                        <a class="nav-link" href="/">Home</a>
                    </li>
                    <li class="nav-item">
                        <a class="nav-link" href="/features">Features</a>
                    </li>
                    <li class="nav-item">
                        <a class="nav-link" href="/how-it-works">How It Works</a>
                    </li>
                    <li class="nav-item">
                        <a class="nav-link" href="/pricing">Pricing</a>
                    </li>
                    <li class="nav-item">
                        <a class="nav-link" href="/blog">Blog</a>
                    </li>
                    <li class="nav-item">
                        <a class="nav-link" href="/reviews">Reviews</a>
                    </li>
                    <li class="nav-item">
                        <a class="nav-link" href="/contact">Contact</a>
                    </li>
                    <li class="nav-item">
                        <a class="nav-link" href="/login">Login</a>
                    </li>
                    <li class="nav-item ms-3">
                        <a class="btn btn-signup" href="/signup">Start Free Trial</a>
                    </li>
                </ul>
            </div>
        </div>
    </nav>

    <!-- Signup Form -->
    <div class="signup-container">
        <div class="signup-card">
            <h1 class="h3 mb-4 text-center" style="color: #FF9800;">Start Your Free Trial</h1>
            <p class="text-center mb-4">Join 500+ contractors already saving time and money</p>
            
            <form id="signupForm" action="/api/auth/register" method="POST">
                <div class="mb-3">
                    <label for="name" class="form-label">Full Name</label>
                    <input type="text" class="form-control" id="name" name="name" required>
                </div>
                
                <div class="mb-3">
                    <label for="email" class="form-label">Email Address</label>
                    <input type="email" class="form-control" id="email" name="email" required>
                </div>
                
                <div class="mb-3">
                    <label for="company" class="form-label">Company Name</label>
                    <input type="text" class="form-control" id="company" name="company" required>
                </div>
                
                <div class="mb-3">
                    <label for="password" class="form-label">Password</label>
                    <input type="password" class="form-control" id="password" name="password" required>
                </div>
                
                <div class="mb-3">
                    <label for="confirmPassword" class="form-label">Confirm Password</label>
                    <input type="password" class="form-control" id="confirmPassword" name="confirmPassword" required>
                </div>
                
                <button type="submit" class="btn btn-signup">Start Free 30-Day Trial</button>
                
                <p class="text-center mt-3 mb-0">
                    Already have an account? <a href="/login" style="color: #FF9800;">Log in</a>
                </p>
            </form>
        </div>
    </div>

    <!-- Bootstrap JS -->
    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js"></script>
    
    <!-- Signup validation -->
    <script>
        document.getElementById('signupForm').addEventListener('submit', function(e) {
            e.preventDefault();
            
            const password = document.getElementById('password').value;
            const confirmPassword = document.getElementById('confirmPassword').value;
            
            if (password !== confirmPassword) {
                alert('Passwords do not match!');
                return;
            }
            
            // Submit the form
            this.submit();
        });
    </script>
</body>
</html>'''
    
    with open(r'C:\CORA\web\templates\signup.html', 'w', encoding='utf-8') as f:
        f.write(content)
    print("Restored signup.html with proper form")

def main():
    print("Restoring pages with proper functionality...")
    restore_signup()
    print("Done! Signup page restored with working form and consistent navigation")

if __name__ == "__main__":
    main()