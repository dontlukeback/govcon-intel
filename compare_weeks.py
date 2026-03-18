#!/usr/bin/env python3
"""
GovCon Intelligence -- Week-over-Week Comparison Report

Compares two weeks of awards data and produces a markdown comparison report
highlighting trends, new entrants, emerging recipients, and agency movers.

Usage:
    python3 compare_weeks.py --current data/govcon_awards_2026-03-18.json --previous data/govcon_awards_2026-03-11.json --output output/comparison.md
    python3 compare_weeks.py --current data/govcon_awards_2026-03-18.json --previous data/govcon_awards_2026-03-11.json

No external dependencies (stdlib only).
"""

import argparse
import json
import os
import random
import sys
from collections import defaultdict
from datetime import datetime

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
OUTPUT_DIR = os.path.join(SCRIPT_DIR, "output")

SMALL_BIZ_KEYWORDS = ["8(a)", "SDVOSB", "HUBZONE", "WOSB", "EDWOSB", "Small Business"]

# ---------------------------------------------------------------------------
# Helpers (matching generate_report.py conventions)
# ---------------------------------------------------------------------------

def fmt_dollars(amount):
    """Format dollar amount with appropriate scale."""
    if amount is None:
        return "N/A"
    raw = abs(amount)
    sign = "-" if amount < 0 else ""
    if raw >= 1_000_000_000:
        return f"{sign}${raw / 1_000_000_000:.2f}B"
    elif raw >= 1_000_000:
        return f"{sign}${raw / 1_000_000:.1f}M"
    elif raw >= 1_000:
        return f"{sign}${raw / 1_000:.0f}K"
    else:
        return f"{sign}${raw:,.0f}"


def safe_amount(award):
    """Safely extract award_amount as a float, defaulting to 0."""
    val = award.get("award_amount")
    if val is None:
        return 0.0
    try:
        return float(val)
    except (ValueError, TypeError):
        return 0.0


def safe_str(val, default="N/A"):
    """Return string or default for None/empty."""
    if val is None or (isinstance(val, str) and not val.strip()):
        return default
    return str(val).strip()


def load_awards(path):
    """Load and validate the awards JSON file. Returns a list of dicts."""
    if not os.path.exists(path):
        print(f"ERROR: Data file not found: {path}", file=sys.stderr)
        sys.exit(1)

    with open(path) as f:
        data = json.load(f)

    if isinstance(data, list):
        return data
    elif isinstance(data, dict):
        for key in ("awards", "results", "data", "items"):
            if key in data and isinstance(data[key], list):
                return data[key]
        return [data]
    else:
        print(f"ERROR: Unexpected data format in {path}", file=sys.stderr)
        sys.exit(1)


def pct_change(current, previous):
    """Calculate percentage change, handling zero division."""
    if previous == 0:
        return float("inf") if current > 0 else 0.0
    return ((current - previous) / previous) * 100


def fmt_change(value, is_pct=False):
    """Format a change value with +/- sign."""
    sign = "+" if value >= 0 else ""
    if is_pct:
        if value == float("inf"):
            return "NEW"
        return f"{sign}{value:.1f}%"
    return f"{sign}{fmt_dollars(value)}"


def extract_date_from_path(path):
    """Try to extract a date string from a filename like govcon_awards_2026-03-18.json."""
    try:
        basename = os.path.basename(path).replace(".json", "")
        parts = basename.split("_")
        candidate = parts[-1]
        datetime.strptime(candidate, "%Y-%m-%d")
        return candidate
    except (ValueError, IndexError):
        return None


def is_small_biz(award):
    """Check if an award has a small business set-aside."""
    sa = safe_str(award.get("set_aside"), "")
    return any(kw.lower() in sa.lower() for kw in SMALL_BIZ_KEYWORDS)


# ---------------------------------------------------------------------------
# Aggregation helpers
# ---------------------------------------------------------------------------

def aggregate_by_recipient(awards):
    """Return {recipient: {count, total_value, agencies, verticals}}."""
    data = defaultdict(lambda: {"count": 0, "total_value": 0.0, "agencies": set(), "verticals": set()})
    for a in awards:
        name = safe_str(a.get("recipient_name"), "Unknown")
        data[name]["count"] += 1
        data[name]["total_value"] += safe_amount(a)
        agency = a.get("awarding_agency")
        if agency:
            data[name]["agencies"].add(agency)
        for v in (a.get("verticals") or []):
            data[name]["verticals"].add(v)
    return dict(data)


