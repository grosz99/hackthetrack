# Circuit Fit Analytics Dashboard - Hack the Track 2025
## PFF/StatMuse-Inspired Racing Analytics Platform

---

## Project Overview
Build a professional racing analytics dashboard modeled after Pro Football Focus (PFF) and StatMuse, featuring comprehensive driver statistics, performance factors, and a unique "skill reallocation simulator" that shows drivers how to optimize their training.

**Category:** Driver Training & Insights  
**Core Innovation:** Interactive skill reallocation simulator showing optimal training paths  
**Design Inspiration:** PFF's clean stats + StatMuse's visual excellence

---

## Technical Stack
- **Frontend:** React 18 + Next.js 14
- **Styling:** Tailwind CSS (PFF-style design system)
- **Charts:** Recharts + D3.js (for advanced visualizations)
- **State Management:** Zustand (lightweight, perfect for dashboards)
- **Data:** JSON files (pre-processed from provisional results)
- **AI:** OpenAI API for improvement summaries

---

## Design System (PFF/StatMuse Inspired)

### Color Palette
```css
:root {
  /* Primary - Toyota GR Red */
  --primary: #E60012;
  --primary-dark: #B8000F;
  
  /* Grays - PFF Style */
  --bg-primary: #0A0E1B;      /* Dark blue-black background */
  --bg-secondary: #151A2E;     /* Card backgrounds */
  --bg-tertiary: #1F2544;      /* Hover states */
  
  /* Text */
  --text-primary: #FFFFFF;
  --text-secondary: #94A3B8;
  --text-muted: #64748B;
  
  /* Stats Colors */
  --stat-elite: #00DC82;       /* 90+ percentile */
  --stat-great: #39FF14;       /* 70-89 percentile */
  --stat-good: #FFD700;        /* 50-69 percentile */
  --stat-average: #FF8C00;     /* 30-49 percentile */
  --stat-poor: #FF4444;        /* <30 percentile */
  
  /* Borders */
  --border: #2A3454;
  --border-light: #3B4565;
}
```

### Typography
```css
/* Headers - Bold, all caps like PFF */
.section-header {
  font-family: 'Inter', sans-serif;
  font-weight: 800;
  text-transform: uppercase;
  letter-spacing: 0.05em;
}

/* Stats - Large, impactful numbers */
.stat-number {
  font-family: 'Roboto Mono', monospace;
  font-weight: 700;
  font-size: 3rem;
}

/* Labels - Clean, minimal */
.stat-label {
  font-family: 'Inter', sans-serif;
  font-weight: 500;
  color: var(--text-secondary);
  font-size: 0.875rem;
}
```

---

## Project Structure
```
circuit-fit-dashboard/
├── app/
│   ├── layout.tsx
│   ├── page.tsx                      # Redirects to /overview
│   ├── overview/
│   │   └── page.tsx                  # Section 1: Season Overview
│   ├── race-log/
│   │   └── page.tsx                  # Section 2: Race by Race
│   ├── skills/
│   │   └── page.tsx                  # Section 3: Driver Skills
│   └── improve/
│       └── page.tsx                  # Section 4: Areas to Improve
├── components/
│   ├── layout/
│   │   ├── Navigation.tsx            # Top nav with driver selector
│   │   ├── SectionTabs.tsx           # Tab navigation
│   │   └── DriverSelector.tsx        # Dropdown with search
│   ├── overview/
│   │   ├── SeasonStats.tsx           # Win/podium cards
│   │   ├── PerformanceTrend.tsx      # Line chart
│   │   └── QuickStats.tsx            # Fast lap badges
│   ├── race-log/
│   │   ├── RaceTable.tsx             # Sortable table
│   │   ├── RaceRow.tsx               # Individual race data
│   │   └── PositionChange.tsx        # Visual position delta
│   ├── skills/
│   │   ├── FactorCards.tsx           # 4 factor percentiles
│   │   ├── SpiderChart.tsx           # D3 radar chart
│   │   ├── VariableBreakdown.tsx     # Expandable variables
│   │   └── TrackSelector.tsx         # Filter by track
│   ├── improve/
│   │   ├── SkillSliders.tsx          # Interactive sliders
│   │   ├── SimulationResults.tsx     # Before/after comparison
│   │   ├── DriverMatch.tsx           # "Most similar to..."
│   │   └── ImprovementSummary.tsx    # AI-generated insights
│   └── shared/
│       ├── StatCard.tsx              # Reusable stat display
│       ├── PercentileBadge.tsx       # Color-coded percentiles
│       └── LoadingState.tsx          # Skeleton loaders
├── data/
│   ├── drivers.json                  # Driver metadata
│   ├── season_stats.json             # Aggregated season data
│   ├── race_results.json             # Race-by-race data
│   ├── driver_factors.json           # Factor scores
│   └── driver_variables.json         # Detailed variables
├── lib/
│   ├── utils.ts                      # Helper functions
│   ├── constants.ts                  # Track names, etc.
│   └── simulator.ts                  # Skill reallocation logic
└── styles/
    └── globals.css                    # Tailwind + custom styles
```

