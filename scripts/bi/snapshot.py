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
from datetime import datetime, date
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
from bs4 import BeautifulSoup
import re
import logging
import time
from urllib3.util.retry import Retry
from requests.adapters import HTTPAdapter
from concurrent.futures import ThreadPoolExecutor, as_completed
import threading

# Configuration
REGISTRY_PATH = Path(__file__).parent.parent.parent / "docs/bi/registry.yml"
CACHE_BASE_PATH = Path(__file__).parent.parent.parent / "docs/bi/cache"
REQUEST_TIMEOUT = 10  # seconds
CAPTURE_ON_ERROR = True  # Capture HTML even on 403/404 responses

# Simple selectors for extracting pricing info (can be expanded)
PRICE_SELECTORS = {
    "default": [
        ".pricing", ".price", "[class*='price']", "[class*='pricing']",
        "[data-price]", ".cost", ".rate", ".fee", ".plan-price",
        "span:contains('$')", "div:contains('$')", "p:contains('$')",
        "h1:contains('$')", "h2:contains('$')", "h3:contains('$')"
    ]
}

# Logger instance (will be set up in main)
logger = None


def setup_logger(log_path: Path) -> logging.Logger:
    """Set up ASCII-safe logger that writes to both stdout and UTF-8 file"""
    # Create logger
    logger = logging.getLogger('bi_snapshot')
    logger.setLevel(logging.INFO)
    
    # Clear any existing handlers
    logger.handlers.clear()
    
    # Create formatter with ASCII-only format
    formatter = logging.Formatter('%(asctime)s %(levelname)s: %(message)s')
    
    # Console handler (stdout)
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    
    # File handler (UTF-8 encoding)
    log_path.parent.mkdir(parents=True, exist_ok=True)
    file_handler = logging.FileHandler(log_path, encoding='utf-8')
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)
    
    return logger


def make_session(retries: int = 3, backoff: float = 0.6) -> requests.Session:
    """Create HTTP session with headers and retry logic"""
    session = requests.Session()
    
    # Set default headers
    session.headers.update({
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124 Safari/537.36',
        'Accept-Language': 'en-US,en;q=0.9',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8'
    })
    
    # Configure retries
    retry_strategy = Retry(
        total=retries,
        backoff_factor=backoff,
        status_forcelist=[429, 500, 502, 503, 504]
    )
    adapter = HTTPAdapter(max_retries=retry_strategy)
    session.mount("https://", adapter)
    session.mount("http://", adapter)
    
    return session


def load_registry() -> Dict[str, Any]:
    """Load the BI registry YAML file"""
    global logger
    try:
        with open(REGISTRY_PATH, 'r', encoding='utf-8') as f:
            return yaml.safe_load(f)
    except Exception as e:
        if logger:
            logger.error("Error loading registry: %s", str(e))
        else:
            print(f"Error loading registry: {e}")
        return {}


def create_cache_dir(date_str: str = None) -> Path:
    """Create cache directory for given date (or today)"""
    if date_str is None:
        date_str = date.today().isoformat()  # YYYY-MM-DD format
    cache_dir = CACHE_BASE_PATH / date_str
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


