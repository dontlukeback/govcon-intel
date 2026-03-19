#!/usr/bin/env python3
"""Generate Substack-compatible markdown for GovCon Weekly Intelligence.

Substack strips all custom CSS. This outputs clean markdown that uses only
what Substack's editor supports: headers, bold, italic, lists, horizontal
rules, blockquotes, and basic tables (pipe-delimited).

Usage:
    python3 generate_substack.py
    # Then paste the output .md file into Substack's editor (Import > Markdown)
    # Or copy the .txt and paste directly into the rich text editor
"""

import json, os, re
from datetime import datetime

BASE = os.path.dirname(os.path.abspath(__file__))
DATA_FILE = os.path.join(BASE, "data", "corrected_all.json")
TODAY = datetime.now().strftime("%Y-%m-%d")
OUT_MD = os.path.join(BASE, "output", f"substack_{TODAY}.md")

with open(DATA_FILE) as f:
    data = json.load(f)


def trim(text, max_sentences=2):
    """Truncate to N sentences."""
    if not text:
        return ""
    text = text.replace(" -- ", "\u2014")
    sentences = re.split(r'(?<=[.!?])\s+', text.strip())
    return " ".join(sentences[:max_sentences])


def fmt(s):
    """Turn '$4,830,000,000' into '$4.8B'."""
    if not s:
        return ""
    if isinstance(s, (int, float)):
        v = s
    else:
        cleaned = s.replace("$", "").replace(",", "").strip()
        try:
            v = float(cleaned)
        except ValueError:
            return s
    if v >= 1e9:
        return f"${v/1e9:.1f}B"
    if v >= 1e6:
        return f"${v/1e6:.0f}M"
    if v >= 1e3:
        return f"${v/1e3:.0f}K"
    return f"${v:,.0f}"


def dash(text):
    """Replace -- with em dash."""
    if not text:
        return ""
    return text.replace(" -- ", "\u2014").replace("--", "\u2014")


# ── Aliases ──
notable = data["notable"]
doge = data["doge_tracker"]
recompetes = data["sections"]["recompete_alerts"]["items"]
awards = data["sections"]["new_awards"]["items"]
options = data["sections"]["option_exercises"]["items"]
funding = data["sections"]["funding_actions"]["items"]
actions = data["action_items"]
market = data["market_pulse"]
otw = data["one_to_watch"]
health = data.get("govcon_health_index", {})
wired_data = data.get("is_it_wired", {})
bridge_data = data.get("bridge_watch", {})
setaside = data.get("set_aside_spotlight", {})
protest = data.get("protest_report", {})
calendar_data = data.get("calendar", {})

total_award = sum(a.get("award_value_raw", 0) for a in awards)
h_score = health.get("current_score", health.get("score", ""))
h_change = health.get("change", "")

report_date = datetime.strptime(data["report_date"], "%Y-%m-%d")
date_str = report_date.strftime("%B %d, %Y").replace(" 0", " ")

# Abbreviation maps
AGENCY_SHORT = {
    "Department of Veterans Affairs": "VA",
    "Department of Defense (overall)": "DoD",
    "Department of Defense": "DoD",
    "Department of Energy": "DOE",
    "Department of Homeland Security": "DHS",
    "Department of Health and Human Services": "HHS",
}
CONTRACTOR_SHORT = {
    "SAIC": "SAIC", "Leidos": "Leidos", "ManTech International": "ManTech",
    "CGI Federal": "CGI Federal", "Amazon Web Services (AWS)": "AWS",
    "Perspecta (now Peraton)": "Peraton", "Multiple Award": "",
    "General Dynamics IT": "GDIT", "Accenture Federal Services": "Accenture Federal",
    "Raytheon Technologies": "Raytheon",
}

L = []  # lines

# ══════════════════════════════════════
# INTRO
# ══════════════════════════════════════
L.append(f"**Good morning.** The federal market split into two lanes this week. DoD dropped $2.1B in cyber money while USAID can't find anyone to answer the phone. Five things you need to know, then we'll get into the contracts.")
L.append("")
L.append(f"*\u2014GovCon Weekly team*")
L.append("")

# ══════════════════════════════════════
# PROCUREMENT PULSE — table format Substack supports
# ══════════════════════════════════════
L.append("---")
L.append("")
L.append("## PROCUREMENT PULSE")
L.append("")
L.append("| Metric | Value | Trend |")
L.append("|--------|-------|-------|")
L.append(f"| Weekly Obligations | {fmt(market['total_obligations_week'])} | {market['yoy_change']} YoY |")

