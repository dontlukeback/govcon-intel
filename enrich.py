#!/usr/bin/env python3
"""
GovCon Intelligence — AI Enrichment Pipeline

Transforms raw award data from pipeline.py into the rich editorial JSON
that generate_newsletter.py and generate_substack.py consume.

Usage:
    python3 enrich.py                          # Use latest govcon_awards_*.json
    python3 enrich.py --input data/govcon_awards_2026-03-18.json
    python3 enrich.py --dry-run                # Print prompt, don't call API

Requires:
    AWS credentials configured (uses Bedrock via boto3)

Output:
    data/enriched_YYYY-MM-DD.json  (the newsletter-ready data model)
"""

import argparse
import glob
import json
import os
import sys
from datetime import datetime, timedelta

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")
MODEL_ID = "us.anthropic.claude-sonnet-4-20250514-v1:0"
MAX_TOKENS = 16000
AWS_REGION = "us-west-2"

# How many top awards to send to Claude (by dollar amount)
TOP_N_AWARDS = 40

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def find_latest_awards():
    """Find the most recent govcon_awards_*.json file."""
    pattern = os.path.join(DATA_DIR, "govcon_awards_*.json")
    files = sorted(glob.glob(pattern))
    if not files:
        print("ERROR: No govcon_awards_*.json found in data/", file=sys.stderr)
        print("Run pipeline.py first.", file=sys.stderr)
        sys.exit(1)
    return files[-1]


def load_awards(path):
    """Load and return the raw awards JSON."""
    with open(path) as f:
        awards = json.load(f)
    print(f"Loaded {len(awards)} awards from {os.path.basename(path)}", file=sys.stderr)
    return awards


def summarize_awards(awards):
    """Create a compact summary of awards for the prompt."""
    sorted_awards = sorted(awards, key=lambda a: a.get("award_amount") or 0, reverse=True)
    top = sorted_awards[:TOP_N_AWARDS]

    total_value = sum(a.get("award_amount") or 0 for a in awards)
    agencies = {}
    verticals = {}
    vehicles = {}
    set_asides = {}

    for a in awards:
        ag = a.get("awarding_agency") or "Unknown"
        agencies[ag] = agencies.get(ag, 0) + (a.get("award_amount") or 0)

        for v in a.get("verticals", []):
            verticals[v] = verticals.get(v, 0) + 1

        veh = a.get("vehicle")
        if veh:
            vehicles[veh] = vehicles.get(veh, 0) + 1

        sa = a.get("set_aside")
        if sa:
            set_asides[sa] = set_asides.get(sa, 0) + 1

    top_agencies = sorted(agencies.items(), key=lambda x: x[1], reverse=True)[:10]

    summary = {
        "total_awards": len(awards),
        "total_value": total_value,
        "date_range": {
            "earliest": min((a.get("start_date") or "9999") for a in awards),
            "latest": max((a.get("start_date") or "0000") for a in awards),
        },
        "top_agencies": [{"agency": ag, "total_spend": val} for ag, val in top_agencies],
        "verticals": dict(sorted(verticals.items(), key=lambda x: x[1], reverse=True)),
        "vehicles_detected": vehicles,
        "set_asides_detected": set_asides,
        "top_awards": [],
    }

    for a in top:
        summary["top_awards"].append({
            "award_id": a.get("award_id"),
            "description": (a.get("description") or "")[:300],
            "award_amount": a.get("award_amount"),
            "awarding_agency": a.get("awarding_agency"),
            "recipient_name": a.get("recipient_name"),
            "start_date": a.get("start_date"),
            "end_date": a.get("end_date"),
            "verticals": a.get("verticals", []),
            "vehicle": a.get("vehicle"),
            "set_aside": a.get("set_aside"),
            "naics_code": a.get("naics_code"),
        })

    return summary


