#!/usr/bin/env python3
"""
AI Dashboard Generator
Creates AI_DASHBOARD.md for 30-second absolute awareness
"""

import os
import json
import asyncio
import re
import time
from datetime import datetime
from pathlib import Path

class AIDashboardGenerator:
    def __init__(self, config_path="tools/ai_dashboard_config.json"):
        self.config = self.load_config(config_path)
        self.output_file = self.config["dashboard"]["output_file"]
        self.max_lines = self.config["dashboard"]["max_lines"]
        self.timeout = self.config["dashboard"]["generation_timeout"]
        
        # Blocker detection patterns
        self.blocker_patterns = [
            r"ImportError.*in\s+(\S+\.py):(\d+)",  # Import errors
            r"(\S+\.py).*exceeds limit.*(\d+)/(\d+)",  # File size violations
            r"FAILED\s+(\S+\.py)::",  # Test failures
            r"TypeError|AttributeError|NameError",  # Runtime errors
        ]
        
    def load_config(self, config_path):
        """Load configuration from JSON file"""
        try:
            with open(config_path, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            print(f"Warning: Config file {config_path} not found, using defaults")
            return {
                "dashboard": {
                    "output_file": "AI_DASHBOARD.md",
                    "max_lines": 100,
                    "generation_timeout": 2
                }
            }
    
    def get_health_emoji(self, violations):
        """Get visual health indicator"""
        if violations == 0: return "🟢"
        elif violations <= 5: return "🟡"
        else: return "🔴"
    
    async def collect_data_parallel(self):
        """Collect all data in parallel for speed"""
        tasks = [
            self.get_focus_now(),
            self.get_blockers(),
            self.get_system_pulse(),
            self.get_instant_navigation(),
            self.get_context()
        ]
        return await asyncio.gather(*tasks)
    
    async def get_focus_now(self):
        """Extract current focus from NOW.md"""
        try:
            with open("NOW.md", 'r') as f:
                content = f.read()
                # Look for current task patterns
                current_task_match = re.search(r"\*\*Current Task:\*\*(.*?)(?=\n\n|\n#|$)", content, re.DOTALL)
                if current_task_match:
                    return current_task_match.group(1).strip()
                return "No current task identified"
        except FileNotFoundError:
            return "NOW.md not found"
    
    async def get_blockers(self):
        """Detect current blockers and issues"""
        blockers = []
        
        # Check for file size violations
        try:
            result = os.popen("python tools/health_check.py 2>&1").read()
            for line in result.split('\n'):
                if "exceeds limit" in line or "FAILED" in line:
                    blockers.append(line.strip())
        except:
            pass
        
        # Check for import errors
        try:
            result = os.popen("python -m py_compile app.py 2>&1").read()
            if "ImportError" in result or "SyntaxError" in result:
                blockers.append("Import/Syntax errors detected")
        except:
            pass
        
        return blockers if blockers else ["No blockers detected"]
    
    async def get_system_pulse(self):
        """Get system health at a glance"""
        health_data = {
            "git_status": "Unknown",
            "file_count": 0,
            "health_score": "Unknown"
        }
        
        # Git status
        try:
            git_result = os.popen("git status --porcelain | wc -l").read().strip()
            health_data["git_status"] = f"{git_result} changes"
        except:
            pass
        
        # File count
        try:
            file_count = len([f for f in Path('.').rglob('*.py') if f.is_file()])
            health_data["file_count"] = file_count
        except:
            pass
        
        return health_data
    
    async def get_instant_navigation(self):
        """Common paths and commands for quick navigation"""
        return {
            "key_files": [
                "NOW.md - Current focus",
                "STATUS.md - System status", 
                "NEXT.md - Next steps",
                "BOOTUP.md - AI guidelines"
            ],
            "commands": [
                "python tools/health_check.py - System health",
                "git status - Repository status",
                "python app.py - Run application"
            ]
        }
    
    async def get_context(self):
        """Where we've been, where we're going"""
        try:
            with open("NEXT.md", 'r') as f:
                next_content = f.read()
                next_match = re.search(r"## Next Steps(.*?)(?=\n#|$)", next_content, re.DOTALL)
                next_steps = next_match.group(1).strip() if next_match else "No next steps defined"
        except:
            next_steps = "NEXT.md not found"
        
        return {
            "next_steps": next_steps,
            "last_updated": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
    
    async def generate_dashboard(self):
        """Generate the complete AI dashboard"""
        start_time = time.time()
        
        # Collect all data in parallel
        focus_now, blockers, system_pulse, navigation, context = await self.collect_data_parallel()
        
        # Generate markdown
        dashboard = f"""# 🎯 AI DASHBOARD - CORA System Awareness

*Generated: {context['last_updated']} | Target: 30-second absolute awareness*

## 🎯 FOCUS NOW
{focus_now}

## 🚨 BLOCKERS
"""
        
        for blocker in blockers:
            dashboard += f"- {blocker}\n"
        
        # Health indicator
        health_emoji = self.get_health_emoji(len(blockers))
        dashboard += f"""
## {health_emoji} SYSTEM PULSE
- **Git Status**: {system_pulse['git_status']}
- **Python Files**: {system_pulse['file_count']}
- **Health**: {health_emoji} ({len(blockers)} issues)

## 🧭 INSTANT NAVIGATION
"""
        
        for file_info in navigation['key_files']:
            dashboard += f"- {file_info}\n"
        
        dashboard += "\n**Quick Commands:**\n"
        for cmd in navigation['commands']:
            dashboard += f"- `{cmd}`\n"
        
        dashboard += f"""
## 📋 CONTEXT
**Next Steps:**
{context['next_steps']}

---
*Dashboard generated in {time.time() - start_time:.2f}s | Target: <2s*
"""
        
        return dashboard
    
    async def save_dashboard(self):
        """Generate and save the dashboard"""
        dashboard = await self.generate_dashboard()
        
        with open(self.output_file, 'w', encoding='utf-8') as f:
            f.write(dashboard)
        
        print(f"✅ AI Dashboard generated: {self.output_file}")
        print(f"📊 Lines: {len(dashboard.split(chr(10)))} (target: <{self.max_lines})")
        
        return dashboard

async def main():
    """Main function to generate the dashboard"""
    generator = AIDashboardGenerator()
    await generator.save_dashboard()

if __name__ == "__main__":
    asyncio.run(main()) 