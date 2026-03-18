#!/usr/bin/env python3
"""
GovCon Intelligence -- Weekly Markdown Report Generator

Reads the awards JSON (a list of award objects from USAspending) and produces
a structured, intelligence-grade markdown report.

Usage:
    python3 generate_report.py --data data/govcon_awards_2026-03-18.json --output output/report_2026-03-18.md --days 7
    python3 generate_report.py --data data/govcon_awards_2026-03-18.json --output report.md --days 14 --template SAMPLE_REPORT_V2.md
"""

import argparse
import json
import os
import sys
from collections import defaultdict
from datetime import datetime, timedelta

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(SCRIPT_DIR, "data")
OUTPUT_DIR = os.path.join(SCRIPT_DIR, "output")

# The 9 verticals used across the pipeline
VERTICALS = [
    "AI/ML",
    "Cloud",
    "Cybersecurity",
    "Data Analytics",
    "DevSecOps",
    "FedRAMP",
    "Identity Management",
    "Networking/SDWAN",
    "Zero Trust",
]

# Known contract vehicles we track
KNOWN_VEHICLES = [
    "GSA OASIS",
    "STARS III",
    "8(a) STARS II",
    "CIO-SP3",
    "SEWP",
    "ALLIANT 2",
]

# Set-aside categories we report on
SET_ASIDE_CATEGORIES = {
    "8(a)": "8(a) Business Development",
    "SDVOSB": "Service-Disabled Veteran-Owned Small Business",
    "HUBZONE SET-ASIDE": "HUBZone",
    "HUBZONE": "HUBZone",
    "WOSB": "Women-Owned Small Business",
    "EDWOSB": "Economically Disadvantaged WOSB",
    "Small Business": "Small Business Set-Aside",
    "NO SET ASIDE USED.": "Full & Open Competition",
}

# NAICS code -> human-readable market segment
NAICS_SEGMENTS = {
    "541512": "IT Systems Design",
    "541511": "Custom Software",
    "541519": "IT Consulting",
    "541330": "Engineering Services",
    "541611": "Management Consulting",
    "541715": "R&D / Defense Science",
    "518210": "Cloud / Data Hosting",
    "511210": "Software Products",
    "334511": "Defense Electronics / UAS",
    "237990": "Heavy Construction",
}


# ---------------------------------------------------------------------------
# Helpers
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


def truncate(text, max_len=200):
    """Truncate text with ellipsis if too long."""
    if not text:
        return ""
    text = str(text).strip()
    if len(text) <= max_len:
        return text
    return text[:max_len - 3].rsplit(" ", 1)[0] + "..."


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
        # Maybe it's wrapped -- look for common keys
        for key in ("awards", "results", "data", "items"):
            if key in data and isinstance(data[key], list):
                return data[key]
        # Single award? Wrap it.
        return [data]
    else:
        print(f"ERROR: Unexpected data format in {path}", file=sys.stderr)
        sys.exit(1)


def find_prior_data(data_path, days):
    """Look for a prior week's data file for week-over-week comparison."""
    if not data_path:
        return None
    data_dir = os.path.dirname(data_path)
    basename = os.path.basename(data_path)

    # Try to extract date from filename like govcon_awards_2026-03-18.json
    try:
        # Find the date portion
        parts = basename.replace(".json", "").split("_")
        date_str = parts[-1]
        current_date = datetime.strptime(date_str, "%Y-%m-%d")
        prior_date = current_date - timedelta(days=days)
        prior_filename = basename.replace(date_str, prior_date.strftime("%Y-%m-%d"))
        prior_path = os.path.join(data_dir, prior_filename)
        if os.path.exists(prior_path):
            try:
                with open(prior_path) as f:
                    return json.load(f)
            except (json.JSONDecodeError, IOError):
                return None
    except (ValueError, IndexError):
        pass

    return None


# ---------------------------------------------------------------------------
# Report sections
# ---------------------------------------------------------------------------

