# Agent 1: Data Science Pipeline

## Mission
Process raw GR Cup telemetry and race data into standardized driver skill metrics and track demand profiles.

## Timeline
Days 1-14 (Weeks 1-2)

## Dependencies
- Raw CSV data in `/data/` directory
- Python 3.10+ environment
- Libraries: pandas, numpy, scipy, scikit-learn

## Available Data

### Data Structure
```
/data/
├── barber/
│   ├── R1_barber_telemetry_data.csv          # Main telemetry (10Hz+)
│   ├── R2_barber_telemetry_data.csv
│   ├── R1_barber_lap_time.csv                # Lap-by-lap times
│   ├── R1_barber_lap_start.csv               # Lap start timestamps
│   ├── R1_barber_lap_end.csv                 # Lap end timestamps
│   ├── 03_Provisional Results_Race 1.CSV     # Race results
│   ├── 05_Results by Class_Race 1.CSV
│   ├── 26_Weather_Race 1.CSV                 # Weather conditions
│   └── 99_Best 10 Laps By Driver_Race 1.CSV
├── COTA/
├── sebring/
├── sonoma/
├── VIR/
└── road_america/
```

### Telemetry Channels
```python
REQUIRED_CHANNELS = [
    'speed',                    # Vehicle speed (mph)
    'VBOX_Lat_Min',            # GPS latitude
    'VBOX_Long_Minutes',       # GPS longitude
    'Laptrigger_lapdist_dls',  # Distance along track
    'accy_can',                # Lateral G-force (cornering)
    'accx_can',                # Longitudinal G-force (braking/acceleration)
    'aps',                     # Throttle position % (0-100)
    'pbrake_f',                # Front brake pressure
    'Steering_Angle',          # Steering input (degrees)
]
```

## Phase 1: Data Validation (Days 1-3)

### Objective
Ensure data quality before processing. <5% missing data acceptable.

### Tasks

#### 1. Create validation module
**File:** `src/data_pipeline/validate.py`

```python
import pandas as pd
import numpy as np
from pathlib import Path
import json

class DataValidator:
    """Validate telemetry and race data quality"""
    
    def __init__(self, data_root='data'):
        self.data_root = Path(data_root)
        self.tracks = ['barber', 'COTA', 'sebring', 'sonoma', 'VIR', 'road_america']
        self.report = {}
    
    def validate_all(self):
        """Run all validation checks"""
        for track in self.tracks:
            self.report[track] = self.validate_track(track)
        
        self.report['overall_quality_score'] = self.calculate_overall_quality()
        self.save_report()
        return self.report
    
    def validate_track(self, track_name):
        """Validate all files for a track"""
        track_path = self.data_root / track_name
        
        if not track_path.exists():
            return {'error': 'Track directory not found'}
        
        validation = {
            'races': [],
            'completeness': 0,
            'issues': []
        }
        
        # Check telemetry files
        for race_num in [1, 2]:
            telemetry_file = track_path / f'R{race_num}_{track_name}_telemetry_data.csv'
            
            if telemetry_file.exists():
                validation['races'].append(race_num)
                telem_check = self.validate_telemetry_file(telemetry_file)
                validation['completeness'] += telem_check['completeness']
                validation['issues'].extend(telem_check['issues'])
        
        if validation['races']:
            validation['completeness'] /= len(validation['races'])
        
        return validation
    
    def validate_telemetry_file(self, file_path):
        """Validate single telemetry file"""
        try:
            df = pd.read_csv(file_path)
        except Exception as e:
            return {
                'completeness': 0,
                'issues': [f'Failed to load: {str(e)}']
            }
        
        issues = []
        
        # Check for required channels
        missing_channels = [ch for ch in REQUIRED_CHANNELS 
                          if ch not in df.columns]
        if missing_channels:
            issues.append(f'Missing channels: {missing_channels}')
        
        # Calculate completeness
        completeness = 1 - (df.isnull().sum().sum() / df.size)
        
        if completeness < 0.95:
            issues.append(f'Low completeness: {completeness:.2%}')
        
        # Check for outliers
        if 'speed' in df.columns:
            outlier_speed = df[df['speed'] > 200].shape[0]
            if outlier_speed > 0:
                issues.append(f'{outlier_speed} rows with unrealistic speed')
        
        if 'accy_can' in df.columns:
            outlier_g = df[df['accy_can'].abs() > 3.5].shape[0]
            if outlier_g > 0:
                issues.append(f'{outlier_g} rows with unrealistic lateral G')
        
        return {
            'completeness': completeness,
            'issues': issues
        }
    
    def calculate_overall_quality(self):
        """Calculate overall data quality score"""
        completeness_scores = [
            track['completeness'] 
            for track in self.report.values() 
            if isinstance(track, dict) and 'completeness' in track
        ]
        
        return np.mean(completeness_scores) if completeness_scores else 0
    
    def save_report(self):
        """Save validation report to JSON"""
        output_path = Path('outputs/data_quality_report.json')
        output_path.parent.mkdir(exist_ok=True)
        
        with open(output_path, 'w') as f:
            json.dump(self.report, f, indent=2)
        
        print(f'Validation report saved to {output_path}')
```

