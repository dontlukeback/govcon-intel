#!/usr/bin/env python3
"""
Generate RSS feed (landing/feed.xml) and blog index (landing/blog/index.html)
by scanning landing/blog/ for HTML posts.

Usage: python3 generate_rss.py
"""

import os
import re
from datetime import datetime
from pathlib import Path

# ── Config ──────────────────────────────────────────────────────────────────
SITE_URL = "https://dontlukeback.github.io/govcon-intel"
CHANNEL_TITLE = "GovCon Weekly Intelligence"
CHANNEL_DESCRIPTION = (
    "Weekly federal contract intelligence — recompetes, competitor tracking, "
    "strategic analysis"
)
BUTTONDOWN_URL = "https://buttondown.com/govcon/archive/"
BLOG_DIR = Path(__file__).parent / "landing" / "blog"
FEED_PATH = Path(__file__).parent / "landing" / "feed.xml"
INDEX_PATH = BLOG_DIR / "index.html"


def extract_meta(html_path: Path) -> dict | None:
    """Pull title, description, date, and slug from a blog post HTML file."""
    text = html_path.read_text(encoding="utf-8")

    title_m = re.search(r"<title>([^<]+)</title>", text)
    desc_m = re.search(r'<meta\s+name="description"\s+content="([^"]+)"', text)
    date_m = re.search(r"Published\s+([\w\s,]+?)(?:\s*\||<)", text)

    if not title_m:
        return None

    title = title_m.group(1).strip()
    # Strip trailing " | GovCon Weekly Intelligence" if present
    title = re.sub(r"\s*\|\s*GovCon Weekly Intelligence$", "", title)
    description = desc_m.group(1).strip() if desc_m else ""

    pub_date = None
    if date_m:
        raw = date_m.group(1).strip()
        for fmt in ("%B %d, %Y", "%b %d, %Y", "%Y-%m-%d"):
            try:
                pub_date = datetime.strptime(raw, fmt)
                break
            except ValueError:
                continue
    if pub_date is None:
        pub_date = datetime.fromtimestamp(html_path.stat().st_mtime)

    return {
        "title": title,
        "description": description,
        "date": pub_date,
        "slug": html_path.name,
        "url": f"{SITE_URL}/blog/{html_path.name}",
    }


def discover_posts() -> list[dict]:
    """Scan BLOG_DIR for HTML files (excluding index.html) and return metadata."""
    posts = []
    for f in sorted(BLOG_DIR.glob("*.html")):
        if f.name == "index.html":
            continue
        meta = extract_meta(f)
        if meta:
            posts.append(meta)
    # Newest first
    posts.sort(key=lambda p: p["date"], reverse=True)
    return posts


def rfc822(dt: datetime) -> str:
    return dt.strftime("%a, %d %b %Y 00:00:00 +0000")


def xml_escape(s: str) -> str:
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;").replace('"', "&quot;")


# ── RSS Generation ──────────────────────────────────────────────────────────
def generate_rss(posts: list[dict]) -> str:
    items = []
    for p in posts:
        items.append(f"""    <item>
      <title>{xml_escape(p["title"])}</title>
      <link>{p["url"]}</link>
      <guid>{p["url"]}</guid>
      <description>{xml_escape(p["description"])}</description>
      <pubDate>{rfc822(p["date"])}</pubDate>
    </item>""")

    # Add latest Buttondown newsletter archive as an item
    items.append(f"""    <item>
      <title>Newsletter Archive — GovCon Weekly Intelligence</title>
      <link>{BUTTONDOWN_URL}</link>
      <guid>{BUTTONDOWN_URL}</guid>
      <description>Browse past issues of GovCon Weekly Intelligence on Buttondown.</description>
      <pubDate>{rfc822(datetime.now())}</pubDate>
    </item>""")

    return f"""<?xml version="1.0" encoding="UTF-8"?>
<rss version="2.0" xmlns:atom="http://www.w3.org/2005/Atom">
  <channel>
    <title>{xml_escape(CHANNEL_TITLE)}</title>
    <link>{SITE_URL}/</link>
    <description>{xml_escape(CHANNEL_DESCRIPTION)}</description>
    <language>en-us</language>
    <lastBuildDate>{rfc822(datetime.now())}</lastBuildDate>
    <atom:link href="{SITE_URL}/feed.xml" rel="self" type="application/rss+xml"/>
{chr(10).join(items)}
  </channel>
</rss>
"""


