# GovCon Weekly Intelligence — Product Roadmap & Value Strategy

**Synthesized from:** 5 parallel research agents covering data sources, enterprise platform reverse-engineering, pain point deep dives, monetization models, and new section concepts.
**Date:** March 18, 2026

---

## The One-Paragraph Strategy

**Build a weekly intelligence newsletter ($249-$699/yr) that delivers 70-80% of the value of $5K-$200K/yr enterprise platforms by cross-referencing 6+ free public data sources with AI synthesis and editorial voice. Use the newsletter as a customer acquisition engine, then layer community, data products, events, and courses to reach $5M ARR within 24 months. Three signature features — "Is It Wired?" scoring, Bridge Contract Watch, and BD-focused Protest Report — have no equivalent at any price point and create the competitive moat.**

---

## The Core Insight

Every research stream converged on the same finding:

> **The value isn't in any single data source — it's in cross-referencing.** Nobody connects budget signals (J-books) to workforce data (OPM) to opportunities (SAM.gov) to awards (USAspending) to protests (GAO) in plain English for small firms.

The $15K-50K bid/no-bid decision happens weekly at thousands of firms. Preventing one bad bid per quarter saves 30-100x the subscription cost. That's the ROI pitch.

---

## What Subscribers Get (Mapped to Enterprise Value)

| Intelligence Layer | Our Sections | Enterprise Equivalent | Their Price |
|---|---|---|---|
| Opportunity Discovery | Recompete Alerts, Bridge Watch, Calendar, Set-Aside Spotlight | GovTribe | $1,350/yr |
| Competitive Intelligence | "Is It Wired?", Incumbent Report Card, Protest Report, Subcontractor Signal | GovWin IQ | $5,000+/yr |
| Market Intelligence | Vehicle Tracker, Market Pulse, AI/Automation Watch, Price-to-Win | BGOV | $8,000+/yr |
| Strategic Intelligence | Budget Preview, DOGE Tracker, Personnel Moves | Govini | $50,000+/yr |
| Editorial Synthesis | "Why They Won", "If You Lost", Action Items, One to Watch | No equivalent | Priceless |
| **Our price** | | | **$249-$699/yr** |

---

## New Sections to Build (Priority Order)

### Tier 1: Launch Immediately (Weeks 1-2)

| Section | What It Is | Data Source | Effort | Moat |
|---|---|---|---|---|
| **"Is It Wired?" Scorecard** | 0-100 score on whether a recompete is pre-determined for incumbent | USAspending (`extent_competed`, `number_of_offers`, `solicitation_procedures`) | Medium | **No competitor has this at any price** |
| **Bridge Contract Watch** | Track contracts on life support — each one signals an imminent recompete | USAspending keyword search: "bridge contract", "bridge extension" | Low | **No competitor curates this** |
| **Set-Aside Spotlight** | Which agencies are behind on SB goals = where set-asides will surge | SBA Scorecards + USAspending `type_set_aside` | Low-Med | Unique synthesis |
| **Calendar: What's Coming** | Industry days, RFI deadlines, procurement forecasts | SAM.gov Special Notices + agency forecasts | Low-Med | Utility that drives opens |

### Tier 2: Weeks 3-6

| Section | What It Is | Data Source | Effort | Moat |
|---|---|---|---|---|
| **Protest Report** | Weekly GAO protest digest with BD implications (not legal analysis) | GAO decisions scrape + USAspending cross-ref | Medium | **No BD-focused protest digest exists** |
| **Vehicle Tracker** | Task order velocity, ceiling utilization, hot/dying vehicles | USAspending IDV endpoints | Medium | Unique at this price |
| **AI/Automation Watch** | Tech mandates creating procurement demand (zero trust, FedRAMP, AI EOs) | Federal Register + agency directives | Low-Med | Good for SEO/shares |
| **Incumbent Report Card** | Inferred performance signals from contract mods, options, terminations | USAspending modification history | Medium | Unique approach |

### Tier 3: Weeks 7-12

| Section | What It Is | Data Source | Effort |
|---|---|---|---|
| **Price-to-Win Intel** | Labor rate benchmarks from GSA Schedules + award data | GSA eLibrary + USAspending | Medium |
| **Subcontractor Signal** | Prime-sub relationship mapping from subaward data | SAM.gov subaward API | Medium |
| **Dead Contract Walking** | Termination risk scoring for active contracts | USAspending + DOGE signals | High |

### Phase 2: After Month 3

| Section | What It Is | Effort | Tier |
|---|---|---|---|
| **Budget Season Preview** | Program-level R-2/P-1 analysis, 12-18 month forward look | High (seasonal) | Insider |
| **Teaming Board** | Community-powered partner matching | High (needs community) | Insider |
| **Personnel Moves** | SES appointments, new COs, program manager rotations | High (manual) | Insider |
| **Win/Loss Debrief** | Statistical patterns from award outcomes + protest insights | High | Pro (monthly) |

---

