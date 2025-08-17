#!/usr/bin/env python3
"""
Environment Configuration Analyzer for CORA
Analyzes current .env configuration and identifies gaps
"""

import os
import re
from pathlib import Path
from typing import Dict, List, Tuple, Any

class EnvironmentAnalyzer:
    """Analyze environment configuration completeness and validity"""
    
    def __init__(self):
        self.env_vars = {}
        self.analysis_results = {
            "configured": [],
            "missing": [],
            "invalid": [],
            "placeholders": [],
            "recommendations": []
        }
        
    def load_env_file(self) -> bool:
        """Load environment variables from .env file"""
        env_path = Path('.env')
        if not env_path.exists():
            return False
            
        with open(env_path, 'r') as f:
            for line_num, line in enumerate(f, 1):
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    try:
                        key, value = line.split('=', 1)
                        self.env_vars[key.strip()] = value.strip()
                    except ValueError:
                        continue
        return True
    
    def analyze_configuration(self) -> Dict[str, Any]:
        """Comprehensive environment analysis"""
        
        # Critical configuration requirements
        critical_config = {
            # Security (CRITICAL)
            'SECRET_KEY': {
                'required': True,
                'description': 'Flask/FastAPI secret key for sessions',
                'validator': self._validate_secret_key,
                'category': 'Security'
            },
            'JWT_SECRET_KEY': {
                'required': True,
                'description': 'JWT token signing key',
                'validator': self._validate_secret_key,
                'category': 'Security'
            },
            
            # External APIs (HIGH PRIORITY)
            'OPENAI_API_KEY': {
                'required': True,
                'description': 'OpenAI API for AI features',
                'validator': self._validate_openai_key,
                'category': 'AI Services'
            },
            'SENDGRID_API_KEY': {
                'required': True,
                'description': 'SendGrid for email notifications',
                'validator': self._validate_sendgrid_key,
                'category': 'Email Services'
            },
            
            # Database & Cache (CRITICAL)
            'DATABASE_URL': {
                'required': True,
                'description': 'Database connection string',
                'validator': self._validate_database_url,
                'category': 'Data Storage'
            },
            'REDIS_URL': {
                'required': False,  # Optional but recommended
                'description': 'Redis for caching and performance',
                'validator': self._validate_redis_url,
                'category': 'Performance'
            },
            
            # Application Configuration (MEDIUM)
            'BASE_URL': {
                'required': True,
                'description': 'Base URL for the application',
                'validator': self._validate_base_url,
                'category': 'Application'
            },
            'ENVIRONMENT': {
                'required': True,
                'description': 'Runtime environment (production/development)',
                'validator': self._validate_environment,
                'category': 'Application'
            },
            
            # Optional but Important
            'STRIPE_API_KEY': {
                'required': False,
                'description': 'Stripe for payment processing',
                'validator': self._validate_stripe_key,
                'category': 'Payments'
            },
            'PLAID_CLIENT_ID': {
                'required': False,
                'description': 'Plaid for bank integration',
                'validator': self._validate_plaid_config,
                'category': 'Banking'
            }
        }
        
        print("CORA Environment Configuration Analysis")
        print("=" * 50)
        
        # Analyze each configuration item
        for var_name, config in critical_config.items():
            self._analyze_variable(var_name, config)
        
        # Generate recommendations
        self._generate_recommendations()
        
        # Print results
        self._print_analysis_results()
        
        return {
            "configured": self.analysis_results["configured"],
            "missing": self.analysis_results["missing"],
            "invalid": self.analysis_results["invalid"],
            "placeholders": self.analysis_results["placeholders"],
            "recommendations": self.analysis_results["recommendations"],
            "ready_for_production": len(self.analysis_results["missing"]) == 0 and len(self.analysis_results["invalid"]) == 0
        }
    
    def _analyze_variable(self, var_name: str, config: Dict[str, Any]):
        """Analyze individual environment variable"""
        value = self.env_vars.get(var_name, '')
        category = config['category']
        description = config['description']
        required = config['required']
        validator = config.get('validator')
        
        if not value:
            if required:
                self.analysis_results["missing"].append({
                    "name": var_name,
                    "category": category,
                    "description": description,
                    "severity": "CRITICAL" if required else "WARNING"
                })
            return
        
        # Check for placeholder values
        if self._is_placeholder(value):
            self.analysis_results["placeholders"].append({
                "name": var_name,
                "category": category,
                "description": description,
                "current_value": value
            })
            return
        
        # Validate the value
        if validator:
            is_valid, message = validator(value)
            if is_valid:
                self.analysis_results["configured"].append({
                    "name": var_name,
                    "category": category,
                    "description": description,
                    "status": "Valid"
                })
            else:
                self.analysis_results["invalid"].append({
                    "name": var_name,
                    "category": category,
                    "description": description,
                    "issue": message
                })
        else:
            self.analysis_results["configured"].append({
                "name": var_name,
                "category": category,
                "description": description,
                "status": "Present"
            })
    
    def _is_placeholder(self, value: str) -> bool:
        """Check if value is a placeholder"""
        placeholder_patterns = [
            'YOUR_',
            'CHANGE_ME',
            'REPLACE_WITH',
            'TODO',
            'PLACEHOLDER'
        ]
        return any(pattern in value.upper() for pattern in placeholder_patterns)
    
    def _validate_secret_key(self, value: str) -> Tuple[bool, str]:
        """Validate secret key strength"""
        if len(value) < 32:
            return False, "Secret key should be at least 32 characters"
        if value.count('_') < 2:  # Basic entropy check
            return False, "Secret key should have more entropy"
        return True, "Valid secret key"
    
    def _validate_openai_key(self, value: str) -> Tuple[bool, str]:
        """Validate OpenAI API key format"""
        if not value.startswith('sk-'):
            return False, "OpenAI API key should start with 'sk-'"
        if len(value) < 50:
            return False, "OpenAI API key appears too short"
        return True, "Valid OpenAI API key format"
    
    def _validate_sendgrid_key(self, value: str) -> Tuple[bool, str]:
        """Validate SendGrid API key format"""
        if not value.startswith('SG.'):
            return False, "SendGrid API key should start with 'SG.'"
        if len(value) < 50:
            return False, "SendGrid API key appears too short"
        return True, "Valid SendGrid API key format"
    
    def _validate_database_url(self, value: str) -> Tuple[bool, str]:
        """Validate database URL"""
        if value.startswith('sqlite:'):
            return True, "SQLite database configured"
        elif value.startswith('postgresql:'):
            return True, "PostgreSQL database configured"
        elif value.startswith('mysql:'):
            return True, "MySQL database configured"
        else:
            return False, "Unknown database URL format"
    
    def _validate_redis_url(self, value: str) -> Tuple[bool, str]:
        """Validate Redis URL"""
        if value.startswith('redis://'):
            return True, "Redis URL configured"
        else:
            return False, "Invalid Redis URL format"
    
    def _validate_base_url(self, value: str) -> Tuple[bool, str]:
        """Validate base URL"""
        if value.startswith('http://') or value.startswith('https://'):
            return True, "Valid base URL"
        else:
            return False, "Base URL should start with http:// or https://"
    
    def _validate_environment(self, value: str) -> Tuple[bool, str]:
        """Validate environment setting"""
        valid_envs = ['production', 'staging', 'development', 'test']
        if value.lower() in valid_envs:
            return True, f"Valid environment: {value}"
        else:
            return False, f"Environment should be one of: {', '.join(valid_envs)}"
    
    def _validate_stripe_key(self, value: str) -> Tuple[bool, str]:
        """Validate Stripe API key"""
        if value.startswith('sk_live_') or value.startswith('sk_test_'):
            return True, "Valid Stripe API key format"
        else:
            return False, "Stripe API key should start with sk_live_ or sk_test_"
    
    def _validate_plaid_config(self, value: str) -> Tuple[bool, str]:
        """Validate Plaid client ID"""
        if len(value) > 10 and not self._is_placeholder(value):
            return True, "Plaid client ID configured"
        else:
            return False, "Invalid Plaid client ID"
    
    def _generate_recommendations(self):
        """Generate configuration recommendations"""
        recommendations = []
        
        if self.analysis_results["missing"]:
            recommendations.append({
                "priority": "HIGH",
                "category": "Missing Configuration",
                "action": f"Configure {len(self.analysis_results['missing'])} missing environment variables",
                "details": [item["name"] for item in self.analysis_results["missing"]]
            })
        
        if self.analysis_results["placeholders"]:
            recommendations.append({
                "priority": "HIGH", 
                "category": "Placeholder Values",
                "action": f"Replace {len(self.analysis_results['placeholders'])} placeholder values with real credentials",
                "details": [item["name"] for item in self.analysis_results["placeholders"]]
            })
        
        if self.analysis_results["invalid"]:
            recommendations.append({
                "priority": "CRITICAL",
                "category": "Invalid Configuration", 
                "action": f"Fix {len(self.analysis_results['invalid'])} invalid configuration values",
                "details": [f"{item['name']}: {item['issue']}" for item in self.analysis_results["invalid"]]
            })
        
        # Check for SQLite in production
        db_url = self.env_vars.get('DATABASE_URL', '')
        environment = self.env_vars.get('ENVIRONMENT', '').lower()
        if 'sqlite' in db_url and environment == 'production':
            recommendations.append({
                "priority": "MEDIUM",
                "category": "Production Optimization",
                "action": "Consider upgrading from SQLite to PostgreSQL for production",
                "details": ["SQLite is fine for development but PostgreSQL is recommended for production"]
            })
        
        # Check for Redis configuration
        if not self.env_vars.get('REDIS_URL'):
            recommendations.append({
                "priority": "MEDIUM",
                "category": "Performance Optimization", 
                "action": "Configure Redis for improved performance",
                "details": ["Redis provides caching and improves response times significantly"]
            })
        
        self.analysis_results["recommendations"] = recommendations
    
    def _print_analysis_results(self):
        """Print comprehensive analysis results"""
        
        print(f"\nConfiguration Status:")
        print(f"- Properly Configured: {len(self.analysis_results['configured'])}")
        print(f"- Missing Variables: {len(self.analysis_results['missing'])}")
        print(f"- Invalid Values: {len(self.analysis_results['invalid'])}")
        print(f"- Placeholder Values: {len(self.analysis_results['placeholders'])}")
        
        # Configured variables
        if self.analysis_results["configured"]:
            print(f"\nProperly Configured ({len(self.analysis_results['configured'])}):")
            by_category = {}
            for item in self.analysis_results["configured"]:
                category = item["category"]
                if category not in by_category:
                    by_category[category] = []
                by_category[category].append(item["name"])
            
            for category, variables in by_category.items():
                print(f"  {category}: {', '.join(variables)}")
        
        # Missing variables
        if self.analysis_results["missing"]:
            print(f"\nMissing Variables ({len(self.analysis_results['missing'])}):")
            for item in self.analysis_results["missing"]:
                severity = item["severity"]
                print(f"  [{severity}] {item['name']} - {item['description']}")
        
        # Placeholder values
        if self.analysis_results["placeholders"]:
            print(f"\nPlaceholder Values ({len(self.analysis_results['placeholders'])}):")
            for item in self.analysis_results["placeholders"]:
                print(f"  {item['name']} = {item['current_value']}")
        
        # Invalid values
        if self.analysis_results["invalid"]:
            print(f"\nInvalid Values ({len(self.analysis_results['invalid'])}):")
            for item in self.analysis_results["invalid"]:
                print(f"  {item['name']}: {item['issue']}")
        
        # Recommendations
        if self.analysis_results["recommendations"]:
            print(f"\nRecommendations:")
            for rec in self.analysis_results["recommendations"]:
                print(f"  [{rec['priority']}] {rec['action']}")
                if isinstance(rec['details'], list):
                    for detail in rec['details'][:3]:  # Show first 3
                        print(f"    - {detail}")
                    if len(rec['details']) > 3:
                        print(f"    ... and {len(rec['details']) - 3} more")
        
        # Overall assessment
        missing_critical = len([item for item in self.analysis_results["missing"] if item["severity"] == "CRITICAL"])
        total_issues = len(self.analysis_results["missing"]) + len(self.analysis_results["invalid"]) + len(self.analysis_results["placeholders"])
        
        print(f"\nOverall Assessment:")
        if total_issues == 0:
            print("  Status: READY FOR PRODUCTION")
            print("  All critical configuration is properly set up!")
        elif missing_critical > 0:
            print("  Status: NOT READY - CRITICAL ISSUES")
            print(f"  Fix {missing_critical} critical configuration issues before deployment")
        elif total_issues <= 3:
            print("  Status: NEARLY READY")
            print(f"  Address {total_issues} remaining issues for optimal production deployment")
        else:
            print("  Status: NEEDS WORK")
            print(f"  {total_issues} configuration issues need attention")

def main():
    """Run environment analysis"""
    analyzer = EnvironmentAnalyzer()
    
    if not analyzer.load_env_file():
        print("ERROR: No .env file found!")
        print("Create a .env file based on the .env.example template")
        return
    
    results = analyzer.analyze_configuration()
    
    # Save results for review
    import json
    with open("environment_analysis_report.json", "w") as f:
        json.dump(results, f, indent=2)
    
    print(f"\nDetailed report saved to: environment_analysis_report.json")

if __name__ == "__main__":
    main()