# Improve Page Implementation Plan

## Overview
Build a driver skill improvement system with interactive sliders, driver matching, and personalized recommendations based on historical performance data.

---

## 🎯 Core Features

### 1. **Persistent Driver Selection**
**Goal**: Driver selection should be "sticky" across pages but changeable

**Implementation**:
```javascript
// DriverContext.jsx enhancement
- Add localStorage to persist selectedDriverNumber
- On mount, check localStorage first, then default to 13
- On change, update localStorage and URL
- Ensure all pages sync with DriverContext state
```

**Acceptance Criteria**:
- ✅ Navigate between pages, driver stays selected
- ✅ Refresh page, driver selection persists
- ✅ Change driver in selector, all pages update
- ✅ URL updates to /driver/{number}/{page}

---

## 🎚️ Feature 2: Interactive Skill Sliders

### Frontend Component: `SkillSliders.jsx`

**UI Design**:
```
┌─────────────────────────────────────────────────┐
│  Set Your Target Skills                         │
├─────────────────────────────────────────────────┤
│                                                  │
│  Speed                      Current: 75 → 80     │
│  ━━━━━━━━━━●───────────────  [+1%] [-1%]        │
│                                                  │
│  Consistency                Current: 68 → 72     │
│  ━━━━━━━●──────────────────  [+1%] [-1%]        │
│                                                  │
│  Racecraft                  Current: 82 → 85     │
│  ━━━━━━━━━━━●──────────────  [+1%] [-1%]        │
│                                                  │
│  Tire Management            Current: 70 → 75     │
│  ━━━━━━━━●─────────────────  [+1%] [-1%]        │
│                                                  │
│  [Find Similar Driver]                           │
└─────────────────────────────────────────────────┘
```

**Implementation**:
```javascript
// State Management
const [targetSkills, setTargetSkills] = useState({
  speed: driverData.speed?.score || 0,
  consistency: driverData.consistency?.score || 0,
  racecraft: driverData.racecraft?.score || 0,
  tire_management: driverData.tire_management?.score || 0
});

// Slider Component
<SkillSlider
  label="Speed"
  current={driverData.speed?.score}
  target={targetSkills.speed}
  onChange={(value) => setTargetSkills({...targetSkills, speed: value})}
  min={0}
  max={100}
  step={1}
/>
```

**Features**:
- Range slider (0-100)
- 1% increment controls (+/- buttons)
- Visual diff showing current → target
- Color coding: current (gray), target (red)
- Prevent target from going below current

---

## 🔍 Feature 3: Similar Driver Matching Algorithm

### Backend Endpoint: `POST /api/drivers/find-similar`

**Request Body**:
```json
{
  "current_driver_number": 13,
  "target_skills": {
    "speed": 80,
    "consistency": 72,
    "racecraft": 85,
    "tire_management": 75
  }
}
```

**Response**:
```json
{
  "similar_driver": {
    "driver_number": 5,
    "driver_name": "Driver #5",
    "skills": {
      "speed": 81,
      "consistency": 73,
      "racecraft": 84,
      "tire_management": 76
    },
    "match_score": 97.5,
    "last_year_performance": {
      "avg_finish": 3.2,
      "wins": 6,
      "top10": 12,
      "consistency_improvement": "+5%",
      "speed_improvement": "+3%"
    }
  }
}
```

**Algorithm** (Python backend):
```python
def find_similar_driver(current_driver_number, target_skills):
    """
    Find driver with skill pattern most similar to target

    Uses weighted Euclidean distance:
    - Smaller distance = more similar
    - Exclude current driver from results
    """

    all_drivers = get_all_drivers_with_skills()

    best_match = None
    best_distance = float('inf')

    for driver in all_drivers:
        if driver.number == current_driver_number:
            continue

        # Calculate distance in 4D skill space
        distance = sqrt(
            (driver.speed - target_skills['speed'])**2 +
            (driver.consistency - target_skills['consistency'])**2 +
            (driver.racecraft - target_skills['racecraft'])**2 +
            (driver.tire_management - target_skills['tire_management'])**2
        )

        if distance < best_distance:
            best_distance = distance
            best_match = driver

    # Convert distance to match score (0-100)
    match_score = max(0, 100 - (best_distance / 4))  # Normalize

    return {
        'similar_driver': best_match,
        'match_score': match_score,
        'distance': best_distance
    }
```