def fetch_single_url(url: str, session: requests.Session, 
                    timeout: int, custom_headers: Dict[str, str]) -> Dict[str, Any]:
    """Fetch a single URL with timing and error handling"""
    try:
        # Prepare headers for this request
        request_headers = {}
        if custom_headers:
            request_headers.update(custom_headers)
        
        # Time the request
        start_time = time.time()
        response = session.get(url, timeout=timeout, headers=request_headers)
        elapsed_ms = int((time.time() - start_time) * 1000)
        
        # Capture response regardless of status
        status_code = response.status_code
        response_content = response.text
        final_url = response.url
        
        # Check if this is an error response but we still got HTML
        if CAPTURE_ON_ERROR and status_code >= 400:
            # We got an error page, but capture it anyway
            return {
                "success": False,  # Mark as failure but include content
                "content": response_content,
                "http_status": status_code,
                "url": url,
                "final_url": final_url,
                "elapsed_ms": elapsed_ms,
                "error": {
                    "type": "http_error",
                    "message": f"HTTP {status_code}"[:200]
                },
                "has_content": True  # Flag that we have content despite error
            }
        
        # Success case (2xx, 3xx)
        if status_code < 400:
            return {
                "success": True,
                "content": response_content,
                "http_status": status_code,
                "url": url,
                "final_url": final_url,
                "elapsed_ms": elapsed_ms,
                "error": None
            }
        
        # If CAPTURE_ON_ERROR is False, raise the error
        response.raise_for_status()
        
    except requests.Timeout as e:
        elapsed_ms = int((time.time() - start_time) * 1000) if 'start_time' in locals() else timeout * 1000
        return {
            "success": False,
            "url": url,
            "final_url": None,
            "http_status": None,
            "elapsed_ms": elapsed_ms,
            "error": {
                "type": "timeout",
                "message": f"Request timed out after {timeout}s"
            },
            "has_content": False
        }
        
    except requests.HTTPError as e:
        # This only happens if CAPTURE_ON_ERROR is False
        elapsed_ms = int((time.time() - start_time) * 1000) if 'start_time' in locals() else 0
        return {
            "success": False,
            "url": url,
            "final_url": None,
            "http_status": e.response.status_code if e.response else None,
            "elapsed_ms": elapsed_ms,
            "error": {
                "type": "http_error", 
                "message": str(e)[:200]
            },
            "has_content": False
        }
        
    except requests.RequestException as e:
        elapsed_ms = int((time.time() - start_time) * 1000) if 'start_time' in locals() else 0
        return {
            "success": False,
            "url": url,
            "final_url": None,
            "http_status": None,
            "elapsed_ms": elapsed_ms,
            "error": {
                "type": "request_error",
                "message": str(e)[:200]
            },
            "has_content": False
        }


def fetch_url_with_overrides(url: str, session: requests.Session, 
                             http_config: Dict[str, Any] = None,
                             alt_urls: List[str] = None) -> Dict[str, Any]:
    """Fetch content from URL with parallel alt URLs and per-site overrides"""
    global logger
    
    # Extract settings from http_config
    timeout = REQUEST_TIMEOUT
    custom_headers = {}
    
    if http_config:
        timeout = http_config.get('timeout', REQUEST_TIMEOUT)
        custom_headers = http_config.get('headers', {})
    
    # Build URL list: primary + alternates
    urls_to_try = [url]
    if alt_urls:
        urls_to_try.extend(alt_urls)
    
    # Track all attempts for metadata
    attempts = []
    best_result = None
    best_snippet_count = -1
    
    # Try URLs in parallel
    with ThreadPoolExecutor(max_workers=min(len(urls_to_try), 3)) as executor:
        # Submit all URLs
        future_to_url = {
            executor.submit(fetch_single_url, u, session, timeout, custom_headers): u 
            for u in urls_to_try
        }
        
        # Process completed requests
        for future in as_completed(future_to_url):
            attempt_url = future_to_url[future]
            try:
                result = future.result()
                
                # Record attempt
                attempt_record = {
                    "url": attempt_url,
                    "status": "success" if result.get("success") else "error",
                    "http_status": result.get("http_status"),
                    "elapsed_ms": result.get("elapsed_ms"),
                }
                if not result.get("success") and result.get("error"):
                    attempt_record["error_type"] = result["error"].get("type")
                attempts.append(attempt_record)
                
                # Determine if this is the best result so far
                if result.get("success"):
                    # Success always beats failure
                    if best_result is None or not best_result.get("success"):
                        best_result = result
                        best_snippet_count = 0  # Will count later
                    # Among successes, prefer the one with content
                    elif result.get("content"):
                        # Quick snippet count estimate
                        content = result.get("content", "")
                        snippet_count = content.lower().count("$") + content.lower().count("pricing")
                        if snippet_count > best_snippet_count:
                            best_result = result
                            best_snippet_count = snippet_count
                elif result.get("has_content"):
                    # Error page with content is better than nothing
                    if best_result is None:
                        best_result = result
                        
            except Exception as e:
                # Record failed attempt
                attempts.append({
                    "url": attempt_url,
                    "status": "error",
                    "http_status": None,
                    "elapsed_ms": 0,
                    "error_type": "exception",
                    "error_message": str(e)[:100]
                })
    
    # If we have a best result, add attempts metadata
    if best_result:
        best_result["attempts"] = attempts
        return best_result
    
    # All URLs failed - return failure with attempts
    return {
        "success": False,
        "url": url,
        "final_url": None,
        "http_status": None,
        "elapsed_ms": sum(a.get("elapsed_ms", 0) for a in attempts),
        "error": {
            "type": "all_failed",
            "message": f"All {len(attempts)} URLs failed"
        },
        "has_content": False,
        "attempts": attempts
    }


