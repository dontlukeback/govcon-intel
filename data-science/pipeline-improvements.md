# Pipeline Improvement Recommendations

**Date:** 2026-03-18
**Analyst:** Data Scientist
**Context:** Based on EDA of `govcon_awards_2026-03-18.json` and review of `pipeline.py` and `generate_insights.py`

---

## Executive Summary

The current pipeline successfully pulls awards from USAspending API, de-duplicates, and tags verticals. However, **95%+ of enrichment fields (vehicle, set-aside, NAICS) are null**, severely limiting competitive intelligence value. This document outlines 10 high-impact improvements across data enrichment, quality checks, and analytical capabilities.

**Quick Wins (implement in Sprint 2):**
1. Parse descriptions for contract vehicle keywords (will enrich ~40% of nulls)
2. Filter out $0 awards before analysis
3. Add week-over-week comparison script
4. Calculate contract duration field

**High-Value Investments (Q2):**
5. SAM.gov Entity API integration for recipient enrichment
6. Historical baseline builder for trend detection
7. Recipient concentration metrics (HHI)
8. Vertical overlap scoring

---

## 1. Contract Vehicle Detection (Description Parsing)

**Problem:** 97.3% of awards have null `vehicle` field. Current logic only checks award ID patterns (lines 239-246 in pipeline.py).

**Solution:** Expand `detect_vehicle()` to parse award descriptions for vehicle keywords.

### Implementation

```python
# Add to pipeline.py after line 167
VEHICLE_KEYWORDS = {
    "GSA OASIS": ["oasis", "gs00q", "47qr"],
    "STARS III": ["stars iii", "stars 3", "47qtcb"],
    "STARS II": ["stars ii", "stars 2"],
    "8(a) STARS II": ["8(a) stars", "8a stars ii"],
    "CIO-SP3": ["cio-sp3", "ciosp3", "cios3", "75n98"],
    "CIO-SP4": ["cio-sp4", "ciosp4", "cios4"],
    "SEWP": ["sewp", "solutions for enterprise-wide procurement", "nng15s"],
    "ALLIANT 2": ["alliant 2", "alliant ii", "alliant2", "47qtc"],
    "VETS 2": ["vets 2", "vets ii", "veteran-owned small business"],
    "NITAAC": ["nitaac", "nih information technology"],
    "OASIS+": ["oasis+", "oasis plus"],
    "GSA Schedule 70": ["schedule 70", "gsa schedule", "multiple award schedule"],
    "Chess": ["chess", "computer hardware enterprise"],
    "EIS": ["eis", "enterprise infrastructure solutions"],
}

def detect_vehicle_enhanced(award_id, generated_id, description):
    """Detect contract vehicle from IDs and description text."""
    # First try ID patterns (existing logic)
    combined_id = f"{award_id or ''} {generated_id or ''}"
    for vehicle, patterns in VEHICLE_PATTERNS.items():
        for pat in patterns:
            if re.search(pat, combined_id, re.IGNORECASE):
                return vehicle

    # Then try description keywords
    if description:
        desc_lower = description.lower()
        for vehicle, keywords in VEHICLE_KEYWORDS.items():
            for kw in keywords:
                if kw in desc_lower:
                    return vehicle

    return None
```

**Update line 396:**
```python
award["vehicle"] = detect_vehicle_enhanced(award["award_id"], gid, award["description"])
```

**Expected Impact:** Vehicle detection rate should increase from 3% to 40-50% (based on manual review of top 100 awards).

---

## 2. Recipient Enrichment via SAM.gov Entity API

**Problem:** 95.2% of awards lack set-aside classification. We can't identify 8(a), SDVOSB, HUBZone, WOSB opportunities without recipient business size data.

**Solution:** Integrate SAM.gov Entity Management API to pull:
- Business size (small, large)
- Socioeconomic status (8(a), SDVOSB, HUBZone, WOSB, EDWOSB)
- NAICS codes (primary + secondary)
- CAGE code
- UEI (Unique Entity Identifier)
- Active registrations (is entity still SAM-registered?)

### Implementation

