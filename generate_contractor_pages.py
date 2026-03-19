#!/usr/bin/env python3
"""
Contractor Lookup Page Generator

Generates public-facing contractor pages for SEO and lead generation.

This is a two-pronged strategy:
1. VALUE ADD: contractors can look up their own federal activity
2. SEO PLAY: people searching "[contractor name] federal contracts" land on our page

Each contractor gets:
- Total awards + breakdown by agency + vertical
- Top 5 recent awards
- Subscribe CTA to track their activity weekly

Usage:
    python3 generate_contractor_pages.py
    python3 generate_contractor_pages.py --limit 50  # Generate more pages
"""

import json
import sys
from pathlib import Path
from datetime import datetime
from collections import defaultdict
from typing import Dict, List, Any
import re


def load_awards() -> List[Dict[str, Any]]:
    """Load all available award data, preferring the cumulative all_awards.json."""
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


def normalize_contractor_name(name: str) -> str:
    """Normalize contractor names for matching."""
    if not name:
        return ""

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


def create_slug(name: str) -> str:
    """Create URL-friendly slug from contractor name."""
    # Normalize first
    normalized = normalize_contractor_name(name)

    # Convert to lowercase, replace spaces and special chars with hyphens
    slug = re.sub(r'[^a-z0-9]+', '-', normalized.lower())
    slug = slug.strip('-')

    return slug


def get_top_contractors(awards: List[Dict], limit: int = 20) -> List[Dict[str, Any]]:
    """Identify top contractors by total award value."""
    contractor_stats = defaultdict(lambda: {
        "name": "",
        "total_value": 0,
        "total_count": 0,
        "awards": []
    })

    for award in awards:
        recipient = award.get("recipient_name", "")
        if not recipient:
            continue

        normalized = normalize_contractor_name(recipient)

        # Use the most common form of the name (longest version)
        if not contractor_stats[normalized]["name"] or len(recipient) > len(contractor_stats[normalized]["name"]):
            contractor_stats[normalized]["name"] = recipient

        contractor_stats[normalized]["total_value"] += award.get("award_amount", 0)
        contractor_stats[normalized]["total_count"] += 1
        contractor_stats[normalized]["awards"].append(award)

    # Sort by total value
    top_contractors = sorted(
        contractor_stats.values(),
        key=lambda x: x["total_value"],
        reverse=True
    )[:limit]

    return top_contractors


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


def calculate_contractor_stats(awards: List[Dict]) -> Dict[str, Any]:
    """Calculate statistics for a contractor."""
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
            verticals = ["Other"]
        for vertical in verticals:
            vertical_stats[vertical]["count"] += 1
            vertical_stats[vertical]["value"] += award.get("award_amount", 0)

    # Sort by value
    agency_stats = sorted(agency_stats.items(), key=lambda x: x[1]["value"], reverse=True)
    vertical_stats = sorted(vertical_stats.items(), key=lambda x: x[1]["value"], reverse=True)

    # Top 5 awards
    top_awards = sorted(awards, key=lambda x: x.get("award_amount", 0), reverse=True)[:5]

    return {
        "agency_stats": agency_stats,
        "vertical_stats": vertical_stats,
        "top_awards": top_awards
    }


