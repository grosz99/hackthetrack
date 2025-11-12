# Product Requirements Document (PRD)
## Racing Driver Training & Insights Dashboard - Final Week Sprint

**Launch Target:** 1 Week (November 19, 2025)
**Product Vision:** Professional analytics dashboard that helps drivers understand their performance through a validated 4-factor predictive model and provides data-driven insights for continuous improvement.

**Status:** 85% Launch Ready - Minor Polish Needed

---

## Executive Summary

### What's Working Excellently

**Technical Foundation:**
- Solid React 19 + FastAPI architecture with 100% backend test pass rate
- Fast performance (in-memory JSON, instant API responses)
- Validated 4-factor model (R² = 0.895, MAE = 1.78 positions)
- Mobile-first responsive design with proper breakpoints
- NASCAR-inspired dark theme with Toyota Racing Red branding

**User Experience:**
- 4 fully functional pages (Rankings, Overview, Race Log, Skills, Improve)
- Rich data visualizations (radar charts, line charts, percentile bars)
- Smooth animations and transitions (Framer Motion)
- Clear information hierarchy and navigation

**Data Quality:**
- 34 drivers across 12 races (291 observations)
- Comprehensive race-by-race results and sector analysis
- AI-generated coaching insights (Anthropic Claude integration)

### Critical Items Completed

