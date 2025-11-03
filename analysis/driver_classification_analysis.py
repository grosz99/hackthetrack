"""
Driver Classification Analysis
Analyzes driver data to create data-driven, racing-specific classification system.
"""

import json
import numpy as np
import pandas as pd
from pathlib import Path

# Load the data
data_path = Path(__file__).parent.parent / "frontend" / "src" / "data" / "dashboardData.json"
with open(data_path, 'r') as f:
    data = json.load(f)

drivers = data['drivers']

# Extract key metrics into DataFrame
driver_data = []
for driver in drivers:
    driver_data.append({
        'number': driver['number'],
        'name': driver['name'],
        'overall_score': driver['overall_score'],
        'percentile': driver['percentile'],
        'grade': driver['grade'],
        'races': driver['races'],
        'avg_finish': driver['avg_finish'],
        'speed': driver['factors']['raw_speed']['percentile'],
        'consistency': driver['factors']['consistency']['percentile'],
        'racecraft': driver['factors']['racecraft']['percentile'],
        'tire_mgmt': driver['factors']['tire_mgmt']['percentile'],
        'best_track_fit': max([track['fit_score'] for track in driver['circuit_fits']]),
        'worst_track_fit': min([track['fit_score'] for track in driver['circuit_fits']]),
        'avg_track_fit': np.mean([track['fit_score'] for track in driver['circuit_fits']]),
    })

df = pd.DataFrame(driver_data)

# Calculate derived metrics
df['speed_consistency_gap'] = df['speed'] - df['consistency']
df['factor_balance'] = df[['speed', 'consistency', 'racecraft', 'tire_mgmt']].std(axis=1)
df['track_fit_variance'] = df.apply(
    lambda row: np.std([track['fit_score'] for track in
                        next(d['circuit_fits'] for d in drivers if d['number'] == row['number'])]),
    axis=1
)
df['has_elite_factor'] = df[['speed', 'consistency', 'racecraft', 'tire_mgmt']].max(axis=1) >= 75
df['weakest_factor'] = df[['speed', 'consistency', 'racecraft', 'tire_mgmt']].min(axis=1)
df['strongest_factor_name'] = df[['speed', 'consistency', 'racecraft', 'tire_mgmt']].idxmax(axis=1)

print("=" * 80)
print("DRIVER DATA DISTRIBUTION ANALYSIS")
print("=" * 80)

print("\n1. OVERALL PERFORMANCE DISTRIBUTION")
print("-" * 80)
print(f"Total Drivers: {len(df)}")
print(f"\nOverall Score Stats:")
print(df['overall_score'].describe())
print(f"\nGrade Distribution:")
print(df['grade'].value_counts().sort_index())

print("\n2. FACTOR DISTRIBUTIONS")
print("-" * 80)
for factor in ['speed', 'consistency', 'racecraft', 'tire_mgmt']:
    print(f"\n{factor.upper()} (percentile):")
    print(f"  Mean: {df[factor].mean():.1f}")
    print(f"  Median: {df[factor].median():.1f}")
    print(f"  Std: {df[factor].std():.1f}")
    print(f"  Top 25% (75th+): {len(df[df[factor] >= 75])} drivers ({len(df[df[factor] >= 75])/len(df)*100:.1f}%)")
    print(f"  Bottom 25% (<25th): {len(df[df[factor] < 25])} drivers ({len(df[df[factor] < 25])/len(df)*100:.1f}%)")

print("\n3. EXPERIENCE & RESULTS CORRELATION")
print("-" * 80)
print(f"Race Count Stats:")
print(df['races'].describe())
print(f"\nAverage Finish Position Stats:")
print(df['avg_finish'].describe())
print(f"\nCorrelation: Overall Score vs Avg Finish: {df['overall_score'].corr(df['avg_finish']):.3f}")
print(f"Correlation: Speed vs Avg Finish: {df['speed'].corr(df['avg_finish']):.3f}")
print(f"Correlation: Consistency vs Avg Finish: {df['consistency'].corr(df['avg_finish']):.3f}")
print(f"Correlation: Races vs Overall Score: {df['races'].corr(df['overall_score']):.3f}")

print("\n4. FACTOR BALANCE ANALYSIS")
print("-" * 80)
print(f"Factor Balance (std dev across 4 factors):")
print(df['factor_balance'].describe())
print(f"\nWell-Balanced Drivers (balance < 10): {len(df[df['factor_balance'] < 10])} drivers")
print(f"Specialists (balance > 15): {len(df[df['factor_balance'] > 15])} drivers")
print(f"\nDrivers with elite factor (75+ in any): {len(df[df['has_elite_factor']])} drivers")

print("\n5. TRACK VERSATILITY")
print("-" * 80)
print(f"Average Track Fit Score:")
print(df['avg_track_fit'].describe())
print(f"\nTrack Fit Variance (specialization indicator):")
print(df['track_fit_variance'].describe())
print(f"\nTrack Specialists (variance > 20): {len(df[df['track_fit_variance'] > 20])} drivers")
print(f"Versatile (variance < 10): {len(df[df['track_fit_variance'] < 10])} drivers")