```python
# Add to pipeline.py after imports
import os
import time

SAM_API_KEY = os.getenv("SAM_API_KEY")  # Get free API key from https://open.gsa.gov/api/entity-api/
SAM_ENTITY_ENDPOINT = "https://api.sam.gov/entity-information/v3/entities"

def enrich_from_sam(recipient_name):
    """Look up recipient in SAM.gov and return enrichment data."""
    if not SAM_API_KEY:
        return {}

    # Search by legal business name
    params = {
        "api_key": SAM_API_KEY,
        "legalBusinessName": recipient_name,
        "includeSections": "entityRegistration,coreData"
    }

    try:
        result = subprocess.run(
            ["curl", "-s", "--max-time", "10", "-G", SAM_ENTITY_ENDPOINT,
             "--data-urlencode", f"api_key={SAM_API_KEY}",
             "--data-urlencode", f"legalBusinessName={recipient_name}",
             "--data-urlencode", "includeSections=entityRegistration,coreData"],
            capture_output=True, text=True, timeout=15
        )
        if result.returncode != 0:
            return {}

        data = json.loads(result.stdout)
        entities = data.get("entityData", [])
        if not entities:
            return {}

        entity = entities[0]  # Take first match
        core = entity.get("coreData", {})
        reg = entity.get("entityRegistration", {})

        return {
            "business_type": core.get("businessTypes", []),
            "cage_code": core.get("cageCode"),
            "uei": core.get("ueiSAM"),
            "primary_naics": core.get("primaryNaics"),
            "is_small_business": "Small Business" in core.get("businessTypes", []),
            "is_8a": "8(a) Program Participant" in core.get("businessTypes", []),
            "is_sdvosb": "Service-Disabled Veteran-Owned Small Business" in core.get("businessTypes", []),
            "is_hubzone": "Historically Underutilized Business Zone (HUBZone) Firm" in core.get("businessTypes", []),
            "is_wosb": "Women-Owned Small Business" in core.get("businessTypes", []),
            "expiration_date": reg.get("expirationDate"),
        }
    except Exception as e:
        log(f"  [warn] SAM.gov lookup failed for {recipient_name}: {e}")
        return {}

# Add after line 408 in main() pipeline
log(f"\nEnriching recipients from SAM.gov...")
sam_enriched = 0
unique_recipients = list(set(a["recipient_name"] for a in awards_map.values()))
log(f"  Unique recipients: {len(unique_recipients)}")

# Cache SAM lookups to avoid duplicate API calls
sam_cache = {}
for recipient in unique_recipients[:100]:  # Cap at 100 to respect API limits
    if recipient not in sam_cache:
        sam_cache[recipient] = enrich_from_sam(recipient)
        time.sleep(0.1)  # Rate limit: 10 req/sec

    sam_data = sam_cache[recipient]
    if sam_data:
        sam_enriched += 1
        # Apply to all awards from this recipient
        for gid, award in awards_map.items():
            if award["recipient_name"] == recipient:
                award["sam_business_type"] = ", ".join(sam_data.get("business_type", []))
                award["sam_is_small"] = sam_data.get("is_small_business", False)
                award["sam_cage_code"] = sam_data.get("cage_code")

                # Update set_aside field if we found socioeconomic status
                if sam_data.get("is_8a"):
                    award["set_aside"] = "8(a)"
                elif sam_data.get("is_sdvosb"):
                    award["set_aside"] = "SDVOSB"
                elif sam_data.get("is_hubzone"):
                    award["set_aside"] = "HUBZone"
                elif sam_data.get("is_wosb"):
                    award["set_aside"] = "WOSB"

log(f"  SAM.gov enriched: {sam_enriched} recipients")
```

**API Access:** Free API key at https://open.gsa.gov/api/entity-api/. Rate limit: 10 requests/second.

**Expected Impact:** Set-aside detection should increase from 5% to 60-70%. Enables filtering newsletter to "small business opportunities" segment.

---

## 3. Data Quality Checks (Automated Validation)

**Problem:** 3% of awards have $0 value, 0.3% have short descriptions, 96% lack NAICS codes. No systematic validation before analysis.

**Solution:** Add data quality layer to pipeline that filters/flags bad records.

### Implementation

