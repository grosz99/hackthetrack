# Product Requirements - Driver Skill Analytics Platform

**Version**: 1.0 (MVP)
**Target Launch**: 3-5 days
**Model**: 4-Factor Driver Skill Model (R² = 0.895)

---

## Executive Summary

Build a driver skill analytics platform that:
1. Calculates overall driver skill scores (0-100)
2. Breaks down skills into 4 dimensions
3. Matches drivers to tracks (circuit fit scoring)
4. Generates actionable driver reports

**Core Value Proposition**: Predict race performance with 90% accuracy using 4 measurable skill dimensions.

---

## 1. Core Features (MVP)

### Feature 1: Driver Overall Score
**Input**: Driver race data (qualifying + race results)
**Output**: Overall skill score (0-100 scale)
**Calculation**: Weighted average of 4 factors
```
Score = 50% × RAW_SPEED + 31% × CONSISTENCY + 16% × RACECRAFT + 10% × TIRE_MGMT
```
**API Endpoint**: `GET /api/driver/{driver_number}/overall-score`

---

### Feature 2: Driver Skill Breakdown
**Input**: Driver race data
**Output**: 4 factor scores (0-100 scale each)

| Factor | Weight | Description |
|--------|--------|-------------|
| RAW SPEED | 50% | Qualifying pace, best lap, sustained speed |
| CONSISTENCY | 31% | Braking consistency, sector consistency |
| RACECRAFT | 16% | Positions gained, position changes |
| TIRE MGMT | 10% | Early vs late pace, tire preservation |

**API Endpoint**: `GET /api/driver/{driver_number}/skill-breakdown`

**Example Response**:
```json
{
  "driver_number": 13,
  "overall_score": 95,
  "skills": {
    "raw_speed": {
      "score": 98,
      "percentile": 99,
      "rating": "ELITE"
    },
    "consistency": {
      "score": 92,
      "percentile": 85,
      "rating": "STRONG"
    },
    "racecraft": {
      "score": 75,
      "percentile": 50,
      "rating": "AVERAGE"
    },
    "tire_management": {
      "score": 68,
      "percentile": 35,
      "rating": "BELOW AVERAGE"
    }
  }
}
```

---

### Feature 3: Circuit Fit Scoring
**Input**: Driver + Track
**Output**: Circuit fit score (0-100) + recommendations

**Calculation**:
```python
# Driver skill profile (z-scores)
driver = {
    'RAW_SPEED': -0.88,      # Faster than average
    'CONSISTENCY': -0.77,    # More consistent than average
    'RACECRAFT': 0.05,       # Average
    'TIRE_MGMT': 0.08        # Average
}

# Track demand profile (regression coefficients)
track = {
    'RAW_SPEED': 5.62,       # Speed important at this track
    'CONSISTENCY': 4.28,     # Consistency important
    'RACECRAFT': 1.19,       # Racecraft moderately important
    'TIRE_MGMT': 2.07        # Tire mgmt moderately important
}

# Dot product + normalize
fit_score = (
    driver['RAW_SPEED'] * track['RAW_SPEED'] +
    driver['CONSISTENCY'] * track['CONSISTENCY'] +
    driver['RACECRAFT'] * track['RACECRAFT'] +
    driver['TIRE_MGMT'] * track['TIRE_MGMT']
)

# Scale to 0-100
circuit_fit = normalize(fit_score) * 100
```

**API Endpoint**: `GET /api/driver/{driver_number}/circuit-fit/{track_name}`

**Example Response**:
```json
{
  "driver_number": 13,
  "track": "barber_r1",
  "circuit_fit_score": 94,
  "predicted_finish": 2.5,
  "confidence_interval": [1, 4],
  "strengths": [
    "Your elite RAW SPEED (98/100) matches this track's high speed demands",
    "Your strong CONSISTENCY (92/100) aligns with track's consistency requirements"
  ],
  "weaknesses": [
    "Average TIRE_MGMT may limit performance at this track"
  ],
  "recommendation": "EXCELLENT FIT - Expect podium finish"
}
```