---

## Section 1: Season Overview

### Layout
```
┌─────────────────────────────────────────────────────────┐
│  DRIVER SELECTOR: [#13 - Driver Name ▼]      Season 2025│
├─────────────────────────────────────────────────────────┤
│                                                          │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐  │
│  │   WINS   │ │ PODIUMS  │ │  TOP 5   │ │  TOP 10  │  │
│  │    2     │ │    5     │ │    8     │ │    12    │  │
│  │  🏆🏆    │ │  🥇🥈🥈🥉🥉 │ │  ████░░░░│ │  ████████│  │
│  └──────────┘ └──────────┘ └──────────┘ └──────────┘  │
│                                                          │
│  PERFORMANCE TREND                                       │
│  ┌──────────────────────────────────────────────────┐  │
│  │   📈 Line chart showing position each race       │  │
│  └──────────────────────────────────────────────────┘  │
│                                                          │
│  QUICK STATS                                            │
│  ⚡ Fastest Lap: 3 races  |  🏁 Avg Finish: P6.4      │
│  🎯 Best Qualifying: P2   |  📊 Points: 287           │
└─────────────────────────────────────────────────────────┘
```

### Component Implementation
```tsx
// components/overview/SeasonStats.tsx
interface SeasonStatsProps {
  driverId: string;
  stats: {
    wins: number;
    podiums: number;
    top5: number;
    top10: number;
    totalRaces: number;
  };
}

export function SeasonStats({ stats }: SeasonStatsProps) {
  return (
    <div className="grid grid-cols-4 gap-4">
      <StatCard
        label="Wins"
        value={stats.wins}
        visual={<WinIndicators count={stats.wins} />}
        percentile={calculatePercentile(stats.wins, 'wins')}
      />
      <StatCard
        label="Podiums"
        value={stats.podiums}
        visual={<PodiumIndicators podiums={stats.podiums} />}
        percentile={calculatePercentile(stats.podiums, 'podiums')}
      />
      {/* ... */}
    </div>
  );
}
```

### Data Structure
```json
// data/season_stats.json
{
  "13": {
    "name": "Driver Name",
    "number": 13,
    "team": "Team Name",
    "stats": {
      "wins": 2,
      "podiums": 5,
      "top5": 8,
      "top10": 12,
      "totalRaces": 16,
      "fastestLaps": 3,
      "polePositions": 1,
      "avgFinish": 6.4,
      "avgQualifying": 7.2,
      "points": 287
    },
    "trend": [
      {"race": 1, "position": 8},
      {"race": 2, "position": 5},
      // ...
    ]
  }
}
```

---

## Section 2: Race-by-Race Log