def generate_contractor_page(contractor: Dict[str, Any]) -> str:
    """Generate HTML for a contractor's page."""
    name = contractor["name"]
    slug = create_slug(name)
    total_value = contractor["total_value"]
    total_count = contractor["total_count"]

    stats = calculate_contractor_stats(contractor["awards"])

    # Format for display
    value_formatted = format_currency(total_value)

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{name} Federal Contracts | GovCon Weekly Intelligence</title>
    <link rel="icon" href="data:image/svg+xml,<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 32 32'><rect width='32' height='32' rx='4' fill='%23C5A44E'/><text x='50%25' y='55%25' font-size='16' font-weight='800' fill='%230A1628' text-anchor='middle' dominant-baseline='middle'>GC</text></svg>">
    <meta name="description" content="Track {name}'s federal contract activity. {total_count} contracts worth {value_formatted} tracked. See agencies, verticals, and recent awards.">
    <link rel="canonical" href="https://dontlukeback.github.io/govcon-intel/contractors/{slug}.html">
    <meta property="og:title" content="{name} Federal Contracts">
    <meta property="og:description" content="{total_count} contracts worth {value_formatted} tracked. See agencies, verticals, and recent awards.">
    <meta property="og:type" content="article">
    <meta property="og:url" content="https://dontlukeback.github.io/govcon-intel/contractors/{slug}.html">
    <meta name="twitter:card" content="summary_large_image">
    <meta name="twitter:title" content="{name} Federal Contracts">
    <meta name="twitter:description" content="{total_count} contracts worth {value_formatted} tracked">
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
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Roboto', sans-serif;
            line-height: 1.7;
            color: var(--gray-800);
            background: var(--gray-50);
        }}

        /* Navigation */
        nav {{
            background: var(--navy);
            padding: 1rem 2rem;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }}

        nav .container {{
            max-width: 1200px;
            margin: 0 auto;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }}

        nav .logo {{
            font-size: 1.25rem;
            font-weight: 700;
            color: var(--gold);
            text-decoration: none;
        }}

        nav a.home-link {{
            color: var(--gold-light);
            text-decoration: none;
            font-weight: 500;
            transition: color 0.2s;
        }}

        nav a.home-link:hover {{
            color: var(--gold);
        }}

        /* Main Content */
        .container {{
            max-width: 1200px;
            margin: 0 auto;
            padding: 3rem 2rem;
        }}

        .header {{
            margin-bottom: 3rem;
        }}

        h1 {{
            font-size: 2.5rem;
            color: var(--navy);
            margin-bottom: 1rem;
            line-height: 1.2;
        }}

        .meta {{
            color: var(--gray-600);
            font-size: 1rem;
            margin-bottom: 2rem;
        }}

        .stats-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 1.5rem;
            margin: 2rem 0;
        }}

        .stat-card {{
            background: white;
            padding: 1.5rem;
            border-radius: 8px;
            box-shadow: 0 1px 3px rgba(0,0,0,0.1);
        }}

        .stat-value {{
            font-size: 2rem;
            font-weight: 700;
            color: var(--navy);
            margin-bottom: 0.25rem;
        }}

        .stat-label {{
            color: var(--gray-600);
            font-size: 0.9rem;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }}

        /* Content sections */
        .section {{
            background: white;
            padding: 2rem;
            margin: 2rem 0;
            border-radius: 8px;
            box-shadow: 0 1px 3px rgba(0,0,0,0.1);
        }}

        h2 {{
            font-size: 1.75rem;
            color: var(--navy);
            margin-bottom: 1.5rem;
            padding-bottom: 0.75rem;
            border-bottom: 2px solid var(--gray-200);
        }}

        h3 {{
            font-size: 1.25rem;
            color: var(--navy-mid);
            margin: 1.5rem 0 0.75rem 0;
        }}

        .breakdown-list {{
            list-style: none;
            padding: 0;
        }}

        .breakdown-item {{
            padding: 1rem;
            border-bottom: 1px solid var(--gray-200);
            display: flex;
            justify-content: space-between;
            align-items: center;
        }}

        .breakdown-item:last-child {{
            border-bottom: none;
        }}

        .breakdown-name {{
            font-weight: 600;
            color: var(--navy);
        }}

        .breakdown-stats {{
            text-align: right;
            color: var(--gray-600);
        }}

        .breakdown-value {{
            font-weight: 700;
            color: var(--gold);
            font-size: 1.1rem;
        }}

        /* Award cards */
        .award-card {{
            background: var(--gray-50);
            padding: 1.5rem;
            margin: 1rem 0;
            border-radius: 8px;
            border-left: 4px solid var(--gold);
        }}

        .award-header {{
            display: flex;
            justify-content: space-between;
            align-items: start;
            margin-bottom: 0.75rem;
        }}

        .award-value {{
            font-size: 1.5rem;
            font-weight: 700;
            color: var(--gold);
        }}

        .award-agency {{
            font-weight: 600;
            color: var(--navy);
            margin-bottom: 0.5rem;
        }}

        .award-date {{
            color: var(--gray-600);
            font-size: 0.9rem;
        }}

        .award-description {{
            color: var(--gray-800);
            line-height: 1.6;
            margin-top: 0.75rem;
        }}

        /* CTA */
        .cta-section {{
            background: linear-gradient(135deg, var(--navy) 0%, var(--navy-mid) 100%);
            color: white;
            padding: 3rem 2rem;
            margin: 3rem 0;
            border-radius: 12px;
            text-align: center;
        }}

        .cta-section h2 {{
            color: white;
            border: none;
            margin-bottom: 1rem;
        }}

        .cta-section p {{
            font-size: 1.1rem;
            margin-bottom: 2rem;
            opacity: 0.9;
        }}

        .cta-button {{
            display: inline-block;
            background: var(--gold);
            color: var(--navy);
            padding: 1rem 2.5rem;
            border-radius: 8px;
            text-decoration: none;
            font-weight: 700;
            font-size: 1.1rem;
            transition: all 0.2s;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        }}

        .cta-button:hover {{
            background: var(--gold-light);
            transform: translateY(-2px);
            box-shadow: 0 6px 12px rgba(0,0,0,0.15);
        }}

        /* Footer */
        footer {{
            background: var(--navy);
            color: white;
            padding: 2rem;
            text-align: center;
            margin-top: 4rem;
        }}

        footer p {{
            opacity: 0.8;
        }}

        footer a {{
            color: var(--gold);
            text-decoration: none;
        }}

        footer a:hover {{
            color: var(--gold-light);
        }}

        @media (max-width: 768px) {{
            h1 {{
                font-size: 2rem;
            }}

            .stats-grid {{
                grid-template-columns: 1fr;
            }}

            .award-header {{
                flex-direction: column;
            }}
        }}
    </style>