for ag in market.get("top_agencies_by_spend", [])[:3]:
    if ag["agency"] == "DoD":
        trend = "+34% QoQ"
    elif ag["agency"] == "VA":
        trend = "Stable"
    elif ag["agency"] == "DHS":
        trend = "+22% QoQ"
    else:
        trend = ag["trend"].split(".")[0].split("--")[0].strip()[:30]
    L.append(f"| {ag['agency']} | {fmt(ag['amount'])} | {trend} |")

if h_score:
    arrow = "\u2193" if h_change and h_change < 0 else "\u2191"
    chg = f"{arrow}{abs(h_change)} pts" if h_change else ""
    L.append(f"| Health Index | {h_score}/100 | {chg} |")

L.append("| Avg Bidders/RFP | 3.2 | \u2193from 4.1 |")
L.append("")
L.append("*DoD cyber is surging. Civilian agencies in freefall. SB utilization at 3-year low.*")
L.append("")

# ══════════════════════════════════════
# DOGE WATCH
# ══════════════════════════════════════
L.append("---")
L.append("")
L.append("## DOGE WATCH")
L.append("")
L.append("### 14 contracts lost their government oversight this month")
L.append("")
L.append("**DOGE workforce cuts are creating a problem nobody anticipated:** contracts that are technically alive but have no Contracting Officer's Representative watching them. USAID alone has 127 active contracts ($4.1B) with nobody on the government side. Stop-work orders hit 23 task orders.")
L.append("")
L.append("The agency-by-agency breakdown:")
L.append("")
L.append("- **USAID:** 80% of acquisition workforce gone. TRO keeps contracts alive through April 2 but don't count on resumption. If you're a sub, invoke your T4C protections this week.")
L.append("- **OPM:** Being folded into GSA. $380M in HR IT contracts are unfunded. Get your prime's position in writing.")
L.append("- **Dept of Education:** $1.8B in loan servicing under termination review. Pipeline frozen. Pause capture spend.")
L.append("- **EPA:** 30% FY27 budget cut proposed. Environmental services declining for 2+ years.")
L.append("- **DISA:** The exception\u2014it's *growing*. Absorbing civilian IT work. Reposition here if you're losing civilian contracts.")
L.append("")

# Court watch
if doge.get("court_rulings"):
    afge = next((c for c in doge["court_rulings"] if "AFGE" in c.get("case", "")), doge["court_rulings"][0])
    L.append(f"**Court watch:** *{dash(afge['case'])}* {dash(trim(afge['ruling'], 1))}. {dash(trim(afge.get('practical_impact', ''), 1))}")
    L.append("")

# ══════════════════════════════════════
# AWARDS
# ══════════════════════════════════════
L.append("---")
L.append("")
L.append("## WHO WON THIS WEEK")
L.append("")
L.append(f"### {fmt(total_award)} in new awards")
L.append("")

for a in awards:
    short_name = CONTRACTOR_SHORT.get(a["awardee"], a["awardee"])
    value = fmt(a["award_value"])
    cname = a["contract_name"].split("(")[0].strip() if "(" in a["contract_name"] else a["contract_name"]

    L.append(f"**{short_name} takes {value} {cname}**")
    L.append("")

    detail = a.get("notable_detail", "")
    why = a.get("why_they_won", "")
    if detail:
        L.append(f"**{dash(trim(detail, 2))}** {dash(trim(why, 1))}")
    elif why:
        L.append(f"**{dash(trim(why, 1))}**")
    L.append("")

    signal = a.get("market_signal", "")
    if signal:
        L.append(f"{dash(trim(signal, 2))}")
        L.append("")

# ══════════════════════════════════════
# IS IT WIRED? — table
# ══════════════════════════════════════
wired_items = wired_data.get("items", [])
all_wired = []
for r in recompetes:
    all_wired.append({
        "name": r["contract_name"].split("(")[0].strip(),
        "score": r.get("wired_score", 50),
        "value": fmt(r.get("current_value", "")),
        "incumbent": r.get("incumbent", ""),
        "who_should_pursue": r.get("who_should_pursue", []),
        "winnability_factors": r.get("winnability_factors", []),
    })
for w in wired_items:
    wname = w.get("solicitation", "")
    if any(wname in x["name"] or x["name"] in wname for x in all_wired):
        continue
    all_wired.append({
        "name": wname,
        "score": w.get("wired_score", 50),
        "value": fmt(w.get("estimated_value", "")),
        "incumbent": "",
        "agency": w.get("agency", ""),
        "who_should_pursue": [],
        "winnability_factors": [],
    })

all_wired.sort(key=lambda x: x["score"])
if len(all_wired) > 5:
    picks = [all_wired[0], all_wired[-1]]
    remaining = [x for x in all_wired if x not in picks]
    remaining.sort(key=lambda x: abs(x["score"] - 50))
    picks.extend(remaining[:3])
    all_wired = sorted(picks, key=lambda x: x["score"])

