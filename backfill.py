#!/usr/bin/env python3
"""
GovCon Intelligence Historical Backfill Tool
Pulls historical contract award data from USAspending.gov API week by week.

This is the moat builder — every week of historical data we accumulate makes our
trend analysis, contractor scorecards, and win predictions more valuable.

Usage:
    python3 backfill.py --weeks 12                           # backfill last 12 weeks
    python3 backfill.py --weeks 52                           # backfill full year
    python3 backfill.py --start 2025-03-01 --end 2026-03-01  # specific range
    python3 backfill.py --weeks 4 --dry-run                  # show what would be pulled
    python3 backfill.py --weeks 12 --skip-existing           # resume partial backfill
"""

import argparse
import json
import os
import sys
import time
from datetime import datetime, timedelta

# Import constants and functions from pipeline
from pipeline import (
    VERTICALS,
    AWARD_TYPE_CODES,
    FIELDS,
    curl_post,
    detect_vehicle,
    match_verticals,
    log,
    SEARCH_ENDPOINT,
    PAGE_LIMIT,
)

# Import archive functions
from archive_data import (
    ARCHIVE_DIR,
    MASTER_FILE,
    load_master,
    save_json,
    compute_stats,
)

# ---------------------------------------------------------------------------
# Backfill Logic
# ---------------------------------------------------------------------------

def generate_week_ranges(start_date, end_date):
    """Generate weekly date ranges from start to end, working backwards from end."""
    weeks = []
    current_end = end_date

    while current_end > start_date:
        current_start = max(current_end - timedelta(days=7), start_date)
        weeks.append((current_start, current_end))
        current_end = current_start

    # Reverse so we process oldest to newest
    weeks.reverse()
    return weeks


def week_already_archived(week_end_date):
    """Check if a week's data already exists in archive."""
    date_str = week_end_date.strftime("%Y-%m-%d")
    snapshot_path = os.path.join(ARCHIVE_DIR, f"{date_str}.json")
    return os.path.exists(snapshot_path)


def pull_awards_for_week(start_date_str, end_date_str, dry_run=False):
    """
    Pull all awards for a single week using the same vertical-based search as pipeline.py.
    Returns deduped awards list.
    """
    if dry_run:
        log(f"    [DRY RUN] Would pull from {start_date_str} to {end_date_str}")
        return []

    # Pull awards per vertical (same logic as pipeline.py)
    raw_by_vertical = {}
    for vertical_name, keywords in VERTICALS.items():
        results = pull_awards_for_vertical(
            vertical_name, keywords, start_date_str, end_date_str
        )
        raw_by_vertical[vertical_name] = results
        # Rate limiting: 1 second between vertical queries
        time.sleep(1)

    # De-duplicate and merge (same logic as pipeline.py)
    awards_map = {}

    for vertical_name, results in raw_by_vertical.items():
        for r in results:
            gid = r.get("generated_internal_id") or r.get("Award ID", "UNKNOWN")
            if gid in awards_map:
                # Add this vertical to existing record
                if vertical_name not in awards_map[gid]["verticals"]:
                    awards_map[gid]["verticals"].append(vertical_name)
            else:
                # Cross-tag against ALL verticals
                desc_verticals = match_verticals(r.get("Description"))
                all_verticals = list(set([vertical_name] + desc_verticals))
                all_verticals.sort()

                awards_map[gid] = {
                    "generated_internal_id": gid,
                    "award_id": r.get("Award ID"),
                    "description": r.get("Description"),
                    "award_amount": r.get("Award Amount"),
                    "awarding_agency": r.get("Awarding Agency"),
                    "recipient_name": r.get("Recipient Name"),
                    "start_date": r.get("Start Date"),
                    "end_date": r.get("End Date"),
                    "verticals": all_verticals,
                    "vehicle": None,
                    "set_aside": None,
                    "naics_code": r.get("NAICS Code"),
                    "naics_description": None,
                }

    # Detect contract vehicles
    for gid, award in awards_map.items():
        award["vehicle"] = detect_vehicle(
            award["award_id"], gid, award.get("description")
        )

    return list(awards_map.values())


def pull_awards_for_vertical(vertical_name, keywords, start_date, end_date):
    """
    Pull all awards matching keywords for a single vertical.
    Copy of pipeline.py logic for backfill context.
    """
    payload = {
        "filters": {
            "keywords": keywords,
            "time_period": [{"start_date": start_date, "end_date": end_date}],
            "award_type_codes": AWARD_TYPE_CODES,
        },
        "fields": FIELDS,
        "limit": PAGE_LIMIT,
        "page": 1,
    }

    all_results = []
    page = 1
    while True:
        payload["page"] = page
        data = curl_post(SEARCH_ENDPOINT, payload)
        if not data or "results" not in data:
            break

        results = data["results"]
        all_results.extend(results)

        meta = data.get("page_metadata", {})
        if not meta.get("hasNext", False):
            break
        page += 1

        # Safety cap
        if page > 50:
            log(f"    [warn] Hit 50-page cap for {vertical_name}, stopping.")
            break

    return all_results


