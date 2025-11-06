"""
Script to reduce sonoma_r1_wide.csv to under 250MB by sampling rows.

Target: Reduce 258MB file to ~240MB
Strategy: Skip rows uniformly to achieve target size
"""

import csv
import os

def shrink_csv(input_file: str, output_file: str, target_size_mb: float = 240.0):
    """
    Reduce CSV file size by uniformly skipping rows.

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

    # Count total lines
    with open(input_file, 'r') as f:
        total_lines = sum(1 for _ in f)

    data_lines = total_lines - 1  # Exclude header
    print(f"Total data lines: {data_lines:,}")

    # Calculate how many rows to keep
    rows_to_keep = int(data_lines * fraction_to_keep)
    print(f"Rows to keep: {rows_to_keep:,}")

    # Calculate step size for uniform sampling
    # If we want to keep N out of M rows, we keep every (M/N)th row
    # For example: keep 2 out of 10 → keep every 5th row (10/2=5)
    if rows_to_keep >= data_lines:
        step = 1
    else:
        step = max(2, round(data_lines / rows_to_keep))
    print(f"Keeping every {step} row(s) (skipping {step-1} rows between keeps)")

    rows_written = 0
    with open(input_file, 'r', newline='') as infile, \
         open(output_file, 'w', newline='') as outfile:

        reader = csv.reader(infile)
        writer = csv.writer(outfile)

        # Always keep header
        header = next(reader)
        writer.writerow(header)

        # Sample data rows uniformly
        for i, row in enumerate(reader):
            if i % step == 0:
                writer.writerow(row)
                rows_written += 1

                if rows_written % 100000 == 0:
                    print(f"Written {rows_written:,} rows...")

    # Check output size
    output_size_mb = os.path.getsize(output_file) / (1024 * 1024)
    print(f"\nOutput file size: {output_size_mb:.2f} MB")
    print(f"Data rows written: {rows_written:,}")
    print(f"Reduction: {current_size_mb - output_size_mb:.2f} MB ({(1 - output_size_mb/current_size_mb) * 100:.1f}%)")

    if output_size_mb > 250:
        print(f"⚠️  Warning: Output file is still over 250MB!")
        return False
    else:
        print(f"✓ Success: Output file is under 250MB")
        return True

if __name__ == "__main__":
    input_file = "/Users/justingrosz/Documents/AI-Work/hackthetrack-master/data/telemetry/sonoma_r1_wide.csv"
    output_file = "/Users/justingrosz/Documents/AI-Work/hackthetrack-master/data/telemetry/sonoma_r1_wide_reduced.csv"

    print("=" * 60)
    print("CSV File Size Reduction Tool")
    print("=" * 60)

    # Start with 240MB target
    success = shrink_csv(input_file, output_file, target_size_mb=240.0)

    # If still too large, try more aggressive reduction
    if not success:
        print("\nTrying more aggressive reduction to 230MB...")
        success = shrink_csv(input_file, output_file, target_size_mb=230.0)

    print("\n" + "=" * 60)
    print("Done!")
    print("=" * 60)
