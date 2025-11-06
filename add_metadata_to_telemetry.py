"""
Add track_id and race_num columns to telemetry CSV files.

This script reads each telemetry CSV file, extracts the track and race number
from the filename, and adds those as columns to the CSV.
"""

import pandas as pd
from pathlib import Path
from typing import Tuple


def parse_filename(filename: str) -> Tuple[str, int]:
    """
    Extract track_id and race_num from filename.

    Args:
        filename: CSV filename (e.g., 'barber_r1_wide.csv')

    Returns:
        Tuple of (track_id, race_num)

    Example:
        >>> parse_filename('barber_r1_wide.csv')
        ('barber', 1)
        >>> parse_filename('sonoma_r2_wide.csv')
        ('sonoma', 2)
    """
    # Remove _wide.csv or .csv suffix
    base = filename.replace('_wide.csv', '').replace('.csv', '')

    # Handle files with " (1)" suffix
    base = base.replace(' (1)', '')

    # Split by underscore
    parts = base.split('_')

    # Last part should be race number (r1, r2)
    race_part = parts[-1]
    race_num = int(race_part.replace('r', ''))

    # Everything before race number is track_id
    track_id = '_'.join(parts[:-1])

    return track_id, race_num


def add_metadata_to_csv(file_path: Path, output_dir: Path):
    """
    Add track_id and race_num columns to a CSV file.

    Args:
        file_path: Path to input CSV file
        output_dir: Directory to save updated CSV file
    """
    print(f"\nProcessing: {file_path.name}")

    # Parse filename
    track_id, race_num = parse_filename(file_path.name)
    print(f"  Track: {track_id}")
    print(f"  Race: {race_num}")

    # Read CSV
    print(f"  Reading CSV...")
    df = pd.read_csv(file_path)
    original_rows = len(df)
    print(f"  Rows: {original_rows:,}")

    # Add metadata columns at the beginning
    df.insert(0, 'race_num', race_num)
    df.insert(0, 'track_id', track_id)

    # Save updated CSV
    output_path = output_dir / file_path.name
    print(f"  Writing to: {output_path.name}")
    df.to_csv(output_path, index=False)

    # Verify
    verify_df = pd.read_csv(output_path)
    print(f"  ✓ Verified: {len(verify_df):,} rows")
    print(f"  ✓ Columns: {list(verify_df.columns[:5])}...")

    # Show file size
    file_size_mb = output_path.stat().st_size / (1024 * 1024)
    print(f"  ✓ File size: {file_size_mb:.1f} MB")


def main():
    """Process all telemetry CSV files."""
    # Directories
    data_dir = Path(__file__).parent / "data" / "telemetry"
    output_dir = data_dir / "processed"

    # Create output directory
    output_dir.mkdir(exist_ok=True)

    print("=" * 70)
    print("ADD METADATA TO TELEMETRY CSV FILES")
    print("=" * 70)
    print(f"Input directory:  {data_dir}")
    print(f"Output directory: {output_dir}")

    # Find all telemetry CSV files (excluding already processed ones)
    pattern = "*_r[12]_wide*.csv"
    files = sorted([f for f in data_dir.glob(pattern) if f.is_file()])

    # Filter out the reduced file if you want to process the full sonoma_r1
    files = [f for f in files if 'reduced' not in f.name]

    print(f"\nFound {len(files)} files to process:")
    for f in files:
        size_mb = f.stat().st_size / (1024 * 1024)
        print(f"  - {f.name:<40} ({size_mb:>6.1f} MB)")

    if not files:
        print("\n❌ No telemetry files found!")
        return

    # Process each file
    print("\n" + "=" * 70)
    print("PROCESSING FILES")
    print("=" * 70)

    success_count = 0
    for file_path in files:
        try:
            add_metadata_to_csv(file_path, output_dir)
            success_count += 1
        except Exception as e:
            print(f"  ❌ Error: {e}")
            import traceback
            traceback.print_exc()
            continue

    print("\n" + "=" * 70)
    print("SUMMARY")
    print("=" * 70)
    print(f"Successfully processed: {success_count}/{len(files)} files")
    print(f"Output directory: {output_dir}")
    print("\n✓ Done!")


if __name__ == "__main__":
    main()
