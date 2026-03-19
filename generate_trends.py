#!/usr/bin/env python3
"""Generate a 'Trends' markdown section from the GovCon historical archive.

Reads all_awards.json (12K+ awards) and historical_stats.json, then produces
a self-contained markdown block ready to paste into the weekly newsletter.

Usage:
    python3 generate_trends.py --output output/trends_2026-03-19.md
    python3 generate_trends.py  # defaults to output/trends_YYYY-MM-DD.md
"""

import argparse
import json
import os
import statistics
from collections import Counter, defaultdict
from datetime import datetime

BASE = os.path.dirname(os.path.abspath(__file__))
ARCHIVE_DIR = os.path.join(BASE, "data", "archive")
ALL_AWARDS = os.path.join(ARCHIVE_DIR, "all_awards.json")
HIST_STATS = os.path.join(ARCHIVE_DIR, "historical_stats.json")

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def iso_week(date_str):
    """Return ISO week string like '2026-W03' from a date string."""
    try:
        dt = datetime.strptime(date_str, "%Y-%m-%d")
        yr, wk, _ = dt.isocalendar()
        return f"{yr}-W{wk:02d}"
    except (ValueError, TypeError):
        return None


def fmt_dollar(val):
    """Format dollar amount with appropriate suffix."""
    if abs(val) >= 1_000_000_000:
        return f"${val / 1_000_000_000:,.1f}B"
    if abs(val) >= 1_000_000:
        return f"${val / 1_000_000:,.1f}M"
    if abs(val) >= 1_000:
        return f"${val / 1_000:,.0f}K"
    return f"${val:,.0f}"


def pct_change(current, baseline):
    """Return percentage change; handle zero baseline."""
    if baseline == 0:
        return 0.0
    return ((current - baseline) / baseline) * 100


def trend_arrow(pct):
    if pct > 5:
        return "up"
    if pct < -5:
        return "down"
    return "flat"


# ---------------------------------------------------------------------------
# Core week detection
# ---------------------------------------------------------------------------

def detect_core_weeks(awards, min_awards_per_week=50):
    """Identify the contiguous block of collection weeks with real volume.

    Returns a sorted list of ISO week strings representing the core period.
    Uses a density scan: walks backward from the most recent big week and
    only keeps weeks that are within 2 weeks of each other (allowing small
    gaps but breaking on sparse historical data).
    """
    week_counts = Counter()
    for a in awards:
        wk = iso_week(a.get("start_date", ""))
        if wk:
            week_counts[wk] += 1

    # Keep only weeks with meaningful volume
    big_weeks = sorted(w for w, c in week_counts.items() if c >= min_awards_per_week)

    if not big_weeks:
        return sorted(week_counts.keys())

    # Walk backward from most recent big week; break if gap > 2 weeks
    run = [big_weeks[-1]]
    for w in reversed(big_weeks[:-1]):
        if _week_distance(w, run[-1]) <= 2:
            run.append(w)
        else:
            break
    run.reverse()

    # Trim trailing partial/incomplete weeks (< 25% of the run average)
    while len(run) >= 3:
        counts = [week_counts[w] for w in run]
        avg_prior = statistics.mean(counts[:-1])
        if counts[-1] < avg_prior * 0.25:
            run = run[:-1]
        else:
            break

    return run


def _week_distance(w1, w2):
    """Rough distance in weeks between two ISO week strings."""
    def _to_num(w):
        parts = w.split("-W")
        return int(parts[0]) * 52 + int(parts[1])
    return abs(_to_num(w1) - _to_num(w2))


# ---------------------------------------------------------------------------
# Build per-week breakdowns from raw awards
# ---------------------------------------------------------------------------

def build_weekly_data(awards, core_weeks):
    """Build per-week aggregations from raw award data."""
    core_set = set(core_weeks)
    weekly = defaultdict(lambda: {
        "count": 0,
        "value": 0.0,
        "agencies": Counter(),
        "recipients": Counter(),
        "verticals": Counter(),
    })

    for a in awards:
        wk = iso_week(a.get("start_date", ""))
        if wk not in core_set:
            continue
        w = weekly[wk]
        w["count"] += 1
        w["value"] += a.get("award_amount", 0) or 0
        agency = a.get("awarding_agency", "Unknown")
        w["agencies"][agency] += 1
        recip = a.get("recipient_name", "Unknown")
        w["recipients"][recip] += 1
        for v in (a.get("verticals") or []):
            w["verticals"][v] += 1

    return weekly


