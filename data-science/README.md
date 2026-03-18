# GovCon Weekly Intelligence — Data Science

This directory contains data analysis work for the GovCon Weekly Intelligence newsletter.

## Contents

### Analysis Documents

1. **eda-awards.md** — Exploratory Data Analysis of govcon_awards_2026-03-18.json
   - Distribution of award amounts (median: $530, mean: $7.5M)
   - Awards by agency, vertical, recipient, set-aside, vehicle
   - Data quality assessment (95%+ null rate on vehicle/NAICS/set-aside fields)
   - Top 20 recipients by value
   - Python code used for analysis

2. **pipeline-improvements.md** — Recommendations for enhancing data pipeline
   - 10 high-impact improvements prioritized by effort/impact
   - Quick wins: Parse descriptions for vehicles, filter $0 awards, add duration fields
   - High-value: SAM.gov API integration, week-over-week comparison, HHI concentration metrics
   - Implementation details with code samples

### Scripts

**analytics.py** — Standalone analytics script (459 lines, no external dependencies)
- Reads awards JSON and outputs summary statistics
- Supports week-over-week comparison with `--compare` flag
- Supports filtering by vertical, agency, amount
- Outputs text or JSON format

**Usage:**
```bash
# Basic stats
python3 analytics.py data/govcon_awards_2026-03-18.json

# Week-over-week comparison
python3 analytics.py data/govcon_awards_2026-03-18.json \
    --compare data/govcon_awards_2026-03-11.json

# Filter to Cloud awards >$1M
python3 analytics.py data/govcon_awards_2026-03-18.json \
    --vertical Cloud --min-amount 1000000

# JSON output
python3 analytics.py data/govcon_awards_2026-03-18.json --format json
```

## Key Findings

### Dataset Overview
- **Total awards:** 1,173
- **Total value:** $8.7B
- **Median award:** $530 (highly skewed distribution)
- **Top 2 awards:** $3.4B (39% of total value) — DOE nuclear cleanup contracts

### Data Quality Issues
- **95.2% null** on set-aside field (critical for small business targeting)
- **97.3% null** on vehicle field (critical for GWAC/IDIQ intelligence)
- **95.7% null** on NAICS codes (incorrect when present)
- **3.0% of awards** have $0 value (should be filtered)

### Market Intelligence
- **Cloud vertical:** 263 awards, $5.9B (highest value)
- **Cybersecurity vertical:** 547 awards, $1.5B (highest volume)
- **FedRAMP premium:** Avg award = $29M (vs $2.8M for non-FedRAMP cyber)
- **GSA volume anomaly:** 788 awards (67%) but only $966M total (avg $1.2M)
- **DOE concentration:** 12 awards, $3.5B (40% of dataset) — dominated by 2 prime contractors

### Competitive Landscape
- **Top 20 recipients** control $6.9B (79% of value)
- **78% of recipients** won only 1 award (winner-take-most dynamic)
- **Major primes:** Leidos, SAIC (Salient CRGT), Accenture Federal, GDIT, Deloitte present
- **Emerging players:** Oddball Inc ($42M), Cognosante ($245M VA DevSecOps)

## Recommendations

### Immediate (Sprint 2)
1. Filter out $0 awards before analysis
2. Parse descriptions for contract vehicle keywords (will enrich 40% of nulls)
3. Add calculated fields: duration, size_bucket, award_age, is_recent
4. Implement week-over-week comparison for newsletter

### Q2 Priorities
1. **SAM.gov API integration** — Pull recipient business type, socioeconomic status, CAGE codes
2. **Historical baseline** — Archive weekly data, build 12-week rolling baseline
3. **Recipient concentration metrics** — Calculate HHI by vertical/agency
4. **Vertical overlap analysis** — Refine multi-tagging logic (currently only 8.5%)

## Data Architecture

```
Pipeline Flow:
USAspending API → pipeline.py → govcon_awards_YYYY-MM-DD.json
                                         ↓
                              analytics.py / generate_insights.py
                                         ↓
                              Newsletter insights + HTML report
```

**Current enrichment sources:**
- USAspending API (base data)
- Vertical keyword matching (9 verticals)
- Regex-based vehicle detection (award ID patterns)
- Regex-based set-aside detection (description text)

**Missing enrichment (Q2):**
- SAM.gov Entity API (recipient business type)
- FPDS (full contract details, better NAICS)
- Historical baseline (trend detection)

## Contact

For questions or contributions, see main project README.