### Layout
```
┌─────────────────────────────────────────────────────────┐
│  RACE LOG - 2025 SEASON                   [Export CSV]  │
├─────────────────────────────────────────────────────────┤
│                                                          │
│  Track    Start  Finish  Change  Fast Lap  Gap to Win  │
│  ─────────────────────────────────────────────────────  │
│  Barber    P8     P5      ↑3     1:23.456   +0.234s    │
│  VIR       P12    P7      ↑5     1:31.234   +0.567s    │
│  COTA      P6     P3      ↑3     1:52.345   +0.123s    │
│  Road Am.  P4     P8      ↓4     2:01.234   +0.890s    │
│  Sebring   P9     P6      ↑3     1:45.678   +0.345s    │
│  Sonoma    P7     P2      ↑5     1:38.901   +0.089s    │
│                                                          │
│  Season Averages:                                       │
│  Avg Start: P7.3 | Avg Finish: P5.2 | Avg Gain: +2.1  │
└─────────────────────────────────────────────────────────┘
```

### Component Implementation
```tsx
// components/race-log/RaceTable.tsx
interface RaceResult {
  track: string;
  round: number;
  startPosition: number;
  finishPosition: number;
  fastestLap: string;
  gapToLeader: string;
  gapToWinner: string;
  incidentsPoints: number;
}

export function RaceTable({ driverId }: { driverId: string }) {
  const results = useRaceResults(driverId);
  
  return (
    <div className="bg-bg-secondary rounded-lg p-6">
      <table className="w-full">
        <thead>
          <tr className="text-text-secondary text-sm uppercase">
            <th>Track</th>
            <th>Start</th>
            <th>Finish</th>
            <th>Change</th>
            <th>Fastest Lap</th>
            <th>Gap to Winner</th>
          </tr>
        </thead>
        <tbody>
          {results.map(race => (
            <RaceRow key={race.round} race={race} />
          ))}
        </tbody>
      </table>
      <SeasonAverages results={results} />
    </div>
  );
}

// Visual position change indicator
function PositionChange({ delta }: { delta: number }) {
  const color = delta > 0 ? 'text-stat-elite' : 
                delta < 0 ? 'text-stat-poor' : 
                'text-text-muted';
  const arrow = delta > 0 ? '↑' : delta < 0 ? '↓' : '→';
  
  return (
    <span className={`font-bold ${color}`}>
      {arrow}{Math.abs(delta)}
    </span>
  );
}
```

### Data Source
```json
// data/race_results.json (from provisional_results files)
{
  "13": [
    {
      "track": "Barber Motorsports Park",
      "round": 1,
      "date": "2025-03-15",
      "startPosition": 8,
      "finishPosition": 5,
      "fastestLap": "1:23.456",
      "fastestLapRank": 3,
      "gapToLeader": "+12.345",
      "gapToWinner": "+0.234",
      "lapsCompleted": 30,
      "incidentsPoints": 0
    },
    // ... more races
  ]
}
```

---

## Section 3: Driver Skills (Factor Analysis)

### Layout
```
┌─────────────────────────────────────────────────────────┐
│  DRIVER SKILLS                    [Compare Driver ▼]    │
├─────────────────────────────────────────────────────────┤
│                                                          │
│  OVERALL FACTORS                   [All Tracks ▼]       │
│  ┌─────────┐ ┌─────────┐ ┌─────────┐ ┌─────────┐     │
│  │CONSIST. │ │RACECRAFT│ │RAW SPEED│ │TIRE MGMT│     │
│  │   66    │ │   53    │ │   67    │ │   54    │     │
│  │  72nd %  │ │  45th % │ │  78th % │ │  51st % │     │
│  └─────────┘ └─────────┘ └─────────┘ └─────────┘     │
│                                                          │
│  SPIDER CHART                                           │
│  ┌──────────────────────────────────────────────────┐  │
│  │         Consistency                              │  │
│  │              *                                   │  │
│  │     RC  *---*---*  RS                           │  │
│  │         \   |   /                                │  │
│  │          \  |  /                                 │  │
│  │           \ | /                                  │  │
│  │            \|/                                   │  │
│  │        -----*-----                               │  │
│  │              TM                                  │  │
│  └──────────────────────────────────────────────────┘  │
│                                                          │
│  [▼ Consistency - Click to see variables]               │
│  └─ Brake Point Variance: 68th percentile              │
│  └─ Lap Time Consistency: 71st percentile              │
│  └─ Steering Smoothness: 65th percentile               │
└─────────────────────────────────────────────────────────┘
```

