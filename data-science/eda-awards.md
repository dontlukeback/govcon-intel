# Exploratory Data Analysis: GovCon Awards Dataset

**Date:** 2026-03-18
**Analyst:** Data Scientist
**Dataset:** `govcon_awards_2026-03-18.json`
**Total Awards:** 1,173
**Total Value:** $8,747,988,663.99

---

## Executive Summary

This EDA reveals a highly skewed dataset dominated by a few mega-awards ($1B+) and a long tail of small-value transactions. The median award is just $530, while the mean is $7.4M due to extreme outliers. Department of Energy drives 40% of total contract value with only 12 awards. Data enrichment is sparse: 95%+ of awards lack NAICS codes, set-aside classifications, and vehicle information—critical gaps for competitive intelligence.

**Key Findings:**
1. **Extreme concentration:** Top 2 awards ($3.4B) represent 39% of total dataset value
2. **Small business opportunity:** 76% of awards are under $100K (but only 0.3% tagged as 8(a) or set-aside)
3. **Data quality issue:** Vehicle/NAICS/set-aside fields are 95%+ null—major enrichment gap
4. **Vertical distribution:** Cybersecurity dominates count (547 awards), Cloud dominates value ($5.9B)
5. **GSA volume play:** 788 awards (67%) but only $966M total (low avg value)

---

## 1. Award Amount Distribution

### Summary Statistics
| Metric | Value |
|--------|-------|
| **Mean** | $7,457,791 |
| **Median** | $530 |
| **Std Dev** | $84,226,431 |
| **Min** | $0 |
| **Max** | $2,101,554,261 |

### Percentiles
| Percentile | Value |
|------------|-------|
| P10 | $15 |
| P25 | $63 |
| P50 | $530 |
| P75 | $80,085 |
| P90 | $1,835,038 |
| P95 | $7,166,814 |
| P99 | $97,122,524 |

**Analysis:** Median of $530 vs mean of $7.4M reveals extreme right skew. 50% of awards are under $530—these are likely task orders, modifications, or delivery orders on existing IDIQs. The top 1% (P99+) controls massive contract value.

### Award Size Distribution
| Bucket | Count | % of Total |
|--------|-------|-----------|
| < $100K | 896 | 76.4% |
| $100K - $500K | 108 | 9.2% |
| $500K - $1M | 22 | 1.9% |
| $1M - $5M | 78 | 6.6% |
| $5M - $10M | 23 | 2.0% |
| $10M - $50M | 28 | 2.4% |
| $50M+ | 18 | 1.5% |

**Insight:** 86% of awards are under $500K. This suggests the dataset captures a lot of contract modifications, task orders, and small purchases—not just prime contract awards. For a newsletter targeting BD professionals, focusing on the $5M+ tier (69 awards, 5.9% of volume) would be higher signal.

### Top 10 Largest Awards
1. **$2.1B** | SAVANNAH RIVER MISSION COMPLETION, LLC | Department of Energy
   _Savannah River Integrated Mission Completion Contract - Task Order 6 (Liquid Waste Operations)_

2. **$1.3B** | IDAHO ENVIRONMENTAL COALITION LLC | Department of Energy
   _ICP Ten Year Plan Hybrid Task Order_

3. **$819.7M** | TRIWEST HEALTHCARE ALLIANCE CORP | Department of Veterans Affairs
   _Express Report: February 2026_

4. **$814.3M** | BL HARBERT INTERNATIONAL LLC | Department of State
   _Construction Manager as Constructor (Design-Phase Services)_

5. **$662.6M** | LEIDOS, INC. | Department of Transportation
   _Advanced Technologies and Oceanic Procedures (ATOP)_

6. **$422.0M** | SALIENT CRGT, INC. | General Services Administration
   _DEA Bluestone Award_

7. **$339.5M** | KRATOS S2, INC | General Services Administration
   _COSMIC AES SBIR III Contract_

8. **$244.7M** | COGNOSANTE MVH LLC | Department of Veterans Affairs
   _Supply Chain Management Product Line DevSecOps and Integration_

9. **$174.7M** | HARRIS CORPORATION | Department of Transportation
   _FTI Telecommunications_

10. **$150.4M** | FOUR POINTS TECHNOLOGY, L.L.C. | Social Security Administration
    _Amazon Web Services (AWS) Connect for Contact Center as a Service_

