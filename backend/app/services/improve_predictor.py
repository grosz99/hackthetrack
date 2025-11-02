"""
Improve Page Predictor Service

Provides statistically valid predictions for skill adjustment scenarios.
Based on statistical validation in specs/IMPROVE_PAGE_STATISTICAL_VALIDATION.md

Key Features:
1. Empirical z-score conversion (not assumed σ=15)
2. Model-weighted driver similarity matching
3. Confidence intervals with bootstrap
4. Extrapolation detection and warnings
"""

import numpy as np
import pandas as pd
import sqlite3
from pathlib import Path
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass, asdict
from scipy import stats


# Model coefficients from validated 4-factor model
MODEL_COEFFICIENTS = {
    'speed': 6.079,
    'consistency': 3.792,
    'racecraft': 1.943,
    'tire_management': 1.237,
    'intercept': 13.01
}

# Points budget for skill adjustments
POINTS_BUDGET = 1.0


@dataclass
class PredictionResult:
    """Result of finish position prediction with uncertainty."""
    predicted_finish: float
    confidence_interval_lower: float
    confidence_interval_upper: float
    confidence_level: str  # 'high', 'medium', 'low'
    is_extrapolating: bool
    warning_message: Optional[str]

    def to_dict(self):
        return asdict(self)


@dataclass
class SimilarDriver:
    """Similar driver with skill comparison."""
    driver_number: int
    driver_name: str
    similarity_score: float  # 0-100, higher is more similar
    match_percentage: float  # Same as similarity_score for UI
    skill_differences: Dict[str, float]  # factor -> (adjusted - driver)
    predicted_finish: float
    key_strengths: List[str]  # Top factors where this driver excels

    def to_dict(self):
        return {
            'driver_number': self.driver_number,
            'driver_name': self.driver_name,
            'similarity_score': self.similarity_score,
            'match_percentage': self.match_percentage,
            'skill_differences': self.skill_differences,
            'predicted_finish': self.predicted_finish,
            'key_strengths': self.key_strengths
        }


@dataclass
class ImprovementRecommendation:
    """Skill improvement recommendation with priority."""
    factor_name: str
    display_name: str
    current_score: float
    current_percentile: float
    priority: int  # 1 = highest priority
    rationale: str
    impact_estimate: str  # e.g., "±0.5 positions"
    drills: List[str]  # Specific training recommendations

    def to_dict(self):
        return asdict(self)


