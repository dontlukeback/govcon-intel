#!/usr/bin/env python3
"""
Agency Intelligence Pages Generator

Creates public SEO-optimized landing pages for federal agencies.
People searching for "[Agency] IT contracts" or "[Agency] contract awards" land on our pages.

This script:
1. Reads all awards data (current + archived)
2. Groups by awarding_agency
3. For each agency with 5+ awards, generates: landing/agencies/{slug}.html
4. Creates landing/agencies/index.html (directory of all agencies)

Usage:
    python3 generate_agency_pages.py
    python3 generate_agency_pages.py --min-awards 10

Output:
    - landing/agencies/{slug}.html (e.g., department-of-energy.html)
    - landing/agencies/index.html (directory page)

Between contractor pages (20+) and agency pages (10+), we're creating 30+ SEO-optimized
pages that auto-regenerate weekly. This is a content moat that compounds.
"""

import json
import argparse
from pathlib import Path
from datetime import datetime
from collections import defaultdict
from typing import Dict, List, Any
import re


def slugify(text: str) -> str:
    """Convert agency name to URL-friendly slug."""
    text = text.lower()
    text = re.sub(r'[^\w\s-]', '', text)
    text = re.sub(r'[-\s]+', '-', text)
    return text.strip('-')


def load_all_awards() -> List[Dict[str, Any]]:
    """
    Load all available award data, preferring the cumulative all_awards.json.
    More weeks = richer analysis (data moat).
    """
    awards = []
    data_dir = Path(__file__).parent / "data"
    archive_dir = data_dir / "archive"

    # Prefer cumulative dataset (12-week backfill lives here)
    all_awards_path = archive_dir / "all_awards.json"
    if all_awards_path.exists():
        print(f"📊 Loading cumulative dataset: {all_awards_path.name}")
        try:
            with open(all_awards_path, 'r', encoding='utf-8') as f:
                awards = json.load(f)
                print(f"   Loaded {len(awards):,} awards from {all_awards_path.name}")
        except Exception as e:
            print(f"   ⚠️  Failed to load {all_awards_path.name}: {e}")
            awards = []

    # Fallback: load individual weekly files if cumulative dataset missing or empty
    if not awards:
        current_files = list(data_dir.glob("govcon_awards_*.json"))
        archive_files = list(archive_dir.glob("govcon_awards_*.json")) if archive_dir.exists() else []
        all_files = current_files + archive_files

        if not all_files:
            print("⚠️  No award data found. Run pipeline.py first.")
            return []

        print(f"📊 Fallback: loading data from {len(all_files)} weekly file(s)...")
        for file_path in sorted(all_files):
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    awards.extend(data)
                    print(f"   Loaded {len(data):,} awards from {file_path.name}")
            except Exception as e:
                print(f"   ⚠️  Failed to load {file_path.name}: {e}")

    print(f"✅ Total awards loaded: {len(awards):,}\n")
    return awards


def group_by_agency(awards: List[Dict]) -> Dict[str, List[Dict]]:
    """Group awards by awarding agency."""
    agency_awards = defaultdict(list)

    for award in awards:
        agency = award.get("awarding_agency", "Unknown")
        if agency and agency != "Unknown":
            agency_awards[agency].append(award)

    return dict(agency_awards)


def calculate_agency_metrics(awards: List[Dict]) -> Dict[str, Any]:
    """Calculate key metrics for an agency."""
    total_count = len(awards)
    total_value = sum(award.get("award_amount", 0) for award in awards)
    avg_value = total_value / total_count if total_count > 0 else 0

    # Top contractors
    contractor_stats = defaultdict(lambda: {"count": 0, "value": 0})
    for award in awards:
        contractor = award.get("recipient_name", "Unknown")
        contractor_stats[contractor]["count"] += 1
        contractor_stats[contractor]["value"] += award.get("award_amount", 0)

    top_contractors = sorted(
        contractor_stats.items(),
        key=lambda x: x[1]["value"],
        reverse=True
    )[:10]

    # Verticals
    vertical_stats = defaultdict(lambda: {"count": 0, "value": 0})
    for award in awards:
        verticals = award.get("verticals", [])
        if not verticals:
            verticals = ["Uncategorized"]
        for vertical in verticals:
            vertical_stats[vertical]["count"] += 1
            vertical_stats[vertical]["value"] += award.get("award_amount", 0)

    top_verticals = sorted(
        vertical_stats.items(),
        key=lambda x: x[1]["value"],
        reverse=True
    )[:5]

    # Top 10 awards by value
    top_awards = sorted(
        awards,
        key=lambda x: x.get("award_amount", 0),
        reverse=True
    )[:10]

    return {
        "total_count": total_count,
        "total_value": total_value,
        "avg_value": avg_value,
        "top_contractors": top_contractors,
        "top_verticals": top_verticals,
        "top_awards": top_awards
    }