def aggregate_by_agency(awards):
    """Return {agency: {count, total_value}}."""
    data = defaultdict(lambda: {"count": 0, "total_value": 0.0})
    for a in awards:
        agency = safe_str(a.get("awarding_agency"), "Unknown Agency")
        data[agency]["count"] += 1
        data[agency]["total_value"] += safe_amount(a)
    return dict(data)


def aggregate_by_vertical(awards):
    """Return {vertical: {count, total_value}}."""
    data = defaultdict(lambda: {"count": 0, "total_value": 0.0})
    for a in awards:
        verticals = a.get("verticals") or []
        if not verticals:
            verticals = ["Untagged"]
        for v in verticals:
            data[v]["count"] += 1
            data[v]["total_value"] += safe_amount(a)
    return dict(data)


def aggregate_by_set_aside(awards):
    """Return {set_aside: {count, total_value}}."""
    data = defaultdict(lambda: {"count": 0, "total_value": 0.0})
    for a in awards:
        sa = safe_str(a.get("set_aside"), "None / Not Specified")
        data[sa]["count"] += 1
        data[sa]["total_value"] += safe_amount(a)
    return dict(data)


# ---------------------------------------------------------------------------
# Report sections
# ---------------------------------------------------------------------------

def build_header(current_date, previous_date, current_count, previous_count,
                 current_value, previous_value):
    """Build the report header and week-over-week summary."""
    lines = []
    lines.append("# GovCon Intelligence: Week-over-Week Comparison")
    lines.append("")
    lines.append(f"**Current Week:** {current_date or 'N/A'} | "
                 f"**Previous Week:** {previous_date or 'N/A'}")
    lines.append(f"**Generated:** {datetime.now().strftime('%B %d, %Y at %H:%M')}")
    lines.append("")
    lines.append("---")
    lines.append("")

    # Week-over-Week Summary
    lines.append("## Week-over-Week Summary")
    lines.append("")

    count_chg = pct_change(current_count, previous_count)
    value_chg = pct_change(current_value, previous_value)
    count_delta = current_count - previous_count
    value_delta = current_value - previous_value

    lines.append("| Metric | Previous | Current | Change | % Change |")
    lines.append("|--------|----------|---------|--------|----------|")
    lines.append(f"| Total Awards | {previous_count:,} | {current_count:,} | "
                 f"{'+' if count_delta >= 0 else ''}{count_delta:,} | "
                 f"{fmt_change(count_chg, is_pct=True)} |")
    lines.append(f"| Total Value | {fmt_dollars(previous_value)} | {fmt_dollars(current_value)} | "
                 f"{fmt_change(value_delta)} | {fmt_change(value_chg, is_pct=True)} |")

    # Average award value
    prev_avg = previous_value / previous_count if previous_count > 0 else 0
    curr_avg = current_value / current_count if current_count > 0 else 0
    avg_chg = pct_change(curr_avg, prev_avg)
    lines.append(f"| Avg Award Value | {fmt_dollars(prev_avg)} | {fmt_dollars(curr_avg)} | "
                 f"{fmt_change(curr_avg - prev_avg)} | {fmt_change(avg_chg, is_pct=True)} |")

    lines.append("")
    return "\n".join(lines)


def build_new_recipients(curr_by_recipient, prev_by_recipient, top_n=15):
    """Companies that appear this week but not last week."""
    lines = []
    lines.append("## New Recipients")
    lines.append("")
    lines.append("*Companies receiving awards this week that did not appear last week -- potential new market entrants.*")
    lines.append("")

    prev_names = {name.upper() for name in prev_by_recipient}
    new = []
    for name, data in curr_by_recipient.items():
        if name.upper() not in prev_names:
            new.append((name, data))

    if not new:
        lines.append("*No new recipients this week.*")
        lines.append("")
        return "\n".join(lines)

    new.sort(key=lambda x: x[1]["total_value"], reverse=True)

    lines.append(f"**{len(new):,} new recipients** this week (top {min(top_n, len(new))} by value):")
    lines.append("")
    lines.append("| Recipient | Awards | Total Value | Agencies |")
    lines.append("|-----------|--------|-------------|----------|")

    for name, data in new[:top_n]:
        agencies = ", ".join(sorted(data["agencies"]))
        lines.append(f"| {name} | {data['count']:,} | {fmt_dollars(data['total_value'])} | {agencies} |")

    lines.append("")
    return "\n".join(lines)


