#!/usr/bin/env python3
"""
GovCon Intelligence -- Deep Analytical Insights Generator
Reads corrected_all.json and produces sharp, opinionated, actionable analysis
that goes far beyond listing transactions.

Usage:
    python3 generate_insights.py                          # today's date
    python3 generate_insights.py --date 2026-03-18        # specific date
    python3 generate_insights.py --input data/custom.json # custom input
"""

import argparse
import json
import os
import sys
from collections import defaultdict
from datetime import datetime, timedelta

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(SCRIPT_DIR, "data")
OUTPUT_DIR = os.path.join(SCRIPT_DIR, "output")

# NAICS code -> human-readable market segment
NAICS_SEGMENTS = {
    "541512": "IT Systems Design",
    "541511": "Custom Software",
    "541519": "IT Consulting",
    "541330": "Engineering Services",
    "541611": "Management Consulting",
    "541715": "R&D / Defense Science",
    "518210": "Cloud / Data Hosting",
    "511210": "Software Products",
    "334511": "Defense Electronics / UAS",
    "237990": "Heavy Construction",
}

# Competitive landscape intelligence -- known major primes and their strengths
CONTRACTOR_INTEL = {
    "Booz Allen Hamilton": {"tier": "prime", "strengths": ["analytics", "cyber", "defense consulting"], "notable": "Dominant in DoD advisory. Recently aggressive on AI/ML."},
    "Leidos": {"tier": "prime", "strengths": ["IT modernization", "defense", "health IT"], "notable": "Largest pure-play federal IT. NGEN is their anchor."},
    "SAIC": {"tier": "prime", "strengths": ["defense engineering", "IT services", "space"], "notable": "Strong DISA presence. DES contract is a cash machine."},
    "General Dynamics IT": {"tier": "prime", "strengths": ["enterprise IT", "cloud", "Army"], "notable": "GDIT rebranded after CSRA acquisition. Deep Army roots."},
    "Accenture Federal Services": {"tier": "prime", "strengths": ["cloud", "digital transformation", "healthcare IT"], "notable": "Fastest-growing federal practice. CMS is their flagship."},
    "ManTech International": {"tier": "prime", "strengths": ["cyber", "intel community", "CMMC"], "notable": "Acquired by Carlyle. Doubling down on cyber assessments."},
    "Peraton": {"tier": "prime", "strengths": ["intel", "space", "homeland security"], "notable": "Formed from Perspecta + Northrop Grumman IT. IC is their bread and butter."},
    "CACI International": {"tier": "prime", "strengths": ["intel", "IT modernization", "electronic warfare"], "notable": "Strong SIGINT and DHS portfolio."},
    "CGI Federal": {"tier": "prime", "strengths": ["financial systems", "health IT"], "notable": "Canadian parent. Quiet but steady grower in civilian."},
    "Deloitte Consulting": {"tier": "advisory", "strengths": ["management consulting", "transformation", "shared services"], "notable": "Largest advisory presence in federal. Premium pricing."},
    "Palantir Technologies": {"tier": "disruptor", "strengths": ["data analytics", "AI/ML", "intel"], "notable": "Commercial software model. Aggressive sole-source strategy."},
    "Raytheon Technologies": {"tier": "defense_prime", "strengths": ["weapons", "space", "comms"], "notable": "RTX merger still integrating. Strong classified portfolio."},
    "Scale AI": {"tier": "disruptor", "strengths": ["AI training data", "ML ops"], "notable": "Silicon Valley entrant. NGA award is a landmark."},
    "Anduril Industries": {"tier": "disruptor", "strengths": ["autonomous systems", "defense tech"], "notable": "Palmer Luckey's defense startup. Growing fast in counter-UAS."},
    "CrowdStrike Federal": {"tier": "specialist", "strengths": ["endpoint security", "threat intel"], "notable": "Commercial cyber leader expanding federal footprint post-SolarWinds."},
    "Maximus": {"tier": "mid", "strengths": ["citizen services", "health IT", "contact centers"], "notable": "Dominates citizen-facing federal services."},
    "Parsons Corporation": {"tier": "mid", "strengths": ["construction", "infrastructure", "defense"], "notable": "Strong MILCON and infrastructure modernization."},
    "HII Mission Technologies": {"tier": "mid", "strengths": ["IT services", "fleet sustainment", "Navy"], "notable": "Huntington Ingalls' tech arm. Deep Navy relationships."},
    "Amazon Web Services (AWS)": {"tier": "hyperscaler", "strengths": ["cloud infrastructure", "GovCloud", "IC"], "notable": "IC cloud incumbent. C2E contract is the prize."},
}

# Small/mid firm size indicators
SMALL_FIRM_INDICATORS = ["small", "8(a)", "SDVOSB", "HUBZone", "WOSB", "SBA", "EDWOSB"]

# ---------------------------------------------------------------------------
# Data loading
# ---------------------------------------------------------------------------

def load_data(input_path):
    """Load and validate the corrected JSON data."""
    if not os.path.exists(input_path):
        print(f"ERROR: Data file not found: {input_path}", file=sys.stderr)
        sys.exit(1)
    with open(input_path) as f:
        data = json.load(f)
    return data


# ---------------------------------------------------------------------------
# Analysis engines
# ---------------------------------------------------------------------------

def fmt_dollars(amount):
    """Format dollar amount with appropriate scale."""
    if amount is None:
        return "N/A"
    raw = abs(amount)
    sign = "-" if amount < 0 else ""
    if raw >= 1_000_000_000:
        return f"{sign}${raw / 1_000_000_000:.1f}B"
    elif raw >= 1_000_000:
        return f"{sign}${raw / 1_000_000:.0f}M"
    elif raw >= 1_000:
        return f"{sign}${raw / 1_000:.0f}K"
    else:
        return f"{sign}${raw:,.0f}"