def format_currency(amount: float) -> str:
    """Format currency with B/M/K suffixes."""
    if amount >= 1_000_000_000:
        return f"${amount / 1_000_000_000:.2f}B"
    elif amount >= 1_000_000:
        return f"${amount / 1_000_000:.2f}M"
    elif amount >= 1_000:
        return f"${amount / 1_000:.2f}K"
    else:
        return f"${amount:,.0f}"


def generate_agency_page(agency_name: str, metrics: Dict[str, Any], slug: str) -> str:
    """Generate HTML for an agency page."""

    # Build top contractors HTML
    contractors_html = ""
    for i, (contractor, stats) in enumerate(metrics["top_contractors"][:10], 1):
        contractors_html += f"""
                    <div class="contractor-row">
                        <div class="contractor-rank">#{i}</div>
                        <div class="contractor-info">
                            <div class="contractor-name">{contractor}</div>
                            <div class="contractor-stats">
                                {stats['count']} award{"s" if stats['count'] != 1 else ""} · {format_currency(stats['value'])}
                            </div>
                        </div>
                    </div>"""

    # Build verticals HTML
    verticals_html = ""
    for vertical, stats in metrics["top_verticals"]:
        percentage = (stats["count"] / metrics["total_count"] * 100) if metrics["total_count"] > 0 else 0
        verticals_html += f"""
                    <div class="vertical-item">
                        <div class="vertical-header">
                            <span class="vertical-name">{vertical}</span>
                            <span class="vertical-count">{stats['count']} awards</span>
                        </div>
                        <div class="vertical-bar">
                            <div class="vertical-fill" style="width: {percentage}%"></div>
                        </div>
                        <div class="vertical-value">{format_currency(stats['value'])}</div>
                    </div>"""

    # Build top awards HTML
    awards_html = ""
    for award in metrics["top_awards"]:
        description = award.get("description", "No description available")
        if len(description) > 150:
            description = description[:147] + "..."

        awards_html += f"""
                    <div class="award-card">
                        <div class="award-header">
                            <div class="award-amount">{format_currency(award.get('award_amount', 0))}</div>
                            <div class="award-date">{award.get('start_date', 'N/A')}</div>
                        </div>
                        <div class="award-contractor">{award.get('recipient_name', 'Unknown')}</div>
                        <div class="award-description">{description}</div>
                        <div class="award-meta">
                            <span class="award-id">{award.get('award_id', 'N/A')}</span>
                            {f'<span class="award-vertical">{", ".join(award.get("verticals", []))}</span>' if award.get("verticals") else ''}
                        </div>
                    </div>"""

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{agency_name} IT Contracts & Awards | Federal Spending Intelligence</title>
    <meta name="description" content="Track {agency_name} IT contract awards, spending trends, and top contractors. {format_currency(metrics['total_value'])} in federal IT spending across {metrics['total_count']} awards.">
    <link rel="canonical" href="https://dontlukeback.github.io/govcon-intel/agencies/{slug}.html">
    <meta property="og:title" content="{agency_name} IT Contracts & Awards">
    <meta property="og:description" content="{format_currency(metrics['total_value'])} in federal IT spending across {metrics['total_count']} awards. Track spending trends and top contractors.">
    <meta property="og:type" content="website">
    <meta property="og:url" content="https://dontlukeback.github.io/govcon-intel/agencies/{slug}.html">
    <meta name="twitter:card" content="summary_large_image">
    <meta name="twitter:title" content="{agency_name} IT Contracts & Awards">
    <meta name="twitter:description" content="{format_currency(metrics['total_value'])} in federal IT spending across {metrics['total_count']} awards.">
    <style>
        :root {{
            --navy: #0A1628;
            --navy-mid: #132238;
            --navy-light: #1B3A5C;
            --gold: #C5A44E;
            --gold-light: #D4BA72;
            --gray-50: #F9FAFB;
            --gray-100: #F3F4F6;
            --gray-200: #E5E7EB;
            --gray-600: #4B5563;
            --gray-800: #1F2937;
        }}

        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}

        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, sans-serif;
            background: var(--navy);
            color: var(--gray-100);
            line-height: 1.6;
        }}

        .header {{
            background: var(--navy-mid);
            border-bottom: 1px solid var(--navy-light);
            padding: 1rem 0;
        }}

        .header-content {{
            max-width: 1200px;
            margin: 0 auto;
            padding: 0 2rem;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }}

        .logo {{
            font-size: 1.25rem;
            font-weight: 700;
            color: var(--gold);
            text-decoration: none;
        }}

        .nav a {{
            color: var(--gray-100);
            text-decoration: none;
            margin-left: 2rem;
            font-size: 0.95rem;
        }}

        .nav a:hover {{
            color: var(--gold);
        }}

        .container {{
            max-width: 1200px;
            margin: 0 auto;
            padding: 3rem 2rem;
        }}

        .breadcrumb {{
            font-size: 0.9rem;
            color: var(--gray-600);
            margin-bottom: 2rem;
        }}

        .breadcrumb a {{
            color: var(--gold);
            text-decoration: none;
        }}

        .breadcrumb a:hover {{
            text-decoration: underline;
        }}

        .page-header {{
            margin-bottom: 3rem;
        }}

        .page-title {{
            font-size: 2.5rem;
            font-weight: 700;
            color: var(--gold);
            margin-bottom: 1rem;
        }}

        .page-subtitle {{
            font-size: 1.25rem;
            color: var(--gray-600);
        }}

        .stats-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 1.5rem;
            margin-bottom: 3rem;
        }}

        .stat-card {{
            background: var(--navy-mid);
            border: 1px solid var(--navy-light);
            border-radius: 8px;
            padding: 1.5rem;
        }}

        .stat-label {{
            font-size: 0.9rem;
            color: var(--gray-600);
            margin-bottom: 0.5rem;
        }}

        .stat-value {{
            font-size: 2rem;
            font-weight: 700;
            color: var(--gold);
        }}

        .section {{
            margin-bottom: 3rem;
        }}

        .section-title {{
            font-size: 1.75rem;
            font-weight: 700;
            margin-bottom: 1.5rem;
            color: var(--gold-light);
        }}

        .card {{
            background: var(--navy-mid);
            border: 1px solid var(--navy-light);
            border-radius: 8px;
            padding: 2rem;
            margin-bottom: 1.5rem;
        }}

        .contractor-row {{
            display: flex;
            align-items: center;
            padding: 1rem 0;
            border-bottom: 1px solid var(--navy-light);
        }}

        .contractor-row:last-child {{
            border-bottom: none;
        }}

        .contractor-rank {{
            font-size: 1.25rem;
            font-weight: 700;
            color: var(--gray-600);
            width: 3rem;
        }}

        .contractor-info {{
            flex: 1;
        }}

        .contractor-name {{
            font-weight: 600;
            color: var(--gray-100);
            margin-bottom: 0.25rem;
        }}

        .contractor-stats {{
            font-size: 0.9rem;
            color: var(--gray-600);
        }}

        .vertical-item {{
            margin-bottom: 1.5rem;
        }}

        .vertical-header {{
            display: flex;
            justify-content: space-between;
            margin-bottom: 0.5rem;
        }}

        .vertical-name {{
            font-weight: 600;
            color: var(--gray-100);
        }}

        .vertical-count {{
            font-size: 0.9rem;
            color: var(--gray-600);
        }}

        .vertical-bar {{
            background: var(--navy);
            height: 8px;
            border-radius: 4px;
            overflow: hidden;
            margin-bottom: 0.5rem;
        }}

        .vertical-fill {{
            background: var(--gold);
            height: 100%;
            transition: width 0.3s ease;
        }}

        .vertical-value {{
            font-size: 0.9rem;
            color: var(--gold-light);
        }}

        .award-card {{
            background: var(--navy);
            border: 1px solid var(--navy-light);
            border-radius: 6px;
            padding: 1.5rem;
            margin-bottom: 1rem;
        }}

        .award-card:last-child {{
            margin-bottom: 0;
        }}

        .award-header {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 0.75rem;
        }}

        .award-amount {{
            font-size: 1.5rem;
            font-weight: 700;
            color: var(--gold);
        }}

        .award-date {{
            font-size: 0.9rem;
            color: var(--gray-600);
        }}

        .award-contractor {{
            font-weight: 600;
            color: var(--gray-100);
            margin-bottom: 0.5rem;
        }}

        .award-description {{
            color: var(--gray-600);
            margin-bottom: 0.75rem;
            font-size: 0.95rem;
        }}

        .award-meta {{
            display: flex;
            gap: 1rem;
            font-size: 0.85rem;
            color: var(--gray-600);
        }}

        .award-id {{
            font-family: monospace;
        }}

        .award-vertical {{
            color: var(--gold-light);
        }}

        .cta-section {{
            background: var(--navy-mid);
            border: 2px solid var(--gold);
            border-radius: 8px;
            padding: 3rem;
            text-align: center;
            margin-top: 3rem;
        }}

        .cta-title {{
            font-size: 1.75rem;
            font-weight: 700;
            color: var(--gold);
            margin-bottom: 1rem;
        }}

        .cta-description {{
            font-size: 1.1rem;
            color: var(--gray-600);
            margin-bottom: 2rem;
        }}

        .cta-button {{
            display: inline-block;
            background: var(--gold);
            color: var(--navy);
            padding: 1rem 2rem;
            border-radius: 6px;
            text-decoration: none;
            font-weight: 600;
            font-size: 1.1rem;
            transition: background 0.3s ease;
        }}

        .cta-button:hover {{
            background: var(--gold-light);
        }}

        @media (max-width: 768px) {{
            .page-title {{
                font-size: 2rem;
            }}

            .stats-grid {{
                grid-template-columns: 1fr;
            }}

            .contractor-row {{
                flex-direction: column;
                align-items: flex-start;
            }}

            .contractor-rank {{
                margin-bottom: 0.5rem;
            }}
        }}
    </style>
