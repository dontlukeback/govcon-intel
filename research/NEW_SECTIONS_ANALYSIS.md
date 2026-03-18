# New Section Concepts: Feasibility Analysis

**Date:** March 18, 2026
**Purpose:** Evaluate 15 new newsletter section concepts for data feasibility, reader value, production effort, competitive uniqueness, and recommended pricing tier.

---

## Executive Summary

Of 15 concepts evaluated, **7 are high-priority additions** that can be built primarily from public data (USAspending API, SAM.gov, SBA scorecards, GAO decisions) with manageable weekly effort. Three are "moat builders" that no competitor offers at any price. Five are medium-priority additions worth phasing in over 90 days. Three are aspirational -- high value but high effort or limited data access.

**Top 5 by impact (add these first):**
1. "Is It Wired?" Scorecard -- highest-demand feature per Reddit; automatable from USAspending
2. "The Bridge Watch" -- proven feasible via API keyword search; signals imminent recompetes
3. "The Set-Aside Spotlight" -- SBA scorecard data is public; agencies behind on goals = opportunity
4. "The Protest Report" -- GAO decisions are public; no one curates weekly for this audience
5. "GWAC/IDIQ Vehicle Tracker" -- IDV data in USAspending; task order velocity is a leading indicator

---

## Concept 1: "Is It Wired?" Scorecard

### What It Is
A scoring system that evaluates whether an upcoming recompete or solicitation shows signals of being pre-determined for the incumbent. Each opportunity gets a 0-100 "Wired Score" based on measurable indicators like sole-source history, number of offers on prior awards, incumbent tenure, requirement specificity, and competition history. Helps readers make faster bid/no-bid decisions.

### Data Source Feasibility
**HIGH -- almost entirely automatable from public data.**

The USAspending award detail API returns exactly the fields needed:
- `extent_competed` -- values like "C" (NOT COMPETED), "A" (FULL AND OPEN), "CDO" (COMPETITIVE DELIVERY ORDER)
- `number_of_offers_received` -- consistently 1 for wired contracts
- `solicitation_procedures` -- "SSS" (ONLY ONE SOURCE) is the smoking gun
- `other_than_full_and_open` -- e.g., "ONLY ONE SOURCE-OTHER (FAR 6.302-1 OTHER)"
- `type_set_aside` -- NONE on historically sole-sourced work
- Description field -- often contains "sole source", "follow-on", "bridge" language

**Scoring algorithm inputs (all from USAspending):**
| Signal | Weight | Source |
|--------|--------|--------|
| Prior award was sole-source/not competed | 25pts | `extent_competed` on predecessor |
| Only 1 offer received on prior award | 15pts | `number_of_offers_received` |
| Incumbent has held contract 10+ years | 20pts | `date_signed` history |
| Highly specific/narrow requirements in description | 10pts | NLP on description text |
| Same recipient won last 2+ iterations | 15pts | Recipient history lookup |
| Set-aside restricts competition pool | 10pts | `type_set_aside` |
| Short response deadline (<15 days) | 5pts | SAM.gov opportunity data |

**Confirmed via API test:** A bridge contract for Department of State showed `extent_competed: C`, `number_of_offers_received: 1`, `solicitation_procedures: SSS`, `other_than_full_and_open: ONLY ONE SOURCE`. All fields populated and parseable.

### Value to Reader
This is the #1 most-requested intelligence per Reddit analysis. The post "The signals that a contract is wired for the incumbent" scored 62 upvotes, and "Stop Writing Proposals You Were Never Going to Win" scored 76. A single bad proposal costs $10-50K. Preventing even one wasted pursuit per year justifies the subscription 20x over.

**Decision enabled:** Bid/no-bid. "Should I spend $30K on this proposal or walk away?"

### Effort to Produce
**MEDIUM.** Initial algorithm build is a one-time 2-3 day effort. Weekly production is ~2 hours: run scoring against that week's recompete alerts, manually review edge cases, write 2-3 sentence commentary on highest-scoring items.

### Uniqueness
**Nobody offers this at any price.** GovWin IQ has "competitive landscape" data but no automated wired-signal scoring. FedScout has "P-Win" calculations but they require manual input. This would be a genuine first-in-market feature.

Enterprise platforms (GovWin, BGOV) have pieces of the underlying data but none synthesize it into a simple score. The closest analog is HigherGov's "incumbent analysis" but it's a data lookup, not a predictive score.

### Recommended Tier
**Free tier gets the score (0-100).** Pro tier gets the breakdown (which signals triggered, competitor history, historical win patterns). Insider tier gets the full "Capture Intel Pack" with recommended pursuit strategy.

This is the gateway drug. Show the score for free, gate the "why" behind Pro.

---

## Concept 2: "Dead Contract Walking" -- Termination Risk Tracker

### What It Is
A weekly tracker of contracts at elevated risk of Termination for Convenience (T4C), especially in the DOGE era. Identifies contracts by cross-referencing agency budget cuts, workforce reductions, DOGE announcements, and contract characteristics (performance period, funding status, agency health) to assign a "T4C Risk" level (Low/Medium/High/Critical).

### Data Source Feasibility
**MEDIUM -- requires blending public data with manual OSINT.**

Available from APIs:
- USAspending: active contracts by agency, obligation amounts, period of performance
- Contract descriptions mentioning "continue performance" or "stop-work"
- Agency-level spending trend data (declining obligations = risk signal)

Requires manual curation:
- DOGE website announcements (no reliable API; site blocks scraping)
- Court rulings on contract terminations (manually tracked from Pacer/legal news)
- Agency RIF announcements (press releases, Federal News Network)
- Congressional budget markup signals

