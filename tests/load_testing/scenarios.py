#!/usr/bin/env python3
"""
🧭 LOCATION: /CORA/tests/load_testing/scenarios.py
🎯 PURPOSE: Predefined load testing scenarios for CORA application
🔗 IMPORTS: json, time
📤 EXPORTS: Test scenarios and configurations
"""

import json
import time
from typing import Dict, List, Any

class LoadTestScenarios:
    """Predefined load testing scenarios for CORA application"""
    
    @staticmethod
    def get_smoke_test_config() -> Dict[str, Any]:
        """Smoke test - basic functionality verification"""
        return {
            "name": "Smoke Test",
            "description": "Basic functionality test with minimal load",
            "users": 5,
            "spawn_rate": 1,
            "run_time": "2m",
            "host": "http://localhost:8000",
            "expected_rps": 10,
            "expected_response_time": 500,  # ms
            "success_criteria": {
                "error_rate": "< 1%",
                "response_time_p95": "< 1000ms",
                "availability": "> 99%"
            }
        }
    
    @staticmethod
    def get_load_test_config() -> Dict[str, Any]:
        """Load test - normal expected load"""
        return {
            "name": "Load Test",
            "description": "Simulate normal beta user load",
            "users": 50,
            "spawn_rate": 5,
            "run_time": "10m",
            "host": "http://localhost:8000",
            "expected_rps": 100,
            "expected_response_time": 200,  # ms
            "success_criteria": {
                "error_rate": "< 2%",
                "response_time_p95": "< 500ms",
                "availability": "> 99%"
            }
        }
    
    @staticmethod
    def get_stress_test_config() -> Dict[str, Any]:
        """Stress test - beyond normal capacity"""
        return {
            "name": "Stress Test",
            "description": "Test system behavior under high load",
            "users": 200,
            "spawn_rate": 10,
            "run_time": "15m",
            "host": "http://localhost:8000",
            "expected_rps": 300,
            "expected_response_time": 1000,  # ms
            "success_criteria": {
                "error_rate": "< 5%",
                "response_time_p95": "< 2000ms",
                "availability": "> 95%"
            }
        }
    
    @staticmethod
    def get_spike_test_config() -> Dict[str, Any]:
        """Spike test - sudden load increase"""
        return {
            "name": "Spike Test",
            "description": "Test system response to sudden load spikes",
            "users": 100,
            "spawn_rate": 50,  # Rapid user spawn
            "run_time": "5m",
            "host": "http://localhost:8000",
            "expected_rps": 200,
            "expected_response_time": 500,  # ms
            "success_criteria": {
                "error_rate": "< 3%",
                "response_time_p95": "< 1000ms",
                "availability": "> 98%"
            }
        }
    
    @staticmethod
    def get_endurance_test_config() -> Dict[str, Any]:
        """Endurance test - sustained load"""
        return {
            "name": "Endurance Test",
            "description": "Test system stability under sustained load",
            "users": 75,
            "spawn_rate": 5,
            "run_time": "30m",
            "host": "http://localhost:8000",
            "expected_rps": 150,
            "expected_response_time": 300,  # ms
            "success_criteria": {
                "error_rate": "< 2%",
                "response_time_p95": "< 800ms",
                "availability": "> 99%"
            }
        }
    
    @staticmethod
    def get_beta_launch_simulation() -> Dict[str, Any]:
        """Simulate expected beta launch load"""
        return {
            "name": "Beta Launch Simulation",
            "description": "Simulate expected load during beta launch",
            "users": 100,
            "spawn_rate": 10,
            "run_time": "20m",
            "host": "http://localhost:8000",
            "expected_rps": 200,
            "expected_response_time": 250,  # ms
            "success_criteria": {
                "error_rate": "< 1%",
                "response_time_p95": "< 500ms",
                "availability": "> 99.5%"
            }
        }