**COMPLETED: White-on-White Text Fix**
- Issue: Driver names displayed white text on white background during page transitions
- Root Cause: App.jsx used bg-bg-primary which mapped to white (#ffffff) in Tailwind config
- Resolution:
  - Changed App.jsx background to dark (#0a0a0a)
  - Updated Tailwind color system for dark theme consistency
  - Updated bg-primary: #ffffff to #0a0a0a
  - Updated text-primary: #1d1d1f to #ffffff
  - Updated all border colors for dark theme
- Status: FIXED and committed

### Critical Gaps for Launch Week

**Priority 1 - Must Fix (2-3 days):**
1. Decide on 3 unused pages (TrackIntelligence, StrategyChat, TelemetryComparison) - Wire up or remove
2. Mobile rankings table - Hide columns on small screens
3. Track selection integration - Add to Improve page for driver comparison
4. Dynamic logic enhancements - Handle edge cases (best driver, no improvement needed)
5. Professional performance indicators - Add benchmark comparisons and development targets

**Priority 2 - Nice to Have (1 day):**
1. Styling consistency cleanup (refactor inline styles)
2. React error boundaries
3. Color scheme audit for Skills/Improve sections

**Priority 3 - Post-Launch:**
1. Advanced telemetry comparison features
2. Performance optimization (code splitting)
3. Historical performance tracking

---

## Part 1: Technical Architecture Review

### 1.1 Backend Architecture Assessment - STABLE

**Verdict:** Backend is production-ready with NO critical issues.

**Strengths:**
- API Design: FastAPI with Pydantic v2 models (type-safe contracts)
- Performance: In-memory JSON data (826KB total, instant responses)
- Error Handling: Custom error classes with sanitized responses
- Test Coverage: 22/22 tests passing (100%)
- Endpoints: 22+ well-documented API routes

**Data Flow Verification:**
```
Rankings Page → GET /api/drivers (all 34 drivers)
  ↓
Driver Selection → GET /api/drivers/{number} (specific driver detail)
  ↓
Overview Page → GET /api/drivers/{number}/stats (season statistics)
  ↓
Race Log Page → GET /api/drivers/{number}/results (race-by-race)
  ↓
Skills Page → GET /api/factors/{factor}/breakdown/{number} (factor variables)
             → GET /api/factors/{factor}/comparison/{number} (vs top 3)
  ↓
Improve Page → GET /api/drivers/{number}/telemetry-coaching (AI insights)
```

**Data Consistency Check: PASSED**
- All pages use centralized DriverContext for state management
- API responses cached in React Context (no duplicate fetches)
- LocalStorage used for selected driver persistence
- No race conditions or stale data issues found

**Minor Recommendations (Non-Blocking):**
1. Add rate limiting for production (current: none)
2. Consider Redis cache for AI coaching endpoints (current: file-based)
3. Add monitoring/logging middleware (Sentry or similar)

---

### 1.2 Responsive Design Issues - NEEDS ATTENTION

**Issue Confirmed:** "Shows up huge on laptops"

**Root Cause Analysis:**

**Problem Components:**

1. **Overview Page - Driver Number Badge**
   - File: /frontend/src/pages/Overview/Overview.jsx:161-180
   - Current: width: 180px, height: 180px, fontSize: 90px
   - Issue: Fixed pixel sizing doesn't scale with viewport
   - Fix: Use viewport-relative units or container queries

2. **Rankings Table - Horizontal Overflow**
   - File: /frontend/src/components/RankingsTable/RankingsTable.jsx
   - Current: 10 columns always visible
   - Issue: Forces horizontal scroll on mobile (<768px)
   - Fix: Hide less critical columns (DNF, Top 10, Poles) on mobile

3. **Skills Page - Factor Cards**
   - File: /frontend/src/pages/Skills/Skills.jsx
   - Current: 2x2 grid at 1400px+ breakpoint
   - Issue: Large gap between breakpoints causes awkward sizing
   - Fix: Add intermediate breakpoint at 1200px

**Specific Action Items:**

```javascript
// ACTION 1: Overview.jsx - Make driver badge responsive
// BEFORE (line 161-180)
const badgeStyle = {
  width: '180px',
  height: '180px',
  fontSize: '90px'
};

// AFTER - Use clamp() for fluid scaling
const badgeStyle = {
  width: 'clamp(120px, 15vw, 180px)',
  height: 'clamp(120px, 15vw, 180px)',
  fontSize: 'clamp(60px, 8vw, 90px)'
};
```

```css
/* ACTION 2: RankingsTable.css - Add responsive column hiding */
@media (max-width: 768px) {
  .rankings-table th:nth-child(n+7),
  .rankings-table td:nth-child(n+7) {
    display: none; /* Hide DNF, Top 10, Poles */
  }
}
```

```css
/* ACTION 3: Skills.css - Add intermediate breakpoint */
@media (min-width: 1200px) and (max-width: 1399px) {
  .factor-cards-grid {
    grid-template-columns: repeat(2, 1fr);
    gap: 1.5rem;
  }
}
```

**Testing Checklist:**
- [ ] Test on mobile (375px iPhone)
- [ ] Test on tablet (768px iPad)
- [ ] Test on laptop (1366px, 1440px)
- [ ] Test on large desktop (1920px)

---

### 1.3 Color Consistency Analysis - MINOR ISSUES

**Toyota Racing Brand Colors: Properly Implemented**
- Primary Red: #e74c3c and #EB0A1E (consistent usage)
- Dark Background: #0a0a0a (NASCAR aesthetic)
- White Cards: #ffffff (clean, professional)

**Problem Areas Identified:**

**1. Skills Page - Inconsistent Factor Card Colors**
- File: /frontend/src/pages/Skills/Skills.css
- Issue: Each factor card has different border color (not just red)
- Current: Speed (red), Consistency (blue), Racecraft (green), Tire Mgmt (orange)
- Recommendation: Use Toyota Red for all borders, differentiate with icons instead

**2. Improve Page - Random Accent Colors**
- File: /frontend/src/pages/Improve/Improve.css
- Issue: Green (#27ae60) used for similar drivers, yellow (#ffc107) for coaching
- Recommendation: Establish secondary color palette (1 accent max)

**3. Percentile Badges - Too Many Colors**
- File: /frontend/src/components/shared/PercentileBadge.jsx
- Current: 5 colors (Elite=Orange, Great=Green, Good=Blue, Average=Pink, Poor=Red)
- Recommendation: Simplify to 3 colors (Red scale: Light/Medium/Dark)

**Proposed Color System:**

```javascript
// /frontend/src/styles/colorSystem.js
export const TOYOTA_RACING_COLORS = {
  // Primary (Use 90% of the time)
  primary: {
    red: '#EB0A1E',        // Toyota Racing Red
    dark: '#0a0a0a',       // Background
    white: '#ffffff',      // Cards/text
  },

  // Functional (Use for specific meanings only)
  functional: {
    success: '#27ae60',    // Green for improvements
    warning: '#f39c12',    // Orange for caution
    error: '#e74c3c',      // Red for problems
    info: '#3498db',       // Blue for informational
  },

  // Grays (Use for secondary elements)
  neutral: {
    gray900: '#1a1a1a',
    gray700: '#4a4a4a',
    gray500: '#888888',
    gray300: '#cccccc',
    gray100: '#f5f5f5',
  },

  // Percentile Performance (Use ONLY for ranking badges)
  performance: {
    elite: '#EB0A1E',      // Top 25% - Toyota Red
    strong: '#ff4444',     // 25-50% - Light Red
    average: '#888888',    // 50-75% - Gray
    developing: '#cccccc', // Bottom 25% - Light Gray
  }
};
```

**Action Items:**
1. Create color system file (above)
2. Update Skills.css to use single border color
3. Update PercentileBadge.jsx to use 4-color system (from 5)
4. Audit Improve page for unnecessary color usage

---

### 1.4 Element Consistency & Alignment - NEEDS CLEANUP

**Issues Found:**

**1. Mixed Styling Approaches (Maintenance Burden)**
- Problem: 3 different CSS patterns used across codebase
  - Tailwind utility classes (Rankings.jsx)
  - CSS modules (RaceLog.css, Skills.css)
  - Inline styles (Overview.jsx lines 161-536)
- Impact: Hard to maintain, inconsistent spacing/sizing
- Recommendation: Standardize on Tailwind + minimal CSS modules

**2. Font Usage Inconsistencies**
- Problem: Mixing rem, px, and em units
  - Overview page: fontSize: '90px' (pixels)
  - Skills page: font-size: 1.5rem (rem)
  - Rankings table: font-size: 14px (pixels)
- Recommendation: Use Tailwind's rem-based scale exclusively

**3. Spacing Inconsistencies**
- Problem: Gaps/padding vary widely
  - Some cards use padding: 24px
  - Others use p-6 (Tailwind = 24px)
  - Some use p-8 (32px)
- Recommendation: Create design system tokens

**Proposed Design System:**

```javascript
// /frontend/config/tailwind.config.js - ADD CUSTOM TOKENS
module.exports = {
  theme: {
    extend: {
      spacing: {
        'card-sm': '16px',    // Small cards
        'card-md': '24px',    // Standard cards (USE THIS 90% OF TIME)
        'card-lg': '32px',    // Large feature cards
        'section': '48px',    // Between sections
      },
      fontSize: {
        'display-xl': '64px', // Driver name
        'display-lg': '48px', // Page titles
        'heading-xl': '32px', // Section headers
        'heading-lg': '24px', // Card titles
        'heading-md': '20px', // Subsection titles
        'body-lg': '16px',    // Standard body (USE THIS DEFAULT)
        'body-md': '14px',    // Secondary text
        'body-sm': '12px',    // Labels
        'label': '11px',      // Uppercase labels
      },
      borderRadius: {
        'card': '12px',       // Standard cards (USE THIS DEFAULT)
        'badge': '8px',       // Small badges
        'button': '8px',      // Buttons
      },
      borderWidth: {
        'card': '3px',        // Standard card borders
        'emphasis': '4px',    // Important cards
      }
    }
  }
};
```

**Alignment Issues:**

File: /frontend/src/pages/Overview/Overview.jsx
- Lines 250-280: Race results chart not vertically centered with factor cards
- Fix: Add display: flex; align-items: center to container

File: /frontend/src/pages/Skills/Skills.jsx
- Lines 120-150: Factor breakdown modal doesn't center properly on mobile
- Fix: Use Tailwind items-center justify-center on modal wrapper

---

## Part 2: Feature Enhancements

### 2.1 Track Selection Integration - HIGH PRIORITY

**Current State:** Track selection exists in codebase but NOT wired into main routing.

**Files Affected:**
- Backend: /backend/data/dashboardData.json (6 tracks defined)
- Backend: API supports GET /api/drivers?track_id=barber (circuit fit calculation)
- Frontend: /frontend/src/pages/TrackIntelligence/TrackIntelligence.jsx (built but not in routing)
- Frontend: No track selector in Improve page

**User Requirement:**
"Integrate track selection in Improve section. In performance analysis, you should be able to click driver to compare to, the track and skill so that you can see how you gauge against that driver to improve performance"

**Implementation Plan:**

**Step 1: Add Track Selector to Improve Page** (4 hours)

```javascript
// /frontend/src/pages/Improve/components/TrackSelector.jsx
import React from 'react';

const TRACKS = [
  { id: 'barber', name: 'Barber Motorsports Park', location: 'Alabama' },
  { id: 'cota', name: 'Circuit of the Americas', location: 'Texas' },
  { id: 'roadamerica', name: 'Road America', location: 'Wisconsin' },
  { id: 'sebring', name: 'Sebring International', location: 'Florida' },
  { id: 'sonoma', name: 'Sonoma Raceway', location: 'California' },
  { id: 'vir', name: 'Virginia International Raceway', location: 'Virginia' }
];

export const TrackSelector = ({ selectedTrack, onTrackChange }) => {
  return (
    <div className="track-selector">
      <label className="text-sm uppercase tracking-wide text-gray-400">
        Select Track
      </label>
      <select
        value={selectedTrack}
        onChange={(e) => onTrackChange(e.target.value)}
        className="w-full p-3 bg-gray-900 border-2 border-primary rounded-lg text-white"
      >
        <option value="">All Tracks (Overall Performance)</option>
        {TRACKS.map(track => (
          <option key={track.id} value={track.id}>
            {track.name} - {track.location}
          </option>
        ))}
      </select>
    </div>
  );
};
```

**Step 2: Update Improve Page to Use Track Context** (3 hours)

```javascript
// /frontend/src/pages/Improve/Improve.jsx - ADD NEAR LINE 30
const [selectedTrack, setSelectedTrack] = useState('');
const [selectedDriverToCompare, setSelectedDriverToCompare] = useState(null);
const [selectedSkill, setSelectedSkill] = useState('speed');

// Fetch track-specific data when track changes
useEffect(() => {
  if (selectedTrack) {
    const url = `/api/drivers/${driverNumber}?track_id=${selectedTrack}`;
    fetch(url)
      .then(res => res.json())
      .then(data => {
        // Update factor scores with track-specific circuit fit
        setTrackSpecificFactors(data.factors);
      });
  }
}, [selectedTrack, driverNumber]);
```

**Step 3: Create Driver Comparison Component** (4 hours)

```javascript
// /frontend/src/pages/Improve/components/DriverComparison.jsx
export const DriverComparison = ({
  currentDriver,
  compareDriver,
  selectedSkill,
  selectedTrack
}) => {
  // Fetch comparison data
  const comparison = useMemo(() => {
    const currentSkillValue = currentDriver.factors[selectedSkill];
    const compareSkillValue = compareDriver.factors[selectedSkill];
    const gap = compareSkillValue - currentSkillValue;

    return {
      current: currentSkillValue,
      target: compareSkillValue,
      gap: gap,
      percentageGap: ((gap / currentSkillValue) * 100).toFixed(1),
      isAhead: gap < 0
    };
  }, [currentDriver, compareDriver, selectedSkill]);

  return (
    <div className="driver-comparison-card">
      <h3>How do you compare to {compareDriver.name}?</h3>

      {/* Skill-specific comparison */}
      <div className="skill-comparison">
        <div className="driver-bar">
          <span>{currentDriver.name}</span>
          <div className="bar" style={{ width: `${comparison.current}%` }} />
          <span>{comparison.current}</span>
        </div>

        <div className="driver-bar">
          <span>{compareDriver.name}</span>
          <div className="bar" style={{ width: `${comparison.target}%` }} />
          <span>{comparison.target}</span>
        </div>
      </div>

      {/* Gap analysis */}
      <div className={`gap-indicator ${comparison.isAhead ? 'ahead' : 'behind'}`}>
        {comparison.isAhead ? (
          <span>You are {Math.abs(comparison.gap)} points ahead</span>
        ) : (
          <span>Close the gap: {comparison.gap} points to match</span>
        )}
      </div>

      {/* Track-specific insights */}
      {selectedTrack && (
        <div className="track-insights">
          <p>
            At {TRACK_NAMES[selectedTrack]}, {compareDriver.name} excels in{' '}
            {selectedSkill} due to their strengths in:
          </p>
          <ul>
            {/* List top 3 variables where compareDriver is stronger */}
          </ul>
        </div>
      )}
    </div>
  );
};
```

**Step 4: Wire Up Track Intelligence Page to Routing** (1 hour)

```javascript
// /frontend/src/App.jsx - ADD TO ROUTES (around line 25)
import TrackIntelligence from './pages/TrackIntelligence/TrackIntelligence';

// Inside <Routes>
<Route path="/track-intelligence" element={<TrackIntelligence />} />
```

**Step 5: Add Navigation Button** (30 minutes)

```javascript
// /frontend/src/components/DashboardHeader/DashboardHeader.jsx
<button
  onClick={() => navigate('/track-intelligence')}
  className="track-intel-button"
>
  Track Intelligence
</button>
```

**Acceptance Criteria:**
- [ ] Track selector dropdown appears on Improve page
- [ ] Selecting a track updates factor scores with circuit fit calculation
- [ ] Driver comparison shows track-specific insights
- [ ] Skill selector (Speed/Consistency/Racecraft/Tire Mgmt) filters comparison view
- [ ] "No comparison available" message when driver is best in that skill

**Time Estimate:** 12 hours (1.5 days)

---

### 2.2 Dynamic Logic Enhancements - HIGH PRIORITY

**User Requirement:**
"Ensure our logic is thoughtful and dynamic. For instance if a driver is the best call that out just don't leave nothing to improve."

**Current Issues:**

**1. Best-in-Class Driver Handling**
- File: /frontend/src/pages/Improve/Improve.jsx
- Issue: If driver is #1 in a skill, "Find Similar Drivers" returns no results
- Fix: Add conditional messaging for top performers

**2. Ranking Normalization**
- Issue: Raw percentiles (0-100) not intuitive for drivers
- Fix: Convert to performance tiers or letter grades

**3. Missing Context for Percentile Scores**
- Issue: "75th percentile in Speed" doesn't tell driver what that means
- Fix: Add contextual explanations

**Implementation:**

**Enhancement 1: Best Driver Messaging**

```javascript
// /frontend/src/pages/Improve/Improve.jsx - ADD AFTER LINE 100
const checkIfBestInSkill = (driverNumber, skill) => {
  const allDrivers = drivers; // from DriverContext
  const driverScore = currentDriver.factors[skill];

  const topDriver = allDrivers.reduce((best, current) => {
    return current.factors[skill] > best.factors[skill] ? current : best;
  }, allDrivers[0]);

  return topDriver.number === driverNumber;
};

const renderImprovementInsights = () => {
  const speedIsBest = checkIfBestInSkill(driverNumber, 'speed');
  const consistencyIsBest = checkIfBestInSkill(driverNumber, 'consistency');

  if (speedIsBest && consistencyIsBest) {
    return (
      <div className="best-driver-card">
        <div className="trophy-icon">LEADER</div>
        <h2>Top Performer</h2>
        <p>
          You are ranked first in both Speed and Consistency. Your focus should be on:
        </p>
        <ul>
          <li>Maintaining your performance edge (consistency is key)</li>
          <li>Developing areas outside your strengths (Racecraft, Tire Mgmt)</li>
          <li>Setting benchmark times for teammates</li>
        </ul>
      </div>
    );
  }

  if (speedIsBest) {
    return (
      <div className="skill-leader-card">
        <div className="medal-icon">FASTEST</div>
        <h3>Speed Leader</h3>
        <p>
          You are the fastest driver in the field. To win races, focus on:
        </p>
        <ul>
          <li>Converting speed into results (improve Racecraft)</li>
          <li>Maintaining pace over race distance (Tire Management)</li>
        </ul>
      </div>
    );
  }

  // Default improvement suggestions for non-leaders
  return <SimilarDriversComponent />;
};
```

**Enhancement 2: Performance Tier System**

```javascript
// /frontend/src/utils/performanceTiers.js
export const percentileToTier = (percentile) => {
  if (percentile >= 90) return { tier: 'ELITE', label: 'Top 10%', color: '#EB0A1E' };
  if (percentile >= 75) return { tier: 'STRONG', label: 'Top 25%', color: '#ff4444' };
  if (percentile >= 50) return { tier: 'COMPETITIVE', label: 'Top 50%', color: '#888888' };
  return { tier: 'DEVELOPING', label: 'Bottom 50%', color: '#cccccc' };
};

// Usage in Skills page
const { tier, label, color } = percentileToTier(driver.factors.speed);

<div className="tier-badge" style={{ backgroundColor: color }}>
  <span className="tier-name">{tier}</span>
  <span className="tier-label">{label}</span>
</div>
```

**Enhancement 3: Contextual Explanations**

```javascript
// /frontend/src/utils/explanations.js
export const getPercentileExplanation = (skill, percentile) => {
  const contexts = {
    speed: {
      90: "You are among the fastest 10% of drivers - elite qualifying pace",
      75: "You consistently qualify in the top half - strong one-lap speed",
      60: "Your qualifying is respectable but has room for improvement",
      40: "Focus on extracting more from qualifying laps - study fastest sectors",
      0: "Qualifying pace is a major area for development - consider setup changes"
    },
    consistency: {
      90: "You rarely make mistakes - rock-solid lap-to-lap consistency",
      75: "Your lap times are predictable - good foundation for race strategy",
      60: "Consistency is decent but occasional errors cost time",
      40: "Work on reducing lap time variation - focus on repeatable techniques",
      0: "High lap-to-lap variation - work with engineers on setup stability"
    },
    racecraft: {
      90: "You are a master of wheel-to-wheel racing - elite overtaking ability",
      75: "You make good decisions in traffic and gain positions",
      60: "Racecraft is solid but could be more aggressive on overtakes",
      40: "Work on race starts and defending position - study replays",
      0: "Racing in traffic needs development - consider simulator practice"
    },
    tire_management: {
      90: "You preserve tires excellently - huge advantage in long runs",
      75: "Your late-race pace is strong - good tire conservation",
      60: "Tire management is okay but could extend stint length",
      40: "Tires degrade faster than competitors - work on smooth inputs",
      0: "Tire wear is a critical issue - focus on driving style changes"
    }
  };

  // Find closest threshold
  const thresholds = [90, 75, 60, 40, 0];
  const closestThreshold = thresholds.find(t => percentile >= t);

  return contexts[skill][closestThreshold];
};
```

**Enhancement 4: Professional Progress Bars**

```javascript
// /frontend/src/components/shared/SkillProgressBar.jsx
export const SkillProgressBar = ({ skill, current, target, max = 100 }) => {
  const progress = (current / max) * 100;
  const targetProgress = (target / max) * 100;
  const gainAvailable = targetProgress - progress;

  return (
    <div className="skill-progress-bar">
      <div className="bar-container">
        {/* Current level (filled) */}
        <div
          className="bar-fill current"
          style={{ width: `${progress}%` }}
        >
          <span className="current-value">{current}</span>
        </div>

        {/* Potential gain (semi-transparent overlay) */}
        {target > current && (
          <div
            className="bar-fill potential"
            style={{
              width: `${targetProgress}%`,
              opacity: 0.3
            }}
          />
        )}

        {/* Target marker */}
        {target > current && (
          <div
            className="target-marker"
            style={{ left: `${targetProgress}%` }}
          >
            <span className="target-flag">TARGET {target}</span>
          </div>
        )}
      </div>

      {/* Gain indicator */}
      {gainAvailable > 0 && (
        <div className="gain-indicator">
          <span className="gain-text">+{gainAvailable.toFixed(1)} points available</span>
        </div>
      )}
    </div>
  );
};
```

**Acceptance Criteria:**
- [ ] Top-ranked drivers see "Top Performer" messaging
- [ ] Percentiles converted to performance tiers (ELITE/STRONG/COMPETITIVE/DEVELOPING)
- [ ] Each score has contextual explanation tooltip
- [ ] Progress bars show current level + potential gain
- [ ] No empty states or missing improvement suggestions

**Time Estimate:** 8 hours (1 day)

---

### 2.3 Professional Performance Indicators - MEDIUM PRIORITY

**User Requirement:**
"We want this to be professional for adult drivers - not gimmicky like a video game"

**Current State:**
- Classification badges (Frontrunner/Contender/Mid-Pack/Development)
- Percentile badges (Elite/Great/Good/Average/Poor)
- Rank badges (Gold/Silver/Bronze for top 3)
- NO benchmark comparison system
- NO development target tracking
- NO historical performance trends

**Recommendation:** Focus on professional sports analytics approach (ESPN/F1 style)

**Phase 1: Launch Week Implementation** (9 hours)

**Feature 1: Benchmark Comparison Bars** (3 hours)

**Professional Approach:** Show driver's performance relative to field benchmarks

**Visual:** Horizontal bar charts with clear markers

```javascript
// /frontend/src/components/shared/BenchmarkBar.jsx
export const BenchmarkBar = ({ skill, driverScore, fieldAverage, topThreeAverage }) => {
  const max = 100;
  const driverPos = (driverScore / max) * 100;
  const avgPos = (fieldAverage / max) * 100;
  const topPos = (topThreeAverage / max) * 100;

  return (
    <div className="benchmark-bar-container">
      <div className="benchmark-labels">
        <span className="skill-name">{skill}</span>
        <span className="driver-score">{driverScore}</span>
      </div>

      <div className="benchmark-bar">
        {/* Progress fill */}
        <div
          className="bar-fill"
          style={{ width: `${driverPos}%` }}
        />

        {/* Markers */}
        <div className="marker driver" style={{ left: `${driverPos}%` }}>
          <span>YOU</span>
        </div>
        <div className="marker average" style={{ left: `${avgPos}%` }}>
          <span>AVG</span>
        </div>
        <div className="marker top" style={{ left: `${topPos}%` }}>
          <span>TOP 3</span>
        </div>
      </div>

      <div className="benchmark-stats">
        <span className="stat">
          {driverScore > fieldAverage
            ? `+${(driverScore - fieldAverage).toFixed(1)} above field average`
            : `${(driverScore - fieldAverage).toFixed(1)} below field average`
          }
        </span>
        <span className="stat">
          {driverScore > topThreeAverage
            ? `+${(driverScore - topThreeAverage).toFixed(1)} above top 3`
            : `${(topThreeAverage - driverScore).toFixed(1)} gap to top 3`
          }
        </span>
      </div>
    </div>
  );
};
```

**Where to Add:**
- Overview page: Below radar chart
- Skills page: On each factor card

**Feature 2: Development Target Cards** (4 hours)

**Professional Approach:** Clear, measurable goals based on data

```javascript
// /frontend/src/components/shared/DevelopmentTarget.jsx
export const DevelopmentTarget = ({ skill, current, targetTier, gap, actionItems }) => {
  const progress = ((current / (current + gap)) * 100).toFixed(0);

  return (
    <div className="development-target-card">
      <div className="target-header">
        <h3>DEVELOPMENT TARGET: {skill}</h3>
        <span className="target-tier">{targetTier}</span>
      </div>

      <div className="target-metrics">
        <div className="metric">
          <span className="metric-label">Current</span>
          <span className="metric-value">{current}</span>
        </div>
        <div className="metric">
          <span className="metric-label">Target</span>
          <span className="metric-value">{current + gap}</span>
        </div>
        <div className="metric">
          <span className="metric-label">Gap</span>
          <span className="metric-value">-{gap}</span>
        </div>
      </div>

      <div className="progress-bar">
        <div className="progress-fill" style={{ width: `${progress}%` }} />
        <span className="progress-label">{progress}%</span>
      </div>

      <div className="action-items">
        <h4>To Achieve:</h4>
        <ul>
          {actionItems.map((item, index) => (
            <li key={index}>{item}</li>
          ))}
        </ul>
      </div>
    </div>
  );
};
```

**Data Structure:**
```javascript
const developmentTargets = {
  speed: {
    current: 72.5,
    targetTier: 'STRONG (Top 25%)',
    targetScore: 80.0,
    gap: 7.5,
    actionItems: [
      'Improve Sector 1 speed by 0.3s',
      'Reduce qualifying variance by 15%',
      'Match top 3 in braking zones'
    ]
  }
};
```

**Where to Add:**
- Improve page: Primary focus area
- Skills page: Expandable section

**Feature 3: Refined Percentile Tier Badges** (2 hours)

**Professional Refinement:**

```javascript
// /frontend/src/components/shared/PerformanceTierBadge.jsx
export const PerformanceTierBadge = ({ percentile }) => {
  const getTier = (pct) => {
    if (pct >= 90) return { name: 'ELITE', label: 'Top 10%', color: '#EB0A1E' };
    if (pct >= 75) return { name: 'STRONG', label: 'Top 25%', color: '#ff4444' };
    if (pct >= 50) return { name: 'COMPETITIVE', label: 'Top 50%', color: '#888888' };
    return { name: 'DEVELOPING', label: 'Bottom 50%', color: '#cccccc' };
  };

  const tier = getTier(percentile);

  return (
    <div className="performance-tier-badge" style={{ borderColor: tier.color }}>
      <span className="tier-name" style={{ color: tier.color }}>
        {tier.name}
      </span>
      <span className="tier-percentile">{percentile.toFixed(1)}th</span>
      <span className="tier-label">{tier.label}</span>
    </div>
  );
};
```

**CSS Styling:**
```css
.performance-tier-badge {
  display: inline-flex;
  flex-direction: column;
  align-items: center;
  padding: 8px 16px;
  border: 2px solid;
  border-radius: 8px;
  background: rgba(255, 255, 255, 0.05);
  font-family: 'Inter', sans-serif;
}

.tier-name {
  font-size: 11px;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 1px;
}

.tier-percentile {
  font-size: 20px;
  font-weight: 800;
  color: #ffffff;
  margin: 4px 0;
}

.tier-label {
  font-size: 10px;
  font-weight: 500;
  color: #888888;
  text-transform: uppercase;
}
```

**Acceptance Criteria:**
- [ ] Benchmark bars display on Overview and Skills pages
- [ ] Development target cards show on Improve page
- [ ] Performance tier badges updated with professional styling
- [ ] All text uses professional language (no "Level up!" or similar)
- [ ] Clean, minimal design (no cartoon graphics)

**Time Estimate:** 9 hours

---

### 2.4 Highlight Differentiating Points - HIGH PRIORITY

**User Requirement:**
"Making sure that our two differentiating points are evident in the product. That is we've developed a fancy algorithm to determine/predict driver success and we've simplified it to a professional analytics experience."

**Current Issue:** These differentiators are NOT prominently featured.

**Solution: Add Explainer Sections**

**Location 1: Landing Page (Rankings) - Add Hero Section** (2 hours)

```javascript
// /frontend/src/pages/Rankings/Rankings.jsx - ADD BEFORE RANKINGS TABLE
export const Rankings = () => {
  return (
    <div className="rankings-page">
      {/* NEW: Hero Section */}
      <div className="hero-section">
        <h1 className="hero-title">
          The Future of Driver Training
        </h1>
        <p className="hero-subtitle">
          Powered by AI-driven analytics and validated predictive modeling
        </p>

        <div className="differentiators-grid">
          {/* Differentiator 1: Algorithm */}
          <div className="diff-card">
            <div className="diff-icon">ANALYTICS</div>
            <h3>Predictive 4-Factor Model</h3>
            <p>
              Our validated algorithm analyzes 291 driver-race observations to predict
              race finishes with 89.5% accuracy (R² = 0.895).
            </p>
            <div className="diff-stats">
              <div className="stat">
                <span className="stat-value">89.5%</span>
                <span className="stat-label">Accuracy</span>
              </div>
              <div className="stat">
                <span className="stat-value">1.78</span>
                <span className="stat-label">Avg Error (positions)</span>
              </div>
              <div className="stat">
                <span className="stat-value">4</span>
                <span className="stat-label">Performance Factors</span>
              </div>
            </div>
          </div>

          {/* Differentiator 2: Professional Analytics */}
          <div className="diff-card">
            <div className="diff-icon">INSIGHTS</div>
            <h3>Professional Analytics Experience</h3>
            <p>
              Complex telemetry simplified into intuitive benchmarks, percentile rankings,
              and visual progress indicators.
            </p>
            <div className="diff-features">
              <div className="feature">Performance tier system</div>
              <div className="feature">Benchmark comparisons</div>
              <div className="feature">Percentile rankings</div>
              <div className="feature">Development targets</div>
            </div>
          </div>
        </div>
      </div>

      {/* Existing Rankings Table */}
      <RankingsTable />
    </div>
  );
};
```

**Location 2: Skills Page - Add "How It Works" Modal** (3 hours)

```javascript
// /frontend/src/pages/Skills/components/AlgorithmExplainer.jsx
export const AlgorithmExplainer = ({ onClose }) => {
  return (
    <div className="modal-overlay" onClick={onClose}>
      <div className="algorithm-modal" onClick={(e) => e.stopPropagation()}>
        <button className="close-button" onClick={onClose}>Close</button>

        <h2>How Our 4-Factor Model Works</h2>

        {/* Step-by-step explanation */}
        <div className="explainer-steps">
          <div className="step">
            <div className="step-number">1</div>
            <div className="step-content">
              <h3>Data Collection</h3>
              <p>
                We analyze telemetry data from 291 driver-race observations across
                12 different tracks in the 2023 season.
              </p>
            </div>
          </div>

          <div className="step">
            <div className="step-number">2</div>
            <div className="step-content">
              <h3>Factor Extraction</h3>
              <p>
                Using statistical analysis (Exploratory Factor Analysis), we identified
                4 core factors that drive race performance:
              </p>
              <ul>
                <li><strong>Speed (46.6%)</strong> - Qualifying pace, sector times</li>
                <li><strong>Consistency (29.1%)</strong> - Lap-to-lap variation</li>
                <li><strong>Racecraft (14.9%)</strong> - Overtaking, race starts</li>
                <li><strong>Tire Management (9.5%)</strong> - Late-race pace</li>
              </ul>
            </div>
          </div>

          <div className="step">
            <div className="step-number">3</div>
            <div className="step-content">
              <h3>Weighted Scoring</h3>
              <p>
                Each factor is scored 0-100 (percentile), then combined using
                validated weights:
              </p>
              <div className="formula">
                Overall = (Speed × 0.466) + (Consistency × 0.291) +
                (Racecraft × 0.149) + (Tire Mgmt × 0.095)
              </div>
            </div>
          </div>

          <div className="step">
            <div className="step-number">4</div>
            <div className="step-content">
              <h3>Validation</h3>
              <p>
                Our model has been rigorously tested:
              </p>
              <div className="validation-metrics">
                <div className="metric">
                  <span className="metric-value">R² = 0.895</span>
                  <span className="metric-desc">Explains 89.5% of performance variance</span>
                </div>
                <div className="metric">
                  <span className="metric-value">MAE = 1.78</span>
                  <span className="metric-desc">Average error of 1.78 finishing positions</span>
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* Call to action */}
        <div className="explainer-cta">
          <p>
            This is not guesswork - it is data science. Every score you see is backed
            by real telemetry and validated against race results.
          </p>
        </div>
      </div>
    </div>
  );
};

// Add button to Skills page to trigger modal
<button
  className="algorithm-explainer-btn"
  onClick={() => setShowExplainer(true)}
>
  How Does This Work?
</button>
```

**Location 3: Overview Page - Add Stat Card** (1 hour)

```javascript
// /frontend/src/pages/Overview/Overview.jsx - ADD TO PERFORMANCE TILES
<div className="performance-tile algorithm-powered">
  <div className="tile-icon">AI</div>
  <div className="tile-label">Model Accuracy</div>
  <div className="tile-value">89.5%</div>
  <div className="tile-description">
    Predicted finish within 1.78 positions on average
  </div>
</div>
```

**Acceptance Criteria:**
- [ ] Hero section on Rankings page explains both differentiators
- [ ] "How It Works" button on Skills page opens algorithm explainer modal
- [ ] Overview page includes model accuracy stat card
- [ ] All mentions of algorithm include R² and MAE values
- [ ] Professional analytics features are visually prominent

**Time Estimate:** 6 hours

---

## Part 3: Priority Action Plan

### Week at a Glance (40 working hours)

**Monday (8 hours) - Critical Fixes**
- [ ] Decision: Unused pages (wire up TrackIntelligence or remove StrategyChat/TelemetryComparison) - 2 hours
- [ ] Fix mobile rankings table (hide columns on mobile) - 2 hours
- [ ] Add React error boundaries - 2 hours
- [ ] Create color system file and audit Skills/Improve pages - 2 hours

**Tuesday (8 hours) - Track Selection**
- [ ] Build TrackSelector component - 2 hours
- [ ] Update Improve page with track context - 2 hours
- [ ] Create DriverComparison component - 3 hours
- [ ] Wire TrackIntelligence page to routing - 1 hour

**Wednesday (8 hours) - Dynamic Logic**
- [ ] Implement best-in-class driver messaging - 2 hours
- [ ] Add performance tier system - 2 hours
- [ ] Create contextual explanation tooltips - 2 hours
- [ ] Build professional progress bars - 2 hours

**Thursday (8 hours) - Professional Performance Indicators**
- [ ] Build benchmark comparison bars - 3 hours
- [ ] Create development target cards - 4 hours
- [ ] Add refined performance tier badges - 1 hour

**Friday (8 hours) - Differentiators & Polish**
- [ ] Add hero section to Rankings page - 2 hours
- [ ] Create algorithm explainer modal for Skills page - 3 hours
- [ ] Add model accuracy stat to Overview page - 1 hour
- [ ] Final responsive design testing (all devices) - 2 hours

---

### Implementation Checklist

**Phase 1: Must-Fix for Launch (Priority 1)**
- [ ] Decide on unused pages (TrackIntelligence/StrategyChat/TelemetryComparison)
- [ ] Fix mobile rankings table column overflow
- [ ] Integrate track selection in Improve page
- [ ] Add dynamic logic for best-in-class drivers
- [ ] Implement professional performance indicators (benchmark bars, development targets)
- [ ] Add hero section highlighting differentiators
- [ ] Create algorithm explainer modal

**Phase 2: Nice-to-Have (Priority 2)**
- [ ] Refactor Overview.jsx inline styles to CSS modules
- [ ] Add React error boundaries to all pages
- [ ] Standardize color usage (audit Skills/Improve)
- [ ] Add intermediate responsive breakpoint (1200px)
- [ ] Create design system tokens in Tailwind config

**Phase 3: Post-Launch (Priority 3)**
- [ ] Historical performance tracking (trend charts)
- [ ] Full telemetry comparison feature
- [ ] AI strategy chat integration
- [ ] Code splitting and lazy loading
- [ ] Performance optimization (bundle size analysis)
- [ ] User analytics integration (Vercel Analytics)

---

## Part 4: Testing & QA Plan

### Testing Checklist

**Responsive Design Testing:**
- [ ] Mobile (375px) - iPhone SE
- [ ] Mobile (414px) - iPhone 14 Pro Max
- [ ] Tablet (768px) - iPad
- [ ] Tablet (1024px) - iPad Pro
- [ ] Laptop (1366px) - Standard laptop
- [ ] Laptop (1440px) - MacBook Pro
- [ ] Desktop (1920px) - Full HD monitor
- [ ] Large Desktop (2560px) - 4K monitor

**Browser Testing:**
- [ ] Chrome (latest)
- [ ] Safari (latest)
- [ ] Firefox (latest)
- [ ] Edge (latest)

**Functionality Testing:**
- [ ] Rankings table sorting (all columns)
- [ ] Driver selection (click row to navigate to Overview)
- [ ] Navigation tabs (Overview, Race Log, Skills, Improve)
- [ ] Skills page factor cards (click to expand breakdown)
- [ ] Track selection dropdown (Improve page)
- [ ] Driver comparison (select driver to compare)
- [ ] Similar drivers algorithm (Find Similar Drivers button)
- [ ] Performance tier badge display
- [ ] Benchmark comparison bars

**Performance Testing:**
- [ ] Initial page load < 2 seconds
- [ ] API response times < 500ms
- [ ] Smooth animations (60fps)
- [ ] No layout shift (CLS < 0.1)
- [ ] Image optimization

**Accessibility Testing:**
- [ ] Keyboard navigation (tab through all interactive elements)
- [ ] Screen reader compatibility (NVDA/VoiceOver)
- [ ] Color contrast ratios (WCAG AA minimum 4.5:1)
- [ ] Focus indicators visible
- [ ] Alt text for all images

---

## Part 5: Launch Criteria

### Definition of Done

**Must Have (Blocking Launch):**
- All 4 main pages functional (Rankings, Overview, Skills, Improve)
- Track selection integrated in Improve page
- Dynamic logic handles edge cases (best driver, no improvement)
- Professional performance indicators visible (benchmark bars, development targets)
- Differentiators highlighted (algorithm stats + professional analytics UX)
- Mobile responsive (no horizontal scroll issues)
- No white-on-white text or contrast issues
- Toyota Racing brand colors consistent throughout
- All API endpoints return < 500ms
- 100% backend tests passing

**Should Have (Launch if time permits):**
- React error boundaries
- Refactored inline styles in Overview.jsx
- Color system standardization
- Algorithm explainer modal
- Design system tokens in Tailwind config

**Could Have (Post-launch):**
- Historical performance tracking
- Full telemetry comparison feature
- AI strategy chat
- Performance optimization (code splitting)

---

## Part 6: Post-Launch Roadmap

### Week 2 Priorities (Post-Launch Enhancements)

**1. Historical Performance Tracking (3 days)**
- Session-by-session improvement graphs
- 5-race moving averages
- Trend analysis (improving/declining/stable)
- Personal best lap time highlights

**2. Full Telemetry Integration (2 days)**
- Wire up TelemetryComparison page
- Add lap-by-lap speed trace visualization
- Corner-by-corner analysis comparison

**3. AI Strategy Chat (2 days)**
- Wire up StrategyChat page
- Add race strategy recommendations
- Integrate with Anthropic Claude API

**4. Performance Optimization (1 day)**
- Implement code splitting (React.lazy)
- Optimize bundle size (tree shaking)
- Add Vercel Analytics
- Lighthouse score > 90 on all metrics

**5. User Onboarding (1 day)**
- Add first-time user tour
- Tooltip explanations for key features
- "What's New" modal for returning users

---

## Part 7: Risk Mitigation

### Identified Risks & Mitigation Strategies

**Risk 1: Time Constraint (1 week is tight)**
- Mitigation: Strict prioritization (must-have vs nice-to-have)
- Action: Focus on Priority 1 items only, defer rest to post-launch

**Risk 2: Scope Creep During Implementation**
- Mitigation: Lock requirements now, no new features this week
- Action: Create "Future Enhancements" document for all new ideas

**Risk 3: Breaking Changes in Existing Features**
- Mitigation: Test thoroughly after each change
- Action: Use git branches, test before merging to main

**Risk 4: Mobile Responsiveness Issues**
- Mitigation: Test on real devices, not just browser DevTools
- Action: Get team members to test on their phones

**Risk 5: Performance Degradation with New Features**
- Mitigation: Monitor bundle size and API response times
- Action: Run Lighthouse audits before/after major changes

---

## Part 8: Success Metrics

### How We'll Measure Launch Success

**Technical Metrics:**
- [ ] Lighthouse Performance Score > 80
- [ ] 100% backend test pass rate maintained
- [ ] API P95 response time < 500ms
- [ ] Zero critical bugs reported in first 48 hours

**User Experience Metrics:**
- [ ] All 4 pages have <2% bounce rate
- [ ] Average session duration > 3 minutes
- [ ] Mobile users don't see horizontal scroll
- [ ] No user reports of white-on-white text

**Product Metrics:**
- [ ] All 34 drivers have accurate scores
- [ ] Track selection changes factor scores correctly
- [ ] Performance tier calculations are accurate for all drivers
- [ ] Benchmark comparisons show correct field averages

---

## Conclusion

Your Racing Driver Training Dashboard is **85% ready for launch**. The technical foundation is solid, the 4-factor model is validated, and the core features work well. This final week should focus on:

1. Polish the UX (track selection, dynamic logic, professional performance indicators)
2. Highlight your differentiators (algorithm + professional analytics experience)
3. Fix mobile responsiveness (rankings table, breakpoints)
4. Test thoroughly (all devices, browsers, edge cases)

With focused execution on the Priority 1 tasks, you will have a compelling product that drivers will use and that showcases your unique approach to driver development.

**Next Steps:**
1. Review this PRD with your team
2. Assign tasks for Monday-Friday
3. Set up daily check-ins to track progress
4. Launch on November 19th

---

**Document Version:** 2.0
**Last Updated:** November 12, 2025
**Owner:** Development Team
**Status:** Awaiting Team Review

**Changelog:**
- v2.0: Removed all decorative elements, updated with white-on-white fix, replaced gamification with professional performance indicators
- v1.0: Initial PRD with comprehensive code review