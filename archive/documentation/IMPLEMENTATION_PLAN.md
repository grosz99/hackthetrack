# Circuit Fit Analytics Dashboard - Implementation Plan

## Project Overview
Building a PFF/StatMuse-inspired racing analytics dashboard with 4 main sections focusing on individual driver performance across a season.

---

## Current State Analysis

### What's Working ✅
- Backend API infrastructure (FastAPI)
- AI strategy chat integration (Anthropic Claude)
- Telemetry comparison functionality
- Basic data loading from CSVs
- React frontend with routing
- Component library started

### What Needs Work ❌
- No season statistics aggregation
- No race-by-race results formatting
- No 4-factor skill breakdown
- No skill reallocation simulator
- Design doesn't match PFF/StatMuse style
- Missing SQLite database implementation

---

## Phase 1: Database & Data Infrastructure (Days 1-2)

### 1.1 SQLite Schema Setup
**Goal:** Create pre-processed database for fast queries

**Tasks:**
- [ ] Create `schema.sql` with tables:
  - `drivers` - Driver metadata
  - `season_stats` - Aggregated season statistics
  - `race_results` - Race-by-race data
  - `tracks` - Track information
  - `driver_factors` - 4-factor scores (overall + per track)
  - `factor_variables` - Detailed variable breakdown
  - `skill_simulations` - Simulation cache

**Files to Create:**
- `backend/database/schema.sql`
- `backend/database/connection.py`
- `scripts/load_data.py` - CSV → SQLite loader

**Deliverable:** `circuit-fit.db` file with all data pre-loaded

---

### 1.2 Data Processing Scripts
**Goal:** Process existing CSV data into required formats

**Tasks:**
- [ ] Calculate season stats from race results:
  - Wins, podiums, top 5, top 10, DNFs
  - Average finish, average qualifying
  - Points calculation (GR86 Cup points system)
  - Fastest laps, pole positions

- [ ] Generate race-by-race results:
  - Combine provisional_results + best_10_laps + lap_timing
  - Calculate position changes (start → finish)
  - Extract fastest lap times
  - Calculate gap to leader/winner

- [ ] Calculate driver factors (if not already done):
  - Run factor analysis on 12 variables
  - Generate overall scores (0-100 scale)
  - Calculate percentiles
  - Track-specific factor scores

**Files to Modify:**
- `backend/app/services/data_loader.py` - Add SQLite queries
- Create `scripts/process_season_stats.py`
- Create `scripts/process_driver_factors.py`

**Deliverable:** Populated SQLite database ready for queries

---

## Phase 2: Backend API Endpoints (Days 2-3)

### 2.1 Season Overview Endpoints

**New Endpoints:**
```python
GET /api/drivers/{driver_number}/season-stats
# Returns: wins, podiums, top5, top10, totalRaces, fastestLaps, points, avgFinish

GET /api/drivers/{driver_number}/performance-trend
# Returns: Array of {race, position} for line chart

GET /api/drivers/{driver_number}/quick-stats
# Returns: Best qualifying, championship position, etc.
```

**File:** `backend/app/api/routes.py` (add new routes)

---

### 2.2 Race Log Endpoints

**New Endpoints:**
```python
GET /api/drivers/{driver_number}/race-results
# Returns: Array of race results with:
# - track, round, date
# - startPosition, finishPosition, positionsGained
# - fastestLap, fastestLapRank
# - gapToLeader, gapToWinner
# - incidentPoints
# Sortable by any field

GET /api/drivers/{driver_number}/season-averages
# Returns: Avg start position, avg finish, avg positions gained
```

**File:** `backend/app/api/routes.py`

---

### 2.3 Skills & Factors Endpoints

**New Endpoints:**
```python
GET /api/drivers/{driver_number}/factors
# Query params: track_id (optional)
# Returns: 4 factors with:
# - value (0-100), percentile, rank
# - variables array with sub-metrics

GET /api/drivers/factors/compare?driver1={}&driver2={}
# Returns: Comparative factor analysis for radar chart
```

**File:** `backend/app/api/routes.py`

---

### 2.4 Skill Simulator Endpoints

**New Endpoints:**
```python
POST /api/simulate/skill-reallocation
Body: {
  driver_number: int,
  adjustments: {
    consistency: int,  # -5 to +5
    racecraft: int,
    rawSpeed: int,
    tireMgmt: int
  }
}

Returns: {
  newFactors: {...},
  similarDriver: {driver_number, similarity_score},
  projectedResults: {
    championshipPos,
    avgFinish,
    wins,
    podiums,
    points
  }
}

POST /api/simulate/generate-coaching
Body: {
  currentFactors: {...},
  targetFactors: {...},
  projectedResults: {...}
}
Returns: { summary: "AI-generated coaching text" }
```

