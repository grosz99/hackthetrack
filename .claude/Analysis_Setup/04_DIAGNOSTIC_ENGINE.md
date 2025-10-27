# Diagnostic Engine - Circuit Fit Analysis

## 🎯 Goal
**Convert validated features into specific, actionable driver coaching**

Input: Statistical features  
Output: "Do THIS differently to go faster"

---

## 🏗️ Diagnostic Architecture

```
Validated Features → Corner Analysis → Issue Diagnosis → Actionable Recommendation → Priority Ranking
```

---

## 📊 Diagnostic Logic

### 1. Corner-Level Diagnosis

```python
def diagnose_corner(driver_data, winner_data, field_avg_data, corner_num):
    """
    Identify THE specific issue costing time in this corner.
    
    Decision tree approach:
    1. Where is time lost? (entry/apex/exit)
    2. What's the root cause? (braking point/speed/line/traction)
    3. What should driver change? (specific action)
    """
    
    diagnosis = {
        'corner_number': corner_num,
        'time_lost': driver_data['section_time'] - winner_data['section_time'],
        'issue_location': None,
        'root_cause': None,
        'recommendation': None,
        'estimated_gain': None
    }
    
    # Step 1: Identify WHERE time is lost
    entry_deficit = driver_data['entry_speed'] - winner_data['entry_speed']
    apex_deficit = driver_data['apex_speed'] - winner_data['apex_speed']
    exit_deficit = driver_data['exit_speed'] - winner_data['exit_speed']
    
    deficits = {
        'entry': entry_deficit,
        'apex': apex_deficit,
        'exit': exit_deficit
    }
    
    # Find biggest issue
    worst_phase = min(deficits, key=deficits.get)
    diagnosis['issue_location'] = worst_phase
    
    # Step 2: Diagnose ROOT CAUSE based on location
    if worst_phase == 'entry':
        diagnosis = diagnose_entry_issue(driver_data, winner_data, diagnosis)
    elif worst_phase == 'apex':
        diagnosis = diagnose_apex_issue(driver_data, winner_data, diagnosis)
    elif worst_phase == 'exit':
        diagnosis = diagnose_exit_issue(driver_data, winner_data, diagnosis)
    
    return diagnosis


def diagnose_entry_issue(driver_data, winner_data, diagnosis):
    """
    Entry speed is low - why?
    
    Possible causes:
    - Braking too early
    - Braking too hard initially
    - Coasting before turn-in
    """
    
    braking_point_delta = driver_data['braking_point'] - winner_data['braking_point']
    brake_pressure_delta = driver_data['max_brake_pressure'] - winner_data['max_brake_pressure']
    
    if braking_point_delta > 10:  # Braking 10m+ earlier
        diagnosis['root_cause'] = 'braking_too_early'
        diagnosis['recommendation'] = (
            f"Brake {abs(braking_point_delta):.0f}m later. "
            f"Winners brake at {winner_data['braking_point']:.0f}m marker, "
            f"you're braking at {driver_data['braking_point']:.0f}m. "
            f"Carry more entry speed."
        )
        diagnosis['estimated_gain'] = braking_point_delta * 0.01  # ~10m = 0.1s
        
    elif brake_pressure_delta > 0.15:  # Over-braking
        diagnosis['root_cause'] = 'excessive_initial_braking'
        diagnosis['recommendation'] = (
            f"Reduce initial brake pressure. You're at {driver_data['max_brake_pressure']:.0%}, "
            f"winners at {winner_data['max_brake_pressure']:.0%}. "
            f"More gradual braking preserves momentum."
        )
        diagnosis['estimated_gain'] = brake_pressure_delta * 0.5
        
    else:  # Late trail braking or turn-in timing
        diagnosis['root_cause'] = 'trail_braking_incomplete'
        diagnosis['recommendation'] = (
            "Extend trail braking deeper into corner. "
            "You're releasing brakes too early, losing rotation and speed."
        )
        diagnosis['estimated_gain'] = 0.05
    
    return diagnosis


def diagnose_apex_issue(driver_data, winner_data, diagnosis):
    """
    Apex speed is low - why?
    
    Possible causes:
    - Scrubbing speed in mid-corner
    - Wrong line (apex too early/late)
    - Lifting mid-corner due to understeer/oversteer
    """
    
    min_speed_location_delta = (driver_data['min_speed_location'] - 
                               winner_data['min_speed_location'])
    
    if abs(min_speed_location_delta) > 2:  # Minimum speed 2m+ off optimal
        if min_speed_location_delta < 0:  # Min speed too early
            diagnosis['root_cause'] = 'early_apex'
            diagnosis['recommendation'] = (
                f"Apex {abs(min_speed_location_delta):.1f}m later. "
                f"Your minimum speed occurs {abs(min_speed_location_delta):.1f}m "
                "before the geometric apex. Move turn-in point later."
            )
        else:  # Min speed too late
            diagnosis['root_cause'] = 'late_apex'
            diagnosis['recommendation'] = (
                f"Turn in earlier - your minimum speed is {min_speed_location_delta:.1f}m "
                "past optimal. Earlier turn-in will let you apex at speed."
            )
        diagnosis['estimated_gain'] = abs(min_speed_location_delta) * 0.01
        
    else:  # Line is okay, just slow
        diagnosis['root_cause'] = 'mid_corner_lift'
        diagnosis['recommendation'] = (
            "Trust the grip. You're lifting or hesitating mid-corner. "
            f"Winners carry {winner_data['apex_speed']:.0f}mph, "
            f"you're at {driver_data['apex_speed']:.0f}mph. "
            "Commit to the turn."
        )
        diagnosis['estimated_gain'] = 0.08
    
    return diagnosis


def diagnose_exit_issue(driver_data, winner_data, diagnosis):
    """
    Exit speed is low - why?
    
    Possible causes:
    - Throttle application too early (wheelspin)
    - Throttle application too late (wasting track)
    - Wrong line compromising exit
    """
    
    throttle_point_delta = (driver_data['throttle_application_point'] - 
                           winner_data['throttle_application_point'])
    throttle_modulation = driver_data['throttle_modulation']
    
    # Early throttle but slow exit = wheelspin
    if throttle_point_delta < -1 and throttle_modulation > 0.15:
        diagnosis['root_cause'] = 'wheelspin_from_early_throttle'
        diagnosis['recommendation'] = (
            f"Delay throttle by {abs(throttle_point_delta):.1f}m. "
            f"You apply at {driver_data['throttle_application_point']:.1f}m after apex, "
            f"winners at {winner_data['throttle_application_point']:.1f}m. "
            "You're getting wheelspin - wait for more rotation before power."
        )
        diagnosis['estimated_gain'] = abs(throttle_point_delta) * 0.02
        
    # Late throttle
    elif throttle_point_delta > 1:
        diagnosis['root_cause'] = 'late_throttle_application'
        diagnosis['recommendation'] = (
            f"Apply throttle {throttle_point_delta:.1f}m earlier. "
            "You're wasting track on exit. Winners are on power sooner."
        )
        diagnosis['estimated_gain'] = throttle_point_delta * 0.015
        
    # Throttle timing okay but still slow
    else:
        diagnosis['root_cause'] = 'exit_line_compromise'
        diagnosis['recommendation'] = (
            "Your exit line is compromised. "
            "You're either too tight (can't unwind steering) or too wide (longer arc). "
            "Use more track on exit."
        )
        diagnosis['estimated_gain'] = 0.05
    
    return diagnosis
```