**Competitive Intelligence:** Top 10 awards = $6.9B (79% of dataset value). DOE nuclear cleanup dominates. Leidos, SAIC (via Salient CRGT), Kratos, and Cognosante are the major tech winners. Notable: Four Points Technology won a $150M SSA cloud contact center deal—AWS resale play.

---

## 2. Awards by Agency

### Top 10 Agencies by Award Count
| Rank | Agency | Count | Total Value | Avg Value |
|------|--------|-------|-------------|-----------|
| 1 | General Services Administration | 788 | $966,394,246 | $1,226,389 |
| 2 | Department of Justice | 113 | $67,106,149 | $593,860 |
| 3 | Department of Homeland Security | 35 | $149,685,653 | $4,276,733 |
| 4 | Department of Veterans Affairs | 33 | $1,151,183,465 | $34,884,347 |
| 5 | Department of Transportation | 30 | $1,095,988,572 | $36,532,952 |
| 6 | Department of the Interior | 27 | $154,221,280 | $5,711,899 |
| 7 | Department of Education | 26 | $106,821,880 | $4,108,534 |
| 8 | Department of State | 22 | $975,376,145 | $44,335,279 |
| 9 | Department of Health and Human Services | 22 | $162,676,309 | $7,394,378 |
| 10 | Social Security Administration | 14 | $161,863,719 | $11,561,694 |

### Top 10 Agencies by Total Value
| Rank | Agency | Total Value | Count | Avg Value |
|------|--------|-------------|-------|-----------|
| 1 | Department of Energy | $3,509,490,711 | 12 | $292,457,559 |
| 2 | Department of Veterans Affairs | $1,151,183,465 | 33 | $34,884,347 |
| 3 | Department of Transportation | $1,095,988,572 | 30 | $36,532,952 |
| 4 | Department of State | $975,376,145 | 22 | $44,335,279 |
| 5 | General Services Administration | $966,394,246 | 788 | $1,226,389 |
| 6 | Department of Health and Human Services | $162,676,309 | 22 | $7,394,378 |
| 7 | Social Security Administration | $161,863,719 | 14 | $11,561,694 |
| 8 | Department of the Interior | $154,221,280 | 27 | $5,711,899 |
| 9 | Department of Homeland Security | $149,685,653 | 35 | $4,276,733 |
| 10 | Department of Education | $106,821,880 | 26 | $4,108,534 |

**Analysis:**
- **GSA volume anomaly:** 788 awards (67% of dataset) but only $966M total. Avg value = $1.2M. This is classic GSA: lots of Schedule 70 purchases, small task orders, and delivery orders. High volume, low value.
- **DOE concentration:** Only 12 awards but $3.5B total (40% of dataset value). Avg = $292M. Nuclear cleanup and energy contracts are massive, multi-year IDIQs.
- **VA + DOT opportunity:** Both have 30+ awards with $1B+ total value and avg values >$30M. Prime targets for mid-tier contractors.
- **DOJ paradox:** 113 awards but only $67M total. Avg = $594K. Likely small cybersecurity/investigative tech purchases.

---

## 3. Awards by Vertical

| Vertical | Count | Total Value | Avg Value |
|----------|-------|-------------|-----------|
| **Cybersecurity** | 547 | $1,512,407,299 | $2,764,913 |
| **AI/ML** | 308 | $2,818,584 | $9,151 |
| **Cloud** | 263 | $5,922,336,565 | $22,518,390 |
| **Identity Management** | 79 | $81,647,742 | $1,033,516 |
| **FedRAMP** | 38 | $1,102,096,911 | $29,002,550 |
| **Networking/SDWAN** | 21 | $64,341,145 | $3,063,864 |
| **Data Analytics** | 17 | $76,832,159 | $4,519,539 |
| **DevSecOps** | 1 | $244,656,805 | $244,656,805 |
| **Zero Trust** | 1 | $54,415 | $54,415 |

**Multi-vertical awards:** 100 awards (8.5%) tagged with 2+ verticals.

**Most Common Vertical Combinations:**
- AI/ML + Identity Management: 23 awards
- Cybersecurity + Identity Management: 22 awards
- Cybersecurity + FedRAMP: 20 awards
- Cloud + Cybersecurity: 8 awards
- Cloud + FedRAMP: 8 awards

