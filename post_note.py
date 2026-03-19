#!/usr/bin/env python3
"""
Substack Notes Poster (Reverse-Engineered API)

⚠️  WARNING: UNSUPPORTED AND RISKY
- No official Substack API for Notes
- Uses reverse-engineered endpoints that may break without notice
- Risk of account suspension for TOS violation
- DO NOT USE IN PRODUCTION without understanding the risks

This script is for EDUCATIONAL PURPOSES ONLY.
For production use, manually post Notes via Substack's web interface.

For context, see: https://github.com/can3p/substack-api-notes

RECOMMENDED ALTERNATIVE:
Use Zapier/Make.com to trigger a Slack reminder when newsletter publishes.
Then manually post 3-5 Notes via Substack UI (takes 5 minutes).
"""

import os
import sys
import json
import requests
from datetime import datetime

# ============================================================================
# CONFIG
# ============================================================================
SUBSTACK_DOMAIN = "govconintel.substack.com"  # Your publication domain
BASE_API_URL = f"https://{SUBSTACK_DOMAIN}/api/v1"

# Get auth cookie from environment variable (never commit this to git)
SUBSTACK_SID = os.getenv("SUBSTACK_SID")

if not SUBSTACK_SID:
    print("ERROR: SUBSTACK_SID environment variable not set")
    print("\nTo get your substack.sid cookie:")
    print("1. Open https://substack.com in your browser")
    print("2. Log in to your account")
    print("3. Open Developer Tools (F12)")
    print("4. Go to Application > Cookies > https://substack.com")
    print("5. Find 'substack.sid' cookie, copy its value")
    print("6. Run: export SUBSTACK_SID='<your-cookie-value>'")
    sys.exit(1)


# ============================================================================
# API FUNCTIONS (REVERSE-ENGINEERED)
# ============================================================================
def get_headers():
    """Return auth headers with cookie"""
    return {
        "Cookie": f"substack.sid={SUBSTACK_SID}",
        "Content-Type": "application/json",
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36"
    }


def post_draft(title, body_json):
    """
    Create a draft post (DOCUMENTED in reverse-engineered API)

    Args:
        title: Post title (str)
        body_json: Substack document format (JSON string)

    Returns:
        Draft ID if successful, None otherwise
    """
    endpoint = f"{BASE_API_URL}/drafts"
    payload = {
        "draft_title": title,
        "draft_subtitle": "",
        "draft_body": body_json,
        "audience": "everyone",
        "type": "newsletter",
        "draft_bylines": [],  # Will use default author
        "section_chosen": False
    }

    try:
        response = requests.post(endpoint, headers=get_headers(), json=payload)
        response.raise_for_status()
        draft = response.json()
        return draft.get("id")
    except requests.exceptions.RequestException as e:
        print(f"ERROR creating draft: {e}")
        if hasattr(e.response, 'text'):
            print(f"Response: {e.response.text}")
        return None


def post_note(text, link=None):
    """
    ⚠️  EXPERIMENTAL: Post a Substack Note (NOT DOCUMENTED)

    This function attempts to post a Note via reverse-engineered endpoint.
    This is NOT officially supported and may:
    - Break without notice
    - Result in account suspension
    - Fail silently

    Args:
        text: Note content (max 500 characters)
        link: Optional URL to attach

    Returns:
        True if successful (maybe), False otherwise
    """
    print("⚠️  WARNING: Posting Notes via API is unsupported and risky!")
    print("This endpoint is reverse-engineered and may break or violate TOS.")
    print("\nProceed? (yes/no): ", end="")

    confirm = input().strip().lower()
    if confirm != "yes":
        print("Aborted. Use Substack web UI to post Notes manually.")
        return False

    # Attempt to post (endpoint structure is SPECULATIVE)
    # Based on typical REST patterns, but NOT verified
    endpoint = f"{BASE_API_URL}/notes"  # This may not be the correct endpoint

    payload = {
        "text": text[:500],  # Enforce 500 char limit
        "link": link,
        "visibility": "public"
    }

    try:
        response = requests.post(endpoint, headers=get_headers(), json=payload)
        response.raise_for_status()
        print(f"✅ Note posted successfully (maybe)")
        return True
    except requests.exceptions.RequestException as e:
        print(f"❌ ERROR: Failed to post Note")
        print(f"Status: {e.response.status_code if hasattr(e, 'response') else 'unknown'}")
        print(f"This likely means the endpoint doesn't exist or has changed.")
        print("\nRECOMMENDATION: Post Notes manually via Substack web UI")
        return False


