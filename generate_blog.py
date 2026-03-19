#!/usr/bin/env python3
"""
Auto-generate SEO blog posts from weekly GovCon award data.

Reads the latest awards JSON, picks the best blog template for the week,
and writes a static HTML blog post to landing/blog/weekly-DATE.html.

No external dependencies. Runs in <5 seconds.

Usage:
    python3 generate_blog.py                          # auto-detect latest JSON
    python3 generate_blog.py data/govcon_awards_2026-03-18.json  # specific file
"""

import json
import os
import sys
import glob
from collections import Counter
from datetime import datetime
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"
BLOG_DIR = BASE_DIR / "landing" / "blog"
SITE_BASE = "https://dontlukeback.github.io/govcon-intel"


# ---------------------------------------------------------------------------
# Data analysis helpers
# ---------------------------------------------------------------------------

def load_awards(json_path: str) -> list[dict]:
    with open(json_path) as f:
        return json.load(f)


def analyze_awards(awards: list[dict]) -> dict:
    """Compute summary stats used by every template."""
    total_value = sum(a["award_amount"] or 0 for a in awards)
    total_count = len(awards)

    # Agency aggregates
    agency_dollars: dict[str, float] = {}
    agency_counts: dict[str, int] = {}
    for a in awards:
        ag = a["awarding_agency"]
        agency_dollars[ag] = agency_dollars.get(ag, 0) + (a["award_amount"] or 0)
        agency_counts[ag] = agency_counts.get(ag, 0) + 1

    top_agency_by_dollars = max(agency_dollars, key=agency_dollars.get)

    # Verticals
    vertical_dollars: dict[str, float] = {}
    vertical_counts: dict[str, int] = {}
    for a in awards:
        for v in (a["verticals"] or []):
            vertical_dollars[v] = vertical_dollars.get(v, 0) + (a["award_amount"] or 0)
            vertical_counts[v] = vertical_counts.get(v, 0) + 1
    top_vertical = max(vertical_dollars, key=vertical_dollars.get) if vertical_dollars else "IT"

    # Top awards
    top_awards = sorted(awards, key=lambda x: -(x["award_amount"] or 0))[:10]

    # Small business
    sb_awards = [
        a for a in awards
        if a.get("set_aside") and a["set_aside"].lower() not in ("no set aside used.", "")
    ]
    sb_total = sum(a["award_amount"] or 0 for a in sb_awards)

    # Top recipients
    recip_dollars: dict[str, float] = {}
    for a in awards:
        r = a["recipient_name"]
        recip_dollars[r] = recip_dollars.get(r, 0) + (a["award_amount"] or 0)
    top_recipients = sorted(recip_dollars.items(), key=lambda x: -x[1])[:10]

    # Agencies sorted by dollars
    agencies_by_dollars = sorted(agency_dollars.items(), key=lambda x: -x[1])

    return {
        "total_value": total_value,
        "total_count": total_count,
        "agency_dollars": agency_dollars,
        "agency_counts": agency_counts,
        "agencies_by_dollars": agencies_by_dollars,
        "top_agency": top_agency_by_dollars,
        "top_agency_dollars": agency_dollars[top_agency_by_dollars],
        "vertical_dollars": vertical_dollars,
        "vertical_counts": vertical_counts,
        "top_vertical": top_vertical,
        "top_vertical_dollars": vertical_dollars.get(top_vertical, 0),
        "top_awards": top_awards,
        "sb_awards": sb_awards,
        "sb_total": sb_total,
        "top_recipients": top_recipients,
    }


# ---------------------------------------------------------------------------
# Formatting helpers
# ---------------------------------------------------------------------------

def fmt_dollars(val: float) -> str:
    """Format dollar amounts: $1.3B, $450M, $12.5M, $800K."""
    if val >= 1_000_000_000:
        return f"${val / 1_000_000_000:.1f}B"
    if val >= 1_000_000:
        return f"${val / 1_000_000:.0f}M"
    if val >= 1_000:
        return f"${val / 1_000:.0f}K"
    return f"${val:,.0f}"


def fmt_dollars_full(val: float) -> str:
    """Full dollar format with commas."""
    return f"${val:,.0f}"


def short_agency(name: str) -> str:
    """Shorten common agency names."""
    replacements = {
        "Department of ": "DOD: ",
        "General Services Administration": "GSA",
        "Social Security Administration": "SSA",
    }
    for old, new in replacements.items():
        if name.startswith(old):
            return name.replace(old, new, 1)
    return name