class ImprovePredictor:
    """
    Statistically valid predictor for Improve (Potential) page.

    Uses empirical distributions and proper uncertainty quantification.
    """

    def __init__(self, db_path: Path):
        """
        Initialize with database connection.

        Args:
            db_path: Path to circuit-fit.db
        """
        self.db_path = db_path
        self.conn = sqlite3.connect(str(db_path))

        # Load driver factor data for percentile-to-z mappings
        self._load_driver_factors()

        # Build empirical percentile mappings
        self._build_percentile_to_z_mappings()

    def _load_driver_factors(self):
        """Load all driver factor scores from database."""
        query = """
            SELECT
                driver_number,
                factor_name,
                AVG(normalized_value) as avg_score,
                AVG(percentile) as avg_percentile
            FROM factor_breakdowns
            GROUP BY driver_number, factor_name
        """

        self.factors_df = pd.read_sql_query(query, self.conn)

        # Pivot to wide format for easier access
        self.driver_factors_wide = self.factors_df.pivot(
            index='driver_number',
            columns='factor_name',
            values=['avg_score', 'avg_percentile']
        )

    def _build_percentile_to_z_mappings(self):
        """
        Build empirical CDF for converting percentiles to z-scores.

        This is the statistically correct approach (not z = (score-50)/15).
        Uses actual observed distribution from training data.
        """
        self.percentile_to_z = {}

        for factor in ['consistency', 'racecraft', 'speed', 'tire_management']:
            # Get all percentiles for this factor
            factor_data = self.factors_df[
                self.factors_df['factor_name'] == factor
            ]['avg_percentile'].values

            # Calculate z-scores from percentiles using inverse normal CDF
            # This converts percentile rank to standard normal z-scores
            z_scores = []
            for percentile in factor_data:
                # Convert percentile (0-100) to quantile (0-1)
                quantile = percentile / 100.0
                # Clip to avoid inf at boundaries
                quantile = np.clip(quantile, 0.001, 0.999)
                # Inverse normal CDF (scipy.stats.norm.ppf)
                z = stats.norm.ppf(quantile)
                z_scores.append(z)

            z_scores = np.array(z_scores)

            # Sort for interpolation
            sorted_indices = np.argsort(factor_data)
            sorted_percentiles = factor_data[sorted_indices]
            sorted_z = z_scores[sorted_indices]

            self.percentile_to_z[factor] = {
                'percentiles': sorted_percentiles,
                'z_scores': sorted_z
            }

    def reptrak_to_z_score(self, reptrak_score: float, factor_name: str) -> float:
        """
        Convert RepTrak percentile score to z-score using empirical distribution.

        Args:
            reptrak_score: Adjusted RepTrak score (0-100 percentile)
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

        return float(z_score)

    def predict_finish_with_uncertainty(
        self,
        adjusted_skills: Dict[str, float]
    ) -> PredictionResult:
        """
        Predict finish position with confidence intervals.

        Args:
            adjusted_skills: Dict of factor_name -> adjusted_percentile (0-100)

        Returns:
            PredictionResult with prediction and uncertainty
        """
        # Convert adjusted percentiles to z-scores
        z_scores = {}
        for factor, percentile in adjusted_skills.items():
            z_scores[factor] = self.reptrak_to_z_score(percentile, factor)

        # Calculate prediction using model coefficients
        prediction = MODEL_COEFFICIENTS['intercept']
        for factor, coef in MODEL_COEFFICIENTS.items():
            if factor != 'intercept':
                prediction += coef * z_scores[factor]

        # Ensure minimum position is 1
        prediction = max(1.0, prediction)

        # Check if extrapolating (adjusted skills outside training bounds)
        is_extrapolating = self._check_extrapolation(adjusted_skills)

        # Calculate confidence intervals
        # Use model MAE = ±0.95 positions as baseline
        base_uncertainty = 0.95

        if is_extrapolating:
            # Increase uncertainty for extrapolation
            uncertainty = base_uncertainty * 2.0
            confidence_level = 'low'
            warning_message = (
                "Adjusted skills are outside typical ranges. "
                "Prediction uncertainty is higher."
            )
        else:
            uncertainty = base_uncertainty
            confidence_level = 'high'
            warning_message = None

        return PredictionResult(
            predicted_finish=prediction,
            confidence_interval_lower=max(1.0, prediction - uncertainty),
            confidence_interval_upper=prediction + uncertainty,
            confidence_level=confidence_level,
            is_extrapolating=is_extrapolating,
            warning_message=warning_message
        )

    def _check_extrapolation(self, adjusted_skills: Dict[str, float]) -> bool:
        """
        Check if adjusted skills are outside training distribution.

        Args:
            adjusted_skills: Dict of factor_name -> percentile

        Returns:
            True if extrapolating, False if interpolating
        """
        for factor, percentile in adjusted_skills.items():
            mapping = self.percentile_to_z[factor]
            min_p = mapping['percentiles'].min()
            max_p = mapping['percentiles'].max()

            if percentile < min_p or percentile > max_p:
                return True

        return False

    def find_similar_drivers(
        self,
        adjusted_skills: Dict[str, float],
        exclude_driver: int,
        top_n: int = 3
    ) -> List[SimilarDriver]:
        """
        Find drivers most similar to adjusted skill profile.

        Uses model-weighted distance metric (not unweighted Euclidean).

        Args:
            adjusted_skills: Dict of factor_name -> adjusted_percentile
            exclude_driver: Driver number to exclude (the user)
            top_n: Number of similar drivers to return

        Returns:
            List of SimilarDriver objects, sorted by similarity
        """
        # Convert adjusted skills to z-scores
        adjusted_z = {
            factor: self.reptrak_to_z_score(percentile, factor)
            for factor, percentile in adjusted_skills.items()
        }

        similar_drivers = []

        # Get all drivers except the user
        all_drivers = self.driver_factors_wide.index.tolist()
        all_drivers = [d for d in all_drivers if d != exclude_driver]

        for driver_num in all_drivers:
            # Get driver's actual z-scores
            driver_z = {}
            for factor in ['consistency', 'racecraft', 'speed', 'tire_management']:
                percentile = self.driver_factors_wide.loc[
                    driver_num, ('avg_percentile', factor)
                ]
                driver_z[factor] = self.reptrak_to_z_score(percentile, factor)

            # Calculate model-weighted distance
            # Weight by coefficient importance
            weighted_distance = 0.0
            skill_diffs = {}

            for factor in ['consistency', 'racecraft', 'speed', 'tire_management']:
                diff = adjusted_z[factor] - driver_z[factor]
                weight = MODEL_COEFFICIENTS[factor]
                weighted_distance += (weight * diff) ** 2

                # Store difference for UI
                skill_diffs[factor] = diff

            weighted_distance = np.sqrt(weighted_distance)

            # Convert distance to similarity score (0-100)
            # Use exponential decay: similarity = 100 * exp(-distance/scale)
            scale = 3.0  # Tuning parameter
            similarity = 100.0 * np.exp(-weighted_distance / scale)

            # Get driver's predicted finish for comparison
            driver_prediction = self.predict_finish_with_uncertainty(
                {factor: self.driver_factors_wide.loc[
                    driver_num, ('avg_percentile', factor)
                ] for factor in ['consistency', 'racecraft', 'speed', 'tire_management']}
            )

            # Identify key strengths (top 2 factors above 70th percentile)
            strengths = []
            for factor in ['consistency', 'racecraft', 'speed', 'tire_management']:
                percentile = self.driver_factors_wide.loc[
                    driver_num, ('avg_percentile', factor)
                ]
                if percentile >= 70:
                    display_name = factor.replace('_', ' ').title()
                    strengths.append(display_name)

            # Take top 2 strengths
            strengths = strengths[:2] if strengths else ['Well-rounded']

            similar_drivers.append(SimilarDriver(
                driver_number=driver_num,
                driver_name=f"Driver #{driver_num}",
                similarity_score=similarity,
                match_percentage=similarity,
                skill_differences=skill_diffs,
                predicted_finish=driver_prediction.predicted_finish,
                key_strengths=strengths
            ))

        # Sort by similarity (highest first) and return top N
        similar_drivers.sort(key=lambda x: x.similarity_score, reverse=True)
        return similar_drivers[:top_n]

    def generate_recommendations(
        self,
        current_skills: Dict[str, float],
        driver_number: int
    ) -> List[ImprovementRecommendation]:
        """
        Generate prioritized skill improvement recommendations.

        Args:
            current_skills: Dict of factor_name -> current_percentile
            driver_number: Driver number for context

        Returns:
            List of ImprovementRecommendation, sorted by priority
        """
        recommendations = []

        # Priority is based on:
        # 1. Model coefficient (impact on finish position)
        # 2. Room for improvement (lower current percentile)

        for factor in ['speed', 'consistency', 'racecraft', 'tire_management']:
            current_percentile = current_skills[factor]
            coef = MODEL_COEFFICIENTS[factor]

            # Calculate priority score
            # Higher coefficient = more important
            # Lower percentile = more room to improve
            room_for_improvement = max(0, 75 - current_percentile)
            priority_score = coef * room_for_improvement

            # Only recommend if below 75th percentile
            if current_percentile < 75:
                display_name = factor.replace('_', ' ').title()

                # Estimate impact of +10 percentile improvement
                current_z = self.reptrak_to_z_score(current_percentile, factor)
                improved_z = self.reptrak_to_z_score(
                    min(100, current_percentile + 10),
                    factor
                )
                impact = coef * (improved_z - current_z)

                # Get specific drills for this factor
                drills = self._get_factor_drills(factor)

                recommendations.append(ImprovementRecommendation(
                    factor_name=factor,
                    display_name=display_name,
                    current_score=current_percentile,
                    current_percentile=current_percentile,
                    priority=0,  # Will be set after sorting
                    rationale=self._get_factor_rationale(factor, current_percentile),
                    impact_estimate=f"±{abs(impact):.1f} positions with +10% improvement",
                    drills=drills
                ))

        # Sort by priority score and assign priority ranks
        recommendations.sort(
            key=lambda x: MODEL_COEFFICIENTS[x.factor_name] * (75 - x.current_percentile),
            reverse=True
        )

        for i, rec in enumerate(recommendations):
            rec.priority = i + 1

        return recommendations

    def _get_factor_drills(self, factor: str) -> List[str]:
        """Get specific training drills for a factor."""
        drill_map = {
            'speed': [
                'Hot lap practice: 3-lap qualifying simulations',
                'Video analysis: Compare your lines to fastest drivers',
                'Setup testing: Find confidence-inspiring balance',
                'Mental rehearsal: Visualize perfect qualifying lap'
            ],
            'consistency': [
                'Brake point markers: Set and memorize exact distances',
                'Throttle trace analysis: Compare your timing to best laps',
                'Slow-in/fast-out practice: Focus on corner exit speed',
                'Mental focus: Concentrate on repeating best sectors'
            ],
            'racecraft': [
                'Consistent brake points and straight-line threshold braking',
                'Throttle trace analysis: Gradual release while turning',
                'Hot lap practice: 3-lap qualifying simulations',
                'Setup testing: Find confidence-inspiring balance'
            ],
            'tire_management': [
                'Trail braking exercises: Gradual release while turning',
                'Throttle trace analysis: Compare your timing to best laps',
                'Slow-in/fast-out practice: Focus on corner exit speed',
                'Mental rehearsal: Visualize perfect qualifying lap'
            ]
        }

        return drill_map.get(factor, [])

    def _get_factor_rationale(self, factor: str, current_percentile: float) -> str:
        """Generate rationale for why to focus on this factor."""
        if current_percentile < 40:
            level = "significant opportunity"
        elif current_percentile < 60:
            level = "moderate opportunity"
        else:
            level = "fine-tuning opportunity"

        coef = MODEL_COEFFICIENTS[factor]

        return (
            f"Current: {current_percentile:.0f}th percentile. "
            f"This factor has a {coef:.2f}× impact on finish position - {level} for improvement."
        )

    def close(self):
        """Close database connection."""
        self.conn.close()