---

## 📊 Feature 4: Recommendations Based on Historical Data

### Backend Endpoint: `GET /api/drivers/{number}/historical-path`

**Purpose**: Get how the similar driver improved last year

**Response**:
```json
{
  "driver_number": 5,
  "driver_name": "Driver #5",
  "current_year": {
    "speed": 81,
    "consistency": 73,
    "racecraft": 84
  },
  "last_year": {
    "speed": 78,
    "consistency": 68,
    "racecraft": 81
  },
  "improvements": [
    {
      "skill": "Speed",
      "change": "+3%",
      "method": "Focused on qualifying performance"
    },
    {
      "skill": "Consistency",
      "change": "+5%",
      "method": "Improved race-to-race variance by 40%"
    },
    {
      "skill": "Racecraft",
      "change": "+3%",
      "method": "Better overtaking efficiency"
    }
  ],
  "key_races": [
    {
      "track": "Barber Motorsports Park",
      "race": 1,
      "breakthrough": "First podium finish after tire strategy improvement"
    }
  ],
  "recommendations": [
    "Focus on qualifying pace - Similar driver improved by 3% through better one-lap speed",
    "Reduce variance in finish positions - Target consistency score of 72+",
    "Study race 1 at Barber - Similar driver had breakthrough with tire management"
  ]
}
```

### Recommendation Engine Logic:

```python
def generate_recommendations(current_driver, target_skills, similar_driver):
    """
    Generate actionable recommendations based on:
    1. Gap between current and target
    2. How similar driver achieved those levels last year
    3. Specific races/tracks where improvement happened
    """

    recommendations = []

    # For each skill gap
    for skill in ['speed', 'consistency', 'racecraft', 'tire_management']:
        gap = target_skills[skill] - current_driver[skill]

        if gap > 0:
            # How did similar driver improve this skill?
            last_year = get_last_year_data(similar_driver)
            improvement = similar_driver[skill] - last_year[skill]

            if improvement > 0:
                # Find races where biggest improvement happened
                breakthrough_races = find_breakthrough_races(
                    similar_driver,
                    skill,
                    last_year
                )

                recommendations.append({
                    'skill': skill,
                    'gap': gap,
                    'similar_driver_improvement': improvement,
                    'method': infer_improvement_method(similar_driver, skill),
                    'breakthrough_races': breakthrough_races,
                    'action': generate_action_item(skill, gap, improvement)
                })

    return recommendations
```

---

## 🎨 Feature 5: Improve Page UI Layout

