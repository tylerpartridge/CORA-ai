#!/usr/bin/env python3
"""
BI Snapshot Tool - Fetch and cache competitor evidence

Reads docs/bi/registry.yml and fetches HTML content from competitor URLs,
caching raw HTML and extracting pricing snippets when possible.
"""

import os
import sys
import json
import yaml
import requests
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional
from bs4 import BeautifulSoup
import re

# Configuration
REGISTRY_PATH = Path(__file__).parent.parent.parent / "docs/bi/registry.yml"
CACHE_BASE_PATH = Path(__file__).parent.parent.parent / "docs/bi/cache"
REQUEST_TIMEOUT = 10  # seconds
USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"

# Simple selectors for extracting pricing info (can be expanded)
PRICE_SELECTORS = {
    "default": [
        ".pricing", ".price", "[class*='price']", "[class*='pricing']",
        "[data-price]", ".cost", ".rate", ".fee", ".plan-price",
        "span:contains('$')", "div:contains('$')", "p:contains('$')",
        "h1:contains('$')", "h2:contains('$')", "h3:contains('$')"
    ]
}


def load_registry() -> Dict[str, Any]:
    """Load the BI registry YAML file"""
    try:
        with open(REGISTRY_PATH, 'r', encoding='utf-8') as f:
            return yaml.safe_load(f)
    except Exception as e:
        print(f"Error loading registry: {e}")
        return {}


def create_cache_dir() -> Path:
    """Create today's cache directory"""
    today = datetime.now().strftime("%Y-%m-%d")
    cache_dir = CACHE_BASE_PATH / today
    cache_dir.mkdir(parents=True, exist_ok=True)
    return cache_dir


def sanitize_filename(url: str) -> str:
    """Convert URL to safe filename"""
    # Remove protocol
    clean = re.sub(r'^https?://', '', url)
    # Replace special chars with underscores
    clean = re.sub(r'[^\w\-.]', '_', clean)
    # Remove trailing underscores and dots
    clean = clean.strip('_.')
    # Limit length
    if len(clean) > 100:
        clean = clean[:100]
    return clean


def fetch_url(url: str) -> Dict[str, Any]:
    """Fetch content from URL with error handling"""
    try:
        headers = {'User-Agent': USER_AGENT}
        response = requests.get(url, headers=headers, timeout=REQUEST_TIMEOUT)
        response.raise_for_status()
        return {
            "success": True,
            "content": response.text,
            "status_code": response.status_code,
            "url": url
        }
    except requests.RequestException as e:
        return {
            "success": False,
            "error": str(e),
            "url": url
        }


def extract_pricing_snippets(html: str, selectors: List[str]) -> List[str]:
    """Extract pricing-related text snippets from HTML"""
    snippets = []
    try:
        soup = BeautifulSoup(html, 'html.parser')
        
        for selector in selectors:
            # Handle jQuery-style :contains() selector
            if ':contains(' in selector:
                base_selector, contains_text = selector.split(':contains(')
                contains_text = contains_text.rstrip(')')
                contains_text = contains_text.strip("'\"")
                
                if base_selector:
                    elements = soup.select(base_selector)
                else:
                    elements = soup.find_all(text=re.compile(re.escape(contains_text)))
                    elements = [el.parent for el in elements if el.parent]
                
                for elem in elements:
                    if elem and contains_text in elem.get_text():
                        text = elem.get_text(strip=True)
                        if text and len(text) < 500:  # Limit snippet length
                            snippets.append(text)
            else:
                # Standard CSS selector
                elements = soup.select(selector)
                for elem in elements:
                    text = elem.get_text(strip=True)
                    if text and len(text) < 500:
                        snippets.append(text)
        
        # Deduplicate while preserving order
        seen = set()
        unique_snippets = []
        for snippet in snippets:
            if snippet not in seen:
                seen.add(snippet)
                unique_snippets.append(snippet)
        
        return unique_snippets[:20]  # Limit to 20 snippets
        
    except Exception as e:
        print(f"Error extracting snippets: {e}")
        return []