def build_emerging_recipients(curr_by_recipient, prev_by_recipient, top_n=15):
    """Companies whose award value grew significantly (>2x or >$1M increase)."""
    lines = []
    lines.append("## Emerging Recipients")
    lines.append("")
    lines.append("*Companies whose award value grew significantly (>2x increase or >$1M absolute increase).*")
    lines.append("")

    prev_names_upper = {name.upper(): name for name in prev_by_recipient}
    emerging = []

    for name, curr_data in curr_by_recipient.items():
        prev_name = prev_names_upper.get(name.upper())
        if prev_name is None:
            continue  # New recipient, handled separately
        prev_data = prev_by_recipient[prev_name]
        curr_val = curr_data["total_value"]
        prev_val = prev_data["total_value"]
        abs_increase = curr_val - prev_val

        if prev_val > 0 and (curr_val >= 2 * prev_val or abs_increase >= 1_000_000):
            chg = pct_change(curr_val, prev_val)
            emerging.append((name, curr_val, prev_val, abs_increase, chg))

    if not emerging:
        lines.append("*No emerging recipients this week.*")
        lines.append("")
        return "\n".join(lines)

    emerging.sort(key=lambda x: x[3], reverse=True)  # Sort by absolute increase

    lines.append(f"**{len(emerging):,} emerging recipients** (top {min(top_n, len(emerging))}):")
    lines.append("")
    lines.append("| Recipient | Previous | Current | Increase | % Change |")
    lines.append("|-----------|----------|---------|----------|----------|")

    for name, curr_val, prev_val, abs_inc, chg in emerging[:top_n]:
        lines.append(f"| {name} | {fmt_dollars(prev_val)} | {fmt_dollars(curr_val)} | "
                     f"{fmt_change(abs_inc)} | {fmt_change(chg, is_pct=True)} |")

    lines.append("")
    return "\n".join(lines)


def build_agency_movers(curr_by_agency, prev_by_agency, top_n=10):
    """Agencies with biggest spend changes (up and down)."""
    lines = []
    lines.append("## Agency Movers")
    lines.append("")
    lines.append("*Agencies with the biggest changes in award spending.*")
    lines.append("")

    all_agencies = set(curr_by_agency.keys()) | set(prev_by_agency.keys())
    changes = []
    for agency in all_agencies:
        curr_val = curr_by_agency.get(agency, {}).get("total_value", 0)
        prev_val = prev_by_agency.get(agency, {}).get("total_value", 0)
        curr_cnt = curr_by_agency.get(agency, {}).get("count", 0)
        prev_cnt = prev_by_agency.get(agency, {}).get("count", 0)
        delta = curr_val - prev_val
        chg = pct_change(curr_val, prev_val)
        changes.append((agency, prev_val, curr_val, delta, chg, prev_cnt, curr_cnt))

    if not changes:
        lines.append("*No agency data available.*")
        lines.append("")
        return "\n".join(lines)

    # Top gainers
    gainers = sorted([c for c in changes if c[3] > 0], key=lambda x: x[3], reverse=True)
    decliners = sorted([c for c in changes if c[3] < 0], key=lambda x: x[3])

    if gainers:
        lines.append(f"### Biggest Gainers")
        lines.append("")
        lines.append("| Agency | Previous | Current | Change | % Change |")
        lines.append("|--------|----------|---------|--------|----------|")
        for agency, prev_val, curr_val, delta, chg, prev_cnt, curr_cnt in gainers[:top_n]:
            lines.append(f"| {agency} | {fmt_dollars(prev_val)} | {fmt_dollars(curr_val)} | "
                         f"{fmt_change(delta)} | {fmt_change(chg, is_pct=True)} |")
        lines.append("")

    if decliners:
        lines.append(f"### Biggest Decliners")
        lines.append("")
        lines.append("| Agency | Previous | Current | Change | % Change |")
        lines.append("|--------|----------|---------|--------|----------|")
        for agency, prev_val, curr_val, delta, chg, prev_cnt, curr_cnt in decliners[:top_n]:
            lines.append(f"| {agency} | {fmt_dollars(prev_val)} | {fmt_dollars(curr_val)} | "
                         f"{fmt_change(delta)} | {fmt_change(chg, is_pct=True)} |")
        lines.append("")

    return "\n".join(lines)