**Key limitation:** DOGE does not publish structured data on targeted contracts. Their "savings" page returns 403. This section depends on manual monitoring of 5-8 sources weekly.

### Value to Reader
Extremely high in the current environment. The Reddit post "Tracking Cancelled Contracts" scored 119 upvotes -- the highest non-DOGE post in the subreddit. Contractors with at-risk positions need early warning to:
- Reduce staffing before stop-work orders hit
- Invoice for work performed before termination
- Redirect BD resources to surviving agencies
- Negotiate favorable T4C settlement terms

**Decision enabled:** "Should I keep staffing this contract or start transitioning people?"

### Effort to Produce
**HIGH.** 3-4 hours/week of manual OSINT monitoring across DOGE announcements, court filings, agency press releases, and congressional actions. Cannot be fully automated due to DOGE data opacity.

### Uniqueness
**Partially unique.** BGOV tracks DOGE actions. GovExec and Federal News Network cover terminations as news. But nobody synthesizes this into a per-contract risk assessment with actionable guidance. Our DOGE Tracker section already covers agency-level impacts; this would extend to contract-level risk scoring.

### Recommended Tier
**Pro.** The DOGE Tracker (agency-level) stays Free. Contract-level T4C risk assessment is Pro. Insider gets advance alerts when new termination signals emerge (mid-week push notifications).

---

## Concept 3: "The Teaming Board" -- Who's Looking for Partners

### What It Is
A curated marketplace/listing of companies actively seeking teaming partners for upcoming pursuits. Includes: (a) companies that need small business partners for set-aside compliance, (b) small businesses seeking primes with past performance, (c) mentor-protege pairings, and (d) JV opportunities. Sourced from SAM.gov opportunity notices, industry day attendee lists, and reader submissions.

### Data Source Feasibility
**MEDIUM-LOW -- data exists but is fragmented and hard to automate.**

Available sources:
- SAM.gov "Sources Sought" and "RFI" notices -- often explicitly ask for teaming interest
- SAM.gov "Special Notices" -- industry day announcements where teams form
- SBA mentor-protege program listings (public but static, not API-accessible)
- USAspending `subcontracting_plan` field ("C" = plan required = prime needs subs)
- Federal Compass claims 2M+ industry contacts for partner matching ($5K+/yr tier)

**Key challenge:** The most valuable teaming intelligence is private (who is pursuing what, who needs partners). Public data only shows after-the-fact teaming (subaward data) or pre-solicitation signals (Sources Sought responses are not public). The highest-value version of this section requires reader community participation -- people posting their own "looking for partners" listings.

### Value to Reader
Very high for Persona 1 (Newcomers) and Persona 2 (Small Contractors). Finding teaming partners is a top-5 pain point. But the value depends on achieving critical mass of listings.

**Decision enabled:** "Who should I team with on this pursuit?" and "Is anyone pursuing this opportunity that I could sub to?"

### Effort to Produce
**HIGH initially, then MEDIUM.** Requires building a submission system and curating listings. Once the community is active, effort shifts to moderation and matching. First 6 months will require seeding with curated opportunities where teaming is clearly needed.

### Uniqueness
**Partially differentiated.** Federal Compass has partner matching ($5K+/yr). FedScout has "Teammate Finder." Govly has collaboration features. But none offer this in a weekly newsletter format accessible at $249/yr. The newsletter format -- "This week's teaming opportunities" -- is novel.

### Recommended Tier
**Insider.** This is a community feature that justifies the premium tier. Insider subscribers can post and browse teaming opportunities. Pro subscribers see a "Top 3 Teaming Opportunities This Week" teaser.

---

## Concept 4: "Price-to-Win Intel" -- What Agencies Are Actually Paying

### What It Is
Analysis of contract pricing patterns derived from public award data. Covers: average $/hour by labor category (using NAICS + PSC + agency cross-tabulation), pricing trends over time, agency-specific pricing norms, and comparisons between contract vehicles. Not individual rate cards, but statistical intelligence on what agencies are actually paying for comparable work.

### Data Source Feasibility
**MEDIUM -- derivable but imprecise.**

Available from USAspending:
- `Award Amount` (total obligated value)
- `type_of_contract_pricing` -- values: FFP (Firm Fixed Price), T&M (Time and Materials), CR (Cost Reimbursement), etc.
- NAICS codes (industry classification)
- PSC codes (product/service classification, e.g., D302 = IT Systems Development)
- Agency, period of performance, number of employees (for some awards)

Available from GSA:
- GSA Schedule pricing is technically public (GSA Advantage) but not easily bulk-queryable
- GSA CALC (Contract-Awarded Labor Category) tool provides actual awarded labor rates

**Key limitation:** USAspending shows total contract value, not per-hour rates. For T&M contracts, you can infer rough rates by dividing total value by estimated FTEs and performance period, but this is noisy. GSA CALC is the best public source for actual labor rates but covers only GSA Schedule contracts.

**What we CAN reliably produce:**
- Average contract value by NAICS + PSC + agency combination
- Price trends (are agencies paying more or less for cybersecurity this year vs. last?)
- Pricing type distribution (is an agency shifting from FFP to T&M?)
- Vehicle-level pricing patterns (OASIS awards average $X vs. Alliant 2 at $Y)

### Value to Reader
Very high for BD professionals (Persona 3) building price-to-win models. Even rough benchmarks save thousands in consultant fees. Price-to-win analysis typically costs $15-50K from consultants like Centurion Research or Lohfeld.

**Decision enabled:** "What should we price this at to be competitive?"