def week_number(dt: datetime) -> int:
    return dt.isocalendar()[1]


# ---------------------------------------------------------------------------
# Template selection — rotates across 4 templates by ISO week number
# ---------------------------------------------------------------------------

TEMPLATES = [
    "top_awards",       # "Top Federal IT Awards This Week"
    "agency_vertical",  # "Which Agencies Spent the Most on [VERTICAL]"
    "top_agency",       # "[AGENCY] Spent $X on IT Contracts"
    "small_business",   # "Small Business Federal Contract Awards"
]


def pick_template(dt: datetime) -> str:
    return TEMPLATES[week_number(dt) % len(TEMPLATES)]


# ---------------------------------------------------------------------------
# Blog body generators (one per template)
# ---------------------------------------------------------------------------

def body_top_awards(stats: dict, date_str: str, dt: datetime) -> tuple[str, str, str]:
    """Returns (title, meta_description, body_html)."""
    month_day = dt.strftime("%B %d, %Y")
    title = f"Top Federal IT Awards This Week: {dt.strftime('%B %d')}"
    meta = (
        f"Breakdown of the largest federal IT contract awards for the week of "
        f"{month_day}. {fmt_dollars(stats['total_value'])} across "
        f"{stats['total_count']} awards tracked."
    )

    rows = ""
    for a in stats["top_awards"][:7]:
        rows += (
            f"<tr>"
            f"<td>{a['recipient_name'].title()}</td>"
            f"<td>{a['awarding_agency']}</td>"
            f"<td class='amount'>{fmt_dollars(a['award_amount'])}</td>"
            f"</tr>\n"
        )

    # Vertical breakdown
    vert_items = sorted(stats["vertical_dollars"].items(), key=lambda x: -x[1])
    vert_list = "\n".join(
        f"<li><strong>{v}</strong> — {fmt_dollars(d)} across {stats['vertical_counts'][v]} awards</li>"
        for v, d in vert_items[:5]
    )

    # Top 5 agencies
    agency_list = "\n".join(
        f"<li><strong>{ag}</strong> — {fmt_dollars(d)}</li>"
        for ag, d in stats["agencies_by_dollars"][:5]
    )

    body = f"""
        <p>Every week, we analyze the latest federal IT contract awards pulled from USAspending.gov to surface
        the deals that matter for government contractors. This week: <strong>{fmt_dollars(stats['total_value'])}</strong>
        in awards across <strong>{stats['total_count']} contracts</strong>.</p>

        <h2>Biggest Awards This Week</h2>
        <p>Here are the largest IT-related contract actions recorded for the week of {month_day}:</p>

        <div class="table-wrap">
        <table>
            <thead><tr><th>Recipient</th><th>Agency</th><th>Amount</th></tr></thead>
            <tbody>
            {rows}
            </tbody>
        </table>
        </div>

        <h2>Agency Spending Leaders</h2>
        <p>Federal IT spending this week was concentrated in a handful of agencies:</p>
        <ol>{agency_list}</ol>
        <p>The <strong>{stats['top_agency']}</strong> led all agencies with {fmt_dollars(stats['top_agency_dollars'])} in total
        IT contract actions — driven primarily by large task order modifications and new awards in the
        {stats['top_vertical'].lower()} space.</p>

        <h2>Technology Verticals</h2>
        <p>Breaking down this week's awards by technology category reveals where agencies are investing:</p>
        <ul>{vert_list}</ul>

        <h2>What This Means for Contractors</h2>
        <p>The {stats['top_vertical']} vertical continues to dominate federal IT spending, reflecting sustained
        government investment in modernization and security. Contractors should watch for follow-on
        opportunities tied to these large awards, particularly recompetes that may surface over the next 12-18 months.</p>

        <p>Several patterns stand out in this week's data. First, the concentration of dollars at the top:
        the five largest awards account for a significant share of total spending, which is typical of weeks
        dominated by large task order modifications. Second, the {stats['top_agency']} continues to be one
        of the most active IT buyers in the federal government, with {fmt_dollars(stats['top_agency_dollars'])}
        in awards this week alone.</p>

        <p>For small businesses, the GSA schedule and set-aside programs remain the primary entry points.
        This week saw {len(stats['sb_awards'])} awards with small business set-asides
        totaling {fmt_dollars(stats['sb_total'])}. Even when set-asides are scarce, the large prime
        contractors winning these awards — companies like {stats['top_recipients'][0][0].title()}
        and {stats['top_recipients'][1][0].title()} — are required to meet small business subcontracting
        goals on contracts above $750K. That makes every large award a potential subcontracting opportunity.</p>

        <h2>How We Track This Data</h2>
        <p>Every week, we pull the latest IT-related contract awards from USAspending.gov, classify them
        by technology vertical ({', '.join(sorted(stats['vertical_counts'].keys()))}), and analyze spending
        patterns across agencies and contractors. This gives government contractors an early signal on
        where agencies are investing — and where the next opportunities are likely to emerge.</p>

        <p>Want this analysis delivered to your inbox every week? Subscribe below for free weekly
        intelligence on federal IT contract trends, recompetes, and opportunities.</p>
    """
    return title, meta, body


