#!/usr/bin/env python3
"""
auto_publish.py — Autonomous Substack publisher for GovCon Weekly Intelligence.

Reads generated newsletter markdown, extracts metadata from data files,
and publishes to Substack using plain-text + headings (proven to render correctly).

Usage:
    python3 auto_publish.py                    # Publish live
    python3 auto_publish.py --dry-run          # Create draft only (no publish)
    python3 auto_publish.py --file FILE        # Override markdown file
    python3 auto_publish.py --date 2026-03-18  # Override date
"""

import argparse
import json
import os
import re
import sys
from collections import Counter
from datetime import datetime

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
OUTPUT_DIR = os.path.join(SCRIPT_DIR, "output")
DATA_DIR = os.path.join(SCRIPT_DIR, "data")
ENV_FILE = os.path.join(SCRIPT_DIR, ".env")
LOG_FILE = os.path.join(OUTPUT_DIR, "publish.log")
PUBLICATION_URL = "https://govconintelligence.substack.com"


def log(msg, level="INFO"):
    """Append to publish.log and print."""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    line = f"[{timestamp}] [{level}] {msg}"
    print(line)
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    with open(LOG_FILE, "a") as f:
        f.write(line + "\n")


def load_env():
    """Load .env file into dict."""
    env = {}
    if not os.path.exists(ENV_FILE):
        return env
    with open(ENV_FILE) as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                key, val = line.split("=", 1)
                env[key.strip()] = val.strip()
    return env


def generate_title(date_str):
    """Generate title: GovCon Weekly Intelligence: March 18, 2026"""
    dt = datetime.strptime(date_str, "%Y-%m-%d")
    return f"GovCon Weekly Intelligence: {dt.strftime('%B %d, %Y').replace(' 0', ' ')}"


def generate_subtitle(date_str):
    """Generate subtitle from data: [N] awards | $[X]B total | [top vertical]"""
    data_file = os.path.join(DATA_DIR, f"govcon_awards_{date_str}.json")
    if not os.path.exists(data_file):
        log(f"Data file not found: {data_file}, using generic subtitle", "WARN")
        return "Federal contracting intelligence for the week"

    try:
        with open(data_file) as f:
            data = json.load(f)

        n_awards = len(data)
        total = sum(d.get("award_amount", 0) or 0 for d in data)

        # Format total
        if total >= 1e9:
            total_str = f"${total / 1e9:.1f}B"
        elif total >= 1e6:
            total_str = f"${total / 1e6:.0f}M"
        else:
            total_str = f"${total:,.0f}"

        # Top vertical
        verticals = Counter()
        for d in data:
            v = d.get("verticals")
            if v:
                if isinstance(v, list):
                    for x in v:
                        verticals[str(x)] += 1
                else:
                    verticals[str(v)] += 1

        top_vertical = verticals.most_common(1)[0][0] if verticals else "Defense"

        subtitle = f"{n_awards} awards | {total_str} total | {top_vertical} leads"
        return subtitle
    except Exception as e:
        log(f"Subtitle generation failed: {e}", "WARN")
        return "Federal contracting intelligence for the week"


def md_to_plain_text_blocks(md_text):
    """
    Convert markdown to plain-text Substack blocks.

    IMPORTANT: Plain text + headings is the PROVEN approach.
    Post ID 191437190 confirmed this renders correctly.
    Do NOT attempt rich formatting — it shows up empty.
    """
    blocks = []
    lines = md_text.strip().split("\n")
    i = 0
    current_paragraph = []

    def flush_paragraph():
        if current_paragraph:
            text = " ".join(current_paragraph).strip()
            if text:
                # Strip markdown formatting to plain text
                text = re.sub(r"\*\*(.+?)\*\*", r"\1", text)  # bold -> plain
                text = re.sub(r"\*(.+?)\*", r"\1", text)  # italic -> plain
                blocks.append({"type": "paragraph", "content": text})
            current_paragraph.clear()

    while i < len(lines):
        line = lines[i].strip()

        # Empty line — flush
        if not line:
            flush_paragraph()
            i += 1
            continue

        # H1
        if line.startswith("# ") and not line.startswith("## "):
            flush_paragraph()
            blocks.append({"type": "heading", "content": line[2:], "level": 1})
            i += 1
            continue

        # H2
        if line.startswith("## "):
            flush_paragraph()
            blocks.append({"type": "heading", "content": line[3:], "level": 2})
            i += 1
            continue

        # H3
        if line.startswith("### "):
            flush_paragraph()
            blocks.append({"type": "heading", "content": line[4:], "level": 3})
            i += 1
            continue

        # Horizontal rule
        if line in ("---", "***", "___"):
            flush_paragraph()
            blocks.append({"type": "divider"})
            i += 1
            continue

        # Bullet list — convert to plain text with bullet char
        if line.startswith("- ") or line.startswith("* "):
            flush_paragraph()
            text = line[2:]
            text = re.sub(r"\*\*(.+?)\*\*", r"\1", text)
            text = re.sub(r"\*(.+?)\*", r"\1", text)
            blocks.append({"type": "paragraph", "content": f"  - {text}"})
            i += 1
            continue

        # Numbered list
        if re.match(r"^\d+\.\s", line):
            flush_paragraph()
            text = re.sub(r"\*\*(.+?)\*\*", r"\1", line)
            text = re.sub(r"\*(.+?)\*", r"\1", text)
            blocks.append({"type": "paragraph", "content": text})
            i += 1
            continue

        # Blockquote
        if line.startswith("> "):
            flush_paragraph()
            text = line[2:]
            text = re.sub(r"\*\*(.+?)\*\*", r"\1", text)
            blocks.append({"type": "paragraph", "content": text})
            i += 1
            continue

        # Table — convert to readable lines
        if line.startswith("|"):
            flush_paragraph()
            table_lines = []
            while i < len(lines) and lines[i].strip().startswith("|"):
                table_lines.append(lines[i].strip())
                i += 1
            for tl in table_lines:
                if not re.match(r"^\|[\s\-|]+\|$", tl):  # Skip separator
                    cells = [c.strip() for c in tl.split("|")[1:-1]]
                    cells = [re.sub(r"\*\*(.+?)\*\*", r"\1", c) for c in cells]
                    blocks.append({"type": "paragraph", "content": " | ".join(cells)})
            continue

        # Regular text
        current_paragraph.append(line)
        i += 1

    flush_paragraph()
    return blocks


