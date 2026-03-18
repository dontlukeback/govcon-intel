#!/usr/bin/env python3
"""
GovCon Intelligence Newsletter Pipeline
Pulls federal contract awards from USAspending.gov API by vertical keyword groups,
de-duplicates, enriches with contract vehicle / set-aside / NAICS data, and outputs
JSON + CSV to data/ directory.

Usage:
    python3 pipeline.py              # last 7 days (default)
    python3 pipeline.py --days 14    # last 14 days
"""

import argparse
import csv
import json
import os
import re
import subprocess
import sys
from datetime import datetime, timedelta

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

API_BASE = "https://api.usaspending.gov/api/v2"
SEARCH_ENDPOINT = f"{API_BASE}/search/spending_by_award/"
AWARD_DETAIL_ENDPOINT = f"{API_BASE}/awards"

# Award type codes: A=BPA, B=Purchase Order, C=Delivery Order, D=Definitive Contract
AWARD_TYPE_CODES = ["A", "B", "C", "D"]

FIELDS = [
    "Award ID",
    "Description",
    "Award Amount",
    "Awarding Agency",
    "Recipient Name",
    "Start Date",
    "End Date",
    "generated_internal_id",
    "NAICS Code",
]

PAGE_LIMIT = 100  # max per page

VERTICALS = {
    "AI/ML": [
        "artificial intelligence",
        "machine learning",
        "deep learning",
        "neural network",
        "computer vision",
        "natural language processing",
        "NLP",
        "generative AI",
        "large language model",
        "LLM",
    ],
    "Cybersecurity": [
        "cybersecurity",
        "cyber security",
        "information security",
        "infosec",
        "threat detection",
        "incident response",
        "penetration testing",
        "vulnerability assessment",
        "SIEM",
        "SOC",
        "endpoint protection",
    ],
    "Cloud": [
        "cloud computing",
        "cloud migration",
        "cloud infrastructure",
        "AWS",
        "Azure",
        "GovCloud",
        "cloud services",
        "IaaS",
        "PaaS",
        "SaaS",
        "multi-cloud",
    ],
    "Data Analytics": [
        "data analytics",
        "data engineering",
        "data warehouse",
        "business intelligence",
        "data visualization",
        "big data",
        "data lake",
        "data pipeline",
        "data science",
        "predictive analytics",
    ],
    "DevSecOps": [
        "DevSecOps",
        "DevOps",
        "CI/CD",
        "continuous integration",
        "continuous delivery",
        "containerization",
        "Kubernetes",
        "Docker",
        "infrastructure as code",
        "platform engineering",
    ],
    "Zero Trust": [
        "zero trust",
        "zero-trust",
        "ZTA",
        "ZTNA",
        "microsegmentation",
        "least privilege",
        "never trust always verify",
    ],
    "FedRAMP": [
        "FedRAMP",
        "Federal Risk and Authorization",
        "FedRAMP authorized",
        "FedRAMP High",
        "FedRAMP Moderate",
        "cloud authorization",
        "ATO",
        "authority to operate",
    ],
    "Identity Management": [
        "identity management",
        "IAM",
        "identity access management",
        "multi-factor authentication",
        "MFA",
        "single sign-on",
        "SSO",
        "ICAM",
        "PIV",
        "credentialing",
        "privileged access",
    ],
    "Networking/SDWAN": [
        "SD-WAN",
        "SDWAN",
        "software-defined networking",
        "SDN",
        "network modernization",
        "network infrastructure",
        "MPLS",
        "network as a service",
        "NaaS",
        "enterprise networking",
        "WAN optimization",
    ],
}

# Contract vehicle patterns in generated_internal_id or Award ID
VEHICLE_PATTERNS = {
    "GSA OASIS": [r"GS00Q", r"47QR[A-Z]A"],
    "STARS III": [r"47QTCB", r"STARS"],
    "CIO-SP3": [r"75N98", r"CIOSP3"],
    "SEWP": [r"NNG15S", r"SEWP"],
    "BPA": [r"^[A-Z0-9]*BPA", r"_BPA_"],
    "ALLIANT 2": [r"47QTC[A-Z]2"],
    "8(a) STARS II": [r"47QTC[A-Z]18"],
}

