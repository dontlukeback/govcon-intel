#!/usr/bin/env python3
"""
GovCon Historical Trend Analysis
Reads the cumulative all_awards.json and generates trend reports.

Gets MORE valuable every week as data accumulates.
- Week 1: Baseline snapshot
- Week 4+: Agency spending trends emerge
- Week 12+: Contractor win streaks, seasonal patterns
- Week 52+: Year-over-year comparisons

Usage:
    python3 historical_analysis.py                  # full report
    python3 historical_analysis.py --weeks 4        # last N weeks only
    python3 historical_analysis.py --vertical AI/ML # filter by vertical
    python3 historical_analysis.py --json           # output JSON only

Output:
    data/archive/historical_report.md   (markdown report)
    data/archive/historical_stats.json  (machine-readable stats)
"""

import argparse
import json
import os
import sys
from collections import Counter, defaultdict
from datetime import datetime

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ARCHIVE_DIR = os.path.join(BASE_DIR, "data", "archive")
MASTER_FILE = os.path.join(ARCHIVE_DIR, "all_awards.json")
STATS_FILE = os.path.join(ARCHIVE_DIR, "stats.json")
REPORT_FILE = os.path.join(ARCHIVE_DIR, "historical_report.md")
HIST_STATS_FILE = os.path.join(ARCHIVE_DIR, "historical_stats.json")


def load_json(filepath):
    if not os.path.exists(filepath):
        return []
    with open(filepath) as f:
        return json.load(f)


def save_json(data, filepath):
    with open(filepath, "w") as f:
        json.dump(data, f, indent=2, default=str)


def iso_week(date_str: str) -> str:
    """Convert YYYY-MM-DD to ISO week label like '2026-W12'."""
    try:
        dt = datetime.strptime(date_str, "%Y-%m-%d")
        iso = dt.isocalendar()
        return f"{iso[0]}-W{iso[1]:02d}"
    except (ValueError, TypeError):
        return "unknown"


def parse_amount(val) -> float:
    if isinstance(val, (int, float)):
        return float(val)
    return 0.0


# ---------------------------------------------------------------------------
# Analysis Functions
# ---------------------------------------------------------------------------
def awards_per_week(awards: list) -> dict:
    """Count awards and total value per ISO week based on start_date."""
    weeks = defaultdict(lambda: {"count": 0, "value": 0.0, "agencies": set(), "recipients": set()})
    for a in awards:
        w = iso_week(a.get("start_date", ""))
        weeks[w]["count"] += 1
        weeks[w]["value"] += parse_amount(a.get("award_amount"))
        ag = a.get("awarding_agency")
        if ag:
            weeks[w]["agencies"].add(ag)
        r = a.get("recipient_name")
        if r:
            weeks[w]["recipients"].add(r)

    # Convert sets to counts for JSON serialization
    result = {}
    for w in sorted(weeks.keys()):
        d = weeks[w]
        result[w] = {
            "count": d["count"],
            "value": round(d["value"], 2),
            "unique_agencies": len(d["agencies"]),
            "unique_recipients": len(d["recipients"]),
        }
    return result


def agency_spending_trends(awards: list) -> dict:
    """Track spending by agency over time."""
    agency_weeks = defaultdict(lambda: defaultdict(lambda: {"count": 0, "value": 0.0}))
    agency_totals = Counter()

    for a in awards:
        ag = a.get("awarding_agency", "Unknown")
        w = iso_week(a.get("start_date", ""))
        agency_weeks[ag][w]["count"] += 1
        agency_weeks[ag][w]["value"] += parse_amount(a.get("award_amount"))
        agency_totals[ag] += parse_amount(a.get("award_amount"))

    # Return top 15 agencies by total value
    top_agencies = [ag for ag, _ in agency_totals.most_common(15)]
    result = {}
    for ag in top_agencies:
        weeks_data = agency_weeks[ag]
        result[ag] = {
            "total_value": round(agency_totals[ag], 2),
            "total_awards": sum(d["count"] for d in weeks_data.values()),
            "weeks": {w: {"count": d["count"], "value": round(d["value"], 2)}
                      for w, d in sorted(weeks_data.items())},
        }
    return result


def contractor_win_rates(awards: list) -> dict:
    """Track contractor wins over time — who's on a streak?"""
    contractor_data = defaultdict(lambda: {
        "total_awards": 0,
        "total_value": 0.0,
        "agencies": set(),
        "verticals": Counter(),
        "weeks_active": set(),
    })

    for a in awards:
        r = a.get("recipient_name", "Unknown")
        contractor_data[r]["total_awards"] += 1
        contractor_data[r]["total_value"] += parse_amount(a.get("award_amount"))
        ag = a.get("awarding_agency")
        if ag:
            contractor_data[r]["agencies"].add(ag)
        for v in a.get("verticals", []):
            contractor_data[r]["verticals"][v] += 1
        w = iso_week(a.get("start_date", ""))
        contractor_data[r]["weeks_active"].add(w)

    # Sort by total value, return top 20
    sorted_contractors = sorted(
        contractor_data.items(), key=lambda x: x[1]["total_value"], reverse=True
    )[:20]

    result = {}
    for name, d in sorted_contractors:
        result[name] = {
            "total_awards": d["total_awards"],
            "total_value": round(d["total_value"], 2),
            "unique_agencies": len(d["agencies"]),
            "top_verticals": dict(d["verticals"].most_common(5)),
            "weeks_active": len(d["weeks_active"]),
            "agency_diversification": sorted(d["agencies"]),
        }
    return result


