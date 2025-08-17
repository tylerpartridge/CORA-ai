#!/usr/bin/env python3
"""
CORA Template Enhancement Script
Integrates all UI/UX modules into templates for A+ experience
"""

import os
import re
import shutil
import sys
from datetime import datetime
from pathlib import Path

# Fix Unicode on Windows
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding='utf-8')

class TemplateEnhancer:
    def __init__(self):
        self.templates_dir = Path("web/templates")
        self.backup_dir = Path("backups/templates_backup_" + datetime.now().strftime("%Y%m%d_%H%M%S"))
        self.enhanced_count = 0
        self.errors = []
        
        # UI/UX modules to integrate
        self.core_modules = [
            '/static/js/performance.js',
            '/static/js/accessibility.js', 
            '/static/js/dark-mode.js',
            '/static/js/error-manager.js',
            '/static/js/timeout-handler.js',
            '/static/js/mobile-navigation.js'
        ]
        
        # CSS files to include
        self.css_files = [
            '/static/css/wellness.css',
            '/static/css/mobile-navigation.css'
        ]
        
    def backup_templates(self):
        """Create backup of all templates before enhancement"""
        print("📦 Creating backup of templates...")
        self.backup_dir.mkdir(parents=True, exist_ok=True)
        
        for template in self.templates_dir.rglob("*.html"):
            relative_path = template.relative_to(self.templates_dir)
            backup_path = self.backup_dir / relative_path
            backup_path.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(template, backup_path)
            
        print(f"✅ Backed up templates to: {self.backup_dir}")
        
    def enhance_template(self, template_path):
        """Enhance a single template with all UI/UX modules"""
        print(f"\n🔧 Enhancing: {template_path}")
        
        try:
            with open(template_path, 'r', encoding='utf-8') as f:
                content = f.read()
                
            # Check if already enhanced
            if all(module in content for module in self.core_modules):
                print(f"✓ Already enhanced: {template_path}")
                return False
                
            # Replace old CSS with wellness.css
            content = self.replace_css(content)
            
            # Add UI/UX modules before </body>
            content = self.add_modules(content)
            
            # Add mobile navigation container
            content = self.add_mobile_nav_container(content)
            
            # Add service worker registration
            content = self.add_service_worker(content)
            
            # Remove old inline styles
            content = self.remove_inline_styles(content)
            
            # Add data-theme attribute
            content = self.add_theme_attribute(content)
            
            # Write enhanced template
            with open(template_path, 'w', encoding='utf-8') as f:
                f.write(content)
                
            self.enhanced_count += 1
            print(f"✅ Enhanced: {template_path}")
            return True
            
        except Exception as e:
            self.errors.append(f"Error enhancing {template_path}: {str(e)}")
            print(f"❌ Error: {str(e)}")
            return False
            
    def replace_css(self, content):
        """Replace inline CSS and old stylesheets with wellness.css"""
        # Remove large inline style blocks
        content = re.sub(r'<style>\s*\/\*.*?\*\/.*?</style>', '', content, flags=re.DOTALL)
        
        # Add wellness CSS if not present
        if 'wellness.css' not in content:
            # Find </head> and insert CSS before it
            head_end = content.find('</head>')
            if head_end > -1:
                css_links = '\n'.join([f'    <link rel="stylesheet" href="{css}">' for css in self.css_files])
                content = content[:head_end] + f"\n    <!-- CORA Wellness Design System -->\n{css_links}\n" + content[head_end:]
                
        return content
        
    def add_modules(self, content):
        """Add all UI/UX JavaScript modules"""
        body_end = content.rfind('</body>')
        if body_end == -1:
            return content
            
        # Check if modules already exist
        if any(module in content for module in self.core_modules):
            return content
            
        modules_html = """
    <!-- CORA UI/UX Enhancement Modules -->
    <script src="/static/js/performance.js"></script>
    <script src="/static/js/accessibility.js"></script>
    <script src="/static/js/dark-mode.js"></script>
    <script src="/static/js/error-manager.js"></script>
    <script src="/static/js/timeout-handler.js"></script>
    <script src="/static/js/mobile-navigation.js"></script>
    
    <!-- Service Worker Registration -->
    <script>
    if ('serviceWorker' in navigator) {
        window.addEventListener('load', () => {
            navigator.serviceWorker.register('/static/js/sw.js')
                .then(reg => console.log('🔧 Service Worker registered'))
                .catch(err => console.error('Service Worker registration failed:', err));
        });
    }
    </script>
"""
        
        return content[:body_end] + modules_html + "\n" + content[body_end:]
        
    def add_mobile_nav_container(self, content):
        """Add mobile navigation container after body tag"""
        # Find <body> tag
        body_match = re.search(r'<body[^>]*>', content)
        if body_match:
            body_end = body_match.end()
            nav_container = '\n    <div id="mobile-nav-container"></div>\n'
            
            # Only add if not already present
            if 'mobile-nav-container' not in content:
                content = content[:body_end] + nav_container + content[body_end:]
                
        return content
        
    def add_service_worker(self, content):
        """Ensure service worker is registered"""
        # Already added in add_modules
        return content
        
    def remove_inline_styles(self, content):
        """Remove large inline style blocks (keep small ones)"""
        # Remove style blocks larger than 500 characters
        def replace_large_styles(match):
            style_content = match.group(0)
            if len(style_content) > 500:
                return '<!-- Inline styles moved to wellness.css -->'
            return style_content
            
        content = re.sub(r'<style[^>]*>.*?</style>', replace_large_styles, content, flags=re.DOTALL)
        return content
        
    def add_theme_attribute(self, content):
        """Add data-theme attribute to html tag"""
        if 'data-theme' not in content:
            content = re.sub(r'<html([^>]*)>', r'<html\1 data-theme="light">', content)
        return content
        
    def enhance_dashboard(self):
        """Special handling for dashboard.html"""
        dashboard_path = self.templates_dir / "dashboard.html"
        if not dashboard_path.exists():
            print("❌ Dashboard.html not found")
            return
            
        print("\n🎯 Special enhancement for dashboard.html...")
        
        with open(dashboard_path, 'r', encoding='utf-8') as f:
            content = f.read()
            
        # Remove ALL inline styles from dashboard
        content = re.sub(r'<style>.*?</style>', '', content, flags=re.DOTALL)
        
        # Update CSS classes to use wellness system
        replacements = {
            'color-primary': 'wellness-primary',
            'color-calm': 'wellness-calm',
            'color-peace': 'wellness-peace',
            'color-warm': 'wellness-warm',
            'transition-calm': 'wellness-transition-calm',
            'animation-breathe': 'wellness-animation-breathe',
            'wellness-score-card': 'wellness-card wellness-score-container',
            'breathing-room-card': 'wellness-card',
            'voice-capture-zone': 'wellness-card voice-capture-container'
        }
        
        for old, new in replacements.items():
            content = content.replace(f'"{old}"', f'"{new}"')
            content = content.replace(f"'{old}'", f"'{new}'")
            content = content.replace(f'var(--{old}', f'var(--{new}')
            
        # Now enhance normally
        with open(dashboard_path, 'w', encoding='utf-8') as f:
            f.write(content)
            
        self.enhance_template(dashboard_path)
        
    def generate_report(self):
        """Generate enhancement report"""
        report = f"""
# Template Enhancement Report
Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## Summary
- Templates Enhanced: {self.enhanced_count}
- Errors: {len(self.errors)}
- Backup Location: {self.backup_dir}

## Enhancements Applied
- ✅ Wellness CSS design system
- ✅ Mobile navigation system  
- ✅ Dark mode support
- ✅ Performance optimizations
- ✅ Accessibility features
- ✅ Error handling
- ✅ Service worker registration

## Templates Enhanced
"""
        
        for template in self.templates_dir.rglob("*.html"):
            with open(template, 'r', encoding='utf-8') as f:
                content = f.read()
            
            has_modules = all(module in content for module in self.core_modules)
            status = "✅ Enhanced" if has_modules else "❌ Not Enhanced"
            report += f"- {template.relative_to(self.templates_dir)}: {status}\n"
            
        if self.errors:
            report += "\n## Errors\n"
            for error in self.errors:
                report += f"- {error}\n"
                
        # Save report
        report_path = Path("docs/TEMPLATE_ENHANCEMENT_REPORT.md")
        with open(report_path, 'w', encoding='utf-8') as f:
            f.write(report)
            
        print(f"\n📄 Report saved to: {report_path}")
        
    def run(self):
        """Run the enhancement process"""
        print("🚀 CORA Template Enhancement Script")
        print("=" * 50)
        
        # Create backup
        self.backup_templates()
        
        # Enhance dashboard first (most critical)
        self.enhance_dashboard()
        
        # Enhance all other templates
        for template in self.templates_dir.rglob("*.html"):
            if template.name != "dashboard.html":  # Already enhanced
                self.enhance_template(template)
                
        # Generate report
        self.generate_report()
        
        print(f"\n✨ Enhancement complete! Enhanced {self.enhanced_count} templates.")
        print(f"📦 Backup saved to: {self.backup_dir}")
        
        if self.errors:
            print(f"\n⚠️ {len(self.errors)} errors occurred. Check the report for details.")


if __name__ == "__main__":
    enhancer = TemplateEnhancer()
    enhancer.run()