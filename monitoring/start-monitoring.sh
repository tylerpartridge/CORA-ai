#!/bin/bash

# CORA Monitoring Stack Startup Script
# This script starts the complete monitoring stack with Prometheus, Grafana, AlertManager, and Loki

echo "🚀 Starting CORA Monitoring Stack..."

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    echo "❌ Docker is not running. Please start Docker and try again."
    exit 1
fi

# Create logs directory if it doesn't exist
mkdir -p logs

# Start the monitoring stack
echo "📊 Starting monitoring services..."
docker-compose up -d

# Wait for services to start
echo "⏳ Waiting for services to start..."
sleep 10

# Check service status
echo "🔍 Checking service status..."
docker-compose ps

echo ""
echo "✅ CORA Monitoring Stack is running!"
echo ""
echo "📊 Access URLs:"
echo "   Grafana:      http://localhost:3000 (admin/cora2025)"
echo "   Prometheus:   http://localhost:9090"
echo "   AlertManager: http://localhost:9093"
echo "   Loki:         http://localhost:3100"
echo ""
echo "📋 Quick Start:"
echo "   1. Open Grafana: http://localhost:3000"
echo "   2. Login with: admin / cora2025"
echo "   3. Navigate to Dashboards > CORA > CORA Overview"
echo ""
echo "🛑 To stop: docker-compose down"
echo "📝 To view logs: docker-compose logs -f"
echo ""
echo "🎯 Make sure your CORA application is running on port 8000 for metrics collection!" 