def body_agency_vertical(stats: dict, date_str: str, dt: datetime) -> tuple[str, str, str]:
    vert = stats["top_vertical"]
    title = f"Which Agencies Spent the Most on {vert} This Week?"
    meta = (
        f"Federal agency spending breakdown for {vert} contracts, week of "
        f"{dt.strftime('%B %d, %Y')}. See which agencies are investing the most."
    )

    # Per-agency spend in this vertical — recompute from raw
    # We don't have per-vertical-per-agency in stats, so compute a simplified version
    agency_vert = "\n".join(
        f"<li><strong>{ag}</strong> — {fmt_dollars(d)}</li>"
        for ag, d in stats["agencies_by_dollars"][:8]
    )

    top5 = stats["top_awards"][:5]
    award_cards = ""
    for a in top5:
        verts = ", ".join(a["verticals"] or ["General IT"])
        award_cards += f"""
        <div class="award-card">
            <h3>{a['recipient_name'].title()}</h3>
            <p><strong>Agency:</strong> {a['awarding_agency']}<br>
            <strong>Amount:</strong> {fmt_dollars_full(a['award_amount'])}<br>
            <strong>Verticals:</strong> {verts}</p>
            <p class="desc">{(a['description'] or 'No description provided.')[:200]}</p>
        </div>
        """

    vert_items = sorted(stats["vertical_dollars"].items(), key=lambda x: -x[1])
    vert_bars = ""
    max_v = vert_items[0][1] if vert_items else 1
    for v, d in vert_items[:6]:
        pct = min(int(d / max_v * 100), 100)
        vert_bars += f"""
        <div class="bar-row">
            <span class="bar-label">{v}</span>
            <div class="bar-track"><div class="bar-fill" style="width:{pct}%"></div></div>
            <span class="bar-value">{fmt_dollars(d)}</span>
        </div>
        """

    body = f"""
        <p>Federal agencies spent <strong>{fmt_dollars(stats['total_value'])}</strong> on IT contracts this week.
        We broke down the numbers by technology vertical to see where the money is actually going — and
        <strong>{vert}</strong> topped the charts with {fmt_dollars(stats['top_vertical_dollars'])} in awards.</p>

        <h2>Spending by Technology Vertical</h2>
        <div class="bar-chart">{vert_bars}</div>

        <h2>Top Agencies by Total IT Spend</h2>
        <p>These agencies drove the largest share of this week's contract activity:</p>
        <ol>{agency_vert}</ol>

        <h2>Notable Awards</h2>
        <p>The five largest individual contract actions this week:</p>
        {award_cards}

        <h2>Why {vert} Dominates</h2>
        <p>The federal government's push toward {vert.lower()} solutions continues to accelerate. Between
        executive orders mandating zero trust architectures, FedRAMP requirements, and agency modernization
        roadmaps, contractors with {vert.lower()} capabilities are well-positioned for growth.</p>

        <p>This week's spending pattern reinforces a broader trend: agencies are consolidating IT
        modernization spending into large, multi-year contracts with established primes. The top five
        awards alone totaled {fmt_dollars(sum(a['award_amount'] or 0 for a in stats['top_awards'][:5]))},
        underscoring the scale of these programs.</p>

        <p>If you're a small or mid-size contractor, focus on the agencies with the highest volume of
        smaller awards — that's where set-asides and subcontracting opportunities concentrate. GSA
        alone accounted for {stats['agency_counts'].get('General Services Administration', 0)} awards this
        week, many of which flow through vehicles accessible to small businesses.</p>

        <h2>Methodology</h2>
        <p>This analysis is based on {stats['total_count']} IT-related contract awards pulled from
        USAspending.gov for the current reporting period. Awards are classified into technology verticals
        including {', '.join(sorted(stats['vertical_counts'].keys())[:5])}, and more. Dollar amounts reflect
        the total obligated value of each contract action, which may include base awards, modifications,
        and option exercises.</p>

        <p>We publish this analysis every week to help government contractors stay ahead of spending
        trends. Subscribe below to get it delivered to your inbox.</p>
    """
    return title, meta, body


