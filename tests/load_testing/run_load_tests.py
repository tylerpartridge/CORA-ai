#!/usr/bin/env python3
"""
🧭 LOCATION: /CORA/tests/load_testing/run_load_tests.py
🎯 PURPOSE: Load testing runner script for CORA application
🔗 IMPORTS: subprocess, json, time, argparse
📤 EXPORTS: Load test execution and reporting functions
"""

import subprocess
import json
import time
import argparse
import os
import sys
from pathlib import Path
from scenarios import LoadTestScenarios, PerformanceBaselines, save_test_results, compare_with_baseline

class LoadTestRunner:
    """Load testing runner for CORA application"""
    
    def __init__(self, host: str = "http://localhost:8000"):
        self.host = host
        self.results_dir = Path("load_test_results")
        self.results_dir.mkdir(exist_ok=True)
    
    def run_smoke_test(self) -> dict:
        """Run smoke test - basic functionality verification"""
        print("Running Smoke Test...")
        config = LoadTestScenarios.get_smoke_test_config()
        config["host"] = self.host
        
        return self._run_locust_test(config, "smoke")
    
    def run_load_test(self) -> dict:
        """Run load test - normal expected load"""
        print("Running Load Test...")
        config = LoadTestScenarios.get_load_test_config()
        config["host"] = self.host
        
        return self._run_locust_test(config, "load")
    
    def run_stress_test(self) -> dict:
        """Run stress test - beyond normal capacity"""
        print("🔥 Running Stress Test...")
        config = LoadTestScenarios.get_stress_test_config()
        config["host"] = self.host
        
        return self._run_locust_test(config, "stress")
    
    def run_spike_test(self) -> dict:
        """Run spike test - sudden load increase"""
        print("⚡ Running Spike Test...")
        config = LoadTestScenarios.get_spike_test_config()
        config["host"] = self.host
        
        return self._run_locust_test(config, "spike")
    
    def run_endurance_test(self) -> dict:
        """Run endurance test - sustained load"""
        print("⏱️ Running Endurance Test...")
        config = LoadTestScenarios.get_endurance_test_config()
        config["host"] = self.host
        
        return self._run_locust_test(config, "endurance")
    
    def run_beta_launch_simulation(self) -> dict:
        """Run beta launch simulation"""
        print("🎯 Running Beta Launch Simulation...")
        config = LoadTestScenarios.get_beta_launch_simulation()
        config["host"] = self.host
        
        return self._run_locust_test(config, "beta_launch")
    
    def run_all_tests(self) -> dict:
        """Run all load test scenarios"""
        print("🔄 Running All Load Tests...")
        
        results = {
            "timestamp": time.time(),
            "host": self.host,
            "tests": {}
        }
        
        # Run tests in order of increasing load
        test_functions = [
            ("smoke", self.run_smoke_test),
            ("load", self.run_load_test),
            ("stress", self.run_stress_test),
            ("spike", self.run_spike_test),
            ("endurance", self.run_endurance_test),
            ("beta_launch", self.run_beta_launch_simulation)
        ]
        
        for test_name, test_func in test_functions:
            try:
                print(f"\n{'='*50}")
                print(f"Running {test_name.upper()} test...")
                print(f"{'='*50}")
                
                test_result = test_func()
                results["tests"][test_name] = test_result
                
                # Wait between tests
                if test_name != "beta_launch":
                    print("⏳ Waiting 30 seconds before next test...")
                    time.sleep(30)
                    
            except Exception as e:
                print(f"❌ {test_name} test failed: {str(e)}")
                results["tests"][test_name] = {"error": str(e)}
        
        # Save comprehensive results
        timestamp = time.strftime("%Y%m%d_%H%M%S")
        results_file = self.results_dir / f"all_load_tests_{timestamp}.json"
        
        with open(results_file, 'w') as f:
            json.dump(results, f, indent=2)
        
        print(f"\n📊 All test results saved to: {results_file}")
        return results
    
    def _run_locust_test(self, config: dict, test_type: str) -> dict:
        """Run a specific Locust test"""
        # Build Locust command
        cmd = [
            "locust",
            "-f", "locustfile.py",
            "--host", config["host"],
            "--users", str(config["users"]),
            "--spawn-rate", str(config["spawn_rate"]),
            "--run-time", config["run_time"],
            "--headless",  # Run without web UI
            "--json",  # Output JSON results
            "--csv", f"results_{test_type}"  # CSV output
        ]
        
        print(f"Command: {' '.join(cmd)}")
        
        try:
            # Run Locust test
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                cwd=Path(__file__).parent,
                timeout=3600  # 1 hour timeout
            )
            
            if result.returncode != 0:
                print(f"❌ Locust test failed: {result.stderr}")
                return {"error": result.stderr}
            
            # Parse results
            test_results = self._parse_locust_results(test_type, config)
            
            # Save results
            timestamp = time.strftime("%Y%m%d_%H%M%S")
            results_file = self.results_dir / f"{test_type}_test_{timestamp}.json"
            
            with open(results_file, 'w') as f:
                json.dump(test_results, f, indent=2)
            
            print(f"✅ {test_type} test completed successfully")
            print(f"📊 Results saved to: {results_file}")
            
            return test_results
            
        except subprocess.TimeoutExpired:
            print(f"❌ {test_type} test timed out")
            return {"error": "Test timed out"}
        except Exception as e:
            print(f"❌ {test_type} test failed: {str(e)}")
            return {"error": str(e)}
    
    def _parse_locust_results(self, test_type: str, config: dict) -> dict:
        """Parse Locust test results"""
        # This is a simplified parser - in production you'd parse the actual Locust output
        results = {
            "test_type": test_type,
            "config": config,
            "timestamp": time.time(),
            "summary": {
                "total_requests": 0,
                "failed_requests": 0,
                "average_response_time": 0,
                "requests_per_second": 0,
                "p95_response_time": 0,
                "p99_response_time": 0
            },
            "endpoints": {},
            "system_metrics": {
                "memory_usage": "N/A",
                "cpu_usage": "N/A",
                "database_connections": "N/A"
            }
        }
        
        # Try to read CSV results if available
        csv_file = Path(__file__).parent / f"results_{test_type}_stats.csv"
        if csv_file.exists():
            try:
                import pandas as pd
                df = pd.read_csv(csv_file)
                
                # Parse summary statistics
                if not df.empty:
                    results["summary"]["total_requests"] = int(df["num_requests"].sum())
                    results["summary"]["failed_requests"] = int(df["num_failures"].sum())
                    results["summary"]["average_response_time"] = float(df["avg_response_time"].mean())
                    results["summary"]["requests_per_second"] = float(df["current_rps"].mean())
                    
                    # Calculate percentiles
                    response_times = df["response_time"].dropna()
                    if len(response_times) > 0:
                        results["summary"]["p95_response_time"] = float(response_times.quantile(0.95))
                        results["summary"]["p99_response_time"] = float(response_times.quantile(0.99))
                
            except Exception as e:
                print(f"⚠️ Could not parse CSV results: {e}")
        
        return results
    
    def generate_report(self, results: dict) -> str:
        """Generate a human-readable performance report"""
        report = []
        report.append("=" * 60)
        report.append("📊 CORA LOAD TESTING REPORT")
        report.append("=" * 60)
        report.append(f"Host: {results.get('host', 'N/A')}")
        report.append(f"Timestamp: {time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(results.get('timestamp', time.time())))}")
        report.append("")
        
        if "tests" in results:
            # Multiple tests
            for test_name, test_result in results["tests"].items():
                report.append(f"🔍 {test_name.upper()} TEST")
                report.append("-" * 40)
                
                if "error" in test_result:
                    report.append(f"❌ Failed: {test_result['error']}")
                else:
                    summary = test_result.get("summary", {})
                    report.append(f"✅ Total Requests: {summary.get('total_requests', 'N/A')}")
                    report.append(f"❌ Failed Requests: {summary.get('failed_requests', 'N/A')}")
                    report.append(f"⚡ Avg Response Time: {summary.get('average_response_time', 'N/A'):.2f}ms")
                    report.append(f"📈 Requests/sec: {summary.get('requests_per_second', 'N/A'):.2f}")
                    report.append(f"📊 P95 Response Time: {summary.get('p95_response_time', 'N/A'):.2f}ms")
                    report.append(f"📊 P99 Response Time: {summary.get('p99_response_time', 'N/A'):.2f}ms")
                
                report.append("")
        else:
            # Single test
            summary = results.get("summary", {})
            report.append(f"✅ Total Requests: {summary.get('total_requests', 'N/A')}")
            report.append(f"❌ Failed Requests: {summary.get('failed_requests', 'N/A')}")
            report.append(f"⚡ Avg Response Time: {summary.get('average_response_time', 'N/A'):.2f}ms")
            report.append(f"📈 Requests/sec: {summary.get('requests_per_second', 'N/A'):.2f}")
            report.append(f"📊 P95 Response Time: {summary.get('p95_response_time', 'N/A'):.2f}ms")
            report.append(f"📊 P99 Response Time: {summary.get('p99_response_time', 'N/A'):.2f}ms")
        
        report.append("=" * 60)
        
        return "\n".join(report)