#### 2. Run validation
```python
# validate_all.py
from data_pipeline.validate import DataValidator

validator = DataValidator()
report = validator.validate_all()

print(f"Overall Quality Score: {report['overall_quality_score']:.2%}")
print(f"\nIssues found:")
for track, data in report.items():
    if isinstance(data, dict) and data.get('issues'):
        print(f"\n{track}:")
        for issue in data['issues']:
            print(f"  - {issue}")
```

### Deliverables
- [ ] `src/data_pipeline/validate.py` implemented
- [ ] `outputs/data_quality_report.json` generated
- [ ] Overall quality score >95%
- [ ] Document any data gaps or issues

## Phase 2: Metric Calculation (Days 4-10)

### Objective
Calculate 5 driver attributes from telemetry and race data.

### Tasks

#### 1. Create metrics calculator base class
**File:** `src/data_pipeline/metrics_calculator.py`

```python
import pandas as pd
import numpy as np
from scipy import stats
from pathlib import Path

class MetricsCalculator:
    """Main driver skill metrics calculation engine"""
    
    def __init__(self, track_name, race_num=1):
        self.track_name = track_name
        self.race_num = race_num
        self.data_path = Path(f'data/{track_name}')
        
        # Load data
        self.telemetry = self.load_telemetry()
        self.lap_times = self.load_lap_times()
        self.results = self.load_results()
    
    def load_telemetry(self):
        """Load telemetry CSV"""
        file_path = self.data_path / f'R{self.race_num}_{self.track_name}_telemetry_data.csv'
        return pd.read_csv(file_path)
    
    def load_lap_times(self):
        """Load lap times CSV"""
        file_path = self.data_path / f'R{self.race_num}_{self.track_name}_lap_time.csv'
        return pd.read_csv(file_path)
    
    def load_results(self):
        """Load race results CSV"""
        file_path = self.data_path / f'03_Provisional Results_Race {self.race_num}.CSV'
        return pd.read_csv(file_path)
    
    def calculate_all_metrics(self, driver_id):
        """Calculate all 5 metrics for a driver"""
        metrics = {
            'driver_id': driver_id,
            'track': self.track_name,
            'metrics': {
                'qualifying_pace': self.calculate_qualifying_pace(driver_id),
                'passing_efficiency': self.calculate_passing_efficiency(driver_id),
                'corner_mastery': self.calculate_corner_mastery(driver_id),
                'racecraft': self.calculate_racecraft(driver_id),
                'consistency': self.calculate_consistency(driver_id)
            }
        }
        
        return metrics
    
    def normalize_to_scale(self, value, field_values):
        """Normalize value to 0-10 scale based on field distribution"""
        # Calculate z-score
        z_score = (value - field_values.mean()) / field_values.std()
        
        # Convert to 0-10 scale (z-score of +2 = 10, -2 = 0)
        normalized = 5 + (z_score * 2.5)
        
        # Clamp to 0-10 range
        return np.clip(normalized, 0, 10)
    
    def calculate_percentile(self, value, field_values):
        """Calculate percentile ranking"""
        return stats.percentileofscore(field_values, value, kind='rank')
```

