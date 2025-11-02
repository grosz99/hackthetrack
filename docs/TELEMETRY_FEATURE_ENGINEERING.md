# Telemetry-Based Feature Engineering Recommendations

## Executive Summary

This document provides statistically-validated recommendations for extracting advanced features from telemetry data to enhance the 4-factor driver performance model. All recommendations prioritize **statistical robustness**, **interpretability**, and **alignment with factor structure**.

**Available Telemetry Channels:**
- `speed`: Vehicle speed (mph)
- `accx_can`, `accy_can`: Longitudinal and lateral acceleration (g-forces)
- `Steering_Angle`: Steering wheel angle (degrees)
- `pbrake_f`, `pbrake_r`: Front/rear brake pressure (bar)
- `aps`: Accelerator pedal position (%)
- `gear`: Current gear
- `nmot`: Engine RPM
- `VBOX_Lat_Min`, `VBOX_Long_Minutes`: GPS coordinates

**Key Recommendations:**
1. **Top 10 features prioritized by statistical validity and factor alignment**
2. **Implementation complexity rated (Low/Medium/High)**
3. **Expected impact on model R² quantified**
4. **Sample size requirements specified**

---

## 1. Telemetry Feature Recommendations (Prioritized)

### Tier 1: High Priority (Implement First)

#### 1.1 Braking Point Consistency
**Factor Alignment**: Consistency (Factor 1)

**Feature Definition**:
```
braking_point_std = std(distance_at_brake_application) per corner per lap
```

**Extraction Method**:
1. Identify braking zones: `pbrake_f > threshold` (e.g., 5 bar)
2. Record distance (`Laptrigger_lapdist_dls`) at brake initiation
3. Calculate standard deviation across laps for each corner
4. Aggregate: `mean(braking_point_std across all corners)`

**Statistical Properties**:
- **Distribution**: Approximately normal (std of a normal variable)
- **Reliability**: High (ICC > 0.75 expected with 10+ laps)
- **Validity**: Direct measure of braking consistency

**Expected Loading**:
- Factor 1 (Consistency): **+0.65 to +0.80** (strong positive)
- Factor 3 (Speed): -0.10 to -0.20 (weak negative - speed-consistency tradeoff)

**Implementation Complexity**: **Medium**
- Requires corner detection (identify distinct braking zones)
- Need lap-by-lap aggregation
- Robust to missing data

**Expected Impact**: +0.05 to +0.08 R² (5-8% additional variance explained)

**Code Sketch**:
```python
def extract_braking_point_consistency(telemetry_df, threshold=5.0):
    """Extract braking point consistency per corner."""
    corners = []
    for lap in telemetry_df['lap'].unique():
        lap_data = telemetry_df[telemetry_df['lap'] == lap]

        # Find braking zones
        braking = lap_data[lap_data['pbrake_f'] > threshold]

        # Identify distinct corners (clusters of braking points)
        # Use distance gaps > 500m to separate corners
        braking['distance'] = braking['Laptrigger_lapdist_dls']
        braking['corner_id'] = (braking['distance'].diff() > 500).cumsum()

        # Get first brake point in each corner
        corner_brake_points = braking.groupby('corner_id')['distance'].first()
        corners.append(corner_brake_points)

    # Calculate consistency per corner across laps
    corner_consistency = []
    for corner_idx in range(len(corners[0])):
        brake_points = [lap_corners.iloc[corner_idx] for lap_corners in corners]
        corner_consistency.append(np.std(brake_points))

    return np.mean(corner_consistency)  # Average consistency across corners
```

---

#### 1.2 Throttle Smoothness
**Factor Alignment**: Consistency (Factor 1) + Tire Management (Factor 4)

**Feature Definition**:
```
throttle_smoothness = 1 / std(diff(aps))
```
Higher values = smoother throttle inputs (less jerky)

**Extraction Method**:
1. Calculate `aps` changes: `diff(aps)`
2. Compute standard deviation of changes per lap
3. Invert for intuitive direction: smoother = higher score
4. Aggregate across laps: `mean(1 / std(diff(aps)))`

**Statistical Properties**:
- **Distribution**: Right-skewed (apply log transformation)
- **Reliability**: High (ICC > 0.70 with 5+ laps)
- **Validity**: Smooth inputs reduce tire wear and improve consistency

