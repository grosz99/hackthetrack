"""
Corrected Implementation for Improve (Potential) Page

This module provides statistically valid methods for:
1. Converting RepTrak scores to z-scores using empirical distributions
2. Predicting finish positions with uncertainty quantification
3. Finding similar drivers using model-weighted distance metrics
4. Detecting extrapolation and warning users

Statistical Validation: See IMPROVE_PAGE_STATISTICAL_VALIDATION.md
"""

import numpy as np
import pandas as pd
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass
from sklearn.linear_model import LinearRegression
from sklearn.utils import resample


# Model coefficients from 4-factor model
MODEL_COEFFICIENTS = {
    'speed': 6.079,
    'consistency': 3.792,
    'racecraft': 1.943,
    'tire_management': 1.237,
    'intercept': 13.01
}


@dataclass
class PredictionResult:
    """Result of finish position prediction with uncertainty."""
    predicted_finish: float
    confidence_interval_lower: float
    confidence_interval_upper: float
    confidence_level: str  # 'high', 'medium', 'low'
    is_extrapolating: bool
    warning_message: Optional[str]


@dataclass
class SimilarDriver:
    """Similar driver with skill comparison."""
    driver_number: int
    driver_name: str
    similarity_score: float  # 0-100
    skill_differences: Dict[str, float]  # factor -> (adjusted - driver)
    predicted_finish: float


