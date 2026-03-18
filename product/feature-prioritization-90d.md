# Feature Prioritization: Next 90 Days
**GovCon Weekly Intelligence** | Version 1.0 | March 18, 2026

---

## Prioritization Framework: RICE Score

We use RICE scoring to prioritize features objectively:

**RICE = (Reach × Impact × Confidence) ÷ Effort**

- **Reach:** How many users will this affect per quarter? (0-10 scale)
- **Impact:** How much will this move our North Star metric? (0.25 = Minimal, 0.5 = Low, 1 = Medium, 2 = High, 3 = Massive)
- **Confidence:** How certain are we about Reach and Impact? (50%, 80%, 100%)
- **Effort:** How many person-days will this take? (1-40)

**High priority:** RICE score >10
**Medium priority:** RICE score 5-10
**Low priority:** RICE score <5

---

## Strategic Context

### Phase 1 Goals (Months 1-3)
1. Ship 4 consecutive weekly newsletters on time
2. Acquire 500 subscribers (50 paid)
3. Validate willingness to pay ($5K MRR)
4. Learn what content drives conversion and retention

### Current State (Week 0)
**What works:**
- Data pipeline (`pipeline.py`) pulls awards across 9 verticals
- Insights engine (`generate_insights.py`) produces high-quality AI analysis
- Landing page exists and looks professional

