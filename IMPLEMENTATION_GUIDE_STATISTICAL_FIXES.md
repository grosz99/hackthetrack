# Implementation Guide: Statistical Fixes for Driver Rankings

This document provides **exact code changes** needed to fix the statistical issues identified in the validation report.

---

## Fix 1: Replace Equal Weighting with Validated Weights

**File:** `/frontend/src/components/RankingsTable/RankingsTable.jsx`
**Lines:** 11-15
**Priority:** 🔴 CRITICAL

### Current Code (WRONG)
```javascript
// Calculate overall score from 4 factors
const getOverallScore = (driver) => {
  const { speed, consistency, racecraft, tire_management } = driver;
  return Math.round((speed + consistency + racecraft + tire_management) / 4);
};
```

### Issue
This gives each factor equal weight (25%), contradicting statistical evidence that Speed contributes 49% to performance.

### Fixed Code (CORRECT - Option A: Weighted Percentile Average)
```javascript
// Calculate overall score from 4 factors using validated regression weights
const getOverallScore = (driver) => {
  const { speed, consistency, racecraft, tire_management } = driver;

  // Model-validated weights (from regression coefficients)
  // Source: /backend/app/api/routes.py lines 740-746
  const WEIGHT_SPEED = 0.466;        // 49% contribution
  const WEIGHT_CONSISTENCY = 0.291;  // 30% contribution
  const WEIGHT_RACECRAFT = 0.149;    // 16% contribution
  const WEIGHT_TIRE = 0.095;         // 10% contribution

  // Weighted average (percentiles are already 0-100 scale)
  const weightedScore = (
    WEIGHT_SPEED * speed +
    WEIGHT_CONSISTENCY * consistency +
    WEIGHT_RACECRAFT * racecraft +
    WEIGHT_TIRE * tire_management
  );

  return Math.round(weightedScore);
};
```

### Alternative Fixed Code (CORRECT - Option B: Use Regression Model Directly)
```javascript
// Calculate overall score using the validated regression model
const getOverallScore = (driver) => {
  const { speed, consistency, racecraft, tire_management } = driver;

  // Regression model coefficients
  const COEF_SPEED = 6.079;
  const COEF_CONSISTENCY = 3.792;
  const COEF_RACECRAFT = 1.943;
  const COEF_TIRE = 1.237;
  const INTERCEPT = 13.01;

  // Convert percentiles to z-scores (approximate)
  const percentileToZ = (p) => {
    // Clamp to valid range
    const clamped = Math.max(0.01, Math.min(99.99, p));
    // Approximate inverse normal CDF
    const p_norm = clamped / 100;
    // Simple approximation: use probit function
    const t = Math.sqrt(-2 * Math.log(1 - p_norm));
    const z = t - (2.515517 + 0.802853 * t + 0.010328 * t * t) /
                  (1 + 1.432788 * t + 0.189269 * t * t + 0.001308 * t * t * t);
    return p_norm < 0.5 ? -z : z;
  };

  const z_speed = percentileToZ(speed);
  const z_consistency = percentileToZ(consistency);
  const z_racecraft = percentileToZ(racecraft);
  const z_tire = percentileToZ(tire_management);

  // Predicted finish position (1-20 range)
  const predicted_finish = INTERCEPT +
    COEF_SPEED * z_speed +
    COEF_CONSISTENCY * z_consistency +
    COEF_RACECRAFT * z_racecraft +
    COEF_TIRE * z_tire;

  // Convert finish position to 0-100 score (inverted: lower finish = higher score)
  // Assuming ~20 car field
  const overall_score = 100 - ((predicted_finish - 1) * (100 / 19));

  // Clamp to valid range
  return Math.max(0, Math.min(100, Math.round(overall_score)));
};
```

### Recommendation
Use **Option A** (simpler, more interpretable). Option B is more theoretically correct but requires z-score conversion which adds complexity.

---

## Fix 2: Replace Arbitrary Percentile Thresholds

