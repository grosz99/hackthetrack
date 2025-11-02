# Driver Performance Dashboard - Design Brief

## Executive Summary

This dashboard transforms racing telemetry and performance data into actionable insights for drivers. It shows **how you perform vs the competition** across 4 core skill dimensions, predicts **which tracks suit your driving style**, and identifies **where to improve**.

**Core Value**: Instead of just lap times, drivers see *why* they're fast or slow and *what skills* separate them from the leaders.

---

## 1. KEY DATA COMPONENTS

### A. Driver Overall Score (0-100)
**What it is**: Single number representing overall driver skill
**How it's calculated**: Weighted average of 4 skill factors
- RAW SPEED: 50% weight
- CONSISTENCY: 31% weight
- RACECRAFT: 16% weight
- TIRE MANAGEMENT: 10% weight

**Example**: Driver #13 = 95/100 (Elite), Driver #80 = 62/100 (Mid-pack)

**Design needs**:
- Large, prominent display
- Color-coded (90-100 = Gold/Elite, 75-89 = Silver/Strong, 60-74 = Bronze/Average, <60 = Red/Developing)
- Percentile ranking ("Top 5%", "Top 25%", etc.)

---

### B. 4-Factor Skill Breakdown
**The factors** (with real driver data):

#### Factor 1: CONSISTENCY/PRECISION (31% of score)
**What it measures**: Lap-to-lap consistency, braking repeatability, smoothness
**Variables**:
- Braking consistency (S1 times)
- Sector consistency (S1, S2, S3)
- Stint consistency (lap times)

**Real Examples**:
- Driver #13: 92/100 (Very consistent - braking_consistency z-score = -0.77)
- Driver #80: 45/100 (Erratic - braking_consistency z-score = +0.92)

**User message**: "You brake at the same point lap after lap" vs "Your braking points vary significantly"

---

#### Factor 2: RACECRAFT/OVERTAKING (16% of score)
**What it measures**: Ability to pass cars, gain positions during race
**Variables**:
- Positions gained (start vs finish)
- Position changes (overtakes during race)

**Real Examples**:
- Driver #2 at Road America R1: 95/100 (Qualified 19th, finished 19th but made 42+ position changes during race)
- Driver #13: 68/100 (Strong but not elite - averages +0.18 positions gained)

**User message**: "You gain X positions per race on average" vs "You tend to finish where you qualify"

---

#### Factor 3: RAW SPEED (50% of score) - **DOMINANT FACTOR**
**What it measures**: Outright car pace - qualifying, best lap, sustained speed
**Variables**:
- Qualifying pace (vs pole)
- Best race lap (vs field)
- Average top-10 lap pace

**Real Examples**:
- Driver #13: 98/100 (Elite - qualifying pace z-score = -0.88, consistently 0.2-0.5s faster)
- Driver #57: 25/100 (Struggles - qualifying pace z-score = +2.05, consistently 1.5-2s slower)

**User message**: "You're X.XX seconds faster than average" vs "You're X.XX seconds off the pace"

**Critical insight**: This factor alone predicts ~6 finishing positions per standard deviation!

---

#### Factor 4: TIRE MANAGEMENT/ENDURANCE (10% of score)
**What it measures**: Ability to maintain pace over long stints, preserve tires
**Variables**:
- Early vs late pace ratio
- Late stint performance (final 33% of race)

**Real Examples**:
- Driver #13: 75/100 (Average - loses 0.3-0.5s by end of stint)
- Driver #31 at COTA R1: 5/100 (Terrible - loses 2.5s+ by end of stint)

**User message**: "You maintain pace throughout the race" vs "Your pace drops X.XX seconds late in stints"

---

### C. Circuit Fit Score (0-100 per track)
**What it is**: How well your skill profile matches each track's demands

**How it works**:
- Each track values different skills (e.g., Road America R1 rewards consistency 9.94x, Sebring R2 rewards speed 7.08x)
- Your skill profile × track demand profile = predicted finish position
- Lower predicted finish = higher circuit fit score

**Real Track Examples**:

