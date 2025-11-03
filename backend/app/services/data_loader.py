"""
Data loading service for Racing Analytics API.
Loads CSV files and dashboard JSON into memory for fast access.
"""

import pandas as pd
import json
import sqlite3
from pathlib import Path
from typing import Dict, List, Optional
from models import (
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

            # Initialize race log processor (for CSV fallback only)
            from .race_log_processor import RaceLogProcessor
            self.race_log_processor = RaceLogProcessor(self.data_path)

            # Load pre-calculated race data from JSON
            self.season_stats_lookup: Dict[int, Dict] = {}
            self.race_results_lookup: Dict[int, List[Dict]] = {}

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

        # Load pre-calculated season stats and race results from JSON
        self._load_season_stats_json()
        self._load_race_results_json()

        print(f"Data loaded: {len(self.tracks)} tracks, {len(self.drivers)} drivers")
        print(f"Season stats loaded: {len(self.season_stats_lookup)} drivers")
        print(f"Race results loaded: {len(self.race_results_lookup)} drivers")

    def _load_driver_factors_json(self):
        """Load driver factors from JSON export (replaces SQLite)."""
        json_path = self.base_path / "backend" / "data" / "driver_factors.json"

        if not json_path.exists():
            print(f"Warning: Driver factors JSON not found at {json_path}")
            return {}

        with open(json_path, "r") as f:
            data = json.load(f)

        # Convert to lookup dict: driver_number -> factors
        driver_factors_lookup = {}
        for driver in data.get("drivers", []):
            driver_num = driver["driver_number"]
            driver_factors_lookup[driver_num] = driver["factors"]

        print(f"Loaded factor data for {len(driver_factors_lookup)} drivers from JSON")
        return driver_factors_lookup

    def _load_season_stats_json(self):
        """Load pre-calculated season statistics from JSON."""
        json_path = self.base_path / "backend" / "data" / "driver_season_stats.json"

        if not json_path.exists():
            print(f"Warning: Season stats JSON not found at {json_path}")
            return

        with open(json_path, "r") as f:
            data = json.load(f)

        # Convert string keys to integers
        self.season_stats_lookup = {
            int(driver_num): stats
            for driver_num, stats in data.get("data", {}).items()
        }

        print(f"Loaded season stats for {len(self.season_stats_lookup)} drivers from JSON")

    def _load_race_results_json(self):
        """Load race-by-race results from JSON."""
        json_path = self.base_path / "backend" / "data" / "driver_race_results.json"

        if not json_path.exists():
            print(f"Warning: Race results JSON not found at {json_path}")
            return

        with open(json_path, "r") as f:
            data = json.load(f)

        # Convert string keys to integers
        self.race_results_lookup = {
            int(driver_num): results
            for driver_num, results in data.get("data", {}).items()
        }

        print(f"Loaded race results for {len(self.race_results_lookup)} drivers from JSON")

    def _get_driver_factor_scores(self, driver_number: int) -> Dict:
        """Get RepTrak-normalized factor scores from JSON data."""
        if not hasattr(self, 'driver_factors_lookup'):
            self.driver_factors_lookup = self._load_driver_factors_json()

        driver_factors = self.driver_factors_lookup.get(driver_number, {})

        factor_scores = {}
        for factor_name in ["speed", "consistency", "racecraft", "tire_management"]:
            factor_data = driver_factors.get(factor_name, {})

            if factor_data:
                score = factor_data.get("score", 50)
                percentile = factor_data.get("percentile", 50)
            else:
                # Fallback to 50 if no data
                score = 50
                percentile = 50

            factor_scores[factor_name] = {
                "score": score,
                "percentile": percentile,
                "z_score": (score - 50) / 10  # Approximate z-score for compatibility
            }

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

        # Load driver factors from JSON
        if not hasattr(self, 'driver_factors_lookup'):
            self.driver_factors_lookup = self._load_driver_factors_json()

        # Get list of drivers with factor data
        drivers_with_data = set(self.driver_factors_lookup.keys())
        print(f"Found {len(drivers_with_data)} drivers with factor data")

        # Load drivers with RepTrak-normalized factor scores from database
        for driver_data in data.get("drivers", []):
            driver_num = driver_data.get("number", driver_data.get("driverNumber"))

            # Skip drivers without factor data (no telemetry)
            if driver_num not in drivers_with_data:
                continue

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
        Get season statistics for a driver from pre-calculated JSON data.

        Returns pre-aggregated stats (wins, podiums, averages, points) for fast API responses.
        Data sourced from driver_season_stats.json which is generated from CSV files.
        """
        # Get pre-calculated stats from JSON lookup
        stats_data = self.season_stats_lookup.get(driver_number)

        if not stats_data:
            return None

        # Convert dict to SeasonStats model
        return SeasonStats(
            driver_number=driver_number,
            wins=stats_data.get("wins", 0),
            podiums=stats_data.get("podiums", 0),
            top5=stats_data.get("top5", 0),
            top10=stats_data.get("top10", 0),
            pole_positions=stats_data.get("pole_positions", 0),
            total_races=stats_data.get("total_races", 0),
            dnfs=stats_data.get("dnfs", 0),
            fastest_laps=stats_data.get("fastest_laps", 0),
            avg_finish=stats_data.get("avg_finish"),
            avg_qualifying=stats_data.get("avg_qualifying"),
            avg_positions_gained=stats_data.get("avg_positions_gained"),
            points=stats_data.get("points", 0),
            championship_position=stats_data.get("championship_position"),
        )

    def get_race_results(self, driver_number: int) -> List[RaceResult]:
        """
        Get all race results for a driver for trending/historical data.

        Returns race-by-race results from pre-loaded JSON data for fast API responses.
        Data sourced from driver_race_results.json which is generated from CSV files.
        """
        # Get race results from JSON lookup
        results_data = self.race_results_lookup.get(driver_number)

        if not results_data:
            return []

        # Convert dicts to RaceResult models
        return [RaceResult(**result) for result in results_data]


# Global instance
data_loader = DataLoader()