### Component Implementation
```tsx
// components/skills/FactorCards.tsx
interface Factor {
  name: string;
  value: number;
  percentile: number;
  variables: Variable[];
}

export function FactorCards({ driverId, track = 'overall' }) {
  const factors = useDriverFactors(driverId, track);
  
  return (
    <div className="grid grid-cols-4 gap-4">
      {factors.map(factor => (
        <FactorCard
          key={factor.name}
          factor={factor}
          onClick={() => toggleVariables(factor.name)}
        />
      ))}
    </div>
  );
}

// components/skills/SpiderChart.tsx
export function SpiderChart({ 
  driver1, 
  driver2 = null,
  track = 'overall' 
}) {
  const data = formatSpiderData(driver1, driver2, track);
  
  return (
    <div className="bg-bg-secondary rounded-lg p-6">
      <ResponsiveContainer width="100%" height={400}>
        <Radar data={data}>
          <PolarGrid stroke="#2A3454" />
          <PolarAngleAxis dataKey="factor" />
          <PolarRadiusAxis domain={[0, 100]} />
          <RadarChart>
            <Radar
              name={driver1.name}
              dataKey="driver1"
              stroke="#E60012"
              fill="#E60012"
              fillOpacity={0.3}
            />
            {driver2 && (
              <Radar
                name={driver2.name}
                dataKey="driver2"
                stroke="#00DC82"
                fill="#00DC82"
                fillOpacity={0.3}
              />
            )}
          </RadarChart>
        </Radar>
      </ResponsiveContainer>
    </div>
  );
}
```

### Data Structure
```json
// data/driver_factors.json
{
  "13": {
    "overall": {
      "consistency": {
        "value": 66,
        "percentile": 72,
        "variables": {
          "brake_point_variance": 68,
          "lap_time_consistency": 71,
          "steering_smoothness": 65,
          "throttle_application": 69,
          "racing_line_deviation": 64
        }
      },
      "racecraft": {
        "value": 53,
        "percentile": 45,
        "variables": {
          "overtaking_success": 48,
          "defensive_success": 51,
          "traffic_navigation": 55,
          "first_lap_gain": 52,
          "wheel_to_wheel": 49
        }
      },
      // ... other factors
    },
    "tracks": {
      "Barber": {
        "consistency": { "value": 68, "percentile": 75 },
        // ... track-specific factors
      }
    }
  }
}
```

---

## Section 4: Areas to Improve (Innovation Section)