def build_executive_summary(awards, prior_awards, days, report_date):
    """Build the Executive Summary section."""
    lines = []
    lines.append("## Executive Summary")
    lines.append("")

    total_count = len(awards)
    total_value = sum(safe_amount(a) for a in awards)

    # Top agency by total value
    agency_totals = defaultdict(float)
    for a in awards:
        agency = safe_str(a.get("awarding_agency"), "Unknown Agency")
        agency_totals[agency] += safe_amount(a)
    top_agency = max(agency_totals, key=agency_totals.get) if agency_totals else "N/A"
    top_agency_value = agency_totals.get(top_agency, 0)

    # Top vertical by count
    vertical_counts = defaultdict(int)
    for a in awards:
        for v in (a.get("verticals") or []):
            vertical_counts[v] += 1
    top_vertical = max(vertical_counts, key=vertical_counts.get) if vertical_counts else "N/A"
    top_vertical_count = vertical_counts.get(top_vertical, 0)

    lines.append(f"**Period:** {report_date} (last {days} days)")
    lines.append(f"**Generated:** {datetime.now().strftime('%B %d, %Y at %H:%M %Z').strip()}")
    lines.append("")
    lines.append(f"| Metric | Value |")
    lines.append(f"|--------|-------|")
    lines.append(f"| Total Awards Tracked | **{total_count:,}** |")
    lines.append(f"| Total Contract Value | **{fmt_dollars(total_value)}** |")
    lines.append(f"| Top Agency (by value) | **{top_agency}** ({fmt_dollars(top_agency_value)}) |")
    lines.append(f"| Top Vertical (by count) | **{top_vertical}** ({top_vertical_count:,} awards) |")

    # Week-over-week if prior data exists
    if prior_awards is not None:
        prior_count = len(prior_awards)
        prior_value = sum(safe_amount(a) for a in prior_awards)

        if prior_count > 0:
            count_change = ((total_count - prior_count) / prior_count) * 100
            count_dir = "+" if count_change >= 0 else ""
            lines.append(f"| Week-over-Week (count) | **{count_dir}{count_change:.0f}%** ({prior_count:,} -> {total_count:,}) |")

        if prior_value > 0:
            value_change = ((total_value - prior_value) / prior_value) * 100
            value_dir = "+" if value_change >= 0 else ""
            lines.append(f"| Week-over-Week (value) | **{value_dir}{value_change:.0f}%** ({fmt_dollars(prior_value)} -> {fmt_dollars(total_value)}) |")
    else:
        lines.append(f"| Week-over-Week | *No prior data available* |")

    lines.append("")
    return "\n".join(lines)


def build_top_awards(awards, count=10):
    """Build the Top Awards This Week section."""
    lines = []
    lines.append("## Top Awards This Week")
    lines.append("")

    if not awards:
        lines.append("*No awards data available.*")
        lines.append("")
        return "\n".join(lines)

    # Sort by dollar value descending
    sorted_awards = sorted(awards, key=lambda a: safe_amount(a), reverse=True)
    top = sorted_awards[:count]

    lines.append(f"The {min(count, len(top))} largest awards by dollar value this period:")
    lines.append("")

    for i, award in enumerate(top, 1):
        amount = safe_amount(award)
        agency = safe_str(award.get("awarding_agency"), "Unknown Agency")
        recipient = safe_str(award.get("recipient_name"), "Unknown Recipient")
        description = truncate(safe_str(award.get("description"), "No description"), 300)
        verticals = award.get("verticals") or []
        vertical_tags = ", ".join(verticals) if verticals else "Untagged"
        vehicle = safe_str(award.get("vehicle"), None)
        set_aside = safe_str(award.get("set_aside"), None)
        naics = safe_str(award.get("naics_code"), None)
        naics_desc = safe_str(award.get("naics_description"), None)

        lines.append(f"### {i}. {fmt_dollars(amount)} -- {recipient}")
        lines.append("")
        lines.append(f"- **Agency:** {agency}")
        lines.append(f"- **Recipient:** {recipient}")
        lines.append(f"- **Value:** {fmt_dollars(amount)}")
        lines.append(f"- **Verticals:** {vertical_tags}")
        if vehicle:
            lines.append(f"- **Vehicle:** {vehicle}")
        if set_aside:
            lines.append(f"- **Set-Aside:** {set_aside}")
        if naics:
            segment = NAICS_SEGMENTS.get(naics, naics_desc or naics)
            lines.append(f"- **NAICS:** {naics} ({segment})")
        lines.append(f"- **Description:** {description}")
        lines.append("")

    return "\n".join(lines)


