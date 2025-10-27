"""
Tiered Feature Building - Start with highest confidence variables.
Build incrementally: Tier 1 → Tier 2 → Tier 3

Tier 1: Highest confidence (12 vars) - We have all the data, validated
Tier 2: Moderate confidence (8 vars) - Need some calculation, clear logic
Tier 3: Proposed enhancements (6 vars) - New ideas, need testing
"""

import pandas as pd
import numpy as np
from pathlib import Path
from scipy.stats import linregress
import warnings
warnings.filterwarnings('ignore')

# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def convert_to_seconds(time_str):
    """Convert lap time string to seconds."""
    import re
    if pd.isna(time_str):
        return np.nan
    time_str = str(time_str).strip()
    if time_str.replace('.', '').replace('-', '').isdigit():
        val = float(time_str)
        return val if val > 0 else np.nan
    if ':' in time_str or "'" in time_str:
        parts = re.split('[:' + "'" + ']', time_str)
        try:
            minutes = int(parts[0])
            seconds = float(parts[1])
            return minutes * 60 + seconds
        except:
            return np.nan
    try:
        return float(time_str)
    except:
        return np.nan

# ============================================================================
# TIER 1: HIGHEST CONFIDENCE VARIABLES (12)
# These are proven to work from METRICS_VALIDATION_REPORT.md
# ============================================================================

# --- FACTOR: RAW SPEED (3 variables) ---

def tier1_qualifying_pace(qualifying_df, driver_number):
    """
    T1.1 - Qualifying Pace (Normalized to pole)
    Factor: RAW SPEED
    Confidence: ✅ HIGH - 100% success in validation
    """
    try:
        if qualifying_df.empty:
            return np.nan
        driver_qual = qualifying_df[qualifying_df['NUMBER'] == driver_number]
        if len(driver_qual) == 0:
            return np.nan
        driver_time = convert_to_seconds(driver_qual['TIME'].iloc[0])
        pole_time = qualifying_df['TIME'].apply(convert_to_seconds).min()
        return pole_time / driver_time if driver_time > 0 else np.nan
    except:
        return np.nan

def tier1_best_race_lap(best_10_df, driver_number):
    """
    T1.2 - Best Race Lap Pace
    Factor: RAW SPEED
    Confidence: ✅ HIGH - 100% success in validation
    """
    try:
        if best_10_df.empty:
            return np.nan
        driver_data = best_10_df[best_10_df['NUMBER'] == driver_number]
        if len(driver_data) == 0:
            return np.nan
        driver_best = convert_to_seconds(driver_data['BESTLAP_1'].iloc[0])
        field_best = best_10_df['BESTLAP_1'].apply(convert_to_seconds).min()
        return field_best / driver_best if driver_best > 0 else np.nan
    except:
        return np.nan

def tier1_avg_top10_pace(best_10_df, driver_number):
    """
    T1.3 - Average Top-10 Lap Pace
    Factor: RAW SPEED
    Confidence: ✅ HIGH - 100% success in validation
    """
    try:
        if best_10_df.empty:
            return np.nan
        driver_data = best_10_df[best_10_df['NUMBER'] == driver_number]
        if len(driver_data) == 0:
            return np.nan
        driver_avg = convert_to_seconds(driver_data['AVERAGE'].iloc[0])
        field_avg = best_10_df['AVERAGE'].apply(convert_to_seconds).min()
        return field_avg / driver_avg if driver_avg > 0 else np.nan
    except:
        return np.nan

# --- FACTOR: CONSISTENCY (3 variables) ---

def tier1_stint_consistency(endurance_df, driver_number):
    """
    T1.4 - Stint Consistency (CoV of lap times)
    Factor: CONSISTENCY
    Confidence: ✅ HIGH - Well validated
    """
    try:
        if endurance_df.empty:
            return np.nan
        clean_laps = endurance_df[
            (endurance_df['NUMBER'] == driver_number) &
            (endurance_df['FLAG_AT_FL'] != 'FCY') &
            (endurance_df['LAP_NUMBER'] > 1)
        ]
        if len(clean_laps) < 5:
            return np.nan
        lap_times = clean_laps['LAP_TIME'].apply(convert_to_seconds)
        best_lap = lap_times.min()
        valid_laps = lap_times[lap_times < best_lap * 1.07]
        if len(valid_laps) < 3:
            return np.nan
        driver_cv = valid_laps.std() / valid_laps.mean()
        field_cv = endurance_df[
            (endurance_df['FLAG_AT_FL'] != 'FCY') &
            (endurance_df['LAP_NUMBER'] > 1)
        ].groupby('NUMBER').apply(
            lambda x: x['LAP_TIME'].apply(convert_to_seconds).std() /
                      x['LAP_TIME'].apply(convert_to_seconds).mean()
        ).min()
        return field_cv / driver_cv if driver_cv > 0 else np.nan
    except:
        return np.nan

