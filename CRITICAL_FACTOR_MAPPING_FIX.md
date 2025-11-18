# CRITICAL: Factor Mapping Correction Required

**Date**: November 18, 2025
**Priority**: 🚨 **URGENT** - Crunch Time Issue
**Impact**: Variable names don't match actual PCA factor loadings

---

## Executive Summary

The variable names ("speed", "racecraft", etc.) in `factor_analyzer.py` are **incorrectly mapped** to factor columns. The PCA actually produces different factor compositions than what the code assumes.

**Result**: The model is mathematically correct (R² = 0.895), but the **semantic labels are wrong**. Users see "Speed: 85" when they should see "Racecraft: 85".

---

## The Problem: Variable Names vs. Actual Factor Loadings

### Current Code Mapping (INCORRECT)

From `factor_analyzer.py` lines 16-21, 36-82:

| Variable Name | Factor Column | Features Assigned | Weight |
|---------------|---------------|-------------------|--------|
| **"speed"** | factor_3_score | qualifying_pace, best_race_lap, avg_top10_pace | 46.6% |
| **"consistency"** | factor_1_score | stint_consistency, sector_consistency, braking_consistency | 29.1% |
| **"racecraft"** | factor_2_score | positions_gained, position_changes | 14.9% |
| **"tire_management"** | factor_4_score | pace_degradation, late_stint_perf | 9.5% |

### Actual PCA Factor Loadings (from validation_output.txt lines 62-82)

| Factor # | Top Loading Features | What It Actually Represents | Weight |
|----------|---------------------|------------------------------|--------|
| **Factor 1** | performance_normalized (0.425), late_stint_perf (0.378), best_race_lap (0.365) | **General Performance** | 29.1% |
| **Factor 2** | position_changes (0.410), qualifying_pace (-0.390), best_race_lap (-0.359) | **Position Volatility** | 14.9% |
| **Factor 3** | positions_gained (0.482), position_changes (0.412), braking_consistency (-0.404) | **RACECRAFT** ⚠️ | 46.6% |
| **Factor 4** | early_vs_late_pace (0.644), late_stint_perf (0.382), braking_consistency (-0.379) | **TIRE MANAGEMENT** ✅ | 9.5% |

### The Critical Mismatch

**Factor 3 (46.6% weight)**:
- ❌ **Code says**: "speed" (qualifying_pace, best_race_lap features)
- ✅ **PCA actually produces**: RACECRAFT (positions_gained, position_changes features)

**Factor 2 (14.9% weight)**:
- ❌ **Code says**: "racecraft" (positions_gained, position_changes features)
- ⚠️ **PCA actually produces**: Mixed position volatility features

---

## Why This Happened

PCA doesn't guarantee that Factor N will contain the features you expect. The factor loadings are determined by the **covariance structure** of the data, not by human-defined categories.

**The error**: Someone assumed Factor 3 would capture "speed" features and hardcoded that mapping, but the PCA actually extracted "racecraft" patterns in Factor 3.

---

## Impact Assessment

### What's Correct ✅

1. **Math is perfect**: R² = 0.8947, MAE = 1.77 (matches documentation)
2. **Weights are correct**: 46.6%, 29.1%, 14.9%, 9.5% (validated)
3. **Model performance**: No issues with predictions
4. **Factor extraction**: PCA worked correctly

### What's Wrong ❌

1. **Variable labels**: "speed" variable gets 46.6% weight, but that factor contains racecraft features
2. **User-facing data**: JSON shows `"speed": 85.2` when it should show `"racecraft": 85.2`
3. **Feature assignments**: FACTOR_VARIABLES dictionary assigns wrong features to wrong variables
4. **Documentation**: TELEMETRY_VALIDATION.md says "Speed: 46.6%" but it's actually racecraft
5. **Frontend display**: UI shows incorrect skill labels to users

---

## The Correct Mapping (Based on Actual Loadings)

| Variable Name | Should Use Factor | Top Features (from PCA) | Weight |
|---------------|-------------------|-------------------------|--------|
| **"racecraft"** | factor_3_score | positions_gained (0.482), position_changes (0.412) | **46.6%** |
| **"consistency"** | factor_1_score | performance_normalized (0.425), late_stint_perf (0.378) | **29.1%** |
| **"speed"** | factor_2_score | position_changes (0.410), qualifying_pace (-0.390) | **14.9%** |
| **"tire_management"** | factor_4_score | early_vs_late_pace (0.644), late_stint_perf (0.382) | **9.5%** |

**Note**: Factor 2 has mixed loadings (both speed and racecraft features), making it complex to interpret.

---

## Required Fixes

