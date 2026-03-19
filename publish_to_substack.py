#!/usr/bin/env python3
"""
Publish a newsletter post to Substack programmatically.

Usage:
    # First time: log in to get cookies
    python3 publish_to_substack.py --login

    # Publish a post
    python3 publish_to_substack.py --title "Title" --subtitle "Subtitle" --file output/substack-post-1.md

    # Publish as draft only (review before sending)
    python3 publish_to_substack.py --title "Title" --file output/substack-post-1.md --draft
"""

import argparse
import json
import os
import sys
import re

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
ENV_FILE = os.path.join(SCRIPT_DIR, ".env")
PUBLICATION_URL = "https://govconintelligence.substack.com"


def check_dependencies():
    try:
        from substack import Api
        from substack.post import Post
        return True
    except ImportError:
        print("Missing dependency. Install with: pip3 install python-substack")
        return False


def login(email):
    """Authenticate with Substack using magic link."""
    from substack import Api

    print(f"Logging in as {email}...")
    print("Substack will send a magic link/code to your email.")
    print()

    api = Api(
        email=email,
        password=None,
        publication_url=PUBLICATION_URL,
    )

    # The library may handle magic link auth — try it
    try:
        user_id = api.get_user_id()
        print(f"Logged in successfully. User ID: {user_id}")
        return api
    except Exception as e:
        print(f"Auto-login failed: {e}")
        print()
        print("Alternative: Log in via browser, then copy your cookies.")
        print("1. Open https://govconintelligence.substack.com in your browser")
        print("2. Log in normally")
        print("3. Open Developer Tools → Application → Cookies")
        print("4. Copy the 'substack.sid' cookie value")
        print("5. Run: python3 publish_to_substack.py --cookie YOUR_COOKIE_VALUE")
        return None


def md_to_substack_blocks(md_text):
    """Convert markdown to Substack post content blocks."""
    blocks = []
    lines = md_text.strip().split("\n")
    i = 0
    current_paragraph = []

    def flush_paragraph():
        if current_paragraph:
            text = " ".join(current_paragraph).strip()
            if text:
                # Convert bold markdown
                text = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', text)
                # Convert italic markdown
                text = re.sub(r'\*(.+?)\*', r'<em>\1</em>', text)
                blocks.append({"type": "paragraph", "content": text})
            current_paragraph.clear()

    while i < len(lines):
        line = lines[i].strip()

        # Skip empty lines (flush paragraph)
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
            blocks.append({"type": "horizontal_rule"})
            i += 1
            continue

        # Bullet list item
        if line.startswith("- ") or line.startswith("* "):
            flush_paragraph()
            text = line[2:]
            text = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', text)
            blocks.append({"type": "bullet_list_item", "content": text})
            i += 1
            continue

        # Numbered list item
        if re.match(r'^\d+\.\s', line):
            flush_paragraph()
            text = re.sub(r'^\d+\.\s', '', line)
            text = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', text)
            blocks.append({"type": "ordered_list_item", "content": text})
            i += 1
            continue

        # Blockquote
        if line.startswith("> "):
            flush_paragraph()
            blocks.append({"type": "blockquote", "content": line[2:]})
            i += 1
            continue

        # Table (skip — Substack doesn't support tables well, convert to text)
        if line.startswith("|"):
            flush_paragraph()
            # Collect table lines
            table_lines = []
            while i < len(lines) and lines[i].strip().startswith("|"):
                table_lines.append(lines[i].strip())
                i += 1
            # Convert table to readable text
            for tl in table_lines:
                if not re.match(r'^\|[\s\-|]+\|$', tl):  # Skip separator rows
                    cells = [c.strip() for c in tl.split("|")[1:-1]]
                    blocks.append({"type": "paragraph", "content": " | ".join(cells)})
            continue

        # Regular paragraph line
        current_paragraph.append(line)
        i += 1

    flush_paragraph()
    return blocks


def publish(api, title, subtitle, md_file, draft_only=False):
    """Publish a markdown file as a Substack post."""
    from substack.post import Post

    # Read markdown
    with open(md_file) as f:
        md_text = f.read()

    # Get user ID
    user_id = api.get_user_id()
    print(f"User ID: {user_id}")

    # Create post
    post = Post(
        title=title,
        subtitle=subtitle or "",
        user_id=user_id,
        audience="everyone",
        write_comment_permissions="everyone",
    )

    # Convert markdown to blocks and add to post
    blocks = md_to_substack_blocks(md_text)
    for block in blocks:
        if block["type"] == "paragraph":
            post.add({"type": "paragraph", "content": block["content"]})
        elif block["type"] == "heading":
            post.add({"type": "heading", "content": block["content"], "level": block.get("level", 2)})
        elif block["type"] == "horizontal_rule":
            post.add({"type": "horizontal_rule"})
        elif block["type"] in ("bullet_list_item", "ordered_list_item"):
            post.add({"type": "paragraph", "content": f"• {block['content']}"})
        elif block["type"] == "blockquote":
            post.add({"type": "paragraph", "content": f"> {block['content']}"})

    # Create draft
    print(f"Creating draft: '{title}'...")
    draft = api.post_draft(post.get_draft())
    draft_id = draft.get("id")
    print(f"Draft created: ID {draft_id}")

    if draft_only:
        print(f"Draft saved. Review it at: {PUBLICATION_URL}/publish/post/{draft_id}")
        print("Publish manually from the Substack dashboard when ready.")
        return draft_id

    # Publish
    print("Publishing...")
    api.prepublish_draft(draft_id)
    api.publish_draft(draft_id)
    print(f"Published! View at: {PUBLICATION_URL}")
    return draft_id


def main():
    parser = argparse.ArgumentParser(description="Publish to Substack")
    parser.add_argument("--login", action="store_true", help="Log in to Substack")
    parser.add_argument("--email", default="lukebaek@gmail.com")
    parser.add_argument("--cookie", help="Substack session cookie (substack.sid)")
    parser.add_argument("--title", help="Post title")
    parser.add_argument("--subtitle", help="Post subtitle")
    parser.add_argument("--file", help="Markdown file to publish")
    parser.add_argument("--draft", action="store_true", help="Create draft only, don't publish")
    args = parser.parse_args()

    if not check_dependencies():
        sys.exit(1)

    from substack import Api

    if args.login:
        login(args.email)
        return

    if not args.title or not args.file:
        parser.error("--title and --file are required for publishing")

    if not os.path.exists(args.file):
        print(f"File not found: {args.file}")
        sys.exit(1)

    # Authenticate
    try:
        if args.cookie:
            # Cookie-based auth
            api = Api(
                email=args.email,
                password=None,
                publication_url=PUBLICATION_URL,
            )
            api.session.cookies.set("substack.sid", args.cookie)
        else:
            api = Api(
                email=args.email,
                password=None,
                publication_url=PUBLICATION_URL,
            )
    except Exception as e:
        print(f"Auth failed: {e}")
        print("Try: python3 publish_to_substack.py --login")
        sys.exit(1)

    publish(api, args.title, args.subtitle, args.file, args.draft)


if __name__ == "__main__":
    main()
