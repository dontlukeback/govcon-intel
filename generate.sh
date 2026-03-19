#!/usr/bin/env bash
#
# generate.sh — GovCon Intelligence Newsletter Pipeline
#
# Usage:
#   ./generate.sh              # Generate this week's report (last 7 days)
#   ./generate.sh --days 14    # Generate for last 14 days
#   ./generate.sh --dry-run    # Pull data but don't generate report
#   ./generate.sh --help       # Show usage
#
# Idempotent: safe to run multiple times. Overwrites same-date outputs.
#

set -euo pipefail

# ─── Configuration ───────────────────────────────────────────────────────────

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
OUTPUT_DIR="${SCRIPT_DIR}/output"
DATA_DIR="${SCRIPT_DIR}/data"
TODAY="$(date +%Y-%m-%d)"
DAYS=7
DRY_RUN=false
PYTHON="${PYTHON:-python3}"

# ─── Color helpers ───────────────────────────────────────────────────────────

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
BOLD='\033[1m'
NC='\033[0m'

info()    { echo -e "${BLUE}[INFO]${NC}  $*"; }
success() { echo -e "${GREEN}[OK]${NC}    $*"; }
warn()    { echo -e "${YELLOW}[SKIP]${NC}  $*"; }
fail()    { echo -e "${RED}[FAIL]${NC}  $*"; }
header()  { echo -e "\n${BOLD}━━━ $* ━━━${NC}"; }

# ─── Parse arguments ─────────────────────────────────────────────────────────

usage() {
    echo "Usage: $0 [OPTIONS]"
    echo ""
    echo "Options:"
    echo "  --days N      Look back N days (default: 7)"
    echo "  --dry-run     Pull data only, skip report generation"
    echo "  --help        Show this help message"
    exit 0
}

while [[ $# -gt 0 ]]; do
    case "$1" in
        --days)
            DAYS="${2:?'--days requires a number'}"
            shift 2
            ;;
        --dry-run)
            DRY_RUN=true
            shift
            ;;
        --help|-h)
            usage
            ;;
        *)
            echo "Unknown option: $1"
            usage
            ;;
    esac
done

# ─── Date range calculation ──────────────────────────────────────────────────

if [[ "$(uname)" == "Darwin" ]]; then
    START_DATE="$(date -v-${DAYS}d +%Y-%m-%d)"
else
    START_DATE="$(date -d "${DAYS} days ago" +%Y-%m-%d)"
fi

# ─── Setup ───────────────────────────────────────────────────────────────────

mkdir -p "${OUTPUT_DIR}" "${DATA_DIR}"

echo -e "${BOLD}"
echo "╔══════════════════════════════════════════════════╗"
echo "║     GovCon Intelligence — Newsletter Pipeline    ║"
echo "╚══════════════════════════════════════════════════╝"
echo -e "${NC}"
info "Date:       ${TODAY}"
info "Range:      ${START_DATE} to ${TODAY} (${DAYS} days)"
info "Dry run:    ${DRY_RUN}"
info "Output dir: ${OUTPUT_DIR}"
echo ""

# Track what was generated for the summary
GENERATED=()
SKIPPED=()

# ─── Step 1: Pull data from USAspending API ─────────────────────────────────

header "Step 1/4 — Pull data from USAspending API"

PIPELINE_DATA_FILE="${DATA_DIR}/govcon_awards_${TODAY}.json"

if ${PYTHON} "${SCRIPT_DIR}/pipeline.py" --days "${DAYS}" 2>&1; then
    success "Data pull complete"
    GENERATED+=("govcon_awards_${TODAY}.json")
else
    fail "pipeline.py failed (exit $?)"
    SKIPPED+=("data pull")
fi

if [[ ! -f "${PIPELINE_DATA_FILE}" ]]; then
    fail "Expected data file not found: ${PIPELINE_DATA_FILE}"
    fail "Cannot continue without data. Exiting."
    exit 1
fi

if [[ "${DRY_RUN}" == true ]]; then
    header "Dry run complete"
    AWARD_COUNT=$(${PYTHON} -c "import json; print(len(json.load(open('${PIPELINE_DATA_FILE}'))))" 2>/dev/null || echo "?")
    info "Awards pulled: ${AWARD_COUNT}"
    exit 0
fi

# ─── Step 2: AI enrichment ──────────────────────────────────────────────────

header "Step 2/4 — Enrich data with AI editorial analysis"

if [[ -f "${SCRIPT_DIR}/enrich.py" ]]; then
    info "Running enrich.py (Claude API)..."
    if ${PYTHON} "${SCRIPT_DIR}/enrich.py" --input "${PIPELINE_DATA_FILE}" --date "${TODAY}" 2>&1; then
        success "Enrichment complete — data/corrected_all.json updated"
        GENERATED+=("enriched_${TODAY}.json")
    else
        fail "enrich.py failed"
        if [[ -f "${DATA_DIR}/corrected_all.json" ]]; then
            warn "Using existing corrected_all.json as fallback"
        else
            fail "No enriched data available. Cannot generate newsletter."
            exit 1
        fi
    fi
else
    warn "enrich.py not found — skipping AI enrichment"
    SKIPPED+=("AI enrichment")
fi

# ─── Step 3: Generate HTML newsletter ────────────────────────────────────────

header "Step 3/4 — Generate HTML newsletter"

if [[ -f "${SCRIPT_DIR}/generate_newsletter.py" ]]; then
    if ${PYTHON} "${SCRIPT_DIR}/generate_newsletter.py" 2>&1; then
        success "HTML newsletter generated"
        GENERATED+=("report_${TODAY}_v2.html")
    else
        fail "generate_newsletter.py failed"
        SKIPPED+=("HTML newsletter")
    fi
else
    warn "generate_newsletter.py not found"
    SKIPPED+=("HTML newsletter")
fi

# ─── Step 4: Generate Substack markdown ──────────────────────────────────────

header "Step 4/4 — Generate Substack markdown"

if [[ -f "${SCRIPT_DIR}/generate_substack.py" ]]; then
    if ${PYTHON} "${SCRIPT_DIR}/generate_substack.py" 2>&1; then
        success "Substack markdown generated"
        GENERATED+=("substack_${TODAY}.md")
    else
        fail "generate_substack.py failed"
        SKIPPED+=("Substack markdown")
    fi
else
    warn "generate_substack.py not found"
    SKIPPED+=("Substack markdown")
fi

# ─── Summary ─────────────────────────────────────────────────────────────────

header "Pipeline Complete"
echo ""

if [[ ${#GENERATED[@]} -gt 0 ]]; then
    echo -e "${GREEN}${BOLD}Generated:${NC}"
    for item in "${GENERATED[@]}"; do
        echo -e "  ${GREEN}+${NC} ${item}"
    done
fi

if [[ ${#SKIPPED[@]} -gt 0 ]]; then
    echo ""
    echo -e "${YELLOW}${BOLD}Skipped:${NC}"
    for item in "${SKIPPED[@]}"; do
        echo -e "  ${YELLOW}-${NC} ${item}"
    done
fi

echo ""
info "Total: ${#GENERATED[@]} generated, ${#SKIPPED[@]} skipped"
echo ""
