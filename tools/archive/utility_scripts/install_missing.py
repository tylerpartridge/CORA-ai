#!/usr/bin/env python3
"""
Install missing dependencies for CORA
"""

import subprocess
import sys

def install_package(package):
    """Install a package using pip"""
    subprocess.check_call([sys.executable, "-m", "pip", "install", package])

def main():
    """Install all missing packages"""
    packages = [
        "slowapi",  # For rate limiting
        "python-multipart",  # For form data
        "requests",  # For API testing
    ]
    
    print("Installing missing packages for CORA...")
    
    for package in packages:
        try:
            print(f"Installing {package}...")
            install_package(package)
            print(f"[OK] {package} installed")
        except Exception as e:
            print(f"[ERROR] Failed to install {package}: {e}")
    
    print("\nInstallation complete!")
    print("You can now run: python app.py")

if __name__ == "__main__":
    main()