# ---------------------------------------------------------------------------
# Section generators
# ---------------------------------------------------------------------------

def section_this_week_vs_avg(weekly, core_weeks):
    """Section 1: This Week vs. Average."""
    current_week = core_weeks[-1]
    current = weekly[current_week]
    all_counts = [weekly[w]["count"] for w in core_weeks]
    all_values = [weekly[w]["value"] for w in core_weeks]

    avg_count = statistics.mean(all_counts)
    avg_value = statistics.mean(all_values)
    n_weeks = len(core_weeks)

    count_pct = pct_change(current["count"], avg_count)
    value_pct = pct_change(current["value"], avg_value)

    direction_count = "above" if count_pct >= 0 else "below"
    direction_value = "above" if value_pct >= 0 else "below"

    lines = [
        "## This Week vs. Average",
        "",
        f"**{current['count']:,}** awards tracked in **{current_week}**. "
        f"{n_weeks}-week average: **{avg_count:,.0f}**. "
        f"**{abs(count_pct):.0f}% {direction_count} average.**",
        "",
        f"Total obligated value this week: **{fmt_dollar(current['value'])}** "
        f"({n_weeks}-week avg: {fmt_dollar(avg_value)}, "
        f"{abs(value_pct):.0f}% {direction_value} average).",
        "",
    ]
    return "\n".join(lines)


def section_top_movers(weekly, core_weeks, top_n=3):
    """Section 2: Top 3 Movers — contractors with biggest volume change."""
    current_week = core_weeks[-1]
    prior_weeks = core_weeks[:-1]

    if not prior_weeks:
        return "## Top 3 Movers\n\n*Insufficient historical data.*\n"

    # Average weekly count per contractor over prior weeks
    contractor_weekly = defaultdict(lambda: defaultdict(int))
    for w in core_weeks:
        for c, cnt in weekly[w]["recipients"].items():
            contractor_weekly[c][w] = cnt

    movers = []
    for c, wk_data in contractor_weekly.items():
        current_count = wk_data.get(current_week, 0)
        prior_counts = [wk_data.get(w, 0) for w in prior_weeks]
        avg_prior = statistics.mean(prior_counts) if prior_counts else 0

        if avg_prior < 1 and current_count < 3:
            continue  # skip noise

        abs_change = current_count - avg_prior
        pct = pct_change(current_count, avg_prior) if avg_prior > 0 else (100 if current_count > 0 else 0)
        movers.append((c, current_count, avg_prior, abs_change, pct))

    # Sort by absolute change magnitude (biggest swings)
    movers.sort(key=lambda x: abs(x[3]), reverse=True)

    lines = ["## Top 3 Movers", ""]
    lines.append("Contractors with the largest shift in award volume vs. their historical weekly average:")
    lines.append("")

    for c, curr, avg, delta, pct in movers[:top_n]:
        direction = "up" if delta > 0 else "down"
        sign = "+" if delta > 0 else ""
        # Clean up ALL-CAPS names but preserve common business suffixes
        name = c.title() if c.isupper() else c
        for old, new in [("Llc", "LLC"), (" Inc.", " Inc."), (" Inc,", " Inc.,"),
                         (" Corp.", " Corp."), (" Corp,", " Corp.,"), ("L.l.c.", "LLC")]:
            name = name.replace(old, new)
        lines.append(
            f"- **{name}** — {curr} awards this week vs. {avg:.1f} avg "
            f"({sign}{delta:.1f}, {direction} {abs(pct):.0f}%)"
        )

    lines.append("")
    return "\n".join(lines)


def section_agency_trends(weekly, core_weeks, top_n=5):
    """Section 3: Agency Spending Trends — top 5 by % change WoW."""
    if len(core_weeks) < 2:
        return "## Agency Spending Trends\n\n*Need at least 2 weeks of data.*\n"

    current_week = core_weeks[-1]
    prev_week = core_weeks[-2]

    current_agencies = weekly[current_week]["agencies"]
    prev_agencies = weekly[prev_week]["agencies"]

    all_agencies = set(current_agencies.keys()) | set(prev_agencies.keys())

    changes = []
    for agency in all_agencies:
        curr = current_agencies.get(agency, 0)
        prev = prev_agencies.get(agency, 0)
        if prev == 0 and curr == 0:
            continue
        if prev == 0:
            pct = 100.0  # new entrant
        else:
            pct = pct_change(curr, prev)
        changes.append((agency, curr, prev, pct))

    # Sort by absolute % change
    changes.sort(key=lambda x: abs(x[3]), reverse=True)

    lines = ["## Agency Spending Trends", ""]
    lines.append(f"Top movers by award count, **{prev_week}** to **{current_week}**:")
    lines.append("")
    lines.append("| Agency | Last Week | This Week | Change |")
    lines.append("|--------|-----------|-----------|--------|")

    for agency, curr, prev, pct in changes[:top_n]:
        sign = "+" if pct >= 0 else ""
        lines.append(f"| {agency} | {prev} | {curr} | {sign}{pct:.0f}% |")

    lines.append("")
    return "\n".join(lines)


