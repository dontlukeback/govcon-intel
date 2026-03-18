# GovCon Intel Newsletter: Data Sources Analysis

**Date:** March 18, 2026
**Purpose:** Catalog every free/cheap data source that can feed unique intelligence into a weekly newsletter for small-to-mid contractors ($2M-$25M revenue).

**Guiding Principle:** A BD manager at a $5M 8(a) firm can already search SAM.gov. Our value comes from CROSS-REFERENCING, TREND-SPOTTING, and ALERTING on things they would never find by browsing one source at a time.

---

## 1. CONTRACT & SPENDING DATA

### 1A. USAspending.gov
- **What it is:** The authoritative source for all federal spending data. Covers contracts, grants, loans, direct payments, and other financial assistance.
- **Data available:** Award-level detail including: awarding agency, recipient (name, UEI, location), NAICS codes, PSC codes, award amounts (obligated + outlayed), place of performance, set-aside type, competition type, contract type (FFP, T&M, CPFF), period of performance, funding agency vs. awarding agency, congressional district.
- **API:** Yes — robust REST API at `api.usaspending.gov`. V2 endpoints, NO authentication required, no published rate limits. Endpoints cover: individual awards, spending by agency/category/geography, recipient profiles, subawards, federal accounts, IDV (IDIQ) contracts.
- **Bulk downloads:** Monthly and annual archives in CSV/TSV. Custom award data downloads with filters by agency, date range, award type, location.
- **Update frequency:** Monthly (typically 2-3 week lag from obligation date).
- **Cost:** Free.

**UNIQUE INSIGHTS WE CAN DERIVE:**
1. **Agency spending velocity tracker** — Which agencies are burning through budget faster than usual? Signals year-end spending surges or new program ramps.
2. **Competitor award tracker** — "Company X just won $2.3M from Army INSCOM for cybersecurity — they've won 4 awards from this office in 18 months." Small firms don't track competitors systematically.
3. **NAICS/PSC trend analysis** — Which service categories are growing 20%+ YoY? Which are declining? "IT modernization spend at DHS is up 34% YoY — here's who's winning it."
4. **Set-aside utilization gaps** — Which agencies are UNDER their small business goals in specific NAICS codes? That's where the next set-aside opportunity lives.
5. **Geographic opportunity heat maps** — Where is federal spending concentrating? New facility construction = new service contracts downstream.
6. **"Who's losing share" alerts** — Incumbent contractors whose recompete awards are shrinking or going to new entrants.

---

### 1B. FPDS (Federal Procurement Data System) / SAM.gov Contract Data
- **What it is:** The source system for contract award data (feeds into USAspending). Now integrated into SAM.gov after FPDS.gov redirected.
- **Data available:** More granular than USAspending for contracts specifically: modification data, reason for modification, extent competed, number of offers received, fair opportunity details, commercial item determination, consolidated/bundled flags, GFE/GFP, place of manufacture.
- **API:** The old FPDS ATOM feed was the gold standard for real-time contract data. Now accessible through SAM.gov's DataBank and APIs via open.gsa.gov. The ATOM feed may still work at `https://www.fpds.gov/efsearch/LATEST?q=` but the domain redirects.
- **Update frequency:** Near real-time (within days of award action).
- **Cost:** Free.

**UNIQUE INSIGHTS:**
1. **Number of offers received** — If an agency consistently gets 1-2 offers on a NAICS code, that's a thin market = easier entry.
2. **Modification patterns** — Contracts with frequent mods/cost growth signal agencies that underscope work = opportunity for support contracts.
3. **Sole-source-to-competed pipeline** — Track J&A (justification & approval) sole-source awards. Many transition to competed recompetes — early warning system.
4. **Commercial item trends** — FAR Part 12 usage signals agencies willing to buy COTS vs. custom = different BD approach.

---