## Free vs. Pro vs. Insider Content Gate Strategy

| Content | Free | Pro ($249/yr) | Insider ($699/yr) |
|---|---|---|---|
| Bridge Watch | 3 contracts/week | Full list + analysis | Full + alerts |
| "Is It Wired?" | Score only (0-100) | Score + all factors | Score + factors + historical |
| Recompete Alerts | 2 cards (headline only) | All cards + winnability | All + who should pursue |
| Awards | Headlines | Why They Won / If You Lost | + Market Signal |
| Set-Aside Spotlight | Concept/overview | Agency-level gap analysis | Agency + goal crunch timing |
| Protest Report | 1 "protest of the week" | Full weekly digest | + alerts on tracked opps |
| Action Items | Top 3 | All items | + priority briefing |
| DOGE Tracker | Headlines | Full agency detail | + contractor exposure |
| Calendar | 2-week lookahead | 90-day lookahead | + personalized alerts |
| Community (Slack) | -- | -- | Full access |
| Monthly live briefing | -- | -- | Full access |
| Flash alerts | -- | -- | Same-day alerts |

**Key principle (from research):** Gate the analysis, not the data. Free sees the cards; paid sees the "so what."

---

## The GovCon Health Index (Brand Asset)

**What:** Monthly proprietary metric (0-100) scoring federal procurement market health.

**Components (weighted):**
- Federal spending velocity (QoQ change) — 25%
- Competition density (avg bidders/solicitation) — 15%
- Small business utilization rate — 15%
- GAO protest rate — 10%
- Recompete volume (contracts expiring in 180d) — 10%
- Set-aside utilization by category — 10%
- Average time to award — 10%
- DOGE impact score — 5%

**Cost to create:** 2 days. **Ongoing:** 2 hours/month.

**Why it matters:** When FedScoop writes "The GovCon Health Index dropped 6 points in March," you've built a brand asset that compounds forever. No competitor has this.

---

## Data Pipeline Architecture

### MVP Sources (5 free APIs)

| Source | Auth | Refresh | Primary Use |
|---|---|---|---|
| USAspending API | None | Monthly | Awards, incumbents, mods, spending trends |
| SAM.gov Opportunities API | Free API key | Real-time | Solicitations, Sources Sought, RFIs |
| Federal Register API | None | Daily | Regulatory changes, proposed rules |
| GAO Decisions | Scrape | Weekly | Protest intelligence |
| SBA Scorecards | Manual download | Annual | Set-aside gap analysis |

### New API Fields to Capture

Add to enrichment pipeline:
```
extent_competed              → "Is It Wired?" scoring
number_of_offers_received    → Competition density
solicitation_procedures      → Sole source detection
other_than_full_and_open     → Non-competitive flag
type_of_contract_pricing     → FFP vs T&M vs CPFF analysis
subcontracting_plan          → Sub-tier intelligence
```

All available from USAspending `/awards/{id}/` endpoint, no new access needed.

### Tier 2 Sources (add months 2-6)

| Source | Auth | Use |
|---|---|---|
| SAM.gov Entity API | Free key (10 req/day) | New registrations, competitor tracking |
| SAM.gov Subaward API | Free key | Prime-sub mapping |
| SBIR API | None | Technology pipeline, Phase II→III tracking |
| OPM Workforce CSV | Download | Agency staffing, DOGE impact |
| SEC EDGAR | None | Prime contractor health signals |
| GSA eLibrary | None | Labor rate benchmarks |

---

## Revenue Roadmap

### Phase 1: Foundation (Months 1-3) — $11K-$29K/mo

| Stream | Revenue |
|---|---|
| Newsletter subscriptions (50 paid) | $3,500-$5,000/mo |
| Consulting (3-5 clients @ $2-4K/mo) | $6,000-$20,000/mo |
| Sponsorship (1 per issue) | $2,000-$4,000/mo |

### Phase 2: Scale (Months 4-6) — $33K-$67K/mo

| Stream | Revenue |
|---|---|
| Newsletter subscriptions (200 paid) | $12,000-$18,000/mo |
| Consulting (5-8 clients) | $10,000-$32,000/mo |
| Events (1 workshop/quarter) | $3,000-$5,000/mo amortized |
| First course ($199) | $4,000/mo |
| Sponsorship | $4,000-$8,000/mo |

### Phase 3: Platform (Months 7-12) — $93K-$170K/mo

| Stream | Revenue |
|---|---|
| Newsletter + content subs (500 paid) | $30,000-$50,000/mo |
| Data platform (50 accounts) | $15,000-$25,000/mo |
| Consulting (8-10 clients, selective) | $16,000-$40,000/mo |
| Courses (3 courses, 50 sales/mo) | $15,000-$20,000/mo |
| Events (workshops + summit) | $8,000-$15,000/mo |
| Sponsorship + matchmaking | $9,000-$20,000/mo |
| **Total Year 1** | **$1.1M-$2.0M** |

### Phase 4: The $5M Version (Months 13-24)

