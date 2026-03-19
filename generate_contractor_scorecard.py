#!/usr/bin/env python3
"""
Contractor Scorecard Generator

Generates performance reports for federal contractors based on accumulated award data.
This becomes a competitive moat: the more weeks of data we accumulate, the richer the analysis.

Usage:
    python3 generate_contractor_scorecard.py "Leidos"
    python3 generate_contractor_scorecard.py "Booz Allen Hamilton" --output reports/
    python3 generate_contractor_scorecard.py "SAIC" --format json

The script reads all available award data (current + archived) and generates:
- Total awards (count + value)
- Agency breakdown
- Vertical distribution
- Contract trends over time
- Competitive positioning
"""

import json
import sys
import argparse
from pathlib import Path
from datetime import datetime
from collections import defaultdict
from typing import Dict, List, Any


def load_all_awards() -> List[Dict[str, Any]]:
    """
    Load all available award data from the cumulative archive.

    Primary source: data/archive/all_awards.json (12-week cumulative data).
    Fallback: individual weekly files from data/ and data/archive/.

    As we accumulate more weeks of data, this function automatically includes them,
    making scorecards richer over time (THE DATA MOAT).
    """
    awards = []
    data_dir = Path(__file__).parent / "data"
    archive_dir = data_dir / "archive"

    # Primary: load cumulative all_awards.json (preferred — deduplicated, complete)
    cumulative_file = archive_dir / "all_awards.json"
    if cumulative_file.exists():
        try:
            with open(cumulative_file, 'r', encoding='utf-8') as f:
                awards = json.load(f)
                print(f"   Loaded {len(awards):,} awards from {cumulative_file.name} (cumulative archive)")
                print(f"Total awards loaded: {len(awards):,}\n")
                return awards
        except Exception as e:
            print(f"   Failed to load {cumulative_file.name}: {e}")
            print("   Falling back to individual weekly files...")

    # Fallback: load individual weekly files
    current_files = list(data_dir.glob("govcon_awards_*.json"))

    if archive_dir.exists():
        archive_files = list(archive_dir.glob("govcon_awards_*.json"))
    else:
        archive_files = []

    all_files = current_files + archive_files

    if not all_files:
        print("No award data found. Run pipeline.py first.")
        return []

    print(f"Loading data from {len(all_files)} file(s)...")

    for file_path in sorted(all_files):
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                awards.extend(data)
                print(f"   Loaded {len(data):,} awards from {file_path.name}")
        except Exception as e:
            print(f"   Failed to load {file_path.name}: {e}")

    print(f"Total awards loaded: {len(awards):,}\n")
    return awards


def normalize_contractor_name(name: str) -> str:
    """
    Normalize contractor names for matching (handles LLC, Inc, Corp variations).
    """
    if not name:
        return ""

    # Convert to uppercase for comparison
    normalized = name.upper().strip()

    # Remove common suffixes
    suffixes = [
        ", LLC", " LLC", ", INC", " INC", ", CORP", " CORP",
        ", LTD", " LTD", ", L.L.C.", " L.L.C.", ", INC.", " INC.",
        ", CORPORATION", " CORPORATION", ", INCORPORATED", " INCORPORATED"
    ]

    for suffix in suffixes:
        if normalized.endswith(suffix):
            normalized = normalized[:-len(suffix)].strip()

    return normalized


def find_contractor_awards(contractor_query: str, all_awards: List[Dict]) -> List[Dict]:
    """
    Find all awards for a given contractor (fuzzy matching on name).
    """
    query_normalized = normalize_contractor_name(contractor_query)

    matching_awards = []
    for award in all_awards:
        recipient = award.get("recipient_name", "")
        recipient_normalized = normalize_contractor_name(recipient)

        # Match if query is substring of recipient name
        if query_normalized in recipient_normalized:
            matching_awards.append(award)

    return matching_awards


def calculate_metrics(awards: List[Dict]) -> Dict[str, Any]:
    """
    Calculate key metrics from contractor's awards.
    """
    if not awards:
        return {}

    # Basic stats
    total_count = len(awards)
    total_value = sum(award.get("award_amount", 0) for award in awards)
    avg_value = total_value / total_count if total_count > 0 else 0

    # Agency breakdown
    agency_stats = defaultdict(lambda: {"count": 0, "value": 0})
    for award in awards:
        agency = award.get("awarding_agency", "Unknown")
        agency_stats[agency]["count"] += 1
        agency_stats[agency]["value"] += award.get("award_amount", 0)

    # Vertical breakdown
    vertical_stats = defaultdict(lambda: {"count": 0, "value": 0})
    for award in awards:
        verticals = award.get("verticals", [])
        if not verticals:
            verticals = ["Uncategorized"]
        for vertical in verticals:
            vertical_stats[vertical]["count"] += 1
            vertical_stats[vertical]["value"] += award.get("award_amount", 0)

    # Time series (by month, if dates available)
    monthly_stats = defaultdict(lambda: {"count": 0, "value": 0})
    for award in awards:
        start_date = award.get("start_date", "")
        if start_date:
            try:
                # Extract year-month
                date_obj = datetime.strptime(start_date, "%Y-%m-%d")
                month_key = date_obj.strftime("%Y-%m")
                monthly_stats[month_key]["count"] += 1
                monthly_stats[month_key]["value"] += award.get("award_amount", 0)
            except:
                pass

    # Top awards
    top_awards = sorted(
        awards,
        key=lambda x: x.get("award_amount", 0),
        reverse=True
    )[:5]

    return {
        "total_count": total_count,
        "total_value": total_value,
        "avg_value": avg_value,
        "agency_stats": dict(agency_stats),
        "vertical_stats": dict(vertical_stats),
        "monthly_stats": dict(monthly_stats),
        "top_awards": top_awards
    }


