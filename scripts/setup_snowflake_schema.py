"""
Setup Snowflake database schema for telemetry data.

This script creates the necessary database, schema, and tables
for storing HackTheTrack telemetry data in Snowflake.
"""

import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.services.snowflake_service import snowflake_service


def run_sql_file(sql_file_path: str):
    """Execute SQL commands from a file."""
    with open(sql_file_path, 'r') as f:
        sql_content = f.read()

    # Split by semicolon and execute each statement
    statements = [stmt.strip() for stmt in sql_content.split(';') if stmt.strip()]

    conn = snowflake_service.get_connection()
    cursor = conn.cursor()

    try:
        for i, statement in enumerate(statements, 1):
            # Skip comments
            if statement.startswith('--'):
                continue

            print(f"Executing statement {i}/{len(statements)}...")
            cursor.execute(statement)

            # Fetch results if available
            try:
                results = cursor.fetchall()
                if results:
                    for row in results:
                        print(f"  {row}")
            except:
                pass

        print("\n✅ Database schema setup complete!")

    except Exception as e:
        print(f"\n❌ Error during setup: {e}")
        raise
    finally:
        cursor.close()
        conn.close()


if __name__ == "__main__":
    sql_file = Path(__file__).parent / "snowflake_setup.sql"

    print("Setting up Snowflake database schema...")
    print(f"SQL file: {sql_file}")
    print()

    run_sql_file(str(sql_file))
