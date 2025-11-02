"""
Data loading service for Racing Analytics API.
Loads CSV files and dashboard JSON into memory for fast access.
"""

import pandas as pd
import json
import sqlite3
from pathlib import Path
from typing import Dict, List, Optional
from ..models import (
    Track,
    TrackDemand,
    Driver,
    FactorScore,
    DriverStats,
    SeasonStats,
    RaceResult,
)


class DataLoader:
    """Singleton class to load and cache racing data."""

    _instance = None
    _initialized = False

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        if not self._initialized:
            self.base_path = Path(__file__).parent.parent.parent.parent
            self.data_path = self.base_path / "data"
            self.frontend_data_path = self.base_path / "frontend" / "src" / "data"
            self.db_path = self.base_path / "circuit-fit.db"

            self.tracks: Dict[str, Track] = {}
            self.drivers: Dict[int, Driver] = {}
            self.track_demand_profiles: pd.DataFrame = pd.DataFrame()
            self.all_races_features: pd.DataFrame = pd.DataFrame()
            self.factor_scores: pd.DataFrame = pd.DataFrame()
            self.race_results: Dict[str, pd.DataFrame] = {}
            self.lap_analysis: Dict[str, pd.DataFrame] = {}

            # Initialize race log processor
            from .race_log_processor import RaceLogProcessor
            self.race_log_processor = RaceLogProcessor(self.data_path)

            self._load_data()
            self._initialized = True

    def _load_data(self):
        """Load all data sources into memory."""
        print("Loading racing data...")

        # Load dashboard data (pre-calculated driver/track data)
        self._load_dashboard_data()

        # Load track demand profiles
        self._load_track_profiles()

        # Load race features
        self._load_race_features()

        # Load race results and lap analysis
        self._load_race_data()

        print(f"Data loaded: {len(self.tracks)} tracks, {len(self.drivers)} drivers")

    def _get_driver_factor_scores(self, driver_number: int) -> Dict:
        """Get RepTrak-normalized factor scores from database."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        factor_scores = {}
        for factor_name in ["speed", "consistency", "racecraft", "tire_management"]:
            # Get overall score and percentile
            cursor.execute("""
                SELECT AVG(normalized_value), AVG(percentile)
                FROM factor_breakdowns
                WHERE driver_number = ? AND factor_name = ?
            """, (driver_number, factor_name))

            result = cursor.fetchone()
            if result and result[0] is not None:
                score = result[0]
                percentile = result[1]
            else:
                # Fallback to 50 if no data
                score = 50
                percentile = 50

            factor_scores[factor_name] = {
                "score": score,
                "percentile": percentile,
                "z_score": 0  # Z-score not needed for RepTrak normalization
            }

        conn.close()
        return factor_scores

    def _load_dashboard_data(self):
        """Load pre-calculated dashboard data from JSON."""
        json_path = self.frontend_data_path / "dashboardData.json"

        if not json_path.exists():
            print(f"Warning: Dashboard data not found at {json_path}")
            return

        with open(json_path, "r") as f:
            data = json.load(f)

        # Load tracks
        for track_data in data.get("tracks", []):
            track_id = track_data["id"]
            demand = track_data.get("demands", {})

            # Parse length from string like "2.38 miles" to float
            length_str = track_data.get("length", "0")
            length_miles = float(length_str.split()[0]) if isinstance(length_str, str) else float(length_str)

            self.tracks[track_id] = Track(
                id=track_id,
                name=track_data["name"],
                length_miles=length_miles,
                location=track_data.get("location", ""),
                demand_profile=TrackDemand(
                    speed=demand.get("raw_speed", 0),
                    consistency=demand.get("consistency", 0),
                    racecraft=demand.get("racecraft", 0),
                    tire_management=demand.get("tire_mgmt", 0),
                ),
                description=track_data.get("description"),
            )

        # Load drivers with RepTrak-normalized factor scores from database
        for driver_data in data.get("drivers", []):
            driver_num = driver_data.get("number", driver_data.get("driverNumber"))

            # Get RepTrak-normalized factor scores from database
            factor_scores = self._get_driver_factor_scores(driver_num)

            # Build stats - some fields might be at top level
            races = driver_data.get("races", 0)
            avg_finish = driver_data.get("avg_finish", 0)

            # Calculate overall score as average of the 4 factor scores
            overall_score = (
                factor_scores["speed"]["score"] +
                factor_scores["consistency"]["score"] +
                factor_scores["racecraft"]["score"] +
                factor_scores["tire_management"]["score"]
            ) / 4

            self.drivers[driver_num] = Driver(
                driver_number=driver_num,
                driver_name=driver_data.get("name"),
                overall_score=overall_score,
                speed=FactorScore(
                    name="Speed",
                    score=factor_scores["speed"]["score"],
                    percentile=factor_scores["speed"]["percentile"],
                    z_score=factor_scores["speed"]["z_score"],
                ),
                consistency=FactorScore(
                    name="Consistency",
                    score=factor_scores["consistency"]["score"],
                    percentile=factor_scores["consistency"]["percentile"],
                    z_score=factor_scores["consistency"]["z_score"],
                ),
                racecraft=FactorScore(
                    name="Racecraft",
                    score=factor_scores["racecraft"]["score"],
                    percentile=factor_scores["racecraft"]["percentile"],
                    z_score=factor_scores["racecraft"]["z_score"],
                ),
                tire_management=FactorScore(
                    name="Tire Management",
                    score=factor_scores["tire_management"]["score"],
                    percentile=factor_scores["tire_management"]["percentile"],
                    z_score=factor_scores["tire_management"]["z_score"],
                ),
                stats=DriverStats(
                    driver_number=driver_num,
                    overall_score=overall_score,
                    races_completed=races,
                    average_finish=avg_finish,
                    best_finish=int(avg_finish) if avg_finish else 1,  # Approximate
                    worst_finish=int(avg_finish) + 5 if avg_finish else 20,  # Approximate
                ),
                circuit_fits={},  # Will be calculated on demand
            )

    def _load_track_profiles(self):
        """Load track demand profiles from CSV."""
        csv_path = (
            self.data_path / "analysis_outputs" / "track_demand_profiles_tier1.csv"
        )

        if csv_path.exists():
            self.track_demand_profiles = pd.read_csv(csv_path)
        else:
            print(f"Warning: Track profiles not found at {csv_path}")

    def _load_race_features(self):
        """Load race features from CSV."""
        csv_path = (
            self.data_path / "analysis_outputs" / "all_races_tier1_features.csv"
        )

        if csv_path.exists():
            self.all_races_features = pd.read_csv(csv_path)

            # Also load factor scores
            factor_path = (
                self.data_path / "analysis_outputs" / "tier1_factor_scores.csv"
            )
            if factor_path.exists():
                self.factor_scores = pd.read_csv(factor_path)
        else:
            print(f"Warning: Race features not found at {csv_path}")

    def _load_race_data(self):
        """Load race results and lap analysis data."""
        # Load provisional results
        results_path = self.data_path / "race_results" / "provisional_results"
        if results_path.exists():
            for csv_file in results_path.glob("*.csv"):
                track_race = csv_file.stem  # e.g., "barber_r1_provisional_results"
                self.race_results[track_race] = pd.read_csv(csv_file)

        # Load lap analysis (endurance data)
        analysis_path = self.data_path / "race_results" / "analysis_endurance"
        if analysis_path.exists():
            for csv_file in analysis_path.glob("*.csv"):
                track_race = csv_file.stem  # e.g., "barber_r1_analysis_endurance"
                self.lap_analysis[track_race] = pd.read_csv(csv_file)

    def get_track(self, track_id: str) -> Optional[Track]:
        """Get track by ID."""
        return self.tracks.get(track_id)

    def get_all_tracks(self) -> List[Track]:
        """Get all tracks."""
        return list(self.tracks.values())

    def get_driver(self, driver_number: int) -> Optional[Driver]:
        """Get driver by number."""
        return self.drivers.get(driver_number)

    def get_all_drivers(self) -> List[Driver]:
        """Get all drivers."""
        return list(self.drivers.values())

    def get_lap_data(self, track_id: str, race_num: int = 1) -> Optional[pd.DataFrame]:
        """Get lap analysis data for a specific track and race."""
        key = f"{track_id}_r{race_num}_analysis_endurance"
        return self.lap_analysis.get(key)

    def calculate_circuit_fit(
        self, driver_number: int, track_id: str
    ) -> Optional[float]:
        """
        Calculate circuit fit score for driver at track.

        Uses dot product of driver skills and track demands.
        Returns score 0-100.
        """
        driver = self.get_driver(driver_number)
        track = self.get_track(track_id)

        if not driver or not track:
            return None

        # Get driver skill vector (z-scores)
        driver_skills = [
            driver.speed.z_score,
            driver.consistency.z_score,
            driver.racecraft.z_score,
            driver.tire_management.z_score,
        ]

        # Get track demand vector
        track_demands = [
            track.demand_profile.speed,
            track.demand_profile.consistency,
            track.demand_profile.racecraft,
            track.demand_profile.tire_management,
        ]

        # Calculate dot product
        dot_product = sum(s * d for s, d in zip(driver_skills, track_demands))

        # Normalize to 0-100 scale (approximate)
        # Assuming dot product range is roughly -10 to 10
        normalized = ((dot_product + 10) / 20) * 100
        return max(0, min(100, normalized))

    def predict_finish_position(
        self, driver_number: int, track_id: str
    ) -> Optional[float]:
        """
        Predict finish position for driver at track.

        Uses the 4-factor model equation:
        Predicted Finish = 13.01 + (3.792 × CONSISTENCY) + (1.943 × RACECRAFT)
                          + (6.079 × SPEED) + (1.237 × TIRE_MGMT)
        """
        driver = self.get_driver(driver_number)

        if not driver:
            return None

        # Model coefficients
        intercept = 13.01
        coef_consistency = 3.792
        coef_racecraft = 1.943
        coef_speed = 6.079
        coef_tire = 1.237

        # Use z-scores for calculation
        predicted = (
            intercept
            + (coef_consistency * driver.consistency.z_score)
            + (coef_racecraft * driver.racecraft.z_score)
            + (coef_speed * driver.speed.z_score)
            + (coef_tire * driver.tire_management.z_score)
        )

        return max(1, predicted)  # Ensure minimum position is 1

    def _get_db_connection(self) -> sqlite3.Connection:
        """Get database connection."""
        conn = sqlite3.connect(str(self.db_path))
        conn.row_factory = sqlite3.Row
        return conn

    def get_season_stats(self, driver_number: int) -> Optional[SeasonStats]:
        """
        Get season statistics for a driver calculated from race_results.
        """
        conn = self._get_db_connection()
        cursor = conn.cursor()

        # Get driver_id from driver_number
        cursor.execute(
            "SELECT driver_id FROM drivers WHERE driver_number = ?", (driver_number,)
        )
        driver_row = cursor.fetchone()

        if not driver_row:
            conn.close()
            return None

        driver_id = driver_row["driver_id"]

        # Calculate stats from race_results
        cursor.execute(
            """
            SELECT
                COUNT(*) as total_races,
                SUM(CASE WHEN finish_position = 1 THEN 1 ELSE 0 END) as wins,
                SUM(CASE WHEN finish_position <= 3 THEN 1 ELSE 0 END) as podiums,
                SUM(CASE WHEN finish_position <= 5 THEN 1 ELSE 0 END) as top5,
                SUM(CASE WHEN finish_position <= 10 THEN 1 ELSE 0 END) as top10,
                SUM(CASE WHEN start_position = 1 THEN 1 ELSE 0 END) as pole_positions,
                SUM(CASE WHEN status = 'DNF' THEN 1 ELSE 0 END) as dnfs,
                AVG(finish_position) as avg_finish,
                AVG(start_position) as avg_qualifying,
                AVG(positions_gained) as avg_positions_gained
            FROM race_results
            WHERE driver_id = ?
            """,
            (driver_id,),
        )

        result = cursor.fetchone()
        conn.close()

        if not result or result["total_races"] == 0:
            return None

        # Calculate points (simplified: 25, 18, 15, 12, 10, 8, 6, 4, 2, 1)
        points_map = {1: 25, 2: 18, 3: 15, 4: 12, 5: 10, 6: 8, 7: 6, 8: 4, 9: 2, 10: 1}

        conn = self._get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            "SELECT finish_position FROM race_results WHERE driver_id = ?", (driver_id,)
        )
        points = sum(
            points_map.get(row["finish_position"], 0)
            for row in cursor.fetchall()
            if row["finish_position"]
        )
        conn.close()

        return SeasonStats(
            driver_number=driver_number,
            wins=result["wins"] or 0,
            podiums=result["podiums"] or 0,
            top5=result["top5"] or 0,
            top10=result["top10"] or 0,
            pole_positions=result["pole_positions"] or 0,
            total_races=result["total_races"] or 0,
            dnfs=result["dnfs"] or 0,
            fastest_laps=0,  # TODO: Add fastest_lap_time tracking
            avg_finish=round(result["avg_finish"], 2) if result["avg_finish"] else None,
            avg_qualifying=round(result["avg_qualifying"], 2)
            if result["avg_qualifying"]
            else None,
            avg_positions_gained=round(result["avg_positions_gained"], 2)
            if result["avg_positions_gained"]
            else None,
            points=points,
            championship_position=None,  # TODO: Calculate from standings
        )

    def get_race_results(self, driver_number: int) -> List[RaceResult]:
        """
        Get all race results for a driver for trending data.
        Uses RaceLogProcessor to merge provisional results, qualifying, and lap data.
        """
        # Use the new race log processor to get comprehensive race data
        return self.race_log_processor.get_driver_results(driver_number)


# Global instance
data_loader = DataLoader()