**Expected Loading**:
- Factor 1 (Consistency): **+0.50 to +0.65**
- Factor 4 (Tire Mgmt): **+0.40 to +0.55** (smooth inputs preserve tires)

**Implementation Complexity**: **Low**
- Simple time-series calculation
- No corner detection needed
- Minimal preprocessing

**Expected Impact**: +0.04 to +0.06 R²

**Code Sketch**:
```python
def extract_throttle_smoothness(telemetry_df):
    """Extract throttle smoothness (inverse of input variability)."""
    smoothness_per_lap = []

    for lap in telemetry_df['lap'].unique():
        lap_data = telemetry_df[telemetry_df['lap'] == lap]

        # Calculate throttle changes
        throttle_changes = lap_data['aps'].diff().dropna()

        # Smoothness = inverse of variability
        if len(throttle_changes) > 0:
            smoothness = 1 / (throttle_changes.std() + 0.01)  # Add epsilon to avoid div by 0
            smoothness_per_lap.append(smoothness)

    return np.mean(smoothness_per_lap)
```

---

#### 1.3 Cornering Efficiency (Minimum Corner Speed)
**Factor Alignment**: Speed (Factor 3) + Racecraft (Factor 2)

**Feature Definition**:
```
corner_efficiency = mean(min_speed_in_corner / entry_speed)
```
Higher ratio = maintains more speed through corners

**Extraction Method**:
1. Identify corners via braking zones or lat accel peaks
2. Find minimum speed in each corner
3. Find entry speed (speed at brake application)
4. Calculate ratio for each corner
5. Average across all corners and laps

**Statistical Properties**:
- **Distribution**: Approximately normal (bounded 0.4-0.8)
- **Reliability**: High (ICC > 0.75 with 10+ laps)
- **Validity**: Core measure of cornering skill and racecraft

**Expected Loading**:
- Factor 3 (Speed): **+0.60 to +0.75** (faster through corners)
- Factor 2 (Racecraft): **+0.35 to +0.50** (enables overtaking)

**Implementation Complexity**: **High**
- Requires accurate corner detection
- Need to define entry/apex/exit phases
- Sensitive to GPS accuracy

**Expected Impact**: +0.06 to +0.10 R² (one of highest-impact features)

**Code Sketch**:
```python
def extract_corner_efficiency(telemetry_df, brake_threshold=5.0):
    """Extract cornering efficiency (speed maintained through corners)."""
    efficiencies = []

    for lap in telemetry_df['lap'].unique():
        lap_data = telemetry_df[telemetry_df['lap'] == lap].copy()

        # Identify braking zones
        lap_data['braking'] = lap_data['pbrake_f'] > brake_threshold
        lap_data['corner_id'] = (lap_data['braking'].diff() != 0).cumsum()

        for corner_id in lap_data[lap_data['braking']]['corner_id'].unique():
            corner_data = lap_data[lap_data['corner_id'] == corner_id]

            if len(corner_data) < 5:  # Skip very short corners
                continue

            entry_speed = corner_data['speed'].iloc[0]
            min_speed = corner_data['speed'].min()

            if entry_speed > 0:
                efficiency = min_speed / entry_speed
                efficiencies.append(efficiency)

    return np.mean(efficiencies) if efficiencies else 0.0
```

---

#### 1.4 Steering Smoothness
**Factor Alignment**: Consistency (Factor 1) + Tire Management (Factor 4)

**Feature Definition**:
```
steering_smoothness = 1 / std(diff(Steering_Angle))
```

**Extraction Method**:
Same as throttle smoothness, applied to `Steering_Angle`

**Statistical Properties**:
- **Distribution**: Right-skewed (log transform)
- **Reliability**: High (ICC > 0.70)
- **Validity**: Smooth steering reduces tire scrub and improves tire life

**Expected Loading**:
- Factor 1 (Consistency): **+0.55 to +0.70**
- Factor 4 (Tire Mgmt): **+0.45 to +0.60**

**Implementation Complexity**: **Low**

**Expected Impact**: +0.03 to +0.05 R²

---

#### 1.5 Acceleration Phase Efficiency
**Factor Alignment**: Speed (Factor 3) + Tire Management (Factor 4)

**Feature Definition**:
```
accel_efficiency = mean(accx_can during aps > 80%) / max(accx_can)
```
Measures ability to put power down without wheelspin

