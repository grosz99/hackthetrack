"""
Statistical Validation of Telemetry Metrics for Driver Improvement Recommendations

This module provides rigorous statistical analysis to validate whether aggregated
telemetry metrics can be used to provide actionable coaching insights.

Author: Statistical Validation System
Date: 2025-11-10
"""

import pandas as pd
import numpy as np
from pathlib import Path
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass
from scipy import stats
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LinearRegression, Ridge, Lasso
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import cross_val_score, KFold
from sklearn.metrics import r2_score, mean_absolute_error, mean_squared_error
import warnings
warnings.filterwarnings('ignore')


@dataclass
class ValidationResult:
    """Container for statistical validation results."""
    metric_name: str
    correlation_with_laptime: float
    p_value: float
    is_significant: bool
    effect_size: str
    actionability_score: float
    data_quality_score: float
    recommendation: str


@dataclass
class RegressionResult:
    """Container for regression model results."""
    model_name: str
    r2_score: float
    adjusted_r2: float
    mae: float
    rmse: float
    cv_score_mean: float
    cv_score_std: float
    feature_importance: Dict[str, float]
    vif_scores: Optional[Dict[str, float]]


class TelemetryMetricValidator:
    """
    Validates telemetry metrics for use in driver coaching recommendations.

    This class performs comprehensive statistical analysis including:
    - Correlation analysis with lap times
    - Multiple regression modeling
    - Feature importance ranking
    - Multicollinearity detection
    - Data quality assessment
    """

    def __init__(self, data_dir: str = "data"):
        self.data_dir = Path(data_dir)
        self.telemetry_features = None
        self.lap_times = None
        self.merged_data = None

        # Define metrics and their theoretical properties
        self.metrics_metadata = {
            'throttle_smoothness': {
                'type': 'skill',
                'lower_is_better': True,
                'expected_correlation': 'negative',
                'actionable': True,
                'description': 'Consistency of throttle application (std dev)'
            },
            'steering_smoothness': {
                'type': 'skill',
                'lower_is_better': True,
                'expected_correlation': 'negative',
                'actionable': True,
                'description': 'Consistency of steering inputs (std dev)'
            },
            'braking_point_consistency': {
                'type': 'skill',
                'lower_is_better': True,
                'expected_correlation': 'negative',
                'actionable': True,
                'description': 'Consistency of braking points (std dev)'
            },
            'corner_efficiency': {
                'type': 'skill',
                'lower_is_better': False,
                'expected_correlation': 'negative',
                'actionable': True,
                'description': 'Efficiency of cornering (higher is better)'
            },
            'accel_efficiency': {
                'type': 'mixed',
                'lower_is_better': False,
                'expected_correlation': 'negative',
                'actionable': False,
                'description': 'Acceleration efficiency (car setup dependent)'
            },
            'lateral_g_utilization': {
                'type': 'mixed',
                'lower_is_better': False,
                'expected_correlation': 'negative',
                'actionable': False,
                'description': 'G-force utilization (car/tire dependent)'
            },
            'straight_speed_consistency': {
                'type': 'skill',
                'lower_is_better': True,
                'expected_correlation': 'negative',
                'actionable': True,
                'description': 'Speed consistency on straights (std dev)'
            }
        }

    def load_data(self, race_name: str = "barber_r1") -> None:
        """Load telemetry features and lap time data for a specific race."""
        print(f"\n{'='*80}")
        print(f"LOADING DATA: {race_name}")
        print(f"{'='*80}\n")

        # Load telemetry features
        telemetry_path = (
            self.data_dir /
            "analysis_outputs" /
            f"{race_name}_telemetry_features.csv"
        )
        self.telemetry_features = pd.read_csv(telemetry_path)
        print(f"Loaded {len(self.telemetry_features)} driver telemetry records")

        # Load lap times (best 10 average)
        lap_times_path = (
            self.data_dir /
            "race_results" /
            "best_10_laps" /
            f"{race_name}_best_10_laps.csv"
        )
        lap_df = pd.read_csv(lap_times_path, sep=';')

        # Convert lap time format (MM:SS.mmm) to seconds
        lap_df['AVERAGE_SECONDS'] = lap_df['AVERAGE'].apply(
            self._convert_laptime_to_seconds
        )

        self.lap_times = lap_df[['NUMBER', 'AVERAGE_SECONDS']].rename(
            columns={'NUMBER': 'driver_number'}
        )
        print(f"Loaded {len(self.lap_times)} driver lap time records")

        # Merge datasets
        self._merge_datasets()

    def _convert_laptime_to_seconds(self, time_str: str) -> float:
        """Convert lap time string (MM:SS.mmm) to seconds."""
        try:
            parts = time_str.split(':')
            minutes = int(parts[0])
            seconds = float(parts[1])
            return minutes * 60 + seconds
        except:
            return np.nan

    def _merge_datasets(self) -> None:
        """Merge telemetry features with lap times."""
        self.merged_data = self.telemetry_features.merge(
            self.lap_times,
            on='driver_number',
            how='inner'
        )

        # Remove rows with insufficient data
        metrics = list(self.metrics_metadata.keys())
        self.merged_data = self.merged_data.dropna(subset=metrics + ['AVERAGE_SECONDS'])

        print(f"Merged dataset: {len(self.merged_data)} complete records")
        print(f"Sample size check: {'✓ PASS' if len(self.merged_data) >= 15 else '✗ FAIL (n<15)'}\n")

    def assess_data_quality(self, metric_name: str) -> float:
        """
        Assess data quality for a specific metric.

        Returns score from 0-1 based on:
        - Missing data percentage
        - Outlier percentage
        - Coefficient of variation
        """
        data = self.merged_data[metric_name]

        # Missing data penalty
        missing_pct = data.isna().sum() / len(data)
        missing_score = 1.0 - missing_pct

        # Outlier detection using IQR method
        Q1 = data.quantile(0.25)
        Q3 = data.quantile(0.75)
        IQR = Q3 - Q1
        outliers = ((data < (Q1 - 1.5 * IQR)) | (data > (Q3 + 1.5 * IQR))).sum()
        outlier_score = 1.0 - (outliers / len(data))

        # Coefficient of variation (penalize excessive variance)
        cv = data.std() / data.mean() if data.mean() != 0 else 0
        cv_score = np.exp(-cv)  # Exponential decay for high CV

        # Weighted average
        quality_score = (
            0.4 * missing_score +
            0.3 * outlier_score +
            0.3 * cv_score
        )

        return quality_score

    def validate_metric(self, metric_name: str) -> ValidationResult:
        """
        Perform comprehensive validation of a single metric.

        Tests:
        1. Correlation with lap time (Pearson + Spearman)
        2. Statistical significance
        3. Effect size calculation
        4. Data quality assessment
        5. Actionability scoring
        """
        print(f"\nValidating: {metric_name}")
        print("-" * 60)

        metric_data = self.merged_data[metric_name]
        lap_time_data = self.merged_data['AVERAGE_SECONDS']

        # Correlation analysis
        pearson_corr, pearson_p = stats.pearsonr(metric_data, lap_time_data)
        spearman_corr, spearman_p = stats.spearmanr(metric_data, lap_time_data)

        # Use Spearman if data is non-normal (more robust)
        shapiro_stat, shapiro_p = stats.shapiro(metric_data)
        is_normal = shapiro_p > 0.05

        correlation = pearson_corr if is_normal else spearman_corr
        p_value = pearson_p if is_normal else spearman_p

        # Effect size (Cohen's d equivalent for correlation)
        # Convert correlation to Cohen's d: d = 2r / sqrt(1-r²)
        r_squared = correlation ** 2
        cohens_d = (2 * abs(correlation)) / np.sqrt(1 - r_squared) if r_squared < 1 else np.inf

        if cohens_d < 0.2:
            effect_size = "negligible"
        elif cohens_d < 0.5:
            effect_size = "small"
        elif cohens_d < 0.8:
            effect_size = "medium"
        else:
            effect_size = "large"

        # Actionability score (based on metadata)
        metadata = self.metrics_metadata[metric_name]
        actionability_base = 1.0 if metadata['actionable'] else 0.3

        # Adjust based on correlation strength
        actionability_score = actionability_base * min(abs(correlation), 1.0)

        # Data quality
        quality_score = self.assess_data_quality(metric_name)

        # Recommendation logic
        is_significant = p_value < 0.05

        if is_significant and abs(correlation) > 0.3 and actionability_score > 0.25:
            recommendation = "RECOMMENDED for coaching insights"
        elif is_significant and abs(correlation) > 0.2:
            recommendation = "USABLE with caution (weak correlation)"
        elif not is_significant:
            recommendation = "NOT RECOMMENDED (not statistically significant)"
        else:
            recommendation = "NOT RECOMMENDED (negligible correlation)"

        print(f"  Correlation: {correlation:.4f} (p={p_value:.4f})")
        print(f"  Effect size: {effect_size}")
        print(f"  Actionability: {actionability_score:.2f}")
        print(f"  Data quality: {quality_score:.2f}")
        print(f"  → {recommendation}")

        return ValidationResult(
            metric_name=metric_name,
            correlation_with_laptime=correlation,
            p_value=p_value,
            is_significant=is_significant,
            effect_size=effect_size,
            actionability_score=actionability_score,
            data_quality_score=quality_score,
            recommendation=recommendation
        )

    def validate_all_metrics(self) -> List[ValidationResult]:
        """Validate all available telemetry metrics."""
        print(f"\n{'='*80}")
        print("METRIC VALIDATION ANALYSIS")
        print(f"{'='*80}")

        results = []
        for metric_name in self.metrics_metadata.keys():
            if metric_name in self.merged_data.columns:
                result = self.validate_metric(metric_name)
                results.append(result)

        return results

    def calculate_vif(self, X: pd.DataFrame) -> Dict[str, float]:
        """
        Calculate Variance Inflation Factor to detect multicollinearity.

        VIF > 10: High multicollinearity (problematic)
        VIF 5-10: Moderate multicollinearity
        VIF < 5: Low multicollinearity (acceptable)
        """
        from statsmodels.stats.outliers_influence import variance_inflation_factor

        vif_data = {}
        for i, col in enumerate(X.columns):
            vif_data[col] = variance_inflation_factor(X.values, i)

        return vif_data

    def build_regression_models(self) -> List[RegressionResult]:
        """
        Build multiple regression models to predict lap time from metrics.

        Models tested:
        1. Linear Regression (OLS)
        2. Ridge Regression (L2 regularization)
        3. Lasso Regression (L1 regularization, feature selection)
        4. Random Forest (non-linear, feature importance)
        """
        print(f"\n{'='*80}")
        print("REGRESSION MODEL ANALYSIS")
        print(f"{'='*80}\n")

        # Prepare data
        metrics = list(self.metrics_metadata.keys())
        X = self.merged_data[metrics].copy()
        y = self.merged_data['AVERAGE_SECONDS'].copy()

        # Standardize features
        scaler = StandardScaler()
        X_scaled = pd.DataFrame(
            scaler.fit_transform(X),
            columns=X.columns,
            index=X.index
        )

        # Check multicollinearity
        print("Multicollinearity Analysis (VIF):")
        print("-" * 60)
        vif_scores = self.calculate_vif(X_scaled)
        for metric, vif in vif_scores.items():
            status = "✗ HIGH" if vif > 10 else "⚠ MODERATE" if vif > 5 else "✓ OK"
            print(f"  {metric:30s}: VIF={vif:6.2f}  [{status}]")
        print()

        # Cross-validation setup
        cv = KFold(n_splits=5, shuffle=True, random_state=42)

        results = []

        # Model 1: Linear Regression
        print("Model 1: Linear Regression (OLS)")
        print("-" * 60)
        lr = LinearRegression()
        lr.fit(X_scaled, y)
        y_pred = lr.predict(X_scaled)

        r2 = r2_score(y, y_pred)
        n, k = len(y), X.shape[1]
        adj_r2 = 1 - (1 - r2) * (n - 1) / (n - k - 1)
        mae = mean_absolute_error(y, y_pred)
        rmse = np.sqrt(mean_squared_error(y, y_pred))

        cv_scores = cross_val_score(lr, X_scaled, y, cv=cv, scoring='r2')

        # Feature importance (standardized coefficients)
        feature_imp = dict(zip(X.columns, lr.coef_))

        print(f"  R² Score: {r2:.4f}")
        print(f"  Adjusted R²: {adj_r2:.4f}")
        print(f"  MAE: {mae:.4f} seconds")
        print(f"  RMSE: {rmse:.4f} seconds")
        print(f"  CV R² Mean: {cv_scores.mean():.4f} ± {cv_scores.std():.4f}")

        results.append(RegressionResult(
            model_name="Linear Regression",
            r2_score=r2,
            adjusted_r2=adj_r2,
            mae=mae,
            rmse=rmse,
            cv_score_mean=cv_scores.mean(),
            cv_score_std=cv_scores.std(),
            feature_importance=feature_imp,
            vif_scores=vif_scores
        ))

        # Model 2: Ridge Regression
        print("\nModel 2: Ridge Regression (L2 Regularization)")
        print("-" * 60)
        ridge = Ridge(alpha=1.0)
        ridge.fit(X_scaled, y)
        y_pred_ridge = ridge.predict(X_scaled)

        r2_ridge = r2_score(y, y_pred_ridge)
        adj_r2_ridge = 1 - (1 - r2_ridge) * (n - 1) / (n - k - 1)
        mae_ridge = mean_absolute_error(y, y_pred_ridge)
        rmse_ridge = np.sqrt(mean_squared_error(y, y_pred_ridge))
        cv_scores_ridge = cross_val_score(ridge, X_scaled, y, cv=cv, scoring='r2')

        feature_imp_ridge = dict(zip(X.columns, ridge.coef_))

        print(f"  R² Score: {r2_ridge:.4f}")
        print(f"  Adjusted R²: {adj_r2_ridge:.4f}")
        print(f"  MAE: {mae_ridge:.4f} seconds")
        print(f"  RMSE: {rmse_ridge:.4f} seconds")
        print(f"  CV R² Mean: {cv_scores_ridge.mean():.4f} ± {cv_scores_ridge.std():.4f}")

        results.append(RegressionResult(
            model_name="Ridge Regression",
            r2_score=r2_ridge,
            adjusted_r2=adj_r2_ridge,
            mae=mae_ridge,
            rmse=rmse_ridge,
            cv_score_mean=cv_scores_ridge.mean(),
            cv_score_std=cv_scores_ridge.std(),
            feature_importance=feature_imp_ridge,
            vif_scores=None
        ))

        # Model 3: Lasso Regression
        print("\nModel 3: Lasso Regression (L1 Regularization)")
        print("-" * 60)
        lasso = Lasso(alpha=0.1)
        lasso.fit(X_scaled, y)
        y_pred_lasso = lasso.predict(X_scaled)

        r2_lasso = r2_score(y, y_pred_lasso)
        adj_r2_lasso = 1 - (1 - r2_lasso) * (n - 1) / (n - k - 1)
        mae_lasso = mean_absolute_error(y, y_pred_lasso)
        rmse_lasso = np.sqrt(mean_squared_error(y, y_pred_lasso))
        cv_scores_lasso = cross_val_score(lasso, X_scaled, y, cv=cv, scoring='r2')

        feature_imp_lasso = dict(zip(X.columns, lasso.coef_))

        print(f"  R² Score: {r2_lasso:.4f}")
        print(f"  Adjusted R²: {adj_r2_lasso:.4f}")
        print(f"  MAE: {mae_lasso:.4f} seconds")
        print(f"  RMSE: {rmse_lasso:.4f} seconds")
        print(f"  CV R² Mean: {cv_scores_lasso.mean():.4f} ± {cv_scores_lasso.std():.4f}")
        print(f"  Features selected: {sum(lasso.coef_ != 0)} / {len(lasso.coef_)}")

        results.append(RegressionResult(
            model_name="Lasso Regression",
            r2_score=r2_lasso,
            adjusted_r2=adj_r2_lasso,
            mae=mae_lasso,
            rmse=rmse_lasso,
            cv_score_mean=cv_scores_lasso.mean(),
            cv_score_std=cv_scores_lasso.std(),
            feature_importance=feature_imp_lasso,
            vif_scores=None
        ))

        # Model 4: Random Forest
        print("\nModel 4: Random Forest Regressor")
        print("-" * 60)
        rf = RandomForestRegressor(n_estimators=100, random_state=42, max_depth=5)
        rf.fit(X_scaled, y)
        y_pred_rf = rf.predict(X_scaled)

        r2_rf = r2_score(y, y_pred_rf)
        adj_r2_rf = 1 - (1 - r2_rf) * (n - 1) / (n - k - 1)
        mae_rf = mean_absolute_error(y, y_pred_rf)
        rmse_rf = np.sqrt(mean_squared_error(y, y_pred_rf))
        cv_scores_rf = cross_val_score(rf, X_scaled, y, cv=cv, scoring='r2')

        feature_imp_rf = dict(zip(X.columns, rf.feature_importances_))

        print(f"  R² Score: {r2_rf:.4f}")
        print(f"  Adjusted R²: {adj_r2_rf:.4f}")
        print(f"  MAE: {mae_rf:.4f} seconds")
        print(f"  RMSE: {rmse_rf:.4f} seconds")
        print(f"  CV R² Mean: {cv_scores_rf.mean():.4f} ± {cv_scores_rf.std():.4f}")

        results.append(RegressionResult(
            model_name="Random Forest",
            r2_score=r2_rf,
            adjusted_r2=adj_r2_rf,
            mae=mae_rf,
            rmse=rmse_rf,
            cv_score_mean=cv_scores_rf.mean(),
            cv_score_std=cv_scores_rf.std(),
            feature_importance=feature_imp_rf,
            vif_scores=None
        ))

        return results

    def generate_improvement_formula(
        self,
        model_result: RegressionResult
    ) -> Dict[str, float]:
        """
        Generate improvement potential formula based on model coefficients.

        Returns expected lap time change per unit change in each metric.
        """
        print(f"\n{'='*80}")
        print("IMPROVEMENT POTENTIAL FORMULA")
        print(f"{'='*80}\n")

        print("Expected lap time change per metric improvement:")
        print("-" * 60)

        # Sort by absolute importance
        sorted_features = sorted(
            model_result.feature_importance.items(),
            key=lambda x: abs(x[1]),
            reverse=True
        )

        improvement_formula = {}

        for metric, coef in sorted_features:
            metadata = self.metrics_metadata[metric]

            # Calculate practical improvement
            if metadata['lower_is_better']:
                direction = "decrease"
                lap_time_change = -coef  # Negative coef means improvement
            else:
                direction = "increase"
                lap_time_change = coef

            improvement_formula[metric] = lap_time_change

            print(f"  {metric:30s}: {lap_time_change:+.4f} sec per unit {direction}")
            print(f"    → Actionable: {'Yes' if metadata['actionable'] else 'No (car dependent)'}")

        return improvement_formula

    def calculate_realistic_improvements(self) -> pd.DataFrame:
        """
        Calculate realistic improvement targets based on percentile analysis.

        For each metric, calculate what improvement from 75th → 25th percentile means.
        """
        print(f"\n{'='*80}")
        print("REALISTIC IMPROVEMENT TARGETS")
        print(f"{'='*80}\n")

        metrics = list(self.metrics_metadata.keys())
        improvement_targets = []

        for metric in metrics:
            if metric not in self.merged_data.columns:
                continue

            metadata = self.metrics_metadata[metric]
            data = self.merged_data[metric]

            # Calculate percentiles
            p25 = data.quantile(0.25)
            p50 = data.quantile(0.50)
            p75 = data.quantile(0.75)

            if metadata['lower_is_better']:
                current = p75  # Worse performance (75th percentile)
                target = p25   # Better performance (25th percentile)
            else:
                current = p25  # Worse performance (25th percentile)
                target = p75   # Better performance (75th percentile)

            improvement = target - current
            improvement_pct = (improvement / current * 100) if current != 0 else 0

            improvement_targets.append({
                'metric': metric,
                'current_75th': current,
                'target_25th': target,
                'improvement_absolute': improvement,
                'improvement_percent': improvement_pct,
                'actionable': metadata['actionable']
            })

        df_targets = pd.DataFrame(improvement_targets)

        print("Improvement from 75th percentile → 25th percentile:")
        print("-" * 60)
        for _, row in df_targets.iterrows():
            print(f"{row['metric']:30s}: {row['improvement_absolute']:+.4f} "
                  f"({row['improvement_percent']:+.1f}%)")

        return df_targets

    def generate_coaching_example(
        self,
        driver_number: int,
        target_driver: int
    ) -> None:
        """
        Generate a concrete coaching example for a specific driver.

        Example: "Driver #7, if you improve X by Y, you could match Driver #13"
        """
        print(f"\n{'='*80}")
        print(f"COACHING EXAMPLE: Driver #{driver_number} → Target: Driver #{target_driver}")
        print(f"{'='*80}\n")

        # Get driver data
        driver_data = self.merged_data[
            self.merged_data['driver_number'] == driver_number
        ]
        target_data = self.merged_data[
            self.merged_data['driver_number'] == target_driver
        ]

        if driver_data.empty or target_data.empty:
            print("ERROR: Driver(s) not found in dataset")
            return

        driver_laptime = driver_data['AVERAGE_SECONDS'].iloc[0]
        target_laptime = target_data['AVERAGE_SECONDS'].iloc[0]
        gap = driver_laptime - target_laptime

        print(f"Current Performance:")
        print(f"  Driver #{driver_number}: {driver_laptime:.3f} sec")
        print(f"  Driver #{target_driver}: {target_laptime:.3f} sec")
        print(f"  Gap: {gap:+.3f} sec\n")

        print("Metric Comparison:")
        print("-" * 60)

        metrics = list(self.metrics_metadata.keys())
        recommendations = []

        for metric in metrics:
            if metric not in driver_data.columns:
                continue

            metadata = self.metrics_metadata[metric]
            driver_value = driver_data[metric].iloc[0]
            target_value = target_data[metric].iloc[0]

            if metadata['lower_is_better']:
                improvement_needed = target_value - driver_value
                is_worse = driver_value > target_value
            else:
                improvement_needed = target_value - driver_value
                is_worse = driver_value < target_value

            status = "⚠ NEEDS IMPROVEMENT" if is_worse else "✓ OK"

            print(f"{metric:30s}:")
            print(f"  Current: {driver_value:.4f}  Target: {target_value:.4f}  "
                  f"Δ={improvement_needed:+.4f}  [{status}]")

            if is_worse and metadata['actionable']:
                recommendations.append({
                    'metric': metric,
                    'current': driver_value,
                    'target': target_value,
                    'improvement': improvement_needed
                })

        if recommendations:
            print(f"\nTop 3 Actionable Improvements:")
            print("-" * 60)
            for i, rec in enumerate(recommendations[:3], 1):
                print(f"{i}. {rec['metric']}")
                print(f"   Improve from {rec['current']:.4f} → {rec['target']:.4f}")
                print(f"   Change needed: {rec['improvement']:+.4f}")