### Layout
```
┌─────────────────────────────────────────────────────────┐
│  SKILL REALLOCATION SIMULATOR            [Reset All]    │
├─────────────────────────────────────────────────────────┤
│                                                          │
│  ADJUST YOUR SKILLS (5% Total to Allocate)             │
│                                                          │
│  Consistency      [████████░░] 66 → 68 (+2%)           │
│  Racecraft        [█████░░░░░] 53 → 56 (+3%)           │
│  Raw Speed        [████████░░] 67 → 67 (0%)            │
│  Tire Management  [█████░░░░░] 54 → 54 (0%)            │
│                                                          │
│  Points Remaining: 0%                    [SIMULATE →]   │
│                                                          │
│  ─────────────────────────────────────────────────────  │
│                                                          │
│  SIMULATION RESULTS                                     │
│                                                          │
│  Your new profile most closely matches:                 │
│  🏁 Driver #7 (92% similarity)                         │
│                                                          │
│  PROJECTED 2025 SEASON RESULTS:                        │
│  ┌──────────────────┬──────────────────┐              │
│  │                  │ Current │ Simulated│              │
│  ├──────────────────┼─────────┼──────────┤              │
│  │ Championship Pos │  P8     │  P5      │              │
│  │ Avg Finish       │  6.4    │  5.1     │              │
│  │ Wins             │  2      │  3       │              │
│  │ Podiums          │  5      │  7       │              │
│  │ Points           │  287    │  342     │              │
│  └──────────────────┴─────────┴──────────┘              │
│                                                          │
│  AI COACHING SUMMARY:                                   │
│  ┌──────────────────────────────────────────────────┐  │
│  │ "By improving your racecraft by 3%, you would    │  │
│  │ gain an average of 1.3 positions per race in     │  │
│  │ wheel-to-wheel battles. Focus your winter        │  │
│  │ training on:                                      │  │
│  │                                                    │  │
│  │ 1. Late braking exercises (confidence building)  │  │
│  │ 2. Side-by-side practice sessions                │  │
│  │ 3. First lap aggression drills                   │  │
│  │                                                    │  │
│  │ This improvement path matches Driver #7's        │  │
│  │ progression from 2024 to 2025."                  │  │
│  └──────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────┘
```

### Component Implementation
```tsx
// components/improve/SkillSliders.tsx
export function SkillSliders({ currentFactors, onUpdate }) {
  const [adjustments, setAdjustments] = useState({
    consistency: 0,
    racecraft: 0,
    rawSpeed: 0,
    tireMgmt: 0
  });
  
  const totalUsed = Object.values(adjustments).reduce((a,b) => a+b, 0);
  const remaining = 5 - totalUsed;
  
  return (
    <div className="space-y-4">
      {Object.entries(currentFactors).map(([key, value]) => (
        <div key={key} className="space-y-2">
          <div className="flex justify-between">
            <span className="text-sm uppercase">{key}</span>
            <span className="text-sm">
              {value} → {value + adjustments[key]} 
              ({adjustments[key] > 0 ? '+' : ''}{adjustments[key]}%)
            </span>
          </div>
          <Slider
            value={[value + adjustments[key]]}
            onValueChange={(val) => updateAdjustment(key, val[0] - value)}
            max={100}
            min={0}
            step={1}
            disabled={remaining <= 0 && adjustments[key] <= 0}
            className="skill-slider"
          />
        </div>
      ))}
      
      <div className="flex justify-between items-center mt-6">
        <span className="text-lg">Points Remaining: {remaining}%</span>
        <Button 
          onClick={() => onUpdate(adjustments)}
          disabled={remaining !== 0}
          className="bg-primary hover:bg-primary-dark"
        >
          SIMULATE →
        </Button>
      </div>
    </div>
  );
}

// lib/simulator.ts
export function simulateReallocation(
  driverId: string,
  adjustments: FactorAdjustments
) {
  // Calculate new factor scores
  const newFactors = applyAdjustments(currentFactors, adjustments);
  
  // Find most similar driver
  const similarDriver = findMostSimilarDriver(newFactors, allDrivers);
  
  // Project results based on similar driver's performance
  const projectedResults = projectSeasonResults(
    similarDriver.results,
    newFactors,
    similarDriver.factors
  );
  
  // Generate AI coaching summary
  const coachingSummary = generateCoachingSummary(
    currentFactors,
    newFactors,
    projectedResults
  );
  
  return {
    newFactors,
    similarDriver,
    projectedResults,
    coachingSummary
  };
}

// AI Coaching Summary Generation
async function generateCoachingSummary(current, target, results) {
  const prompt = `
    Driver currently has factors: ${JSON.stringify(current)}
    They want to improve to: ${JSON.stringify(target)}
    This would result in: ${JSON.stringify(results)}
    
    Provide 3 specific training recommendations for the off-season
    that would help achieve these improvements. Be specific about
    exercises and drills. Keep it under 100 words.
  `;
  
  const response = await openai.complete(prompt);
  return response.text;
}
```

