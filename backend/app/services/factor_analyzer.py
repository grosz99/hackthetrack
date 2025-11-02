"""
Factor Analyzer Service
Analyzes and breaks down driver skill factors into underlying variables.
Uses reflected factor scores for statistically correct interpretation.
"""

import pandas as pd
import numpy as np
import sqlite3
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from pydantic import BaseModel, Field


# Mapping of factor numbers to skill names based on factor loadings analysis
FACTOR_MAPPING = {
    "factor_1": "consistency",
    "factor_2": "racecraft",
    "factor_3": "speed",
    "factor_4": "tire_management",
}

# Factors that need reflection (multiplication by -1) due to negative loadings
# Based on factor analysis: Factors 1, 2, 3 have dominant negative loadings
# Factor 4 has positive loadings and does not need reflection
FACTORS_TO_REFLECT = {
    "factor_1_score": True,   # Consistency: dominant variables have negative loadings
    "factor_2_score": True,   # Racecraft: dominant variables have negative loadings
    "factor_3_score": True,   # Speed: all variables have negative loadings
    "factor_4_score": False,  # Tire Management: positive loadings, correct sign
    "factor_5_score": False,  # Not interpreted, keep as-is
}

# Factor variable mappings with weights
FACTOR_VARIABLES = {
    "speed": {
        "factor_column": "factor_3_score",
        "variables": [
            ("qualifying_pace", "Qualifying Speed", 0.35),
            ("best_race_lap", "Fastest Lap Ability", 0.30),
            ("avg_top10_pace", "Sustained Pace", 0.35)
        ],
        "description": "Pure speed - how fast the driver can go in qualifying and race conditions",
        "racing_explanation": "Speed shows how fast you can push the car. High qualifying speed means you can extract maximum performance in a single lap. Fastest lap ability shows you can hit that peak speed during the race. Sustained pace means you can keep that speed consistent over multiple laps."
    },

    "consistency": {
        "factor_column": "factor_1_score",
        "variables": [
            ("stint_consistency", "Lap-to-Lap Consistency", 0.35),
            ("sector_consistency", "Sector Consistency", 0.25),
            ("braking_consistency", "Braking Consistency", 0.20),
            ("position_changes", "Position Stability", 0.20)
        ],
        "description": "Ability to hit the same lap times repeatedly without mistakes",
        "racing_explanation": "Consistency is about hitting your marks every lap. Lap-to-lap consistency means similar lap times throughout a stint. Sector consistency shows you're nailing each section of track the same way. Braking consistency means hitting braking points precisely. Position stability shows you're not making mistakes that cost positions."
    },

    "racecraft": {
        "factor_column": "factor_2_score",
        "variables": [
            ("positions_gained", "Net Positions Gained", 0.30),
            ("position_changes", "Wheel-to-Wheel Racing", 0.25),
            ("performance_normalized", "Race Pace vs Competition", 0.25),
            ("qualifying_pace", "Quali vs Race Gap", 0.20)
        ],
        "description": "Racing IQ - overtaking, defending, and race management skills",
        "racing_explanation": "Racecraft is your ability to race others. Net positions gained shows if you're moving forward through the field. Wheel-to-wheel racing measures how often you're making passes or defending. Race pace vs competition shows if you're faster than those around you. Quali vs race gap indicates if you race better than you qualify (or vice versa)."
    },

    "tire_management": {
        "factor_column": "factor_4_score",
        "variables": [
            ("pace_degradation", "Tire Wear Management", 0.20),
            ("late_stint_perf", "Late Stint Speed", 0.20),
            ("early_vs_late_pace", "Stint Consistency", 0.25),
            ("steering_smoothness", "Steering Smoothness", 0.175),
            ("lateral_g_utilization", "Cornering G-Force Usage", 0.175)
        ],
        "description": "Managing tire wear to maintain pace throughout a stint",
        "racing_explanation": "Tire management is keeping your tires alive while staying fast. Tire wear management shows how well you preserve the rubber. Late stint speed means you're still quick even on old tires. Stint consistency shows your pace doesn't fall off a cliff as the stint goes on. Steering smoothness means gentle inputs that preserve tire life. Cornering G-force usage shows how hard you push through turns."
    }
}


class VariableBreakdown(BaseModel):
    """Individual variable contribution to a factor."""
    name: str
    display_name: str
    raw_value: float
    normalized_value: float = Field(..., ge=0, le=100)
    weight: float
    contribution: float
    percentile: float