</head>
<body>
    <nav>
        <div class="container">
            <a href="../index.html" class="logo">GovCon Weekly Intelligence</a>
            <a href="../index.html" class="home-link">Home</a>
        </div>
    </nav>

    <div class="container">
        <div class="header">
            <h1>{name}</h1>
            <div class="meta">Federal Contract Activity</div>
        </div>

        <div class="stats-grid">
            <div class="stat-card">
                <div class="stat-value">{total_count}</div>
                <div class="stat-label">Total Contracts</div>
            </div>
            <div class="stat-card">
                <div class="stat-value">{value_formatted}</div>
                <div class="stat-label">Total Value</div>
            </div>
            <div class="stat-card">
                <div class="stat-value">{len(stats['agency_stats'])}</div>
                <div class="stat-label">Agencies</div>
            </div>
            <div class="stat-card">
                <div class="stat-value">{len(stats['vertical_stats'])}</div>
                <div class="stat-label">Verticals</div>
            </div>
        </div>

        <div class="cta-section">
            <h2>Track {name}'s Federal Activity</h2>
            <p>Get weekly updates on new contracts, recompetes, and competitor moves in your inbox.</p>
            <a href="https://govconintelligence.substack.com/subscribe" class="cta-button">Subscribe for Free</a>
        </div>

        <div class="section">
            <h2>Awards by Agency</h2>
            <ul class="breakdown-list">
