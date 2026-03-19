#!/usr/bin/env python3
"""
GovCon Awards Data Archiver
Builds a cumulative historical dataset from weekly pipeline runs.

- Copies latest awards JSON to data/archive/YYYY-MM-DD.json
- Maintains data/archive/all_awards.json (deduped by generated_internal_id)
- Tracks cumulative stats in data/archive/stats.json
- Logs all activity to data/archive/archive.log

Usage:
    python3 archive_data.py                    # auto-find latest file
    python3 archive_data.py --file data/govcon_awards_2026-03-18.json
    python3 archive_data.py --stats            # print cumulative stats only
"""

import argparse
import glob
import json
import logging
import os
import re
import shutil
import sys
from collections import Counter
from datetime import datetime

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")
ARCHIVE_DIR = os.path.join(DATA_DIR, "archive")
MASTER_FILE = os.path.join(ARCHIVE_DIR, "all_awards.json")
STATS_FILE = os.path.join(ARCHIVE_DIR, "stats.json")
LOG_FILE = os.path.join(ARCHIVE_DIR, "archive.log")

# ---------------------------------------------------------------------------
# Logging
# ---------------------------------------------------------------------------
os.makedirs(ARCHIVE_DIR, exist_ok=True)

logger = logging.getLogger("archive")
logger.setLevel(logging.INFO)
# File handler
fh = logging.FileHandler(LOG_FILE)
fh.setFormatter(logging.Formatter("%(asctime)s  %(levelname)s  %(message)s"))
logger.addHandler(fh)
# Console handler
ch = logging.StreamHandler()
ch.setFormatter(logging.Formatter("%(message)s"))
logger.addHandler(ch)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------
def find_latest_awards_file() -> str | None:
    """Find the most recent govcon_awards_YYYY-MM-DD.json in data/."""
    pattern = os.path.join(DATA_DIR, "govcon_awards_*.json")
    files = sorted(glob.glob(pattern))
    return files[-1] if files else None


def extract_date_from_filename(filepath: str) -> str | None:
    """Pull YYYY-MM-DD from a filename like govcon_awards_2026-03-18.json."""
    match = re.search(r"(\d{4}-\d{2}-\d{2})", os.path.basename(filepath))
    return match.group(1) if match else None


def load_json(filepath: str) -> list | dict:
    if not os.path.exists(filepath):
        return []
    with open(filepath, "r") as f:
        return json.load(f)


def save_json(data, filepath: str):
    with open(filepath, "w") as f:
        json.dump(data, f, indent=2, default=str)


def load_master() -> dict:
    """Load master as a dict keyed by generated_internal_id for O(1) dedup."""
    awards = load_json(MASTER_FILE)
    if isinstance(awards, list):
        return {a["generated_internal_id"]: a for a in awards}
    return {}