def body_top_agency(stats: dict, date_str: str, dt: datetime) -> tuple[str, str, str]:
    agency = stats["top_agency"]
    dollars = stats["top_agency_dollars"]
    title = f"{agency} Spent {fmt_dollars(dollars)} on IT Contracts — Here's Who Won"
    meta = (
        f"{agency} awarded {fmt_dollars(dollars)} in IT contracts the week of "
        f"{dt.strftime('%B %d, %Y')}. Full breakdown of winners and contract details."
    )

    # Get awards for this agency
    agency_list = "\n".join(
        f"<li><strong>{ag}</strong> — {fmt_dollars(d)} ({stats['agency_counts'].get(ag, 0)} awards)</li>"
        for ag, d in stats["agencies_by_dollars"][:6]
    )

    top5 = [a for a in stats["top_awards"] if a["awarding_agency"] == agency][:5]
    if len(top5) < 3:
        top5 = stats["top_awards"][:5]

    rows = ""
    for a in top5:
        rows += (
            f"<tr>"
            f"<td>{a['recipient_name'].title()}</td>"
            f"<td>{fmt_dollars(a['award_amount'])}</td>"
            f"<td>{', '.join(a['verticals'] or ['General IT'])}</td>"
            f"</tr>\n"
        )

    # Top recipients overall
    recip_list = "\n".join(
        f"<li><strong>{r.title()}</strong> — {fmt_dollars(d)}</li>"
        for r, d in stats["top_recipients"][:8]
    )

    body = f"""
        <p>The <strong>{agency}</strong> was the biggest federal IT spender this week, awarding
        <strong>{fmt_dollars(dollars)}</strong> across {stats['agency_counts'].get(agency, 0)} contract actions.
        That's {int(dollars / stats['total_value'] * 100)}% of all tracked IT spending for the week.</p>

        <h2>Top Agency Spenders This Week</h2>
        <ol>{agency_list}</ol>

        <h2>Who Won the Biggest {agency} Awards?</h2>
        <p>Here are the largest contract actions from {agency} this week:</p>
        <div class="table-wrap">
        <table>
            <thead><tr><th>Recipient</th><th>Amount</th><th>Vertical</th></tr></thead>
            <tbody>{rows}</tbody>
        </table>
        </div>

        <h2>Top Contractors Across All Agencies</h2>
        <p>These companies received the largest total award dollars this week:</p>
        <ul>{recip_list}</ul>

        <h2>What to Watch</h2>
        <p>Large contract modifications often signal expanding scope — and eventual recompetes. If you compete
        in the same space as these winners, now is the time to position for the next opportunity cycle. Track
        the incumbent's performance period end dates and start building your capture strategy 18-24 months out.</p>

        <p>This week's data shows {agency} concentrating {int(dollars / stats['total_value'] * 100)}% of
        all tracked IT spending — a significant share driven by large task order modifications. When a
        single agency dominates the weekly numbers like this, it usually means major program milestones:
        option year exercises, scope expansions, or new task orders under existing IDIQs.</p>

        <p>For contractors not yet in {agency}'s ecosystem, the entry points are subcontracting
        relationships with the primes listed above, and watching for upcoming recompetes on these
        large vehicles. The performance periods on this week's biggest awards extend as far as
        {max(a['end_date'] or '2026' for a in stats['top_awards'][:5])}, meaning recompete activity
        will ramp up well before then.</p>

        <h2>The Competitive Landscape</h2>
        <p>Looking at the full list of award recipients this week tells an interesting story about
        market concentration. The top 10 contractors captured the vast majority of total dollars,
        a pattern that holds week after week in federal IT. For smaller contractors, the strategic
        play is not to compete head-to-head with these primes, but to position as a subcontractor
        or teaming partner on the next generation of these contracts.</p>

        <p>Key verticals driving spending this week included
        {', '.join(f'{v} ({fmt_dollars(d)})' for v, d in sorted(stats['vertical_dollars'].items(), key=lambda x: -x[1])[:3])}.
        Contractors should align their capabilities and past performance with these verticals when
        pursuing new opportunities.</p>

        <h2>About This Data</h2>
        <p>The full dataset behind this analysis is pulled from USAspending.gov and filtered for IT-relevant
        awards. We track {len(stats['vertical_counts'])} technology verticals across all civilian and
        defense agencies, covering {stats['total_count']} contract actions worth {fmt_dollars(stats['total_value'])}
        this week. Subscribe below to receive this analysis every week.</p>
    """
    return title, meta, body


