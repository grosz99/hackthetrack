# Statistical Validation - Circuit Fit Analysis

## 🎯 Goal
**Only use features that ACTUALLY discriminate between performance levels**

Don't build analytics theater. Build features proven to separate winners from mid-pack from back-field.

---

## 📊 Validation Framework

### Performance Groups
Define three groups for comparison:
```python
# Based on finishing position
top_3 = drivers[drivers['finishing_position'] <= 3]
mid_pack = drivers[(drivers['finishing_position'] > 3) & 
                   (drivers['finishing_position'] <= 12)]
back_field = drivers[drivers['finishing_position'] > 12]
```

---

## 🔬 Statistical Tests

### 1. ANOVA (Analysis of Variance)
**Tests**: Do the three groups have significantly different means?

```python
import scipy.stats as stats

def run_anova_test(feature_name, data):
    """
    Test if feature discriminates across performance groups.
    
    Returns p-value: 
    - p < 0.05 = Significant discrimination
    - p >= 0.05 = No discrimination (DROP feature)
    """
    
    top_3 = data[data['performance_group'] == 'top_3'][feature_name]
    mid_pack = data[data['performance_group'] == 'mid_pack'][feature_name]
    back_field = data[data['performance_group'] == 'back_field'][feature_name]
    
    f_statistic, p_value = stats.f_oneway(top_3, mid_pack, back_field)
    
    return {
        'feature': feature_name,
        'f_stat': f_statistic,
        'p_value': p_value,
        'significant': p_value < 0.05
    }
```

**Interpretation:**
- p < 0.01: **Strong evidence** - Feature definitely discriminates
- p < 0.05: **Moderate evidence** - Feature likely discriminates
- p < 0.10: **Weak evidence** - Investigate further
- p >= 0.10: **No evidence** - DROP this feature

---

### 2. Effect Size (Cohen's d)
**Tests**: How MUCH do the groups differ? (statistical significance ≠ practical significance)

```python
import numpy as np

def calculate_effect_size(feature_name, data):
    """
    Calculate Cohen's d between top-3 and mid-pack.
    
    Effect size interpretation:
    - |d| > 0.8: Large effect (KEEP)
    - |d| > 0.5: Medium effect (KEEP)
    - |d| > 0.2: Small effect (INVESTIGATE)
    - |d| <= 0.2: Tiny effect (DROP)
    """
    
    top_3 = data[data['performance_group'] == 'top_3'][feature_name]
    mid_pack = data[data['performance_group'] == 'mid_pack'][feature_name]
    
    # Cohen's d formula
    pooled_std = np.sqrt((top_3.std()**2 + mid_pack.std()**2) / 2)
    cohens_d = (top_3.mean() - mid_pack.mean()) / pooled_std
    
    return {
        'feature': feature_name,
        'cohens_d': cohens_d,
        'top_3_mean': top_3.mean(),
        'mid_pack_mean': mid_pack.mean(),
        'practical_significance': abs(cohens_d) > 0.5
    }
```

**Why both tests?**
- ANOVA tells you IF groups differ
- Effect size tells you HOW MUCH they differ
- Need BOTH for a good feature

---

### 3. Post-Hoc Pairwise Comparisons
**Tests**: Which specific groups differ from each other?

```python
from scipy.stats import ttest_ind

def pairwise_comparisons(feature_name, data):
    """
    Test which pairs of groups are significantly different.
    
    Useful for understanding:
    - Does feature separate winners from everyone?
    - Or just winners from back-field?
    """
    
    top_3 = data[data['performance_group'] == 'top_3'][feature_name]
    mid_pack = data[data['performance_group'] == 'mid_pack'][feature_name]
    back_field = data[data['performance_group'] == 'back_field'][feature_name]
    
    # Three pairwise tests
    top_vs_mid = ttest_ind(top_3, mid_pack)
    top_vs_back = ttest_ind(top_3, back_field)
    mid_vs_back = ttest_ind(mid_pack, back_field)
    
    return {
        'feature': feature_name,
        'top_vs_mid_p': top_vs_mid.pvalue,
        'top_vs_back_p': top_vs_back.pvalue,
        'mid_vs_back_p': mid_vs_back.pvalue,
        'discriminates_top_3': top_vs_mid.pvalue < 0.05,
        'discriminates_mid_pack': mid_vs_back.pvalue < 0.05
    }
```

