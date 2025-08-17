#!/usr/bin/env python3
"""
🧭 LOCATION: /CORA/tools/ui_ux_file_registry.py
🎯 PURPOSE: Comprehensive UI/UX file tracking and enhancement management
🔗 IMPORTS: pathlib, json, os
📤 EXPORTS: UIUXFileRegistry, get_file_status, track_enhancements
🔄 PATTERN: Centralized file tracking with bootup integration
📝 STATUS: Production ready for A+ UI/UX tracking

💡 AI HINT: This ensures no UI/UX files are missed during enhancements
⚠️ NEVER: Track sensitive files or credentials
"""

import json
import os
import re
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional, Set
import hashlib

class UIUXFileRegistry:
    """Comprehensive UI/UX file tracking and enhancement management"""
    
    def __init__(self, project_root: str = None):
        self.project_root = Path(project_root) if project_root else Path(__file__).parent.parent
        self.registry_file = self.project_root / "data" / "ui_ux_registry.json"
        self.registry = self._load_registry()
        
        # File categories for tracking
        self.categories = {
            'css': ['wellness.css', 'onboarding.css'],
            'js_modules': [
                'dark-mode.js', 'error-manager.js', 'timeout-handler.js',
                'performance.js', 'accessibility.js', 'mobile-navigation.js',
                'voice_onboarding.js', 'sw.js', 'security.js'
            ],
            'templates': [
                'index.html', 'expenses.html', 'dashboard.html', 'admin.html',
                'signup_wellness.html', 'login.html', 'receipt_upload.html',
                'privacy.html', 'terms.html', 'signup.html'
            ],
            'onboarding_templates': [
                'welcome.html', 'connect_bank.html', 'success.html'
            ],
            'integration_templates': [
                'plaid.html', 'quickbooks.html', 'stripe.html'
            ],
            'middleware': [
                'security_headers_enhanced.py'
            ]
        }
        
        # Enhancement levels
        self.enhancement_levels = {
            'none': 0,
            'basic': 1,
            'enhanced': 2,
            'complete': 3,
            'a_plus': 4
        }
        
        # Required features for A+ rating
        self.a_plus_requirements = {
            'dark_mode': ['dark-mode.js', 'wellness.css'],
            'error_handling': ['error-manager.js'],
            'timeout_management': ['timeout-handler.js'],
            'performance': ['performance.js'],
            'accessibility': ['accessibility.js'],
            'mobile_navigation': ['mobile-navigation.js'],
            'voice_features': ['voice_onboarding.js'],
            'service_worker': ['sw.js'],
            'security': ['security.js', 'security_headers_enhanced.py']
        }

    def _load_registry(self) -> Dict:
        """Load existing registry or create new one"""
        if self.registry_file.exists():
            try:
                with open(self.registry_file, 'r') as f:
                    return json.load(f)
            except (json.JSONDecodeError, FileNotFoundError):
                pass
        
        return {
            'version': '1.0.0',
            'last_updated': datetime.now().isoformat(),
            'files': {},
            'enhancement_status': {},
            'dependencies': {},
            'integration_status': {},
            'performance_metrics': {},
            'accessibility_scores': {}
        }

    def _save_registry(self):
        """Save registry to file"""
        self.registry['last_updated'] = datetime.now().isoformat()
        self.registry_file.parent.mkdir(parents=True, exist_ok=True)
        
        with open(self.registry_file, 'w') as f:
            json.dump(self.registry, f, indent=2)

    def scan_all_files(self) -> Dict:
        """Comprehensive scan of all UI/UX files"""
        print("🔍 Scanning UI/UX files...")
        
        scan_results = {
            'css_files': self._scan_css_files(),
            'js_files': self._scan_js_files(),
            'template_files': self._scan_template_files(),
            'middleware_files': self._scan_middleware_files(),
            'missing_files': [],
            'orphaned_files': []
        }
        
        # Update registry with scan results
        self._update_registry_from_scan(scan_results)
        self._save_registry()
        
        return scan_results

    def _scan_css_files(self) -> List[Dict]:
        """Scan CSS files in web/static/css/"""
        css_dir = self.project_root / "web" / "static" / "css"
        css_files = []
        
        if css_dir.exists():
            for file_path in css_dir.glob("*.css"):
                file_info = self._get_file_info(file_path)
                css_files.append(file_info)
        
        return css_files

    def _scan_js_files(self) -> List[Dict]:
        """Scan JavaScript files in web/static/js/"""
        js_dir = self.project_root / "web" / "static" / "js"
        js_files = []
        
        if js_dir.exists():
            for file_path in js_dir.glob("*.js"):
                file_info = self._get_file_info(file_path)
                js_files.append(file_info)
        
        return js_files

    def _scan_template_files(self) -> List[Dict]:
        """Scan HTML template files"""
        template_files = []
        
        # Main templates
        templates_dir = self.project_root / "web" / "templates"
        if templates_dir.exists():
            for file_path in templates_dir.glob("*.html"):
                file_info = self._get_file_info(file_path)
                template_files.append(file_info)
        
        # Onboarding templates
        onboarding_dir = templates_dir / "onboarding"
        if onboarding_dir.exists():
            for file_path in onboarding_dir.glob("*.html"):
                file_info = self._get_file_info(file_path)
                template_files.append(file_info)
        
        # Integration templates
        integrations_dir = templates_dir / "integrations"
        if integrations_dir.exists():
            for file_path in integrations_dir.glob("*.html"):
                file_info = self._get_file_info(file_path)
                template_files.append(file_info)
        
        return template_files

    def _scan_middleware_files(self) -> List[Dict]:
        """Scan middleware files"""
        middleware_dir = self.project_root / "middleware"
        middleware_files = []
        
        if middleware_dir.exists():
            for file_path in middleware_dir.glob("*.py"):
                if "ui" in file_path.name.lower() or "ux" in file_path.name.lower() or "security" in file_path.name.lower():
                    file_info = self._get_file_info(file_path)
                    middleware_files.append(file_info)
        
        return middleware_files

    def _get_file_info(self, file_path: Path) -> Dict:
        """Get comprehensive file information"""
        try:
            stat = file_path.stat()
            content = file_path.read_text(encoding='utf-8')
            
            return {
                'path': str(file_path.relative_to(self.project_root)),
                'name': file_path.name,
                'size': stat.st_size,
                'modified': datetime.fromtimestamp(stat.st_mtime).isoformat(),
                'hash': hashlib.md5(content.encode()).hexdigest(),
                'lines': len(content.splitlines()),
                'enhancement_level': self._detect_enhancement_level(file_path, content),
                'dependencies': self._extract_dependencies(file_path, content),
                'features': self._detect_features(file_path, content),
                'issues': self._detect_issues(file_path, content)
            }
        except Exception as e:
            return {
                'path': str(file_path.relative_to(self.project_root)),
                'name': file_path.name,
                'error': str(e)
            }

    def _detect_enhancement_level(self, file_path: Path, content: str) -> str:
        """Detect current enhancement level of a file"""
        file_name = file_path.name.lower()
        
        # Check for A+ features
        a_plus_features = 0
        total_features = len(self.a_plus_requirements)
        
        for feature, required_files in self.a_plus_requirements.items():
            if any(req_file in file_name for req_file in required_files):
                a_plus_features += 1
        
        # Check content for enhancement indicators
        enhancement_indicators = {
            'dark_mode': ['data-theme', 'dark-mode', 'theme-toggle'],
            'error_handling': ['error-manager', 'error handling', 'retry'],
            'timeout_management': ['timeout', 'abort controller'],
            'performance': ['performance', 'lighthouse', 'core web vitals'],
            'accessibility': ['aria-', 'accessibility', 'screen reader'],
            'mobile_navigation': ['mobile-menu', 'hamburger', 'touch'],
            'voice_features': ['voice', 'speech', 'microphone'],
            'service_worker': ['service worker', 'sw.js'],
            'security': ['csp', 'security', 'nonce']
        }
        
        detected_features = 0
        for feature, indicators in enhancement_indicators.items():
            if any(indicator in content.lower() for indicator in indicators):
                detected_features += 1
        
        # Calculate enhancement level
        if detected_features == total_features:
            return 'a_plus'
        elif detected_features >= total_features * 0.8:
            return 'complete'
        elif detected_features >= total_features * 0.6:
            return 'enhanced'
        elif detected_features >= total_features * 0.3:
            return 'basic'
        else:
            return 'none'

    def _extract_dependencies(self, file_path: Path, content: str) -> List[str]:
        """Extract file dependencies"""
        dependencies = []
        
        if file_path.suffix == '.html':
            # Extract CSS and JS dependencies
            import re
            
            # CSS dependencies
            css_patterns = [
                r'href="([^"]*\.css)"',
                r'href=\'([^\']*\.css)\'',
                r'rel="stylesheet"[^>]*href="([^"]*)"',
                r'rel=\'stylesheet\'[^>]*href=\'([^\']*)\''
            ]
            
            for pattern in css_patterns:
                matches = re.findall(pattern, content)
                dependencies.extend(matches)
            
            # JS dependencies
            js_patterns = [
                r'src="([^"]*\.js)"',
                r'src=\'([^\']*\.js)\'',
                r'<script[^>]*src="([^"]*)"',
                r'<script[^>]*src=\'([^\']*)\''
            ]
            
            for pattern in js_patterns:
                matches = re.findall(pattern, content)
                dependencies.extend(matches)
        
        return list(set(dependencies))

    def _detect_features(self, file_path: Path, content: str) -> List[str]:
        """Detect features present in the file"""
        features = []
        
        feature_patterns = {
            'dark_mode': [r'dark-mode', r'data-theme', r'theme-toggle'],
            'error_handling': [r'error-manager', r'error handling', r'retry'],
            'timeout_management': [r'timeout', r'abort controller'],
            'performance': [r'performance', r'lighthouse', r'core web vitals'],
            'accessibility': [r'aria-', r'accessibility', r'screen reader'],
            'mobile_navigation': [r'mobile-menu', r'hamburger', r'touch'],
            'voice_features': [r'voice', r'speech', r'microphone'],
            'service_worker': [r'service worker', r'sw\.js'],
            'security': [r'csp', r'security', r'nonce'],
            'wellness_design': [r'wellness', r'calm', r'peace'],
            'responsive_design': [r'@media', r'responsive', r'mobile'],
            'animations': [r'animation', r'transition', r'keyframes']
        }
        
        for feature, patterns in feature_patterns.items():
            if any(re.search(pattern, content, re.IGNORECASE) for pattern in patterns):
                features.append(feature)
        
        return features

    def _detect_issues(self, file_path: Path, content: str) -> List[str]:
        """Detect potential issues in the file"""
        issues = []
        
        # Check for common issues
        if file_path.suffix == '.html':
            if 'wellness.css' not in content and 'wellness' not in file_path.name.lower():
                issues.append('missing_wellness_css')
            
            if 'dark-mode.js' not in content:
                issues.append('missing_dark_mode')
            
            if 'error-manager.js' not in content:
                issues.append('missing_error_handling')
            
            if 'timeout-handler.js' not in content:
                issues.append('missing_timeout_management')
            
            if 'performance.js' not in content:
                issues.append('missing_performance_optimization')
            
            if 'accessibility.js' not in content:
                issues.append('missing_accessibility_features')
        
        return issues

    def _update_registry_from_scan(self, scan_results: Dict):
        """Update registry with scan results"""
        all_files = []
        all_files.extend(scan_results['css_files'])
        all_files.extend(scan_results['js_files'])
        all_files.extend(scan_results['template_files'])
        all_files.extend(scan_results['middleware_files'])
        
        # Update files in registry
        for file_info in all_files:
            if 'path' in file_info:
                self.registry['files'][file_info['path']] = file_info
        
        # Calculate overall enhancement status
        self._calculate_overall_status()

    def _calculate_overall_status(self):
        """Calculate overall enhancement status"""
        total_files = len(self.registry['files'])
        enhanced_files = 0
        a_plus_files = 0
        
        for file_info in self.registry['files'].values():
            if 'enhancement_level' in file_info:
                if file_info['enhancement_level'] in ['enhanced', 'complete', 'a_plus']:
                    enhanced_files += 1
                if file_info['enhancement_level'] == 'a_plus':
                    a_plus_files += 1
        
        self.registry['enhancement_status'] = {
            'total_files': total_files,
            'enhanced_files': enhanced_files,
            'a_plus_files': a_plus_files,
            'enhancement_percentage': (enhanced_files / total_files * 100) if total_files > 0 else 0,
            'a_plus_percentage': (a_plus_files / total_files * 100) if total_files > 0 else 0
        }

    def get_enhancement_report(self) -> Dict:
        """Generate comprehensive enhancement report"""
        report = {
            'summary': self.registry['enhancement_status'],
            'files_by_level': {},
            'missing_integrations': [],
            'recommendations': []
        }
        
        # Group files by enhancement level
        for file_info in self.registry['files'].values():
            level = file_info.get('enhancement_level', 'none')
            if level not in report['files_by_level']:
                report['files_by_level'][level] = []
            report['files_by_level'][level].append(file_info['path'])
        
        # Find missing integrations
        for file_info in self.registry['files'].values():
            if file_info.get('issues'):
                report['missing_integrations'].append({
                    'file': file_info['path'],
                    'issues': file_info['issues']
                })
        
        # Generate recommendations
        report['recommendations'] = self._generate_recommendations()
        
        return report

    def _generate_recommendations(self) -> List[str]:
        """Generate enhancement recommendations"""
        recommendations = []
        
        # Check for files missing core features
        for file_info in self.registry['files'].values():
            if file_info.get('issues'):
                for issue in file_info['issues']:
                    if issue == 'missing_dark_mode':
                        recommendations.append(f"Add dark mode to {file_info['path']}")
                    elif issue == 'missing_error_handling':
                        recommendations.append(f"Add error handling to {file_info['path']}")
                    elif issue == 'missing_timeout_management':
                        recommendations.append(f"Add timeout management to {file_info['path']}")
                    elif issue == 'missing_performance_optimization':
                        recommendations.append(f"Add performance optimization to {file_info['path']}")
                    elif issue == 'missing_accessibility_features':
                        recommendations.append(f"Add accessibility features to {file_info['path']}")
        
        return recommendations

    def track_enhancement(self, file_path: str, enhancement_type: str, details: Dict):
        """Track an enhancement made to a file"""
        if file_path not in self.registry['files']:
            self.registry['files'][file_path] = {}
        
        if 'enhancements' not in self.registry['files'][file_path]:
            self.registry['files'][file_path]['enhancements'] = []
        
        enhancement_record = {
            'type': enhancement_type,
            'timestamp': datetime.now().isoformat(),
            'details': details
        }
        
        self.registry['files'][file_path]['enhancements'].append(enhancement_record)
        self._save_registry()

    def get_file_status(self, file_path: str) -> Dict:
        """Get current status of a specific file"""
        return self.registry['files'].get(file_path, {})

    def export_registry(self, output_path: str = None):
        """Export registry to file"""
        if not output_path:
            output_path = self.project_root / "reports" / f"ui_ux_registry_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_path, 'w') as f:
            json.dump(self.registry, f, indent=2)
        
        return str(output_path)

