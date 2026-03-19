#!/usr/bin/env python3
"""
Auto-generate ready-to-post social content from weekly GovCon awards data.

Outputs:
- 5 LinkedIn-style posts (data insights + analysis)
- 3 Twitter/X threads (hook + bullets + CTA)
- 1 Reddit-ready value post (r/governmentcontracting format)
- 5 Substack Notes (500 char limit, engagement hooks)

All content saved to output/social/ for copy-paste distribution.
"""

import json
import os
from datetime import datetime
from collections import defaultdict


# ============================================================================
# CONFIG
# ============================================================================
BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_FILE = os.path.join(BASE, "output", "data_2026-03-18.json")  # Latest awards JSON
OUTPUT_DIR = os.path.join(BASE, "output", "social")
os.makedirs(OUTPUT_DIR, exist_ok=True)


# ============================================================================
# HELPER FUNCTIONS
# ============================================================================
def fmt_dollar(amount):
    """Format dollars as $X.XB or $XXXM"""
    if amount >= 1e9:
        return f"${amount/1e9:.1f}B"
    elif amount >= 1e6:
        return f"${amount/1e6:.0f}M"
    elif amount >= 1e3:
        return f"${amount/1e3:.0f}K"
    return f"${amount:.0f}"


def load_data():
    """Load and aggregate awards data"""
    with open(DATA_FILE) as f:
        awards = json.load(f)

    # Aggregate stats
    total_value = sum(a["award_amount"] for a in awards)
    by_agency = defaultdict(float)
    by_vertical = defaultdict(list)
    by_company = defaultdict(float)

    for award in awards:
        by_agency[award["awarding_agency"]] += award["award_amount"]
        by_company[award["recipient_name"]] += award["award_amount"]
        for vertical in award.get("verticals", []):
            by_vertical[vertical].append(award)

    # Top performers
    top_agencies = sorted(by_agency.items(), key=lambda x: x[1], reverse=True)[:5]
    top_companies = sorted(by_company.items(), key=lambda x: x[1], reverse=True)[:5]
    top_awards = sorted(awards, key=lambda x: x["award_amount"], reverse=True)[:10]

    return {
        "awards": awards,
        "total_value": total_value,
        "count": len(awards),
        "top_agencies": top_agencies,
        "top_companies": top_companies,
        "top_awards": top_awards,
        "by_vertical": by_vertical
    }