**Analysis:**
- **Cybersecurity volume leader:** 547 awards but only $1.5B total. Avg = $2.8M. Lots of small security assessments, pentests, CMMC compliance work.
- **Cloud value leader:** 263 awards, $5.9B total. Avg = $22.5M. This is where the big money lives: cloud migrations, GovCloud, multi-year IaaS/PaaS contracts.
- **AI/ML disappointment:** 308 awards but only $2.8M total. Avg = $9K. These are likely contract modifications or small R&D pilots, not major AI platform awards.
- **FedRAMP premium:** Only 38 awards but $1.1B total. Avg = $29M. FedRAMP-authorized solutions command massive contracts.
- **DevSecOps single award:** The $244.7M Cognosante VA award is the only one tagged DevSecOps. Major tagging gap—many cloud/cyber awards should have this tag.

**Opportunity:** Cloud + FedRAMP is the sweet spot. If your product is FedRAMP-authorized, avg deal size is 10x higher than non-FedRAMP cloud work.

---

## 4. Awards by Set-Aside Type

| Set-Aside Type | Count | % | Total Value | % | Avg Value |
|----------------|-------|---|-------------|---|-----------|
| **None/Null** | 1,117 | 95.2% | $8,731,164,304 | 99.8% | $7,816,620 |
| **NO SET ASIDE USED.** | 49 | 4.2% | $2,315,914 | 0.0% | $47,264 |
| **8(a)** | 4 | 0.3% | $8,679,227 | 0.1% | $2,169,807 |
| **Small Business** | 2 | 0.2% | $5,592,986 | 0.1% | $2,796,493 |
| **HUBZONE SET-ASIDE** | 1 | 0.1% | $236,232 | 0.0% | $236,232 |

**Critical Data Quality Issue:** 95.2% of awards have null set-aside data. This is a **major enrichment gap**. We know from federal procurement rules that ~23% of federal contract dollars must go to small businesses, yet only 7 awards (0.6%) are tagged with set-aside classifications.

**Impact:** Newsletter readers (small/mid GovCon firms) rely on set-aside intel to identify winnable opportunities. Current data is unusable for this purpose.

**Recommendation:** Enrich pipeline with SAM.gov Entity Management API to pull business size/socioeconomic status for each recipient. Cross-reference with FPDS set-aside codes.

---

## 5. Awards by Contract Vehicle

| Vehicle | Count | % | Total Value | Avg Value |
|---------|-------|---|-------------|-----------|
| **None/Null** | 1,141 | 97.3% | $7,917,717,251 | $6,939,279 |
| **SEWP** | 13 | 1.1% | $23,132,808 | $1,779,447 |
| **GSA OASIS** | 7 | 0.6% | $153,426,618 | $21,918,088 |
| **ALLIANT 2** | 5 | 0.4% | $26,803,511 | $5,360,702 |
| **8(a) STARS II** | 3 | 0.3% | $588,286,098 | $196,095,366 |
| **STARS III** | 3 | 0.3% | $10,020,155 | $3,340,052 |
| **CIO-SP3** | 1 | 0.1% | $28,602,224 | $28,602,224 |

**Critical Data Quality Issue:** 97.3% of awards have null vehicle data. Known GWACs/IDIQs (OASIS, ALLIANT, STARS, CIO-SP3, SEWP) represent only 32 awards.

**Analysis:**
- **8(a) STARS II premium:** 3 awards, $588M total. Avg = $196M. This is a monster vehicle for small disadvantaged businesses.
- **OASIS strong:** 7 awards, $153M total. Avg = $21.9M. OASIS+ just launched—watch for awards under new vehicle.
- **SEWP volume:** 13 awards but only $23M total. Avg = $1.8M. Classic IT hardware/software buys.

**Recommendation:** Enrich pipeline by parsing award descriptions for vehicle keywords (OASIS, STARS, ALLIANT, CIO-SP3, VETS 2, NITAAC, etc.). Most vehicles are mentioned in description text even if not in structured fields.

---

## 6. Time Distribution

### Contract Duration Statistics
- **Awards with start_date:** 1,173 (100%)
- **Awards with end_date:** 1,173 (100%)
- **Awards with valid durations:** 1,162 (99.1%)

| Metric | Days | Years |
|--------|------|-------|
| **Mean** | 282 | 0.8 |
| **Median** | 60 | 0.2 |
| **Min** | 3 | 0.0 |
| **Max** | 11,731 | 32.1 |

**Analysis:** Median duration of 60 days suggests most awards are short-term task orders or modifications. Mean of 282 days (9 months) is pulled up by multi-year IDIQs. The 32-year max is likely a nuclear cleanup or facility O&M contract (probably one of the DOE mega-awards).