**What's blocking launch:**
- `generate_report.py` doesn't exist (need to format insights into newsletter structure)
- `report_to_html.py` doesn't exist (need HTML email conversion)
- Beehiiv not set up (distribution channel)
- No payment integration (can't collect revenue)
- No Terms of Service / Privacy Policy (legal blocker)

### User Feedback Signals (Hypothesized)
Based on persona research, users will likely ask for:
1. **CSV export of raw data** (Sarah and Mike need to import into their systems)
2. **Filtering by vertical** (Sarah only cares about Cybersecurity, not all 9 verticals)
3. **Saved searches** (Mike wants to track specific agencies or NAICS codes)
4. **Mobile-friendly format** (Jim reads on his phone 40% of the time)
5. **Shorter newsletter** (Jim doesn't have time for 5,000 words)

---

## 90-Day Feature Roadmap

### Week 0-1: Launch Blockers (Must Ship)
**Goal:** Produce and send first newsletter on March 23, 2026

#### 1. Build `generate_report.py`
**RICE Score:** (10 × 3 × 100%) ÷ 2 = **150** 🔥🔥🔥
- **Reach:** 10 (affects every user, every week)
- **Impact:** 3 (Massive — can't launch without this)
- **Confidence:** 100% (we know exactly what to build)
- **Effort:** 2 days

**What it does:**
- Takes insights markdown from `generate_insights.py`
- Formats into newsletter structure (Executive Summary, Recompetes, Agency Trends, Quick Hits)
- Outputs clean markdown with consistent headers and formatting
- Validates all data (no broken links, no missing fields)

**Acceptance criteria:**
- Outputs markdown file: `output/newsletter_{date}.md`
- Executive Summary is <200 words
- Recompete section has 4-6 entries with all required fields (incumbent, timeline, analysis)
- Quick Hits section has 10 notable awards
- All USAspending links are valid

---

#### 2. Build `report_to_html.py`
**RICE Score:** (10 × 3 × 100%) ÷ 2 = **150** 🔥🔥🔥
- **Reach:** 10 (affects every user, every week)
- **Impact:** 3 (Massive — Beehiiv requires HTML)
- **Confidence:** 100% (standard Markdown → HTML conversion)
- **Effort:** 2 days

**What it does:**
- Converts newsletter markdown to HTML with inline CSS
- Matches brand colors (navy #0A1628, gold #C5A44E)
- Ensures Gmail/Outlook compatibility (no external stylesheets)
- Responsive design (mobile-friendly)
- Includes Beehiiv merge tags for unsubscribe, forward links

**Acceptance criteria:**
- Outputs HTML file: `output/newsletter_{date}.html`
- Renders correctly in Gmail, Outlook, Apple Mail (test on all 3)
- Mobile-responsive (test on iPhone and Android)
- All links track clicks (UTM parameters)

---

#### 3. Set Up Beehiiv Newsletter
**RICE Score:** (10 × 3 × 100%) ÷ 1 = **300** 🔥🔥🔥
- **Reach:** 10 (distribution channel for all users)
- **Impact:** 3 (Massive — can't send newsletter without this)
- **Confidence:** 100% (straightforward setup)
- **Effort:** 1 day

**What it does:**
- Create Beehiiv account (Launch plan, $49/mo)
- Configure newsletter branding (logo, colors, footer)
- Set up free tier vs. paid tier segmentation
- Configure automated send (Mondays at 7 AM EST)
- Test send to internal team

**Acceptance criteria:**
- Newsletter sends successfully to test list
- Free tier receives limited content (top 3 recompetes only)
- Paid tier receives full content
- Unsubscribe and forward links work
- Analytics dashboard shows opens, clicks, unsubscribes

---

#### 4. Stripe Payment Integration
**RICE Score:** (10 × 3 × 100%) ÷ 1 = **300** 🔥🔥🔥
- **Reach:** 10 (every paid user)
- **Impact:** 3 (Massive — can't collect revenue without this)
- **Confidence:** 100% (standard Stripe integration)
- **Effort:** 1 day

**What it does:**
- Integrate Stripe Checkout on landing page
- Configure $99/month Pro tier subscription
- Webhook to sync paid users with Beehiiv (auto-add to Pro list)
- Success page after payment ("Check your email for the next newsletter")
- Cancellation flow (self-serve in Stripe portal)

**Acceptance criteria:**
- User can subscribe to Pro tier from landing page
- Payment captured in Stripe
- User automatically added to Beehiiv Pro list
- Cancellation flow works (user removed from Pro list)

---

#### 5. Terms of Service + Privacy Policy
**RICE Score:** (10 × 2 × 100%) ÷ 0.5 = **400** 🔥🔥🔥
- **Reach:** 10 (legal requirement for all users)
- **Impact:** 2 (High — blocks launch, but not core value)
- **Confidence:** 100% (template-based, straightforward)
- **Effort:** 0.5 days (use templates)

**What it does:**
- Terms of Service page (liability, refunds, acceptable use)
- Privacy Policy page (data collection, email usage, GDPR compliance)
- Footer links on landing page and in newsletter

**Acceptance criteria:**
- ToS and Privacy pages live at govconintel.com/terms and /privacy
- CAN-SPAM compliant (unsubscribe link, physical address)
- GDPR compliant (data collection disclosure, user rights)

---

### Week 1-2: MVP Enhancements (Quick Wins)
**Goal:** Improve conversion and retention based on first 100 subscribers

#### 6. CSV Export for Paid Users
**RICE Score:** (8 × 2 × 80%) ÷ 1 = **128** 🔥🔥
- **Reach:** 8 (50% of paid users will use this, per persona research)
- **Impact:** 2 (High — drives paid conversion and retention)
- **Confidence:** 80% (Sarah and Mike explicitly need this)
- **Effort:** 1 day

**What it does:**
- Export all awards from the week to CSV
- Columns: Award ID, Recipient, Agency, Amount, NAICS, Description, Start Date, End Date, Vehicle, Set-Aside, USAspending Link
- Download link in newsletter (paid tier only)
- Hosted on S3 or similar (publicly accessible with unguessable URL)

**Acceptance criteria:**
- CSV downloads successfully
- Opens in Excel/Google Sheets without formatting issues
- All 500+ awards from the week are included
- Free tier users see "Upgrade to Pro for CSV export" message

---

#### 7. Referral Program (Forward to a Friend)
**RICE Score:** (10 × 1 × 80%) ÷ 0.5 = **160** 🔥🔥
- **Reach:** 10 (virality affects all users)
- **Impact:** 1 (Medium — drives acquisition via word-of-mouth)
- **Confidence:** 80% (referral programs work for B2B newsletters, but unclear by how much)
- **Effort:** 0.5 days

**What it does:**
- "Forward to a friend" link in every newsletter
- Track referrals in Beehiiv (who referred whom)
- Referral incentive: Refer 3 people → get 1 month free (for paid users)
- Leaderboard (top referrers featured in newsletter)

**Acceptance criteria:**
- Forward link works and tracks referrer
- Referrer gets credit when new user subscribes
- Auto-apply 1-month discount after 3 referrals
- Dashboard shows referral sources

---

#### 8. A/B Test Subject Lines
**RICE Score:** (10 × 1 × 100%) ÷ 0.5 = **200** 🔥🔥
- **Reach:** 10 (affects all users)
- **Impact:** 1 (Medium — could improve open rate by 5-10%)
- **Confidence:** 100% (A/B testing is proven best practice)
- **Effort:** 0.5 days

**What it does:**
- Test 2 subject line variants each week (Week 1: data-driven vs. curiosity-driven)
- Measure open rate for each variant
- Use winner for full list in Week 2
- Document learnings (what works, what doesn't)

**Example tests:**
- Week 1: "$890M in recompetes hitting in 60 days" vs. "3 recompetes you need to track this week"
- Week 2: "DoD cyber spending up 34%" vs. "Where DoD is spending on cyber this week"
- Week 3: "Your weekly federal contract intelligence" vs. "4 opportunities worth $400M"

**Acceptance criteria:**
- Beehiiv A/B test configured correctly (50/50 split)
- Open rate measured for each variant
- Winner documented in dashboard
- Learnings inform next week's subject line

---

#### 9. Onboarding Email Sequence
**RICE Score:** (10 × 1 × 80%) ÷ 1 = **80** 🔥
- **Reach:** 10 (all new subscribers)
- **Impact:** 1 (Medium — improves activation and early retention)
- **Confidence:** 80% (onboarding works for SaaS, but unclear for newsletters)
- **Effort:** 1 day

**What it does:**
- Day 0 (immediately after signup): Welcome email + what to expect
- Day 3: "How to get the most value from GovCon Intel" (tips: set SAM.gov alerts, download CSV, etc.)
- Day 7: "Upgrade to Pro and unlock full reports" (conversion prompt)
- Day 14: NPS survey ("How likely are you to recommend us?")

**Acceptance criteria:**
- Automated sequence in Beehiiv
- Emails send on schedule
- Open rate >50% for welcome email
- Conversion rate measured for Day 7 upgrade prompt

---

#### 10. Landing Page Improvements
**RICE Score:** (8 × 1 × 100%) ÷ 1 = **80** 🔥
- **Reach:** 8 (affects new visitors, not existing subscribers)
- **Impact:** 1 (Medium — could improve signup conversion by 10-20%)
- **Confidence:** 100% (landing page optimization is proven)
- **Effort:** 1 day

**What it does:**
- Add sample report preview (first 500 words of a real newsletter)
- Testimonials section (once we have 10+ users, add quotes)
- FAQ section (pricing, content, frequency, cancellation)
- Trust signals (# of subscribers, # of awards tracked, data freshness)

**Acceptance criteria:**
- Sample report loads without breaking layout
- Testimonials section ready (populate as we get quotes)
- FAQ answers top 5 questions from user interviews
- Conversion rate measured (visitors → signups)

---

### Week 3-4: Retention & Monetization
**Goal:** Reduce early churn and increase paid conversions

#### 11. Usage Monitoring & Alerts
**RICE Score:** (5 × 2 × 80%) ÷ 1 = **80** 🔥
- **Reach:** 5 (targets at-risk users, ~20% of base)
- **Impact:** 2 (High — prevents churn)
- **Confidence:** 80% (proactive outreach works, but unclear ROI)
- **Effort:** 1 day

**What it does:**
- Track user engagement (opens, clicks, last activity)
- Flag at-risk users (no opens in 2 weeks)
- Automated "We miss you" email with special offer
- Manual outreach for paid users at risk (CPO calls to understand why they're disengaged)

**Acceptance criteria:**
- Dashboard shows at-risk users
- Automated email sends to disengaged users
- Win-back rate measured (% who re-engage)
- Churn prevented = success metric

---

#### 12. In-Email Upgrade Prompts
**RICE Score:** (10 × 1 × 100%) ÷ 0.5 = **200** 🔥🔥
- **Reach:** 10 (all free tier users)
- **Impact:** 1 (Medium — drives paid conversion)
- **Confidence:** 100% (in-content CTAs convert better than footer links)
- **Effort:** 0.5 days

**What it does:**
- Free tier newsletter cuts off after top 3 recompetes
- "Upgrade to Pro to see 3 more recompetes worth $400M" callout box
- CTA button: "Unlock Full Report ($99/mo)"
- Track clicks (measure intent)

**Acceptance criteria:**
- Free tier users see upgrade prompt
- Paid tier users don't see prompt (clean experience)
- Click rate on upgrade CTA measured
- Conversion rate from click to purchase tracked

---

#### 13. First-Month Discount Campaign
**RICE Score:** (8 × 1 × 80%) ÷ 0.5 = **128** 🔥🔥
- **Reach:** 8 (all free tier users in first 30 days)
- **Impact:** 1 (Medium — increases early paid conversion)
- **Confidence:** 80% (discounts work, but risk training users to wait for deals)
- **Effort:** 0.5 days

**What it does:**
- Email campaign (Day 7): "Get 50% off your first month (pay $49 instead of $99)"
- Limited-time offer (expires in 7 days)
- Stripe coupon code: LAUNCH50
- Track redemption rate

**Acceptance criteria:**
- Email sends to free tier users on Day 7
- Coupon works in Stripe
- Conversion rate measured (free → paid with discount)
- Revenue impact tracked (discounted MRR vs. full-price MRR)

---

#### 14. Exit Survey for Churned Users
**RICE Score:** (3 × 2 × 100%) ÷ 0.5 = **120** 🔥🔥
- **Reach:** 3 (only churned users, ~5% of paid base monthly)
- **Impact:** 2 (High — informs product improvements to prevent future churn)
- **Confidence:** 100% (exit surveys are standard best practice)
- **Effort:** 0.5 days

**What it does:**
- Automated email when user cancels subscription
- Survey: "Why did you cancel?" (multiple choice + open text)
- Options: Too expensive, Not finding relevant opportunities, Too much information, Using another tool, Budget cuts, Other
- Offer win-back discount (50% off for 3 months to stay)

**Acceptance criteria:**
- Survey sends automatically on cancellation
- Response rate >40% (typical for exit surveys)
- Data logged in spreadsheet (review monthly)
- Win-back rate measured (% who accept discount offer)

---

#### 15. Weekly Metrics Dashboard
**RICE Score:** (10 × 0.5 × 100%) ÷ 1 = **50** 🔥
- **Reach:** 10 (internal team, affects all future decisions)
- **Impact:** 0.5 (Low — doesn't directly affect users, but enables better decisions)
- **Confidence:** 100% (metrics are essential)
- **Effort:** 1 day

**What it does:**
- Google Sheet or Notion dashboard
- Pulls data from Beehiiv (subscribers, opens, clicks) and Stripe (MRR, churn)
- Weekly snapshot: Total subscribers, Paid subscribers, MRR, Open rate, CTR, Churn rate, Referrals
- Reviewed every Monday morning before newsletter send

**Acceptance criteria:**
- Dashboard updates automatically (or semi-manually in MVP)
- All key metrics visible at a glance
- Week-over-week change calculated
- Red/yellow/green status based on targets

---

### Week 5-8: Content & Engagement Optimization
**Goal:** Improve newsletter quality and user engagement

#### 16. Vertical Rotation Schedule
**RICE Score:** (10 × 0.5 × 80%) ÷ 0.5 = **80** 🔥
- **Reach:** 10 (all users)
- **Impact:** 0.5 (Low — improves content variety, but unclear if it drives retention)
- **Confidence:** 80% (rotating content keeps newsletter fresh, but some users may want only their vertical)
- **Effort:** 0.5 days

**What it does:**
- Vertical Deep Dive section rotates through 9 verticals on a schedule
- Week 1: Cybersecurity
- Week 2: AI/ML
- Week 3: Cloud
- Week 4: Data Analytics
- Week 5: DevSecOps
- Week 6: Zero Trust
- Week 7: FedRAMP
- Week 8: Identity Management
- Week 9: Networking/SDWAN
- (Repeat)

**Acceptance criteria:**
- Rotation schedule documented
- Each vertical gets deep dive once every 9 weeks
- Users surveyed: "Do you prefer rotating verticals or a fixed focus?" (informs Phase 2 personalization)

---

#### 17. Quick Hits Expansion
**RICE Score:** (10 × 0.5 × 80%) ÷ 0.5 = **80** 🔥
- **Reach:** 10 (all users, Quick Hits is highly read)
- **Impact:** 0.5 (Low — incremental value, but users love scannable lists)
- **Confidence:** 80% (based on scroll depth, Quick Hits is popular)
- **Effort:** 0.5 days

**What it does:**
- Expand Quick Hits from 10 to 20 notable awards
- Add one-line "So What" for each (not just award description)
- Example: "Army Cyber Command — $12.3M zero-trust architecture (NAICS 541512) → **Why it matters:** First major zero-trust award at Army in 6 months. Signals renewed focus."

**Acceptance criteria:**
- Quick Hits section has 20 entries
- Each entry has 1-sentence context ("Why it matters")
- Section remains scannable (<5 min to read all 20)

---

#### 18. Agency Spending Trend Visualizations
**RICE Score:** (8 × 1 × 60%) ÷ 2 = **24** 🟡
- **Reach:** 8 (users who care about agency trends, ~80%)
- **Impact:** 1 (Medium — makes trends more digestible, but unclear if it drives conversion)
- **Confidence:** 60% (visualizations are nice-to-have, but we don't know if users will engage)
- **Effort:** 2 days (charting in Python, embedding in email)

**What it does:**
- Generate simple bar charts or line graphs for agency spending trends
- Example: "DoD cyber spending by month (Jan-Mar 2026)"
- Embed as inline image in email (not external link)

**Acceptance criteria:**
- Chart renders correctly in email clients
- Data is accurate (validated against USAspending)
- Users surveyed: "Do you find the charts helpful?" (informs whether to continue)

**Decision:** DEFER to Week 9+ (medium priority, but higher effort)

---

#### 19. Historical Archive (Web)
**RICE Score:** (8 × 0.5 × 80%) ÷ 2 = **16** 🟡
- **Reach:** 8 (users who want to reference past reports)
- **Impact:** 0.5 (Low — nice-to-have, but most users only care about current week)
- **Confidence:** 80% (easy to build, but unclear if users will use it)
- **Effort:** 2 days (build simple web page with list of past reports)

**What it does:**
- Web page at govconintel.com/archive
- List of past newsletters (4 weeks free, full archive for paid)
- Click to read in browser (HTML version)

**Acceptance criteria:**
- Archive page exists and links work
- Free users see last 4 weeks
- Paid users see full history
- Page is indexed by Google (SEO benefit)

**Decision:** DEFER to Week 9+ (nice-to-have, but not urgent)

---

#### 20. Mobile Optimization Audit
**RICE Score:** (10 × 1 × 100%) ÷ 1 = **100** 🔥
- **Reach:** 10 (40-50% of users read on mobile, per persona research)
- **Impact:** 1 (Medium — improves experience, but unclear if it drives retention)
- **Confidence:** 100% (mobile optimization is proven best practice)
- **Effort:** 1 day

**What it does:**
- Test newsletter on iPhone, Android, Gmail app, Outlook app
- Fix layout issues (text too small, images don't load, buttons not tappable)
- Ensure scannable on mobile (headers, short paragraphs, bullet points)

**Acceptance criteria:**
- Newsletter renders correctly on all major mobile email clients
- Text is readable without zooming
- Links and buttons are tappable (48px min touch target)
- User survey: "Do you read on mobile? How's the experience?"

---

### Week 9-12: Phase 2 Prep & Feedback Loop
**Goal:** Learn from first 8 weeks, prepare for Phase 2 features

#### 21. User Feedback Survey (Comprehensive)
**RICE Score:** (10 × 2 × 100%) ÷ 1 = **200** 🔥🔥
- **Reach:** 10 (all users)
- **Impact:** 2 (High — informs product roadmap)
- **Confidence:** 100% (user feedback is essential)
- **Effort:** 1 day

**What it does:**
- Send survey to all users (free + paid)
- Questions:
  1. What's most valuable in the newsletter? (recompetes, agency trends, quick hits, etc.)
  2. What would you like to see more of?
  3. Would you pay for daily alerts? (yes/no, gauge Phase 2 demand)
  4. How likely are you to recommend us? (NPS)
  5. What tools do you currently use for GovCon intelligence? (competitive analysis)

**Acceptance criteria:**
- Survey sent to all users
- Response rate >30%
- Data analyzed and summarized (inform Phase 2 priorities)
- Key insights shared with team

---

#### 22. Case Study Development
**RICE Score:** (5 × 2 × 60%) ÷ 2 = **30** 🟡
- **Reach:** 5 (future prospects, not current users)
- **Impact:** 2 (High — case studies drive enterprise sales, but we're not there yet)
- **Confidence:** 60% (unclear if we'll have a case study-worthy customer by Week 12)
- **Effort:** 2 days (interview user, write case study, get approval)

**What it does:**
- Identify 1-2 power users who've gotten value from the newsletter
- Interview: "Did you find an opportunity via GovCon Intel? Did you win it?"
- Write case study: "[Company] won a $4M contract with GovCon Intel"
- Get user approval, publish on landing page

**Acceptance criteria:**
- At least 1 case study published
- Includes company name, contract value, testimonial quote
- Used in sales outreach and landing page

**Decision:** DEFER to Week 12+ (depends on user success stories emerging)

---

#### 23. Competitive Analysis Deep Dive
**RICE Score:** (5 × 1 × 80%) ÷ 2 = **20** 🟡
- **Reach:** 5 (internal team, informs positioning)
- **Impact:** 1 (Medium — helps differentiation, but doesn't directly affect users)
- **Confidence:** 80% (competitive intel is always useful)
- **Effort:** 2 days (research GovWin, Bloomberg Gov, CB Insights, etc.)

**What it does:**
- Deep dive on 3 main competitors (GovWin IQ, Bloomberg Government, FedScoop)
- Pricing, features, user reviews, strengths, weaknesses
- Positioning: Where do we win? Where do we lose?
- Inform messaging ("We're more actionable than GovWin, more affordable than Bloomberg Gov")

**Acceptance criteria:**
- Competitive matrix documented
- Positioning messaging updated on landing page
- Sales team has talking points for "Why not just use GovWin?"

**Decision:** DEFER to Week 9-12 (lower priority, but useful for sales)

---

#### 24. Phase 2 Spec: Daily Alerts
**RICE Score:** (10 × 2 × 80%) ÷ 3 = **53** 🔥
- **Reach:** 10 (all users in Phase 2)
- **Impact:** 2 (High — Phase 2 core feature)
- **Confidence:** 80% (user survey will validate demand)
- **Effort:** 3 days (spec, not build — that's Phase 2)

**What it does:**
- Document requirements for Phase 2 Daily Alerts feature
- User profile setup (verticals, agencies, NAICS, set-asides, contract size)
- Alert delivery options (email, Slack, webhook)
- Filtering logic (match user profile to new awards)
- Pricing model (included in Pro tier or separate upsell?)

**Acceptance criteria:**
- PRD written for Daily Alerts
- Wireframes or mockups (basic UX flow)
- Technical architecture spec (database schema for user profiles)
- Ready to build in Month 4

---

#### 25. SAM.gov API Integration (Prep)
**RICE Score:** (8 × 1 × 80%) ÷ 3 = **21** 🟡
- **Reach:** 8 (benefits users who need entity enrichment)
- **Impact:** 1 (Medium — adds company intelligence, but not essential for Phase 1)
- **Confidence:** 80% (SAM.gov API is free and documented)
- **Effort:** 3 days (API integration, data mapping, testing)

**What it does:**
- Integrate SAM.gov Entity Management API
- Enrich recipient companies with: CAGE code, DUNS, certifications (8(a), SDVOSB, WOSB, etc.), company size, address
- Display in newsletter: "Recipient: CyberShield Solutions (8(a), SDVOSB, $8M revenue)"

**Acceptance criteria:**
- SAM.gov API integration working
- 80%+ of recipients enriched (some may not be in SAM.gov)
- Data displayed in newsletter (pilot in Week 12)
- Users surveyed: "Is this enrichment valuable?"

**Decision:** DEFER to Week 9-12 (nice-to-have, but not urgent)

---

## Summary: 90-Day Feature Priorities

### Week 0-1: Launch Blockers (MUST SHIP)
1. Build `generate_report.py` ✅ **RICE 150**
2. Build `report_to_html.py` ✅ **RICE 150**
3. Set up Beehiiv ✅ **RICE 300**
4. Stripe payment integration ✅ **RICE 300**
5. Terms of Service + Privacy Policy ✅ **RICE 400**

**Total effort:** 6.5 days
**Goal:** Ship first newsletter on March 23, 2026

---

### Week 1-2: MVP Enhancements (QUICK WINS)
6. CSV export for paid users ✅ **RICE 128**
7. Referral program ✅ **RICE 160**
8. A/B test subject lines ✅ **RICE 200**
9. Onboarding email sequence ✅ **RICE 80**
10. Landing page improvements ✅ **RICE 80**

**Total effort:** 4 days
**Goal:** Improve conversion and engagement

---

### Week 3-4: Retention & Monetization (CRITICAL)
11. Usage monitoring & alerts ✅ **RICE 80**
12. In-email upgrade prompts ✅ **RICE 200**
13. First-month discount campaign ✅ **RICE 128**
14. Exit survey for churned users ✅ **RICE 120**
15. Weekly metrics dashboard ✅ **RICE 50**

**Total effort:** 3.5 days
**Goal:** Reduce churn, increase paid conversions

---

### Week 5-8: Content & Engagement (OPTIMIZATION)
16. Vertical rotation schedule ✅ **RICE 80**
17. Quick Hits expansion ✅ **RICE 80**
20. Mobile optimization audit ✅ **RICE 100**

**Total effort:** 2 days
**Goal:** Improve content quality and mobile experience

---

### Week 9-12: Phase 2 Prep & Feedback (LEARNING)
21. User feedback survey ✅ **RICE 200**
24. Phase 2 spec: Daily Alerts ✅ **RICE 53**

**Total effort:** 4 days
**Goal:** Learn from Phase 1, prepare for Phase 2

---

## Deferred Features (Not in 90 Days)

These features scored lower on RICE or require Phase 2 infrastructure:

- **Agency spending trend visualizations** (RICE 24) — Defer to Month 4+
- **Historical archive** (RICE 16) — Defer to Month 4+
- **Case study development** (RICE 30) — Defer to Week 12+ (depends on customer wins)
- **Competitive analysis deep dive** (RICE 20) — Defer to Week 9-12 (low priority)
- **SAM.gov API integration** (RICE 21) — Defer to Week 9-12 (nice-to-have)

---

## Resource Allocation

**CTO:** 20 days over 90 days
- Week 0-1: 6.5 days (launch blockers)
- Week 1-2: 4 days (MVP enhancements)
- Week 3-4: 3.5 days (retention & monetization)
- Week 5-8: 2 days (content optimization)
- Week 9-12: 4 days (Phase 2 prep)

**CMO:** 10 days over 90 days
- Week 1-2: 2 days (landing page, referral program)
- Week 3-4: 2 days (discount campaign, metrics dashboard)
- Week 5-8: 3 days (content strategy, A/B testing)
- Week 9-12: 3 days (user survey, case studies)

**CPO:** 8 days over 90 days
- Week 0-1: 1 day (product specs)
- Week 3-4: 2 days (usage monitoring, churn analysis)
- Week 9-12: 5 days (user feedback analysis, Phase 2 spec)

**Total effort:** 38 person-days over 90 days (feasible for small team)

---

## Decision Framework for New Feature Requests

When users request new features, evaluate using this framework:

### 1. Does it increase paid conversions?
- **Yes, directly:** High priority (e.g., CSV export, in-email upgrade prompts)
- **Yes, indirectly:** Medium priority (e.g., mobile optimization, content improvements)
- **No:** Low priority (e.g., historical archive, visualizations)

### 2. Does it reduce churn?
- **Yes, directly:** High priority (e.g., usage monitoring, onboarding sequence)
- **Yes, indirectly:** Medium priority (e.g., content quality, mobile UX)
- **No:** Low priority

### 3. Is it a Phase 2 prerequisite?
- **Yes:** High priority (e.g., Phase 2 spec, user feedback survey)
- **No:** Prioritize based on #1 and #2

### 4. What's the effort?
- **<1 day:** Do it if Impact >0.5
- **1-3 days:** Do it if RICE >50
- **>3 days:** Defer unless RICE >100

---

## Key Assumptions to Validate

1. **CSV export drives paid conversions** → Track upgrade rate before/after adding CSV
2. **Referral program drives 15%+ growth** → Track referral attribution in Beehiiv
3. **Subject line A/B testing improves open rate 5-10%** → Track open rate variance
4. **Onboarding sequence reduces early churn** → Compare churn rate for cohorts with/without onboarding
5. **Mobile optimization improves retention** → Survey mobile users before/after fixes
6. **Users want daily alerts more than weekly deep dives** → User survey in Week 9-12

---

## Success Metrics (90 Days)

**By end of Week 12 (April 30, 2026):**
- 500+ total subscribers ✅
- 50+ paid subscribers (10% conversion) ✅
- $5K+ MRR ✅
- Open rate >30% ✅
- Churn <10% ✅
- NPS >30 ✅
- 4 consecutive weekly newsletters published on time ✅

**Stretch goals:**
- 1,000 total subscribers
- 100 paid subscribers (10% conversion)
- $10K MRR
- Open rate >35%
- Churn <7%
- NPS >40

---

## Phase 2 Trigger (Go/No-Go Decision)

**After 12 weeks, evaluate:**

**GREEN LIGHT (proceed to Phase 2: Daily Alerts):**
- 500+ subscribers, 50+ paid, $5K+ MRR
- Open rate >30%, churn <10%
- User survey shows strong demand for daily alerts (>60% say "yes")
- At least 1 user testimonial or case study

**YELLOW LIGHT (iterate on Phase 1):**
- 300-500 subscribers, 20-50 paid
- Need to improve conversion or retention before scaling
- Double down on content quality, pricing experiments, onboarding

**RED LIGHT (pivot or shut down):**
- <300 subscribers, <20 paid
- High churn (>15%), low NPS (<20)
- User feedback is consistently negative
- Consider: Different target market? Different format? Different pricing?

---

## Conclusion

**The next 90 days are about validation, not scale.**

We're testing 3 core hypotheses:
1. **People will pay $99/mo for curated GovCon intelligence** (test via paid conversion rate)
2. **A weekly newsletter is valuable enough to retain users** (test via churn rate)
3. **Our insights are better than what users get from GovWin/Bloomberg** (test via NPS and competitive displacement)

If we validate all 3, we proceed to Phase 2 (daily alerts, personalization, web dashboard).
If we validate 1-2, we iterate on Phase 1 (improve content, pricing, or targeting).
If we validate 0, we pivot or shut down.

**Focus:** Ship fast, measure everything, learn quickly, adapt or die.
