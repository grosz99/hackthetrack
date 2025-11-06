#!/usr/bin/env python3
"""
Upload telemetry CSV files to Snowflake.

This script automates the process of uploading local telemetry CSV files
to Snowflake for cloud-based storage and access.

Usage:
    python upload_to_snowflake.py

Environment Variables Required:
    SNOWFLAKE_ACCOUNT - Your Snowflake account identifier
    SNOWFLAKE_USER - Snowflake username
    SNOWFLAKE_PASSWORD - Snowflake password
    SNOWFLAKE_WAREHOUSE - Warehouse name (default: COMPUTE_WH)
    SNOWFLAKE_DATABASE - Database name (default: HACKTHETRACK)
    SNOWFLAKE_SCHEMA - Schema name (default: TELEMETRY)
"""

import os
import sys
from pathlib import Path
import snowflake.connector
import pandas as pd
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Telemetry data path
DATA_DIR = Path(__file__).parent / "data" / "telemetry"

# Track and race mapping
TELEMETRY_FILES = [
    ("barber", 1, "barber_r1_wide.csv"),
    ("barber", 2, "barber_r2_wide.csv"),
    ("cota", 1, "cota_r1_wide.csv"),
    ("cota", 2, "cota_r2_wide.csv"),
    ("roadamerica", 1, "roadamerica_r1_wide.csv"),
    ("roadamerica", 2, "roadamerica_r2_wide.csv"),
    ("sebring", 1, "sebring_r1_wide.csv"),
    ("sebring", 2, "sebring_r2_wide.csv"),
    ("sonoma", 1, "sonoma_r1_wide.csv"),
    ("sonoma", 2, "sonoma_r2_wide.csv"),
    ("vir", 1, "vir_r1_wide.csv"),
    ("vir", 2, "vir_r2_wide.csv"),
]


def get_snowflake_connection():
    """Create Snowflake connection from environment variables."""
    account = os.getenv("SNOWFLAKE_ACCOUNT")
    user = os.getenv("SNOWFLAKE_USER")
    password = os.getenv("SNOWFLAKE_PASSWORD")
    warehouse = os.getenv("SNOWFLAKE_WAREHOUSE", "COMPUTE_WH")
    database = os.getenv("SNOWFLAKE_DATABASE", "HACKTHETRACK")
    schema = os.getenv("SNOWFLAKE_SCHEMA", "TELEMETRY")

    if not all([account, user, password]):
        print("❌ Error: Missing Snowflake credentials")
        print("Set SNOWFLAKE_ACCOUNT, SNOWFLAKE_USER, and SNOWFLAKE_PASSWORD")
        sys.exit(1)

    return snowflake.connector.connect(
        account=account,
        user=user,
        password=password,
        warehouse=warehouse,
        database=database,
        schema=schema
    )


def upload_csv_to_snowflake(
    conn,
    track_id: str,
    race_num: int,
    csv_path: Path
):
    """
    Upload a single CSV file to Snowflake.

    Args:
        conn: Snowflake connection
        track_id: Track identifier
        race_num: Race number
        csv_path: Path to CSV file
    """
    if not csv_path.exists():
        print(f"⚠️  Skipping {csv_path.name} - file not found")
        return False

    print(f"📤 Uploading {csv_path.name}...")

    try:
        # Read CSV with pandas
        df = pd.read_csv(csv_path)

        # Add metadata columns
        df['track_id'] = track_id
        df['race_num'] = race_num
        df['data_source'] = csv_path.name

        # Write to Snowflake using pandas
        # This uses the COPY INTO method internally for efficiency
        from snowflake.connector.pandas_tools import write_pandas

        success, nchunks, nrows, _ = write_pandas(
            conn=conn,
            df=df,
            table_name='TELEMETRY_DATA',
            database=os.getenv("SNOWFLAKE_DATABASE", "HACKTHETRACK"),
            schema=os.getenv("SNOWFLAKE_SCHEMA", "TELEMETRY"),
            auto_create_table=False,
            overwrite=False
        )

        if success:
            print(f"   ✅ Uploaded {nrows:,} rows")
            return True
        else:
            print(f"   ❌ Upload failed")
            return False

    except Exception as e:
        print(f"   ❌ Error: {e}")
        return False


def verify_upload(conn):
    """Verify uploaded data in Snowflake."""
    print("\n📊 Verifying uploaded data...")

    cursor = conn.cursor()

    # Count records per track/race
    cursor.execute("""
        SELECT track_id, race_num, COUNT(*) as record_count,
               COUNT(DISTINCT vehicle_number) as driver_count
        FROM telemetry_data
        GROUP BY track_id, race_num
        ORDER BY track_id, race_num
    """)

    results = cursor.fetchall()

    if not results:
        print("⚠️  No data found in Snowflake")
        return

    print("\nTrack/Race Summary:")
    print("-" * 60)
    for track_id, race_num, record_count, driver_count in results:
        print(f"{track_id:15} Race {race_num}: "
              f"{record_count:8,} records, {driver_count:2} drivers")

    # Get total driver count
    cursor.execute("""
        SELECT COUNT(DISTINCT vehicle_number) as total_drivers
        FROM telemetry_data
    """)
    total_drivers = cursor.fetchone()[0]

    print("-" * 60)
    print(f"Total unique drivers: {total_drivers}")


def main():
    """Main upload process."""
    print("🚀 HackTheTrack Telemetry Upload to Snowflake")
    print("=" * 60)

    # Connect to Snowflake
    print("\n🔌 Connecting to Snowflake...")
    try:
        conn = get_snowflake_connection()
        print("   ✅ Connected successfully")
    except Exception as e:
        print(f"   ❌ Connection failed: {e}")
        sys.exit(1)

    # Upload each CSV file
    print(f"\n📁 Found {len(TELEMETRY_FILES)} telemetry files to upload")
    print("-" * 60)

    success_count = 0
    fail_count = 0

    for track_id, race_num, filename in TELEMETRY_FILES:
        csv_path = DATA_DIR / filename
        if upload_csv_to_snowflake(conn, track_id, race_num, csv_path):
            success_count += 1
        else:
            fail_count += 1

    print("-" * 60)
    print(f"✅ Successfully uploaded: {success_count}")
    print(f"❌ Failed uploads: {fail_count}")

    # Verify uploaded data
    verify_upload(conn)

    # Close connection
    conn.close()

    print("\n✅ Upload process complete!")
    print("\nNext steps:")
    print("1. Set Snowflake credentials in Vercel environment variables")
    print("2. Deploy backend to Vercel")
    print("3. Test the telemetry endpoints in production")


if __name__ == "__main__":
    main()