def build_vertical_breakdown(awards):
    """Build the By Vertical Breakdown section."""
    lines = []
    lines.append("## Vertical Breakdown")
    lines.append("")

    if not awards:
        lines.append("*No awards data available.*")
        lines.append("")
        return "\n".join(lines)

    # Aggregate by vertical
    vertical_data = defaultdict(lambda: {"count": 0, "total_value": 0.0, "awards": []})

    for a in awards:
        verticals = a.get("verticals") or []
        if not verticals:
            verticals = ["Untagged"]
        for v in verticals:
            vertical_data[v]["count"] += 1
            vertical_data[v]["total_value"] += safe_amount(a)
            vertical_data[v]["awards"].append(a)

    # Summary table
    lines.append("| Vertical | Awards | Total Value |")
    lines.append("|----------|--------|-------------|")

    # Sort by total value descending
    sorted_verticals = sorted(vertical_data.items(), key=lambda x: x[1]["total_value"], reverse=True)

    for vertical, vdata in sorted_verticals:
        lines.append(f"| {vertical} | {vdata['count']:,} | {fmt_dollars(vdata['total_value'])} |")
    lines.append("")

    # Detail for each defined vertical
    for vertical in VERTICALS:
        if vertical not in vertical_data:
            continue
        vdata = vertical_data[vertical]
        lines.append(f"### {vertical}")
        award_word = "award" if vdata["count"] == 1 else "awards"
        lines.append(f"**{vdata['count']:,} {award_word}** totaling **{fmt_dollars(vdata['total_value'])}**")
        lines.append("")

        # Top 3 by value
        top3 = sorted(vdata["awards"], key=lambda a: safe_amount(a), reverse=True)[:3]
        if top3:
            lines.append("Top awards:")
            for a in top3:
                recipient = safe_str(a.get("recipient_name"), "Unknown")
                agency = safe_str(a.get("awarding_agency"), "Unknown")
                amount = safe_amount(a)
                lines.append(f"- **{fmt_dollars(amount)}** to {recipient} ({agency})")
            lines.append("")

    # Include Untagged if present
    if "Untagged" in vertical_data:
        vdata = vertical_data["Untagged"]
        lines.append(f"### Untagged")
        award_word = "award" if vdata["count"] == 1 else "awards"
        lines.append(f"**{vdata['count']:,} {award_word}** totaling **{fmt_dollars(vdata['total_value'])}** had no vertical classification.")
        lines.append("")

    return "\n".join(lines)


def build_set_aside_analysis(awards):
    """Build the Set-Aside Analysis section."""
    lines = []
    lines.append("## Set-Aside Analysis")
    lines.append("")

    if not awards:
        lines.append("*No awards data available.*")
        lines.append("")
        return "\n".join(lines)

    # Aggregate by set-aside type
    sa_data = defaultdict(lambda: {"count": 0, "total_value": 0.0})

    for a in awards:
        sa = safe_str(a.get("set_aside"), "None / Not Specified")
        sa_data[sa]["count"] += 1
        sa_data[sa]["total_value"] += safe_amount(a)

    total_value = sum(safe_amount(a) for a in awards)

    lines.append("| Set-Aside Type | Awards | Total Value | % of Total |")
    lines.append("|----------------|--------|-------------|------------|")

    sorted_sa = sorted(sa_data.items(), key=lambda x: x[1]["total_value"], reverse=True)

    for sa, data in sorted_sa:
        label = SET_ASIDE_CATEGORIES.get(sa, sa)
        pct = (data["total_value"] / total_value * 100) if total_value > 0 else 0
        lines.append(f"| {label} | {data['count']:,} | {fmt_dollars(data['total_value'])} | {pct:.1f}% |")

    lines.append("")

    # Small business total
    small_biz_keywords = ["8(a)", "SDVOSB", "HUBZONE", "WOSB", "EDWOSB", "Small Business"]
    small_biz_value = 0.0
    small_biz_count = 0
    for a in awards:
        sa = safe_str(a.get("set_aside"), "")
        if any(kw.lower() in sa.lower() for kw in small_biz_keywords):
            small_biz_value += safe_amount(a)
            small_biz_count += 1

    if small_biz_count > 0:
        sb_pct = (small_biz_value / total_value * 100) if total_value > 0 else 0
        lines.append(f"**Small Business Total:** {small_biz_count:,} awards worth {fmt_dollars(small_biz_value)} ({sb_pct:.1f}% of total value)")
        lines.append("")

    return "\n".join(lines)