"""

    # Add agency breakdown (top 10)
    for agency, stats_data in stats["agency_stats"][:10]:
        count = stats_data["count"]
        value = format_currency(stats_data["value"])
        html += f"""                <li class="breakdown-item">
                    <div>
                        <div class="breakdown-name">{agency}</div>
                        <div class="breakdown-stats">{count} contract{'s' if count != 1 else ''}</div>
                    </div>
                    <div class="breakdown-value">{value}</div>
                </li>
"""

    html += """            </ul>
        </div>

        <div class="section">
            <h2>Awards by Vertical</h2>
            <ul class="breakdown-list">
"""

    # Add vertical breakdown (top 10)
    for vertical, stats_data in stats["vertical_stats"][:10]:
        count = stats_data["count"]
        value = format_currency(stats_data["value"])
        html += f"""                <li class="breakdown-item">
                    <div>
                        <div class="breakdown-name">{vertical}</div>
                        <div class="breakdown-stats">{count} contract{'s' if count != 1 else ''}</div>
                    </div>
                    <div class="breakdown-value">{value}</div>
                </li>
"""

    html += """            </ul>
        </div>

        <div class="section">
            <h2>Top 5 Recent Awards</h2>
"""

    # Add top awards
    for award in stats["top_awards"]:
        award_value = format_currency(award.get("award_amount", 0))
        agency = award.get("awarding_agency", "Unknown Agency")
        start_date = award.get("start_date", "Unknown")
        description = award.get("description", "No description available")[:300]

        html += f"""            <div class="award-card">
                <div class="award-header">
                    <div class="award-value">{award_value}</div>
                </div>
                <div class="award-agency">{agency}</div>
                <div class="award-date">Start Date: {start_date}</div>
                <div class="award-description">{description}{'...' if len(award.get('description', '')) > 300 else ''}</div>
            </div>
"""

    html += f"""        </div>

        <div class="cta-section">
            <h2>Want Weekly Updates?</h2>
            <p>Track {name} and 100+ other contractors. Get alerted to new awards, recompetes, and competitive intelligence.</p>
            <a href="https://govconintelligence.substack.com/subscribe" class="cta-button">Subscribe Now</a>
        </div>
    </div>

    <footer>
        <p>&copy; {datetime.now().year} GovCon Weekly Intelligence. <a href="../index.html">Home</a> | <a href="../privacy.html">Privacy</a> | <a href="../terms.html">Terms</a></p>
    </footer>

    <script src="../js/tracker.js"></script>
