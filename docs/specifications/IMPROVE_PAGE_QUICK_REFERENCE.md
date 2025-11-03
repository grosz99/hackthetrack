# Improve Page: Developer Quick Reference

## 🚨 Critical Rules (DO NOT VIOLATE)

### ❌ NEVER Do This
```python
# DON'T: Convert RepTrak to z-score with fixed σ
z_score = (reptrak_score - 50) / 15  # WRONG - σ varies by factor

# DON'T: Use unweighted distance on percentile scale
distance = sqrt(sum((adjusted[i] - driver[i])**2))  # WRONG - ignores model weights

# DON'T: Show predictions without confidence intervals
predicted_finish = 8.5  # INCOMPLETE - where's the uncertainty?

# DON'T: Apply model to extreme adjustments without warnings
if adjusted_skills_are_crazy():
    pass  # WRONG - must detect and warn about extrapolation
```

### ✅ ALWAYS Do This
```python
# DO: Use empirical percentile-to-z conversion
z_score = predictor.reptrak_to_z_score(reptrak_score, factor_name)

# DO: Use model-weighted distance in z-score space
similarity = predictor.find_similar_drivers(adjusted_z_scores)

# DO: Show predictions with uncertainty
result = predictor.predict_finish_with_uncertainty(adjusted_z_scores)
print(f"{result.predicted_finish:.1f} ± {result.confidence_interval_upper - result.predicted_finish:.1f}")

# DO: Check for extrapolation and warn users
if result.is_extrapolating:
    show_warning(result.warning_message)
```

---

## 📊 Data Flow

```
User Adjusts Skills (RepTrak 0-100)
    ↓
Convert to Z-Scores (Empirical Method)
    ↓
Predict Finish Position (Linear Model)
    ↓
Bootstrap for Confidence Interval (1000 iterations)
    ↓
Check for Extrapolation (Distance to Training Data)
    ↓
Find Similar Drivers (Model-Weighted Distance)
    ↓
Display Results + Uncertainty + Warnings
```

---

## 🔢 Key Constants

```python
MODEL_COEFFICIENTS = {
    'speed': 6.079,              # Highest impact
    'consistency': 3.792,         # Second highest
    'racecraft': 1.943,           # Third
    'tire_management': 1.237,     # Fourth
    'intercept': 13.01
}

BOOTSTRAP_ITERATIONS = 1000      # For confidence intervals
CONFIDENCE_LEVEL = 0.95          # 95% CI
DEFAULT_POINTS_BUDGET = 5        # Total adjustable points
```

---

## 🧮 Core Formulas

### Finish Position Prediction
```python
predicted_finish = (
    13.01
    + 6.079 × z_speed
    + 3.792 × z_consistency
    + 1.943 × z_racecraft
    + 1.237 × z_tire_mgmt
)
```

### Model-Weighted Distance (for similarity)
```python
weights = [6.079, 3.792, 1.943, 1.237]  # Model coefficients
distance = sqrt(sum(w² × (z_adjusted - z_driver)² for w, z in zip(weights, z_scores)))
```

### Similarity Score (0-100 scale)
```python
similarity = 100 × exp(-distance / 5)
```

---

## 🎯 API Usage Examples

### Basic Prediction
```python
from improve_page_predictor import ImprovePagePredictor

# Initialize
predictor = ImprovePagePredictor(
    training_data_path="data/analysis_outputs/tier1_factor_scores.csv"
)

# User's adjusted RepTrak scores
adjusted_reptrak = {
    'speed': 68.0,
    'consistency': 57.0,
    'racecraft': 60.0,
    'tire_management': 50.0
}

# Convert to z-scores
adjusted_z = {
    factor: predictor.reptrak_to_z_score(score, factor)
    for factor, score in adjusted_reptrak.items()
}

# Predict with uncertainty
result = predictor.predict_finish_with_uncertainty(adjusted_z)

print(f"Predicted: {result.predicted_finish:.1f}")
print(f"95% CI: [{result.confidence_interval_lower:.1f}, {result.confidence_interval_upper:.1f}]")
print(f"Confidence: {result.confidence_level}")
if result.warning_message:
    print(result.warning_message)
```

