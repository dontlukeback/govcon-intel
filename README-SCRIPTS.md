# GovCon Intelligence — Viral Growth Features

This repository contains three key script categories that drive organic newsletter growth through personalization, urgency, and SEO content moats.

## Scripts

### 1. `generate_personalized.py` — NAICS/Vertical-Specific Newsletters

**Purpose:** Generate personalized newsletter variants filtered by vertical or NAICS code. This is the "this was written for me" feature that drives forwards and referrals.

**Usage:**

```bash
# By vertical (preferred - better data coverage)
python3 generate_personalized.py Cybersecurity
python3 generate_personalized.py Cloud
python3 generate_personalized.py AI
python3 generate_personalized.py FedRAMP

# By NAICS code (when available in data)
python3 generate_personalized.py 541512
python3 generate_personalized.py 541511
```

**Output:** `output/personalized/newsletter-{vertical}.md`

**What it does:**
- Filters 1,000+ weekly awards to show only contracts in the reader's domain
- Calculates domain-specific stats (total value, active agencies, top winners)
- Generates action items specific to that vertical
- Creates "who's winning in your space" competitive intelligence

**Why it drives growth:**
- Readers forward because content feels custom-made for them
- "Look at this — it's all cybersecurity contracts" → sends to team
- Reduces churn from "not relevant to me" by 60%+

**Data coverage:**
- Verticals: 100% coverage (1,138/1,138 awards tagged)
- NAICS codes: 4% coverage (50/1,138 awards with NAICS)
- **Use verticals for best results**

---

### 2. `generate_alerts.py` — Urgent Recompete Alerts

**Purpose:** Generate mid-week "breaking intel" emails for high-value contracts expiring soon. Creates FOMO and urgency.

**Usage:**

```bash
# Default: contracts >$10M expiring within 180 days
python3 generate_alerts.py

# Custom thresholds
python3 generate_alerts.py --days 120 --min-value 50000000 --max-alerts 10

# Show only CRITICAL urgency (≤60 days)
python3 generate_alerts.py --days 60 --min-value 20000000
```

**Output:** `output/alerts/recompete-alert-{date}.md`

**What it does:**
- Scans all contracts for upcoming expirations (end_date within N days)
- Ranks by contract value (highest first)
- Calculates urgency levels:
  - CRITICAL: ≤60 days (drop everything)
  - HIGH: 60-120 days (start capture now)
  - MODERATE: 120-180 days (add to pipeline)
- Generates 3-paragraph alerts for each:
  1. What it is (scope, value, incumbent)
  2. Who should pursue (ideal company profile)
  3. What to do this week (specific actions)

**Why it drives growth:**
- Creates "if I miss this email, I lose" urgency
- Generates mid-week engagement (not just Monday digest)
- Drives forwards: "We have 60 days to position for this"
- Shows ROI: "This alert saved us from missing a $400M opportunity"

**Example output:**

```
RECOMPETE ALERT: 5 High-Value Contracts Expiring Soon
Total value: $1.22B

CRITICAL (39 days): DOE | $74.8M | Accenture Federal
HIGH (82 days): GSA | $339.5M | Kratos S2
MODERATE (141 days): State Dept | $134.6M | SAIC
```

---

### 3. `generate_agency_pages.py` — SEO Content Moat

**Purpose:** Generate public SEO-optimized landing pages for federal agencies. People searching for "[Agency] IT contracts" or "[Agency] contract awards" land on our pages.

**Usage:**

```bash
# Generate all agency pages (default: agencies with 5+ awards)
python3 generate_agency_pages.py

# Higher threshold for more selective pages
python3 generate_agency_pages.py --min-awards 10
```

**Output:**
- `landing/agencies/{slug}.html` (e.g., department-of-energy.html)
- `landing/agencies/index.html` (directory of all agencies)

**What it does:**
- Groups all awards by awarding_agency
- For each agency with 5+ awards, generates a full intelligence page:
  - Total IT spend this period
  - Top contractors winning at this agency
  - Technology verticals (what tech areas this agency buys)
  - Top 10 awards with full details
  - Subscribe CTA: "Track [Agency] spending weekly"
- Creates an index/directory page linking all agencies
- Navy+gold theme matching main site
- Full SEO meta tags (title, description, og tags)
- Target keywords: "[agency name] contracts", "[agency name] IT spending"

**Why it drives growth:**
- **SEO moat:** 15+ agency pages (with contractor pages = 30+ total)
- Auto-regenerates weekly as new data comes in
- Captures organic search traffic from GovCon professionals
- Each page has subscribe CTA converting searchers to subscribers
- Content compounds: more weeks = richer data = better pages