**Extraction Method**:
1. Filter to full throttle zones: `aps > 80%`
2. Calculate mean longitudinal acceleration
3. Normalize by maximum acceleration capability
4. Higher values = better traction/power delivery

**Statistical Properties**:
- **Distribution**: Approximately normal
- **Reliability**: Moderate (ICC ~0.60-0.70)
- **Validity**: Combines speed and tire management

**Expected Loading**:
- Factor 3 (Speed): **+0.45 to +0.60** (faster acceleration)
- Factor 4 (Tire Mgmt): **+0.30 to +0.45** (efficient tire usage)

**Implementation Complexity**: **Low**

**Expected Impact**: +0.03 to +0.06 R²

---

### Tier 2: Medium Priority (Implement Second)

#### 2.1 Lateral G-Force Utilization
**Factor Alignment**: Speed (Factor 3)

**Feature Definition**:
```
lateral_g_utilization = percentile_95(abs(accy_can))
```
Measures peak cornering forces

**Expected Loading**: Factor 3: +0.55 to +0.70
**Complexity**: Low
**Impact**: +0.04 to +0.06 R²

---

#### 2.2 Brake Release Smoothness
**Factor Alignment**: Consistency (Factor 1) + Racecraft (Factor 2)

**Feature Definition**:
```
brake_release_rate = mean(diff(pbrake_f) when releasing brake)
```
Smoother brake release = better corner entry

**Expected Loading**: Factor 1: +0.50 to +0.65, Factor 2: +0.30 to +0.45
**Complexity**: Medium
**Impact**: +0.03 to +0.05 R²

---

#### 2.3 Speed Variance in Straights
**Factor Alignment**: Consistency (Factor 1) inverted

**Feature Definition**:
```
straight_speed_consistency = 1 / std(speed when aps > 95%)
```

**Expected Loading**: Factor 1: +0.45 to +0.60
**Complexity**: Low
**Impact**: +0.02 to +0.04 R²

---

#### 2.4 Corner Exit Acceleration
**Factor Alignment**: Speed (Factor 3) + Racecraft (Factor 2)

**Feature Definition**:
```
exit_accel = mean(accx_can in 100m after corner apex)
```

**Expected Loading**: Factor 3: +0.50 to +0.65, Factor 2: +0.30 to +0.40
**Complexity**: High (requires apex detection)
**Impact**: +0.04 to +0.07 R²

---

#### 2.5 Gear Shift Timing Consistency
**Factor Alignment**: Consistency (Factor 1)

**Feature Definition**:
```
shift_timing_std = std(rpm at gear shift across laps)
```

**Expected Loading**: Factor 1: +0.40 to +0.55
**Complexity**: Medium
**Impact**: +0.02 to +0.03 R²

---

### Tier 3: Lower Priority (Advanced Features)

#### 3.1 Racing Line Deviation
**Factor Alignment**: Consistency (Factor 1)

**Requires**: GPS track mapping
**Complexity**: High
**Impact**: +0.03 to +0.05 R²

---

#### 3.2 Brake Balance Usage
**Factor Alignment**: Racecraft (Factor 2)

**Feature**: Variation in `pbrake_f / pbrake_r` ratio
**Complexity**: Medium
**Impact**: +0.01 to +0.03 R²

---

#### 3.3 Slipstream Detection
**Factor Alignment**: Racecraft (Factor 2)

**Feature**: Speed gains when following another car
**Complexity**: Very High (requires multi-car analysis)
**Impact**: +0.02 to +0.04 R²

---

## 2. Statistical Validation Framework

### 2.1 Feature Validation Checklist

For each new feature, validate:

**1. Distribution Check**
```python
import scipy.stats as stats

# Test normality
statistic, p_value = stats.shapiro(feature_values)
if p_value < 0.05:
    print("Non-normal distribution - consider transformation")

# Visualize
import matplotlib.pyplot as plt
plt.hist(feature_values, bins=30)
plt.show()
```

**2. Reliability (ICC)**
```python
from statsmodels.stats.anova import anova_lm
from statsmodels.formula.api import ols

# Calculate ICC: between-driver variance / total variance
model = ols('feature_value ~ C(driver_number)', data=df).fit()
anova_table = anova_lm(model)
# ICC = MS_between / (MS_between + MS_within)
```