### Effort to Produce
**MEDIUM.** Initial statistical model takes ~1 week to build. Weekly updates are ~1-2 hours: pull new award data, update rolling averages, flag outliers and notable pricing shifts.

### Uniqueness
**Moderately unique at this price point.** BGOV has "BGOV200" pricing data but costs $8K+/yr. GovWin has pricing intelligence at $10K+/yr. GSA CALC is free but narrow. Nobody publishes weekly pricing trend analysis in a newsletter format. We would be the only source of this intelligence under $1,000/yr.

### Recommended Tier
**Pro** for trend data and agency averages. **Insider** for detailed breakdowns by labor category, vehicle, and NAICS.

---

## Concept 5: "The Bridge Watch" -- Contracts on Life Support

### What It Is
A weekly listing of newly awarded or modified bridge contracts -- short-term sole-source extensions issued when an agency fails to complete a recompete on time. Bridge contracts are the strongest leading indicator of an imminent full-and-open competition. They also signal agency urgency and provide intelligence on the incumbent, scope, and pricing baseline.

### Data Source Feasibility
**HIGH -- proven feasible via API testing.**

Direct USAspending keyword search for "bridge contract" returns real, relevant results. Tested on March 18, 2026:
- "ACQUISITION SUPPORT SERVICES BRIDGE CONTRACT" -- MCC, $3.5M (March 2025)
- "SECURITY OFFICER BRIDGE CONTRACT" -- CFPB, $1.5M
- "TWO YEAR BRIDGE CONTRACT" -- State Dept, $23.5M

The API also returns critical context:
- `extent_competed: C` (NOT COMPETED) -- confirms bridge status
- `solicitation_procedures: SSS` (ONLY ONE SOURCE) -- confirms sole-source
- `number_of_offers_received: 1` -- incumbent only
- Full description with scope of work
- Award amount (pricing baseline for the recompete)
- Period of performance (tells you when the recompete will hit)

**Supplementary sources:**
- SAM.gov J&A (Justification & Approval) postings -- required for sole-source over $750K
- SAM.gov "Intent to Sole Source" notices -- sometimes posted before bridge award
- Agency acquisition forecasts on SAM.gov -- bridge predecessors often appear here

**Automation approach:** Weekly API query for keywords ["bridge contract", "bridge extension", "interim contract", "sole source extension", "continuation of services"] filtered to awards from the past 7 days. Enrich each with predecessor contract data and estimated recompete timeline.

