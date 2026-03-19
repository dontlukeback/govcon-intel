#!/usr/bin/env python3
"""
Data Quality Monitor for GovCon Intelligence Pipeline

Runs after pipeline.py and validates the output data against expected baselines.
Outputs a human-readable report to stdout and saves a structured JSON report.

Usage:
    python3 data_quality.py data/govcon_awards_2026-03-18.json
    python3 data_quality.py data/govcon_awards_2026-03-18.json --baseline data/quality_report_2026-03-11.json

Exit codes:
    0 — All checks passed (or warnings only)
    1 — One or more CRITICAL checks failed
    2 — Input error (file not found, bad JSON, etc.)
"""

import argparse
import json
import os
import sys
from collections import Counter
from datetime import datetime, timedelta

# ---------------------------------------------------------------------------
# Configuration — expected ranges derived from EDA (eda-awards.md)
# ---------------------------------------------------------------------------

EXPECTED_AWARD_COUNT = (500, 2000)
EXPECTED_TOTAL_VALUE = (1_000_000_000, 50_000_000_000)  # $1B - $50B
MEGA_AWARD_THRESHOLD = 1_000_000_000  # $1B

EXPECTED_VERTICALS = [
    "AI/ML",
    "Cybersecurity",
    "Cloud",
    "Data Analytics",
    "DevSecOps",
    "Zero Trust",
    "FedRAMP",
    "Identity Management",
    "Networking/SDWAN",
]

# Baseline null rates from EDA (eda-awards.md section 8)
# Used as comparison — alert if null rate increases by more than 10pp
BASELINE_NULL_RATES = {
    "award_id": 0.0,
    "description": 0.0,
    "award_amount": 3.0,
    "awarding_agency": 0.0,
    "recipient_name": 0.0,
    "start_date": 0.0,
    "end_date": 0.0,
    "verticals": 0.0,
    "vehicle": 97.3,
    "set_aside": 95.2,
    "naics_code": 95.7,
    "naics_description": 95.7,
}

# Fields where nulls are critical (core fields that must be populated)
CRITICAL_FIELDS = ["award_id", "description", "awarding_agency", "recipient_name", "start_date"]

# Known major federal contractors — if top recipients are all unknown names,
# something went wrong with the data pull
KNOWN_CONTRACTORS = [
    "LEIDOS",
    "BOOZ ALLEN",
    "SAIC",
    "GENERAL DYNAMICS",
    "RAYTHEON",
    "NORTHROP GRUMMAN",
    "LOCKHEED",
    "DELOITTE",
    "ACCENTURE",
    "MANTECH",
    "PERATON",
    "CGI",
    "ICF",
    "MAXIMUS",
    "UNISYS",
    "BAE SYSTEMS",
    "L3HARRIS",
    "HARRIS CORPORATION",
    "COGNOSANTE",
    "FOUR POINTS TECHNOLOGY",
    "SCIENCE APPLICATIONS INTERNATIONAL",
    "KRATOS",
    "SALIENT CRGT",
    "AT&T",
    "TRIWEST",
    "SAVANNAH RIVER",
    "IDAHO ENVIRONMENTAL",
]

# Date range: awards should have start dates within a reasonable window
# Pipeline pulls last N days, but awards may reference older base contracts
MAX_START_DATE_AGE_YEARS = 10  # Flag if start_date is more than 10 years ago


# ---------------------------------------------------------------------------
# Check functions — each returns a dict with status, message, details
# ---------------------------------------------------------------------------

def check_award_count(awards):
    """Check: award count within expected range (500-2000)."""
    count = len(awards)
    lo, hi = EXPECTED_AWARD_COUNT

    if lo <= count <= hi:
        status = "PASS"
        message = f"Award count {count} is within expected range [{lo}, {hi}]"
    elif count == 0:
        status = "CRITICAL"
        message = f"Award count is 0 — pipeline likely failed"
    elif count < lo:
        status = "WARNING"
        message = f"Award count {count} is below expected minimum {lo}"
    else:
        status = "WARNING"
        message = f"Award count {count} exceeds expected maximum {hi}"

    return {
        "check": "award_count",
        "status": status,
        "message": message,
        "details": {
            "count": count,
            "expected_range": list(EXPECTED_AWARD_COUNT),
        },
    }