def analyze_recompetes(data):
    """Generate 'So What' analysis for each recompete alert."""
    sections = data.get("sections", {})
    recompetes = sections.get("recompete_alerts", {}).get("items", [])
    if not recompetes:
        return ""

    lines = []
    lines.append("## 1. Recompete \"So What\" Analysis")
    lines.append("")
    lines.append("These aren't just expiring contracts -- they're specific windows of opportunity")
    lines.append("(or threat, if you're the incumbent). Here's what each one actually means for you.")
    lines.append("")

    for rc in recompetes:
        name = rc.get("contract_name", "Unknown")
        agency = rc.get("agency", "Unknown")
        incumbent = rc.get("incumbent", "Unknown")
        value = rc.get("current_value", "Unknown")
        value_raw = rc.get("current_value_raw", 0)
        days = rc.get("days_remaining", 0)
        naics = rc.get("naics", "")
        set_aside = rc.get("set_aside", "Full & Open")
        sol_status = rc.get("solicitation_status", "Unknown")
        detail = rc.get("notable_detail", "")
        urgency = rc.get("urgency", "medium")

        lines.append(f"### {name}")
        lines.append(f"**{agency}** | Incumbent: {incumbent} | Current value: {value} | {days} days to expiration")
        lines.append("")

        # Incumbent advantage assessment
        if days < 120:
            timeline_pressure = "HIGH -- less than 4 months out"
            if "Draft RFP" in sol_status or "Expected" in sol_status:
                timeline_note = f"The solicitation ({sol_status}) hasn't even dropped yet with only {days} days left. This screams bridge contract or sole-source extension for the incumbent. If you're NOT the incumbent, your window to influence requirements is nearly closed."
            else:
                timeline_note = f"At {days} days with '{sol_status}', the acquisition timeline is tight. Expect compressed evaluation periods."
        elif days < 180:
            timeline_pressure = "MEDIUM -- 4-6 months"
            timeline_note = f"Still time to position, but you need to be engaging the program office NOW, not when the RFP drops."
        else:
            timeline_pressure = "STANDARD"
            timeline_note = "Healthy timeline for new entrants to shape requirements through white papers and industry days."

        lines.append(f"**Timeline pressure:** {timeline_pressure}")
        lines.append(f"{timeline_note}")
        lines.append("")

        # Who should pursue
        lines.append("**Who should pursue this:**")
        if set_aside and "Small" in set_aside:
            lines.append(f"- This is a **small business set-aside** ({set_aside}). Primes are locked out of competing directly but will be looking for teaming partners.")
            lines.append(f"- If you're a small business with NAICS {naics} and relevant past performance, this is exactly your lane.")
            lines.append(f"- If you're a large firm, identify your SB teaming partner NOW. The smart play is to provide sub-tier technical depth while the SB holds prime.")
        else:
            if value_raw > 200_000_000:
                lines.append(f"- At {value}, this is **prime-tier only**. You need $50M+ in single-award past performance to be credible.")
                lines.append(f"- Mid-tier firms: your play is as a key subcontractor. Start conversations with likely primes this week.")
            elif value_raw > 50_000_000:
                lines.append(f"- Sweet spot for **large mid-tier firms** ({value}). Past performance in {naics} at the $20M+ range is your ticket.")
                lines.append(f"- Primes will compete but may not bring their A-team. This is where strong technical proposals win.")
            else:
                lines.append(f"- At {value}, accessible to mid-tier and strong small businesses with relevant past performance.")

        lines.append("")

        # Incumbent advantage
        lines.append("**Incumbent advantage assessment:**")
        if "sole" in sol_status.lower() or "bridge" in detail.lower() or "extension" in detail.lower():
            lines.append(f"- **STRONG.** {incumbent} is almost certainly getting a bridge or extension. Breaking in requires a protest-ready proposal or a major incumbent stumble.")
        elif days < 120 and ("Draft" in sol_status or "Expected" in sol_status):
            lines.append(f"- **STRONG.** The timeline math favors {incumbent}. Late RFP + short evaluation = advantage to the team that's already running the program.")
        elif "restructur" in detail.lower() or "break" in detail.lower() or "multiple" in detail.lower():
            lines.append(f"- **WEAKENED.** The agency is signaling they want change ('{detail}'). This is the best possible scenario for challengers.")
        else:
            lines.append(f"- **MODERATE.** {incumbent} has the relationship advantage but the agency hasn't signaled a lock-in. Competitive proposals will get a fair look.")

        lines.append("")

        # Specific action
        lines.append("**What you should do this week:**")
        if days < 120:
            lines.append(f"- If you're targeting this: submit a capabilities brief to the contracting officer by Friday. Search SAM.gov for the solicitation notice.")
            lines.append(f"- Set a SAM.gov alert for NAICS {naics} + \"{agency}\" immediately.")
        else:
            lines.append(f"- Request a meeting with the {agency} program office to discuss upcoming requirements.")
            lines.append(f"- Set a SAM.gov alert for NAICS {naics} + \"{agency}\".")

        if "multiple" in detail.lower() or "task" in detail.lower():
            lines.append(f"- Multiple-award signal detected: start identifying teaming partners for complementary task areas.")

        lines.append("")
        lines.append("---")
        lines.append("")

    return "\n".join(lines)


