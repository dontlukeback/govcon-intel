# GovCon Weekly Intelligence — Product Roadmap
**Version 1.0** | Updated: March 18, 2026

---

## Vision

Become the Bloomberg Terminal for small/mid government contractors. Start with a weekly intelligence newsletter, expand to real-time opportunity matching, proposal assistance, and win probability scoring. Every GovCon BD team checks us before making a capture decision.

---

## Strategic Phases

### Phase 1: Newsletter as Wedge (Months 1-3)
**Goal:** Build audience + validate willingness to pay
**Metric:** 500 subscribers, 50 paid (10% conversion)

The newsletter is not the business — it's the customer acquisition channel. We're building trust and demonstrating value before asking for SaaS commitment.

**What ships:**
- Weekly newsletter (manual curation + AI insights)
- Free tier (limited to top 10 opportunities)
- Pro tier ($99/mo) — full report, recompete analysis, agency spending trends
- Basic landing page + Beehiiv distribution
- Manual pipeline (Python scripts → Markdown → HTML → Email)

**Key capabilities:**
- Award tracking across 9 tech verticals
- Recompete identification with timeline analysis
- Agency spending trend detection
- "So what" analysis (actionable takeaways)

**Success criteria:**
- 4 consecutive weekly reports published
- Open rate >35%
- Click-through rate >12%
- First 10 paying subscribers within 30 days

---

### Phase 2: Daily Alerts + Personalization (Months 4-6)
**Goal:** Move from weekly batch to real-time intelligence
**Metric:** 2,000 subscribers, 200 paid (10% conversion), 20% retention month-over-month

Users shouldn't wait 7 days for time-sensitive opportunities. This phase shifts to instant notification + personalized filtering.

**What ships:**
- Daily opportunity alerts (email or Slack)
- User profile setup (verticals, agencies, NAICS codes, set-asides)
- Filtering by contract size range ($100K-$1M, $1M-$10M, $10M+)
- Saved searches ("Show me all DHS cyber contracts >$5M")
- Web dashboard (basic table view, search, export CSV)
- API access for Pro tier

**New data sources:**
- SAM.gov entity enrichment (company size, certifications, past performance)
- Contract vehicle tracking (GSA Schedules, GWACs, BPAs)
- Set-aside intelligence (8(a), SDVOSB, WOSB, HUBZone)

**Success criteria:**
- Median time-to-alert <2 hours from award publication
- 50% of paid users set up custom alerts
- 10+ companies using API integration

---

### Phase 3: Opportunity Matching (Months 7-9)
**Goal:** AI recommends which opportunities to pursue
**Metric:** 5,000 subscribers, 500 paid, $50K MRR

This is where we become defensible. Matching requires understanding the user's company profile, past performance, team capabilities, and strategic priorities.

**What ships:**
- Company profile builder (CAGE code import from SAM.gov)
- Past performance library (user enters contracts won/lost)
- Capability matrix (NAICS codes, clearances, certifications, geographic presence)
- AI-powered opportunity scoring (fit score 0-100)
- Recommended bid/no-bid with rationale
- Competitive intelligence (who else is likely to bid)
- Win probability estimation (based on historical FPDS patterns)

**Matching algorithm inputs:**
- Company NAICS codes vs. requirement NAICS
- Past performance agency overlap
- Contract size vs. company revenue (sweet spot = 3-10x annual revenue)
- Incumbent status (are you defending?)
- Set-aside eligibility
- Geographic requirements
- Clearance requirements
- Teaming history with likely primes/subs

**Success criteria:**
- 80% of matched opportunities are rated "relevant" by users
- 30% of paid users upload past performance data
- First case study: "We won a $4M contract because of the opportunity match"

---

### Phase 4: Proposal Assistance (Months 10-12)
**Goal:** Help users write better proposals faster
**Metric:** 10,000 subscribers, 1,000 paid, $100K MRR