def check_total_value(awards):
    """Check: total award value between $1B and $50B."""
    amounts = []
    null_count = 0
    zero_count = 0
    negative_count = 0

    for a in awards:
        amt = a.get("award_amount")
        if amt is None:
            null_count += 1
        elif amt == 0:
            zero_count += 1
        elif amt < 0:
            negative_count += 1
        else:
            amounts.append(amt)

    total = sum(amounts)
    lo, hi = EXPECTED_TOTAL_VALUE

    if lo <= total <= hi:
        status = "PASS"
        message = f"Total value ${total:,.0f} is within expected range"
    elif total < lo:
        status = "WARNING"
        message = f"Total value ${total:,.0f} is below expected minimum ${lo:,.0f}"
    elif total > hi:
        status = "WARNING"
        message = f"Total value ${total:,.0f} exceeds expected maximum ${hi:,.0f}"
    else:
        status = "PASS"
        message = f"Total value ${total:,.0f}"

    # Flag outliers: individual awards > $1B
    mega_awards = [
        {
            "recipient": a.get("recipient_name", "UNKNOWN"),
            "amount": a.get("award_amount"),
            "agency": a.get("awarding_agency", "UNKNOWN"),
        }
        for a in awards
        if (a.get("award_amount") or 0) > MEGA_AWARD_THRESHOLD
    ]

    return {
        "check": "total_value",
        "status": status,
        "message": message,
        "details": {
            "total_value": round(total, 2),
            "expected_range": list(EXPECTED_TOTAL_VALUE),
            "null_amounts": null_count,
            "zero_amounts": zero_count,
            "negative_amounts": negative_count,
            "mega_awards_over_1B": mega_awards,
        },
    }


def check_vertical_coverage(awards):
    """Check: all 9 verticals have at least 1 award."""
    vertical_counts = Counter()
    for a in awards:
        for v in a.get("verticals", []):
            vertical_counts[v] += 1

    found = set(vertical_counts.keys())
    expected = set(EXPECTED_VERTICALS)
    missing = expected - found
    extra = found - expected

    if not missing:
        status = "PASS"
        message = f"All {len(EXPECTED_VERTICALS)} expected verticals have coverage"
    else:
        status = "WARNING"
        message = f"Missing {len(missing)} vertical(s): {', '.join(sorted(missing))}"

    # Flag verticals with very low counts (< 3)
    low_count = {v: vertical_counts[v] for v in expected if vertical_counts.get(v, 0) < 3}

    return {
        "check": "vertical_coverage",
        "status": status,
        "message": message,
        "details": {
            "vertical_counts": dict(sorted(vertical_counts.items(), key=lambda x: -x[1])),
            "missing_verticals": sorted(missing),
            "unexpected_verticals": sorted(extra),
            "low_count_verticals": low_count,
        },
    }


def check_null_rates(awards):
    """Check: null rates per field, compared to baseline."""
    total = len(awards)
    if total == 0:
        return {
            "check": "null_rates",
            "status": "CRITICAL",
            "message": "No awards to check",
            "details": {},
        }

    field_nulls = {}
    degraded_fields = []

    for field in BASELINE_NULL_RATES:
        null_count = 0
        for a in awards:
            val = a.get(field)
            if val is None:
                null_count += 1
            elif isinstance(val, str) and val.strip() == "":
                null_count += 1
            elif isinstance(val, list) and len(val) == 0:
                null_count += 1

        null_pct = (null_count / total) * 100
        baseline_pct = BASELINE_NULL_RATES[field]
        delta = null_pct - baseline_pct

        field_nulls[field] = {
            "null_count": null_count,
            "null_pct": round(null_pct, 1),
            "baseline_pct": baseline_pct,
            "delta_pp": round(delta, 1),
        }

        # Alert if critical field has any nulls, or if null rate increased > 10pp
        if field in CRITICAL_FIELDS and null_count > 0:
            degraded_fields.append((field, null_pct, "critical field has nulls"))
        elif delta > 10.0:
            degraded_fields.append((field, null_pct, f"+{delta:.1f}pp vs baseline"))

    if not degraded_fields:
        status = "PASS"
        message = "Null rates within expected ranges"
    elif any(f[0] in CRITICAL_FIELDS for f in degraded_fields):
        status = "CRITICAL"
        message = f"Critical field(s) have nulls: {', '.join(f[0] for f in degraded_fields if f[0] in CRITICAL_FIELDS)}"
    else:
        status = "WARNING"
        message = f"{len(degraded_fields)} field(s) degraded vs baseline: {', '.join(f[0] for f in degraded_fields)}"

    return {
        "check": "null_rates",
        "status": status,
        "message": message,
        "details": {
            "field_null_rates": field_nulls,
            "degraded_fields": [
                {"field": f, "null_pct": p, "reason": r} for f, p, r in degraded_fields
            ],
        },
    }