def tier1_sector_consistency(endurance_df, driver_number):
    """
    T1.5 - Sector Time Consistency (Avg variance across S1, S2, S3)
    Factor: CONSISTENCY / FOCUS
    Confidence: ✅ HIGH - Have all sector data
    """
    try:
        if endurance_df.empty:
            return np.nan
        clean_laps = endurance_df[
            (endurance_df['NUMBER'] == driver_number) &
            (endurance_df['FLAG_AT_FL'] != 'FCY')
        ]
        if len(clean_laps) < 5:
            return np.nan

        # Calculate variance for each sector
        s1_cv = clean_laps['S1_SECONDS'].std() / clean_laps['S1_SECONDS'].mean()
        s2_cv = clean_laps['S2_SECONDS'].std() / clean_laps['S2_SECONDS'].mean()
        s3_cv = clean_laps['S3_SECONDS'].std() / clean_laps['S3_SECONDS'].mean()

        driver_avg_cv = np.mean([s1_cv, s2_cv, s3_cv])

        # Field best
        def calc_sector_cv(df):
            if len(df) < 3:
                return np.nan
            s1 = df['S1_SECONDS'].std() / df['S1_SECONDS'].mean()
            s2 = df['S2_SECONDS'].std() / df['S2_SECONDS'].mean()
            s3 = df['S3_SECONDS'].std() / df['S3_SECONDS'].mean()
            return np.mean([s1, s2, s3])

        field_cv = endurance_df[
            endurance_df['FLAG_AT_FL'] != 'FCY'
        ].groupby('NUMBER').apply(calc_sector_cv).min()

        return field_cv / driver_avg_cv if driver_avg_cv > 0 else np.nan
    except:
        return np.nan

def tier1_braking_consistency(endurance_df, driver_number):
    """
    T1.6 - Braking Consistency (S1 lap-to-lap variation)
    Factor: CONSISTENCY / PRECISION
    Confidence: ✅ HIGH - S1 = braking zones
    """
    try:
        if endurance_df.empty:
            return np.nan
        clean_laps = endurance_df[
            (endurance_df['NUMBER'] == driver_number) &
            (endurance_df['FLAG_AT_FL'] != 'FCY')
        ]
        if len(clean_laps) < 5:
            return np.nan

        driver_s1_std = clean_laps['S1_SECONDS'].std()
        driver_s1_mean = clean_laps['S1_SECONDS'].mean()
        driver_cv = driver_s1_std / driver_s1_mean

        field_cv = endurance_df[
            endurance_df['FLAG_AT_FL'] != 'FCY'
        ].groupby('NUMBER')['S1_SECONDS'].agg(lambda x: x.std() / x.mean()).min()

        return field_cv / driver_cv if driver_cv > 0 else np.nan
    except:
        return np.nan

# --- FACTOR: TIRE MANAGEMENT (3 variables) ---

def tier1_pace_degradation(endurance_df, driver_number):
    """
    T1.7 - Pace Degradation Rate (lap time slope)
    Factor: TIRE MANAGEMENT
    Confidence: ✅ HIGH - Validated in testing
    """
    try:
        if endurance_df.empty:
            return np.nan
        clean_laps = endurance_df[
            (endurance_df['NUMBER'] == driver_number) &
            (endurance_df['FLAG_AT_FL'] != 'FCY') &
            (endurance_df['LAP_NUMBER'] > 1)
        ].copy()
        if len(clean_laps) < 5:
            return np.nan

        clean_laps['LAP_TIME_SECONDS'] = clean_laps['LAP_TIME'].apply(convert_to_seconds)
        slope, _, _, _, _ = linregress(
            clean_laps['LAP_NUMBER'],
            clean_laps['LAP_TIME_SECONDS']
        )

        if slope <= 0:
            return 1.0  # No degradation

        # Field slopes
        field_slopes = []
        for num in endurance_df['NUMBER'].unique():
            driver_laps = endurance_df[
                (endurance_df['NUMBER'] == num) &
                (endurance_df['FLAG_AT_FL'] != 'FCY') &
                (endurance_df['LAP_NUMBER'] > 1)
            ]
            if len(driver_laps) >= 5:
                lap_times = driver_laps['LAP_TIME'].apply(convert_to_seconds)
                s, _, _, _, _ = linregress(driver_laps['LAP_NUMBER'], lap_times)
                field_slopes.append(s)

        if len(field_slopes) == 0:
            return 0.5

        field_best = min(field_slopes)
        return field_best / slope if slope > 0 else 1.0
    except:
        return np.nan

