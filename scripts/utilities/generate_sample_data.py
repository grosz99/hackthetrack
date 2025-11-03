"""
Generate sample race data for testing the dashboard UI.

Creates realistic race results for 8-10 drivers across all 12 races
with varying performance profiles.
"""

import sys
from pathlib import Path
import random
import logging

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent))

from backend.database.connection import get_database

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class SampleDataGenerator:
    """Generate sample race data for testing."""

    def __init__(self):
        self.db = get_database()

        # Define driver profiles with different characteristics
        self.driver_profiles = {
            13: {  # Elite driver - dominant
                "name": "Sarah Chen",
                "team": "Apex Racing",
                "avg_finish": 2.5,
                "variability": 1.5,
                "improvement": 0.1  # Gets better over season
            },
            7: {  # Strong driver - consistent
                "name": "Marcus Rodriguez",
                "team": "Velocity Motorsports",
                "avg_finish": 5.0,
                "variability": 2.0,
                "improvement": 0.05
            },
            72: {  # Strong driver - fast but inconsistent
                "name": "Alex Thompson",
                "team": "Thunder Racing",
                "avg_finish": 6.0,
                "variability": 4.0,
                "improvement": 0
            },
            22: {  # Average driver - steady
                "name": "Jordan Kim",
                "team": "Phoenix Racing",
                "avg_finish": 10.0,
                "variability": 2.5,
                "improvement": 0.02
            },
            88: {  # Average driver - improving
                "name": "Taylor Santos",
                "team": "Rising Star Racing",
                "avg_finish": 12.0,
                "variability": 3.0,
                "improvement": 0.15  # Big improvement trend
            },
            45: {  # Developing driver
                "name": "Casey Morgan",
                "team": "Next Gen Racing",
                "avg_finish": 15.0,
                "variability": 3.5,
                "improvement": 0.08
            },
            33: {  # Rookie - struggling early
                "name": "Riley Park",
                "team": "Rookie Racing Team",
                "avg_finish": 18.0,
                "variability": 4.0,
                "improvement": 0.12
            },
            51: {  # Veteran - declining
                "name": "Jamie Foster",
                "team": "Classic Racing",
                "avg_finish": 14.0,
                "variability": 2.8,
                "improvement": -0.05  # Getting worse
            }
        }

        # Track names and characteristics
        self.tracks = {
            "barber": "Barber Motorsports Park",
            "cota": "Circuit of the Americas",
            "roadamerica": "Road America",
            "sebring": "Sebring International Raceway",
            "sonoma": "Sonoma Raceway",
            "vir": "Virginia International Raceway"
        }

        # Race schedule (chronological order)
        self.race_schedule = [
            ("barber", 1, 1),
            ("barber", 2, 2),
            ("cota", 3, 1),
            ("cota", 4, 2),
            ("roadamerica", 5, 1),
            ("roadamerica", 6, 2),
            ("sebring", 7, 1),
            ("sebring", 8, 2),
            ("sonoma", 9, 1),
            ("sonoma", 10, 2),
            ("vir", 11, 1),
            ("vir", 12, 2)
        ]

    def update_driver_info(self):
        """Update driver names and teams."""
        logger.info("Updating driver information...")

        for driver_number, profile in self.driver_profiles.items():
            # Check if driver exists
            check_query = "SELECT driver_id FROM drivers WHERE driver_number = ?"
            result = self.db.fetch_one(check_query, (driver_number,))

            if result:
                # Update existing driver
                query = """
                    UPDATE drivers
                    SET name = ?, team = ?
                    WHERE driver_number = ?
                """
                self.db.execute(query, (profile["name"], profile["team"], driver_number))
            else:
                # Insert new driver
                query = """
                    INSERT INTO drivers (driver_id, driver_number, name, team, grade)
                    VALUES (?, ?, ?, ?, 'Unknown')
                """
                self.db.execute(query, (driver_number, driver_number, profile["name"], profile["team"]))

                # Also create factor entry for new driver
                factor_query = """
                    INSERT INTO driver_factors
                    (driver_id, track_id, consistency_value, racecraft_value,
                     raw_speed_value, tire_mgmt_value, overall_score)
                    VALUES (?, NULL, 50, 50, 50, 50, 50)
                """
                self.db.execute(factor_query, (driver_number,))

        logger.info(f"Updated {len(self.driver_profiles)} driver profiles")

    def generate_race_results(self):
        """Generate realistic race results for all drivers and races."""
        logger.info("Generating race results...")

        race_results = []
        num_drivers = len(self.driver_profiles)

        for track_id, round_num, race_num in self.race_schedule:
            # Simulate race progression (improvement over season)
            race_factor = (round_num - 1) / 11.0  # 0 to 1 over season

            # Generate positions for this race
            positions = []

            for driver_number, profile in self.driver_profiles.items():
                # Calculate expected finish based on profile
                base_finish = profile["avg_finish"]
                improvement_effect = profile["improvement"] * race_factor * 10
                variability = random.gauss(0, profile["variability"])

                finish_pos = base_finish + improvement_effect + variability
                finish_pos = max(1, min(num_drivers, round(finish_pos)))

                # Generate qualifying position (correlated but not identical)
                qual_offset = random.gauss(0, 2)
                start_pos = max(1, min(num_drivers, round(finish_pos + qual_offset)))

                positions.append({
                    "driver_number": driver_number,
                    "start_pos": start_pos,
                    "finish_pos": finish_pos,
                    "raw_score": finish_pos  # For sorting
                })

            # Sort by raw score and assign actual positions (handle ties)
            positions.sort(key=lambda x: x["raw_score"])

            for idx, pos_data in enumerate(positions, 1):
                pos_data["finish_pos"] = idx

            # Adjust start positions to be more spread out
            start_positions = [p["start_pos"] for p in positions]
            start_positions.sort()
            for idx, pos_data in enumerate(positions):
                pos_data["start_pos"] = start_positions[idx]

            # Generate race data
            for pos_data in positions:
                driver_number = pos_data["driver_number"]
                start_pos = pos_data["start_pos"]
                finish_pos = pos_data["finish_pos"]

                # Generate lap times (faster finishers have faster laps)
                base_lap_time = 85.0  # Base lap time in seconds
                driver_speed = (num_drivers - finish_pos) / num_drivers
                lap_time = base_lap_time - (driver_speed * 2) + random.uniform(-0.5, 0.5)

                # Format lap time
                minutes = int(lap_time // 60)
                seconds = lap_time % 60
                fastest_lap = f"{minutes}:{seconds:06.3f}"

                # Gap to leader (winner has no gap)
                if finish_pos == 1:
                    gap_to_leader = "0.000"
                    gap_to_winner = "0.000"
                else:
                    gap = (finish_pos - 1) * random.uniform(0.5, 2.0)
                    gap_to_leader = f"+{gap:.3f}"
                    gap_to_winner = f"+{gap:.3f}"

                # Incident points (mostly 0, occasional 2-4)
                incident_points = 0 if random.random() > 0.15 else random.choice([2, 2, 4])

                race_results.append((
                    driver_number,  # driver_id
                    track_id,
                    round_num,
                    race_num,
                    None,  # date
                    start_pos,
                    finish_pos,
                    start_pos - finish_pos,  # positions_gained
                    fastest_lap,
                    None,  # fastest_lap_rank (calculate later)
                    gap_to_leader,
                    gap_to_winner,
                    30,  # laps_completed (standard race)
                    incident_points,
                    "finished"
                ))

        # Insert all race results
        query = """
            INSERT INTO race_results
            (driver_id, track_id, round, race_number, date,
             start_position, finish_position, positions_gained,
             fastest_lap_time, fastest_lap_rank,
             gap_to_leader, gap_to_winner, laps_completed,
             incident_points, status)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """

        self.db.execute_many(query, race_results)
        logger.info(f"Generated {len(race_results)} race results")

    def calculate_season_stats(self):
        """Calculate season statistics from race results."""
        logger.info("Calculating season statistics...")

        query = """
            INSERT OR REPLACE INTO season_stats
            (driver_id, wins, podiums, top5, top10, dnfs, total_races,
             fastest_laps, avg_finish, avg_qualifying, avg_positions_gained, points)
            SELECT
                driver_id,
                SUM(CASE WHEN finish_position = 1 THEN 1 ELSE 0 END) as wins,
                SUM(CASE WHEN finish_position <= 3 THEN 1 ELSE 0 END) as podiums,
                SUM(CASE WHEN finish_position <= 5 THEN 1 ELSE 0 END) as top5,
                SUM(CASE WHEN finish_position <= 10 THEN 1 ELSE 0 END) as top10,
                0 as dnfs,
                COUNT(*) as total_races,
                0 as fastest_laps,
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
                        ELSE MAX(0, 24 - (finish_position - 8) * 2)
                    END
                ) as points
            FROM race_results
            WHERE status = 'finished'
            GROUP BY driver_id
        """

        self.db.execute(query)

        # Calculate championship positions
        query = """
            UPDATE season_stats
            SET championship_position = (
                SELECT rank
                FROM (
                    SELECT driver_id, ROW_NUMBER() OVER (ORDER BY points DESC) as rank
                    FROM season_stats
                ) ranked
                WHERE ranked.driver_id = season_stats.driver_id
            )
        """

        self.db.execute(query)

        logger.info("Season statistics calculated")

    def generate_performance_trends(self):
        """Generate performance trends for charts."""
        logger.info("Generating performance trends...")

        query = """
            INSERT INTO performance_trends
            (driver_id, round, track_id, finish_position)
            SELECT driver_id, round, track_id, finish_position
            FROM race_results
            ORDER BY round
        """

        self.db.execute(query)
        logger.info("Performance trends generated")

    def generate_all(self):
        """Generate all sample data."""
        logger.info("Starting sample data generation...")

        self.update_driver_info()
        self.generate_race_results()
        self.calculate_season_stats()
        self.generate_performance_trends()

        # Print summary
        logger.info("\n" + "=" * 60)
        logger.info("Sample Data Generation Complete!")
        logger.info("=" * 60)

        # Show top 5 drivers in championship
        query = """
            SELECT
                d.driver_number,
                d.name,
                d.team,
                ss.championship_position,
                ss.wins,
                ss.podiums,
                ss.points,
                ROUND(ss.avg_finish, 2) as avg_finish
            FROM drivers d
            JOIN season_stats ss ON d.driver_id = ss.driver_id
            ORDER BY ss.championship_position
            LIMIT 5
        """

        top_drivers = self.db.fetch_all(query)

        logger.info("\nTop 5 Drivers in Championship:")
        logger.info("-" * 60)
        for driver in top_drivers:
            logger.info(
                f"P{driver['championship_position']:2d} | #{driver['driver_number']:2d} {driver['name']:20s} | "
                f"{driver['wins']:2d} wins | {driver['podiums']:2d} podiums | "
                f"{driver['points']:3d} pts | Avg: P{driver['avg_finish']}"
            )

        logger.info("=" * 60)

        # Show table counts
        table_info = self.db.get_table_info()
        logger.info("\nDatabase Contents:")
        for table_name, row_count in sorted(table_info.items()):
            if row_count > 0:
                logger.info(f"  {table_name:30s}: {row_count:5d} rows")

        logger.info("\nSample data ready for dashboard testing! 🎉")


def main():
    """Main entry point."""
    generator = SampleDataGenerator()
    generator.generate_all()
    return 0


if __name__ == "__main__":
    sys.exit(main())