**File:** `/frontend/src/components/RankingsTable/RankingsTable.jsx`
**Lines:** 72-76
**Priority:** 🟡 IMPORTANT

### Current Code (ARBITRARY)
```javascript
const getPercentileColor = (value) => {
  if (value >= 75) return 'var(--color-success)';
  if (value >= 50) return 'var(--color-warning)';
  return 'var(--color-danger)';
};
```

### Issue
- Thresholds (75, 50) are arbitrary with no statistical justification
- Doesn't account for actual driver distribution (most cluster 45-55)
- Fixed thresholds mean 75% of drivers see yellow/red

### Fixed Code (CORRECT - Option A: Relative to Current Pool)
```javascript
const getPercentileColor = (value, factorName, allDrivers) => {
  // Calculate percentile rank within current driver pool
  const allValues = allDrivers.map(d => d[factorName]).filter(v => v != null);
  const sortedValues = [...allValues].sort((a, b) => a - b);
  const rank = sortedValues.filter(v => v < value).length;
  const percentileRank = (rank / sortedValues.length) * 100;

  // Top 25% = green, 25-50% = yellow, bottom 50% = red
  if (percentileRank >= 75) return 'var(--color-success)';   // Top 25%
  if (percentileRank >= 50) return 'var(--color-warning)';   // Top 50%
  return 'var(--color-danger)';                              // Bottom 50%
};
```

### Fixed Code (CORRECT - Option B: Statistical Z-Score Based)
```javascript
const getPercentileColor = (value, factorStats) => {
  // Calculate z-score relative to driver pool
  const zScore = (value - factorStats.mean) / factorStats.std;

  // +0.67 std dev = ~75th percentile (top 25%)
  // 0.00 std dev = 50th percentile (median)
  if (zScore >= 0.67) return 'var(--color-success)';    // Above +0.67σ
  if (zScore >= 0.00) return 'var(--color-warning)';    // Above mean
  return 'var(--color-danger)';                         // Below mean
};

// Also need to calculate factor statistics
const calculateFactorStats = (allDrivers, factorName) => {
  const values = allDrivers.map(d => d[factorName]).filter(v => v != null);
  const mean = values.reduce((sum, v) => sum + v, 0) / values.length;
  const variance = values.reduce((sum, v) => sum + Math.pow(v - mean, 2), 0) / values.length;
  const std = Math.sqrt(variance);
  return { mean, std };
};
```

### Fixed Code (CORRECT - Option C: Data-Driven Absolute Thresholds)
```javascript
const getPercentileColor = (value) => {
  // Based on actual data distribution:
  // 80th percentile ≈ 62-65 for most factors
  // 50th percentile ≈ 47-49 for most factors
  // (See STATISTICAL_VALIDATION_REPORT.md for derivation)

  if (value >= 62) return 'var(--color-success)';    // Top ~20% (data-driven)
  if (value >= 47) return 'var(--color-warning)';    // Above median (data-driven)
  return 'var(--color-danger)';                      // Below median
};
```

### Recommendation
Use **Option A** (relative to pool) for best adaptability. Option B is more statistically rigorous. Option C is simplest but won't adapt to new driver distributions.

---

## Fix 3: Update Display Logic for Weighted Scores

**File:** `/frontend/src/components/RankingsTable/RankingsTable.jsx`
**Lines:** 17-38

### Current Code
```javascript
// Add ranking and stats to drivers
const enrichedDrivers = drivers.map(driver => {
  // Get stats from driver object or stats property
  const stats = driver.stats || driver || {};
  const wins = stats.wins || 0;
  const top10 = stats.top_10 || stats.top10 || 0;
  const dnfs = stats.dnfs || 0;

  return {
    ...driver,
    overall_score: driver.overall_score || getOverallScore(driver),
    wins,
    top10,
    dnfs,
    cornering: driver.racecraft || 0,  // Map to design mockup names
    tire_mgmt: driver.tire_management || 0,
    raw_speed: driver.speed || 0,
  };
});
```