</body>
</html>
"""

    return html


def generate_index_page(contractors: List[Dict[str, Any]]) -> str:
    """Generate index page listing all contractors."""
    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Federal Contractor Directory | GovCon Weekly Intelligence</title>
    <link rel="icon" href="data:image/svg+xml,<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 32 32'><rect width='32' height='32' rx='4' fill='%23C5A44E'/><text x='50%25' y='55%25' font-size='16' font-weight='800' fill='%230A1628' text-anchor='middle' dominant-baseline='middle'>GC</text></svg>">
    <meta name="description" content="Track federal contract activity for top government contractors. View contracts by agency, vertical, and award value.">
    <link rel="canonical" href="https://dontlukeback.github.io/govcon-intel/contractors/">
    <meta property="og:title" content="Federal Contractor Directory">
    <meta property="og:description" content="Track federal contract activity for top government contractors.">
    <meta property="og:type" content="website">
    <meta property="og:url" content="https://dontlukeback.github.io/govcon-intel/contractors/">
    <meta name="twitter:card" content="summary_large_image">
    <meta name="twitter:title" content="Federal Contractor Directory">
    <meta name="twitter:description" content="Track federal contract activity for top government contractors.">
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
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Roboto', sans-serif;
            line-height: 1.7;
            color: var(--gray-800);
            background: var(--gray-50);
        }}

        nav {{
            background: var(--navy);
            padding: 1rem 2rem;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }}

        nav .container {{
            max-width: 1200px;
            margin: 0 auto;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }}

        nav .logo {{
            font-size: 1.25rem;
            font-weight: 700;
            color: var(--gold);
            text-decoration: none;
        }}

        nav a.home-link {{
            color: var(--gold-light);
            text-decoration: none;
            font-weight: 500;
            transition: color 0.2s;
        }}

        nav a.home-link:hover {{
            color: var(--gold);
        }}

        .container {{
            max-width: 1200px;
            margin: 0 auto;
            padding: 3rem 2rem;
        }}

        h1 {{
            font-size: 2.5rem;
            color: var(--navy);
            margin-bottom: 1rem;
            line-height: 1.2;
        }}

        .intro {{
            font-size: 1.1rem;
            color: var(--gray-600);
            margin-bottom: 3rem;
            line-height: 1.8;
        }}

        .contractor-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(350px, 1fr));
            gap: 1.5rem;
            margin: 2rem 0;
        }}

        .contractor-card {{
            background: white;
            padding: 1.5rem;
            border-radius: 8px;
            box-shadow: 0 1px 3px rgba(0,0,0,0.1);
            transition: all 0.2s;
            text-decoration: none;
            color: inherit;
            display: block;
        }}

        .contractor-card:hover {{
            box-shadow: 0 4px 12px rgba(0,0,0,0.15);
            transform: translateY(-2px);
        }}

        .contractor-name {{
            font-size: 1.25rem;
            font-weight: 700;
            color: var(--navy);
            margin-bottom: 0.75rem;
        }}

        .contractor-stats {{
            display: flex;
            gap: 1.5rem;
            color: var(--gray-600);
            font-size: 0.9rem;
        }}

        .stat {{
            display: flex;
            flex-direction: column;
        }}

        .stat-value {{
            font-weight: 700;
            color: var(--gold);
            font-size: 1.1rem;
        }}

        .stat-label {{
            font-size: 0.85rem;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }}

        .cta-section {{
            background: linear-gradient(135deg, var(--navy) 0%, var(--navy-mid) 100%);
            color: white;
            padding: 3rem 2rem;
            margin: 3rem 0;
            border-radius: 12px;
            text-align: center;
        }}

        .cta-section h2 {{
            color: white;
            margin-bottom: 1rem;
        }}

        .cta-section p {{
            font-size: 1.1rem;
            margin-bottom: 2rem;
            opacity: 0.9;
        }}

        .cta-button {{
            display: inline-block;
            background: var(--gold);
            color: var(--navy);
            padding: 1rem 2.5rem;
            border-radius: 8px;
            text-decoration: none;
            font-weight: 700;
            font-size: 1.1rem;
            transition: all 0.2s;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        }}

        .cta-button:hover {{
            background: var(--gold-light);
            transform: translateY(-2px);
            box-shadow: 0 6px 12px rgba(0,0,0,0.15);
        }}

        footer {{
            background: var(--navy);
            color: white;
            padding: 2rem;
            text-align: center;
            margin-top: 4rem;
        }}

        footer p {{
            opacity: 0.8;
        }}

        footer a {{
            color: var(--gold);
            text-decoration: none;
        }}

        footer a:hover {{
            color: var(--gold-light);
        }}

        @media (max-width: 768px) {{
            .contractor-grid {{
                grid-template-columns: 1fr;
            }}
        }}
    </style>
</head>
<body>
    <nav>
        <div class="container">
            <a href="../index.html" class="logo">GovCon Weekly Intelligence</a>
            <a href="../index.html" class="home-link">Home</a>
        </div>
    </nav>

    <div class="container">
        <h1>Federal Contractor Directory</h1>
        <p class="intro">
            Track federal contract activity for the top government contractors.
            Click any contractor to see their agencies, verticals, and recent awards.
        </p>

        <div class="cta-section">
            <h2>Get Weekly Contractor Intelligence</h2>
            <p>Track new awards, recompetes, and competitor moves. Free to start.</p>
            <a href="https://govconintelligence.substack.com/subscribe" class="cta-button">Subscribe for Free</a>
        </div>

        <div class="contractor-grid">
"""

    for contractor in contractors:
        name = contractor["name"]
        slug = create_slug(name)
        total_value = format_currency(contractor["total_value"])
        total_count = contractor["total_count"]

        html += f"""            <a href="{slug}.html" class="contractor-card">
                <div class="contractor-name">{name}</div>
                <div class="contractor-stats">
                    <div class="stat">
                        <div class="stat-value">{total_count}</div>
                        <div class="stat-label">Contracts</div>
                    </div>
                    <div class="stat">
                        <div class="stat-value">{total_value}</div>
                        <div class="stat-label">Total Value</div>
                    </div>
                </div>
            </a>
"""

    html += f"""        </div>

        <div class="cta-section">
            <h2>Want Deeper Intelligence?</h2>
            <p>Subscribe to get weekly updates on contractor activity, recompetes, and competitive moves.</p>
            <a href="https://govconintelligence.substack.com/subscribe" class="cta-button">Subscribe Now</a>
        </div>
    </div>

    <footer>
        <p>&copy; {datetime.now().year} GovCon Weekly Intelligence. <a href="../index.html">Home</a> | <a href="../privacy.html">Privacy</a> | <a href="../terms.html">Terms</a></p>
    </footer>

    <script src="../js/tracker.js"></script>
</body>
</html>
"""

    return html