```python
# Add to pipeline.py after line 436 (before final output prep)

def validate_award(award):
    """Return dict of data quality flags for an award."""
    issues = []

    # Critical issues (should filter out)
    if not award.get("award_amount") or award["award_amount"] == 0:
        issues.append("zero_value")
    if not award.get("description") or len(award.get("description", "")) < 10:
        issues.append("missing_description")
    if not award.get("recipient_name"):
        issues.append("missing_recipient")

    # Warnings (keep but flag)
    if not award.get("vehicle"):
        issues.append("no_vehicle")
    if not award.get("set_aside"):
        issues.append("no_set_aside")
    if not award.get("naics_code"):
        issues.append("no_naics")
    if award.get("award_amount", 0) > 1_000_000_000:
        issues.append("mega_award")  # Flag for editorial review

    return issues

log(f"\nValidating data quality...")
for gid, award in awards_map.items():
    award["dq_issues"] = validate_award(award)

# Filter out critical issues
critical_issues = ["zero_value", "missing_description", "missing_recipient"]
filtered_awards = {
    gid: award for gid, award in awards_map.items()
    if not any(issue in award["dq_issues"] for issue in critical_issues)
}

log(f"  Awards before filtering: {len(awards_map)}")
log(f"  Awards after filtering:  {len(filtered_awards)}")
log(f"  Filtered out: {len(awards_map) - len(filtered_awards)} bad records")

# Replace awards_map with filtered version
awards_map = filtered_awards
```

**Expected Impact:** Remove ~35-40 bad records per run. Clean data = better insights.

---

## 4. Calculated Fields (New Derived Metrics)

**Problem:** Pipeline outputs raw fields but doesn't calculate useful derived metrics (contract duration, agency spending velocity, recipient concentration).

**Solution:** Add calculated fields to each award before output.

### Implementation

```python
# Add after line 430 in pipeline.py (after enrichment)

log(f"\nCalculating derived fields...")

for gid, award in awards_map.items():
    # 1. Contract duration (days and years)
    if award.get("start_date") and award.get("end_date"):
        try:
            start = datetime.strptime(award["start_date"], "%Y-%m-%d")
            end = datetime.strptime(award["end_date"], "%Y-%m-%d")
            duration_days = (end - start).days
            award["duration_days"] = max(0, duration_days)
            award["duration_years"] = round(duration_days / 365, 2)
        except:
            award["duration_days"] = None
            award["duration_years"] = None

    # 2. Award size bucket
    amt = award.get("award_amount", 0)
    if amt == 0:
        award["size_bucket"] = "Zero"
    elif amt < 100_000:
        award["size_bucket"] = "< $100K"
    elif amt < 500_000:
        award["size_bucket"] = "$100K-$500K"
    elif amt < 1_000_000:
        award["size_bucket"] = "$500K-$1M"
    elif amt < 5_000_000:
        award["size_bucket"] = "$1M-$5M"
    elif amt < 10_000_000:
        award["size_bucket"] = "$5M-$10M"
    elif amt < 50_000_000:
        award["size_bucket"] = "$10M-$50M"
    else:
        award["size_bucket"] = "$50M+"

    # 3. Vertical count (for multi-vertical analysis)
    award["vertical_count"] = len(award.get("verticals", []))

    # 4. Award age (days since start_date)
    if award.get("start_date"):
        try:
            start = datetime.strptime(award["start_date"], "%Y-%m-%d")
            age_days = (datetime.now() - start).days
            award["award_age_days"] = age_days
        except:
            award["award_age_days"] = None

    # 5. Is recent? (started in past 30 days)
    award["is_recent"] = award.get("award_age_days", 999) <= 30
```

**New fields added:**
- `duration_days`: Contract length in days
- `duration_years`: Contract length in years (rounded)
- `size_bucket`: Award amount category (for segmentation)
- `vertical_count`: Number of verticals tagged
- `award_age_days`: Days since start_date
- `is_recent`: Boolean flag for recently-started awards

**Expected Impact:** Enables filtering newsletter to "awards started in past 30 days" and analysis by contract duration / award size.

---

## 5. Agency Spending Trends (Time Series)

**Problem:** Current pipeline only captures one snapshot. No visibility into whether an agency's spending is increasing, decreasing, or stable.

**Solution:** Build historical baseline and calculate week-over-week changes.