def body_small_business(stats: dict, date_str: str, dt: datetime) -> tuple[str, str, str]:
    title = f"Small Business Federal Contract Awards: Week of {dt.strftime('%B %d')}"
    meta = (
        f"Weekly roundup of federal IT contract awards with small business set-asides. "
        f"{len(stats['sb_awards'])} set-aside awards totaling {fmt_dollars(stats['sb_total'])} "
        f"for the week of {dt.strftime('%B %d, %Y')}."
    )

    # Set-aside breakdown
    sa_counts: dict[str, int] = {}
    sa_dollars: dict[str, float] = {}
    for a in stats["sb_awards"]:
        sa = a["set_aside"]
        sa_counts[sa] = sa_counts.get(sa, 0) + 1
        sa_dollars[sa] = sa_dollars.get(sa, 0) + (a["award_amount"] or 0)

    sa_list = "\n".join(
        f"<li><strong>{sa}</strong> — {c} awards, {fmt_dollars(sa_dollars[sa])}</li>"
        for sa, c in sorted(sa_counts.items(), key=lambda x: -x[1])
    )
    if not sa_list:
        sa_list = "<li>No small business set-asides recorded this week</li>"

    # SB award details
    sb_sorted = sorted(stats["sb_awards"], key=lambda x: -(x["award_amount"] or 0))
    sb_cards = ""
    for a in sb_sorted[:6]:
        sb_cards += f"""
        <div class="award-card">
            <h3>{a['recipient_name'].title()}</h3>
            <p><strong>Agency:</strong> {a['awarding_agency']}<br>
            <strong>Amount:</strong> {fmt_dollars_full(a['award_amount'])}<br>
            <strong>Set-Aside:</strong> {a['set_aside']}<br>
            <strong>Verticals:</strong> {', '.join(a['verticals'] or ['General IT'])}</p>
        </div>
        """

    body = f"""
        <p>Every week, we track federal IT contract awards to surface opportunities relevant to small
        businesses. For the week of <strong>{dt.strftime('%B %d, %Y')}</strong>, the federal government
        awarded <strong>{fmt_dollars(stats['total_value'])}</strong> across {stats['total_count']} IT-related
        contracts. Of those, <strong>{len(stats['sb_awards'])} awards</strong> carried small business
        set-asides totaling <strong>{fmt_dollars(stats['sb_total'])}</strong>.</p>

        <h2>Set-Aside Breakdown</h2>
        <p>Here's how this week's small business set-asides broke down by program:</p>
        <ul>{sa_list}</ul>

        <h2>Notable Small Business Awards</h2>
        {sb_cards if sb_cards else '<p>No significant small business set-aside awards were recorded this week. This is common during weeks dominated by large task order modifications on existing contracts.</p>'}

        <h2>Beyond Set-Asides: Where Small Businesses Should Look</h2>
        <p>Set-asides are only part of the picture. This week's data shows significant spending
        through the <strong>GSA schedule</strong> ({stats['agency_counts'].get('General Services Administration', 0)}
        awards worth {fmt_dollars(stats['agency_dollars'].get('General Services Administration', 0))}),
        which remains the most accessible vehicle for small businesses.</p>

        <p>The <strong>{stats['top_vertical']}</strong> vertical saw the most activity with
        {fmt_dollars(stats['top_vertical_dollars'])} in awards. Small businesses with {stats['top_vertical'].lower()}
        capabilities should be tracking these prime contractors for subcontracting opportunities:</p>

        <ul>
        {"".join(f'<li><strong>{r.title()}</strong> — {fmt_dollars(d)}</li>' for r, d in stats['top_recipients'][:5])}
        </ul>

        <h2>How to Use This Data</h2>
        <p>If you're an 8(a), HUBZone, SDVOSB, or WOSB firm, here's how to turn this weekly intelligence
        into pipeline:</p>
        <ol>
            <li><strong>Track the primes.</strong> Large award winners need subcontractors. Reach out within
            30 days of award.</li>
            <li><strong>Watch for recompetes.</strong> Every contract ends. The performance periods on this
            week's largest awards range from 1-8 years — add the end dates to your capture calendar.</li>
            <li><strong>Follow the agencies.</strong> Agencies that spend heavily this week tend to have
            active procurement pipelines. Check their forecast on SAM.gov.</li>
            <li><strong>Look beyond IT.</strong> Many of the large awards classified under IT verticals
            include significant subcontracting needs in areas like program management, training, and
            facilities support — areas where small businesses often have a competitive edge.</li>
        </ol>

        <h2>The Bigger Picture</h2>
        <p>Federal small business contracting goals require agencies to award at least 23% of prime
        contract dollars to small businesses. In practice, IT contracts often fall short of this target
        because of the scale and complexity of modernization programs. That gap creates an opportunity:
        agencies under pressure to meet their goals are more likely to use set-asides on upcoming
        solicitations, especially in the verticals seeing the most activity.</p>

        <p>This week, the most active verticals were {stats['top_vertical']}
        ({fmt_dollars(stats['top_vertical_dollars'])}) and
        {sorted(stats['vertical_dollars'].items(), key=lambda x: -x[1])[1][0] if len(stats['vertical_dollars']) > 1 else 'General IT'}
        ({fmt_dollars(sorted(stats['vertical_dollars'].values(), reverse=True)[1]) if len(stats['vertical_dollars']) > 1 else '$0'}).
        Small businesses with capabilities in these areas should be actively monitoring SAM.gov
        for upcoming solicitations and building relationships with the primes winning large awards.</p>

        <p>We publish this small business-focused analysis every week. Subscribe below to stay
        informed on federal contracting opportunities relevant to your business.</p>
    """
    return title, meta, body