---

## 🎯 Decision Framework

Combine all tests to make keep/drop decisions:

```python
def evaluate_feature(feature_name, data):
    """
    Complete evaluation of a single feature.
    
    Returns recommendation: KEEP, INVESTIGATE, or DROP
    """
    
    # Run all statistical tests
    anova_result = run_anova_test(feature_name, data)
    effect_size = calculate_effect_size(feature_name, data)
    pairwise = pairwise_comparisons(feature_name, data)
    
    # Decision logic
    if (anova_result['p_value'] < 0.05 and 
        abs(effect_size['cohens_d']) > 0.5):
        recommendation = "KEEP"
        reason = "Strong statistical and practical significance"
        
    elif (anova_result['p_value'] < 0.05 and 
          abs(effect_size['cohens_d']) > 0.2):
        recommendation = "INVESTIGATE"
        reason = "Statistically significant but small effect"
        
    elif anova_result['p_value'] < 0.10:
        recommendation = "INVESTIGATE"
        reason = "Marginally significant - need more data"
        
    else:
        recommendation = "DROP"
        reason = "No evidence of discrimination"
    
    return {
        'feature': feature_name,
        'recommendation': recommendation,
        'reason': reason,
        'anova_p': anova_result['p_value'],
        'effect_size': effect_size['cohens_d'],
        'discriminates_winners': pairwise['discriminates_top_3']
    }
```

---

## 📋 Validation Pipeline

### Step 1: Load Data
```python
import pandas as pd

# Load your processed features from analysis_outputs
features_df = pd.read_csv('data/analysis_outputs/driver_corner_features.csv')

# Add performance groups
def assign_performance_group(position):
    if position <= 3:
        return 'top_3'
    elif position <= 12:
        return 'mid_pack'
    else:
        return 'back_field'

features_df['performance_group'] = features_df['finishing_position'].apply(
    assign_performance_group
)
```

### Step 2: Test All Features
```python
# List of all features to test
features_to_test = [
    'braking_point_vs_winner',
    'entry_speed_vs_winner',
    'apex_speed_vs_winner',
    'exit_speed_vs_winner',
    'throttle_application_point',
    'time_to_full_throttle',
    'brake_pressure_degradation_rate',
    'lap_time_coefficient_of_variation',
    # ... add all your features here
]

# Run validation on all features
results = []
for feature in features_to_test:
    result = evaluate_feature(feature, features_df)
    results.append(result)

# Create summary report
validation_report = pd.DataFrame(results)
```

### Step 3: Generate Report
```python
# Filter to features we should keep
keep_features = validation_report[
    validation_report['recommendation'] == 'KEEP'
].sort_values('effect_size', ascending=False)

# Features to investigate further
investigate_features = validation_report[
    validation_report['recommendation'] == 'INVESTIGATE'
]

# Features to drop
drop_features = validation_report[
    validation_report['recommendation'] == 'DROP'
]

print(f"\n✅ KEEP: {len(keep_features)} features")
print(f"🔍 INVESTIGATE: {len(investigate_features)} features")
print(f"❌ DROP: {len(drop_features)} features")
```

---

## 📊 Example Validation Results