---

## 🎯 Priority Ranking System

```python
def prioritize_corner_issues(all_corner_diagnoses):
    """
    Sort improvement opportunities by impact.
    
    Priority score = time_gain * consistency_factor * actionability
    """
    
    for diagnosis in all_corner_diagnoses:
        # Consistency factor: Is this a repeated issue across laps?
        corner_num = diagnosis['corner_number']
        consistency = calculate_corner_consistency(driver_data, corner_num)
        
        # Actionability: How easy is this to fix?
        actionability_scores = {
            'braking_too_early': 0.9,           # Easy - just brake later
            'excessive_initial_braking': 0.8,   # Easy - reduce pressure
            'early_apex': 0.7,                  # Medium - change turn-in
            'wheelspin_from_early_throttle': 0.9,  # Easy - delay throttle
            'late_throttle_application': 0.8,   # Easy - throttle sooner
            'trail_braking_incomplete': 0.5,    # Hard - technique change
            'mid_corner_lift': 0.4,             # Hard - confidence issue
            'exit_line_compromise': 0.6         # Medium - line adjustment
        }
        
        actionability = actionability_scores.get(diagnosis['root_cause'], 0.5)
        
        # Calculate priority score
        diagnosis['priority_score'] = (
            diagnosis['estimated_gain'] * 
            consistency * 
            actionability
        )
    
    # Sort by priority score
    return sorted(all_corner_diagnoses, 
                 key=lambda x: x['priority_score'], 
                 reverse=True)
```

