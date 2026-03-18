# GovCon Intelligence Newsletter

Weekly intelligence brief on federal contract awards, powered by USAspending API data. Designed to run every Sunday night and produce Monday's newsletter.

Tracks 9 verticals: AI/ML, Cybersecurity, Cloud, Data Analytics, DevSecOps, Zero Trust, FedRAMP, Identity Management, Networking/SDWAN.

## Quick Start

```bash
cd ~/Personal/govcon-intel
./generate.sh              # Generate this week's report (last 7 days)
./generate.sh --days 14    # Custom lookback window
./generate.sh --dry-run    # Pull data only, skip report generation
```

## File Structure

```
govcon-intel/
├── generate.sh                # Master pipeline script (run this)
├── pipeline.py                # USAspending API data pull + enrichment
├── README.md
├── SAMPLE_REPORT_V2.md        # Report template / reference format (to create)
│
├── generate_report.py         # Markdown report generator (to create)
├── generate_insights.py       # AI-powered insights layer (to create)
├── report_to_html.py          # Markdown to newsletter HTML (to create)
│
├── data/                      # Raw data from API pulls
│   ├── govcon_awards_YYYY-MM-DD.json
│   └── govcon_awards_YYYY-MM-DD.csv
│
├── output/                    # Generated newsletter outputs (date-stamped)
│   ├── data_YYYY-MM-DD.json
│   ├── report_YYYY-MM-DD.md
│   ├── report_YYYY-MM-DD.html
│   └── insights_YYYY-MM-DD.md
│
└── landing/                   # Landing page assets
```

## Pipeline Steps

| Step | Script | What it does | Status |
|------|--------|-------------|--------|
| 1. Pull data | `pipeline.py` | Pulls awards from USAspending API by vertical keywords, de-duplicates, enriches with NAICS/vehicle/set-aside | Done |
| 2. Generate report | `generate_report.py` | Transforms raw data into V2 newsletter format | To build |
| 3. Generate insights | `generate_insights.py` | AI-generated trend detection + "so what" commentary | To build |
| 4. Generate HTML | `report_to_html.py` | Converts markdown to Beehiiv-compatible HTML | To build |

The pipeline is resilient -- if a component script doesn't exist yet, it skips that step and continues. Build incrementally.

## How pipeline.py Works

1. Searches USAspending `/search/spending_by_award/` for each vertical's keyword list
2. De-duplicates by `generated_internal_id`, cross-tags awards matching multiple verticals
3. Detects contract vehicles (OASIS, STARS III, CIO-SP3, SEWP, etc.) from award ID patterns
4. Detects set-asides (8(a), SDVOSB, HUBZone, WOSB) from description text
5. Enriches up to 50 awards with NAICS codes from the award detail API
6. Outputs sorted JSON + CSV to `data/`

## What's Needed to Launch

**Already have:**
- Data pull pipeline (`pipeline.py`) -- working, pulls from USAspending API
- Pipeline orchestration (`generate.sh`) -- runs full end-to-end flow
- Output directory structure

**Scripts to build:**
- `generate_report.py` -- Transform raw award data into the V2 report format. Could use Claude API for narrative sections.
- `SAMPLE_REPORT_V2.md` -- Report template that generate_report.py renders into.
- `generate_insights.py` -- Trend detection, anomaly flagging, week-over-week comparisons. Claude API recommended.
- `report_to_html.py` -- Converts markdown to Beehiiv-compatible HTML with inline styles.

**External setup:**
- **USAspending API** -- Free, no key required. Already integrated. https://api.usaspending.gov/
- **SAM.gov API key** -- Free at https://open.gsa.gov/api/entity-api/. Needed for entity enrichment (contractor details, past performance).
- **Beehiiv account** -- Newsletter distribution. Import the HTML output or use their API. https://www.beehiiv.com/
- **Claude API key** (optional) -- For AI-generated narrative sections and insights. Set `ANTHROPIC_API_KEY` env var.

## Running on a Schedule

For Sunday night automation (cron):

```bash
crontab -e

# Run every Sunday at 9 PM PT
0 21 * * 0 cd ~/Personal/govcon-intel && ./generate.sh >> output/cron.log 2>&1
```

Or use launchd on macOS for better reliability (survives sleep/wake).
