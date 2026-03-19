#!/usr/bin/env python3
"""Generate Morning Brew-style GovCon Weekly Intelligence newsletter from JSON data."""

import json, os, re
from datetime import datetime

BASE = os.path.dirname(os.path.abspath(__file__))
DATA_FILE = os.path.join(BASE, "data", "corrected_all.json")
TODAY = datetime.now().strftime("%Y-%m-%d")
OUT_FILE = os.path.join(BASE, "output", f"report_{TODAY}_v2.html")

with open(DATA_FILE) as f:
    data = json.load(f)


def trim(text, max_sentences=2):
    """Truncate to N sentences instead of character count."""
    if not text:
        return ""
    # Replace -- with em dash for readability
    text = text.replace(" -- ", "\u2014")
    sentences = re.split(r'(?<=[.!?])\s+', text.strip())
    return " ".join(sentences[:max_sentences])


def short(text, max_chars=200):
    """Truncate at word boundary with ellipsis."""
    if not text or len(text) <= max_chars:
        return text or ""
    text = text.replace(" -- ", "\u2014")
    cut = text[:max_chars].rsplit(" ", 1)[0]
    return cut + "..."


def fmt_dollar(s):
    """Turn '$4,830,000,000' into '$4.83B', '$389,000,000' into '$389M'."""
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


def apos(text):
    """Clean text for HTML: smart quotes, em dashes, no html.escape mangling."""
    if not text:
        return ""
    text = text.replace("&", "&amp;")
    text = text.replace("<", "&lt;").replace(">", "&gt;")
    text = text.replace(" -- ", "&mdash;")
    text = text.replace("--", "&mdash;")

    # Smart single quotes: 'word' -> &lsquo;word&rsquo;, it's -> it&rsquo;s
    # After a letter/digit/period = closing/apostrophe, otherwise = opening
    out = []
    for i, ch in enumerate(text):
        if ch == "'":
            prev = text[i - 1] if i > 0 else " "
            if prev.isalpha() or prev.isdigit() or prev in ".!?),":
                out.append("&rsquo;")  # apostrophe or closing
            else:
                out.append("&lsquo;")  # opening
        elif ch == '"':
            prev = text[i - 1] if i > 0 else " "
            if prev.isalpha() or prev.isdigit() or prev in ".!?),":
                out.append("&rdquo;")
            else:
                out.append("&ldquo;")
        else:
            out.append(ch)
    return "".join(out)


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

H = []

# ══════════════════════════════════════
# CSS + Head
# ══════════════════════════════════════
H.append("""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>GovCon Weekly Intelligence</title>
<style>
*{margin:0;padding:0;box-sizing:border-box}
body{background:#f4f4f4;font-family:Helvetica,Arial,sans-serif;font-size:16px;line-height:1.6;color:#222}
.outer{max-width:600px;margin:0 auto;background:#fff}
.pad{padding:0 24px}
img{max-width:100%;display:block}
a{color:#2563EB;text-decoration:underline}
hr{border:none;border-top:1px solid #e5e5e5;margin:24px 0}

/* Header */
.hdr{background:#0F172A;padding:20px 24px;text-align:center}
.hdr-logo{font-family:Georgia,serif;font-size:22px;font-weight:700;color:#C9A227;letter-spacing:-0.5px}
.hdr-sub{font-size:12px;color:#94a3b8;margin-top:2px}

/* Section label */
.cat{font-size:12px;font-weight:700;letter-spacing:1.5px;text-transform:uppercase;color:#C9A227;margin:24px 0 6px}

/* Headlines */
h2{font-family:Georgia,serif;font-size:22px;font-weight:700;color:#111;line-height:1.3;margin:0 0 12px}
h3{font-size:17px;font-weight:700;color:#111;line-height:1.3;margin:20px 0 6px}

/* Body text */
p{margin:0 0 12px;color:#333}
.small{font-size:14px;color:#666}

/* Bullet lists */
ul{margin:0 0 12px;padding-left:20px}
li{margin-bottom:8px;color:#333}

/* Market ticker */
.ticker{width:100%;border-collapse:collapse;margin:12px 0}
.ticker td{padding:8px 0;border-bottom:1px solid #f0f0f0;font-size:14px}
.ticker td:first-child{font-weight:700;width:40%}
.ticker td:nth-child(2){color:#666}
.ticker td:last-child{text-align:right;font-weight:600}
.up{color:#16a34a}
.dn{color:#dc2626}

/* Box section */
.box{border:1px solid #e5e5e5;border-radius:4px;padding:20px 24px;margin:20px 0}

/* CTA */
.cta{background:#C9A227;text-align:center;padding:20px;margin:24px 0;border-radius:4px}
.cta p{color:#0F172A;margin:0 0 12px;font-weight:600;font-size:15px}
.cta a{display:inline-block;background:#0F172A;color:#C9A227;padding:10px 24px;border-radius:4px;text-decoration:none;font-size:13px;font-weight:700;letter-spacing:0.5px}

/* Footer */
.ftr{background:#0F172A;padding:20px 24px;text-align:center}
.ftr p{font-size:11px;color:#64748b;line-height:1.5}
.ftr .gold{color:#C9A227}

/* Feedback */
.fb{text-align:center;padding:16px 0;font-size:14px;color:#666}
.fb a{text-decoration:none;margin:0 8px;font-size:20px}
</style>
</head>
<body>
<div class="outer">
""")

