# GovCon Weekly Intelligence — Startup State

## Company
- **Name:** GovCon Weekly Intelligence
- **One-liner:** AI-powered federal contract intelligence that tells small/mid GovCon firms exactly which opportunities to chase and why
- **Stage:** pre-launch
- **Founded:** 2026-03-18

## Vision
Become the Bloomberg Terminal for small/mid government contractors. Start with a weekly intelligence newsletter, expand to real-time opportunity matching, proposal assistance, and win probability scoring. Every GovCon BD team checks us before making a capture decision.

## Current Priorities (Top 3)
1. **Launch Week (Mar 18-24):** Get landing page live, set up Beehiiv, deploy ToS/Privacy, and send first newsletter to live subscribers
2. **Sprint 1 Goal:** Acquire 100 subscribers through direct outreach and community engagement
3. **Q1 Goal:** Validate product-market fit (500 subscribers, 40% open rate, $5K revenue, 3+ paid conversions)

## What Exists Already
- **Data pipeline** (`pipeline.py`): Working. Pulls awards from USAspending API across 9 verticals (AI/ML, Cybersecurity, Cloud, Data Analytics, DevSecOps, Zero Trust, FedRAMP, Identity Management, Networking/SDWAN). De-duplicates, enriches with NAICS/vehicle/set-aside data.
- **Insights engine** (`generate_insights.py`): Working. AI-generated deep analysis with recompete tracking, trend detection, and actionable "so what" commentary.
- **HTML generator** (`report_to_html.py`): Working. Converts insights to Beehiiv-compatible HTML with inline styles.
- **Landing page** (`landing/index.html`): Built. Navy + gold design, professional look.
- **Pipeline orchestration** (`generate.sh`): Working. End-to-end automation.
- **First report**: Generated for week of March 16-22, 2026 (HTML output confirmed working).
- **Strategy docs**: Sprint plan, Q1 OKRs, and department directives in `strategy/` directory.

## What's Missing (Sprint 1 Blockers)
- **Newsletter distribution** (Beehiiv account setup + signup form integration) — CRITICAL for Day 1
- **Landing page deployment** (Vercel/Netlify/GitHub Pages) — CRITICAL for Day 1
- **Terms of Service / Privacy Policy** on landing page — CRITICAL for Day 1
- **First 50 outreach targets** identified (GovCon BD professionals) — Needed by Day 2
- **Launch content** (LinkedIn posts, email templates) — Needed by Day 2

## What's Deferred (Q2+)
- SAM.gov API integration for entity enrichment
- SEO / content strategy for organic growth
- Pricing model implementation (free tier proven first)
- Pro tier features (daily alerts, API access, advanced search)
- Enterprise features (white-label, custom reports)

## Metrics
| Metric | Current | Target | Updated |
|--------|---------|--------|---------|
| Subscribers | 0 | 100 | 2026-03-18 |
| Paid subscribers | 0 | 10 | 2026-03-18 |
| Weekly reports generated | 1 | 4 | 2026-03-18 |
| Verticals tracked | 9 | 9 | 2026-03-18 |
| Awards processed/week | ~500 | 500+ | 2026-03-18 |

## Department Status
| Role | Status | Current Focus | Blockers |
|------|--------|---------------|----------|
| CEO | **active** | Sprint 1 planning, strategic priorities set | None |
| CTO | **ready** | Test pipeline, deploy to production, monitor data quality | Beehiiv account needed for HTML import test |
| CMO | **ready** | Set up Beehiiv, create launch content, direct outreach | Need Beehiiv account by EOD |
| Sales | **ready** | Identify 50 outreach targets, start warm conversations | None |
| CFO | **ready** | Set up Stripe, finalize pricing model by April 15 | None |
| Legal | **ready** | Generate ToS + Privacy Policy, deploy to landing page | None |
| Ops | **ready** | Automate weekly pipeline, set up monitoring | None |
| CPO | **monitoring** | Collect feedback, prioritize roadmap by April 15 | None |
| Design | **idle** | Landing page and newsletter design complete | None |
| Data | **monitoring** | Data quality audit, baseline metrics | None |
| Customer Success | **standby** | Will activate when first subscribers arrive | None |
| People | **monitoring** | Energy management, sustainable pace | None |

