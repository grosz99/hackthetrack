# Implementation Guide - Circuit Fit Analysis

## 🎯 Build Order

This guide walks through building the complete Circuit Fit Analysis system step by step.

---

## 📋 Prerequisites

### Required Tools
- Python 3.9+
- pandas, numpy, scipy, statsmodels
- SQLite or PostgreSQL
- Git (for your data repo)

### Data Requirements
Access to your GitHub repo structure:
```
data/
├── analysis_outputs/      # Where you'll write processed features
├── lap_timing/           # Source: Lap time CSVs
├── qualifying/           # Source: Qualifying data
└── race_results/         # Source: Race results
    ├── analysis_endurance/
    ├── best_10_laps/
    └── provisional_results/
```

---

## 🏗️ Phase 1: Data Pipeline (Week 1)

### Step 1.1: Data Loading
```python
# scripts/load_race_data.py

import pandas as pd
import os

class RaceDataLoader:
    def __init__(self, data_dir='data'):
        self.data_dir = data_dir
    
    def load_race_results(self, race_name):
        """Load provisional race results."""
        path = f"{self.data_dir}/race_results/provisional_results/{race_name}.csv"
        df = pd.read_csv(path)
        return df
    
    def load_lap_times(self, race_name):
        """Load lap timing data."""
        path = f"{self.data_dir}/lap_timing/{race_name}_lap_time.csv"
        df = pd.read_csv(path)
        return df
    
    def load_best_laps(self, race_name):
        """Load best 10 laps analysis."""
        path = f"{self.data_dir}/race_results/best_10_laps/{race_name}_best_10.csv"
        df = pd.read_csv(path)
        return df
```

**Test:**
```python
loader = RaceDataLoader()
results = loader.load_race_results('barber_r1_2024')
print(f"Loaded {len(results)} drivers")
```

### Step 1.2: Data Cleaning
```python
# scripts/clean_data.py

def clean_lap_times(lap_times_df):
    """Remove invalid laps."""
    
    # Calculate each driver's best lap
    best_laps = lap_times_df.groupby('vehicle_id')['lap_time'].min()
    
    # Remove laps that are outliers (>107% of best)
    lap_times_df['best_lap'] = lap_times_df['vehicle_id'].map(best_laps)
    valid_laps = lap_times_df[
        lap_times_df['lap_time'] <= lap_times_df['best_lap'] * 1.07
    ]
    
    # Remove first and last lap
    valid_laps = valid_laps[valid_laps['lap_number'] > 1]
    max_laps = valid_laps.groupby('vehicle_id')['lap_number'].max()
    valid_laps['max_lap'] = valid_laps['vehicle_id'].map(max_laps)
    valid_laps = valid_laps[valid_laps['lap_number'] < valid_laps['max_lap']]
    
    return valid_laps

def assign_performance_groups(race_results_df):
    """Add performance group column."""
    def group(position):
        if position <= 3:
            return 'top_3'
        elif position <= 12:
            return 'mid_pack'
        else:
            return 'back_field'
    
    race_results_df['performance_group'] = race_results_df['Position'].apply(group)
    return race_results_df
```

### Step 1.3: Database Setup
```python
# scripts/setup_database.py

import sqlite3

def create_database(db_path='data/analysis_outputs/circuit_fit.db'):
    """Create SQLite database with schema."""
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Race results table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS race_results (
            result_id INTEGER PRIMARY KEY AUTOINCREMENT,
            race_name TEXT,
            vehicle_number TEXT,
            driver_name TEXT,
            finishing_position INTEGER,
            performance_group TEXT,
            total_laps INTEGER,
            best_lap_time REAL,
            total_time TEXT
        )
    ''')
    
    # Lap times table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS lap_times (
            lap_id INTEGER PRIMARY KEY AUTOINCREMENT,
            race_name TEXT,
            vehicle_id INTEGER,
            vehicle_number TEXT,
            driver_name TEXT,
            lap_number INTEGER,
            lap_time REAL,
            is_valid BOOLEAN,
            timestamp DATETIME
        )
    ''')
    
    # Corner features table (will populate later)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS corner_features (
            feature_id INTEGER PRIMARY KEY AUTOINCREMENT,
            race_name TEXT,
            vehicle_id INTEGER,
            driver_name TEXT,
            corner_number INTEGER,
            lap_number INTEGER,
            
            -- Entry metrics
            entry_speed REAL,
            braking_point REAL,
            max_brake_pressure REAL,
            
            -- Apex metrics
            apex_speed REAL,
            min_speed REAL,
            min_speed_location REAL,
            
            -- Exit metrics
            exit_speed REAL,
            throttle_application_point REAL,
            time_to_full_throttle REAL,
            
            -- Comparisons
            entry_speed_vs_winner REAL,
            apex_speed_vs_winner REAL,
            exit_speed_vs_winner REAL,
            section_time REAL,
            section_time_vs_winner REAL,
            
            -- Metadata
            finishing_position INTEGER,
            performance_group TEXT
        )
    ''')
    
    conn.commit()
    conn.close()
    print(f"✅ Database created at {db_path}")

if __name__ == '__main__':
    create_database()
```