**Road America R1** (High tire degradation, hard to pass):
- **Rewards**: CONSISTENCY (9.94x), TIRE MGMT (5.59x), RAW SPEED (6.37x)
- **Doesn't reward**: RACECRAFT (-1.08x - negative! Can't pass here)
- Driver #13 fit: 85/100 (Strong speed/consistency, average tire mgmt)
- Driver #2 fit: 72/100 (Elite racecraft doesn't help on this track)

**Sebring R2** (Power track, low degradation):
- **Rewards**: RAW SPEED (7.08x - DOMINANT!), CONSISTENCY (3.74x)
- **Less important**: TIRE MGMT (1.51x), RACECRAFT (0.91x)
- Driver #13 fit: 96/100 (Elite speed dominates here)

**VIR R1** (Technical, balanced):
- **Rewards**: CONSISTENCY (9.07x), RAW SPEED (5.19x)
- **Doesn't reward**: TIRE MGMT (-0.19x - negative! Tire mgmt doesn't matter)
- Driver #7 fit: 91/100 (Great consistency + speed)

**Design needs**:
- Track map thumbnails with circuit fit scores
- Sort tracks by "Best Fit" and "Worst Fit"
- Show WHY each track fits ("Sebring rewards your elite speed")
- Highlight upcoming tracks in calendar

---

### D. Competitive Benchmarking
**What to show**: Where driver ranks vs field in each factor

**Data available**:
- 35 drivers in dataset
- Average z-scores per driver across all races
- Percentile rankings

**Examples**:
- RAW SPEED: Driver #13 = 2nd/35 (Top 6%)
- CONSISTENCY: Driver #13 = 8th/35 (Top 23%)
- RACECRAFT: Driver #13 = 18th/35 (51st percentile - average)
- TIRE MGMT: Driver #13 = 20th/35 (57th percentile - average)

**Design needs**:
- Comparison to field average (horizontal bar: You vs Average vs Leader)
- Percentile badge ("Top 5%", "Above Average", "Below Average")
- Highlight strengths and weaknesses

---

### E. Performance Trends (Race-by-Race)
**What to show**: How driver's scores changed over the season

**Data available**:
- 12 races per season (Barber R1/R2, COTA R1/R2, etc.)
- Factor scores per race
- Finishing position per race

**Examples**:
- Driver #13 RAW SPEED progression: [-1.17, -0.81, -0.67, -0.69, ...] → Consistently fast all season
- Driver #21 CONSISTENCY: Improved from +0.74 (Barber R1) to -0.58 (COTA R2) → Learning curve

**Design needs**:
- Line chart with 4 factors over time
- Annotate with race names/tracks
- Highlight improvement/regression
- "You improved X points in CONSISTENCY since Race 1"

---

### F. Predictive Insights
**What to show**: Predicted performance for upcoming races

**Data available**:
- Track demand profiles for all 7 circuits (12 races)
- Driver skill profile (4 factors)
- Predicted finishing position ± MAE (1.78 positions)

**Examples**:
Driver #13 predictions:
- Sebring R2: Predicted 1.2 ± 1.8 (90% chance of podium)
- Road America R1: Predicted 5.8 ± 1.8 (top-10 likely, podium possible)
- VIR R2: Predicted 3.1 ± 1.8 (podium likely)

**Design needs**:
- Forecast panel for next race
- Probability ranges (90% confidence interval)
- "Based on your elite speed, you're predicted to finish X at [track]"

---

## 2. DASHBOARD LAYOUTS

### Layout A: **Overview Dashboard** (Homepage)
**Goal**: At-a-glance performance summary

**Components** (priority order):
1. **Hero section**: Overall score (0-100) + percentile + grade
2. **4-Factor card grid**: 2x2 cards showing each factor score + trend arrow
3. **Best/Worst tracks**: Top 3 circuit fits + Bottom 3 circuit fits (with track maps)
4. **Next race prediction**: Upcoming race forecast panel
5. **Competitive position**: "You rank Xth/35 overall"

