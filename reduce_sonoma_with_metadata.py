"""
Reduce sonoma_r1_wide.csv with metadata to under 250MB by sampling rows.
"""

import pandas as pd
import os

def reduce_csv_with_metadata(input_file: str, output_file: str, target_size_mb: float = 240.0):
    """
    Reduce CSV file size by uniformly sampling rows while preserving metadata.

    Args:
        input_file: Path to input CSV file
        output_file: Path to output CSV file
        target_size_mb: Target file size in MB
    """
    # Get current file size
    current_size_mb = os.path.getsize(input_file) / (1024 * 1024)
    print(f"Current file size: {current_size_mb:.2f} MB")

    # Calculate what fraction to keep
    fraction_to_keep = target_size_mb / current_size_mb
    print(f"Target: {target_size_mb:.2f} MB (keep {fraction_to_keep:.2%} of data)")

    # Read CSV in chunks to save memory
    print("Reading CSV header...")
    df_sample = pd.read_csv(input_file, nrows=1000)
    print(f"Columns: {list(df_sample.columns[:7])}...")

    # Count total lines
    print("Counting rows...")
    with open(input_file, 'r') as f:
        total_lines = sum(1 for _ in f)

    data_lines = total_lines - 1  # Exclude header
    print(f"Total data lines: {data_lines:,}")

    # Calculate how many rows to keep
    rows_to_keep = int(data_lines * fraction_to_keep)
    print(f"Rows to keep: {rows_to_keep:,}")

    # Calculate step size
    if rows_to_keep >= data_lines:
        step = 1
    else:
        step = max(2, round(data_lines / rows_to_keep))
    print(f"Keeping every {step} row(s) (skipping {step-1} rows between keeps)")

    # Read and sample
    print("Reading and sampling CSV...")
    df = pd.read_csv(input_file)

    # Sample every step-th row
    sampled_indices = list(range(0, len(df), step))
    df_sampled = df.iloc[sampled_indices].copy()

    print(f"Sampled rows: {len(df_sampled):,}")

    # Save
    print(f"Writing to: {output_file}")
    df_sampled.to_csv(output_file, index=False)

    # Verify
    output_size_mb = os.path.getsize(output_file) / (1024 * 1024)
    print(f"\nOutput file size: {output_size_mb:.2f} MB")
    print(f"Reduction: {current_size_mb - output_size_mb:.2f} MB ({(1 - output_size_mb/current_size_mb) * 100:.1f}%)")

    if output_size_mb > 250:
        print(f"⚠️  Warning: Output file is still over 250MB!")
        return False
    else:
        print(f"✓ Success: Output file is under 250MB")
        return True


if __name__ == "__main__":
    input_file = "data/telemetry/processed/sonoma_r1_wide.csv"
    output_file = "data/telemetry/processed/sonoma_r1_wide_reduced.csv"

    print("=" * 70)
    print("REDUCE SONOMA R1 WITH METADATA TO UNDER 250MB")
    print("=" * 70)

    success = reduce_csv_with_metadata(input_file, output_file, target_size_mb=240.0)

    if not success:
        print("\nTrying more aggressive reduction to 230MB...")
        success = reduce_csv_with_metadata(input_file, output_file, target_size_mb=230.0)

    print("\n" + "=" * 70)
    print("Done!")
    print("=" * 70)