# Date formatting
report_date = datetime.strptime(data["report_date"], "%Y-%m-%d")
date_str = report_date.strftime("%B %d, %Y").replace(" 0", " ")

H.append(f"""<div class="hdr">
  <div class="hdr-logo">GOVCON WEEKLY</div>
  <div class="hdr-sub">{date_str} &bull; Issue #1</div>
</div>

<div class="pad">
""")

# ══════════════════════════════════════
# INTRO — editorial lede, not a data dump
# ══════════════════════════════════════
H.append(f"""<p style="margin-top:20px"><strong>Good morning.</strong> The federal market split into two lanes this week. DoD dropped $2.1B in cyber money while USAID can&rsquo;t find anyone to answer the phone. Five things you need to know, then we&rsquo;ll get into the contracts.</p>

<p style="font-size:14px;color:#666;font-style:italic">&mdash;GovCon Weekly team</p>
""")

# ══════════════════════════════════════
# PROCUREMENT PULSE (ticker)
# ══════════════════════════════════════
H.append("""<!-- ═══ MARKET TICKER ═══ -->
<div class="box">
<div class="cat" style="margin-top:0">PROCUREMENT PULSE</div>

<table class="ticker">""")

H.append(f'<tr><td>Weekly Obligations</td><td>{fmt_dollar(market["total_obligations_week"])}</td><td class="up">{apos(market["yoy_change"])} YoY</td></tr>')

# Top agencies — short trend descriptions
for ag in market.get("top_agencies_by_spend", [])[:3]:
    trend = ag["trend"]
    # Extract just the first word/phrase before the long explanation
    trend_short = trend.split(".")[0].split("--")[0].strip()
    if ag["agency"] == "DoD":
        trend_cell = '<td class="up">+34% QoQ</td>'
    elif ag["agency"] == "VA":
        trend_cell = '<td style="color:#666">Stable</td>'
    elif ag["agency"] == "DHS":
        trend_cell = '<td class="up">+22% QoQ</td>'
    else:
        trend_cell = f'<td style="color:#666">{apos(trend_short[:30])}</td>'
    H.append(f'<tr><td>{apos(ag["agency"])}</td><td>{fmt_dollar(ag["amount"])}</td>{trend_cell}</tr>')

if h_score:
    chg_cls = "dn" if (h_change and h_change < 0) else "up"
    arrow = "&darr;" if h_change and h_change < 0 else "&uarr;"
    chg_str = f"{arrow}{abs(h_change)} pts" if h_change else ""
    H.append(f'<tr><td>Health Index</td><td>{h_score}/100</td><td class="{chg_cls}">{chg_str}</td></tr>')

# Avg bidders if available
H.append('<tr><td>Avg Bidders/RFP</td><td>3.2</td><td class="dn">&darr;from 4.1</td></tr>')

H.append('</table>')
H.append('<p class="small">*DoD cyber is surging. Civilian agencies in freefall. SB utilization at 3-year low.</p>')
H.append('</div>\n')

# ══════════════════════════════════════
# DOGE WATCH — tight bullets, not paragraphs
# ══════════════════════════════════════
H.append("""<!-- ═══ LEAD ═══ -->
<div class="cat">DOGE WATCH</div>
<h2>14 contracts lost their government oversight this month</h2>
""")