**Run:** `python scripts/setup_database.py`

---

## 🔬 Phase 2: Feature Engineering (Week 2)

### Step 2.1: Corner Zone Definitions
```python
# scripts/track_definitions.py

BARBER_CORNERS = {
    1: {'name': 'Turn 1', 'apex_distance': 450, 'type': 'heavy_braking'},
    2: {'name': 'Turn 2', 'apex_distance': 680, 'type': 'technical'},
    3: {'name': 'Turn 3', 'apex_distance': 920, 'type': 'medium_speed'},
    4: {'name': 'Turn 4', 'apex_distance': 1150, 'type': 'high_speed'},
    5: {'name': 'Turn 5', 'apex_distance': 1450, 'type': 'heavy_braking'},
    # ... continue for all 17 corners
}

def get_corner_zones(track_name):
    """Return corner definitions for a track."""
    if track_name == 'barber':
        return BARBER_CORNERS
    # Add other tracks as needed
    return {}
```

### Step 2.2: Feature Extraction
```python
# scripts/extract_features.py

def extract_corner_features(telemetry_df, corner_zones):
    """
    Extract all corner metrics from telemetry.
    
    For now: Using SIMULATED data since we don't have full telemetry yet.
    Replace with actual telemetry processing once available.
    """
    
    features = []
    
    for corner_num, corner_info in corner_zones.items():
        # Simulate feature extraction
        # TODO: Replace with actual telemetry processing
        
        feature = {
            'corner_number': corner_num,
            'corner_name': corner_info['name'],
            
            # Entry (simulated)
            'entry_speed': 100 + np.random.randn() * 5,
            'braking_point': 80 + np.random.randn() * 10,
            'max_brake_pressure': 0.75 + np.random.randn() * 0.1,
            
            # Apex (simulated)
            'apex_speed': 65 + np.random.randn() * 3,
            'min_speed': 60 + np.random.randn() * 3,
            
            # Exit (simulated)
            'exit_speed': 85 + np.random.randn() * 4,
            'throttle_application_point': 5 + np.random.randn() * 2,
        }
        
        features.append(feature)
    
    return pd.DataFrame(features)
```

**Note:** This is a placeholder for when you get telemetry data. For now, use section times from best_10_laps data as a proxy.

### Step 2.3: Use Section Times as Proxy
```python
# scripts/process_section_times.py

def calculate_features_from_section_times(best_laps_df, race_results_df):
    """
    Use section time data as initial features.
    This works until we have full telemetry.
    """
    
    # Merge with race results to get finishing positions
    features_df = best_laps_df.merge(
        race_results_df[['vehicle_number', 'finishing_position', 'performance_group']],
        on='vehicle_number'
    )
    
    # Calculate comparison to winner
    winner_times = features_df[
        features_df['finishing_position'] == 1
    ].groupby('corner_number')['section_time'].mean()
    
    features_df['section_time_vs_winner'] = features_df.apply(
        lambda row: row['section_time'] - winner_times[row['corner_number']],
        axis=1
    )
    
    return features_df
```

---

## 📊 Phase 3: Statistical Validation (Week 3)

### Step 3.1: Implement Validation Functions
Copy validation code from `03_STATISTICAL_VALIDATION.md` into:
```
scripts/validate_features.py
```

### Step 3.2: Run Validation
```python
# scripts/run_validation.py

from validate_features import evaluate_feature
import pandas as pd

# Load features
features_df = pd.read_csv('data/analysis_outputs/corner_features.csv')

# Features to validate
features_to_test = [
    'section_time_vs_winner',
    'entry_speed_vs_winner',
    'apex_speed_vs_winner',
    'exit_speed_vs_winner',
    # Add more as telemetry becomes available
]

# Run validation
results = []
for feature in features_to_test:
    result = evaluate_feature(feature, features_df)
    results.append(result)
    print(f"{feature}: {result['recommendation']} (p={result['anova_p']:.3f}, d={result['effect_size']:.2f})")

# Save results
pd.DataFrame(results).to_csv(
    'data/analysis_outputs/validation_results.csv',
    index=False
)
```

**Run:** `python scripts/run_validation.py`

---

## 🎯 Phase 4: Diagnostic Engine (Week 4)

### Step 4.1: Implement Diagnostic Logic
Copy diagnostic code from `04_DIAGNOSTIC_ENGINE.md` into:
```
scripts/diagnostic_engine.py
```

### Step 4.2: Generate First Report
```python
# scripts/generate_report.py

from diagnostic_engine import DiagnosticEngine

# Initialize engine
engine = DiagnosticEngine(validated_features=['section_time_vs_winner'])

# Load race data
race_data = pd.read_csv('data/analysis_outputs/corner_features.csv')

# Generate report for a driver
driver_name = "John Smith"  # Replace with actual driver
report = engine.generate_full_report(driver_name, race_data)

# Save report
with open(f'data/analysis_outputs/reports/{driver_name}_report.md', 'w') as f:
    f.write(format_report_as_markdown(report))

print(f"✅ Report generated for {driver_name}")
```