#### 2. Implement each metric calculator

**Metric 1: Qualifying Pace**
```python
def calculate_qualifying_pace(self, driver_id):
    """
    Calculate raw single-lap speed.
    
    Algorithm:
    1. Get driver's best lap (exclude outliers)
    2. Get field average and std dev
    3. Normalize to 0-10 scale
    """
    # Get driver's lap times
    driver_laps = self.lap_times[self.lap_times['driver_id'] == driver_id]
    
    # Remove outliers (>2 std dev)
    lap_times = driver_laps['lap_time']
    clean_laps = lap_times[
        (lap_times < lap_times.mean() + 2*lap_times.std()) &
        (lap_times > lap_times.mean() - 2*lap_times.std())
    ]
    
    best_lap = clean_laps.min()
    
    # Get field statistics
    all_best_laps = self.lap_times.groupby('driver_id')['lap_time'].min()
    
    # Normalize (lower time = higher score)
    field_avg = all_best_laps.mean()
    z_score = (field_avg - best_lap) / all_best_laps.std()
    score = np.clip(5 + (z_score * 2.5), 0, 10)
    
    percentile = 100 - stats.percentileofscore(all_best_laps, best_lap, kind='rank')
    
    return {
        'score': round(score, 1),
        'percentile': int(percentile),
        'raw': {
            'best_lap': float(best_lap),
            'field_avg': float(field_avg),
            'vs_field': float(field_avg - best_lap),
            'z_score': float(z_score)
        }
    }
```

**Metric 2: Passing Efficiency**
```python
def calculate_passing_efficiency(self, driver_id):
    """
    Calculate close racing performance.
    
    Algorithm:
    1. Identify passing opportunities in telemetry
    2. Calculate success rate
    3. Measure draft utilization
    """
    driver_telemetry = self.telemetry[self.telemetry['driver_id'] == driver_id]
    
    # TODO: Implement gap-to-car-ahead calculation
    # For now, use position changes as proxy
    
    driver_results = self.results[self.results['driver_id'] == driver_id]
    start_pos = driver_results['start_position'].iloc[0]
    finish_pos = driver_results['finish_position'].iloc[0]
    
    positions_gained = start_pos - finish_pos
    
    # Normalize based on field
    all_position_changes = (
        self.results['start_position'] - self.results['finish_position']
    )
    
    score = self.normalize_to_scale(positions_gained, all_position_changes)
    percentile = self.calculate_percentile(positions_gained, all_position_changes)
    
    return {
        'score': round(score, 1),
        'percentile': int(percentile),
        'raw': {
            'positions_gained': int(positions_gained),
            'start_position': int(start_pos),
            'finish_position': int(finish_pos)
        }
    }
```