### 1C. SAM.gov Opportunities
- **What it is:** The official source for all federal solicitations, presolicitations, sources sought, and award notices.
- **Data available:** Solicitation number, title, description, NAICS code, set-aside type, response deadline, place of performance, contracting office, points of contact, attached documents.
- **API:** Yes — Contract Opportunities API via `api.sam.gov`. Requires API key (free, register at SAM.gov). Supports keyword search, notice type, date range, organization, solicitation number filters.
- **Update frequency:** Real-time (as posted by contracting officers).
- **Cost:** Free.

**UNIQUE INSIGHTS:**
1. **Pre-solicitation to solicitation conversion tracker** — "This sources-sought from 6 months ago just became an RFP — here are the likely competitors based on who responded."
2. **Contracting office pattern analysis** — "Fort Meade Contracting Command posts 3x more IT services RFPs in Q4 than any other quarter."
3. **Set-aside type shifts** — Track when agencies change from full-and-open to small business set-aside (or vice versa) on recompetes.
4. **Response deadline clustering** — "14 cybersecurity RFPs due in the next 30 days across DoD — here's which ones match YOUR capabilities."
5. **Keyword trend alerts** — Emerging terms in solicitations (e.g., "zero trust," "AI/ML," "CMMC Level 2") signal where agencies are heading.

---

### 1D. SAM.gov Entity Registration Data
- **What it is:** Registry of all entities (companies, nonprofits, individuals) registered to do business with the federal government.
- **Data available (public):** Legal business name, UEI, CAGE code, physical/mailing address, business types (small, WOSB, SDVOSB, HUBZone, 8(a)), NAICS codes, PSC codes, registration status, activation/expiration dates, socioeconomic certifications, congressional district.
- **API:** Entity Management API via `api.sam.gov`. Requires API key. Rate limits: 10 requests/day for basic public accounts, 1,000/day with a role. System accounts get 1,000-10,000/day.
- **Bulk extracts:** Monthly full extract + daily deltas. Public extracts are free. Format: CSV/ZIP. Naming: `SAM_PUBLIC_MONTHLY_V2_YYYYMMDD.ZIP`.
- **Update frequency:** Daily (entities update registrations continuously; bulk extracts monthly + daily deltas).
- **Cost:** Free.

**UNIQUE INSIGHTS:**
1. **New registrations by NAICS** — "47 new cybersecurity firms registered in SAM.gov this month — the market is getting more crowded in 541512."
2. **Expiring registrations** — Firms whose registrations lapse may be exiting the market = less competition on recompetes.
3. **Certification tracker** — Track new 8(a), HUBZone, SDVOSB certifications. New certees are potential teaming partners or competitors.
4. **Market density analysis** — How many registered firms per NAICS per state? Thin markets = teaming opportunity.
5. **Registration surge alerts** — Spikes in registrations in a specific NAICS code after a large solicitation posts = competitive intelligence.

---

### 1E. Federal Subaward Data (FSRS, now SAM.gov)
- **What it is:** Subaward reporting for prime contracts and grants over $30K. Migrated from FSRS.gov to SAM.gov in March 2025.
- **Data available:** Prime award details, subawardee name/UEI/address, subaward amount, place of performance, NAICS code, executive compensation for top 5 officers.
- **API:** Public subaward API and public subcontract API via SAM.gov.
- **Update frequency:** As reported by primes (required within 30 days of subaward).
- **Cost:** Free.

**UNIQUE INSIGHTS:**
1. **Prime-sub relationship mapping** — "Booz Allen consistently subs cybersecurity work to these 5 small firms on DHS contracts." A BD manager can't see this without digging through FSRS.
2. **Subcontracting plan compliance** — Which primes are meeting their small business subcontracting goals? Those falling short are actively seeking small business subs.
3. **"Hidden" revenue pools** — Sub opportunities don't appear on SAM.gov as solicitations. This data reveals the real subcontracting market.
4. **Teaming partner identification** — Find firms who already sub in your NAICS to the agencies you target.

---

## 2. BUDGET & APPROPRIATIONS

### 2A. OMB Budget Documents
- **What it is:** The President's annual budget request, including agency-level detail and historical tables.
- **Data available:** Agency budget requests by account, program, and function. Historical tables going back decades. Agency budget justification documents (the "J-books") contain line-item detail on every program, including contract spend.
- **Machine-readable:** Historical tables are in Excel/CSV. Budget appendix is in PDF. Prior years archived at GovInfo.gov.
- **Update frequency:** Annual (February budget request) + Mid-Session Review (July).
- **Cost:** Free.