### Component Structure:
```
┌─────────────────────────────────────────────────────────────┐
│  BACK TO RANKINGS                                           │
│  Rankings › Driver #13 › Improve                            │
├─────────────────────────────────────────────────────────────┤
│  [Overview] [Race Log] [Skills] [Improve]                   │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  ┌──────────────────────────┐  ┌────────────────────────┐  │
│  │  Current Skills          │  │  Target Skills         │  │
│  │                          │  │                        │  │
│  │  Speed:        75        │  │  ━━━━━━━━●───  80    │  │
│  │  Consistency:  68        │  │  ━━━━━━●─────  72    │  │
│  │  Racecraft:    82        │  │  ━━━━━━━━━●──  85    │  │
│  │  Tire Mgmt:    70        │  │  ━━━━━━━●────  75    │  │
│  │                          │  │                        │  │
│  │                          │  │  [Find Match]          │  │
│  └──────────────────────────┘  └────────────────────────┘  │
│                                                              │
│  ┌──────────────────────────────────────────────────────┐  │
│  │  Similar Driver Found: Driver #5 (97.5% match)       │  │
│  │                                                       │  │
│  │  Radar Chart Comparison:                             │  │
│  │  [Your Current] [Your Target] [Driver #5 Current]    │  │
│  │                                                       │  │
│  │  ┌─────────────────────────────────────────────┐     │  │
│  │  │        Consistency                           │     │  │
│  │  │           ▲                                  │     │  │
│  │  │           │                                  │     │  │
│  │  │   Speed ──┼── Racecraft                     │     │  │
│  │  │           │                                  │     │  │
│  │  │      Tire Mgmt                              │     │  │
│  │  └─────────────────────────────────────────────┘     │  │
│  └──────────────────────────────────────────────────────┘  │
│                                                              │
│  ┌──────────────────────────────────────────────────────┐  │
│  │  📈 How Driver #5 Got There (Last Year)              │  │
│  │                                                       │  │
│  │  ✓ Speed: +3% improvement                            │  │
│  │    → Focused on qualifying performance               │  │
│  │    → Breakthrough at Barber Race 1                   │  │
│  │                                                       │  │
│  │  ✓ Consistency: +5% improvement                      │  │
│  │    → Reduced race-to-race variance by 40%            │  │
│  │    → Study races 3-5 at Road America                 │  │
│  │                                                       │  │
│  │  ✓ Racecraft: +3% improvement                        │  │
│  │    → Better overtaking efficiency                    │  │
│  │    → Focus on wheel-to-wheel racing                  │  │
│  │                                                       │  │
│  │  [View Detailed Analysis] [Download Training Plan]   │  │
│  └──────────────────────────────────────────────────────┘  │
│                                                              │
│  ┌──────────────────────────────────────────────────────┐  │
│  │  🎯 Your Personalized Recommendations                │  │
│  │                                                       │  │
│  │  1. Target Speed 80 (+5 points)                      │  │
│  │     • Study Driver #5's qualifying laps at Barber    │  │
│  │     • Focus on brake point optimization              │  │
│  │     • Expected timeline: 3-4 races                   │  │
│  │                                                       │  │
│  │  2. Target Consistency 72 (+4 points)                │  │
│  │     • Reduce finish position variance                │  │
│  │     • Focus on avoiding mistakes in races 8-12       │  │
│  │     • Expected timeline: 6-8 races                   │  │
│  │                                                       │  │
│  │  3. Target Racecraft 85 (+3 points)                  │  │
│  │     • Improve overtaking success rate                │  │
│  │     • Study race starts and restarts                 │  │
│  │     • Expected timeline: 4-5 races                   │  │
│  └──────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
```

---

## 📁 File Structure

### Frontend
```
frontend/src/
  pages/Improve/
    Improve.jsx                    # Main page component
    Improve.css                    # Styles
    components/
      SkillSliders.jsx             # Interactive slider controls
      SimilarDriverCard.jsx        # Match result display
      ComparisonRadarChart.jsx     # 3-overlay radar chart
      ImprovementPath.jsx          # Historical improvement display
      RecommendationsList.jsx      # Personalized recommendations
```

### Backend
```
backend/
  routes/
    improve_routes.py              # New routes for Improve page
  services/
    driver_matching.py             # Similar driver algorithm
    recommendation_engine.py       # Generate recommendations
  data/
    historical_performance.py      # Last year's data queries
```

---

## 🔌 API Endpoints to Create

### 1. Find Similar Driver
```
POST /api/drivers/find-similar
Body: { current_driver_number, target_skills }
Returns: { similar_driver, match_score, last_year_performance }
```

### 2. Historical Performance Path
```
GET /api/drivers/{number}/historical-path
Returns: { current_year, last_year, improvements, key_races }
```

### 3. Generate Recommendations
```
POST /api/drivers/{number}/recommendations
Body: { target_skills, similar_driver_number }
Returns: { recommendations[], estimated_timeline, focus_areas }
```

### 4. Achievements (move from mock)
```
GET /api/drivers/{number}/achievements
Returns: [ { id, name, description, unlocked, progress } ]
```

### 5. Training Programs (move from mock)
```
GET /api/training-programs
Returns: [ { id, name, duration, xp, skills, recommended } ]
```

---

## ⚙️ Implementation Steps for Tomorrow

### Phase 1: Foundation (2-3 hours)
1. ✅ Make driver selection persistent with localStorage
2. ✅ Fix driver selector URL navigation
3. ✅ Test driver switching across all pages

