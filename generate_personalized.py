#!/usr/bin/env python3
"""
Generate personalized newsletter variants by vertical or NAICS code.

This script filters the weekly newsletter to show only awards relevant to a specific vertical or NAICS code.
The "personalization" feature that makes readers think "this was written for me."

Usage:
    python3 generate_personalized.py Cloud              # Filter by vertical
    python3 generate_personalized.py Cybersecurity      # Filter by vertical
    python3 generate_personalized.py 541512             # Filter by NAICS (if available)

Available verticals: Cloud, Cybersecurity, AI/ML, FedRAMP, Data, etc.
"""

import json
import sys
from datetime import datetime
from pathlib import Path


def load_awards_data(data_path):
    """Load the raw awards JSON data."""
    with open(data_path, 'r') as f:
        return json.load(f)


def filter_by_vertical(awards, target_vertical):
    """
    Filter awards by vertical (primary method).

    Verticals are tags like: Cloud, Cybersecurity, AI/ML, FedRAMP, Data, etc.
    """
    filtered = []
    target_lower = target_vertical.lower()

    for award in awards:
        verticals = award.get('verticals', [])
        if verticals:
            # Check if any vertical matches (case-insensitive partial match)
            if any(target_lower in v.lower() for v in verticals):
                filtered.append(award)

    return filtered


def filter_by_naics(awards, target_naics):
    """
    Filter awards by NAICS code (fallback method when NAICS data is available).

    Match on exact NAICS or first 4 digits (industry group level).
    This allows 541512 to match both 541512 and 5415XX codes.
    """
    filtered = []
    target_prefix = str(target_naics)[:4]

    for award in awards:
        naics = award.get('naics_code')
        if naics:
            naics_str = str(naics)
            if naics_str == str(target_naics) or naics_str.startswith(target_prefix):
                filtered.append(award)

    return filtered


def format_currency(amount):
    """Format currency with B/M suffix."""
    if amount >= 1_000_000_000:
        return f"${amount / 1_000_000_000:.2f}B"
    elif amount >= 1_000_000:
        return f"${amount / 1_000_000:.1f}M"
    elif amount >= 1_000:
        return f"${amount / 1_000:.0f}K"
    else:
        return f"${amount:.2f}"


def get_naics_description(naics_code):
    """Map NAICS codes to business-friendly descriptions."""
    naics_map = {
        '541512': 'Cybersecurity & Computer Systems Design',
        '541511': 'Custom Computer Programming Services',
        '541519': 'Other Computer Related Services',
        '541330': 'Engineering Services',
        '541715': 'R&D in Physical, Engineering & Life Sciences',
        '518210': 'Data Processing, Hosting & Related Services',
        '541690': 'Scientific & Technical Consulting',
        '541611': 'Administrative Management Consulting',
        '541620': 'Environmental Consulting Services',
        '336411': 'Aircraft Manufacturing',
        '336414': 'Guided Missile & Space Vehicle Manufacturing',
        '237310': 'Highway, Street & Bridge Construction',
        '562910': 'Environmental Remediation Services',
    }

    # Try exact match first
    naics_str = str(naics_code)
    if naics_str in naics_map:
        return naics_map[naics_str]

    # Try 4-digit prefix match
    prefix = naics_str[:4]
    for key, val in naics_map.items():
        if key.startswith(prefix):
            return val

    return f"NAICS {naics_code}"


def calculate_stats(awards):
    """Calculate aggregate statistics for the filtered dataset."""
    total_value = sum(a.get('award_amount', 0) for a in awards)
    agencies = set(a.get('awarding_agency') for a in awards if a.get('awarding_agency'))
    recipients = set(a.get('recipient_name') for a in awards if a.get('recipient_name'))

    return {
        'count': len(awards),
        'total_value': total_value,
        'unique_agencies': len(agencies),
        'unique_recipients': len(recipients),
        'top_agencies': sorted(
            [(agency, sum(1 for a in awards if a.get('awarding_agency') == agency))
             for agency in agencies],
            key=lambda x: x[1],
            reverse=True
        )[:5],
        'top_recipients': sorted(
            [(recipient, sum(a.get('award_amount', 0) for a in awards if a.get('recipient_name') == recipient))
             for recipient in recipients],
            key=lambda x: x[1],
            reverse=True
        )[:5]
    }


