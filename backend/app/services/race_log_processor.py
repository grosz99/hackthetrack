"""
Race Log Data Processor
Processes and merges race results, qualifying, and lap data for the Race Log page.
"""

import pandas as pd
from pathlib import Path
from typing import Dict, List, Optional
from ..models import RaceResult


class RaceLogProcessor:
    """Process race log data from CSV files."""

    def __init__(self, data_path: Path):
        self.data_path = data_path
        self.race_results_path = data_path / "race_results"
        self.lap_timing_path = data_path / "lap_timing"
        self.qualifying_path = data_path / "qualifying"
        self.analysis_endurance_path = data_path / "race_results" / "analysis_endurance"

        # Track configuration: maps track names to their IDs and race rounds
        self.track_config = {
            "barber": {"id": "barber", "name": "Barber Motorsports Park", "rounds": [1, 2]},
            "cota": {"id": "cota", "name": "Circuit of the Americas", "rounds": [1, 2]},
            "roadamerica": {"id": "roadamerica", "name": "Road America", "rounds": [1, 2]},
            "sebring": {"id": "sebring", "name": "Sebring International Raceway", "rounds": [1, 2]},
            "sonoma": {"id": "sonoma", "name": "Sonoma Raceway", "rounds": [1, 2]},
            "vir": {"id": "vir", "name": "Virginia International Raceway", "rounds": [1, 2]},
        }

    def get_driver_results(self, driver_number: int) -> List[RaceResult]:
        """
        Get all race results for a driver across all tracks and races.
        Merges provisional results, qualifying, and lap sector data.
        """
        results = []
        race_id = 1
        round_num = 1

        for track_key, track_info in self.track_config.items():
            track_id = track_info["id"]
            track_name = track_info["name"]

            for race_num in track_info["rounds"]:
                # Load all data sources for this race
                race_data = self._load_race_data(track_key, race_num, driver_number)

                if race_data:
                    result = RaceResult(
                        race_id=race_id,
                        track_id=track_id,
                        track_name=track_name,
                        round=round_num,
                        race_number=race_num,
                        start_position=race_data.get("start_position"),
                        finish_position=race_data.get("finish_position"),
                        positions_gained=race_data.get("positions_gained"),
                        fastest_lap=race_data.get("fastest_lap"),
                        gap_to_winner=race_data.get("gap_to_winner"),
                        status=race_data.get("status"),
                        qualifying_time=race_data.get("qualifying_time"),
                        gap_to_pole=race_data.get("gap_to_pole"),
                        s1_best_time=race_data.get("s1_best_time"),
                        s2_best_time=race_data.get("s2_best_time"),
                        s3_best_time=race_data.get("s3_best_time"),
                        total_laps=race_data.get("total_laps"),
                        avg_lap_time=race_data.get("avg_lap_time"),
                        best_lap_time=race_data.get("best_lap_time"),
                        worst_lap_time=race_data.get("worst_lap_time"),
                        lap_time_std_dev=race_data.get("lap_time_std_dev"),
                        driver_fastest_lap=race_data.get("driver_fastest_lap"),
                        gap_to_fastest_lap=race_data.get("gap_to_fastest_lap"),
                        driver_s1_best=race_data.get("driver_s1_best"),
                        gap_to_s1_best=race_data.get("gap_to_s1_best"),
                        driver_s2_best=race_data.get("driver_s2_best"),
                        gap_to_s2_best=race_data.get("gap_to_s2_best"),
                        driver_s3_best=race_data.get("driver_s3_best"),
                        gap_to_s3_best=race_data.get("gap_to_s3_best"),
                    )
                    results.append(result)
                    race_id += 1

                round_num += 1

        return results

    def _load_race_data(self, track_key: str, race_num: int, driver_number: int) -> Optional[Dict]:
        """Load and merge all data sources for a specific race."""
        race_data = {}

        # 1. Load provisional race results (finish position, fastest lap, gap to winner)
        provisional_data = self._load_provisional_results(track_key, race_num, driver_number)
        if provisional_data:
            race_data.update(provisional_data)
        else:
            return None  # No race data for this driver

        # 2. Load qualifying data (start position, qualifying time, gap to pole)
        qualifying_data = self._load_qualifying_data(track_key, race_num, driver_number)
        if qualifying_data:
            race_data.update(qualifying_data)

        # 3. Load lap sector times (S1, S2, S3 best times)
        sector_data = self._load_sector_times(track_key, race_num, driver_number)
        if sector_data:
            race_data.update(sector_data)

        # 4. Load lap analysis from analysis_endurance
        lap_analysis = self._load_lap_analysis(track_key, race_num, driver_number)
        if lap_analysis:
            race_data.update(lap_analysis)

        # 5. Calculate positions gained
        if race_data.get("start_position") and race_data.get("finish_position"):
            race_data["positions_gained"] = (
                race_data["start_position"] - race_data["finish_position"]
            )

        return race_data

    def _load_provisional_results(self, track_key: str, race_num: int, driver_number: int) -> Optional[Dict]:
        """Load provisional race results."""
        file_path = self.race_results_path / "provisional_results" / f"{track_key}_r{race_num}_provisional_results.csv"

        if not file_path.exists():
            return None

        try:
            # Read CSV with semicolon delimiter
            df = pd.read_csv(file_path, delimiter=";")

            # Find driver row
            driver_row = df[df["NUMBER"] == driver_number]
            if driver_row.empty:
                return None

            row = driver_row.iloc[0]

            return {
                "finish_position": int(row["POSITION"]) if pd.notna(row["POSITION"]) else None,
                "fastest_lap": str(row["FL_TIME"]) if pd.notna(row["FL_TIME"]) else None,
                "gap_to_winner": str(row["GAP_FIRST"]) if pd.notna(row["GAP_FIRST"]) and row["GAP_FIRST"] != "-" else None,
                "status": str(row["STATUS"]) if pd.notna(row["STATUS"]) else None,
            }
        except Exception as e:
            print(f"Error loading provisional results for {track_key} R{race_num}: {e}")
            return None

    def _load_qualifying_data(self, track_key: str, race_num: int, driver_number: int) -> Optional[Dict]:
        """Load qualifying data."""
        # Map track keys to qualifying file names
        qual_file_map = {
            "barber": f"Barberrd{race_num}Qualifying.csv",
            "cota": f"Cotard{race_num}Qualifying.csv",
            "roadamerica": f"RoadAmericard{race_num}Qualifying.csv",
            "sebring": f"Sebringrd{race_num}Qualifying.csv",
            "sonoma": f"Sonomard{race_num}Qualifying.csv",
            "vir": f"VIRrd{race_num}Qualifying.csv",
        }

        qual_filename = qual_file_map.get(track_key)
        if not qual_filename:
            return None

        file_path = self.qualifying_path / qual_filename

        if not file_path.exists():
            return None

        try:
            # Read CSV with semicolon delimiter
            df = pd.read_csv(file_path, delimiter=";")

            # Find driver row
            driver_row = df[df["NUMBER"] == driver_number]
            if driver_row.empty:
                return None

            row = driver_row.iloc[0]

            return {
                "start_position": int(row["POS"]) if pd.notna(row["POS"]) else None,
                "qualifying_time": str(row["TIME"]) if pd.notna(row["TIME"]) else None,
                "gap_to_pole": str(row["GAP_FIRST"]) if pd.notna(row["GAP_FIRST"]) and row["GAP_FIRST"] != "-" else None,
            }
        except Exception as e:
            print(f"Error loading qualifying data for {track_key} R{race_num}: {e}")
            return None

    def _load_sector_times(self, track_key: str, race_num: int, driver_number: int) -> Optional[Dict]:
        """Load best sector times from lap data."""
        file_path = self.lap_timing_path / f"{track_key}_r{race_num}_lap_time.csv"

        if not file_path.exists():
            return None

        try:
            # Note: Lap timing files may have different structure
            # For now, return None until we understand the format better
            # TODO: Parse lap timing CSV to extract S1, S2, S3 best times
            return None
        except Exception as e:
            print(f"Error loading sector times for {track_key} R{race_num}: {e}")
            return None

    def _load_lap_analysis(self, track_key: str, race_num: int, driver_number: int) -> Optional[Dict]:
        """Load and analyze lap data from analysis_endurance files."""
        file_path = self.analysis_endurance_path / f"{track_key}_r{race_num}_analysis_endurance.csv"

        if not file_path.exists():
            return None

        try:
            # Read CSV with semicolon delimiter
            df = pd.read_csv(file_path, delimiter=";")

            # Strip whitespace from column names
            df.columns = df.columns.str.strip()

            # Filter for this driver (NUMBER column contains car number, not DRIVER_NUMBER)
            driver_laps = df[df["NUMBER"] == driver_number].copy()
            if driver_laps.empty:
                return None

            # Convert lap times from string format (e.g., "1:39.725") to seconds
            def lap_time_to_seconds(time_str):
                """Convert lap time string to seconds."""
                if pd.isna(time_str) or time_str == "":
                    return None
                try:
                    # Handle format like "1:39.725"
                    parts = str(time_str).split(":")
                    if len(parts) == 2:
                        minutes = int(parts[0])
                        seconds = float(parts[1])
                        return minutes * 60 + seconds
                    return float(time_str)
                except:
                    return None

            # Convert sector times from string to seconds
            def sector_time_to_seconds(time_str):
                """Convert sector time to seconds."""
                if pd.isna(time_str) or time_str == "" or str(time_str).strip() == "":
                    return None
                try:
                    return float(time_str)
                except:
                    return None

            # Convert lap times to seconds
            driver_laps["lap_seconds"] = driver_laps["LAP_TIME"].apply(lap_time_to_seconds)
            valid_laps = driver_laps[driver_laps["lap_seconds"].notna()]

            if valid_laps.empty:
                return None

            # Calculate driver's lap time statistics
            lap_times = valid_laps["lap_seconds"]
            total_laps = len(valid_laps)
            avg_seconds = lap_times.mean()
            driver_best_seconds = lap_times.min()
            worst_seconds = lap_times.max()
            std_dev = lap_times.std()

            # Calculate driver's best sector times
            driver_laps["s1_seconds"] = driver_laps["S1"].apply(sector_time_to_seconds)
            driver_laps["s2_seconds"] = driver_laps["S2"].apply(sector_time_to_seconds)
            driver_laps["s3_seconds"] = driver_laps["S3"].apply(sector_time_to_seconds)

            driver_s1_best = driver_laps["s1_seconds"].min()
            driver_s2_best = driver_laps["s2_seconds"].min()
            driver_s3_best = driver_laps["s3_seconds"].min()

            # Calculate race-wide best times (all drivers)
            df["lap_seconds"] = df["LAP_TIME"].apply(lap_time_to_seconds)
            df["s1_seconds"] = df["S1"].apply(sector_time_to_seconds)
            df["s2_seconds"] = df["S2"].apply(sector_time_to_seconds)
            df["s3_seconds"] = df["S3"].apply(sector_time_to_seconds)

            race_best_lap = df["lap_seconds"].min()
            race_best_s1 = df["s1_seconds"].min()
            race_best_s2 = df["s2_seconds"].min()
            race_best_s3 = df["s3_seconds"].min()

            # Calculate gaps
            gap_to_fastest_lap = driver_best_seconds - race_best_lap if pd.notna(driver_best_seconds) and pd.notna(race_best_lap) else None
            gap_to_s1 = driver_s1_best - race_best_s1 if pd.notna(driver_s1_best) and pd.notna(race_best_s1) else None
            gap_to_s2 = driver_s2_best - race_best_s2 if pd.notna(driver_s2_best) and pd.notna(race_best_s2) else None
            gap_to_s3 = driver_s3_best - race_best_s3 if pd.notna(driver_s3_best) and pd.notna(race_best_s3) else None

            # Convert back to time string format
            def seconds_to_lap_time(seconds):
                """Convert seconds to lap time string."""
                if seconds is None or pd.isna(seconds):
                    return None
                minutes = int(seconds // 60)
                secs = seconds % 60
                return f"{minutes}:{secs:06.3f}"

            def seconds_to_sector_time(seconds):
                """Convert seconds to sector time string."""
                if seconds is None or pd.isna(seconds):
                    return None
                return f"{seconds:.3f}"

            def format_gap(gap_seconds):
                """Format gap as +X.XXX"""
                if gap_seconds is None or pd.isna(gap_seconds):
                    return None
                return f"+{gap_seconds:.3f}" if gap_seconds > 0 else f"{gap_seconds:.3f}"

            return {
                "total_laps": total_laps,
                "avg_lap_time": seconds_to_lap_time(avg_seconds),
                "best_lap_time": seconds_to_lap_time(driver_best_seconds),
                "worst_lap_time": seconds_to_lap_time(worst_seconds),
                "lap_time_std_dev": round(std_dev, 3) if pd.notna(std_dev) else None,
                # Driver's best times
                "driver_fastest_lap": seconds_to_lap_time(driver_best_seconds),
                "gap_to_fastest_lap": format_gap(gap_to_fastest_lap),
                "driver_s1_best": seconds_to_sector_time(driver_s1_best),
                "gap_to_s1_best": format_gap(gap_to_s1),
                "driver_s2_best": seconds_to_sector_time(driver_s2_best),
                "gap_to_s2_best": format_gap(gap_to_s2),
                "driver_s3_best": seconds_to_sector_time(driver_s3_best),
                "gap_to_s3_best": format_gap(gap_to_s3),
            }
        except Exception as e:
            print(f"Error loading lap analysis for {track_key} R{race_num}: {e}")
            return None

    def calculate_season_averages(self, results: List[RaceResult]) -> Dict:
        """Calculate season averages from race results."""
        if not results:
            return {
                "avg_start": 0.0,
                "avg_finish": 0.0,
                "avg_gain": 0.0,
            }

        total_races = len(results)
        total_start = sum(r.start_position for r in results if r.start_position)
        total_finish = sum(r.finish_position for r in results if r.finish_position)
        total_gain = sum(r.positions_gained for r in results if r.positions_gained)

        return {
            "avg_start": total_start / total_races if total_races > 0 else 0.0,
            "avg_finish": total_finish / total_races if total_races > 0 else 0.0,
            "avg_gain": total_gain / total_races if total_races > 0 else 0.0,
        }