def check_duplicates(awards):
    """Check: no duplicate generated_internal_ids."""
    ids = [a.get("generated_internal_id") for a in awards if a.get("generated_internal_id")]
    id_counts = Counter(ids)
    duplicates = {k: v for k, v in id_counts.items() if v > 1}

    if not duplicates:
        status = "PASS"
        message = f"No duplicate IDs among {len(ids)} awards"
    else:
        status = "WARNING"
        message = f"{len(duplicates)} duplicate generated_internal_id(s) found"

    # Also check for awards missing generated_internal_id entirely
    missing_id_count = sum(1 for a in awards if not a.get("generated_internal_id"))

    return {
        "check": "duplicates",
        "status": status,
        "message": message,
        "details": {
            "total_ids": len(ids),
            "unique_ids": len(set(ids)),
            "duplicate_count": len(duplicates),
            "duplicate_ids": dict(list(duplicates.items())[:20]),  # Cap at 20 for readability
            "missing_id_count": missing_id_count,
        },
    }


def check_date_range(awards):
    """Check: all award start_dates within expected range."""
    today = datetime.now()
    cutoff_past = today - timedelta(days=MAX_START_DATE_AGE_YEARS * 365)
    cutoff_future = today + timedelta(days=365)  # 1 year in future is suspicious

    parse_errors = 0
    too_old = []
    future_dates = []
    valid_dates = []

    for a in awards:
        sd = a.get("start_date")
        if not sd:
            continue
        try:
            dt = datetime.strptime(sd, "%Y-%m-%d")
            valid_dates.append(dt)

            if dt < cutoff_past:
                too_old.append({
                    "award_id": a.get("award_id"),
                    "start_date": sd,
                    "recipient": a.get("recipient_name", "UNKNOWN"),
                })
            elif dt > cutoff_future:
                future_dates.append({
                    "award_id": a.get("award_id"),
                    "start_date": sd,
                    "recipient": a.get("recipient_name", "UNKNOWN"),
                })
        except (ValueError, TypeError):
            parse_errors += 1

    issues = len(too_old) + len(future_dates) + parse_errors

    if issues == 0:
        status = "PASS"
        message = "All dates within expected range"
    elif parse_errors > 0:
        status = "WARNING"
        message = f"{parse_errors} unparseable date(s), {len(too_old)} too old, {len(future_dates)} in future"
    else:
        status = "WARNING"
        message = f"{len(too_old)} date(s) older than {MAX_START_DATE_AGE_YEARS}y, {len(future_dates)} in future"

    date_range = {}
    if valid_dates:
        date_range = {
            "earliest": min(valid_dates).strftime("%Y-%m-%d"),
            "latest": max(valid_dates).strftime("%Y-%m-%d"),
        }

    return {
        "check": "date_range",
        "status": status,
        "message": message,
        "details": {
            "valid_dates": len(valid_dates),
            "parse_errors": parse_errors,
            "too_old_count": len(too_old),
            "future_count": len(future_dates),
            "date_range": date_range,
            "too_old_samples": too_old[:10],
            "future_samples": future_dates[:10],
        },
    }