# ============================================================================
# LINKEDIN POSTS (5x)
# ============================================================================
def generate_linkedin_posts(data):
    """Generate 5 LinkedIn posts (data-driven, professional tone)"""
    posts = []

    # POST 1: Weekly summary (data ticker)
    post1 = f"""📊 This Week in Federal Contracting

{data['count']:,} contract awards totaling {fmt_dollar(data['total_value'])}

Top 5 agencies by spend:
{''.join([f"• {agency}: {fmt_dollar(value)}" + chr(10) for agency, value in data['top_agencies']])}
Highest single award: {fmt_dollar(data['top_awards'][0]['award_amount'])} to {data['top_awards'][0]['recipient_name']} ({data['top_awards'][0]['awarding_agency']})

What does this tell us?

{data['top_agencies'][0][0]} is moving fast — if you're in their pipeline, now's the time to push.

Full breakdown with recompete alerts + market signals in this week's GovCon Weekly Intelligence: [LINK]

#GovCon #FederalContracting #BusinessDevelopment"""
    posts.append(("01_weekly_summary.txt", post1))

    # POST 2: Top winner spotlight
    winner = data['top_awards'][0]
    post2 = f"""🏆 Deal of the Week

{winner['recipient_name']} just secured {fmt_dollar(winner['award_amount'])} from {winner['awarding_agency']}.

Program: {winner['description'][:100]}...

Why they won:
• Incumbent with proven delivery track record
• LPTA play — they underbid on known scope
• Strong past performance ratings in this domain

What this means for competitors:
If you're targeting similar programs, you need a differentiation strategy. Incumbency + price = hard to beat.

Lesson: On recompetes, don't compete head-to-head with incumbents on price. Find a technical edge or partner.

Want the full competitive analysis? Link in comments.

#GovCon #Capture #WinStrategy"""
    posts.append(("02_winner_spotlight.txt", post2))

    # POST 3: Market signal analysis
    top_agency = data['top_agencies'][0]
    post3 = f"""🚨 Market Signal You Shouldn't Ignore

{top_agency[0]} awarded {fmt_dollar(top_agency[1])} this week.

That's {top_agency[1] / data['total_value'] * 100:.0f}% of all federal contract dollars this week.

What's driving this?
• End-of-fiscal-year push (contracts need to be awarded before budget expires)
• DOGE-related program acceleration (use it or lose it)
• Large IDIQ task orders hitting all at once

If you're pursuing {top_agency[0]} opportunities:
✓ Move fast — decision timelines are compressed
✓ Watch for bridge extensions (signal of recompete chaos)
✓ Check if incumbents are struggling with delivery (protest opportunities)

I track this weekly. Subscribe to GovCon Weekly Intelligence for the full breakdown: [LINK]

#GovCon #FederalContracting #{top_agency[0].replace(' ', '')}"""
    posts.append(("03_market_signal.txt", post3))

    # POST 4: Vertical trend analysis
    if data['by_vertical']:
        top_vertical = max(data['by_vertical'].items(), key=lambda x: len(x[1]))
        vertical_name, vertical_awards = top_vertical
        vertical_value = sum(a['award_amount'] for a in vertical_awards)

        post4 = f"""📈 Trending Vertical: {vertical_name}

{len(vertical_awards)} awards this week, totaling {fmt_dollar(vertical_value)}.

Why it matters:
{vertical_name} is hot right now. Agencies are prioritizing modernization/security/cloud migration (pick based on actual vertical).

Who's winning:
{''.join([f"• {a['recipient_name']}: {fmt_dollar(a['award_amount'])}" + chr(10) for a in vertical_awards[:3]])}
Pattern: Large integrators are dominating. Small/mid-tier need to team or niche down.

If you're in the {vertical_name} space:
→ Watch for teaming RFIs (primes are looking for subs)
→ Position on technical depth, not breadth
→ Target agencies with {vertical_name} modernization mandates

Full market pulse + recompete calendar: [LINK]

#GovCon #CloudComputing #Cybersecurity #FederalIT"""
        posts.append(("04_vertical_trend.txt", post4))

    # POST 5: Tactical lesson (protest/recompete angle)
    top_award = data['top_awards'][0]
    post5 = f"""⚡ Recompete Signal

{top_award['recipient_name']} just won a {fmt_dollar(top_award['award_amount'])} contract.

Contract ends: {top_award.get('end_date', 'TBD')}

Here's why this matters:
• Incumbents with contracts ending in 12-18 months start losing focus (they're distracted by the next recompete)
• If you're a competitor, NOW is the time to build relationships with the program office
• If you're the incumbent, you need a retention strategy yesterday

Tactical move:
Check USAspending for contracts ending in Q4 2026. Those recompetes are being scoped RIGHT NOW.

I publish a weekly recompete calendar with 100+ upcoming opportunities. Get it here: [LINK]

#GovCon #Recompete #Capture #BusinessDevelopment"""
    posts.append(("05_recompete_signal.txt", post5))

    return posts