def format_currency(amount: float) -> str:
    """Format currency with B/M/K suffixes."""
    if amount >= 1_000_000_000:
        return f"${amount / 1_000_000_000:.1f}B"
    elif amount >= 1_000_000:
        return f"${amount / 1_000_000:.1f}M"
    elif amount >= 1_000:
        return f"${amount / 1_000:.1f}K"
    else:
        return f"${amount:.0f}"


def generate_markdown_report(contractor_name: str, awards: List[Dict], metrics: Dict) -> str:
    """
    Generate markdown report for contractor.
    """
    if not awards:
        return f"# Contractor Report: {contractor_name}\n\n**No awards found.**\n"

    report = []
    report.append(f"# Contractor Scorecard: {contractor_name}")
    report.append(f"\n**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    report.append(f"**Data Coverage:** {len(awards):,} awards analyzed")
    report.append("\n---\n")

    # Overview
    report.append("## Overview")
    report.append(f"- **Total Awards:** {metrics['total_count']:,} contracts")
    report.append(f"- **Total Value:** {format_currency(metrics['total_value'])}")
    report.append(f"- **Average Award Size:** {format_currency(metrics['avg_value'])}")

    # Agency breakdown
    report.append("\n## Agency Distribution")
    agency_stats = sorted(
        metrics['agency_stats'].items(),
        key=lambda x: x[1]['value'],
        reverse=True
    )

    for agency, stats in agency_stats[:10]:  # Top 10 agencies
        count = stats['count']
        value = stats['value']
        pct = (value / metrics['total_value'] * 100) if metrics['total_value'] > 0 else 0
        report.append(f"- **{agency}:** {count} awards, {format_currency(value)} ({pct:.1f}%)")

    # Vertical breakdown
    report.append("\n## Vertical Distribution")
    vertical_stats = sorted(
        metrics['vertical_stats'].items(),
        key=lambda x: x[1]['value'],
        reverse=True
    )

    for vertical, stats in vertical_stats[:10]:  # Top 10 verticals
        count = stats['count']
        value = stats['value']
        pct = (value / metrics['total_value'] * 100) if metrics['total_value'] > 0 else 0
        report.append(f"- **{vertical}:** {count} awards, {format_currency(value)} ({pct:.1f}%)")

    # Top awards
    report.append("\n## Top 5 Awards")
    for i, award in enumerate(metrics['top_awards'], 1):
        desc = award.get('description', 'No description')[:100]
        value = format_currency(award.get('award_amount', 0))
        agency = award.get('awarding_agency', 'Unknown')
        start_date = award.get('start_date', 'Unknown')
        report.append(f"\n### {i}. {value} — {agency}")
        report.append(f"**Date:** {start_date}")
        report.append(f"**Description:** {desc}...")

    # Trend analysis (if we have multi-month data)
    if len(metrics['monthly_stats']) > 1:
        report.append("\n## Monthly Trend")
        monthly_sorted = sorted(metrics['monthly_stats'].items())

        report.append("\n| Month | Awards | Value |")
        report.append("|-------|--------|-------|")
        for month, stats in monthly_sorted:
            count = stats['count']
            value = format_currency(stats['value'])
            report.append(f"| {month} | {count} | {value} |")

        # Calculate growth (if we have 2+ months)
        if len(monthly_sorted) >= 2:
            first_month = monthly_sorted[0][1]
            last_month = monthly_sorted[-1][1]

            value_growth = ((last_month['value'] - first_month['value']) / first_month['value'] * 100) if first_month['value'] > 0 else 0

            report.append(f"\n**Trend:** {'📈 Growing' if value_growth > 0 else '📉 Declining'} ({value_growth:+.1f}% value change)")

    # Data moat notice
    report.append("\n---")
    report.append("\n## About This Report")
    report.append(f"\nThis scorecard is generated from {len(awards):,} federal contract awards tracked by GovCon Weekly Intelligence.")
    report.append("\n**The more data we accumulate, the richer this analysis becomes.** This is our competitive moat.")
    report.append("\nAs we track awards over months and years:")
    report.append("- Trend analysis becomes more accurate")
    report.append("- Win rate calculations become possible")
    report.append("- Recompete predictions emerge")
    report.append("- Market share analysis deepens")
    report.append("\n*Want full scorecards with competitive benchmarking? Upgrade to Pro tier.*")

    return "\n".join(report)


def generate_json_report(contractor_name: str, awards: List[Dict], metrics: Dict) -> str:
    """
    Generate JSON report for contractor.
    """
    output = {
        "contractor": contractor_name,
        "generated_at": datetime.now().isoformat(),
        "data_coverage": {
            "awards_analyzed": len(awards),
            "date_range": "TBD"  # TODO: extract from award dates
        },
        "metrics": {
            "total_awards": metrics['total_count'],
            "total_value": metrics['total_value'],
            "average_value": metrics['avg_value']
        },
        "agency_breakdown": [
            {
                "agency": agency,
                "awards": stats['count'],
                "value": stats['value'],
                "percentage": (stats['value'] / metrics['total_value'] * 100) if metrics['total_value'] > 0 else 0
            }
            for agency, stats in sorted(
                metrics['agency_stats'].items(),
                key=lambda x: x[1]['value'],
                reverse=True
            )[:10]
        ],
        "vertical_breakdown": [
            {
                "vertical": vertical,
                "awards": stats['count'],
                "value": stats['value'],
                "percentage": (stats['value'] / metrics['total_value'] * 100) if metrics['total_value'] > 0 else 0
            }
            for vertical, stats in sorted(
                metrics['vertical_stats'].items(),
                key=lambda x: x[1]['value'],
                reverse=True
            )[:10]
        ],
        "top_awards": [
            {
                "description": award.get('description', '')[:200],
                "value": award.get('award_amount', 0),
                "agency": award.get('awarding_agency', 'Unknown'),
                "start_date": award.get('start_date', 'Unknown')
            }
            for award in metrics['top_awards']
        ]
    }

    return json.dumps(output, indent=2)


def main():
    parser = argparse.ArgumentParser(
        description="Generate contractor scorecard from accumulated award data",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python3 generate_contractor_scorecard.py "Leidos"
  python3 generate_contractor_scorecard.py "Booz Allen Hamilton" --output reports/
  python3 generate_contractor_scorecard.py "SAIC" --format json
        """
    )

    parser.add_argument(
        "contractor",
        help="Contractor name (e.g., 'Leidos', 'Booz Allen Hamilton')"
    )

    parser.add_argument(
        "--output",
        "-o",
        help="Output directory (default: current directory)",
        default="."
    )

    parser.add_argument(
        "--format",
        "-f",
        choices=["markdown", "json"],
        default="markdown",
        help="Output format (default: markdown)"
    )

    args = parser.parse_args()

    # Load all available data
    all_awards = load_all_awards()

    if not all_awards:
        print("❌ No data available. Run the pipeline first to generate award data.")
        sys.exit(1)

    # Find contractor's awards
    print(f"🔍 Searching for awards matching '{args.contractor}'...")
    contractor_awards = find_contractor_awards(args.contractor, all_awards)

    if not contractor_awards:
        print(f"❌ No awards found for '{args.contractor}'")
        print("\nTips:")
        print("- Try shorter name (e.g., 'Leidos' instead of 'Leidos, Inc.')")
        print("- Check spelling")
        print("- Try partial match (e.g., 'Booz' for 'Booz Allen Hamilton')")
        sys.exit(1)

    print(f"✅ Found {len(contractor_awards):,} awards\n")

    # Calculate metrics
    print("📊 Calculating metrics...")
    metrics = calculate_metrics(contractor_awards)

    # Generate report
    print(f"📝 Generating {args.format} report...")

    if args.format == "markdown":
        report = generate_markdown_report(args.contractor, contractor_awards, metrics)
        filename = f"scorecard_{normalize_contractor_name(args.contractor).replace(' ', '_').lower()}.md"
    else:
        report = generate_json_report(args.contractor, contractor_awards, metrics)
        filename = f"scorecard_{normalize_contractor_name(args.contractor).replace(' ', '_').lower()}.json"

    # Write output
    output_path = Path(args.output) / filename
    output_path.parent.mkdir(parents=True, exist_ok=True)

    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(report)

    print(f"✅ Report saved to: {output_path}")
    print(f"\n📊 Summary:")
    print(f"   Contractor: {args.contractor}")
    print(f"   Awards: {metrics['total_count']:,}")
    print(f"   Total Value: {format_currency(metrics['total_value'])}")
    print(f"   Avg Award: {format_currency(metrics['avg_value'])}")

    # Data moat reminder
    print(f"\n🏰 DATA MOAT REMINDER:")
    print(f"   This scorecard analyzed {len(all_awards):,} awards.")
    print(f"   As we accumulate more weeks of data, these reports get richer.")
    print(f"   Competitors starting today need {len(all_awards) // 1000} months to catch up.")


if __name__ == "__main__":
    main()
