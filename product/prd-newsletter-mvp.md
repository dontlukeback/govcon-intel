# PRD: GovCon Weekly Intelligence Newsletter (MVP)
**Version 1.0** | March 18, 2026 | Owner: CPO

---

## Problem Statement

Small and mid-tier government contractors waste 10-15 hours per week manually searching USAspending, SAM.gov, and FedBizOpps for relevant contract opportunities. By the time they find a good match, the incumbent has already positioned for the recompete. They need:

1. **Signal in the noise** — 100,000+ awards per month, but only 50-100 are relevant to their capabilities
2. **Recompete intelligence** — Most valuable opportunities are recompetes (lower risk, known scope), but tracking expiration dates is manual
3. **Actionable analysis** — Raw data doesn't tell you WHY an opportunity matters or WHAT to do about it

## Solution

A weekly email newsletter that delivers:
- Curated list of relevant contract awards in tech verticals (AI/ML, Cybersecurity, Cloud, etc.)
- Recompete tracking with timeline pressure analysis
- AI-generated "So What" insights (why this matters, who should pursue it, what action to take)
- Agency spending trends (which agencies are accelerating spend in which areas)

**The wedge:** We prove value with the newsletter, then upsell to daily alerts, opportunity matching, and proposal assistance.

---

## Success Metrics

| Metric | Target | Measurement |
|--------|--------|-------------|
| Week 1 subscribers | 100 | Beehiiv analytics |
| Week 4 subscribers | 500 | Beehiiv analytics |
| Open rate | >35% | Industry benchmark for B2B newsletter = 30% |
| Click-through rate | >12% | Industry benchmark = 8-10% |
| Paid conversion | 10% by week 4 | Stripe dashboard |
| Churn rate | <10% monthly | Beehiiv + Stripe |
| Referral rate | 15% | Beehiiv referral tracking |

**Success definition:** If we hit 50 paid subscribers ($4,950 MRR) by April 30, we validate demand and continue building. If we're under 25 paid, we pivot the offer or pricing.

---

## User Stories

### BD Manager at 8(a) firm
"As a BD manager at a small 8(a) cybersecurity firm, I need to know when DoD cyber contracts worth $1-10M are hitting the street, so I can position early and avoid competing against 50 other firms on the final RFP."

### Capture Manager at mid-tier prime
"As a capture manager at a $200M systems integrator, I need to track recompetes where my team is the incumbent, so I can allocate resources to defense strategies before challengers start positioning."

### CEO of small GovCon
"As the CEO of a 15-person AI/ML consultancy, I need to understand which agencies are increasing AI spend, so I can allocate my limited BD budget to the right agency relationships."

---

## MVP Feature Set

### Core Features (Week 1 Release)

#### 1. Weekly Email Newsletter
**Format:** HTML email via Beehiiv
**Send time:** Every Monday at 7:00 AM EST (prime inbox time for BD teams)
**Length:** 3,000-5,000 words (10-15 min read)

**Structure:**
1. Executive Summary (150 words)
   - Top trend of the week
   - Biggest recompete deadline
   - One specific action item

2. Recompete "So What" Analysis (40% of content)
   - 4-6 major recompetes (>$50M value or strategic importance)
   - For each: incumbent, timeline pressure, pursuit recommendation, specific action

3. Agency Strategy Signals (20% of content)
   - Spending acceleration/deceleration by agency
   - New vehicle announcements
   - Policy changes affecting procurement

4. Vertical Deep Dive (20% of content)
   - Rotate through verticals weekly (Week 1 = Cybersecurity, Week 2 = AI/ML, etc.)
   - Trend analysis for that vertical
   - Top 10 awards of the week

5. Market Intelligence (10% of content)
   - NAICS code trends
   - Set-aside utilization (are agencies hitting small business goals?)
   - Contract vehicle popularity

6. Quick Hits (10% of content)
   - 5-10 notable awards worth flagging but not full analysis
   - Format: One-sentence description + link to USAspending

**Free vs. Paid tiers:**
- **Free tier:** Executive summary + top 3 recompetes + quick hits (limited to top 10 opportunities)
- **Pro tier ($99/mo):** Full report including agency trends, vertical deep dive, complete data tables, CSV export

#### 2. Landing Page with Subscription
**URL:** https://govconintel.com
**Tech:** Static HTML + Beehiiv embed form
**Copy focus:** Problem/solution, sample report preview, pricing tiers
**CTA:** "Get the next report free" (email capture)

