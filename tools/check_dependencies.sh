#!/bin/bash
# Quick dependency check and fix for CORA

echo "🔍 CORA Dependency Check"
echo "Server: 159.203.183.48"
echo "========================"

# SSH into server and run checks
ssh root@159.203.183.48 << 'EOF'
cd /var/www/cora/

echo -e "\n📋 Checking Python version..."
python --version

echo -e "\n📦 Checking key dependencies..."
pip list | grep -E "fastapi|uvicorn|pydantic|starlette" || echo "❌ Missing core dependencies!"

echo -e "\n📄 Checking if requirements.txt exists..."
if [ -f requirements.txt ]; then
    echo "✅ requirements.txt found"
    echo "Installing all dependencies..."
    pip install -r requirements.txt
else
    echo "❌ requirements.txt not found!"
    echo "Installing core dependencies manually..."
    pip install fastapi uvicorn pydantic python-multipart python-jose passlib bcrypt sqlalchemy starlette
fi

echo -e "\n🔍 Testing imports..."
python -c "
try:
    import fastapi
    import uvicorn
    from middleware.security_headers import setup_security_headers
    print('✅ All imports successful!')
except ImportError as e:
    print(f'❌ Import error: {e}')
"

echo -e "\n🔄 Restarting application..."
pm2 restart cora
sleep 3
pm2 status

echo -e "\n📊 Recent logs..."
pm2 logs cora --lines 20 --nostream
EOF

echo -e "\n✅ Dependency check complete!"