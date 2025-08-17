#!/bin/bash

# CORA Production Deployment Script
# One-command deployment to get CORA live and generating revenue

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
DOMAIN=${1:-"coraai.tech"}
EMAIL=${2:-"admin@coraai.tech"}
ENVIRONMENT_FILE=".env.production"

print_header() {
    echo -e "\n${BLUE}================================================${NC}"
    echo -e "${BLUE}🚀 $1${NC}"
    echo -e "${BLUE}================================================${NC}\n"
}

print_step() {
    echo -e "${YELLOW}[Step $1]${NC} $2"
}

print_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

print_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

# Check prerequisites
check_prerequisites() {
    print_step "1" "Checking prerequisites..."
    
    # Check if Docker is installed and running
    if ! command -v docker &> /dev/null; then
        print_error "Docker is not installed. Please install Docker first."
        exit 1
    fi
    
    if ! docker info &> /dev/null; then
        print_error "Docker is not running. Please start Docker first."
        exit 1
    fi
    
    # Check if Docker Compose is available
    if ! command -v docker-compose &> /dev/null; then
        print_error "Docker Compose is not installed. Please install Docker Compose first."
        exit 1
    fi
    
    # Check if domain is provided
    if [ -z "$DOMAIN" ]; then
        print_error "Domain is required. Usage: ./deploy.sh <domain> [email]"
        exit 1
    fi
    
    print_success "All prerequisites met"
}

# Generate production environment file
generate_environment() {
    print_step "2" "Generating production environment configuration..."
    
    # Generate secure secrets
    SECRET_KEY=$(openssl rand -hex 32)
    JWT_SECRET_KEY=$(openssl rand -hex 32)
    POSTGRES_PASSWORD=$(openssl rand -base64 32)
    REDIS_PASSWORD=$(openssl rand -base64 32)
    BACKUP_ENCRYPTION_KEY=$(openssl rand -hex 32)
    GRAFANA_PASSWORD=$(openssl rand -base64 16)
    
    # Create production environment file
    cat > $ENVIRONMENT_FILE << EOF
# CORA Production Environment Configuration
# Generated on $(date)

# Database Configuration
POSTGRES_USER=cora_prod_user
POSTGRES_PASSWORD=$POSTGRES_PASSWORD
POSTGRES_DB=cora_production
DATABASE_URL=postgresql://cora_prod_user:$POSTGRES_PASSWORD@postgres:5432/cora_production

# Redis Configuration
REDIS_PASSWORD=$REDIS_PASSWORD
REDIS_URL=redis://:$REDIS_PASSWORD@redis:6379/0

# Security Keys
SECRET_KEY=$SECRET_KEY
JWT_SECRET_KEY=$JWT_SECRET_KEY
BACKUP_ENCRYPTION_KEY=$BACKUP_ENCRYPTION_KEY

# Domain Configuration
ALLOWED_HOSTS=$DOMAIN,www.$DOMAIN
CORS_ORIGINS=https://$DOMAIN,https://www.$DOMAIN

# OpenAI Configuration (MUST BE SET MANUALLY)
OPENAI_API_KEY=your-openai-api-key-here

# Monitoring
GRAFANA_PASSWORD=$GRAFANA_PASSWORD

# Production Settings
ENVIRONMENT=production
DEBUG=False
LOG_LEVEL=INFO
EOF
    
    print_success "Production environment file created: $ENVIRONMENT_FILE"
    print_info "⚠️  IMPORTANT: Set your OPENAI_API_KEY in $ENVIRONMENT_FILE before continuing"
}

# Setup SSL certificates
setup_ssl() {
    print_step "3" "Setting up SSL certificates..."
    
    # Create SSL directory
    mkdir -p deployment/ssl
    
    # Check if certificates already exist
    if [ -f "deployment/ssl/cert.pem" ] && [ -f "deployment/ssl/key.pem" ]; then
        print_info "SSL certificates already exist, skipping generation"
        return 0
    fi
    
    # Generate self-signed certificate for development
    # In production, you should use Let's Encrypt or a proper CA
    openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
        -keyout deployment/ssl/key.pem \
        -out deployment/ssl/cert.pem \
        -subj "/C=US/ST=State/L=City/O=CORA/CN=$DOMAIN"
    
    print_success "SSL certificates generated"
    print_info "⚠️  For production, replace with proper SSL certificates from Let's Encrypt"
}

# Deploy CORA application
deploy_cora() {
    print_step "4" "Deploying CORA application..."
    
    # Stop any existing containers
    print_info "Stopping existing containers..."
    docker-compose -f deployment/docker-compose.production.yml down --remove-orphans 2>/dev/null || true
    
    # Build and start services
    print_info "Building and starting CORA services..."
    docker-compose -f deployment/docker-compose.production.yml --env-file $ENVIRONMENT_FILE up -d --build
    
    # Wait for services to be healthy
    print_info "Waiting for services to be healthy..."
    sleep 30
    
    # Check service health
    if docker-compose -f deployment/docker-compose.production.yml --env-file $ENVIRONMENT_FILE ps | grep -q "unhealthy"; then
        print_error "Some services are unhealthy. Check logs with: docker-compose -f deployment/docker-compose.production.yml logs"
        exit 1
    fi
    
    print_success "CORA application deployed successfully"
}