def vertical_trends(awards: list) -> dict:
    """Track vertical growth/decline over time."""
    vert_weeks = defaultdict(lambda: defaultdict(lambda: {"count": 0, "value": 0.0}))
    vert_totals = defaultdict(lambda: {"count": 0, "value": 0.0})

    for a in awards:
        w = iso_week(a.get("start_date", ""))
        for v in a.get("verticals", []):
            vert_weeks[v][w]["count"] += 1
            vert_weeks[v][w]["value"] += parse_amount(a.get("award_amount"))
            vert_totals[v]["count"] += 1
            vert_totals[v]["value"] += parse_amount(a.get("award_amount"))

    result = {}
    for v in sorted(vert_totals.keys(), key=lambda x: vert_totals[x]["value"], reverse=True):
        weeks_data = vert_weeks[v]
        sorted_weeks = sorted(weeks_data.keys())

        # Calculate week-over-week trend if we have 2+ weeks
        wow_trend = None
        if len(sorted_weeks) >= 2:
            recent = weeks_data[sorted_weeks[-1]]["count"]
            prior = weeks_data[sorted_weeks[-2]]["count"]
            if prior > 0:
                wow_trend = round((recent - prior) / prior * 100, 1)

        result[v] = {
            "total_awards": vert_totals[v]["count"],
            "total_value": round(vert_totals[v]["value"], 2),
            "weeks_present": len(sorted_weeks),
            "wow_trend_pct": wow_trend,
            "weekly_breakdown": {
                w: {"count": d["count"], "value": round(d["value"], 2)}
                for w, d in sorted(weeks_data.items())
            },
        }
    return result


def data_moat_score(stats: dict, weeks_archived: int) -> dict:
    """Quantify the competitive moat of the historical dataset."""
    total = stats.get("total_awards", 0)
    weeks = max(weeks_archived, 1)

    # Time to replicate: a competitor starting today needs this many weeks
    # to accumulate the same data (assuming same ~1100/week rate)
    replication_weeks = weeks

    return {
        "total_records": total,
        "weeks_of_data": weeks,
        "avg_awards_per_week": round(total / weeks, 1),
        "replication_time_weeks": replication_weeks,
        "moat_strength": (
            "nascent" if weeks < 4 else
            "emerging" if weeks < 12 else
            "established" if weeks < 26 else
            "strong" if weeks < 52 else
            "dominant"
        ),
        "unlocked_analyses": [
            "baseline_snapshot" if weeks >= 1 else None,
            "week_over_week_trends" if weeks >= 2 else None,
            "monthly_patterns" if weeks >= 4 else None,
            "contractor_win_streaks" if weeks >= 8 else None,
            "seasonal_patterns" if weeks >= 12 else None,
            "quarterly_comparisons" if weeks >= 13 else None,
            "half_year_trends" if weeks >= 26 else None,
            "year_over_year" if weeks >= 52 else None,
        ],
    }


# ---------------------------------------------------------------------------
# Report Generation
# ---------------------------------------------------------------------------
def fmt_usd(val: float) -> str:
    if val >= 1_000_000_000:
        return f"${val/1_000_000_000:.1f}B"
    if val >= 1_000_000:
        return f"${val/1_000_000:.1f}M"
    if val >= 1_000:
        return f"${val/1_000:.0f}K"
    return f"${val:.0f}"


