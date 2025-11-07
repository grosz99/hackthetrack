# 🎮 2K-Style Driver Development API

## Overview
NBA 2K-inspired driver development system for the **Driver Training & Insights** hackathon category.

This gives drivers a gamified experience to:
- See their tier ranking (S/A/B/C/D)
- View skill radar charts
- Run "what-if" scenarios with skill sliders
- Get AI-generated training plans
- Find similar drivers to benchmark against

---

## 🏆 New Endpoints

### 1. GET `/api/drivers/{driver_number}/profile-2k`

**Get 2K-style driver profile with tier and archetype**

#### Response Example:
```json
{
  "driver_number": 27,
  "driver_name": "Driver #27",
  "tier": {
    "tier": "A",
    "overall_rating": 78,
    "rank_in_tier": 2,
    "total_in_tier": 7,
    "next_tier_threshold": 90
  },
  "current_skills": {
    "speed": 82.5,
    "consistency": 75.3,
    "racecraft": 71.2,
    "tire_management": 68.9
  },
  "season_stats": {
    "wins": 2,
    "podiums": 8,
    "top5": 15,
    "avg_finish": 5.2,
    "total_races": 24
  },
  "archetype": "Speed Demon"
}
```

#### Archetypes:
- **Speed Demon**: Elite speed (85+ percentile)
- **Consistent Finisher**: Elite consistency
- **Wheel-to-Wheel Specialist**: Elite racecraft
- **Strategic Tactician**: Elite tire management
- **All-Rounder**: Balanced across all skills (<15 point spread)
- **Raw Speed**, **Point Scorer**, **Battler**, **Tire Whisperer**: Moderate strength versions

#### Tier Breakdown:
- **S Tier**: Top 10% (90-100 percentile)
- **A Tier**: Next 20% (70-90 percentile)
- **B Tier**: Middle 40% (30-70 percentile)
- **C Tier**: Next 20% (10-30 percentile)
- **D Tier**: Bottom 10% (0-10 percentile)

---

### 2. POST `/api/drivers/{driver_number}/what-if`

**Run what-if scenario with skill adjustments**

#### Request Body:
```json
{
  "adjustments": [
    {
      "factor": "consistency",
      "adjustment_percent": 5.0
    },
    {
      "factor": "tire_management",
      "adjustment_percent": 3.0
    }
  ]
}
```

#### Valid factors:
- `speed`
- `consistency`
- `racecraft`
- `tire_management`

#### Adjustment limits:
- Min: -10%
- Max: +10%

#### Response Example:
```json
{
  "scenario_name": "Consistency +5.0%, Tire Management +3.0%",
  "adjusted_skills": {
    "speed": 82.5,
    "consistency": 80.3,
    "racecraft": 71.2,
    "tire_management": 71.9
  },
  "predicted_finish": 4.1,
  "predicted_position_change": +1,
  "similar_driver_match": {
    "driver_number": 13,
    "driver_name": "Driver #13",
    "similarity_score": 94.2,
    "match_percentage": 94.2,
    "skill_differences": {
      "speed": -2.1,
      "consistency": +1.5,
      "racecraft": +3.2,
      "tire_management": -0.8
    },
    "predicted_finish": 4.3,
    "key_strengths": ["Speed", "Consistency"]
  },
  "training_plan": {
    "target_skill": "Consistency",
    "current_level": 75.3,
    "target_level": 80.3,
    "estimated_time": "2-4 weeks",
    "drills": [
      {
        "drill_name": "Pace Management Stint",
        "description": "Run 10-lap stints focusing on hitting the same lap time (±0.2s) every lap. No heroics, just consistency.",
        "focus_area": "Lap Time Repeatability",
        "duration": "1 hour",
        "difficulty": "Advanced",
        "expected_improvement": "+1.3 percentile points"
      },
      // ... 3 more drills
    ],
    "ai_coaching_summary": "Your consistency is currently at 75.3 percentile. To reach 80.3, focus on maintaining consistent reference points..."
  }
}
```

---

### 3. POST `/api/drivers/{driver_number}/training-plan`

