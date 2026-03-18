# Weekly Monitoring Checklist

Run through this every Monday after sending the newsletter, and again on Tuesday to capture final metrics. Copy this into your tracking spreadsheet each week.

---

## Pipeline Health (Monday morning)

- [ ] `generate.sh` completed without errors (check `output/cron.log`)
- [ ] All 4 pipeline steps ran (data pull, report, insights, HTML)
- [ ] Output files exist with correct date stamp in `output/`
- [ ] Pipeline runtime was reasonable (under 5 minutes typical; over 10 = investigate)
- [ ] No Python tracebacks in the log

**If something failed:**
```bash
# Re-run manually and watch output
cd ~/Personal/govcon-intel
./generate.sh 2>&1 | tee output/debug-run.log
```

---

## Data Quality (Monday morning)

- [ ] Total awards pulled: _____ (typical range: 50-200/week; flag if < 20)
- [ ] Awards by vertical (flag any with 0 results):

| Vertical | Count | Flag? |
|----------|-------|-------|
| AI/ML | | |
| Cybersecurity | | |
| Cloud | | |
| Data Analytics | | |
| DevSecOps | | |
| Zero Trust | | |
| FedRAMP | | |
| Identity Management | | |
| Networking/SDWAN | | |

- [ ] No awards with $0 or null amounts
- [ ] Award descriptions are populated (not blank or "UNKNOWN")
- [ ] Date range in report matches the intended week
- [ ] Spot-check: pick 2 awards, verify they exist on usaspending.gov

**Quick data quality check:**
```bash
python3 -c "
import json
data = json.load(open('data/govcon_awards_$(date +%Y-%m-%d -v-1d).json'))
print(f'Total: {len(data)}')
zeros = [a for a in data if not a.get('award_amount')]
print(f'Zero/null amounts: {len(zeros)}')
blanks = [a for a in data if not a.get('description','').strip()]
print(f'Blank descriptions: {len(blanks)}')
from collections import Counter
verts = Counter()
for a in data:
    for v in a.get('verticals', []):
        verts[v] += 1
for v, c in sorted(verts.items()):
    flag = ' *** LOW' if c < 3 else ''
    print(f'  {v}: {c}{flag}')
"
```

---

## Newsletter Metrics (Monday afternoon + Tuesday)

Check in Beehiiv dashboard.

| Metric | This week | Last week | Trend |
|--------|-----------|-----------|-------|
| Emails sent | | | |
| Open rate | | | |
| Click-through rate | | | |
| Unsubscribes | | | |
| Bounces | | | |
| Spam complaints | | | |

**Benchmarks:**
- Open rate: 40-50% (early), 25-35% (at scale). Below 20% = problem.
- CTR: 3-8% is good for B2B. Below 1% = content isn't actionable enough.
- Unsubscribe rate: Under 0.5% per send is healthy. Over 1% = investigate.
- Spam complaints: Should be 0. Any complaints = check content and list hygiene.
- Bounce rate: Under 2%. Over 5% = clean your list.

---

## Landing Page Metrics (Tuesday)

Check Google Analytics or Beehiiv subscribe page stats.

- [ ] Page visitors this week: _____
- [ ] New subscribers from page: _____
- [ ] Conversion rate: _____% (good = 20-40% for a focused landing page)
- [ ] Top traffic sources: _____
- [ ] Any referral spikes? (LinkedIn post went well, someone shared it, etc.)

---

## Subscriber Growth (Tuesday)

- [ ] Total subscribers (start of week): _____
- [ ] New subscribers this week: _____
- [ ] Unsubscribes this week: _____
- [ ] Net growth: _____
- [ ] Total subscribers (end of week): _____
- [ ] Growth rate: _____% week-over-week

**Log this in your tracking spreadsheet every week.** You want to see the trendline, not just individual data points.

---

## Monthly Review (first Monday of each month)

In addition to the weekly checks, once a month review:

- [ ] Month-over-month subscriber growth rate
- [ ] Average open rate trend (improving or declining?)
- [ ] Which subject lines performed best (open rate) and worst
- [ ] Which content sections got the most clicks
- [ ] Any feedback received from readers (replies, social mentions)
- [ ] Pipeline reliability: how many weeks ran cleanly vs. needed manual intervention
- [ ] Cost review: API usage, any tool upgrades needed?
- [ ] Content ideas backlog: any new verticals or sections to add?