**UNIQUE INSIGHTS:**
1. **Agency J-book mining** — J-books contain specific contract line items and program funding levels. "The Army's PEO for Enterprise Information Systems is requesting $340M for cloud migration in FY27 — up 28% from FY26." This is where opportunities are born 12-18 months before RFPs drop.
2. **Budget trend lines** — 3-year funding trajectories by agency/program. Growing programs = bid targets. Declining programs = exit signals.
3. **New program starts** — New line items in the budget = greenfield opportunities with no incumbents.
4. **Unfunded requirements lists** (published by military services to Congress) — Programs the services want but didn't make the President's budget. Congress often adds these back.

---

### 2B. GovInfo.gov Bulk Data
- **What it is:** GPO's bulk data repository for government publications.
- **Data available (relevant to GovCon):** Federal Register (rules, proposed rules, notices), Congressional Bills (including appropriations/authorization bills), Code of Federal Regulations, Bill Status.
- **Format:** XML bulk data.
- **API:** GovInfo has a basic API for document retrieval.
- **Update frequency:** Daily for Federal Register; varies for other collections.
- **Cost:** Free.

**UNIQUE INSIGHTS:**
1. **Appropriations bill tracker** — Parse appropriations bills to extract agency funding levels before they become law. Early signal for which programs get boosted or cut.
2. **Authorization act tracker** — Defense authorization bills often contain acquisition reform provisions, new program mandates, and small business provisions.

---

## 3. WORKFORCE & ORGANIZATION

### 3A. OPM Federal Workforce Data (data.opm.gov)
- **What it is:** The official source for federal civilian workforce data. Formerly FedScope, now at data.opm.gov.
- **Current stats:** 2,035,344 federal civilian employees. 86.8% work outside DC. 27.9% are veterans.
- **Data available:** Three record-level CSV datasets updated monthly:
  - **Federal Employment** — Monthly snapshot of all active employees (2M+ rows)
  - **Federal Accessions** — New hires, transfers in
  - **Federal Separations** — Resignations, retirements, terminations
- **Dimensions:** Agency, occupation series, grade, location, demographics, appointment type.
- **Interactive dashboards:** Workforce size, changes, compensation, recruitment, demographics, location.
- **Update frequency:** Monthly (published ~1 month after data date; e.g., Jan 2026 data published March 4, 2026).
- **Cost:** Free.

**UNIQUE INSIGHTS:**
1. **Agency staffing surge/decline alerts** — "CISA added 340 cybersecurity positions in Q1 — that means more contract oversight capacity AND likely more cyber service contracts." Conversely, agencies losing staff often backfill with contractors.
2. **Retirement wave tracker** — Senior GS-14/15 retirements in acquisition roles = new contracting officers = relationship-building opportunity.
3. **DOGE/RIF impact tracker** — Track which agencies are losing headcount fastest. Headcount reductions often INCREASE contractor spend (agencies still need the work done).
4. **Occupation gap analysis** — If an agency has 50% vacancy in IT specialists, they're likely contracting that capability out. Cross-reference with contract awards to validate.

---

### 3B. DOGE (Department of Government Efficiency) Tracker
- **What it is:** The government efficiency initiative publishing data on spending cuts, contract cancellations, and workforce reductions.
- **Data available:** Claimed savings, terminated contracts, RIF notices, agency-specific cuts.
- **Access:** doge.gov (returned 403 when fetched — may require direct browser access). News coverage provides secondary data.
- **Update frequency:** Ad hoc.
- **Cost:** Free (if accessible).

**UNIQUE INSIGHTS:**
1. **Contract cancellation tracker** — Which contracts are being terminated? Terminated service contracts may be re-awarded under different vehicles, smaller scope, or to different firms.
2. **Agency disruption map** — Agencies with the most DOGE activity are in flux. Flux = opportunity for firms that can move fast.
3. **"What's still funded" analysis** — Cross-reference DOGE cuts with USAspending to identify programs that survived = durable opportunities.
4. **Recompete impact** — If DOGE cancels a $50M IT contract, does that work disappear or get redistributed to smaller contracts/task orders?