def build_vehicle_tracker(awards):
    """Build the Contract Vehicle Tracker section."""
    lines = []
    lines.append("## Contract Vehicle Tracker")
    lines.append("")

    if not awards:
        lines.append("*No awards data available.*")
        lines.append("")
        return "\n".join(lines)

    # Aggregate by vehicle
    vehicle_data = defaultdict(lambda: {"count": 0, "total_value": 0.0})
    no_vehicle_count = 0
    no_vehicle_value = 0.0

    for a in awards:
        vehicle = a.get("vehicle")
        if vehicle and str(vehicle).strip():
            vehicle_data[str(vehicle).strip()]["count"] += 1
            vehicle_data[str(vehicle).strip()]["total_value"] += safe_amount(a)
        else:
            no_vehicle_count += 1
            no_vehicle_value += safe_amount(a)

    if not vehicle_data:
        lines.append("*No contract vehicle data tagged for this period.*")
        lines.append("")
        return "\n".join(lines)

    lines.append("| Vehicle | Awards | Total Value |")
    lines.append("|---------|--------|-------------|")

    sorted_vehicles = sorted(vehicle_data.items(), key=lambda x: x[1]["total_value"], reverse=True)

    for vehicle, data in sorted_vehicles:
        lines.append(f"| {vehicle} | {data['count']:,} | {fmt_dollars(data['total_value'])} |")

    if no_vehicle_count > 0:
        lines.append(f"| *No Vehicle / Other* | {no_vehicle_count:,} | {fmt_dollars(no_vehicle_value)} |")

    lines.append("")

    # Highlight known vehicles with detail
    for vehicle in KNOWN_VEHICLES:
        if vehicle in vehicle_data:
            vd = vehicle_data[vehicle]
            award_word = "award" if vd["count"] == 1 else "awards"
            lines.append(f"**{vehicle}:** {vd['count']:,} {award_word} totaling {fmt_dollars(vd['total_value'])}")
    lines.append("")

    return "\n".join(lines)


def build_agency_spotlight(awards, top_n=5):
    """Build the Agency Spotlight section."""
    lines = []
    lines.append("## Agency Spotlight")
    lines.append("")

    if not awards:
        lines.append("*No awards data available.*")
        lines.append("")
        return "\n".join(lines)

    # Aggregate by agency
    agency_data = defaultdict(lambda: {"count": 0, "total_value": 0.0, "recipients": set(), "verticals": set()})

    for a in awards:
        agency = safe_str(a.get("awarding_agency"), "Unknown Agency")
        agency_data[agency]["count"] += 1
        agency_data[agency]["total_value"] += safe_amount(a)
        recipient = a.get("recipient_name")
        if recipient:
            agency_data[agency]["recipients"].add(recipient)
        for v in (a.get("verticals") or []):
            agency_data[agency]["verticals"].add(v)

    sorted_agencies = sorted(agency_data.items(), key=lambda x: x[1]["total_value"], reverse=True)
    top_agencies = sorted_agencies[:top_n]

    lines.append(f"Top {min(top_n, len(top_agencies))} agencies by total obligated value:")
    lines.append("")

    for i, (agency, data) in enumerate(top_agencies, 1):
        unique_recipients = len(data["recipients"])
        verticals_str = ", ".join(sorted(data["verticals"])) if data["verticals"] else "N/A"
        lines.append(f"### {i}. {agency}")
        lines.append("")
        lines.append(f"- **Total Value:** {fmt_dollars(data['total_value'])}")
        lines.append(f"- **Award Count:** {data['count']:,}")
        lines.append(f"- **Unique Recipients:** {unique_recipients:,}")
        lines.append(f"- **Active Verticals:** {verticals_str}")
        lines.append("")

    return "\n".join(lines)


