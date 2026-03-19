#!/usr/bin/env python3
"""
Update sitemap.xml with all contractor pages.

Run this after generate_contractor_pages.py to keep sitemap fresh.
"""

from pathlib import Path
from datetime import datetime


def main():
    landing_dir = Path(__file__).parent / "landing"
    contractors_dir = landing_dir / "contractors"
    sitemap_path = landing_dir / "sitemap.xml"

    # Base URL
    base_url = "https://dontlukeback.github.io/govcon-intel"
    today = datetime.now().strftime("%Y-%m-%d")

    # Start sitemap
    lines = [
        '<?xml version="1.0" encoding="UTF-8"?>',
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">',
        '  <url>',
        f'    <loc>{base_url}/</loc>',
        f'    <lastmod>{today}</lastmod>',
        '    <changefreq>weekly</changefreq>',
        '    <priority>1.0</priority>',
        '  </url>',
    ]

    # Add static pages
    static_pages = [
        ("terms", "monthly", "0.3"),
        ("privacy", "monthly", "0.3"),
        ("sample.html", "weekly", "0.8"),
        ("insights.html", "weekly", "0.7"),
    ]

    for page, freq, priority in static_pages:
        lines.extend([
            '  <url>',
            f'    <loc>{base_url}/{page}</loc>',
            f'    <lastmod>{today}</lastmod>',
            f'    <changefreq>{freq}</changefreq>',
            f'    <priority>{priority}</priority>',
            '  </url>',
        ])

    # Add blog posts
    blog_dir = landing_dir / "blog"
    if blog_dir.exists():
        blog_posts = sorted([f for f in blog_dir.glob("*.html")])
        for post in blog_posts:
            lines.extend([
                '  <url>',
                f'    <loc>{base_url}/blog/{post.name}</loc>',
                f'    <lastmod>{today}</lastmod>',
                '    <changefreq>monthly</changefreq>',
                '    <priority>0.8</priority>',
                '  </url>',
            ])

    # Add contractor directory index
    lines.extend([
        '  <url>',
        f'    <loc>{base_url}/contractors/</loc>',
        f'    <lastmod>{today}</lastmod>',
        '    <changefreq>weekly</changefreq>',
        '    <priority>0.9</priority>',
        '  </url>',
    ])

    # Add all contractor pages
    if contractors_dir.exists():
        contractor_pages = sorted([
            f for f in contractors_dir.glob("*.html")
            if f.name != "index.html"
        ])

        print(f"📄 Adding {len(contractor_pages)} contractor pages to sitemap...")

        for page in contractor_pages:
            lines.extend([
                '  <url>',
                f'    <loc>{base_url}/contractors/{page.name}</loc>',
                f'    <lastmod>{today}</lastmod>',
                '    <changefreq>weekly</changefreq>',
                '    <priority>0.7</priority>',
                '  </url>',
            ])

    # Close sitemap
    lines.append('</urlset>')

    # Write sitemap
    with open(sitemap_path, 'w', encoding='utf-8') as f:
        f.write('\n'.join(lines) + '\n')

    print(f"✅ Sitemap updated: {sitemap_path}")
    print(f"   Total URLs: {len(contractor_pages) + len(static_pages) + len(blog_posts) + 2}")


if __name__ == "__main__":
    main()