def analyze_agency_strategies(data):
    """Detect agency-level strategy signals from the week's activity."""
    sections = data.get("sections", {})
    market = data.get("market_pulse", {})

    # Collect all transactions by agency, normalizing names to merge duplicates
    # E.g., "DISA" and "Defense Information Systems Agency (DISA)" -> merge under longer name
    raw_agency_actions = defaultdict(list)

    for section_key in ["new_awards", "option_exercises", "funding_actions"]:
        section = sections.get(section_key, {})
        for item in section.get("items", []):
            agency = item.get("agency", "Unknown")
            raw_agency_actions[agency].append({
                "section": section_key,
                "item": item,
            })

    # Also pull recompetes as signals
    for item in sections.get("recompete_alerts", {}).get("items", []):
        agency = item.get("agency", "Unknown")
        raw_agency_actions[agency].append({
            "section": "recompete",
            "item": item,
        })

    # Merge agencies with overlapping names (short acronym absorbed into full name)
    agency_actions = defaultdict(list)
    agency_names = list(raw_agency_actions.keys())
    merged_to = {}
    for name in sorted(agency_names, key=len, reverse=True):  # longest first
        # Check if this name is a substring of an already-seen canonical name
        canonical = None
        for existing in merged_to.values():
            if name.lower() in existing.lower() or existing.lower() in name.lower():
                canonical = existing
                break
        if canonical is None:
            # Check against other raw names
            for other in agency_names:
                if other != name and len(other) > len(name) and name.lower() in other.lower():
                    canonical = other
                    break
        if canonical and canonical != name:
            merged_to[name] = canonical
        else:
            merged_to[name] = name

    for name, actions in raw_agency_actions.items():
        canonical = merged_to.get(name, name)
        agency_actions[canonical].extend(actions)

    lines = []
    lines.append("## 2. Agency Strategy Signals")
    lines.append("")
    lines.append("What this week's spending tells us about where each agency is headed.")
    lines.append("These signals compound over time -- track them weekly to spot shifts before your competitors do.")
    lines.append("")

    # Sort agencies by total dollar activity
    agency_totals = {}
    for agency, actions in agency_actions.items():
        total = 0
        for a in actions:
            item = a["item"]
            for key in ["award_value_raw", "option_value_raw", "modification_value_raw", "current_value_raw"]:
                if key in item and item[key]:
                    total += abs(item[key])
                    break
        agency_totals[agency] = total

    for agency in sorted(agency_totals, key=agency_totals.get, reverse=True):
        actions = agency_actions[agency]
        total = agency_totals[agency]

        if total < 10_000_000 and len(actions) < 2:
            continue  # Skip minor single-action agencies

        lines.append(f"### {agency}")

        # Classify the types of actions
        new_awards = [a for a in actions if a["section"] == "new_awards"]
        options = [a for a in actions if a["section"] == "option_exercises"]
        funding = [a for a in actions if a["section"] == "funding_actions"]
        recompetes = [a for a in actions if a["section"] == "recompete"]

        # Generate strategy signal
        signals = []

        if len(new_awards) >= 2:
            vendors = [a["item"].get("awardee", "Unknown") for a in new_awards]
            unique_vendors = set(vendors)
            if len(unique_vendors) == len(vendors):
                signals.append(f"Spreading awards across {len(unique_vendors)} different vendors ({', '.join(unique_vendors)}). **Signal: diversification strategy.** They're reducing single-vendor risk. Good news for challengers.")
            else:
                signals.append(f"Concentrating awards. **Signal: trusted vendor consolidation.** Harder to break in, but sub-contracting opportunities are rich.")

        if new_awards and recompetes:
            signals.append(f"Simultaneously awarding new work and recompeting legacy contracts. **Signal: active portfolio reshaping.** The agency is investing, not just maintaining. Get in front of the program office now.")

        if options and not new_awards:
            signals.append(f"Only exercising options this week, no new competitions. **Signal: steady-state operations.** The agency is satisfied with current vendors or too busy to run new acquisitions. If you're NOT an incumbent here, focus your BD elsewhere for now.")

        if funding:
            ceiling_increases = [a for a in funding if a["item"].get("action_type") == "Ceiling Increase"]
            if ceiling_increases:
                total_increase = sum(a["item"].get("modification_value_raw", 0) for a in ceiling_increases)
                signals.append(f"Ceiling increases totaling {fmt_dollars(total_increase)}. **Signal: scope is growing faster than planned.** The programs they bet on are expanding. If you're positioned on these vehicles, pursue task orders aggressively.")

        if recompetes:
            for r in recompetes:
                detail = r["item"].get("notable_detail", "")
                if "restructur" in detail.lower() or "multiple" in detail.lower() or "break" in detail.lower():
                    signals.append(f"Recompete restructuring detected ('{r['item'].get('contract_name', '')}'). **Signal: the agency is unhappy with the current approach.** Challengers take note -- this is your opening.")

        if not signals:
            signals.append(f"Activity totaling {fmt_dollars(total)} this week. Monitoring for trend development.")

        for s in signals:
            lines.append(f"- {s}")

        lines.append("")

    # Market-level signal from top agencies
    top_agencies = market.get("top_agencies_by_spend", [])
    if top_agencies:
        lines.append("### Market-Level Read")
        total_market = market.get("total_obligations_week", "Unknown")
        yoy = market.get("yoy_change", "Unknown")
        lines.append(f"Total federal obligations this week: **{total_market}** ({yoy} YoY)")
        lines.append("")
        top3 = ", ".join(f"{a['agency']} ({a['amount']})" for a in top_agencies[:3])
        lines.append(f"Top spenders: {top3}")
        lines.append("")

        trending = market.get("trending_naics", [])
        if trending:
            top_naics = trending[0]
            lines.append(f"Hottest NAICS: **{top_naics['code']} - {top_naics['description']}** ({top_naics['change']} WoW). "
                        f"If this isn't in your NAICS list on SAM.gov, add it today.")
        lines.append("")

    lines.append("**What you should do:** Cross-reference your pipeline against these agency signals. If you're investing BD resources in an agency showing steady-state signals, reallocate to agencies in active-reshaping mode.")
    lines.append("")

    return "\n".join(lines)