def generate_markdown(awards, filter_value, stats, date_str, is_vertical=True):
    """Generate personalized newsletter markdown."""
    if is_vertical:
        title = filter_value
        subtitle = f"Weekly Digest for {filter_value} Contracts"
    else:
        naics_desc = get_naics_description(filter_value)
        title = naics_desc
        subtitle = f"Weekly Digest for NAICS {filter_value}"

    md = f"""# GovCon Intelligence: {title}
**{subtitle}** | {date_str}

---

## Your Numbers This Week

- **{stats['count']} awards** in your NAICS code
- **{format_currency(stats['total_value'])}** total contract value
- **{stats['unique_agencies']} agencies** awarding contracts
- **{stats['unique_recipients']} contractors** winning work

---

## 60-Second Brief

"""

    # Top 3 awards by value
    top_awards = sorted(awards, key=lambda x: x.get('award_amount', 0), reverse=True)[:3]

    if top_awards:
        md += "**Top opportunities in your space this week:**\n\n"
        for i, award in enumerate(top_awards, 1):
            amount = format_currency(award.get('award_amount', 0))
            agency = award.get('awarding_agency', 'Unknown Agency')
            recipient = award.get('recipient_name', 'Unknown Recipient')
            md += f"{i}. **{agency}** awarded {amount} to {recipient}\n"
        md += "\n"

    # Agency hotspots
    if stats['top_agencies']:
        md += "**Agency hotspots (most active buyers):**\n\n"
        for agency, count in stats['top_agencies'][:3]:
            md += f"- **{agency}**: {count} awards this week\n"
        md += "\n"

    md += "---\n\n## All Awards This Week\n\n"

    # Sort by amount descending
    sorted_awards = sorted(awards, key=lambda x: x.get('award_amount', 0), reverse=True)

    for award in sorted_awards:
        amount = format_currency(award.get('award_amount', 0))
        agency = award.get('awarding_agency', 'Unknown Agency')
        recipient = award.get('recipient_name', 'Unknown Recipient')
        description = award.get('description', 'No description available')[:200]
        start = award.get('start_date', 'N/A')
        end = award.get('end_date', 'N/A')
        vehicle = award.get('vehicle')
        set_aside = award.get('set_aside')

        md += f"### {agency} | {amount}\n\n"
        md += f"**Winner:** {recipient}\n\n"
        md += f"**Description:** {description}\n\n"
        md += f"**Period:** {start} to {end}\n\n"

        if vehicle:
            md += f"**Vehicle:** {vehicle}\n\n"
        if set_aside:
            md += f"**Set-Aside:** {set_aside}\n\n"

        md += "---\n\n"

    # Market Intelligence section
    md += "## Market Intelligence\n\n"
    md += f"### Who's Winning in {title}\n\n"

    if stats['top_recipients']:
        for recipient, total_value in stats['top_recipients'][:5]:
            md += f"- **{recipient}**: {format_currency(total_value)} total awards\n"
        md += "\n"

    md += "### Where to Focus Your BD Efforts\n\n"

    if stats['top_agencies']:
        top_agency, top_count = stats['top_agencies'][0]
        md += f"**{top_agency}** is the most active buyer in your space with {top_count} awards this week. "
        md += "If you're not tracking their upcoming solicitations, you're missing opportunities.\n\n"

        md += "**Action items:**\n\n"
        if is_vertical:
            md += f"1. Set SAM.gov alerts for {filter_value} keywords + {top_agency}\n"
        else:
            md += f"1. Set SAM.gov alerts for NAICS {filter_value} + {top_agency}\n"
        md += f"2. Review {top_agency}'s forecast for upcoming recompetes\n"
        md += "3. Identify teaming partners who have recent wins with this agency\n\n"

    md += "---\n\n"
    if is_vertical:
        md += f"*This personalized digest was generated from {len(awards)} awards in the {filter_value} vertical. "
        md += f"Want a different vertical? Run: `python3 generate_personalized.py [vertical-name]`*\n"
    else:
        md += f"*This personalized digest was generated from {len(awards)} awards in NAICS {filter_value}. "
        md += f"Want a different NAICS code? Run: `python3 generate_personalized.py [your-naics]`*\n"

    return md