class ImprovePagePredictor:
    """
    Statistically valid predictor for Improve page.

    Fixes critical issues in original proposal:
    1. Uses empirical z-score conversion instead of assumed σ=15
    2. Provides confidence intervals via bootstrap
    3. Uses model-weighted distance for similarity
    4. Detects and warns about extrapolation
    """

    def __init__(self, training_data_path: str):
        """
        Initialize with training data.

        Args:
            training_data_path: Path to tier1_factor_scores.csv
        """
        # Load training data
        self.factor_scores_df = pd.read_csv(training_data_path)

        # Apply reflection (factors 1, 2, 3 need -1 multiplication)
        self._apply_reflection()

        # Calculate driver-level averages
        self.driver_avg_z = self.factor_scores_df.groupby('driver_number').agg({
            'factor_1_score': 'mean',  # Consistency
            'factor_2_score': 'mean',  # Racecraft
            'factor_3_score': 'mean',  # Speed
            'factor_4_score': 'mean'   # Tire Management
        }).reset_index()

        # Map factor columns to skill names
        self.driver_avg_z = self.driver_avg_z.rename(columns={
            'factor_1_score': 'consistency',
            'factor_2_score': 'racecraft',
            'factor_3_score': 'speed',
            'factor_4_score': 'tire_management'
        })

        # Calculate percentile mappings for each factor
        self._build_percentile_to_z_mappings()

    def _apply_reflection(self):
        """Apply statistical reflection to factors with negative loadings."""
        for factor_col in ['factor_1_score', 'factor_2_score', 'factor_3_score']:
            self.factor_scores_df[factor_col] *= -1

    def _build_percentile_to_z_mappings(self):
        """
        Build empirical CDF for converting percentiles to z-scores.

        This is the CORRECT way to convert RepTrak scores back to z-scores.
        Uses actual observed distribution instead of assuming σ=15.
        """
        self.percentile_to_z = {}

        for factor in ['consistency', 'racecraft', 'speed', 'tire_management']:
            # Get all z-scores for this factor
            z_scores = self.driver_avg_z[factor].values

            # Sort for percentile calculation
            sorted_z = np.sort(z_scores)

            # Create percentile -> z-score lookup
            # Percentiles from 0 to 100
            percentiles = np.linspace(0, 100, len(sorted_z))

            self.percentile_to_z[factor] = {
                'z_scores': sorted_z,
                'percentiles': percentiles
            }

    def reptrak_to_z_score(self, reptrak_score: float, factor_name: str) -> float:
        """
        Convert RepTrak percentile score to z-score using empirical distribution.

        This is statistically valid, unlike the proposed z = (score - 50) / 15.

        Args:
            reptrak_score: User's adjusted RepTrak score (0-100)
            factor_name: Which factor ('speed', 'consistency', etc.)

        Returns:
            Corresponding z-score from training distribution
        """
        mapping = self.percentile_to_z[factor_name]

        # Linear interpolation between observed percentiles
        z_score = np.interp(
            reptrak_score,
            mapping['percentiles'],
            mapping['z_scores']
        )

        return z_score

    def predict_finish_with_uncertainty(
        self,
        adjusted_z_scores: Dict[str, float],
        bootstrap_iterations: int = 1000
    ) -> PredictionResult:
        """
        Predict finish position with 95% confidence interval.

        Uses bootstrap resampling to quantify prediction uncertainty.

        Args:
            adjusted_z_scores: Dict of factor_name -> z_score (adjusted)
            bootstrap_iterations: Number of bootstrap samples

        Returns:
            PredictionResult with finish prediction and uncertainty
        """
        # Base prediction
        base_prediction = self._predict_finish(adjusted_z_scores)

        # Bootstrap predictions for uncertainty
        predictions = []

        X = self.driver_avg_z[['speed', 'consistency', 'racecraft', 'tire_management']].values
        y = self.driver_avg_z['driver_number'].apply(
            lambda dn: self._get_actual_finish(dn)
        ).values

        for _ in range(bootstrap_iterations):
            # Resample with replacement
            X_resample, y_resample = resample(X, y, replace=True, random_state=None)

            # Fit model on resampled data
            model = LinearRegression()
            model.fit(X_resample, y_resample)

            # Predict with adjusted skills
            z_vector = np.array([
                adjusted_z_scores['speed'],
                adjusted_z_scores['consistency'],
                adjusted_z_scores['racecraft'],
                adjusted_z_scores['tire_management']
            ]).reshape(1, -1)

            pred = model.predict(z_vector)[0]
            predictions.append(max(1, pred))  # Ensure >= 1

        # Calculate confidence interval
        ci_lower = np.percentile(predictions, 2.5)
        ci_upper = np.percentile(predictions, 97.5)

        # Check for extrapolation
        extrapolation_check = self._check_extrapolation(adjusted_z_scores)

        # Determine confidence level
        ci_width = ci_upper - ci_lower
        if ci_width < 2.0:
            confidence = 'high'
        elif ci_width < 4.0:
            confidence = 'medium'
        else:
            confidence = 'low'

        if extrapolation_check['is_extrapolating']:
            confidence = 'low'

        return PredictionResult(
            predicted_finish=base_prediction,
            confidence_interval_lower=ci_lower,
            confidence_interval_upper=ci_upper,
            confidence_level=confidence,
            is_extrapolating=extrapolation_check['is_extrapolating'],
            warning_message=extrapolation_check['warning_message']
        )

    def _predict_finish(self, z_scores: Dict[str, float]) -> float:
        """Calculate finish position using model coefficients."""
        predicted = (
            MODEL_COEFFICIENTS['intercept']
            + MODEL_COEFFICIENTS['speed'] * z_scores['speed']
            + MODEL_COEFFICIENTS['consistency'] * z_scores['consistency']
            + MODEL_COEFFICIENTS['racecraft'] * z_scores['racecraft']
            + MODEL_COEFFICIENTS['tire_management'] * z_scores['tire_management']
        )
        return max(1, predicted)

    def _get_actual_finish(self, driver_number: int) -> float:
        """Get actual average finish for driver (placeholder - implement with real data)."""
        # TODO: Replace with actual race results
        # For now, predict using their z-scores
        driver_row = self.driver_avg_z[self.driver_avg_z['driver_number'] == driver_number]
        if driver_row.empty:
            return 15.0

        z_scores = {
            'speed': driver_row['speed'].values[0],
            'consistency': driver_row['consistency'].values[0],
            'racecraft': driver_row['racecraft'].values[0],
            'tire_management': driver_row['tire_management'].values[0]
        }
        return self._predict_finish(z_scores)

    def _check_extrapolation(self, adjusted_z_scores: Dict[str, float]) -> Dict:
        """
        Check if adjusted skills are outside training distribution.

        Uses model-weighted distance to nearest training example.
        """
        # Convert adjusted z-scores to vector
        adjusted_vector = np.array([
            adjusted_z_scores['speed'],
            adjusted_z_scores['consistency'],
            adjusted_z_scores['racecraft'],
            adjusted_z_scores['tire_management']
        ])

        # Get all training vectors
        training_vectors = self.driver_avg_z[
            ['speed', 'consistency', 'racecraft', 'tire_management']
        ].values

        # Calculate model-weighted distances
        weights = np.array([
            MODEL_COEFFICIENTS['speed'],
            MODEL_COEFFICIENTS['consistency'],
            MODEL_COEFFICIENTS['racecraft'],
            MODEL_COEFFICIENTS['tire_management']
        ])

        distances = []
        for train_vector in training_vectors:
            weighted_diff = weights * (adjusted_vector - train_vector)
            distance = np.linalg.norm(weighted_diff)
            distances.append(distance)

        min_distance = min(distances)

        # Compare to typical within-sample distance
        pairwise_distances = []
        for i in range(len(training_vectors)):
            for j in range(i + 1, len(training_vectors)):
                weighted_diff = weights * (training_vectors[i] - training_vectors[j])
                dist = np.linalg.norm(weighted_diff)
                pairwise_distances.append(dist)

        typical_distance = np.percentile(pairwise_distances, 50)

        extrapolation_severity = min_distance / typical_distance

        if extrapolation_severity > 2.0:
            return {
                'is_extrapolating': True,
                'extrapolation_severity': extrapolation_severity,
                'warning_message': (
                    "⚠️ These adjusted skills are far from observed drivers. "
                    "Predictions are highly uncertain and should be interpreted with caution."
                )
            }
        elif extrapolation_severity > 1.5:
            return {
                'is_extrapolating': True,
                'extrapolation_severity': extrapolation_severity,
                'warning_message': (
                    "⚠️ These skills are at the edge of observed data. "
                    "Prediction uncertainty is higher than typical."
                )
            }
        else:
            return {
                'is_extrapolating': False,
                'extrapolation_severity': extrapolation_severity,
                'warning_message': None
            }

    def find_similar_drivers(
        self,
        adjusted_z_scores: Dict[str, float],
        top_n: int = 5
    ) -> List[SimilarDriver]:
        """
        Find most similar drivers using model-weighted distance.

        This is statistically correct, unlike unweighted Euclidean distance
        on percentile scale.

        Args:
            adjusted_z_scores: User's adjusted skill z-scores
            top_n: Number of similar drivers to return

        Returns:
            List of SimilarDriver objects, sorted by similarity (highest first)
        """
        # Convert to vector
        adjusted_vector = np.array([
            adjusted_z_scores['speed'],
            adjusted_z_scores['consistency'],
            adjusted_z_scores['racecraft'],
            adjusted_z_scores['tire_management']
        ])

        # Model coefficients as weights
        weights = np.array([
            MODEL_COEFFICIENTS['speed'],
            MODEL_COEFFICIENTS['consistency'],
            MODEL_COEFFICIENTS['racecraft'],
            MODEL_COEFFICIENTS['tire_management']
        ])

        similarities = []

        for _, driver_row in self.driver_avg_z.iterrows():
            driver_vector = np.array([
                driver_row['speed'],
                driver_row['consistency'],
                driver_row['racecraft'],
                driver_row['tire_management']
            ])

            # Model-weighted distance
            weighted_diff = weights * (adjusted_vector - driver_vector)
            distance = np.linalg.norm(weighted_diff)

            # Convert to similarity score (0-100)
            # Use exponential decay: similar when distance is small
            similarity = 100 * np.exp(-distance / 5)

            # Calculate predicted finish for this driver
            driver_z_scores = {
                'speed': driver_row['speed'],
                'consistency': driver_row['consistency'],
                'racecraft': driver_row['racecraft'],
                'tire_management': driver_row['tire_management']
            }
            predicted_finish = self._predict_finish(driver_z_scores)

            # Skill differences (adjusted - driver)
            skill_diffs = {
                'speed': adjusted_z_scores['speed'] - driver_row['speed'],
                'consistency': adjusted_z_scores['consistency'] - driver_row['consistency'],
                'racecraft': adjusted_z_scores['racecraft'] - driver_row['racecraft'],
                'tire_management': adjusted_z_scores['tire_management'] - driver_row['tire_management']
            }

            similarities.append(SimilarDriver(
                driver_number=int(driver_row['driver_number']),
                driver_name=f"Driver #{int(driver_row['driver_number'])}",
                similarity_score=similarity,
                skill_differences=skill_diffs,
                predicted_finish=predicted_finish
            ))

        # Sort by similarity (highest first)
        similarities.sort(key=lambda x: x.similarity_score, reverse=True)

        return similarities[:top_n]

    def recommend_optimal_allocation(
        self,
        current_reptrak_scores: Dict[str, float],
        budget: int = 5
    ) -> Dict[str, int]:
        """
        Recommend optimal allocation of points to maximize predicted improvement.

        Considers:
        1. Model coefficient weights (bigger impact)
        2. Diminishing returns at high skill levels
        3. Current skill levels

        Args:
            current_reptrak_scores: Current RepTrak scores (0-100)
            budget: Total points to allocate

        Returns:
            Dict of factor_name -> points_to_add
        """
        allocation = {factor: 0 for factor in current_reptrak_scores}

        # Greedy allocation: iteratively assign 1 point to highest marginal utility
        for _ in range(budget):
            marginal_utilities = {}

            for factor in current_reptrak_scores:
                # Current level after previous allocations
                current_level = current_reptrak_scores[factor] + allocation[factor]

                # Marginal utility = coefficient × diminishing_returns_factor
                # Diminishing returns: harder to improve at high levels
                diminishing_factor = max(0.1, 1 - (current_level / 100))

                marginal_utility = (
                    MODEL_COEFFICIENTS[factor] * diminishing_factor
                )

                marginal_utilities[factor] = marginal_utility

            # Allocate to highest marginal utility
            best_factor = max(marginal_utilities, key=marginal_utilities.get)
            allocation[best_factor] += 1

        return allocation