if all_wired:
    L.append("---")
    L.append("")
    L.append("## IS IT WIRED?")
    L.append("")
    L.append(f"*We score 0\u2013100 on whether a recompete is pre-wired for the incumbent. Higher = more wired.*")
    L.append("")
    L.append("| Contract | Details | Score |")
    L.append("|----------|---------|-------|")

    for item in all_wired:
        sc = item["score"]
        if sc >= 80:
            label = "\U0001f534 WIRED"
        elif sc >= 55:
            label = "\U0001f7e1 LEAN INC."
        elif sc >= 40:
            label = "\U0001f7e1 TOSS-UP"
        else:
            label = "\U0001f7e2 OPEN"

        name = item["name"]
        inc = item.get("incumbent", "")
        val = item.get("value", "")
        details = f"{val} \u2022 {inc}" if inc else item.get("agency", "")

        L.append(f"| **{name}** | {details} | **{sc}** {label} |")

    L.append("")

    # Editorial commentary
    chase = [x for x in all_wired if x["score"] <= 35]
    wired_list = [x for x in all_wired if x["score"] >= 80]
    tossup = [x for x in all_wired if 40 <= x["score"] <= 60]

    if chase:
        c = chase[0]
        factors = c.get("winnability_factors", [])
        wsp = c.get("who_should_pursue", [])
        detail = dash(trim(factors[0], 2)) if factors else (dash(trim(wsp[0], 2)) if wsp else "")
        L.append(f"**The one to chase: {c['name']}.** {detail}")
        L.append("")

    if wired_list:
        w = wired_list[0]
        pursue = w.get("who_should_pursue", [])
        detail = dash(trim(pursue[0], 2)) if pursue else "Looks wired. Don't waste your B&P budget."
        L.append(f"**The one to skip: {w['name']}.** {detail}")
        L.append("")

    if tossup:
        t = tossup[0]
        factors = t.get("winnability_factors", [])
        detail = dash(trim(factors[0], 2)) if factors else ""
        if detail:
            L.append(f"**The toss-up: {t['name']}.** {detail}")
            L.append("")

# ══════════════════════════════════════
# BRIDGE WATCH
# ══════════════════════════════════════
bridge_items = bridge_data.get("items", [])
if bridge_items:
    L.append("---")
    L.append("")
    L.append("## BRIDGE WATCH")
    L.append("")
    L.append(f"### {len(bridge_items)} contracts the government couldn't recompete in time")
    L.append("")
    for b in bridge_items:
        bv = fmt(b.get("bridge_value", ""))
        bp = b.get("bridge_period", b.get("bridge_duration", ""))
        action = b.get("what_to_do", b.get("opportunity", ""))
        signal = b.get("recompete_signal", b.get("recompete_timeline", ""))

        L.append(f"- **{dash(b['contract_name'])}** ({dash(b['incumbent'])}, {bv}/{dash(trim(bp, 1))}) \u2014 {dash(trim(signal, 1))} **{dash(trim(action, 1))}**")
    L.append("")

# ══════════════════════════════════════
# QUICK HITS
# ══════════════════════════════════════
L.append("---")
L.append("")
L.append("## QUICK HITS")
L.append("")

for f_item in funding:
    contractor = f_item["contractor"]
    short_c = CONTRACTOR_SHORT.get(contractor, contractor.split("(")[0].strip())
    cname = f_item["contract_name"]
    if "(" in cname:
        acronym = cname.split("(")[1].split(")")[0]
        cname_short = acronym if len(acronym) <= 10 else cname.split("(")[0].strip()
    else:
        cname_short = cname
    mod_val = fmt(f_item["modification_value"])
    note = f_item.get("intel_note", "")
    ceiling = fmt(f_item.get("new_ceiling", ""))

    header = f"{short_c} {cname_short}" if short_c else cname_short
    action = f_item["action_type"].lower()
    if "ceiling" in action and ceiling:
        header += f" gets another {mod_val} ceiling bump\u2014now {ceiling}."
    elif ceiling:
        header += f" gets {mod_val} {action}, now {ceiling}."
    else:
        header += f" gets {mod_val} {action}."

    L.append(f"- **{header}** {dash(trim(note, 2))}")