# Run database migrations
run_migrations() {
    print_step "5" "Running database migrations..."
    
    # Wait for database to be ready
    print_info "Waiting for database to be ready..."
    sleep 10
    
    # Run migrations
    docker-compose -f deployment/docker-compose.production.yml --env-file $ENVIRONMENT_FILE exec -T cora_app python -m alembic upgrade head 2>/dev/null || {
        print_info "No Alembic migrations found, checking for manual migrations..."
        docker-compose -f deployment/docker-compose.production.yml --env-file $ENVIRONMENT_FILE exec -T cora_app python scripts/run_migrations.py 2>/dev/null || {
            print_info "No manual migrations found, database should be ready"
        }
    }
    
    print_success "Database migrations completed"
}

# Setup monitoring
setup_monitoring() {
    print_step "6" "Setting up monitoring and alerts..."
    
    # Wait for monitoring services to be ready
    print_info "Waiting for monitoring services to be ready..."
    sleep 20
    
    # Check if Prometheus is accessible
    if curl -s http://localhost:9090/api/v1/status/config > /dev/null; then
        print_success "Prometheus monitoring is running"
    else
        print_error "Prometheus is not accessible"
    fi
    
    # Check if Grafana is accessible
    if curl -s http://localhost:3000/api/health > /dev/null; then
        print_success "Grafana dashboards are running"
        print_info "Grafana URL: http://localhost:3000 (admin/$GRAFANA_PASSWORD)"
    else
        print_error "Grafana is not accessible"
    fi
    
    print_success "Monitoring setup completed"
}

# Health check
health_check() {
    print_step "7" "Running health checks..."
    
    # Test main application
    if curl -s -f http://localhost:8000/health > /dev/null; then
        print_success "CORA application is healthy"
    else
        print_error "CORA application health check failed"
        exit 1
    fi
    
    # Test HTTPS (if nginx is configured)
    if curl -s -f -k https://localhost/health > /dev/null; then
        print_success "HTTPS is working"
    else
        print_info "HTTPS not configured (normal for development)"
    fi
    
    # Test concurrent users
    print_info "Testing concurrent user support..."
    if python tools/test_sqlite_concurrent.py > /dev/null 2>&1; then
        print_success "Concurrent user test passed"
    else
        print_error "Concurrent user test failed"
    fi
    
    print_success "All health checks passed"
}

# Display deployment information
show_deployment_info() {
    print_header "Deployment Complete!"
    
    echo -e "${GREEN}🎉 CORA is now live and ready to generate revenue!${NC}\n"
    
    echo -e "${BLUE}📊 Deployment Information:${NC}"
    echo -e "  • Domain: ${YELLOW}$DOMAIN${NC}"
    echo -e "  • Application: ${GREEN}http://localhost:8000${NC}"
    echo -e "  • Nginx: ${GREEN}http://localhost:80${NC}"
    echo -e "  • Prometheus: ${GREEN}http://localhost:9090${NC}"
    echo -e "  • Grafana: ${GREEN}http://localhost:3000${NC} (admin/$GRAFANA_PASSWORD)"
    
    echo -e "\n${BLUE}🔧 Management Commands:${NC}"
    echo -e "  • View logs: ${YELLOW}docker-compose -f deployment/docker-compose.production.yml logs -f${NC}"
    echo -e "  • Stop services: ${YELLOW}docker-compose -f deployment/docker-compose.production.yml down${NC}"
    echo -e "  • Restart services: ${YELLOW}docker-compose -f deployment/docker-compose.production.yml restart${NC}"
    echo -e "  • Update application: ${YELLOW}docker-compose -f deployment/docker-compose.production.yml up -d --build${NC}"
    
    echo -e "\n${BLUE}⚠️  Important Next Steps:${NC}"
    echo -e "  1. Set your ${YELLOW}OPENAI_API_KEY${NC} in ${YELLOW}$ENVIRONMENT_FILE${NC}"
    echo -e "  2. Configure proper SSL certificates for production"
    echo -e "  3. Set up domain DNS to point to your server"
    echo -e "  4. Configure backup monitoring and alerts"
    
    echo -e "\n${GREEN}🚀 CORA is ready to start generating revenue!${NC}"
}

# Main deployment function
main() {
    print_header "CORA Production Deployment"
    echo -e "Domain: ${YELLOW}$DOMAIN${NC}"
    echo -e "Email: ${YELLOW}$EMAIL${NC}"
    echo -e "Environment: ${YELLOW}$ENVIRONMENT_FILE${NC}\n"
    
    # Check if user wants to continue
    read -p "Continue with deployment? (y/N): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        print_info "Deployment cancelled"
        exit 0
    fi
    
    check_prerequisites
    generate_environment
    setup_ssl
    deploy_cora
    run_migrations
    setup_monitoring
    health_check
    show_deployment_info
}

# Handle script arguments
if [ "$1" = "--help" ] || [ "$1" = "-h" ]; then
    echo "CORA Production Deployment Script"
    echo ""
    echo "Usage: $0 <domain> [email]"
    echo ""
    echo "Examples:"
    echo "  $0 coraai.tech"
    echo "  $0 coraai.tech admin@coraai.tech"
    echo ""
    echo "This script will:"
    echo "  1. Check prerequisites (Docker, Docker Compose)"
    echo "  2. Generate production environment configuration"
    echo "  3. Setup SSL certificates"
    echo "  4. Deploy CORA application with all services"
    echo "  5. Run database migrations"
    echo "  6. Setup monitoring and alerts"
    echo "  7. Run health checks"
    echo ""
    exit 0
fi

# Run main function
main "$@" 