def build_prompt(summary, report_date):
    """Build the system + user prompt for Claude."""
    week_start = datetime.strptime(report_date, "%Y-%m-%d")
    week_end = week_start + timedelta(days=6)
    week_label = f"Week of {week_start.strftime('%B %d')}-{week_end.strftime('%d, %Y')}"

    system_prompt = """You are a senior government contracting intelligence analyst writing for
small-to-mid-tier federal contractors ($5M-$500M revenue). Your readers are BD directors,
capture managers, and company owners who make bid/no-bid decisions weekly.

Your writing style:
- Morning Brew meets Jane's Defence Weekly: authoritative but accessible
- Bold, opinionated editorial voice. Say "don't bid this" or "drop everything and respond"
- Every section must answer "so what should I DO about this?"
- Use specific dollar amounts, dates, agency names, contract numbers
- Reference real government contracting concepts: CPARS, FAR, GAO protests, set-asides,
  NAICS codes, contract vehicles (OASIS, STARS, CIO-SP4, etc.)
- Use double dashes (--) for em dashes, not unicode

CRITICAL: Generate realistic, plausible content grounded in the actual award data provided.
For sections that require information beyond the raw data (DOGE tracker, protests, calendar),
synthesize based on current federal contracting trends and public knowledge.
Mark any speculative items clearly.

Output ONLY valid JSON matching the exact schema specified. No markdown, no commentary."""

    user_prompt = f"""Generate this week's GovCon Weekly Intelligence newsletter data.

**Report date:** {report_date}
**Week label:** {week_label}

**Raw award data summary:**
{json.dumps(summary, indent=2, default=str)}

Generate a complete JSON object with this EXACT structure. Every field must be populated:

{{
  "report_date": "{report_date}",
  "report_title": "GovCon Weekly Intelligence",
  "report_subtitle": "{week_label}",

  "notable": {{
    "headline": "<Bold headline about the biggest trend this week>",
    "summary": "<2-3 sentence editorial lede with specific numbers>",
    "key_stat": "<Single number, e.g. '$2.1B'>",
    "key_stat_label": "<What the stat measures>"
  }},

  "doge_tracker": {{
    "headline": "<1-sentence summary of DOGE/efficiency impact on contracting>",
    "agencies_affected": [
      {{
        "agency": "<Agency name>",
        "action": "<What DOGE/admin is doing>",
        "impact": "<Specific contract/dollar impact>",
        "status": "<Current status + what contractors should do>"
      }}
    ],
    "court_rulings": [
      {{
        "case": "<Case name>",
        "ruling": "<What happened>",
        "practical_impact": "<What it means for contractors>"
      }}
    ],
    "contractor_impact": [
      {{
        "contractor": "<Company name>",
        "exposure": "<Dollar amount at risk>",
        "status": "<Current situation>",
        "signal": "<What BD teams should do>"
      }}
    ],
    "outlook": "<2-3 sentence forward-looking analysis>"
  }},

  "sections": {{
    "recompete_alerts": {{
      "title": "Recompete Alerts",
      "subtitle": "Contracts expiring within 180 days",
      "items": [
        {{
          "contract_name": "<Name>",
          "agency": "<Agency>",
          "incumbent": "<Company>",
          "current_value": "<Formatted, e.g. $487,000,000>",
          "current_value_raw": <number>,
          "expiration_date": "<YYYY-MM-DD>",
          "days_remaining": <number>,
          "naics": "<code>",
          "set_aside": "<type or Full & Open>",
          "solicitation_status": "<status>",
          "notable_detail": "<2-3 sentences of insider context>",
          "urgency": "<high/medium/low>",
          "winnability_score": "<high/medium/low>",
          "winnability_factors": ["<factor 1>", "<factor 2>", "<factor 3>"],
          "incumbent_tenure_years": <number>,
          "protest_history": "<brief history>",
          "who_should_pursue": ["<audience 1>", "<audience 2>"],
          "wired_score": <0-100>
        }}
      ]
    }},
    "new_awards": {{
      "title": "New Contract Awards",
      "subtitle": "Awarded this week",
      "items": [
        {{
          "contract_name": "<Name>",
          "agency": "<Agency>",
          "awardee": "<Company>",
          "award_value": "<Formatted>",
          "award_value_raw": <number>,
          "award_date": "<YYYY-MM-DD>",
          "period_of_performance": "<e.g. 5 years>",
          "naics": "<code>",
          "set_aside": "<type>",
          "competitors_known": ["<company>"],
          "notable_detail": "<1-2 sentences>",
          "why_they_won": "<3-5 sentence editorial analysis>",
          "what_losers_should_do": "<Tactical advice for competitors>",
          "market_signal": "<What this award tells us about the market>"
        }}
      ]
    }},
    "option_exercises": {{
      "title": "Option Year Exercises",
      "subtitle": "Incumbents extending",
      "items": [
        {{
          "contract_name": "<Name>",
          "agency": "<Agency>",
          "contractor": "<Company>",
          "option_value": "<Formatted>",
          "option_value_raw": <number>,
          "option_year": "<e.g. Option Year 2 of 4>",
          "base_contract_value": "<Formatted>",
          "notable_detail": "<1-2 sentences>",
          "recompete_signal": "<What this means for future competition>",
          "who_should_watch": ["<audience>"]
        }}
      ]
    }},
    "funding_actions": {{
      "title": "Significant Funding Actions",
      "subtitle": "Budget movements and ceiling increases",
      "items": [
        {{
          "action_type": "<Ceiling Increase/New Task Order/Incremental Funding>",
          "contract_name": "<Name>",
          "agency": "<Agency>",
          "contractor": "<Company>",
          "modification_value": "<Formatted>",
          "modification_value_raw": <number>,
          "new_ceiling": "<Formatted or null>",
          "notable_detail": "<1-2 sentences>",
          "intel_note": "<Editorial analysis -- what BD teams should do>"
        }}
      ]
    }}
  }},

  "market_pulse": {{
    "total_obligations_week": "<Formatted total>",
    "yoy_change": "<e.g. +12.3%>",
    "top_agencies_by_spend": [
      {{
        "agency": "<Name>",
        "amount": "<Formatted>",
        "trend": "<1 sentence trend + editorial>"
      }}
    ],
    "trending_naics": [
      {{
        "code": "<NAICS code>",
        "description": "<NAICS description>",
        "change": "<e.g. +28%>",
        "insight": "<Why and what to do about it>"
      }}
    ]
  }},

  "action_items": [
    {{
      "priority": "<urgent/this_week/this_month>",
      "action": "<Specific action>",
      "context": "<Why and how>",
      "deadline": "<YYYY-MM-DD or null>"
    }}
  ],

  "one_to_watch": {{
    "headline": "<Forward-looking program headline>",
    "agency": "<Agency>",
    "description": "<3-4 sentences about an emerging program>",
    "why_it_matters": "<Why BD teams should care>",
    "estimated_value": "<Dollar range>",
    "timeline": "<Key dates>",
    "what_to_do_now": ["<action 1>", "<action 2>", "<action 3>"]
  }},

  "govcon_health_index": {{
    "current_score": <0-100>,
    "previous_score": <0-100>,
    "change": <signed number>,
    "trend": "<improving/declining/stable>",
    "components": [
      {{
        "name": "<Metric name>",
        "score": <0-100>,
        "weight": "<percentage>",
        "detail": "<1 sentence explanation>"
      }}
    ],
    "interpretation": "<2-3 sentence editorial on market health>"
  }},

  "bridge_watch": {{
    "subtitle": "Bridge contracts signal imminent recompetes",
    "items": [
      {{
        "contract_name": "<Name>",
        "agency": "<Agency>",
        "incumbent": "<Company>",
        "bridge_value": "<Formatted>",
        "bridge_period": "<e.g. 6 months (Apr 1 - Sep 30, 2026)>",
        "predecessor_contract": "<Original contract name>",
        "predecessor_value": "<Formatted>",
        "predecessor_years": <number>,
        "recompete_signal": "<Editorial analysis>",
        "wired_score": <0-100>,
        "naics": "<code>",
        "set_aside": "<type>",
        "what_to_do": "<Tactical advice>"
      }}
    ]
  }},

  "is_it_wired": {{
    "subtitle": "Proprietary analysis of whether upcoming solicitations are pre-determined",
    "methodology_note": "Wired Score (0-100): 0 = wide open, 100 = pre-determined.",
    "items": [
      {{
        "solicitation": "<Name>",
        "agency": "<Agency>",
        "posted_date": "<YYYY-MM-DD>",
        "response_deadline": "<YYYY-MM-DD>",
        "estimated_value": "<Formatted>",
        "wired_score": <0-100>,
        "signals": [
          {{
            "signal": "<Signal name>",
            "finding": "<What we found>",
            "red_flag": <true/false>
          }}
        ],
        "verdict": "<LIKELY WIRED / TOSS-UP / WIDE OPEN + editorial>",
        "exception": "<Any exception or null>"
      }}
    ]
  }},

  "set_aside_spotlight": {{
    "subtitle": "Agencies behind on small business goals",
    "government_wide": {{
      "sb_goal": "<percentage>",
      "sb_actual": "<percentage>",
      "status": "<1 sentence>",
      "fiscal_year": "<e.g. FY26 (through Q2)>"
    }},
    "underperforming_agencies": [
      {{
        "agency": "<Agency>",
        "category": "<HUBZone/WOSB/SDVOSB/8(a)/SDB>",
        "goal": "<percentage>",
        "actual": "<percentage>",
        "gap": "<signed percentage>",
        "dollar_gap": "<Formatted>",
        "grade_last_year": "<A-F>",
        "action": "<What small businesses should do>",
        "contact": "<Office name>"
      }}
    ],
    "upcoming_set_aside_opportunities": [
      {{
        "title": "<Opportunity name>",
        "agency": "<Agency>",
        "set_aside": "<type>",
        "est_value": "<Formatted>",
        "expected_date": "<Month Year>"
      }}
    ]
  }},

  "protest_report": {{
    "subtitle": "GAO protest decisions and competitor strategy insights",
    "week_stats": {{
      "filed": <number>,
      "decided": <number>,
      "sustained": <number>,
      "denied": <number>,
      "dismissed": <number>,
      "sustain_rate": "<percentage>"
    }},
    "notable_decisions": [
      {{
        "case": "<Case name, e.g. Matter of X, B-NNNNNN>",
        "protester": "<Company>",
        "awardee": "<Company>",
        "agency": "<Agency>",
        "contract_value": "<Formatted>",
        "outcome": "<SUSTAINED/DENIED/DISMISSED>",
        "grounds": "<What the protest was about>",
        "what_it_means": "<Impact on the procurement>",
        "lesson": "<Tactical lesson for readers>"
      }}
    ]
  }},

  "calendar": {{
    "subtitle": "Deadlines and events for BD teams",
    "this_week": [
      {{
        "date": "<YYYY-MM-DD>",
        "type": "<Deadline/Event/Webinar/Legal>",
        "title": "<Event name>",
        "detail": "<1 sentence>",
        "urgency": "<high/medium/low>"
      }}
    ],
    "next_two_weeks": [
      {{
        "date": "<YYYY-MM-DD>",
        "type": "<type>",
        "title": "<Event name>",
        "detail": "<1 sentence>",
        "urgency": "<high/medium/low>"
      }}
    ],
    "looking_ahead": [
      {{
        "date": "<YYYY-MM-DD>",
        "type": "<type>",
        "title": "<Event name>",
        "detail": "<1 sentence>"
      }}
    ]
  }}
}}

REQUIREMENTS:
1. Use the actual award data to populate new_awards (pick the 4-5 most interesting/largest)
2. Generate 3-4 recompete alerts (infer from awards nearing end dates or large modifications)
3. Generate 3 option exercises, 3-4 funding actions from the data
4. All other sections (DOGE, protests, calendar, bridge watch, etc.) should be plausible
   and grounded in real federal contracting trends for {report_date}
5. The "Is It Wired?" section needs 3 items with varying scores (one high, one medium, one low)
6. Include 6-8 action items spanning urgent/this_week/this_month priorities
7. Bridge Watch needs 2-3 items
8. Set-Aside Spotlight needs 3 underperforming agencies and 3-4 upcoming opportunities
9. Protest Report needs 2-3 notable decisions
10. Calendar needs 3 this_week, 4-5 next_two_weeks, 3 looking_ahead items
11. EVERY editorial section must end with specific advice: who should bid, who should skip, what to do this week"""

    return system_prompt, user_prompt