### Awards by Start Year
| Year | Count | % |
|------|-------|---|
| 2026 | 850 | 72.5% |
| 2025 | 162 | 13.8% |
| 2024 | 65 | 5.5% |
| 2023 | 34 | 2.9% |
| 2022 | 21 | 1.8% |
| 2021 | 22 | 1.9% |
| 2020 | 7 | 0.6% |
| Pre-2020 | 12 | 1.0% |

**Analysis:** 72.5% of awards started in 2026 (current year). This confirms the dataset is capturing **recent modifications and task orders on existing contracts**, not just new prime contract awards. For weekly intelligence, we should filter to awards that started in the past 7-30 days to avoid stale data.

**Insight:** The 13.8% of awards with 2025 start dates but captured in March 2026 data suggests these are recently modified/funded task orders on FY2025 base contracts.

---

## 7. Top 20 Recipients by Total Award Value

| Rank | Recipient | Total Value | Awards | Avg Value |
|------|-----------|-------------|--------|-----------|
| 1 | SAVANNAH RIVER MISSION COMPLETION, LLC | $2,101,554,261 | 1 | $2,101,554,261 |
| 2 | IDAHO ENVIRONMENTAL COALITION LLC | $1,304,803,621 | 1 | $1,304,803,621 |
| 3 | TRIWEST HEALTHCARE ALLIANCE CORP | $819,701,547 | 1 | $819,701,547 |
| 4 | BL HARBERT INTERNATIONAL LLC | $814,339,696 | 1 | $814,339,696 |
| 5 | LEIDOS, INC. | $662,632,660 | 1 | $662,632,660 |
| 6 | SALIENT CRGT, INC. | $422,039,859 | 1 | $422,039,859 |
| 7 | KRATOS S2, INC | $339,524,745 | 1 | $339,524,745 |
| 8 | HARRIS CORPORATION | $269,432,824 | 2 | $134,716,412 |
| 9 | COGNOSANTE MVH LLC | $244,656,805 | 1 | $244,656,805 |
| 10 | SCIENCE APPLICATIONS INTERNATIONAL CORPORATION | $182,381,260 | 6 | $30,396,877 |
| 11 | FOUR POINTS TECHNOLOGY, L.L.C. | $160,463,721 | 3 | $53,487,907 |
| 12 | ALLIANT INSURANCE SERVICES, INC. | $97,122,524 | 1 | $97,122,524 |
| 13 | HIVE GROUP, LLC | $91,061,279 | 1 | $91,061,279 |
| 14 | ACCENTURE FEDERAL SERVICES LLC | $83,556,817 | 2 | $41,778,409 |
| 15 | DELOITTE & TOUCHE LLP | $77,580,513 | 4 | $19,395,128 |
| 16 | AT&T ENTERPRISES, LLC | $58,262,118 | 1 | $58,262,118 |
| 17 | TRACE3 GOVERNMENT, LLC | $57,912,707 | 1 | $57,912,707 |
| 18 | CDA INC | $49,281,909 | 2 | $24,640,955 |
| 19 | GENERAL DYNAMICS INFORMATION TECHNOLOGY, INC. | $45,819,457 | 3 | $15,273,152 |
| 20 | ODDBALL, INC. | $41,891,530 | 1 | $41,891,530 |