---

## 4. LEGAL & PROTESTS

### 4A. GAO Bid Protest Decisions
- **What it is:** GAO publishes all bid protest decisions — when contractors challenge an award, the result tells you about the agency's procurement environment.
- **Data available:** Protester name, agency, solicitation number, decision (sustained/denied/dismissed), grounds for protest, decision reasoning.
- **API/Feed:** The GAO search page returned 403, but decisions are published on gao.gov and are scrapeable. No official API found.
- **Update frequency:** Decisions published within days of issuance.
- **Cost:** Free.

**UNIQUE INSIGHTS:**
1. **Sustained protest alerts** — "GAO sustained a protest on this $20M Army IT contract — the award is vacated, rebid incoming." Immediate competitive opportunity.
2. **Agency procurement quality scorecard** — Which agencies get protested most? Which get sustained most? Poor procurement shops = more risk but also more second chances.
3. **Protester pattern analysis** — Some firms protest everything. Know who they are before you compete against them.
4. **Grounds for protest trends** — If "unequal access to information" protests are up, agencies are tightening debriefs. Adjust your debrief strategy.

---

### 4B. Court of Federal Claims / PACER
- **What it is:** The COFC handles larger contract disputes, post-award protests (alternative to GAO), and Contract Disputes Act cases.
- **Data available:** Case filings, rulings, injunctions on contract awards.
- **Access:** PACER system ($0.10/page, capped at $3/document). CourtListener.com provides free access to many opinions.
- **Update frequency:** As cases are decided.
- **Cost:** PACER has per-page fees; CourtListener is free for published opinions.

**UNIQUE INSIGHTS:**
1. **Injunction tracker** — COFC can enjoin (stop) contract performance. When a $100M contract is enjoined, that work stops and the agency scrambles.
2. **Claims data** — Contract Disputes Act claims reveal which contracts are troubled. Troubled incumbent contracts = recompete opportunities.

---

## 5. REGULATORY & POLICY

### 5A. Federal Register API
- **What it is:** The daily journal of the US government — every proposed rule, final rule, notice, and executive order.
- **API:** `federalregister.gov/api/v1/` — free, no authentication needed. The main site had a redirect/block but the API itself is well-documented.
  - Endpoints: `/documents`, `/documents/{id}`, `/public-inspection-documents`
  - Query parameters: keyword, agency, type (rule/proposed_rule/notice/presidential_document), date range, CFR part
  - Response: JSON with full text, metadata, PDF links
- **Update frequency:** Daily.
- **Cost:** Free.

**UNIQUE INSIGHTS:**
1. **Acquisition rule change alerts** — "FAR Case 2025-007 just changed wage thresholds in 10 sections. Here's what it means for your cost proposals." Small firms don't read the Federal Register.
2. **Proposed rule comment tracker** — When FAR changes are proposed, the comment period is where industry can influence outcomes. Alert subscribers to comment.
3. **Agency-specific notice mining** — Agencies post Sources Sought, Notices of Intent, and other pre-solicitation signals in the Federal Register that don't always appear on SAM.gov.
4. **Executive order tracker** — EOs on procurement reform, cybersecurity requirements, Buy American, etc. directly affect contract requirements.

---

### 5B. FAR/DFARS Change Tracking (acquisition.gov)
- **What it is:** The Federal Acquisition Regulation site with change tracking.
- **Data available:** Full FAR text (53 parts), current FAC number (FAC 2026-01, effective 3/13/2026), "List of Sections Affected" with case numbers and descriptions.
- **Formats:** HTML, PDF, Word, DITA, EPUB, Kindle, Apple Books.
- **Change notifications:** "Sign up for FAR News" subscription available.
- **Update frequency:** As Federal Acquisition Circulars are issued (roughly quarterly).
- **Cost:** Free.