## Recent Decisions
| Date | Decision | Made By | Rationale |
|------|----------|---------|-----------|
| 2026-03-18 | Start as weekly newsletter before building SaaS platform | CEO | Fastest path to audience + revenue validation. Newsletter is the wedge. |
| 2026-03-18 | Focus on 9 tech verticals initially | CEO | Highest contract volume + most underserved by existing tools |
| 2026-03-18 | 7-day launch sprint (Mar 18-24) vs 2-week timeline | CEO | Solo founder = speed is survival. Ship fast, learn fast. |
| 2026-03-18 | Launch with free tier only, defer pricing to April | CEO | Validate demand before pricing; easier to upsell later than down-sell |
| 2026-03-18 | Beehiiv over Substack for newsletter platform | CEO | Better growth tools (referral program, analytics, A/B testing) |
| 2026-03-18 | Direct outreach over paid ads for subscriber acquisition | CEO | $0 budget. LinkedIn + warm emails = highest ROI channel. |
| 2026-03-18 | Q1 success criteria: 500 subs, 40% open rate, $5K revenue | CEO | These prove product-market fit. Everything else is noise. |

## Action Items — Sprint 1 (March 18-24)
| Item | Owner | Status | Due |
|------|-------|--------|-----|
| Set up Beehiiv account (free tier) | CMO | **pending** | 2026-03-18 EOD |
| Connect Beehiiv signup form to landing page | CMO | **pending** | 2026-03-18 EOD |
| Deploy landing page to production (Vercel/Netlify) | CTO | **pending** | 2026-03-18 EOD |
| Write ToS + Privacy Policy (use Claude + templates) | Legal | **pending** | 2026-03-18 EOD |
| Add legal pages to landing site | Legal | **pending** | 2026-03-18 EOD |
| Test full newsletter flow (generate → Beehiiv import) | CTO | **pending** | 2026-03-18 EOD |
| Draft launch announcement (LinkedIn, email) | CMO | **pending** | 2026-03-19 |
| Identify 50 GovCon BD professionals to target | Sales | **pending** | 2026-03-19 |
| Write 3 LinkedIn posts (teaser content) | CMO | **pending** | 2026-03-19 |
| Send personalized LinkedIn DMs (Wave 1: 25 leads) | Sales | **pending** | 2026-03-20 |
| Post first LinkedIn teaser | CMO | **pending** | 2026-03-20 |
| Email 10 warm contacts with early access link | Sales | **pending** | 2026-03-20 |
| Send personalized LinkedIn DMs (Wave 2: 25 leads) | Sales | **pending** | 2026-03-21 |
| Post second LinkedIn teaser | CMO | **pending** | 2026-03-21 |
| Generate Week 2 newsletter (test automation) | CTO | **pending** | 2026-03-22 |
| Set up automated welcome email sequence | CMO | **pending** | 2026-03-23 |
| **Send first official newsletter to live subscribers** | CEO | **pending** | 2026-03-24 |
| Monitor open rates + click-through rates | CMO | **pending** | 2026-03-24 |

## Action Items — Q1 Strategic (April-June)
| Item | Owner | Status | Due |
|------|-------|--------|-----|
| Finalize pricing model (Free/Pro/Enterprise) | CFO | pending | 2026-04-15 |
| 10 pre-sales conversations with potential Pro/Enterprise buyers | Sales | pending | 2026-04-30 |
| Set up Stripe for paid tier subscriptions | CFO | pending | 2026-04-30 |
| Automate newsletter generation to <2 hours/week | CTO | pending | 2026-06-18 |
| Integrate 2 new data sources (SAM.gov, FPDS) | CTO | pending | 2026-06-18 |
| Publish 10 SEO blog posts on landing site | CMO | pending | 2026-06-18 |
| Close first enterprise pilot contract ($2.5K-5K) | Sales | pending | 2026-06-18 |

## Context & Assets
- **Strategy docs**: `strategy/sprint-1-plan.md`, `strategy/okrs-q1.md`, `strategy/department-directives.md`
- **Landing page**: `landing/index.html` (needs deployment to Vercel/Netlify)
- **Data pipeline**: `pipeline.py` (working, tested)
- **Insights engine**: `generate_insights.py` (working, tested)
- **HTML generator**: `report_to_html.py` (working, tested)
- **Pipeline runner**: `generate.sh` (working, end-to-end automation)
- **Data**: `data/govcon_awards_2026-03-18.json` (~500 awards)
- **Output**: `output/insights_2026-03-18.md`, `output/report_2026-03-18.html` (confirmed working)
- **USAspending API**: Free, no key needed (https://api.usaspending.gov/)
- **SAM.gov API**: Free key available (https://open.gsa.gov/api/entity-api/) — for Q2
- **Beehiiv**: Newsletter platform (https://www.beehiiv.com/) — free tier 0-2,500 subscribers