---

## Navigation & Layout Components

### Main Navigation
```tsx
// components/layout/Navigation.tsx
export function Navigation() {
  const router = useRouter();
  const { driverId, setDriverId } = useDriverContext();
  
  const tabs = [
    { id: 'overview', label: 'Overview', icon: '📊' },
    { id: 'race-log', label: 'Race Log', icon: '🏁' },
    { id: 'skills', label: 'Skills', icon: '💪' },
    { id: 'improve', label: 'Improve', icon: '📈' }
  ];
  
  return (
    <nav className="bg-bg-secondary border-b border-border">
      <div className="max-w-7xl mx-auto px-4">
        <div className="flex justify-between items-center h-16">
          <div className="flex items-center space-x-8">
            <h1 className="text-xl font-bold text-primary">
              CIRCUIT FIT ANALYTICS
            </h1>
            <div className="flex space-x-1">
              {tabs.map(tab => (
                <TabButton
                  key={tab.id}
                  active={router.pathname.includes(tab.id)}
                  onClick={() => router.push(`/${tab.id}`)}
                >
                  {tab.icon} {tab.label}
                </TabButton>
              ))}
            </div>
          </div>
          <DriverSelector 
            value={driverId}
            onChange={setDriverId}
          />
        </div>
      </div>
    </nav>
  );
}
```

### Driver Selector
```tsx
// components/layout/DriverSelector.tsx
export function DriverSelector({ value, onChange }) {
  const drivers = useDrivers();
  
  return (
    <Select value={value} onValueChange={onChange}>
      <SelectTrigger className="w-[200px]">
        <SelectValue>
          #{drivers[value]?.number} - {drivers[value]?.name}
        </SelectValue>
      </SelectTrigger>
      <SelectContent>
        {Object.entries(drivers).map(([id, driver]) => (
          <SelectItem key={id} value={id}>
            <div className="flex items-center gap-2">
              <span className="font-mono">#{driver.number}</span>
              <span>{driver.name}</span>
              <PercentileBadge value={driver.circuitFitScore} />
            </div>
          </SelectItem>
        ))}
      </SelectContent>
    </Select>
  );
}
```

---

## Shared Components

### Stat Card (PFF Style)
```tsx
// components/shared/StatCard.tsx
interface StatCardProps {
  label: string;
  value: number | string;
  percentile?: number;
  visual?: ReactNode;
  trend?: 'up' | 'down' | 'neutral';
}

export function StatCard({ label, value, percentile, visual, trend }) {
  return (
    <div className="bg-bg-secondary rounded-lg p-6 border border-border hover:border-border-light transition-all">
      <div className="text-text-secondary text-xs uppercase tracking-wider mb-2">
        {label}
      </div>
      <div className="flex items-end justify-between">
        <div>
          <div className="text-4xl font-bold text-text-primary">
            {value}
          </div>
          {percentile && (
            <PercentileBadge value={percentile} className="mt-2" />
          )}
        </div>
        {visual && <div className="ml-4">{visual}</div>}
      </div>
      {trend && <TrendIndicator direction={trend} />}
    </div>
  );
}
```

### Percentile Badge (Color Coded)
```tsx
// components/shared/PercentileBadge.tsx
export function PercentileBadge({ value }: { value: number }) {
  const getColor = (percentile: number) => {
    if (percentile >= 90) return 'bg-stat-elite';
    if (percentile >= 70) return 'bg-stat-great';
    if (percentile >= 50) return 'bg-stat-good';
    if (percentile >= 30) return 'bg-stat-average';
    return 'bg-stat-poor';
  };
  
  const getLabel = (percentile: number) => {
    if (percentile >= 90) return 'ELITE';
    if (percentile >= 70) return 'GREAT';
    if (percentile >= 50) return 'GOOD';
    if (percentile >= 30) return 'AVG';
    return 'POOR';
  };
  
  return (
    <span className={`
      inline-flex items-center px-2 py-1 rounded text-xs font-bold
      ${getColor(value)} text-bg-primary
    `}>
      {getLabel(value)} ({value}%)
    </span>
  );
}
```

