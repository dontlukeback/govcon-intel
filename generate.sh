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

# ─── Step 1: Pull data ──────────────────────────────────────────────────────

header "Step 1/4 — Pull transaction data from USAspending API"

# pipeline.py saves to data/govcon_awards_YYYY-MM-DD.json by convention
PIPELINE_DATA_FILE="${DATA_DIR}/govcon_awards_${TODAY}.json"
# We also copy/symlink to the output dir for clean date-stamped output
OUTPUT_DATA_FILE="${OUTPUT_DIR}/data_${TODAY}.json"

pull_succeeded=false

if [[ -f "${SCRIPT_DIR}/pipeline.py" ]]; then
    info "Found pipeline.py (improved pipeline)"
    if ${PYTHON} "${SCRIPT_DIR}/pipeline.py" --days "${DAYS}" 2>&1; then
        pull_succeeded=true
        success "Data pull complete"
    else
        fail "pipeline.py failed (exit $?)"
        # Fall through to try pull_corrected.py
        if [[ -f "${SCRIPT_DIR}/pull_corrected.py" ]]; then
            warn "Falling back to pull_corrected.py"
        fi
    fi
fi

if [[ "${pull_succeeded}" == false && -f "${SCRIPT_DIR}/pull_corrected.py" ]]; then
    info "Found pull_corrected.py"
    if ${PYTHON} "${SCRIPT_DIR}/pull_corrected.py" --days "${DAYS}" 2>&1; then
        pull_succeeded=true
        success "Data pull complete (via pull_corrected.py)"
    else
        fail "pull_corrected.py failed (exit $?)"
    fi
fi

# Locate the data file — check both expected locations
DATA_FILE=""
if [[ -f "${PIPELINE_DATA_FILE}" ]]; then
    DATA_FILE="${PIPELINE_DATA_FILE}"
elif [[ -f "${DATA_DIR}/corrected_all.json" ]]; then
    # Fallback to corrected_all.json if that's what the pull script produced
    DATA_FILE="${DATA_DIR}/corrected_all.json"
fi

if [[ -n "${DATA_FILE}" ]]; then
    # Copy to output dir with date stamp
    cp "${DATA_FILE}" "${OUTPUT_DATA_FILE}"
    success "Data saved to output/data_${TODAY}.json"
    GENERATED+=("data_${TODAY}.json")
elif [[ "${pull_succeeded}" == false ]]; then
    if [[ ! -f "${SCRIPT_DIR}/pipeline.py" && ! -f "${SCRIPT_DIR}/pull_corrected.py" ]]; then
        warn "No data pull script found (expected pipeline.py or pull_corrected.py)"
    fi
    SKIPPED+=("data pull")
fi

if [[ "${DRY_RUN}" == true ]]; then
    header "Dry run complete"
    info "Data pull finished. Skipping report generation (--dry-run)."
    if [[ -n "${DATA_FILE}" ]]; then
        AWARD_COUNT=$(${PYTHON} -c "import json; print(len(json.load(open('${DATA_FILE}'))))" 2>/dev/null || echo "?")
        info "Awards pulled: ${AWARD_COUNT}"
    fi
    exit 0
fi

# ─── Step 2: Generate markdown report ───────────────────────────────────────

header "Step 2/4 — Generate markdown report"

REPORT_FILE="${OUTPUT_DIR}/report_${TODAY}.md"

if [[ -f "${SCRIPT_DIR}/generate_report.py" ]]; then
    info "Found generate_report.py"
    REPORT_ARGS=(--output "${REPORT_FILE}" --days "${DAYS}")
    # Pass data file if it exists
    if [[ -n "${DATA_FILE}" ]]; then
        REPORT_ARGS+=(--data "${DATA_FILE}")
    fi
    # Pass template if it exists
    if [[ -f "${SCRIPT_DIR}/SAMPLE_REPORT_V2.md" ]]; then
        REPORT_ARGS+=(--template "${SCRIPT_DIR}/SAMPLE_REPORT_V2.md")
    fi
    if ${PYTHON} "${SCRIPT_DIR}/generate_report.py" "${REPORT_ARGS[@]}" 2>&1; then
        success "Report saved to report_${TODAY}.md"
        GENERATED+=("report_${TODAY}.md")
    else
        fail "generate_report.py failed"
        SKIPPED+=("markdown report")
    fi