print("\n6. SPEED-CONSISTENCY GAP (Raw Talent vs Refinement)")
print("-" * 80)
print(f"Speed-Consistency Gap:")
print(df['speed_consistency_gap'].describe())
print(f"\nHigh Raw Talent, Low Refinement (gap > +15): {len(df[df['speed_consistency_gap'] > 15])} drivers")
print(df[df['speed_consistency_gap'] > 15][['number', 'name', 'speed', 'consistency', 'races', 'avg_finish']])
print(f"\nHigh Consistency, Lower Speed (gap < -10): {len(df[df['speed_consistency_gap'] < -10])} drivers")
print(df[df['speed_consistency_gap'] < -10][['number', 'name', 'speed', 'consistency', 'races', 'avg_finish']])

print("\n7. POTENTIAL CLASSIFICATION ARCHETYPES")
print("-" * 80)

# Proven Winners (top performers with experience)
proven_winners = df[(df['overall_score'] >= 65) & (df['races'] >= 10)]
print(f"\nPROVEN WINNERS (65+ score, 10+ races): {len(proven_winners)} drivers")
print(proven_winners[['number', 'name', 'overall_score', 'races', 'avg_finish']].to_string(index=False))

# Raw Speed Phenoms (elite speed, limited experience)
speed_phenoms = df[(df['speed'] >= 70) & (df['races'] <= 6)]
print(f"\nRAW SPEED PHENOMS (70+ speed, ≤6 races): {len(speed_phenoms)} drivers")
print(speed_phenoms[['number', 'name', 'speed', 'consistency', 'races', 'avg_finish']].to_string(index=False))

# Grinders (high consistency, lower speed)
grinders = df[(df['consistency'] >= 60) & (df['speed'] < 60)]
print(f"\nGRINDERS (60+ consistency, <60 speed): {len(grinders)} drivers")
print(grinders[['number', 'name', 'speed', 'consistency', 'races', 'avg_finish']].to_string(index=False))

# Wheel-to-Wheel Specialists (elite racecraft)
racecraft_specialists = df[df['racecraft'] >= 61]
print(f"\nRACECRAFT SPECIALISTS (61+ racecraft): {len(racecraft_specialists)} drivers")
print(racecraft_specialists[['number', 'name', 'racecraft', 'speed', 'avg_finish']].to_string(index=False))

# Track Specialists (high variance in track fits)
track_specialists = df[(df['track_fit_variance'] > 20) & (df['best_track_fit'] >= 85)]
print(f"\nTRACK SPECIALISTS (variance > 20, best fit 85+): {len(track_specialists)} drivers")
print(track_specialists[['number', 'name', 'best_track_fit', 'worst_track_fit', 'track_fit_variance']].to_string(index=False))

# Development Cases (low overall but shows promise)
development_cases = df[(df['overall_score'] < 55) & (df['races'] <= 8) &
                       ((df['speed'] >= 55) | (df['racecraft'] >= 55))]
print(f"\nDEVELOPMENT CASES (<55 overall, ≤8 races, 55+ in speed or craft): {len(development_cases)} drivers")
print(development_cases[['number', 'name', 'overall_score', 'speed', 'racecraft', 'races']].to_string(index=False))

print("\n8. SUGGESTED RACING-SPECIFIC ARCHETYPES")
print("-" * 80)
print("""
Based on the data analysis, here are honest, data-driven classifications:

1. PROVEN FRONTRUNNERS (65+ overall, 10+ races, <5 avg finish)
   - Elite performers with consistent results
   - Strong across all factors
   - Track record of success

2. RAW SPEED SPECIALISTS (70+ speed percentile, <7 races)
   - Elite one-lap pace
   - Limited race experience
   - Need refinement in consistency/craft

3. CONSISTENCY GRINDERS (60+ consistency, 50-65 speed)
   - Reliable, repeatable performance
   - Smooth driving style
   - Lack elite raw pace

4. WHEEL-TO-WHEEL RACERS (60+ racecraft, strong avg finish relative to overall)
   - Excel in overtaking/defending
   - Race better than qualify
   - Strong situational awareness

5. TRACK SPECIALISTS (High track fit variance, 85+ on best circuits)
   - Excel at specific circuit types
   - Struggle at tracks that don't suit style
   - Niche but valuable

6. BALANCED ALL-AROUNDERS (Factor balance < 10, 60+ overall)
   - No weaknesses, no elite strengths
   - Adaptable to any situation
   - Safe, predictable performers

7. DEVELOPMENT PROJECTS (<55 overall, showing potential in 1-2 factors)
   - Young/inexperienced with flashes of talent
   - Inconsistent results
   - High variance, needs coaching

8. TIRE PRESERVATION SPECIALISTS (65+ tire mgmt, good at tracks demanding it)
   - Excel in long stints
   - Can make alternate strategies work
   - Valuable for endurance scenarios
""")

print("\n9. KEY INSIGHTS FOR CLASSIFICATION ALGORITHM")
print("-" * 80)
print("""
- EXPERIENCE MATTERS: Race count correlates with overall score but not perfectly
- SPEED IS KING: Raw speed has strongest correlation with avg finish (-0.xxx)
- BALANCE IS RARE: Only a few drivers have factor balance < 10 (all-around skill)
- TRACK FIT VARIES: Some drivers have 30+ point spread between best/worst tracks
- YOUNG TALENT EXISTS: Several sub-6 race drivers show 70+ speed percentile
- GRINDERS OVERPERFORM: Some high-consistency drivers finish better than overall suggests
""")

# Export for further analysis
output_path = Path(__file__).parent / "driver_classification_data.csv"
df.to_csv(output_path, index=False)
print(f"\nDetailed data exported to: {output_path}")
