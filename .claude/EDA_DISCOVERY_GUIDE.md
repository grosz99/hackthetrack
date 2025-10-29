# EDA Guide - Discovering the 6 Key Skills

## 🎯 Goal
**Use exploratory data analysis to DISCOVER which 6 skills actually discriminate between winners, mid-pack, and back-field drivers.**

Don't assume we know the answer. Let the data tell us.

---

## 📊 Discovery Process

### Phase 1: Load and Explore Your Data

```python
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from scipy import stats

# Load your actual data from GitHub repo
race_results = pd.read_csv('data/race_results/provisional_results/barber_r1_2024.csv')
lap_times = pd.read_csv('data/lap_timing/barber_r1_lap_time.csv')
best_laps = pd.read_csv('data/race_results/best_10_laps/barber_r1_best_10.csv')

print(f"Race Results: {race_results.shape}")
print(f"Lap Times: {lap_times.shape}")
print(f"Best Laps: {best_laps.shape}")

# Look at what columns we actually have
print("\nRace Results Columns:")
print(race_results.columns.tolist())

print("\nLap Times Columns:")
print(lap_times.columns.tolist())

print("\nBest Laps Columns:")
print(best_laps.columns.tolist())
```

### Phase 2: Define Performance Groups

```python
# Create performance groups based on finishing position
def assign_performance_group(position):
    if position <= 3:
        return 'top_3'
    elif position <= 12:
        return 'mid_pack'
    else:
        return 'back_field'

race_results['performance_group'] = race_results['Position'].apply(assign_performance_group)

print("\nPerformance Group Distribution:")
print(race_results['performance_group'].value_counts())

# What's the time gap?
print("\nTime Gaps:")
print(race_results[['Position', 'Driver Name', 'Best Lap', 'Gap']].head(15))
```

---

## 🔍 Discovery Questions to Answer

### Question 1: What section time data do we have?

```python
# If you have best_10_laps data with section times
print("\nAvailable Corners/Sections:")
section_cols = [col for col in best_laps.columns if 'section' in col.lower() or 'corner' in col.lower()]
print(section_cols)

# Or look at actual column names
print("\nAll columns in best_laps:")
for col in best_laps.columns:
    print(f"  - {col}")
```

### Question 2: Which corners discriminate the most?

```python
# Merge to get performance groups
analysis_df = best_laps.merge(
    race_results[['vehicle_number', 'finishing_position', 'performance_group']],
    on='vehicle_number',
    how='left'
)

# For each corner/section, test if it discriminates
corner_discrimination = []

for col in section_cols:
    if analysis_df[col].dtype in ['float64', 'int64']:
        top_3 = analysis_df[analysis_df['performance_group'] == 'top_3'][col]
        mid_pack = analysis_df[analysis_df['performance_group'] == 'mid_pack'][col]
        back_field = analysis_df[analysis_df['performance_group'] == 'back_field'][col]
        
        # ANOVA test
        f_stat, p_value = stats.f_oneway(top_3.dropna(), mid_pack.dropna(), back_field.dropna())
        
        # Effect size
        pooled_std = np.sqrt((top_3.std()**2 + mid_pack.std()**2) / 2)
        cohens_d = (top_3.mean() - mid_pack.mean()) / pooled_std if pooled_std > 0 else 0
        
        corner_discrimination.append({
            'corner': col,
            'p_value': p_value,
            'effect_size': cohens_d,
            'top_3_mean': top_3.mean(),
            'mid_pack_mean': mid_pack.mean(),
            'back_field_mean': back_field.mean(),
            'time_delta': top_3.mean() - mid_pack.mean()
        })

discrimination_df = pd.DataFrame(corner_discrimination)
discrimination_df = discrimination_df.sort_values('effect_size', ascending=False)

print("\n🎯 MOST DISCRIMINATING CORNERS:")
print(discrimination_df[discrimination_df['p_value'] < 0.05].head(10))
```

**This tells us:** Which specific corners separate fast from slow drivers!

### Question 3: Are there corner "types" or clusters?