**Generate AI training plan for specific skill**

#### Query Parameters:
- `target_skill` (required): One of `speed`, `consistency`, `racecraft`, `tire_management`
- `target_improvement_percent` (required): 1-20 (how many percentage points to improve)

#### Example Request:
```
POST /api/drivers/27/training-plan?target_skill=consistency&target_improvement_percent=10
```

#### Response Example:
```json
{
  "target_skill": "Consistency",
  "current_level": 75.3,
  "target_level": 85.3,
  "estimated_time": "1-2 months",
  "drills": [
    {
      "drill_name": "Pace Management Stint",
      "description": "Run 10-lap stints focusing on hitting the same lap time (±0.2s) every lap...",
      "focus_area": "Lap Time Repeatability",
      "duration": "1 hour",
      "difficulty": "Advanced",
      "expected_improvement": "+2.5 percentile points"
    },
    {
      "drill_name": "Reference Point Discipline",
      "description": "Identify 5 key reference points per lap and hit them exactly every lap...",
      "focus_area": "Reference Points",
      "duration": "45 minutes",
      "difficulty": "Advanced",
      "expected_improvement": "+2.5 percentile points"
    },
    // ... 2 more drills
  ],
  "ai_coaching_summary": "Claude AI-generated coaching advice specific to your current level and target..."
}
```

---

## 📊 Training Drill Library

### Speed Drills:
1. **Hotlap Time Attack** - Qualifying-style single laps (30 min)
2. **Brake Point Optimization** - Find absolute limit on brake markers (45 min)
3. **Minimum Corner Speed Analysis** - Telemetry comparison vs fastest driver (1 hour)
4. **Throttle Application Drill** - Get to full throttle earlier (30 min)

### Consistency Drills:
1. **Pace Management Stint** - Hit same lap time ±0.2s for 10 laps (1 hour)
2. **Reference Point Discipline** - Hit 5 key points exactly each lap (45 min)
3. **Traffic Navigation** - Maintain pace through slower traffic (30 min)
4. **Mental Reset Exercise** - Recover from mistakes within 2 laps (30 min)

### Racecraft Drills:
1. **Overtaking Scenarios** - Practice outbraking, late apex, switchback (45 min)
2. **Defensive Driving** - Defensive lines without losing time (30 min)
3. **Wheel-to-Wheel Awareness** - Practice alongside cars, first-lap positioning (45 min)
4. **Strategic Decision Making** - Study race scenarios with engineer (1 hour)

### Tire Management Drills:
1. **Tire Save Stint** - Extend tire life by 20% (1.5 hours)
2. **Thermal Management** - Keep tires in optimal temp window (45 min)
3. **Degradation Analysis** - Monitor lap-by-lap tire wear (1 hour)
4. **Setup Optimization** - Reduce tire wear through setup changes (2 hours)

---

## 🎨 Frontend UI Recommendations

### 1. Driver Profile Page (2K-Style)
```
┌─────────────────────────────────────────────────────┐
│  DRIVER #27                         [A TIER] ⭐      │
│  Speed Demon                         Rank: 2/7       │
├─────────────────────────────────────────────────────┤
│                                                       │
│         📊 SKILL RADAR CHART                         │
│                                                       │
│              Speed (82)                               │
│                  ●                                    │
│                 / \                                   │
│    Tire (69)   /   \   Consistency (75)              │
│         ●─────●─────●                                 │
│                 \ /                                   │
│                  ●                                    │
│            Racecraft (71)                             │
│                                                       │
├─────────────────────────────────────────────────────┤
│  📈 SEASON STATS                                      │
│  • Wins: 2  • Podiums: 8  • Top 5: 15                │
│  • Avg Finish: 5.2  • Total Races: 24                │
│                                                       │
│  🎯 NEXT TIER: Need 90 rating for S Tier (12 pts)    │
└─────────────────────────────────────────────────────┘
```