#### 3. Data Pipeline
**Inputs:**
- USAspending.gov API (primary source)
- 9 tech verticals: AI/ML, Cybersecurity, Cloud, Data Analytics, DevSecOps, Zero Trust, FedRAMP, Identity Management, Networking/SDWAN
- Last 7 days of awards (rolling window)

**Processing:**
- De-duplication (same award across multiple keyword searches)
- NAICS enrichment
- Contract vehicle detection (GWAC, BPA, Schedule)
- Set-aside classification
- Recompete identification (expiration date <180 days)

**Outputs:**
- JSON data file (archive for historical analysis)
- CSV export (for Pro tier users)
- Markdown report (for AI insight generation)
- HTML email (for distribution)

#### 4. AI Insights Generation
**Model:** Claude 3.5 Sonnet via Anthropic API
**Inputs:** Markdown report with structured data tables
**Outputs:**
- Recompete analysis with timeline pressure scoring
- Agency spending trend narrative
- Vertical deep dive analysis
- Actionable recommendations

**Prompt structure:**
- "Analyze these recompetes and tell me: timeline pressure (HIGH/MEDIUM/STANDARD), incumbent advantage (STRONG/MODERATE/WEAKENED), who should pursue (prime vs. mid-tier vs. small business), specific action to take this week"
- Include examples from past reports to maintain consistent tone

#### 5. Distribution via Beehiiv
**Beehiiv plan:** Launch ($49/mo, up to 10K subscribers)
**Automation:**
- Markdown → HTML conversion script
- Inline CSS for email compatibility
- Automatic send on Mondays at 7 AM EST
- Segmentation: Free list vs. Pro list (different email content)

**Email features:**
- Unsubscribe link (CAN-SPAM compliant)
- "Forward to a friend" link (virality)
- Click tracking on all USAspending.gov links (measure engagement)
- Reply-to: hello@govconintel.com (direct feedback channel)

---

## Out of Scope (Phase 1)

The following are explicitly NOT in MVP:

- Daily alerts (Phase 2)
- User profiles / custom filtering (Phase 2)
- Web dashboard / search interface (Phase 2)
- Opportunity matching / scoring (Phase 3)
- Proposal assistance (Phase 4)
- API access (Phase 2)
- Mobile app (Phase 3+)
- Integration with CRM systems (Phase 4+)
- Team collaboration features (Phase 3+)

---

## Technical Architecture

### Data Pipeline
```
USAspending API → pipeline.py → data/awards_{date}.json
                                → output/insights_{date}.md
                                → output/report_{date}.html
```

**Scripts:**
1. `pipeline.py` — Fetch awards, de-dupe, enrich (existing, working)
2. `generate_insights.py` — AI analysis (existing, working)
3. `generate_report.py` — Format newsletter (NEW, needed)
4. `report_to_html.py` — Convert to HTML with inline styles (NEW, needed)
5. `generate.sh` — Orchestrate full pipeline (existing, working)

**Execution:** Cron job every Sunday at 8 PM EST (generates report overnight, sends Monday 7 AM)

### Newsletter Format

**HTML template structure:**
```html
<div style="max-width: 600px; margin: 0 auto; font-family: -apple-system, sans-serif;">
  <header>
    <h1>GovCon Intelligence: Week of {date_range}</h1>
    <p>AI-powered federal contract intelligence</p>
  </header>

  <section id="executive-summary">
    <!-- Callout box with key insight -->
  </section>

  <section id="recompetes">
    <!-- Structured cards per recompete -->
  </section>

  <section id="agency-signals">
    <!-- Trend charts + narrative -->
  </section>

  <section id="vertical-deep-dive">
    <!-- Focused analysis on one vertical -->
  </section>

  <footer>
    <a href="{{unsubscribe}}">Unsubscribe</a> |
    <a href="{{forward}}">Forward to a friend</a>
  </footer>
</div>
```