---

### Feature 4: Driver Report Generation
**Input**: Driver number
**Output**: Comprehensive PDF/HTML report

**Report Sections**:
1. **Overall Rating** (0-100 with visual gauge)
2. **Skill Breakdown** (4 factors with radar chart)
3. **Best Tracks** (Top 5 circuit fits)
4. **Worst Tracks** (Bottom 3 circuit fits)
5. **Recommendations** (Actionable improvement areas)
6. **Historical Performance** (Results across 12 races)

**API Endpoint**: `GET /api/driver/{driver_number}/report`

**Example Report Structure**:
```
═══════════════════════════════════════════════════════════
DRIVER #13 - SKILL ANALYSIS REPORT
═══════════════════════════════════════════════════════════

OVERALL RATING: 95/100 ⭐⭐⭐⭐⭐
Percentile: Top 1% of drivers analyzed

───────────────────────────────────────────────────────────
SKILL BREAKDOWN
───────────────────────────────────────────────────────────

RAW SPEED:        98/100 ████████████████████ ELITE
CONSISTENCY:      92/100 ██████████████████░░ STRONG
RACECRAFT:        75/100 ███████████████░░░░░ AVERAGE
TIRE MANAGEMENT:  68/100 █████████████░░░░░░░ AVERAGE

[Radar Chart Visualization]

───────────────────────────────────────────────────────────
TOP 5 BEST TRACKS (Circuit Fit)
───────────────────────────────────────────────────────────

1. Sebring R2     96/100  ⭐ Speed-focused track suits you
2. COTA R1        94/100  ⭐ Speed + consistency alignment
3. Barber R1      94/100  ⭐ Your strengths match perfectly
4. Sonoma R1      91/100  ⭐ Good racecraft opportunities
5. Barber R2      90/100  ⭐ Consistent performance track

───────────────────────────────────────────────────────────
AREAS FOR IMPROVEMENT
───────────────────────────────────────────────────────────

❌ TIRE MANAGEMENT (68/100) - PRIORITY FOCUS
   Your pace drops 1.2s from early to late stints
   Field average: 0.8s
   Recommendation: Practice long runs, focus on tire preservation

⚠️ RACECRAFT (75/100) - SECONDARY FOCUS
   Position changes: +0.15 per lap (field avg: +0.18)
   Recommendation: Work on overtaking setups, traffic racing

───────────────────────────────────────────────────────────
RACE HISTORY
───────────────────────────────────────────────────────────

Barber R1:        1st  [96/100 circuit fit]
Barber R2:        1st  [90/100 circuit fit]
COTA R1:          3rd  [94/100 circuit fit]
[... 9 more races ...]

Average Finish: 2.8
Win Rate: 25%
Podium Rate: 67%
```

---

## 2. Data Requirements

### Input Data (Per Race)
1. **Qualifying Results** (`data/qualifying/{race}_Qualifying.csv`)
   - Driver number, qualifying time, grid position

2. **Race Results** (`data/race_results/provisional_results/{race}_provisional_results.csv`)
   - Driver number, finishing position, status

3. **Endurance Analysis** (`data/race_results/analysis_endurance/{race}_analysis_endurance.csv`)
   - Lap-by-lap data: lap times, sector times, elapsed times
   - Used for: consistency, tire mgmt, position changes

4. **Best 10 Laps** (`data/race_results/best_10_laps/{race}_best_10_laps.csv`)
   - Best 10 laps per driver
   - Used for: sustained pace metrics

### Pre-Computed Data (Generated by Scripts)
1. **Feature Matrix** (`all_races_tier1_features.csv`)
   - 12 variables × 291 observations

2. **Factor Scores** (`tier1_factor_scores.csv`)
   - 4 factor scores per driver-race