def analyze_contractor_power_rankings(data):
    """Build competitive intelligence on who's winning and losing."""
    sections = data.get("sections", {})

    contractor_scores = defaultdict(lambda: {
        "wins": [], "options": [], "funding_up": [], "funding_down": [],
        "total_new": 0, "total_options": 0, "total_funding": 0,
    })

    # New awards
    for item in sections.get("new_awards", {}).get("items", []):
        name = item.get("awardee", "Unknown")
        val = item.get("award_value_raw", 0)
        contractor_scores[name]["wins"].append(item)
        contractor_scores[name]["total_new"] += val

    # Options
    for item in sections.get("option_exercises", {}).get("items", []):
        name = item.get("contractor", "Unknown")
        val = item.get("option_value_raw", 0)
        contractor_scores[name]["options"].append(item)
        contractor_scores[name]["total_options"] += val

    # Funding actions
    for item in sections.get("funding_actions", {}).get("items", []):
        name = item.get("contractor", "Unknown")
        val = item.get("modification_value_raw", 0)
        if val > 0:
            contractor_scores[name]["funding_up"].append(item)
            contractor_scores[name]["total_funding"] += val
        else:
            contractor_scores[name]["funding_down"].append(item)
            contractor_scores[name]["total_funding"] += val

    lines = []
    lines.append("## 3. Contractor Power Rankings")
    lines.append("")
    lines.append("Who won this week, who's holding steady, and who's losing ground.")
    lines.append("Use this to track competitive positioning and identify teaming targets.")
    lines.append("")

    # Sort by total positive activity
    ranked = sorted(
        contractor_scores.items(),
        key=lambda x: x[1]["total_new"] + x[1]["total_options"] + max(x[1]["total_funding"], 0),
        reverse=True,
    )

    # Winners section
    lines.append("### Winners This Week")
    lines.append("")
    lines.append("| Rank | Contractor | New Awards | Options Exercised | Funding Actions | Total Activity |")
    lines.append("|------|-----------|------------|-------------------|-----------------|----------------|")

    for i, (name, scores) in enumerate(ranked[:10], 1):
        total = scores["total_new"] + scores["total_options"] + scores["total_funding"]
        new_str = fmt_dollars(scores["total_new"]) if scores["total_new"] else "--"
        opt_str = fmt_dollars(scores["total_options"]) if scores["total_options"] else "--"
        fund_str = fmt_dollars(scores["total_funding"]) if scores["total_funding"] else "--"
        lines.append(f"| {i} | **{name}** | {new_str} | {opt_str} | {fund_str} | {fmt_dollars(total)} |")

    lines.append("")

    # Color commentary on top performers
    lines.append("### Analysis")
    lines.append("")

    for i, (name, scores) in enumerate(ranked[:5], 1):
        intel = CONTRACTOR_INTEL.get(name, {})
        tier = intel.get("tier", "unknown")
        notable = intel.get("notable", "")

        commentary = []
        if scores["wins"]:
            win_agencies = [w.get("agency", "Unknown") for w in scores["wins"]]
            commentary.append(f"Won {len(scores['wins'])} new award(s) at {', '.join(win_agencies)}")
        if scores["options"]:
            commentary.append(f"got {len(scores['options'])} option(s) exercised (customers are happy)")
        if scores["funding_up"]:
            commentary.append(f"received {fmt_dollars(sum(f.get('modification_value_raw', 0) for f in scores['funding_up']))} in ceiling increases")

        lines.append(f"**#{i} {name}** ({tier}): {'; '.join(commentary)}.")
        if notable:
            lines.append(f"  - Background: {notable}")

        # Competitive implication
        if scores["total_new"] > 500_000_000:
            lines.append(f"  - **Implication:** {name} is on a war path. If they're in your competitive space, you need to differentiate on something other than price.")
        elif scores["total_new"] > 100_000_000:
            lines.append(f"  - **Implication:** Solid quarter for {name}. They're building past performance that makes them harder to beat in future competitions.")
        if scores["options"] and not scores["wins"]:
            lines.append(f"  - **Implication:** Riding incumbency. No new wins this week -- watch for complacency if this pattern continues.")

        lines.append("")

    # Losers / de-obligations
    losers = [(name, scores) for name, scores in contractor_scores.items()
              if scores["total_funding"] < 0]
    if losers:
        lines.append("### Watch List (De-obligations / Reductions)")
        lines.append("")
        for name, scores in losers:
            lines.append(f"- **{name}**: {fmt_dollars(scores['total_funding'])} in de-obligations. ")
            for f in scores["funding_down"]:
                detail = f.get("notable_detail", "")
                if detail:
                    lines.append(f"  Reason: {detail}")
            intel = CONTRACTOR_INTEL.get(name, {})
            if intel:
                lines.append(f"  Background: {intel.get('notable', 'N/A')}")
        lines.append("")
        lines.append("De-obligations are the canary in the coal mine. They signal program trouble, ")
        lines.append("scope reduction, or agency dissatisfaction. If you compete against these firms, ")
        lines.append("their weakened position on these programs is your opening.")
        lines.append("")

    lines.append("**What you should do:** If a top-ranked contractor is winning in your space, study their winning proposals (FOIA the evaluation documents). If a competitor just got de-obligated, reach out to that agency -- they may be looking for alternatives.")
    lines.append("")

    return "\n".join(lines)