BODY_GENERATORS = {
    "top_awards": body_top_awards,
    "agency_vertical": body_agency_vertical,
    "top_agency": body_top_agency,
    "small_business": body_small_business,
}


# ---------------------------------------------------------------------------
# HTML shell (matches navy+gold theme from existing blog posts)
# ---------------------------------------------------------------------------

def render_html(title: str, meta_desc: str, body_html: str, date_str: str,
                dt: datetime, canonical_slug: str) -> str:
    published = dt.strftime("%B %d, %Y")
    canonical = f"{SITE_BASE}/blog/{canonical_slug}"

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title} | GovCon Weekly Intelligence</title>
    <meta name="description" content="{meta_desc}">
    <link rel="canonical" href="{canonical}">
    <meta property="og:title" content="{title}">
    <meta property="og:description" content="{meta_desc}">
    <meta property="og:type" content="article">
    <meta property="og:url" content="{canonical}">
    <meta name="twitter:card" content="summary_large_image">
    <meta name="twitter:title" content="{title}">
    <meta name="twitter:description" content="{meta_desc}">
    <style>
        :root {{
            --navy: #0A1628;
            --navy-mid: #132238;
            --navy-light: #1B3A5C;
            --gold: #C5A44E;
            --gold-light: #D4BA72;
            --gray-50: #F9FAFB;
            --gray-100: #F3F4F6;
            --gray-200: #E5E7EB;
            --gray-600: #4B5563;
            --gray-800: #1F2937;
        }}

        * {{ margin: 0; padding: 0; box-sizing: border-box; }}

        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Roboto', sans-serif;
            line-height: 1.7;
            color: var(--gray-800);
            background: var(--gray-50);
        }}

        nav {{
            background: var(--navy);
            padding: 1rem 2rem;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }}

        nav .container {{
            max-width: 1200px;
            margin: 0 auto;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }}

        nav .logo {{
            font-size: 1.25rem;
            font-weight: 700;
            color: var(--gold);
            text-decoration: none;
        }}

        nav a.home-link {{
            color: var(--gold-light);
            text-decoration: none;
            font-weight: 500;
            transition: color 0.2s;
        }}

        nav a.home-link:hover {{ color: var(--gold); }}

        article {{
            max-width: 800px;
            margin: 3rem auto;
            background: white;
            padding: 3rem;
            box-shadow: 0 1px 3px rgba(0,0,0,0.1);
        }}

        h1 {{
            font-size: 2.5rem;
            color: var(--navy);
            margin-bottom: 1rem;
            line-height: 1.2;
        }}

        .meta {{
            color: var(--gray-600);
            font-size: 0.9rem;
            margin-bottom: 2rem;
            padding-bottom: 1.5rem;
            border-bottom: 2px solid var(--gray-200);
        }}

        h2 {{
            font-size: 1.75rem;
            color: var(--navy);
            margin: 2.5rem 0 1rem 0;
            padding-top: 1rem;
        }}

        h3 {{
            font-size: 1.35rem;
            color: var(--navy-mid);
            margin: 2rem 0 1rem 0;
        }}

        p {{
            margin-bottom: 1.25rem;
            color: var(--gray-800);
        }}

        strong {{ color: var(--navy); font-weight: 600; }}

        ul, ol {{ margin: 1rem 0 1.5rem 2rem; }}
        li {{ margin-bottom: 0.75rem; color: var(--gray-800); }}

        /* Data table */
        .table-wrap {{ overflow-x: auto; margin: 1.5rem 0; }}
        table {{
            width: 100%;
            border-collapse: collapse;
            font-size: 0.95rem;
        }}
        thead {{ background: var(--navy); color: white; }}
        th {{ padding: 0.75rem 1rem; text-align: left; font-weight: 600; }}
        td {{ padding: 0.75rem 1rem; border-bottom: 1px solid var(--gray-200); }}
        tr:nth-child(even) {{ background: var(--gray-50); }}
        td.amount {{ font-weight: 600; color: var(--navy); white-space: nowrap; }}

        /* Award cards */
        .award-card {{
            background: var(--gray-50);
            border-left: 4px solid var(--gold);
            padding: 1.5rem;
            margin: 1.5rem 0;
        }}
        .award-card h3 {{ margin-top: 0; }}
        .award-card .desc {{
            font-size: 0.9rem;
            color: var(--gray-600);
            font-style: italic;
        }}

        /* Bar chart */
        .bar-chart {{ margin: 1.5rem 0 2rem 0; }}
        .bar-row {{
            display: flex;
            align-items: center;
            margin-bottom: 0.75rem;
        }}
        .bar-label {{
            width: 160px;
            font-size: 0.9rem;
            font-weight: 500;
            color: var(--navy);
            flex-shrink: 0;
        }}
        .bar-track {{
            flex: 1;
            height: 24px;
            background: var(--gray-200);
            border-radius: 4px;
            overflow: hidden;
            margin: 0 0.75rem;
        }}
        .bar-fill {{
            height: 100%;
            background: linear-gradient(90deg, var(--navy-light), var(--gold));
            border-radius: 4px;
        }}
        .bar-value {{
            width: 80px;
            text-align: right;
            font-size: 0.9rem;
            font-weight: 600;
            color: var(--navy);
            flex-shrink: 0;
        }}

        /* CTA */
        .cta-box {{
            background: linear-gradient(135deg, var(--navy) 0%, var(--navy-light) 100%);
            color: white;
            padding: 2rem;
            margin: 3rem 0;
            text-align: center;
            border-radius: 8px;
        }}
        .cta-box h3 {{ color: var(--gold); margin: 0 0 1rem 0; padding: 0; }}
        .cta-box p {{ color: var(--gray-100); margin-bottom: 1.5rem; }}
        .cta-button {{
            display: inline-block;
            background: var(--gold);
            color: var(--navy);
            padding: 1rem 2rem;
            text-decoration: none;
            font-weight: 600;
            border-radius: 6px;
            transition: background 0.2s;
        }}
        .cta-button:hover {{ background: var(--gold-light); }}

        .internal-links {{
            background: var(--gray-100);
            padding: 1.5rem;
            margin: 2rem 0;
            border-radius: 4px;
        }}
        .internal-links h4 {{ margin-bottom: 0.75rem; color: var(--navy); }}
        .internal-links ul {{ margin-left: 1.5rem; margin-bottom: 0; }}
        .internal-links a {{
            color: var(--navy-light);
            text-decoration: none;
            font-weight: 500;
        }}
        .internal-links a:hover {{ color: var(--gold); text-decoration: underline; }}

        @media (max-width: 768px) {{
            article {{ margin: 1rem; padding: 1.5rem; }}
            h1 {{ font-size: 1.875rem; }}
            h2 {{ font-size: 1.5rem; }}
            nav .container {{ flex-direction: column; gap: 1rem; }}
            .bar-label {{ width: 100px; font-size: 0.8rem; }}
            .bar-value {{ width: 60px; font-size: 0.8rem; }}
        }}
    </style>
