#!/usr/bin/env python3
import os

PRODUCTION_IP = "159.203.183.48"

print("Copying utils directory and finalizing deployment...")
print("=" * 50)

# Copy utils directory
print("\n1. Copying utils directory...")
os.system(f'scp -r utils/ root@{PRODUCTION_IP}:/var/www/cora/')

# Copy models directory (just to be sure)
print("\n2. Copying models directory...")
os.system(f'scp -r models/ root@{PRODUCTION_IP}:/var/www/cora/')

# Copy routes directory
print("\n3. Copying routes directory...")
os.system(f'scp -r routes/ root@{PRODUCTION_IP}:/var/www/cora/')

# Copy services directory
print("\n4. Copying services directory...")
os.system(f'scp -r services/ root@{PRODUCTION_IP}:/var/www/cora/')

# Copy dependencies directory
print("\n5. Copying dependencies directory...")
os.system(f'scp -r dependencies/ root@{PRODUCTION_IP}:/var/www/cora/')

# Ensure all __init__.py files exist
print("\n6. Creating __init__.py files...")
dirs = ['utils', 'models', 'routes', 'services', 'dependencies', 'middleware']
for d in dirs:
    os.system(f'ssh root@{PRODUCTION_IP} "touch /var/www/cora/{d}/__init__.py"')

# Restart app
print("\n7. Restarting app...")
os.system(f'ssh root@{PRODUCTION_IP} "pm2 restart cora"')

# Wait
print("\n8. Waiting for startup...")
os.system('timeout 5')

# Test
print("\n9. Testing health endpoint...")
os.system(f'ssh root@{PRODUCTION_IP} "curl -s http://localhost:8000/health"')

# Check PM2 status
print("\n10. PM2 Status...")
os.system(f'ssh root@{PRODUCTION_IP} "pm2 list"')

# Test public URL
print("\n11. Testing public URL...")
os.system(f'ssh root@{PRODUCTION_IP} "curl -I https://coraai.tech | head -5"')

print("\n" + "=" * 50)
print("DEPLOYMENT COMPLETE!")
print("All directories copied. App should be running now.")
print("Test at: https://coraai.tech")
print("=" * 50)