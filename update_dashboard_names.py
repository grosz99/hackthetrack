"""
Update driver names in dashboardData.json with 2025 GR Cup roster.
Source: https://www.grcupseries.com/entry-list/2025/Circuit-of-the-Americas
"""

import json
from pathlib import Path

# Driver number to name mapping from 2025 GR Cup season
DRIVER_NAMES = {
    2: "Will Robusto",
    3: "Jason Kos",
    5: "Beltre Curtis",
    7: "Jaxon Bell",
    8: "Tom Rudnai",
    11: "Farran Davis",
    12: "Unknown Driver #12",  # Not in 2025 COTA roster
    13: "Westin Workman",
    14: "Alex Garcia",
    15: "Brett Kowalski",
    16: "John Dean",
    17: "Unknown Driver #17",  # Not in database
    18: "Rutledge Wood",
    21: "Ford Koch",
    31: "Jackson Tovo",
    41: "Jenson Sofronas",
    46: "Lucas Weisenberg",
    47: "Ayden Kirk",
    50: "Unknown Driver #50",  # Not in 2025 COTA roster
    51: "Massimo Sunseri",
    55: "Spike Kohlbecker",
    57: "Jeff Curry",
    67: "Unknown Driver #67",  # Not in database
    71: "Christian Weir",
    72: "Ethan Goulart",
    73: "Mike Lamarra",
    78: "Ethan Ayars",
    80: "Paityn Feyen",
    86: "Andrew Gilleland",
    88: "Zach Hollingshead",
    89: "Livio Galanti",
    93: "Patrick Brunson",
    98: "Max Schweid",
    113: "Ethan Tovo",
}


def update_dashboard_data():
    """Update driver names in dashboardData.json."""
    json_path = Path("backend/data/dashboardData.json")

    if not json_path.exists():
        print(f"❌ File not found: {json_path}")
        return

    with open(json_path, 'r') as f:
        data = json.load(f)

    # Update driver names
    updated_count = 0
    for driver in data.get('drivers', []):
        driver_num = driver.get('number')
        if driver_num in DRIVER_NAMES:
            old_name = driver.get('name', '')
            driver['name'] = DRIVER_NAMES[driver_num]
            if old_name != driver['name']:
                updated_count += 1
                print(f"  #{driver_num:3d}: {old_name} → {driver['name']}")

    # Write back
    with open(json_path, 'w') as f:
        json.dump(data, f, indent=2)

    print(f"\n✅ Updated {updated_count} driver names in dashboardData.json")
    print(f"   File size: {json_path.stat().st_size / 1024:.1f} KB")


if __name__ == "__main__":
    print("Updating driver names in dashboardData.json...\n")
    update_dashboard_data()
    print("\nNext steps:")
    print("- Commit changes: git add backend/data/dashboardData.json")
    print("- Deploy to Heroku: git push heroku master")