**UNIQUE INSIGHTS:**
1. **Plain-English FAR change summaries** — "FAR just raised the SCA wage threshold to $105,767. If your contracts have SCA-covered positions, update your pricing." Most BD managers don't read FAR updates.
2. **DFARS change tracker** — Defense-specific regulation changes affect half the contracting market.
3. **Compliance alert system** — New clauses flowing down to subcontractors = required action for small firms.

---

### 5C. CMMC (Cybersecurity Maturity Model Certification)
- **What it is:** DoD's cybersecurity certification requirement for contractors handling CUI.
- **Data available:** No public registry of certified firms yet. The CMMC Marketplace (cyberab.org) lists Registered Practitioners and C3PAOs (assessors).
- **Update frequency:** Evolving — CMMC 2.0 final rule was published in late 2024; phased implementation ongoing.
- **Cost:** Free to monitor.

**UNIQUE INSIGHTS:**
1. **CMMC readiness tracker** — As more RFPs require CMMC Level 2, firms that certify early gain competitive advantage. Track which solicitations now require CMMC.
2. **C3PAO availability** — The assessor pipeline is bottlenecked. Alerting firms on assessor availability is directly valuable.
3. **"CMMC required" solicitation counter** — How many active RFPs require CMMC? Trend line is the signal for urgency.

---

## 6. INTELLIGENCE ENRICHMENT SOURCES

### 6A. SBA Small Business Procurement Scorecard
- **What it is:** Annual agency-by-agency report card on small business contracting goal achievement.
- **Data available:** Agency grades (A+ to F) across 5 categories: SB, WOSB, SDB, SDVOSB, HUBZone. Includes prime contracting (50% weight), subcontracting (20%), small business contractor growth (10%), and OSDBU compliance (20%). Historical data from 2007-2020+.
- **Update frequency:** Annual.
- **Cost:** Free.

**UNIQUE INSIGHTS:**
1. **Underperforming agency alerts** — "VA got a D in HUBZone contracting last year. They need to award more HUBZone contracts to improve their score — if you're HUBZone certified, target VA."
2. **Year-over-year trend** — An agency that dropped from B to D is under pressure from SBA. That pressure creates set-aside opportunities.
3. **Category gap targeting** — If WOSB goals are missed government-wide, WOSB-certified firms have leverage.
4. **Subcontracting achievement tracking** — Primes at agencies with low subcontracting scores need more small business subs.

---

### 6B. SBIR/STTR Awards Database (sbir.gov)
- **What it is:** Database of all Small Business Innovation Research and Small Business Technology Transfer awards.
- **Data available:** Firm name, award title, agency, phase (I/II/III), program, contract number, award amount, company location, PI details, research keywords, abstracts.
- **API:** REST API at `api.www.sbir.gov/public/api/`. Endpoints: awards, companies, solicitations. Pagination (100/page), JSON or XML output. **Note: API was under maintenance as of research date — may be intermittent.**
- **Query parameters:** Agency, company, year, research institution.
- **Participating agencies:** DOD, HHS, NASA, NSF, DOE, USDA, EPA, DOC, ED, DOT, DHS.
- **Update frequency:** As awards are made.
- **Cost:** Free.

**UNIQUE INSIGHTS:**
1. **Phase II to Phase III pipeline** — Phase II SBIR winners often need teaming partners for Phase III (full production/deployment). Small firms can position as subs.
2. **Technology trend tracker** — SBIR topics reveal what agencies want to buy in 2-3 years. "DoD issued 14 SBIR topics on quantum computing this year vs. 3 last year."
3. **Competitor technology mapping** — Know which companies are developing capabilities funded by SBIR that will compete with (or complement) your offerings.
4. **Agency innovation priorities** — Aggregate SBIR topics by agency to see R&D direction.

---

### 6C. CPARS (Contractor Performance Assessment Reporting System)
- **What it is:** The government's system for evaluating contractor past performance.
- **Data available:** Performance ratings on contracts (quality, schedule, cost control, management, small business subcontracting). Ratings: Exceptional, Very Good, Satisfactory, Marginal, Unsatisfactory.
- **Public access:** **NONE.** CPARS data is restricted to government evaluators and the rated contractor. NOT publicly available. Past performance is accessed through SAM.gov's Responsibility/Qualification section, but only by federal users.
- **Cost:** N/A (not accessible to the public).