# Global registry instance
ui_ux_registry = UIUXFileRegistry()

def get_file_status(file_path: str) -> Dict:
    """Get file status from global registry"""
    return ui_ux_registry.get_file_status(file_path)

def track_enhancements(file_path: str, enhancement_type: str, details: Dict):
    """Track enhancements in global registry"""
    ui_ux_registry.track_enhancement(file_path, enhancement_type, details)

def scan_ui_ux_files() -> Dict:
    """Scan all UI/UX files and return report"""
    return ui_ux_registry.scan_all_files()

def get_enhancement_report() -> Dict:
    """Get comprehensive enhancement report"""
    return ui_ux_registry.get_enhancement_report()

if __name__ == "__main__":
    # Run comprehensive scan
    print("🔍 Starting UI/UX file registry scan...")
    scan_results = scan_ui_ux_files()
    report = get_enhancement_report()
    
    print(f"\n📊 UI/UX Enhancement Status:")
    print(f"Total Files: {report['summary']['total_files']}")
    print(f"Enhanced Files: {report['summary']['enhanced_files']}")
    print(f"A+ Files: {report['summary']['a_plus_files']}")
    print(f"Enhancement Percentage: {report['summary']['enhancement_percentage']:.1f}%")
    print(f"A+ Percentage: {report['summary']['a_plus_percentage']:.1f}%")
    
    if report['recommendations']:
        print(f"\n🎯 Recommendations:")
        for rec in report['recommendations']:
            print(f"  - {rec}")
    
    # Export registry
    export_path = ui_ux_registry.export_registry()
    print(f"\n📁 Registry exported to: {export_path}") 