---

## Demo Flow (3-Minute Video)

### 0:00-0:30 - Hook & Overview
- Open on Overview page
- "Every driver gets the same car, but not the same results"
- Show season stats, highlight wins/podiums
- Quick scroll through performance trend

### 0:30-1:00 - Race Log
- Switch to Race Log tab
- "Track-by-track breakdown shows patterns"
- Highlight position gains
- Show sorting by different columns

### 1:00-1:30 - Skills Analysis
- Navigate to Skills tab
- "Our algorithm found 4 key factors"
- Expand Consistency to show variables
- Compare two drivers on spider chart

### 1:30-2:30 - Skill Reallocation (THE INNOVATION)
- Move to Improve tab
- "What if you could reallocate your training?"
- Adjust sliders: +3% Racecraft, +2% Consistency
- Hit SIMULATE
- "You'd match Driver #7's profile..."
- Show projected improvements: "3 more podiums, P5 in championship"
- Read AI coaching summary

### 2:30-3:00 - Impact & Close
- "Same car. Smarter training. Better results."
- Quick montage of all 4 sections
- "Circuit Fit Analytics - Your path to the podium"

---

## Implementation Timeline

### Phase 1: Setup & Data (Hours 0-4)
- [ ] Initialize Next.js project with TypeScript
- [ ] Set up Tailwind with PFF color scheme
- [ ] Process provisional results into JSON
- [ ] Create data structures
- [ ] Set up Zustand store

### Phase 2: Core Components (Hours 4-12)
- [ ] Build Navigation and DriverSelector
- [ ] Create Overview section with stats
- [ ] Implement Race Log table
- [ ] Design shared components

### Phase 3: Skills Section (Hours 12-18)
- [ ] Factor cards with percentiles
- [ ] Spider chart with D3/Recharts
- [ ] Variable breakdown accordion
- [ ] Track-specific filtering

### Phase 4: Improve Section (Hours 18-26)
- [ ] Skill adjustment sliders
- [ ] Simulation algorithm
- [ ] Results comparison table
- [ ] AI coaching integration

### Phase 5: Polish (Hours 26-32)
- [ ] Animations and transitions
- [ ] Loading states
- [ ] Responsive design
- [ ] Data validation

### Phase 6: Demo (Hours 32-36)
- [ ] Record video
- [ ] Deploy to Vercel
- [ ] Submit to DevPost
- [ ] Buffer time

---

## Key Features That Win

1. **Professional Design** - Looks like PFF/StatMuse, not a hackathon project
2. **Complete Data Story** - From season overview to granular improvements
3. **Novel Innovation** - Skill reallocation simulator is unique
4. **Clear Value** - Shows exactly how to improve with projected results
5. **Actionable Insights** - AI coaching gives specific training plans

---

## Deployment

```bash
# Development
npm install
npm run dev

# Production Build
npm run build
npm run start

# Deploy to Vercel
vercel --prod
```

---

## Critical Success Factors

### DO:
- Make it visually stunning (PFF-quality)
- Focus on the Improve section as innovation
- Use real data from provisional results
- Keep navigation simple and intuitive
- Show clear cause-and-effect in simulator

### DON'T:
- Add features beyond these 4 sections
- Make it look like a typical hackathon project
- Forget mobile responsiveness
- Skip the AI coaching summary
- Submit without testing all interactions

---

## Winning Pitch

"We built the PFF of racing - a professional analytics dashboard that not only shows your performance but tells you exactly how to improve. Our skill reallocation simulator lets drivers experiment with different training focuses and see projected results. It's not just data - it's your personalized path to the podium."

**Remember: Polish wins hackathons. Make this look like a $100K product, not a weekend project.**
