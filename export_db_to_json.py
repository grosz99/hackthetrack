"""
Export SQLite database to comprehensive JSON for Vercel deployment.
This creates a single JSON file with all driver factor data.
"""

import sqlite3
import json
from pathlib import Path

def export_database_to_json():
    """Export all driver factor data from SQLite to JSON."""
    db_path = Path("circuit-fit.db")

    if not db_path.exists():
        print(f"Error: Database not found at {db_path}")
        return

    conn = sqlite3.connect(str(db_path))
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    # Export factor_breakdowns table (the main data we need)
    cursor.execute("""
        SELECT
            driver_number,
            factor_name,
            variable_name,
            variable_display_name,
            raw_value,
            normalized_value,
            weight,
            contribution,
            percentile
        FROM factor_breakdowns
        ORDER BY driver_number, factor_name, variable_name
    """)

    factor_breakdowns = []
    for row in cursor.fetchall():
        factor_breakdowns.append({
            "driver_number": row["driver_number"],
            "factor_name": row["factor_name"],
            "variable_name": row["variable_name"],
            "variable_display_name": row["variable_display_name"],
            "raw_value": row["raw_value"],
            "normalized_value": row["normalized_value"],
            "weight": row["weight"],
            "contribution": row["contribution"],
            "percentile": row["percentile"]
        })

    # Calculate aggregated driver factor scores (what the backend needs)
    cursor.execute("""
        SELECT
            driver_number,
            factor_name,
            AVG(normalized_value) as avg_score,
            AVG(percentile) as avg_percentile
        FROM factor_breakdowns
        GROUP BY driver_number, factor_name
        ORDER BY driver_number, factor_name
    """)

    driver_factors = {}
    for row in cursor.fetchall():
        driver_num = row["driver_number"]
        if driver_num not in driver_factors:
            driver_factors[driver_num] = {
                "driver_number": driver_num,
                "factors": {}
            }

        driver_factors[driver_num]["factors"][row["factor_name"]] = {
            "score": round(row["avg_score"], 2),
            "percentile": round(row["avg_percentile"], 2)
        }

    # Convert to list
    driver_factors_list = list(driver_factors.values())

    conn.close()

    # Create output JSON
    output = {
        "version": "1.0",
        "description": "Driver factor analysis data exported from SQLite",
        "driver_count": len(driver_factors_list),
        "total_records": len(factor_breakdowns),
        "drivers": driver_factors_list,
        "detailed_breakdowns": factor_breakdowns
    }

    # Save to backend data directory
    output_path = Path("backend/data/driver_factors.json")
    output_path.parent.mkdir(parents=True, exist_ok=True)

    with open(output_path, "w") as f:
        json.dump(output, f, indent=2)

    print(f"✅ Exported {len(driver_factors_list)} drivers to {output_path}")
    print(f"   Total factor records: {len(factor_breakdowns)}")
    print(f"   File size: {output_path.stat().st_size / 1024:.1f} KB")

    # Also copy to root for easy access
    root_path = Path("backend/data/driver_factors.json")
    print(f"✅ Driver factors ready at: {root_path}")

if __name__ == "__main__":
    export_database_to_json()