```
Newsletter + Content Subscriptions    $800K-$1.2M
Data Platform (SaaS)                  $1.5M-$2.0M
Events                                $500K-$800K
Courses + Training                    $500K-$800K
Enterprise Contracts                  $500K-$1.0M
Consulting/Advisory                   $300K-$500K
Sponsorship + API + Licensing         $400K-$700K
─────────────────────────────────────
TOTAL                                 $4.5M-$7.0M
```

**Team:** 7-8 people. **Margins:** 60-70% gross.

---

## 15 Pain Points We Solve (Ranked by Value)

| # | Pain Point | Our Solution | ROI to Subscriber |
|---|---|---|---|
| 1 | Bid/no-bid ($15-50K decision) | "Is It Wired?" + winnability scoring | 30-100x subscription cost |
| 2 | Incumbent intelligence gap | Recompete Alerts + Incumbent Report Card | Hours saved per pursuit |
| 3 | SAM.gov search disaster | Curated opportunity roundups by domain | Time savings + missed-opp prevention |
| 4 | DOGE chaos / no source of truth | DOGE Tracker with agency risk ratings | Contract survival intelligence |
| 5 | Price pressure on FFP contracts | "Know Your Rights" FAR explainers | Margin protection |
| 6 | "Wired contract" detection | "Is It Wired?" Scorecard (7-signal checklist) | $15-50K saved per bad bid avoided |
| 7 | Don't know what evaluators care about | "From the Other Side" COR/CO perspectives | Proposal quality improvement |
| 8 | Proposal volume explosion | AI-for-proposals best practices | Efficiency gain |
| 9 | Past performance catch-22 | Subcontracting opportunities + mentor-protege spotlights | Pathway to first win |
| 10 | Vehicle strategy confusion | GWAC/IDIQ Vehicle Tracker | Strategic positioning |
| 11 | Payment delays (Net 30 ≠ 30) | Cash flow survival guide + agency payment data | Financial planning |
| 12 | Competitive intelligence void | Award trend analysis + pricing benchmarks | Win rate improvement |
| 13 | Regulatory whiplash | Weekly regulatory digest with impact ratings | Compliance + opportunity |
| 14 | Pre-RFP shaping window missed | Bridge Watch + Pipeline Preview + Calendar | 12-18 month head start |
| 15 | Small business isolation | Community (Slack) + peer networking | Peer support + teaming |

---

## Three Unfair Advantages (What We Do That Enterprise Platforms Can't)

1. **Editorial voice + contrarian analysis.** Platforms must stay neutral because they serve all sides. We can say "this recompete is wired, don't waste your B&P budget." No $200K platform will ever do that.

2. **Cross-source synthesis at speed.** AI lets us connect budget → workforce → opportunities → awards → protests into narrative in one week. BGOV analyst reports take months. By the time GovWin publishes a market assessment, we've covered it in 3 weekly issues.

3. **DOGE/disruption coverage.** Enterprise platforms are built for steady-state procurement. We cover disruption in real-time. This is the highest-demand topic right now and nobody serves it well.

---

## Positioning

> **"We're not replacing GovWin. We're replacing the $0 your people currently spend on synthesis — and we're cheaper than the time they waste doing it themselves."**

---

## Immediate Next Actions

1. **Build the "Is It Wired?" scoring algorithm** using USAspending API fields
2. **Run first Bridge Watch query** — keyword search for bridge contracts, validate data quality
3. **Download SBA Scorecards** and build Set-Aside gap analysis for top 10 agencies
4. **Calculate first GovCon Health Index** retroactively for 12 months
5. **Set up SAM.gov API key** for Opportunities and Entity endpoints
6. **Draft the free-tier lead magnet**: "Is Your Next Bid Wired? The 7-Signal Checklist"
7. **Add new sections to newsletter data model** (`corrected_all.json`)
8. **Update HTML template** to render new sections
9. **Launch Slack workspace** for future Insider community
10. **Pitch 3 GovCon media outlets** on the Health Index as a quotable metric

---

## Source Files

| File | Contents |
|---|---|
| `research/DATA_SOURCES_ANALYSIS.md` | 20+ data sources with APIs, refresh rates, unique insights |
| `research/ENTERPRISE_FEATURE_ANALYSIS.md` | 7 platforms reverse-engineered, replicability matrix |
| `research/PAIN_POINTS_DEEP_DIVE.md` | 15 intelligence moments from Reddit, Lohfeld, job postings |
| `research/MONETIZATION_MODELS.md` | 9 revenue streams, phased roadmap, benchmark newsletter models |
| `research/NEW_SECTIONS_ANALYSIS.md` | 15 new section concepts with feasibility, effort, tier assignment |
| `RESEARCH_SYNTHESIS.md` | Market sizing, competitive gaps, audience personas |
| `COMPETITIVE_ANALYSIS.md` | 14 competitors analyzed |
| `VISUAL_DESIGN_BENCHMARK.md` | 10 newsletter designs benchmarked |
