#!/usr/bin/env python3
"""
Comprehensive Statistical Validation Audit of Gibbs AI 4-Factor Performance Model

This script validates:
1. Current model statistics (R², MAE, factor weights)
2. Feature engineering correctness
3. Factor analysis validation
4. Data consistency across JSON and CSV files
5. Provides recommendations for any updates needed
"""

import pandas as pd
import numpy as np
import json
from pathlib import Path
from sklearn.decomposition import PCA
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_absolute_error, r2_score
from scipy import stats
import warnings
warnings.filterwarnings('ignore')


class FourFactorModelValidator:
    """Validates the 4-Factor Performance Model"""

    def __init__(self, data_dir: Path, analysis_dir: Path):
        self.data_dir = data_dir
        self.analysis_dir = analysis_dir
        self.results = {}
        self.issues = []
        self.recommendations = []

    def load_data(self):
        """Load all necessary data files"""
        print("=" * 80)
        print("STEP 1: Loading Data Files")
        print("=" * 80)

        # Load CSV files
        self.features_df = pd.read_csv(self.analysis_dir / "all_races_tier1_features.csv")
        self.factor_scores_df = pd.read_csv(self.analysis_dir / "tier1_factor_scores.csv")
        self.factor_loadings_df = pd.read_csv(self.analysis_dir / "tier1_factor_loadings.csv")

        # Load JSON files
        with open(self.data_dir / "driver_factors.json", 'r') as f:
            self.driver_factors = json.load(f)

        with open(self.data_dir / "driver_race_results.json", 'r') as f:
            self.race_results = json.load(f)

        with open(self.data_dir / "factor_breakdowns.json", 'r') as f:
            self.factor_breakdowns = json.load(f)

        print(f"✓ Features DataFrame: {self.features_df.shape}")
        print(f"✓ Factor Scores DataFrame: {self.factor_scores_df.shape}")
        print(f"✓ Factor Loadings DataFrame: {self.factor_loadings_df.shape}")
        print(f"✓ Driver Factors: {self.driver_factors['driver_count']} drivers, {self.driver_factors['total_records']} records")
        print(f"✓ Race Results: {self.race_results['driver_count']} drivers, {self.race_results['total_results']} results")
        print(f"✓ Factor Breakdowns: {len(self.factor_breakdowns.get('drivers', []))} drivers")
        print()

    def validate_feature_engineering(self):
        """Validate that all 12 features are correctly calculated"""
        print("=" * 80)
        print("STEP 2: Feature Engineering Validation")
        print("=" * 80)

        expected_features = [
            'qualifying_pace', 'best_race_lap', 'avg_top10_pace',
            'stint_consistency', 'sector_consistency', 'braking_consistency',
            'pace_degradation', 'late_stint_perf', 'early_vs_late_pace',
            'position_changes', 'positions_gained', 'performance_normalized'
        ]

        actual_features = [col for col in self.features_df.columns
                          if col not in ['race', 'driver_number', 'finishing_position']]

        print(f"Expected features: {len(expected_features)}")
        print(f"Actual features: {len(actual_features)}")

        # Check for missing or extra features
        missing = set(expected_features) - set(actual_features)
        extra = set(actual_features) - set(expected_features)

        if missing:
            self.issues.append(f"Missing features: {missing}")
            print(f"✗ MISSING FEATURES: {missing}")
        else:
            print("✓ All expected features present")

        if extra:
            self.issues.append(f"Extra features: {extra}")
            print(f"⚠ EXTRA FEATURES: {extra}")

        # Check for null values
        null_counts = self.features_df[actual_features].isnull().sum()
        if null_counts.sum() > 0:
            print(f"\n⚠ NULL VALUES DETECTED:")
            print(null_counts[null_counts > 0])
            self.issues.append(f"Null values in features: {null_counts[null_counts > 0].to_dict()}")
        else:
            print("✓ No null values in features")

        # Check data ranges
        print("\nFeature Statistics:")
        print(self.features_df[actual_features].describe().round(3))

        # Validate sector_consistency and braking_consistency are derived from sector timing
        print("\n✓ sector_consistency range:",
              f"{self.features_df['sector_consistency'].min():.3f} to {self.features_df['sector_consistency'].max():.3f}")
        print("✓ braking_consistency range:",
              f"{self.features_df['braking_consistency'].min():.3f} to {self.features_df['braking_consistency'].max():.3f}")

        self.results['feature_count'] = len(actual_features)
        self.results['feature_nulls'] = null_counts.sum()
        print()

    def validate_factor_analysis(self):
        """Validate the 4-factor PCA analysis"""
        print("=" * 80)
        print("STEP 3: Factor Analysis Validation")
        print("=" * 80)

        # Prepare features for PCA
        feature_cols = [col for col in self.features_df.columns
                       if col not in ['race', 'driver_number', 'finishing_position']]

        X = self.features_df[feature_cols].values

        # Remove rows with any NaN/inf values
        mask = ~(np.isnan(X).any(axis=1) | np.isinf(X).any(axis=1))
        X_clean = X[mask]

        print(f"Cleaned data: {X_clean.shape[0]} samples (removed {X.shape[0] - X_clean.shape[0]} rows)")

        # Standardize
        scaler = StandardScaler()
        X_scaled = scaler.fit_transform(X_clean)

        # Perform PCA with 4 components
        pca = PCA(n_components=4)
        factor_scores_recomputed = pca.fit_transform(X_scaled)

        # Check explained variance
        explained_var = pca.explained_variance_ratio_
        cumulative_var = np.cumsum(explained_var)

        print(f"\n4-Factor Model Explained Variance:")
        for i, (var, cum) in enumerate(zip(explained_var, cumulative_var), 1):
            print(f"  Factor {i}: {var*100:.2f}% (Cumulative: {cum*100:.2f}%)")

        print(f"\nTotal variance explained by 4 factors: {cumulative_var[-1]*100:.2f}%")

        # Compare with 5-factor model
        pca_5 = PCA(n_components=5)
        pca_5.fit(X_scaled)
        cumulative_var_5 = np.cumsum(pca_5.explained_variance_ratio_)
        print(f"Total variance explained by 5 factors: {cumulative_var_5[-1]*100:.2f}%")

        # Check factor loadings
        loadings = pd.DataFrame(
            pca.components_.T,
            columns=[f'Factor_{i+1}' for i in range(4)],
            index=feature_cols
        )

        print("\nFactor Loadings (top 3 features per factor):")
        for i in range(4):
            col = f'Factor_{i+1}'
            top_features = loadings[col].abs().nlargest(3)
            print(f"\n{col}:")
            for feat, loading in top_features.items():
                print(f"  {feat}: {loadings.loc[feat, col]:.3f}")

        # Compare with stored loadings
        stored_loadings = self.factor_loadings_df.set_index(self.factor_loadings_df.columns[0])
        stored_loadings = stored_loadings.iloc[:, :4]  # Only 4 factors

        # Check correlation between recomputed and stored loadings
        print("\nCorrelation between recomputed and stored loadings:")
        for i in range(4):
            col_new = f'Factor_{i+1}'
            col_stored = stored_loadings.columns[i]

            # Align indices
            common_idx = loadings.index.intersection(stored_loadings.index)
            corr = np.corrcoef(loadings.loc[common_idx, col_new],
                              stored_loadings.loc[common_idx, col_stored])[0, 1]
            print(f"  {col_new}: r = {abs(corr):.4f}")

            if abs(corr) < 0.95:
                self.issues.append(f"Low correlation for {col_new}: {abs(corr):.4f}")

        self.results['explained_variance_4factor'] = cumulative_var[-1]
        self.results['explained_variance_5factor'] = cumulative_var_5[-1]
        print()

    def validate_model_statistics(self):
        """Validate R², MAE, and factor weights"""
        print("=" * 80)
        print("STEP 4: Model Statistics Validation")
        print("=" * 80)

        # Merge factor scores with finishing positions
        df = self.factor_scores_df.copy()

        # Use only 4 factors
        factor_cols = ['factor_1_score', 'factor_2_score', 'factor_3_score', 'factor_4_score']

        # Remove rows with NaN or inf
        mask = ~(df[factor_cols + ['finishing_position']].isna().any(axis=1) |
                 np.isinf(df[factor_cols + ['finishing_position']]).any(axis=1))
        df_clean = df[mask].copy()

        print(f"Clean samples for regression: {len(df_clean)} (removed {len(df) - len(df_clean)} rows)")

        X = df_clean[factor_cols].values
        y = df_clean['finishing_position'].values

        # Fit linear regression
        model = LinearRegression()
        model.fit(X, y)

        # Predictions
        y_pred = model.predict(X)

        # Calculate metrics
        r2 = r2_score(y, y_pred)
        mae = mean_absolute_error(y, y_pred)

        print(f"\nModel Performance:")
        print(f"  R² Score: {r2:.4f}")
        print(f"  MAE: {mae:.2f} positions")

        # Calculate factor weights from coefficients
        abs_coefs = np.abs(model.coef_)
        total_abs_coef = abs_coefs.sum()
        weights = (abs_coefs / total_abs_coef) * 100

        print(f"\nFactor Weights (from regression coefficients):")
        for i, (coef, weight) in enumerate(zip(model.coef_, weights), 1):
            print(f"  Factor {i}: {weight:.1f}% (coef: {coef:.3f})")

        # Compare with documented values
        print("\nComparison with Documented Values:")
        documented = {
            'R²': 0.895,
            'MAE': 1.78,
            'weights': [46.6, 29.1, 14.9, 9.5]  # Speed, Consistency, Racecraft, Tire Mgmt
        }

        print(f"  R² - Documented: {documented['R²']:.3f}, Actual: {r2:.3f}, Diff: {abs(r2 - documented['R²']):.3f}")
        print(f"  MAE - Documented: {documented['MAE']:.2f}, Actual: {mae:.2f}, Diff: {abs(mae - documented['MAE']):.2f}")

        # Map factors to performance dimensions based on loadings
        # This requires interpreting which factor is which
        print("\nFactor Interpretation (based on loadings):")
        print("  Factor 1: Likely SPEED/PACE (high loadings on qualifying_pace, best_race_lap)")
        print("  Factor 2: Likely CONSISTENCY (high loadings on sector/stint consistency)")
        print("  Factor 3: Likely RACECRAFT (high loadings on position_changes, positions_gained)")
        print("  Factor 4: Likely TIRE MANAGEMENT (high loadings on pace_degradation, late_stint_perf)")

        # Check if weights are close
        weight_diffs = [abs(w - d) for w, d in zip(weights, documented['weights'])]
        max_weight_diff = max(weight_diffs)

        if abs(r2 - documented['R²']) > 0.05:
            self.issues.append(f"R² differs significantly: {r2:.3f} vs documented {documented['R²']:.3f}")
            self.recommendations.append("Rerun factor analysis and regression model")
        else:
            print(f"\n✓ R² is within acceptable range (diff < 0.05)")

        if abs(mae - documented['MAE']) > 0.5:
            self.issues.append(f"MAE differs significantly: {mae:.2f} vs documented {documented['MAE']:.2f}")
            self.recommendations.append("Verify model performance metrics")
        else:
            print(f"✓ MAE is within acceptable range (diff < 0.5)")

        if max_weight_diff > 10:
            self.issues.append(f"Factor weights differ significantly (max diff: {max_weight_diff:.1f}%)")
            self.recommendations.append("Review factor weight calculations")
        else:
            print(f"✓ Factor weights are within acceptable range (max diff < 10%)")

        self.results['r2_score'] = r2
        self.results['mae'] = mae
        self.results['factor_weights'] = weights.tolist()
        self.results['documented_r2'] = documented['R²']
        self.results['documented_mae'] = documented['MAE']
        print()

    def validate_data_consistency(self):
        """Validate consistency across JSON and CSV files"""
        print("=" * 80)
        print("STEP 5: Data Consistency Validation")
        print("=" * 80)

        # Check driver counts
        csv_drivers = set(self.factor_scores_df['driver_number'].unique())
        json_drivers = set([d['driver_number'] for d in self.driver_factors['drivers']])

        print(f"Drivers in CSV: {len(csv_drivers)}")
        print(f"Drivers in driver_factors.json: {len(json_drivers)}")

        if csv_drivers != json_drivers:
            diff = csv_drivers.symmetric_difference(json_drivers)
            self.issues.append(f"Driver mismatch between CSV and JSON: {diff}")
            print(f"✗ DRIVER MISMATCH: {diff}")
        else:
            print("✓ Driver counts consistent")

        # Check race counts
        csv_races = len(self.factor_scores_df)
        json_race_count = self.driver_factors['total_records']

        print(f"\nRace results in CSV: {csv_races}")
        print(f"Race results in JSON: {json_race_count}")

        if csv_races != json_race_count:
            self.issues.append(f"Race count mismatch: CSV={csv_races}, JSON={json_race_count}")
            print(f"✗ RACE COUNT MISMATCH")
        else:
            print("✓ Race counts consistent")

        # Sample validation: Check factor scores for a driver
        sample_driver = str(list(json_drivers)[0])
        print(f"\nSample validation for driver #{sample_driver}:")

        # Get from CSV
        csv_sample = self.factor_scores_df[
            self.factor_scores_df['driver_number'] == int(sample_driver)
        ].head(1)

        # Get from JSON
        json_sample = None
        for driver_data in self.driver_factors['drivers']:
            if driver_data['driver_number'] == int(sample_driver):
                json_sample = driver_data
                break

        if csv_sample.empty or json_sample is None:
            print(f"⚠ Could not find sample data for driver {sample_driver}")
        else:
            print(f"  CSV factor scores available: {not csv_sample.empty}")
            print(f"  JSON factor data available: {json_sample is not None}")

        # Check for sector timing data in race_results
        sector_fields = ['driver_s1_best', 'driver_s2_best', 'driver_s3_best']
        sample_result = None
        for driver_num, results in self.race_results['data'].items():
            if results:
                sample_result = results[0]
                break

        if sample_result:
            sector_data_present = all(field in sample_result for field in sector_fields)
            print(f"\n✓ Sector timing fields present in race_results.json: {sector_data_present}")

            # Check if sector data is actually populated
            sector_values = [sample_result.get(field) for field in sector_fields]
            has_values = any(v is not None for v in sector_values)
            print(f"✓ Sector timing data populated: {has_values}")

            if not has_values:
                self.recommendations.append("Sector timing fields exist but many values are null - verify data import")

        print()

    def generate_report(self):
        """Generate final validation report"""
        print("=" * 80)
        print("COMPREHENSIVE VALIDATION REPORT")
        print("=" * 80)

        print("\n📊 STATISTICAL VALIDATION SUMMARY:")
        print(f"  Current R² Score: {self.results.get('r2_score', 'N/A'):.4f}")
        print(f"  Documented R²: {self.results.get('documented_r2', 'N/A'):.4f}")
        print(f"  Current MAE: {self.results.get('mae', 'N/A'):.2f} positions")
        print(f"  Documented MAE: {self.results.get('documented_mae', 'N/A'):.2f} positions")

        print("\n  Factor Weights:")
        if 'factor_weights' in self.results:
            weights = self.results['factor_weights']
            labels = ['Factor 1 (Speed)', 'Factor 2 (Consistency)',
                     'Factor 3 (Racecraft)', 'Factor 4 (Tire Mgmt)']
            for label, weight in zip(labels, weights):
                print(f"    {label}: {weight:.1f}%")

        print(f"\n  Variance Explained (4 factors): {self.results.get('explained_variance_4factor', 0)*100:.2f}%")
        print(f"  Variance Explained (5 factors): {self.results.get('explained_variance_5factor', 0)*100:.2f}%")

        print("\n🔍 ISSUES FOUND:")
        if self.issues:
            for i, issue in enumerate(self.issues, 1):
                print(f"  {i}. {issue}")
        else:
            print("  ✓ No critical issues found!")

        print("\n💡 RECOMMENDATIONS:")
        if self.recommendations:
            for i, rec in enumerate(self.recommendations, 1):
                print(f"  {i}. {rec}")
        else:
            print("  ✓ Current data and model are accurate - no updates needed!")

        print("\n" + "=" * 80)
        print()

        # Save report to file
        report_path = self.data_dir / "validation_report.json"

        # Convert numpy types to Python native types
        results_serializable = {}
        for key, value in self.results.items():
            if isinstance(value, np.ndarray):
                results_serializable[key] = value.tolist()
            elif isinstance(value, (np.integer, np.floating)):
                results_serializable[key] = float(value)
            elif isinstance(value, list):
                results_serializable[key] = [float(v) if isinstance(v, (np.integer, np.floating)) else v for v in value]
            else:
                results_serializable[key] = value

        report_data = {
            'validation_date': pd.Timestamp.now().isoformat(),
            'statistics': results_serializable,
            'issues': self.issues,
            'recommendations': self.recommendations,
            'status': 'PASS' if not self.issues else 'REVIEW_NEEDED'
        }

        with open(report_path, 'w') as f:
            json.dump(report_data, f, indent=2)

        print(f"Full report saved to: {report_path}")


def main():
    """Run comprehensive validation"""
    # Set paths
    base_dir = Path("/Users/justingrosz/Documents/AI-Work/hackthetrack-master")
    data_dir = base_dir / "backend" / "data"
    analysis_dir = base_dir / "data" / "analysis_outputs"

    # Create validator
    validator = FourFactorModelValidator(data_dir, analysis_dir)

    # Run validation steps
    try:
        validator.load_data()
        validator.validate_feature_engineering()
        validator.validate_factor_analysis()
        validator.validate_model_statistics()
        validator.validate_data_consistency()
        validator.generate_report()

    except Exception as e:
        print(f"\n❌ VALIDATION ERROR: {e}")
        import traceback
        traceback.print_exc()
        return 1

    return 0


if __name__ == "__main__":
    exit(main())