def call_bedrock(system_prompt, user_prompt):
    """Call Claude via AWS Bedrock and return the response text."""
    import boto3
    from botocore.config import Config

    config = Config(read_timeout=300, connect_timeout=10, retries={"max_attempts": 2})
    client = boto3.client("bedrock-runtime", region_name=AWS_REGION, config=config)

    body = json.dumps({
        "anthropic_version": "bedrock-2023-05-31",
        "max_tokens": MAX_TOKENS,
        "system": system_prompt,
        "messages": [{"role": "user", "content": user_prompt}],
    })

    print(f"Calling Bedrock model {MODEL_ID}...", file=sys.stderr)
    response = client.invoke_model(
        modelId=MODEL_ID,
        body=body,
        contentType="application/json",
        accept="application/json",
    )

    result = json.loads(response["body"].read())

    # Extract text from content blocks
    text = ""
    for block in result.get("content", []):
        if block.get("type") == "text":
            text += block["text"]

    if not text:
        print("ERROR: Empty response from Bedrock", file=sys.stderr)
        print(f"Full response: {json.dumps(result, indent=2)}", file=sys.stderr)
        sys.exit(1)

    usage = result.get("usage", {})
    print(f"Tokens — input: {usage.get('input_tokens', '?')}, output: {usage.get('output_tokens', '?')}", file=sys.stderr)

    return text