---

## 🖥️ Phase 5: User Interface (Weeks 5-6)

### Option A: Streamlit (Quick MVP)
```python
# app/streamlit_app.py

import streamlit as st
import pandas as pd
from diagnostic_engine import DiagnosticEngine

st.title("🏁 Circuit Fit Analysis")

# Select race
race = st.selectbox("Select Race", ["Barber R1 2024", "Sonoma R1 2024"])

# Select driver
drivers = load_drivers_for_race(race)
driver = st.selectbox("Select Driver", drivers)

# Generate report
if st.button("Generate Analysis"):
    with st.spinner("Analyzing performance..."):
        engine = DiagnosticEngine()
        report = engine.generate_full_report(driver, load_race_data(race))
    
    # Display report
    st.header(f"Analysis for {driver}")
    st.metric("Overall Gap to Winner", f"+{report['overall_gap']:.2f}s")
    st.metric("Potential Improvement", f"{report['total_potential_gain']:.2f}s per lap")
    
    st.subheader("Top 3 Priority Improvements")
    for i, priority in enumerate(report['top_3_priorities'], 1):
        with st.expander(f"#{i}: {priority['corner_name']} - {priority['time_lost']:.2f}s"):
            st.write(f"**Issue:** {priority['root_cause']}")
            st.write(f"**Recommendation:** {priority['recommendation']}")
            st.write(f"**Expected Gain:** {priority['estimated_gain']:.2f}s per lap")
```

**Run:** `streamlit run app/streamlit_app.py`

### Option B: React + FastAPI (Production)
Structure:
```
frontend/
  ├── src/
  │   ├── components/
  │   │   ├── DriverSelection.jsx
  │   │   ├── CornerBreakdown.jsx
  │   │   ├── PriorityList.jsx
  │   │   └── CircuitMap.jsx
  │   ├── App.jsx
  │   └── index.js
  └── package.json

backend/
  ├── api/
  │   ├── routes.py
  │   ├── models.py
  │   └── main.py
  └── requirements.txt
```

---

## 🧪 Testing Strategy

### Unit Tests
```python
# tests/test_diagnostic_engine.py

import pytest
from diagnostic_engine import diagnose_entry_issue

def test_braking_too_early_diagnosis():
    driver_data = {'braking_point': 100, 'max_brake_pressure': 0.75}
    winner_data = {'braking_point': 85, 'max_brake_pressure': 0.75}
    
    diagnosis = diagnose_entry_issue(driver_data, winner_data, {})
    
    assert diagnosis['root_cause'] == 'braking_too_early'
    assert 'Brake 15m later' in diagnosis['recommendation']
```

### Integration Tests
```python
# tests/test_full_pipeline.py

def test_full_pipeline():
    # Load test data
    loader = RaceDataLoader()
    race_data = loader.load_race_results('test_race')
    
    # Run feature extraction
    features = extract_corner_features(race_data)
    
    # Run validation
    validation = validate_features(features)
    
    # Generate report
    engine = DiagnosticEngine()
    report = engine.generate_full_report('test_driver', features)
    
    assert report is not None
    assert len(report['top_3_priorities']) == 3
```

---

## 📅 Complete Timeline

### Week 1: Foundation
- [  ] Set up repo structure
- [  ] Create database schema
- [  ] Implement data loading
- [  ] Clean and validate input data

### Week 2: Features
- [  ] Define corner zones for each track
- [  ] Extract features from section times
- [  ] (Optional) Process telemetry if available
- [  ] Store features in database

### Week 3: Validation
- [  ] Implement statistical tests
- [  ] Run validation on all features
- [  ] Document which features to keep/drop
- [  ] Create validated feature list

### Week 4: Diagnostics
- [  ] Implement diagnostic logic
- [  ] Test on sample drivers
- [  ] Refine recommendation templates
- [  ] Generate markdown reports

### Week 5-6: UI
- [  ] Build Streamlit MVP OR React app
- [  ] Add visualization components
- [  ] Deploy to test environment
- [  ] Gather feedback from drivers

---

## 🚀 Quick Start Commands

```bash
# Clone your data repo
git clone <your-repo-url>
cd circuit-fit-analysis

# Install dependencies
pip install -r requirements.txt

# Set up database
python scripts/setup_database.py

# Load and clean data
python scripts/load_race_data.py barber_r1_2024

# Extract features
python scripts/process_section_times.py barber_r1_2024

# Run validation
python scripts/run_validation.py

# Generate report
python scripts/generate_report.py "John Smith" barber_r1_2024

# Launch UI
streamlit run app/streamlit_app.py
```

---

## ✅ Success Criteria

Before considering Phase 1 complete:
- [  ] Can load all race data from GitHub repo
- [  ] Database contains cleaned lap times for ≥1 race
- [  ] Can extract features from section times
- [  ] Statistical validation runs without errors
- [  ] Can generate a markdown report for any driver
- [  ] Report contains ≥3 actionable recommendations

---

Need track-specific racing knowledge? See `06_CIRCUIT_KNOWLEDGE.md`
