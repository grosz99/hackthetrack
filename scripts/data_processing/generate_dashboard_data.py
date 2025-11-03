"""
Generate dashboard data JSON from CSV files for the React frontend
"""
import pandas as pd
import json
import os

# Read the data files
driver_scores = pd.read_csv('data/analysis_outputs/driver_average_scores_tier1.csv')
track_demands = pd.read_csv('data/analysis_outputs/track_demand_profiles_tier1.csv')
all_race_scores = pd.read_csv('data/analysis_outputs/tier1_factor_scores.csv')

# Factor names mapping
FACTOR_NAMES = {
    'factor_1_score': 'consistency',
    'factor_2_score': 'racecraft',
    'factor_3_score': 'raw_speed',
    'factor_4_score': 'tire_mgmt'
}

FACTOR_INFO = {
    'raw_speed': {
        'name': 'Raw Speed',
        'weight': '50%',
        'color': '#FF4444',
        'description': 'Outright car pace - qualifying, best lap, sustained speed',
        'icon': '⚡'
    },
    'consistency': {
        'name': 'Consistency',
        'weight': '31%',
        'color': '#4444FF',
        'description': 'Lap-to-lap consistency, braking repeatability, smoothness',
        'icon': '🎯'
    },
    'racecraft': {
        'name': 'Racecraft',
        'weight': '16%',
        'color': '#FF9900',
        'description': 'Ability to pass cars, gain positions during race',
        'icon': '⚔️'
    },
    'tire_mgmt': {
        'name': 'Tire Management',
        'weight': '10%',
        'color': '#00CC66',
        'description': 'Ability to maintain pace over long stints, preserve tires',
        'icon': '🏁'
    }
}

# Track metadata - one entry per unique track
TRACK_INFO = {
    'barber': {
        'id': 'barber',
        'name': 'Barber Motorsports Park',
        'location': 'Birmingham, AL',
        'length': '2.38 miles',
        'description': 'High tire degradation, hard to pass',
        'image': '/track_maps/barber.png',
        'race_ids': ['barber_r1', 'barber_r2']
    },
    'cota': {
        'id': 'cota',
        'name': 'Circuit of The Americas',
        'location': 'Austin, TX',
        'length': '3.41 miles',
        'description': 'Balanced track, rewards speed and consistency',
        'image': '/track_maps/cota.png',
        'race_ids': ['cota_r1', 'cota_r2']
    },
    'roadamerica': {
        'id': 'roadamerica',
        'name': 'Road America',
        'location': 'Elkhart Lake, WI',
        'length': '4.05 miles',
        'description': 'Fast, flowing, rewards racecraft',
        'image': None,
        'race_ids': ['roadamerica_r1', 'roadamerica_r2']
    },
    'sebring': {
        'id': 'sebring',
        'name': 'Sebring International',
        'location': 'Sebring, FL',
        'length': '3.74 miles',
        'description': 'Power track, low degradation, rewards raw speed',
        'image': None,
        'race_ids': ['sebring_r1', 'sebring_r2']
    },
    'sonoma': {
        'id': 'sonoma',
        'name': 'Sonoma Raceway',
        'location': 'Sonoma, CA',
        'length': '2.52 miles',
        'description': 'Technical, elevation changes',
        'image': None,
        'race_ids': ['sonoma_r1', 'sonoma_r2']
    },
    'vir': {
        'id': 'vir',
        'name': 'Virginia International Raceway',
        'location': 'Alton, VA',
        'length': '3.27 miles',
        'description': 'Technical, balanced, tire mgmt doesn\'t matter',
        'image': None,
        'race_ids': ['vir_r1', 'vir_r2']
    }
}

def z_score_to_percentile(z_score):
    """Convert z-score to 0-100 scale (lower z-score = higher percentile)"""
    return max(0, min(100, int(50 - (z_score * 20))))

def calculate_overall_score(factors):
    """Calculate weighted overall score from 4 factors"""
    weights = {
        'raw_speed': 0.50,
        'consistency': 0.31,
        'racecraft': 0.16,
        'tire_mgmt': 0.10
    }

    total = sum(factors[k]['score'] * weights[k] for k in weights.keys())
    return int(total)

def get_grade(score):
    """Get grade based on score"""
    if score >= 90:
        return 'Elite'
    elif score >= 75:
        return 'Strong'
    elif score >= 60:
        return 'Average'
    else:
        return 'Developing'