# ── Blog Index Generation ──────────────────────────────────────────────────
def generate_blog_index(posts: list[dict]) -> str:
    post_cards = []
    for p in posts:
        date_str = p["date"].strftime("%B %d, %Y")
        post_cards.append(f"""            <a href="{p["slug"]}" class="post-card">
                <div class="post-date">{date_str}</div>
                <h2 class="post-title">{p["title"]}</h2>
                <p class="post-desc">{p["description"]}</p>
                <span class="read-more">Read article &rarr;</span>
            </a>""")

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Blog | GovCon Weekly Intelligence</title>
    <meta name="description" content="Federal contract intelligence articles — recompetes, competitor analysis, small business strategies, and weekly award breakdowns.">
    <link rel="canonical" href="{SITE_URL}/blog/">
    <link rel="alternate" type="application/rss+xml" title="{CHANNEL_TITLE}" href="{SITE_URL}/feed.xml">
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

        * {{ margin: 0; padding: 0; box-sizing: border-box; }}

        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: var(--navy);
            color: var(--gray-100);
            line-height: 1.6;
        }}

        /* ── Nav ─────────────────────────────────────── */
        nav {{
            background: var(--navy-mid);
            border-bottom: 1px solid rgba(197, 164, 78, 0.2);
            padding: 1rem 0;
        }}
        nav .container {{
            max-width: 900px;
            margin: 0 auto;
            padding: 0 1.5rem;
            display: flex;
            align-items: center;
            justify-content: space-between;
            flex-wrap: wrap;
            gap: 0.75rem;
        }}
        nav .logo {{
            color: var(--gold);
            font-weight: 700;
            font-size: 1.1rem;
            text-decoration: none;
        }}
        nav .nav-links {{
            display: flex;
            gap: 1.5rem;
            flex-wrap: wrap;
        }}
        nav .nav-links a {{
            color: var(--gray-200);
            text-decoration: none;
            font-size: 0.95rem;
            transition: color 0.2s;
        }}
        nav .nav-links a:hover {{ color: var(--gold); }}

        /* ── Page ────────────────────────────────────── */
        .page-header {{
            max-width: 900px;
            margin: 3rem auto 2rem;
            padding: 0 1.5rem;
        }}
        .page-header h1 {{
            font-size: 2rem;
            color: var(--gold);
            margin-bottom: 0.5rem;
        }}
        .page-header p {{
            color: var(--gray-200);
            font-size: 1.05rem;
        }}

        /* ── Post Cards ──────────────────────────────── */
        .posts {{
            max-width: 900px;
            margin: 0 auto 3rem;
            padding: 0 1.5rem;
            display: flex;
            flex-direction: column;
            gap: 1.25rem;
        }}
        .post-card {{
            display: block;
            background: var(--navy-mid);
            border: 1px solid rgba(197, 164, 78, 0.15);
            border-radius: 8px;
            padding: 1.5rem 1.75rem;
            text-decoration: none;
            transition: border-color 0.2s, transform 0.15s;
        }}
        .post-card:hover {{
            border-color: var(--gold);
            transform: translateY(-2px);
        }}
        .post-date {{
            color: var(--gold-light);
            font-size: 0.85rem;
            margin-bottom: 0.4rem;
        }}
        .post-title {{
            color: var(--gray-50);
            font-size: 1.25rem;
            margin-bottom: 0.5rem;
            line-height: 1.35;
        }}
        .post-desc {{
            color: var(--gray-200);
            font-size: 0.95rem;
            line-height: 1.55;
            margin-bottom: 0.75rem;
        }}
        .read-more {{
            color: var(--gold);
            font-size: 0.9rem;
            font-weight: 600;
        }}

        /* ── Subscribe CTA ───────────────────────────── */
        .subscribe {{
            max-width: 900px;
            margin: 0 auto 4rem;
            padding: 2.5rem 1.75rem;
            background: var(--navy-mid);
            border: 1px solid var(--gold);
            border-radius: 10px;
            text-align: center;
        }}
        .subscribe h2 {{
            color: var(--gold);
            font-size: 1.4rem;
            margin-bottom: 0.5rem;
        }}
        .subscribe p {{
            color: var(--gray-200);
            margin-bottom: 1.25rem;
            font-size: 1rem;
        }}
        .subscribe .btn {{
            display: inline-block;
            background: var(--gold);
            color: var(--navy);
            font-weight: 700;
            padding: 0.75rem 2rem;
            border-radius: 6px;
            text-decoration: none;
            font-size: 1rem;
            transition: background 0.2s;
        }}
        .subscribe .btn:hover {{ background: var(--gold-light); }}

        /* ── Footer ──────────────────────────────────── */
        footer {{
            text-align: center;
            padding: 2rem 1rem;
            color: var(--gray-600);
            font-size: 0.85rem;
            border-top: 1px solid rgba(197, 164, 78, 0.1);
        }}
        footer a {{ color: var(--gold); text-decoration: none; }}
    </style>
</head>
<body>
    <nav>
        <div class="container">
            <a href="../index.html" class="logo">GovCon Weekly Intelligence</a>
            <div class="nav-links">
                <a href="../index.html">Home</a>
                <a href="../contractors/index.html">Contractors</a>
                <a href="../agencies/index.html">Agencies</a>
                <a href="https://buttondown.com/govcon" target="_blank">Subscribe</a>
            </div>
        </div>
    </nav>

    <div class="page-header">
        <h1>Blog</h1>
        <p>Federal contract intelligence articles, weekly award breakdowns, and strategy guides.</p>
    </div>

    <div class="posts">
{chr(10).join(post_cards)}
    </div>

    <div class="subscribe">
        <h2>Get weekly federal contract intelligence</h2>
        <p>Recompetes, new awards, competitor moves — delivered every Monday.</p>
        <a href="https://buttondown.com/govcon" target="_blank" class="btn">Subscribe Free</a>
    </div>

    <footer>
        &copy; 2026 GovCon Weekly Intelligence &middot;
        <a href="../feed.xml">RSS Feed</a>
    </footer>
</body>
</html>
"""


# ── Main ────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    posts = discover_posts()
    print(f"Found {len(posts)} blog posts:")
    for p in posts:
        print(f"  - {p['date'].strftime('%Y-%m-%d')} | {p['title']}")

    # Write RSS
    FEED_PATH.parent.mkdir(parents=True, exist_ok=True)
    FEED_PATH.write_text(generate_rss(posts), encoding="utf-8")
    print(f"\nRSS feed written to {FEED_PATH}")

    # Write blog index
    INDEX_PATH.write_text(generate_blog_index(posts), encoding="utf-8")
    print(f"Blog index written to {INDEX_PATH}")
