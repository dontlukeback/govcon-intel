#!/usr/bin/env bash
#
# prepare_publish.sh — One-command newsletter publish workflow
#
# Runs the full pipeline, generates charts, copies Substack markdown
# to clipboard, and opens the Substack editor in the browser.
#
# Usage:
#   ./prepare_publish.sh              # Full pipeline + copy + open browser
#   ./prepare_publish.sh --skip-gen   # Skip pipeline (use today's existing output)
#   ./prepare_publish.sh --days 14    # Pass --days through to generate.sh
#

set -euo pipefail

# ─── Configuration ───────────────────────────────────────────────────────────

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
OUTPUT_DIR="${SCRIPT_DIR}/output"
TODAY="$(date +%Y-%m-%d)"
PYTHON="${PYTHON:-python3}"
SUBSTACK_URL="https://govconintelligence.substack.com"
NEW_POST_URL="${SUBSTACK_URL}/publish/post"

SUBSTACK_MD="${OUTPUT_DIR}/substack_${TODAY}.md"
DATA_FILE="${SCRIPT_DIR}/data/govcon_awards_${TODAY}.json"

SKIP_GEN=false
GEN_ARGS=()

# ─── Color helpers ───────────────────────────────────────────────────────────

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
BOLD='\033[1m'
DIM='\033[2m'
NC='\033[0m'

info()    { echo -e "${BLUE}[INFO]${NC}  $*"; }
success() { echo -e "${GREEN}[OK]${NC}    $*"; }
warn()    { echo -e "${YELLOW}[SKIP]${NC}  $*"; }
fail()    { echo -e "${RED}[FAIL]${NC}  $*"; }
header()  { echo -e "\n${BOLD}━━━ $* ━━━${NC}"; }

# ─── Parse arguments ─────────────────────────────────────────────────────────

while [[ $# -gt 0 ]]; do
    case "$1" in
        --skip-gen)
            SKIP_GEN=true
            shift
            ;;
        --days)
            GEN_ARGS+=(--days "${2:?'--days requires a number'}")
            shift 2
            ;;
        --help|-h)
            echo "Usage: $0 [OPTIONS]"
            echo ""
            echo "Options:"
            echo "  --skip-gen    Skip pipeline generation (use today's existing output)"
            echo "  --days N      Pass --days N through to generate.sh"
            echo "  --help        Show this help message"
            exit 0
            ;;
        *)
            echo "Unknown option: $1"
            exit 1
            ;;
    esac
done

# ─── Banner ──────────────────────────────────────────────────────────────────

echo -e "${BOLD}"
echo "╔══════════════════════════════════════════════════╗"
echo "║    GovCon Intelligence — Publish Workflow        ║"
echo "╚══════════════════════════════════════════════════╝"
echo -e "${NC}"
info "Date: ${TODAY}"
echo ""

ERRORS=0

# ─── Step 1: Run the full pipeline ───────────────────────────────────────────

header "Step 1/4 — Generate newsletter"

if [[ "${SKIP_GEN}" == true ]]; then
    if [[ -f "${SUBSTACK_MD}" ]]; then
        warn "Skipping generation (--skip-gen). Using existing ${SUBSTACK_MD##*/}"
    else
        fail "No Substack markdown found for today: ${SUBSTACK_MD##*/}"
        fail "Cannot skip generation when no output exists. Remove --skip-gen."
        exit 1
    fi
elif [[ -f "${SUBSTACK_MD}" ]]; then
    warn "Substack markdown already exists for today: ${SUBSTACK_MD##*/}"
    echo -ne "  ${DIM}Re-generate? [y/N]:${NC} "
    read -r REGEN </dev/tty || REGEN="n"
    if [[ "${REGEN}" =~ ^[Yy]$ ]]; then
        info "Re-running pipeline..."
        if bash "${SCRIPT_DIR}/generate.sh" "${GEN_ARGS[@]+"${GEN_ARGS[@]}"}"; then
            success "Pipeline complete"
        else
            fail "Pipeline failed (exit $?)"
            ERRORS=$((ERRORS + 1))
        fi
    else
        warn "Keeping existing output"
    fi
