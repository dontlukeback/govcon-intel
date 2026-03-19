# Archive Integration into Pipeline

## Overview

`archive_data.py` should run after every successful pipeline execution to build the cumulative historical dataset. This is the data moat — every week of data makes the dataset harder for competitors to replicate.

## Suggested Addition to pipeline.py

Add the following after the final JSON/CSV write step (around the end of the `main()` function):

```python
# --- Archive for historical dataset ---
import subprocess

print("\n--- Archiving to historical dataset ---")
try:
    result = subprocess.run(
        [sys.executable, os.path.join(BASE_DIR, "archive_data.py")],
        capture_output=True, text=True, timeout=60,
    )
    print(result.stdout)
    if result.returncode != 0:
        print(f"Archive warning: {result.stderr}")
except Exception as e:
    print(f"Archive step failed (non-fatal): {e}")
```

## Suggested Addition to generate.sh

If using the shell wrapper, append:

```bash
# Archive to historical dataset
echo "Archiving awards to historical dataset..."
python3 archive_data.py
```

## Weekly Historical Analysis

After archiving, optionally run the trend analysis:

```bash
python3 historical_analysis.py
```

This generates `data/archive/historical_report.md` and `data/archive/historical_stats.json`. The report gets more valuable every week:

| Weeks | Unlocked Analysis |
|-------|-------------------|
| 1 | Baseline snapshot |
| 2+ | Week-over-week trends |
| 4+ | Monthly patterns, agency spending trends |
| 8+ | Contractor win streaks |
| 12+ | Seasonal patterns, quarterly comparisons |
| 26+ | Half-year trends |
| 52+ | Year-over-year comparisons |

## Files Created

- `data/archive/YYYY-MM-DD.json` — Weekly snapshot (one per pipeline run)
- `data/archive/all_awards.json` — Cumulative deduped master file
- `data/archive/stats.json` — Running statistics
- `data/archive/archive.log` — Activity log
- `data/archive/historical_report.md` — Trend report (from historical_analysis.py)
- `data/archive/historical_stats.json` — Machine-readable trends (from historical_analysis.py)
