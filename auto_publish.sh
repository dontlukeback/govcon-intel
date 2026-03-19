#!/usr/bin/env bash
#
# auto_publish.sh — Fully autonomous GovCon newsletter + alerts + blog pipeline
#
# Sunday:    pull data -> enrich -> generate -> publish newsletter -> archive -> blog -> social -> git push
# Wednesday: recompete alerts only (if CRITICAL contracts exist) -> publish alert email
#
# Usage:
#   ./auto_publish.sh              # Full pipeline + publish
#   ./auto_publish.sh --dry-run    # Full pipeline + draft only (no publish)
#   ./auto_publish.sh --skip-gen   # Skip generation, publish today's existing file
#   ./auto_publish.sh --alerts-only # Mid-week alerts only (Wednesday cron)
#
# Crontab entries:
#   0 21 * * 0 /Users/luke/Personal/govcon-intel/auto_publish.sh >> /Users/luke/Personal/govcon-intel/output/cron.log 2>&1
#   0 9 * * 3 /Users/luke/Personal/govcon-intel/auto_publish.sh --alerts-only >> /Users/luke/Personal/govcon-intel/output/cron.log 2>&1
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
ALERTS_ONLY=false

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
        --alerts-only)
            ALERTS_ONLY=true
            shift
            ;;
        *)
            echo "Unknown option: $1"
            echo "Usage: $0 [--dry-run] [--skip-gen] [--alerts-only]"
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
log "Alerts only: ${ALERTS_ONLY}"

# ─── Mid-week alerts-only mode (Wednesday cron) ─────────────────────────────

if [[ "${ALERTS_ONLY}" == true ]]; then
    log "ALERTS-ONLY MODE: Generating recompete alerts..."

    ALERT_FILE="${OUTPUT_DIR}/alerts/recompete-alert-${TODAY}.md"

    if ${PYTHON} "${SCRIPT_DIR}/generate_alerts.py" >> "${LOG_FILE}" 2>&1; then
        log "Alerts generated successfully"
    else
        log "Alert generation failed or no contracts found" "WARN"
        notify "GovCon mid-week: No critical recompetes this week."
        log "========== ALERTS-ONLY COMPLETE (${TODAY}) =========="
        exit 0
    fi

    # Only publish if there are CRITICAL alerts (contracts expiring in ≤60 days)
    if [[ -f "${ALERT_FILE}" ]] && grep -q "CRITICAL" "${ALERT_FILE}"; then
        log "CRITICAL recompetes found — publishing alert email..."
        ALERT_PUBLISH_ARGS="--file ${ALERT_FILE}"
        if [[ -n "${DRY_RUN}" ]]; then
            ALERT_PUBLISH_ARGS="${ALERT_PUBLISH_ARGS} --draft"
        fi
        if ${PYTHON} "${SCRIPT_DIR}/buttondown_publish.py" ${ALERT_PUBLISH_ARGS} 2>&1 | tee -a "${LOG_FILE}"; then
            log "Alert email published to Buttondown"
            notify "GovCon ALERT: Critical recompetes published for ${TODAY}" "high"
        else
            log "Alert email publish FAILED" "ERROR"
            notify "FAIL: Mid-week alert publish failed" "high"
            exit 1
        fi
    else
        log "No CRITICAL recompetes — skipping alert email"
        notify "GovCon mid-week: No critical recompetes. No email sent."
    fi

    log "========== ALERTS-ONLY COMPLETE (${TODAY}) =========="
    exit 0
fi

# ─── Full Sunday Pipeline ───────────────────────────────────────────────────

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

# Step 3: Publish to Buttondown
log "Step 3: Publishing to Buttondown..."
PUBLISH_ARGS=""
if [[ -n "${DRY_RUN}" ]]; then
    PUBLISH_ARGS="--draft"
fi
if ${PYTHON} "${SCRIPT_DIR}/buttondown_publish.py" ${PUBLISH_ARGS} 2>&1 | tee -a "${LOG_FILE}"; then
    if [[ -n "${DRY_RUN}" ]]; then
        log "Step 3: Draft created (dry run)"
        notify "GovCon Weekly draft created for ${TODAY}. Review in Buttondown dashboard."
    else
        log "Step 3: Published to Buttondown"
        notify "GovCon Weekly published for ${TODAY}. ${FILE_SIZE} bytes. Sent to all subscribers."
    fi