**Files:**
- `backend/app/api/routes.py` (routes)
- `backend/app/services/skill_simulator.py` (NEW - simulation logic)

---

## Phase 3: Frontend - Season Overview Page (Day 3)

### 3.1 Season Stats Component
**Goal:** Big stat cards showing wins, podiums, top 5, top 10

**Component Structure:**
```
components/overview/
├── SeasonStats.jsx       # Grid of 4 stat cards
├── StatCard.jsx          # Reusable stat display
├── PerformanceTrend.jsx  # Line chart with Recharts
└── QuickStats.jsx        # Badge displays for misc stats
```

**Features:**
- Large numbers with visual indicators (🏆 for wins)
- Percentile badges
- Hover states
- Responsive grid

**Design:** Dark cards (#151A2E) with red accents (#E60012)

---

### 3.2 Performance Trend Chart
**Goal:** Line chart showing finish position over season

**Library:** Recharts (already installed)

**Features:**
- X-axis: Race rounds (1-12)
- Y-axis: Position (inverted - 1 at top)
- Annotations: Track names
- Hover tooltips with details

---

## Phase 4: Frontend - Race Log Page (Day 4)

### 4.1 Race Table Component
**Goal:** Sortable table with all race results

**Component:**
```jsx
components/race-log/
├── RaceTable.jsx         # Main table with sorting
├── RaceRow.jsx           # Individual row
├── PositionChange.jsx    # ↑/↓ indicators with color
└── SeasonAverages.jsx    # Summary footer
```

**Features:**
- Sortable by any column (click headers)
- Color-coded position changes:
  - Green (↑) for gains
  - Red (↓) for losses
  - Gray (→) for same
- Fast lap highlighting (top 3 = gold/silver/bronze)
- Sticky header

**Design:** Clean table with hover effects, alternating row colors

---

## Phase 5: Frontend - Driver Skills Page (Day 5)

### 5.1 Factor Cards
**Goal:** 4 large cards showing factor scores and percentiles

**Component:**
```jsx
components/skills/
├── FactorCards.jsx          # Grid of 4 cards
├── FactorCard.jsx           # Individual factor display
├── PercentileBadge.jsx      # Color-coded percentile
├── SpiderChart.jsx          # Recharts radar chart
├── VariableBreakdown.jsx    # Expandable accordion
└── TrackSelector.jsx        # Dropdown filter
```

**Percentile Colors (PFF Style):**
- Elite (90+): #00DC82 (green)
- Great (70-89): #39FF14 (bright green)
- Good (50-69): #FFD700 (gold)
- Average (30-49): #FF8C00 (orange)
- Poor (<30): #FF4444 (red)

---

### 5.2 Spider/Radar Chart
**Goal:** Visual comparison of 4 factors

**Library:** Recharts `<Radar>`

**Features:**
- 4-axis chart (Consistency, Racecraft, Raw Speed, Tire Mgmt)
- Driver profile in red (#E60012)
- Field average in gray (optional overlay)
- Comparison driver in blue (optional)

---

### 5.3 Variable Breakdown
**Goal:** Expandable details showing sub-metrics

**UI Pattern:**
```
[▼ Consistency - Click to see variables]
  └─ Brake Point Variance: 68th percentile
  └─ Lap Time Consistency: 71st percentile
  └─ Steering Smoothness: 65th percentile
  └─ Throttle Application: 69th percentile
  └─ Racing Line Deviation: 64th percentile
```

**Component:** Accordion with smooth animations

---

## Phase 6: Frontend - Improve/Simulator Page (Day 6) ⭐ INNOVATION

### 6.1 Skill Sliders
**Goal:** Interactive sliders to adjust factors (5% total budget)

**Component:**
```jsx
components/improve/
├── SkillSliders.jsx         # 4 sliders + budget display
├── SimulationResults.jsx    # Before/after comparison
├── DriverMatch.jsx          # Most similar driver card
└── ImprovementSummary.jsx   # AI coaching display
```

**Features:**
- 4 sliders (range: -5 to +5)
- Real-time budget tracking (5% total)
- Disable sliders when budget = 0
- "SIMULATE" button (disabled until budget = 0)
- Reset button

**UX Flow:**
1. Adjust sliders (total must = 5%)
2. Click "SIMULATE"
3. Backend finds most similar driver
4. Shows projected results
5. Displays AI coaching summary

---

### 6.2 Simulation Algorithm
**Goal:** Match adjusted profile to real driver and project results

**Logic:**
```python
def find_similar_driver(target_factors, all_drivers):
    """
    Calculate Euclidean distance between target and all drivers.
    Return closest match.
    """
    similarities = []
    for driver in all_drivers:
        distance = sqrt(
            (target.consistency - driver.consistency)^2 +
            (target.racecraft - driver.racecraft)^2 +
            (target.rawSpeed - driver.rawSpeed)^2 +
            (target.tireMgmt - driver.tireMgmt)^2
        )
        similarity = 1 / (1 + distance)  # Convert to 0-1 score
        similarities.append((driver, similarity))

    return max(similarities, key=lambda x: x[1])

def project_results(similar_driver, adjustment_magnitude):
    """
    Project results based on similar driver's performance.
    Apply boost based on adjustment magnitude.
    """
    boost = 1 + (adjustment_magnitude * 0.02)  # 2% boost per point
    return {
        "wins": round(similar_driver.wins * boost),
        "podiums": round(similar_driver.podiums * boost),
        "points": round(similar_driver.points * boost * 1.05),
        "avgFinish": similar_driver.avgFinish / boost
    }
```

---

### 6.3 AI Coaching Summary
**Goal:** Generate specific training recommendations

**Prompt Template:**
```python
prompt = f"""
Driver currently has these skill levels:
- Consistency: {current.consistency}
- Racecraft: {current.racecraft}
- Raw Speed: {current.rawSpeed}
- Tire Management: {current.tireMgmt}

They want to improve to:
- Consistency: {target.consistency} ({delta.consistency:+d}%)
- Racecraft: {target.racecraft} ({delta.racecraft:+d}%)
- Raw Speed: {target.rawSpeed} ({delta.rawSpeed:+d}%)
- Tire Management: {target.tireMgmt} ({delta.tireMgmt:+d}%)

This would result in:
- Championship Position: P{current.pos} → P{projected.pos}
- Average Finish: P{current.avg} → P{projected.avg}
- Wins: {current.wins} → {projected.wins}
- Podiums: {current.podiums} → {projected.podiums}

Provide 3 specific, actionable training exercises to achieve these improvements.
Focus on the factors with the largest adjustments.
Keep it under 100 words and make it motivating.
Format as a bulleted list.
"""
```

**Integration:** Use existing AI service (`backend/app/services/ai_strategy.py`)

---

## Phase 7: Design System Implementation (Day 7)

### 7.1 Global Styles
**Goal:** Apply PFF/StatMuse design system

**File:** `frontend/src/index.css`

**CSS Variables:**
```css
:root {
  /* Backgrounds */
  --bg-primary: #0A0E1B;
  --bg-secondary: #151A2E;
  --bg-tertiary: #1F2544;

  /* Brand */
  --primary: #E60012;
  --primary-dark: #B8000F;

  /* Text */
  --text-primary: #FFFFFF;
  --text-secondary: #94A3B8;
  --text-muted: #64748B;

  /* Stats */
  --stat-elite: #00DC82;
  --stat-great: #39FF14;
  --stat-good: #FFD700;
  --stat-average: #FF8C00;
  --stat-poor: #FF4444;

  /* Borders */
  --border: #2A3454;
  --border-light: #3B4565;
}
```

**Typography:**
```css
/* Import Inter font */
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&family=Roboto+Mono:wght@700&display=swap');

body {
  font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
  background: var(--bg-primary);
  color: var(--text-primary);
}

.section-header {
  font-weight: 800;
  text-transform: uppercase;
  letter-spacing: 0.05em;
}

.stat-number {
  font-family: 'Roboto Mono', monospace;
  font-weight: 700;
  font-size: 3rem;
}
```

---

### 7.2 Component Updates
**Goal:** Update all components to use new design system

**Tasks:**
- [ ] Update Navigation component
  - Dark background (#151A2E)
  - Red active states (#E60012)
  - Driver selector with #card styling

- [ ] Create reusable components:
  - `StatCard.jsx` - PFF-style stat display
  - `PercentileBadge.jsx` - Color-coded badges
  - `Button.jsx` - Red primary buttons
  - `Card.jsx` - Dark card with borders

- [ ] Apply dark theme to all pages

---

## Phase 8: Integration & Testing (Day 8)

### 8.1 End-to-End Testing
**Tasks:**
- [ ] Test complete user flow:
  1. Select driver
  2. View season overview
  3. Check race log
  4. Analyze skills
  5. Run simulator
  6. Get coaching

- [ ] Test all API endpoints
- [ ] Test error states
- [ ] Test responsive design (mobile, tablet, desktop)

### 8.2 Performance Optimization
**Tasks:**
- [ ] Add loading states to all pages
- [ ] Implement data caching
- [ ] Optimize chart renders
- [ ] Add skeleton loaders

### 8.3 Polish
**Tasks:**
- [ ] Add smooth transitions
- [ ] Hover effects
- [ ] Loading spinners
- [ ] Empty states
- [ ] Error messages

---

## Phase 9: Deployment (Day 9)

### 9.1 Backend Deployment
**Platform:** Railway.app (free tier)

**Steps:**
1. Create `railway.json` config
2. Set environment variables:
   - `ANTHROPIC_API_KEY`
3. Deploy backend
4. Test endpoints

### 9.2 Frontend Deployment
**Platform:** Vercel (already configured with netlify.toml)

**Steps:**
1. Update `VITE_API_URL` to production backend
2. Run `npm run build`
3. Deploy to Vercel
4. Test production app

---

## File Structure (Final State)

```
hackthetrack-master/
├── backend/
│   ├── app/
│   │   ├── api/
│   │   │   └── routes.py                    # All API endpoints
│   │   ├── database/
│   │   │   ├── schema.sql                   # SQLite schema
│   │   │   └── connection.py                # DB connection
│   │   ├── services/
│   │   │   ├── data_loader.py              # SQLite queries
│   │   │   ├── ai_strategy.py              # Anthropic integration
│   │   │   ├── skill_simulator.py          # NEW - Simulator logic
│   │   │   └── telemetry_processor.py      # Existing
│   │   └── models.py                        # Pydantic models
│   ├── main.py                              # FastAPI app
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   │   ├── shared/
│   │   │   │   ├── StatCard.jsx            # NEW
│   │   │   │   ├── PercentileBadge.jsx     # NEW
│   │   │   │   ├── Button.jsx              # NEW
│   │   │   │   └── Card.jsx                # NEW
│   │   │   ├── overview/
│   │   │   │   ├── SeasonStats.jsx         # NEW
│   │   │   │   ├── PerformanceTrend.jsx    # NEW
│   │   │   │   └── QuickStats.jsx          # NEW
│   │   │   ├── race-log/
│   │   │   │   ├── RaceTable.jsx           # NEW
│   │   │   │   ├── RaceRow.jsx             # NEW
│   │   │   │   └── PositionChange.jsx      # NEW
│   │   │   ├── skills/
│   │   │   │   ├── FactorCards.jsx         # NEW
│   │   │   │   ├── SpiderChart.jsx         # NEW
│   │   │   │   └── VariableBreakdown.jsx   # NEW
│   │   │   ├── improve/
│   │   │   │   ├── SkillSliders.jsx        # NEW
│   │   │   │   ├── SimulationResults.jsx   # NEW
│   │   │   │   └── ImprovementSummary.jsx  # NEW
│   │   │   └── Navigation.jsx              # UPDATE
│   │   ├── pages/
│   │   │   ├── Overview.jsx                # NEW
│   │   │   ├── RaceLog.jsx                 # NEW
│   │   │   ├── Skills.jsx                  # NEW
│   │   │   └── Improve.jsx                 # NEW
│   │   ├── services/
│   │   │   └── api.js                      # UPDATE with new endpoints
│   │   ├── App.jsx                         # UPDATE routes
│   │   └── index.css                       # UPDATE design system
│   └── package.json
├── data/
│   ├── circuit-fit.db                       # NEW - SQLite database
│   ├── race_results/                        # Existing
│   ├── lap_timing/                          # Existing
│   └── analysis_outputs/                    # Existing
├── scripts/
│   ├── load_data.py                         # NEW - CSV → SQLite
│   ├── process_season_stats.py             # NEW
│   └── process_driver_factors.py           # NEW
└── specs/                                    # Existing
    ├── circuit-fit-dashboard-spec.md
    └── circuit-fit-database-spec.md
```

---

## Success Criteria

### Functionality
- ✅ All 4 pages working (Overview, Race Log, Skills, Improve)
- ✅ SQLite database with pre-loaded data
- ✅ API endpoints returning correct data
- ✅ Skill simulator finding similar drivers
- ✅ AI coaching generating relevant advice

### Design
- ✅ Matches PFF/StatMuse style
- ✅ Dark theme with red accents
- ✅ Color-coded percentiles
- ✅ Responsive on all devices

### Performance
- ✅ Page loads < 2 seconds
- ✅ Smooth animations
- ✅ No layout shift
- ✅ API responses < 500ms

---

## Timeline Summary

**Total Time:** 9 days

- **Days 1-2:** Database & data processing
- **Day 3:** Season Overview page
- **Day 4:** Race Log page
- **Day 5:** Driver Skills page
- **Day 6:** Improve/Simulator page ⭐
- **Day 7:** Design system implementation
- **Day 8:** Testing & polish
- **Day 9:** Deployment

**Estimated Hours:** 50-60 hours

---

## Next Steps

1. ✅ Review this plan with team
2. ⏳ Start Phase 1: Database setup
3. ⏳ Create `schema.sql`
4. ⏳ Write data processing scripts
5. ⏳ Build out API endpoints
6. ⏳ Start frontend components

**Let's start building! 🚀**
