#!/bin/bash
# PostgreSQL Deployment Script for CORA
# This script guides through the PostgreSQL migration process

set -e  # Exit on error

echo "🗄️ CORA PostgreSQL Deployment Script"
echo "===================================="
echo ""

# Color codes for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${GREEN}✓${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}⚠${NC} $1"
}

print_error() {
    echo -e "${RED}✗${NC} $1"
}

# Check if we're using DigitalOcean or local PostgreSQL
echo "Select PostgreSQL deployment option:"
echo "1) DigitalOcean Managed Database (Recommended for production)"
echo "2) Docker PostgreSQL (For local testing)"
echo "3) Existing PostgreSQL instance"
read -p "Enter choice (1-3): " DEPLOY_CHOICE

case $DEPLOY_CHOICE in
    1)
        echo ""
        echo "📋 DigitalOcean Managed Database Setup"
        echo "======================================"
        echo ""
        echo "Please create a PostgreSQL database in DigitalOcean Console:"
        echo ""
        echo "1. Go to: https://cloud.digitalocean.com/databases"
        echo "2. Click 'Create Database Cluster'"
        echo "3. Configure:"
        echo "   - Engine: PostgreSQL 15"
        echo "   - Region: nyc1 (same as your droplet)"
        echo "   - Size: Basic (2 vCPU, 4GB RAM) - \$60/month"
        echo "   - Database name: cora_production"
        echo ""
        echo "Once created, you'll get connection details."
        echo ""
        read -p "Press Enter when database is created..."
        
        # Get connection details
        read -p "Enter DATABASE_URL from DigitalOcean: " DATABASE_URL
        export DATABASE_URL
        ;;
        
    2)
        echo ""
        echo "🐳 Setting up local PostgreSQL with Docker"
        echo ""
        
        # Check if Docker is installed
        if ! command -v docker &> /dev/null; then
            print_error "Docker is not installed. Please install Docker first."
            exit 1
        fi
        
        # Create docker-compose for PostgreSQL
        cat > docker-compose.postgres.yml << EOF
version: '3.8'

services:
  postgres:
    image: postgres:15-alpine
    container_name: cora_postgres
    environment:
      POSTGRES_DB: cora_db
      POSTGRES_USER: cora_user
      POSTGRES_PASSWORD: cora_secure_password_2025
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data
      - ./schema:/docker-entrypoint-initdb.d
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U cora_user -d cora_db"]
      interval: 5s
      timeout: 5s
      retries: 5

volumes:
  postgres_data:
EOF
        
        print_status "Docker compose file created"
        
        # Start PostgreSQL
        docker-compose -f docker-compose.postgres.yml up -d
        
        # Wait for PostgreSQL to be ready
        echo "Waiting for PostgreSQL to start..."
        sleep 10
        
        DATABASE_URL="postgresql://cora_user:cora_secure_password_2025@localhost:5432/cora_db?sslmode=disable"
        export DATABASE_URL
        print_status "Local PostgreSQL started"
        ;;
        
    3)
        echo ""
        read -p "Enter your PostgreSQL DATABASE_URL: " DATABASE_URL
        export DATABASE_URL
        ;;
esac

# Test database connection
echo ""
echo "🔌 Testing database connection..."
if psql "$DATABASE_URL" -c "SELECT 1;" > /dev/null 2>&1; then
    print_status "Database connection successful"
else
    print_error "Failed to connect to database. Please check your DATABASE_URL"
    exit 1
fi

# Apply schema
echo ""
echo "📊 Applying PostgreSQL schema..."
if [ -f "schema/postgresql_schema.sql" ]; then
    if psql "$DATABASE_URL" -f schema/postgresql_schema.sql; then
        print_status "Schema applied successfully"
    else
        print_error "Failed to apply schema"
        exit 1
    fi
else
    print_error "Schema file not found: schema/postgresql_schema.sql"
    exit 1
fi

# Import data
echo ""
echo "📥 Importing data from SQLite..."
if [ -f "postgres_data.sql" ]; then
    if psql "$DATABASE_URL" -f postgres_data.sql; then
        print_status "Data imported successfully"
    else
        print_error "Failed to import data"
        exit 1
    fi
else
    print_warning "Data file not found: postgres_data.sql"
    echo "Skipping data import..."
fi

# Verify migration
echo ""
echo "✅ Verifying migration..."
echo ""
echo "Database tables:"
psql "$DATABASE_URL" -c "\dt"
echo ""
echo "Row counts:"
psql "$DATABASE_URL" -c "SELECT 'users' as table_name, COUNT(*) as count FROM users UNION ALL SELECT 'expenses', COUNT(*) FROM expenses UNION ALL SELECT 'expense_categories', COUNT(*) FROM expense_categories;"

# Update environment configuration
echo ""
echo "🔧 Updating environment configuration..."
echo ""
echo "Add these to your .env file:"
echo "=============================="
echo "DATABASE_URL=$DATABASE_URL"
echo "DATABASE_POOL_SIZE=20"
echo "DATABASE_MAX_OVERFLOW=30"
echo "DATABASE_POOL_TIMEOUT=30"
echo "DATABASE_POOL_RECYCLE=3600"
echo "=============================="
echo ""

# Create .env.postgres template
cat > .env.postgres << EOF
# PostgreSQL Configuration
DATABASE_URL=$DATABASE_URL
DATABASE_POOL_SIZE=20
DATABASE_MAX_OVERFLOW=30
DATABASE_POOL_TIMEOUT=30
DATABASE_POOL_RECYCLE=3600

# Copy other variables from your existing .env
EOF

print_status "Environment template created: .env.postgres"

# Final instructions
echo ""
echo "🚀 PostgreSQL migration complete!"
echo ""
echo "Next steps:"
echo "1. Update your .env file with the PostgreSQL configuration above"
echo "2. Restart your application: pm2 restart cora"
echo "3. Test the application: curl http://localhost:8000/api/health/detailed"
echo "4. Run load tests to verify performance"
echo ""
echo "Rollback instructions:"
echo "- To rollback, update DATABASE_URL back to SQLite and restart"
echo ""

# Offer to run quick test
read -p "Would you like to test the application now? (y/n): " TEST_NOW
if [ "$TEST_NOW" = "y" ]; then
    echo ""
    echo "Starting CORA with PostgreSQL..."
    export $(cat .env.postgres | xargs)
    python -m uvicorn app:app --reload --port 8000 &
    APP_PID=$!
    
    sleep 5
    
    echo ""
    echo "Testing health endpoint..."
    curl -s http://localhost:8000/api/health/detailed | python -m json.tool
    
    echo ""
    echo "Testing categories endpoint..."
    curl -s http://localhost:8000/api/expenses/categories | python -m json.tool
    
    # Stop the test server
    kill $APP_PID 2>/dev/null
    
    echo ""
    print_status "Test complete!"
fi

echo ""
echo "✨ PostgreSQL deployment script finished!"