def generate_markdown_report(
    weekly: dict,
    agencies: dict,
    contractors: dict,
    verticals: dict,
    moat: dict,
    cumulative_stats: dict,
) -> str:
    """Generate a markdown trend report."""
    now = datetime.now().strftime("%Y-%m-%d %H:%M")
    weeks_count = moat["weeks_of_data"]

    lines = [
        f"# GovCon Historical Trend Report",
        f"",
        f"*Generated: {now} | Data: {weeks_count} week(s) | "
        f"{moat['total_records']:,} awards | Moat: {moat['moat_strength']}*",
        f"",
        f"---",
        f"",
    ]

    # Data Moat Status
    lines.append("## Data Moat Status")
    lines.append("")
    lines.append(f"- **Records accumulated:** {moat['total_records']:,}")
    lines.append(f"- **Weeks of data:** {moat['weeks_of_data']}")
    lines.append(f"- **Avg awards/week:** {moat['avg_awards_per_week']}")
    lines.append(f"- **Time for competitor to replicate:** {moat['replication_time_weeks']} weeks")
    lines.append(f"- **Moat strength:** {moat['moat_strength']}")
    unlocked = [a for a in moat["unlocked_analyses"] if a]
    lines.append(f"- **Unlocked analyses:** {', '.join(unlocked)}")
    lines.append("")

    # Weekly Overview
    lines.append("## Awards Per Week")
    lines.append("")
    lines.append("| Week | Awards | Value | Agencies | Recipients |")
    lines.append("|------|--------|-------|----------|------------|")
    for w, d in weekly.items():
        lines.append(
            f"| {w} | {d['count']:,} | {fmt_usd(d['value'])} | "
            f"{d['unique_agencies']} | {d['unique_recipients']} |"
        )
    lines.append("")

    # Agency Spending
    lines.append("## Top Agencies by Spending")
    lines.append("")
    lines.append("| Agency | Awards | Total Value |")
    lines.append("|--------|--------|-------------|")
    for ag, d in agencies.items():
        lines.append(f"| {ag} | {d['total_awards']:,} | {fmt_usd(d['total_value'])} |")
    lines.append("")

    # Contractor Leaderboard
    lines.append("## Top Contractors")
    lines.append("")
    lines.append("| Contractor | Awards | Value | Agencies | Weeks Active |")
    lines.append("|-----------|--------|-------|----------|-------------|")
    for name, d in contractors.items():
        lines.append(
            f"| {name} | {d['total_awards']} | {fmt_usd(d['total_value'])} | "
            f"{d['unique_agencies']} | {d['weeks_active']} |"
        )
    lines.append("")

    # Vertical Trends
    lines.append("## Vertical Trends")
    lines.append("")
    lines.append("| Vertical | Awards | Value | Weeks | WoW Trend |")
    lines.append("|----------|--------|-------|-------|-----------|")
    for v, d in verticals.items():
        trend = f"{d['wow_trend_pct']:+.1f}%" if d.get("wow_trend_pct") is not None else "N/A (need 2+ weeks)"
        lines.append(
            f"| {v} | {d['total_awards']:,} | {fmt_usd(d['total_value'])} | "
            f"{d['weeks_present']} | {trend} |"
        )
    lines.append("")

    # What's Next
    if weeks_count < 4:
        lines.append("## Next Milestones")
        lines.append("")
        lines.append(f"- **Week 2:** Week-over-week trends unlock")
        lines.append(f"- **Week 4:** Monthly patterns visible, agency spending trends emerge")
        lines.append(f"- **Week 8:** Contractor win streaks identifiable")
        lines.append(f"- **Week 12:** Seasonal patterns, quarterly comparisons")
        lines.append(f"- **Week 52:** Year-over-year analysis, full seasonal model")
        lines.append("")

    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------
def main():
    parser = argparse.ArgumentParser(description="GovCon historical trend analysis")
    parser.add_argument("--weeks", type=int, help="Limit to last N weeks")
    parser.add_argument("--vertical", help="Filter to specific vertical")
    parser.add_argument("--json", action="store_true", help="Output JSON stats only")
    args = parser.parse_args()

    # Load data
    awards = load_json(MASTER_FILE)
    if not awards:
        print("No historical data yet. Run archive_data.py first.")
        sys.exit(1)

    cumulative_stats = load_json(STATS_FILE)
    if isinstance(cumulative_stats, list):
        cumulative_stats = {}

    print(f"Loaded {len(awards):,} awards from historical archive")

    # Optional filters
    if args.vertical:
        awards = [a for a in awards if args.vertical in a.get("verticals", [])]
        print(f"Filtered to {len(awards):,} awards in vertical: {args.vertical}")

    if args.weeks:
        # Get the last N weeks by ISO week
        all_weeks = sorted(set(iso_week(a.get("start_date", "")) for a in awards))
        keep_weeks = set(all_weeks[-args.weeks:])
        awards = [a for a in awards if iso_week(a.get("start_date", "")) in keep_weeks]
        print(f"Filtered to last {args.weeks} weeks: {len(awards):,} awards")

    # Run analyses
    weekly = awards_per_week(awards)
    agencies = agency_spending_trends(awards)
    contractors = contractor_win_rates(awards)
    verts = vertical_trends(awards)
    weeks_archived = cumulative_stats.get("weeks_archived", 1)
    moat = data_moat_score(cumulative_stats, weeks_archived)

    # Build combined stats
    hist_stats = {
        "generated_at": datetime.now().isoformat(),
        "total_awards_analyzed": len(awards),
        "moat": moat,
        "weekly_summary": weekly,
        "agency_trends": agencies,
        "contractor_leaderboard": contractors,
        "vertical_trends": verts,
    }

    # Save JSON stats
    save_json(hist_stats, HIST_STATS_FILE)

    if args.json:
        print(json.dumps(hist_stats, indent=2, default=str))
        return

    # Generate and save markdown report
    report = generate_markdown_report(weekly, agencies, contractors, verts, moat, cumulative_stats)
    with open(REPORT_FILE, "w") as f:
        f.write(report)

    print(f"\nReport saved: {REPORT_FILE}")
    print(f"Stats saved:  {HIST_STATS_FILE}")
    print(f"\nMoat strength: {moat['moat_strength']} ({moat['weeks_of_data']} weeks)")
    print(f"Unlocked: {', '.join(a for a in moat['unlocked_analyses'] if a)}")


if __name__ == "__main__":
    main()