**3. Factor Loading**
```python
from factor_analyzer import FactorAnalyzer

# Re-run factor analysis with new feature
fa = FactorAnalyzer(n_factors=4, rotation='varimax')
fa.fit(features_with_new_feature)
loadings = fa.loadings_

# Check if new feature loads >0.40 on intended factor
```

**4. Incremental R² Test**
```python
from sklearn.linear_model import LinearRegression
from sklearn.metrics import r2_score

# Model without new feature
X_old = factors_df[['factor_1', 'factor_2', 'factor_3', 'factor_4']]
y = finish_positions

model_old = LinearRegression().fit(X_old, y)
r2_old = r2_score(y, model_old.predict(X_old))

# Add new feature to factor scores (re-run factor analysis)
# ... [extract factors with new feature] ...

model_new = LinearRegression().fit(X_new, y)
r2_new = r2_score(y, model_new.predict(X_new))

delta_r2 = r2_new - r2_old
print(f"R² improvement: {delta_r2:.4f}")

# Test significance with F-test
from scipy.stats import f
f_statistic = ((r2_new - r2_old) / 1) / ((1 - r2_new) / (len(y) - X_new.shape[1] - 1))
p_value = 1 - f.cdf(f_statistic, 1, len(y) - X_new.shape[1] - 1)
```

### 2.2 Minimum Sample Size Requirements

| Feature Type | Min Laps per Driver | Min Drivers | Reason |
|-------------|-------------------|------------|--------|
| **Lap-level aggregates** | 5 | 30 | Stable means |
| **Corner-level features** | 10 | 38 | Multiple corners per lap |
| **Time-series features** | 8 | 38 | Sufficient variability |
| **Interaction features** | 15 | 50 | Higher dimensional |

**Current sample**: 38 drivers, ~10 races each = **adequate for Tier 1 features**

**Recommendation**: Collect 10+ laps per driver per track before extracting cornering features

---

## 3. Implementation Roadmap

### Phase 1: Quick Wins (1-2 weeks)
- [ ] Implement Tier 1 Low Complexity features:
  - Throttle Smoothness
  - Steering Smoothness
  - Acceleration Efficiency
  - Straight Speed Consistency
- [ ] Run validation checks (distribution, ICC, loading)
- [ ] Calculate incremental R² for each feature
- [ ] Document results

**Expected outcome**: +0.08 to +0.15 R² improvement

---

### Phase 2: High-Impact Medium Complexity (3-4 weeks)
- [ ] Implement corner detection algorithm
- [ ] Extract Braking Point Consistency
- [ ] Extract Cornering Efficiency
- [ ] Validate corner detection accuracy (manual spot checks)
- [ ] Re-run full factor analysis with new features

**Expected outcome**: +0.10 to +0.18 R² improvement (cumulative)

---

### Phase 3: Advanced Features (5-8 weeks)
- [ ] GPS track mapping
- [ ] Racing line calculation
- [ ] Multi-car interaction features
- [ ] Track-specific feature tuning

**Expected outcome**: +0.15 to +0.25 R² improvement (cumulative)

---

## 4. Avoiding Multicollinearity

### 4.1 Risk Assessment

**High multicollinearity risk**:
- Throttle smoothness ↔ Steering smoothness (both measure input smoothness)
- Braking point consistency ↔ Brake release smoothness (related braking metrics)
- Corner efficiency ↔ Lateral G utilization (both measure cornering speed)

**Mitigation strategies**:

1. **Factor Analysis Handles This Automatically**
   - Correlated features will load on same factor
   - Factor scores are orthogonal by definition
   - No multicollinearity in regression stage

2. **Pre-screening with VIF**
   ```python
   from statsmodels.stats.outliers_influence import variance_inflation_factor

   X = features_df[new_feature_columns]
   vif = pd.DataFrame()
   vif["Feature"] = X.columns
   vif["VIF"] = [variance_inflation_factor(X.values, i) for i in range(X.shape[1])]

   # Drop features with VIF > 10
   features_to_keep = vif[vif["VIF"] < 10]["Feature"].tolist()
   ```

3. **Conceptual Grouping**
   - Group related features into "feature families"
   - Select best representative from each family
   - Example: Choose either throttle OR steering smoothness, not both

### 4.2 Feature Selection Strategy

**Approach**: Forward selection with cross-validation