def main():
    if len(sys.argv) < 2:
        print("Usage: python3 generate_personalized.py <VERTICAL_OR_NAICS>")
        print("\nExamples (by vertical - preferred):")
        print("  Cloud          - Cloud computing contracts")
        print("  Cybersecurity  - Cybersecurity contracts")
        print("  AI             - AI/ML contracts")
        print("  FedRAMP        - FedRAMP-related contracts")
        print("\nExamples (by NAICS code - when available):")
        print("  541512  - Cybersecurity & Computer Systems Design")
        print("  541511  - Custom Computer Programming Services")
        print("  518210  - Data Processing, Hosting & Related Services")
        sys.exit(1)

    filter_value = sys.argv[1]

    # Paths
    script_dir = Path(__file__).parent
    data_path = script_dir / 'data' / 'govcon_awards_2026-03-18.json'
    output_dir = script_dir / 'output' / 'personalized'
    output_dir.mkdir(parents=True, exist_ok=True)

    if not data_path.exists():
        print(f"Error: Data file not found at {data_path}")
        sys.exit(1)

    # Load data
    print(f"Loading awards data...")
    awards = load_awards_data(data_path)
    print(f"Total awards in dataset: {len(awards)}")

    # Determine if it's a vertical or NAICS code
    is_vertical = not filter_value.isdigit()

    # Filter
    if is_vertical:
        print(f"Filtering for vertical: {filter_value}...")
        filtered = filter_by_vertical(awards, filter_value)
        print(f"Found {len(filtered)} awards matching vertical '{filter_value}'")
    else:
        print(f"Filtering for NAICS {filter_value}...")
        filtered = filter_by_naics(awards, filter_value)
        print(f"Found {len(filtered)} awards matching NAICS {filter_value}")

    if not filtered:
        if is_vertical:
            print(f"\nNo awards found for vertical '{filter_value}'.")
            print("\nAvailable verticals in this dataset:")
            all_verticals = set()
            for award in awards:
                for v in award.get('verticals', []):
                    all_verticals.add(v)
            for v in sorted(all_verticals):
                count = sum(1 for a in awards if v in a.get('verticals', []))
                print(f"  {v}: {count} awards")
        else:
            print(f"\nNo awards found for NAICS {filter_value}.")
            print("This could mean:")
            print("1. No contracts were awarded in this NAICS code this week")
            print("2. The NAICS data is incomplete in the source")
            print("\nTry filtering by vertical instead (more data coverage)")
        sys.exit(0)

    # Calculate stats
    stats = calculate_stats(filtered)

    # Generate markdown
    date_str = datetime.now().strftime("%B %d, %Y")
    markdown = generate_markdown(filtered, filter_value, stats, date_str, is_vertical)

    # Write output
    if is_vertical:
        # Sanitize filename (remove slashes, spaces, special chars)
        safe_name = filter_value.lower().replace('/', '-').replace(' ', '-').replace('_', '-')
        output_path = output_dir / f'newsletter-{safe_name}.md'
    else:
        output_path = output_dir / f'newsletter-naics-{filter_value}.md'

    with open(output_path, 'w') as f:
        f.write(markdown)

    print(f"\nSuccess! Personalized newsletter written to:")
    print(f"  {output_path}")
    print(f"\nSummary:")
    print(f"  {stats['count']} awards")
    print(f"  {format_currency(stats['total_value'])} total value")
    print(f"  {stats['unique_agencies']} agencies")
    print(f"  {stats['unique_recipients']} unique contractors")


if __name__ == '__main__':
    main()
