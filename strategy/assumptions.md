# Assumption Audit — GovCon Weekly Intelligence

| # | Assumption | Evidence For | Evidence Against | Confidence | Test |
|---|-----------|-------------|-----------------|-----------|------|
| 1 | Small/mid GovCon firms have dedicated BD professionals who read newsletters | - LinkedIn shows ~500 "GovCon BD" profiles<br>- r/govcon subreddit exists | - Many small firms are technical shops without dedicated BD staff<br>- No data on newsletter reading habits | **LOW** | LinkedIn search: count profiles at 50-500 employee firms. Target 10 for phone calls: "Do you read industry newsletters?" |
| 2 | BD professionals need better contract intelligence (have a "looking for opportunities" problem) | - Incumbent tools (GovWin, Deltek) exist and have paying customers<br>- USAspending data is public but hard to parse | - Incumbents may already solve this<br>- BD pros might use informal networks (LinkedIn, conferences) instead<br>- SAM.gov already aggregates opportunities | **MEDIUM** | Interview 5 GovCon BD professionals: "Walk me through how you found your last 3 capture targets. What tools did you use? Where did you get stuck?" |
| 3 | AI-generated insights are more valuable than raw data dumps | - Humans prefer narrative to tables<br>- Successful newsletters (Morning Brew, TLDR) use curation + commentary | - GovCon is a data-driven industry—maybe they prefer raw data<br>- AI might miss context that domain experts catch | **MEDIUM** | A/B test: send 25 people AI narrative version, 25 people raw data table version. Measure open rate + replies. |
| 4 | Weekly cadence is optimal (vs daily, monthly, or real-time alerts) | - Most B2B newsletters are weekly<br>- Award data accumulates weekly | - BD capture cycles are multi-month—weekly might be too frequent<br>- Daily might catch urgent opportunities better<br>- Monthly might be "enough" for strategic planning | **LOW** | Survey first 50 subscribers Week 2: "Would you prefer daily, weekly, or monthly?" Track open rates over 4 weeks—do they decline (suggesting too frequent)? |
| 5 | 9 tech verticals is the right focus (AI/ML, Cyber, Cloud, etc.) | - These are high-growth areas in federal IT<br>- Data shows ~500 awards/week in these categories | - Many GovCon firms specialize in ONE vertical—9 might be too broad<br>- Other high-volume verticals (facilities, logistics) ignored<br>- "Tech" focus might exclude 70% of GovCon market | **MEDIUM** | Week 3: Ask subscribers "Which of these 9 verticals do you care about?" If 80%+ pick 2-3 verticals, narrow focus. |
| 6 | Free tier drives adoption, paid tier drives revenue | - Standard SaaS playbook<br>- Beehiiv supports this model | - GovCon firms may have procurement friction—free is easy, paid requires approvals<br>- If free tier is "good enough," nobody upgrades | **MEDIUM** | Month 2: Survey 20 engaged free users: "What would make you pay $49/mo for this?" If answer is vague or "nothing," paid tier is in trouble. |
| 7 | LinkedIn + email outreach can acquire 500 subscribers in Q1 | - Founder has warm network<br>- LinkedIn connection rate is typically 20-40% | - Addressable market might be <500 people<br>- Cold outreach conversion rates are typically 1-3%<br>- No paid acquisition budget | **LOW** | Week 2: Track metrics. If you send 100 LinkedIn messages and get <5 subscribers, the math doesn't work. |
| 8 | USAspending API data is accurate and sufficient | - It's the official government data source<br>- Pipeline successfully pulled ~500 awards | - Data might be delayed (awards posted weeks after signature)<br>- Descriptions might be vague or incomplete<br>- NAICS codes might be wrong (contractors misclassify to meet set-asides) | **MEDIUM-HIGH** | Week 1: Manually spot-check 20 awards against SAM.gov and FPDS. If >3 have incorrect data, pipeline needs additional sources. |
| 9 | Recompete tracking is a high-value feature | - Incumbents have inside track on recompetes<br>- Recompetes are 40-60% of federal contract volume | - Maybe firms already track their own incumbencies<br>- Historical data might not be available via API | **MEDIUM** | Month 1: Add recompete flag to newsletter. Track clicks. Ask subscribers: "Did you pursue any recompetes from our alert?" If zero by Month 2, deprioritize. |
| 10 | Beehiiv is the right platform (vs Substack, Ghost, custom) | - Better growth tools than Substack<br>- Free tier up to 2,500 subs | - Beehiiv HTML import might be flaky<br>- Custom solution gives more control<br>- Substack has better discovery/network effects | **MEDIUM-HIGH** | Week 1: Test HTML import to Beehiiv. If it requires >30min of manual formatting per send, switch to Markdown + custom renderer. |
| 11 | The founder can generate quality insights without deep GovCon expertise | - AI can analyze patterns in data<br>- Founder has technical/data background | - GovCon is highly specialized—nuance matters<br>- Veterans can spot BS instantly<br>- Domain expertise might be table stakes | **LOW** | Pre-launch: Hire a GovCon consultant ($500) to review first 3 newsletters. If they find >5 major errors per newsletter, hire them as advisor or kill the project. |
| 12 | Solo founder can execute launch + operations | - Founder has technical skills (built pipeline)<br>- No payroll = lower burn | - Newsletter + sales + ops + technical = 40+ hrs/week<br>- Solo = single point of failure<br>- No domain expertise = higher error rate | **MEDIUM** | Week 4: Track hours. If >15 hrs/week and founder is burning out, hire contractor or shut down. |
| 13 | $49/mo Pro tier pricing is feasible | - GovWin IQ starts at $200/mo<br>- B2B SaaS newsletters charge $29-99/mo | - GovCon firms might have budget constraints<br>- Free tier might cannibalize paid tier<br>- $49/mo requires perceived value of 2-4 hours saved per month | **LOW** | Month 2: Run 10 pricing conversations. Show Pro features, ask: "Would you pay $49/mo for this?" If <3 say yes, pricing is wrong. |
| 14 | Enterprise tier ($500-2,500/mo) is viable | - GovCon consulting firms bill $150-300/hr<br>- White-label intelligence is valuable to multi-office firms | - Enterprise sales cycle is 3-6 months<br>- Requires trust + proven ROI<br>- Solo founder can't support enterprise SLAs | **LOW** | Month 3: Identify 5 enterprise prospects (>500 employees). Cold email pitch. If zero responses, enterprise is 12+ months away. |
| 15 | Q1 goals (500 subs, 40% open rate, $5K revenue) prove PMF | - Industry benchmarks: 40% open = strong engagement<br>- $5K = 100 paid subs at $50/mo = real willingness to pay | - 500 subs might be acquired through unsustainable manual outreach<br>- Open rates decline over time<br>- Early revenue might be "pity purchases" from warm network | **MEDIUM** | Month 3: If you hit these numbers, ask: "Can we 10x this with same effort?" If answer is no, PMF is false positive. |
| 16 | Vertical expansion (more contract types, more agencies) increases value | - More data = more opportunities<br>- Some firms work across multiple verticals | - More data = more noise<br>- Generalist newsletters lose focus<br>- Better to be #1 in one niche than #4 in nine | **MEDIUM** | Month 2: Survey power users: "Would you pay more for coverage of [additional vertical]?" If answer is "no, I only care about X," narrow focus. |
| 17 | This can become a $1M+ ARR business | - GovCon market is $600B+<br>- Incumbents (GovWin) are multi-million dollar businesses | - Addressable market might be <5,000 people<br>- Newsletter model caps at $500K ARR without platform<br>- Requires transition to SaaS, not just newsletter | **LOW** | Month 6: If subscriber count plateaus <1,000, newsletter is a lifestyle business ($50K/yr), not a venture-scale startup. Adjust expectations or pivot. |
| 18 | Word-of-mouth / referrals will drive organic growth after initial outreach | - Good newsletters grow via forwarding<br>- Beehiiv has referral program built-in | - B2B newsletters don't go viral<br>- GovCon is relationship-driven, not viral-driven<br>- No incentive for subscribers to share | **LOW** | Month 2: Track referral source. If <10% of new subs come from referrals, organic growth is dead—must pay for ads or partner with communities. |
| 19 | The landing page converts visitors to subscribers | - Clean design, clear value prop<br>- Industry standard conversion is 10-30% | - No social proof yet<br>- CTA might be weak<br>- Visitors might bounce if they don't immediately understand value | **MEDIUM** | Week 2: Run LinkedIn ads ($100 budget) to drive 200 visitors. Measure conversion rate. If <5%, landing page needs A/B testing. |
| 20 | Newsletter format (HTML + narrative) is better than alternatives (Slack, Discord, daily digest) | - Email is where B2B professionals live<br>- HTML allows rich formatting | - GovCon community might prefer real-time discussion (Slack)<br>- Daily digest might be more actionable<br>- Some professionals ignore newsletters | **MEDIUM** | Month 2: Survey 30 subscribers: "If we launched a Slack community, would you join?" If >50% say yes, test a parallel Slack channel. |

