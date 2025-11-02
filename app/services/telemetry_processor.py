"""
Telemetry processing service for visualization data.
"""

import pandas as pd
from typing import Dict, List, Optional, Tuple
from pathlib import Path


class TelemetryProcessor:
    """Service for processing and aggregating telemetry data."""

    def __init__(self, data_path: Path):
        self.data_path = data_path
        self.telemetry_cache: Dict[str, pd.DataFrame] = {}

    def get_telemetry(self, track_id: str, race_num: int) -> Optional[pd.DataFrame]:
        """Load telemetry data with caching."""
        key = f"{track_id}_r{race_num}"

        if key not in self.telemetry_cache:
            path = self.data_path / "Telemetry" / f"{track_id}_r{race_num}_wide.csv"
            if path.exists():
                self.telemetry_cache[key] = pd.read_csv(path)
            else:
                return None

        return self.telemetry_cache.get(key)

    def identify_comparison_drivers(
        self,
        track_id: str,
        race_num: int,
        driver_number: int
    ) -> Dict[str, Optional[int]]:
        """
        Identify three-tier comparison drivers WITH telemetry data:
        1. next_tier: Driver 1-2 positions ahead (with telemetry)
        2. leader: Race winner or top performer (with telemetry)

        Returns:
            {"next_tier": 72, "leader": 13, "user_position": 3}
        """
        # Load race results to get finishing positions
        results_path = (
            self.data_path / "analysis_outputs" / f"{track_id}_r{race_num}_tier1_features.csv"
        )

        if not results_path.exists():
            return {"next_tier": None, "leader": None, "user_position": None}

        results = pd.read_csv(results_path)
        results = results.sort_values('finishing_position')

        # Find user's position
        user_row = results[results['driver_number'] == driver_number]
        if user_row.empty:
            return {"next_tier": None, "leader": None, "user_position": None}

        user_position = int(user_row.iloc[0]['finishing_position'])

        # Get telemetry data to check which drivers have data
        telemetry_df = self.get_telemetry(track_id, race_num)
        available_drivers = set()
        if telemetry_df is not None:
            available_drivers = set(telemetry_df['vehicle_number'].unique())

        # Find next tier (driver 1-2 positions ahead WITH telemetry)
        next_tier = None
        if user_position > 1:
            # Look for nearest driver ahead with telemetry data
            for pos in range(user_position - 1, 0, -1):
                candidate_row = results[results['finishing_position'] == pos]
                if not candidate_row.empty:
                    candidate_driver = int(candidate_row.iloc[0]['driver_number'])
                    if candidate_driver in available_drivers:
                        next_tier = candidate_driver
                        break
        else:
            # User is P1 - next_tier is P2 (next best available)
            for pos in range(2, len(results) + 1):
                candidate_row = results[results['finishing_position'] == pos]
                if not candidate_row.empty:
                    candidate_driver = int(candidate_row.iloc[0]['driver_number'])
                    if candidate_driver in available_drivers:
                        next_tier = candidate_driver
                        break

        # Find leader (best driver that's not the user, WITH telemetry)
        leader = None
        for pos in range(1, len(results) + 1):
            candidate_row = results[results['finishing_position'] == pos]
            if not candidate_row.empty:
                candidate_driver = int(candidate_row.iloc[0]['driver_number'])
                if candidate_driver != driver_number and candidate_driver in available_drivers:
                    leader = candidate_driver
                    break

        return {
            "next_tier": next_tier,
            "leader": leader,
            "user_position": user_position
        }

    def get_driver_lap_telemetry(
        self,
        track_id: str,
        race_num: int,
        driver_number: int,
        lap_number: Optional[int] = None
    ) -> Optional[pd.DataFrame]:
        """
        Get telemetry for a specific driver and lap.
        If lap_number is None, returns best lap.
        """
        df = self.get_telemetry(track_id, race_num)
        if df is None:
            return None

        driver_data = df[df['vehicle_number'] == driver_number].copy()

        if driver_data.empty:
            return None

        if lap_number is None:
            # Find best lap (fastest average speed or lap time if available)
            lap_speeds = driver_data.groupby('lap')['speed'].mean()
            best_lap = lap_speeds.idxmax()
            lap_number = best_lap

        return driver_data[driver_data['lap'] == lap_number]

    def downsample_telemetry(
        self,
        df: pd.DataFrame,
        target_points: int = 500
    ) -> pd.DataFrame:
        """
        Downsample telemetry data for visualization performance.
        Keeps first, last, and evenly spaced points.
        """
        if len(df) <= target_points:
            return df

        step = len(df) // target_points
        indices = list(range(0, len(df), step))

        # Ensure first and last points are included
        if indices[0] != 0:
            indices = [0] + indices
        if indices[-1] != len(df) - 1:
            indices.append(len(df) - 1)

        return df.iloc[indices]

    def create_speed_trace(
        self,
        track_id: str,
        race_num: int,
        driver_number: int,
        comparison_drivers: Dict[str, Optional[int]],
        lap_number: Optional[int] = None
    ) -> Dict:
        """
        Create speed trace data for three-tier comparison.

        Returns:
            {
                "user": {driver: 13, lap: 5, data: [...]},
                "next_tier": {driver: 72, lap: 5, data: [...]},
                "leader": {driver: 22, lap: 4, data: [...]}
            }
        """
        result = {}

        # Get user's telemetry
        user_data = self.get_driver_lap_telemetry(track_id, race_num, driver_number, lap_number)
        if user_data is not None:
            user_data = self.downsample_telemetry(user_data, target_points=500)
            result["user"] = {
                "driver_number": driver_number,
                "lap": int(user_data.iloc[0]['lap']),
                "speed": user_data['speed'].ffill().bfill().tolist(),
                "distance": list(range(len(user_data))),  # Normalized distance
                "brake_pressure": user_data['pbrake_f'].fillna(0).tolist(),
                "steering_angle": user_data['Steering_Angle'].fillna(0).tolist()
            }

        # Get next tier telemetry
        if comparison_drivers.get("next_tier"):
            next_tier_data = self.get_driver_lap_telemetry(
                track_id, race_num, comparison_drivers["next_tier"], lap_number
            )
            if next_tier_data is not None:
                next_tier_data = self.downsample_telemetry(next_tier_data, target_points=500)
                result["next_tier"] = {
                    "driver_number": comparison_drivers["next_tier"],
                    "lap": int(next_tier_data.iloc[0]['lap']),
                    "speed": next_tier_data['speed'].ffill().bfill().tolist(),
                    "distance": list(range(len(next_tier_data))),
                    "brake_pressure": next_tier_data['pbrake_f'].fillna(0).tolist()
                }

        # Get leader telemetry
        if comparison_drivers.get("leader") and comparison_drivers["leader"] != driver_number:
            leader_data = self.get_driver_lap_telemetry(
                track_id, race_num, comparison_drivers["leader"], lap_number
            )
            if leader_data is not None:
                leader_data = self.downsample_telemetry(leader_data, target_points=500)
                result["leader"] = {
                    "driver_number": comparison_drivers["leader"],
                    "lap": int(leader_data.iloc[0]['lap']),
                    "speed": leader_data['speed'].ffill().bfill().tolist(),
                    "distance": list(range(len(leader_data))),
                    "brake_pressure": leader_data['pbrake_f'].fillna(0).tolist()
                }

        return result


# Global instance
telemetry_processor = None

def get_telemetry_processor(data_path: Path):
    """Get or create telemetry processor instance."""
    global telemetry_processor
    if telemetry_processor is None:
        telemetry_processor = TelemetryProcessor(data_path)
    return telemetry_processor