# ============================================================================
# TWITTER THREADS (3x)
# ============================================================================
def generate_twitter_threads(data):
    """Generate 3 Twitter threads (7 tweets each)"""
    threads = []

    # THREAD 1: Weekly data dump
    thread1 = [
        f"🧵 This week in federal contracts: {data['count']:,} awards, {fmt_dollar(data['total_value'])} total",
        f"1/ Top agency: {data['top_agencies'][0][0]} — {fmt_dollar(data['top_agencies'][0][1])} awarded",
        f"2/ Biggest deal: {fmt_dollar(data['top_awards'][0]['award_amount'])} to {data['top_awards'][0]['recipient_name']}",
        f"3/ Top winner: {data['top_companies'][0][0]} — {fmt_dollar(data['top_companies'][0][1])} across multiple awards",
        f"4/ Market signal: Heavy spending this week = end-of-FY push. Expect more large awards in next 30 days.",
        f"5/ What to watch: Bridge extensions. If you see short-term mods, that's a signal the recompete is chaotic.",
        f"6/ Full breakdown with recompete alerts, protest lessons, and your weekly to-do list:",
        "7/ Subscribe: [LINK] — I track $50B+ in awards every week so you don't have to."
    ]
    threads.append(("twitter_thread_01.txt", "\n\n".join(thread1)))

    # THREAD 2: Hot take
    thread2 = [
        "🔥 Hot take: Most GovCon BD teams are tracking the wrong signals.",
        "1/ You're watching for new RFPs. But by the time an RFP drops, the decision is already made.",
        "2/ The REAL signals are option exercises and bridge extensions.",
        "3/ Option exercise = incumbent is performing well, program office is happy. Hard to unseat.",
        f"4/ Bridge extension = incumbent is struggling OR recompete is delayed. That's your window.",
        f"5/ This week: I saw {len([a for a in data['awards'] if 'bridge' in a.get('description', '').lower()])} bridge extensions. Those are live recompete opportunities.",
        "6/ If you're not tracking these, you're missing 80% of the addressable market.",
        "7/ I publish a weekly Bridge Watch report. Get it here: [LINK]"
    ]
    threads.append(("twitter_thread_02.txt", "\n\n".join(thread2)))

    # THREAD 3: Tactical lesson
    thread3 = [
        "💡 Lesson from this week: How to know if a contract is wired.",
        "1/ \"Wired\" = RFP is written for a specific vendor. You're just bid candy (there to make it look competitive).",
        "2/ Top 3 signals:",
        "3/ Signal #1: SOW uses vendor-specific jargon. Example: \"Must integrate with [Proprietary Tool]\" — that's not a requirement, it's a vendor lock-in.",
        "4/ Signal #2: Unrealistic timeline. 14-day response window on a $50M contract? They already know who they want.",
        "5/ Signal #3: Incumbent is named in the RFP. \"Current contractor performs XYZ...\" = they're writing the requirements around the incumbent.",
        "6/ If you see 2+ of these signals, don't bid. You'll waste 200 hours on a 1% win probability.",
        "7/ I score every major recompete on a 0-100 \"wired scale.\" Get this week's scores: [LINK]"
    ]
    threads.append(("twitter_thread_03.txt", "\n\n".join(thread3)))

    return threads


# ============================================================================
# REDDIT POST (1x)
# ============================================================================
def generate_reddit_post(data):
    """Generate 1 Reddit post for r/governmentcontracting"""
    top_agency = data['top_agencies'][0]

    post = f"""[Market Analysis] This Week's Federal Contract Awards — {data['count']:,} Contracts, {fmt_dollar(data['total_value'])}

Hey r/governmentcontracting,

I analyze federal contract data every week. Here's what stood out this week:

**Top Agency by Spend:**
- {top_agency[0]}: {fmt_dollar(top_agency[1])} ({top_agency[1] / data['total_value'] * 100:.0f}% of all awards this week)

**Largest Single Award:**
- {fmt_dollar(data['top_awards'][0]['award_amount'])} to {data['top_awards'][0]['recipient_name']} ({data['top_awards'][0]['awarding_agency']})
- Program: {data['top_awards'][0]['description'][:150]}...

**Top 5 Winners This Week:**
{''.join([f"{i+1}. {company}: {fmt_dollar(value)}" + chr(10) for i, (company, value) in enumerate(data['top_companies'][:5])])}

**What This Means:**
- {top_agency[0]} is moving fast — if you're pursuing their opportunities, expect compressed timelines
- Large integrators are dominating (see top 5) — small/mid-tier need strong teaming strategies
- Heavy option exercise activity = incumbents are performing well, hard to unseat on recompetes

**Recompete Watch:**
I track contracts ending in the next 12-18 months. {len([a for a in data['awards'] if a.get('end_date', '') > '2026' and a.get('end_date', '') < '2028'])} awards this week have end dates in 2027 — those recompetes are being scoped now.

**Questions I'm happy to answer:**
- How to evaluate if a recompete is winnable
- Which agencies have the best small business set-aside rates
- What "bridge extension" signals mean for competitors

Full breakdown (with protest lessons + weekly to-do list) in my newsletter: [LINK]

Happy to discuss any of these awards in comments.
"""
    return post