### Implementation (new script)

```python
#!/usr/bin/env python3
"""
Calculate week-over-week changes in agency spending and award counts.

Usage:
    python3 calculate_trends.py \
        --current data/govcon_awards_2026-03-18.json \
        --previous data/govcon_awards_2026-03-11.json
"""

import argparse
import json
from collections import defaultdict

def load_awards(path):
    with open(path) as f:
        return json.load(f)

def calculate_stats(awards):
    """Calculate counts and totals by agency, vertical, recipient."""
    stats = {
        "total_count": len(awards),
        "total_value": sum(a.get("award_amount", 0) for a in awards),
        "by_agency": defaultdict(lambda: {"count": 0, "value": 0}),
        "by_vertical": defaultdict(lambda: {"count": 0, "value": 0}),
        "by_recipient": defaultdict(lambda: {"count": 0, "value": 0}),
    }

    for award in awards:
        amt = award.get("award_amount", 0)
        agency = award.get("awarding_agency", "Unknown")
        recipient = award.get("recipient_name", "Unknown")

        stats["by_agency"][agency]["count"] += 1
        stats["by_agency"][agency]["value"] += amt

        stats["by_recipient"][recipient]["count"] += 1
        stats["by_recipient"][recipient]["value"] += amt

        for vertical in award.get("verticals", []):
            stats["by_vertical"][vertical]["count"] += 1
            stats["by_vertical"][vertical]["value"] += amt

    return stats

def calculate_change(current, previous):
    """Calculate percent change."""
    if previous == 0:
        return float('inf') if current > 0 else 0
    return ((current - previous) / previous) * 100

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--current", required=True)
    parser.add_argument("--previous", required=True)
    args = parser.parse_args()

    current = calculate_stats(load_awards(args.current))
    previous = calculate_stats(load_awards(args.previous))

    print("WEEK-OVER-WEEK TRENDS")
    print("=" * 80)

    # Overall
    count_change = calculate_change(current["total_count"], previous["total_count"])
    value_change = calculate_change(current["total_value"], previous["total_value"])
    print(f"\nTotal Awards: {current['total_count']} ({count_change:+.1f}% vs last week)")
    print(f"Total Value:  ${current['total_value']:,.0f} ({value_change:+.1f}% vs last week)")

    # Top movers by agency
    print("\nTOP AGENCY MOVERS (by value change):")
    agency_changes = []
    for agency in current["by_agency"]:
        curr_val = current["by_agency"][agency]["value"]
        prev_val = previous["by_agency"].get(agency, {}).get("value", 0)
        change = curr_val - prev_val
        pct_change = calculate_change(curr_val, prev_val) if prev_val > 0 else 0
        agency_changes.append((agency, change, pct_change, curr_val))

    for agency, change, pct, curr in sorted(agency_changes, key=lambda x: abs(x[1]), reverse=True)[:10]:
        print(f"  {agency:<50} ${change:>12,.0f} ({pct:>+6.1f}%)")

    # Emerging recipients (new this week or big increases)
    print("\nEMERGING RECIPIENTS (new or 2x increase):")
    for recipient in current["by_recipient"]:
        curr_val = current["by_recipient"][recipient]["value"]
        prev_val = previous["by_recipient"].get(recipient, {}).get("value", 0)
        if prev_val == 0 and curr_val > 1_000_000:  # New recipient with $1M+
            print(f"  {recipient:<50} ${curr_val:>12,.0f} (NEW)")
        elif prev_val > 0 and curr_val > 2 * prev_val:  # 2x increase
            pct = calculate_change(curr_val, prev_val)
            print(f"  {recipient:<50} ${curr_val:>12,.0f} ({pct:>+6.1f}%)")

if __name__ == "__main__":
    main()
```

**Usage:**
```bash
python3 calculate_trends.py \
    --current data/govcon_awards_2026-03-18.json \
    --previous data/govcon_awards_2026-03-11.json
```

**Expected Impact:** Newsletter can include "This week, DOD spending increased 23% with $450M in new cloud awards" type insights.

---

## 6. Recipient Concentration Metrics (Herfindahl-Hirschman Index)

