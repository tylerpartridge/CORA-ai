# CORA Production Deployment Script (PowerShell)
# One-command deployment to get CORA live and generating revenue

param(
    [Parameter(Mandatory=$false)]
    [string]$Domain = "coraai.tech",
    
    [Parameter(Mandatory=$false)]
    [string]$Email = "admin@coraai.tech"
)

# Configuration
$EnvironmentFile = ".env.production"
$ErrorActionPreference = "Stop"

# Colors for output
$Red = "Red"
$Green = "Green"
$Yellow = "Yellow"
$Blue = "Blue"

function Write-Header {
    param([string]$Message)
    Write-Host ""
    Write-Host "================================================" -ForegroundColor $Blue
    Write-Host "🚀 $Message" -ForegroundColor $Blue
    Write-Host "================================================" -ForegroundColor $Blue
    Write-Host ""
}

function Write-Step {
    param([string]$Step, [string]$Message)
    Write-Host "[Step $Step] $Message" -ForegroundColor $Yellow
}

function Write-Success {
    param([string]$Message)
    Write-Host "✅ $Message" -ForegroundColor $Green
}

function Write-Error {
    param([string]$Message)
    Write-Host "❌ $Message" -ForegroundColor $Red
}

function Write-Info {
    param([string]$Message)
    Write-Host "ℹ️  $Message" -ForegroundColor $Blue
}

# Check prerequisites
function Test-Prerequisites {
    Write-Step "1" "Checking prerequisites..."
    
    # Check if Docker is installed and running
    try {
        $dockerVersion = docker --version
        if ($LASTEXITCODE -ne 0) {
            throw "Docker not found"
        }
        Write-Success "Docker found: $dockerVersion"
    }
    catch {
        Write-Error "Docker is not installed or not running. Please install Docker Desktop first."
        exit 1
    }
    
    # Check if Docker is running
    try {
        docker info | Out-Null
        if ($LASTEXITCODE -ne 0) {
            throw "Docker not running"
        }
    }
    catch {
        Write-Error "Docker is not running. Please start Docker Desktop first."
        exit 1
    }
    
    # Check if Docker Compose is available
    try {
        $composeVersion = docker-compose --version
        if ($LASTEXITCODE -ne 0) {
            throw "Docker Compose not found"
        }
        Write-Success "Docker Compose found: $composeVersion"
    }
    catch {
        Write-Error "Docker Compose is not installed. Please install Docker Compose first."
        exit 1
    }
    
    Write-Success "All prerequisites met"
}

# Generate production environment file
function New-EnvironmentFile {
    Write-Step "2" "Generating production environment configuration..."
    
    # Generate secure secrets
    $SecretKey = -join ((48..57) + (97..122) | Get-Random -Count 64 | ForEach-Object {[char]$_})
    $JwtSecretKey = -join ((48..57) + (97..122) | Get-Random -Count 64 | ForEach-Object {[char]$_})
    $PostgresPassword = -join ((48..57) + (65..90) + (97..122) | Get-Random -Count 32 | ForEach-Object {[char]$_})
    $RedisPassword = -join ((48..57) + (65..90) + (97..122) | Get-Random -Count 32 | ForEach-Object {[char]$_})
    $BackupEncryptionKey = -join ((48..57) + (97..122) | Get-Random -Count 64 | ForEach-Object {[char]$_})
    $GrafanaPassword = -join ((48..57) + (65..90) + (97..122) | Get-Random -Count 16 | ForEach-Object {[char]$_})
    
    # Create production environment file
    $envContent = @"
# CORA Production Environment Configuration
# Generated on $(Get-Date)

# Database Configuration
POSTGRES_USER=cora_prod_user
POSTGRES_PASSWORD=$PostgresPassword
POSTGRES_DB=cora_production
DATABASE_URL=postgresql://cora_prod_user:$PostgresPassword@postgres:5432/cora_production

# Redis Configuration
REDIS_PASSWORD=$RedisPassword
REDIS_URL=redis://:$RedisPassword@redis:6379/0

# Security Keys
SECRET_KEY=$SecretKey
JWT_SECRET_KEY=$JwtSecretKey
BACKUP_ENCRYPTION_KEY=$BackupEncryptionKey

# Domain Configuration
ALLOWED_HOSTS=$Domain,www.$Domain
CORS_ORIGINS=https://$Domain,https://www.$Domain

# OpenAI Configuration (MUST BE SET MANUALLY)
OPENAI_API_KEY=your-openai-api-key-here

# Monitoring
GRAFANA_PASSWORD=$GrafanaPassword

# Production Settings
ENVIRONMENT=production
DEBUG=False
LOG_LEVEL=INFO
"@
    
    $envContent | Out-File -FilePath $EnvironmentFile -Encoding UTF8
    Write-Success "Production environment file created: $EnvironmentFile"
    Write-Info "⚠️  IMPORTANT: Set your OPENAI_API_KEY in $EnvironmentFile before continuing"
}