**Layout**:
```
┌─────────────────────────────────────────────────┐
│  DRIVER #13 PERFORMANCE                         │
│  Overall: 95/100 ★★★★★ ELITE (Top 5%)         │
└─────────────────────────────────────────────────┘

┌───────────────┬───────────────┐
│ RAW SPEED     │ CONSISTENCY   │
│ 98/100 ▲      │ 92/100 ▲      │
│ Top 6%        │ Top 23%       │
└───────────────┴───────────────┘
┌───────────────┬───────────────┐
│ RACECRAFT     │ TIRE MGMT     │
│ 68/100 →      │ 75/100 ▼      │
│ 51st pct      │ 57th pct      │
└───────────────┴───────────────┘

BEST TRACKS               WORST TRACKS
1. Sebring R2 (96/100)    1. Road America R1 (72/100)
2. COTA R1 (94/100)       2. VIR R1 (78/100)
3. Sonoma R2 (92/100)     3. Barber R2 (81/100)

NEXT RACE: Sebring R1
Predicted: P2 (±1.8 positions)
Your elite speed gives you a 90% chance of podium
```

---

### Layout B: **Skill Deep Dive**
**Goal**: Understand strengths/weaknesses in detail

**Components**:
1. **Factor comparison radar chart**: 4-axis radar showing you vs field average vs leader
2. **Variable breakdown**: Expand each factor to show underlying variables
3. **Competitive benchmarking**: Horizontal bars showing your rank vs field
4. **Improvement opportunities**: "Focus on Tire Management (your weakest area)"

**Example - RAW SPEED expanded**:
```
RAW SPEED: 98/100 (Top 6%)

Underlying Variables:
├─ Qualifying Pace: 97/100 (0.42s faster than average)
├─ Best Race Lap: 96/100 (0.38s faster than average)
└─ Top-10 Avg Pace: 99/100 (0.51s faster than average)

You vs Field:
You        ▰▰▰▰▰▰▰▰▰▱ 98
Average    ▰▰▰▰▰▱▱▱▱▱ 50
Leader     ▰▰▰▰▰▰▰▰▰▰ 100
```

---

### Layout C: **Circuit Fit Analysis**
**Goal**: See which tracks suit your driving style

**Components**:
1. **Track grid**: 12 race cards with circuit maps + fit scores
2. **Track demand profiles**: Bar chart showing what each track rewards
3. **Fit explanation**: "Sebring rewards speed (your strength)"
4. **Historical performance**: Past results at each track

**Example - Track Card**:
```
┌─────────────────────────────┐
│  [Track Map Thumbnail]      │
│  SEBRING R2                 │
│  Circuit Fit: 96/100 ⭐     │
│                             │
│  Why it fits you:           │
│  ✓ Rewards RAW SPEED (7.08x)│
│    You're Top 6% in speed   │
│  ✓ Rewards CONSISTENCY      │
│    You're Top 23%           │
│                             │
│  Past results:              │
│  2024 R1: P1 (predicted P1.2)│
│  2024 R2: P1 (predicted P1.2)│
└─────────────────────────────┘
```

---

### Layout D: **Race Report** (Post-race)
**Goal**: Understand what happened in the race

**Components**:
1. **Result vs prediction**: "You finished P1, we predicted P1.2 ± 1.8"
2. **Factor performance**: How each factor performed vs your average
3. **Key moments**: Positions gained/lost, consistency lapses
4. **Comparison to field**: "Your speed was 0.6s faster than average today"

**Example**:
```
BARBER R1 - RACE REPORT
Result: P1 ✓ (Predicted P1.2)

Factor Performance:
├─ RAW SPEED: Exceptional (-1.17 z-score, best in field)
├─ CONSISTENCY: Strong (-0.77 z-score)
├─ RACECRAFT: Average (0.05 z-score)
└─ TIRE MGMT: Average (0.08 z-score)

What drove your win:
• Elite speed: 0.6s faster than average all race
• Consistent braking: Top 3 in braking consistency
• Clean race: No major mistakes

Comparison to P2 (Driver #22):
• You were 0.4s faster per lap (speed advantage)
• You were equally consistent
• Similar tire management
```

---

## 3. VISUAL DESIGN ELEMENTS

