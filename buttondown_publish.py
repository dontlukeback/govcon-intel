#!/usr/bin/env python3
"""
Buttondown Newsletter Publisher — Fully Automated

Publishes the weekly GovCon newsletter via Buttondown API.
No browser, no paste, no human touch.

Usage:
    python3 buttondown_publish.py                    # publish today's newsletter
    python3 buttondown_publish.py --draft            # create draft only
    python3 buttondown_publish.py --file output/newsletter-v3-substack.md  # specific file
    python3 buttondown_publish.py --dry-run          # print what would happen
"""

import argparse
import json
import os
import re
import sys
from datetime import datetime
from glob import glob
from urllib.request import Request, urlopen
from urllib.error import HTTPError

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
ENV_FILE = os.path.join(SCRIPT_DIR, ".env")
OUTPUT_DIR = os.path.join(SCRIPT_DIR, "output")
BASE_URL = "https://api.buttondown.com/v1"


def load_api_key():
    """Load API key from .env file."""
    if os.path.exists(ENV_FILE):
        with open(ENV_FILE) as f:
            for line in f:
                if line.startswith("BUTTONDOWN_API_KEY="):
                    return line.strip().split("=", 1)[1]
    key = os.environ.get("BUTTONDOWN_API_KEY")
    if key:
        return key
    print("ERROR: No BUTTONDOWN_API_KEY found in .env or environment", file=sys.stderr)
    sys.exit(1)


def api_call(method, endpoint, api_key, data=None):
    """Make a Buttondown API call."""
    url = f"{BASE_URL}/{endpoint}"
    headers = {
        "Authorization": f"Token {api_key}",
        "Content-Type": "application/json",
    }
    body = json.dumps(data).encode() if data else None
    req = Request(url, data=body, headers=headers, method=method)
    try:
        with urlopen(req) as resp:
            return json.loads(resp.read())
    except HTTPError as e:
        error_body = e.read().decode()
        print(f"API Error: {e.code} {error_body}", file=sys.stderr)
        return None


def find_newsletter_file(specific_file=None):
    """Find the most recent newsletter markdown file."""
    if specific_file:
        if os.path.exists(specific_file):
            return specific_file
        full = os.path.join(SCRIPT_DIR, specific_file)
        if os.path.exists(full):
            return full
        print(f"ERROR: File not found: {specific_file}", file=sys.stderr)
        sys.exit(1)

    today = datetime.now().strftime("%Y-%m-%d")

    # Try in order of preference
    candidates = [
        os.path.join(OUTPUT_DIR, f"newsletter-v3-substack.md"),
        os.path.join(OUTPUT_DIR, f"substack_{today}.md"),
        os.path.join(OUTPUT_DIR, f"newsletter-v2-substack.md"),
        os.path.join(OUTPUT_DIR, f"substack-post-1.md"),
    ]

    for c in candidates:
        if os.path.exists(c):
            return c

    # Fall back to most recent substack_*.md
    pattern = os.path.join(OUTPUT_DIR, "substack_*.md")
    files = sorted(glob(pattern), reverse=True)
    if files:
        return files[0]

    print("ERROR: No newsletter file found", file=sys.stderr)
    sys.exit(1)


def generate_metadata(md_content, data_dir=None):
    """Auto-generate subject and description from content and data."""
    today = datetime.now()
    subject = f"GovCon Weekly Intelligence: {today.strftime('%B %d, %Y')}"

    # Try to extract stats from data file
    description = ""
    if data_dir:
        data_pattern = os.path.join(data_dir, "govcon_awards_*.json")
        data_files = sorted(glob(data_pattern), reverse=True)
        if data_files:
            try:
                with open(data_files[0]) as f:
                    awards = json.load(f)
                count = len(awards)
                total = sum(a.get("award_amount", 0) or 0 for a in awards)
                if total >= 1e9:
                    total_str = f"${total/1e9:.1f}B"
                else:
                    total_str = f"${total/1e6:.0f}M"

                # Find top vertical by count
                verticals = {}
                for a in awards:
                    for v in (a.get("verticals") or []):
                        verticals[v] = verticals.get(v, 0) + 1
                top_vertical = max(verticals, key=verticals.get) if verticals else "IT"

                description = f"{count} awards | {total_str} total | {top_vertical} leads"
            except Exception:
                pass

    return subject, description


def publish(api_key, md_file, draft_only=False, dry_run=False):
    """Publish newsletter to Buttondown."""
    with open(md_file) as f:
        body = f.read()

    # Strip H1 title (Buttondown uses subject field)
    lines = body.strip().split("\n")
    if lines[0].startswith("# "):
        lines = lines[1:]
    body_clean = "\n".join(lines).strip()

    # Generate metadata
    data_dir = os.path.join(SCRIPT_DIR, "data")
    subject, description = generate_metadata(body_clean, data_dir)

    if dry_run:
        print(f"DRY RUN:")
        print(f"  Subject: {subject}")
        print(f"  Description: {description}")
        print(f"  Body: {len(body_clean)} chars")
        print(f"  Status: {'draft' if draft_only else 'about_to_send'}")
        print(f"  File: {md_file}")
        return True

    status = "draft" if draft_only else "about_to_send"

    print(f"Publishing to Buttondown...")
    print(f"  Subject: {subject}")
    print(f"  Status: {status}")
    print(f"  Body: {len(body_clean)} chars")

    result = api_call("POST", "emails", api_key, {
        "subject": subject,
        "body": body_clean,
        "status": status,
    })

    if not result:
        print("FAILED: API call returned no result", file=sys.stderr)
        return False

    email_id = result.get("id", "?")
    final_status = result.get("status", "?")
    url = result.get("absolute_url", "?")

    print(f"  ID: {email_id}")
    print(f"  Status: {final_status}")
    print(f"  URL: {url}")

    if final_status in ("sent", "about_to_send"):
        print(f"SUCCESS: Newsletter published!")
    elif final_status == "draft":
        print(f"Draft saved. Review at Buttondown dashboard.")
    else:
        print(f"WARNING: Unexpected status: {final_status}")

    return True


def main():
    parser = argparse.ArgumentParser(description="Publish to Buttondown")
    parser.add_argument("--file", help="Specific markdown file to publish")
    parser.add_argument("--draft", action="store_true", help="Create draft only")
    parser.add_argument("--dry-run", action="store_true", help="Print what would happen")
    args = parser.parse_args()

    api_key = load_api_key()
    md_file = find_newsletter_file(args.file)

    print(f"Newsletter file: {md_file}")
    success = publish(api_key, md_file, args.draft, args.dry_run)
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