## Highest-Risk Assumptions

### 1. Small/mid GovCon firms have dedicated BD professionals who read newsletters (LOW confidence)
**Why it's critical:** If the target persona doesn't exist, the entire business model collapses. No amount of better content or features fixes "nobody wants this."

**What would have to be true:**
- At least 1,000 people on LinkedIn match the profile (50-500 employee GovCon firms, BD/Capture role)
- These people spend time reading industry content (newsletters, blogs, reports)
- They're not fully served by existing tools (GovWin, personal networks, SAM.gov)

**Test (WEEK 1-2, $0 cost):**
1. Search LinkedIn: "GovCon Business Development" + filter by company size (50-500 employees). Count results.
2. If <500 profiles, the newsletter model is too narrow. Expand to adjacent personas (proposal writers, capture managers, technical leads) OR pivot to services.
3. Cold-call 10 people: "Do you read any newsletters about federal contracting? If yes, which ones? What do you wish existed?"
4. **Decision criteria:** If you can't identify 1,000 ICP profiles + 3+ say "I'd read that" → PIVOT to consulting or fractional BD services instead of newsletter.

### 2. AI-generated insights are more valuable than raw data dumps (MEDIUM confidence)
**Why it's critical:** If subscribers prefer raw data, the entire AI value proposition is wrong. The founder's competitive advantage (AI content generation) becomes a liability (adds latency, introduces errors).