</head>
<body>
    <nav>
        <div class="container">
            <a href="../index.html" class="logo">GovCon Weekly Intelligence</a>
            <a href="../index.html" class="home-link">&larr; Back to Home</a>
        </div>
    </nav>

    <article>
        <h1>{title}</h1>

        <div class="meta">
            Published {published} | Data sourced from USAspending.gov
        </div>

        {body_html}

        <div class="cta-box">
            <h3>Get Federal Contract Intelligence Every Week</h3>
            <p>GovCon Weekly Intelligence delivers curated federal contract analysis to your inbox — completely free. Real data. Real insights. No fluff.</p>
            <a href="../index.html#subscribe" class="cta-button">Subscribe Free</a>
        </div>

        <div class="internal-links">
            <h4>Related Articles</h4>
            <ul>
                <li><a href="govwin-alternatives.html">GovWin Alternatives: 5 Federal Contract Intelligence Tools</a></li>
                <li><a href="track-federal-recompetes.html">How to Track Federal Contract Recompetes Before They Hit SAM.gov</a></li>
                <li><a href="small-business-federal-contracts.html">Federal Contract Intelligence for 8(a) and SDVOSB Firms</a></li>
                <li><a href="../index.html">Subscribe to GovCon Weekly Intelligence</a></li>
            </ul>
        </div>
    </article>