---

## 📋 Diagnostic Report Format

### Full Driver Report

```python
def generate_driver_report(driver_name, race, all_diagnoses):
    """
    Create comprehensive coaching report.
    """
    
    report = {
        'driver': driver_name,
        'race': race,
        'overall_gap': calculate_overall_gap_to_winner(),
        'total_potential_gain': sum(d['estimated_gain'] for d in all_diagnoses),
        
        'top_3_priorities': all_diagnoses[:3],
        'by_corner': all_diagnoses,
        
        'consistency_issues': identify_consistency_problems(),
        'tire_management': analyze_tire_degradation(),
        'racecraft': analyze_wheel_to_wheel_performance(),
        
        'circuit_fit_score': calculate_circuit_fit(),
        'strengths': identify_strong_corners(),
        'weaknesses': identify_weak_corners()
    }
    
    return report
```

### Example Report Output

```markdown
# Circuit Fit Analysis Report
**Driver:** John Smith (#42)  
**Race:** Barber Motorsports Park - R1 2024  
**Finishing Position:** 7th  
**Gap to Winner:** +12.4 seconds

---

## Executive Summary
**Total Potential Gain:** 1.8 seconds per lap  
**Key Focus Areas:** Entry speed (3 corners), Exit traction (2 corners)

---

## Top 3 Priority Improvements

### 1. Turn 5 - Entry Speed Issue ⚡ Potential Gain: 0.18s
**Current:** You're 0.18s slower than winners in Turn 5  
**Root Cause:** Braking 15m too early (103m marker vs winners' 88m)  
**Action:** Brake at the 90m marker. Use the brake marker board as reference.  
**Expected Impact:** 0.18s per lap = 3.6s over 20 laps

### 2. Turn 8 Exit - Wheelspin from Early Throttle ⚡ Potential Gain: 0.15s
**Current:** You're 4mph slower on exit (87mph vs 91mph)  
**Root Cause:** Applying throttle 1.2s after apex, winners wait 1.5s. You're getting wheelspin.  
**Action:** Wait 0.3s longer before throttle. Let car rotate more before power application.  
**Expected Impact:** 0.15s per lap = 3.0s over 20 laps

### 3. Turn 1 - Excessive Initial Braking ⚡ Potential Gain: 0.12s
**Current:** Entry speed 8mph slower (110mph vs 118mph)  
**Root Cause:** Peak brake pressure 88% vs winners' 72%. Over-braking kills momentum.  
**Action:** Reduce initial brake force. More gradual application, deeper trail braking.  
**Expected Impact:** 0.12s per lap = 2.4s over 20 laps

---

## Corner-by-Corner Breakdown

### High-Priority Corners (>0.10s potential gain)
| Corner | Time Lost | Issue | Quick Fix |
|--------|-----------|-------|-----------|
| Turn 5 | 0.18s | Entry | Brake 15m later |
| Turn 8 | 0.15s | Exit | Delay throttle 0.3s |
| Turn 1 | 0.12s | Entry | Reduce brake pressure |

### Medium-Priority Corners (0.05-0.10s potential gain)
| Corner | Time Lost | Issue | Quick Fix |
|--------|-----------|-------|-----------|
| Turn 11 | 0.08s | Apex | Turn in 2m earlier |
| Turn 3 | 0.06s | Exit | Apply throttle 0.8m sooner |

### Strong Corners (<0.03s from winners)
Turns 2, 7, 9, 13, 15 - Maintain your technique here! ✅

---

## Consistency Analysis
**Most Inconsistent Corner:** Turn 5  
- Braking point varies by 14m across laps  
- Best lap: 95m marker, Worst lap: 109m marker  
- Establish a visual reference point: Use the 100m board consistently

**Overall Lap Time Consistency:** 0.8s std dev  
- Field average: 0.5s  
- **Action:** Focus on corner entry consistency. Your mid-corner and exit are stable.

---

## Tire Management
**Degradation Rate:** 0.09s/lap (laps 8-15)  
**Field Average:** 0.06s/lap  
**Issue:** Front tire wear in Turns 1, 5, 11 (heavy braking)

**Recommendation:**  
Reduce initial brake pressure by 8% to preserve front tires. You're over-braking on entry, heating fronts faster than winners.

---

## Circuit Fit Score: 7.2/10
**Barber Style:** High-speed flow, technical precision  

**Your Strengths:**  
✅ High-speed corners (T4, T9, T13) - Only 0.04s off winners  
✅ Technical slow corners (T2, T15) - Matching winners

**Your Weaknesses:**  
❌ Heavy braking zones (T1, T5) - Entry speed 8-10mph slow  
❌ Exit traction (T8, T11) - Wheelspin issues costing 4-5mph

**Circuit Fit:** You match this track well! Focus on braking confidence and exit traction for next visit.

---

## Practice Plan

### Session 1: Entry Speed Focus
1. **Turn 5:** Practice braking at 90m board (15 laps)
2. **Turn 1:** Reduce initial brake force, extend trail braking (10 laps)
3. **Video review:** Compare your entries to fastest lap

### Session 2: Exit Traction
1. **Turn 8:** Delay throttle application by 0.3s (10 laps)
2. **Turn 11:** Wait for car rotation before power (10 laps)
3. **Experiment:** Try different throttle application points

### Session 3: Full Lap Integration
1. Combine entry and exit improvements
2. Focus on consistency - hit your reference points every lap
3. Target lap time: Current best minus 0.45s

---

**Estimated Total Improvement:** 0.45s per lap with these changes  
**Race Impact:** ~9 seconds over 20 laps = 2-3 positions
```

