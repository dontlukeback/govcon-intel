#!/usr/bin/env python3
"""
Simple metrics tracking CLI for GovCon Intel.
Logs metrics to JSON and displays trends.
"""

import json
import argparse
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional

METRICS_FILE = Path(__file__).parent / "data.json"

TRACKED_METRICS = [
    "subscribers",
    "page_views",
    "newsletter_opens",
    "newsletter_clicks",
    "linkedin_impressions",
    "linkedin_engagement",
]


def load_metrics() -> List[Dict]:
    """Load metrics from JSON file."""
    if not METRICS_FILE.exists():
        return []

    with open(METRICS_FILE, "r") as f:
        return json.load(f)


def save_metrics(metrics: List[Dict]):
    """Save metrics to JSON file."""
    METRICS_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(METRICS_FILE, "w") as f:
        json.dump(metrics, f, indent=2)


def log_metrics(args):
    """Log a new metrics entry."""
    metrics = load_metrics()

    entry = {
        "timestamp": datetime.now().isoformat(),
        "date": datetime.now().strftime("%Y-%m-%d"),
    }

    # Add all tracked metrics
    for metric in TRACKED_METRICS:
        value = getattr(args, metric, None)
        if value is not None:
            entry[metric] = value

    metrics.append(entry)
    save_metrics(metrics)

    print(f"✓ Logged metrics for {entry['date']}")


def calculate_trend(current: float, previous: float) -> str:
    """Calculate trend arrow."""
    if previous == 0:
        return "→" if current == 0 else "↑"

    change_pct = ((current - previous) / previous) * 100

    if change_pct > 5:
        return f"↑ +{change_pct:.0f}%"
    elif change_pct < -5:
        return f"↓ {change_pct:.0f}%"
    else:
        return "→"


def show_metrics(args):
    """Display metrics in table format."""
    metrics = load_metrics()

    if not metrics:
        print("No metrics logged yet.")
        return

    # Filter by date range if requested
    if args.last:
        cutoff_date = datetime.now() - timedelta(days=args.last)
        metrics = [
            m for m in metrics
            if datetime.fromisoformat(m["timestamp"]) >= cutoff_date
        ]

    if not metrics:
        print(f"No metrics in the last {args.last} days.")
        return

    # Output format
    if args.format == "csv":
        _output_csv(metrics)
    else:
        _output_table(metrics)


def _output_table(metrics: List[Dict]):
    """Display metrics as a formatted table."""
    print("\n" + "="*80)
    print("GOVCON INTEL METRICS")
    print("="*80 + "\n")

    # Group by date (in case multiple entries per day)
    daily_metrics = {}
    for entry in metrics:
        date = entry["date"]
        if date not in daily_metrics:
            daily_metrics[date] = entry
        else:
            # Take the latest entry for each day
            if entry["timestamp"] > daily_metrics[date]["timestamp"]:
                daily_metrics[date] = entry

    # Sort by date
    sorted_dates = sorted(daily_metrics.keys())

    if len(sorted_dates) == 0:
        print("No data to display.")
        return

    # Header
    print(f"{'Date':<12} {'Subs':<6} {'Views':<8} {'Opens':<7} {'Clicks':<7} {'LI Impr':<9} {'LI Eng':<8}")
    print("-" * 80)

    # Rows with trend arrows
    for i, date in enumerate(sorted_dates):
        entry = daily_metrics[date]

        row = f"{date:<12}"

        for metric in TRACKED_METRICS:
            value = entry.get(metric, 0)

            # Calculate trend if we have previous data
            if i > 0:
                prev_entry = daily_metrics[sorted_dates[i-1]]
                prev_value = prev_entry.get(metric, 0)
                trend = calculate_trend(value, prev_value)
            else:
                trend = ""

            # Format based on metric
            if metric == "subscribers":
                row += f"{value:<6}"
            elif metric == "page_views":
                row += f"{value:<8}"
            elif metric == "newsletter_opens":
                row += f"{value:<7}"
            elif metric == "newsletter_clicks":
                row += f"{value:<7}"
            elif metric == "linkedin_impressions":
                row += f"{value:<9}"
            elif metric == "linkedin_engagement":
                row += f"{value:<8}"

            # Add trend on next line if present
            if i == len(sorted_dates) - 1 and trend:  # Only show trend on last row
                pass  # We'll add summary instead

        print(row)

    # Summary section
    if len(sorted_dates) >= 2:
        print("\n" + "-" * 80)
        print("TRENDS (vs. previous day)\n")

        latest = daily_metrics[sorted_dates[-1]]
        previous = daily_metrics[sorted_dates[-2]]

        for metric in TRACKED_METRICS:
            latest_val = latest.get(metric, 0)
            prev_val = previous.get(metric, 0)
            trend = calculate_trend(latest_val, prev_val)

            metric_name = metric.replace("_", " ").title()
            print(f"  {metric_name:<25} {trend}")

    print("\n" + "="*80 + "\n")


def _output_csv(metrics: List[Dict]):
    """Output metrics as CSV."""
    if not metrics:
        return

    # Header
    headers = ["timestamp", "date"] + TRACKED_METRICS
    print(",".join(headers))

    # Rows
    for entry in metrics:
        row = [
            entry.get("timestamp", ""),
            entry.get("date", ""),
        ]
        for metric in TRACKED_METRICS:
            row.append(str(entry.get(metric, 0)))
        print(",".join(row))


def main():
    parser = argparse.ArgumentParser(
        description="Track GovCon Intel metrics",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Log today's metrics
  python3 track.py --subscribers 5 --page-views 120 --newsletter-opens 3

  # Show all metrics
  python3 track.py --show

  # Show last 7 days
  python3 track.py --show --last 7

  # Export to CSV
  python3 track.py --show --format csv > metrics.csv
        """
    )

    # Metric inputs
    for metric in TRACKED_METRICS:
        parser.add_argument(
            f"--{metric.replace('_', '-')}",
            type=int,
            dest=metric,
            help=f"Log {metric.replace('_', ' ')}"
        )

    # Display options
    parser.add_argument("--show", action="store_true", help="Display metrics")
    parser.add_argument("--last", type=int, help="Show last N days")
    parser.add_argument(
        "--format",
        choices=["table", "csv"],
        default="table",
        help="Output format (default: table)"
    )

    args = parser.parse_args()

    # Determine action
    if args.show:
        show_metrics(args)
    else:
        # Check if any metrics were provided
        has_metrics = any(getattr(args, metric, None) is not None for metric in TRACKED_METRICS)

        if not has_metrics:
            parser.print_help()
        else:
            log_metrics(args)


if __name__ == "__main__":
    main()