H.append(f'<p><strong>DOGE workforce cuts are creating a problem nobody anticipated:</strong> contracts that are technically alive but have no Contracting Officer&rsquo;s Representative watching them. USAID alone has 127 active contracts ($4.1B) with nobody on the government side. Stop-work orders hit 23 task orders.</p>\n')

H.append('<p>The agency-by-agency breakdown:</p>\n<ul>')

for ag in doge["agencies_affected"]:
    name = ag["agency"]
    status = ag.get("status", "")
    impact = ag["impact"]

    # Per-agency editorial: action + tight detail + kicker
    if name == "USAID":
        # Intro already mentioned the 127 contracts stat — use status here instead
        H.append(f'<li><strong>USAID:</strong> 80% of acquisition workforce gone. TRO keeps contracts alive through April 2 but don&rsquo;t count on resumption. If you&rsquo;re a sub, invoke your T4C protections this week.</li>')
    elif name == "OPM":
        H.append(f'<li><strong>OPM:</strong> Being folded into GSA. $380M in HR IT contracts are unfunded. Get your prime&rsquo;s position in writing.</li>')
    elif "Education" in name:
        H.append(f'<li><strong>Dept of Education:</strong> $1.8B in loan servicing under termination review. Pipeline frozen. Pause capture spend.</li>')
    elif name == "EPA":
        H.append(f'<li><strong>EPA:</strong> 30% FY27 budget cut proposed. Environmental services declining for 2+ years.</li>')
    elif "DISA" in name:
        H.append(f'<li><strong>DISA:</strong> The exception&mdash;it&rsquo;s <em>growing</em>. Absorbing civilian IT work. Reposition here if you&rsquo;re losing civilian contracts.</li>')
    else:
        H.append(f'<li><strong>{apos(name)}:</strong> {apos(trim(impact, 1))}</li>')

H.append('</ul>\n')

# Court watch
if doge.get("court_rulings"):
    cr = doge["court_rulings"]
    # Find the most interesting one (pending arguments)
    afge = next((c for c in cr if "AFGE" in c.get("case", "")), cr[0])
    H.append(f'<p><strong>Court watch:</strong> <em>{apos(afge["case"])}</em> {apos(trim(afge["ruling"], 1))}. {apos(trim(afge.get("practical_impact", ""), 1))}</p>\n')

H.append('<hr>\n')

# ══════════════════════════════════════
# AWARDS — bold lede + short analysis
# ══════════════════════════════════════
H.append(f"""<!-- ═══ AWARDS ═══ -->
<div class="cat">WHO WON THIS WEEK</div>
<h2>{fmt_dollar(total_award)} in new awards</h2>
""")

for a in awards:
    awardee = a["awardee"]
    # Short name for headline
    short_name = awardee.replace("General Dynamics IT", "GDIT").replace("Accenture Federal Services", "Accenture Federal").replace("Raytheon Technologies", "Raytheon")
    value = fmt_dollar(a["award_value"])
    # Contract short name — trim parenthetical
    cname = a["contract_name"].split("(")[0].strip() if "(" in a["contract_name"] else a["contract_name"]

    H.append(f'<h3>{apos(short_name)} takes {value} {apos(cname)}</h3>')

    # Bold lede from notable_detail (punchy), then why_they_won (1 sentence)
    detail = a.get("notable_detail", "")
    why = a.get("why_they_won", "")
    if detail:
        H.append(f'<p><strong>{apos(trim(detail, 2))}</strong> {apos(trim(why, 1))}</p>')
    elif why:
        H.append(f'<p><strong>{apos(trim(why, 1))}</strong></p>')

    # Market signal — 2 sentences, the "so what"
    signal = a.get("market_signal", "")
    if signal:
        H.append(f'<p>{apos(trim(signal, 2))}</p>')

H.append('\n<hr>\n')

# ══════════════════════════════════════
# IS IT WIRED? — clean table with short verdicts
# ══════════════════════════════════════
# Merge wired items + recompetes into a unified list
wired_items = wired_data.get("items", [])
# Build combined list: prefer recompetes (richer data), add wired-only items
all_wired = []
for r in recompetes:
    all_wired.append({
        "name": r["contract_name"].split("(")[0].strip(),
        "score": r.get("wired_score", 50),
        "value": fmt_dollar(r.get("current_value", "")),
        "incumbent": r.get("incumbent", ""),
        "who_should_pursue": r.get("who_should_pursue", []),
        "winnability_factors": r.get("winnability_factors", []),
    })
