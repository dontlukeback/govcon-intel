# Quality Check Integration for generate.sh

**Date:** 2026-03-19
**Context:** Add `data_quality.py` as a validation step after pipeline.py in the main generation script.

---

## Suggested Patch

Insert a new step between Step 1 (data pull) and Step 2 (AI enrichment) in `generate.sh`. The quality check runs against the raw pipeline output before any downstream processing.

### Where to insert

After the existing Step 1 block (after the `fi` that closes the "Expected data file not found" check, around line 107), add:

```bash
# ─── Step 1.5: Data quality validation ───────────────────────────────────────

header "Step 1.5 — Data quality validation"

if ${PYTHON} "${SCRIPT_DIR}/data_quality.py" "${PIPELINE_DATA_FILE}"; then
    success "Data quality checks passed"
    GENERATED+=("quality_report_${TODAY}.json")
else
    DQ_EXIT=$?
    if [[ ${DQ_EXIT} -eq 1 ]]; then
        fail "Data quality: CRITICAL issues detected (see report above)"
        fail "Continuing pipeline, but review quality_report_${TODAY}.json before publishing"
        SKIPPED+=("quality gate — critical issues")
    elif [[ ${DQ_EXIT} -eq 2 ]]; then
        fail "Data quality: could not read input file"
        SKIPPED+=("quality validation — input error")
    fi
fi
```

### Also update the step numbering

Rename the subsequent steps:
- Step 2/4 -> Step 2/5
- Step 3/4 -> Step 3/5
- Step 4/4 -> Step 4/5

Or, to avoid renumbering, keep the 1.5 convention since it clearly communicates this is a validation gate between data pull and processing.

---

## Behavior

| Exit Code | Meaning | Pipeline Action |
|-----------|---------|-----------------|
| 0 | All checks passed (or warnings only) | Continue normally |
| 1 | Critical issues found | Log warning, continue (manual review before publish) |
| 2 | Input error (file missing, bad JSON) | Log error, continue (step 1 already validates file exists) |

The quality check does **not** halt the pipeline on failure. This is intentional: the newsletter can still be generated with imperfect data, but the operator should review `data/quality_report_DATE.json` before publishing.

To make it a hard gate (stop pipeline on critical), change the `fail` line to `exit 1`.

---

## Historical tracking

The JSON report saves to `data/quality_report_DATE.json` on each run. Over time this builds a history of data quality trends. A future enhancement could compare the current report to the previous week's report using the `--baseline` flag:

```bash
PREV_REPORT=$(ls -t "${DATA_DIR}"/quality_report_*.json 2>/dev/null | head -2 | tail -1)
if [[ -n "${PREV_REPORT}" ]]; then
    ${PYTHON} "${SCRIPT_DIR}/data_quality.py" "${PIPELINE_DATA_FILE}" --baseline "${PREV_REPORT}"
else
    ${PYTHON} "${SCRIPT_DIR}/data_quality.py" "${PIPELINE_DATA_FILE}"
fi
```
