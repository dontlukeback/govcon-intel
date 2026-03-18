# Weekly Newsletter SOP

Standard operating procedure for generating and sending the GovCon Intelligence weekly newsletter. One-person operation, designed to take 30-45 minutes end-to-end.

## Schedule

| When | What |
|------|------|
| Sunday 9:00 PM PT | Pipeline runs automatically (cron/launchd) |
| Monday 7:00 AM PT | You review output, fix anything, import to Beehiiv |
| Monday 8:00 AM PT | Final QA in Beehiiv preview |
| Monday 8:30 AM PT | Send newsletter |
| Monday afternoon | Check metrics (open rate, bounces) |

---

## Step 1: Verify the Pipeline Ran (Monday morning, 5 min)

Check that Sunday night's automated run succeeded.

```bash
cd ~/Personal/govcon-intel

# Check the cron log for errors
tail -50 output/cron.log

# Verify output files exist for this week
ls -la output/data_$(date +%Y-%m-%d -v-1d).json    # yesterday's date (Sunday)
ls -la output/report_$(date +%Y-%m-%d -v-1d).md
ls -la output/report_$(date +%Y-%m-%d -v-1d).html
```

**If the pipeline failed**, re-run it manually:

```bash
./generate.sh 2>&1 | tee output/manual-run.log
```

Common failure reasons:
- USAspending API was down (just re-run, it's free and keyless)
- Python dependency missing (`pip3 install -r requirements.txt`)
- Network timeout (re-run, the API is occasionally slow on weekends)

## Step 2: Review the Output (10 min)

Open the markdown report and scan for quality issues.

```bash
# Quick stats check
python3 -c "
import json
data = json.load(open('data/govcon_awards_$(date +%Y-%m-%d -v-1d).json'))
print(f'Total awards: {len(data)}')
from collections import Counter
verticals = Counter()
for a in data:
    for v in a.get('verticals', []):
        verticals[v] += 1
for v, c in verticals.most_common():
    print(f'  {v}: {c}')
"

# Open the report
open output/report_$(date +%Y-%m-%d -v-1d).md
```

**What to look for:**
- Total award count is reasonable (typically 50-200 per week; fewer than 20 = possible API issue)
- No verticals with 0 results (if one is empty, the keyword list may need updating)
- Dollar amounts look sane (no $0 awards, no obviously wrong numbers)
- Top awards section has meaningful descriptions (not just "UNKNOWN" or blanks)
- Agency names are complete, not truncated

## Step 3: Import to Beehiiv (10 min)

### If HTML output exists (report_to_html.py is built):

1. Open Beehiiv > Posts > New Post
2. Switch to HTML/code view
3. Paste contents of `output/report_YYYY-MM-DD.html`
4. Switch back to visual editor, verify formatting looks right
5. Set subject line: "GovCon Weekly: [Top headline from this week's data]"
6. Set preview text: 1-sentence hook from the top insight

### If only markdown exists (early stage):

1. Open Beehiiv > Posts > New Post
2. Copy-paste from the markdown report
3. Manually format in Beehiiv's editor (headers, bold, tables)
4. Add a brief intro paragraph and sign-off

### Subject line formula:

```
GovCon Weekly: $[total_value] in [top_vertical] Awards | [notable_agency] Moves
```

Example: "GovCon Weekly: $340M in Cybersecurity Awards | DoD OASIS Surge"

## Step 4: QA Checklist Before Sending

Run through this every single week. No exceptions.

- [ ] **Subject line** -- Is it specific and compelling? (Not generic "Weekly Update")
- [ ] **Preview text** -- Does it add info beyond the subject line?
- [ ] **Send a test email** -- Send to your personal email, open on both desktop and mobile
- [ ] **Links work** -- Click every link in the test email
- [ ] **Tables render** -- Award tables display correctly (especially on mobile)
- [ ] **Numbers match** -- Spot-check 2-3 award amounts against the raw data
- [ ] **No placeholder text** -- Search for "TODO", "TBD", "PLACEHOLDER", "[insert"
- [ ] **Date is correct** -- Report header shows the right week
- [ ] **Footer** -- Unsubscribe link works, sender info is present (CAN-SPAM compliance)
- [ ] **From name** -- "GovCon Intelligence" (not your personal name, unless that's the brand)

## Step 5: Send

1. In Beehiiv, set the send time (8:30 AM PT is a good default -- catches East Coast mid-morning)
2. Select your audience segment (all subscribers, or exclude any test addresses)
3. Hit Send (or Schedule if you're doing this ahead of time)

## Step 6: Post-Send Monitoring (Monday afternoon + Tuesday)

### Monday afternoon (2-4 PM PT):

- [ ] Check Beehiiv dashboard: open rate should appear within 2-4 hours
- [ ] Look for bounce-backs or delivery failures
- [ ] Check for any reply emails (early subscribers often reply with feedback)

### Tuesday morning:

- [ ] **Open rate** -- Benchmark: 40-50% for early subscribers, 25-35% at scale
- [ ] **Click-through rate** -- Benchmark: 3-8% is healthy for B2B newsletters
- [ ] **Unsubscribes** -- More than 1% per send = content or frequency problem
- [ ] **New subscribers** -- Track week-over-week growth
- [ ] Log metrics in your tracking spreadsheet (see tools.md)

### If metrics are bad:

| Signal | Likely cause | Fix |
|--------|-------------|-----|
| Open rate < 20% | Weak subject line or deliverability issue | A/B test subjects; check spam score |
| CTR < 1% | Content not actionable enough | Add more "so what" analysis per award |
| Unsubscribes > 2% | Wrong audience or too frequent | Survey churned subs; consider biweekly |
| Bounces > 5% | Bad email list hygiene | Clean list, remove invalid addresses |

---

## Emergency Procedures

**Pipeline breaks on Sunday night and you discover Monday morning:**
Run manually. The pipeline is idempotent -- safe to re-run. If the API is down, use `--days 8` or `--days 9` to extend the window and run Tuesday instead. Notify subscribers if the delay is significant.

**Beehiiv is down at send time:**
Draft the email in Gmail and BCC your subscriber list (only viable under ~50 subscribers). Otherwise, delay to afternoon or next morning.

**You find a data error after sending:**
If it's minor (one wrong number), don't send a correction -- note it next week. If it's major (wrong agency, order-of-magnitude dollar error), send a brief correction email: "Correction: [specific fix]. We apologize for the error."
