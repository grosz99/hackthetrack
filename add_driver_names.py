"""
Add driver names to database and JSON files based on 2024 GR Cup roster.
Source: https://www.driverdb.com/championships/toyota-gr-cup-north-america-overall/2024
"""

import json
import sqlite3
from pathlib import Path

# Driver number to name mapping from 2024 GR Cup season
DRIVER_NAMES = {
    2: "Will Robusto",
    3: "Unknown Driver #3",  # Not in 2024 roster
    5: "Gresham Wagner",
    7: "Spencer Bucknum",
    8: "Unknown Driver #8",  # Not in 2024 roster
    11: "Farran Davis",
    12: "Unknown Driver #12",  # Not in 2024 roster
    13: "Westin Workman",
    14: "Alex Garcia",
    15: "Bennett Muldoon",
    16: "Unknown Driver #16",  # Not in 2024 roster
    17: "Unknown Driver #17",  # Not in 2024 roster
    18: "Jordan Segrini",
    21: "Ford Koch",
    31: "Luke Rumburg",
    41: "Unknown Driver #41",  # Not in 2024 roster
    46: "Lucas Weisenberg",
    47: "Unknown Driver #47",  # Not in 2024 roster
    50: "Casey Mashore",
    51: "Adam Brickley",
    55: "Spike Kohlbecker",
    57: "Mia Lovell",
    67: "Unknown Driver #67",  # Not in 2024 roster
    71: "Unknown Driver #71",  # Not in 2024 roster
    72: "Unknown Driver #72",  # Not in 2024 roster
    73: "Unknown Driver #73",  # Not in 2024 roster
    78: "Julian DaCosta",
    80: "Tyler Wettengel",
    86: "Unknown Driver #86",  # Not in 2024 roster
    88: "Henry Drury",
    89: "Unknown Driver #89",  # Not in 2024 roster
    93: "Unknown Driver #93",  # Not in 2024 roster
    98: "Unknown Driver #98",  # Not in 2024 roster
    113: "Unknown Driver #113",  # Not in 2024 roster
}


def update_database():
    """Add driver_name column to database tables and populate it."""
    db_path = Path("backend/data/circuit-fit.db")

    if not db_path.exists():
        print(f"❌ Database not found: {db_path}")
        return

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    try:
        # Check if driver_name column exists in driver_factors table
        cursor.execute("PRAGMA table_info(driver_factors)")
        columns = [col[1] for col in cursor.fetchall()]

        if "driver_name" not in columns:
            print("Adding driver_name column to driver_factors table...")
            cursor.execute("ALTER TABLE driver_factors ADD COLUMN driver_name TEXT")
            conn.commit()

        # Update driver names
        for driver_num, driver_name in DRIVER_NAMES.items():
            cursor.execute(
                "UPDATE driver_factors SET driver_name = ? WHERE driver_number = ?",
                (driver_name, driver_num)
            )

        conn.commit()
        updated_count = cursor.rowcount
        print(f"✅ Updated {updated_count} driver records in database")

        # Do the same for factor_breakdowns table
        cursor.execute("PRAGMA table_info(factor_breakdowns)")
        columns = [col[1] for col in cursor.fetchall()]

        if "driver_name" not in columns:
            print("Adding driver_name column to factor_breakdowns table...")
            cursor.execute("ALTER TABLE factor_breakdowns ADD COLUMN driver_name TEXT")
            conn.commit()

        # Update driver names in factor_breakdowns
        for driver_num, driver_name in DRIVER_NAMES.items():
            cursor.execute(
                "UPDATE factor_breakdowns SET driver_name = ? WHERE driver_number = ?",
                (driver_name, driver_num)
            )

        conn.commit()
        print(f"✅ Updated factor_breakdowns table with driver names")

    finally:
        conn.close()


def update_driver_factors_json():
    """Add driver names to driver_factors.json."""
    json_path = Path("backend/data/driver_factors.json")

    if not json_path.exists():
        print(f"❌ File not found: {json_path}")
        return

    with open(json_path, 'r') as f:
        data = json.load(f)

    # Update each driver record
    updated_count = 0
    for driver in data['drivers']:
        driver_num = driver['driver_number']
        if driver_num in DRIVER_NAMES:
            driver['driver_name'] = DRIVER_NAMES[driver_num]
            updated_count += 1

    # Write back
    with open(json_path, 'w') as f:
        json.dump(data, f, indent=2)

    print(f"✅ Updated {updated_count} drivers in driver_factors.json")
    print(f"   File size: {json_path.stat().st_size / 1024:.1f} KB")


def update_factor_breakdowns_json():
    """Add driver names to factor_breakdowns.json."""
    json_path = Path("backend/data/factor_breakdowns.json")

    if not json_path.exists():
        print(f"❌ File not found: {json_path}")
        return

    with open(json_path, 'r') as f:
        data = json.load(f)

    # Update driver_breakdowns section
    updated_count = 0
    if 'driver_breakdowns' in data:
        for driver_num_str, driver_data in data['driver_breakdowns'].items():
            driver_num = int(driver_num_str)
            if driver_num in DRIVER_NAMES:
                driver_data['driver_name'] = DRIVER_NAMES[driver_num]
                updated_count += 1

    # Write back
    with open(json_path, 'w') as f:
        json.dump(data, f, indent=2)

    print(f"✅ Updated {updated_count} drivers in factor_breakdowns.json")
    print(f"   File size: {json_path.stat().st_size / 1024:.1f} KB")


def print_driver_mapping():
    """Print the driver mapping for verification."""
    print("\n" + "="*70)
    print("DRIVER NUMBER → NAME MAPPING (2024 GR Cup Season)")
    print("="*70)

    known_drivers = {k: v for k, v in DRIVER_NAMES.items() if not v.startswith("Unknown")}
    unknown_drivers = {k: v for k, v in DRIVER_NAMES.items() if v.startswith("Unknown")}

    print(f"\n✅ Known Drivers ({len(known_drivers)}):")
    for num, name in sorted(known_drivers.items()):
        print(f"   #{num:3d} → {name}")

    print(f"\n⚠️  Unknown Drivers ({len(unknown_drivers)}):")
    for num, name in sorted(unknown_drivers.items()):
        print(f"   #{num:3d} → {name}")

    print("\n" + "="*70 + "\n")


if __name__ == "__main__":
    print("Adding driver names to Gibbs AI database and JSON files...")
    print("Source: 2024 Toyota GR Cup North America roster\n")

    # Print mapping first
    print_driver_mapping()

    # Update database
    print("1. Updating database...")
    update_database()

    # Update JSON files
    print("\n2. Updating JSON files...")
    update_driver_factors_json()
    update_factor_breakdowns_json()

    print("\n✅ Driver names added successfully!")
    print("\nNext steps:")
    print("- Re-export data with: python3 export_db_to_json.py")
    print("- Deploy to Heroku")