Most small GovCon firms don't have dedicated proposal writers. We use AI to generate first-draft proposal sections based on the solicitation + company profile.

**What ships:**
- Solicitation parser (extracts PWS, evaluation criteria, compliance matrix)
- AI proposal section writer (executive summary, technical approach, past performance)
- Compliance checker (flags missing requirements)
- Win theme generator (based on competitor analysis + agency priorities)
- Proposal library (reusable boilerplate by vertical)
- Collaboration tools (multi-user editing, version control)

**AI models:**
- Fine-tuned on 10,000+ winning proposals (public + customer-contributed)
- Agency-specific writing style analysis (e.g., "DHS prefers active voice, DoD wants passive")
- Evaluation criteria weighting (detect which sections are worth the most points)

**Success criteria:**
- 100+ proposals started in the platform
- First customer wins contract using AI-generated proposal sections
- NPS >50 among proposal users

---

### Phase 5: Win Probability Scoring + Market Intelligence (Months 13-18)
**Goal:** Full intelligence suite — predictive + prescriptive
**Metric:** 20,000 subscribers, 2,500 paid, $250K MRR

We've built the dataset (18 months of awards + user feedback). Now we train predictive models and sell market intelligence reports.

**What ships:**
- Win probability scoring (pre-RFP and post-submission)
- Market trend reports (quarterly deep dives by vertical)
- Agency spending forecasts (budget justification analysis)
- Competitor tracking dashboard (who's winning what)
- Pricing intelligence (what agencies pay for specific services)
- Pipeline analytics for BD teams (conversion funnel, win rate tracking)

**Advanced features:**
- Recompete risk scoring (how defensible is your incumbent position?)
- Teaming matchmaking (find complementary partners)
- Solicitation deadline calendar (sync to Google Calendar)
- Integration with CRM systems (Salesforce, HubSpot, Deltek)

**Data science capabilities:**
- Historical win rate by agency/vertical/contract size
- Predictive models for recompete outcomes
- Anomaly detection (unusual spending patterns = new requirements)
- Relationship mapping (which program managers work with which contractors)

**Success criteria:**
- Win probability model accuracy >70%
- First enterprise contract ($50K+ annual)
- Expansion into non-tech verticals (professional services, facilities, etc.)

---

## Revenue Model Evolution

| Phase | Pricing | ARPU | Target |
|-------|---------|------|--------|
| Phase 1 | Free + $99/mo Pro | $10 | 50 paid |
| Phase 2 | Free + $149/mo Pro + $499/mo Team | $30 | 200 paid |
| Phase 3 | $199 Starter + $499 Pro + $999 Enterprise | $60 | 500 paid |
| Phase 4 | $299 Starter + $799 Pro + $1999 Enterprise | $100 | 1,000 paid |
| Phase 5 | $499 Pro + $1999 Team + Custom Enterprise | $200 | 2,500 paid |

**Phase 1 tier breakdown:**
- **Free:** Top 10 opportunities, weekly newsletter only
- **Pro ($99/mo):** Full report, recompete analysis, agency trends, CSV export

**Phase 3 tier breakdown (example):**
- **Starter ($199/mo):** Daily alerts, basic filtering, 1 user
- **Pro ($499/mo):** Opportunity matching, win probability, 3 users, API access
- **Enterprise ($999/mo):** Proposal assistance, custom alerts, 10 users, CRM integration, account manager

---

## Go-to-Market Strategy by Phase

### Phase 1: Content-Led Growth
- Weekly LinkedIn posts with key insights from newsletter
- Guest posts on GovCon industry blogs (GovConWire, ExecutiveBiz, FedScoop)
- SEO for "[agency] contract opportunities" and "federal recompete tracker"
- Direct outreach to 100 target accounts (BD managers at 8(a) firms, mid-tier primes)

### Phase 2: Community + Referral
- Private Slack for paid subscribers (BD war stories, teaming opportunities)
- Referral program (give 1 month, get 1 month free)
- Webinars on capture strategy (with industry experts as guests)
- Partnership with PTAC networks (Procurement Technical Assistance Centers)

### Phase 3: Sales-Led for Enterprise
- Hire first sales rep (inside sales, quota = 10 paid/month)
- Attend industry conferences (SEWP Summit, AFCEA, NDIA)
- Case studies + testimonials from early customers
- Freemium → paid conversion playbook (targeted nurture sequences)

### Phase 4-5: Platform Play
- Integration partnerships (Deltek, GovWin, Salesforce)
- Data partnerships (resell our market intelligence to primes)
- Agency relationship program (sponsor agency industry days)
- Expansion into adjacent verticals (construction, healthcare, logistics)

---

## Risks & Mitigations

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| Users don't pay for newsletter | High | High | Launch paid tier immediately (no long free trial). Test $99 price point. Be willing to drop to $49 if conversion <5%. |
| Data quality issues (USAspending API lags) | Medium | Medium | Add SAM.gov scraper as backup. Build redundancy into pipeline. |
| Large competitors (GovWin, Bloomberg Gov) copy us | Medium | High | Speed + specialization. We go deeper on tech verticals than generalist tools. Build community moat (Slack, referrals). |
| Churn after first month | High | High | Onboarding sequence focuses on quick wins (set up alerts, download CSV, save first search). Monthly "wins report" showing ROI. |
| Proposal assistance hits legal/ethics issues | Low | High | Clear disclaimers: "AI-generated content must be reviewed." No auto-submission. Partner with proposal consultants for review service. |

---

## Key Assumptions to Validate

1. **Small GovCon firms will pay $99/mo for intelligence** — Test in first 30 days. Need 10 paid subscribers by April 15.
2. **Users want daily alerts more than weekly deep dives** — Survey users in Phase 1 before building Phase 2.
3. **Opportunity matching is more valuable than proposal writing** — A/B test messaging. Which drives more upgrades?
4. **Market size is 50,000+ potential customers** — Validate by tracking SAM.gov active bidders in our verticals.
5. **Win probability models require 10,000+ data points to be accurate** — Start tracking outcomes now. User feedback = ground truth labels.

---

## North Star Metrics

- **Phase 1:** Paid subscriber count (target: 50)
- **Phase 2:** Daily active users on dashboard (target: 500)
- **Phase 3:** Opportunities matched per user per week (target: 5)
- **Phase 4:** Proposals started in platform (target: 100)
- **Phase 5:** Annual contract value (target: $3M ARR)

---

## When to Build vs. Buy

**Build:**
- Core data pipeline (USAspending, SAM.gov integration)
- Insights engine (AI analysis, recompete detection)
- Opportunity matching algorithm (our secret sauce)
- Newsletter formatting + distribution logic

**Buy/Integrate:**
- Email platform (Beehiiv → ConvertKit → Customer.io as we scale)
- Payment processing (Stripe)
- CRM (HubSpot or Salesforce)
- Analytics (PostHog or Mixpanel)
- Customer support (Intercom)

**Partner:**
- Proposal review services (hire consultants, don't build in-house)
- Agency training (co-market with PTAC networks)
- Data enrichment (partner with Dun & Bradstreet for company intelligence)

---

## Success Definition

**By Month 12:**
- 5,000 total subscribers
- 500 paying customers
- $50K MRR ($600K ARR)
- 4.5-star rating on G2/Capterra
- First enterprise customer ($50K+ annual contract)
- Profitable unit economics (LTV:CAC >3:1)

**By Month 18:**
- 20,000 total subscribers
- 2,000 paying customers
- $200K MRR ($2.4M ARR)
- Product-qualified leads (PQL) from free tier = 50% of new paid
- Churn <5% monthly
- Ready for Series A fundraising ($5M+ round)
