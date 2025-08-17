#!/usr/bin/env python3
"""
Simple production deployment validation for CORA
Checks system readiness without external dependencies
"""

import os
import json
import sqlite3
from pathlib import Path
from datetime import datetime, timezone

class SimpleDeploymentValidator:
    """Simple deployment validation without external dependencies"""
    
    def __init__(self):
        self.results = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "overall_status": "unknown",
            "readiness_score": 0,
            "critical_issues": [],
            "warnings": [],
            "validations": {}
        }
        
    def run_validation(self):
        """Run deployment validation"""
        print("CORA Production Deployment Validation")
        print("=" * 50)
        
        # Core validations
        self._check_environment()
        self._check_database()
        self._check_files()
        self._check_optimization_files()
        
        # Calculate score
        self._calculate_score()
        self._generate_report()
        
        return self.results
    
    def _check_environment(self):
        """Check environment configuration"""
        print("\nValidating Environment Configuration...")
        
        validation = {"status": "pass", "details": {}, "issues": []}
        
        # Check .env file
        if Path(".env").exists():
            validation["details"]["env_file"] = "Found"
        else:
            validation["status"] = "warning"
            validation["details"]["env_file"] = "Missing"
            validation["issues"].append("No .env file found")
        
        # Check critical variables
        critical_vars = ["OPENAI_API_KEY", "SECRET_KEY", "SENDGRID_API_KEY"]
        for var in critical_vars:
            if os.getenv(var):
                validation["details"][var] = "Configured"
            else:
                validation["details"][var] = "Missing"
                if var == "SECRET_KEY":
                    validation["status"] = "fail"
                    validation["issues"].append(f"Critical: {var} missing")
                else:
                    validation["issues"].append(f"Warning: {var} missing")
        
        self.results["validations"]["environment"] = validation
        print(f"   Status: {validation['status'].upper()}")
    
    def _check_database(self):
        """Check database health"""
        print("\nValidating Database Health...")
        
        validation = {"status": "pass", "details": {}, "issues": []}
        
        db_path = "cora.db"
        if Path(db_path).exists():
            try:
                conn = sqlite3.connect(db_path)
                cursor = conn.cursor()
                
                # Count tables
                cursor.execute("SELECT count(*) FROM sqlite_master WHERE type='table'")
                table_count = cursor.fetchone()[0]
                validation["details"]["tables"] = f"{table_count} tables"
                
                # Count users if table exists
                try:
                    cursor.execute("SELECT COUNT(*) FROM users")
                    user_count = cursor.fetchone()[0]
                    validation["details"]["users"] = f"{user_count} users"
                except:
                    validation["details"]["users"] = "No users table"
                
                # Database size
                db_size_mb = Path(db_path).stat().st_size / (1024 * 1024)
                validation["details"]["size"] = f"{db_size_mb:.2f} MB"
                
                conn.close()
                
                if table_count < 10:
                    validation["status"] = "warning"
                    validation["issues"].append("Low table count")
                    
            except Exception as e:
                validation["status"] = "fail"
                validation["details"]["error"] = str(e)
                validation["issues"].append(f"Database error: {str(e)}")
        else:
            validation["status"] = "fail"
            validation["details"]["database"] = "Missing"
            validation["issues"].append("Database file not found")
        
        self.results["validations"]["database"] = validation
        print(f"   Status: {validation['status'].upper()}")
    
    def _check_files(self):
        """Check critical files and directories"""
        print("\nValidating File System...")
        
        validation = {"status": "pass", "details": {}, "issues": []}
        
        # Critical files
        critical_files = [
            "app.py",
            "routes/auth_coordinator.py",
            "routes/dashboard_routes.py", 
            "routes/expenses.py",
            "services/emotional_intelligence.py"
        ]
        
        for file_path in critical_files:
            if Path(file_path).exists():
                validation["details"][file_path] = "Exists"
            else:
                validation["status"] = "warning" if validation["status"] != "fail" else "fail"
                validation["details"][file_path] = "Missing"
                validation["issues"].append(f"Missing: {file_path}")
        
        # Critical directories
        critical_dirs = ["web/static", "web/templates", "models", "utils"]
        for dir_path in critical_dirs:
            if Path(dir_path).exists():
                validation["details"][dir_path] = "Directory exists"
            else:
                validation["status"] = "warning"
                validation["issues"].append(f"Missing directory: {dir_path}")
        
        self.results["validations"]["files"] = validation
        print(f"   Status: {validation['status'].upper()}")
    
    def _check_optimization_files(self):
        """Check Cursor's optimization work"""
        print("\nValidating Performance Optimizations...")
        
        validation = {"status": "pass", "details": {}, "issues": []}
        
        # Check Cursor's optimization files
        optimization_files = [
            "utils/query_optimizer.py",
            "utils/materialized_views.py",
            "utils/performance_monitor.py",
            "utils/validation.py"
        ]
        
        found_count = 0
        for file_path in optimization_files:
            if Path(file_path).exists():
                validation["details"][file_path] = "Implemented"
                found_count += 1
            else:
                validation["details"][file_path] = "Missing"
        
        validation["details"]["optimization_coverage"] = f"{found_count}/{len(optimization_files)} files"
        
        if found_count == len(optimization_files):
            validation["details"]["status"] = "All optimizations present"
        elif found_count >= len(optimization_files) * 0.75:
            validation["status"] = "warning"
            validation["issues"].append("Some optimization files missing")
        else:
            validation["status"] = "fail"
            validation["issues"].append("Most optimization files missing")
        
        self.results["validations"]["optimizations"] = validation
        print(f"   Status: {validation['status'].upper()}")
    
    def _calculate_score(self):
        """Calculate readiness score"""
        total = len(self.results["validations"])
        passed = sum(1 for v in self.results["validations"].values() if v["status"] == "pass")
        failed = sum(1 for v in self.results["validations"].values() if v["status"] == "fail")
        
        # Collect issues
        for validation in self.results["validations"].values():
            if validation["status"] == "fail":
                self.results["critical_issues"].extend(validation["issues"])
            elif validation["status"] == "warning":
                self.results["warnings"].extend(validation["issues"])
        
        # Calculate score
        base_score = (passed / total) * 100
        penalty = failed * 20
        self.results["readiness_score"] = max(0, base_score - penalty)
        
        # Overall status
        if failed > 0:
            self.results["overall_status"] = "not_ready"
        elif len(self.results["warnings"]) > 2:
            self.results["overall_status"] = "ready_with_warnings"
        else:
            self.results["overall_status"] = "ready"
    
    def _generate_report(self):
        """Generate final report"""
        print("\n" + "=" * 50)
        print("DEPLOYMENT READINESS REPORT")
        print("=" * 50)
        
        score = self.results["readiness_score"]
        status = self.results["overall_status"]
        
        if status == "ready":
            print(f"\nOverall Status: READY FOR DEPLOYMENT")
        elif status == "ready_with_warnings":
            print(f"\nOverall Status: READY WITH WARNINGS")
        else:
            print(f"\nOverall Status: NOT READY FOR DEPLOYMENT")
        
        print(f"Readiness Score: {score:.1f}/100")
        
        if self.results["critical_issues"]:
            print(f"\nCritical Issues ({len(self.results['critical_issues'])}):")
            for issue in self.results["critical_issues"]:
                print(f"   - {issue}")
        
        if self.results["warnings"]:
            print(f"\nWarnings ({len(self.results['warnings'])}):")
            for warning in self.results["warnings"][:5]:
                print(f"   - {warning}")
        
        print(f"\nRecommendations:")
        if score >= 90:
            print("   - System is production-ready!")
        elif score >= 75:
            print("   - Address warnings for optimal deployment")
        else:
            print("   - Fix critical issues before deployment")

def main():
    """Run validation"""
    validator = SimpleDeploymentValidator()
    results = validator.run_validation()
    
    # Save results
    with open("deployment_validation_report.json", "w") as f:
        json.dump(results, f, indent=2)
    
    print(f"\nFull report saved to: deployment_validation_report.json")
    return results

if __name__ == "__main__":
    main()