def build_new_entrants(awards, prior_awards):
    """Build the New Entrants section (recipients appearing for the first time)."""
    lines = []
    lines.append("## New Entrants")
    lines.append("")

    if prior_awards is None:
        lines.append("*New entrant detection requires prior period data for comparison.*")
        lines.append("*This section will populate automatically once two consecutive weeks of data are available.*")
        lines.append("")
        return "\n".join(lines)

    # Get prior recipients
    prior_recipients = set()
    for a in prior_awards:
        recipient = a.get("recipient_name")
        if recipient:
            prior_recipients.add(recipient.strip().upper())

    # Find new recipients this period
    new_entrants = defaultdict(lambda: {"count": 0, "total_value": 0.0, "agencies": set()})
    for a in awards:
        recipient = a.get("recipient_name")
        if not recipient:
            continue
        normalized = recipient.strip().upper()
        if normalized not in prior_recipients:
            new_entrants[recipient.strip()]["count"] += 1
            new_entrants[recipient.strip()]["total_value"] += safe_amount(a)
            agency = a.get("awarding_agency")
            if agency:
                new_entrants[recipient.strip()]["agencies"].add(agency)

    if not new_entrants:
        lines.append("*No new recipients identified this period.*")
        lines.append("")
        return "\n".join(lines)

    lines.append(f"**{len(new_entrants):,} recipients** appeared this week that were not present in the prior period.")
    lines.append("")

    # Top new entrants by value
    sorted_new = sorted(new_entrants.items(), key=lambda x: x[1]["total_value"], reverse=True)[:10]

    lines.append("| Recipient | Awards | Total Value | Agencies |")
    lines.append("|-----------|--------|-------------|----------|")

    for recipient, data in sorted_new:
        agencies = ", ".join(sorted(data["agencies"]))
        lines.append(f"| {recipient} | {data['count']:,} | {fmt_dollars(data['total_value'])} | {agencies} |")

    lines.append("")
    return "\n".join(lines)


def build_naics_breakdown(awards, top_n=10):
    """Build a NAICS code breakdown section."""
    lines = []
    lines.append("## NAICS Code Breakdown")
    lines.append("")

    # Aggregate by NAICS
    naics_data = defaultdict(lambda: {"count": 0, "total_value": 0.0, "description": ""})

    for a in awards:
        code = a.get("naics_code")
        if not code:
            code = "Unknown"
        desc = a.get("naics_description") or NAICS_SEGMENTS.get(str(code), "")
        naics_data[str(code)]["count"] += 1
        naics_data[str(code)]["total_value"] += safe_amount(a)
        if desc and not naics_data[str(code)]["description"]:
            naics_data[str(code)]["description"] = desc

    if not naics_data:
        lines.append("*No NAICS data available.*")
        lines.append("")
        return "\n".join(lines)

    sorted_naics = sorted(naics_data.items(), key=lambda x: x[1]["total_value"], reverse=True)[:top_n]

    display_count = min(top_n, len(sorted_naics))
    lines.append(f"Top {display_count} NAICS code{'s' if display_count != 1 else ''} by total value:")
    lines.append("")
    lines.append("| NAICS | Description | Awards | Total Value |")
    lines.append("|-------|-------------|--------|-------------|")

    for code, data in sorted_naics:
        desc = data["description"] or NAICS_SEGMENTS.get(code, "N/A")
        lines.append(f"| {code} | {desc} | {data['count']:,} | {fmt_dollars(data['total_value'])} |")

    lines.append("")
    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Report assembly
# ---------------------------------------------------------------------------