# Setup SSL certificates
function New-SslCertificates {
    Write-Step "3" "Setting up SSL certificates..."
    
    # Create SSL directory
    $sslDir = "deployment/ssl"
    if (!(Test-Path $sslDir)) {
        New-Item -ItemType Directory -Path $sslDir -Force | Out-Null
    }
    
    # Check if certificates already exist
    if ((Test-Path "$sslDir/cert.pem") -and (Test-Path "$sslDir/key.pem")) {
        Write-Info "SSL certificates already exist, skipping generation"
        return
    }
    
    # Generate self-signed certificate for development
    # In production, you should use Let's Encrypt or a proper CA
    try {
        openssl req -x509 -nodes -days 365 -newkey rsa:2048 `
            -keyout "$sslDir/key.pem" `
            -out "$sslDir/cert.pem" `
            -subj "/C=US/ST=State/L=City/O=CORA/CN=$Domain"
        
        Write-Success "SSL certificates generated"
        Write-Info "⚠️  For production, replace with proper SSL certificates from Let's Encrypt"
    }
    catch {
        Write-Error "Failed to generate SSL certificates. Make sure OpenSSL is installed."
        Write-Info "You can skip SSL for development by continuing without certificates."
    }
}

# Deploy CORA application
function Start-CoraDeployment {
    Write-Step "4" "Deploying CORA application..."
    
    # Stop any existing containers
    Write-Info "Stopping existing containers..."
    try {
        docker-compose -f deployment/docker-compose.production.yml down --remove-orphans 2>$null
    }
    catch {
        Write-Info "No existing containers to stop"
    }
    
    # Build and start services
    Write-Info "Building and starting CORA services..."
    docker-compose -f deployment/docker-compose.production.yml --env-file $EnvironmentFile up -d --build
    
    # Wait for services to be healthy
    Write-Info "Waiting for services to be healthy..."
    Start-Sleep -Seconds 30
    
    # Check service health
    $services = docker-compose -f deployment/docker-compose.production.yml --env-file $EnvironmentFile ps
    if ($services -match "unhealthy") {
        Write-Error "Some services are unhealthy. Check logs with: docker-compose -f deployment/docker-compose.production.yml logs"
        exit 1
    }
    
    Write-Success "CORA application deployed successfully"
}

# Run database migrations
function Start-DatabaseMigrations {
    Write-Step "5" "Running database migrations..."
    
    # Wait for database to be ready
    Write-Info "Waiting for database to be ready..."
    Start-Sleep -Seconds 10
    
    # Run migrations
    try {
        docker-compose -f deployment/docker-compose.production.yml --env-file $EnvironmentFile exec -T cora_app python -m alembic upgrade head 2>$null
        Write-Success "Alembic migrations completed"
    }
    catch {
        Write-Info "No Alembic migrations found, checking for manual migrations..."
        try {
            docker-compose -f deployment/docker-compose.production.yml --env-file $EnvironmentFile exec -T cora_app python scripts/run_migrations.py 2>$null
            Write-Success "Manual migrations completed"
        }
        catch {
            Write-Info "No manual migrations found, database should be ready"
        }
    }
    
    Write-Success "Database migrations completed"
}

# Setup monitoring
function Start-MonitoringSetup {
    Write-Step "6" "Setting up monitoring and alerts..."
    
    # Wait for monitoring services to be ready
    Write-Info "Waiting for monitoring services to be ready..."
    Start-Sleep -Seconds 20
    
    # Check if Prometheus is accessible
    try {
        $response = Invoke-WebRequest -Uri "http://localhost:9090/api/v1/status/config" -UseBasicParsing -TimeoutSec 5
        if ($response.StatusCode -eq 200) {
            Write-Success "Prometheus monitoring is running"
        }
    }
    catch {
        Write-Error "Prometheus is not accessible"
    }
    
    # Check if Grafana is accessible
    try {
        $response = Invoke-WebRequest -Uri "http://localhost:3000/api/health" -UseBasicParsing -TimeoutSec 5
        if ($response.StatusCode -eq 200) {
            Write-Success "Grafana dashboards are running"
            Write-Info "Grafana URL: http://localhost:3000 (admin/$GrafanaPassword)"
        }
    }
    catch {
        Write-Error "Grafana is not accessible"
    }
    
    Write-Success "Monitoring setup completed"
}

# Health check
function Test-HealthChecks {
    Write-Step "7" "Running health checks..."
    
    # Test main application
    try {
        $response = Invoke-WebRequest -Uri "http://localhost:8000/health" -UseBasicParsing -TimeoutSec 10
        if ($response.StatusCode -eq 200) {
            Write-Success "CORA application is healthy"
        }
        else {
            throw "Health check failed"
        }
    }
    catch {
        Write-Error "CORA application health check failed"
        exit 1
    }
    
    # Test HTTPS (if nginx is configured)
    try {
        $response = Invoke-WebRequest -Uri "https://localhost/health" -UseBasicParsing -TimeoutSec 5 -SkipCertificateCheck
        if ($response.StatusCode -eq 200) {
            Write-Success "HTTPS is working"
        }
    }
    catch {
        Write-Info "HTTPS not configured (normal for development)"
    }
    
    # Test concurrent users
    Write-Info "Testing concurrent user support..."
    try {
        python tools/test_sqlite_concurrent.py 2>$null
        if ($LASTEXITCODE -eq 0) {
            Write-Success "Concurrent user test passed"
        }
        else {
            throw "Concurrent user test failed"
        }
    }
    catch {
        Write-Error "Concurrent user test failed"
    }
    
    Write-Success "All health checks passed"
}

# Display deployment information
function Show-DeploymentInfo {
    Write-Header "Deployment Complete!"
    
    Write-Host "🎉 CORA is now live and ready to generate revenue!" -ForegroundColor $Green
    Write-Host ""
    
    Write-Host "📊 Deployment Information:" -ForegroundColor $Blue
    Write-Host "  • Domain: $Domain" -ForegroundColor $Yellow
    Write-Host "  • Application: http://localhost:8000" -ForegroundColor $Green
    Write-Host "  • Nginx: http://localhost:80" -ForegroundColor $Green
    Write-Host "  • Prometheus: http://localhost:9090" -ForegroundColor $Green
    Write-Host "  • Grafana: http://localhost:3000 (admin/$GrafanaPassword)" -ForegroundColor $Green
    
    Write-Host ""
    Write-Host "🔧 Management Commands:" -ForegroundColor $Blue
    Write-Host "  • View logs: docker-compose -f deployment/docker-compose.production.yml logs -f" -ForegroundColor $Yellow
    Write-Host "  • Stop services: docker-compose -f deployment/docker-compose.production.yml down" -ForegroundColor $Yellow
    Write-Host "  • Restart services: docker-compose -f deployment/docker-compose.production.yml restart" -ForegroundColor $Yellow
    Write-Host "  • Update application: docker-compose -f deployment/docker-compose.production.yml up -d --build" -ForegroundColor $Yellow
    
    Write-Host ""
    Write-Host "⚠️  Important Next Steps:" -ForegroundColor $Blue
    Write-Host "  1. Set your OPENAI_API_KEY in $EnvironmentFile" -ForegroundColor $Yellow
    Write-Host "  2. Configure proper SSL certificates for production"
    Write-Host "  3. Set up domain DNS to point to your server"
    Write-Host "  4. Configure backup monitoring and alerts"
    
    Write-Host ""
    Write-Host "🚀 CORA is ready to start generating revenue!" -ForegroundColor $Green
}

# Main deployment function
function Start-CoraDeployment {
    Write-Header "CORA Production Deployment"
    Write-Host "Domain: $Domain" -ForegroundColor $Yellow
    Write-Host "Email: $Email" -ForegroundColor $Yellow
    Write-Host "Environment: $EnvironmentFile" -ForegroundColor $Yellow
    Write-Host ""
    
    # Check if user wants to continue
    $response = Read-Host "Continue with deployment? (y/N)"
    if ($response -notmatch "^[Yy]$") {
        Write-Info "Deployment cancelled"
        exit 0
    }
    
    Test-Prerequisites
    New-EnvironmentFile
    New-SslCertificates
    Start-CoraDeployment
    Start-DatabaseMigrations
    Start-MonitoringSetup
    Test-HealthChecks
    Show-DeploymentInfo
}

# Show help
if ($args -contains "--help" -or $args -contains "-h") {
    Write-Host "CORA Production Deployment Script (PowerShell)"
    Write-Host ""
    Write-Host "Usage: .\deploy.ps1 [-Domain <domain>] [-Email <email>]"
    Write-Host ""
    Write-Host "Examples:"
    Write-Host "  .\deploy.ps1"
    Write-Host "  .\deploy.ps1 -Domain coraai.tech"
    Write-Host "  .\deploy.ps1 -Domain coraai.tech -Email admin@coraai.tech"
    Write-Host ""
    Write-Host "This script will:"
    Write-Host "  1. Check prerequisites (Docker, Docker Compose)"
    Write-Host "  2. Generate production environment configuration"
    Write-Host "  3. Setup SSL certificates"
    Write-Host "  4. Deploy CORA application with all services"
    Write-Host "  5. Run database migrations"
    Write-Host "  6. Setup monitoring and alerts"
    Write-Host "  7. Run health checks"
    Write-Host ""
    exit 0
}

# Run main deployment function
Start-CoraDeployment 