def analyze_small_business(data):
    """Spotlight small business activity."""
    sections = data.get("sections", {})
    lines = []
    lines.append("## 4. Small Business Spotlight")
    lines.append("")
    lines.append("If you're a small or mid-size firm, this section is specifically for you.")
    lines.append("These are proof points that firms your size are winning real federal work.")
    lines.append("")

    sb_wins = []
    sb_recompetes = []

    # Find set-aside awards
    for item in sections.get("new_awards", {}).get("items", []):
        set_aside = item.get("set_aside", "")
        if set_aside and any(ind in set_aside for ind in SMALL_FIRM_INDICATORS):
            sb_wins.append(item)

    # Find set-aside recompetes
    for item in sections.get("recompete_alerts", {}).get("items", []):
        set_aside = item.get("set_aside", "")
        if set_aside and any(ind in set_aside for ind in SMALL_FIRM_INDICATORS):
            sb_recompetes.append(item)

    if sb_wins:
        lines.append("### Small Business Wins This Week")
        lines.append("")
        for item in sb_wins:
            name = item.get("awardee", "Unknown")
            agency = item.get("agency", "Unknown")
            value = item.get("award_value", "Unknown")
            desc = item.get("contract_name", item.get("description", "Unknown"))
            set_aside = item.get("set_aside", "")
            naics = item.get("naics", "")

            lines.append(f"**{name}** won {value} at {agency}")
            lines.append(f"- Contract: {desc}")
            lines.append(f"- Set-aside: {set_aside} | NAICS: {naics}")
            lines.append(f"- **Why this matters:** Every small business win like this proves the set-aside program works. If you hold the same certifications and NAICS codes, this agency is actively buying from firms like yours.")
            lines.append("")
    else:
        lines.append("No small business set-aside awards in this week's top transactions. ")
        lines.append("But that doesn't mean the opportunity isn't there:")
        lines.append("")

    if sb_recompetes:
        lines.append("### Small Business Recompetes Coming Up")
        lines.append("")
        for item in sb_recompetes:
            name = item.get("contract_name", "Unknown")
            agency = item.get("agency", "Unknown")
            value = item.get("current_value", "Unknown")
            days = item.get("days_remaining", 0)
            naics = item.get("naics", "")

            lines.append(f"**{name}** ({agency}) -- {value}, {days} days out")
            lines.append(f"- NAICS {naics} -- set-aside recompete")
            lines.append(f"- **Action:** If you have past performance in this NAICS and the right certifications, submit a capabilities statement to the PCO this week. Don't wait for the RFP.")
            lines.append("")

    # General small business intelligence from the week
    lines.append("### Subcontracting Opportunities on Large Awards")
    lines.append("")
    lines.append("Every large prime award this week comes with small business subcontracting requirements. ")
    lines.append("Here's where to position:")
    lines.append("")

    for item in sections.get("new_awards", {}).get("items", []):
        value_raw = item.get("award_value_raw", 0)
        if value_raw >= 100_000_000:
            awardee = item.get("awardee", "Unknown")
            agency = item.get("agency", "Unknown")
            contract = item.get("contract_name", "Unknown")
            value = item.get("award_value", "Unknown")

            intel = CONTRACTOR_INTEL.get(awardee, {})
            strengths = intel.get("strengths", [])

            lines.append(f"- **{contract}** ({agency}, {value} to {awardee})")
            if strengths:
                complement = "cyber, cloud, or data" if "IT" in " ".join(strengths) else "IT modernization, analytics, or software development"
                lines.append(f"  {awardee}'s strengths are in {', '.join(strengths)}. They'll need small business partners for {complement}.")
            lines.append(f"  Contact {awardee}'s small business liaison office and reference this specific contract.")
            lines.append("")

    lines.append("**What you should do:** Pick ONE large award from above. Find the prime's small business liaison (usually listed on their website). Send a 1-page capabilities brief referencing the specific contract name and your relevant past performance. Do this by Friday.")
    lines.append("")

    return "\n".join(lines)