def extract_pricing_snippets(html: str, selectors: List[str] = None) -> List[str]:
    """Extract pricing-related text snippets from HTML"""
    global logger
    snippets = []
    
    try:
        soup = BeautifulSoup(html, 'html.parser')
        
        # Try CSS selectors if provided
        if selectors:
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
                            text = elem.get_text(" ", strip=True)
                            if text and len(text) < 500:  # Limit snippet length
                                snippets.append(text)
                else:
                    # Standard CSS selector
                    try:
                        elements = soup.select(selector)
                        for elem in elements:
                            text = elem.get_text(" ", strip=True)
                            if text and len(text) < 500:
                                snippets.append(text)
                    except Exception:
                        continue  # Skip invalid selectors
        
        # Fallback: regex search for pricing patterns
        if len(snippets) < 5:  # If not enough snippets from selectors
            text_content = soup.get_text(" ", strip=True)
            pricing_pattern = r'(?i)(\$\s?\d+[\d,]*(?:\.\d{1,2})?|free|unlimited users?)'
            
            for match in re.finditer(pricing_pattern, text_content):
                start = max(0, match.start() - 45)
                end = min(len(text_content), match.end() + 45)
                context = text_content[start:end].strip()
                
                if context and len(context) > 10 and context not in snippets:
                    snippets.append(context)
        
        # Deduplicate while preserving order
        seen = set()
        unique_snippets = []
        for snippet in snippets:
            if snippet not in seen:
                seen.add(snippet)
                unique_snippets.append(snippet)
        
        return unique_snippets[:20]  # Limit to 20 snippets
        
    except Exception as e:
        if logger:
            logger.error("Error extracting snippets: %s", str(e)[:200])
        return []