def check_recipients(awards):
    """Check: top recipients include known federal contractors (not garbage data)."""
    recipient_totals = Counter()
    for a in awards:
        name = a.get("recipient_name", "")
        amt = a.get("award_amount") or 0
        recipient_totals[name] += amt

    top_20 = recipient_totals.most_common(20)

    # Check how many of the top 20 match known contractors
    recognized = 0
    unrecognized = []
    for name, value in top_20:
        name_upper = name.upper()
        if any(known in name_upper for known in KNOWN_CONTRACTORS):
            recognized += 1
        else:
            unrecognized.append({"name": name, "total_value": round(value, 2)})

    recognition_rate = (recognized / len(top_20) * 100) if top_20 else 0

    if recognition_rate >= 30:
        status = "PASS"
        message = f"{recognized}/{len(top_20)} top recipients are known contractors ({recognition_rate:.0f}%)"
    elif recognition_rate >= 15:
        status = "WARNING"
        message = f"Only {recognized}/{len(top_20)} top recipients recognized ({recognition_rate:.0f}%)"
    else:
        status = "CRITICAL"
        message = f"Only {recognized}/{len(top_20)} top recipients recognized — possible garbage data"

    # Additional checks
    unique_recipients = len(recipient_totals)
    empty_names = sum(1 for a in awards if not a.get("recipient_name", "").strip())

    return {
        "check": "recipients",
        "status": status,
        "message": message,
        "details": {
            "unique_recipients": unique_recipients,
            "empty_recipient_names": empty_names,
            "top_20_recognized": recognized,
            "top_20_total": len(top_20),
            "recognition_rate_pct": round(recognition_rate, 1),
            "unrecognized_top_recipients": unrecognized[:10],
        },
    }


# ---------------------------------------------------------------------------
# Report generation
# ---------------------------------------------------------------------------

def generate_report(awards, input_file, baseline_file=None):
    """Run all checks and produce structured report."""
    checks = [
        check_award_count(awards),
        check_total_value(awards),
        check_vertical_coverage(awards),
        check_null_rates(awards),
        check_duplicates(awards),
        check_date_range(awards),
        check_recipients(awards),
    ]

    # Summary
    statuses = Counter(c["status"] for c in checks)
    overall = "CRITICAL" if statuses.get("CRITICAL", 0) > 0 else \
              "WARNING" if statuses.get("WARNING", 0) > 0 else "PASS"

    report = {
        "report_date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "input_file": os.path.basename(input_file),
        "award_count": len(awards),
        "overall_status": overall,
        "summary": {
            "pass": statuses.get("PASS", 0),
            "warning": statuses.get("WARNING", 0),
            "critical": statuses.get("CRITICAL", 0),
            "total_checks": len(checks),
        },
        "checks": checks,
    }

    return report


def print_report(report):
    """Print human-readable report to stdout."""
    STATUS_ICONS = {
        "PASS": "  PASS",
        "WARNING": "  WARN",
        "CRITICAL": "**FAIL",
    }

    print()
    print("=" * 72)
    print("  GOVCON DATA QUALITY REPORT")
    print("=" * 72)
    print(f"  Date:    {report['report_date']}")
    print(f"  Input:   {report['input_file']}")
    print(f"  Awards:  {report['award_count']}")
    print(f"  Status:  {report['overall_status']}")
    print("-" * 72)
    s = report["summary"]
    print(f"  {s['pass']} passed  |  {s['warning']} warnings  |  {s['critical']} critical  |  {s['total_checks']} total")
    print("=" * 72)
    print()

    for check in report["checks"]:
        icon = STATUS_ICONS.get(check["status"], "  ????")
        print(f"  {icon}  {check['check']}")
        print(f"         {check['message']}")

        # Print relevant details for non-PASS checks
        details = check.get("details", {})
        if check["status"] != "PASS":
            _print_check_details(check["check"], details)

        print()

    # Final summary
    print("-" * 72)
    if report["overall_status"] == "PASS":
        print("  All checks passed. Data quality is acceptable.")
    elif report["overall_status"] == "WARNING":
        print(f"  {s['warning']} warning(s) detected. Review flagged items above.")
    else:
        print(f"  {s['critical']} CRITICAL issue(s). Pipeline output may be unreliable.")
    print("-" * 72)
    print()


