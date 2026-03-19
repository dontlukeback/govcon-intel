#!/usr/bin/env bash
#
# auto_publish.sh — Fully autonomous GovCon newsletter pipeline
#
# Cron (Sunday 9 PM PST) -> pull data -> enrich -> generate -> publish to Substack -> done
#
# Usage:
#   ./auto_publish.sh              # Full pipeline + publish
#   ./auto_publish.sh --dry-run    # Full pipeline + draft only (no publish)
#   ./auto_publish.sh --skip-gen   # Skip generation, publish today's existing file
#
# Crontab entry (Sunday 9 PM PST):
#   0 21 * * 0 /Users/luke/Personal/govcon-intel/auto_publish.sh >> /Users/luke/Personal/govcon-intel/output/cron.log 2>&1
#

set -euo pipefail

# ─── Configuration ───────────────────────────────────────────────────────────

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
OUTPUT_DIR="${SCRIPT_DIR}/output"
TODAY="$(date +%Y-%m-%d)"
PYTHON="${PYTHON:-python3}"
LOG_FILE="${OUTPUT_DIR}/publish.log"
NTFY_TOPIC="luke-claude"
DRY_RUN=""
SKIP_GEN=false

# ─── Parse arguments ─────────────────────────────────────────────────────────

while [[ $# -gt 0 ]]; do
    case "$1" in
        --dry-run)
            DRY_RUN="--dry-run"
            shift
            ;;
        --skip-gen)
            SKIP_GEN=true
            shift
            ;;
        *)
            echo "Unknown option: $1"
            echo "Usage: $0 [--dry-run] [--skip-gen]"
            exit 1
            ;;
    esac
done

# ─── Helpers ─────────────────────────────────────────────────────────────────

log() {
    local level="${2:-INFO}"
    local timestamp
    timestamp="$(date '+%Y-%m-%d %H:%M:%S')"
    local msg="[${timestamp}] [${level}] $1"
    echo "${msg}"
    mkdir -p "${OUTPUT_DIR}"
    echo "${msg}" >> "${LOG_FILE}"
}

notify() {
    local msg="$1"
    local priority="${2:-default}"
    curl -s \
        -H "Priority: ${priority}" \
        -H "Tags: newspaper" \
        -d "${msg}" \
        "https://ntfy.sh/${NTFY_TOPIC}" > /dev/null 2>&1 || true
}

# ─── Main Pipeline ───────────────────────────────────────────────────────────

log "========== AUTO PUBLISH START (${TODAY}) =========="
log "Dry run: ${DRY_RUN:-no}"
log "Skip generation: ${SKIP_GEN}"

# Step 1: Run the full generation pipeline (unless --skip-gen)
if [[ "${SKIP_GEN}" == false ]]; then
    log "Step 1: Running generate.sh..."
    if "${SCRIPT_DIR}/generate.sh" >> "${LOG_FILE}" 2>&1; then
        log "Step 1: Pipeline completed successfully"
    else
        EXIT_CODE=$?
        log "Step 1: generate.sh FAILED (exit ${EXIT_CODE})" "ERROR"
        notify "FAIL: GovCon pipeline failed (exit ${EXIT_CODE})" "high"
        exit 1
    fi
else
    log "Step 1: Skipped (--skip-gen)"
fi

# Step 2: Verify the newsletter file exists
SUBSTACK_FILE="${OUTPUT_DIR}/substack_${TODAY}.md"
if [[ ! -f "${SUBSTACK_FILE}" ]]; then
    log "Step 2: Newsletter file not found: ${SUBSTACK_FILE}" "ERROR"
    notify "FAIL: Newsletter file not found for ${TODAY}" "high"
    exit 1
fi
FILE_SIZE=$(wc -c < "${SUBSTACK_FILE}" | tr -d ' ')
log "Step 2: Found ${SUBSTACK_FILE} (${FILE_SIZE} bytes)"

# Sanity check: file should be at least 1KB
if [[ "${FILE_SIZE}" -lt 1000 ]]; then
    log "Step 2: File suspiciously small (${FILE_SIZE} bytes)" "WARN"
    notify "WARN: GovCon newsletter only ${FILE_SIZE} bytes — check quality" "high"
fi

# Step 3: Publish to Substack
log "Step 3: Publishing to Substack..."
if ${PYTHON} "${SCRIPT_DIR}/auto_publish.py" ${DRY_RUN} --date "${TODAY}" 2>&1 | tee -a "${LOG_FILE}"; then
    if [[ -n "${DRY_RUN}" ]]; then
        log "Step 3: Draft created (dry run)"
        notify "GovCon Weekly draft created for ${TODAY} (dry run). Review in Substack dashboard."
    else
        log "Step 3: Published to Substack"
        notify "GovCon Weekly published for ${TODAY}. ${FILE_SIZE} bytes, live on Substack."
    fi
else
    EXIT_CODE=$?
    log "Step 3: auto_publish.py FAILED (exit ${EXIT_CODE})" "ERROR"
    notify "FAIL: Substack publish failed (exit ${EXIT_CODE})" "high"
    exit 1
fi

# ─── Done ────────────────────────────────────────────────────────────────────

log "========== AUTO PUBLISH COMPLETE (${TODAY}) =========="