### Fixed Code (with proper color calculation)
```javascript
// Add ranking and stats to drivers
const enrichedDrivers = drivers.map(driver => {
  // Get stats from driver object or stats property
  const stats = driver.stats || driver || {};
  const wins = stats.wins || 0;
  const top10 = stats.top_10 || stats.top10 || 0;
  const dnfs = stats.dnfs || 0;

  return {
    ...driver,
    overall_score: driver.overall_score || getOverallScore(driver),
    wins,
    top10,
    dnfs,
    cornering: driver.racecraft || 0,
    tire_mgmt: driver.tire_management || 0,
    raw_speed: driver.speed || 0,
    // Store original factor values for color calculation
    speed: driver.speed || 0,
    consistency: driver.consistency || 0,
    racecraft: driver.racecraft || 0,
    tire_management: driver.tire_management || 0,
  };
});

// Calculate factor statistics for color thresholds (if using Option B)
const factorStats = {
  speed: calculateFactorStats(enrichedDrivers, 'speed'),
  consistency: calculateFactorStats(enrichedDrivers, 'consistency'),
  racecraft: calculateFactorStats(enrichedDrivers, 'racecraft'),
  tire_management: calculateFactorStats(enrichedDrivers, 'tire_management'),
};
```

---

## Fix 4: Update Percentile Color Calls

**File:** `/frontend/src/components/RankingsTable/RankingsTable.jsx`
**Lines:** 150-211

### Update color function calls to pass context

If using **Option A (Relative to Pool)**:
```javascript
// Replace getPercentileColor(driver.cornering) with:
style={{ backgroundColor: getPercentileColor(driver.cornering, 'cornering', enrichedDrivers) }}

// Do same for tire_mgmt, racecraft, raw_speed
```

If using **Option B (Z-Score Based)**:
```javascript
// Replace getPercentileColor(driver.cornering) with:
style={{ backgroundColor: getPercentileColor(driver.cornering, factorStats.racecraft) }}

// Note: 'cornering' display maps to 'racecraft' factor
// Do same for tire_mgmt, racecraft, raw_speed
```

If using **Option C (Data-Driven Absolute)**:
```javascript
// No changes needed - keeps current getPercentileColor(value) signature
```

---

## Fix 5: Add Explanatory Tooltip

**File:** `/frontend/src/components/RankingsTable/RankingsTable.jsx`
**Add after line 82**

```javascript
<div className="rankings-header">
  <h1 className="rankings-title">DRIVER RANKINGS</h1>
  <p className="rankings-subtitle">Development Pool - 4 Factor Performance Model</p>

  {/* Add explanatory tooltip */}
  <div className="rankings-methodology-note">
    <InfoIcon />
    <span className="methodology-tooltip">
      Overall score uses validated regression weights:
      Speed (49%), Consistency (30%), Racecraft (16%), Tire Management (10%).
      Thresholds are relative to current driver pool.
    </span>
  </div>
</div>
```

Add corresponding CSS (in RankingsTable.css):
```css
.rankings-methodology-note {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-top: 8px;
  padding: 12px;
  background-color: rgba(52, 152, 219, 0.1);
  border-radius: 4px;
  font-size: 13px;
  color: var(--text-secondary);
}

.methodology-tooltip {
  font-style: italic;
}
```

---

## Testing Checklist

After implementing fixes, verify:

### Functionality Tests
- [ ] Overall scores calculate correctly with weighted formula
- [ ] Rankings change appropriately (speed specialists rank higher)
- [ ] Percentile colors adapt to driver pool distribution
- [ ] No errors in browser console
- [ ] Table sorts correctly by all columns

### Statistical Validation Tests
```javascript
// Test Case 1: Speed specialist vs Tire specialist
const speedSpecialist = { speed: 90, consistency: 60, racecraft: 55, tire_management: 50 };
const tireSpecialist = { speed: 50, consistency: 60, racecraft: 55, tire_management: 90 };

const score1 = getOverallScore(speedSpecialist);  // Should be ~69
const score2 = getOverallScore(tireSpecialist);   // Should be ~59

console.assert(score1 > score2, "Speed specialist should rank higher");
console.assert(score1 - score2 >= 8, "Gap should be at least 8 points");
```