### 2. What-If Simulator Page
```
┌─────────────────────────────────────────────────────┐
│  WHAT-IF SIMULATOR                                    │
├─────────────────────────────────────────────────────┤
│  Adjust your skills to see predicted outcomes:       │
│                                                       │
│  Speed:        [============●----] 82.5   [+0%]      │
│  Consistency:  [=========●-------] 75.3   [+5%] ⬆️   │
│  Racecraft:    [========●--------] 71.2   [+0%]      │
│  Tire Mgmt:    [=======●---------] 68.9   [+3%] ⬆️   │
│                                                       │
│  📊 PREDICTED OUTCOME:                                │
│  • Current Avg Finish: 5.2                            │
│  • Predicted Finish: 4.1   [+1 position] ⬆️           │
│                                                       │
│  🎯 YOU'D BE LIKE:                                    │
│  Driver #13 (94.2% match)                             │
│  - Similar speed and consistency                      │
│  - Avg finish: 4.3                                    │
│                                                       │
│  [View Training Plan →]                               │
└─────────────────────────────────────────────────────┘
```

### 3. Training Plan Page
```
┌─────────────────────────────────────────────────────┐
│  TRAINING PLAN: Consistency +5%                       │
│  Current: 75.3 → Target: 80.3 (⏱️ 2-4 weeks)         │
├─────────────────────────────────────────────────────┤
│  💬 AI COACHING:                                      │
│  "Your consistency is strong but can be improved..."  │
│                                                       │
│  📋 TRAINING DRILLS:                                  │
│                                                       │
│  1️⃣ Pace Management Stint                            │
│     ⏱️ 1 hour  |  🎯 Lap Time Repeatability           │
│     💪 Advanced                                       │
│     Run 10-lap stints hitting ±0.2s every lap...     │
│     Expected: +1.3 percentile points                  │
│                                                       │
│  2️⃣ Reference Point Discipline                       │
│     ⏱️ 45 min  |  🎯 Reference Points                 │
│     💪 Advanced                                       │
│     Identify 5 key reference points per lap...       │
│     Expected: +1.3 percentile points                  │
│                                                       │
│  [+ 2 more drills...]                                 │
│                                                       │
│  [Start Training] [Download PDF]                      │
└─────────────────────────────────────────────────────┘
```

---

## 🚀 Demo Flow for Judges

### 1. Opening Hook (30 sec)
"Racing drivers have access to gigabytes of telemetry data, but no idea how to improve. We built NBA 2K for racing."

### 2. Show Driver Profile (1 min)
- Pull up Driver #27's profile
- "This is a B-tier driver. Speed Demon archetype - fast but inconsistent"
- Show radar chart highlighting speed (high) vs consistency (low)

### 3. Run What-If Scenario (1.5 min)
- "Let's say they improve consistency by just 5%"
- Move slider from 75 → 80
- "Now they're predicted to finish 4.1 instead of 5.2 - that's a full position better"
- "They'd be like Driver #13, who averages 4.3"

### 4. Show Training Plan (1 min)
- Click "View Training Plan"
- "Here are 4 specific drills to get there"
- Show AI coaching summary
- "Takes 2-4 weeks of focused practice"

### 5. Differentiation (30 sec)
- "We're the only team using RepTrak normalization for skill scoring"
- "We combine macro (lap times) and micro (telemetry) analysis"
- "AI coaching generates personalized training based on your weaknesses"

### 6. Closing
"Drivers can finally answer: 'If I improve X by Y%, where do I finish?' And more importantly: 'How do I actually get there?'"

---

## 🎯 Winning Pitch

**Category**: Driver Training & Insights

**Value Prop**: Turn complex telemetry data into actionable training plans

**Unique Differentiators**:
1. **Gamification**: 2K-style tiers, archetypes, ratings
2. **Prediction**: "What-if" scenarios with skill sliders
3. **Actionability**: AI-generated training drills specific to driver's level
4. **Benchmarking**: Match drivers with similar skill profiles
5. **Scientific**: RepTrak-normalized percentile rankings

**User Journey**:
1. Driver sees they're B-tier with weak consistency
2. Runs what-if: "If I improve consistency 5%, I move up a position"
3. Gets personalized 4-week training plan
4. Benchmarks against Driver #13 who has similar profile
5. Follows drills, improves consistency, moves up to A-tier