def analyze_trends(data):
    """Generate forward-looking trend analysis."""
    sections = data.get("sections", {})
    market = data.get("market_pulse", {})
    notable = data.get("notable", {})

    lines = []
    lines.append("## 5. Trend Analysis & Forward Look")
    lines.append("")

    # Pull key stats
    headline = notable.get("headline", "")
    key_stat = notable.get("key_stat", "")
    key_label = notable.get("key_stat_label", "")

    if headline:
        lines.append(f"### Headline: {headline}")
        lines.append("")

    # Cyber trend
    trending = market.get("trending_naics", [])
    cyber_naics = [t for t in trending if "541512" in t.get("code", "") or "541519" in t.get("code", "")]
    if cyber_naics or "cyber" in headline.lower():
        lines.append("### Cybersecurity Dominance Continues")
        lines.append("")
        lines.append(f"The numbers don't lie: cybersecurity and IT systems design are the hottest NAICS codes this week. "
                     f"{'NAICS ' + cyber_naics[0]['code'] + ' is up ' + cyber_naics[0]['change'] + ' week-over-week. ' if cyber_naics else ''}"
                     f"This isn't a blip -- it's a structural shift driven by:")
        lines.append("- Zero trust mandates hitting compliance deadlines (OMB M-22-09 enforcement)")
        lines.append("- CMMC 2.0 driving assessment demand across the defense industrial base")
        lines.append("- Post-SolarWinds/MOVEit security investment still accelerating")
        lines.append("")
        lines.append("**Forward look:** Expect cybersecurity spending to remain elevated through FY26 Q3. "
                     "Agencies are front-loading cyber budgets before potential CR disruptions in Q4. "
                     "If you're a cyber firm, your pipeline should be at maximum capacity right now.")
        lines.append("")

    # Advanced Technology trend
    ai_awards = []
    for item in sections.get("new_awards", {}).get("items", []):
        desc = (item.get("contract_name", "") + " " + item.get("notable_detail", "")).lower()
        if any(kw in desc for kw in ["ai", "ml", "machine learning", "artificial intelligence", "autonomous"]):
            ai_awards.append(item)

    if ai_awards:
        total_ai = sum(a.get("award_value_raw", 0) for a in ai_awards)
        lines.append("### Advanced Technology Spending: From Pilots to Production")
        lines.append("")
        lines.append(f"This week saw {fmt_dollars(total_ai)} in advanced technology awards across {len(ai_awards)} contracts. "
                     f"Notable: these aren't study contracts or research grants. They're production deployments.")
        lines.append("")
        for a in ai_awards:
            lines.append(f"- {a.get('contract_name', 'Unknown')}: {a.get('award_value', 'N/A')} to {a.get('awardee', 'Unknown')}")
        lines.append("")
        lines.append("**Forward look:** The federal advanced technology market is bifurcating. Large platforms (Palantir, Scale AI) "
                     "are winning the data infrastructure layer. Traditional primes are winning the integration layer. "
                     "Small firms can win in niche verticals (healthcare analytics, environmental modeling, financial fraud detection) "
                     "where domain expertise beats platform scale.")
        lines.append("")

    # Cloud migration trend
    cloud_signals = []
    for section_key in ["new_awards", "funding_actions"]:
        for item in sections.get(section_key, {}).get("items", []):
            desc = json.dumps(item).lower()
            if any(kw in desc for kw in ["cloud", "migration", "modernization", "saas", "paas"]):
                cloud_signals.append(item)

    if cloud_signals:
        lines.append("### Cloud Migration: The Modernization Tax")
        lines.append("")
        lines.append(f"At least {len(cloud_signals)} actions this week involved cloud migration or modernization. "
                     "Federal agencies are deep in the 'modernization tax' phase -- spending heavily to move off legacy systems "
                     "with limited new capability until migration completes.")
        lines.append("")
        lines.append("**Forward look:** The agencies that started cloud migrations in FY23-24 are now hitting Option Year 2-3. "
                     "Watch for 'post-migration optimization' task orders -- smaller, specialized work that favors nimble firms "
                     "over the primes who ran the initial lift-and-shift.")
        lines.append("")

    # FY timing analysis
    report_date_str = data.get("report_date", "")
    if report_date_str:
        try:
            report_date = datetime.strptime(report_date_str, "%Y-%m-%d")
            month = report_date.month
            if month >= 10:
                fy_quarter = "Q1"
                fy = report_date.year + 1
            elif month >= 7:
                fy_quarter = "Q4"
                fy = report_date.year
            elif month >= 4:
                fy_quarter = "Q3"
                fy = report_date.year
            else:
                fy_quarter = "Q2"
                fy = report_date.year

            lines.append(f"### Fiscal Calendar Context: FY{fy} {fy_quarter}")
            lines.append("")

            if fy_quarter == "Q2":
                lines.append("We're in the **sweet spot of the fiscal year**. Q2 is when agencies have confirmed budgets, "
                            "contracting officers are fresh off Q1 closeout, and there's enough runway to run full competitions. "
                            "The spending you see this week is intentional and strategic -- not year-end panic buying.")
                lines.append("")
                lines.append("**What this means for your pipeline:** Proposals submitted now will be evaluated before the Q3 "
                            "summer slowdown. If you have anything ready to bid, submit it. Don't wait for 'perfect.'")
            elif fy_quarter == "Q3":
                lines.append("Summer slowdown is approaching, but the smart money is positioning for Q4 year-end spending. "
                            "Capture managers should be finalizing teaming agreements and past performance packages now.")
            elif fy_quarter == "Q4":
                lines.append("**Year-end spending surge.** Agencies are burning through remaining budgets. "
                            "Expect a flood of small awards, BPA calls, and micro-purchases. This is the best quarter for small firms.")
            else:
                lines.append("Q1 -- new fiscal year, fresh budgets, but many agencies are operating under CR. "
                            "Watch for which agencies got full-year appropriations (they'll spend freely) vs. those on CR (maintenance mode).")
            lines.append("")
        except ValueError:
            pass

    lines.append("**What you should do:** Update your 12-month pipeline forecast with these trend signals. If more than 40% of your pipeline is in a single NAICS code, diversify. The federal market rewards firms that can pivot across adjacent domains.")
    lines.append("")

    return "\n".join(lines)


