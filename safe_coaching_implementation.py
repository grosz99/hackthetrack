"""
Statistically Valid Coaching Implementation

This module provides ONLY statistically validated coaching insights,
avoiding overfitting and unsupported causal claims.

Based on: STATISTICAL_VALIDATION_REPORT.md

Author: Statistical Validation System
Date: 2025-11-10
"""

import pandas as pd
import numpy as np
from pathlib import Path
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass
from scipy import stats


@dataclass
class DriverInsight:
    """Statistically valid driver insight."""
    metric_name: str
    driver_value: float
    percentile: float
    target_25th: float
    target_10th: float
    improvement_needed_25th: float
    improvement_needed_10th: float
    is_validated: bool
    recommendation: str
    confidence: str


class SafeCoachingAnalyzer:
    """
    Provides statistically valid coaching insights without overfitting.

    ONLY uses validated metrics with proper uncertainty quantification.
    Avoids causal claims and predictive modeling with insufficient data.
    """

    def __init__(self, data_dir: str = "data"):
        self.data_dir = Path(data_dir)

        # Only validated metrics (from statistical validation)
        self.validated_metrics = {
            'braking_point_consistency': {
                'correlation': 0.573,
                'p_value': 0.020,
                'actionable': True,
                'lower_is_better': True,
                'description': 'Consistency of braking points',
                'unit': 'seconds (std dev)',
                'confidence': 'MEDIUM'
            }
        }

        # Metrics to show for context only (no coaching)
        self.informational_metrics = {
            'lateral_g_utilization': {
                'correlation': -0.803,
                'p_value': 0.0002,
                'actionable': False,
                'lower_is_better': False,
                'description': 'G-force utilization (car setup)',
                'unit': 'G',
                'confidence': 'LOW (car dependent)'
            }
        }

        # Metrics NOT validated (do not use)
        self.unvalidated_metrics = [
            'throttle_smoothness',
            'steering_smoothness',
            'corner_efficiency',
            'accel_efficiency',
            'straight_speed_consistency'
        ]

    def load_race_data(self, race_name: str) -> pd.DataFrame:
        """Load telemetry and lap time data for a race."""
        # Load telemetry
        telemetry_path = (
            self.data_dir /
            "analysis_outputs" /
            f"{race_name}_telemetry_features.csv"
        )
        telemetry = pd.read_csv(telemetry_path)

        # Load lap times
        lap_times_path = (
            self.data_dir /
            "race_results" /
            "best_10_laps" /
            f"{race_name}_best_10_laps.csv"
        )
        lap_df = pd.read_csv(lap_times_path, sep=';')

        # Convert lap times
        lap_df['AVERAGE_SECONDS'] = lap_df['AVERAGE'].apply(
            self._convert_laptime_to_seconds
        )

        # Merge
        merged = telemetry.merge(
            lap_df[['NUMBER', 'AVERAGE_SECONDS']],
            left_on='driver_number',
            right_on='NUMBER',
            how='inner'
        )

        return merged

    def _convert_laptime_to_seconds(self, time_str: str) -> float:
        """Convert lap time string (MM:SS.mmm) to seconds."""
        try:
            parts = time_str.split(':')
            minutes = int(parts[0])
            seconds = float(parts[1])
            return minutes * 60 + seconds
        except:
            return np.nan

    def calculate_percentile(
        self,
        value: float,
        population: pd.Series,
        lower_is_better: bool
    ) -> float:
        """
        Calculate percentile ranking for a metric value.

        Args:
            value: Driver's metric value
            population: All drivers' values for this metric
            lower_is_better: Whether lower values are better

        Returns:
            Percentile (0-100)
        """
        if lower_is_better:
            # Lower is better: percentile = % of drivers with worse (higher) values
            percentile = (population > value).sum() / len(population) * 100
        else:
            # Higher is better: percentile = % of drivers with worse (lower) values
            percentile = (population < value).sum() / len(population) * 100

        return percentile

    def generate_driver_insights(
        self,
        driver_number: int,
        race_name: str
    ) -> List[DriverInsight]:
        """
        Generate statistically valid insights for a driver.

        ONLY returns insights for validated metrics.
        Uses percentile comparisons, not predictive modeling.
        """
        data = self.load_race_data(race_name)

        driver_data = data[data['driver_number'] == driver_number]

        if driver_data.empty:
            raise ValueError(f"Driver {driver_number} not found in {race_name}")

        insights = []

        # Analyze validated metrics only
        for metric, metadata in self.validated_metrics.items():
            if metric not in data.columns:
                continue

            # Get driver value
            driver_value = driver_data[metric].iloc[0]

            # Get population distribution
            population = data[metric].dropna()

            # Calculate percentiles
            percentile = self.calculate_percentile(
                driver_value,
                population,
                metadata['lower_is_better']
            )

            # Calculate targets
            target_25th = population.quantile(0.25 if metadata['lower_is_better'] else 0.75)
            target_10th = population.quantile(0.10 if metadata['lower_is_better'] else 0.90)

            improvement_25th = target_25th - driver_value
            improvement_10th = target_10th - driver_value

            # Generate recommendation
            if percentile >= 75:
                recommendation = (
                    f"EXCELLENT: You're in the top 25% for {metadata['description']}. "
                    f"Continue maintaining this consistency."
                )
            elif percentile >= 50:
                recommendation = (
                    f"GOOD: You're above average. Target: {target_25th:.4f} "
                    f"({improvement_25th:+.4f} improvement) to reach top 25%."
                )
            elif percentile >= 25:
                recommendation = (
                    f"FOCUS AREA: {metadata['description']} needs improvement. "
                    f"Target: {target_25th:.4f} ({improvement_25th:+.4f} change) "
                    f"as initial goal."
                )
            else:
                recommendation = (
                    f"PRIORITY: This is your biggest opportunity. "
                    f"Target: {target_25th:.4f} ({improvement_25th:+.4f} change). "
                    f"Work with coach on specific braking drills."
                )

            insights.append(DriverInsight(
                metric_name=metric,
                driver_value=driver_value,
                percentile=percentile,
                target_25th=target_25th,
                target_10th=target_10th,
                improvement_needed_25th=improvement_25th,
                improvement_needed_10th=improvement_10th,
                is_validated=True,
                recommendation=recommendation,
                confidence=metadata['confidence']
            ))

        return insights

    def compare_drivers_safely(
        self,
        driver_a: int,
        driver_b: int,
        race_name: str
    ) -> Dict:
        """
        Compare two drivers without making unsupported causal claims.

        Returns:
            Dictionary with safe comparisons
        """
        data = self.load_race_data(race_name)

        driver_a_data = data[data['driver_number'] == driver_a]
        driver_b_data = data[data['driver_number'] == driver_b]

        if driver_a_data.empty or driver_b_data.empty:
            raise ValueError(f"One or both drivers not found in {race_name}")

        # Get lap times
        laptime_a = driver_a_data['AVERAGE_SECONDS'].iloc[0]
        laptime_b = driver_b_data['AVERAGE_SECONDS'].iloc[0]
        gap = laptime_a - laptime_b

        comparison = {
            'driver_a': driver_a,
            'driver_b': driver_b,
            'laptime_a': laptime_a,
            'laptime_b': laptime_b,
            'gap_seconds': gap,
            'faster_driver': driver_b if gap > 0 else driver_a,
            'validated_differences': [],
            'informational_differences': [],
            'warning': (
                "CAUTION: Differences may be due to car setup, experience, "
                "or other confounding factors. Do not assume metric differences "
                "directly cause lap time differences."
            )
        }

        # Compare validated metrics
        for metric, metadata in self.validated_metrics.items():
            if metric not in data.columns:
                continue

            value_a = driver_a_data[metric].iloc[0]
            value_b = driver_b_data[metric].iloc[0]
            diff = value_b - value_a

            # Calculate percentiles
            population = data[metric].dropna()
            percentile_a = self.calculate_percentile(
                value_a, population, metadata['lower_is_better']
            )
            percentile_b = self.calculate_percentile(
                value_b, population, metadata['lower_is_better']
            )

            comparison['validated_differences'].append({
                'metric': metric,
                'driver_a_value': value_a,
                'driver_b_value': value_b,
                'difference': diff,
                'driver_a_percentile': percentile_a,
                'driver_b_percentile': percentile_b,
                'description': metadata['description'],
                'actionable': metadata['actionable']
            })

        # Compare informational metrics (no coaching)
        for metric, metadata in self.informational_metrics.items():
            if metric not in data.columns:
                continue

            value_a = driver_a_data[metric].iloc[0]
            value_b = driver_b_data[metric].iloc[0]
            diff = value_b - value_a

            comparison['informational_differences'].append({
                'metric': metric,
                'driver_a_value': value_a,
                'driver_b_value': value_b,
                'difference': diff,
                'description': metadata['description'],
                'warning': 'This metric is car/setup dependent. Not actionable for drivers.'
            })

        return comparison

    def generate_coaching_report(
        self,
        driver_number: int,
        race_name: str
    ) -> str:
        """
        Generate a complete coaching report with proper statistical disclaimers.

        Returns:
            Formatted text report
        """
        insights = self.generate_driver_insights(driver_number, race_name)

        report = []
        report.append(f"="*80)
        report.append(f"DRIVER PERFORMANCE ANALYSIS")
        report.append(f"Driver #{driver_number} | {race_name.replace('_', ' ').title()}")
        report.append(f"="*80)
        report.append("")

        # Statistical disclaimer
        report.append("STATISTICAL DISCLAIMER:")
        report.append("-" * 80)
        report.append(
            "This analysis uses only statistically validated metrics (p<0.05)."
        )
        report.append(
            "Correlations do not imply causation. Improvements in metrics are"
        )
        report.append(
            "associated with better lap times but may not directly cause them."
        )
        report.append("")

        # Validated insights
        report.append("VALIDATED METRICS:")
        report.append("-" * 80)

        for insight in insights:
            report.append(f"\n{insight.metric_name.replace('_', ' ').title()}")
            report.append(f"  Current Value: {insight.driver_value:.4f}")
            report.append(f"  Percentile Rank: {insight.percentile:.0f}th")
            report.append(f"  Top 25% Target: {insight.target_25th:.4f}")
            report.append(f"  Improvement Needed: {insight.improvement_needed_25th:+.4f}")
            report.append(f"  Confidence: {insight.confidence}")
            report.append(f"  → {insight.recommendation}")

        # Metrics NOT validated
        report.append("\n")
        report.append("METRICS NOT YET VALIDATED:")
        report.append("-" * 80)
        report.append("The following metrics are tracked but NOT statistically")
        report.append("validated for coaching recommendations (insufficient evidence):")
        report.append("")
        for metric in self.unvalidated_metrics:
            report.append(f"  - {metric.replace('_', ' ').title()}")
        report.append("")
        report.append("These metrics may become actionable with larger sample sizes.")

        # Footer
        report.append("")
        report.append("="*80)
        report.append("Analysis Method: Percentile-based comparison")
        report.append("Sample Size: n=16 drivers")
        report.append("Validation: See STATISTICAL_VALIDATION_REPORT.md")
        report.append("="*80)

        return "\n".join(report)

    def get_track_leaderboard(
        self,
        race_name: str,
        metric: str
    ) -> pd.DataFrame:
        """
        Generate percentile leaderboard for a specific metric.

        Args:
            race_name: Race identifier
            metric: Metric name (must be validated)

        Returns:
            DataFrame with rankings
        """
        if metric not in self.validated_metrics:
            raise ValueError(
                f"Metric '{metric}' is not validated. "
                f"Use only: {list(self.validated_metrics.keys())}"
            )

        data = self.load_race_data(race_name)

        if metric not in data.columns:
            raise ValueError(f"Metric '{metric}' not available for {race_name}")

        metadata = self.validated_metrics[metric]

        # Calculate percentiles
        data['percentile'] = data[metric].apply(
            lambda x: self.calculate_percentile(
                x, data[metric].dropna(), metadata['lower_is_better']
            )
        )

        # Sort
        if metadata['lower_is_better']:
            data_sorted = data.sort_values(metric)
        else:
            data_sorted = data.sort_values(metric, ascending=False)

        # Select columns
        leaderboard = data_sorted[[
            'driver_number',
            metric,
            'percentile',
            'AVERAGE_SECONDS'
        ]].copy()

        leaderboard['rank'] = range(1, len(leaderboard) + 1)

        return leaderboard[['rank', 'driver_number', metric, 'percentile', 'AVERAGE_SECONDS']]