</head>
<body>
    <header class="header">
        <div class="header-content">
            <a href="../index.html" class="logo">GovCon Intelligence</a>
            <nav class="nav">
                <a href="../index.html">Home</a>
                <a href="index.html">Agencies</a>
                <a href="../insights.html">Insights</a>
            </nav>
        </div>
    </header>

    <div class="container">
        <div class="breadcrumb">
            <a href="../index.html">Home</a> / <a href="index.html">Agencies</a> / {agency_name}
        </div>

        <div class="page-header">
            <h1 class="page-title">{agency_name}</h1>
            <p class="page-subtitle">IT Contract Awards & Spending Intelligence</p>
        </div>

        <div class="stats-grid">
            <div class="stat-card">
                <div class="stat-label">Total IT Spending</div>
                <div class="stat-value">{format_currency(metrics['total_value'])}</div>
            </div>
            <div class="stat-card">
                <div class="stat-label">Total Awards</div>
                <div class="stat-value">{metrics['total_count']:,}</div>
            </div>
            <div class="stat-card">
                <div class="stat-label">Average Award</div>
                <div class="stat-value">{format_currency(metrics['avg_value'])}</div>
            </div>
        </div>

        <div class="section">
            <h2 class="section-title">Top Contractors</h2>
            <div class="card">
                {contractors_html}
            </div>
        </div>

        <div class="section">
            <h2 class="section-title">Technology Areas</h2>
            <div class="card">
                {verticals_html}
            </div>
        </div>

        <div class="section">
            <h2 class="section-title">Top 10 Awards by Value</h2>
            {awards_html}
        </div>

        <div class="cta-section">
            <h2 class="cta-title">Track {agency_name} Spending Weekly</h2>
            <p class="cta-description">Get alerts when {agency_name} awards new contracts in your tech area. Real-time competitive intelligence delivered to your inbox.</p>
            <a href="https://buttondown.com/govcon" class="cta-button">Subscribe Now</a>
        </div>
    </div>

    <script src="../js/tracker.js"></script>
