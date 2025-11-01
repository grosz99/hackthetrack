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

        # 4. Calculate positions gained
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
            "barber": None,  # No qualifying files for barber yet
            "cota": f"Cotard{race_num}Qualifying.csv",
            "roadamerica": None,
            "sebring": f"Sebringrd{race_num}Qualifying.csv",
            "sonoma": f"Sonomard{race_num}Qualifying.csv",
            "vir": f"VIRd{race_num}Qualifying.csv",
        }

        qual_filename = qual_file_map.get(track_key)
        if not qual_filename:
            return None

        file_path = self.race_results_path / "qualifying" / qual_filename

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