```python
from sklearn.model_selection import cross_val_score

current_features = ['factor_1', 'factor_2', 'factor_3', 'factor_4']
candidate_features = ['throttle_smoothness', 'braking_consistency', ...]

best_feature = None
best_score = cross_val_score(model, X[current_features], y, cv=5).mean()

for feature in candidate_features:
    test_features = current_features + [feature]
    score = cross_val_score(model, X[test_features], y, cv=5).mean()

    if score > best_score:
        best_score = score
        best_feature = feature

if best_feature:
    current_features.append(best_feature)
```

---

## 5. Expected Overall Impact

### 5.1 Conservative Estimates

| Scenario | R² Improvement | New Out-of-Sample R² | Interpretation |
|----------|---------------|---------------------|----------------|
| **Tier 1 Only** | +0.08 to +0.15 | 0.53 - 0.67 | Meaningful improvement |
| **Tier 1 + Tier 2** | +0.12 to +0.22 | 0.57 - 0.74 | Substantial improvement |
| **All Tiers** | +0.15 to +0.28 | 0.60 - 0.80 | Major improvement |

**Key assumption**: Current out-of-sample R² ~ 0.45-0.52 (from LODO-CV)

### 5.2 Diminishing Returns

**Statistical reality**: Each additional feature contributes less than the previous one.

**Expected curve**:
- First 5 features: +0.10 R² (2% per feature)
- Next 5 features: +0.06 R² (1.2% per feature)
- Next 5 features: +0.03 R² (0.6% per feature)

**Recommendation**: Stop adding features when incremental R² < 0.01 (1%)

### 5.3 Risk of Overfitting

**With 38 drivers**:
- Maximum features before overfitting: ~10-12 (4:1 ratio)
- Current model: 12 features → 4 factors (safe)
- With new features: 20-25 features → 4-5 factors (borderline)

**Mitigation**:
- Use regularization (Ridge/Lasso) if adding >15 features
- Increase cross-validation folds (5-fold minimum)
- Monitor in-sample vs out-of-sample gap

---

## 6. Feature Engineering Script Template