def tier1_late_stint_perf(endurance_df, driver_number):
    """
    T1.8 - Late Stint Performance (final 33% pace)
    Factor: TIRE MANAGEMENT / ENDURANCE
    Confidence: ✅ HIGH - Validated
    """
    try:
        if endurance_df.empty:
            return np.nan
        driver_laps = endurance_df[
            (endurance_df['NUMBER'] == driver_number) &
            (endurance_df['FLAG_AT_FL'] != 'FCY')
        ]
        max_lap = driver_laps['LAP_NUMBER'].max()
        late_threshold = max_lap * 0.66
        late_laps = driver_laps[driver_laps['LAP_NUMBER'] > late_threshold]

        if len(late_laps) < 3:
            return np.nan

        driver_late_pace = late_laps['LAP_TIME'].apply(convert_to_seconds).mean()
        field_late_pace = endurance_df[
            endurance_df['FLAG_AT_FL'] != 'FCY'
        ].groupby('NUMBER').apply(
            lambda x: x[x['LAP_NUMBER'] > x['LAP_NUMBER'].max() * 0.66]['LAP_TIME'].apply(convert_to_seconds).mean()
        ).min()

        return field_late_pace / driver_late_pace if driver_late_pace > 0 else np.nan
    except:
        return np.nan

def tier1_early_vs_late_pace(endurance_df, driver_number):
    """
    T1.9 - Early vs Late Race Pace Ratio
    Factor: TIRE MANAGEMENT / ENDURANCE
    Confidence: ✅ HIGH - Clear calculation
    """
    try:
        if endurance_df.empty:
            return np.nan
        driver_laps = endurance_df[
            (endurance_df['NUMBER'] == driver_number) &
            (endurance_df['FLAG_AT_FL'] != 'FCY') &
            (endurance_df['LAP_NUMBER'] > 1)
        ]

        max_lap = driver_laps['LAP_NUMBER'].max()
        if max_lap < 10:
            return np.nan

        early_laps = driver_laps[driver_laps['LAP_NUMBER'].between(2, 5)]
        late_laps = driver_laps[driver_laps['LAP_NUMBER'] > max_lap * 0.66]

        if len(early_laps) < 2 or len(late_laps) < 3:
            return np.nan

        early_avg = early_laps['LAP_TIME'].apply(convert_to_seconds).mean()
        late_avg = late_laps['LAP_TIME'].apply(convert_to_seconds).mean()

        # Ratio: 1.0 = no degradation, >1.0 = getting slower
        ratio = late_avg / early_avg

        # Invert so higher = better endurance
        return 2.0 - ratio if ratio < 2.0 else 0.0
    except:
        return np.nan

# --- FACTOR: RACECRAFT (3 variables) ---

def tier1_position_changes(endurance_df, driver_number):
    """
    T1.10 - In-Race Position Changes (lap-by-lap)
    Factor: RACECRAFT
    Confidence: ✅ HIGH - 100% success in validation
    """
    try:
        if endurance_df.empty:
            return np.nan
        if 'ELAPSED' not in endurance_df.columns:
            return np.nan

        valid = endurance_df[
            (endurance_df['FLAG_AT_FL'] != 'FCY') &
            (endurance_df['LAP_NUMBER'] > 1)
        ].copy()

        if len(valid) == 0:
            return np.nan

        try:
            valid['ELAPSED_SECONDS'] = pd.to_timedelta(valid['ELAPSED']).dt.total_seconds()
        except:
            valid['ELAPSED_SECONDS'] = valid['ELAPSED'].apply(convert_to_seconds)

        positions = []
        for lap_num in valid['LAP_NUMBER'].unique():
            lap_data = valid[valid['LAP_NUMBER'] == lap_num].copy()
            lap_data['running_position'] = lap_data['ELAPSED_SECONDS'].rank(method='min')
            positions.append(lap_data[['NUMBER', 'LAP_NUMBER', 'running_position']])

        if len(positions) == 0:
            return np.nan

        positions_df = pd.concat(positions)
        positions_df['position_change'] = (
            positions_df.groupby('NUMBER')['running_position'].diff() * -1
        ).fillna(0)

        driver_changes = positions_df[positions_df['NUMBER'] == driver_number]
        if len(driver_changes) == 0:
            return np.nan

        avg_change = driver_changes['position_change'].mean()
        field_avg = positions_df.groupby('NUMBER')['position_change'].mean().mean()
        field_std = positions_df.groupby('NUMBER')['position_change'].mean().std()

        if field_std == 0:
            return 0.5

        z_score = (avg_change - field_avg) / field_std
        return 0.5 + (z_score / 6)
    except:
        return np.nan