**Metric 3: Corner Mastery**
```python
def calculate_corner_mastery(self, driver_id):
    """
    Calculate technical cornering skill (entry + apex + exit).
    
    Algorithm:
    1. Entry: Braking consistency and max deceleration
    2. Mid: Apex speed and lateral G utilization
    3. Exit: Throttle application timing and exit speed
    """
    driver_telemetry = self.telemetry[self.telemetry['driver_id'] == driver_id]
    
    # Entry phase (30% weight)
    braking_zones = driver_telemetry[
        (driver_telemetry['pbrake_f'] > 50) & 
        (driver_telemetry['accx_can'] < -0.3)
    ]
    
    if len(braking_zones) > 0:
        max_decel = abs(braking_zones['accx_can'].min())
        brake_consistency = 1 / (braking_zones['pbrake_f'].std() + 1)
        entry_score = (max_decel * 3 + brake_consistency) / 2
    else:
        entry_score = 5
    
    # Mid-corner phase (40% weight)
    corners = driver_telemetry[driver_telemetry['accy_can'].abs() > 0.5]
    
    if len(corners) > 0:
        avg_apex_speed = corners['speed'].mean()
        avg_lateral_g = corners['accy_can'].abs().mean()
        mid_score = (avg_apex_speed / 10) + (avg_lateral_g * 2)
    else:
        mid_score = 5
    
    # Exit phase (30% weight)
    exits = driver_telemetry[
        (driver_telemetry['aps'].diff() > 5) &
        (driver_telemetry['speed'].diff() > 0)
    ]
    
    if len(exits) > 0:
        avg_exit_accel = exits['accx_can'].mean()
        exit_score = (avg_exit_accel * 5) + 5
    else:
        exit_score = 5
    
    # Weighted composite
    composite = (entry_score * 0.3 + mid_score * 0.4 + exit_score * 0.3)
    
    # Normalize to 0-10
    score = np.clip(composite, 0, 10)
    
    # Get percentile vs field
    # TODO: Calculate for all drivers and compare
    percentile = 50  # Placeholder
    
    return {
        'score': round(score, 1),
        'percentile': percentile,
        'raw': {
            'entry_score': round(entry_score, 2),
            'mid_corner_score': round(mid_score, 2),
            'exit_score': round(exit_score, 2),
            'composite': round(composite, 2)
        }
    }
```

**Metric 4: Racecraft**
```python
def calculate_racecraft(self, driver_id):
    """
    Calculate pack positioning and defense.
    
    Algorithm:
    1. Position changes during race
    2. Clean air vs traffic performance
    3. Defensive success
    """
    # Use position changes as proxy for racecraft
    driver_results = self.results[self.results['driver_id'] == driver_id]
    
    positions_gained = (
        driver_results['start_position'].iloc[0] - 
        driver_results['finish_position'].iloc[0]
    )
    
    # Normalize
    all_position_changes = (
        self.results['start_position'] - self.results['finish_position']
    )
    
    score = self.normalize_to_scale(positions_gained, all_position_changes)
    percentile = self.calculate_percentile(positions_gained, all_position_changes)
    
    return {
        'score': round(score, 1),
        'percentile': int(percentile),
        'raw': {
            'positions_gained': int(positions_gained)
        }
    }
```

**Metric 5: Consistency**
```python
def calculate_consistency(self, driver_id):
    """
    Calculate lap time consistency and pace degradation.
    
    Algorithm:
    1. Lap time standard deviation (lower = better)
    2. Pace degradation over stint
    3. Coefficient of variation
    """
    driver_laps = self.lap_times[self.lap_times['driver_id'] == driver_id]
    lap_times = driver_laps['lap_time']
    
    # Remove outliers
    clean_laps = lap_times[
        (lap_times < lap_times.mean() + 2*lap_times.std()) &
        (lap_times > lap_times.mean() - 2*lap_times.std())
    ]
    
    # Calculate consistency metrics
    std_dev = clean_laps.std()
    coef_variation = std_dev / clean_laps.mean()
    
    # Pace degradation (linear regression)
    if len(clean_laps) > 5:
        x = np.arange(len(clean_laps))
        slope, _ = np.polyfit(x, clean_laps, 1)
        degradation_rate = slope
    else:
        degradation_rate = 0
    
    # Score: Lower std dev = higher score
    # Invert so lower variance = higher score
    consistency_score = 10 - (std_dev * 10)
    tire_mgmt_score = 10 - (abs(degradation_rate) * 100)
    
    score = np.clip((consistency_score + tire_mgmt_score) / 2, 0, 10)
    
    # Get field percentile
    all_std_devs = self.lap_times.groupby('driver_id')['lap_time'].std()
    percentile = 100 - self.calculate_percentile(std_dev, all_std_devs)
    
    return {
        'score': round(score, 1),
        'percentile': int(percentile),
        'raw': {
            'lap_time_std': round(float(std_dev), 3),
            'degradation_rate': round(float(degradation_rate), 4),
            'coefficient_variation': round(float(coef_variation), 4)
        }
    }
```