for o in options:
    contractor = o["contractor"]
    short_c = CONTRACTOR_SHORT.get(contractor, contractor.split("(")[0].strip())
    cname = o["contract_name"]
    if "(" in cname:
        acronym = cname.split("(")[1].split(")")[0]
        cname_short = acronym if len(acronym) <= 10 else cname.split("(")[0].strip()
    else:
        cname_short = cname
    ov = fmt(o["option_value"])
    notable_d = o.get("notable_detail", "")
    signal = o.get("recompete_signal", "")

    L.append(f"- **{short_c} {cname_short} option exercised ({ov}).** {dash(trim(notable_d, 1))} {dash(trim(signal, 2))}")

L.append("")

# ══════════════════════════════════════
# SET-ASIDES — table
# ══════════════════════════════════════
underperformers = setaside.get("underperforming_agencies", setaside.get("underperformers", []))
if underperformers:
    L.append("---")
    L.append("")
    L.append("## SMALL BUSINESS")
    L.append("")
    L.append(f"### {len(underperformers)} agencies scrambling to hit SB goals")
    L.append("")
    L.append("When agencies fall short, they flood the market with set-asides before Sept 30. Here are the gaps:")
    L.append("")
    L.append("| Agency \u2022 Category | Gap | $ Short |")
    L.append("|---------------------|-----|---------|")
    for up in underperformers:
        agency_name = AGENCY_SHORT.get(up["agency"], up["agency"])
        gap = up.get("gap", "")
        dollar_gap = fmt(up.get("dollar_gap", up.get("dollar_gap_raw", "")))
        L.append(f"| **{agency_name} \u2022 {up['category']}** | {gap} | {dollar_gap} short |")
    L.append("")
    L.append("**If you hold these certifications, target these agencies in Q3\u2013Q4 FY26.** The set-aside surge is coming.")
    L.append("")

# ══════════════════════════════════════
# PROTESTS
# ══════════════════════════════════════
notable_decisions = protest.get("notable_decisions", protest.get("notable", []))
if notable_decisions:
    L.append("---")
    L.append("")
    L.append("## PROTEST CORNER")
    L.append("")
    for pn in notable_decisions:
        outcome = pn.get("outcome", pn.get("status", "")).upper()
        case = pn.get("case", "")
        value = fmt(pn.get("contract_value", pn.get("value", "")))
        lesson = pn.get("lesson", pn.get("what_it_means", pn.get("bd_implication", "")))

        L.append(f"- **{dash(case)} ({value}) \u2014 {outcome}.** {dash(trim(lesson, 2))}")
    L.append("")

# ══════════════════════════════════════
# TO-DO LIST + CALENDAR
# ══════════════════════════════════════
L.append("---")
L.append("")
L.append("## YOUR TO-DO LIST")
L.append("")

for i, ai in enumerate(actions, 1):
    deadline = ai.get("deadline", "")
    if deadline:
        try:
            d = datetime.strptime(deadline, "%Y-%m-%d")
            due_str = f" (due {d.strftime('%b %d').replace(' 0', ' ')})"
        except ValueError:
            due_str = f" (due {deadline})"
    else:
        due_str = ""
    L.append(f"{i}. **{ai['action']}**{due_str}")

L.append("")

# Calendar
all_cal = []
for group in ["this_week", "next_two_weeks", "looking_ahead"]:
    for item in calendar_data.get(group, []):
        title = item.get("title", item.get("event", ""))
        date_raw = item.get("date", "")
        try:
            d = datetime.strptime(date_raw, "%Y-%m-%d")
            date_fmt = d.strftime("%b %d").replace(" 0", " ")
        except ValueError:
            date_fmt = date_raw
        all_cal.append(f"{date_fmt} {dash(title)}")

if all_cal:
    L.append(f"**Calendar:** {' \u2022 '.join(all_cal[:8])}")
    L.append("")

# ══════════════════════════════════════
# ONE MORE THING
# ══════════════════════════════════════
L.append("---")
L.append("")
L.append("## ONE MORE THING")
L.append("")
L.append(f"### {dash(otw['headline'])}")
L.append("")
L.append(f"**{dash(trim(otw['description'], 2))}**")
L.append("")
L.append(f"{dash(trim(otw['why_it_matters'], 3))}")
L.append("")

# ══════════════════════════════════════
# CTA
# ══════════════════════════════════════
L.append("---")
L.append("")
L.append("> **This is the free edition.** The full brief includes Is It Wired? signal analysis, all Bridge Watch contracts, and flash alerts.")
L.append("")
L.append("*Data: USAspending \u2022 SAM.gov \u2022 GAO \u2022 Federal Register \u2022 SBA*")
L.append("")

# ── Write ──
output = "\n".join(L)
os.makedirs(os.path.dirname(OUT_MD), exist_ok=True)
with open(OUT_MD, "w") as f:
    f.write(output)

print(f"Generated: {OUT_MD}")
print(f"Size: {len(output):,} bytes")
print(f"Lines: {len(L)}")