---

## 📝 Implementation Checklist

### Backend ✅ (DONE)
- [x] Tier calculation (S/A/B/C/D)
- [x] Archetype determination
- [x] What-if scenario endpoint
- [x] Training plan generator
- [x] 16 racing-specific drills
- [x] AI coaching integration
- [x] Similar driver matching

### Frontend (TO DO)
- [ ] Driver profile page with radar chart
- [ ] Skill sliders with real-time prediction
- [ ] Training plan display
- [ ] Tier badge/ranking display
- [ ] Similar driver card
- [ ] PDF export for training plans (bonus)

### Testing
- [ ] Test with multiple drivers (different tiers)
- [ ] Verify tier calculations
- [ ] Test what-if predictions
- [ ] Confirm training plans generate correctly

---

## 💡 Quick Frontend Example (React)

```jsx
// Example: Display driver profile
const DriverProfile2K = ({ driverNumber }) => {
  const [profile, setProfile] = useState(null);

  useEffect(() => {
    fetch(`/api/drivers/${driverNumber}/profile-2k`)
      .then(res => res.json())
      .then(setProfile);
  }, [driverNumber]);

  if (!profile) return <Loading />;

  return (
    <div className="driver-profile-2k">
      <div className="tier-badge tier-{profile.tier.tier}">
        {profile.tier.tier} TIER
      </div>

      <h1>Driver #{profile.driver_number}</h1>
      <p className="archetype">{profile.archetype}</p>

      <RadarChart data={profile.current_skills} />

      <div className="season-stats">
        <Stat label="Wins" value={profile.season_stats.wins} />
        <Stat label="Podiums" value={profile.season_stats.podiums} />
        <Stat label="Avg Finish" value={profile.season_stats.avg_finish.toFixed(1)} />
      </div>

      {profile.tier.next_tier_threshold && (
        <div className="next-tier">
          Need {profile.tier.next_tier_threshold} rating for next tier
        </div>
      )}
    </div>
  );
};

// Example: What-if simulator
const WhatIfSimulator = ({ driverNumber }) => {
  const [adjustments, setAdjustments] = useState({
    speed: 0,
    consistency: 0,
    racecraft: 0,
    tire_management: 0
  });
  const [result, setResult] = useState(null);

  const runScenario = async () => {
    const body = {
      adjustments: Object.entries(adjustments)
        .filter(([_, val]) => val !== 0)
        .map(([factor, adjustment_percent]) => ({
          factor,
          adjustment_percent
        }))
    };

    const res = await fetch(`/api/drivers/${driverNumber}/what-if`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(body)
    });

    setResult(await res.json());
  };

  return (
    <div className="what-if-simulator">
      <h2>What-If Simulator</h2>

      {Object.keys(adjustments).map(skill => (
        <SkillSlider
          key={skill}
          skill={skill}
          value={adjustments[skill]}
          onChange={val => setAdjustments({...adjustments, [skill]: val})}
          min={-10}
          max={10}
        />
      ))}

      <button onClick={runScenario}>Run Scenario</button>

      {result && (
        <div className="scenario-result">
          <h3>{result.scenario_name}</h3>
          <p>Predicted Finish: {result.predicted_finish.toFixed(1)}</p>
          <p>Position Change: {result.predicted_position_change > 0 ? '+' : ''}{result.predicted_position_change}</p>

          <SimilarDriverCard driver={result.similar_driver_match} />

          <TrainingPlanCard plan={result.training_plan} />
        </div>
      )}
    </div>
  );
};
```

---

## 🏆 Why This Wins

1. **Addresses Real Pain Point**: Drivers have data but no actionable insights
2. **Gamified & Engaging**: 2K-style progression feels like a video game
3. **Predictive**: Shows outcomes before committing to training
4. **Actionable**: Specific drills with durations and difficulty levels
5. **Scientific Backing**: RepTrak normalization, 4-factor model
6. **AI-Powered**: Claude generates personalized coaching
7. **Complete Solution**: Profile → What-If → Training → Improvement

Good luck! 🏁