### Find Similar Drivers
```python
similar_drivers = predictor.find_similar_drivers(adjusted_z, top_n=3)

for driver in similar_drivers:
    print(f"{driver.driver_name}: {driver.similarity_score:.1f}% similar")
    print(f"  Predicted finish: {driver.predicted_finish:.1f}")
    print(f"  Skill gaps:")
    for factor, diff in driver.skill_differences.items():
        print(f"    {factor}: {diff:+.2f} z-scores")
```

### Optimal Allocation
```python
current_reptrak = {
    'speed': 65.0,
    'consistency': 55.0,
    'racecraft': 60.0,
    'tire_management': 50.0
}

optimal = predictor.recommend_optimal_allocation(current_reptrak, budget=5)

print("Recommended allocation:")
for factor, points in optimal.items():
    if points > 0:
        print(f"  {factor}: +{points} points")
```

---

## 🎨 UI/UX Guidelines

### Confidence Level Display
```python
if result.confidence_level == 'high':
    color = 'green'
    icon = '✓'
    message = "High confidence - adjusted skills similar to observed drivers"
elif result.confidence_level == 'medium':
    color = 'yellow'
    icon = '⚠'
    message = "Medium confidence - some uncertainty in prediction"
else:  # low
    color = 'red'
    icon = '⚠'
    message = "Low confidence - adjusted skills far from observed data"
```

### Prediction Display Format
```
┌─────────────────────────────────────────────┐
│ Predicted Finish: 8.5 ± 2.1 positions      │
│ 95% Confidence: [6.4, 10.6]                │
│                                             │
│ Current Avg Finish: 12.3                   │
│ Predicted Improvement: 3.8 positions ↑     │
│                                             │
│ Confidence: High ✓                         │
│ These skills are similar to observed       │
│ drivers. Prediction is reliable.           │
└─────────────────────────────────────────────┘
```

### Extrapolation Warning
```
┌─────────────────────────────────────────────┐
│ ⚠️ Warning: High Uncertainty                │
│                                             │
│ These adjusted skills are far from         │
│ observed drivers. Predictions are highly   │
│ uncertain and should be interpreted with   │
│ caution.                                   │
│                                             │
│ Consider adjusting skills closer to your   │
│ current levels for more reliable           │
│ predictions.                               │
└─────────────────────────────────────────────┘
```

---

## 🧪 Testing Checklist

### Unit Tests
- [ ] `reptrak_to_z_score()` returns correct z-scores for known percentiles
- [ ] `predict_finish_with_uncertainty()` produces CIs that contain true values 95% of time
- [ ] `find_similar_drivers()` ranks by model-weighted distance
- [ ] `recommend_optimal_allocation()` prioritizes high-coefficient factors
- [ ] `_check_extrapolation()` detects when adjusted skills are far from training data

### Integration Tests
- [ ] End-to-end flow from RepTrak input to prediction output
- [ ] Bootstrap produces consistent results (seed-controlled)
- [ ] Confidence intervals widen appropriately with extrapolation

### Edge Cases
- [ ] RepTrak scores at boundaries (0, 100)
- [ ] All factors adjusted to maximum
- [ ] Single factor adjusted, others unchanged
- [ ] Negative z-scores handled correctly
- [ ] Empty training data raises informative error

---

## 🐛 Common Pitfalls

### Pitfall #1: Forgetting to Apply Reflection
```python
# Factor scores 1, 2, 3 need reflection (multiply by -1)
# This is already done in __init__, but if you reload raw data:
for col in ['factor_1_score', 'factor_2_score', 'factor_3_score']:
    df[col] *= -1  # MUST DO THIS
```

### Pitfall #2: Mixing RepTrak and Z-Score Scales
```python
# RepTrak is 0-100 percentile scale
# Z-scores are standardized, mean=0, σ≈1

# BAD: Comparing RepTrak to z-scores directly
if reptrak_score > z_score:  # WRONG - different scales!

# GOOD: Convert before comparing
z_from_reptrak = predictor.reptrak_to_z_score(reptrak_score, factor)
if z_from_reptrak > z_score:  # Correct
```

### Pitfall #3: Not Handling NaN/Missing Values
```python
# Some drivers may lack telemetry features
# Filter before using:
drivers_with_telemetry = df[df['steering_smoothness'].notna()]
```