**Competitive Intelligence:**
- **DOE cleanup dominance:** Top 2 recipients (Savannah River, Idaho Environmental) are nuclear site O&M contractors. Not relevant to tech GovCon audience.
- **Major primes present:** Leidos (#5), SAIC (#10 via Salient CRGT), Accenture Federal (#14), Deloitte (#15), GDIT (#19). These are the "usual suspects" in large federal IT.
- **Mid-tier opportunities:** Four Points Technology (#11, 3 awards, $160M), Trace3 Government (#17, 1 award, $58M), CDA Inc (#18, 2 awards, $49M). These are $50M-200M firms winning sizable contracts—good benchmark for newsletter readers.
- **Emerging players:** Oddball, Inc. (#20, $42M) is a modern dev shop (Agile/DevSecOps). Cognosante (#9, $245M VA DevSecOps award) is a healthcare IT specialist expanding into VA modernization.

**Recipient Concentration:**
- **Unique recipients:** 363
- **Recipients with only 1 award:** 284 (78.2%)
- **Recipients with 2+ awards:** 79 (21.8%)

**Analysis:** Winner-take-most dynamic. 79 firms (22%) won multiple awards in this dataset, suggesting incumbent advantage or IDIQ dominance. For newsletter readers, identifying who won what on which vehicles is critical for teaming/subcontracting strategy.

---

## 8. Data Quality Analysis

### Null/Missing Values by Field
| Field | Nulls | % Null |
|-------|-------|--------|
| award_id | 0 | 0.0% |
| description | 0 | 0.0% |
| **award_amount** | **35** | **3.0%** |
| awarding_agency | 0 | 0.0% |
| recipient_name | 0 | 0.0% |
| start_date | 0 | 0.0% |
| end_date | 0 | 0.0% |
| verticals | 0 | 0.0% |
| **vehicle** | **1,141** | **97.3%** |
| **set_aside** | **1,117** | **95.2%** |
| **naics_code** | **1,123** | **95.7%** |
| **naics_description** | **1,123** | **95.7%** |

**Critical Issues:**
1. **Award amount nulls:** 35 awards (3%) have no dollar value. These should be filtered out or flagged as data quality issues.
2. **Vehicle/set-aside/NAICS gaps:** 95%+ null rate on enrichment fields. **This is the biggest pipeline improvement opportunity.**

### Zero-Value Awards
- **Count:** 35 (3.0%)
- **Issue:** Awards with $0 value are likely data errors or administrative actions (contract closeouts, corrections). Should be filtered from analysis.

### Duplicate Award IDs
- **Count:** 0 duplicates detected
- **Status:** Clean on deduplication

### Missing/Short Descriptions
- **Count:** 4 awards (0.3%) with descriptions <10 characters
- **Status:** Minimal issue

### Mega-Awards (>$1B)
- **Count:** 2 awards
- **Recipients:**
  - SAVANNAH RIVER MISSION COMPLETION, LLC: $2.1B (DOE)
  - IDAHO ENVIRONMENTAL COALITION LLC: $1.3B (DOE)
- **Analysis:** Both are DOE nuclear site contracts. Not representative of typical tech GovCon awards.

### NAICS Code Coverage
- **Populated:** 50 awards (4.3%)
- **Top NAICS codes:**
  - 332216 (Saw Blade and Handtool Manufacturing): 48 awards
  - 541519 (Other Computer Related Services): 2 awards

**Data Quality Red Flag:** NAICS code 332216 (saw blades/handtools) appears 48 times in a dataset of AI/ML, Cloud, and Cybersecurity contracts. This is clearly **incorrect NAICS mapping**. The pipeline is likely pulling default/legacy NAICS codes from parent IDIQs instead of task order-specific codes.

**Recommendation:** Drop NAICS codes from pipeline until enrichment is fixed. Misleading data is worse than no data.

---

## Data Quality Summary

### What's Working
- Core fields (award_id, description, agency, recipient, dates) are 100% populated
- No duplicate awards
- Vertical tagging is consistent (9 verticals, clean taxonomy)
- Date coverage is complete

### What's Broken
1. **Vehicle field:** 97% null—must enrich via description parsing
2. **Set-aside field:** 95% null—must enrich via SAM.gov Entity API
3. **NAICS codes:** 96% null + incorrect mapping when present—drop from pipeline
4. **Award amounts:** 3% null—filter these out
5. **Multi-vertical tagging:** Only 8.5% of awards have multiple verticals. Many Cloud awards should also be tagged Cybersecurity or FedRAMP.

### Recommendations (see pipeline-improvements.md for full details)
1. Enrich vehicle field by parsing description text for GWAC/IDIQ keywords
2. Pull recipient socioeconomic status from SAM.gov to classify set-asides
3. Drop NAICS codes until data source is fixed
4. Filter out $0 awards before analysis
5. Refine vertical tagging logic to capture overlaps (Cloud+Cyber, Cloud+FedRAMP)

---

## Python Code Used

```python
import json
from collections import defaultdict, Counter
from datetime import datetime
import statistics

# Load data
with open('/Users/luke/Personal/govcon-intel/data/govcon_awards_2026-03-18.json') as f:
    awards = json.load(f)

# Basic stats
total_awards = len(awards)
total_value = sum(a['award_amount'] for a in awards)

# Amount distribution
amounts = [a['award_amount'] for a in awards]
amounts_sorted = sorted(amounts)
mean_amt = statistics.mean(amounts)
median_amt = statistics.median(amounts)
stdev_amt = statistics.stdev(amounts)

# Percentiles
percentiles = {}
for p in [10, 25, 50, 75, 90, 95, 99]:
    idx = int(len(amounts_sorted) * p / 100)
    percentiles[p] = amounts_sorted[idx]

# Award size buckets
buckets = {
    "< $100K": sum(1 for amt in amounts if amt < 100_000),
    "$100K - $500K": sum(1 for amt in amounts if 100_000 <= amt < 500_000),
    "$500K - $1M": sum(1 for amt in amounts if 500_000 <= amt < 1_000_000),
    "$1M - $5M": sum(1 for amt in amounts if 1_000_000 <= amt < 5_000_000),
    "$5M - $10M": sum(1 for amt in amounts if 5_000_000 <= amt < 10_000_000),
    "$10M - $50M": sum(1 for amt in amounts if 10_000_000 <= amt < 50_000_000),
    "$50M+": sum(1 for amt in amounts if amt >= 50_000_000)
}

# Top awards
top_awards = sorted(awards, key=lambda x: x['award_amount'], reverse=True)[:10]

# Agency stats
agency_stats = defaultdict(lambda: {'count': 0, 'total_value': 0})
for award in awards:
    agency = award['awarding_agency']
    agency_stats[agency]['count'] += 1
    agency_stats[agency]['total_value'] += award['award_amount']

top_agencies_by_count = sorted(agency_stats.items(),
                                key=lambda x: x[1]['count'], reverse=True)[:10]
top_agencies_by_value = sorted(agency_stats.items(),
                                key=lambda x: x[1]['total_value'], reverse=True)[:10]

# Vertical stats
vertical_stats = defaultdict(lambda: {'count': 0, 'total_value': 0})
for award in awards:
    for vertical in award.get('verticals', []):
        vertical_stats[vertical]['count'] += 1
        vertical_stats[vertical]['total_value'] += award['award_amount']

# Set-aside stats
set_aside_stats = defaultdict(lambda: {'count': 0, 'total_value': 0})
for award in awards:
    set_aside = award.get('set_aside') or 'None/Null'
    set_aside_stats[set_aside]['count'] += 1
    set_aside_stats[set_aside]['total_value'] += award['award_amount']

# Vehicle stats
vehicle_stats = defaultdict(lambda: {'count': 0, 'total_value': 0})
for award in awards:
    vehicle = award.get('vehicle') or 'None/Null'
    vehicle_stats[vehicle]['count'] += 1
    vehicle_stats[vehicle]['total_value'] += award['award_amount']

# Duration calculation
durations = []
for award in awards:
    if award.get('start_date') and award.get('end_date'):
        try:
            start = datetime.strptime(award['start_date'], '%Y-%m-%d')
            end = datetime.strptime(award['end_date'], '%Y-%m-%d')
            duration_days = (end - start).days
            if duration_days > 0:
                durations.append(duration_days)
        except:
            pass

duration_stats = {
    'mean': statistics.mean(durations),
    'median': statistics.median(durations),
    'min': min(durations),
    'max': max(durations)
}

# Start year distribution
start_year_counts = Counter()
for award in awards:
    if award.get('start_date'):
        try:
            year = datetime.strptime(award['start_date'], '%Y-%m-%d').year
            start_year_counts[year] += 1
        except:
            pass

# Top recipients
recipient_stats = defaultdict(lambda: {'count': 0, 'total_value': 0})
for award in awards:
    recipient = award['recipient_name']
    recipient_stats[recipient]['count'] += 1
    recipient_stats[recipient]['total_value'] += award['award_amount']

top_recipients = sorted(recipient_stats.items(),
                        key=lambda x: x[1]['total_value'], reverse=True)[:20]

# Data quality checks
null_counts = {}
for field in ['award_id', 'description', 'award_amount', 'awarding_agency',
              'recipient_name', 'start_date', 'end_date', 'verticals',
              'vehicle', 'set_aside', 'naics_code', 'naics_description']:
    null_count = sum(1 for a in awards if not a.get(field) or
                     (isinstance(a.get(field), list) and len(a.get(field)) == 0))
    null_counts[field] = null_count

zero_value_awards = [a for a in awards if a['award_amount'] == 0]
duplicate_ids = [aid for aid, count in Counter([a['award_id'] for a in awards]).items()
                 if count > 1]
mega_awards = [a for a in awards if a['award_amount'] > 1_000_000_000]
```

---

## Next Steps

1. **Read pipeline-improvements.md** for specific enrichment recommendations
2. **Filter dataset** to awards >$1M and started in past 30 days for weekly newsletter
3. **Build week-over-week comparison** to identify trending agencies/verticals/recipients
4. **Add recipient intelligence** (firm size, past performance, teaming partners)
5. **Calculate market concentration** (HHI by vertical, agency spending trends)