```python
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler

# Get corner time deltas for each driver
corner_deltas = []
for corner in section_cols:
    winner_time = analysis_df[analysis_df['finishing_position'] == 1][corner].mean()
    analysis_df[f'{corner}_delta'] = analysis_df[corner] - winner_time

# Cluster corners by their discrimination patterns
delta_cols = [f'{col}_delta' for col in section_cols]
corner_features = analysis_df.groupby('finishing_position')[delta_cols].mean()

# Standardize
scaler = StandardScaler()
corner_features_scaled = scaler.fit_transform(corner_features.T)

# Cluster corners into groups
kmeans = KMeans(n_clusters=6, random_state=42)  # Try 6 clusters for 6 skills
corner_clusters = kmeans.fit_predict(corner_features_scaled)

# Assign clusters to corners
corner_types = pd.DataFrame({
    'corner': section_cols,
    'cluster': corner_clusters
})

print("\n🔍 CORNER TYPE CLUSTERS:")
for cluster_num in range(6):
    corners = corner_types[corner_types['cluster'] == cluster_num]['corner'].tolist()
    print(f"\nCluster {cluster_num + 1}:")
    print(f"  Corners: {corners}")
    
    # What do these corners have in common?
    # Look at average times, discrimination strength, etc.
```

**This tells us:** Natural groupings of corners that might represent different skills!

### Question 4: What about pace consistency?

```python
# Calculate lap-to-lap consistency
driver_consistency = lap_times.groupby('vehicle_number').agg({
    'lap_time': ['mean', 'std', 'min', 'max']
}).reset_index()

driver_consistency.columns = ['vehicle_number', 'avg_lap', 'std_lap', 'best_lap', 'worst_lap']
driver_consistency['coefficient_of_variation'] = driver_consistency['std_lap'] / driver_consistency['avg_lap']

# Merge with performance groups
driver_consistency = driver_consistency.merge(
    race_results[['vehicle_number', 'finishing_position', 'performance_group']],
    on='vehicle_number'
)

print("\n📊 CONSISTENCY BY PERFORMANCE GROUP:")
print(driver_consistency.groupby('performance_group')[['std_lap', 'coefficient_of_variation']].mean())

# Does consistency discriminate?
f_stat, p_value = stats.f_oneway(
    driver_consistency[driver_consistency['performance_group'] == 'top_3']['coefficient_of_variation'],
    driver_consistency[driver_consistency['performance_group'] == 'mid_pack']['coefficient_of_variation'],
    driver_consistency[driver_consistency['performance_group'] == 'back_field']['coefficient_of_variation']
)

print(f"\nConsistency discrimination: p={p_value:.3f}")
```

**This tells us:** If "consistency" is one of the 6 skills!

### Question 5: What about tire degradation?

```python
# Divide race into thirds
driver_degradation = []

for vehicle in lap_times['vehicle_number'].unique():
    driver_laps = lap_times[lap_times['vehicle_number'] == vehicle].sort_values('lap_number')
    
    # Skip first and last lap
    valid_laps = driver_laps[(driver_laps['lap_number'] > 1) & 
                             (driver_laps['lap_number'] < driver_laps['lap_number'].max())]
    
    if len(valid_laps) < 6:
        continue
    
    # Split into thirds
    n = len(valid_laps)
    early = valid_laps.iloc[:n//3]['lap_time'].mean()
    mid = valid_laps.iloc[n//3:2*n//3]['lap_time'].mean()
    late = valid_laps.iloc[2*n//3:]['lap_time'].mean()
    
    degradation_rate = (late - early) / (n/3)  # seconds per lap
    
    driver_degradation.append({
        'vehicle_number': vehicle,
        'early_pace': early,
        'late_pace': late,
        'degradation_rate': degradation_rate,
        'total_degradation': late - early
    })

degradation_df = pd.DataFrame(driver_degradation)
degradation_df = degradation_df.merge(
    race_results[['vehicle_number', 'finishing_position', 'performance_group']],
    on='vehicle_number'
)

print("\n⏱️ DEGRADATION BY PERFORMANCE GROUP:")
print(degradation_df.groupby('performance_group')['degradation_rate'].mean())

# Does degradation discriminate?
f_stat, p_value = stats.f_oneway(
    degradation_df[degradation_df['performance_group'] == 'top_3']['degradation_rate'],
    degradation_df[degradation_df['performance_group'] == 'mid_pack']['degradation_rate'],
    degradation_df[degradation_df['performance_group'] == 'back_field']['degradation_rate']
)

print(f"\nDegradation discrimination: p={p_value:.3f}")
```

**This tells us:** If "tire management" is one of the 6 skills!

### Question 6: What about qualifying vs race pace?

```python
# If you have qualifying data
qualifying = pd.read_csv('data/qualifying/barber_q1_2024.csv')

# Compare qualifying position vs race position
comparison = race_results.merge(
    qualifying[['vehicle_number', 'qualifying_position']],
    on='vehicle_number'
)

comparison['positions_gained'] = comparison['qualifying_position'] - comparison['Position']

print("\n🏁 QUALIFYING VS RACE:")
print(comparison.groupby('performance_group')['positions_gained'].mean())

# Test if "racecraft" discriminates
f_stat, p_value = stats.f_oneway(
    comparison[comparison['performance_group'] == 'top_3']['positions_gained'],
    comparison[comparison['performance_group'] == 'mid_pack']['positions_gained'],
    comparison[comparison['performance_group'] == 'back_field']['positions_gained']
)

print(f"\nRacecraft (positions gained) discrimination: p={p_value:.3f}")
```