def generate_action_items(data):
    """Generate the master action list -- specific to THIS week's data."""
    sections = data.get("sections", {})

    lines = []
    lines.append("## 6. This Week's Action Items")
    lines.append("")
    lines.append("Not generic advice. These are specific actions driven by this week's data.")
    lines.append("Prioritized by time-sensitivity.")
    lines.append("")

    actions = []

    # Recompete-driven actions
    recompetes = sections.get("recompete_alerts", {}).get("items", [])
    for rc in recompetes:
        days = rc.get("days_remaining", 999)
        if days < 120:
            actions.append({
                "priority": "URGENT",
                "deadline": f"{days} days",
                "action": f"**{rc.get('contract_name', 'Unknown')}** recompete at {rc.get('agency', 'Unknown')}: "
                          f"Submit capabilities brief to the contracting office. NAICS {rc.get('naics', 'Unknown')}. "
                          f"Current value {rc.get('current_value', 'Unknown')}. "
                          f"Set SAM.gov alert for this solicitation TODAY.",
            })
        elif days < 180:
            actions.append({
                "priority": "THIS WEEK",
                "deadline": f"{days} days",
                "action": f"**{rc.get('contract_name', 'Unknown')}** at {rc.get('agency', 'Unknown')}: "
                          f"Request industry day or pre-solicitation meeting. "
                          f"Start teaming discussions for NAICS {rc.get('naics', 'Unknown')} work.",
            })

    # Award-driven actions (teaming with winners, learning from losses)
    for item in sections.get("new_awards", {}).get("items", []):
        competitors = item.get("competitors_known", [])
        if competitors:
            losers_str = ", ".join(competitors)
            actions.append({
                "priority": "THIS WEEK",
                "deadline": "7 days",
                "action": f"**{item.get('contract_name', 'Unknown')}** won by {item.get('awardee', 'Unknown')}: "
                          f"FOIA the evaluation documents to understand scoring. "
                          f"Losing bidders ({losers_str}) may be looking for teaming partners on the next opportunity.",
            })

    # Option exercise actions
    for item in sections.get("option_exercises", {}).get("items", []):
        option_year = item.get("option_year", "")
        if "4 of" in option_year or "5 of" in option_year or "final" in option_year.lower():
            actions.append({
                "priority": "THIS MONTH",
                "deadline": "30 days",
                "action": f"**{item.get('contract_name', 'Unknown')}** -- final option year exercised for {item.get('contractor', 'Unknown')}. "
                          f"This contract is ending. The follow-on RFP is coming. "
                          f"Start your capture campaign for the recompete NOW.",
            })

    # Ceiling increase actions
    for item in sections.get("funding_actions", {}).get("items", []):
        if item.get("action_type") == "Ceiling Increase":
            actions.append({
                "priority": "THIS MONTH",
                "deadline": "30 days",
                "action": f"**{item.get('contract_name', 'Unknown')}** ceiling increased by {item.get('modification_value', 'Unknown')}. "
                          f"New ceiling: {item.get('new_ceiling', 'Unknown')}. "
                          f"If you're on this vehicle, new task orders are coming. Check for upcoming task order competitions.",
            })

    # Sort by priority
    priority_order = {"URGENT": 0, "THIS WEEK": 1, "THIS MONTH": 2}
    actions.sort(key=lambda x: priority_order.get(x["priority"], 3))

    for a in actions:
        emoji_map = {"URGENT": "[!!!]", "THIS WEEK": "[!!]", "THIS MONTH": "[!]"}
        marker = emoji_map.get(a["priority"], "[ ]")
        lines.append(f"- {marker} **{a['priority']}** ({a['deadline']}): {a['action']}")
        lines.append("")

    if not actions:
        lines.append("No time-critical actions identified this week. Use this window to:")
        lines.append("- Update your SAM.gov entity registration (check expiration date)")
        lines.append("- Refresh your capabilities statements for your top 3 target agencies")
        lines.append("- Review your subcontracting plan and identify gaps in teaming partners")
        lines.append("")

    return "\n".join(lines)


def generate_one_liners(data):
    """Generate tweet/LinkedIn-worthy one-liners for social promotion."""
    sections = data.get("sections", {})
    notable = data.get("notable", {})
    market = data.get("market_pulse", {})

    lines = []
    lines.append("## 7. Social Media One-Liners")
    lines.append("")
    lines.append("Ready-to-post hooks for LinkedIn, X/Twitter, or newsletter promotion.")
    lines.append("Each one is designed to stop the scroll and drive clicks to the full report.")
    lines.append("")

    hooks = []

    # From notable headline
    headline = notable.get("headline", "")
    key_stat = notable.get("key_stat", "")
    if headline and key_stat:
        hooks.append(f"{key_stat} in new DoD cyber spending this quarter. The zero-trust deadline isn't theoretical anymore -- it's a budget line item.")

    # From new awards -- use varied templates to avoid repetition
    award_templates_used = 0
    for item in sections.get("new_awards", {}).get("items", []):
        name = item.get("contract_name", "")
        awardee = item.get("awardee", "")
        value = item.get("award_value", "")
        detail = item.get("notable_detail", "")
        agency = item.get("agency", "a federal agency")

        if "AI" in name or "AI" in detail:
            hooks.append(f"{awardee} just won {value} for advanced technology work at {agency}. The federal tech market isn't coming -- it's here, and it's moving fast.")
            award_templates_used += 1
            continue

        # Rotate through varied templates based on detail content and index
        if "first" in detail.lower() or "shift" in detail.lower():
            hooks.append(f"{detail} Read that again. The procurement system is telling you where the market is going.")
            award_templates_used += 1
        elif "beat" in detail.lower() or "score" in detail.lower():
            hooks.append(f"{awardee} beat {', '.join(item.get('competitors_known', ['the field']))} for {value} at {agency}. Technical approach > lowest price. Every time.")
            award_templates_used += 1
        elif "largest" in detail.lower() or "biggest" in detail.lower():
            if award_templates_used % 2 == 0:
                hooks.append(f"{agency} just made its biggest bet yet: {value} to {awardee} for {name}. When an agency goes all-in, pay attention.")
            else:
                hooks.append(f"{value}. One contract. One vendor. {agency} is consolidating and {awardee} is the beneficiary. Your move.")
            award_templates_used += 1
        elif award_templates_used < 3:
            # General high-value award hooks with variety
            templates = [
                f"{awardee} just locked up {value} at {agency} for {name}. That's past performance your competitors can't replicate.",
                f"{agency} awarded {value} to {awardee}. If you compete in NAICS {item.get('naics', 'this space')}, study this win closely.",
                f"{name}: {value} to {awardee}. The gap between winners and everyone else in federal IT is widening.",
            ]
            hooks.append(templates[award_templates_used % len(templates)])
            award_templates_used += 1

    # From funding actions -- pick the single most impressive ceiling increase
    ceiling_increases = [
        item for item in sections.get("funding_actions", {}).get("items", [])
        if item.get("action_type") == "Ceiling Increase" and item.get("new_ceiling")
    ]
    if ceiling_increases:
        # Pick the largest by modification value
        biggest = max(ceiling_increases, key=lambda x: x.get("modification_value_raw", 0))
        new_ceiling = biggest.get("new_ceiling", "")
        contract = biggest.get("contract_name", "")
        mod_value = biggest.get("modification_value", "")
        hooks.append(f"{contract} ceiling just jumped by {mod_value} to {new_ceiling}. Ceiling increases are the federal government's way of voting with their wallet. Follow the money.")

    # From option exercises
    for item in sections.get("option_exercises", {}).get("items", []):
        option_year = item.get("option_year", "")
        if "final" in option_year.lower() or "4 of" in option_year or "5 of" in option_year:
            contractor = item.get("contractor", "")
            contract = item.get("contract_name", "")
            agency = item.get("agency", "")
            hooks.append(f"{agency} just exercised the final option on {contractor}'s {contract} contract. The recompete clock is ticking. Is your capture team ready?")

    # From market pulse
    yoy = market.get("yoy_change", "")
    if yoy and yoy.startswith("+"):
        hooks.append(f"Federal IT spending is up {yoy} year-over-year. The market is growing. The question isn't whether there's opportunity -- it's whether you're positioned to capture it.")

    # Add general market hooks
    hooks.append("Your competitor read this week's federal contract awards before you did. That's why they're winning recompetes and you're not. (Subscribe to change that.)")

    # Deduplicate and limit
    seen = set()
    unique_hooks = []
    for h in hooks:
        if h not in seen:
            seen.add(h)
            unique_hooks.append(h)

    for i, hook in enumerate(unique_hooks[:7], 1):
        lines.append(f"{i}. \"{hook}\"")
        lines.append("")

    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Main output assembly