3. **Track Demand Profiles** (`track_demand_profiles_tier1.csv`)
   - Factor importance per track

4. **Driver Averages** (`driver_average_scores_tier1.csv`)
   - Average factor scores across all races

---

## 3. Technical Architecture

### Backend (Python FastAPI)
```
/api
  /driver
    GET /{driver_number}/overall-score
    GET /{driver_number}/skill-breakdown
    GET /{driver_number}/circuit-fit/{track}
    GET /{driver_number}/report
    GET /{driver_number}/history

  /track
    GET /{track_name}/demand-profile
    GET /{track_name}/driver-rankings

  /leaderboard
    GET /overall
    GET /by-skill/{skill_name}

  /comparison
    GET /drivers?driver1={}&driver2={}
```

### Data Pipeline
```
Raw Data (CSV)
    ↓
build_features_tiered.py → Feature Matrix
    ↓
run_tier1_efa.py → Factor Scores
    ↓
validate_tier1_for_product.py → Track Profiles
    ↓
API Layer (FastAPI) → JSON Responses
    ↓
Frontend / Reports
```

### Database Schema (Optional)
```sql
-- If using database instead of CSV files

CREATE TABLE drivers (
    driver_number INT PRIMARY KEY,
    name VARCHAR(100),
    team VARCHAR(100)
);

CREATE TABLE factor_scores (
    id SERIAL PRIMARY KEY,
    driver_number INT REFERENCES drivers,
    race VARCHAR(50),
    raw_speed_score FLOAT,
    consistency_score FLOAT,
    racecraft_score FLOAT,
    tire_mgmt_score FLOAT,
    finishing_position INT,
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE track_profiles (
    track_name VARCHAR(50) PRIMARY KEY,
    raw_speed_importance FLOAT,
    consistency_importance FLOAT,
    racecraft_importance FLOAT,
    tire_mgmt_importance FLOAT
);
```

---

## 4. API Specifications

### Example: Get Driver Overall Score

**Request**:
```http
GET /api/driver/13/overall-score
```

**Response** (200 OK):
```json
{
  "driver_number": 13,
  "overall_score": 95,
  "percentile": 99,
  "rating": "ELITE",
  "races_analyzed": 12,
  "factors": {
    "raw_speed": 98,
    "consistency": 92,
    "racecraft": 75,
    "tire_management": 68
  },
  "recent_form": {
    "last_3_races_avg": 94,
    "trend": "stable"
  }
}
```

---

### Example: Get Circuit Fit

**Request**:
```http
GET /api/driver/13/circuit-fit/barber_r1
```

**Response** (200 OK):
```json
{
  "driver_number": 13,
  "track": "barber_r1",
  "circuit_fit_score": 94,
  "predicted_finish": 2.5,
  "confidence": {
    "lower_bound": 1,
    "upper_bound": 4,
    "interval": "95%"
  },
  "skill_alignment": {
    "raw_speed": {
      "driver_score": 98,
      "track_demand": 5.62,
      "contribution": +5.51,
      "alignment": "EXCELLENT"
    },
    "consistency": {
      "driver_score": 92,
      "track_demand": 4.28,
      "contribution": +3.29,
      "alignment": "STRONG"
    },
    "racecraft": {
      "driver_score": 75,
      "track_demand": 1.19,
      "contribution": +0.06,
      "alignment": "NEUTRAL"
    },
    "tire_management": {
      "driver_score": 68,
      "track_demand": 2.07,
      "contribution": +0.17,
      "alignment": "WEAK"
    }
  },
  "recommendation": "EXCELLENT FIT - Your elite speed and strong consistency match this track's demands perfectly."
}
```

---

## 5. User Interface (Optional - Phase 2)

### Dashboard View
- Driver search/filter
- Top 10 drivers leaderboard
- Recent race results

### Driver Profile Page
- Overall score gauge
- 4-factor radar chart
- Best/worst tracks list
- Historical performance graph
- Download report button