def section_vertical_heat_map(weekly, core_weeks):
    """Section 4: Vertical Heat Map — HOT / STEADY / COOLING."""
    if len(core_weeks) < 4:
        return "## Vertical Heat Map\n\n*Need at least 4 weeks for trend detection.*\n"

    current_week = core_weeks[-1]
    n_weeks = len(core_weeks)

    # Compute per-vertical weekly counts
    vert_weekly = defaultdict(lambda: defaultdict(int))
    for w in core_weeks:
        for v, cnt in weekly[w]["verticals"].items():
            vert_weekly[v][w] = cnt

    lines = ["## Vertical Heat Map", ""]
    lines.append(f"Based on {n_weeks} weeks of award data:")
    lines.append("")

    heat_rows = []
    for vert, wk_data in sorted(vert_weekly.items()):
        counts = [wk_data.get(w, 0) for w in core_weeks]
        avg_all = statistics.mean(counts)

        # Recent 3 weeks vs. prior
        recent = counts[-3:]
        prior = counts[:-3] if len(counts) > 3 else counts
        avg_recent = statistics.mean(recent)
        avg_prior = statistics.mean(prior) if prior else avg_all

        pct = pct_change(avg_recent, avg_prior)
        current_count = counts[-1]

        if pct > 15:
            tag = "HOT"
        elif pct < -15:
            tag = "COOLING"
        else:
            tag = "STEADY"

        heat_rows.append((vert, tag, current_count, avg_all, pct))

    # Sort: HOT first, then STEADY, then COOLING
    order = {"HOT": 0, "STEADY": 1, "COOLING": 2}
    heat_rows.sort(key=lambda x: (order.get(x[1], 1), -abs(x[4])))

    lines.append("| Vertical | Status | This Week | Avg/Week | Trend |")
    lines.append("|----------|--------|-----------|----------|-------|")
    for vert, tag, curr, avg, pct in heat_rows:
        sign = "+" if pct >= 0 else ""
        lines.append(f"| {vert} | **{tag}** | {curr} | {avg:.0f} | {sign}{pct:.0f}% |")

    lines.append("")
    return "\n".join(lines)