# Set-aside keywords (case-insensitive match against description + type_set_aside)
SET_ASIDE_PATTERNS = {
    "8(a)": [r"8\s*\(\s*a\s*\)", r"8a\b"],
    "SDVOSB": [r"SDVOSB", r"service.disabled.veteran"],
    "HUBZone": [r"HUBZone", r"hub.zone"],
    "WOSB": [r"WOSB", r"women.owned\s+small"],
    "Small Business": [r"small\s+business", r"SBA\b", r"small\s+disadvantaged"],
}

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def log(msg):
    """Print to stderr."""
    print(msg, file=sys.stderr)


def curl_post(url, payload, timeout=30, retries=1):
    """POST JSON via curl subprocess. Returns parsed JSON or None."""
    payload_str = json.dumps(payload)
    for attempt in range(1 + retries):
        try:
            result = subprocess.run(
                [
                    "curl", "-s", "--max-time", str(timeout),
                    "-X", "POST",
                    "-H", "Content-Type: application/json",
                    "-d", payload_str,
                    url,
                ],
                capture_output=True, text=True, timeout=timeout + 10,
            )
            if result.returncode != 0:
                if attempt < retries:
                    log(f"  [retry] curl POST failed (rc={result.returncode}), retrying...")
                    continue
                log(f"  [error] curl POST failed: {result.stderr.strip()}")
                return None
            return json.loads(result.stdout)
        except (subprocess.TimeoutExpired, json.JSONDecodeError) as e:
            if attempt < retries:
                log(f"  [retry] {e}, retrying...")
                continue
            log(f"  [error] {e}")
            return None
    return None


def curl_get(url, timeout=20, retries=1):
    """GET via curl subprocess. Returns parsed JSON or None."""
    for attempt in range(1 + retries):
        try:
            result = subprocess.run(
                ["curl", "-s", "--max-time", str(timeout), url],
                capture_output=True, text=True, timeout=timeout + 10,
            )
            if result.returncode != 0:
                if attempt < retries:
                    continue
                log(f"  [error] curl GET failed: {result.stderr.strip()}")
                return None
            return json.loads(result.stdout)
        except (subprocess.TimeoutExpired, json.JSONDecodeError) as e:
            if attempt < retries:
                continue
            log(f"  [error] {e}")
            return None
    return None


def detect_vehicle(award_id, generated_id):
    """Detect contract vehicle from award ID patterns."""
    combined = f"{award_id or ''} {generated_id or ''}"
    for vehicle, patterns in VEHICLE_PATTERNS.items():
        for pat in patterns:
            if re.search(pat, combined, re.IGNORECASE):
                return vehicle
    return None


def detect_set_aside_from_text(text):
    """Detect set-aside type from description text."""
    if not text:
        return None
    matches = []
    for sa_type, patterns in SET_ASIDE_PATTERNS.items():
        for pat in patterns:
            if re.search(pat, text, re.IGNORECASE):
                matches.append(sa_type)
                break
    return "; ".join(matches) if matches else None


def match_verticals(description):
    """Return list of vertical names whose keywords appear in the description."""
    if not description:
        return []
    desc_lower = description.lower()
    matched = []
    for vertical, keywords in VERTICALS.items():
        for kw in keywords:
            if kw.lower() in desc_lower:
                matched.append(vertical)
                break
    return matched


# ---------------------------------------------------------------------------
# Main pipeline
# ---------------------------------------------------------------------------

def pull_awards_for_vertical(vertical_name, keywords, start_date, end_date):
    """Pull all awards matching keywords for a single vertical. Returns list of raw results."""
    log(f"  Pulling: {vertical_name} ({len(keywords)} keywords)...")
    payload = {
        "filters": {
            "keywords": keywords,
            "time_period": [{"start_date": start_date, "end_date": end_date}],
            "award_type_codes": AWARD_TYPE_CODES,
        },
        "fields": FIELDS,
        "limit": PAGE_LIMIT,
        "page": 1,
    }

    all_results = []
    page = 1
    while True:
        payload["page"] = page
        data = curl_post(SEARCH_ENDPOINT, payload)
        if not data or "results" not in data:
            log(f"    [warn] No results on page {page}, stopping.")
            break

        results = data["results"]
        all_results.extend(results)

        meta = data.get("page_metadata", {})
        if not meta.get("hasNext", False):
            break
        page += 1

        # Safety cap
        if page > 50:
            log(f"    [warn] Hit 50-page cap for {vertical_name}, stopping.")
            break

    log(f"    Got {len(all_results)} raw awards for {vertical_name}")
    return all_results