**What would have to be true:**
- GovCon BD professionals lack time to analyze raw data themselves
- The AI's "So What" commentary is accurate and actionable
- Narrative format drives more engagement (clicks, replies) than tables

**Test (WEEK 2-3, $0 cost):**
1. A/B test with first 50 subscribers:
   - Group A (25 people): AI narrative format (current design)
   - Group B (25 people): Raw data table (awards + NAICS + value + links)
2. Measure: open rate, click-through rate, replies, unsubscribes
3. Week 3: Email both groups: "Which format do you prefer? Why?"
4. **Decision criteria:** If Group B (raw data) has higher engagement OR >60% say they prefer raw data → PIVOT to data-first format, deprioritize AI narrative.

### 3. LinkedIn + email outreach can acquire 500 subscribers in Q1 (LOW confidence)
**Why it's critical:** If the acquisition channel doesn't scale, the growth targets are fantasy. No subscribers = no revenue = dead business.

**What would have to be true:**
- LinkedIn connection request acceptance rate >30%
- Conversion rate from connection → subscriber >10%
- Addressable market is at least 5,000 people (to acquire 500 at 10% conversion)
- Email open rates >30%, click-through >5%

**Test (WEEK 1-3, $0 cost):**
1. Send 100 LinkedIn connection requests to ICP profiles (Week 1)
2. Track: acceptance rate, conversion to subscriber
3. Week 2: If you sent 100 messages and got <5 subscribers (5% conversion), the math doesn't work:
   - 500 subscribers ÷ 0.05 conversion = 10,000 outreach touches required
   - That's 150+ messages/day for 60 days (not sustainable)
