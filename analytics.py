#!/usr/bin/env python3
"""
GovCon Intelligence Analytics Script
Reads awards JSON and outputs clean summary statistics, trends, and comparisons.

Usage:
    python3 analytics.py data/govcon_awards_2026-03-18.json
    python3 analytics.py data/govcon_awards_2026-03-18.json --compare data/govcon_awards_2026-03-11.json
    python3 analytics.py data/govcon_awards_2026-03-18.json --format json
    python3 analytics.py data/govcon_awards_2026-03-18.json --vertical Cloud --min-amount 1000000

No external dependencies (stdlib only).
"""

import argparse
import json
import os
import sys
from collections import defaultdict, Counter
from datetime import datetime

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))

# ---------------------------------------------------------------------------
# Core analytics functions
# ---------------------------------------------------------------------------

def load_awards(path):
    """Load awards from JSON file."""
    if not os.path.exists(path):
        print(f"ERROR: File not found: {path}", file=sys.stderr)
        sys.exit(1)
    with open(path) as f:
        return json.load(f)


def calculate_summary_stats(awards):
    """Calculate overall summary statistics."""
    amounts = [a.get("award_amount", 0) for a in awards if a.get("award_amount")]

    if not amounts:
        return {
            "total_awards": len(awards),
            "total_value": 0,
            "mean": 0,
            "median": 0,
            "min": 0,
            "max": 0,
        }

    amounts_sorted = sorted(amounts)
    n = len(amounts)

    return {
        "total_awards": len(awards),
        "total_value": sum(amounts),
        "mean": sum(amounts) / n,
        "median": amounts_sorted[n // 2],
        "min": amounts_sorted[0],
        "max": amounts_sorted[-1],
        "p25": amounts_sorted[n // 4],
        "p75": amounts_sorted[3 * n // 4],
        "p90": amounts_sorted[int(n * 0.9)],
        "p99": amounts_sorted[int(n * 0.99)] if n > 100 else amounts_sorted[-1],
    }


def group_by_agency(awards):
    """Group awards by agency and calculate stats."""
    stats = defaultdict(lambda: {"count": 0, "total_value": 0})
    for award in awards:
        agency = award.get("awarding_agency", "Unknown")
        amt = award.get("award_amount", 0)
        stats[agency]["count"] += 1
        stats[agency]["total_value"] += amt

    # Add average
    for agency, data in stats.items():
        data["avg_value"] = data["total_value"] / data["count"] if data["count"] > 0 else 0

    return dict(stats)


def group_by_vertical(awards):
    """Group awards by vertical and calculate stats."""
    stats = defaultdict(lambda: {"count": 0, "total_value": 0})
    for award in awards:
        for vertical in award.get("verticals", []):
            amt = award.get("award_amount", 0)
            stats[vertical]["count"] += 1
            stats[vertical]["total_value"] += amt

    # Add average
    for vertical, data in stats.items():
        data["avg_value"] = data["total_value"] / data["count"] if data["count"] > 0 else 0

    return dict(stats)


def group_by_recipient(awards):
    """Group awards by recipient and calculate stats."""
    stats = defaultdict(lambda: {"count": 0, "total_value": 0})
    for award in awards:
        recipient = award.get("recipient_name", "Unknown")
        amt = award.get("award_amount", 0)
        stats[recipient]["count"] += 1
        stats[recipient]["total_value"] += amt

    # Add average
    for recipient, data in stats.items():
        data["avg_value"] = data["total_value"] / data["count"] if data["count"] > 0 else 0

    return dict(stats)


def group_by_set_aside(awards):
    """Group awards by set-aside type and calculate stats."""
    stats = defaultdict(lambda: {"count": 0, "total_value": 0})
    for award in awards:
        set_aside = award.get("set_aside") or "None/Null"
        amt = award.get("award_amount", 0)
        stats[set_aside]["count"] += 1
        stats[set_aside]["total_value"] += amt

    return dict(stats)


def group_by_vehicle(awards):
    """Group awards by contract vehicle and calculate stats."""
    stats = defaultdict(lambda: {"count": 0, "total_value": 0})
    for award in awards:
        vehicle = award.get("vehicle") or "None/Null"
        amt = award.get("award_amount", 0)
        stats[vehicle]["count"] += 1
        stats[vehicle]["total_value"] += amt

    return dict(stats)


def calculate_size_distribution(awards):
    """Calculate distribution of awards by size bucket."""
    buckets = {
        "Zero": 0,
        "< $100K": 0,
        "$100K - $500K": 0,
        "$500K - $1M": 0,
        "$1M - $5M": 0,
        "$5M - $10M": 0,
        "$10M - $50M": 0,
        "$50M+": 0,
    }

    for award in awards:
        amt = award.get("award_amount", 0)
        if amt == 0:
            buckets["Zero"] += 1
        elif amt < 100_000:
            buckets["< $100K"] += 1
        elif amt < 500_000:
            buckets["$100K - $500K"] += 1
        elif amt < 1_000_000:
            buckets["$500K - $1M"] += 1
        elif amt < 5_000_000:
            buckets["$1M - $5M"] += 1
        elif amt < 10_000_000:
            buckets["$5M - $10M"] += 1
        elif amt < 50_000_000:
            buckets["$10M - $50M"] += 1
        else:
            buckets["$50M+"] += 1

    return buckets


def compare_datasets(current, previous):
    """Calculate week-over-week changes between two datasets."""
    curr_stats = {
        "total_count": len(current),
        "total_value": sum(a.get("award_amount", 0) for a in current),
        "by_agency": group_by_agency(current),
        "by_vertical": group_by_vertical(current),
        "by_recipient": group_by_recipient(current),
    }

    prev_stats = {
        "total_count": len(previous),
        "total_value": sum(a.get("award_amount", 0) for a in previous),
        "by_agency": group_by_agency(previous),
        "by_vertical": group_by_vertical(previous),
        "by_recipient": group_by_recipient(previous),
    }

    def calc_change(curr, prev):
        if prev == 0:
            return float('inf') if curr > 0 else 0
        return ((curr - prev) / prev) * 100

    comparison = {
        "total_count_change": calc_change(curr_stats["total_count"], prev_stats["total_count"]),
        "total_value_change": calc_change(curr_stats["total_value"], prev_stats["total_value"]),
        "agency_changes": {},
        "vertical_changes": {},
        "new_recipients": [],
        "emerging_recipients": [],
    }

    # Agency changes
    for agency in curr_stats["by_agency"]:
        curr_val = curr_stats["by_agency"][agency]["total_value"]
        prev_val = prev_stats["by_agency"].get(agency, {}).get("total_value", 0)
        change = curr_val - prev_val
        pct_change = calc_change(curr_val, prev_val) if prev_val > 0 else 0
        comparison["agency_changes"][agency] = {
            "current": curr_val,
            "previous": prev_val,
            "change": change,
            "pct_change": pct_change,
        }

    # Vertical changes
    for vertical in curr_stats["by_vertical"]:
        curr_val = curr_stats["by_vertical"][vertical]["total_value"]
        prev_val = prev_stats["by_vertical"].get(vertical, {}).get("total_value", 0)
        change = curr_val - prev_val
        pct_change = calc_change(curr_val, prev_val) if prev_val > 0 else 0
        comparison["vertical_changes"][vertical] = {
            "current": curr_val,
            "previous": prev_val,
            "change": change,
            "pct_change": pct_change,
        }

    # New recipients (appeared this week)
    for recipient in curr_stats["by_recipient"]:
        if recipient not in prev_stats["by_recipient"]:
            curr_val = curr_stats["by_recipient"][recipient]["total_value"]
            if curr_val > 1_000_000:  # Only flag if >$1M
                comparison["new_recipients"].append({
                    "name": recipient,
                    "value": curr_val,
                })

    # Emerging recipients (2x increase)
    for recipient in curr_stats["by_recipient"]:
        curr_val = curr_stats["by_recipient"][recipient]["total_value"]
        prev_val = prev_stats["by_recipient"].get(recipient, {}).get("total_value", 0)
        if prev_val > 0 and curr_val > 2 * prev_val:
            comparison["emerging_recipients"].append({
                "name": recipient,
                "current": curr_val,
                "previous": prev_val,
                "pct_change": calc_change(curr_val, prev_val),
            })

    return comparison


# ---------------------------------------------------------------------------
# Output formatters
# ---------------------------------------------------------------------------

def print_text_report(awards, compare_data=None):
    """Print human-readable text report."""
    print("="*80)
    print("GOVCON AWARDS ANALYTICS")
    print("="*80)

    # Summary stats
    stats = calculate_summary_stats(awards)
    print(f"\nSUMMARY STATISTICS")
    print(f"Total Awards:  {stats['total_awards']:,}")
    print(f"Total Value:   ${stats['total_value']:,.2f}")
    print(f"Mean:          ${stats['mean']:,.2f}")
    print(f"Median:        ${stats['median']:,.2f}")
    print(f"Min:           ${stats['min']:,.2f}")
    print(f"Max:           ${stats['max']:,.2f}")
    print(f"P25:           ${stats.get('p25', 0):,.2f}")
    print(f"P75:           ${stats.get('p75', 0):,.2f}")
    print(f"P90:           ${stats.get('p90', 0):,.2f}")

    # Top agencies by value
    print(f"\nTOP 10 AGENCIES BY VALUE")
    agencies = group_by_agency(awards)
    for i, (agency, data) in enumerate(
        sorted(agencies.items(), key=lambda x: x[1]["total_value"], reverse=True)[:10], 1
    ):
        print(f"{i:2}. {agency:<50} ${data['total_value']:>13,.0f} | {data['count']:>3} awards")

    # Vertical breakdown
    print(f"\nVERTICAL BREAKDOWN")
    verticals = group_by_vertical(awards)
    for vertical, data in sorted(verticals.items(), key=lambda x: x[1]["count"], reverse=True):
        print(f"  {vertical:<25} {data['count']:>4} awards | ${data['total_value']:>13,.0f} | Avg: ${data['avg_value']:>11,.0f}")

    # Top recipients
    print(f"\nTOP 20 RECIPIENTS BY VALUE")
    recipients = group_by_recipient(awards)
    for i, (recipient, data) in enumerate(
        sorted(recipients.items(), key=lambda x: x[1]["total_value"], reverse=True)[:20], 1
    ):
        print(f"{i:2}. {recipient:<55} ${data['total_value']:>13,.0f} | {data['count']:>2} awards")

    # Set-aside breakdown
    print(f"\nSET-ASIDE BREAKDOWN")
    set_asides = group_by_set_aside(awards)
    for sa, data in sorted(set_asides.items(), key=lambda x: x[1]["count"], reverse=True):
        pct = (data["count"] / len(awards)) * 100
        print(f"  {sa:<30} {data['count']:>4} ({pct:>5.1f}%) | ${data['total_value']:>13,.0f}")

    # Vehicle breakdown
    print(f"\nCONTRACT VEHICLE BREAKDOWN")
    vehicles = group_by_vehicle(awards)
    for vehicle, data in sorted(vehicles.items(), key=lambda x: x[1]["count"], reverse=True):
        pct = (data["count"] / len(awards)) * 100
        print(f"  {vehicle:<30} {data['count']:>4} ({pct:>5.1f}%) | ${data['total_value']:>13,.0f}")

    # Size distribution
    print(f"\nAWARD SIZE DISTRIBUTION")
    sizes = calculate_size_distribution(awards)
    for bucket, count in sizes.items():
        pct = (count / len(awards)) * 100 if len(awards) > 0 else 0
        print(f"  {bucket:<20} {count:>5} awards ({pct:>5.1f}%)")

    # Week-over-week comparison
    if compare_data:
        print(f"\n{'='*80}")
        print("WEEK-OVER-WEEK COMPARISON")
        print("="*80)

        print(f"\nOVERALL CHANGE")
        print(f"Awards: {stats['total_awards']:,} ({compare_data['total_count_change']:+.1f}% vs previous)")
        print(f"Value:  ${stats['total_value']:,.0f} ({compare_data['total_value_change']:+.1f}% vs previous)")

        print(f"\nTOP AGENCY MOVERS (by absolute change)")
        for agency, data in sorted(
            compare_data["agency_changes"].items(),
            key=lambda x: abs(x[1]["change"]),
            reverse=True
        )[:10]:
            print(f"  {agency:<50} ${data['change']:>12,.0f} ({data['pct_change']:>+6.1f}%)")

        print(f"\nTOP VERTICAL MOVERS (by absolute change)")
        for vertical, data in sorted(
            compare_data["vertical_changes"].items(),
            key=lambda x: abs(x[1]["change"]),
            reverse=True
        )[:10]:
            print(f"  {vertical:<25} ${data['change']:>12,.0f} ({data['pct_change']:>+6.1f}%)")

        if compare_data["new_recipients"]:
            print(f"\nNEW RECIPIENTS (>$1M)")
            for rec in sorted(compare_data["new_recipients"], key=lambda x: x["value"], reverse=True):
                print(f"  {rec['name']:<55} ${rec['value']:>13,.0f}")

        if compare_data["emerging_recipients"]:
            print(f"\nEMERGING RECIPIENTS (2x increase)")
            for rec in sorted(compare_data["emerging_recipients"], key=lambda x: x["pct_change"], reverse=True):
                print(f"  {rec['name']:<55} ${rec['current']:>13,.0f} ({rec['pct_change']:>+6.1f}%)")

    print(f"\n{'='*80}")


def output_json(awards, compare_data=None):
    """Output results as JSON."""
    result = {
        "summary": calculate_summary_stats(awards),
        "by_agency": group_by_agency(awards),
        "by_vertical": group_by_vertical(awards),
        "by_recipient": group_by_recipient(awards),
        "by_set_aside": group_by_set_aside(awards),
        "by_vehicle": group_by_vehicle(awards),
        "size_distribution": calculate_size_distribution(awards),
    }

    if compare_data:
        result["comparison"] = compare_data

    print(json.dumps(result, indent=2))


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(
        description="GovCon Awards Analytics",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python3 analytics.py data/govcon_awards_2026-03-18.json
  python3 analytics.py data/govcon_awards_2026-03-18.json --compare data/govcon_awards_2026-03-11.json
  python3 analytics.py data/govcon_awards_2026-03-18.json --format json
  python3 analytics.py data/govcon_awards_2026-03-18.json --vertical Cloud --min-amount 1000000
        """
    )
    parser.add_argument("input", help="Path to awards JSON file")
    parser.add_argument(
        "--compare",
        help="Path to previous week's JSON file for week-over-week comparison"
    )
    parser.add_argument(
        "--format",
        choices=["text", "json"],
        default="text",
        help="Output format (default: text)"
    )
    parser.add_argument(
        "--vertical",
        help="Filter to specific vertical (e.g., Cloud, Cybersecurity)"
    )
    parser.add_argument(
        "--agency",
        help="Filter to specific agency"
    )
    parser.add_argument(
        "--min-amount",
        type=float,
        help="Filter to awards >= this amount"
    )
    parser.add_argument(
        "--max-amount",
        type=float,
        help="Filter to awards <= this amount"
    )

    args = parser.parse_args()

    # Load data
    awards = load_awards(args.input)

    # Apply filters
    if args.vertical:
        awards = [a for a in awards if args.vertical in a.get("verticals", [])]

    if args.agency:
        awards = [a for a in awards if args.agency in a.get("awarding_agency", "")]

    if args.min_amount is not None:
        awards = [a for a in awards if a.get("award_amount", 0) >= args.min_amount]

    if args.max_amount is not None:
        awards = [a for a in awards if a.get("award_amount", 0) <= args.max_amount]

    # Load comparison data if provided
    compare_data = None
    if args.compare:
        previous = load_awards(args.compare)
        compare_data = compare_datasets(awards, previous)

    # Output
    if args.format == "json":
        output_json(awards, compare_data)
    else:
        print_text_report(awards, compare_data)


if __name__ == "__main__":
    main()