def publish_to_substack(md_file, title, subtitle, cookie, email, dry_run=False):
    """Publish markdown to Substack using plain-text blocks."""
    from substack import Api
    from substack.post import Post

    # Read markdown
    with open(md_file) as f:
        md_text = f.read()

    # Authenticate with cookie
    # python-substack now requires cookies_string param directly
    cookies_str = f"substack.sid={cookie}"
    api = Api(
        cookies_string=cookies_str,
        publication_url=PUBLICATION_URL,
    )

    # Verify auth
    user_id = api.get_user_id()
    log(f"Authenticated as user {user_id}")

    # Create post
    post = Post(
        title=title,
        subtitle=subtitle,
        user_id=user_id,
        audience="everyone",
        write_comment_permissions="everyone",
    )

    # Convert to plain-text blocks
    blocks = md_to_plain_text_blocks(md_text)
    log(f"Converted {len(blocks)} blocks from markdown")

    for block in blocks:
        if block["type"] == "paragraph":
            post.add({"type": "paragraph", "content": block["content"]})
        elif block["type"] == "heading":
            post.add({"type": "heading", "content": block["content"], "level": block.get("level", 2)})
        elif block["type"] == "divider":
            post.add({"type": "horizontal_rule"})

    # Create draft
    log(f"Creating draft: '{title}'")
    draft = api.post_draft(post.get_draft())
    draft_id = draft.get("id")
    log(f"Draft created: ID {draft_id}")
    log(f"Preview: {PUBLICATION_URL}/publish/post/{draft_id}")

    if dry_run:
        log(f"DRY RUN — draft saved, not published. ID: {draft_id}")
        return draft_id, "draft"

    # Publish
    log("Publishing draft...")
    api.prepublish_draft(draft_id)
    api.publish_draft(draft_id)
    log(f"PUBLISHED: {PUBLICATION_URL} — post ID {draft_id}")
    return draft_id, "published"


def main():
    parser = argparse.ArgumentParser(description="Auto-publish GovCon newsletter to Substack")
    parser.add_argument("--dry-run", action="store_true", help="Create draft only, don't publish")
    parser.add_argument("--file", help="Override markdown file path")
    parser.add_argument("--date", help="Override date (YYYY-MM-DD)")
    parser.add_argument("--title", help="Override title")
    parser.add_argument("--subtitle", help="Override subtitle")
    args = parser.parse_args()

    # Determine date
    date_str = args.date or datetime.now().strftime("%Y-%m-%d")

    # Load env
    env = load_env()
    cookie = env.get("SUBSTACK_COOKIE")
    email = env.get("SUBSTACK_EMAIL", "lukebaek@gmail.com")

    if not cookie:
        log("SUBSTACK_COOKIE not found in .env", "ERROR")
        sys.exit(1)

    # Find markdown file
    md_file = args.file
    if not md_file:
        md_file = os.path.join(OUTPUT_DIR, f"substack_{date_str}.md")
    if not os.path.exists(md_file):
        log(f"Newsletter file not found: {md_file}", "ERROR")
        sys.exit(1)

    log(f"Publishing: {md_file}")

    # Generate title and subtitle
    title = args.title or generate_title(date_str)
    subtitle = args.subtitle or generate_subtitle(date_str)
    log(f"Title: {title}")
    log(f"Subtitle: {subtitle}")

    # Check dependency
    try:
        from substack import Api
        from substack.post import Post
    except ImportError:
        log("Missing python-substack. Install: pip3 install python-substack", "ERROR")
        sys.exit(1)

    # Publish
    try:
        draft_id, status = publish_to_substack(
            md_file, title, subtitle, cookie, email, dry_run=args.dry_run
        )
        log(f"SUCCESS — status={status}, draft_id={draft_id}")
        return 0
    except Exception as e:
        log(f"PUBLISH FAILED: {e}", "ERROR")
        import traceback
        log(traceback.format_exc(), "ERROR")
        return 1


if __name__ == "__main__":
    sys.exit(main())
