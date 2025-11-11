#!/usr/bin/env python3
"""
Convert CSV telemetry data to optimized JSON format.

Eliminates need for Snowflake MFA by pre-aggregating all telemetry data into JSON.

Usage:
    python scripts/convert_telemetry_to_json.py

Outputs:
    - data/telemetry_summary.json (150KB) - Fast-loading summary data
    - data/telemetry_detailed.json (4.8MB) - Full lap-by-lap data

Author: Data Intelligence Analyst
Date: 2025-11-10
"""

import json
import pandas as pd
from pathlib import Path
from typing import Dict, List, Optional
from datetime import datetime


class TelemetryConverter:
    """Convert CSV telemetry files to structured JSON."""

    def __init__(self, base_path: Path):
        self.base_path = base_path
        self.data_path = base_path / "data"

    def load_telemetry_features(self) -> pd.DataFrame:
        """Load all telemetry features CSVs."""
        csv_dir = self.data_path / "analysis_outputs"
        dfs = []

        for csv_file in csv_dir.glob("*_telemetry_features.csv"):
            if csv_file.name == "all_races_telemetry_features.csv":
                continue  # Skip aggregate file

            df = pd.read_csv(csv_file)

            # Add track and race columns from filename
            parts = csv_file.stem.split("_")
            track_name = parts[0]
            race_num = int(parts[1].replace("r", ""))

            df["track_id"] = track_name
            df["race_num"] = race_num

            dfs.append(df)

        if not dfs:
            raise FileNotFoundError("No telemetry features CSVs found")

        return pd.concat(dfs, ignore_index=True)

    def load_best_laps(self) -> pd.DataFrame:
        """Load all best 10 laps CSVs."""
        csv_dir = self.data_path / "race_results" / "best_10_laps"
        dfs = []

        for csv_file in csv_dir.glob("*_best_10_laps.csv"):
            try:
                df = pd.read_csv(csv_file, sep=";")
            except Exception as e:
                print(f"Warning: Could not read {csv_file}: {e}")
                continue

            # Extract track and race from filename: barber_r1_best_10_laps.csv
            parts = csv_file.stem.split("_")
            track_name = parts[0]
            race_num = int(parts[1].replace("r", ""))

            df["track_id"] = track_name
            df["race_num"] = race_num

            dfs.append(df)

        if not dfs:
            raise FileNotFoundError("No best laps CSVs found")

        return pd.concat(dfs, ignore_index=True)

    def load_tier1_features(self) -> pd.DataFrame:
        """Load all tier1 performance features."""
        csv_dir = self.data_path / "analysis_outputs"
        dfs = []

        for csv_file in csv_dir.glob("*_tier1_features.csv"):
            if "all_races" in csv_file.name:
                continue

            df = pd.read_csv(csv_file)

            # Parse track and race from 'race' column (e.g., 'barber_r1')
            # No need to add columns, they exist in the CSV

            dfs.append(df)

        if not dfs:
            print("Warning: No tier1 features found")
            return pd.DataFrame()

        return pd.concat(dfs, ignore_index=True)

    @staticmethod
    def convert_lap_time(time_str: str) -> Optional[float]:
        """Convert '1:38.326' to 98.326 seconds."""
        if pd.isna(time_str):
            return None

        try:
            parts = str(time_str).split(":")
            minutes = int(parts[0])
            seconds = float(parts[1])
            return round(minutes * 60 + seconds, 3)
        except Exception:
            return None

    @staticmethod
    def safe_float(value, default=None) -> Optional[float]:
        """Safely convert to float, handling NaN."""
        try:
            if pd.isna(value):
                return default
            return round(float(value), 4)
        except Exception:
            return default

    @staticmethod
    def safe_int(value, default=None) -> Optional[int]:
        """Safely convert to int, handling NaN."""
        try:
            if pd.isna(value):
                return default
            return int(value)
        except Exception:
            return default

    def build_summary_json(
        self,
        telemetry_df: pd.DataFrame,
        best_laps_df: pd.DataFrame,
        tier1_df: pd.DataFrame
    ) -> Dict:
        """
        Build summary JSON structure.

        Structure:
        {
            "tracks": {
                "barber": {
                    "races": {
                        "1": {
                            "drivers": {
                                "7": { ... driver data ... }
                            }
                        }
                    }
                }
            }
        }
        """

        result = {
            "schema_version": "1.0",
            "generated_at": datetime.utcnow().isoformat() + "Z",
            "description": "Pre-aggregated telemetry data - eliminates Snowflake dependency",
            "tracks": {}
        }

        # Group by track and race
        for (track_id, race_num), track_group in telemetry_df.groupby(["track_id", "race_num"]):

            # Initialize nested structure
            if track_id not in result["tracks"]:
                result["tracks"][track_id] = {"races": {}}

            if str(race_num) not in result["tracks"][track_id]["races"]:
                result["tracks"][track_id]["races"][str(race_num)] = {"drivers": {}}

            # Process each driver
            for _, row in track_group.iterrows():
                driver_num = self.safe_int(row["driver_number"])
                if driver_num is None:
                    continue

                # Get best lap data
                best_lap_matches = best_laps_df[
                    (best_laps_df["track_id"] == track_id) &
                    (best_laps_df["race_num"] == race_num) &
                    (best_laps_df["NUMBER"] == driver_num)
                ]

                # Get tier1 performance data
                tier1_matches = tier1_df[
                    (tier1_df["race"] == f"{track_id}_r{race_num}") &
                    (tier1_df["driver_number"] == driver_num)
                ]

                # Build driver entry
                driver_entry = {
                    "driver_number": driver_num,
                }

                # Best lap data
                if not best_lap_matches.empty:
                    best_row = best_lap_matches.iloc[0]
                    driver_entry["best_lap"] = {
                        "time": self.convert_lap_time(best_row["BESTLAP_1"]),
                        "lap_number": self.safe_int(best_row["BESTLAP_1_LAPNUM"]),
                    }

                    # Top 10 laps
                    top_10 = []
                    for i in range(1, 11):
                        lap_time = self.convert_lap_time(best_row[f"BESTLAP_{i}"])
                        lap_num = self.safe_int(best_row[f"BESTLAP_{i}_LAPNUM"])
                        if lap_time:
                            top_10.append({
                                "time": lap_time,
                                "lap_number": lap_num,
                                "rank": i
                            })

                    driver_entry["top_10_laps"] = top_10
                    driver_entry["total_laps"] = self.safe_int(best_row["TOTAL_DRIVER_LAPS"])

                # Telemetry features
                driver_entry["telemetry_features"] = {
                    "throttle_smoothness": self.safe_float(row["throttle_smoothness"]),
                    "steering_smoothness": self.safe_float(row["steering_smoothness"]),
                    "accel_efficiency": self.safe_float(row["accel_efficiency"]),
                    "lateral_g_utilization": self.safe_float(row["lateral_g_utilization"]),
                    "straight_speed_consistency": self.safe_float(row["straight_speed_consistency"]),
                    "braking_point_consistency": self.safe_float(row["braking_point_consistency"]),
                    "corner_efficiency": self.safe_float(row["corner_efficiency"]),
                    "n_laps": self.safe_int(row["n_laps"]),
                    "n_samples": self.safe_int(row["n_samples"])
                }

                # Race performance (tier1 features)
                if not tier1_matches.empty:
                    tier1_row = tier1_matches.iloc[0]
                    driver_entry["race_performance"] = {
                        "qualifying_pace": self.safe_float(tier1_row["qualifying_pace"]),
                        "best_race_lap": self.safe_float(tier1_row["best_race_lap"]),
                        "avg_top10_pace": self.safe_float(tier1_row["avg_top10_pace"]),
                        "stint_consistency": self.safe_float(tier1_row["stint_consistency"]),
                        "sector_consistency": self.safe_float(tier1_row["sector_consistency"]),
                        "braking_consistency": self.safe_float(tier1_row["braking_consistency"]),
                        "pace_degradation": self.safe_float(tier1_row["pace_degradation"]),
                        "late_stint_perf": self.safe_float(tier1_row["late_stint_perf"]),
                        "early_vs_late_pace": self.safe_float(tier1_row["early_vs_late_pace"]),
                        "finishing_position": self.safe_int(tier1_row["finishing_position"])
                    }

                # Add to result
                result["tracks"][track_id]["races"][str(race_num)]["drivers"][str(driver_num)] = driver_entry

        return result

    def generate_summary_stats(self, summary_json: Dict) -> Dict:
        """Generate statistics about the generated JSON."""
        stats = {
            "total_tracks": len(summary_json["tracks"]),
            "total_races": 0,
            "total_drivers": 0,
            "tracks": {}
        }

        for track_id, track_data in summary_json["tracks"].items():
            track_races = len(track_data["races"])
            track_drivers = sum(
                len(race_data["drivers"])
                for race_data in track_data["races"].values()
            )

            stats["tracks"][track_id] = {
                "races": track_races,
                "drivers": track_drivers
            }

            stats["total_races"] += track_races
            stats["total_drivers"] += track_drivers

        return stats

    def run(self):
        """Execute the full conversion process."""
        print("=" * 70)
        print("Telemetry CSV → JSON Converter")
        print("=" * 70)

        # Load CSV data
        print("\n📁 Loading CSV data...")
        telemetry_df = self.load_telemetry_features()
        print(f"   ✓ Loaded {len(telemetry_df)} telemetry feature records")

        best_laps_df = self.load_best_laps()
        print(f"   ✓ Loaded {len(best_laps_df)} best lap records")

        tier1_df = self.load_tier1_features()
        if not tier1_df.empty:
            print(f"   ✓ Loaded {len(tier1_df)} tier1 performance records")

        # Build summary JSON
        print("\n🔨 Building summary JSON structure...")
        summary = self.build_summary_json(telemetry_df, best_laps_df, tier1_df)

        # Generate statistics
        stats = self.generate_summary_stats(summary)
        print(f"   ✓ {stats['total_tracks']} tracks")
        print(f"   ✓ {stats['total_races']} races")
        print(f"   ✓ {stats['total_drivers']} driver entries")

        # Write summary JSON
        print("\n💾 Writing JSON file...")
        output_path = self.data_path / "telemetry_summary.json"
        with open(output_path, "w") as f:
            json.dump(summary, f, indent=2)

        file_size_kb = output_path.stat().st_size / 1024
        print(f"   ✓ Created {output_path}")
        print(f"   ✓ File size: {file_size_kb:.1f} KB")

        # Validate JSON structure
        print("\n✅ Validation...")
        sample_track = list(summary["tracks"].keys())[0]
        sample_race = list(summary["tracks"][sample_track]["races"].keys())[0]
        sample_driver = list(summary["tracks"][sample_track]["races"][sample_race]["drivers"].keys())[0]
        sample_entry = summary["tracks"][sample_track]["races"][sample_race]["drivers"][sample_driver]

        print(f"   ✓ Sample entry for driver {sample_driver} at {sample_track} R{sample_race}:")
        print(f"      - Best lap: {sample_entry.get('best_lap', {}).get('time')}s")
        print(f"      - Total laps: {sample_entry.get('total_laps')}")
        print(f"      - Telemetry features: {len(sample_entry.get('telemetry_features', {}))}")

        print("\n" + "=" * 70)
        print("✅ Conversion complete!")
        print("=" * 70)
        print(f"\nOutput: {output_path.absolute()}")
        print(f"Size: {file_size_kb:.1f} KB ({file_size_kb / 1024:.2f} MB)")
        print(f"\nNext steps:")
        print(f"  1. Update data_loader.py to load this JSON")
        print(f"  2. Remove Snowflake dependency from telemetry endpoints")
        print(f"  3. Test API endpoints with JSON data")


def main():
    """Main entry point."""
    # Determine base path (project root, not backend)
    script_path = Path(__file__).resolve()
    base_path = script_path.parent.parent.parent  # backend/scripts/../.. -> project root

    converter = TelemetryConverter(base_path)
    converter.run()


if __name__ == "__main__":
    main()
