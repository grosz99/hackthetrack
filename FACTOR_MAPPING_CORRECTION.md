# 4-Factor Model - Corrected Factor Mapping

## CRITICAL: Documentation Update Required

The current documentation has the factor labels **reversed** from what the PCA actually produces. This table shows the correct mapping based on factor loadings analysis.

## Correct Factor Interpretation

| Factor # | Weight | Correct Label | Top Contributing Features | Interpretation |
|----------|--------|---------------|---------------------------|----------------|
| **Factor 1** | **29.1%** | **CONSISTENCY** | sector_consistency (high)<br>braking_consistency (high)<br>stint_consistency (high) | Driver's ability to maintain consistent sector times, braking points, and lap times. High consistency = more predictable, stable performance. |
| **Factor 2** | **14.9%** | **TIRE MANAGEMENT** | pace_degradation (high)<br>late_stint_perf (high)<br>early_vs_late_pace (high) | Driver's ability to manage tire wear and maintain pace as tires degrade. Better tire mgmt = stronger late-stint performance. |
| **Factor 3** | **46.6%** | **RACECRAFT** | positions_gained (high)<br>position_changes (high)<br>overtaking skill | Driver's racing skill - ability to gain positions, execute overtakes, and navigate race situations. **Most important factor** at 46.6% weight. |
| **Factor 4** | **9.5%** | **SPEED/PACE** | qualifying_pace (high)<br>best_race_lap (high)<br>avg_top10_pace (high) | Raw speed - qualifying pace and single-lap performance. Surprisingly the **least important** factor (only 9.5%). |

## Key Insight

**Racecraft (46.6%) matters MORE than raw Speed (9.5%)** in determining race results. This makes intuitive sense - in close racing, the ability to gain positions through overtaking and race management is more important than pure qualifying pace.

## What Needs to Be Updated

### 1. Documentation Files
Update any references to factor weights in:
- README.md
- API documentation
- Model description documents
- Research papers/presentations

### 2. Code Comments
Search for comments that reference factor interpretations:
```bash
rg "Speed.*46.6" 
rg "Factor.*Speed|Factor.*Consistency|Factor.*Racecraft|Factor.*Tire"
```

### 3. UI Labels
If the frontend displays factor names, update:
- Dashboard factor breakdown displays
- Driver profile factor scores
- Analytics visualizations
- Any tooltips or help text

### 4. JSON Data Files
Check if any JSON files have hardcoded factor labels:
- `driver_factors.json` - Verify factor keys/labels
- `factor_breakdowns.json` - Update any label fields
- `dashboardData.json` - Update factor descriptions

## Search & Replace Commands

```bash
# Find all references to the incorrect mapping
cd /Users/justingrosz/Documents/AI-Work/hackthetrack-master

# Search for factor label references
rg -i "speed.*46|46.*speed"
rg -i "consistency.*29|29.*consistency"
rg -i "racecraft.*14|14.*racecraft"
rg -i "tire.*9|9.*tire"

# Check JSON files specifically
rg "\"speed\".*46|46.*\"speed\"" --type json
rg "\"factor_1\".*speed|speed.*\"factor_1\"" --type json
```

## Verification

After updates, verify the mapping by checking:

1. **Factor loadings** in `tier1_factor_loadings.csv` - Factor 3 should have highest loadings on `positions_gained`
2. **Regression coefficients** - Factor 3 should have coefficient ~6.079 (highest absolute value)
3. **UI displays** - Factor labels should match the corrected table above

## Mathematical Proof

From validation output:
```
Factor 3 (46.6% weight):
  Top loadings:
    positions_gained:      0.482  ← Highest loading
    position_changes:      0.412  ← Second highest
    braking_consistency:  -0.404

Factor 4 (9.5% weight):
  Top loadings:
    early_vs_late_pace:    0.644
    late_stint_perf:       0.382
    braking_consistency:  -0.379
```

This clearly shows Factor 3 captures **Racecraft** (positions gained/changed), not Speed.

---

**Status:** Documentation correction required
**Priority:** High (affects user understanding of model)
**Impact:** No model changes needed, labels only
**Validated:** November 18, 2025