**Problem:** No measure of market concentration. Is a vertical dominated by 2-3 primes, or is it competitive?

**Solution:** Calculate HHI (Herfindahl-Hirschman Index) by vertical and agency.

### Implementation

```python
# Add to analytics.py or generate_insights.py

def calculate_hhi(awards, group_by="vertical"):
    """
    Calculate HHI (market concentration) for each vertical or agency.
    HHI = sum of squared market shares (0-10,000 scale).

    HHI < 1,500: Competitive
    HHI 1,500-2,500: Moderately concentrated
    HHI > 2,500: Highly concentrated
    """
    from collections import defaultdict

    # Group awards by vertical/agency and sum recipient values
    groups = defaultdict(lambda: defaultdict(float))
    group_totals = defaultdict(float)

    for award in awards:
        amt = award.get("award_amount", 0)
        recipient = award.get("recipient_name", "Unknown")

        if group_by == "vertical":
            for vertical in award.get("verticals", []):
                groups[vertical][recipient] += amt
                group_totals[vertical] += amt
        elif group_by == "agency":
            agency = award.get("awarding_agency", "Unknown")
            groups[agency][recipient] += amt
            group_totals[agency] += amt

    # Calculate HHI for each group
    hhi_results = {}
    for group, recipients in groups.items():
        total = group_totals[group]
        if total == 0:
            continue

        # HHI = sum of squared market shares (as percentages)
        market_shares = [(amt / total) * 100 for amt in recipients.values()]
        hhi = sum(share ** 2 for share in market_shares)

        # Get top 3 recipients
        top_recipients = sorted(recipients.items(), key=lambda x: x[1], reverse=True)[:3]
        top3_share = sum(amt for _, amt in top_recipients) / total * 100

        hhi_results[group] = {
            "hhi": round(hhi, 1),
            "interpretation": "Competitive" if hhi < 1500 else "Moderate" if hhi < 2500 else "Concentrated",
            "top3_share_pct": round(top3_share, 1),
            "top_recipients": [(name, amt) for name, amt in top_recipients],
            "recipient_count": len(recipients),
        }

    return hhi_results

# Usage example
hhi_by_vertical = calculate_hhi(awards, group_by="vertical")
for vertical, metrics in sorted(hhi_by_vertical.items(), key=lambda x: x[1]["hhi"], reverse=True):
    print(f"{vertical:25} HHI: {metrics['hhi']:>6.1f} ({metrics['interpretation']:12}) | " +
          f"Top 3: {metrics['top3_share_pct']:>5.1f}% | {metrics['recipient_count']} recipients")
```

**Expected Impact:** Newsletter can include insights like "Cloud vertical is highly concentrated (HHI: 3,200) — top 3 primes control 78% of spending" to guide teaming strategy.

---

## 7. Vertical Overlap Scoring (Co-occurrence Analysis)

**Problem:** Only 8.5% of awards are tagged with multiple verticals. Many Cloud awards should also be tagged Cybersecurity or FedRAMP.

**Solution:** Analyze co-occurrence patterns and refine vertical tagging logic.

### Implementation

```python
# Add to pipeline.py or analytics.py

def analyze_vertical_overlap(awards):
    """Calculate co-occurrence matrix for verticals."""
    from collections import defaultdict
    from itertools import combinations

    # Count co-occurrences
    cooccur = defaultdict(int)
    vertical_counts = defaultdict(int)

    for award in awards:
        verticals = award.get("verticals", [])
        for v in verticals:
            vertical_counts[v] += 1
        for v1, v2 in combinations(sorted(verticals), 2):
            cooccur[(v1, v2)] += 1

    # Calculate lift scores (how much more likely are verticals to co-occur than by chance?)
    total_awards = len(awards)
    lift_scores = {}
    for (v1, v2), count in cooccur.items():
        expected = (vertical_counts[v1] / total_awards) * (vertical_counts[v2] / total_awards) * total_awards
        lift = count / expected if expected > 0 else 0
        lift_scores[(v1, v2)] = {
            "count": count,
            "lift": round(lift, 2),
            "v1_pct": round(count / vertical_counts[v1] * 100, 1),
            "v2_pct": round(count / vertical_counts[v2] * 100, 1),
        }

    # Print top overlaps
    print("VERTICAL OVERLAP ANALYSIS")
    print("=" * 80)
    for (v1, v2), metrics in sorted(lift_scores.items(), key=lambda x: x[1]["lift"], reverse=True)[:20]:
        print(f"{v1:25} + {v2:25} | {metrics['count']:>3} awards | Lift: {metrics['lift']:>5.2f}")

    return lift_scores

# Usage
overlap_scores = analyze_vertical_overlap(awards)
```