# ---------------------------------------------------------------------------

def generate_insights(data, report_date):
    """Assemble the full insights document."""
    parts = []

    # Header
    report_week = data.get("report_subtitle", data.get("report_title", f"Week of {report_date}"))
    parts.append(f"# GovCon Intelligence: Deep Analytical Insights")
    parts.append(f"## {report_week}")
    parts.append(f"*Generated {report_date} | Data source: USAspending.gov / FPDS-NG*")
    parts.append("")
    parts.append("---")
    parts.append("")

    # Executive summary from notable
    notable = data.get("notable", {})
    if notable:
        parts.append("## Executive Summary")
        parts.append("")
        summary = notable.get("summary", "")
        if summary:
            parts.append(f"> {summary}")
            parts.append("")

    parts.append("This report goes beyond the data. Every section ends with a specific action item ")
    parts.append("tied to this week's transactions. If you read this and don't change at least one ")
    parts.append("thing in your BD pipeline, we haven't done our job.")
    parts.append("")
    parts.append("---")
    parts.append("")

    # Section 1: Recompete "So What"
    parts.append(analyze_recompetes(data))

    # Section 2: Agency Strategy Signals
    parts.append(analyze_agency_strategies(data))

    # Section 3: Contractor Power Rankings
    parts.append(analyze_contractor_power_rankings(data))

    # Section 4: Small Business Spotlight
    parts.append(analyze_small_business(data))

    # Section 5: Trend Analysis
    parts.append(analyze_trends(data))

    # Section 6: Action Items
    parts.append(generate_action_items(data))

    # Section 7: Social One-Liners
    parts.append(generate_one_liners(data))

    # Footer
    parts.append("---")
    parts.append("")
    parts.append("*This analysis is generated from public federal procurement data. ")
    parts.append("It represents one interpretation of market signals and should be combined ")
    parts.append("with your own competitive intelligence and agency relationships. ")
    parts.append("Past contract activity does not guarantee future procurement patterns.*")
    parts.append("")
    parts.append("**Want the full transaction data behind these insights?** ")
    parts.append("The raw dataset powering this report is available to subscribers.")
    parts.append("")

    return "\n".join(parts)


def main():
    parser = argparse.ArgumentParser(description="GovCon Deep Insights Generator")
    parser.add_argument("--date", default=datetime.now().strftime("%Y-%m-%d"),
                       help="Report date (default: today)")
    parser.add_argument("--input", default=None,
                       help="Path to input JSON (default: data/corrected_all.json)")
    parser.add_argument("--output", default=None,
                       help="Path to output markdown (default: output/insights_DATE.md)")
    args = parser.parse_args()

    # Resolve paths
    input_path = args.input or os.path.join(DATA_DIR, "corrected_all.json")
    output_path = args.output or os.path.join(OUTPUT_DIR, f"insights_{args.date}.md")

    print(f"GovCon Insights Generator", file=sys.stderr)
    print(f"  Input:  {input_path}", file=sys.stderr)
    print(f"  Output: {output_path}", file=sys.stderr)
    print(f"  Date:   {args.date}", file=sys.stderr)
    print("", file=sys.stderr)

    # Load data
    data = load_data(input_path)

    # Generate insights
    insights_md = generate_insights(data, args.date)

    # Write output
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, "w") as f:
        f.write(insights_md)

    # Stats
    line_count = insights_md.count("\n")
    word_count = len(insights_md.split())
    print(f"  Output: {line_count} lines, {word_count} words", file=sys.stderr)
    print(f"  Saved:  {output_path}", file=sys.stderr)


if __name__ == "__main__":
    main()