class PerformanceBaselines:
    """Performance baseline definitions for CORA application"""
    
    @staticmethod
    def get_baseline_metrics() -> Dict[str, Any]:
        """Define performance baselines for different endpoints"""
        return {
            "authentication": {
                "login": {"p95": 200, "p99": 500, "max": 1000},
                "register": {"p95": 300, "p99": 800, "max": 1500},
                "refresh": {"p95": 100, "p99": 300, "max": 500}
            },
            "expenses": {
                "list": {"p95": 150, "p99": 400, "max": 800},
                "create": {"p95": 200, "p99": 500, "max": 1000},
                "update": {"p95": 180, "p99": 450, "max": 900},
                "delete": {"p95": 120, "p99": 300, "max": 600},
                "stats": {"p95": 100, "p99": 250, "max": 500},
                "export": {"p95": 500, "p99": 1000, "max": 2000}
            },
            "receipts": {
                "upload": {"p95": 2000, "p99": 5000, "max": 10000},
                "process": {"p95": 3000, "p99": 8000, "max": 15000},
                "stats": {"p95": 150, "p99": 400, "max": 800}
            },
            "dashboard": {
                "overview": {"p95": 300, "p99": 800, "max": 1500},
                "analytics": {"p95": 500, "p99": 1200, "max": 2500}
            },
            "admin": {
                "user_stats": {"p95": 400, "p99": 1000, "max": 2000},
                "system_metrics": {"p95": 200, "p99": 500, "max": 1000}
            }
        }
    
    @staticmethod
    def get_system_baselines() -> Dict[str, Any]:
        """System-level performance baselines"""
        return {
            "memory_usage": {
                "normal": "< 512MB",
                "high": "< 1GB",
                "critical": "> 1GB"
            },
            "cpu_usage": {
                "normal": "< 30%",
                "high": "< 70%",
                "critical": "> 70%"
            },
            "database_connections": {
                "normal": "< 10",
                "high": "< 20",
                "critical": "> 20"
            },
            "error_rate": {
                "normal": "< 1%",
                "high": "< 5%",
                "critical": "> 5%"
            }
        }

class TestDataGenerator:
    """Generate test data for load testing"""
    
    @staticmethod
    def generate_expense_data(count: int = 100) -> List[Dict[str, Any]]:
        """Generate realistic expense data for testing"""
        import random
        from datetime import datetime, timedelta
        
        categories = [
            "Food & Dining", "Transportation", "Office Supplies", 
            "Utilities", "Entertainment", "Travel", "Other"
        ]
        
        vendors = [
            "Starbucks", "Uber", "Amazon", "Office Depot", 
            "Verizon", "Netflix", "Delta Airlines", "Walmart"
        ]
        
        expenses = []
        for i in range(count):
            expense = {
                "amount": round(random.uniform(5.0, 500.0), 2),
                "description": f"Test expense {i+1}",
                "category": random.choice(categories),
                "date": (datetime.now() - timedelta(days=random.randint(0, 30))).strftime("%Y-%m-%d"),
                "vendor": random.choice(vendors)
            }
            expenses.append(expense)
        
        return expenses
    
    @staticmethod
    def generate_user_data(count: int = 50) -> List[Dict[str, Any]]:
        """Generate test user data"""
        import random
        
        users = []
        for i in range(count):
            user = {
                "email": f"loadtestuser{i+1}@test.com",
                "password": "testpassword123",
                "first_name": f"Test{i+1}",
                "last_name": f"User{i+1}"
            }
            users.append(user)
        
        return users

def save_test_results(scenario_name: str, results: Dict[str, Any], output_file: str = None):
    """Save test results to JSON file"""
    if not output_file:
        timestamp = time.strftime("%Y%m%d_%H%M%S")
        output_file = f"load_test_results_{scenario_name}_{timestamp}.json"
    
    results["timestamp"] = time.time()
    results["scenario"] = scenario_name
    
    with open(output_file, 'w') as f:
        json.dump(results, f, indent=2)
    
    print(f"📊 Test results saved to: {output_file}")
    return output_file

def load_test_results(file_path: str) -> Dict[str, Any]:
    """Load test results from JSON file"""
    with open(file_path, 'r') as f:
        return json.load(f)

def compare_with_baseline(results: Dict[str, Any], baseline: Dict[str, Any]) -> Dict[str, Any]:
    """Compare test results with performance baselines"""
    comparison = {
        "passed": True,
        "issues": [],
        "improvements": []
    }
    
    # Compare response times
    for endpoint, metrics in results.get("response_times", {}).items():
        if endpoint in baseline:
            baseline_metrics = baseline[endpoint]
            
            if metrics.get("p95", 0) > baseline_metrics.get("p95", 0):
                comparison["passed"] = False
                comparison["issues"].append(f"{endpoint} P95 response time exceeds baseline")
            
            if metrics.get("p99", 0) > baseline_metrics.get("p99", 0):
                comparison["issues"].append(f"{endpoint} P99 response time exceeds baseline")
    
    # Compare error rates
    error_rate = results.get("error_rate", 0)
    if error_rate > 0.01:  # 1%
        comparison["passed"] = False
        comparison["issues"].append(f"Error rate {error_rate:.2%} exceeds 1% baseline")
    
    return comparison 