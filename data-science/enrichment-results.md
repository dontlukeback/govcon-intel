# Enrichment Improvement Results

**Date:** 2026-03-18
**Pipeline run:** `python3 pipeline.py --days 7` (2026-03-11 to 2026-03-18)

---

## Before vs After

| Metric | Before | After | Change |
|--------|--------|-------|--------|
| Total awards | 1,173 | 1,138 | -35 (filtered $0 awards) |
| Vehicle populated | 32 (2.7%) | 37 (3.3%) | +5 awards (+15.6%) |
| Set-aside populated | 56 (4.8%) | 56 (4.9%) | Same count, higher % (smaller denominator) |
| $0 amount awards | 35 | 0 | All removed |

---

## Improvement 1: Enhanced Vehicle Detection

Added `VEHICLE_KEYWORDS` dict with 14 vehicle types detected from description text (in addition to existing ID-based regex patterns).

**New detections from description parsing:** 5 additional awards tagged with vehicles.

| Vehicle | Count |
|---------|-------|
| SEWP | 13 |
| GSA OASIS | 7 |
| ALLIANT 2 | 5 |
| GSA Schedule 70 | 5 (all new from description parsing) |
| 8(a) STARS II | 3 |
| STARS III | 3 |
| CIO-SP3 | 1 |

**Note:** The 3.3% detection rate is lower than the 40-50% projected in the improvement plan. This is because most award descriptions in this week's pull don't mention vehicle names explicitly -- they describe the work being performed. The ID-based patterns remain the primary detection method. The description-based detection adds incremental value, particularly for GSA Schedule 70 and SEWP references.

---

## Improvement 2: Enhanced Set-Aside Detection

Expanded `SET_ASIDE_PATTERNS` with additional regex patterns:
- Added `VOSB` as a new category
- Added patterns: `EDWOSB`, `economically disadvantaged women`, `historically underutilized`, `service disabled` (without veteran), `small business set-aside`, `SDB`
- Added `8(a) program`, `8(a) set-aside`, `8(a) sole source` patterns

**Set-aside breakdown:**
- 1,082 awards: No set-aside data (95.1%)
- 49 awards: API returned "NO SET ASIDE USED" (confirmed no set-aside)
- 7 awards: Real set-aside detected (4 x 8(a), 2 x Small Business, 1 x HUBZone)

**Observation:** The 95%+ null rate is structural -- most federal IT contracts in these verticals are full-and-open competition, not set-asides. The API detail endpoint (Step 5, capped at 50 calls) is the primary source of set-aside data. To materially improve coverage, the SAM.gov Entity API integration (Improvement #2 in the plan, P2 priority) would be needed to look up recipient socioeconomic status.

---

## Improvement 3: $0 Award Filtering

Added Step 6 to pipeline: filters awards where `award_amount` is null or zero before final output.

**Result:** 35 awards removed (3.0% of total). These were noise records (modifications, administrative actions, or placeholder entries) that added no analytical value.

**Impact on data quality:**
- Total award value unchanged (zero-value awards contributed $0)
- Average award amount increased slightly (removed denominator noise)
- All downstream analysis (verticals, vehicles, set-asides) now operates on cleaner data

---

## Code Changes

All changes in `/Users/luke/Personal/govcon-intel/pipeline.py`:

1. **Lines 169-184:** Added `VEHICLE_KEYWORDS` dictionary (14 vehicle types with substring keywords)
2. **Lines 199-213:** Updated `detect_vehicle()` to accept optional `description` parameter and check `VEHICLE_KEYWORDS` as fallback after ID patterns
3. **Lines 186-193:** Expanded `SET_ASIDE_PATTERNS` with additional regex patterns and new `VOSB` category
4. **Line 425:** Updated `detect_vehicle()` call to pass `award.get("description")`
5. **Lines 460-467:** Added Step 6 post-processing filter for $0/null awards

---

## Recommendations for Next Sprint

1. **SAM.gov API integration** would have the highest marginal impact on set-aside detection (P2 in improvement plan)
2. **Increase API enrichment cap** from 50 to 200 -- the detail endpoint provides the most reliable set-aside data
3. **Consider negative vehicle detection** -- awards on GSA Schedule or SEWP often don't mention the vehicle in descriptions; the award ID patterns remain the best signal