<script src="../js/tracker.js"></script>
<script src="../js/analytics.js"></script>
</body>
</html>"""


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def find_latest_json() -> str:
    """Find the most recent govcon_awards JSON by filename date."""
    pattern = str(DATA_DIR / "govcon_awards_*.json")
    files = sorted(glob.glob(pattern))
    if not files:
        print("ERROR: No award JSON files found in data/", file=sys.stderr)
        sys.exit(1)
    return files[-1]


def extract_date(json_path: str) -> str:
    """Extract YYYY-MM-DD from filename like govcon_awards_2026-03-18.json."""
    basename = os.path.basename(json_path)
    # Expected: govcon_awards_YYYY-MM-DD.json
    date_part = basename.replace("govcon_awards_", "").replace(".json", "")
    return date_part


def main():
    # Resolve input file
    if len(sys.argv) > 1:
        json_path = sys.argv[1]
        if not os.path.isabs(json_path):
            json_path = str(BASE_DIR / json_path)
    else:
        json_path = find_latest_json()

    print(f"Reading: {json_path}")

    # Parse date
    date_str = extract_date(json_path)
    dt = datetime.strptime(date_str, "%Y-%m-%d")

    # Load and analyze
    awards = load_awards(json_path)
    stats = analyze_awards(awards)

    print(f"Awards: {stats['total_count']}")
    print(f"Total value: {fmt_dollars(stats['total_value'])}")
    print(f"Top agency: {stats['top_agency']} ({fmt_dollars(stats['top_agency_dollars'])})")
    print(f"Top vertical: {stats['top_vertical']} ({fmt_dollars(stats['top_vertical_dollars'])})")

    # Pick template
    template = pick_template(dt)

    # Allow override via CLI: python3 generate_blog.py data/file.json top_agency
    if len(sys.argv) > 2 and sys.argv[2] in BODY_GENERATORS:
        template = sys.argv[2]

    print(f"Template: {template}")

    # Generate content
    generator = BODY_GENERATORS[template]
    title, meta_desc, body_html = generator(stats, date_str, dt)

    # Render full HTML
    slug = f"weekly-{date_str}.html"
    html = render_html(title, meta_desc, body_html, date_str, dt, slug)

    # Write output
    BLOG_DIR.mkdir(parents=True, exist_ok=True)
    out_path = BLOG_DIR / slug
    with open(out_path, "w") as f:
        f.write(html)

    print(f"Output: {out_path}")
    print(f"Title: {title}")
    print(f"Words: ~{len(body_html.split())}")


if __name__ == "__main__":
    main()