### Value to Reader
Extremely high. Bridge contracts are the most actionable intelligence in GovCon:
1. **They guarantee a recompete is coming** -- the agency MUST compete the requirement
2. **They reveal the scope** -- the bridge description IS the future SOW baseline
3. **They reveal the price** -- the bridge value IS the pricing benchmark
4. **They reveal the incumbent** -- and the incumbent is vulnerable (they're on a bridge because the agency is considering alternatives)
5. **They set a timeline** -- bridge periods are typically 6-12 months, so the RFP drops within that window

**Decision enabled:** "Which contracts should I start shaping for capture NOW?" This is true "left of the RFP" intelligence.

### Effort to Produce
**LOW.** Fully automatable API query. ~30 min/week for editorial annotation (adding context like "This bridge replaces a $50M contract that's been with Booz Allen since 2019 -- recompete expected Q1 FY27"). This is one of the lowest-effort, highest-value sections possible.

### Uniqueness
**Highly unique.** No one systematically tracks bridge contracts in a weekly digest. GovWin and BGOV users could find this data with manual searching, but nobody curates it. This would be genuinely novel intelligence even compared to $200K/yr enterprise platforms.

### Recommended Tier
**Free tier gets 3 bridge contracts/week** (the hook). **Pro gets the full list** with predecessor analysis, incumbent history, estimated recompete timeline, and pricing baseline. This section alone justifies Pro.

---

## Concept 6: "GWAC/IDIQ Vehicle Tracker"

### What It Is
Weekly intelligence on task order activity across major government-wide acquisition contracts (GWACs) and IDIQs. Tracks: task order velocity (how many TOs issued this week by vehicle), ceiling utilization (how much of the vehicle's ceiling has been obligated), new vehicles ramping up, vehicles approaching expiration, and "hot" vehicles seeing surges in activity. Covers: OASIS+, Alliant 3, CIO-SP4, SEWP VI, ITES-3S, 8(a) STARS III, Polaris, etc.

### Data Source Feasibility
**MEDIUM-HIGH -- data is available but requires careful API work.**

USAspending supports IDV (Indefinite Delivery Vehicle) searches with award type codes `IDV_B`, `IDV_B_A`, etc. The API also has a `/api/v2/idvs/awards/` endpoint for querying task orders under a parent IDV, and `/api/v2/idvs/activity/` for obligation timeline data.

**What we can track:**
- New task orders issued under each vehicle (weekly count + value)
- Cumulative obligations vs. ceiling (utilization rate)
- Which agencies are using which vehicles most heavily
- Average task order size by vehicle
- New entrants (companies winning their first TO on a vehicle)

**Challenge:** Mapping vehicle names to parent award IDs requires a one-time lookup table. OASIS+ = GS00Q17GWD*, CIO-SP4 = 75N98*, etc. Once mapped, ongoing tracking is automated.

### Value to Reader
High for BD professionals who need to decide which vehicles to pursue or which to prioritize for task order capture. Vehicle selection is a strategic decision that affects years of business development.

**Decisions enabled:**
- "Should I bid on the next GWAC on-ramp?" (Is the vehicle active enough to justify the effort?)
- "Which vehicle should I use for this opportunity?" (Vehicle with most activity in this NAICS)
- "Is my vehicle dying?" (Declining task order velocity = wind-down signal)

### Effort to Produce
**MEDIUM.** One-time vehicle mapping (~1 day). Weekly automated pull (~1 hour for QA and annotation). Requires maintaining the vehicle lookup table as new vehicles are awarded.

### Uniqueness
**Moderately unique.** HigherGov tracks "K+ Vehicles" in their database. GovTribe offers vehicle-level intelligence at $1,350-$5,500/yr. But neither publishes a weekly velocity/health report in newsletter format. We'd be the only weekly curated tracker under $1,000/yr.

### Recommended Tier
**Pro.** Vehicle health dashboard is core BD intelligence. Free tier gets a "Vehicle of the Week" highlight. Insider gets historical trend data and alerts when a tracked vehicle crosses a utilization threshold.

---

## Concept 7: "The Set-Aside Spotlight" -- Small Business Intelligence

### What It Is
Weekly intelligence on small business contracting opportunities, anchored by SBA agency scorecard data. Identifies which agencies are behind on their small business goals (and therefore likely to increase set-aside activity), tracks new set-aside solicitations by category (8(a), SDVOSB, HUBZone, WOSB, SDB), and highlights agencies with upcoming "goal crunch" periods (Q3-Q4 of the fiscal year when agencies scramble to meet targets).

### Data Source Feasibility
**HIGH -- multiple strong public data sources.**

1. **SBA Agency Scorecards** (confirmed available): Published annually with historical data back to FY2007. Grades agencies A+ through F across 5 categories: SB, WOSB, SDB, SDVOSB, HUBZone. Combined score weighted: 50% prime contracting + 20% subcontracting + 10% SB contractor growth + 20% OSDBU compliance.

2. **USAspending API**: `type_set_aside` field on every contract, with values like "SBA" (Small Business), "8AN" (8(a) Sole Source), "SDVOSBS" (SDVOSB Sole Source), "HZS" (HUBZone Sole Source), etc. Can track set-aside award volume by agency in real time.

3. **SAM.gov**: Set-aside type is a filter on opportunities. Can identify upcoming set-aside solicitations.

4. **SBA Dynamic Small Business Search**: Registry of certified small businesses by category.

**Scoring approach:** Compare each agency's current-year set-aside obligations (from USAspending) against their SBA goal (from scorecard). Agencies below target in Q2-Q3 = high probability of Q3-Q4 set-aside surge.

### Value to Reader
Very high for Personas 1 and 2 (Newcomers and Small Contractors). Small business set-asides are the primary entry point for new GovCon companies. Knowing which agencies will NEED to issue more set-asides is strategic gold.

**Decision enabled:** "Which agencies should I target this quarter for set-aside work?"

### Effort to Produce
**LOW-MEDIUM.** Annual scorecard data changes once/year. Weekly set-aside award tracking is automated from USAspending. ~1 hour/week for curation and commentary. The Q3-Q4 "goal crunch" analysis is particularly valuable and only needs updating monthly.

### Uniqueness
**Unique synthesis.** The raw SBA scorecard data is public. USAspending set-aside data is public. But nobody combines them into forward-looking "which agencies are behind and will scramble" intelligence. This is exactly the "so what" layer that justifies a newsletter.

### Recommended Tier
**Free tier** for the concept (Personas 1 and 2 are the largest audience and lowest WTP, but highest growth potential). **Pro** for agency-specific deep dives and the goal-gap analysis. This section drives free-to-paid conversion for small business readers.

---

## Concept 8: "Personnel Moves" -- Who's Changing Jobs in Government

### What It Is
Weekly tracker of notable personnel changes in federal acquisition: new Contracting Officers, program managers rotating, SES appointments, agency acquisition leadership changes. When a new person takes over a program, priorities shift, relationships reset, and opportunities emerge.

### Data Source Feasibility
**LOW -- very difficult to automate.**

Potential sources:
- SES appointments are published in the Federal Register (but with significant lag)
- Agency press releases announce leadership changes (manual monitoring)
- LinkedIn tracking (manual, borderline privacy concerns)
- SAM.gov opportunity notices sometimes include new CO names (but only per-solicitation)
- HigherGov claims "K+ People" in their database -- unclear how they source this

**Key limitation:** There is no centralized database of federal acquisition workforce appointments. COs are appointed via SF-1402 (Certificate of Appointment) which is internal. Program managers are not publicly announced. The government does not publish an org chart API.

**What IS feasible:** Monitoring a curated list of ~50 high-impact positions (agency CAOs, OSDBU directors, major program executive officers) via press releases and Federal Register notices. This is manual but manageable.

### Value to Reader
High when available. A new program manager often means new priorities, new industry days, and a reset of incumbent relationships. But the intelligence is sporadic -- some weeks there's nothing, some weeks there are 5 moves.

**Decision enabled:** "Who do I need to build a relationship with for this program?"

### Effort to Produce
**HIGH.** 2-3 hours/week of manual monitoring across 10+ sources. Low automation potential. High editorial judgment needed (which moves matter vs. routine transfers).

### Uniqueness
**Moderately unique.** GovWin tracks some personnel. BGOV covers SES appointments. But nobody publishes a weekly "musical chairs" summary focused on acquisition impact. The editorial layer ("this new CO previously championed small business -- expect more set-asides") is where we add value.

### Recommended Tier
**Insider.** This is high-effort, high-value intelligence best reserved for the premium tier. When personnel moves are directly relevant to a recompete or opportunity in the newsletter, reference them in the Free/Pro sections.

---

## Concept 9: "The Protest Report" -- Weekly GAO Protest Intelligence

### What It Is
Weekly digest of GAO bid protest decisions with analysis of what they reveal about agency evaluation practices, competitor strategies, and winning proposal characteristics. Covers: sustained protests (the agency made an error), denied protests (the agency was right), and notable protest filings that signal competitive tensions.

### Data Source Feasibility
**MEDIUM-HIGH -- data exists but requires scraping/manual processing.**

GAO publishes all protest decisions at gao.gov (though their site returned 403 during testing, the decisions are public record). Each decision includes:
- Protester name and awardee name
- Agency and contract at issue
- Grounds for protest (evaluation errors, cost/technical tradeoff, organizational conflict of interest, etc.)
- Decision and reasoning
- Corrective action taken

GAO also publishes annual statistics:
- ~2,500 protests filed/year
- ~15% sustain rate (agency made correctable error)
- ~43% result in some form of corrective action (including voluntary agency correction)

**Automation approach:**
- Scrape GAO decisions page weekly (or use RSS if available)
- NLP extraction of key fields (protester, awardee, agency, grounds, outcome)
- Cross-reference with USAspending for contract value and incumbent data

**Challenge:** GAO's website returned 403 during testing, suggesting they may block automated access. May need to use manual download + NLP processing, or their Docket Search API if one exists.

### Value to Reader
Very high for BD professionals. Protest decisions are essentially free debrief intelligence:
- **Sustained protests** reveal evaluation criteria the agency misapplied (i.e., what they actually value)
- **Denied protests** reveal what evaluators consider reasonable (pricing norms, technical approach expectations)
- **Protest filings** reveal who is competing for what (competitor intelligence)
- **Corrective actions** create re-bid opportunities (a second chance to win)

**Decision enabled:** "How will this agency evaluate proposals?" and "Should I protest this award?"

### Effort to Produce
**MEDIUM.** ~2 hours/week to review 40-50 new decisions, select 5-10 most relevant, and write commentary. The analysis requires GovCon expertise (understanding evaluation factors, technical acceptability, cost realism) but follows a repeatable pattern.

### Uniqueness
**Highly unique at this price point.** Law firms (Blank Rome, PilieroMazza, Sheppard Mullin) publish occasional protest alerts for free, but they're marketing for $500/hr legal services. No one publishes a systematic weekly digest of protests with BD-oriented analysis (not legal analysis). This fills a gap between "law firm blog posts" and "hiring a $50K/yr protest consultant."

### Recommended Tier
**Pro.** Free tier gets a "Protest of the Week" highlight with one notable decision. Pro gets the full weekly digest with competitor intelligence extracted. Insider gets alerts when protests are filed on opportunities they're tracking.

---

## Concept 10: "Budget Season Preview" -- Forward-Looking Fiscal Intelligence

### What It Is
Analysis of federal budget documents (President's Budget Request, Congressional marks, agency budget justifications) to identify program-level funding changes 12-18 months before they become contracts. Covers: new programs being funded, existing programs getting cuts, R-1/R-2 exhibits (DoD RDT&E line items), and procurement line items (P-1).

### Data Source Feasibility
**MEDIUM -- data is public but requires deep expertise to interpret.**

Available sources:
- President's Budget Request (published annually, ~February)
- Agency Congressional Budget Justifications (published with PBR, highly detailed)
- DoD R-1/R-2 exhibits (RDT&E by program element -- the gold standard for defense BD)
- DoD P-1 exhibits (procurement by line item)
- Congressional appropriations committee marks (published during markup season)
- Conference reports (final appropriations language)
- Treasury fiscal data (monthly treasury statements show actual spending vs. plan)

**All of these are public.** The challenge is not access, it's interpretation. A single R-2 exhibit is 2-3 pages of dense technical and financial data. DoD alone has ~1,500 program elements. Analyzing this requires domain expertise.

**Automation potential:** Budget documents are PDFs, but structured enough for parsing. The basic extraction (program name, FY requested amount, prior year amount, delta) is automatable. The "so what" analysis requires human expertise.

### Value to Reader
Extremely high for defense contractors (the largest GovCon segment). Budget docs are the ultimate "left of the RFP" intelligence -- they reveal agency priorities 12-18 months before solicitations. A BD team that reads the budget before their competitors has a massive shaping advantage.

**Decision enabled:** "Which programs should we invest in capturing?" and "Where should we hire/position for future growth?"

### Effort to Produce
**HIGH initially, MEDIUM ongoing.** Building the parsing pipeline for budget documents takes 2-3 weeks. Annual analysis (February budget release) is a 20-40 hour sprint. Monthly/quarterly updates on appropriations progress are ~2-3 hours each. Congressional markup season (May-September) requires weekly monitoring (~3 hours/week).

### Uniqueness
**Moderately unique.** BGOV's budget analysis is the gold standard but costs $8K+/yr. Govini does budget-to-contract pipeline analysis at enterprise prices. Several free outlets (Defense One, Federal News Network) cover budget toplines but not program-level detail. Our niche: program-level budget intelligence at $249-699/yr, focused on "what contracts will this create?" rather than "what did Congress do?"

### Recommended Tier
**Pro** for topline budget analysis and notable program changes. **Insider** for program-level deep dives, especially DoD R-2 analysis. Consider a seasonal "Budget Season Special Edition" as a paid add-on.

---

## Concept 11: "The Incumbent Report Card" -- Contractor Performance Signals

### What It Is
Inference-based assessment of contractor performance using public data signals. Since CPARS (Contractor Performance Assessment Reporting System) ratings are not public, we derive performance signals from observable contract actions: option exercises (good performance), early terminations (bad), contract modifications (scope changes = potential trouble), ceiling increases (exceeding expectations), and re-award patterns.

### Data Source Feasibility
**MEDIUM -- inference-based, not direct performance data.**

**What's NOT available:** CPARS ratings are only accessible to registered government users and contractors reviewing their own ratings. There is no public API or data dump. PPIRS (Past Performance Information Retrieval System) is similarly restricted.

**What IS available from USAspending:**
- Option exercises (modification type = option exercise, positive signal)
- Funding modifications (incremental funding = continued confidence)
- Contract terminations (negative signal, though T4C ≠ poor performance)
- Re-award to same contractor (the ultimate positive signal)
- Ceiling increases (agency wants MORE of this contractor's work)
- Negative modifications (scope reduction, ceiling decrease)

**Derived "report card" signals:**
| Signal | Interpretation | Data Source |
|--------|---------------|-------------|
| All options exercised | Strong performance | USAspending modifications |
| Options NOT exercised | Performance concern or budget issue | Absence of expected modifications |
| Ceiling increase | Exceeding expectations | USAspending modifications |
| Bridge contract awarded to same incumbent | OK performance but slow recompete | USAspending keyword search |
| Contract terminated early | Potential performance failure | USAspending (limited data) |
| Re-awarded same work to same contractor | Strong past performance | Historical award pattern |
| Subcontractor changes mid-performance | Team instability | Subaward data changes |

### Value to Reader
High for competitive intelligence. When pursuing a recompete, knowing whether the incumbent performed well or poorly is critical to the capture strategy. If the incumbent has a "report card" showing missed options and scope reductions, that's a vulnerability to exploit.

**Decision enabled:** "How strong is the incumbent?" and "Should we position as an alternative or as a complement?"

### Effort to Produce
**MEDIUM.** Requires building modification history for target contracts, which is an API-intensive process. Could be produced on-demand for contracts featured in Recompete Alerts rather than as a comprehensive weekly section. ~2 hours/week for 5-10 featured incumbents.

### Uniqueness
**Unique.** Nobody publishes inferred performance assessments from public data. The enterprise platforms have some modification tracking, but they don't synthesize it into performance narratives. This is genuinely novel competitive intelligence.

### Recommended Tier
**Pro.** Include with Recompete Alert cards as an "Incumbent Performance Signal" badge (green/yellow/red). Insider gets detailed modification history and performance timeline.

---

## Concept 12: "AI/Automation Watch" -- Tech Trends Reshaping GovCon

### What It Is
Weekly tracking of technology mandates, policies, and procurement trends that create new contract opportunities or disrupt existing ones. Covers: AI executive orders and agency implementation plans, zero trust architecture mandates (OMB M-22-09 deadline), FedRAMP authorizations, cloud migration progress, cybersecurity directives (CISA BODs), and emerging tech pilots.

### Data Source Feasibility
**MEDIUM -- combination of public data and manual curation.**

Available sources:
- FedRAMP Marketplace (public, lists authorized products and authorization dates)
- USAspending filtered by tech-related NAICS/PSC codes (our pipeline already does this)
- OMB memoranda and executive orders (public, published on whitehouse.gov)
- CISA Binding Operational Directives (public)
- Agency AI inventories (required by EO, published publicly)
- Federal CIO Council publications
- NIST standards and guidelines

**What we already have:** The pipeline.py already tracks 9 tech verticals (AI/ML, Cybersecurity, Cloud, Data Analytics, DevSecOps, Zero Trust, FedRAMP, Identity Management, Networking/SDWAN). This section would add the policy/mandate layer on top of the spending data.

### Value to Reader
High for tech-focused contractors. Understanding which mandates are creating procurement demand is the difference between chasing trends and riding them. Zero trust, for example, has created billions in new contracts since OMB M-22-09.

**Decision enabled:** "Which technology capabilities should we invest in?" and "Where is mandate-driven demand headed?"

### Effort to Produce
**LOW-MEDIUM.** We already track tech vertical spending. Adding the policy layer is ~1-2 hours/week of monitoring 5-6 government tech publications and mapping mandates to spending trends.

### Uniqueness
**Low uniqueness for the news; high uniqueness for the synthesis.** MeriTalk, Federal News Network, GovCIO Media, and Nextgov all cover GovCon tech trends. But nobody maps mandates to contract spending data in a weekly intelligence format. "Zero trust spending is up 45% QoQ, driven by CISA BOD 23-02 compliance deadline in Q2" is the kind of synthesis no one else publishes.

### Recommended Tier
**Free.** This section drives SEO and attracts the tech-first audience (Persona 2 and 3). It's also the section most likely to get shared on LinkedIn. Gate the spending data analysis behind Pro.

---

## Concept 13: "The Subcontractor Signal" -- Sub-tier Intelligence

### What It Is
Analysis of federal subaward data to reveal prime-sub relationships, team compositions, and subcontracting patterns. Shows which primes are most active in subcontracting, which subs are gaining or losing work, and how team compositions are shifting across major contracts.

### Data Source Feasibility
**MEDIUM -- data exists but has limitations.**

The former FSRS (Federal Subaward Reporting System) has been migrated to SAM.gov as of March 2025. SAM.gov provides:
- Public subaward API and public subcontract API (confirmed available)
- Prime-sub relationship data for awards above $30K threshold
- Subaward amounts, recipients, and descriptions

USAspending also shows:
- `subaward_count` and `total_subaward_amount` per prime award
- `subcontracting_plan` field (whether a plan is required)

**Limitations:**
- Reporting compliance varies (not all primes report sub data on time)
- Only covers subawards above $30K (misses many small business subs)
- Subaward descriptions are often vague
- No API returned results in testing for some awards (may be data freshness issue)

### Value to Reader
Moderate-to-high. Understanding team compositions helps with:
- Identifying potential teaming partners (who works with whom?)
- Competitive intelligence (what does the incumbent's team look like?)
- Pipeline development (which primes are growing their subcontracting?)

**Decision enabled:** "Who is the incumbent teamed with?" and "Which primes should I approach as a sub?"

### Effort to Produce
**MEDIUM.** Automated API pull of subaward data. ~1-2 hours/week for analysis and commentary. The visualization challenge (team composition diagrams) adds complexity for newsletter format.

### Uniqueness
**Moderately unique.** HigherGov and Federal Compass offer some teaming/partner data. But a weekly "who's teaming with whom" digest in newsletter format is novel.

### Recommended Tier
**Pro.** Subaward data enriches Recompete Alerts and New Awards sections. Insider gets searchable prime-sub relationship database.

---

## Concept 14: "Calendar: What's Coming" -- Events, Deadlines, Industry Days

### What It Is
A curated weekly calendar of upcoming government contracting events: industry days, pre-solicitation conferences, RFI response deadlines, proposal due dates for major opportunities, acquisition forecast releases, budget hearings, and relevant conferences. Focuses on "shaping opportunities" -- events where contractors can influence requirements before the RFP drops.

### Data Source Feasibility
**HIGH -- multiple public sources, straightforward curation.**

Available sources:
- SAM.gov opportunity notices (industry days are posted as Special Notices)
- SAM.gov response deadlines (every solicitation has a due date)
- Agency acquisition forecasts (published semi-annually on SAM.gov)
- Congressional hearing schedules (public, on committee websites)
- Trade show calendars (AFCEA, NDIA, PSC, etc.)
- Agency "FBO Forecast" pages

**Automation potential:** SAM.gov API can be queried for upcoming deadlines and industry day notices. Congressional hearings and trade shows require manual monitoring but follow predictable schedules.

### Value to Reader
High for BD professionals who need to plan their week. Missing an industry day or RFI deadline is a costly mistake. A consolidated calendar saves time and prevents missed opportunities.

**Decision enabled:** "What should I attend this week?" and "What deadlines am I about to miss?"

### Effort to Produce
**LOW-MEDIUM.** SAM.gov query is automatable. Trade show and hearing monitoring is ~1 hour/week. Calendar format is simple to produce and easy to scan.

### Uniqueness
**Low standalone uniqueness.** Several platforms offer opportunity calendars (GovTribe, Govly). But embedding it in a weekly newsletter with editorial context ("Why this industry day matters: the agency just posted a bridge contract on this same requirement") adds value beyond a raw calendar. Also, nobody offers it at our price point.

### Recommended Tier
**Free.** Calendar is a utility feature that drives opens and habit formation. Free tier gets the next 2 weeks. Pro gets 90-day lookahead. This is the section that makes readers open the email every Monday.

---

## Concept 15: "Win/Loss Debrief" -- Learning from Others' Outcomes

### What It Is
Anonymized or generalized lessons from contract award outcomes. Analyzes patterns in who wins and why, based on observable data: winning proposal characteristics (team size, past performance signals, pricing patterns), common reasons for protest (evaluation errors, unrealistic pricing), and structural patterns (incumbents win X% of the time in these conditions, newcomers win when Y).

### Data Source Feasibility
**LOW-MEDIUM -- requires inference and expert synthesis.**

**What's available:**
- USAspending: winner, price, agency, competition level, set-aside type
- GAO protest decisions: detailed evaluation reasoning (when protested)
- Historical win patterns: can compute win rates by contractor, agency, set-aside type

**What's NOT available:**
- Losing bidders' identities (only the winner is public for most contracts)
- Actual evaluation scores or technical ratings
- Debrief content (confidential between agency and bidder)
- Proposal content or technical approaches

**What we CAN produce:**
- Statistical patterns: "In 8(a) sole-source awards under $5M, the winning contractor has an average of X years in that NAICS"
- Protest-derived insights: "3 of 5 sustained protests this month cited unrealistic cost evaluation"
- Incumbent advantage statistics by agency and contract type
- "What winners look like" profiles based on observable data

### Value to Reader
Moderate. Useful for improving proposal strategies, but the analysis is necessarily generalized rather than specific to any one pursuit. Best used as educational content rather than tactical intelligence.

**Decision enabled:** "How should we approach this type of opportunity?" and "What do winning contractors look like?"

### Effort to Produce
**HIGH.** Requires statistical analysis of award patterns, protest decision review, and expert synthesis. ~3-4 hours/week for meaningful content. Risk of being too generic to be actionable.

### Uniqueness
**Moderately unique.** Lohfeld, Shipley, and other proposal consultants publish occasional win/loss insights for marketing purposes. GovWin publishes win rate statistics. But nobody publishes a systematic weekly analysis. However, the generalized nature limits its value compared to more specific sections.

### Recommended Tier
**Pro** as a monthly feature rather than weekly. Publish "Monthly Win/Loss Patterns" with 3-5 actionable insights. Too thin for weekly publication.

---

## Priority Matrix

### Add Immediately (Before Launch or Week 1-2)

| # | Section | Effort | Value | Tier |
|---|---------|--------|-------|------|
| 1 | "Is It Wired?" Scorecard | Medium | Highest | Free (score) / Pro (detail) |
| 5 | "The Bridge Watch" | Low | Very High | Free (3/wk) / Pro (full) |
| 7 | "Set-Aside Spotlight" | Low-Med | Very High | Free (concept) / Pro (agency detail) |
| 14 | "Calendar: What's Coming" | Low-Med | High | Free |

### Add in Weeks 3-6

| # | Section | Effort | Value | Tier |
|---|---------|--------|-------|------|
| 9 | "The Protest Report" | Medium | Very High | Pro |
| 6 | "GWAC/IDIQ Vehicle Tracker" | Medium | High | Pro |
| 12 | "AI/Automation Watch" | Low-Med | High | Free |
| 11 | "Incumbent Report Card" | Medium | High | Pro (badge on Recompete cards) |

### Add in Weeks 7-12

| # | Section | Effort | Value | Tier |
|---|---------|--------|-------|------|
| 4 | "Price-to-Win Intel" | Medium | Very High | Pro / Insider |
| 13 | "Subcontractor Signal" | Medium | Moderate-High | Pro |
| 2 | "Dead Contract Walking" | High | High (timely) | Pro |

### Phase 2 (After Month 3)

| # | Section | Effort | Value | Tier |
|---|---------|--------|-------|------|
| 10 | "Budget Season Preview" | High (seasonal) | Very High | Insider |
| 3 | "The Teaming Board" | High (community) | High | Insider |
| 8 | "Personnel Moves" | High | Moderate-High | Insider |
| 15 | "Win/Loss Debrief" | High | Moderate | Pro (monthly) |

---

## Data Architecture Implications

The existing `pipeline.py` pulls from USAspending's `/search/spending_by_award/` endpoint with keyword-based vertical filtering. To support the new sections, we need to expand the pipeline:

### New API Queries Needed

| Section | API Endpoint | Query Type |
|---------|-------------|------------|
| Is It Wired? | `/awards/{id}/` | Detail enrichment (extent_competed, number_of_offers) |
| Bridge Watch | `/search/spending_by_award/` | Keyword: "bridge contract", "bridge extension" |
| Set-Aside Spotlight | `/search/spending_by_award/` | Filter by `type_set_aside` values |
| Vehicle Tracker | `/search/spending_by_award/` | IDV award type codes |
| Incumbent Report Card | `/awards/{id}/` | Modification history |
| Subcontractor Signal | SAM.gov subaward API | Prime-sub relationships |
| Protest Report | GAO website scrape | Decision text extraction |

### New Data Fields to Capture

Add to the enrichment phase of `pipeline.py`:
```
extent_competed
extent_competed_description
number_of_offers_received
solicitation_procedures
other_than_full_and_open
type_of_contract_pricing
subcontracting_plan
```

These fields are already available from the `/awards/{id}/` detail endpoint (confirmed via API testing) and require no new API access.

---

## Competitive Moat Assessment

### What This Bundle Creates

With these 15 sections (8 current + 15 new = 23 total), the newsletter offers:

| Intelligence Layer | Sections | Nearest Competitor | Competitor Price |
|-------------------|----------|-------------------|-----------------|
| Opportunity Discovery | Recompete Alerts, Bridge Watch, Calendar, Set-Aside Spotlight | GovTribe | $1,350/yr |
| Competitive Intelligence | Is It Wired?, Incumbent Report Card, Protest Report, Subcontractor Signal | GovWin IQ | $5,000+/yr |
| Market Intelligence | Vehicle Tracker, Price-to-Win, Market Pulse, AI/Automation Watch | BGOV | $8,000+/yr |
| Strategic Intelligence | Budget Preview, Personnel Moves, DOGE Tracker, Dead Contract Walking | Govini | $50K+/yr |
| Community/Network | Teaming Board, Win/Loss Debrief | Federal Compass | $5,000+/yr |

**At $249-699/yr, we offer 70-80% of the intelligence value of platforms costing $5K-$200K/yr.** The gap is depth (they have decades of historical data) and breadth (they cover every contract, we curate the most relevant). But for a small contractor making bid/no-bid decisions, curated intelligence beats exhaustive databases.

### The Three "Moat" Sections

These sections have no equivalent at any price point and should be marketed as signature features:

1. **"Is It Wired?" Scorecard** -- Nobody scores opportunities for incumbent predetermination
2. **"The Bridge Watch"** -- Nobody systematically tracks bridge contracts as recompete signals
3. **"The Protest Report" (BD-focused)** -- Nobody curates protest decisions for competitive intelligence (only for legal analysis)

---

## Revenue Impact Estimate

### Free-to-Paid Conversion Drivers

| Section | Role in Funnel |
|---------|---------------|
| Bridge Watch (3/wk free) | "I need to see all of them" -> Pro |
| Is It Wired? (score only free) | "I need to see WHY it's wired" -> Pro |
| Set-Aside Spotlight | "Which agencies are behind?" -> Pro |
| Calendar | Habit formation, opens every Monday |
| AI/Automation Watch | SEO/LinkedIn shares, top-of-funnel |

### Pro-to-Insider Upgrade Drivers

| Section | Role in Upgrade |
|---------|----------------|
| Budget Preview (deep dives) | "I need the R-2 analysis" -> Insider |
| Teaming Board | "I need to find partners" -> Insider |
| Personnel Moves | "I need to know who's in charge" -> Insider |
| Price-to-Win (detailed) | "I need labor rate benchmarks" -> Insider |

### Estimated Impact on Conversion

Adding the top 5 sections should increase free-to-Pro conversion by 2-4 percentage points (from estimated 5-7% baseline to 7-11%) based on the principle that each uniquely valuable gated section adds ~0.5-1pp of conversion. The "Is It Wired?" scorecard alone, given it's the #1 requested feature, could drive 1-2pp by itself.

At 15K free subs (Year 1 target), that's 150-300 additional Pro subscribers = $37K-$75K incremental ARR.
