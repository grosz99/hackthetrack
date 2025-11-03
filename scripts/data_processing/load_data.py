"""
Load data from CSV files into SQLite database.

This script processes all race data, driver statistics, and factor scores
into a structured SQLite database for fast querying.
"""

import sys
from pathlib import Path
import pandas as pd
import numpy as np
import logging
from typing import Dict, List

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent))

from backend.database.connection import get_database

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class DataLoader:
    """Load and process racing data into SQLite database."""

    def __init__(self, data_dir: Path):
        """
        Initialize data loader.

        Args:
            data_dir: Path to data directory
        """
        self.data_dir = data_dir
        self.db = get_database()

        # Track mapping
        self.track_mapping = {
            "barber": {
                "name": "Barber Motorsports Park",
                "location": "Leeds, AL",
                "length_miles": 2.38,
                "turns": 17,
                "track_type": "road"
            },
            "cota": {
                "name": "Circuit of the Americas",
                "location": "Austin, TX",
                "length_miles": 3.41,
                "turns": 20,
                "track_type": "road"
            },
            "roadamerica": {
                "name": "Road America",
                "location": "Elkhart Lake, WI",
                "length_miles": 4.05,
                "turns": 14,
                "track_type": "road"
            },
            "sebring": {
                "name": "Sebring International Raceway",
                "location": "Sebring, FL",
                "length_miles": 3.74,
                "turns": 17,
                "track_type": "road"
            },
            "sonoma": {
                "name": "Sonoma Raceway",
                "location": "Sonoma, CA",
                "length_miles": 2.52,
                "turns": 12,
                "track_type": "road"
            },
            "vir": {
                "name": "Virginia International Raceway",
                "location": "Alton, VA",
                "length_miles": 3.27,
                "turns": 18,
                "track_type": "road"
            }
        }

    def initialize_database(self):
        """Initialize database schema."""
        logger.info("Initializing database schema...")
        self.db.initialize_schema()
        logger.info("Schema initialized successfully")

    def load_tracks(self):
        """Load track data into database."""
        logger.info("Loading tracks...")

        tracks_data = []
        for track_id, info in self.track_mapping.items():
            tracks_data.append((
                track_id,
                info["name"],
                info["location"],
                info["length_miles"],
                info["turns"],
                info["track_type"],
                f"/track_maps/{track_id}.png"
            ))

        query = """
            INSERT OR REPLACE INTO tracks
            (track_id, name, location, length_miles, turns, track_type, thumbnail_url)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """

        self.db.execute_many(query, tracks_data)
        logger.info(f"Loaded {len(tracks_data)} tracks")

    def load_drivers(self):
        """Load driver data from analysis outputs."""
        logger.info("Loading drivers...")

        # Load from driver average scores
        scores_file = self.data_dir / "analysis_outputs" / "driver_average_scores_tier1.csv"

        if not scores_file.exists():
            logger.warning(f"Driver scores file not found: {scores_file}")
            return

        df = pd.read_csv(scores_file)

        drivers_data = []
        for _, row in df.iterrows():
            driver_number = int(row["driver_number"])
            drivers_data.append((
                driver_number,  # driver_id = driver_number
                driver_number,
                f"Driver #{driver_number}",  # Placeholder name
                "Team TBD",  # Placeholder team
                None,  # circuit_fit_score (calculated later)
                None,  # overall_rating (calculated later)
                "Unknown"  # grade
            ))

        query = """
            INSERT OR REPLACE INTO drivers
            (driver_id, driver_number, name, team, circuit_fit_score, overall_rating, grade)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """

        self.db.execute_many(query, drivers_data)
        logger.info(f"Loaded {len(drivers_data)} drivers")

    def load_race_results(self):
        """Load race results from provisional results CSVs."""
        logger.info("Loading race results...")

        provisional_dir = self.data_dir / "race_results" / "provisional_results"

        if not provisional_dir.exists():
            logger.warning(f"Provisional results directory not found: {provisional_dir}")
            return

        # Track to round mapping (in chronological order)
        track_rounds = {
            "barber_r1": 1,
            "barber_r2": 2,
            "cota_r1": 3,
            "cota_r2": 4,
            "roadamerica_r1": 5,
            "roadamerica_r2": 6,
            "sebring_r1": 7,
            "sebring_r2": 8,
            "sonoma_r1": 9,
            "sonoma_r2": 10,
            "vir_r1": 11,
            "vir_r2": 12
        }

        race_results_data = []

        for track_race, round_num in track_rounds.items():
            parts = track_race.split("_")
            track_id = parts[0]
            race_num = int(parts[1][1])  # Extract race number from 'r1' or 'r2'

            csv_file = provisional_dir / f"{track_race}_provisional_results.csv"

            if not csv_file.exists():
                logger.warning(f"Race results file not found: {csv_file}")
                continue

            df = pd.read_csv(csv_file)

            for _, row in df.iterrows():
                driver_number = int(row.get("Car", row.get("VEHICLE_NO", 0)))

                if driver_number == 0:
                    continue

                start_pos = int(row.get("Start", row.get("QUAL_POS", 0)))
                finish_pos = int(row.get("Finish", row.get("FINISH_POS", 0)))

                race_results_data.append((
                    driver_number,  # driver_id
                    track_id,
                    round_num,
                    race_num,
                    None,  # date (not in provisional results)
                    start_pos,
                    finish_pos,
                    start_pos - finish_pos,  # positions_gained
                    None,  # fastest_lap_time (add from best_10_laps later)
                    None,  # fastest_lap_rank
                    None,  # gap_to_leader
                    None,  # gap_to_winner
                    None,  # laps_completed
                    int(row.get("Pts", row.get("INCIDENT_PTS", 0))),  # incident_points
                    "finished"  # status
                ))

        query = """
            INSERT OR REPLACE INTO race_results
            (driver_id, track_id, round, race_number, date, start_position, finish_position,
             positions_gained, fastest_lap_time, fastest_lap_rank, gap_to_leader, gap_to_winner,
             laps_completed, incident_points, status)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """

        self.db.execute_many(query, race_results_data)
        logger.info(f"Loaded {len(race_results_data)} race results")

    def calculate_season_stats(self):
        """Calculate and store season statistics for all drivers."""
        logger.info("Calculating season statistics...")

        # Check if we have race results
        result_count = self.db.count_rows("race_results")
        if result_count == 0:
            logger.warning("No race results found, skipping season stats calculation")
            return

        query = """
            INSERT OR REPLACE INTO season_stats
            (driver_id, wins, podiums, top5, top10, dnfs, total_races,
             avg_finish, avg_qualifying, avg_positions_gained, points)
            SELECT
                driver_id,
                SUM(CASE WHEN finish_position = 1 THEN 1 ELSE 0 END) as wins,
                SUM(CASE WHEN finish_position <= 3 THEN 1 ELSE 0 END) as podiums,
                SUM(CASE WHEN finish_position <= 5 THEN 1 ELSE 0 END) as top5,
                SUM(CASE WHEN finish_position <= 10 THEN 1 ELSE 0 END) as top10,
                SUM(CASE WHEN status = 'dnf' THEN 1 ELSE 0 END) as dnfs,
                COUNT(*) as total_races,
                AVG(finish_position) as avg_finish,
                AVG(start_position) as avg_qualifying,
                AVG(positions_gained) as avg_positions_gained,
                SUM(
                    CASE finish_position
                        WHEN 1 THEN 50
                        WHEN 2 THEN 40
                        WHEN 3 THEN 35
                        WHEN 4 THEN 32
                        WHEN 5 THEN 30
                        WHEN 6 THEN 28
                        WHEN 7 THEN 26
                        WHEN 8 THEN 24
                        WHEN 9 THEN 22
                        WHEN 10 THEN 20
                        WHEN 11 THEN 19
                        WHEN 12 THEN 18
                        WHEN 13 THEN 17
                        WHEN 14 THEN 16
                        WHEN 15 THEN 15
                        WHEN 16 THEN 14
                        WHEN 17 THEN 13
                        WHEN 18 THEN 12
                        WHEN 19 THEN 11
                        WHEN 20 THEN 10
                        ELSE MAX(0, 10 - (finish_position - 20))
                    END
                ) as points
            FROM race_results
            WHERE status = 'finished'
            GROUP BY driver_id
        """

        self.db.execute(query)
        logger.info("Season statistics calculated")

    def load_driver_factors(self):
        """Load driver factor scores from analysis outputs."""
        logger.info("Loading driver factors...")

        scores_file = self.data_dir / "analysis_outputs" / "driver_average_scores_tier1.csv"

        if not scores_file.exists():
            logger.warning(f"Driver scores file not found: {scores_file}")
            return

        df = pd.read_csv(scores_file)

        # Convert z-scores to 0-100 scale and calculate percentiles
        factors_data = []

        for _, row in df.iterrows():
            driver_id = int(row["driver_number"])

            # Get factor z-scores (using first 4 factors based on spec)
            factor_1 = row["factor_1_score"]  # Raw Speed
            factor_2 = row["factor_2_score"]  # Consistency
            factor_3 = row["factor_3_score"]  # Racecraft
            factor_4 = row["factor_4_score"]  # Tire Management

            # Convert z-scores to 0-100 scale
            # Higher z-score = better performance
            # Use inverse since negative z-scores are better (lower finishing position)
            raw_speed_value = int(50 + (factor_1 * -10))  # Invert
            consistency_value = int(50 + (factor_2 * -10))
            racecraft_value = int(50 + (factor_3 * -10))
            tire_mgmt_value = int(50 + (factor_4 * -10))

            # Calculate overall score (weighted average based on importance from spec)
            overall_score = int(
                raw_speed_value * 0.50 +
                consistency_value * 0.31 +
                racecraft_value * 0.16 +
                tire_mgmt_value * 0.10
            )

            factors_data.append((
                driver_id,
                None,  # track_id (NULL for overall)
                consistency_value,
                None,  # consistency_percentile (calculated later)
                None,  # consistency_rank
                racecraft_value,
                None,  # racecraft_percentile
                None,  # racecraft_rank
                raw_speed_value,
                None,  # raw_speed_percentile
                None,  # raw_speed_rank
                tire_mgmt_value,
                None,  # tire_mgmt_percentile
                None,  # tire_mgmt_rank
                overall_score
            ))

        query = """
            INSERT OR REPLACE INTO driver_factors
            (driver_id, track_id,
             consistency_value, consistency_percentile, consistency_rank,
             racecraft_value, racecraft_percentile, racecraft_rank,
             raw_speed_value, raw_speed_percentile, raw_speed_rank,
             tire_mgmt_value, tire_mgmt_percentile, tire_mgmt_rank,
             overall_score)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """

        self.db.execute_many(query, factors_data)
        logger.info(f"Loaded factors for {len(factors_data)} drivers")

        # Calculate percentiles
        self._calculate_factor_percentiles()

    def _calculate_factor_percentiles(self):
        """Calculate percentile ranks for all factors."""
        logger.info("Calculating factor percentiles...")

        factors = ["consistency", "racecraft", "raw_speed", "tire_mgmt"]

        for factor in factors:
            # Calculate percentile using ranking
            query = f"""
                UPDATE driver_factors
                SET {factor}_percentile = (
                    SELECT CAST(
                        100.0 * (
                            SELECT COUNT(*)
                            FROM driver_factors as df2
                            WHERE df2.{factor}_value < driver_factors.{factor}_value
                                  AND df2.track_id IS NULL
                        ) / (
                            SELECT COUNT(*) - 1
                            FROM driver_factors
                            WHERE track_id IS NULL
                        ) AS INTEGER
                    )
                )
                WHERE track_id IS NULL
            """
            self.db.execute(query)

        # Update ranks
        for factor in factors:
            query = f"""
                UPDATE driver_factors
                SET {factor}_rank = (
                    SELECT rank || '/' || total
                    FROM (
                        SELECT
                            driver_id,
                            ROW_NUMBER() OVER (ORDER BY {factor}_value DESC) as rank,
                            (SELECT COUNT(*) FROM driver_factors WHERE track_id IS NULL) as total
                        FROM driver_factors
                        WHERE track_id IS NULL
                    ) ranks
                    WHERE ranks.driver_id = driver_factors.driver_id
                )
                WHERE track_id IS NULL
            """
            self.db.execute(query)

        logger.info("Factor percentiles calculated")

    def load_performance_trends(self):
        """Load performance trends for line charts."""
        logger.info("Loading performance trends...")

        # Check if we have race results
        result_count = self.db.count_rows("race_results")
        if result_count == 0:
            logger.warning("No race results found, skipping performance trends")
            return

        query = """
            INSERT OR REPLACE INTO performance_trends
            (driver_id, round, track_id, finish_position)
            SELECT driver_id, round, track_id, finish_position
            FROM race_results
            ORDER BY driver_id, round
        """

        self.db.execute(query)
        logger.info("Performance trends loaded")

    def update_driver_grades(self):
        """Update driver overall ratings and grades based on factors."""
        logger.info("Updating driver grades...")

        query = """
            UPDATE drivers
            SET
                overall_rating = (
                    SELECT overall_score
                    FROM driver_factors
                    WHERE driver_factors.driver_id = drivers.driver_id
                      AND driver_factors.track_id IS NULL
                ),
                grade = (
                    SELECT CASE
                        WHEN overall_score >= 90 THEN 'Elite'
                        WHEN overall_score >= 75 THEN 'Strong'
                        WHEN overall_score >= 60 THEN 'Average'
                        WHEN overall_score >= 45 THEN 'Developing'
                        ELSE 'Rookie'
                    END
                    FROM driver_factors
                    WHERE driver_factors.driver_id = drivers.driver_id
                      AND driver_factors.track_id IS NULL
                )
        """

        self.db.execute(query)
        logger.info("Driver grades updated")

    def load_all(self):
        """Load all data into database."""
        logger.info("Starting data load process...")

        self.initialize_database()
        self.load_tracks()
        self.load_drivers()
        self.load_race_results()
        self.calculate_season_stats()
        self.load_driver_factors()
        self.load_performance_trends()
        self.update_driver_grades()

        # Print summary
        table_info = self.db.get_table_info()
        logger.info("\n" + "=" * 50)
        logger.info("Database Load Summary")
        logger.info("=" * 50)
        for table_name, row_count in table_info.items():
            logger.info(f"{table_name:30s}: {row_count:5d} rows")
        logger.info("=" * 50)

        logger.info("Data load completed successfully!")


def main():
    """Main entry point."""
    # Get data directory
    data_dir = Path(__file__).parent.parent / "data"

    if not data_dir.exists():
        logger.error(f"Data directory not found: {data_dir}")
        return 1

    # Create data loader and load all data
    loader = DataLoader(data_dir)
    loader.load_all()

    return 0


if __name__ == "__main__":
    sys.exit(main())