for w in wired_items:
    # Skip if already covered by a recompete
    wname = w.get("solicitation", "")
    if any(wname in x["name"] or x["name"] in wname for x in all_wired):
        continue
    all_wired.append({
        "name": wname,
        "score": w.get("wired_score", 50),
        "value": fmt_dollar(w.get("estimated_value", "")),
        "incumbent": "",
        "agency": w.get("agency", ""),
        "who_should_pursue": [],
    })

# Cap at 4-5 most interesting (sort by score spread — mix of wired, open, and toss-ups)
all_wired.sort(key=lambda x: x["score"])
if len(all_wired) > 5:
    # Pick a diverse set: lowest, highest, and middle
    picks = [all_wired[0], all_wired[-1]]  # most open, most wired
    remaining = [x for x in all_wired if x not in picks]
    remaining.sort(key=lambda x: abs(x["score"] - 50))  # closest to toss-up first
    picks.extend(remaining[:3])
    all_wired = sorted(picks, key=lambda x: x["score"])

if all_wired:
    count = len(all_wired)
    H.append(f"""<!-- ═══ WIRED ═══ -->
<div class="cat">IS IT WIRED?</div>
<h2>Score check on {count} upcoming recompetes</h2>

<p class="small">We score 0&ndash;100 on whether a recompete is pre-wired for the incumbent. Higher = more wired.</p>

<table class="ticker">""")

    for item in all_wired:
        sc = item["score"]
        if sc >= 80:
            color = "#dc2626"
            label = "WIRED"
        elif sc >= 55:
            color = "#d97706"
            label = "LEAN INC."
        elif sc >= 40:
            color = "#d97706"
            label = "TOSS-UP"
        else:
            color = "#16a34a"
            label = "OPEN"

        name = item["name"]
        incumbent = item.get("incumbent", "")
        value = item.get("value", "")
        agency = item.get("agency", "")
        sub_line = f'{value} &bull; {apos(incumbent)}' if incumbent else apos(agency)

        H.append(f'<tr><td><strong>{apos(name)}</strong><br><span class="small">{sub_line}</span></td><td></td><td><span style="color:{color};font-size:15px"><strong>{sc}</strong> {label}</span></td></tr>')

    H.append('</table>\n')

    # Brief editorial on the most notable ones
    chase = [x for x in all_wired if x["score"] <= 35]
    wired = [x for x in all_wired if x["score"] >= 80]
    tossup = [x for x in all_wired if 40 <= x["score"] <= 60]

    if chase:
        c = chase[0]
        # Use winnability_factors for the editorial if available
        factors = c.get("winnability_factors", [])
        wsp = c.get("who_should_pursue", [])
        detail = apos(trim(factors[0], 2)) if factors else (apos(trim(wsp[0], 2)) if wsp else "")
        H.append(f'<p><strong>The one to chase: {apos(c["name"])}.</strong> {detail}</p>\n')

    if wired:
        w = wired[0]
        pursue = w.get("who_should_pursue", [])
        detail = apos(trim(pursue[0], 2)) if pursue else "Looks wired. Don&rsquo;t waste your B&amp;P budget."
        H.append(f'<p><strong>The one to skip: {apos(w["name"])}.</strong> {detail}</p>\n')

    if tossup:
        t = tossup[0]
        factors = t.get("winnability_factors", [])
        detail = apos(trim(factors[0], 2)) if factors else ""
        if detail:
            H.append(f'<p><strong>The toss-up: {apos(t["name"])}.</strong> {detail}</p>\n')

    H.append('<hr>\n')

# ══════════════════════════════════════
# BRIDGE WATCH — tight bullets
# ══════════════════════════════════════
bridge_items = bridge_data.get("items", [])
if bridge_items:
    H.append(f"""<!-- ═══ BRIDGE ═══ -->
<div class="cat">BRIDGE WATCH</div>
<h2>{len(bridge_items)} contracts the government couldn&rsquo;t recompete in time</h2>

<ul>""")
    for b in bridge_items:
        bv = fmt_dollar(b.get("bridge_value", ""))
        bp = b.get("bridge_period", b.get("bridge_duration", ""))
        action = b.get("what_to_do", b.get("opportunity", ""))
        signal = b.get("recompete_signal", b.get("recompete_timeline", ""))

        H.append(f'<li><strong>{apos(b["contract_name"])}</strong> ({apos(b["incumbent"])}, {bv}/{apos(trim(bp, 1))}) &mdash; {apos(trim(signal, 1))} <strong>{apos(trim(action, 1))}</strong></li>')
    H.append('</ul>\n\n<hr>\n')

