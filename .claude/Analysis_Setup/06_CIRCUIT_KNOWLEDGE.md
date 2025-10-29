# Circuit Knowledge - Track-Specific Racing Expertise

## 🎯 Purpose
Encode racing domain knowledge about each circuit in the GR Cup series to inform:
- Corner classifications
- Feature importance weighting
- Track-specific diagnostic logic
- Circuit fit scoring

---

## 🏁 Track Profiles

### Barber Motorsports Park
**Location:** Birmingham, Alabama  
**Length:** 2.38 miles (3.83 km)  
**Corners:** 17 turns  
**Character:** Technical, flowing, elevation changes

#### Track Characteristics
- **Surface:** High grip, well-maintained
- **Elevation:** 80 feet of elevation change
- **Weather:** Often hot, humid (tire management critical)
- **Overtaking:** Limited opportunities (T1, T5, T16)

#### Corner Classifications
```python
BARBER_CORNERS = {
    1: {
        'name': 'Turn 1',
        'type': 'heavy_braking',
        'apex_speed_target': 55,  # mph
        'importance': 'critical',  # Affects long back straight
        'overtaking': True,
        'tire_wear': 'high',
        'key_skill': 'late_braking'
    },
    2: {
        'name': 'Turn 2',
        'type': 'technical',
        'apex_speed_target': 45,
        'importance': 'medium',
        'overtaking': False,
        'tire_wear': 'medium',
        'key_skill': 'precision'
    },
    3: {
        'name': 'Turn 3',
        'type': 'medium_speed',
        'apex_speed_target': 70,
        'importance': 'medium',
        'overtaking': False,
        'tire_wear': 'low',
        'key_skill': 'flow'
    },
    4: {
        'name': 'Turn 4',
        'type': 'high_speed',
        'apex_speed_target': 90,
        'importance': 'high',
        'overtaking': False,
        'tire_wear': 'low',
        'key_skill': 'commitment'
    },
    5: {
        'name': 'Turn 5',
        'type': 'heavy_braking',
        'apex_speed_target': 50,
        'importance': 'critical',
        'overtaking': True,
        'tire_wear': 'high',
        'key_skill': 'trail_braking'
    },
    # Continue for all 17 corners...
}
```

#### Track Strategy
**Circuit Type:** High-speed flow track  
**Winning Style:** Smooth, committed, high minimum speeds  
**Setup Priority:** High-speed stability over low-speed rotation  

**Most Important Corners:**
1. **Turn 5** - Heavy braking before long straight
2. **Turn 1** - Sets up entire back straight
3. **Turn 16-17** - Exit determines main straight speed

**Common Mistakes:**
- Over-braking at Turn 1 (confidence issue)
- Lifting at Turn 4 (commitment issue)
- Early apex at Turn 5 (compromises exit)

---

### Sonoma Raceway
**Location:** Sonoma, California  
**Length:** 2.52 miles (4.06 km)  
**Corners:** 12 turns  
**Character:** Technical, elevation changes, challenging

#### Track Characteristics
- **Surface:** Abrasive, high tire wear
- **Elevation:** 160 feet of elevation change (most in series)
- **Weather:** Variable, often windy
- **Overtaking:** Very difficult, defensive track

#### Corner Classifications
```python
SONOMA_CORNERS = {
    1: {
        'name': 'Turn 1',
        'type': 'technical_uphill',
        'apex_speed_target': 40,
        'importance': 'high',
        'overtaking': False,
        'tire_wear': 'high',
        'key_skill': 'throttle_control',
        'notes': 'Blind apex, uphill, easy to overshoot'
    },
    2: {
        'name': 'Turn 2 - Esses',
        'type': 'high_speed_complex',
        'apex_speed_target': 75,
        'importance': 'critical',
        'overtaking': False,
        'tire_wear': 'medium',
        'key_skill': 'flow',
        'notes': 'Rhythm section, sets up Turn 3'
    },
    # Continue for all 12 corners...
}
```

**Circuit Type:** Technical, driver-focused  
**Winning Style:** Precision, adaptability, tire management  
**Setup Priority:** Balance over outright speed  

---

### Road America
**Location:** Elkhart Lake, Wisconsin  
**Length:** 4.048 miles (6.515 km)  
**Corners:** 14 turns  
**Character:** High-speed, long straights, flowing

#### Track Characteristics
- **Surface:** Smooth, high grip
- **Elevation:** 80 feet of elevation change
- **Weather:** Variable, can be cool
- **Overtaking:** Multiple opportunities (T1, T5, T14)