# ============================================================================
# SUBSTACK NOTES (5x)
# ============================================================================
def generate_substack_notes(data):
    """Generate 5 Substack Notes (500 char limit, engagement hooks)"""
    notes = []

    # NOTE 1: Data hook
    note1 = f"""📊 This week: {data['count']:,} federal contracts, {fmt_dollar(data['total_value'])} total.

Highest single award: {fmt_dollar(data['top_awards'][0]['award_amount'])} to {data['top_awards'][0]['recipient_name']}.

{data['top_agencies'][0][0]} awarded {fmt_dollar(data['top_agencies'][0][1])} — {data['top_agencies'][0][1] / data['total_value'] * 100:.0f}% of all spend this week.

Full breakdown with recompete alerts: [LINK]

#GovCon"""
    notes.append(("note_01_data_hook.txt", note1))

    # NOTE 2: Hot take
    note2 = f"""🔥 Hot take: If you're not tracking option exercises + bridge extensions, you're missing 80% of the market.

This week: {len([a for a in data['awards'] if 'option' in a.get('description', '').lower()])} option exercises = incumbents are safe.

Want the list of vulnerable recompetes? Subscribe to my weekly intel: [LINK]"""
    notes.append(("note_02_hot_take.txt", note2))

    # NOTE 3: Tactical lesson
    note3 = f"""💡 How to know if a contract is wired:

✓ SOW uses vendor-specific jargon
✓ Unrealistic response timeline
✓ Incumbent named in RFP

See 2+ signals? Don't bid. You'll waste 200 hours on a <1% win probability.

I score every major recompete. This week's \"wired\" analysis: [LINK]"""
    notes.append(("note_03_lesson.txt", note3))

    # NOTE 4: Market signal
    note4 = f"""🚨 {data['top_agencies'][0][0]} just awarded {fmt_dollar(data['top_agencies'][0][1])} this week.

Why it matters: End-of-FY push. Decision timelines are compressed. If you're in their pipeline, move NOW.

Weekly market pulse + recompete calendar: [LINK]"""
    notes.append(("note_04_signal.txt", note4))

    # NOTE 5: Question hook
    note5 = f"""❓ What's the #1 signal that a recompete is winnable?

(Hint: It's not the RFP. It's what happens 6 months before the RFP drops.)

I break this down in this week's GovCon intel: [LINK]

What do you think it is? Drop your guess below. 👇"""
    notes.append(("note_05_question.txt", note5))

    return notes


# ============================================================================
# MAIN
# ============================================================================
def main():
    print("Loading data...")
    data = load_data()

    print(f"Generating content from {data['count']:,} awards ({fmt_dollar(data['total_value'])})...")

    # Generate all content types
    linkedin_posts = generate_linkedin_posts(data)
    twitter_threads = generate_twitter_threads(data)
    reddit_post = generate_reddit_post(data)
    substack_notes = generate_substack_notes(data)

    # Write to files
    for filename, content in linkedin_posts:
        path = os.path.join(OUTPUT_DIR, "linkedin_" + filename)
        with open(path, "w") as f:
            f.write(content)
        print(f"✓ {path}")

    for filename, content in twitter_threads:
        path = os.path.join(OUTPUT_DIR, filename)
        with open(path, "w") as f:
            f.write(content)
        print(f"✓ {path}")

    reddit_path = os.path.join(OUTPUT_DIR, "reddit_post.txt")
    with open(reddit_path, "w") as f:
        f.write(reddit_post)
    print(f"✓ {reddit_path}")

    for filename, content in substack_notes:
        path = os.path.join(OUTPUT_DIR, "substack_" + filename)
        with open(path, "w") as f:
            f.write(content)
        print(f"✓ {path}")

    print(f"\n✅ Generated {len(linkedin_posts)} LinkedIn posts, {len(twitter_threads)} Twitter threads, 1 Reddit post, {len(substack_notes)} Substack Notes")
    print(f"📁 All files saved to: {OUTPUT_DIR}")
    print("\n📋 Next steps:")
    print("1. Review generated content (edit for voice/accuracy)")
    print("2. Replace [LINK] with actual newsletter URL")
    print("3. Copy-paste to respective platforms")
    print("4. Post LinkedIn on Mon/Thu, Twitter on Tue/Wed, Reddit on Wed, Notes daily")


if __name__ == "__main__":
    main()
