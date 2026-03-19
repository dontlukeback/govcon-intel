#!/usr/bin/env python3
"""
Generate urgent recompete alerts for high-value contracts ending soon.

This script scans award data for contracts ending within 180 days,
ranks by value, and generates "breaking intel" email content.

These become mid-week "urgent alert" emails separate from the weekly digest.

Usage:
    python3 generate_alerts.py
    python3 generate_alerts.py --days 120  # Custom threshold
    python3 generate_alerts.py --min-value 10000000  # Min $10M
"""

import json
import argparse
from datetime import datetime, timedelta
from pathlib import Path


def load_awards_data(data_path):
    """Load the raw awards JSON data."""
    with open(data_path, 'r') as f:
        return json.load(f)


def parse_date(date_str):
    """Parse date string to datetime object."""
    if not date_str:
        return None
    try:
        return datetime.strptime(date_str, '%Y-%m-%d')
    except ValueError:
        return None


def find_expiring_contracts(awards, days_threshold=180, min_value=0):
    """
    Find contracts ending within N days.

    Returns list of (award, days_until_expiration) tuples.
    """
    today = datetime.now()
    threshold_date = today + timedelta(days=days_threshold)

    expiring = []

    for award in awards:
        end_date = parse_date(award.get('end_date'))
        if not end_date:
            continue

        # Only future expirations
        if end_date < today:
            continue

        # Within threshold
        if end_date <= threshold_date:
            days_until = (end_date - today).days
            value = award.get('award_amount', 0)

            if value >= min_value:
                expiring.append((award, days_until))

    # Sort by value descending
    expiring.sort(key=lambda x: x[0].get('award_amount', 0), reverse=True)

    return expiring


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


def get_urgency_level(days_until):
    """Determine urgency level based on days remaining."""
    if days_until <= 60:
        return "CRITICAL", "Contract expires in 2 months or less"
    elif days_until <= 120:
        return "HIGH", "Contract expires in 4 months or less"
    else:
        return "MODERATE", "Contract expires within 6 months"


def generate_alert_content(award, days_until):
    """
    Generate 3-paragraph alert for a single contract:
    1. What it is (scope, value, incumbent)
    2. Who should pursue (ideal company profile)
    3. What to do this week (specific actions)
    """
    amount = format_currency(award.get('award_amount', 0))
    agency = award.get('awarding_agency', 'Unknown Agency')
    recipient = award.get('recipient_name', 'Unknown Recipient')
    description = award.get('description', 'No description available')
    naics = award.get('naics_code')
    naics_desc = award.get('naics_description', '')
    vehicle = award.get('vehicle')
    set_aside = award.get('set_aside')
    end_date = award.get('end_date')

    urgency, urgency_desc = get_urgency_level(days_until)

    # Paragraph 1: What it is
    para1 = f"**{agency}** has a **{amount}** contract expiring in **{days_until} days** (ends {end_date}). "
    para1 += f"Current incumbent: **{recipient}**. "

    if naics:
        para1 += f"NAICS {naics}"
        if naics_desc:
            para1 += f" ({naics_desc})"
        para1 += ". "

    if vehicle:
        para1 += f"Contract vehicle: {vehicle}. "

    if set_aside:
        para1 += f"Set-aside: {set_aside}. "

    para1 += f"\n\n**Scope:** {description[:250]}"
    if len(description) > 250:
        para1 += "..."

    # Paragraph 2: Who should pursue
    para2 = "\n\n**Who should pursue this:**\n\n"

    # Determine ideal company profile
    value = award.get('award_amount', 0)
    if value >= 100_000_000:
        para2 += f"Large prime contractors with {format_currency(value * 0.5)}+ in past performance. "
    elif value >= 10_000_000:
        para2 += f"Mid-tier firms or large subs with {format_currency(value * 0.3)}+ in past performance. "
    else:
        para2 += f"Small businesses with {format_currency(value * 0.2)}+ in past performance. "

    if naics:
        para2 += f"Must have demonstrated experience in NAICS {naics}. "

    if set_aside:
        para2 += f"Must hold {set_aside} certification. "

    para2 += f"If you're NOT the incumbent ({recipient}), you need a compelling technical discriminator or significant price advantage."

    # Paragraph 3: What to do this week
    para3 = "\n\n**Action items for this week:**\n\n"

    if days_until <= 60:
        para3 += "- **URGENT:** RFP may already be out or imminent. Check SAM.gov daily.\n"
        para3 += f"- Contact the contracting officer at {agency} TODAY to request RFI/sources sought if not yet published.\n"
        para3 += "- Assemble your capture team now. You have 60 days or less to respond.\n"
    elif days_until <= 120:
        para3 += "- Set SAM.gov alerts for this contract number and agency.\n"
        para3 += f"- Request a pre-RFP meeting with {agency} program office to discuss upcoming requirements.\n"
        para3 += "- Start building your teaming strategy. Identify complementary partners.\n"
    else:
        para3 += "- Add this to your BD pipeline tracker. Review monthly.\n"
        para3 += f"- Research {recipient}'s performance on this contract (CPARS, protests, past performance).\n"
        para3 += f"- Start relationship-building with {agency} stakeholders.\n"

    if vehicle:
        para3 += f"- Verify you have access to {vehicle} or identify a prime partner who does.\n"

    if naics:
        para3 += f"- Audit your past performance library for NAICS {naics} references.\n"

    return f"{para1}{para2}{para3}"