elif [[ -n "${DATA_FILE}" ]]; then
    # Fallback: create a minimal report from data
    info "No generate_report.py found — creating stub report from data"
    AWARD_COUNT=$(${PYTHON} -c "import json; print(len(json.load(open('${DATA_FILE}'))))" 2>/dev/null || echo "?")
    TOTAL_VALUE=$(${PYTHON} -c "
import json
awards = json.load(open('${DATA_FILE}'))
total = sum(a.get('award_amount') or 0 for a in awards)
print(f'\${total:,.0f}')
" 2>/dev/null || echo "N/A")
    cat > "${REPORT_FILE}" <<REPORT_EOF
# GovCon Intelligence Weekly Brief

**Period:** ${START_DATE} to ${TODAY}
**Generated:** $(date '+%B %d, %Y at %H:%M %Z')

---

## Summary

- **Total awards tracked:** ${AWARD_COUNT}
- **Total contract value:** ${TOTAL_VALUE}

> Full report generation (generate_report.py) not yet implemented.
> This is a stub. Raw data available at: data_${TODAY}.json

---

*Generated by GovCon Intelligence Pipeline*
REPORT_EOF
    success "Stub report saved to report_${TODAY}.md"
    GENERATED+=("report_${TODAY}.md (stub)")
else
    warn "No report generator and no data file — skipping report"
    SKIPPED+=("markdown report")
fi

# ─── Step 3: Generate insights ──────────────────────────────────────────────

header "Step 3/4 — Generate insights"

INSIGHTS_FILE="${OUTPUT_DIR}/insights_${TODAY}.md"

if [[ -f "${SCRIPT_DIR}/generate_insights.py" ]]; then
    info "Found generate_insights.py"
    INSIGHTS_ARGS=(--output "${INSIGHTS_FILE}")
    if [[ -n "${DATA_FILE}" ]]; then
        INSIGHTS_ARGS+=(--data "${DATA_FILE}")
    fi
    if [[ -f "${REPORT_FILE}" ]]; then
        INSIGHTS_ARGS+=(--report "${REPORT_FILE}")
    fi
    if ${PYTHON} "${SCRIPT_DIR}/generate_insights.py" "${INSIGHTS_ARGS[@]}" 2>&1; then
        success "Insights saved to insights_${TODAY}.md"
        GENERATED+=("insights_${TODAY}.md")
    else
        fail "generate_insights.py failed"
        SKIPPED+=("insights")
    fi
else
    warn "generate_insights.py not found — skipping insights generation"
    SKIPPED+=("insights")
fi

# ─── Step 4: Generate HTML ──────────────────────────────────────────────────

header "Step 4/4 — Generate HTML report"

HTML_FILE="${OUTPUT_DIR}/report_${TODAY}.html"

if [[ -f "${SCRIPT_DIR}/report_to_html.py" ]]; then
    info "Found report_to_html.py"
    HTML_ARGS=(--output "${HTML_FILE}")
    if [[ -f "${REPORT_FILE}" ]]; then
        HTML_ARGS+=(--input "${REPORT_FILE}")
    fi
    if ${PYTHON} "${SCRIPT_DIR}/report_to_html.py" "${HTML_ARGS[@]}" 2>&1; then
        success "HTML saved to report_${TODAY}.html"
        GENERATED+=("report_${TODAY}.html")
    else
        fail "report_to_html.py failed"
        SKIPPED+=("HTML report")
    fi
else
    warn "report_to_html.py not found — skipping HTML generation"
    SKIPPED+=("HTML report")
fi

# ─── Summary ─────────────────────────────────────────────────────────────────

header "Pipeline Complete"
echo ""

if [[ ${#GENERATED[@]} -gt 0 ]]; then
    echo -e "${GREEN}${BOLD}Generated:${NC}"
    for item in "${GENERATED[@]}"; do
        echo -e "  ${GREEN}+${NC} ${OUTPUT_DIR}/${item}"
    done
fi

if [[ ${#SKIPPED[@]} -gt 0 ]]; then
    echo ""
    echo -e "${YELLOW}${BOLD}Skipped (component not yet built):${NC}"
    for item in "${SKIPPED[@]}"; do
        echo -e "  ${YELLOW}-${NC} ${item}"
    done
fi

echo ""
info "Total: ${#GENERATED[@]} generated, ${#SKIPPED[@]} skipped"

if [[ ${#SKIPPED[@]} -gt 0 ]]; then
    echo ""
    info "To build missing components, create these scripts in ${SCRIPT_DIR}/:"
    [[ ! -f "${SCRIPT_DIR}/pipeline.py" && ! -f "${SCRIPT_DIR}/pull_corrected.py" ]] && \
        echo "    - pipeline.py (or pull_corrected.py) — USAspending API data pull"
    [[ ! -f "${SCRIPT_DIR}/generate_report.py" ]] && \
        echo "    - generate_report.py — markdown report from V2 template"
    [[ ! -f "${SCRIPT_DIR}/generate_insights.py" ]] && \
        echo "    - generate_insights.py — AI-generated insights layer"
    [[ ! -f "${SCRIPT_DIR}/report_to_html.py" ]] && \
        echo "    - report_to_html.py — markdown to newsletter HTML"
fi

echo ""