def _print_check_details(check_name, details):
    """Print additional context for failed/warning checks."""
    if check_name == "total_value":
        if details.get("zero_amounts"):
            print(f"         -> {details['zero_amounts']} awards with $0 value")
        if details.get("negative_amounts"):
            print(f"         -> {details['negative_amounts']} awards with negative value")
        for ma in details.get("mega_awards_over_1B", []):
            print(f"         -> MEGA: ${ma['amount']:,.0f} | {ma['recipient']} | {ma['agency']}")

    elif check_name == "vertical_coverage":
        for v in details.get("missing_verticals", []):
            print(f"         -> Missing: {v}")
        for v, c in details.get("low_count_verticals", {}).items():
            print(f"         -> Low count: {v} = {c} award(s)")

    elif check_name == "null_rates":
        for d in details.get("degraded_fields", []):
            print(f"         -> {d['field']}: {d['null_pct']}% null ({d['reason']})")

    elif check_name == "duplicates":
        for did, count in list(details.get("duplicate_ids", {}).items())[:5]:
            print(f"         -> {did} appears {count}x")
        if details.get("missing_id_count"):
            print(f"         -> {details['missing_id_count']} award(s) missing generated_internal_id")

    elif check_name == "date_range":
        for s in details.get("too_old_samples", [])[:3]:
            print(f"         -> Old: {s['start_date']} | {s['recipient']}")
        for s in details.get("future_samples", [])[:3]:
            print(f"         -> Future: {s['start_date']} | {s['recipient']}")

    elif check_name == "recipients":
        for u in details.get("unrecognized_top_recipients", [])[:5]:
            print(f"         -> Unrecognized: {u['name']} (${u['total_value']:,.0f})")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(
        description="Data quality monitor for GovCon pipeline output",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="Example:\n  python3 data_quality.py data/govcon_awards_2026-03-18.json",
    )
    parser.add_argument(
        "input_file",
        help="Path to govcon_awards JSON file",
    )
    parser.add_argument(
        "--baseline",
        help="Path to previous quality_report JSON for comparison (optional)",
        default=None,
    )
    parser.add_argument(
        "--output-dir",
        help="Directory to save JSON report (default: data/)",
        default=None,
    )
    parser.add_argument(
        "--json-only",
        help="Suppress stdout report, only write JSON",
        action="store_true",
    )
    args = parser.parse_args()

    # --- Validate input ---
    if not os.path.isfile(args.input_file):
        print(f"ERROR: File not found: {args.input_file}", file=sys.stderr)
        sys.exit(2)

    # --- Load data ---
    try:
        with open(args.input_file, "r") as f:
            awards = json.load(f)
    except json.JSONDecodeError as e:
        print(f"ERROR: Invalid JSON in {args.input_file}: {e}", file=sys.stderr)
        sys.exit(2)
    except OSError as e:
        print(f"ERROR: Could not read {args.input_file}: {e}", file=sys.stderr)
        sys.exit(2)

    if not isinstance(awards, list):
        print(f"ERROR: Expected a JSON array, got {type(awards).__name__}", file=sys.stderr)
        sys.exit(2)

    # --- Run checks ---
    report = generate_report(awards, args.input_file, args.baseline)

    # --- Print human-readable report ---
    if not args.json_only:
        print_report(report)

    # --- Save JSON report ---
    output_dir = args.output_dir or os.path.join(os.path.dirname(args.input_file) or ".", "")
    # Ensure output_dir exists; fall back to directory containing input file
    if not os.path.isdir(output_dir):
        try:
            os.makedirs(output_dir, exist_ok=True)
        except OSError:
            output_dir = os.path.dirname(os.path.abspath(args.input_file))

    today = datetime.now().strftime("%Y-%m-%d")
    report_path = os.path.join(output_dir, f"quality_report_{today}.json")

    try:
        with open(report_path, "w") as f:
            json.dump(report, f, indent=2, default=str)
        if not args.json_only:
            print(f"  JSON report saved to: {report_path}")
            print()
    except OSError as e:
        print(f"WARNING: Could not save JSON report: {e}", file=sys.stderr)

    # --- Exit code ---
    if report["overall_status"] == "CRITICAL":
        sys.exit(1)
    else:
        sys.exit(0)


if __name__ == "__main__":
    main()