def extract_json(text):
    """Extract JSON from the response, handling possible markdown fencing."""
    text = text.strip()

    # Strip markdown code fences if present
    if text.startswith("```"):
        text = text.split("\n", 1)[1] if "\n" in text else text[3:]
        if text.rstrip().endswith("```"):
            text = text.rstrip()[:-3]

    return json.loads(text)


def validate_enriched(data):
    """Basic validation that critical sections exist."""
    required_keys = [
        "report_date", "notable", "doge_tracker", "sections",
        "market_pulse", "action_items", "one_to_watch",
        "govcon_health_index", "bridge_watch", "is_it_wired",
        "set_aside_spotlight", "protest_report", "calendar",
    ]
    missing = [k for k in required_keys if k not in data]
    if missing:
        print(f"WARNING: Missing top-level keys: {missing}", file=sys.stderr)
        return False

    sections = data.get("sections", {})
    required_sections = ["recompete_alerts", "new_awards", "option_exercises", "funding_actions"]
    missing_sections = [s for s in required_sections if s not in sections]
    if missing_sections:
        print(f"WARNING: Missing sections: {missing_sections}", file=sys.stderr)
        return False

    checks = [
        ("sections.new_awards.items", len(sections.get("new_awards", {}).get("items", []))),
        ("sections.recompete_alerts.items", len(sections.get("recompete_alerts", {}).get("items", []))),
        ("action_items", len(data.get("action_items", []))),
        ("is_it_wired.items", len(data.get("is_it_wired", {}).get("items", []))),
        ("bridge_watch.items", len(data.get("bridge_watch", {}).get("items", []))),
    ]
    for name, count in checks:
        if count == 0:
            print(f"WARNING: {name} is empty", file=sys.stderr)

    return True


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(description="Enrich raw awards with AI editorial analysis")
    parser.add_argument("--input", help="Path to govcon_awards_*.json (default: latest)")
    parser.add_argument("--output", help="Output path (default: data/enriched_YYYY-MM-DD.json)")
    parser.add_argument("--dry-run", action="store_true", help="Print prompt without calling API")
    parser.add_argument("--date", help="Report date YYYY-MM-DD (default: today)")
    args = parser.parse_args()

    # Determine input file
    input_path = args.input or find_latest_awards()
    awards = load_awards(input_path)

    # Determine report date
    report_date = args.date or datetime.now().strftime("%Y-%m-%d")

    # Summarize awards for prompt
    summary = summarize_awards(awards)

    print(f"Report date: {report_date}", file=sys.stderr)
    print(f"Awards: {summary['total_awards']}", file=sys.stderr)
    print(f"Total value: ${summary['total_value']:,.0f}", file=sys.stderr)
    print(f"Top agencies: {', '.join(a['agency'] for a in summary['top_agencies'][:5])}", file=sys.stderr)
    print(f"Sending top {len(summary['top_awards'])} awards to Claude", file=sys.stderr)

    # Build prompt
    system_prompt, user_prompt = build_prompt(summary, report_date)

    if args.dry_run:
        print("\n=== SYSTEM PROMPT ===", file=sys.stderr)
        print(system_prompt, file=sys.stderr)
        print("\n=== USER PROMPT ===", file=sys.stderr)
        print(user_prompt, file=sys.stderr)
        print(f"\n=== Prompt size: ~{len(system_prompt) + len(user_prompt):,} chars ===", file=sys.stderr)
        return

    # Call Bedrock
    response_text = call_bedrock(system_prompt, user_prompt)

    # Parse response
    try:
        enriched = extract_json(response_text)
    except json.JSONDecodeError as e:
        print(f"ERROR: Failed to parse JSON response: {e}", file=sys.stderr)
        debug_path = os.path.join(DATA_DIR, f"enrichment_debug_{report_date}.txt")
        with open(debug_path, "w") as f:
            f.write(response_text)
        print(f"Raw response saved to {debug_path}", file=sys.stderr)
        sys.exit(1)

    # Validate
    validate_enriched(enriched)

    # Determine output path
    output_path = args.output or os.path.join(DATA_DIR, f"enriched_{report_date}.json")
    with open(output_path, "w") as f:
        json.dump(enriched, f, indent=2, default=str)
    print(f"\nEnriched data saved to {output_path}", file=sys.stderr)

    # Also update corrected_all.json (what the generators read)
    canonical_path = os.path.join(DATA_DIR, "corrected_all.json")
    with open(canonical_path, "w") as f:
        json.dump(enriched, f, indent=2, default=str)
    print(f"Updated {canonical_path}", file=sys.stderr)

    # Stats
    n_awards = len(enriched.get("sections", {}).get("new_awards", {}).get("items", []))
    n_recompetes = len(enriched.get("sections", {}).get("recompete_alerts", {}).get("items", []))
    n_actions = len(enriched.get("action_items", []))
    n_wired = len(enriched.get("is_it_wired", {}).get("items", []))
    n_bridge = len(enriched.get("bridge_watch", {}).get("items", []))
    print(f"\nGenerated: {n_awards} awards, {n_recompetes} recompetes, "
          f"{n_actions} action items, {n_wired} wired scores, {n_bridge} bridge contracts",
          file=sys.stderr)


if __name__ == "__main__":
    main()