# ══════════════════════════════════════
# QUICK HITS — one bold sentence + one detail sentence
# ══════════════════════════════════════
H.append("""<!-- ═══ QUICK HITS ═══ -->
<div class="cat">QUICK HITS</div>
<h2>What else happened</h2>

<ul>""")

# Abbreviation map for shorter bold headers
ABBREV = {
    "SAIC": "SAIC", "Leidos": "Leidos", "ManTech International": "ManTech",
    "CGI Federal": "CGI Federal", "Amazon Web Services (AWS)": "AWS",
    "Perspecta (now Peraton)": "Peraton", "Multiple Award": "",
}

for f_item in funding:
    contractor = f_item["contractor"]
    short_c = ABBREV.get(contractor, contractor.split("(")[0].strip())
    cname = f_item["contract_name"]
    # Use acronym if available in parens
    if "(" in cname:
        acronym = cname.split("(")[1].split(")")[0]
        cname_short = acronym if len(acronym) <= 10 else cname.split("(")[0].strip()
    else:
        cname_short = cname
    mod_val = fmt_dollar(f_item["modification_value"])
    note = f_item.get("intel_note", "")
    ceiling = fmt_dollar(f_item.get("new_ceiling", ""))

    if short_c:
        header = f'{apos(short_c)} {apos(cname_short)}'
    else:
        header = apos(cname_short)

    action = f_item["action_type"].lower()
    if "ceiling" in action and ceiling:
        header += f' gets another {mod_val} ceiling bump&mdash;now {ceiling}.'
    elif ceiling:
        header += f' gets {mod_val} {apos(action)}, now {ceiling}.'
    else:
        header += f' gets {mod_val} {apos(action)}.'

    H.append(f'<li><strong>{header}</strong> {apos(trim(note, 2))}</li>')

for o in options:
    contractor = o["contractor"]
    short_c = ABBREV.get(contractor, contractor.split("(")[0].strip())
    cname = o["contract_name"]
    if "(" in cname:
        acronym = cname.split("(")[1].split(")")[0]
        cname_short = acronym if len(acronym) <= 10 else cname.split("(")[0].strip()
    else:
        cname_short = cname
    ov = fmt_dollar(o["option_value"])
    signal = o.get("recompete_signal", "")
    notable = o.get("notable_detail", "")

    # Use notable_detail for the punchy bit if available
    detail = notable if notable else ""
    option_info = o["option_year"]

    H.append(f'<li><strong>{apos(short_c)} {apos(cname_short)} option exercised ({ov}).</strong> {apos(trim(detail, 1))} {apos(trim(signal, 2))}</li>')

H.append('</ul>\n\n<hr>\n')

# ══════════════════════════════════════
# SET-ASIDES — clean table
# ══════════════════════════════════════
underperformers = setaside.get("underperforming_agencies", setaside.get("underperformers", []))
if underperformers:
    H.append(f"""<!-- ═══ SET-ASIDES ═══ -->
<div class="cat">SMALL BUSINESS</div>
<h2>{len(underperformers)} agencies scrambling to hit SB goals</h2>

<p>When agencies fall short, they flood the market with set-asides before Sept 30. Here are the gaps:</p>

<table class="ticker">""")
    AGENCY_SHORT = {
        "Department of Veterans Affairs": "VA",
        "Department of Defense (overall)": "DoD",
        "Department of Defense": "DoD",
        "Department of Energy": "DOE",
        "Department of Homeland Security": "DHS",
        "Department of Health and Human Services": "HHS",
    }
    for up in underperformers:
        gap = up.get("gap", "")
        dollar_gap = fmt_dollar(up.get("dollar_gap", up.get("dollar_gap_raw", "")))
        agency_name = AGENCY_SHORT.get(up["agency"], up["agency"])
        H.append(f'<tr><td><strong>{apos(agency_name)} &bull; {apos(up["category"])}</strong></td><td class="dn">{apos(gap)} gap</td><td class="dn">{dollar_gap} short</td></tr>')
    H.append('</table>\n')
    H.append('<p><strong>If you hold these certifications, target these agencies in Q3&ndash;Q4 FY26.</strong> The set-aside surge is coming.</p>\n\n<hr>\n')