**Recommendation based on expected output:**
- If Cloud + FedRAMP have high lift (>2.0), add logic: "If award has Cloud tag and description contains 'FedRAMP', add FedRAMP tag"
- If Cybersecurity + Identity Management have high lift, refine IAM keyword list

**Expected Impact:** Increase multi-vertical tagging from 8.5% to 15-20%, improving relevance matching for subscribers.

---

## 8. Week-Over-Week Comparison Methodology

**Problem:** Newsletter readers want to know "what's new this week" vs last week. No systematic comparison logic.

**Solution:** Standardized comparison script that outputs changes in:
- Award count by agency/vertical
- New recipients (first-time winners)
- Recompete signals (same agency + description keywords)
- Spending velocity (awards started in past 7 days vs previous 7 days)

### Implementation

See section 5 (calculate_trends.py) for full script. Key additions:

```python
# Add to calculate_trends.py

def detect_recompetes(current_awards, previous_awards):
    """Identify potential recompetes (similar awards from same agency)."""
    from difflib import SequenceMatcher

    recompetes = []
    for curr in current_awards:
        curr_desc = curr.get("description", "").lower()
        curr_agency = curr.get("awarding_agency")

        for prev in previous_awards:
            prev_desc = prev.get("description", "").lower()
            prev_agency = prev.get("awarding_agency")

            if curr_agency == prev_agency:
                similarity = SequenceMatcher(None, curr_desc, prev_desc).ratio()
                if similarity > 0.7:  # 70% similar
                    recompetes.append({
                        "agency": curr_agency,
                        "current_recipient": curr.get("recipient_name"),
                        "previous_recipient": prev.get("recipient_name"),
                        "current_amount": curr.get("award_amount"),
                        "previous_amount": prev.get("award_amount"),
                        "similarity": round(similarity, 2),
                    })

    return recompetes
```

**Expected Impact:** Newsletter section: "Recompete Watch — 12 awards this week that renewed similar contracts from last year."

---

## 9. Historical Baseline Builder (Automated Archiving)

**Problem:** Each pipeline run overwrites previous data. No historical archive for trend analysis.

**Solution:** Automatically archive each week's data and build rolling 12-week baseline.

### Implementation

```bash
# Add to generate.sh after pipeline.py runs

# Archive to historical/ directory
DATESTAMP=$(date +%Y-%m-%d)
mkdir -p data/historical
cp data/govcon_awards_${DATESTAMP}.json data/historical/

# Keep last 12 weeks only (cleanup)
find data/historical -name "govcon_awards_*.json" -mtime +84 -delete

# Build rolling baseline (combine last 12 weeks into one file)
python3 scripts/build_baseline.py --weeks 12 --output data/baseline_12wk.json
```

**build_baseline.py:**
```python
#!/usr/bin/env python3
"""Combine last N weeks of awards into a single baseline file."""
import argparse
import json
import glob
import os

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--weeks", type=int, default=12)
    parser.add_argument("--output", required=True)
    args = parser.parse_args()

    # Find all historical files
    files = sorted(glob.glob("data/historical/govcon_awards_*.json"), reverse=True)[:args.weeks]

    all_awards = []
    for fpath in files:
        with open(fpath) as f:
            awards = json.load(f)
            # Add week identifier
            week_date = os.path.basename(fpath).replace("govcon_awards_", "").replace(".json", "")
            for a in awards:
                a["week_captured"] = week_date
            all_awards.extend(awards)

    # De-duplicate by generated_internal_id (keep most recent)
    seen = {}
    for a in all_awards:
        gid = a.get("generated_internal_id")
        if gid not in seen or a["week_captured"] > seen[gid]["week_captured"]:
            seen[gid] = a

    baseline = list(seen.values())

    with open(args.output, "w") as f:
        json.dump(baseline, f, indent=2)

    print(f"Baseline built: {len(baseline)} unique awards from {len(files)} weeks")
    print(f"Saved to: {args.output}")

if __name__ == "__main__":
    main()
```