def process_competitor(competitor: Dict[str, Any], cache_dir: Path, session: requests.Session) -> Dict[str, Any]:
    """Process a single competitor entry with per-site overrides and manual fallback"""
    global logger
    name = competitor.get('name', 'Unknown')
    urls = competitor.get('urls', [])
    selectors = competitor.get('selectors')  # Optional custom selectors
    http_config = competitor.get('http')  # Optional HTTP overrides
    alt_urls = competitor.get('alt_urls', [])  # Optional alternate URLs
    manual_notes = competitor.get('manual_notes')  # Optional manual fallback data
    
    # Check if we need a custom session for this competitor
    if http_config and ('retries' in http_config or 'backoff' in http_config):
        # Create custom session with specific retry settings
        custom_retries = http_config.get('retries', 3)
        custom_backoff = http_config.get('backoff', 0.6)
        custom_session = make_session(retries=custom_retries, backoff=custom_backoff)
    else:
        custom_session = session
    
    results = {
        "vendor": name,
        "captured_at": datetime.now().isoformat(),
        "urls_processed": []
    }
    
    for url in urls:
        logger.info("  Fetching: %s", url)
        
        # Fetch the URL with overrides
        fetch_result = fetch_url_with_overrides(url, custom_session, http_config, alt_urls)
        
        # Create filename based on original URL
        slug = sanitize_filename(url)
        
        # Check if we have content to save (success or error with content)
        has_content = fetch_result.get('has_content', False) or fetch_result['success']
        
        if has_content and 'content' in fetch_result:
            # Determine file path based on success/failure
            if fetch_result['success']:
                html_path = cache_dir / f"{slug}.html"
            else:
                html_path = cache_dir / f"{slug}_error.html"
            
            # Save HTML (works for both success and error pages)
            with open(html_path, 'w', encoding='utf-8') as f:
                f.write(fetch_result['content'])
            
            # Extract pricing snippets even from error pages
            if selectors:
                snippets = extract_pricing_snippets(fetch_result['content'], selectors)
            else:
                snippets = extract_pricing_snippets(fetch_result['content'], PRICE_SELECTORS['default'])
            
            # Save JSON with richer metadata
            json_data = {
                "vendor": name,
                "url": url,
                "final_url": fetch_result.get('final_url'),
                "http_status": fetch_result.get('http_status'),
                "elapsed_ms": fetch_result.get('elapsed_ms'),
                "captured_at": datetime.now().isoformat(),
                "snippets": snippets,
                "html_cached": str(html_path.relative_to(CACHE_BASE_PATH)),
                "error": fetch_result.get('error')
            }
            
            # Choose JSON filename based on success/failure
            if fetch_result['success']:
                json_path = cache_dir / f"{slug}.json"
            else:
                json_path = cache_dir / f"{slug}_error.json"
            
            with open(json_path, 'w', encoding='utf-8') as f:
                json.dump(json_data, f, indent=2, ensure_ascii=False)
            
            # Update results
            if fetch_result['success']:
                results["urls_processed"].append({
                    "url": url,
                    "status": "success",
                    "http_status": fetch_result.get('http_status'),
                    "elapsed_ms": fetch_result.get('elapsed_ms'),
                    "snippets_found": len(snippets)
                })
                
                logger.info("    %s: [OK] cached HTML; snippets=%d status=%s elapsed=%dms", 
                           name, len(snippets), fetch_result.get('http_status'), fetch_result.get('elapsed_ms'))
            else:
                # Error but we captured the HTML
                error_info = fetch_result.get('error', {})
                error_type = error_info.get('type', 'unknown')
                error_msg = error_info.get('message', 'Unknown error')[:200]
                
                results["urls_processed"].append({
                    "url": url,
                    "status": "error",
                    "http_status": fetch_result.get('http_status'),
                    "elapsed_ms": fetch_result.get('elapsed_ms'),
                    "error_type": error_type,
                    "error": error_msg,
                    "snippets_found": len(snippets)
                })
                
                logger.error("    %s: [ERR] status=%s; cached error HTML; snippets=%d elapsed=%dms", 
                            name, fetch_result.get('http_status'), len(snippets), fetch_result.get('elapsed_ms', 0))
        
        else:
            # No content available (network error, timeout, etc.)
            error_info = fetch_result.get('error', {})
            error_type = error_info.get('type', 'unknown')
            error_msg = error_info.get('message', 'Unknown error')[:200]
            
            # Save error JSON without HTML reference
            json_data = {
                "vendor": name,
                "url": url,
                "final_url": fetch_result.get('final_url'),
                "http_status": fetch_result.get('http_status'),
                "elapsed_ms": fetch_result.get('elapsed_ms'),
                "captured_at": datetime.now().isoformat(),
                "snippets": [],
                "html_cached": None,
                "error": {
                    "type": error_type,
                    "message": error_msg
                }
            }
            
            json_path = cache_dir / f"{slug}_error.json"
            with open(json_path, 'w', encoding='utf-8') as f:
                json.dump(json_data, f, indent=2, ensure_ascii=False)
            
            results["urls_processed"].append({
                "url": url,
                "status": "error",
                "http_status": fetch_result.get('http_status'),
                "elapsed_ms": fetch_result.get('elapsed_ms'),
                "error_type": error_type,
                "error": error_msg
            })
            
            logger.error("    %s: [ERR] %s (%s) elapsed=%dms", 
                        name, error_msg, error_type, fetch_result.get('elapsed_ms', 0))
    
    # Check if we need manual fallback
    total_snippets = sum(r.get('snippets_found', 0) for r in results["urls_processed"])
    used_manual_fallback = False
    
    if total_snippets == 0 and manual_notes and manual_notes.get('pricing_bullets'):
        # Use manual fallback data
        manual_bullets = manual_notes.get('pricing_bullets', [])
        manual_updated = manual_notes.get('updated', 'unknown')
        manual_source = manual_notes.get('source_hint', 'manual entry')
        
        # Add manual fallback to results
        results["manual_fallback"] = {
            "pricing_bullets": manual_bullets,
            "updated": manual_updated,
            "source_hint": manual_source
        }
        results["urls_processed"].append({
            "url": "manual_fallback",
            "status": "manual_fallback",
            "snippets_found": len(manual_bullets),
            "manual": {
                "pricing_bullets": manual_bullets,
                "updated": manual_updated,
                "source_hint": manual_source
            }
        })
        used_manual_fallback = True
        total_snippets = len(manual_bullets)
        
        logger.info("    %s: [MANUAL] Using fallback data; bullets=%d updated=%s", 
                   name, len(manual_bullets), manual_updated)
    
    # Add attempts metadata if available
    if fetch_result and fetch_result.get('attempts'):
        results["attempts"] = fetch_result.get('attempts')
    
    # Log summary line
    success_count = sum(1 for r in results["urls_processed"] if r.get('status') == 'success')
    urls_tried = len([r for r in results["urls_processed"] if r.get('status') != 'manual_fallback'])
    best_url = fetch_result.get('final_url') or fetch_result.get('url') if fetch_result else 'none'
    
    logger.info("[SUMMARY] %s: success=%s, manual_fallback=%s, urls_tried=%d, best_url=%s, total_snippets=%d",
               name, 
               "Y" if success_count > 0 else "N",
               "Y" if used_manual_fallback else "N",
               urls_tried,
               best_url,
               total_snippets)
    
    return results