def main():
    import argparse

    parser = argparse.ArgumentParser(
        description="Generate public contractor lookup pages for SEO and lead generation",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )

    parser.add_argument(
        "--limit",
        type=int,
        default=20,
        help="Number of contractor pages to generate (default: 20)"
    )

    args = parser.parse_args()

    # Load awards
    awards = load_awards()
    if not awards:
        print("❌ No data available. Run the pipeline first.")
        sys.exit(1)

    # Get top contractors
    print(f"🔍 Identifying top {args.limit} contractors by award value...")
    top_contractors = get_top_contractors(awards, limit=args.limit)

    print(f"✅ Found {len(top_contractors)} contractors\n")

    # Create output directory
    output_dir = Path(__file__).parent / "landing" / "contractors"
    output_dir.mkdir(parents=True, exist_ok=True)

    # Generate individual contractor pages
    print("📝 Generating contractor pages...")
    for contractor in top_contractors:
        name = contractor["name"]
        slug = create_slug(name)

        html = generate_contractor_page(contractor)

        output_path = output_dir / f"{slug}.html"
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(html)

        print(f"   ✓ {name} → {slug}.html")

    # Generate index page
    print("\n📝 Generating contractor directory index...")
    index_html = generate_index_page(top_contractors)
    index_path = output_dir / "index.html"
    with open(index_path, 'w', encoding='utf-8') as f:
        f.write(index_html)

    print(f"   ✓ index.html")

    # Summary
    print(f"\n✅ Generated {len(top_contractors)} contractor pages + index")
    print(f"📂 Output directory: {output_dir}")
    print(f"\n🎯 SEO STRATEGY:")
    print(f"   - {len(top_contractors)} pages targeting '[contractor] federal contracts' searches")
    print(f"   - Each page includes 2x subscribe CTAs")
    print(f"   - Analytics tracking via tracker.js")
    print(f"   - Auto-regenerates weekly with fresh data")
    print(f"\n💰 VALUE PLAY:")
    print(f"   - Contractors can look up their own federal activity")
    print(f"   - Transparent pricing (free tier)")
    print(f"   - Subscribe CTA to track activity weekly")
    print(f"\n🚀 Next steps:")
    print(f"   1. Deploy to Netlify/GitHub Pages")
    print(f"   2. Submit sitemap to Google")
    print(f"   3. Monitor organic traffic to contractor pages")
    print(f"   4. Track conversion rate (page view → subscribe)")


if __name__ == "__main__":
    main()