**Design principles:**
- Navy (#0A1628) and gold (#C5A44E) brand colors (match landing page)
- Mobile-responsive (50%+ of users read on phone)
- Inline CSS only (Gmail compatibility)
- No external images (except small header logo)
- Print-friendly (BD managers print reports for team meetings)

---

## Content Standards

### Writing Tone
- **Direct, not academic:** "This is a prime-tier opportunity" vs. "This procurement vehicle may be suitable for larger integrators"
- **Prescriptive, not descriptive:** "Set a SAM.gov alert for NAICS 541512 + DISA" vs. "Monitoring SAM.gov is recommended"
- **Skeptical, not promotional:** "Timeline favors the incumbent" vs. "Great opportunity for challengers"

### Insight Quality Bar
Every recompete analysis must answer:
1. **Timeline pressure:** HIGH (<120 days), MEDIUM (120-180 days), STANDARD (>180 days)
2. **Incumbent advantage:** STRONG (locked in), MODERATE (fair fight), WEAKENED (agency wants change)
3. **Who should pursue:** Prime-tier only / mid-tier / small business / teaming opportunity
4. **Specific action this week:** One concrete thing to do (e.g., "Request meeting with program office")

If we can't answer all 4, we don't include the recompete.

### Data Accuracy
- All award amounts, dates, agencies verified against USAspending.gov
- Incumbent company names researched (not assumed from previous awards)
- NAICS codes validated
- If data is uncertain, flag it: "(Unconfirmed: may be bridge contract)"

---

## Launch Checklist

### Week 0 (Pre-Launch)
- [ ] `generate_report.py` built and tested
- [ ] `report_to_html.py` built and tested
- [ ] Beehiiv account set up, newsletter configured
- [ ] Landing page live at govconintel.com
- [ ] Stripe payment integration for Pro tier
- [ ] Privacy policy + Terms of Service pages
- [ ] Test email sent to internal team (check formatting in Gmail, Outlook, Apple Mail)
- [ ] CSV export functionality tested
- [ ] Sample report v2 generated and reviewed

### Week 1 (Launch Week)
- [ ] First newsletter generated and sent Monday 7 AM EST
- [ ] Post announcement on LinkedIn (personal + company page)
- [ ] Direct outreach to 25 target customers (BD managers at 8(a) firms)
- [ ] Monitor open rates, click rates, unsubscribe rate
- [ ] Reply to all user feedback within 24 hours
- [ ] Fix any bugs in pipeline or formatting

### Week 2-4 (Iteration)
- [ ] 4 consecutive newsletters published on time
- [ ] A/B test subject lines (which drives higher open rate?)
- [ ] Survey first 100 subscribers: "What's most valuable in the newsletter?"
- [ ] Refine recompete analysis based on feedback
- [ ] Add 2-3 new verticals based on demand
- [ ] Launch referral program ("Forward to a friend" tracking)
- [ ] First case study: customer shares a win from newsletter intel

---

## Pricing Strategy

### Free Tier
**What's included:**
- Weekly newsletter (Monday AM)
- Executive summary (150 words)
- Top 3 recompetes with basic analysis
- Quick hits (top 10 notable awards)
- Archive access to past 4 weeks

**What's NOT included:**
- Full recompete analysis (limited to top 3)
- Agency spending trends
- Vertical deep dives
- CSV data export
- Email support

**Goal:** Prove value fast. Free tier should be good enough to make users think "If this is free, the paid version must be incredible."

### Pro Tier ($99/month)
**What's included:**
- Everything in Free
- Full recompete analysis (all 4-6 major recompetes)
- Agency spending trends
- Vertical deep dive (rotates weekly)
- Market intelligence section
- CSV export of all awards
- Archive access to all historical reports
- Email support (48-hour response time)

**Positioning:** "The cost of one BD lunch per month. Pays for itself if you win one contract per year."

**Annual discount:** $990/year (2 months free) — encourage annual commits early

### Team Tier (Phase 2)
**Not in MVP.** Placeholder for future: $499/month for 5 users, Slack integration, shared saved searches.

---

## Risk Mitigation

| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|------------|
| Pipeline breaks (API changes) | Medium | High | Monitoring script (alerts if no data for 24 hours). Backup data source (SAM.gov scraper). |
| AI generates inaccurate insights | Medium | High | Human review before send (CTO reviews every report Week 1-4). Feedback mechanism in newsletter ("Report an error"). |
| Low open rates (<20%) | High | High | A/B test subject lines. Send time optimization. Survey users on preferred frequency. |
| Paid conversion <5% | High | Critical | Test pricing ($99 → $49 → $149 to find optimal). Offer first-month discount. Free trial extension. |
| Users forward newsletter (cannibalizes paid) | Medium | Medium | Free tier is limited enough that forwarding doesn't replace paid need. Track "forward to friend" to measure virality. |
| Competitor launches similar product | Low | Medium | Speed is advantage. Ship fast, iterate based on user feedback. Build community moat (Slack group for paid users). |

---

## Open Questions (To Resolve by Week 2)

1. **CSV export format:** What columns do users actually want? (Ask in Week 1 survey)
2. **Vertical rotation:** Should we let users choose their vertical focus vs. rotating for everyone? (Test in Phase 2)
3. **Send frequency:** Is Monday 7 AM optimal? (A/B test Monday vs. Tuesday, 7 AM vs. 9 AM)
4. **Length:** Are 3,000-5,000 words too long? (Track scroll depth, time-to-read)
5. **Referral incentive:** What motivates users to forward? (Test: 1 month free, 20% discount, exclusive content)

---

## Success Criteria (Go/No-Go Decision)

**By April 15, 2026 (4 weeks post-launch):**

**GREEN LIGHT (continue building):**
- 500+ total subscribers
- 50+ paid subscribers (10% conversion)
- Open rate >30%
- <5% churn rate
- NPS >40

**YELLOW LIGHT (iterate on offer):**
- 300-500 subscribers
- 20-50 paid (7-10% conversion)
- Open rate 20-30%
- Test different pricing, content mix, or send frequency

**RED LIGHT (pivot or shut down):**
- <300 subscribers
- <20 paid subscribers (<7% conversion)
- Open rate <20%
- High churn (>15% monthly)
- Negative feedback ("Not worth the money")

---

## Appendix: Sample Report Structure

### Email Subject Line Options (A/B Test)
1. "GovCon Intel: $890M in recompetes hitting in 60 days"
2. "DoD cyber spending up 34% — here's where it's going"
3. "4 recompetes you need to track this week"
4. "Your weekly federal contract intelligence [March 16-22]"

### Executive Summary Example
```
The Department of Defense has accelerated cyber spending by 34% QoQ,
with CYBERCOM and DISA leading procurement. Three major recompetes worth
$890M are hitting the street in the next 60 days. If you hold incumbent
positions in network defense or zero-trust architecture, now is the time
to prep your capture teams.

THIS WEEK'S ACTION: Set SAM.gov alerts for NAICS 541512 + DISA and
541519 + CYBERCOM. The EITSS-III recompete ($487M) hasn't dropped a
draft RFP yet and only has 104 days to expiration — this screams bridge
contract or sole-source extension.
```

### Recompete Analysis Example
```
### Enterprise IT Support Services (EITSS-III)
**Defense Information Systems Agency (DISA)** | Incumbent: Leidos |
Current value: $487,000,000 | 104 days to expiration

**Timeline pressure:** HIGH -- less than 4 months out
The solicitation hasn't even dropped yet with only 104 days left. This
screams bridge contract or sole-source extension for the incumbent.

**Incumbent advantage:** STRONG. The timeline math favors Leidos. Late
RFP + short evaluation = advantage to the team that's already running
the program.

**Who should pursue this:**
- At $487M, this is prime-tier only. You need $50M+ in single-award
  past performance to be credible.
- Mid-tier firms: your play is as a key subcontractor. Start
  conversations with likely primes this week.

**What you should do this week:**
- If you're targeting this: submit a capabilities brief to the
  contracting officer by Friday.
- Set a SAM.gov alert for NAICS 541512 + "DISA" immediately.
- Mid-tier: reach out to top 3 likely primes (Leidos, CACI, Booz Allen)
  about subcontracting.
```

### Quick Hits Example
```
## Quick Hits
Worth watching but not full analysis:

1. **Army Cyber Command** — $12.3M zero-trust architecture (NAICS 541512)
2. **GSA** — $8.7M cloud migration (AWS GovCloud, NAICS 541512)
3. **DHS CISA** — $5.4M threat intel platform (8(a) set-aside, NAICS 541519)
4. **Air Force** — $4.2M AI/ML for logistics (SBIR Phase III, NAICS 541715)
5. **VA** — $3.8M identity management (NAICS 541519)

[View all 487 awards in CSV export →]
```

---

## Feedback Loops

### User Feedback Channels
1. **Reply to newsletter:** hello@govconintel.com (monitored daily)
2. **Survey (Week 1):** "What's most valuable in this newsletter?" (3 questions, <2 min)
3. **Survey (Week 4):** "Would you recommend us to a colleague?" (NPS)
4. **Feature requests:** Trello board or GitHub issues (public roadmap)

### Internal Metrics Dashboard
Track weekly:
- Subscriber growth (free + paid)
- Open rate, click rate, unsubscribe rate
- Paid conversion rate
- Churn rate
- Revenue (MRR)
- Top clicked links (which opportunities generate most interest)
- Referral rate

**Review cadence:** Every Monday morning (before newsletter send)

---

## Post-MVP: What's Next?

After 4 successful newsletters (end of Week 4), we evaluate:

1. **User feedback themes:** What do they want more of? Less of?
2. **Engagement patterns:** Which sections get the most clicks?
3. **Conversion drivers:** What convinced paid users to upgrade?
4. **Churn reasons:** Why did users cancel?

**Phase 2 decision point:** Do we build daily alerts (Phase 2) or double down on improving the newsletter? Data decides.