def process_competitor(competitor: Dict[str, Any], cache_dir: Path) -> Dict[str, Any]:
    """Process a single competitor entry"""
    name = competitor.get('name', 'Unknown')
    urls = competitor.get('urls', [])
    
    results = {
        "vendor": name,
        "captured_at": datetime.now().isoformat(),
        "urls_processed": []
    }
    
    for url in urls:
        print(f"  Fetching: {url}")
        
        # Fetch the URL
        fetch_result = fetch_url(url)
        
        # Create filename
        slug = sanitize_filename(url)
        
        # Save result based on success/failure
        if fetch_result['success']:
            # Save HTML
            html_path = cache_dir / f"{slug}.html"
            with open(html_path, 'w', encoding='utf-8') as f:
                f.write(fetch_result['content'])
            
            # Extract pricing snippets
            selectors = PRICE_SELECTORS.get(name.lower(), PRICE_SELECTORS['default'])
            snippets = extract_pricing_snippets(fetch_result['content'], selectors)
            
            # Save JSON with extracted data
            json_data = {
                "vendor": name,
                "url": url,
                "captured_at": datetime.now().isoformat(),
                "snippets": snippets,
                "html_cached": str(html_path.relative_to(CACHE_BASE_PATH))
            }
            
            json_path = cache_dir / f"{slug}.json"
            with open(json_path, 'w', encoding='utf-8') as f:
                json.dump(json_data, f, indent=2)
            
            results["urls_processed"].append({
                "url": url,
                "status": "success",
                "snippets_found": len(snippets)
            })
            
            print(f"    ✓ Cached HTML and found {len(snippets)} snippets")
            
        else:
            # Save error JSON
            json_data = {
                "vendor": name,
                "url": url,
                "captured_at": datetime.now().isoformat(),
                "error": fetch_result['error']
            }
            
            json_path = cache_dir / f"{slug}_error.json"
            with open(json_path, 'w', encoding='utf-8') as f:
                json.dump(json_data, f, indent=2)
            
            results["urls_processed"].append({
                "url": url,
                "status": "error",
                "error": fetch_result['error']
            })
            
            print(f"    ✗ Error: {fetch_result['error']}")
    
    return results


def main(dry_run: bool = False) -> None:
    """Main execution function"""
    print("BI Snapshot Tool")
    print("=" * 50)
    
    # Load registry
    registry = load_registry()
    if not registry:
        print("Failed to load registry. Exiting.")
        return
    
    # Create cache directory
    cache_dir = create_cache_dir()
    print(f"Cache directory: {cache_dir}")
    print()
    
    # Process competitors
    competitors = registry.get('competitors', [])
    regulations = registry.get('regulations_watch', [])
    
    all_results = []
    
    print(f"Processing {len(competitors)} competitors...")
    for competitor in competitors:
        print(f"\n{competitor.get('name', 'Unknown')}:")
        if dry_run:
            print("  [DRY RUN - skipping fetch]")
            continue
        result = process_competitor(competitor, cache_dir)
        all_results.append(result)
    
    print(f"\n\nProcessing {len(regulations)} regulation sources...")
    for regulation in regulations:
        print(f"\n{regulation.get('name', 'Unknown')}:")
        if dry_run:
            print("  [DRY RUN - skipping fetch]")
            continue
        result = process_competitor(regulation, cache_dir)
        all_results.append(result)
    
    # Save summary
    if not dry_run:
        summary_path = cache_dir / "snapshot_summary.json"
        summary = {
            "run_date": datetime.now().isoformat(),
            "total_sources": len(all_results),
            "results": all_results
        }
        with open(summary_path, 'w', encoding='utf-8') as f:
            json.dump(summary, f, indent=2)
    
    # Print summary
    print("\n" + "=" * 50)
    print("Snapshot Summary:")
    if dry_run:
        print("  DRY RUN - No files written")
    else:
        total_urls = sum(len(r.get('urls_processed', [])) for r in all_results)
        successful = sum(1 for r in all_results 
                        for u in r.get('urls_processed', []) 
                        if u['status'] == 'success')
        print(f"  Sources processed: {len(all_results)}")
        print(f"  URLs fetched: {total_urls}")
        print(f"  Successful: {successful}")
        print(f"  Failed: {total_urls - successful}")
        print(f"  Cache directory: {cache_dir}")
    print("=" * 50)


if __name__ == "__main__":
    # Check for dry-run flag
    dry_run = "--dry-run" in sys.argv
    main(dry_run=dry_run)