```
Feature Validation Report - Barber R1 2024
===========================================

✅ KEEP (Strong Discrimination):
  1. braking_point_vs_winner        (p=0.002, d=1.24) - Large effect
  2. exit_speed_vs_winner           (p=0.008, d=0.89) - Large effect
  3. apex_speed_vs_winner           (p=0.012, d=0.72) - Medium effect
  4. lap_time_coefficient_of_variation (p=0.019, d=0.63) - Medium effect

🔍 INVESTIGATE (Marginal):
  5. throttle_application_point     (p=0.041, d=0.38) - Small effect
  6. brake_pressure_degradation     (p=0.067, d=0.45) - Marginal significance

❌ DROP (No Discrimination):
  7. steering_angle_variance        (p=0.342, d=0.11) - No evidence
  8. gear_shift_timing              (p=0.581, d=-0.05) - No evidence
```

**Action Items:**
- Use features 1-4 in production system
- Collect more data on features 5-6 before deciding
- Remove features 7-8 from pipeline

---

## 🎯 Corner-Level Validation

Don't just validate features globally - validate per corner:

```python
def validate_corner_features(data, corner_number):
    """
    Test if features discriminate for THIS SPECIFIC CORNER.
    
    Some features may work at Turn 1 but not Turn 5.
    """
    
    corner_data = data[data['corner_number'] == corner_number]
    
    # Test each feature for this corner
    corner_results = []
    for feature in ['entry_speed', 'apex_speed', 'exit_speed']:
        result = evaluate_feature(feature, corner_data)
        result['corner'] = corner_number
        corner_results.append(result)
    
    return pd.DataFrame(corner_results)

# Validate all corners
all_corners = []
for corner in range(1, 18):  # Barber has 17 corners
    corner_validation = validate_corner_features(features_df, corner)
    all_corners.append(corner_validation)

corner_report = pd.concat(all_corners)
```

**Example Output:**
```
Turn 1: entry_speed discriminates (p=0.003), apex_speed does not (p=0.312)
Turn 5: All three speeds discriminate (p<0.01)
Turn 11: Only exit_speed discriminates (p=0.024)
```

**Insight**: Different corners require different coaching focus!

---

## 🔄 Continuous Validation

As you collect more data:

```python
def monitor_feature_drift(feature_name, historical_data, new_data):
    """
    Check if feature's discrimination power changes over time.
    
    Use cases:
    - Track conditions change (wet vs dry)
    - Car setup changes
    - Driver skill improves
    """
    
    historical_p = run_anova_test(feature_name, historical_data)['p_value']
    new_p = run_anova_test(feature_name, new_data)['p_value']
    
    if abs(historical_p - new_p) > 0.10:
        print(f"⚠️ WARNING: {feature_name} discrimination changed!")
        print(f"  Historical p={historical_p:.3f}, New p={new_p:.3f}")
```

---

## 💾 Save Validation Results

```python
# Save full validation report
validation_report.to_csv(
    'data/analysis_outputs/feature_validation_report.csv',
    index=False
)

# Save list of validated features to use in production
validated_features = keep_features['feature'].tolist()
with open('data/analysis_outputs/validated_features.json', 'w') as f:
    json.dump(validated_features, f, indent=2)
```

---

## ✅ Validation Checklist

Before moving to diagnostic engine:

- [ ] Run ANOVA on all features
- [ ] Calculate effect sizes for all features
- [ ] Perform pairwise comparisons
- [ ] Generate keep/investigate/drop decisions
- [ ] Validate corner-by-corner (not just global)
- [ ] Document why each feature was kept or dropped
- [ ] Save validated feature list for production use

---

## 🚨 Common Pitfalls

1. **Multiple Comparisons Problem**: Testing 100 features? Use Bonferroni correction:
   ```python
   adjusted_alpha = 0.05 / num_features_tested
   ```

2. **Small Sample Sizes**: Need at least 10 drivers per group for reliable results

3. **Outliers**: One super-fast/slow driver can skew results:
   ```python
   # Remove outliers beyond 3 standard deviations
   data = data[np.abs(stats.zscore(data[feature])) < 3]
   ```

4. **Correlated Features**: If two features are 90% correlated, pick the more actionable one

---

Ready to build the diagnostic engine? See `04_DIAGNOSTIC_ENGINE.md`