### Track Analysis Page
- Track demand profile visualization
- Driver rankings for this track
- Historical winners analysis

### Comparison Tool
- Side-by-side driver comparison
- Skill difference highlights
- Head-to-head race results

---

## 6. Success Metrics

### Technical Metrics
- ✅ API response time < 200ms
- ✅ 99% uptime
- ✅ Prediction accuracy: MAE < 2.0 positions

### Product Metrics
- ✅ Driver reports generated: 100+ in first week
- ✅ User satisfaction: 4.5+ / 5 stars
- ✅ Feature requests for additional metrics < 20%

### Business Metrics
- ✅ User adoption: 50+ unique users in first month
- ✅ API usage: 1000+ requests/day
- ✅ Report downloads: 200+ in first week

---

## 7. Implementation Timeline

### Day 1: Core API (4-6 hours)
- [ ] Setup FastAPI project structure
- [ ] Implement `/driver/{id}/overall-score` endpoint
- [ ] Implement `/driver/{id}/skill-breakdown` endpoint
- [ ] Load pre-computed factor scores
- [ ] Basic error handling

### Day 2: Circuit Fit (4-6 hours)
- [ ] Load track demand profiles
- [ ] Implement circuit fit calculation
- [ ] Implement `/driver/{id}/circuit-fit/{track}` endpoint
- [ ] Add recommendation logic
- [ ] Test all 12 tracks

### Day 3: Reports & Polish (4-6 hours)
- [ ] Design report template (HTML/PDF)
- [ ] Implement report generation
- [ ] Add visualizations (charts, gauges)
- [ ] API documentation (Swagger/OpenAPI)
- [ ] Testing & bug fixes

### Day 4: Deployment (2-4 hours)
- [ ] Docker containerization
- [ ] Deploy to cloud (AWS/GCP/Heroku)
- [ ] Setup CI/CD
- [ ] Performance testing
- [ ] Documentation

### Day 5: Buffer & Launch
- [ ] Final testing
- [ ] User acceptance testing
- [ ] Bug fixes
- [ ] Go live!

---

## 8. Out of Scope (Version 2.0)

- ❌ Defensive racecraft metrics (not in current model)
- ❌ Telemetry-based features (data quality issues)
- ❌ Real-time race prediction (batch processing only)
- ❌ Multi-season analysis (currently 2025 only)
- ❌ Weather impact analysis (no weather data)
- ❌ Setup recommendations (no setup data)
- ❌ Mobile app (web API only)

---

## 9. Dependencies

### Python Packages
```
fastapi>=0.100.0
uvicorn>=0.23.0
pandas>=2.0.0
numpy>=1.24.0
scikit-learn>=1.3.0
matplotlib>=3.7.0
reportlab>=4.0.0  # For PDF generation
jinja2>=3.1.0     # For HTML templates
```

### Data Files Required
- `data/analysis_outputs/tier1_factor_scores.csv`
- `data/analysis_outputs/track_demand_profiles_tier1.csv`
- `data/analysis_outputs/driver_average_scores_tier1.csv`

---

## 10. Risk Mitigation

| Risk | Mitigation |
|------|------------|
| **Data quality issues** | Already validated - 95%+ completeness |
| **Model overfitting** | Cross-validation shows R² = 0.877 (minimal drop) |
| **Track generalization** | LORO validation shows R² = 0.867 (works on new tracks) |
| **API performance** | Use caching, pre-compute scores |
| **Missing driver data** | Return 404 with clear error message |
| **Invalid track name** | Validate against known tracks, return 400 |

---

## 11. Next Steps

1. **Review this document** - Confirm requirements with stakeholders
2. **Prioritize features** - MVP vs Phase 2
3. **Setup development environment** - FastAPI + dependencies
4. **Begin implementation** - Start with Day 1 tasks

---

**Ready to build?** Review this document and let me know if any requirements need adjustment!
