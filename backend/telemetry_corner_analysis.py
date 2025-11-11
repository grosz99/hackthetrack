"""
Telemetry Corner Analysis System

Processes high-frequency telemetry data (20-40Hz) to extract corner-specific metrics
for driver coaching and performance comparison.

Features:
- Automatic corner detection using steering angle + lateral G
- Corner metric extraction (braking point, entry/apex/exit speeds, etc.)
- Driver comparison analysis
- Efficient chunked processing for large datasets

Author: Data Intelligence Team
Created: 2025-11-10
"""

import pandas as pd
import numpy as np
import json
from pathlib import Path
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass, asdict
import warnings
from datetime import datetime
import time

warnings.filterwarnings('ignore')


@dataclass
class CornerMetrics:
    """Container for corner-specific telemetry metrics."""
    corner_number: int
    distance_start_m: float
    distance_apex_m: float
    distance_exit_m: float
    braking_point_m: float
    brake_pressure_max_bar: float
    entry_speed_kmh: float
    apex_speed_kmh: float
    exit_speed_kmh: float
    corner_time_s: float
    lateral_g_max: float
    steering_angle_max_deg: float
    throttle_application_point_m: float
    steering_smoothness: float


class CornerDetector:
    """
    Automatic corner detection using steering angle and lateral G-force analysis.

    Uses hybrid approach combining steering input and vehicle dynamics to identify
    corner entry, apex, and exit points.
    """

    def __init__(
        self,
        steering_threshold_deg: float = 30.0,
        lateral_g_threshold: float = 0.8,
        min_corner_duration_s: float = 0.5,
        merge_gap_m: float = 50.0
    ):
        """
        Initialize corner detector with configurable thresholds.

        Args:
            steering_threshold_deg: Minimum steering angle to consider cornering
            lateral_g_threshold: Minimum lateral G-force to confirm corner
            min_corner_duration_s: Minimum time to qualify as corner vs kink
            merge_gap_m: Distance gap to merge consecutive corner sections
        """
        self.steering_threshold = steering_threshold_deg
        self.lateral_g_threshold = lateral_g_threshold
        self.min_corner_duration = min_corner_duration_s
        self.merge_gap = merge_gap_m

    def detect_corners(self, lap_data: pd.DataFrame) -> List[Dict]:
        """
        Detect all corners in a single lap using telemetry signals.

        Args:
            lap_data: DataFrame with telemetry for one lap

        Returns:
            List of corner dictionaries with entry/apex/exit points
        """
        if len(lap_data) < 10:
            return []

        # Calculate corner indicators
        lap_data = lap_data.copy()
        lap_data['abs_steering'] = lap_data['Steering_Angle'].abs()
        lap_data['abs_lateral_g'] = lap_data['accy_can'].abs()

        # Identify cornering zones
        is_cornering = (
            (lap_data['abs_steering'] > self.steering_threshold) &
            (lap_data['abs_lateral_g'] > self.lateral_g_threshold)
        )

        # Find continuous corner zones
        corner_zones = self._find_continuous_zones(lap_data, is_cornering)

        # Filter by minimum duration
        corner_zones = self._filter_by_duration(lap_data, corner_zones)

        # Merge nearby corners (chicanes)
        corner_zones = self._merge_nearby_corners(corner_zones)

        # Calculate corner details
        corners = []
        for i, zone in enumerate(corner_zones, 1):
            corner = self._analyze_corner_zone(lap_data, zone, i)
            if corner:
                corners.append(corner)

        return corners

    def _find_continuous_zones(
        self,
        lap_data: pd.DataFrame,
        mask: pd.Series
    ) -> List[Tuple[int, int]]:
        """Find continuous True zones in boolean mask."""
        zones = []
        in_zone = False
        start_idx = None

        for idx, value in enumerate(mask):
            if value and not in_zone:
                # Start of new zone
                in_zone = True
                start_idx = idx
            elif not value and in_zone:
                # End of zone
                in_zone = False
                zones.append((start_idx, idx - 1))

        # Handle zone extending to end of lap
        if in_zone:
            zones.append((start_idx, len(mask) - 1))

        return zones

    def _filter_by_duration(
        self,
        lap_data: pd.DataFrame,
        zones: List[Tuple[int, int]]
    ) -> List[Tuple[int, int]]:
        """Filter zones by minimum duration."""
        filtered_zones = []

        for start_idx, end_idx in zones:
            zone_data = lap_data.iloc[start_idx:end_idx + 1]

            # Calculate duration using timestamp
            if len(zone_data) < 2:
                continue

            try:
                start_time = pd.to_datetime(zone_data.iloc[0]['timestamp'])
                end_time = pd.to_datetime(zone_data.iloc[-1]['timestamp'])
                duration = (end_time - start_time).total_seconds()

                if duration >= self.min_corner_duration:
                    filtered_zones.append((start_idx, end_idx))
            except:
                # If timestamp parsing fails, use sampling rate estimate
                duration = len(zone_data) * 0.04  # Assume ~25Hz
                if duration >= self.min_corner_duration:
                    filtered_zones.append((start_idx, end_idx))

        return filtered_zones

    def _merge_nearby_corners(
        self,
        zones: List[Tuple[int, int]]
    ) -> List[Tuple[int, int]]:
        """Merge corner zones that are close together (chicanes)."""
        if not zones:
            return zones

        merged = [zones[0]]

        for current_start, current_end in zones[1:]:
            last_start, last_end = merged[-1]

            gap = current_start - last_end

            if gap <= self.merge_gap:
                # Merge with previous zone
                merged[-1] = (last_start, current_end)
            else:
                # Add as separate zone
                merged.append((current_start, current_end))

        return merged

    def _analyze_corner_zone(
        self,
        lap_data: pd.DataFrame,
        zone: Tuple[int, int],
        corner_num: int
    ) -> Optional[Dict]:
        """Extract detailed metrics from a corner zone."""
        start_idx, end_idx = zone
        corner_data = lap_data.iloc[start_idx:end_idx + 1].copy()

        if len(corner_data) < 3:
            return None

        try:
            # Find apex (minimum speed in corner)
            apex_idx = corner_data['speed'].idxmin()
            apex_data = corner_data.loc[apex_idx]

            # Calculate corner phases
            entry_idx = corner_data.index[0]
            exit_idx = corner_data.index[-1]

            corner = {
                'number': corner_num,
                'distance_start_m': float(corner_data.iloc[0]['Laptrigger_lapdist_dls']),
                'distance_apex_m': float(apex_data['Laptrigger_lapdist_dls']),
                'distance_exit_m': float(corner_data.iloc[-1]['Laptrigger_lapdist_dls']),
                'entry_speed_kmh': float(corner_data.iloc[0]['speed']),
                'apex_speed_kmh': float(apex_data['speed']),
                'exit_speed_kmh': float(corner_data.iloc[-1]['speed']),
                'lateral_g_max': float(corner_data['abs_lateral_g'].max()),
                'steering_angle_max_deg': float(corner_data['abs_steering'].max()),
                'steering_smoothness': float(corner_data['Steering_Angle'].std())
            }

            # Calculate corner time
            try:
                start_time = pd.to_datetime(corner_data.iloc[0]['timestamp'])
                end_time = pd.to_datetime(corner_data.iloc[-1]['timestamp'])
                corner['corner_time_s'] = (end_time - start_time).total_seconds()
            except:
                corner['corner_time_s'] = len(corner_data) * 0.04

            # Find braking point (before corner entry)
            braking_point = self._find_braking_point(
                lap_data,
                start_idx,
                corner_data.iloc[0]['Laptrigger_lapdist_dls']
            )
            corner['braking_point_m'] = braking_point['distance']
            corner['brake_pressure_max_bar'] = braking_point['max_pressure']

            # Find throttle application point
            throttle_point = self._find_throttle_point(corner_data, apex_idx)
            corner['throttle_application_point_m'] = throttle_point

            return corner

        except Exception as e:
            print(f"Warning: Failed to analyze corner {corner_num}: {e}")
            return None

    def _find_braking_point(
        self,
        lap_data: pd.DataFrame,
        corner_start_idx: int,
        corner_start_distance: float
    ) -> Dict:
        """Find braking point before corner entry."""
        # Look back up to 100 rows before corner
        lookback_start = max(0, corner_start_idx - 100)
        braking_zone = lap_data.iloc[lookback_start:corner_start_idx]

        if len(braking_zone) == 0:
            return {'distance': corner_start_distance, 'max_pressure': 0.0}

        # Find where brake pressure exceeds threshold
        brake_threshold = 20.0  # bar
        braking_mask = braking_zone['pbrake_f'] > brake_threshold

        if braking_mask.any():
            first_brake_idx = braking_mask.idxmax()
            braking_data = braking_zone.loc[first_brake_idx:corner_start_idx - 1]

            return {
                'distance': float(braking_zone.loc[first_brake_idx, 'Laptrigger_lapdist_dls']),
                'max_pressure': float(braking_data['pbrake_f'].max())
            }

        return {'distance': corner_start_distance, 'max_pressure': 0.0}

    def _find_throttle_point(
        self,
        corner_data: pd.DataFrame,
        apex_idx: int
    ) -> float:
        """Find where driver gets back to throttle after apex."""
        # Look from apex onwards
        post_apex = corner_data.loc[apex_idx:]

        if len(post_apex) < 2:
            return float(corner_data.loc[apex_idx, 'Laptrigger_lapdist_dls'])

        # Find where throttle exceeds 50%
        throttle_threshold = 50.0
        throttle_mask = post_apex['aps'] > throttle_threshold

        if throttle_mask.any():
            throttle_idx = throttle_mask.idxmax()
            return float(post_apex.loc[throttle_idx, 'Laptrigger_lapdist_dls'])

        return float(corner_data.iloc[-1]['Laptrigger_lapdist_dls'])


