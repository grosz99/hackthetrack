"""Analyze factor score distributions for statistical validation."""
import pandas as pd
import numpy as np
import sqlite3
from pathlib import Path

base_path = Path(__file__).parent.parent

# Load factor scores
fs_path = base_path / "data" / "analysis_outputs" / "tier1_factor_scores.csv"
fs = pd.read_csv(fs_path)

print("Factor Score Statistics (z-score scale, pre-reflection):")
print("=" * 70)

for col in ['factor_1_score', 'factor_2_score', 'factor_3_score', 'factor_4_score']:
    print(f"\n{col}:")
    print(f"  Mean: {fs[col].mean():.3f}")
    print(f"  Std Dev: {fs[col].std():.3f}")
    print(f"  Min: {fs[col].min():.3f}")
    print(f"  Max: {fs[col].max():.3f}")
    print(f"  25th percentile: {fs[col].quantile(0.25):.3f}")
    print(f"  50th percentile: {fs[col].quantile(0.50):.3f}")
    print(f"  75th percentile: {fs[col].quantile(0.75):.3f}")

# Get RepTrak normalized scores from database
print("\n\n" + "=" * 70)
print("RepTrak-Normalized Scores (0-100 scale):")
print("=" * 70)

db_path = base_path / "circuit-fit.db"
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

cursor.execute("""
    SELECT factor_name,
           AVG(normalized_value) as avg_score,
           MIN(normalized_value) as min_score,
           MAX(normalized_value) as max_score,
           AVG(percentile) as avg_percentile
    FROM factor_breakdowns
    GROUP BY factor_name
""")

for row in cursor.fetchall():
    factor_name = row[0]
    avg_score = row[1]
    min_score = row[2]
    max_score = row[3]
    avg_pct = row[4]
    print(f"\n{factor_name}:")
    print(f"  Average: {avg_score:.1f}")
    print(f"  Range: {min_score:.1f} - {max_score:.1f}")
    print(f"  Average Percentile: {avg_pct:.1f}")

# Get per-driver averages
print("\n\n" + "=" * 70)
print("Driver-Level Score Statistics (averaged across races):")
print("=" * 70)

driver_avg = fs.groupby('driver_number').agg({
    'factor_1_score': 'mean',
    'factor_2_score': 'mean',
    'factor_3_score': 'mean',
    'factor_4_score': 'mean'
})

print(f"\nNumber of drivers: {len(driver_avg)}")
print("\nDriver-average standard deviations:")
for col in ['factor_1_score', 'factor_2_score', 'factor_3_score', 'factor_4_score']:
    print(f"  {col}: σ = {driver_avg[col].std():.3f}")

conn.close()