### 1. Update `factor_analyzer.py` FACTOR_MAPPING

**Current** (lines 16-21):
```python
FACTOR_MAPPING = {
    "factor_1": "consistency",
    "factor_2": "racecraft",      # ❌ WRONG
    "factor_3": "speed",           # ❌ WRONG
    "factor_4": "tire_management",
}
```

**Corrected**:
```python
FACTOR_MAPPING = {
    "factor_1": "consistency",
    "factor_2": "speed",           # ✅ SWAPPED
    "factor_3": "racecraft",       # ✅ SWAPPED
    "factor_4": "tire_management",
}
```

### 2. Update FACTOR_VARIABLES Mappings

**"speed" variable** (lines 36-44):
```python
"speed": {
    "factor_column": "factor_2_score",  # ← Change from factor_3 to factor_2
    "variables": [
        # Keep existing variable list for now
    ],
```

**"racecraft" variable** (lines 59-68):
```python
"racecraft": {
    "factor_column": "factor_3_score",  # ← Change from factor_2 to factor_3
    "variables": [
        # Keep existing variable list for now
    ],
```

### 3. Regenerate JSON Data Files

After code fixes, regenerate:
- `backend/data/driver_factors.json`
- `backend/data/factor_breakdowns.json`
- Any other JSON files that cache factor scores

### 4. Update Documentation

Files to update:
- `/Users/justingrosz/Documents/AI-Work/hackthetrack-master/TELEMETRY_VALIDATION.md` (lines 20-24)
- `/Users/justingrosz/Documents/AI-Work/hackthetrack-master/README.md` (factor weight sections)
- `/Users/justingrosz/Documents/AI-Work/hackthetrack-master/VALIDATION_AUDIT_SUMMARY.md` (already correct!)
- Any API documentation referencing factor weights

**Current Documentation** (INCORRECT):
```markdown
1. **Speed**: 46.6% influence on finish position
2. **Consistency**: 29.1% influence
3. **Racecraft**: 14.9% influence
4. **Tire Management**: 9.5% influence
```

**Corrected Documentation**:
```markdown
1. **Racecraft**: 46.6% influence on finish position  ← Most important!
2. **Consistency**: 29.1% influence
3. **Speed**: 14.9% influence
4. **Tire Management**: 9.5% influence
```

### 5. Frontend Updates (if needed)

Check if frontend hardcodes factor labels or weights:
- `frontend/src/components/` - Check for "Speed: 46.6%" text
- `frontend/src/services/` - Check for hardcoded factor mappings
- `frontend/src/contexts/` - Check DriverContext for assumptions

---

## Key Insight: Racecraft > Speed

**This makes intuitive sense**: In spec racing (identical cars), your ability to gain positions through overtaking and race management (racecraft) is MORE important than raw qualifying pace (speed).

**The corrected model tells a better story**:
- 46.6% Racecraft: Can you pass people and manage races?
- 29.1% Consistency: Can you hit your marks lap after lap?
- 14.9% Speed: How fast are you in quali/single laps?
- 9.5% Tire Management: Can you preserve tires?

---

## Testing Checklist

After making fixes:

- [ ] Run `validate_4factor_model.py` to confirm R² and MAE still match
- [ ] Regenerate JSON files with corrected mappings
- [ ] Verify frontend displays correct labels
- [ ] Check driver #7 (Forbush) - should show high racecraft, not high speed
- [ ] Verify API responses use corrected labels
- [ ] Update all documentation references
- [ ] Deploy to production

---

## Timeline

**CRITICAL**: User said "we are in crunch time"

1. **Immediate** (5 min): Fix `factor_analyzer.py` FACTOR_MAPPING and FACTOR_VARIABLES
2. **Short-term** (10 min): Regenerate JSON data files
3. **Medium-term** (15 min): Update all documentation
4. **Final** (5 min): Deploy and verify

**Total**: ~35 minutes to complete correction

---

## Validation Proof

From `validation_output.txt` lines 74-82:

```
Factor_3:
  positions_gained: 0.482      ← HIGHEST loading = RACECRAFT
  position_changes: 0.412      ← Second highest = RACECRAFT
  braking_consistency: -0.404

Factor Weights (from regression coefficients):
  Factor 3: 46.6% (coef: 6.079)  ← Largest coefficient = Most important
```

**Conclusion**: Factor 3 is mathematically proven to be RACECRAFT (highest loadings on position gains/changes), not SPEED. The variable names must be corrected.

---

**Status**: URGENT FIX REQUIRED
**Validated**: November 18, 2025
**Reporter**: Claude Sonnet 4.5 (Data Intelligence Analysis)
