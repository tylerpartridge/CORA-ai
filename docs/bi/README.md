# CORA BI Engine

## Overview

The CORA Business Intelligence Engine provides structured competitive monitoring and market intelligence gathering to inform product and pricing decisions. The system produces evidence-based reports through systematic competitor sweeps.

## How We Run Sweeps

1. **Registry-Driven:** All targets tracked in `registry.yml` with URLs and tags
2. **Template-Based:** Use `templates/pulse_template.md` for regular sweeps, `templates/profile_template.md` for deep dives
3. **Date-Organized:** Each sweep session creates folder `YYYY-MM-DD/` with pulse and sources
4. **Evidence-First:** All findings documented in `sources.log.md` with timestamps and impact assessment
5. **Human Review:** Findings promoted to awareness docs (NEXT.md) only after human validation

## File Structure

```
docs/bi/
├── README.md                    # This overview
├── registry.yml                 # Competitor URLs and tags
├── templates/
│   ├── pulse_template.md       # Regular market pulse format
│   └── profile_template.md     # Deep competitor profile format
└── YYYY-MM-DD/
    ├── pulse.md                # Market snapshot for date
    └── sources.log.md          # Evidence log with citations
```

## Usage

- **Regular Pulse:** Weekly competitor pricing/feature monitoring
- **Profile Deep-Dive:** Quarterly full competitor analysis
- **Alert-Driven:** Ad-hoc sweeps triggered by market changes
- **Evidence Chain:** All insights traceable to source URLs and timestamps

## How to Run the Snapshot Tool

The BI Snapshot Tool automatically fetches and caches competitor evidence from the registry:

```bash
# Setup virtual environment and install dependencies
python -m venv .venv
.venv/bin/pip install -r scripts/bi/requirements.txt

# Run the snapshot tool
python scripts/bi/snapshot.py

# Or run in dry-run mode (no network calls)
python scripts/bi/snapshot.py --dry-run
```

The tool will:
- Read URLs from `docs/bi/registry.yml`
- Fetch HTML content with 10-second timeout
- Save raw HTML to `docs/bi/cache/YYYY-MM-DD/<slug>.html`
- Extract pricing snippets to `docs/bi/cache/YYYY-MM-DD/<slug>.json`
- Handle errors gracefully with JSON error entries
- Print a summary of all operations