def main():
    """Demonstration of safe coaching implementation."""

    analyzer = SafeCoachingAnalyzer(data_dir="data")

    # Example 1: Individual driver insights
    print("\n" + "="*80)
    print("EXAMPLE 1: Individual Driver Analysis")
    print("="*80 + "\n")

    insights = analyzer.generate_driver_insights(
        driver_number=7,
        race_name="barber_r1"
    )

    for insight in insights:
        print(f"Metric: {insight.metric_name}")
        print(f"  Value: {insight.driver_value:.4f}")
        print(f"  Percentile: {insight.percentile:.0f}th")
        print(f"  Recommendation: {insight.recommendation}")
        print()

    # Example 2: Driver comparison
    print("\n" + "="*80)
    print("EXAMPLE 2: Safe Driver Comparison")
    print("="*80 + "\n")

    comparison = analyzer.compare_drivers_safely(
        driver_a=7,
        driver_b=13,
        race_name="barber_r1"
    )

    print(f"Driver #{comparison['driver_a']}: {comparison['laptime_a']:.3f} sec")
    print(f"Driver #{comparison['driver_b']}: {comparison['laptime_b']:.3f} sec")
    print(f"Gap: {comparison['gap_seconds']:+.3f} sec")
    print(f"\n⚠️  {comparison['warning']}\n")

    print("Validated Metric Differences:")
    for diff in comparison['validated_differences']:
        print(f"\n{diff['metric']}:")
        print(f"  Driver #{comparison['driver_a']}: {diff['driver_a_value']:.4f} "
              f"({diff['driver_a_percentile']:.0f}th %ile)")
        print(f"  Driver #{comparison['driver_b']}: {diff['driver_b_value']:.4f} "
              f"({diff['driver_b_percentile']:.0f}th %ile)")

    # Example 3: Full report
    print("\n" + "="*80)
    print("EXAMPLE 3: Complete Coaching Report")
    print("="*80 + "\n")

    report = analyzer.generate_coaching_report(
        driver_number=7,
        race_name="barber_r1"
    )

    print(report)

    # Example 4: Leaderboard
    print("\n" + "="*80)
    print("EXAMPLE 4: Metric Leaderboard")
    print("="*80 + "\n")

    leaderboard = analyzer.get_track_leaderboard(
        race_name="barber_r1",
        metric="braking_point_consistency"
    )

    print("Braking Point Consistency Leaderboard:")
    print(leaderboard.to_string(index=False))


if __name__ == "__main__":
    main()