### Phase 2: Frontend Sliders (2-3 hours)
4. ✅ Create `SkillSliders.jsx` component
5. ✅ Add +1% / -1% controls
6. ✅ Build visual diff (current → target)
7. ✅ Create "Find Similar Driver" button

### Phase 3: Backend Matching Algorithm (3-4 hours)
8. ✅ Create `/api/drivers/find-similar` endpoint
9. ✅ Implement Euclidean distance algorithm
10. ✅ Test with various driver combinations
11. ✅ Validate match scores make sense

### Phase 4: Historical Data & Recommendations (3-4 hours)
12. ✅ Query last year's performance data
13. ✅ Create `/api/drivers/{number}/historical-path` endpoint
14. ✅ Build recommendation engine logic
15. ✅ Generate personalized action items

### Phase 5: UI Integration (2-3 hours)
16. ✅ Build `SimilarDriverCard.jsx`
17. ✅ Create 3-overlay radar chart comparison
18. ✅ Build `ImprovementPath.jsx` component
19. ✅ Build `RecommendationsList.jsx`

### Phase 6: Polish & Testing (1-2 hours)
20. ✅ Add loading states
21. ✅ Add error handling
22. ✅ Test full workflow
23. ✅ Deploy to Vercel

---

## 🧪 Testing Scenarios

### Test 1: Basic Slider Interaction
- Driver #13, current speed 75
- Slide to 80
- Verify target updates
- Click "Find Similar Driver"
- Should return a driver with ~80 speed

### Test 2: Multi-Skill Target
- Set targets: Speed 80, Consistency 75, Racecraft 85, Tire 78
- Find similar driver
- Should return driver with pattern closest to all 4 targets
- Match score should be 85%+

### Test 3: Recommendation Quality
- Driver #13 → Driver #5 match
- Should show:
  - How Driver #5 improved last year
  - Specific races where improvement happened
  - Actionable recommendations for Driver #13
  - Estimated timeline for each improvement

### Test 4: Persistence
- Select Driver #13
- Set target skills
- Navigate to Skills page
- Come back to Improve
- Target skills should persist
- Change to Driver #5
- Target skills should reset to Driver #5's current

---

## 📊 Success Metrics

**User Experience**:
- ✅ Driver selection persists across page navigation
- ✅ Sliders are smooth and responsive (1% increments)
- ✅ Similar driver found within 2 seconds
- ✅ Recommendations are actionable and specific

**Technical**:
- ✅ Matching algorithm returns >90% match scores for valid targets
- ✅ Historical data accurately reflects last year's performance
- ✅ All API endpoints return in <1 second
- ✅ No errors in console

**Data Quality**:
- ✅ Match scores make intuitive sense
- ✅ Recommendations reference real races
- ✅ Historical improvements are accurate
- ✅ Timeline estimates are realistic

---

## 🚧 Known Challenges & Solutions

### Challenge 1: No Historical Data
**Problem**: We may not have last year's data in database
**Solution**:
- Use current year data with synthetic "last year" = current - 5%
- Add note in UI: "Using projected data"
- Plan to integrate real historical data later

### Challenge 2: Poor Matches
**Problem**: Target might not match any real driver
**Solution**:
- Show top 3 matches with scores
- Allow user to pick from alternatives
- Explain why match score is lower

### Challenge 3: Generic Recommendations
**Problem**: Recommendations might be too vague
**Solution**:
- Reference specific tracks and races
- Include quantitative targets (e.g., "+3%", "reduce variance by 40%")
- Add telemetry comparison screenshots if available

---

## 🎯 Tomorrow's Goal

**By end of day, the Improve page should**:
1. ✅ Allow users to set target skills with sliders
2. ✅ Find similar driver with matching skill pattern
3. ✅ Show how that driver improved last year
4. ✅ Provide 3-5 actionable, specific recommendations
5. ✅ Driver selection persists across all pages
6. ✅ All features work with real API data (no mocks)

---

## 📝 Notes for Implementation

- Use CSS variables for consistent styling
- Reuse Button component for all actions
- Leverage existing Recharts radar chart component
- Follow existing error handling patterns
- Keep components under 500 lines per file
- Write clear TODO comments for future enhancements

---

**Status**: Ready to implement tomorrow 🚀