def enrich_award(award, generated_id):
    """Fetch award detail to get NAICS and set-aside info."""
    if not generated_id:
        return {}, None, None
    url = f"{AWARD_DETAIL_ENDPOINT}/{generated_id}/"
    data = curl_get(url, timeout=15)
    if not data:
        return {}, None, None

    latest = data.get("latest_transaction_contract_data") or {}
    naics = latest.get("naics") or data.get("naics") or None
    naics_desc = latest.get("naics_description") or None
    type_set_aside = latest.get("type_set_aside_description") or latest.get("type_set_aside") or None

    return {
        "naics_code": naics,
        "naics_description": naics_desc,
    }, type_set_aside, latest


def main():
    parser = argparse.ArgumentParser(description="GovCon Intel Pipeline")
    parser.add_argument("--days", type=int, default=7, help="Number of days to look back (default: 7)")
    args = parser.parse_args()

    end_date = datetime.now().strftime("%Y-%m-%d")
    start_date = (datetime.now() - timedelta(days=args.days)).strftime("%Y-%m-%d")

    log(f"GovCon Intel Pipeline")
    log(f"Date range: {start_date} to {end_date} ({args.days} days)")
    log(f"Verticals: {len(VERTICALS)}")
    log("")

    # Step 1: Pull awards per vertical
    raw_by_vertical = {}
    for vertical_name, keywords in VERTICALS.items():
        results = pull_awards_for_vertical(vertical_name, keywords, start_date, end_date)
        raw_by_vertical[vertical_name] = results

    # Step 2: De-duplicate by generated_internal_id, keeping all matching verticals as tags
    # Key: generated_internal_id -> merged award record
    awards_map = {}

    for vertical_name, results in raw_by_vertical.items():
        for r in results:
            gid = r.get("generated_internal_id") or r.get("Award ID", "UNKNOWN")
            if gid in awards_map:
                # Add this vertical to existing record
                if vertical_name not in awards_map[gid]["verticals"]:
                    awards_map[gid]["verticals"].append(vertical_name)
            else:
                # Also check description against ALL verticals (cross-tagging)
                desc_verticals = match_verticals(r.get("Description"))
                all_verticals = list(set([vertical_name] + desc_verticals))
                all_verticals.sort()

                awards_map[gid] = {
                    "generated_internal_id": gid,
                    "award_id": r.get("Award ID"),
                    "description": r.get("Description"),
                    "award_amount": r.get("Award Amount"),
                    "awarding_agency": r.get("Awarding Agency"),
                    "recipient_name": r.get("Recipient Name"),
                    "start_date": r.get("Start Date"),
                    "end_date": r.get("End Date"),
                    "verticals": all_verticals,
                    "vehicle": None,
                    "set_aside": None,
                    "naics_code": r.get("NAICS Code"),
                    "naics_description": None,
                }

    log(f"\nDe-duplicated: {len(awards_map)} unique awards from {sum(len(v) for v in raw_by_vertical.values())} raw results")

    # Step 3: Detect contract vehicles from award IDs
    for gid, award in awards_map.items():
        award["vehicle"] = detect_vehicle(award["award_id"], gid)

    vehicle_count = sum(1 for a in awards_map.values() if a["vehicle"])
    log(f"Contract vehicles detected: {vehicle_count}")

    # Step 4: Detect set-aside from description text
    for gid, award in awards_map.items():
        sa = detect_set_aside_from_text(award["description"])
        if sa:
            award["set_aside"] = sa

    sa_count = sum(1 for a in awards_map.values() if a["set_aside"])
    log(f"Set-asides detected from description: {sa_count}")

    # Step 5: Enrich with NAICS from award detail endpoint (for awards missing NAICS)
    # Limit enrichment calls to keep runtime reasonable
    enrich_candidates = [
        gid for gid, a in awards_map.items()
        if not a["naics_code"] and a["generated_internal_id"].startswith("CONT_")
    ]
    log(f"\nEnriching {min(len(enrich_candidates), 50)} awards with NAICS/set-aside from detail API...")

    enriched_count = 0
    for gid in enrich_candidates[:50]:  # cap at 50 to avoid hammering API
        award = awards_map[gid]
        naics_info, api_set_aside, _ = enrich_award(award, gid)
        if naics_info.get("naics_code"):
            award["naics_code"] = naics_info["naics_code"]
            award["naics_description"] = naics_info["naics_description"]
            enriched_count += 1
        if api_set_aside and not award["set_aside"]:
            award["set_aside"] = api_set_aside

    log(f"  NAICS enriched: {enriched_count} awards")

    # Step 6: Prepare final output
    awards_list = sorted(
        awards_map.values(),
        key=lambda a: (a["award_amount"] or 0),
        reverse=True,
    )

    # Convert verticals list to comma-separated string for CSV compatibility
    for a in awards_list:
        a["verticals_str"] = ", ".join(a["verticals"])

    # Step 7: Save outputs
    script_dir = os.path.dirname(os.path.abspath(__file__))
    data_dir = os.path.join(script_dir, "data")
    os.makedirs(data_dir, exist_ok=True)

    datestamp = datetime.now().strftime("%Y-%m-%d")
    json_path = os.path.join(data_dir, f"govcon_awards_{datestamp}.json")
    csv_path = os.path.join(data_dir, f"govcon_awards_{datestamp}.csv")

    # JSON output (keep verticals as list)
    json_records = []
    for a in awards_list:
        rec = {k: v for k, v in a.items() if k != "verticals_str"}
        json_records.append(rec)

    with open(json_path, "w") as f:
        json.dump(json_records, f, indent=2, default=str)
    log(f"\nJSON saved: {json_path}")

    # CSV output
    csv_fields = [
        "award_id", "description", "award_amount", "awarding_agency",
        "recipient_name", "start_date", "end_date", "verticals_str",
        "vehicle", "set_aside", "naics_code", "naics_description",
        "generated_internal_id",
    ]
    with open(csv_path, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=csv_fields, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(awards_list)
    log(f"CSV saved:  {csv_path}")

    # Step 8: Summary stats
    log(f"\n{'='*60}")
    log(f"SUMMARY")
    log(f"{'='*60}")
    log(f"Date range:       {start_date} to {end_date}")
    log(f"Total unique awards: {len(awards_list)}")
    total_value = sum(a["award_amount"] or 0 for a in awards_list)
    log(f"Total value:      ${total_value:,.2f}")
    log(f"")
    log(f"By vertical:")
    vert_counts = {}
    vert_values = {}
    for a in awards_list:
        for v in a["verticals"]:
            vert_counts[v] = vert_counts.get(v, 0) + 1
            vert_values[v] = vert_values.get(v, 0) + (a["award_amount"] or 0)
    for v in sorted(vert_counts, key=lambda x: vert_values[x], reverse=True):
        log(f"  {v:25s}  {vert_counts[v]:4d} awards  ${vert_values[v]:>15,.2f}")

    log(f"\nTop 10 by award amount:")
    for a in awards_list[:10]:
        amt = f"${a['award_amount']:,.2f}" if a["award_amount"] else "N/A"
        log(f"  {amt:>18s}  {(a['recipient_name'] or 'Unknown'):30s}  {(a['awarding_agency'] or ''):30s}")

    if vehicle_count:
        log(f"\nContract vehicles:")
        veh_counts = {}
        for a in awards_list:
            if a["vehicle"]:
                veh_counts[a["vehicle"]] = veh_counts.get(a["vehicle"], 0) + 1
        for v, c in sorted(veh_counts.items(), key=lambda x: x[1], reverse=True):
            log(f"  {v:20s}  {c} awards")

    if sa_count:
        log(f"\nSet-asides:")
        sa_counts = {}
        for a in awards_list:
            if a["set_aside"]:
                sa_counts[a["set_aside"]] = sa_counts.get(a["set_aside"], 0) + 1
        for s, c in sorted(sa_counts.items(), key=lambda x: x[1], reverse=True):
            log(f"  {s:30s}  {c} awards")

    log(f"\nMulti-vertical awards: {sum(1 for a in awards_list if len(a['verticals']) > 1)}")
    log(f"{'='*60}")


if __name__ == "__main__":
    main()