else
    info "Running full pipeline..."
    if bash "${SCRIPT_DIR}/generate.sh" "${GEN_ARGS[@]+"${GEN_ARGS[@]}"}"; then
        success "Pipeline complete"
    else
        fail "Pipeline failed (exit $?)"
        ERRORS=$((ERRORS + 1))
    fi
fi

# Verify the markdown exists after generation
if [[ ! -f "${SUBSTACK_MD}" ]]; then
    fail "Substack markdown not found: ${SUBSTACK_MD}"
    fail "Pipeline did not produce expected output. Check errors above."
    exit 1
fi

# ─── Step 2: Generate charts ─────────────────────────────────────────────────

header "Step 2/4 — Generate charts"

CHARTS_SCRIPT="${SCRIPT_DIR}/create_charts.py"
ASSETS_DIR="${SCRIPT_DIR}/assets"

if [[ ! -f "${CHARTS_SCRIPT}" ]]; then
    warn "create_charts.py not found — skipping charts"
elif [[ -d "${ASSETS_DIR}" ]] && [[ $(find "${ASSETS_DIR}" -name "*.png" -newer "${DATA_FILE}" 2>/dev/null | head -1) ]]; then
    warn "Charts already up to date (newer than data file)"
else
    info "Generating charts..."
    if ${PYTHON} "${CHARTS_SCRIPT}" 2>&1; then
        CHART_COUNT=$(find "${ASSETS_DIR}" -name "*.png" 2>/dev/null | wc -l | tr -d ' ')
        success "Charts generated (${CHART_COUNT} images in assets/)"
    else
        fail "create_charts.py failed"
        warn "Continuing without charts — you can add them manually in the Substack editor"
        ERRORS=$((ERRORS + 1))
    fi
fi

# ─── Step 3: Copy to clipboard ───────────────────────────────────────────────

header "Step 3/4 — Copy to clipboard"

if command -v pbcopy &>/dev/null; then
    pbcopy < "${SUBSTACK_MD}"
    LINES=$(wc -l < "${SUBSTACK_MD}" | tr -d ' ')
    CHARS=$(wc -c < "${SUBSTACK_MD}" | tr -d ' ')
    success "Copied to clipboard (${LINES} lines, ${CHARS} chars)"
elif command -v xclip &>/dev/null; then
    xclip -selection clipboard < "${SUBSTACK_MD}"
    success "Copied to clipboard via xclip"
elif command -v xsel &>/dev/null; then
    xsel --clipboard < "${SUBSTACK_MD}"
    success "Copied to clipboard via xsel"
else
    fail "No clipboard utility found (pbcopy/xclip/xsel)"
    info "Manual copy: cat ${SUBSTACK_MD} | pbcopy"
    ERRORS=$((ERRORS + 1))
fi

# ─── Step 4: Open Substack editor ────────────────────────────────────────────

header "Step 4/4 — Open Substack editor"

if command -v open &>/dev/null; then
    open "${NEW_POST_URL}"
    success "Opened ${NEW_POST_URL}"
elif command -v xdg-open &>/dev/null; then
    xdg-open "${NEW_POST_URL}"
    success "Opened ${NEW_POST_URL}"
else
    warn "Cannot open browser automatically"
    info "Open manually: ${NEW_POST_URL}"
fi

# ─── Final instructions ─────────────────────────────────────────────────────

header "Ready to Publish"
echo ""
echo -e "${GREEN}${BOLD}Content copied to clipboard.${NC}"
echo ""
echo -e "  ${BOLD}1.${NC} Paste into the Substack editor (Cmd+V)"
echo -e "  ${BOLD}2.${NC} Set the title and subtitle"
echo -e "  ${BOLD}3.${NC} Add chart images from: ${DIM}${ASSETS_DIR}/${NC}"
echo -e "  ${BOLD}4.${NC} Preview, then publish"
echo ""

if [[ ${ERRORS} -gt 0 ]]; then
    echo -e "${YELLOW}Completed with ${ERRORS} warning(s). Check output above.${NC}"
else
    echo -e "${GREEN}All steps completed successfully.${NC}"
fi

echo ""
echo -e "${DIM}Source:  ${SUBSTACK_MD}${NC}"
echo -e "${DIM}Charts: ${ASSETS_DIR}/${NC}"
echo -e "${DIM}Instructions: ${SCRIPT_DIR}/prepare_publish_instructions.md${NC}"
echo ""