#### 3. Calculate for all drivers
**File:** `src/data_pipeline/calculate_all_metrics.py`

```python
import json
from pathlib import Path
from metrics_calculator import MetricsCalculator

def calculate_all_drivers_all_tracks():
    """Calculate metrics for all drivers at all tracks"""
    
    tracks = ['barber', 'COTA', 'sebring', 'sonoma', 'VIR', 'road_america']
    
    all_metrics = {
        'metadata': {
            'version': '1.0',
            'tracks': tracks
        },
        'drivers': {}
    }
    
    for track in tracks:
        print(f"\nProcessing {track}...")
        
        calculator = MetricsCalculator(track, race_num=1)
        
        # Get all driver IDs from results
        driver_ids = calculator.results['driver_id'].unique()
        
        for driver_id in driver_ids:
            print(f"  Calculating metrics for driver {driver_id}...")
            
            if driver_id not in all_metrics['drivers']:
                all_metrics['drivers'][driver_id] = {
                    'id': driver_id,
                    'tracks': {}
                }
            
            metrics = calculator.calculate_all_metrics(driver_id)
            all_metrics['drivers'][driver_id]['tracks'][track] = metrics['metrics']
    
    # Save to JSON
    output_path = Path('outputs/driver_metrics.json')
    output_path.parent.mkdir(exist_ok=True)
    
    with open(output_path, 'w') as f:
        json.dump(all_metrics, f, indent=2)
    
    print(f"\nMetrics saved to {output_path}")
    return all_metrics

if __name__ == '__main__':
    metrics = calculate_all_drivers_all_tracks()
    print(f"\nCalculated metrics for {len(metrics['drivers'])} drivers")
```

### Deliverables
- [ ] All 5 metric calculators implemented
- [ ] `outputs/driver_metrics.json` generated
- [ ] Metrics on 0-10 scale with proper distribution
- [ ] Test on 2 drivers × 2 tracks manually

## Phase 3: Track Profiling (Days 11-14)

### Objective
Calculate track demand profiles using data-driven regression.

### Tasks

#### 1. Create track profiler
**File:** `src/data_pipeline/track_profiler.py`

