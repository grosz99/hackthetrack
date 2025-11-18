"""
Update driver names in dashboardData.json to match driver_factors.json.
"""

import json
from pathlib import Path

# Driver number to name mapping from 2024 GR Cup season
DRIVER_NAMES = {
    2: "Will Robusto",
    3: "Unknown Driver #3",
    5: "Gresham Wagner",
    7: "Spencer Bucknum",
    8: "Unknown Driver #8",
    11: "Farran Davis",
    12: "Unknown Driver #12",
    13: "Westin Workman",
    14: "Alex Garcia",
    15: "Bennett Muldoon",
    16: "Unknown Driver #16",
    17: "Unknown Driver #17",
    18: "Jordan Segrini",
    21: "Ford Koch",
    31: "Luke Rumburg",
    41: "Unknown Driver #41",
    46: "Lucas Weisenberg",
    47: "Unknown Driver #47",
    50: "Casey Mashore",
    51: "Adam Brickley",
    55: "Spike Kohlbecker",
    57: "Mia Lovell",
    67: "Unknown Driver #67",
    71: "Unknown Driver #71",
    72: "Unknown Driver #72",
    73: "Unknown Driver #73",
    78: "Julian DaCosta",
    80: "Tyler Wettengel",
    86: "Unknown Driver #86",
    88: "Henry Drury",
    89: "Unknown Driver #89",
    93: "Unknown Driver #93",
    98: "Unknown Driver #98",
    113: "Unknown Driver #113",
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