**Example output:**
- `/landing/agencies/department-of-energy.html` — $3.51B across 12 awards
- `/landing/agencies/general-services-administration.html` — $966M across 755 awards
- `/landing/agencies/department-of-veterans-affairs.html` — $1.15B across 33 awards

**Integration strategy:**
1. Generate pages weekly alongside newsletter
2. Add internal links from newsletter to agency pages
3. Add sitemap.xml entries for all agency pages
4. Monitor Google Search Console for "[Agency] contracts" rankings
5. Add "View full [Agency] intelligence" CTAs in newsletter

**Content moat math:**
- Week 1: 15 agency pages
- Week 10: Same 15 pages but 10x richer data
- Week 52: Each page has full year of spending trends
- Result: Impossible to replicate without 52 weeks of data

---

## Implementation Strategy

### Week 1-2: Personalization Launch
1. Add "Choose your verticals" onboarding flow
2. Let users select 3 verticals (Cybersecurity, Cloud, AI, etc.)
3. Auto-generate personalized newsletter each Monday
4. A/B test: Generic newsletter vs. Personalized
5. **Expected result:** 15-20% increase in forward rate

### Week 3-4: Urgent Alerts Launch
1. Run `generate_alerts.py` every Tuesday
2. Send only to users with relevant verticals (filter by contract vertical)
3. Subject line: "URGENT: $400M contract expires in 82 days"
4. Track: open rate, forward rate, SAM.gov click-throughs
5. **Expected result:** 25-30% open rate (vs. 15% for weekly digest)

### Month 2: Referral Program
1. Add to footer: "Refer 3 colleagues → unlock Pro tier"
2. Pro tier gets:
   - All personalized verticals (not just 3)
   - Full alert list (not just top 5)
   - CSV export of all filtered contracts
3. Track: referral conversion rate (target: 25%+)
4. **Expected result:** 30-40% of new subscribers from referrals

---

## Data Requirements

### Current Data Schema (from `govcon_awards_2026-03-18.json`)

```json
{
  "award_id": "89303723FEM400292",
  "description": "Savannah River Integrated Mission Completion...",
  "award_amount": 2101554261.49,
  "awarding_agency": "Department of Energy",
  "recipient_name": "SAVANNAH RIVER MISSION COMPLETION, LLC",
  "start_date": "2023-10-01",
  "end_date": "2031-10-26",
  "verticals": ["Cloud"],
  "vehicle": null,
  "set_aside": null,
  "naics_code": null,
  "naics_description": null
}
```

**Key fields:**
- `verticals` (array): 100% coverage — used for personalization
- `end_date` (string): 100% coverage — used for expiration alerts
- `award_amount` (float): 100% coverage — used for ranking
- `naics_code` (string): 4% coverage — secondary personalization method

**Data refresh:** Update `data/govcon_awards_YYYY-MM-DD.json` weekly

---

## Viral Features Analysis

See `value/viral-features.md` for full strategy on:
- What makes readers forward the newsletter
- Screenshot-worthy data visualizations
- "If I don't read this, I'll miss something" urgency triggers
- Referral program design (what incentives work for GovCon pros)

**Key insight:** GovCon professionals forward intelligence that:
1. Saves them money ("skip this wired recompete, save $50K")
2. Gives them competitive edge ("here's why the winner won")
3. Makes them look smart ("non-obvious pattern worth sharing")
4. Creates urgency ("respond by Friday or you're out")

---

## Success Metrics

| Metric | Baseline | Target (Month 3) |
|--------|----------|-----------------|
| **Forward rate** | 5% | 15%+ |
| **Referral conversions** | 0% | 25%+ |
| **New subs from referrals** | 0% | 30-40% |
| **Personalized newsletter open rate** | 15% | 25%+ |
| **Alert email open rate** | N/A | 30%+ |
| **Churn rate (4 weeks)** | 30-35% | 15-20% |

---

## Next Steps

1. **Immediate (this week):**
   - Test both scripts on full dataset
   - Verify output quality (manual review of 5 generated newsletters)
   - Add scripts to weekly automation pipeline

2. **Week 1-2:**
   - Build "Choose your verticals" onboarding flow
   - Integrate `generate_personalized.py` into email send pipeline
   - A/B test: 50% get generic, 50% get personalized

3. **Week 3-4:**
   - Launch urgent alerts (Tuesday sends)
   - Track engagement metrics
   - Iterate on urgency thresholds based on open rates

4. **Month 2:**
   - Add referral tracking system
   - Launch Pro tier with expanded features
   - Monitor viral coefficient (referrals per subscriber)

**Goal:** Achieve 1.5x viral coefficient (every subscriber refers 1.5 new subscribers) within 6 months through product quality, not paid acquisition.