4. **Decision criteria:** If Week 2 conversion is <5% → TEST paid acquisition (LinkedIn ads, GovCon community sponsorships) or PIVOT to partnership model (white-label for existing GovCon media).

### 4. The founder can generate quality insights without deep GovCon expertise (LOW confidence)
**Why it's critical:** If the insights are wrong, credibility is destroyed. One "your analysis is BS" post on r/govcon kills the business.

**What would have to be true:**
- AI can accurately interpret NAICS codes, contract vehicles, set-asides, recompetes
- The founder can spot-check and catch errors before publication
- Domain expertise isn't required for high-level trend analysis

**Test (PRE-LAUNCH, $500 cost):**
1. Hire a GovCon consultant with 10+ years experience ($500 for 3-hour review)
2. Send them the first 3 newsletters before publication
3. Ask: "What's wrong with this analysis? What would you change?"
4. **Decision criteria:** If they find >3 major errors per newsletter (wrong contract type, misinterpreted trend, bad recommendation) → HIRE them as ongoing advisor ($200/mo) OR SHUT DOWN until founder learns GovCon domain.

### 5. Beehiiv HTML import works reliably (MEDIUM-HIGH confidence)
**Why it's critical:** If newsletter publishing takes >1 hour/week due to formatting issues, the time budget collapses. Solo founder can't spend 4+ hours/week fighting HTML.

**Test (WEEK 1, $0 cost):**
1. Import the existing `report_2026-03-18.html` into Beehiiv
2. Preview in desktop + mobile
3. Send test newsletter to 3 personal emails (Gmail, Outlook, iPhone)
4. Track time: if import + formatting takes >30 minutes, the HTML approach is too fragile
5. **Decision criteria:** If import fails OR requires >30min manual cleanup → PIVOT to Markdown + simpler template OR switch to Substack (better Markdown support).

## Cheapest Tests Summary

| Assumption | Test | Cost | Time | Kill Signal |
|-----------|------|------|------|-------------|
| ICP exists | LinkedIn search + 10 phone calls | $0 | 4 hours | <500 LinkedIn profiles OR <3 say "I'd read that" |
| AI > raw data | A/B test (50 subscribers) | $0 | 2 hours | Raw data group has 2x engagement |
| Outreach scales | 100 LinkedIn messages, track conversion | $0 | 6 hours | <5% conversion rate by Week 2 |
| Insights are accurate | Hire GovCon consultant to review | $500 | 3 hours | >3 major errors per newsletter |
| Beehiiv works | Import + send test newsletter | $0 | 1 hour | >30min formatting per send |

## What Happens If We're Wrong About Everything

**Worst case scenario:** All 5 high-risk assumptions are false.

- The ICP is <300 people (too small for newsletter)
- They prefer raw data (AI narrative is overhead, not value)
- LinkedIn outreach caps out at 80 subscribers (unsustainable channel)
- The insights are wrong (no domain expertise = no credibility)
- Beehiiv is a formatting nightmare (too much manual work)

**Fallback option:** Pivot to **GovCon Fractional BD Consulting**
- Target: Small GovCon firms (10-50 employees) with no BD staff
- Offer: Fractional BD services (10 hrs/mo, $2,500/mo)
- Deliverable: Weekly opportunity briefing + capture target recommendations
- Channel: Direct outreach to technical founders (engineers who won contracts but don't know how to grow)
- Advantage: High-touch, high-price, no scale required, uses same data pipeline

If newsletter hits kill criteria by Month 2, this is the pivot.