def main():
    """Run complete statistical validation workflow."""

    # Initialize validator
    validator = TelemetryMetricValidator(data_dir="data")

    # Load data for Barber Race 1
    validator.load_data("barber_r1")

    # Step 1: Validate individual metrics
    metric_results = validator.validate_all_metrics()

    # Step 2: Build regression models
    model_results = validator.build_regression_models()

    # Step 3: Generate improvement formula
    best_model = max(model_results, key=lambda x: x.cv_score_mean)
    print(f"\nBest Model: {best_model.model_name} (CV R² = {best_model.cv_score_mean:.4f})")

    improvement_formula = validator.generate_improvement_formula(best_model)

    # Step 4: Calculate realistic improvement targets
    improvement_targets = validator.calculate_realistic_improvements()

    # Step 5: Generate coaching example
    validator.generate_coaching_example(driver_number=7, target_driver=13)

    # Final summary
    print(f"\n{'='*80}")
    print("STATISTICAL VALIDATION SUMMARY")
    print(f"{'='*80}\n")

    print("Metric Recommendations:")
    print("-" * 60)
    for result in metric_results:
        status = "✓" if "RECOMMENDED" in result.recommendation else "✗"
        print(f"{status} {result.metric_name:30s}: {result.recommendation}")

    print(f"\n\nModel Performance Summary:")
    print("-" * 60)
    for model in model_results:
        print(f"{model.model_name:20s}: R²={model.r2_score:.4f}  "
              f"CV R²={model.cv_score_mean:.4f}  MAE={model.mae:.4f}s")

    print(f"\n{'='*80}")
    print("VALIDATION COMPLETE")
    print(f"{'='*80}\n")


if __name__ == "__main__":
    main()
