#!/bin/bash

# CORA Test Runner Script
# Comprehensive test execution with coverage reporting

echo "🧪 CORA Test Suite Runner"
echo "========================="
echo ""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check if pytest is installed
if ! command -v pytest &> /dev/null; then
    echo -e "${RED}❌ pytest is not installed${NC}"
    echo "Installing test dependencies..."
    pip install pytest pytest-cov pytest-asyncio pytest-mock httpx
fi

# Install missing test dependencies if needed
echo "📦 Checking test dependencies..."
pip install -q coverage pytest-cov pytest-html 2>/dev/null

# Run different test suites based on argument
case "$1" in
    "unit")
        echo -e "${YELLOW}Running Unit Tests...${NC}"
        pytest tests/ -m unit -v
        ;;
    
    "integration")
        echo -e "${YELLOW}Running Integration Tests...${NC}"
        pytest tests/ -m integration -v
        ;;
    
    "auth")
        echo -e "${YELLOW}Running Authentication Tests...${NC}"
        pytest tests/test_auth.py -v
        ;;
    
    "security")
        echo -e "${YELLOW}Running Security Tests...${NC}"
        pytest tests/ -m security -v
        ;;
    
    "database")
        echo -e "${YELLOW}Running Database Tests...${NC}"
        pytest tests/ -m database -v
        ;;
    
    "coverage")
        echo -e "${YELLOW}Running All Tests with Coverage...${NC}"
        pytest tests/ --cov=. --cov-report=term-missing --cov-report=html
        echo ""
        echo -e "${GREEN}✅ Coverage report generated in htmlcov/index.html${NC}"
        ;;
    
    "smoke")
        echo -e "${YELLOW}Running Smoke Tests (Quick)...${NC}"
        pytest tests/ -m smoke -v --maxfail=1
        ;;
    
    "all")
        echo -e "${YELLOW}Running All Tests...${NC}"
        pytest tests/ -v
        ;;
    
    "verbose")
        echo -e "${YELLOW}Running All Tests (Verbose with Coverage)...${NC}"
        pytest tests/ -vv --tb=long --cov=. --cov-report=term-missing
        ;;
    
    "failed")
        echo -e "${YELLOW}Re-running Failed Tests...${NC}"
        pytest tests/ --lf -v
        ;;
    
    "parallel")
        echo -e "${YELLOW}Running Tests in Parallel...${NC}"
        # Install pytest-xdist if not present
        pip install -q pytest-xdist 2>/dev/null
        pytest tests/ -n auto -v
        ;;
    
    "report")
        echo -e "${YELLOW}Generating HTML Test Report...${NC}"
        pytest tests/ --html=test_report.html --self-contained-html
        echo -e "${GREEN}✅ Report generated: test_report.html${NC}"
        ;;
    
    *)
        echo "Usage: $0 [option]"
        echo ""
        echo "Options:"
        echo "  unit        - Run unit tests only"
        echo "  integration - Run integration tests only"
        echo "  auth        - Run authentication tests"
        echo "  security    - Run security tests"
        echo "  database    - Run database tests"
        echo "  coverage    - Run all tests with coverage report"
        echo "  smoke       - Run quick smoke tests"
        echo "  all         - Run all tests"
        echo "  verbose     - Run all tests with detailed output"
        echo "  failed      - Re-run only failed tests"
        echo "  parallel    - Run tests in parallel"
        echo "  report      - Generate HTML test report"
        echo ""
        echo "Default: Running all tests with coverage..."
        echo ""
        pytest tests/ --cov=. --cov-report=term-missing
        ;;
esac

# Check exit code
if [ $? -eq 0 ]; then
    echo ""
    echo -e "${GREEN}✅ Tests completed successfully!${NC}"
else
    echo ""
    echo -e "${RED}❌ Some tests failed!${NC}"
    exit 1
fi