```python
import pandas as pd
import numpy as np
from sklearn.linear_model import LinearRegression
from pathlib import Path
import json

class TrackProfiler:
    """Analyze track characteristics and calculate demands"""
    
    def __init__(self, track_name):
        self.track_name = track_name
        self.data_path = Path(f'data/{track_name}')
        
        # Load driver metrics
        with open('outputs/driver_metrics.json') as f:
            self.metrics_data = json.load(f)
    
    def calculate_track_characteristics(self):
        """Calculate physical track characteristics from telemetry"""
        
        # Load telemetry
        telemetry_file = self.data_path / f'R1_{self.track_name}_telemetry_data.csv'
        df = pd.read_csv(telemetry_file)
        
        characteristics = {}
        
        # Corner count (where lateral G > 0.5)
        corners = df[df['accy_can'].abs() > 0.5]
        characteristics['corner_count'] = len(corners) // 100  # Approximate
        
        # Average lateral G in corners
        characteristics['avg_lateral_g'] = float(corners['accy_can'].abs().mean())
        
        # Heavy braking zones
        braking = df[(df['pbrake_f'] > 50) & (df['accx_can'] < -0.5)]
        characteristics['heavy_braking_zones'] = len(braking) // 50
        
        # Straight percentage (throttle > 95%)
        full_throttle = df[df['aps'] > 95]
        characteristics['straight_percentage'] = (len(full_throttle) / len(df)) * 100
        
        # Technical score (corners + braking)
        characteristics['technical_score'] = min(
            (characteristics['corner_count'] / 2) + 
            (characteristics['heavy_braking_zones'] / 2),
            10
        )
        
        # High-speed score (straights + high G)
        characteristics['high_speed_score'] = min(
            (characteristics['straight_percentage'] / 5) + 
            (characteristics['avg_lateral_g'] * 2),
            10
        )
        
        return characteristics
    
    def calculate_demand_scores(self):
        """
        Calculate track demands using regression.
        
        Algorithm:
        For each attribute, run regression:
        Y = finish_position (lower is better)
        X = driver's score on that attribute
        
        Demand = |coefficient| × R² × 10
        """
        
        attributes = [
            'qualifying_pace',
            'passing_efficiency',
            'corner_mastery',
            'racecraft',
            'consistency'
        ]
        
        demands = {}
        
        # Build dataset
        X_data = {attr: [] for attr in attributes}
        y_data = []
        
        for driver_id, driver_data in self.metrics_data['drivers'].items():
            if self.track_name in driver_data['tracks']:
                track_metrics = driver_data['tracks'][self.track_name]
                
                # Get scores
                for attr in attributes:
                    score = track_metrics[attr]['score']
                    X_data[attr].append(score)
                
                # Get finish position (would need to load from results)
                # For now, use placeholder
                y_data.append(np.random.randint(1, 20))
        
        # Run regression for each attribute
        for attr in attributes:
            X = np.array(X_data[attr]).reshape(-1, 1)
            y = np.array(y_data)
            
            model = LinearRegression()
            model.fit(X, y)
            
            r_squared = model.score(X, y)
            coefficient = abs(model.coef_[0])
            
            # Demand score = coefficient strength × goodness of fit
            demand = coefficient * r_squared * 10
            demands[attr] = round(demand, 1)
        
        # Normalize to reasonable scale
        total = sum(demands.values())
        if total > 0:
            for attr in demands:
                demands[attr] = round((demands[attr] / total) * 40, 1)
        
        return demands
    
    def classify_track_type(self, characteristics):
        """Classify track into persona"""
        
        technical = characteristics['technical_score']
        high_speed = characteristics['high_speed_score']
        
        if technical > 7 and high_speed < 6:
            return "Technical Corner Track"
        elif high_speed > 7 and technical < 6:
            return "High-Speed Flow Track"
        elif abs(technical - high_speed) < 2:
            return "Balanced Power Track"
        else:
            return "Mixed Technical Track"
    
    def generate_profile(self):
        """Generate complete track profile"""
        
        characteristics = self.calculate_track_characteristics()
        demands = self.calculate_demand_scores()
        persona = self.classify_track_type(characteristics)
        
        profile = {
            'id': self.track_name,
            'name': self.track_name.replace('_', ' ').title(),
            'characteristics': characteristics,
            'demands': demands,
            'persona': persona
        }
        
        return profile

def profile_all_tracks():
    """Generate profiles for all tracks"""
    
    tracks = ['barber', 'COTA', 'sebring', 'sonoma', 'VIR', 'road_america']
    
    profiles = {'tracks': {}}
    
    for track in tracks:
        print(f"Profiling {track}...")
        profiler = TrackProfiler(track)
        profile = profiler.generate_profile()
        profiles['tracks'][track] = profile
    
    # Save
    output_path = Path('outputs/track_profiles.json')
    with open(output_path, 'w') as f:
        json.dump(profiles, f, indent=2)
    
    print(f"\nTrack profiles saved to {output_path}")
    return profiles

if __name__ == '__main__':
    profiles = profile_all_tracks()
```

### Deliverables
- [ ] `outputs/track_profiles.json` generated
- [ ] All 6 tracks profiled
- [ ] Demand scores calculated
- [ ] Track personas assigned

## Phase 4: Statistical Validation (Day 14)

### Objective
Validate that metrics are statistically sound.

### Tasks

#### 1. Create validation module
**File:** `src/data_pipeline/validate_metrics.py`

