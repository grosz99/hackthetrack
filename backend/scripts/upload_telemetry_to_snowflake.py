"""
Upload telemetry CSV files to Snowflake.

This script reads all processed telemetry CSV files (with track_id and race_num)
and uploads them to the Snowflake TELEMETRY_DATA_ALL table.
"""

import sys
from pathlib import Path
import pandas as pd
from typing import List

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.services.snowflake_service import snowflake_service


def get_telemetry_files(data_dir: str) -> List[Path]:
    """Find all telemetry CSV files."""
    data_path = Path(data_dir)
    return sorted(data_path.glob("*_r[12]_wide.csv"))


def parse_filename(filename: str) -> tuple:
    """
    Extract track_id and race_num from filename.

    Example: barber_r1_wide.csv -> ('barber', 1)
    """
    parts = filename.replace('_wide.csv', '').split('_')
    track_id = parts[0]
    race_num = int(parts[1].replace('r', ''))
    return track_id, race_num


def upload_file(file_path: Path):
    """Upload a single CSV file to Snowflake."""
    print(f"\n{'='*60}")
    print(f"Processing: {file_path.name}")
    print(f"{'='*60}")

    # Read CSV (already has track_id and race_num from processing)
    print("Reading CSV file...")
    df = pd.read_csv(file_path)
    print(f"  Rows: {len(df):,}")
    print(f"  Columns: {len(df.columns)}")

    # Get track_id and race_num from the CSV columns
    track_id = df['track_id'].iloc[0]
    race_num = int(df['race_num'].iloc[0])
    print(f"  Track: {track_id} | Race: {race_num}")
    print(f"  Drivers: {sorted(df['vehicle_number'].unique())}")

    # Prepare data for Snowflake (track_id and race_num already in CSV)
    print("Preparing data...")

    # Use all columns as-is (already have track_id, race_num, vehicle_number, etc.)
    df_upload = df.copy()

    # Replace NaN with None (NULL in SQL)
    df_upload = df_upload.where(pd.notnull(df_upload), None)

    print("Uploading to Snowflake...")
    conn = snowflake_service.get_connection()

    try:
        cursor = conn.cursor()

        # Delete existing data for this track/race (in case of re-upload)
        delete_query = """
            DELETE FROM HACKTHETRACK.TELEMETRY.TELEMETRY_DATA_ALL
            WHERE track_id = %s AND race_num = %s
        """
        cursor.execute(delete_query, (track_id, race_num))
        deleted = cursor.rowcount
        if deleted > 0:
            print(f"  Deleted {deleted:,} existing rows")

        # Upload in batches using INSERT statements
        batch_size = 10000
        total_rows = len(df_upload)
        uploaded = 0

        # Get column names for INSERT
        columns = list(df_upload.columns)
        col_str = ', '.join(columns)
        placeholders = ', '.join(['%s'] * len(columns))

        insert_query = f"""
            INSERT INTO HACKTHETRACK.TELEMETRY.TELEMETRY_DATA_ALL
            ({col_str})
            VALUES ({placeholders})
        """

        print(f"  Uploading {total_rows:,} rows in batches of {batch_size:,}...")

        for i in range(0, total_rows, batch_size):
            batch = df_upload.iloc[i:i+batch_size]
            # Convert NaN to None for each row
            values = [
                tuple(None if pd.isna(val) else val for val in row)
                for row in batch.values
            ]

            cursor.executemany(insert_query, values)
            uploaded += len(values)

            progress = (uploaded / total_rows) * 100
            print(f"    Progress: {uploaded:,}/{total_rows:,} ({progress:.1f}%)", end='\r')

        print(f"\n  ✅ Uploaded {uploaded:,} rows successfully!")

    except Exception as e:
        print(f"  ❌ Error: {e}")
        raise
    finally:
        conn.close()


def main():
    """Main upload process."""
    # Use processed directory with metadata
    data_dir = Path(__file__).parent.parent.parent / "data" / "telemetry" / "processed"

    print("=" * 60)
    print("SNOWFLAKE TELEMETRY DATA UPLOAD")
    print("=" * 60)
    print(f"Data directory: {data_dir}")

    # Get all CSV files (exclude the full sonoma_r1, use reduced version)
    all_files = get_telemetry_files(str(data_dir))
    files = [f for f in all_files if 'reduced' not in f.name or 'sonoma_r1' in f.name]

    # Remove full sonoma_r1 if reduced version exists
    has_reduced_sonoma = any('sonoma_r1_wide_reduced.csv' in f.name for f in files)
    if has_reduced_sonoma:
        files = [f for f in files if f.name != 'sonoma_r1_wide.csv']

    print(f"\nFound {len(files)} telemetry files:")
    for f in files:
        size_mb = f.stat().st_size / (1024 * 1024)
        print(f"  - {f.name:<45} ({size_mb:>6.1f} MB)")

    if not files:
        print("\n❌ No telemetry files found!")
        return

    # Upload each file
    for file_path in files:
        try:
            upload_file(file_path)
        except Exception as e:
            print(f"\n❌ Failed to upload {file_path.name}: {e}")
            continue

    print("\n" + "=" * 60)
    print("UPLOAD COMPLETE")
    print("=" * 60)

    # Verify upload
    print("\nVerifying data in Snowflake...")
    conn = snowflake_service.get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT
            track_id,
            race_num,
            COUNT(*) as row_count,
            COUNT(DISTINCT vehicle_number) as driver_count
        FROM HACKTHETRACK.TELEMETRY.TELEMETRY_DATA_ALL
        GROUP BY track_id, race_num
        ORDER BY track_id, race_num
    """)

    results = cursor.fetchall()
    print(f"\n{'Track':<15} {'Race':<6} {'Rows':<12} {'Drivers':<8}")
    print("-" * 45)

    total_rows = 0
    for track_id, race_num, row_count, driver_count in results:
        print(f"{track_id:<15} {race_num:<6} {row_count:>10,}  {driver_count:>6}")
        total_rows += row_count

    print("-" * 45)
    print(f"{'TOTAL':<15} {'':<6} {total_rows:>10,}")

    conn.close()
    print("\n✅ All data uploaded successfully!")


if __name__ == "__main__":
    main()