def main(dry_run: bool = False) -> None:
    """Main execution function"""
    global logger
    
    # Use consistent date for both cache and logs
    today_str = date.today().isoformat()
    
    # Set up logging
    log_dir = Path(__file__).parent.parent.parent / "docs/bi" / today_str
    log_path = log_dir / "snapshot.log"
    logger = setup_logger(log_path)
    
    logger.info("BI Snapshot Tool")
    logger.info("=" * 50)
    
    # Load registry
    registry = load_registry()
    if not registry:
        logger.error("Failed to load registry. Exiting.")
        return
    
    # Create cache directory with same date
    cache_dir = create_cache_dir(today_str)
    logger.info("Cache directory: %s", cache_dir)
    logger.info("")
    
    # Create HTTP session
    session = make_session()
    
    # Process competitors
    competitors = registry.get('competitors', [])
    regulations = registry.get('regulations_watch', [])
    
    all_results = []
    
    logger.info("Processing %d competitors...", len(competitors))
    for competitor in competitors:
        logger.info("")
        logger.info("%s:", competitor.get('name', 'Unknown'))
        if dry_run:
            logger.info("  [DRY RUN - skipping fetch]")
            continue
        result = process_competitor(competitor, cache_dir, session)
        all_results.append(result)
    
    logger.info("")
    logger.info("")
    logger.info("Processing %d regulation sources...", len(regulations))
    for regulation in regulations:
        logger.info("")
        logger.info("%s:", regulation.get('name', 'Unknown'))
        if dry_run:
            logger.info("  [DRY RUN - skipping fetch]")
            continue
        result = process_competitor(regulation, cache_dir, session)
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
            json.dump(summary, f, indent=2, ensure_ascii=False)
    
    # Print summary
    logger.info("")
    logger.info("=" * 50)
    logger.info("Snapshot Summary:")
    if dry_run:
        logger.info("  DRY RUN - No files written")
    else:
        total_urls = sum(len(r.get('urls_processed', [])) for r in all_results)
        successful = sum(1 for r in all_results 
                        for u in r.get('urls_processed', []) 
                        if u['status'] == 'success')
        logger.info("  Sources processed: %d", len(all_results))
        logger.info("  URLs fetched: %d", total_urls)
        logger.info("  Successful: %d", successful)
        logger.info("  Failed: %d", total_urls - successful)
        logger.info("  Cache directory: %s", cache_dir)
        logger.info("  Log file: %s", log_path)
    logger.info("=" * 50)


if __name__ == "__main__":
    # Check for dry-run flag
    dry_run = "--dry-run" in sys.argv
    main(dry_run=dry_run)