**This tells us:** If "racecraft/overtaking" is one of the 6 skills!

---

## 🎯 Synthesizing the 6 Skills

### Step 1: Rank ALL potential skills by discrimination power

```python
skill_candidates = []

# 1. Individual corner performance
for corner in section_cols:
    result = discrimination_df[discrimination_df['corner'] == corner].iloc[0]
    if result['p_value'] < 0.10:  # At least marginally significant
        skill_candidates.append({
            'skill_name': f'{corner}_performance',
            'type': 'corner_specific',
            'p_value': result['p_value'],
            'effect_size': result['effect_size'],
            'discrimination_score': abs(result['effect_size']) * (1 - result['p_value'])
        })

# 2. Corner type clusters (if meaningful)
if len(set(corner_clusters)) > 1:
    for cluster_num in range(6):
        cluster_corners = corner_types[corner_types['cluster'] == cluster_num]['corner'].tolist()
        # Calculate average performance in this cluster
        # ... discrimination test
        skill_candidates.append({
            'skill_name': f'corner_cluster_{cluster_num}_performance',
            'type': 'corner_type',
            # ... metrics
        })

# 3. Consistency
skill_candidates.append({
    'skill_name': 'pace_consistency',
    'type': 'global',
    'p_value': p_value,  # from consistency test
    'effect_size': effect_size,  # calculate this
    'discrimination_score': abs(effect_size) * (1 - p_value)
})

# 4. Tire management
skill_candidates.append({
    'skill_name': 'tire_management',
    'type': 'global',
    # ... metrics from degradation test
})

# 5. Racecraft (if data available)
# 6. Qualifying pace (if data available)

# Sort by discrimination power
skills_df = pd.DataFrame(skill_candidates)
skills_df = skills_df.sort_values('discrimination_score', ascending=False)

print("\n🏆 TOP SKILL CANDIDATES:")
print(skills_df.head(10))
```

### Step 2: Select the final 6 skills

```python
# Selection criteria:
# 1. Strong discrimination (p < 0.05, |d| > 0.5)
# 2. Diverse (not all corner-specific)
# 3. Actionable (driver can change it)
# 4. Independent (low correlation between skills)

# Check correlation between top candidates
top_skills = skills_df.head(10)['skill_name'].tolist()

# Build feature matrix
feature_matrix = pd.DataFrame()
for skill in top_skills:
    if 'corner' in skill:
        # Extract corner performance
        corner_name = skill.replace('_performance', '')
        feature_matrix[skill] = analysis_df[corner_name]
    elif skill == 'pace_consistency':
        feature_matrix[skill] = driver_consistency['coefficient_of_variation']
    # ... etc

# Correlation matrix
correlation = feature_matrix.corr()

print("\n🔗 SKILL CORRELATIONS:")
print(correlation)

# Visualize
plt.figure(figsize=(12, 10))
sns.heatmap(correlation, annot=True, cmap='coolwarm', center=0)
plt.title('Correlation Between Candidate Skills')
plt.tight_layout()
plt.savefig('data/analysis_outputs/skill_correlations.png')
```

### Step 3: Name and define the final 6 skills

```python
# Based on EDA, your 6 skills might be something like:

DISCOVERED_SKILLS = {
    'skill_1': {
        'name': 'Heavy Braking Execution',  # Turns 1, 5, 11 cluster
        'corners': [1, 5, 11],
        'description': 'Ability to brake late and carry speed into slow corners',
        'p_value': 0.003,
        'effect_size': 1.24
    },
    'skill_2': {
        'name': 'High-Speed Commitment',  # Turns 4, 9, 13 cluster
        'corners': [4, 9, 13],
        'description': 'Confidence to carry speed through fast, flowing corners',
        'p_value': 0.008,
        'effect_size': 0.89
    },
    'skill_3': {
        'name': 'Exit Traction Management',  # Turns before straights
        'corners': [5, 8, 16],
        'description': 'Throttle control to maximize exit speed without wheelspin',
        'p_value': 0.012,
        'effect_size': 0.72
    },
    'skill_4': {
        'name': 'Pace Consistency',  # Global metric
        'metric': 'lap_time_coefficient_of_variation',
        'description': 'Ability to repeat fast laps without variation',
        'p_value': 0.019,
        'effect_size': 0.63
    },
    'skill_5': {
        'name': 'Tire Management',  # Degradation over stint
        'metric': 'degradation_rate',
        'description': 'Preserving tire performance over race distance',
        'p_value': 0.041,
        'effect_size': 0.52
    },
    'skill_6': {
        'name': 'Racecraft',  # Positions gained
        'metric': 'positions_gained',
        'description': 'Performance in traffic and overtaking ability',
        'p_value': 0.067,
        'effect_size': 0.45
    }
}

# Save this
import json
with open('data/analysis_outputs/discovered_skills.json', 'w') as f:
    json.dump(DISCOVERED_SKILLS, f, indent=2)

print("\n✅ FINAL 6 SKILLS DISCOVERED:")
for skill_id, skill in DISCOVERED_SKILLS.items():
    print(f"\n{skill_id}: {skill['name']}")
    print(f"  Description: {skill['description']}")
    print(f"  Discrimination: p={skill['p_value']:.3f}, d={skill['effect_size']:.2f}")
```