def generate_alert_email(expiring_contracts, days_threshold, min_value):
    """Generate full alert email markdown."""
    today = datetime.now().strftime("%B %d, %Y")

    md = f"""# RECOMPETE ALERT: High-Value Contracts Expiring Soon
**Urgent Intelligence Brief** | {today}

---

## Summary

We've identified **{len(expiring_contracts)}** high-value contracts expiring within {days_threshold} days. Total value at risk: **{format_currency(sum(c[0].get('award_amount', 0) for c in expiring_contracts))}**.

These contracts either have no visible RFP activity yet (bridge contract risk) or are in active solicitation. If you're not tracking these, you're leaving opportunities on the table.

---

"""

    # Quick reference table
    md += "## Quick Reference\n\n"
    md += "| Agency | Value | Incumbent | Days Left | Urgency |\n"
    md += "|--------|-------|-----------|-----------|----------|\n"

    for award, days in expiring_contracts:
        agency = award.get('awarding_agency', 'Unknown')[:30]
        amount = format_currency(award.get('award_amount', 0))
        recipient = award.get('recipient_name', 'Unknown')[:30]
        urgency, _ = get_urgency_level(days)

        md += f"| {agency} | {amount} | {recipient} | {days} | **{urgency}** |\n"

    md += "\n---\n\n"

    # Detailed alerts
    md += "## Detailed Intelligence\n\n"

    for i, (award, days) in enumerate(expiring_contracts, 1):
        amount = format_currency(award.get('award_amount', 0))
        agency = award.get('awarding_agency', 'Unknown Agency')
        urgency, urgency_desc = get_urgency_level(days)

        md += f"### {i}. {agency} | {amount} | {days} days\n\n"
        md += f"**Urgency Level:** {urgency} — {urgency_desc}\n\n"
        md += generate_alert_content(award, days)
        md += "\n\n---\n\n"

    # Bottom matter
    md += "## How to Use This Alert\n\n"
    md += "**If you see a contract in your domain:**\n\n"
    md += "1. **CRITICAL (60 days or less):** Drop everything. RFP is imminent or already out.\n"
    md += "2. **HIGH (60-120 days):** Start capture activities this week. Build team, engage agency.\n"
    md += "3. **MODERATE (120-180 days):** Add to pipeline. Begin relationship-building.\n\n"

    md += "**If you DON'T see your domain:** That's good news. No urgent fires in your space this week.\n\n"

    md += "---\n\n"
    md += f"*This alert was generated from contracts ending within {days_threshold} days with value ≥ {format_currency(min_value)}. "
    md += "These are mid-week urgent briefs, separate from the Monday weekly digest.*\n\n"
    md += "*Questions? Reply to this email.*\n"

    return md


def main():
    parser = argparse.ArgumentParser(
        description='Generate urgent recompete alerts for high-value contracts ending soon'
    )
    parser.add_argument(
        '--days',
        type=int,
        default=180,
        help='Days threshold (default: 180)'
    )
    parser.add_argument(
        '--min-value',
        type=float,
        default=10_000_000,
        help='Minimum contract value in dollars (default: 10,000,000)'
    )
    parser.add_argument(
        '--max-alerts',
        type=int,
        default=10,
        help='Maximum number of alerts to generate (default: 10)'
    )

    args = parser.parse_args()

    # Paths
    script_dir = Path(__file__).parent
    data_path = script_dir / 'data' / 'govcon_awards_2026-03-18.json'
    output_dir = script_dir / 'output' / 'alerts'
    output_dir.mkdir(parents=True, exist_ok=True)

    if not data_path.exists():
        print(f"Error: Data file not found at {data_path}")
        return 1

    # Load and process
    print(f"Loading awards data...")
    awards = load_awards_data(data_path)
    print(f"Total awards in dataset: {len(awards)}")

    print(f"\nScanning for contracts expiring within {args.days} days...")
    print(f"Minimum value: {format_currency(args.min_value)}")

    expiring = find_expiring_contracts(
        awards,
        days_threshold=args.days,
        min_value=args.min_value
    )

    print(f"Found {len(expiring)} contracts meeting criteria")

    if not expiring:
        print("\nNo high-value contracts expiring soon. No alert needed this week.")
        return 0

    # Limit to top N by value
    expiring = expiring[:args.max_alerts]

    # Generate email
    email_content = generate_alert_email(expiring, args.days, args.min_value)

    # Write output
    today = datetime.now().strftime("%Y-%m-%d")
    output_path = output_dir / f'recompete-alert-{today}.md'

    with open(output_path, 'w') as f:
        f.write(email_content)

    print(f"\nSuccess! Alert email written to:")
    print(f"  {output_path}")

    print(f"\nAlert Summary:")
    print(f"  {len(expiring)} contracts")
    print(f"  {format_currency(sum(c[0].get('award_amount', 0) for c in expiring))} total value")

    # Urgency breakdown
    critical = sum(1 for _, days in expiring if days <= 60)
    high = sum(1 for _, days in expiring if 60 < days <= 120)
    moderate = sum(1 for _, days in expiring if days > 120)

    print(f"\nUrgency Breakdown:")
    print(f"  CRITICAL (≤60 days): {critical}")
    print(f"  HIGH (60-120 days): {high}")
    print(f"  MODERATE (120-180 days): {moderate}")

    print(f"\nTop 3 by value:")
    for i, (award, days) in enumerate(expiring[:3], 1):
        amount = format_currency(award.get('award_amount', 0))
        agency = award.get('awarding_agency', 'Unknown')
        print(f"  {i}. {agency}: {amount} ({days} days)")

    return 0


if __name__ == '__main__':
    exit(main())