**NEWSLETTER ANGLE (indirect):**
1. **Proxy performance signals** — Cross-reference contract modifications (scope reductions, early terminations) with specific contractors to infer performance issues.
2. **Award protest decisions** — GAO decisions sometimes reference past performance evaluations in their reasoning.
3. **Recompete outcome analysis** — If an incumbent loses a recompete, their performance was likely problematic. Track incumbent displacement rates by agency.

---

### 6D. GSA Schedule Pricing Data (GSA eLibrary / GSA Advantage)
- **What it is:** Pricing data for contractors on GSA Multiple Award Schedules.
- **Data available:** Contractor name, contract number, SIN (Special Item Number), labor categories, labor rates, product pricing, contract terms.
- **Access:** GSA eLibrary (gsaelibrary.gsa.gov) for contractor/SIN lookup. GSA Advantage (gsaadvantage.gov) for product/service pricing. The eLibrary site didn't return content but the data is publicly browsable.
- **Bulk data:** GSA publishes schedule pricing in CSV/Excel format.
- **Update frequency:** As contractors update their price lists (at least annually).
- **Cost:** Free.

**UNIQUE INSIGHTS:**
1. **Competitor pricing intelligence** — See exactly what competitors charge for similar labor categories on GSA Schedule. "Your competitor charges $145/hr for a Senior Systems Engineer on Schedule 70. You're at $152/hr."
2. **Rate trend analysis** — Are rates in your SIN category going up or down? Informs your pricing strategy.
3. **New schedule holders** — Track who just got on Schedule. New competitors or potential teaming partners.
4. **Labor category benchmarking** — What's the going rate for a CISSP-certified security analyst across all schedule holders?

---

## 7. ALTERNATIVE & NOVEL SOURCES

### 7A. SEC EDGAR (10-K/10-Q Filings)
- **What it is:** Public company financial filings. Large GovCon primes (Leidos, SAIC, Booz Allen, L3Harris, etc.) disclose government revenue, contract backlog, and segment performance.
- **Data available:** Government revenue by segment, contract backlog, book-to-bill ratios, major program wins/losses, risk factors mentioning specific agencies, management discussion of pipeline.
- **API:** EDGAR XBRL API + full-text search (EFTS). The full-text search returned 403 in testing but is generally available at `efts.sec.gov/LATEST/search-index`.
- **Update frequency:** Quarterly (10-Q) and annually (10-K).
- **Cost:** Free.

**UNIQUE INSIGHTS:**
1. **Prime contractor health signals** — "Leidos reported a book-to-bill of 0.8x in their Defense segment — they're winning less than they're delivering. Watch for recompetes they might not bid."
2. **Backlog drawdown alerts** — When a prime's backlog shrinks, they're hungrier for new wins = more aggressive pricing = tougher competition.
3. **Segment revenue shifts** — If a prime's civilian agency revenue is growing but defense is flat, they're repositioning. Affects competitive dynamics.
4. **Risk factor mining** — 10-K risk factors mention specific contracts under protest, potential terminations, and regulatory risks. Early warning system.
5. **M&A signal detection** — "SAIC's 10-K mentions evaluating strategic acquisitions in the $50-200M cybersecurity space" = watch for capability acquisitions that change competitive landscape.

---

### 7B. LinkedIn / Job Posting Signals
- **What it is:** Hiring activity by federal contractors reveals their pipeline and win expectations.
- **Data available:** Job postings (titles, clearance requirements, location, skills), company growth rates, employee count changes.
- **Access:** LinkedIn API is restricted (requires partnership). However, job boards (Indeed, ClearanceJobs, LinkedIn Jobs) can be monitored via scraping or RSS.
- **Cost:** Free to monitor manually; scraping requires engineering.