def build_vertical_trends(curr_by_vertical, prev_by_vertical):
    """Which verticals are growing/shrinking by count and value."""
    lines = []
    lines.append("## Vertical Trends")
    lines.append("")

    all_verticals = set(curr_by_vertical.keys()) | set(prev_by_vertical.keys())
    if "Untagged" in all_verticals:
        all_verticals.discard("Untagged")  # Handle separately at end

    trends = []
    for vertical in all_verticals:
        curr_cnt = curr_by_vertical.get(vertical, {}).get("count", 0)
        prev_cnt = prev_by_vertical.get(vertical, {}).get("count", 0)
        curr_val = curr_by_vertical.get(vertical, {}).get("total_value", 0)
        prev_val = prev_by_vertical.get(vertical, {}).get("total_value", 0)
        cnt_chg = pct_change(curr_cnt, prev_cnt)
        val_chg = pct_change(curr_val, prev_val)
        val_delta = curr_val - prev_val
        trends.append((vertical, prev_cnt, curr_cnt, cnt_chg, prev_val, curr_val, val_delta, val_chg))

    if not trends:
        lines.append("*No vertical data available.*")
        lines.append("")
        return "\n".join(lines)

    # Sort by absolute value change
    trends.sort(key=lambda x: abs(x[6]), reverse=True)

    lines.append("| Vertical | Prev Count | Curr Count | Count Change | Prev Value | Curr Value | Value Change |")
    lines.append("|----------|------------|------------|--------------|------------|------------|--------------|")

    for (vertical, prev_cnt, curr_cnt, cnt_chg, prev_val, curr_val,
         val_delta, val_chg) in trends:
        # Trend indicator
        if val_delta > 0:
            trend = "^"  # up arrow
        elif val_delta < 0:
            trend = "v"  # down arrow
        else:
            trend = "="
        lines.append(
            f"| {trend} {vertical} | {prev_cnt:,} | {curr_cnt:,} | "
            f"{fmt_change(cnt_chg, is_pct=True)} | {fmt_dollars(prev_val)} | "
            f"{fmt_dollars(curr_val)} | {fmt_change(val_chg, is_pct=True)} |"
        )

    lines.append("")
    return "\n".join(lines)


def build_hot_contracts(current_awards, current_value, current_count):
    """Awards this week that are notably larger than the weekly average."""
    lines = []
    lines.append("## Hot Contracts")
    lines.append("")
    lines.append("*Awards this week that are notably larger than the weekly average.*")
    lines.append("")

    if current_count == 0:
        lines.append("*No awards data available.*")
        lines.append("")
        return "\n".join(lines)

    avg = current_value / current_count
    threshold = max(avg * 5, 10_000_000)  # 5x average or $10M, whichever is higher

    hot = [a for a in current_awards if safe_amount(a) >= threshold]
    hot.sort(key=lambda a: safe_amount(a), reverse=True)

    if not hot:
        lines.append(f"*No awards exceeded the hot-contract threshold of {fmt_dollars(threshold)} "
                     f"(5x the weekly average of {fmt_dollars(avg)}).*")
        lines.append("")
        return "\n".join(lines)

    lines.append(f"**{len(hot):,} awards** exceeded {fmt_dollars(threshold)} "
                 f"(5x the weekly average of {fmt_dollars(avg)}):")
    lines.append("")

    for i, a in enumerate(hot[:15], 1):
        amount = safe_amount(a)
        recipient = safe_str(a.get("recipient_name"), "Unknown")
        agency = safe_str(a.get("awarding_agency"), "Unknown")
        description = safe_str(a.get("description"), "No description")
        if len(description) > 200:
            description = description[:197].rsplit(" ", 1)[0] + "..."
        verticals = ", ".join(a.get("verticals") or ["Untagged"])
        multiplier = amount / avg if avg > 0 else 0

        lines.append(f"**{i}. {fmt_dollars(amount)}** -- {recipient}")
        lines.append(f"   - Agency: {agency} | Verticals: {verticals}")
        lines.append(f"   - {multiplier:.0f}x weekly average")
        lines.append(f"   - {description}")
        lines.append("")

    return "\n".join(lines)