def save_week_snapshot(awards, week_end_date):
    """Save week's awards to archive snapshot."""
    date_str = week_end_date.strftime("%Y-%m-%d")
    snapshot_path = os.path.join(ARCHIVE_DIR, f"{date_str}.json")
    save_json(awards, snapshot_path)
    return snapshot_path


def merge_into_master(awards):
    """Merge week's awards into master all_awards.json (deduped)."""
    master = load_master()
    pre_count = len(master)

    new_count = 0
    updated_count = 0
    for award in awards:
        aid = award.get("generated_internal_id")
        if not aid:
            continue
        if aid not in master:
            new_count += 1
        else:
            updated_count += 1
        master[aid] = award

    # Save master
    save_json(list(master.values()), MASTER_FILE)

    return new_count, updated_count, len(master)


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(
        description="Backfill historical GovCon awards data"
    )
    parser.add_argument(
        "--weeks",
        type=int,
        help="Number of weeks to backfill from today (e.g., 12 or 52)"
    )
    parser.add_argument(
        "--start",
        help="Start date (YYYY-MM-DD) for custom range"
    )
    parser.add_argument(
        "--end",
        help="End date (YYYY-MM-DD) for custom range"
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show what would be pulled without making API calls"
    )
    parser.add_argument(
        "--skip-existing",
        action="store_true",
        help="Skip weeks that already have snapshots in archive"
    )
    args = parser.parse_args()

    # Ensure archive directory exists
    os.makedirs(ARCHIVE_DIR, exist_ok=True)

    # Determine date range
    if args.start and args.end:
        start_date = datetime.strptime(args.start, "%Y-%m-%d")
        end_date = datetime.strptime(args.end, "%Y-%m-%d")
    elif args.weeks:
        end_date = datetime.now()
        start_date = end_date - timedelta(weeks=args.weeks)
    else:
        log("ERROR: Must specify either --weeks or both --start and --end")
        sys.exit(1)

    # Generate week ranges
    weeks = generate_week_ranges(start_date, end_date)

    log("=" * 70)
    log("GovCon Intelligence Historical Backfill")
    log("=" * 70)
    log(f"Date range:     {start_date.strftime('%Y-%m-%d')} to {end_date.strftime('%Y-%m-%d')}")
    log(f"Weeks to pull:  {len(weeks)}")
    log(f"Verticals:      {len(VERTICALS)}")
    log(f"Mode:           {'DRY RUN' if args.dry_run else 'LIVE'}")
    log(f"Skip existing:  {'Yes' if args.skip_existing else 'No'}")
    log("")

    # Process each week
    total_awards = 0
    total_new = 0
    weeks_processed = 0
    weeks_skipped = 0

    for i, (week_start, week_end) in enumerate(weeks, 1):
        week_start_str = week_start.strftime("%Y-%m-%d")
        week_end_str = week_end.strftime("%Y-%m-%d")

        # Check if already archived
        if args.skip_existing and week_already_archived(week_end):
            log(f"Week {i}/{len(weeks)}: {week_start_str} to {week_end_str} — SKIPPED (already archived)")
            weeks_skipped += 1
            continue

        log(f"Week {i}/{len(weeks)}: {week_start_str} to {week_end_str}")

        # Pull awards for this week
        awards = pull_awards_for_week(week_start_str, week_end_str, dry_run=args.dry_run)

        if args.dry_run:
            log(f"  [DRY RUN] Would process {len(awards)} awards")
            weeks_processed += 1
            continue

        log(f"  Pulled {len(awards)} unique awards")
        total_awards += len(awards)

        if awards:
            # Save week snapshot
            snapshot_path = save_week_snapshot(awards, week_end)
            log(f"  Snapshot saved: {os.path.basename(snapshot_path)}")

            # Merge into master
            new_count, updated_count, master_total = merge_into_master(awards)
            total_new += new_count
            log(f"  Master updated: +{new_count} new, {updated_count} existing updated (total: {master_total})")

        weeks_processed += 1
        log("")

    # Summary
    log("=" * 70)
    log("BACKFILL COMPLETE")
    log("=" * 70)
    log(f"Weeks processed:      {weeks_processed}")
    if weeks_skipped > 0:
        log(f"Weeks skipped:        {weeks_skipped}")
    log(f"Total awards pulled:  {total_awards:,}")
    log(f"New awards added:     {total_new:,}")

    if not args.dry_run:
        # Compute final stats
        master = load_master()
        stats = compute_stats(master)
        log("")
        log("=== Historical Data Moat ===")
        log(f"Total awards:         {stats.get('total_awards', 0):,}")
        log(f"Unique recipients:    {stats.get('unique_recipients', 0):,}")
        log(f"Unique agencies:      {stats.get('unique_agencies', 0):,}")
        log(f"Total value:          ${stats.get('total_value_usd', 0):,.2f}")
        log(f"Weeks archived:       {stats.get('weeks_archived', 0)}")
        log(f"Coverage:             {stats.get('week_dates', [])[0]} to {stats.get('week_dates', [])[-1]}")

    log("")
    log("The moat grows deeper.")


if __name__ == "__main__":
    main()