### Color System
**Factor colors** (use consistently throughout):
- RAW SPEED: `#FF4444` (Red/Hot - fast!)
- CONSISTENCY: `#4444FF` (Blue/Cool - steady)
- RACECRAFT: `#FF9900` (Orange - aggressive)
- TIRE MGMT: `#00CC66` (Green - endurance)

**Score gradients**:
- 90-100: Gold `#FFD700` (Elite)
- 75-89: Silver `#C0C0C0` (Strong)
- 60-74: Bronze `#CD7F32` (Average)
- 40-59: Red `#FF6B6B` (Developing)
- 0-39: Dark Red `#CC0000` (Needs work)

### Icons/Badges
- **Speed**: Lightning bolt ⚡
- **Consistency**: Bullseye 🎯
- **Racecraft**: Crossed swords ⚔️
- **Tire Management**: Tire/wheel 🏁

### Data Visualization Types

**Radar Chart** (Skill profile):
```
        RAW SPEED
            ↑
            |
RACECRAFT ← + → CONSISTENCY
            |
            ↓
       TIRE MGMT
```
- Driver profile = filled shape
- Field average = dotted line
- Leader = outer ring

**Horizontal Bars** (Competitive ranking):
```
RAW SPEED     You  ▰▰▰▰▰▰▰▰▰▱ 98  (2nd/35)
CONSISTENCY   Avg  ▰▰▰▰▰▱▱▱▱▱ 50
              Lead ▰▰▰▰▰▰▰▰▰▰ 100
```

**Track Map Heatmap** (Circuit fit):
- Green = 90-100 (excellent fit)
- Yellow = 75-89 (good fit)
- Orange = 60-74 (average fit)
- Red = <60 (poor fit)

**Line Chart** (Progression over season):
- X-axis: Race 1 → Race 12
- Y-axis: Factor score (-2 to +2 z-score, or convert to 0-100)
- 4 colored lines (one per factor)
- Annotate with track names

---

## 4. KEY USER INTERACTIONS

### Filters/Views
1. **Time range**: "Last 3 races", "Full season", "2024 vs 2023"
2. **Track filter**: "All tracks", "Road courses only", "Ovals only"
3. **Comparison mode**: "Me vs Field", "Me vs Teammate", "Me vs Leader"

### Drilldowns
- Click factor card → See variable breakdown
- Click track → See track-specific performance + circuit fit
- Click race → See race report
- Hover data point → See tooltip with details

### Actions
- "Export Report" → PDF with all insights
- "Share with Team" → Send dashboard link
- "Set Goals" → Target improvement areas

---

## 5. MOBILE CONSIDERATIONS

**Priority content** (what fits on mobile):
1. Overall score (large)
2. 4-Factor scores (compact cards)
3. Next race prediction
4. Best/worst tracks (top 3 each)

**Mobile-specific interactions**:
- Swipe left/right to navigate factor cards
- Tap track map → Full circuit fit page
- Pull down to refresh with latest race data

---

## 6. COPYWRITING GUIDELINES

**Tone**: Direct, actionable, data-driven (not fluffy)
- ✅ "Your speed is 0.42s faster than average"
- ❌ "You're doing great on speed!"

**Insight framing**:
- **Strengths**: "Your elite speed gives you a 6-position advantage"
- **Weaknesses**: "Improving tire management by 1 standard deviation would gain you 1.2 positions"
- **Predictions**: "Based on your profile, you're predicted P2 at Sebring (90% confidence)"

**Avoid jargon** (explain z-scores in plain English):
- ✅ "Top 5% in raw speed"
- ❌ "Z-score of -1.17 in Factor 3"

---

## 7. DATA REFRESH CADENCE

**Real-time** (during race):
- Live position tracking
- Lap times
- Sector consistency

**Post-race** (within 1 hour):
- Factor scores updated
- Race report generated
- Circuit fit recalculated

**Weekly**:
- Overall score recalculated
- Competitive rankings updated
- Season progression trends

---

## 8. EXAMPLE DATA PAYLOADS (For API)