def build_set_aside_trends(curr_by_sa, prev_by_sa, current_awards, previous_awards):
    """Changes in small business set-aside patterns."""
    lines = []
    lines.append("## Set-Aside Trends")
    lines.append("")

    # Overall small biz summary
    curr_sb_count = sum(1 for a in current_awards if is_small_biz(a))
    curr_sb_value = sum(safe_amount(a) for a in current_awards if is_small_biz(a))
    prev_sb_count = sum(1 for a in previous_awards if is_small_biz(a))
    prev_sb_value = sum(safe_amount(a) for a in previous_awards if is_small_biz(a))

    curr_total = sum(safe_amount(a) for a in current_awards) or 1
    prev_total = sum(safe_amount(a) for a in previous_awards) or 1

    curr_sb_share = (curr_sb_value / curr_total) * 100
    prev_sb_share = (prev_sb_value / prev_total) * 100

    lines.append("### Small Business Overall")
    lines.append("")
    lines.append("| Metric | Previous | Current | Change |")
    lines.append("|--------|----------|---------|--------|")
    lines.append(f"| SB Award Count | {prev_sb_count:,} | {curr_sb_count:,} | "
                 f"{fmt_change(pct_change(curr_sb_count, prev_sb_count), is_pct=True)} |")
    lines.append(f"| SB Award Value | {fmt_dollars(prev_sb_value)} | {fmt_dollars(curr_sb_value)} | "
                 f"{fmt_change(pct_change(curr_sb_value, prev_sb_value), is_pct=True)} |")
    lines.append(f"| SB Share of Total Value | {prev_sb_share:.1f}% | {curr_sb_share:.1f}% | "
                 f"{'+' if curr_sb_share >= prev_sb_share else ''}{curr_sb_share - prev_sb_share:.1f}pp |")
    lines.append("")

    # By set-aside type
    all_types = set(curr_by_sa.keys()) | set(prev_by_sa.keys())
    type_changes = []
    for sa_type in all_types:
        curr_cnt = curr_by_sa.get(sa_type, {}).get("count", 0)
        prev_cnt = prev_by_sa.get(sa_type, {}).get("count", 0)
        curr_val = curr_by_sa.get(sa_type, {}).get("total_value", 0)
        prev_val = prev_by_sa.get(sa_type, {}).get("total_value", 0)
        val_delta = curr_val - prev_val
        val_chg = pct_change(curr_val, prev_val)
        type_changes.append((sa_type, prev_cnt, curr_cnt, prev_val, curr_val, val_delta, val_chg))

    type_changes.sort(key=lambda x: abs(x[5]), reverse=True)

    lines.append("### By Set-Aside Type")
    lines.append("")
    lines.append("| Set-Aside | Prev Count | Curr Count | Prev Value | Curr Value | Value Change |")
    lines.append("|-----------|------------|------------|------------|------------|--------------|")

    for sa_type, prev_cnt, curr_cnt, prev_val, curr_val, val_delta, val_chg in type_changes:
        lines.append(
            f"| {sa_type} | {prev_cnt:,} | {curr_cnt:,} | "
            f"{fmt_dollars(prev_val)} | {fmt_dollars(curr_val)} | "
            f"{fmt_change(val_chg, is_pct=True)} |"
        )

    lines.append("")
    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Synthetic prior data (for testing with a single week)
# ---------------------------------------------------------------------------

def generate_synthetic_previous(awards, sample_rate=0.80, seed=42):
    """
    Generate a synthetic 'previous week' by sampling a subset of current awards.
    Useful for testing when only one week of data exists.
    """
    rng = random.Random(seed)
    sampled = [a for a in awards if rng.random() < sample_rate]
    return sampled


# ---------------------------------------------------------------------------
# Report assembly
# ---------------------------------------------------------------------------