class TelemetryProcessor:
    """
    Main processor for telemetry data analysis.

    Handles data loading, corner detection, metric extraction, and output generation.
    """

    def __init__(self, data_dir: str = "data/telemetry/processed"):
        """
        Initialize processor with data directory.

        Args:
            data_dir: Path to directory containing telemetry CSV files
        """
        self.data_dir = Path(data_dir)
        self.corner_detector = CornerDetector()
        self.results = {}

    def process_race(
        self,
        track_name: str,
        race_num: int,
        vehicle_numbers: Optional[List[int]] = None,
        best_lap_only: bool = True
    ) -> Dict:
        """
        Process telemetry for a single race.

        Args:
            track_name: Track identifier (e.g., 'barber')
            race_num: Race number (1 or 2)
            vehicle_numbers: List of vehicle numbers to process (None = all)
            best_lap_only: If True, only analyze best lap per driver

        Returns:
            Dictionary with race analysis results
        """
        print(f"\n{'='*80}")
        print(f"Processing: {track_name.upper()} Race {race_num}")
        print(f"{'='*80}")

        start_time = time.time()

        # Load telemetry data
        filename = f"{track_name}_r{race_num}_wide.csv"
        filepath = self.data_dir / filename

        if not filepath.exists():
            print(f"ERROR: File not found: {filepath}")
            return {}

        print(f"Loading data from {filename}...")
        df = pd.read_csv(filepath)
        print(f"Loaded {len(df):,} rows, {df['Laptrigger_lapdist_dls'].memory_usage()/1024/1024:.1f} MB")

        # Filter vehicles if specified
        if vehicle_numbers:
            df = df[df['vehicle_number'].isin(vehicle_numbers)]

        # Process each driver
        race_results = {
            'track_name': track_name,
            'race_num': race_num,
            'drivers': {}
        }

        unique_vehicles = sorted(df['vehicle_number'].unique())
        print(f"\nProcessing {len(unique_vehicles)} drivers: {unique_vehicles}")

        for vehicle_num in unique_vehicles:
            driver_results = self._process_driver(
                df,
                vehicle_num,
                best_lap_only
            )
            race_results['drivers'][str(vehicle_num)] = driver_results

        elapsed = time.time() - start_time
        print(f"\nRace processing completed in {elapsed:.1f}s")

        return race_results

    def _process_driver(
        self,
        df: pd.DataFrame,
        vehicle_num: int,
        best_lap_only: bool
    ) -> Dict:
        """Process telemetry for a single driver."""
        print(f"\n  Driver {vehicle_num}:")

        driver_data = df[df['vehicle_number'] == vehicle_num].copy()

        if len(driver_data) == 0:
            print(f"    No data found")
            return {}

        # Find best lap
        lap_times = self._calculate_lap_times(driver_data)
        best_lap_num = lap_times['lap_num'].iloc[0] if len(lap_times) > 0 else None
        best_lap_time = lap_times['lap_time_s'].iloc[0] if len(lap_times) > 0 else None

        print(f"    Laps: {sorted(driver_data['lap'].unique())}")
        print(f"    Best lap: {best_lap_num} ({best_lap_time:.2f}s)")

        # Process laps
        laps_to_process = [best_lap_num] if best_lap_only and best_lap_num else driver_data['lap'].unique()

        driver_results = {
            'best_lap_num': int(best_lap_num) if best_lap_num else None,
            'best_lap_time_s': float(best_lap_time) if best_lap_time else None,
            'laps_analyzed': []
        }

        for lap_num in laps_to_process:
            lap_data = driver_data[driver_data['lap'] == lap_num].copy()
            lap_data = lap_data.sort_values('Laptrigger_lapdist_dls')

            if len(lap_data) < 50:  # Skip incomplete laps
                continue

            # Detect corners
            corners = self.corner_detector.detect_corners(lap_data)

            if lap_num == best_lap_num:
                print(f"    Corners detected: {len(corners)}")

            driver_results['laps_analyzed'].append({
                'lap_num': int(lap_num),
                'corners': corners
            })

        return driver_results

    def _calculate_lap_times(self, driver_data: pd.DataFrame) -> pd.DataFrame:
        """Calculate lap times from telemetry."""
        lap_times = []

        for lap_num in driver_data['lap'].unique():
            lap_data = driver_data[driver_data['lap'] == lap_num]

            if len(lap_data) < 50:  # Skip incomplete laps
                continue

            try:
                lap_data = lap_data.sort_values('timestamp')
                start_time = pd.to_datetime(lap_data.iloc[0]['timestamp'])
                end_time = pd.to_datetime(lap_data.iloc[-1]['timestamp'])
                lap_time = (end_time - start_time).total_seconds()

                # Sanity check (typical lap times 60-120s)
                if 50 < lap_time < 200:
                    lap_times.append({
                        'lap_num': lap_num,
                        'lap_time_s': lap_time
                    })
            except:
                continue

        if lap_times:
            return pd.DataFrame(lap_times).sort_values('lap_time_s')
        else:
            return pd.DataFrame(columns=['lap_num', 'lap_time_s'])

    def save_results(self, results: Dict, output_path: str):
        """Save analysis results to JSON file."""
        output_file = Path(output_path)
        output_file.parent.mkdir(parents=True, exist_ok=True)

        with open(output_file, 'w') as f:
            json.dump(results, f, indent=2)

        file_size_mb = output_file.stat().st_size / 1024 / 1024
        print(f"\nResults saved to: {output_file}")
        print(f"File size: {file_size_mb:.2f} MB")