**UNIQUE INSIGHTS:**
1. **Pre-award hiring signals** — "Company X just posted 30 positions requiring TS/SCI clearance in Tampa — they likely expect to win the CENTCOM J6 recompete."
2. **Clearance demand tracker** — Aggregate clearance-required postings by type and location. Rising demand = rising labor costs = adjust proposals.
3. **Skill gap identification** — If everyone's hiring for "Kubernetes engineers with Secret clearance," that's the hot skill and the scarce resource.
4. **Incumbent staffing** — If the incumbent on your target contract is NOT hiring for positions, they may not be bidding the recompete.

---

### 7C. FOIA Requests
- **What it is:** Freedom of Information Act requests can obtain contract documents, performance work statements, proposal evaluations (redacted), and pricing volumes.
- **Data available:** SOWs/PWSs from awarded contracts, technical evaluation criteria, pricing structures, contract modifications, correspondence.
- **Access:** File FOIA requests with individual agencies. Many agencies have FOIA reading rooms with previously released documents.
- **Turnaround:** 20 business days (legally) but often 3-12 months in practice.
- **Cost:** Free to file; some agencies charge reproduction costs for large requests.

**UNIQUE INSIGHTS:**
1. **Evaluation criteria intelligence** — FOIA the source selection decision document on a contract you lost. See exactly how you scored vs. the winner.
2. **Pricing intelligence** — FOIA competitor pricing volumes (heavily redacted but sometimes revealing).
3. **PWS/SOW library** — Build a library of performance work statements for contracts you want to bid. Understand the agency's language and expectations.
4. **Proactive FOIA reading rooms** — Agencies publish frequently-requested documents. Check FOIA logs to see what competitors are requesting.

---

### 7D. GovCon Conference Calendar
- **What it is:** Industry days, pre-solicitation conferences, and networking events are critical BD touchpoints.
- **Data available:** Event dates, agencies participating, topics, registration info.
- **Sources:** SAM.gov (industry day notices), agency websites, AFCEA, NDIA, PSC (Professional Services Council), ACT-IAC, NCMA events.
- **Cost:** Free to track; event attendance $200-2,000+.

**UNIQUE INSIGHTS:**
1. **Industry day tracker** — Automated alerts for industry days in your NAICS codes. "Army G-6 is holding an industry day for their $500M network modernization program next month."
2. **Agency event calendar** — Consolidated calendar of agency outreach events, OSDBU matchmaking sessions, and mentor-protege events.
3. **Networking ROI** — Which conferences have the highest concentration of contracting officers from your target agencies?

---

## 8. AGGREGATION STRATEGY: WHERE THE REAL VALUE LIVES

The magic isn't in any single source — it's in CROSS-REFERENCING them. Here's how:

### Tier 1: Automated Weekly Pipeline (build these first)
| Source | API? | Refresh | Pipeline Complexity |
|--------|------|---------|-------------------|
| USAspending API | Yes, no auth | Monthly | Low — pull award data by NAICS/agency |
| SAM.gov Opportunities API | Yes, free key | Real-time | Low — keyword alerts |
| Federal Register API | Yes, no auth | Daily | Low — filter by acquisition-related agencies |
| SAM.gov Entity Extracts | Yes, free key | Monthly + daily | Medium — parse bulk CSV |
| SBIR API | Yes, no auth | As awarded | Low — filter by agency/topic |
| OPM Workforce Data | CSV download | Monthly | Medium — parse 2M+ row CSVs |

### Tier 2: Semi-Automated (scrape + manual enrichment)
| Source | Method | Refresh | Notes |
|--------|--------|---------|-------|
| GAO Bid Protests | Scrape gao.gov | Weekly | No API; parse HTML |
| FAR/DFARS Changes | Subscribe + scrape | Quarterly | FAR News subscription + acquisition.gov |
| SEC EDGAR 10-Ks | EDGAR API | Quarterly | Focus on top 20 GovCon primes |
| SBA Scorecards | Manual download | Annual | Small dataset, high value |
| GSA Schedule Pricing | eLibrary/Advantage | Varies | Competitor pricing goldmine |