def calculate_circuit_fit(driver_factors, track_demands):
    """Calculate circuit fit score (0-100)"""
    # Dot product of z-scores and demands
    fit_value = sum(
        driver_factors[factor]['z_score'] * track_demands[factor]
        for factor in ['raw_speed', 'consistency', 'racecraft', 'tire_mgmt']
    )

    # Convert to 0-100 scale (negative fit_value is better)
    normalized = 50 - (fit_value * 5)
    return max(0, min(100, int(normalized)))

# Process drivers
drivers_data = []
for _, row in driver_scores.iterrows():
    driver_num = int(row['driver_number'])

    # Build factors dict
    factors = {}
    for csv_col, factor_name in FACTOR_NAMES.items():
        z_score = row[csv_col]
        score = z_score_to_percentile(z_score)

        factors[factor_name] = {
            'score': score,
            'z_score': float(z_score),
            'percentile': score,
            'trend': 'stable'  # Could calculate from race-by-race data
        }

    overall_score = calculate_overall_score(factors)
    grade = get_grade(overall_score)

    driver_data = {
        'number': driver_num,
        'name': f'Driver #{driver_num}',
        'overall_score': overall_score,
        'grade': grade,
        'percentile': overall_score,
        'races': int(row['num_races']),
        'avg_finish': float(row['finishing_position']),
        'factors': factors
    }

    drivers_data.append(driver_data)

# Sort by overall score descending
drivers_data.sort(key=lambda x: x['overall_score'], reverse=True)

# Process tracks - average demands across both races for each track
tracks_data = []
track_demands_dict = track_demands.set_index(track_demands.columns[0]).to_dict('index')

for track_id, track_info in TRACK_INFO.items():
    # Get demands for both races and average them
    race_ids = track_info['race_ids']
    demands_sum = {
        'raw_speed': 0,
        'consistency': 0,
        'racecraft': 0,
        'tire_mgmt': 0,
        'r2': 0
    }

    count = 0
    for race_id in race_ids:
        if race_id in track_demands_dict:
            demands_row = track_demands_dict[race_id]
            demands_sum['raw_speed'] += float(demands_row.get('Factor_3_RAW_SPEED', 0))
            demands_sum['consistency'] += float(demands_row.get('Factor_1_CONSISTENCY', 0))
            demands_sum['racecraft'] += float(demands_row.get('Factor_2_RACECRAFT', 0))
            demands_sum['tire_mgmt'] += float(demands_row.get('Factor_4_TIRE_MGMT', 0))
            demands_sum['r2'] += float(demands_row.get('R2', 0))
            count += 1

    if count > 0:
        track_data = {
            'id': track_info['id'],
            'name': track_info['name'],
            'location': track_info['location'],
            'length': track_info['length'],
            'description': track_info['description'],
            'image': track_info['image'],
            'demands': {
                'raw_speed': demands_sum['raw_speed'] / count,
                'consistency': demands_sum['consistency'] / count,
                'racecraft': demands_sum['racecraft'] / count,
                'tire_mgmt': demands_sum['tire_mgmt'] / count
            },
            'r2': demands_sum['r2'] / count
        }

        tracks_data.append(track_data)

# Calculate circuit fit for each driver/track combination
for driver in drivers_data:
    best_tracks = []
    worst_tracks = []

    track_fits = []
    for track in tracks_data:
        fit_score = calculate_circuit_fit(driver['factors'], track['demands'])
        track_fits.append({
            'track_id': track['id'],
            'track_name': track['name'],
            'fit_score': fit_score
        })

    # Sort by fit score
    track_fits.sort(key=lambda x: x['fit_score'], reverse=True)

    driver['best_tracks'] = [t['track_id'] for t in track_fits[:3]]
    driver['worst_tracks'] = [t['track_id'] for t in track_fits[-3:]]
    driver['circuit_fits'] = track_fits

# Create final data structure
dashboard_data = {
    'drivers': drivers_data,
    'tracks': tracks_data,
    'factor_info': FACTOR_INFO,
    'model_stats': {
        'r_squared': 0.895,
        'cross_val_r_squared': 0.877,
        'mae': 1.78,
        'races_analyzed': len(all_race_scores)
    }
}

# Write to JSON file
output_path = 'frontend/src/data/dashboardData.json'
os.makedirs(os.path.dirname(output_path), exist_ok=True)

with open(output_path, 'w') as f:
    json.dump(dashboard_data, f, indent=2)

print(f"Generated dashboard data: {output_path}")
print(f"   - {len(drivers_data)} drivers")
print(f"   - {len(tracks_data)} tracks")
top_drivers = ', '.join([f"#{d['number']} ({d['overall_score']})" for d in drivers_data[:3]])
print(f"   - Top 3 drivers: {top_drivers}")