**Circuit Type:** Power track with technical sections  
**Winning Style:** High terminal speeds, strong exits  
**Setup Priority:** Straight-line speed, low drag

**Most Important Corners:**
1. **Turn 14** - Fastest corner in series, sets up main straight
2. **Turn 1** - Heavy braking, overtaking opportunity
3. **Turn 5 - Kink** - Flat-out confidence

---

### Sebring International Raceway
**Location:** Sebring, Florida  
**Length:** 3.74 miles (6.02 km)  
**Corners:** 17 turns  
**Character:** Bumpy, technical, endurance-style

#### Track Characteristics
- **Surface:** Rough, bumpy (former airfield)
- **Elevation:** Minimal
- **Weather:** Hot, humid, afternoon thunderstorms
- **Overtaking:** Many opportunities, wide track

**Circuit Type:** Mixed - slow technical + fast sections  
**Winning Style:** Car control, adaptability, consistency  
**Setup Priority:** Compliance, ride height, durability

---

### Virginia International Raceway (VIR)
**Location:** Alton, Virginia  
**Length:** 3.27 miles (5.26 km)  
**Corners:** 18 turns  
**Character:** Fast, flowing, elevation changes

#### Track Characteristics
- **Surface:** Good grip, well-maintained
- **Elevation:** Significant changes
- **Weather:** Variable
- **Overtaking:** Difficult, flow track

**Circuit Type:** High-speed flow  
**Winning Style:** Rhythm, commitment, consistency  
**Setup Priority:** High-speed stability, downforce

---

## 🎯 Circuit Fit Scoring

### Methodology
Match driver's strengths to track requirements.

```python
def calculate_circuit_fit_score(driver_features, track_profile):
    """
    Score how well driver's style matches track requirements.
    
    Returns 0-10 score where:
    - 8-10: Excellent fit, expect strong performance
    - 6-7: Good fit, competitive
    - 4-5: Average fit, room for improvement
    - 0-3: Poor fit, significant weaknesses
    """
    
    scores = []
    
    # 1. High-speed corner performance
    if track_profile['type'] == 'high_speed_flow':
        high_speed_corners = [c for c in track_profile['corners'].values() 
                             if c['type'] == 'high_speed']
        driver_high_speed_delta = calculate_average_delta(
            driver_features, 
            [c['number'] for c in high_speed_corners]
        )
        high_speed_score = normalize_score(driver_high_speed_delta)
        scores.append(('high_speed', high_speed_score, 0.40))  # 40% weight
    
    # 2. Technical precision
    if track_profile['type'] in ['technical', 'mixed']:
        technical_corners = [c for c in track_profile['corners'].values() 
                           if c['type'] == 'technical']
        driver_technical_delta = calculate_average_delta(
            driver_features,
            [c['number'] for c in technical_corners]
        )
        technical_score = normalize_score(driver_technical_delta)
        scores.append(('technical', technical_score, 0.30))  # 30% weight
    
    # 3. Braking performance
    heavy_braking = [c for c in track_profile['corners'].values() 
                    if c['type'] == 'heavy_braking']
    driver_braking_delta = calculate_average_delta(
        driver_features,
        [c['number'] for c in heavy_braking]
    )
    braking_score = normalize_score(driver_braking_delta)
    scores.append(('braking', braking_score, 0.20))  # 20% weight
    
    # 4. Exit speed (for power tracks)
    if track_profile['has_long_straights']:
        exit_critical = [c for c in track_profile['corners'].values() 
                        if c['importance'] == 'critical' and 'straight_after' in c]
        driver_exit_delta = calculate_average_exit_speed_delta(
            driver_features,
            [c['number'] for c in exit_critical]
        )
        exit_score = normalize_score(driver_exit_delta)
        scores.append(('exit', exit_score, 0.10))  # 10% weight
    
    # Calculate weighted average
    total_score = sum(score * weight for _, score, weight in scores)
    
    return {
        'overall_score': total_score,
        'component_scores': {name: score for name, score, _ in scores},
        'interpretation': interpret_score(total_score)
    }
```

---

## 📋 Corner Feature Importance by Track

### Barber Motorsports Park
**Key Success Factors:**
1. High-speed commitment (40% of lap time)
2. Exit speed on power corners (25%)
3. Braking confidence (20%)
4. Technical precision (15%)

**Feature Weights:**
- `apex_speed_vs_winner` in high-speed corners: 1.5x
- `exit_speed_vs_winner` before straights: 1.3x
- `braking_point_vs_winner` at T1, T5: 1.4x