---

## 📊 Visualization for Validation

```python
# Create comprehensive EDA visualizations

fig, axes = plt.subplots(3, 2, figsize=(15, 12))
fig.suptitle('EDA: Discovering the 6 Key Driver Skills', fontsize=16)

# 1. Corner discrimination strength
ax = axes[0, 0]
discrimination_df.sort_values('effect_size', ascending=False).head(10).plot(
    x='corner', y='effect_size', kind='barh', ax=ax
)
ax.set_title('Top 10 Discriminating Corners')
ax.set_xlabel('Effect Size (Cohen\'s d)')

# 2. Performance group lap time distributions
ax = axes[0, 1]
for group in ['top_3', 'mid_pack', 'back_field']:
    group_data = lap_times.merge(race_results[['vehicle_number', 'performance_group']], on='vehicle_number')
    group_laps = group_data[group_data['performance_group'] == group]['lap_time']
    ax.hist(group_laps, alpha=0.5, label=group, bins=20)
ax.set_title('Lap Time Distribution by Performance Group')
ax.set_xlabel('Lap Time (seconds)')
ax.legend()

# 3. Consistency vs Finishing Position
ax = axes[1, 0]
ax.scatter(driver_consistency['finishing_position'], 
          driver_consistency['coefficient_of_variation'])
ax.set_title('Consistency vs Performance')
ax.set_xlabel('Finishing Position')
ax.set_ylabel('Lap Time CoV')

# 4. Tire Degradation by Group
ax = axes[1, 1]
degradation_df.boxplot(column='degradation_rate', by='performance_group', ax=ax)
ax.set_title('Tire Degradation by Performance Group')
ax.set_xlabel('Performance Group')
ax.set_ylabel('Degradation Rate (s/lap)')

# 5. Skill correlation heatmap (subset)
ax = axes[2, 0]
# Show correlation between discovered skills
# ... plot

# 6. Cumulative discrimination power
ax = axes[2, 1]
skills_ranked = skills_df.sort_values('discrimination_score', ascending=False)
cumulative_discrimination = skills_ranked['discrimination_score'].cumsum()
ax.plot(range(1, len(cumulative_discrimination) + 1), cumulative_discrimination)
ax.axvline(x=6, color='r', linestyle='--', label='6 Skills')
ax.set_title('Cumulative Discrimination Power')
ax.set_xlabel('Number of Skills')
ax.set_ylabel('Cumulative Discrimination Score')
ax.legend()

plt.tight_layout()
plt.savefig('data/analysis_outputs/eda_skill_discovery.png', dpi=150)
print("\n📊 Saved EDA visualizations to data/analysis_outputs/eda_skill_discovery.png")
```

---

## ✅ EDA Checklist

- [ ] Load all available data from GitHub repo
- [ ] Define performance groups (top-3, mid-pack, back-field)
- [ ] Test discrimination for ALL corners individually
- [ ] Cluster corners to find natural skill groupings
- [ ] Calculate consistency metrics
- [ ] Calculate tire degradation metrics
- [ ] Calculate racecraft metrics (if data available)
- [ ] Rank all candidate skills by discrimination power
- [ ] Check correlation between top candidates
- [ ] Select final 6 skills (high discrimination, low correlation)
- [ ] Name and document each skill
- [ ] Create visualizations to validate findings
- [ ] Save discovered skills to JSON for feature engineering

---

## 🚀 Next Step

Once you've discovered your 6 skills through EDA, use them to guide feature engineering in `02_FEATURE_ENGINEERING.md`.

**The skills you discover HERE will determine what features you build THERE.**