def compare_drivers(
    results: Dict,
    driver_a: int,
    driver_b: int,
    corner_num: int
) -> Dict:
    """
    Compare two drivers on a specific corner.

    Args:
        results: Race analysis results dictionary
        driver_a: First driver number
        driver_b: Second driver number
        corner_num: Corner number to compare

    Returns:
        Comparison dictionary with insights
    """
    drivers = results.get('drivers', {})

    driver_a_data = drivers.get(str(driver_a), {})
    driver_b_data = drivers.get(str(driver_b), {})

    if not driver_a_data or not driver_b_data:
        return {'error': 'Driver data not found'}

    # Get best lap corners
    driver_a_laps = driver_a_data.get('laps_analyzed', [])
    driver_b_laps = driver_b_data.get('laps_analyzed', [])

    if not driver_a_laps or not driver_b_laps:
        return {'error': 'No lap data found'}

    # Find the corner in each driver's best lap
    corner_a = None
    corner_b = None

    for lap in driver_a_laps:
        if lap['lap_num'] == driver_a_data['best_lap_num']:
            corners = lap['corners']
            if corner_num <= len(corners):
                corner_a = corners[corner_num - 1]
            break

    for lap in driver_b_laps:
        if lap['lap_num'] == driver_b_data['best_lap_num']:
            corners = lap['corners']
            if corner_num <= len(corners):
                corner_b = corners[corner_num - 1]
            break

    if not corner_a or not corner_b:
        return {'error': f'Corner {corner_num} not found for both drivers'}

    # Calculate differences
    comparison = {
        'track': results.get('track_name'),
        'race': results.get('race_num'),
        'corner_number': corner_num,
        'driver_a': driver_a,
        'driver_b': driver_b,
        'driver_a_metrics': corner_a,
        'driver_b_metrics': corner_b,
        'differences': {
            'braking_point_m': corner_b['braking_point_m'] - corner_a['braking_point_m'],
            'entry_speed_kmh': corner_b['entry_speed_kmh'] - corner_a['entry_speed_kmh'],
            'apex_speed_kmh': corner_b['apex_speed_kmh'] - corner_a['apex_speed_kmh'],
            'exit_speed_kmh': corner_b['exit_speed_kmh'] - corner_a['exit_speed_kmh'],
            'corner_time_s': corner_b['corner_time_s'] - corner_a['corner_time_s'],
            'throttle_application_point_m': (
                corner_b['throttle_application_point_m'] -
                corner_a['throttle_application_point_m']
            )
        },
        'coaching_insights': []
    }

    # Generate coaching insights
    insights = []

    # Braking point
    brake_diff = comparison['differences']['braking_point_m']
    if abs(brake_diff) > 5:
        direction = 'later' if brake_diff > 0 else 'earlier'
        insights.append(
            f"Driver {driver_b} brakes {abs(brake_diff):.1f}m {direction} "
            f"({corner_a['braking_point_m']:.1f}m vs {corner_b['braking_point_m']:.1f}m)"
        )

    # Entry speed
    entry_diff = comparison['differences']['entry_speed_kmh']
    if abs(entry_diff) > 2:
        direction = 'more' if entry_diff > 0 else 'less'
        insights.append(
            f"Driver {driver_b} carries {abs(entry_diff):.1f} km/h {direction} entry speed "
            f"({corner_a['entry_speed_kmh']:.1f} vs {corner_b['entry_speed_kmh']:.1f})"
        )

    # Apex speed
    apex_diff = comparison['differences']['apex_speed_kmh']
    if abs(apex_diff) > 1:
        direction = 'higher' if apex_diff > 0 else 'lower'
        insights.append(
            f"Apex speed is {abs(apex_diff):.1f} km/h {direction} for driver {driver_b} "
            f"({corner_a['apex_speed_kmh']:.1f} vs {corner_b['apex_speed_kmh']:.1f})"
        )

    # Exit speed
    exit_diff = comparison['differences']['exit_speed_kmh']
    if abs(exit_diff) > 2:
        direction = 'higher' if exit_diff > 0 else 'lower'
        insights.append(
            f"Driver {driver_b} has {abs(exit_diff):.1f} km/h {direction} exit speed "
            f"({corner_a['exit_speed_kmh']:.1f} vs {corner_b['exit_speed_kmh']:.1f})"
        )

    # Corner time
    time_diff = comparison['differences']['corner_time_s']
    if abs(time_diff) > 0.05:
        direction = 'faster' if time_diff < 0 else 'slower'
        insights.append(
            f"Driver {driver_b} is {abs(time_diff):.2f}s {direction} through the corner "
            f"({corner_a['corner_time_s']:.2f}s vs {corner_b['corner_time_s']:.2f}s)"
        )

    comparison['coaching_insights'] = insights

    return comparison