def compute_stats(master: dict) -> dict:
    """Compute cumulative statistics from the master dataset."""
    awards = list(master.values())
    if not awards:
        return {"total_awards": 0, "weeks_archived": 0}

    # Collect dates from archive snapshots
    snapshot_pattern = os.path.join(ARCHIVE_DIR, "????-??-??.json")
    snapshots = sorted(glob.glob(snapshot_pattern))
    weeks = [os.path.basename(s).replace(".json", "") for s in snapshots]

    # Unique recipients and agencies
    recipients = set()
    agencies = set()
    verticals = Counter()
    total_value = 0.0

    for a in awards:
        r = a.get("recipient_name")
        if r:
            recipients.add(r)
        ag = a.get("awarding_agency")
        if ag:
            agencies.add(ag)
        amt = a.get("award_amount")
        if amt and isinstance(amt, (int, float)):
            total_value += amt
        for v in a.get("verticals", []):
            verticals[v] += 1

    return {
        "total_awards": len(awards),
        "unique_recipients": len(recipients),
        "unique_agencies": len(agencies),
        "total_value_usd": round(total_value, 2),
        "weeks_archived": len(weeks),
        "week_dates": weeks,
        "top_verticals": dict(verticals.most_common(10)),
        "last_updated": datetime.now().isoformat(),
    }


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------
def archive(filepath: str):
    """Archive a single awards file into the cumulative dataset."""
    date_str = extract_date_from_filename(filepath)
    if not date_str:
        logger.error(f"Cannot extract date from filename: {filepath}")
        sys.exit(1)

    # 1. Load new awards
    new_awards = load_json(filepath)
    if not isinstance(new_awards, list):
        logger.error(f"Expected a list of awards, got {type(new_awards)}")
        sys.exit(1)
    logger.info(f"Loaded {len(new_awards)} awards from {os.path.basename(filepath)}")

    # 2. Copy snapshot to archive
    snapshot_dest = os.path.join(ARCHIVE_DIR, f"{date_str}.json")
    if os.path.exists(snapshot_dest):
        logger.warning(f"Snapshot {date_str}.json already exists — overwriting")
    shutil.copy2(filepath, snapshot_dest)
    logger.info(f"Snapshot saved: {snapshot_dest}")

    # 3. Merge into master (dedup by generated_internal_id)
    master = load_master()
    pre_count = len(master)

    new_count = 0
    updated_count = 0
    for award in new_awards:
        aid = award.get("generated_internal_id")
        if not aid:
            logger.warning(f"Award missing generated_internal_id, skipping: {award.get('award_id', '?')}")
            continue
        if aid not in master:
            new_count += 1
        else:
            updated_count += 1
        # Always update with latest data (awards can be modified)
        master[aid] = award

    # 4. Save master
    save_json(list(master.values()), MASTER_FILE)
    logger.info(
        f"Master updated: {pre_count} -> {len(master)} total awards "
        f"(+{new_count} new, {updated_count} existing updated)"
    )

    # 5. Compute and save stats
    stats = compute_stats(master)
    save_json(stats, STATS_FILE)
    logger.info(f"Stats: {stats['total_awards']} awards, "
                f"{stats['unique_recipients']} recipients, "
                f"{stats['unique_agencies']} agencies, "
                f"{stats['weeks_archived']} weeks archived")
    logger.info(f"Total contract value: ${stats['total_value_usd']:,.2f}")

    return stats


def print_stats():
    """Print current cumulative stats."""
    if not os.path.exists(STATS_FILE):
        print("No stats yet. Run archive first.")
        return
    stats = load_json(STATS_FILE)
    print("\n=== GovCon Historical Data Moat ===")
    print(f"  Total awards:      {stats.get('total_awards', 0):,}")
    print(f"  Unique recipients: {stats.get('unique_recipients', 0):,}")
    print(f"  Unique agencies:   {stats.get('unique_agencies', 0):,}")
    print(f"  Total value:       ${stats.get('total_value_usd', 0):,.2f}")
    print(f"  Weeks archived:    {stats.get('weeks_archived', 0)}")
    print(f"  Week dates:        {', '.join(stats.get('week_dates', []))}")
    print(f"  Top verticals:     {stats.get('top_verticals', {})}")
    print(f"  Last updated:      {stats.get('last_updated', 'N/A')}")
    print()


def main():
    parser = argparse.ArgumentParser(description="Archive GovCon awards data")
    parser.add_argument("--file", help="Specific awards JSON to archive")
    parser.add_argument("--stats", action="store_true", help="Print cumulative stats only")
    args = parser.parse_args()

    if args.stats:
        print_stats()
        return

    # Find file to archive
    filepath = args.file
    if not filepath:
        filepath = find_latest_awards_file()
        if not filepath:
            logger.error("No govcon_awards_*.json found in data/")
            sys.exit(1)
        logger.info(f"Auto-detected latest file: {os.path.basename(filepath)}")

    if not os.path.exists(filepath):
        logger.error(f"File not found: {filepath}")
        sys.exit(1)

    archive(filepath)
    print_stats()


if __name__ == "__main__":
    main()