def generate_comparison_report(current_awards, previous_awards, current_path, previous_path):
    """Assemble the full comparison markdown report."""
    current_date = extract_date_from_path(current_path) if current_path else None
    previous_date = extract_date_from_path(previous_path) if previous_path else None

    current_count = len(current_awards)
    previous_count = len(previous_awards)
    current_value = sum(safe_amount(a) for a in current_awards)
    previous_value = sum(safe_amount(a) for a in previous_awards)

    curr_by_recipient = aggregate_by_recipient(current_awards)
    prev_by_recipient = aggregate_by_recipient(previous_awards)
    curr_by_agency = aggregate_by_agency(current_awards)
    prev_by_agency = aggregate_by_agency(previous_awards)
    curr_by_vertical = aggregate_by_vertical(current_awards)
    prev_by_vertical = aggregate_by_vertical(previous_awards)
    curr_by_sa = aggregate_by_set_aside(current_awards)
    prev_by_sa = aggregate_by_set_aside(previous_awards)

    parts = []

    parts.append(build_header(current_date, previous_date,
                              current_count, previous_count,
                              current_value, previous_value))
    parts.append("---\n")
    parts.append(build_new_recipients(curr_by_recipient, prev_by_recipient))
    parts.append("---\n")
    parts.append(build_emerging_recipients(curr_by_recipient, prev_by_recipient))
    parts.append("---\n")
    parts.append(build_agency_movers(curr_by_agency, prev_by_agency))
    parts.append("---\n")
    parts.append(build_vertical_trends(curr_by_vertical, prev_by_vertical))
    parts.append("---\n")
    parts.append(build_hot_contracts(current_awards, current_value, current_count))
    parts.append("---\n")
    parts.append(build_set_aside_trends(curr_by_sa, prev_by_sa, current_awards, previous_awards))
    parts.append("---\n")

    # Footer
    parts.append("*Generated by GovCon Intelligence Pipeline -- Week-over-Week Comparison*")
    parts.append(f"*Data source: USAspending.gov*")
    parts.append("")

    return "\n".join(parts)


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(
        description="GovCon Week-over-Week Comparison Report",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python3 compare_weeks.py --current data/govcon_awards_2026-03-18.json --previous data/govcon_awards_2026-03-11.json
  python3 compare_weeks.py --current data/govcon_awards_2026-03-18.json --previous data/govcon_awards_2026-03-11.json --output output/comparison.md
  python3 compare_weeks.py --current data/govcon_awards_2026-03-18.json --synthetic
        """
    )
    parser.add_argument("--current", required=True,
                        help="Path to this week's awards JSON")
    parser.add_argument("--previous", default=None,
                        help="Path to last week's awards JSON")
    parser.add_argument("--output", default=None,
                        help="Path to output markdown file")
    parser.add_argument("--synthetic", action="store_true",
                        help="Generate synthetic previous week (80%% sample of current) for testing")

    args = parser.parse_args()

    # Resolve output path
    output_path = args.output or os.path.join(OUTPUT_DIR, "comparison.md")

    print(f"GovCon Week-over-Week Comparison", file=sys.stderr)
    print(f"  Current:  {args.current}", file=sys.stderr)

    # Load current data
    current_awards = load_awards(args.current)
    print(f"  Loaded current: {len(current_awards):,} awards", file=sys.stderr)

    # Load or generate previous data
    if args.synthetic or args.previous is None:
        if args.previous is not None:
            print(f"  NOTE: --synthetic flag overrides --previous", file=sys.stderr)
        previous_awards = generate_synthetic_previous(current_awards)
        previous_path = "(synthetic 80% sample)"
        print(f"  Previous: synthetic ({len(previous_awards):,} awards, 80% sample)", file=sys.stderr)
    else:
        previous_awards = load_awards(args.previous)
        previous_path = args.previous
        print(f"  Loaded previous: {len(previous_awards):,} awards", file=sys.stderr)

    print(f"  Output:   {output_path}", file=sys.stderr)
    print("", file=sys.stderr)

    # Generate report
    report = generate_comparison_report(current_awards, previous_awards,
                                        args.current, previous_path)

    # Write output
    os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
    with open(output_path, "w") as f:
        f.write(report)

    line_count = report.count("\n")
    word_count = len(report.split())
    print(f"  Output: {line_count} lines, {word_count} words", file=sys.stderr)
    print(f"  Saved:  {output_path}", file=sys.stderr)


if __name__ == "__main__":
    main()