### GET /api/driver/13/overview
```json
{
  "driver_number": 13,
  "overall_score": 95,
  "percentile": 95,
  "grade": "Elite",
  "factors": {
    "raw_speed": {
      "score": 98,
      "z_score": -0.88,
      "rank": "2/35",
      "percentile": 94,
      "trend": "up"
    },
    "consistency": {
      "score": 92,
      "z_score": -0.82,
      "rank": "8/35",
      "percentile": 77,
      "trend": "stable"
    },
    "racecraft": {
      "score": 68,
      "z_score": -0.18,
      "rank": "18/35",
      "percentile": 49,
      "trend": "stable"
    },
    "tire_mgmt": {
      "score": 75,
      "z_score": -0.20,
      "rank": "20/35",
      "percentile": 43,
      "trend": "down"
    }
  },
  "best_tracks": [
    {"track": "sebring_r2", "fit_score": 96},
    {"track": "cota_r1", "fit_score": 94},
    {"track": "sonoma_r2", "fit_score": 92}
  ],
  "worst_tracks": [
    {"track": "roadamerica_r1", "fit_score": 72},
    {"track": "vir_r1", "fit_score": 78},
    {"track": "barber_r2", "fit_score": 81}
  ],
  "next_race_prediction": {
    "track": "sebring_r1",
    "predicted_finish": 1.2,
    "confidence_interval": [0, 3],
    "podium_probability": 0.92
  }
}
```

### GET /api/driver/13/circuit-fit/sebring_r2
```json
{
  "track": "sebring_r2",
  "circuit_fit_score": 96,
  "track_demands": {
    "raw_speed": 7.08,
    "consistency": 3.74,
    "racecraft": 0.91,
    "tire_mgmt": 1.51
  },
  "driver_profile": {
    "raw_speed": -0.88,
    "consistency": -0.82,
    "racecraft": -0.18,
    "tire_mgmt": -0.20
  },
  "fit_explanation": "Sebring R2 heavily rewards RAW SPEED (7.08x coefficient), your strongest skill (Top 6%). Your elite speed gives you a 6-position advantage at this track.",
  "historical_results": [
    {"race": "sebring_r1", "finish": 1, "predicted": 1.2},
    {"race": "sebring_r2", "finish": 1, "predicted": 1.2}
  ]
}
```

---

## 9. TECHNICAL NOTES FOR DESIGNER

**Data source**: All data comes from pre-computed factor scores
- Factor scores are z-scores (mean=0, std=1)
- Negative z-score = better than average
- Positive z-score = worse than average
- Convert to 0-100 scale: `score = 50 - (z_score * 20)` (clamp at 0-100)

**Performance calculations**:
- Overall score = weighted avg: `0.50*speed + 0.31*consistency + 0.16*racecraft + 0.10*tire_mgmt`
- Circuit fit = dot product: `sum(driver[factor] * track[factor])`
- Predicted finish = `13.01 + 3.79*consistency + 1.94*racecraft + 6.08*speed + 1.24*tire_mgmt`

**Statistical terms to hide**:
- "Z-score" → "Performance rating"
- "Standard deviation" → "Typical variation"
- "Coefficient" → "Impact weight"
- "R² = 0.895" → "Model is 90% accurate"

---

## 10. SUCCESS METRICS

**Driver engagement**:
- Time spent on dashboard
- Sections viewed per session
- Return visits per week

**Actionability**:
- "Export Report" clicks
- "Set Goals" usage
- Post-race report views

**Accuracy validation**:
- Predicted vs actual finish error
- User feedback on insights quality
- Coach/team feedback

---

## PRIORITY RANKING FOR MVP

**Must Have** (Launch blockers):
1. Overall score display
2. 4-Factor breakdown
3. Circuit fit scores (all tracks)
4. Competitive benchmarking (vs field)

**Should Have** (Launch +2 weeks):
5. Race-by-race trends
6. Next race predictions
7. Post-race reports

**Nice to Have** (V2):
8. Teammate comparisons
9. Goal setting
10. Historical season comparisons

---

**Status**: Ready for design mockups
**Next Steps**: Create wireframes for Overview Dashboard + Circuit Fit page