</body>
</html>"""

    return html


def generate_index_page(agencies: List[tuple]) -> str:
    """Generate the agency directory index page."""

    # Sort agencies by total value
    agencies_sorted = sorted(agencies, key=lambda x: x[2], reverse=True)

    # Build agency cards HTML
    agency_cards_html = ""
    for agency_name, slug, total_value, award_count in agencies_sorted:
        agency_cards_html += f"""
            <a href="{slug}.html" class="agency-card">
                <div class="agency-name">{agency_name}</div>
                <div class="agency-stats">
                    <div class="agency-stat">
                        <div class="stat-value">{format_currency(total_value)}</div>
                        <div class="stat-label">Total Spending</div>
                    </div>
                    <div class="agency-stat">
                        <div class="stat-value">{award_count:,}</div>
                        <div class="stat-label">Awards</div>
                    </div>
                </div>
            </a>"""

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Federal Agency IT Contracts Directory | Government Contract Intelligence</title>
    <meta name="description" content="Browse federal agency IT contract awards and spending data. Track Department of Defense, VA, DHS, and other agency procurement across {len(agencies_sorted)} agencies.">
    <link rel="canonical" href="https://dontlukeback.github.io/govcon-intel/agencies/">
    <meta property="og:title" content="Federal Agency IT Contracts Directory">
    <meta property="og:description" content="Track IT contract awards across {len(agencies_sorted)} federal agencies. Real-time spending intelligence.">
    <meta property="og:type" content="website">
    <meta property="og:url" content="https://dontlukeback.github.io/govcon-intel/agencies/">
    <meta name="twitter:card" content="summary_large_image">
    <style>
        :root {{
            --navy: #0A1628;
            --navy-mid: #132238;
            --navy-light: #1B3A5C;
            --gold: #C5A44E;
            --gold-light: #D4BA72;
            --gray-50: #F9FAFB;
            --gray-100: #F3F4F6;
            --gray-200: #E5E7EB;
            --gray-600: #4B5563;
            --gray-800: #1F2937;
        }}

        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}

        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, sans-serif;
            background: var(--navy);
            color: var(--gray-100);
            line-height: 1.6;
        }}

        .header {{
            background: var(--navy-mid);
            border-bottom: 1px solid var(--navy-light);
            padding: 1rem 0;
        }}

        .header-content {{
            max-width: 1200px;
            margin: 0 auto;
            padding: 0 2rem;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }}

        .logo {{
            font-size: 1.25rem;
            font-weight: 700;
            color: var(--gold);
            text-decoration: none;
        }}

        .nav a {{
            color: var(--gray-100);
            text-decoration: none;
            margin-left: 2rem;
            font-size: 0.95rem;
        }}

        .nav a:hover {{
            color: var(--gold);
        }}

        .container {{
            max-width: 1200px;
            margin: 0 auto;
            padding: 3rem 2rem;
        }}

        .page-header {{
            text-align: center;
            margin-bottom: 3rem;
        }}

        .page-title {{
            font-size: 2.5rem;
            font-weight: 700;
            color: var(--gold);
            margin-bottom: 1rem;
        }}

        .page-subtitle {{
            font-size: 1.25rem;
            color: var(--gray-600);
        }}

        .agencies-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(350px, 1fr));
            gap: 1.5rem;
            margin-top: 3rem;
        }}

        .agency-card {{
            background: var(--navy-mid);
            border: 1px solid var(--navy-light);
            border-radius: 8px;
            padding: 2rem;
            text-decoration: none;
            color: inherit;
            transition: all 0.3s ease;
        }}

        .agency-card:hover {{
            border-color: var(--gold);
            transform: translateY(-2px);
        }}

        .agency-name {{
            font-size: 1.25rem;
            font-weight: 700;
            color: var(--gray-100);
            margin-bottom: 1rem;
        }}

        .agency-stats {{
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 1rem;
        }}

        .agency-stat {{
            text-align: center;
        }}

        .stat-value {{
            font-size: 1.5rem;
            font-weight: 700;
            color: var(--gold);
        }}

        .stat-label {{
            font-size: 0.85rem;
            color: var(--gray-600);
            margin-top: 0.25rem;
        }}

        @media (max-width: 768px) {{
            .page-title {{
                font-size: 2rem;
            }}

            .agencies-grid {{
                grid-template-columns: 1fr;
            }}
        }}
    </style>
</head>
<body>
    <header class="header">
        <div class="header-content">
            <a href="../index.html" class="logo">GovCon Intelligence</a>
            <nav class="nav">
                <a href="../index.html">Home</a>
                <a href="index.html">Agencies</a>
                <a href="../insights.html">Insights</a>
            </nav>
        </div>
    </header>

    <div class="container">
        <div class="page-header">
            <h1 class="page-title">Federal Agency IT Contracts</h1>
            <p class="page-subtitle">Browse contract awards and spending data across {len(agencies_sorted)} federal agencies</p>
        </div>

        <div class="agencies-grid">
            {agency_cards_html}
        </div>
    </div>

    <script src="../js/tracker.js"></script>
</body>
</html>"""

    return html


