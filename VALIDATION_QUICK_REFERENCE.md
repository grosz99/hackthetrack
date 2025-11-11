# Statistical Validation: Quick Reference Card

**Last Updated**: 2025-11-10
**Data**: Barber R1 (n=16 drivers)

---

## ✅ APPROVED FOR COACHING

### braking_point_consistency (ONLY)
- **r = 0.573**, p = 0.020
- **Effect**: LARGE
- **Actionable**: ✅ YES
- **Status**: **VALIDATED**

---

## ❌ NOT APPROVED (6 metrics)

| Metric | Reason |
|--------|--------|
| throttle_smoothness | Not significant (p=0.55) |
| steering_smoothness | Not significant (p=0.59) |
| corner_efficiency | Not significant (p=0.25) |
| accel_efficiency | Not significant (p=0.92) |
| straight_speed_consistency | Not significant (p=0.75) |
| lateral_g_utilization | Car dependent (not actionable) |

---

## 🚨 CRITICAL: DO NOT Build Predictive Models

**ALL models FAIL cross-validation**:
- Linear: CV R² = **-1.08** ❌
- Ridge: CV R² = **-0.75** ❌
- Random Forest: CV R² = **-0.82** ❌

**Negative CV R²** = Predictions worse than guessing average

**Cause**: 16 drivers ÷ 7 metrics = 2.3:1 (need 10:1 minimum)

---

## ✅ SAFE Use Cases

1. **Percentile rankings** (braking only)
2. **Progress tracking** over time
3. **Peer comparisons** (with disclaimers)
4. **Descriptive stats** (mean, median, quartiles)

---

## ❌ FORBIDDEN Use Cases

1. **Predictive models** (lap_time ~ metrics)
2. **Causal claims** ("improving X will cause Y")
3. **Unvalidated metrics** for coaching
4. **Multi-metric formulas** (regression coefficients unreliable)

---

## 📊 Sample Output (SAFE)

```
Driver #7 - Braking Consistency Analysis

Your Value: 0.048 seconds (std dev)
Your Ranking: 50th percentile (above average)

Benchmark:
  Top 25%: <0.014 seconds
  Top 10%: <0.009 seconds

Improvement Target:
  To reach top 25%: -0.034 (-70% reduction)

Note: Correlation does not imply causation.
Improvements in this metric are associated with
faster lap times (r=0.57, p=0.02).
```

---

## 📈 Sample Size Requirements

| Analysis Type | Current | Required | Status |
|--------------|---------|----------|--------|
| Single correlation | 16 | 15 | ✅ OK |
| Multiple regression | 16 | 70 | ❌ -54 |
| Stable estimates | 16 | 140 | ❌ -124 |

---

## 🔧 Quick Start Code

```python
from safe_coaching_implementation import SafeCoachingAnalyzer

analyzer = SafeCoachingAnalyzer(data_dir="data")

# Get driver insights
insights = analyzer.generate_driver_insights(
    driver_number=7,
    race_name="barber_r1"
)

# Compare drivers
comparison = analyzer.compare_drivers_safely(
    driver_a=7,
    driver_b=13,
    race_name="barber_r1"
)

# Get leaderboard
leaderboard = analyzer.get_track_leaderboard(
    race_name="barber_r1",
    metric="braking_point_consistency"
)
```

---

## 📁 Documentation Files

| File | Purpose | Audience |
|------|---------|----------|
| `STATISTICAL_VALIDATION_REPORT.md` | Full technical report (50+ pages) | Data scientists |
| `VALIDATION_EXECUTIVE_SUMMARY.md` | Business summary (10 pages) | Stakeholders |
| `README_VALIDATION.md` | Complete guide | Developers |
| `VALIDATION_QUICK_REFERENCE.md` | This card | Everyone |

---

## 🎯 Next Steps

### Phase 1: Today
- ✅ Use braking_consistency for coaching
- ✅ Show percentile rankings
- ✅ Track progress over time

### Phase 2: 3-6 months
- Standardize telemetry collection
- Pool data from 3-5 races (n=50+)
- Validate 2-3 additional metrics

### Phase 3: 6-12 months
- Implement corner-level telemetry
- Build hierarchical models
- Enable predictive recommendations

---

## ⚠️ Key Warnings

1. **DO NOT** use unvalidated metrics for coaching
2. **DO NOT** build predictive models with n=16
3. **DO NOT** make causal claims from correlations
4. **ALWAYS** include statistical disclaimers

---

## 📞 Support

- **Technical details**: `STATISTICAL_VALIDATION_REPORT.md`
- **Implementation**: `safe_coaching_implementation.py`
- **Questions**: See `README_VALIDATION.md` FAQ section

---

**Status**: ✅ PRODUCTION READY (braking_consistency only)
**Confidence**: HIGH (for overfitting diagnosis), MEDIUM (for validation)
**Version**: 1.0 (2025-11-10)