**Expected Impact:** Enables "This award is 3x larger than typical DOD Cloud awards (12-week avg: $8M)" insights.

---

## 10. Anomaly Detection (Statistical Outliers)

**Problem:** $2.1B DOE nuclear cleanup contracts are included alongside $50K cybersecurity assessments. No filtering for "editorial relevance."

**Solution:** Flag statistical outliers and exclude from newsletter (or segment into separate "mega-deals" section).

### Implementation

```python
# Add to analytics.py

def detect_outliers(awards, field="award_amount", method="iqr", threshold=3.0):
    """
    Detect outliers using IQR or z-score method.

    method="iqr": Flag values outside [Q1 - 1.5*IQR, Q3 + 1.5*IQR]
    method="zscore": Flag values with |z-score| > threshold
    """
    import statistics

    values = [a.get(field, 0) for a in awards if a.get(field)]

    if method == "iqr":
        values_sorted = sorted(values)
        q1 = values_sorted[len(values) // 4]
        q3 = values_sorted[3 * len(values) // 4]
        iqr = q3 - q1
        lower_bound = q1 - 1.5 * iqr
        upper_bound = q3 + 1.5 * iqr

        outliers = [a for a in awards if a.get(field, 0) < lower_bound or a.get(field, 0) > upper_bound]

    elif method == "zscore":
        mean = statistics.mean(values)
        stdev = statistics.stdev(values)

        outliers = [
            a for a in awards
            if abs((a.get(field, 0) - mean) / stdev) > threshold
        ]

    return outliers

# Usage
outliers = detect_outliers(awards, field="award_amount", method="iqr")
print(f"Detected {len(outliers)} outliers (IQR method)")
for award in sorted(outliers, key=lambda x: x.get("award_amount", 0), reverse=True)[:10]:
    print(f"  ${award['award_amount']:>15,.0f} | {award['recipient_name'][:50]} | {award['awarding_agency']}")

# Filter out for main newsletter, create separate "Mega-Deals" section
normal_awards = [a for a in awards if a not in outliers]
mega_deals = outliers
```

**Expected Impact:** Newsletter main body focuses on $100K-$50M awards (relevant to SMB readers). "Mega-Deals of the Week" section highlights $100M+ awards separately.

---

## Summary: Implementation Priority

| Priority | Improvement | Effort | Impact | ETA |
|----------|-------------|--------|--------|-----|
| **P0** | Filter $0 awards | 10 min | High | Sprint 2, Day 1 |
| **P0** | Calculate duration fields | 20 min | High | Sprint 2, Day 1 |
| **P0** | Week-over-week comparison script | 2 hours | High | Sprint 2, Week 1 |
| **P1** | Enhanced vehicle detection (description parsing) | 1 hour | High | Sprint 2, Week 1 |
| **P1** | Data quality validation layer | 1 hour | Medium | Sprint 2, Week 1 |
| **P1** | Calculated fields (size buckets, age, recent flag) | 30 min | Medium | Sprint 2, Week 1 |
| **P2** | SAM.gov recipient enrichment | 4 hours | Very High | Q2, Month 1 |
| **P2** | Historical baseline builder | 2 hours | High | Q2, Month 1 |
| **P2** | HHI concentration metrics | 2 hours | Medium | Q2, Month 2 |
| **P3** | Vertical overlap analysis | 2 hours | Low | Q2, Month 2 |
| **P3** | Anomaly detection | 1 hour | Low | Q2, Month 3 |

**Total Sprint 2 effort:** ~6 hours (can complete in 1 day)
**Total Q2 effort:** ~13 additional hours (spread over 3 months)

---

## Next Steps

1. Implement P0 improvements before next newsletter (March 24)
2. Get free SAM.gov API key (https://open.gsa.gov/api/entity-api/)
3. Set up `data/historical/` archiving in `generate.sh`
4. Test week-over-week comparison with March 11 vs March 18 data
5. Review vertical overlap scores and refine tagging logic