def generate_report(awards, prior_awards, days, report_date):
    """Assemble the full markdown report."""
    parts = []

    # Header
    parts.append("# GovCon Intelligence Weekly Brief")
    parts.append("")
    parts.append(f"**Week of {report_date}** | {len(awards):,} awards tracked | {fmt_dollars(sum(safe_amount(a) for a in awards))} total value")
    parts.append("")
    parts.append("---")
    parts.append("")

    # Sections
    parts.append(build_executive_summary(awards, prior_awards, days, report_date))
    parts.append("---")
    parts.append("")
    parts.append(build_top_awards(awards, count=10))
    parts.append("---")
    parts.append("")
    parts.append(build_vertical_breakdown(awards))
    parts.append("---")
    parts.append("")
    parts.append(build_set_aside_analysis(awards))
    parts.append("---")
    parts.append("")
    parts.append(build_vehicle_tracker(awards))
    parts.append("---")
    parts.append("")
    parts.append(build_agency_spotlight(awards, top_n=5))
    parts.append("---")
    parts.append("")
    parts.append(build_new_entrants(awards, prior_awards))
    parts.append("---")
    parts.append("")
    parts.append(build_naics_breakdown(awards, top_n=10))
    parts.append("---")
    parts.append("")

    # Footer
    parts.append("*Generated by GovCon Intelligence Pipeline*")
    parts.append(f"*Data source: USAspending.gov | Report date: {report_date}*")
    parts.append("")

    return "\n".join(parts)


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(description="GovCon Weekly Markdown Report Generator")
    parser.add_argument("--data", default=None,
                        help="Path to input awards JSON file")
    parser.add_argument("--output", default=None,
                        help="Path to output markdown file")
    parser.add_argument("--days", type=int, default=7,
                        help="Lookback period in days (default: 7)")
    parser.add_argument("--template", default=None,
                        help="Path to report template (reserved for future use)")
    args = parser.parse_args()

    today = datetime.now().strftime("%Y-%m-%d")

    # Resolve input path
    if args.data:
        input_path = args.data
    else:
        # Default: look for today's data file
        input_path = os.path.join(DATA_DIR, f"govcon_awards_{today}.json")
        if not os.path.exists(input_path):
            # Fallback to corrected_all.json
            fallback = os.path.join(DATA_DIR, "corrected_all.json")
            if os.path.exists(fallback):
                input_path = fallback

    # Resolve output path
    output_path = args.output or os.path.join(OUTPUT_DIR, f"report_{today}.md")

    print(f"GovCon Report Generator", file=sys.stderr)
    print(f"  Input:  {input_path}", file=sys.stderr)
    print(f"  Output: {output_path}", file=sys.stderr)
    print(f"  Days:   {args.days}", file=sys.stderr)
    if args.template:
        print(f"  Template: {args.template} (noted, not yet used)", file=sys.stderr)
    print("", file=sys.stderr)

    # Load awards data
    awards = load_awards(input_path)
    print(f"  Loaded: {len(awards):,} awards", file=sys.stderr)

    # Try to find prior period data for week-over-week comparison
    prior_awards = find_prior_data(args.data or input_path, args.days)
    if prior_awards is not None:
        if isinstance(prior_awards, dict):
            # Try to unwrap
            for key in ("awards", "results", "data", "items"):
                if key in prior_awards and isinstance(prior_awards[key], list):
                    prior_awards = prior_awards[key]
                    break
            else:
                prior_awards = None
        if prior_awards is not None:
            print(f"  Prior:  {len(prior_awards):,} awards (for WoW comparison)", file=sys.stderr)
    else:
        print(f"  Prior:  none found (WoW comparison unavailable)", file=sys.stderr)

    # Compute report date from the data filename or use today
    report_date = today
    if args.data:
        try:
            basename = os.path.basename(args.data).replace(".json", "")
            parts = basename.split("_")
            candidate = parts[-1]
            datetime.strptime(candidate, "%Y-%m-%d")
            report_date = candidate
        except (ValueError, IndexError):
            pass

    # Generate report
    report_md = generate_report(awards, prior_awards, args.days, report_date)

    # Write output
    os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
    with open(output_path, "w") as f:
        f.write(report_md)

    # Stats
    line_count = report_md.count("\n")
    word_count = len(report_md.split())
    print(f"  Output: {line_count} lines, {word_count} words", file=sys.stderr)
    print(f"  Saved:  {output_path}", file=sys.stderr)


if __name__ == "__main__":
    main()