def main():
    """Main function for command-line execution"""
    parser = argparse.ArgumentParser(description="Run CORA load tests")
    parser.add_argument("--host", default="http://localhost:8000", help="Target host URL")
    parser.add_argument("--test", choices=["smoke", "load", "stress", "spike", "endurance", "beta_launch", "all"], 
                       default="smoke", help="Test type to run")
    parser.add_argument("--report", action="store_true", help="Generate detailed report")
    
    args = parser.parse_args()
    
    # Check if Locust is installed
    try:
        subprocess.run(["locust", "--version"], capture_output=True, check=True)
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("❌ Locust is not installed. Please install it with: pip install locust")
        sys.exit(1)
    
    # Check if target host is accessible
    try:
        import requests
        response = requests.get(f"{args.host}/health", timeout=5)
        if response.status_code != 200:
            print(f"⚠️ Warning: Target host {args.host} returned status {response.status_code}")
    except Exception as e:
        print(f"⚠️ Warning: Could not reach target host {args.host}: {e}")
    
    # Run tests
    runner = LoadTestRunner(args.host)
    
    if args.test == "all":
        results = runner.run_all_tests()
    elif args.test == "smoke":
        results = runner.run_smoke_test()
    elif args.test == "load":
        results = runner.run_load_test()
    elif args.test == "stress":
        results = runner.run_stress_test()
    elif args.test == "spike":
        results = runner.run_spike_test()
    elif args.test == "endurance":
        results = runner.run_endurance_test()
    elif args.test == "beta_launch":
        results = runner.run_beta_launch_simulation()
    
    # Generate report
    if args.report:
        report = runner.generate_report(results)
        print("\n" + report)
        
        # Save report to file
        timestamp = time.strftime("%Y%m%d_%H%M%S")
        report_file = runner.results_dir / f"load_test_report_{args.test}_{timestamp}.txt"
        
        with open(report_file, 'w') as f:
            f.write(report)
        
        print(f"\n📄 Report saved to: {report_file}")

if __name__ == "__main__":
    main() 