#!/usr/bin/env python3
"""
🧭 LOCATION: /CORA/tools/ui_ux_commands.py
🎯 PURPOSE: Simple UI/UX registry command handler
🔗 IMPORTS: ui_ux_file_registry
📤 EXPORTS: ui_status, ui_scan
🔄 PATTERN: Command-line interface for UI/UX tracking
📝 STATUS: Production ready for bootup integration

💡 AI HINT: Simple commands for checking UI/UX file status
⚠️ NEVER: Modify files without explicit user permission
"""

import sys
import os
from pathlib import Path

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    from ui_ux_file_registry import scan_ui_ux_files, get_enhancement_report, ui_ux_registry
except ImportError as e:
    print(f"❌ UI/UX registry not available: {e}")
    sys.exit(1)

def ui_status():
    """Show current UI/UX enhancement status"""
    print("🎨 UI/UX Enhancement Status")
    print("=" * 40)
    
    try:
        report = get_enhancement_report()
        
        # Summary
        print(f"📊 Total Files: {report['summary']['total_files']}")
        print(f"✨ Enhanced Files: {report['summary']['enhanced_files']}")
        print(f"🌟 A+ Files: {report['summary']['a_plus_files']}")
        print(f"📈 Enhancement: {report['summary']['enhancement_percentage']:.1f}%")
        print(f"🏆 A+ Rating: {report['summary']['a_plus_percentage']:.1f}%")
        print()
        
        # Files by level
        if report['files_by_level']:
            print("📁 Files by Enhancement Level:")
            for level, files in report['files_by_level'].items():
                print(f"   {level.upper()}: {len(files)} files")
            print()
        
        # Recommendations
        if report['recommendations']:
            print("🎯 Top Recommendations:")
            for i, rec in enumerate(report['recommendations'][:5], 1):
                print(f"   {i}. {rec}")
            if len(report['recommendations']) > 5:
                print(f"   ... and {len(report['recommendations']) - 5} more")
            print()
        
        # Missing integrations
        if report['missing_integrations']:
            print("⚠️  Files Missing Core Features:")
            for item in report['missing_integrations'][:3]:
                print(f"   {item['file']}: {', '.join(item['issues'])}")
            if len(report['missing_integrations']) > 3:
                print(f"   ... and {len(report['missing_integrations']) - 3} more")
            print()
        
        return True
        
    except Exception as e:
        print(f"❌ Error getting UI/UX status: {e}")
        return False

def ui_scan():
    """Run comprehensive UI/UX file scan"""
    print("🔍 Running UI/UX File Scan...")
    print("=" * 40)
    
    try:
        scan_results = scan_ui_ux_files()
        report = get_enhancement_report()
        
        print("✅ Scan Complete!")
        print()
        
        # Show scan results
        print("📊 Scan Results:")
        print(f"   CSS Files: {len(scan_results['css_files'])}")
        print(f"   JS Files: {len(scan_results['js_files'])}")
        print(f"   Templates: {len(scan_results['template_files'])}")
        print(f"   Middleware: {len(scan_results['middleware_files'])}")
        print()
        
        # Show enhancement status
        print("🎨 Enhancement Status:")
        print(f"   Total Files: {report['summary']['total_files']}")
        print(f"   Enhanced: {report['summary']['enhanced_files']} ({report['summary']['enhancement_percentage']:.1f}%)")
        print(f"   A+ Rating: {report['summary']['a_plus_files']} ({report['summary']['a_plus_percentage']:.1f}%)")
        print()
        
        # Export registry
        export_path = ui_ux_registry.export_registry()
        print(f"📁 Registry exported to: {export_path}")
        print()
        
        return True
        
    except Exception as e:
        print(f"❌ Error during UI/UX scan: {e}")
        return False

def ui_details(file_path: str = None):
    """Show detailed information about a specific file or all files"""
    if file_path:
        # Show details for specific file
        file_info = ui_ux_registry.get_file_status(file_path)
        if file_info:
            print(f"📄 File Details: {file_path}")
            print("=" * 50)
            print(f"Name: {file_info.get('name', 'N/A')}")
            print(f"Size: {file_info.get('size', 'N/A')} bytes")
            print(f"Lines: {file_info.get('lines', 'N/A')}")
            print(f"Modified: {file_info.get('modified', 'N/A')}")
            print(f"Enhancement Level: {file_info.get('enhancement_level', 'N/A')}")
            
            if file_info.get('features'):
                print(f"Features: {', '.join(file_info['features'])}")
            
            if file_info.get('issues'):
                print(f"Issues: {', '.join(file_info['issues'])}")
            
            if file_info.get('dependencies'):
                print(f"Dependencies: {', '.join(file_info['dependencies'])}")
            
            if file_info.get('enhancements'):
                print(f"Enhancements: {len(file_info['enhancements'])} recorded")
        else:
            print(f"❌ File not found: {file_path}")
    else:
        # Show summary of all files
        print("📄 All UI/UX Files:")
        print("=" * 50)
        
        for file_path, file_info in ui_ux_registry.registry['files'].items():
            level = file_info.get('enhancement_level', 'none')
            issues = len(file_info.get('issues', []))
            features = len(file_info.get('features', []))
            
            status_icon = "🌟" if level == "a_plus" else "✨" if level in ["enhanced", "complete"] else "📄"
            issue_icon = "⚠️" if issues > 0 else "✅"
            
            print(f"{status_icon} {file_path}")
            print(f"   Level: {level.upper()}, Features: {features}, Issues: {issues} {issue_icon}")

def main():
    """Main command handler"""
    if len(sys.argv) < 2:
        print("Usage: python ui_ux_commands.py <command> [file_path]")
        print("Commands:")
        print("  status  - Show UI/UX enhancement status")
        print("  scan    - Run comprehensive file scan")
        print("  details [file] - Show detailed file information")
        return 1
    
    command = sys.argv[1].lower()
    
    if command == "status":
        return 0 if ui_status() else 1
    elif command == "scan":
        return 0 if ui_scan() else 1
    elif command == "details":
        file_path = sys.argv[2] if len(sys.argv) > 2 else None
        ui_details(file_path)
        return 0
    else:
        print(f"❌ Unknown command: {command}")
        return 1

if __name__ == "__main__":
    sys.exit(main()) 