### Pitfall #4: Ignoring Bootstrap Randomness
```python
# Bootstrap predictions vary run-to-run
# For reproducible testing, set seed:
np.random.seed(42)
result = predictor.predict_finish_with_uncertainty(z_scores)
```

---

## 📏 Validation Metrics

### Expected Ranges

| Metric | Typical Value | Concern Threshold |
|--------|--------------|-------------------|
| Confidence Interval Width | 2-4 positions | > 6 positions |
| Extrapolation Severity | < 1.5 | > 2.0 |
| Similarity Score (top match) | > 80% | < 60% |
| Bootstrap Std Dev | 0.5-1.5 | > 3.0 |

### Statistical Properties

```python
# Bootstrap predictions should be roughly normal
predictions = [predict() for _ in range(1000)]
assert scipy.stats.normaltest(predictions).pvalue > 0.05

# Confidence intervals should contain true values 95% of time
coverage = sum(
    ci_lower <= true_value <= ci_upper
    for ci_lower, true_value, ci_upper in test_cases
) / len(test_cases)
assert 0.93 <= coverage <= 0.97  # Allow some sampling variation
```

---

## 🔗 Related Files

| File | Purpose |
|------|---------|
| `IMPROVE_PAGE_STATISTICAL_VALIDATION.md` | Full statistical analysis (18,500 words) |
| `IMPROVE_PAGE_CORRECTED_IMPLEMENTATION.py` | Production implementation |
| `IMPROVE_PAGE_SUMMARY.md` | Executive summary for stakeholders |
| `IMPROVE_PAGE_QUICK_REFERENCE.md` | This file |

---

## 💡 Pro Tips

### Performance Optimization
```python
# Bootstrap is slow (1000 iterations)
# Cache results for same adjusted_z_scores:
from functools import lru_cache

@lru_cache(maxsize=128)
def predict_cached(adjusted_z_tuple):
    adjusted_z = dict(zip(['speed', 'consistency', 'racecraft', 'tire_management'], adjusted_z_tuple))
    return predictor.predict_finish_with_uncertainty(adjusted_z)

# Use with tuple (hashable) instead of dict
z_tuple = tuple(adjusted_z.values())
result = predict_cached(z_tuple)
```

### Debugging
```python
# Print intermediate values
print(f"RepTrak: {reptrak_score}")
print(f"Z-score: {predictor.reptrak_to_z_score(reptrak_score, 'speed')}")
print(f"Predicted: {result.predicted_finish}")
print(f"CI width: {result.confidence_interval_upper - result.confidence_interval_lower}")
print(f"Extrapolating: {result.is_extrapolating}")
```

### User Feedback Loop
```python
# Log predictions for later validation
log_prediction(
    driver_id=driver_id,
    adjusted_skills=adjusted_reptrak,
    predicted_finish=result.predicted_finish,
    confidence_interval=(result.confidence_interval_lower, result.confidence_interval_upper),
    timestamp=datetime.now()
)

# Later, compare to actual performance
validate_predictions()
```

---

## 🆘 Troubleshooting

### Issue: Predictions seem off
**Check:**
1. Are factor scores reflected correctly? (Factors 1, 2, 3 should be negative → positive)
2. Are you using z-scores (not RepTrak scores) in predict function?
3. Is training data loaded correctly?

### Issue: Confidence intervals are huge
**Check:**
1. Are adjusted skills far from training data? (extrapolation)
2. Is bootstrap using enough iterations? (should be ≥ 1000)
3. Is training data too small? (n < 30 drivers)

### Issue: All drivers look equally similar
**Check:**
1. Are you using model-weighted distance? (not unweighted Euclidean)
2. Are distances in z-score space? (not RepTrak percentile space)
3. Are factor names matching correctly?

---

## 📞 Support

**Statistical questions:** See `IMPROVE_PAGE_STATISTICAL_VALIDATION.md` sections 1-8

**Implementation questions:** Read docstrings in `IMPROVE_PAGE_CORRECTED_IMPLEMENTATION.py`

**Bug reports:** Include:
- Input values (adjusted_reptrak dict)
- Expected output
- Actual output
- Error messages (if any)

---

**Version:** 1.0
**Last Updated:** 2025-11-02
**Status:** ✅ Production Ready