def print_comparison_report(comparison: Dict):
    """Print formatted comparison report."""
    print(f"\n{'='*80}")
    print(f"CORNER COMPARISON: {comparison['track'].upper()} Race {comparison['race']}")
    print(f"Corner {comparison['corner_number']}: Driver {comparison['driver_a']} vs Driver {comparison['driver_b']}")
    print(f"{'='*80}\n")

    print("Coaching Insights:")
    for insight in comparison['coaching_insights']:
        print(f"  • {insight}")

    print(f"\n{'='*80}\n")


if __name__ == "__main__":
    # Example usage: Process Barber Race 1, compare drivers 7 and 13 on Turn 1

    processor = TelemetryProcessor(
        data_dir="/Users/justingrosz/Documents/AI-Work/hackthetrack-master/data/telemetry/processed"
    )

    # Process race (just drivers 7 and 13 for speed)
    results = processor.process_race(
        track_name="barber",
        race_num=1,
        vehicle_numbers=[7, 13],
        best_lap_only=True
    )

    # Save results
    processor.save_results(
        results,
        "/Users/justingrosz/Documents/AI-Work/hackthetrack-master/backend/data/corner_analysis_barber_r1.json"
    )

    # Compare drivers on Turn 1
    comparison = compare_drivers(results, driver_a=7, driver_b=13, corner_num=1)
    print_comparison_report(comparison)

    # Save comparison
    with open(
        "/Users/justingrosz/Documents/AI-Work/hackthetrack-master/backend/data/corner_comparison_example.json",
        'w'
    ) as f:
        json.dump(comparison, f, indent=2)