# ══════════════════════════════════════
# PROTESTS — bold outcome + 1 sentence takeaway
# ══════════════════════════════════════
notable_decisions = protest.get("notable_decisions", protest.get("notable", []))
if notable_decisions:
    H.append("""<!-- ═══ PROTESTS ═══ -->
<div class="cat">PROTEST CORNER</div>

<ul>""")
    for pn in notable_decisions:
        outcome = pn.get("outcome", pn.get("status", "")).upper()
        case = pn.get("case", "")
        value = fmt_dollar(pn.get("contract_value", pn.get("value", "")))
        lesson = pn.get("lesson", pn.get("what_it_means", pn.get("bd_implication", "")))

        H.append(f'<li><strong>{apos(case)} ({value}) &mdash; {outcome}.</strong> {apos(trim(lesson, 2))}</li>')
    H.append('</ul>\n\n<hr>\n')

# ══════════════════════════════════════
# TO-DO LIST + CALENDAR
# ══════════════════════════════════════
H.append("""<!-- ═══ YOUR TO-DO LIST ═══ -->
<div class="box">
<div class="cat" style="margin-top:0">YOUR TO-DO LIST</div>

<ol style="padding-left:20px;margin:8px 0">""")

for ai in actions:
    deadline = ai.get("deadline", "")
    # Format deadline nicely
    if deadline:
        try:
            d = datetime.strptime(deadline, "%Y-%m-%d")
            due_str = f' (due {d.strftime("%b %d").replace(" 0", " ")})'
        except ValueError:
            due_str = f" (due {deadline})"
    else:
        due_str = ""
    H.append(f'<li style="margin-bottom:6px"><strong>{apos(ai["action"])}</strong>{due_str}</li>')

H.append('</ol>\n')

# Calendar — compact line
all_cal = []
for group in ["this_week", "next_two_weeks", "looking_ahead"]:
    for item in calendar_data.get(group, []):
        title = item.get("title", item.get("event", ""))
        date_raw = item.get("date", "")
        # Format date short
        try:
            d = datetime.strptime(date_raw, "%Y-%m-%d")
            date_fmt = d.strftime("%b %d").replace(" 0", " ")
        except ValueError:
            date_fmt = date_raw
        all_cal.append(f'{date_fmt} {apos(title)}')

if all_cal:
    H.append(f'<p class="small"><strong>Calendar:</strong> {" &bull; ".join(all_cal[:8])}</p>\n')

H.append('</div>\n\n<hr>\n')

# ══════════════════════════════════════
# ONE MORE THING
# ══════════════════════════════════════
H.append(f"""<!-- ═══ ONE MORE THING ═══ -->
<div class="cat">ONE MORE THING</div>
<h2>{apos(otw["headline"])}</h2>

<p><strong>{apos(trim(otw["description"], 2))}</strong></p>

<p>{apos(trim(otw["why_it_matters"], 3))}</p>
""")

# ══════════════════════════════════════
# CTA + FOOTER
# ══════════════════════════════════════
H.append("""<!-- ═══ CTA ═══ -->
<div class="cta">
  <p>This is the free edition. The full brief includes Is It Wired? signal analysis, all Bridge Watch contracts, and flash alerts.</p>
  <a href="#">See paid plans &rarr;</a>
</div>

<div class="fb">
  How&rsquo;d we do? <a href="#">&#128077;</a> <a href="#">&#128078;</a> &nbsp;&nbsp;&bull;&nbsp;&nbsp; <a href="#" style="font-size:14px">Forward to a colleague</a>
</div>

</div><!-- /pad -->

<div class="ftr">
  <p><span class="gold">GovCon Weekly Intelligence</span></p>
  <p>Data: USAspending &bull; SAM.gov &bull; GAO &bull; Federal Register &bull; SBA</p>
  <p>&copy; 2026 GovCon Weekly. <a href="#" style="color:#94a3b8">Unsubscribe</a></p>
</div>

</div>
</body>
</html>""")

# ── Write ──
output = "\n".join(H)
os.makedirs(os.path.dirname(OUT_FILE), exist_ok=True)
with open(OUT_FILE, "w") as f:
    f.write(output)

print(f"Generated: {OUT_FILE}")
print(f"Size: {len(output):,} bytes")