def tier1_positions_gained(provisional_df, qualifying_df, driver_number):
    """
    T1.11 - Positions Gained (Quali → Finish)
    Factor: RACECRAFT / SPRINTING
    Confidence: ✅ HIGH - 100% success after int() fix
    """
    try:
        if provisional_df.empty or qualifying_df.empty:
            return np.nan

        race_finish_data = provisional_df[provisional_df['NUMBER'] == driver_number]
        if len(race_finish_data) == 0:
            return np.nan
        race_finish = int(race_finish_data['POSITION'].iloc[0])

        qual_data = qualifying_df[qualifying_df['NUMBER'] == driver_number]
        if len(qual_data) == 0:
            return np.nan
        qual_position = int(qual_data['POS'].iloc[0])

        positions_gained = qual_position - race_finish
        max_drivers = len(provisional_df)
        normalized = positions_gained / max_drivers

        return 0.5 + normalized
    except:
        return np.nan

def tier1_finishing_position_normalized(provisional_df, driver_number):
    """
    T1.12 - Finishing Position (Normalized)
    Factor: OVERALL PERFORMANCE (outcome variable)
    Confidence: ✅ HIGH - Direct from results
    """
    try:
        if provisional_df.empty:
            return np.nan
        driver_data = provisional_df[provisional_df['NUMBER'] == driver_number]
        if len(driver_data) == 0:
            return np.nan

        finish_pos = int(driver_data['POSITION'].iloc[0])
        field_size = len(provisional_df)

        # Normalize: 1.0 = winner, 0.0 = last
        return (field_size - finish_pos) / (field_size - 1) if field_size > 1 else 0.5
    except:
        return np.nan

# ============================================================================
# MAIN BUILDER - TIER 1 ONLY
# ============================================================================

def build_tier1_features(race_name):
    """Build Tier 1 feature matrix (12 highest confidence variables)."""

    print(f"\n{'='*80}")
    print(f"TIER 1 FEATURES: {race_name}")
    print(f"{'='*80}")

    # Load data
    try:
        provisional = pd.read_csv(
            f'data/race_results/provisional_results/{race_name}_provisional_results.csv',
            delimiter=';'
        )
        provisional.columns = provisional.columns.str.strip()
        print(f"[OK] Provisional: {len(provisional)} drivers")
    except Exception as e:
        print(f"[FAIL] {e}")
        return None

    try:
        endurance = pd.read_csv(
            f'data/race_results/analysis_endurance/{race_name}_analysis_endurance.csv',
            delimiter=';'
        )
        endurance.columns = endurance.columns.str.strip()
        print(f"[OK] Endurance: {len(endurance)} laps")
    except Exception as e:
        print(f"[FAIL] {e}")
        return None

    try:
        best_10 = pd.read_csv(
            f'data/race_results/best_10_laps/{race_name}_best_10_laps.csv',
            delimiter=';'
        )
        best_10.columns = best_10.columns.str.strip()
        print(f"[OK] Best 10: {len(best_10)} drivers")
    except Exception as e:
        print(f"[FAIL] {e}")
        return None

    # Load qualifying
    qualifying = None
    track = race_name.split('_')[0]
    race_num = race_name.split('_')[1][-1]
    qual_paths = [
        f'data/qualifying/{track.capitalize()}rd{race_num}Qualifying.csv',
        f'data/qualifying/{track.capitalize()}rd1Qualifying.csv',
    ]
    for qpath in qual_paths:
        if Path(qpath).exists():
            try:
                qualifying = pd.read_csv(qpath, delimiter=';')
                qualifying.columns = qualifying.columns.str.strip()
                print(f"[OK] Qualifying: {len(qualifying)} drivers")
                break
            except:
                continue
    if qualifying is None:
        print(f"[WARN] No qualifying")
        qualifying = pd.DataFrame()

    # Build features
    drivers = provisional['NUMBER'].unique()
    features = []

    print(f"\nCalculating Tier 1 features for {len(drivers)} drivers...")

    for i, driver in enumerate(drivers):
        if (i + 1) % 5 == 0:
            print(f"  Progress: {i+1}/{len(drivers)}")

        feature_row = {
            'race': race_name,
            'driver_number': driver,

            # RAW SPEED (3)
            'qualifying_pace': tier1_qualifying_pace(qualifying, driver),
            'best_race_lap': tier1_best_race_lap(best_10, driver),
            'avg_top10_pace': tier1_avg_top10_pace(best_10, driver),

            # CONSISTENCY (3)
            'stint_consistency': tier1_stint_consistency(endurance, driver),
            'sector_consistency': tier1_sector_consistency(endurance, driver),
            'braking_consistency': tier1_braking_consistency(endurance, driver),

            # TIRE MANAGEMENT (3)
            'pace_degradation': tier1_pace_degradation(endurance, driver),
            'late_stint_perf': tier1_late_stint_perf(endurance, driver),
            'early_vs_late_pace': tier1_early_vs_late_pace(endurance, driver),

            # RACECRAFT (3)
            'position_changes': tier1_position_changes(endurance, driver),
            'positions_gained': tier1_positions_gained(provisional, qualifying, driver),
            'performance_normalized': tier1_finishing_position_normalized(provisional, driver),

        }

        # OUTCOME - Handle DNS drivers properly
        driver_data = provisional[provisional['NUMBER'] == driver]
        if len(driver_data) > 0 and not pd.isna(driver_data['POSITION'].iloc[0]):
            feature_row['finishing_position'] = int(driver_data['POSITION'].iloc[0])
            features.append(feature_row)
        else:
            # Skip drivers who didn't start or have no position data
            print(f"  [SKIP] Driver {driver} DNS or no position data")

    feature_df = pd.DataFrame(features)

    print(f"\n[DONE] Shape: {feature_df.shape}")
    feature_cols = [c for c in feature_df.columns if c not in ['race', 'driver_number', 'finishing_position']]
    completeness = (feature_df[feature_cols].notna().sum() / len(feature_df)) * 100
    print(f"Data completeness: {completeness.mean():.1f}% average")

    return feature_df

