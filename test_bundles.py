
import sys
from pathlib import Path
# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

import requests

response = requests.get('http://localhost:8000/')
html = response.text

print("Bundle loading test:")
print(f"Module script tags: {html.count('script type=\"module\"')}")
print(f"Performance bundle: {'performance.js' in html}")
print(f"Accessibility bundle: {'accessibility.js' in html}")
print(f"Error manager bundle: {'error-manager.js' in html}")
print(f"Timeout handler bundle: {'timeout-handler.js' in html}")
print(f"Web vitals bundle: {'web-vitals-monitoring.js' in html}")

# Check for hashed bundles
if 'bundles/performance.' in html:
    print("✅ Hashed bundles detected")
else:
    print("❌ No hashed bundles found") 