```javascript
// Test Case 2: Verify weights sum to 1.0
const weights = {
  speed: 0.466,
  consistency: 0.291,
  racecraft: 0.149,
  tire: 0.095
};

const sum = Object.values(weights).reduce((a, b) => a + b, 0);
console.assert(Math.abs(sum - 1.0) < 0.001, "Weights should sum to 1.0");
```

```javascript
// Test Case 3: Color thresholds are relative
const testDrivers = [
  { speed: 90 }, { speed: 80 }, { speed: 70 }, { speed: 60 },
  { speed: 50 }, { speed: 40 }, { speed: 30 }, { speed: 20 }
];

// Top 25% (90, 80) should be green
// Middle 50% (70, 60, 50, 40) should be yellow
// Bottom 25% (30, 20) should be red
```

### Visual Regression Tests
- [ ] Compare before/after screenshots of rankings table
- [ ] Verify color distribution is more balanced (not 75% yellow/red)
- [ ] Check that rankings match predicted finish positions

---

## Deployment Plan

### Phase 1: Backend Validation (No User Impact)
1. Deploy updated weighting calculation as new endpoint: `/api/rankings/weighted`
2. Run A/B comparison: old equal weights vs new validated weights
3. Verify differences match expectations (speed specialists rank higher)

### Phase 2: Frontend Implementation
1. Update `getOverallScore()` to use weighted formula
2. Update `getPercentileColor()` to use relative thresholds
3. Add methodology tooltip
4. Deploy to staging environment
5. QA testing with real driver data

### Phase 3: User Communication
1. Prepare announcement: "Rankings now use statistically validated weights"
2. Add changelog entry explaining methodology improvement
3. Consider "beta" label for 1 week with option to view old rankings

### Phase 4: Monitoring
1. Monitor user feedback on ranking changes
2. Track engagement metrics (time on rankings page, click-through to driver details)
3. Validate predictions against actual race results (if available)

---

## Rollback Plan

If major issues arise:

1. Revert `getOverallScore()` to equal weighting:
```javascript
// Emergency rollback - use equal weights
return Math.round((speed + consistency + racecraft + tire_management) / 4);
```

2. Revert `getPercentileColor()` to fixed thresholds:
```javascript
// Emergency rollback - use fixed thresholds
if (value >= 75) return 'var(--color-success)';
if (value >= 50) return 'var(--color-warning)';
return 'var(--color-danger)';
```

3. Remove methodology tooltip

4. Investigate issues before re-deploying fixes

---

## Estimated Effort

| Task | Effort | Priority |
|------|--------|----------|
| Update getOverallScore() | 1 hour | Critical |
| Update getPercentileColor() | 2 hours | Important |
| Add methodology tooltip | 30 min | Nice-to-have |
| Testing | 2 hours | Critical |
| Documentation | 1 hour | Important |
| Deployment | 1 hour | Critical |
| **TOTAL** | **7.5 hours** | - |

Single developer can complete in 1 day. 2-day timeline recommended for thorough testing.

---

## Questions?

See full documentation:
- **Technical details:** `STATISTICAL_VALIDATION_REPORT.md`
- **Quick reference:** `STATISTICAL_VALIDATION_SUMMARY.md`
- **Executive summary:** `EXECUTIVE_SUMMARY_STATISTICAL_VALIDATION.md`

For statistical methodology questions, refer to:
- `/backend/app/services/factor_analyzer.py` - Factor calculation logic
- `/scripts/utilities/demonstrate_factor_prediction.py` - Overfitting validation
- `/backend/app/api/routes.py` lines 740-746 - Model coefficients

---

**Last Updated:** November 10, 2025
**Status:** Ready for implementation
**Reviewer:** Statistical Validation Team