```python
import pandas as pd
import numpy as np
from scipy import stats
from sklearn.ensemble import RandomForestRegressor
import json

class MetricsValidator:
    """Statistical validation of driver metrics"""
    
    def __init__(self):
        # Load data
        with open('outputs/driver_metrics.json') as f:
            self.metrics = json.load(f)
    
    def test_factor_independence(self):
        """Test that 5 factors are not highly correlated"""
        
        # Build correlation matrix
        attributes = [
            'qualifying_pace',
            'passing_efficiency',
            'corner_mastery',
            'racecraft',
            'consistency'
        ]
        
        # Extract scores for all drivers at all tracks
        data = {attr: [] for attr in attributes}
        
        for driver_data in self.metrics['drivers'].values():
            for track_data in driver_data['tracks'].values():
                for attr in attributes:
                    score = track_data[attr]['score']
                    data[attr].append(score)
        
        df = pd.DataFrame(data)
        corr_matrix = df.corr()
        
        print("=== Factor Correlation Matrix ===")
        print(corr_matrix)
        
        # Check for high correlations
        high_corr = []
        for i, attr1 in enumerate(attributes):
            for j, attr2 in enumerate(attributes):
                if i < j:  # Upper triangle only
                    r = corr_matrix.loc[attr1, attr2]
                    if abs(r) > 0.7:
                        high_corr.append((attr1, attr2, r))
        
        if high_corr:
            print("\n⚠️ High correlations detected:")
            for attr1, attr2, r in high_corr:
                print(f"  {attr1} <-> {attr2}: {r:.3f}")
        else:
            print("\n✓ All factors sufficiently independent (r < 0.7)")
        
        return corr_matrix
    
    def test_predictive_validity(self):
        """Test if metrics predict race results"""
        
        # This would require actual race results
        # Placeholder implementation
        
        print("\n=== Predictive Validity ===")
        print("TODO: Implement with actual race results")
        print("Target: R² > 0.5")
        
        return {'r_squared': 0.0}
    
    def run_all_tests(self):
        """Run all validation tests"""
        
        print("=" * 60)
        print("METRICS VALIDATION REPORT")
        print("=" * 60)
        
        corr = self.test_factor_independence()
        pred = self.test_predictive_validity()
        
        report = {
            'correlation_matrix': corr.to_dict(),
            'predictive_validity': pred
        }
        
        # Save report
        with open('outputs/validation_report.json', 'w') as f:
            json.dump(report, f, indent=2)
        
        print("\n" + "=" * 60)
        print("VALIDATION COMPLETE")
        print("=" * 60)
        
        return report

if __name__ == '__main__':
    validator = MetricsValidator()
    validator.run_all_tests()
```

### Deliverables
- [ ] `outputs/validation_report.json` generated
- [ ] Correlation matrix shows independence
- [ ] Any issues documented

## Final Checklist

### Week 1 (Days 1-7)
- [ ] Data validation complete
- [ ] Metric calculations working
- [ ] Initial dataset created

### Week 2 (Days 8-14)
- [ ] Track profiling complete
- [ ] Statistical validation passed
- [ ] All output JSON files generated

### Output Files
- [ ] `outputs/data_quality_report.json`
- [ ] `outputs/driver_metrics.json`
- [ ] `outputs/track_profiles.json`
- [ ] `outputs/validation_report.json`

## Handoff to Agent 2

Once complete, Agent 2 (Frontend) can begin using:
- `driver_metrics.json` for visualizations
- `track_profiles.json` for track demand overlays
- Both files should be placed in `src/frontend/data/`

## Handoff to Agent 3

Once complete, Agent 3 (Coaching) can use:
- `driver_metrics.json` for gap analysis
- `track_profiles.json` for demand comparison
- Telemetry CSVs for detailed insights

## Questions or Issues?

If you encounter:
- **Data quality issues:** Document in validation report, may need to adjust thresholds
- **Calculation errors:** Review algorithm, may need domain expert input
- **Statistical concerns:** Consult validation tests, may need to adjust metrics

Refer to `DOMAIN_KNOWLEDGE.md` for racing expertise context.