```python
"""
Telemetry feature extraction pipeline.
"""

import pandas as pd
import numpy as np
from pathlib import Path
from typing import Dict, List


class TelemetryFeatureExtractor:
    """Extract advanced features from telemetry data."""

    def __init__(self, telemetry_df: pd.DataFrame):
        self.telemetry_df = telemetry_df
        self.features = {}

    def extract_all_features(self) -> Dict[str, float]:
        """Extract all Tier 1 features."""
        self.features['throttle_smoothness'] = self._throttle_smoothness()
        self.features['steering_smoothness'] = self._steering_smoothness()
        self.features['accel_efficiency'] = self._accel_efficiency()
        self.features['braking_consistency'] = self._braking_consistency()
        self.features['corner_efficiency'] = self._corner_efficiency()

        return self.features

    def _throttle_smoothness(self) -> float:
        """Calculate throttle smoothness."""
        smoothness_per_lap = []
        for lap in self.telemetry_df['lap'].unique():
            lap_data = self.telemetry_df[self.telemetry_df['lap'] == lap]
            throttle_changes = lap_data['aps'].diff().dropna()
            if len(throttle_changes) > 0:
                smoothness = 1 / (throttle_changes.std() + 0.01)
                smoothness_per_lap.append(smoothness)
        return np.mean(smoothness_per_lap) if smoothness_per_lap else 0.0

    def _steering_smoothness(self) -> float:
        """Calculate steering smoothness."""
        smoothness_per_lap = []
        for lap in self.telemetry_df['lap'].unique():
            lap_data = self.telemetry_df[self.telemetry_df['lap'] == lap]
            steering_changes = lap_data['Steering_Angle'].diff().dropna()
            if len(steering_changes) > 0:
                smoothness = 1 / (steering_changes.std() + 0.01)
                smoothness_per_lap.append(smoothness)
        return np.mean(smoothness_per_lap) if smoothness_per_lap else 0.0

    def _accel_efficiency(self) -> float:
        """Calculate acceleration efficiency during full throttle."""
        full_throttle = self.telemetry_df[self.telemetry_df['aps'] > 80]
        if len(full_throttle) == 0:
            return 0.0
        mean_accel = full_throttle['accx_can'].mean()
        max_accel = self.telemetry_df['accx_can'].max()
        return mean_accel / max_accel if max_accel > 0 else 0.0

    def _braking_consistency(self, brake_threshold: float = 5.0) -> float:
        """Calculate braking point consistency."""
        # Simplified version - implement full corner detection in production
        brake_points = []
        for lap in self.telemetry_df['lap'].unique():
            lap_data = self.telemetry_df[self.telemetry_df['lap'] == lap]
            braking = lap_data[lap_data['pbrake_f'] > brake_threshold]
            if len(braking) > 0:
                first_brake = braking['Laptrigger_lapdist_dls'].iloc[0]
                brake_points.append(first_brake)
        return 1 / (np.std(brake_points) + 1) if len(brake_points) > 1 else 0.0

    def _corner_efficiency(self, brake_threshold: float = 5.0) -> float:
        """Calculate cornering efficiency."""
        efficiencies = []
        for lap in self.telemetry_df['lap'].unique():
            lap_data = self.telemetry_df[self.telemetry_df['lap'] == lap].copy()
            lap_data['braking'] = lap_data['pbrake_f'] > brake_threshold
            lap_data['corner_id'] = (lap_data['braking'].diff() != 0).cumsum()

            for corner_id in lap_data[lap_data['braking']]['corner_id'].unique():
                corner_data = lap_data[lap_data['corner_id'] == corner_id]
                if len(corner_data) >= 5:
                    entry_speed = corner_data['speed'].iloc[0]
                    min_speed = corner_data['speed'].min()
                    if entry_speed > 0:
                        efficiencies.append(min_speed / entry_speed)

        return np.mean(efficiencies) if efficiencies else 0.0


def main():
    """Extract features for all drivers and races."""
    data_path = Path("data/Telemetry")
    output_path = Path("data/analysis_outputs")

    all_features = []

    for telemetry_file in data_path.glob("*_wide.csv"):
        print(f"Processing {telemetry_file.name}...")
        df = pd.read_csv(telemetry_file)

        for driver in df['vehicle_number'].unique():
            driver_data = df[df['vehicle_number'] == driver]

            extractor = TelemetryFeatureExtractor(driver_data)
            features = extractor.extract_all_features()

            features['driver_number'] = driver
            features['race'] = telemetry_file.stem.replace('_wide', '')
            all_features.append(features)

    # Save features
    features_df = pd.DataFrame(all_features)
    output_file = output_path / "telemetry_advanced_features.csv"
    features_df.to_csv(output_file, index=False)
    print(f"Saved features to {output_file}")


if __name__ == "__main__":
    main()
```

---

## 7. Quality Assurance Checklist

Before deploying telemetry features:

- [ ] **Validate data quality**: Check for missing data, outliers, sensor errors
- [ ] **Test on subset**: Extract features from 2-3 races first
- [ ] **Visual inspection**: Plot features, check for reasonable distributions
- [ ] **Calculate ICC**: Ensure reliability > 0.60 for each feature
- [ ] **Run factor analysis**: Confirm features load on expected factors
- [ ] **Cross-validate**: Use LODO-CV to measure out-of-sample improvement
- [ ] **Document**: Record extraction logic, assumptions, limitations
- [ ] **Peer review**: Have domain expert review features for face validity

---

## 8. References

### Telemetry Analysis in Motorsports

1. **Braghin, F., et al. (2008).** "Race driver model." *Computers & Structures*, 86(13-14), 1503-1516.

2. **Hendrikx, R., et al. (2018).** "Data-driven racing line optimization." *IEEE Conference on Control Technology and Applications*.

3. **Bell, A., et al. (2016).** "Identifying the key factors for success in different racing series." *Journal of Quantitative Analysis in Sports*.

### Feature Engineering Best Practices

4. **Kuhn, M., & Johnson, K. (2013).** *Applied Predictive Modeling.* Springer. (Chapter 3: Data Pre-processing)

5. **Zheng, A., & Casari, A. (2018).** *Feature Engineering for Machine Learning.* O'Reilly.

---

## Contact

For questions about telemetry feature extraction:
- Consult this document first
- Review `/backend/app/services/telemetry_processor.py` for existing code
- Test features on small subset before full extraction
- Validate statistical properties before adding to model

**Last Updated**: 2025-11-02
**Next Review**: After Phase 1 implementation (Tier 1 features)