def main():
    parser = argparse.ArgumentParser(
        description="Generate agency intelligence landing pages"
    )
    parser.add_argument(
        "--min-awards",
        type=int,
        default=5,
        help="Minimum number of awards required to generate agency page (default: 5)"
    )
    args = parser.parse_args()

    print("🏛️  Agency Intelligence Pages Generator\n")
    print("=" * 60)

    # Load all awards
    all_awards = load_all_awards()
    if not all_awards:
        return

    # Group by agency
    print("📋 Grouping awards by agency...")
    agency_awards = group_by_agency(all_awards)
    print(f"   Found {len(agency_awards)} unique agencies\n")

    # Create output directory
    output_dir = Path(__file__).parent / "landing" / "agencies"
    output_dir.mkdir(parents=True, exist_ok=True)
    print(f"📁 Output directory: {output_dir}\n")

    # Generate pages for qualifying agencies
    agencies_list = []
    pages_generated = 0

    for agency_name, awards in agency_awards.items():
        if len(awards) < args.min_awards:
            continue

        slug = slugify(agency_name)
        print(f"🔨 Generating page for {agency_name}...")
        print(f"   Slug: {slug}")
        print(f"   Awards: {len(awards):,}")

        # Calculate metrics
        metrics = calculate_agency_metrics(awards)
        print(f"   Total value: {format_currency(metrics['total_value'])}")

        # Generate HTML
        html = generate_agency_page(agency_name, metrics, slug)

        # Write file
        output_file = output_dir / f"{slug}.html"
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(html)

        print(f"   ✅ Saved to {output_file}\n")

        agencies_list.append((
            agency_name,
            slug,
            metrics['total_value'],
            metrics['total_count']
        ))
        pages_generated += 1

    # Generate index page
    if agencies_list:
        print(f"📚 Generating agency directory index...")
        index_html = generate_index_page(agencies_list)
        index_file = output_dir / "index.html"
        with open(index_file, 'w', encoding='utf-8') as f:
            f.write(index_html)
        print(f"   ✅ Saved to {index_file}\n")

    print("=" * 60)
    print(f"✅ Generated {pages_generated} agency pages + 1 index page")
    print(f"📍 Location: {output_dir}")
    print(f"\n💡 Content moat: {pages_generated} agency pages will auto-regenerate weekly")
    print(f"   Combined with contractor pages, you're building 30+ SEO landing pages")


if __name__ == "__main__":
    main()