def build_all_races_tier1():
    """Build Tier 1 features for all 12 races."""

    races = [
        'barber_r1', 'barber_r2',
        'cota_r1', 'cota_r2',
        'roadamerica_r1', 'roadamerica_r2',
        'sebring_r1', 'sebring_r2',
        'sonoma_r1', 'sonoma_r2',
        'vir_r1', 'vir_r2'
    ]

    print(f"{'='*80}")
    print(f"BUILDING TIER 1 FEATURES - ALL RACES")
    print(f"12 highest confidence variables")
    print(f"{'='*80}")

    all_features = []

    for race in races:
        feature_df = build_tier1_features(race)
        if feature_df is not None:
            all_features.append(feature_df)
            output_path = f'data/analysis_outputs/{race}_tier1_features.csv'
            feature_df.to_csv(output_path, index=False)
            print(f"  Saved: {output_path}")

    if len(all_features) > 0:
        combined_df = pd.concat(all_features, ignore_index=True)
        output_path = 'data/analysis_outputs/all_races_tier1_features.csv'
        combined_df.to_csv(output_path, index=False)

        print(f"\n{'='*80}")
        print(f"TIER 1 COMBINED RESULTS")
        print(f"{'='*80}")
        print(f"Shape: {combined_df.shape}")
        print(f"Races: {combined_df['race'].nunique()}")
        print(f"Drivers: {combined_df['driver_number'].nunique()}")
        print(f"Total observations: {len(combined_df)}")
        print(f"Saved: {output_path}")

        # Completeness report
        print(f"\nData Completeness by Variable:")
        feature_cols = [c for c in combined_df.columns
                       if c not in ['race', 'driver_number', 'finishing_position']]
        for col in feature_cols:
            pct = (combined_df[col].notna().sum() / len(combined_df)) * 100
            status = "[OK]" if pct > 90 else "[WARN]" if pct > 70 else "[FAIL]"
            print(f"  {status} {col:30s}: {pct:5.1f}%")

        return combined_df

    return None

if __name__ == '__main__':
    print("\n" + "="*80)
    print("TIERED FEATURE BUILDING - TIER 1 ONLY")
    print("="*80)
    print("\nBuilding 12 highest confidence variables:")
    print("  - RAW SPEED: 3 variables")
    print("  - CONSISTENCY: 3 variables")
    print("  - TIRE MANAGEMENT: 3 variables")
    print("  - RACECRAFT: 3 variables")
    print("\nThese variables have been validated in METRICS_VALIDATION_REPORT.md")
    print("="*80)

    combined = build_all_races_tier1()

    if combined is not None:
        print(f"\n{'='*80}")
        print("SUCCESS - TIER 1 COMPLETE")
        print(f"{'='*80}")
        print("\nNext steps:")
        print("1. Run EFA on Tier 1 to validate approach")
        print("2. If successful, add Tier 2 variables")
        print("3. Then add Tier 3 (proposed enhancements)")