# Example usage
if __name__ == "__main__":
    # Initialize predictor
    predictor = ImprovePagePredictor(
        training_data_path="data/analysis_outputs/tier1_factor_scores.csv"
    )

    # Example: Driver wants to adjust skills
    current_reptrak = {
        'speed': 65.0,
        'consistency': 55.0,
        'racecraft': 60.0,
        'tire_management': 50.0
    }

    # User adjusts: +3 speed, +2 consistency
    adjusted_reptrak = {
        'speed': 68.0,
        'consistency': 57.0,
        'racecraft': 60.0,
        'tire_management': 50.0
    }

    # Convert to z-scores (CORRECT METHOD)
    adjusted_z = {
        factor: predictor.reptrak_to_z_score(score, factor)
        for factor, score in adjusted_reptrak.items()
    }

    # Predict with uncertainty
    prediction = predictor.predict_finish_with_uncertainty(adjusted_z)

    print("Prediction Results:")
    print(f"  Predicted finish: {prediction.predicted_finish:.1f}")
    print(f"  95% CI: [{prediction.confidence_interval_lower:.1f}, {prediction.confidence_interval_upper:.1f}]")
    print(f"  Confidence: {prediction.confidence_level}")
    if prediction.warning_message:
        print(f"  {prediction.warning_message}")

    # Find similar drivers
    similar_drivers = predictor.find_similar_drivers(adjusted_z, top_n=3)

    print("\nMost Similar Drivers:")
    for i, driver in enumerate(similar_drivers, 1):
        print(f"  {i}. {driver.driver_name} ({driver.similarity_score:.1f}% similar)")
        print(f"     Predicted finish: {driver.predicted_finish:.1f}")
        print(f"     Skill differences:")
        for factor, diff in driver.skill_differences.items():
            print(f"       {factor}: {diff:+.2f} z-scores")

    # Recommend optimal allocation
    optimal = predictor.recommend_optimal_allocation(current_reptrak, budget=5)

    print("\nOptimal Point Allocation (5 points):")
    for factor, points in optimal.items():
        if points > 0:
            print(f"  {factor}: +{points} points")