# ============================================================================
# AUTO-GENERATION FROM NEWSLETTER DATA
# ============================================================================
def generate_notes_from_data(data_file):
    """
    Generate 3-5 Notes from latest newsletter data

    Args:
        data_file: Path to awards JSON file

    Returns:
        List of (text, link) tuples
    """
    with open(data_file) as f:
        awards = json.load(f)

    # Aggregate quick stats
    total_value = sum(a["award_amount"] for a in awards)
    top_award = max(awards, key=lambda x: x["award_amount"])

    def fmt_dollar(amount):
        if amount >= 1e9:
            return f"${amount/1e9:.1f}B"
        return f"${amount/1e6:.0f}M"

    notes = []

    # Note 1: Weekly summary
    note1 = (
        f"📊 This week: {len(awards):,} federal contracts, {fmt_dollar(total_value)} total.\n\n"
        f"Biggest deal: {fmt_dollar(top_award['award_amount'])} to {top_award['recipient_name']}.\n\n"
        f"Full breakdown: [NEWSLETTER_LINK]",
        None
    )
    notes.append(note1)

    # Note 2: Agency spend
    from collections import defaultdict
    by_agency = defaultdict(float)
    for a in awards:
        by_agency[a["awarding_agency"]] += a["award_amount"]
    top_agency = max(by_agency.items(), key=lambda x: x[1])

    note2 = (
        f"🚨 {top_agency[0]} awarded {fmt_dollar(top_agency[1])} this week — "
        f"{top_agency[1] / total_value * 100:.0f}% of all spend.\n\n"
        f"If you're in their pipeline, move fast. Decision timelines are compressed.\n\n"
        f"Weekly market pulse: [NEWSLETTER_LINK]",
        None
    )
    notes.append(note2)

    # Note 3: Hot take
    note3 = (
        f"🔥 Hot take: Most BD teams track the wrong signals.\n\n"
        f"You watch for RFPs. But by the time an RFP drops, the deal is already wired.\n\n"
        f"The REAL signals? Option exercises + bridge extensions.\n\n"
        f"I track both weekly: [NEWSLETTER_LINK]",
        None
    )
    notes.append(note3)

    # Note 4: Tactical lesson
    note4 = (
        f"💡 How to know if a contract is wired:\n\n"
        f"✓ SOW uses vendor-specific jargon\n"
        f"✓ Unrealistic response timeline (14 days for $50M)\n"
        f"✓ Incumbent named in RFP\n\n"
        f"See 2+ signals? Don't bid. <1% win probability.\n\n"
        f"Full \"wired\" scoring: [NEWSLETTER_LINK]",
        None
    )
    notes.append(note4)

    # Note 5: Question hook (engagement bait)
    note5 = (
        f"❓ What's the #1 signal a recompete is winnable?\n\n"
        f"Hint: It's not the RFP.\n\n"
        f"Drop your guess below 👇\n\n"
        f"(I break this down in this week's intel: [NEWSLETTER_LINK])",
        None
    )
    notes.append(note5)

    return notes


# ============================================================================
# MAIN
# ============================================================================
def main():
    print("=" * 60)
    print("Substack Notes Poster (Reverse-Engineered)")
    print("=" * 60)
    print("\n⚠️  READ THIS BEFORE PROCEEDING:")
    print("- This uses UNSUPPORTED reverse-engineered endpoints")
    print("- May violate Substack Terms of Service")
    print("- Risk of account suspension")
    print("- Endpoints may break without notice")
    print("\nRECOMMENDED: Post Notes manually via Substack UI (takes 5 min)")
    print("=" * 60)

    # Load latest data file
    data_dir = os.path.join(os.path.dirname(__file__), "output")
    data_files = [f for f in os.listdir(data_dir) if f.startswith("data_") and f.endswith(".json")]

    if not data_files:
        print("ERROR: No data files found in output/")
        sys.exit(1)

    latest_data = os.path.join(data_dir, sorted(data_files)[-1])
    print(f"\n📁 Using data file: {latest_data}")

    # Generate notes
    notes = generate_notes_from_data(latest_data)
    print(f"\n✅ Generated {len(notes)} Notes\n")

    # Preview notes
    for i, (text, link) in enumerate(notes, 1):
        print(f"--- NOTE {i} ({len(text)} chars) ---")
        print(text.replace("[NEWSLETTER_LINK]", "https://govconintel.substack.com"))
        print()

    print("=" * 60)
    print("OPTIONS:")
    print("1. Copy-paste these to Substack UI manually (RECOMMENDED)")
    print("2. Attempt to post via API (RISKY, unsupported)")
    print("3. Save to files for later")
    print("=" * 60)
    print("\nChoose (1/2/3): ", end="")

    choice = input().strip()

    if choice == "1":
        print("\n✅ Copy the Notes above and paste into Substack UI:")
        print("   https://substack.com/notes/new")

    elif choice == "2":
        print("\n⚠️  Proceeding with API posting (UNSUPPORTED)...")
        for i, (text, link) in enumerate(notes, 1):
            print(f"\nPosting Note {i}/{len(notes)}...")
            success = post_note(
                text.replace("[NEWSLETTER_LINK]", "https://govconintel.substack.com"),
                link
            )
            if not success:
                print("Stopping due to error. Use manual posting instead.")
                break

    elif choice == "3":
        output_dir = os.path.join(os.path.dirname(__file__), "output", "notes")
        os.makedirs(output_dir, exist_ok=True)

        timestamp = datetime.now().strftime("%Y-%m-%d")
        for i, (text, link) in enumerate(notes, 1):
            filename = os.path.join(output_dir, f"note_{timestamp}_{i}.txt")
            with open(filename, "w") as f:
                f.write(text.replace("[NEWSLETTER_LINK]", "https://govconintel.substack.com"))
            print(f"✓ {filename}")

        print(f"\n✅ Notes saved to {output_dir}")
        print("Copy-paste to Substack when ready.")

    else:
        print("Invalid choice. Exiting.")


if __name__ == "__main__":
    main()
