# Generated: 2025-07-11 by SmartHeaderGenerator v1.0
"""
🧭 LOCATION: CORA/.archive/2025/01/11/root_cleanup/cleanup_script.py
🎯 PURPOSE: [Auto-generated header - could not analyze file]
🔗 IMPORTS: [Unknown]
📤 EXPORTS: [Unknown]
🔄 PATTERN: [Unknown]
📝 TODOS: [Unknown]
💡 AI HINT: [Unknown]
⚠️ NEVER: [Unknown]
"""

🧭 LOCATION: /CORA/.archive\2025\01\11\root_cleanup\cleanup_script.py
🎯 PURPOSE: [To be determined - please update]
🔗 IMPORTS: [To be determined - please update]
📤 EXPORTS: [To be determined - please update]
🔄 PATTERN: [To be determined - please update]
📝 TODOS: [To be determined - please update]
"""

#!/usr/bin/env python3
# Auto-generated cleanup script - Review before running!
import os
import shutil
from pathlib import Path

def cleanup():
    removed_count = 0
    freed_space = 0

    # Clean __pycache__ directories
    if Path('C:\CORA\__pycache__').exists():
        shutil.rmtree('C:\CORA\__pycache__')
        removed_count += 4
        freed_space += 40945
    if Path('C:\CORA\middleware\__pycache__').exists():
        shutil.rmtree('C:\CORA\middleware\__pycache__')
        removed_count += 4
        freed_space += 13220
    if Path('C:\CORA\models\__pycache__').exists():
        shutil.rmtree('C:\CORA\models\__pycache__')
        removed_count += 18
        freed_space += 74829
    if Path('C:\CORA\routes\__pycache__').exists():
        shutil.rmtree('C:\CORA\routes\__pycache__')
        removed_count += 34
        freed_space += 332569
    if Path('C:\CORA\tools\__pycache__').exists():
        shutil.rmtree('C:\CORA\tools\__pycache__')
        removed_count += 81
        freed_space += 962958
    if Path('C:\CORA\utils\__pycache__').exists():
        shutil.rmtree('C:\CORA\utils\__pycache__')
        removed_count += 4
        freed_space += 14686
    if Path('C:\CORA\tools\agents\__pycache__').exists():
        shutil.rmtree('C:\CORA\tools\agents\__pycache__')
        removed_count += 11
        freed_space += 175185
    if Path('C:\CORA\tools\context\__pycache__').exists():
        shutil.rmtree('C:\CORA\tools\context\__pycache__')
        removed_count += 8
        freed_space += 165560
    if Path('C:\CORA\tools\context\modules\__pycache__').exists():
        shutil.rmtree('C:\CORA\tools\context\modules\__pycache__')
        removed_count += 10
        freed_space += 68146
    if Path('C:\CORA\tools\agents\patterns\__pycache__').exists():
        shutil.rmtree('C:\CORA\tools\agents\patterns\__pycache__')
        removed_count += 4
        freed_space += 9830
    if Path('C:\CORA\tools\agents\utils\__pycache__').exists():
        shutil.rmtree('C:\CORA\tools\agents\utils\__pycache__')
        removed_count += 7
        freed_space += 70638
    if Path('C:\CORA\tools\agents\validators\__pycache__').exists():
        shutil.rmtree('C:\CORA\tools\agents\validators\__pycache__')
        removed_count += 14
        freed_space += 176746
    if Path('C:\CORA\.claude\state\__pycache__').exists():
        shutil.rmtree('C:\CORA\.claude\state\__pycache__')
        removed_count += 4
        freed_space += 68456
    if Path('C:\CORA\.claude\state\modules\__pycache__').exists():
        shutil.rmtree('C:\CORA\.claude\state\modules\__pycache__')
        removed_count += 2
        freed_space += 357
    if Path('C:\CORA\.claude\state\modules\compression\__pycache__').exists():
        shutil.rmtree('C:\CORA\.claude\state\modules\compression\__pycache__')
        removed_count += 10
        freed_space += 59663


    print(f'Removed {removed_count} files')
    print(f'Freed {freed_space / 1024 / 1024:.2f} MB')

if __name__ == '__main__':
    if input('Run cleanup? (y/n): ').lower() == 'y':
        cleanup()
    else:
        print('Cleanup cancelled')