---

## 🔧 Implementation Code

```python
class DiagnosticEngine:
    def __init__(self, validated_features):
        self.validated_features = validated_features
    
    def generate_full_report(self, driver_name, race_data):
        """
        Main entry point for generating diagnostic report.
        """
        
        # Get driver's data
        driver_data = race_data[race_data['driver_name'] == driver_name]
        winner_data = race_data[race_data['finishing_position'] == 1]
        field_avg = race_data.groupby('corner_number').mean()
        
        # Diagnose all corners
        diagnoses = []
        for corner in range(1, 18):
            corner_driver = driver_data[driver_data['corner_number'] == corner]
            corner_winner = winner_data[winner_data['corner_number'] == corner]
            
            diagnosis = diagnose_corner(
                corner_driver.iloc[0],
                corner_winner.iloc[0],
                field_avg.loc[corner],
                corner
            )
            diagnoses.append(diagnosis)
        
        # Prioritize issues
        prioritized = prioritize_corner_issues(diagnoses)
        
        # Generate full report
        report = generate_driver_report(driver_name, race_data.name, prioritized)
        
        return report
```

---

## ✅ Diagnostic Quality Checklist

Every recommendation must:
- [ ] Be specific (exact meters, seconds, mph)
- [ ] Compare to winner (not just "brake later")
- [ ] Include expected time gain
- [ ] Be physically actionable by driver
- [ ] Reference a visual cue when possible ("100m board")
- [ ] Explain WHY (root cause, not just symptom)

---

Ready to implement the full system? See `05_IMPLEMENTATION_GUIDE.md`