### Tier 3: Manual but High-Value
| Source | Method | Frequency | Notes |
|--------|--------|-----------|-------|
| Agency J-books | PDF download/parse | Annual (Feb) | NLP/LLM to extract line items |
| FOIA reading rooms | Manual browse | Monthly | Build PWS library over time |
| Job posting signals | Monitor boards | Weekly | ClearanceJobs, Indeed |
| DOGE tracker | News + doge.gov | Ad hoc | Secondary source analysis |
| Subaward data (FSRS) | SAM.gov API | As reported | Map prime-sub relationships |

---

## 9. COMPETITIVE MOAT ANALYSIS

### What existing platforms charge for (and how we replicate for free)

| Enterprise Feature | Their Price | Our Free Alternative | Gap |
|---|---|---|---|
| Opportunity alerts | $1,350-8,000/yr (GovTribe, GovWin) | SAM.gov API + our curation | We add context they don't |
| Award tracking | $4,000+/yr (GovWin) | USAspending API | 2-3 week lag vs. near real-time |
| Competitor intelligence | $5,000+/yr (BGOV) | USAspending + Entity API + FSRS | No CRM integration |
| Budget/pipeline forecasting | $8,000+/yr (GovWin) | J-books + appropriations tracking | More labor-intensive |
| Market sizing by NAICS | $4,000+/yr (GovTribe Growth) | USAspending bulk data | Requires our own analysis |
| Bid protest monitoring | Included in enterprise tiers | GAO scrape + COFC (CourtListener) | Need to build scraper |

### Our unique advantages (things NO platform does well):
1. **Cross-source synthesis** — Connecting budget signals to opportunities to awards to workforce data. No platform does this end-to-end.
2. **Plain-English translation** — FAR changes, budget documents, and protest decisions written for a BD manager, not a lawyer.
3. **Small business focus** — Enterprise tools optimize for $100M+ primes. We optimize for $2-25M firms.
4. **DOGE/policy disruption tracking** — New territory. No established product covers this well.
5. **"So what" framing** — Every data point linked to a specific action: bid, don't bid, team up, or watch.

---

## 10. RECOMMENDED DATA PIPELINE: WEEK 1 MVP

**Minimum data sources for a useful first issue:**

1. **SAM.gov Opportunities API** — This week's notable RFPs in 5 target NAICS codes
2. **USAspending API** — Notable awards this month (who won what)
3. **Federal Register API** — Any acquisition-related proposed rules or final rules
4. **GAO Bid Protests** — Any sustained protests (manual scan of gao.gov)
5. **One "deep dive" insight** — e.g., J-book analysis of one agency, or SBA scorecard gap analysis

This gives you a newsletter with: opportunities, competitive intel, regulatory updates, legal alerts, and strategic analysis — all from free sources, all stuff a BD manager can't efficiently assemble themselves.

---

## APPENDIX: API Quick Reference

```
# USAspending — no auth required
curl "https://api.usaspending.gov/api/v2/search/spending_by_award/" \
  -X POST -H "Content-Type: application/json" \
  -d '{"filters":{"award_type_codes":["A","B","C","D"],"time_period":[{"start_date":"2026-01-01","end_date":"2026-03-18"}]},"fields":["Award ID","Recipient Name","Award Amount"],"limit":10}'

# SAM.gov Opportunities — requires API key
curl "https://api.sam.gov/prod/opportunity/v2/search?api_key=YOUR_KEY&keyword=cybersecurity&postedFrom=01/01/2026&postedTo=03/18/2026"

# Federal Register — no auth required
curl "https://www.federalregister.gov/api/v1/documents.json?conditions[term]=acquisition&conditions[type][]=RULE&conditions[type][]=PRORULE"

# SAM.gov Entity Management — requires API key
curl "https://api.sam.gov/entity-information/v3/entities?api_key=YOUR_KEY&naicsCode=541512&registrationStatus=A"

# SBIR Awards — no auth required (may be under maintenance)
curl "https://api.www.sbir.gov/public/api/awards?agency=DOD&rows=10"
```

---

*Last updated: March 18, 2026*