else
    EXIT_CODE=$?
    log "Step 3: buttondown_publish.py FAILED (exit ${EXIT_CODE})" "ERROR"
    notify "FAIL: Buttondown publish failed (exit ${EXIT_CODE})" "high"
    exit 1
fi

# Step 4: Archive this week's data
log "Step 4: Archiving data to historical dataset..."
if ${PYTHON} "${SCRIPT_DIR}/archive_data.py" >> "${LOG_FILE}" 2>&1; then
    log "Step 4: Archive complete"
else
    log "Step 4: Archive failed (non-fatal, continuing)" "WARN"
fi

# Step 5: Generate recompete alerts
log "Step 5: Generating recompete alerts..."
ALERT_FILE="${OUTPUT_DIR}/alerts/recompete-alert-${TODAY}.md"
if ${PYTHON} "${SCRIPT_DIR}/generate_alerts.py" >> "${LOG_FILE}" 2>&1; then
    log "Step 5: Alerts generated"
else
    log "Step 5: No alerts generated or failed (non-fatal)" "WARN"
fi

# Step 6: Publish alerts as second email (only if CRITICAL recompetes exist)
if [[ -f "${ALERT_FILE}" ]] && grep -q "CRITICAL" "${ALERT_FILE}"; then
    log "Step 6: CRITICAL recompetes found — publishing alert email..."
    ALERT_PUBLISH_ARGS="--file ${ALERT_FILE}"
    if [[ -n "${DRY_RUN}" ]]; then
        ALERT_PUBLISH_ARGS="${ALERT_PUBLISH_ARGS} --draft"
    fi
    if ${PYTHON} "${SCRIPT_DIR}/buttondown_publish.py" ${ALERT_PUBLISH_ARGS} 2>&1 | tee -a "${LOG_FILE}"; then
        log "Step 6: Alert email published"
        notify "GovCon ALERT: Critical recompetes also published for ${TODAY}" "high"
    else
        log "Step 6: Alert email publish failed (non-fatal)" "WARN"
    fi
else
    log "Step 6: No CRITICAL recompetes — skipping alert email"
fi

# Step 7: Generate weekly blog post
log "Step 7: Generating blog post..."
if ${PYTHON} "${SCRIPT_DIR}/generate_blog.py" >> "${LOG_FILE}" 2>&1; then
    log "Step 7: Blog post generated"
else
    log "Step 7: Blog generation failed (non-fatal)" "WARN"
fi

# Step 8: Generate social content
log "Step 8: Generating social content..."
if ${PYTHON} "${SCRIPT_DIR}/marketing/weekly-auto-content.py" >> "${LOG_FILE}" 2>&1; then
    log "Step 8: Social content generated"
else
    log "Step 8: Social content generation failed (non-fatal)" "WARN"
fi

# Step 9: Git commit + push (auto-deploys blog to GitHub Pages)
log "Step 9: Committing and pushing to GitHub..."
cd "${SCRIPT_DIR}"
git add landing/blog/ output/alerts/ output/social/ data/archive/ >> "${LOG_FILE}" 2>&1 || true
if git diff --cached --quiet 2>/dev/null; then
    log "Step 9: No new files to commit"
else
    COMMIT_MSG="auto: weekly pipeline ${TODAY} — blog + alerts + social"
    if git commit -m "${COMMIT_MSG}" >> "${LOG_FILE}" 2>&1; then
        log "Step 9: Committed"
        if [[ -n "${DRY_RUN}" ]]; then
            log "Step 9: Skipping push (dry run)"
        else
            if git push origin main >> "${LOG_FILE}" 2>&1; then
                log "Step 9: Pushed to origin/main (GitHub Pages deploy triggered)"
                notify "GovCon pipeline complete: newsletter + blog + social for ${TODAY}"
            else
                log "Step 9: Git push failed" "ERROR"
                notify "WARN: GovCon pipeline finished but git push failed" "high"
            fi
        fi
    else
        log "Step 9: Git commit failed" "WARN"
    fi
fi
cd - > /dev/null 2>&1

# ─── Done ────────────────────────────────────────────────────────────────────

log "========== AUTO PUBLISH COMPLETE (${TODAY}) =========="