### Sonoma Raceway
**Key Success Factors:**
1. Technical precision (40%)
2. Adaptability to elevation (25%)
3. Tire management (20%)
4. Throttle control (15%)

**Feature Weights:**
- `apex_speed_vs_winner` in technical sections: 1.6x
- `tire_degradation_rate`: 1.4x
- `throttle_modulation` on elevation changes: 1.3x

---

## 🎓 Driver Style Profiles

### Flow Driver
**Strengths:**
- High-speed corners
- Rhythm sections
- Smooth inputs

**Weaknesses:**
- Heavy braking zones
- Ultra-technical slow corners

**Best Tracks:** Barber, Road America, VIR  
**Challenging Tracks:** Sonoma, Sebring

---

### Technical Driver
**Strengths:**
- Precision in slow corners
- Late braking
- Rotation on entry

**Weaknesses:**
- High-speed commitment
- Flow sections

**Best Tracks:** Sonoma, Sebring  
**Challenging Tracks:** Road America, VIR

---

### Balanced Driver
**Strengths:**
- Adaptable
- Consistent
- Tire management

**Weaknesses:**
- May lack standout strength

**Best Tracks:** All (competitive everywhere)  
**Challenging Tracks:** None specifically

---

## 🔧 Using Circuit Knowledge in Diagnostics

### Example: Barber-Specific Coaching

```python
def generate_barber_specific_coaching(driver_features, winner_features):
    """
    Add Barber-specific context to generic diagnostics.
    """
    
    recommendations = []
    
    # Check high-speed corners (critical at Barber)
    high_speed_corners = [4, 9, 13]
    for corner in high_speed_corners:
        delta = driver_features[f'corner_{corner}_apex_speed'] - \
                winner_features[f'corner_{corner}_apex_speed']
        
        if delta < -3:  # 3+ mph slow
            recommendations.append({
                'corner': corner,
                'priority': 'HIGH',  # Barber rewards flow
                'message': f"Turn {corner} is a high-speed flow corner - critical at Barber. "
                          f"You're {abs(delta):.0f}mph slow. Work on commitment and trust. "
                          f"This corner type accounts for 40% of lap time here."
            })
    
    # Check Turn 5 exit (long straight after)
    t5_exit_delta = driver_features['corner_5_exit_speed'] - \
                    winner_features['corner_5_exit_speed']
    
    if t5_exit_delta < -2:
        recommendations.append({
            'corner': 5,
            'priority': 'CRITICAL',
            'message': f"Turn 5 exit sets up the longest straight at Barber. "
                      f"You're {abs(t5_exit_delta):.0f}mph slow on exit. "
                      f"Each 1mph here costs ~0.08s on the straight. "
                      f"Total impact: {abs(t5_exit_delta) * 0.08:.2f}s per lap."
        })
    
    return recommendations
```

---

## ✅ Circuit Knowledge Checklist

For each track, document:
- [  ] Track length, corner count, character
- [  ] Surface characteristics and tire wear
- [  ] Elevation profile
- [  ] Weather patterns
- [  ] All corner definitions with types
- [  ] Most important corners for lap time
- [  ] Overtaking opportunities
- [  ] Track-specific success factors
- [  ] Feature importance weights
- [  ] Common driver mistakes

---

## 📝 Template for Adding New Tracks

```python
NEW_TRACK_TEMPLATE = {
    'name': 'Track Name',
    'location': 'City, State',
    'length_miles': 0.0,
    'length_km': 0.0,
    'corner_count': 0,
    'character': 'Description',
    
    'characteristics': {
        'surface': 'Description',
        'elevation_change_feet': 0,
        'weather': 'Typical conditions',
        'overtaking': 'Description of opportunities'
    },
    
    'corners': {
        1: {
            'name': 'Turn 1',
            'type': 'heavy_braking|technical|high_speed|etc',
            'apex_speed_target': 0,
            'importance': 'critical|high|medium|low',
            'overtaking': True/False,
            'tire_wear': 'high|medium|low',
            'key_skill': 'Skill name',
            'notes': 'Additional context'
        },
        # ... all corners
    },
    
    'strategy': {
        'circuit_type': 'Description',
        'winning_style': 'Description',
        'setup_priority': 'Description',
        'most_important_corners': [1, 5, 12],
        'common_mistakes': ['Mistake 1', 'Mistake 2']
    }
}
```

---

Ready to build? Go to `05_IMPLEMENTATION_GUIDE.md` for step-by-step instructions.

**Have questions about a specific track?** Fill in the template and let the diagnostic engine use that knowledge to generate better coaching!