class FactorBreakdown(BaseModel):
    """Complete breakdown of a skill factor."""
    factor_name: str
    overall_score: float
    percentile: float
    variables: List[VariableBreakdown]
    explanation: str
    strongest_area: str
    weakest_area: str


class DriverComparison(BaseModel):
    """Comparison data for a single driver."""
    driver_number: int
    driver_name: str
    factor_score: float
    percentile: float
    variables: Dict[str, float]  # variable_name -> normalized_value


class FactorComparison(BaseModel):
    """Complete factor comparison analysis."""
    factor_name: str
    user_driver: DriverComparison
    top_drivers: List[DriverComparison]
    insights: List[str]


class FactorAnalyzer:
    """Service for analyzing and breaking down skill factors."""

    def __init__(self, data_path: Path, db_path: Path):
        self.data_path = data_path
        self.db_path = db_path

        # Load features data
        features_path = data_path / "analysis_outputs" / "all_races_tier1_features.csv"
        self.features_df = pd.read_csv(features_path)

        # Load telemetry features and merge
        telemetry_path = data_path / "analysis_outputs" / "all_races_telemetry_features.csv"
        if telemetry_path.exists():
            telemetry_df = pd.read_csv(telemetry_path)
            # Merge telemetry features (steering_smoothness and lateral_g_utilization)
            self.features_df = pd.merge(
                self.features_df,
                telemetry_df[['race', 'driver_number', 'steering_smoothness', 'lateral_g_utilization']],
                on=['race', 'driver_number'],
                how='left'  # Left join to keep all tier-1 data
            )
            print(f"Merged telemetry features: {len(self.features_df)} observations")
        else:
            print(f"Warning: Telemetry features not found at {telemetry_path}")
            # Add dummy columns filled with NaN
            self.features_df['steering_smoothness'] = np.nan
            self.features_df['lateral_g_utilization'] = np.nan

        # Load factor scores and apply reflection
        factor_scores_path = data_path / "analysis_outputs" / "tier1_factor_scores.csv"
        self.factor_scores_df = pd.read_csv(factor_scores_path)
        self._apply_factor_reflection()

    def _apply_factor_reflection(self):
        """
        Apply reflection to factors with negative loadings.

        This is a standard factor analysis procedure: when dominant variables
        have negative loadings on a factor, multiply the factor scores by -1
        to make interpretation intuitive (higher score = better performance).

        Statistical justification:
        - Factor 1 (consistency): braking_consistency loads at -0.934
        - Factor 2 (racecraft): positions_gained loads at -0.857
        - Factor 3 (speed): all speed metrics have negative loadings (-0.69 to -0.76)
        - Factor 4 (tire_mgmt): positive loadings (+0.47 to +0.62), no reflection needed
        """
        for factor_col, should_reflect in FACTORS_TO_REFLECT.items():
            if should_reflect and factor_col in self.factor_scores_df.columns:
                self.factor_scores_df[factor_col] = -1 * self.factor_scores_df[factor_col]
                print(f"Reflected {factor_col} (multiplied by -1 due to negative loadings)")

    def calculate_all_factors(self):
        """Pre-calculate all factor breakdowns for all drivers."""
        # For hackathon: only include drivers with telemetry data
        driver_telemetry = self.features_df.groupby('driver_number')['steering_smoothness'].mean()
        drivers_with_telemetry = driver_telemetry[driver_telemetry > 0].index.tolist()

        print(f"Total drivers: {len(self.features_df['driver_number'].unique())}")
        print(f"Drivers with telemetry: {len(drivers_with_telemetry)}")
        print(f"Excluding {len(self.features_df['driver_number'].unique()) - len(drivers_with_telemetry)} drivers without telemetry")

        drivers = drivers_with_telemetry
        factors = list(FACTOR_VARIABLES.keys())

        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # Create tables if they don't exist
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS factor_breakdowns (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                driver_number INTEGER NOT NULL,
                factor_name TEXT NOT NULL,
                variable_name TEXT NOT NULL,
                variable_display_name TEXT NOT NULL,
                raw_value REAL,
                normalized_value REAL,
                weight REAL,
                contribution REAL,
                percentile REAL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(driver_number, factor_name, variable_name)
            )
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS factor_comparisons (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                driver_number INTEGER NOT NULL,
                factor_name TEXT NOT NULL,
                top_driver_1 INTEGER,
                top_driver_2 INTEGER,
                top_driver_3 INTEGER,
                insights TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(driver_number, factor_name)
            )
        """)

        # Clear existing data
        cursor.execute("DELETE FROM factor_breakdowns")
        cursor.execute("DELETE FROM factor_comparisons")

        for driver_number in drivers:
            print(f"Processing driver #{driver_number}...")

            for factor_name in factors:
                try:
                    # Calculate breakdown
                    breakdown = self._calculate_factor_breakdown(driver_number, factor_name)

                    # Store breakdown variables
                    for var in breakdown.variables:
                        cursor.execute("""
                            INSERT OR REPLACE INTO factor_breakdowns
                            (driver_number, factor_name, variable_name, variable_display_name,
                             raw_value, normalized_value, weight, contribution, percentile)
                            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                        """, (
                            int(driver_number), factor_name, var.name, var.display_name,
                            float(var.raw_value), float(var.normalized_value), float(var.weight),
                            float(var.contribution), float(var.percentile)
                        ))

                    # Calculate and store comparison
                    comparison = self._calculate_factor_comparison(driver_number, factor_name)

                    cursor.execute("""
                        INSERT OR REPLACE INTO factor_comparisons
                        (driver_number, factor_name, top_driver_1, top_driver_2, top_driver_3, insights)
                        VALUES (?, ?, ?, ?, ?, ?)
                    """, (
                        int(driver_number), factor_name,
                        int(comparison.top_drivers[0].driver_number) if len(comparison.top_drivers) > 0 else None,
                        int(comparison.top_drivers[1].driver_number) if len(comparison.top_drivers) > 1 else None,
                        int(comparison.top_drivers[2].driver_number) if len(comparison.top_drivers) > 2 else None,
                        "\n".join(comparison.insights)
                    ))

                except Exception as e:
                    print(f"Error processing driver {driver_number}, factor {factor_name}: {e}")

        conn.commit()
        conn.close()
        print("All factors calculated and stored with reflected scores!")

    def _calculate_factor_breakdown(self, driver_number: int, factor_name: str) -> FactorBreakdown:
        """
        Calculate detailed breakdown for a driver's factor using reflected scores.

        Uses the reflected factor scores directly for overall_score, then converts
        to percentiles only for display purposes. This maintains statistical validity
        while providing intuitive 0-100 scale for users.
        """
        factor_config = FACTOR_VARIABLES[factor_name]
        factor_column = factor_config["factor_column"]

        # Get driver's reflected factor score (from factor analysis)
        driver_factor_data = self.factor_scores_df[
            self.factor_scores_df['driver_number'] == driver_number
        ]

        if driver_factor_data.empty:
            # If no factor score available, calculate as average across races
            overall_factor_score = 0.0
        else:
            # Average reflected factor score across all races for this driver
            overall_factor_score = driver_factor_data[factor_column].mean()

        # Calculate percentile of the reflected factor score for display
        all_driver_scores = self.factor_scores_df.groupby('driver_number')[factor_column].mean()
        factor_percentile = (all_driver_scores < overall_factor_score).sum() / len(all_driver_scores) * 100

        # Get driver's features (averaged across all races)
        driver_features = self.features_df[
            self.features_df['driver_number'] == driver_number
        ].drop(columns=['race', 'driver_number']).mean()

        # Calculate breakdown for each variable
        variables = []

        for var_name, display_name, weight in factor_config["variables"]:
            raw_value = driver_features.get(var_name, 0)

            # Calculate percentile across all drivers for this variable
            all_values = self.features_df.groupby('driver_number')[var_name].mean()

            # For telemetry features, exclude zero/missing values from percentile calculation
            if var_name in ['steering_smoothness', 'lateral_g_utilization']:
                valid_values = all_values[all_values > 0]
                if len(valid_values) > 0 and raw_value > 0:
                    percentile = (valid_values < raw_value).sum() / len(valid_values) * 100
                else:
                    percentile = 0.0  # No data or driver has no telemetry
            else:
                percentile = (all_values < raw_value).sum() / len(all_values) * 100

            # Use percentile as normalized value for interpretability
            normalized_value = percentile

            # Calculate contribution to overall display score
            contribution = weight * normalized_value

            variables.append(VariableBreakdown(
                name=var_name,
                display_name=display_name,
                raw_value=raw_value,
                normalized_value=normalized_value,
                weight=weight,
                contribution=contribution,
                percentile=percentile
            ))

        # Use factor percentile as overall score for display consistency
        overall_score = factor_percentile

        # Find strongest and weakest
        sorted_vars = sorted(variables, key=lambda x: x.percentile, reverse=True)
        strongest = sorted_vars[0]
        weakest = sorted_vars[-1]

        # Generate racing-focused explanation
        explanation = self._generate_racing_explanation(
            factor_name, strongest, weakest, factor_percentile
        )

        return FactorBreakdown(
            factor_name=factor_name,
            overall_score=overall_score,
            percentile=factor_percentile,
            variables=variables,
            explanation=explanation,
            strongest_area=strongest.display_name,
            weakest_area=weakest.display_name
        )

    def _calculate_factor_comparison(self, driver_number: int, factor_name: str) -> FactorComparison:
        """Calculate comparison vs top 3 drivers using reflected factor scores."""
        # Get user driver breakdown
        user_breakdown = self._calculate_factor_breakdown(driver_number, factor_name)

        # Get top 3 drivers for this factor based on reflected factor scores
        factor_column = FACTOR_VARIABLES[factor_name]["factor_column"]

        # Only compare with drivers that have telemetry data
        driver_telemetry = self.features_df.groupby('driver_number')['steering_smoothness'].mean()
        drivers_with_telemetry = driver_telemetry[driver_telemetry > 0].index.tolist()

        # Calculate average reflected factor score for each driver
        driver_scores = self.factor_scores_df.groupby('driver_number')[factor_column].mean()

        # Filter to only drivers with telemetry and exclude current driver
        driver_scores = driver_scores[
            (driver_scores.index.isin(drivers_with_telemetry)) &
            (driver_scores.index != driver_number)
        ]

        top_3_drivers = driver_scores.nlargest(3)

        top_drivers = []
        for driver_num in top_3_drivers.index:
            top_breakdown = self._calculate_factor_breakdown(driver_num, factor_name)

            # Build variables dict
            variables_dict = {
                var.name: var.normalized_value
                for var in top_breakdown.variables
            }

            top_drivers.append(DriverComparison(
                driver_number=int(driver_num),
                driver_name=f"Driver #{driver_num}",
                factor_score=top_breakdown.overall_score,
                percentile=top_breakdown.percentile,
                variables=variables_dict
            ))

        # Build user driver comparison object
        user_driver = DriverComparison(
            driver_number=driver_number,
            driver_name=f"Driver #{driver_number}",
            factor_score=user_breakdown.overall_score,
            percentile=user_breakdown.percentile,
            variables={var.name: var.normalized_value for var in user_breakdown.variables}
        )

        # Generate insights
        insights = self._generate_comparison_insights(user_breakdown, top_drivers, factor_name)

        return FactorComparison(
            factor_name=factor_name,
            user_driver=user_driver,
            top_drivers=top_drivers,
            insights=insights
        )

    def _generate_racing_explanation(
        self, factor_name: str, strongest: VariableBreakdown,
        weakest: VariableBreakdown, overall_percentile: float
    ) -> str:
        """Generate plain-English, racing-focused explanation."""

        # Overall performance qualifier
        if overall_percentile >= 90:
            qualifier = "elite"
        elif overall_percentile >= 75:
            qualifier = "strong"
        elif overall_percentile >= 50:
            qualifier = "solid"
        elif overall_percentile >= 25:
            qualifier = "developing"
        else:
            qualifier = "needs work"

        explanation = (
            f"Your {factor_name} is {qualifier} (top {100-overall_percentile:.0f}% of the field). "
            f"Your best area is {strongest.display_name} where you rank in the top {100-strongest.percentile:.0f}%. "
            f"Focus on improving {weakest.display_name} - that's where you're giving up the most."
        )

        return explanation

    def _generate_comparison_insights(
        self, user: FactorBreakdown, top_drivers: List[DriverComparison], factor_name: str
    ) -> List[str]:
        """Generate racing-focused insights from comparison."""
        insights = []

        # Compare each variable
        for var in user.variables:
            user_value = var.normalized_value
            top_avg = np.mean([
                driver.variables.get(var.name, 0)
                for driver in top_drivers
            ])

            gap = user_value - top_avg

            if gap > 5:
                insights.append(
                    f"You're actually better than the top 3 in {var.display_name} - keep that strength!"
                )
            elif gap < -10:
                insights.append(
                    f"The top 3 are significantly faster in {var.display_name}. This is your biggest opportunity to improve."
                )

        # If no major gaps found, add generic insight
        if not insights:
            insights.append(
                f"You're competitive with the top drivers in {factor_name}. Small improvements in each area will move you up."
            )

        return insights[:3]  # Limit to top 3 insights


def main():
    """Run batch calculation for all drivers and factors with reflected scores."""
    base_path = Path(__file__).parent.parent.parent.parent
    data_path = base_path / "data"
    db_path = base_path / "circuit-fit.db"

    analyzer = FactorAnalyzer(data_path, db_path)
    analyzer.calculate_all_factors()


if __name__ == "__main__":
    main()
