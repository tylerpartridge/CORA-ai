# BI Snapshot HTTP Overrides Configuration

## Overview

The BI Snapshot tool now supports per-site HTTP configuration overrides to handle challenging sites like QuickBooks (slow) and Jobber (requires Referer header).

## Configuration Format

Add these optional fields to any competitor in `registry.yml`:

```yaml
competitors:
  - name: QuickBooks Online
    urls:
      - https://quickbooks.intuit.com/pricing/
    http:
      timeout: 25  # Increase timeout to 25 seconds (default is 10)
      headers:
        Referer: "https://quickbooks.intuit.com/"
      retries: 5  # More retries for flaky sites (default is 3)
      backoff: 1.0  # Longer backoff between retries (default is 0.6)
    alt_urls:  # Fallback URLs if primary fails
      - https://quickbooks.intuit.com/products/online/
    selectors:
      - "main"
      - "[class*=pricing]"
    tags: ["accounting", "pricing"]

  - name: Jobber
    urls:
      - https://www.getjobber.com/pricing/
    http:
      timeout: 20
      headers:
        Referer: "https://www.getjobber.com/"
        Accept: "text/html,application/xhtml+xml"
    selectors:
      - ".pricing"
      - ".plan"
    tags: ["field-service", "pricing"]
```

## Available HTTP Overrides

### `http` Section
- `timeout`: Request timeout in seconds (default: 10)
- `headers`: Additional headers to send (merged with defaults)
- `retries`: Number of retry attempts (default: 3)
- `backoff`: Backoff factor between retries (default: 0.6)

### `alt_urls` Section
- List of alternative URLs to try if primary URLs fail
- Uses same HTTP settings as primary URL
- Tried in order until one succeeds

## Default Headers

The tool sends these headers by default:
```
User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124 Safari/537.36
Accept-Language: en-US,en;q=0.9
Accept: text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8
```

Custom headers are merged with these defaults.

## Enhanced JSON Output

The tool now captures richer metadata in JSON files:

```json
{
  "vendor": "QuickBooks Online",
  "url": "https://quickbooks.intuit.com/pricing/",
  "final_url": "https://quickbooks.intuit.com/pricing/",
  "http_status": 200,
  "elapsed_ms": 2345,
  "captured_at": "2025-09-02T10:30:45",
  "snippets": ["$15/month", "Simple Start plan", ...],
  "html_cached": "2025-09-02/quickbooks_intuit_com_pricing.html",
  "error": null
}
```

## Error Page Capture (NEW)

The tool now captures HTML content even from error responses (403, 404, etc.) and attempts to extract snippets. This helps gather evidence even when sites block access:

```json
{
  "vendor": "Jobber",
  "url": "https://www.getjobber.com/pricing/",
  "final_url": "https://www.getjobber.com/pricing/",
  "http_status": 403,
  "elapsed_ms": 345,
  "captured_at": "2025-09-02T10:30:45",
  "snippets": ["Access Denied", "Please enable cookies", ...],
  "html_cached": "2025-09-02/getjobber_com_pricing_error.html",
  "error": {
    "type": "http_error",
    "message": "HTTP 403"
  }
}
```

### Benefits of Error Page Capture

1. **Evidence Collection**: Even 403/404 pages often contain useful information
2. **Human Review**: Error pages can be manually reviewed for insights
3. **No Arms Race**: Avoids endless header tweaking; captures what we can
4. **Snippet Extraction**: Attempts to extract text even from error pages

### File Naming Convention

- Success (200-399): `vendor_com.html` and `vendor_com.json`
- Error (400+): `vendor_com_error.html` and `vendor_com_error.json`

### Disabling Error Capture

To disable error page capture (not recommended), modify the tool:
```python
CAPTURE_ON_ERROR = False  # At top of snapshot.py
```

## Manual Fallback Data

When all URLs fail or return zero snippets, the tool can use manual fallback pricing data from the registry. This ensures we always have some pricing information for analysis.

### Configuration

Add a `manual_notes` section to any competitor in `registry.yml`:

```yaml
competitors:
  - name: Difficult Vendor
    urls:
      - https://vendor.com/pricing/
    manual_notes:
      pricing_bullets:
        - "Solo plan: $29/mo (last known)"
        - "Team: $69/mo (hypothesis based on competitors)"
        - "Enterprise: Custom pricing"
      updated: "2025-09-01"
      source_hint: "sales page screenshot / competitor analysis"
    tags: ["fallback-needed"]
```

### How It Works

1. Tool attempts all URLs (including alt_urls) in parallel
2. If total snippets extracted = 0, checks for `manual_notes`
3. If present, merges pricing_bullets into results
4. JSON output includes `status: "manual_fallback"` marker
5. Summary log shows `manual_fallback=Y`

### JSON Output with Manual Fallback

```json
{
  "vendor": "Difficult Vendor",
  "urls_processed": [
    {
      "url": "https://vendor.com/pricing/",
      "status": "error",
      "http_status": 403,
      "elapsed_ms": 234
    },
    {
      "url": "manual_fallback",
      "status": "manual_fallback",
      "snippets_found": 3,
      "manual": {
        "pricing_bullets": [
          "Solo plan: $29/mo (last known)",
          "Team: $69/mo (hypothesis based on competitors)",
          "Enterprise: Custom pricing"
        ],
        "updated": "2025-09-01",
        "source_hint": "sales page screenshot / competitor analysis"
      }
    }
  ]
}
```

### Benefits

- **Always Have Data**: Never completely empty-handed for competitive analysis
- **Track Hypotheses**: Document pricing assumptions when sites block access
- **Historical Reference**: Keep last-known pricing when sites change
- **Human Intelligence**: Incorporate manual research and sales calls

## Example Registry Updates for Common Issues

### Slow Sites (Increase Timeout)
```yaml
http:
  timeout: 30  # 30 seconds for very slow sites
```

### Sites Requiring Referer
```yaml
http:
  headers:
    Referer: "https://example.com/"
```

### Sites with Rate Limiting
```yaml
http:
  retries: 5
  backoff: 2.0  # Wait longer between retries
```

### Sites with Multiple URLs
```yaml
urls:
  - https://primary.example.com/pricing/
alt_urls:
  - https://www.example.com/plans/
  - https://example.com/products/pricing/
```

## Testing Configuration

Run with dry-run to verify configuration loads correctly:
```bash
python scripts/bi/snapshot.py --dry-run
```

Then run normally to test actual fetching:
```bash
python scripts/bi/snapshot.py
```

Check the logs and JSON files for success/failure details:
- Logs: `docs/bi/YYYY-MM-DD/snapshot.log`
- JSON: `docs/bi/cache/YYYY-MM-DD/*.json`