def section_prediction(weekly, core_weeks):
    """Section 5: Prediction — linear trend extrapolation to end of Q2."""
    if len(core_weeks) < 4:
        return "## Looking Ahead\n\n*Need more data for projections.*\n"

    # Compute per-vertical weekly counts and find strongest trend
    vert_weekly = defaultdict(lambda: defaultdict(int))
    for w in core_weeks:
        for v, cnt in weekly[w]["verticals"].items():
            vert_weekly[v][w] = cnt

    # Simple linear regression per vertical
    best = None
    best_slope = 0
    worst = None
    worst_slope = 0

    vert_stats = {}
    for vert, wk_data in vert_weekly.items():
        counts = [wk_data.get(w, 0) for w in core_weeks]
        if sum(counts) < 20:
            continue  # skip very low-volume verticals

        n = len(counts)
        xs = list(range(n))
        x_mean = statistics.mean(xs)
        y_mean = statistics.mean(counts)

        numerator = sum((x - x_mean) * (y - y_mean) for x, y in zip(xs, counts))
        denominator = sum((x - x_mean) ** 2 for x in xs)
        slope = numerator / denominator if denominator else 0

        # Slope as % of mean
        slope_pct = (slope / y_mean * 100) if y_mean else 0
        vert_stats[vert] = {
            "slope": slope,
            "slope_pct": slope_pct,
            "mean": y_mean,
            "current": counts[-1],
            "total": sum(counts),
        }

        if slope_pct > best_slope or best is None:
            best_slope = slope_pct
            best = vert
        if slope_pct < worst_slope or worst is None:
            worst_slope = slope_pct
            worst = vert

    # Project forward: weeks remaining to end of Q2 (2026-W26)
    current_week_num = int(core_weeks[-1].split("-W")[1])
    weeks_to_q2_end = max(26 - current_week_num, 1)
    n_weeks = len(core_weeks)

    lines = ["## Looking Ahead", ""]

    if best and vert_stats[best]["slope_pct"] > 5:
        bs = vert_stats[best]
        projected = bs["current"] + (bs["slope"] * weeks_to_q2_end)
        growth_pct = pct_change(projected, bs["mean"])
        caveat = ""
        if abs(growth_pct) > 100:
            caveat = " (Note: steep trajectory — likely to moderate as baselines adjust.)"
        lines.append(
            f"Based on {n_weeks} weeks of data, **{best}** is on track to "
            f"**grow {abs(growth_pct):.0f}%** above its weekly average by end of Q2 "
            f"(projected ~{max(int(projected), 0)} awards/week vs. {bs['mean']:.0f} avg).{caveat}"
        )
    else:
        lines.append("No verticals show strong sustained growth over the tracking period.")

    if worst and vert_stats[worst]["slope_pct"] < -5 and worst != best:
        ws = vert_stats[worst]
        projected = ws["current"] + (ws["slope"] * weeks_to_q2_end)
        decline_pct = pct_change(projected, ws["mean"])
        lines.append("")
        lines.append(
            f"Conversely, **{worst}** is trending downward — projected to "
            f"**decline {abs(decline_pct):.0f}%** below average by end of Q2 "
            f"(~{max(int(projected), 0)} awards/week vs. {ws['mean']:.0f} avg)."
        )

    # Add a brief summary table of all vertical trajectories
    lines.append("")
    lines.append("**Vertical trajectory summary:**")
    lines.append("")
    lines.append("| Vertical | Trend (per week) | Projection |")
    lines.append("|----------|------------------|------------|")

    for vert in sorted(vert_stats.keys(), key=lambda v: vert_stats[v]["slope_pct"], reverse=True):
        vs = vert_stats[vert]
        direction = "growing" if vs["slope"] > 0.5 else ("declining" if vs["slope"] < -0.5 else "stable")
        sign = "+" if vs["slope_pct"] >= 0 else ""
        lines.append(f"| {vert} | {sign}{vs['slope_pct']:.1f}%/wk | {direction} |")

    lines.append("")
    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(description="Generate GovCon trend insights from historical archive.")
    parser.add_argument(
        "--output", "-o",
        default=os.path.join(BASE, "output", f"trends_{datetime.now().strftime('%Y-%m-%d')}.md"),
        help="Output markdown file path",
    )
    parser.add_argument(
        "--min-week-volume", type=int, default=50,
        help="Minimum awards per week to be considered a core collection week (default: 50)",
    )
    args = parser.parse_args()

    # Load data
    print(f"Loading awards from {ALL_AWARDS}...")
    with open(ALL_AWARDS) as f:
        awards = json.load(f)
    print(f"  {len(awards):,} total awards loaded.")

    # Detect core weeks
    core_weeks = detect_core_weeks(awards, min_awards_per_week=args.min_week_volume)
    print(f"  {len(core_weeks)} core weeks detected: {core_weeks[0]} to {core_weeks[-1]}")

    # Build weekly breakdowns from raw data
    weekly = build_weekly_data(awards, core_weeks)

    total_core = sum(weekly[w]["count"] for w in core_weeks)
    print(f"  {total_core:,} awards in core period.")

    # Generate sections
    sections = [
        "---",
        "",
        "# Trend Insights",
        "",
        f"*{len(core_weeks)}-week historical analysis "
        f"({core_weeks[0]} through {core_weeks[-1]}) "
        f"| {total_core:,} awards tracked*",
        "",
        section_this_week_vs_avg(weekly, core_weeks),
        section_top_movers(weekly, core_weeks),
        section_agency_trends(weekly, core_weeks),
        section_vertical_heat_map(weekly, core_weeks),
        section_prediction(weekly, core_weeks),
        "---",
    ]

    output = "\n".join(sections)

    # Ensure output directory exists
    os.makedirs(os.path.dirname(os.path.abspath(args.output)), exist_ok=True)

    with open(args.output, "w") as f:
        f.write(output)

    print(f"\nTrends written to {args.output}")
    print(f"({len(output):,} characters, ready to append to newsletter)")


if __name__ == "__main__":
    main()
