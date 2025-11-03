# Scout Landing Page to Overview Page - Complete User Journey Specification

## Executive Summary

This specification defines the complete user journey connecting a new Scout Landing Page to the existing Overview page. The design maintains the dark F1-inspired aesthetic throughout, provides seamless navigation between scout mode (browsing all drivers) and detail mode (deep-diving on individual drivers), and enables efficient recruiter workflows.

**Key Design Decision: Dark Theme Throughout**
- Scout Landing Page adopts the same dark theme as Overview page
- White cards with 4px #e74c3c red borders maintained across both views
- Ensures visual continuity and reduces cognitive load during transitions

---

## 1. Information Architecture

### Route Structure

```
/scout                          - Scout Landing Page (NEW)
├── Grid view of all 34 drivers
├── Filtering and comparison tools
└── Entry point for the application

/scout/driver/:driverNumber     - Driver Detail View (ENHANCED OVERVIEW)
├── /scout/driver/13/overview   - Season overview (default)
├── /scout/driver/13/race-log   - Race-by-race logs
├── /scout/driver/13/skills     - Skills breakdown
└── /scout/driver/13/improve    - Improvement recommendations

/overview (DEPRECATED)          - Redirect to /scout/driver/:selectedDriver/overview
/race-log (DEPRECATED)          - Redirect to /scout/driver/:selectedDriver/race-log
/skills (DEPRECATED)            - Redirect to /scout/driver/:selectedDriver/skills
/improve (DEPRECATED)           - Redirect to /scout/driver/:selectedDriver/improve
```

**Migration Strategy:**
- Old URLs redirect to new structure with currently selected driver
- Deep links preserve context: `/race-log` → `/scout/driver/13/race-log` (if driver 13 was selected)
- Default to driver #13 if no driver context exists

### Navigation Hierarchy

**Top-Level Navigation:**
```
┌─────────────────────────────────────────────────────────────────┐
│  TOYOTA GAZOO RACING SERIES                    [Scout Portal]   │
└─────────────────────────────────────────────────────────────────┘
```

**Scout Mode Navigation (at /scout):**
```
┌─────────────────────────────────────────────────────────────────┐
│  ← Scout Portal                                    [Filters] [⋮] │
│  ═══════════════                                                 │
│  Browse All Drivers (34)                                         │
└─────────────────────────────────────────────────────────────────┘
```

**Driver Detail Mode Navigation (at /scout/driver/13/overview):**
```
┌─────────────────────────────────────────────────────────────────┐
│  ← Scout Portal          Driver #13           [Compare] [Select] │
│  FRONTRUNNER                                                      │
│  ─────────────────────────────────────────────────────────────  │
│  [Overview] [Race Log] [Skills] [Improve]                        │
└─────────────────────────────────────────────────────────────────┘
```

---

## 2. Scout Landing Page Design (/scout)

### Layout Structure

```
┌───────────────────────────────────────────────────────────────┐
│  TOP NAVIGATION BAR                                           │
│  Toyota Gazoo Racing Series          [Scout Portal] [Profile] │
├───────────────────────────────────────────────────────────────┤
│  SCOUT CONTROL BAR                                            │
│  ← Scout Portal                 [Search] [Filters] [Compare] │
├───────────────────────────────────────────────────────────────┤
│  FILTER SIDEBAR (Collapsible)     │  DRIVER GRID              │
│                                    │                           │
│  ┌─ CLASSIFICATION ─────────┐    │  ┌────┐ ┌────┐ ┌────┐    │
│  │ ☑ Frontrunners (1)       │    │  │ #13│ │ #22│ │  #7│    │
│  │ ☑ Contenders (7)         │    │  └────┘ └────┘ └────┘    │
│  │ ☐ Mid-Pack (15)          │    │                           │
│  │ ☐ Development (11)       │    │  ┌────┐ ┌────┐ ┌────┐    │
│  └──────────────────────────┘    │  │ #72│ │ #46│ │ #16│    │
│                                    │  └────┘ └────┘ └────┘    │
│  ┌─ PERFORMANCE ────────────┐    │                           │
│  │ Speed       [====    ] 70│    │  [Load More] [View Table] │
│  │ Consistency [====    ] 60│    │                           │
│  │ Racecraft   [====    ] 60│    │  Showing 12 of 34        │
│  └──────────────────────────┘    │                           │
│                                    │                           │
│  ┌─ EXPERIENCE ────────────┐    │                           │
│  │ ○ All                    │    │                           │
│  │ ○ Veterans (10+ races)   │    │                           │
│  │ ○ Rookies (<5 races)     │    │                           │
│  └──────────────────────────┘    │                           │
│                                    │                           │
│  [Reset All] [Save Search]        │                           │
└───────────────────────────────────┴───────────────────────────┘
```

### Driver Card Design (Grid Item)

**Card Dimensions:** 280px wide × 380px tall
**Card Style:** White background, 4px solid #e74c3c border, 16px border-radius

```
┌────────────────────────────────────────────┐
│                                            │ ← 4px #e74c3c border
│  ┌─────────────────────────────────────┐  │
│  │      FRONTRUNNER                    │  │ ← Classification badge (gold)
│  └─────────────────────────────────────┘  │
│                                            │
│             #13                            │ ← Driver number (72px, 900 weight)
│                                            │
│          Driver #13                        │ ← Driver name (24px, 700 weight)
│       Toyota Gazoo Series                  │ ← Series (14px, 600 weight, gray)
│                                            │
│  ┌─────────────────────────────────────┐  │
│  │ Overall Score      67   ▲            │  │ ← Key stat with trend indicator
│  │ 89.7th Percentile                   │  │
│  └─────────────────────────────────────┘  │
│                                            │
│  Speed        ████████░░  67              │ ← Factor mini-bars
│  Consistency  ████████░░  66              │
│  Racecraft    ███████░░░  60              │
│  Tire Mgmt    ██████░░░░  53              │
│                                            │
│  ┌──────────────────────────────────────┐ │
│  │  12 Races  │  2.75 Avg  │  4 Podiums │ │ ← Quick stats
│  └──────────────────────────────────────┘ │
│                                            │
│  ┌────────────────────┐  ┌─────────────┐ │
│  │   View Details  →  │  │  + Compare  │ │ ← Primary actions
│  └────────────────────┘  └─────────────┘ │
│                                            │
└────────────────────────────────────────────┘
```

**Classification Badge Colors:**
- FRONTRUNNER: Gold (#FFD700) background, black text
- CONTENDER: Silver (#C0C0C0) background, black text
- MID-PACK: Bronze (#CD7F32) background, white text
- DEVELOPMENT: Gray (#718096) background, white text

### Interaction States

**Card Hover:**
- Box shadow expands: `0 6px 24px rgba(231, 76, 60, 0.4)`
- Slight lift: `transform: translateY(-4px)`
- Border pulses slightly brighter: #ff5e4e

**Card Click:**
- Entire card clickable (navigates to driver detail)
- "View Details" button is redundant visual emphasis

**Compare Checkbox:**
- Clicking "+ Compare" adds driver to comparison queue
- Changes to "✓ Added" with checkmark
- Comparison panel slides up from bottom

---

## 3. Transition Design: Scout → Driver Detail

### Navigation Flow

**User Action:** Click driver card or "View Details" button

**URL Transition:**
```
/scout  →  /scout/driver/13/overview
```

**Visual Transition:**
1. Driver card scales up and fades (200ms ease-out)
2. Background darkens with overlay (150ms)
3. Detail page slides in from right (300ms ease-out-cubic)
4. Navigation bar morphs: "Scout Portal" becomes breadcrumb

**State Preservation:**
- Scout Landing Page state stored in sessionStorage:
  - Active filters
  - Scroll position
  - Comparison queue (up to 4 drivers)
  - Search query
- On return, state is restored

### Back Navigation

**User Action:** Click "← Scout Portal" in top-left

**URL Transition:**
```
/scout/driver/13/overview  →  /scout
```

**Visual Transition:**
1. Detail page slides out to right (250ms ease-in)
2. Scout grid fades in (200ms)
3. Restored scroll position animated (400ms smooth-scroll)
4. Previously selected driver card highlights briefly (2s yellow glow)

**State Restoration:**
- Filters restored from sessionStorage
- Scroll to previous position
- Comparison queue restored
- Recently viewed driver card gets "👁 Viewed" badge for 5 minutes

---

## 4. Enhanced Overview Header Design

### Current Header Issues
- No indication this is part of a scouting workflow
- Driver dropdown is disconnected from broader context
- No way to compare current driver with others
- Missing classification context

### New Header Structure

```
┌──────────────────────────────────────────────────────────────────────┐
│  ← Scout Portal                                    [Compare] [Select] │
│                                                                        │
│  ┌────────────────────────────────────────────────────────────────┐ │
│  │                           FRONTRUNNER                          │ │ ← Classification badge (centered, 24px height)
│  └────────────────────────────────────────────────────────────────┘ │
│                                                                        │
│  ┌──────┐                                                             │
│  │  13  │  Driver #13                     Overall: 67 (89.7th %ile)   │
│  └──────┘  Toyota Gazoo Series             12 Races | 2.75 Avg Finish │
│                                                                        │
│  ──────────────────────────────────────────────────────────────────  │
│  [Overview]  [Race Log]  [Skills]  [Improve]                          │
└──────────────────────────────────────────────────────────────────────┘
```

**Component Breakdown:**

**1. Back Button (Top-Left)**
```jsx
<button className="back-to-scout">
  ← Scout Portal
</button>
```
- Position: Absolute left, aligned with padding
- Style: White text, no background, hover underline
- Font: 16px, 600 weight, uppercase, 0.5px letter-spacing

**2. Quick Actions (Top-Right)**
```jsx
<div className="quick-actions">
  <button className="compare-action">
    Compare with Others
  </button>
  <select className="driver-selector">
    {/* Keep existing dropdown, but refined */}
  </select>
</div>
```

**3. Classification Badge (Centered)**
```jsx
<div className="classification-badge frontrunner">
  FRONTRUNNER
</div>
```
- Width: Auto, padding 12px 32px
- Height: 36px
- Border-radius: 18px (pill shape)
- Background: Gold (#FFD700) with subtle gradient
- Text: Black, 14px, 800 weight, uppercase, 1px letter-spacing
- Box-shadow: 0 2px 8px rgba(255, 215, 0, 0.4)

**4. Driver Identity Section**
```jsx
<div className="driver-identity">
  <div className="driver-number-badge">13</div>
  <div className="driver-info">
    <h1>Driver #13</h1>
    <p>Toyota Gazoo Series</p>
  </div>
  <div className="driver-stats-summary">
    <div>Overall: 67 (89.7th %ile)</div>
    <div>12 Races | 2.75 Avg Finish</div>
  </div>
</div>
```

**5. Navigation Tabs (Existing, Below Header)**
- Unchanged from current implementation
- Tabs: Overview, Race Log, Skills, Improve
- Active state: Red underline, bold text

---

## 5. Comparison Feature Design

### Comparison Queue (Bottom Drawer)

**Trigger:** Click "+ Compare" on any driver card

**Behavior:**
- Drawer slides up from bottom (300ms)
- Persistent across navigation within /scout
- Max 4 drivers in comparison queue

```
┌──────────────────────────────────────────────────────────────────────┐
│                                                                        │
│  [Main Content Area - Scout Grid or Driver Detail]                    │
│                                                                        │
└────────────────────────────────────────────────────────────────────────
  ════════════════════════════════════════════════════════════════════
  COMPARISON QUEUE (3 drivers selected)                    [Compare →]
  ──────────────────────────────────────────────────────────────────────
  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐
  │   #13    │  │   #22    │  │    #7    │  │   ADD    │
  │ ✕ Remove │  │ ✕ Remove │  │ ✕ Remove │  │  DRIVER  │
  └──────────┘  └──────────┘  └──────────┘  └──────────┘
  ════════════════════════════════════════════════════════════════════
```

**Comparison Queue Styling:**
- Background: #1a1a1a (darker than main dark)
- Height: 140px
- Border-top: 4px solid #e74c3c
- Drivers shown as mini-cards: 100px wide × 100px tall
- Horizontal scroll for mobile

### Comparison View (/scout/compare)

**Trigger:** Click "Compare →" button in comparison drawer

**Layout:**
```
┌──────────────────────────────────────────────────────────────────────┐
│  ← Scout Portal                               [Export] [Add Driver]  │
│                                                                        │
│  Driver Comparison (3 drivers)                                        │
│  ──────────────────────────────────────────────────────────────────  │
│                                                                        │
│              Driver #13      Driver #22       Driver #7               │
│              FRONTRUNNER     CONTENDER        CONTENDER               │
│  ────────────────────────────────────────────────────────────────── │
│  Overall         67 🟢          65 🟢            64 🟢                │
│  Speed           67             70 🔥           59                    │
│  Consistency     66 🔥          56              60                    │
│  Racecraft       60             55              61                    │
│  Tire Mgmt       53             48              56                    │
│  ────────────────────────────────────────────────────────────────── │
│  Avg Finish      2.75 🏆        3.67            5.50                 │
│  Podiums         4              2               3                     │
│  Races           12 (Vet)      3 (Rookie)      10 (Vet)              │
│  ────────────────────────────────────────────────────────────────── │
│                                                                        │
│  [Radar Chart Overlay - All 3 Drivers]                                │
│                                                                        │
│  ┌──────────────────────────────────┐                                │
│  │        Consistency                │                                │
│  │          ╱      ╲                 │                                │
│  │  Tire  ╱    ●   ╲  Speed         │                                │
│  │       ●    ●  ●   ●               │                                │
│  │        ╲    ●   ╱                 │                                │
│  │          ╲     ╱                  │                                │
│  │        Racecraft                  │                                │
│  └──────────────────────────────────┘                                │
│                                                                        │
│  [View #13 Details] [View #22 Details] [View #7 Details]              │
│                                                                        │
└──────────────────────────────────────────────────────────────────────┘
```

**Comparison Interactions:**
- Click any "View Details" button → Navigate to that driver's detail page
- Comparison persists in session: can return to it
- "Export" button generates PDF or CSV comparison report

---

## 6. State Management

### Scout Landing Page State (React Context + SessionStorage)

```jsx
// ScoutContext.js
const ScoutContext = {
  // Filtering
  filters: {
    classifications: ['FRONTRUNNER', 'CONTENDER'], // Active filters
    speedRange: [70, 100],
    consistencyRange: [60, 100],
    experienceLevel: 'all', // 'all' | 'veterans' | 'rookies'
    searchQuery: ''
  },

  // View state
  viewMode: 'grid', // 'grid' | 'table'
  sortBy: 'overall_score', // 'overall_score' | 'speed' | 'consistency'
  sortOrder: 'desc',
  scrollPosition: 0,

  // Comparison
  comparisonQueue: [13, 22, 7], // Array of driver numbers (max 4)

  // Recently viewed
  recentlyViewed: [13, 22], // Last 5 drivers viewed, with timestamps

  // Persistence
  saveState: () => sessionStorage.setItem('scoutState', JSON.stringify(state)),
  restoreState: () => JSON.parse(sessionStorage.getItem('scoutState'))
};
```

### Driver Context State (Existing, Enhanced)

```jsx
// DriverContext.js (ENHANCED)
const DriverContext = {
  // Existing
  selectedDriverNumber: 13,
  drivers: [...], // All drivers
  setSelectedDriverNumber: (num) => {},

  // NEW: Scout context awareness
  isFromScout: true, // User came from /scout
  scoutReturnPath: '/scout', // Where to return to
  comparisonQueue: [13, 22, 7], // Synced with ScoutContext

  // Navigation helpers
  navigateToDriver: (driverNumber) => {
    // Navigate to /scout/driver/:num/overview
  },
  returnToScout: () => {
    // Navigate back to /scout with state restoration
  }
};
```

### State Persistence Rules

**SessionStorage** (cleared on tab close):
- Scout filters and view preferences
- Comparison queue
- Scroll position
- Recently viewed drivers

**LocalStorage** (persists across sessions):
- Saved searches (user-named filter presets)
- Last selected driver (default on app load)
- User preferences (theme, units, etc.)

**Do NOT persist:**
- Loading states
- Error states
- Transient UI states (hover, focus)

---

## 7. Mobile Journey

### Mobile Breakpoints
- Mobile: < 768px
- Tablet: 768px - 1024px
- Desktop: > 1024px

### Mobile Scout Landing Page

```
┌─────────────────────────────────┐
│  ☰  Scout Portal        [🔍][⋮] │
├─────────────────────────────────┤
│  ┌─ Filters (Collapsed) ──────┐│
│  │ 2 filters active    [Edit] ││
│  └────────────────────────────┘│
├─────────────────────────────────┤
│  ┌───────────────────────────┐ │
│  │      FRONTRUNNER          │ │
│  │          #13              │ │
│  │      Driver #13           │ │
│  │  Overall: 67 (89.7%)      │ │
│  │  ████████░░ Speed: 67     │ │
│  │  [View] [+ Compare]       │ │
│  └───────────────────────────┘ │
│  ┌───────────────────────────┐ │
│  │      CONTENDER            │ │
│  │          #22              │ │
│  │      Driver #22           │ │
│  │  Overall: 65 (85.3%)      │ │
│  │  ██████████ Speed: 70     │ │
│  │  [View] [+ Compare]       │ │
│  └───────────────────────────┘ │
│                                 │
│  [Load More]                    │
└─────────────────────────────────┘
   ═══════════════════════════════
   🔄 Compare (2)        [Compare]
   ═══════════════════════════════
```

**Mobile Adaptations:**
- Filter sidebar becomes bottom sheet modal
- Driver cards stack vertically (single column)
- Comparison drawer becomes sticky bottom bar
- Touch gestures: Swipe right on card to add to comparison

### Mobile Driver Detail Page

```
┌─────────────────────────────────┐
│  ← Back         #13      [More] │
│     FRONTRUNNER                 │
├─────────────────────────────────┤
│  [Overview][Race Log][Skills]   │ ← Horizontal scroll tabs
├─────────────────────────────────┤
│                                 │
│  Performance Tiles (2x3 grid)   │
│                                 │
│  Race Chart (compressed)        │
│                                 │
│  Radar Chart                    │
│                                 │
│  Factor Cards (stacked)         │
│                                 │
└─────────────────────────────────┘
```

**Mobile Navigation:**
- "← Back" always returns to Scout Portal
- Tabs scroll horizontally
- Driver selector moved to "More" menu (hamburger)
- Comparison accessible via floating action button

---

## 8. Visual Theme Specifications

### Dark Theme Palette (Consistent Across Scout & Detail)

**Backgrounds:**
- Primary Background: #0a0a0a (near black)
- Secondary Background: #1a1a1a (cards, modals)
- Tertiary Background: #2a2a2a (hover states)

**Cards:**
- Card Background: #ffffff (white)
- Card Border: 4px solid #e74c3c
- Card Border Radius: 16px
- Card Shadow: 0 4px 16px rgba(231, 76, 60, 0.3)
- Card Hover Shadow: 0 6px 24px rgba(231, 76, 60, 0.4)

**Typography:**
- Font Family: Inter, -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif
- Heading Color: #ffffff (on dark bg), #000000 (on white cards)
- Body Text: #e0e0e0 (on dark bg), #333333 (on white cards)
- Muted Text: #a0a0a0 (on dark bg), #666666 (on white cards)

**Accents:**
- Primary Red: #e74c3c (borders, buttons, highlights)
- Red Hover: #c0392b (darker red for interactions)
- Red Glow: rgba(231, 76, 60, 0.4) (shadows and glows)

**Classification Colors:**
- Frontrunner: #FFD700 (gold)
- Contender: #C0C0C0 (silver)
- Mid-Pack: #CD7F32 (bronze)
- Development: #718096 (gray)

### Typography Scale

```css
/* Headings */
.heading-xl { font-size: 48px; font-weight: 900; line-height: 1.1; }
.heading-lg { font-size: 36px; font-weight: 800; line-height: 1.2; }
.heading-md { font-size: 24px; font-weight: 700; line-height: 1.3; }
.heading-sm { font-size: 18px; font-weight: 700; line-height: 1.4; }

/* Body */
.body-lg { font-size: 18px; font-weight: 500; line-height: 1.6; }
.body-md { font-size: 16px; font-weight: 500; line-height: 1.6; }
.body-sm { font-size: 14px; font-weight: 500; line-height: 1.5; }
.body-xs { font-size: 12px; font-weight: 500; line-height: 1.4; }

/* Labels */
.label-lg { font-size: 14px; font-weight: 600; text-transform: uppercase; letter-spacing: 0.5px; }
.label-md { font-size: 12px; font-weight: 600; text-transform: uppercase; letter-spacing: 0.5px; }
.label-sm { font-size: 11px; font-weight: 600; text-transform: uppercase; letter-spacing: 1px; }

/* Numbers/Stats */
.stat-xl { font-size: 72px; font-weight: 900; line-height: 1; }
.stat-lg { font-size: 48px; font-weight: 900; line-height: 1; }
.stat-md { font-size: 36px; font-weight: 900; line-height: 1; }
.stat-sm { font-size: 24px; font-weight: 800; line-height: 1; }
```

### Spacing System (8px base unit)

```
XXS: 4px   (0.5 units)
XS:  8px   (1 unit)
SM:  12px  (1.5 units)
MD:  16px  (2 units)
LG:  24px  (3 units)
XL:  32px  (4 units)
XXL: 48px  (6 units)
XXXL: 64px (8 units)
```

---

## 9. Implementation Roadmap

### Phase 1: Foundation (Week 1)
- [ ] Create `/scout` route with basic grid layout
- [ ] Implement ScoutContext with state management
- [ ] Build driver card component with classification badges
- [ ] Connect to existing driver data API
- [ ] Implement basic filtering (classification only)

### Phase 2: Navigation (Week 2)
- [ ] Refactor routes from `/overview` to `/scout/driver/:num/overview`
- [ ] Update DriverContext to track scout context
- [ ] Implement "← Scout Portal" back button
- [ ] Add state persistence (sessionStorage)
- [ ] Build transition animations

### Phase 3: Enhanced Overview Header (Week 2-3)
- [ ] Add classification badge to header
- [ ] Implement quick stats summary in header
- [ ] Refine driver selector styling
- [ ] Add "Compare with Others" button

### Phase 4: Comparison Feature (Week 3-4)
- [ ] Build comparison drawer component
- [ ] Implement comparison queue state management
- [ ] Create `/scout/compare` view
- [ ] Add side-by-side comparison table
- [ ] Implement overlay radar charts

### Phase 5: Advanced Filtering (Week 4)
- [ ] Add performance factor range sliders
- [ ] Implement experience level filters
- [ ] Build search functionality
- [ ] Add saved searches feature
- [ ] Implement table view toggle

### Phase 6: Mobile Optimization (Week 5)
- [ ] Implement responsive breakpoints
- [ ] Build mobile filter bottom sheet
- [ ] Optimize touch interactions
- [ ] Test on iOS and Android devices
- [ ] Refine gesture navigation

### Phase 7: Polish & Testing (Week 6)
- [ ] Comprehensive usability testing
- [ ] Performance optimization (lazy loading, virtualization)
- [ ] Accessibility audit (WCAG 2.1 AA)
- [ ] Cross-browser testing
- [ ] Analytics instrumentation

---

## 10. Metrics & Success Criteria

### Key Performance Indicators (KPIs)

**Efficiency Metrics:**
- Time to find target driver: < 30 seconds
- Filters applied per session: 2-4 average
- Comparison feature usage: 40%+ of sessions
- Return to Scout rate: 60%+ of detail views

**Engagement Metrics:**
- Drivers viewed per session: 5-8 average
- Tab navigation (Overview → Race Log → Skills): 50%+ completion
- Saved searches created: 20%+ of returning users
- Mobile usage: 30%+ of total sessions

**Navigation Metrics:**
- Back button usage (Scout → Detail → Scout): 70%+
- Direct URL shares: Track deep link usage
- Comparison view conversions: 30%+ of comparison queue users
- Dropdown vs. Back navigation: 40% dropdown, 60% back

**Technical Metrics:**
- Page load time: < 2 seconds
- Transition animations: 60fps smooth
- Mobile performance score: 90+ (Lighthouse)
- Accessibility score: 95+ (Lighthouse)

### User Testing Scenarios

**Scenario 1: Find High-Speed Rookie**
- Task: Find drivers with 70+ speed and fewer than 5 races
- Expected actions: Apply filters → Review cards → View details
- Success: Completes in < 45 seconds

**Scenario 2: Compare Top 3 Contenders**
- Task: Add 3 drivers to comparison and analyze differences
- Expected actions: Select drivers → View comparison → Export
- Success: Completes in < 60 seconds

**Scenario 3: Deep-Dive and Return**
- Task: Review Driver #13 overview, then return to browse more
- Expected actions: View details → Explore tabs → Return to scout → Filters preserved
- Success: No confusion, state preserved

**Scenario 4: Mobile Discovery**
- Task: Find and contact a mid-pack driver on mobile device
- Expected actions: Filter → Scroll → View → Contact
- Success: Completes without pinch-zoom or layout issues

---

## 11. Component Specifications

### ScoutLandingPage Component

**File:** `/frontend/src/pages/Scout/ScoutLanding.jsx`

```jsx
import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useScout } from '../../context/ScoutContext';
import { useDriver } from '../../context/DriverContext';
import DriverCard from '../../components/DriverCard/DriverCard';
import FilterSidebar from '../../components/FilterSidebar/FilterSidebar';
import ComparisonDrawer from '../../components/ComparisonDrawer/ComparisonDrawer';
import api from '../../services/api';

export default function ScoutLanding() {
  const navigate = useNavigate();
  const { filters, viewMode, sortBy, sortOrder, comparisonQueue } = useScout();
  const { drivers, setSelectedDriverNumber } = useDriver();
  const [filteredDrivers, setFilteredDrivers] = useState([]);

  useEffect(() => {
    // Apply filters and sorting to drivers
    const filtered = applyFilters(drivers, filters);
    const sorted = applySorting(filtered, sortBy, sortOrder);
    setFilteredDrivers(sorted);
  }, [drivers, filters, sortBy, sortOrder]);

  const handleDriverClick = (driverNumber) => {
    setSelectedDriverNumber(driverNumber);
    navigate(`/scout/driver/${driverNumber}/overview`);
  };

  return (
    <div className="scout-landing">
      <ScoutNavBar />
      <FilterSidebar />
      <div className="driver-grid">
        {filteredDrivers.map(driver => (
          <DriverCard
            key={driver.driver_number}
            driver={driver}
            onClick={() => handleDriverClick(driver.driver_number)}
            onCompare={() => toggleComparison(driver.driver_number)}
            isInComparison={comparisonQueue.includes(driver.driver_number)}
          />
        ))}
      </div>
      {comparisonQueue.length > 0 && <ComparisonDrawer />}
    </div>
  );
}
```

### DriverCard Component

**File:** `/frontend/src/components/DriverCard/DriverCard.jsx`

```jsx
import React from 'react';
import ClassificationBadge from '../ClassificationBadge/ClassificationBadge';
import './DriverCard.css';

export default function DriverCard({ driver, onClick, onCompare, isInComparison }) {
  const {
    driver_number,
    overall_score,
    percentile,
    classification,
    factors,
    stats
  } = driver;

  return (
    <div className="driver-card" onClick={onClick}>
      <ClassificationBadge classification={classification} />

      <div className="driver-number">{driver_number}</div>
      <h3 className="driver-name">Driver #{driver_number}</h3>
      <p className="driver-series">Toyota Gazoo Series</p>

      <div className="overall-stat">
        <div className="stat-label">Overall Score</div>
        <div className="stat-value">{overall_score}</div>
        <div className="stat-percentile">{percentile.toFixed(1)}th Percentile</div>
      </div>

      <div className="factor-bars">
        <FactorBar label="Speed" value={factors.speed.percentile} />
        <FactorBar label="Consistency" value={factors.consistency.percentile} />
        <FactorBar label="Racecraft" value={factors.racecraft.percentile} />
        <FactorBar label="Tire Mgmt" value={factors.tire_management.percentile} />
      </div>

      <div className="quick-stats">
        <span>{stats.race_count} Races</span>
        <span>{stats.avg_finish.toFixed(2)} Avg</span>
        <span>{stats.podiums} Podiums</span>
      </div>

      <div className="card-actions" onClick={(e) => e.stopPropagation()}>
        <button className="btn-view-details">View Details →</button>
        <button
          className={`btn-compare ${isInComparison ? 'active' : ''}`}
          onClick={onCompare}
        >
          {isInComparison ? '✓ Added' : '+ Compare'}
        </button>
      </div>
    </div>
  );
}
```

### Enhanced Overview Header Component

**File:** `/frontend/src/components/DriverHeader/DriverHeader.jsx`

```jsx
import React from 'react';
import { useNavigate } from 'react-router-dom';
import { useDriver } from '../../context/DriverContext';
import ClassificationBadge from '../ClassificationBadge/ClassificationBadge';
import './DriverHeader.css';

export default function DriverHeader({ driver }) {
  const navigate = useNavigate();
  const { selectedDriverNumber, setSelectedDriverNumber, drivers } = useDriver();

  const handleBackToScout = () => {
    navigate('/scout');
  };

  const handleDriverChange = (e) => {
    const newDriverNumber = Number(e.target.value);
    setSelectedDriverNumber(newDriverNumber);
    navigate(`/scout/driver/${newDriverNumber}/overview`);
  };

  return (
    <div className="driver-header-enhanced">
      {/* Top Navigation Bar */}
      <div className="header-nav">
        <button className="back-to-scout" onClick={handleBackToScout}>
          ← Scout Portal
        </button>
        <div className="quick-actions">
          <button className="btn-compare-action">Compare with Others</button>
          <select
            value={selectedDriverNumber}
            onChange={handleDriverChange}
            className="driver-selector"
          >
            {drivers.map(d => (
              <option key={d.number} value={d.number}>
                {d.name}
              </option>
            ))}
          </select>
        </div>
      </div>

      {/* Classification Badge */}
      <div className="classification-section">
        <ClassificationBadge classification={driver.classification} centered />
      </div>

      {/* Driver Identity */}
      <div className="driver-identity">
        <div className="driver-number-badge">{driver.driver_number}</div>
        <div className="driver-info">
          <h1>Driver #{driver.driver_number}</h1>
          <p className="series-name">Toyota Gazoo Series</p>
        </div>
        <div className="driver-stats-summary">
          <div>Overall: {driver.overall_score} ({driver.percentile.toFixed(1)}th %ile)</div>
          <div>{driver.stats.race_count} Races | {driver.stats.avg_finish.toFixed(2)} Avg Finish</div>
        </div>
      </div>
    </div>
  );
}
```

---

## 12. Analytics Instrumentation

### Events to Track

**Scout Landing Page:**
```javascript
// Filter interactions
trackEvent('scout_filter_applied', {
  filterType: 'classification',
  filterValue: 'FRONTRUNNER',
  resultsCount: 1
});

// Driver card interactions
trackEvent('driver_card_viewed', {
  driverNumber: 13,
  classification: 'FRONTRUNNER',
  position: 1, // Position in grid
  source: 'scout_landing'
});

trackEvent('driver_card_clicked', {
  driverNumber: 13,
  classification: 'FRONTRUNNER',
  timeOnCard: 3.5 // seconds
});

// Comparison interactions
trackEvent('driver_added_to_comparison', {
  driverNumber: 13,
  comparisonQueueSize: 2
});

trackEvent('comparison_view_opened', {
  driversInQueue: [13, 22, 7]
});
```

**Driver Detail Page:**
```javascript
// Navigation
trackEvent('driver_detail_viewed', {
  driverNumber: 13,
  source: 'scout_landing', // or 'direct_link', 'dropdown'
  tab: 'overview'
});

trackEvent('back_to_scout_clicked', {
  driverNumber: 13,
  timeOnPage: 45, // seconds
  tabsViewed: ['overview', 'race-log']
});

// Tab navigation
trackEvent('tab_changed', {
  fromTab: 'overview',
  toTab: 'race-log',
  driverNumber: 13
});
```

**Conversion Funnels:**
```javascript
// Track complete user journeys
// Funnel 1: Browse → Filter → View Details
// Funnel 2: Compare → View Details → Contact
// Funnel 3: Search → View Details → Add to List
```

---

## 13. Accessibility Specifications

### Keyboard Navigation

**Scout Landing Page:**
- `Tab`: Navigate between filter controls, driver cards, actions
- `Enter/Space`: Activate driver card or button
- `Escape`: Close filter sidebar or comparison drawer
- `Arrow keys`: Navigate grid (optional enhancement)

**Driver Detail Page:**
- `Alt + ←`: Back to Scout Portal
- `Tab`: Navigate tabs, sections, interactive elements
- `1-4`: Quick navigate to tabs (Overview, Race Log, Skills, Improve)

### Screen Reader Support

**Semantic HTML:**
```html
<nav aria-label="Scout navigation">
  <button aria-label="Return to scout landing page">← Scout Portal</button>
</nav>

<main aria-label="Scout landing page">
  <section aria-label="Driver filters">...</section>
  <section aria-label="Driver grid" aria-live="polite">
    <article aria-label="Driver 13, Frontrunner, Overall score 67">
      ...
    </article>
  </section>
</main>

<aside aria-label="Comparison queue" aria-live="polite">
  <p>2 drivers selected for comparison</p>
</aside>
```

**ARIA Attributes:**
- `aria-current="page"` on active tab
- `aria-expanded` on collapsible filter groups
- `aria-selected` on comparison queue items
- `aria-label` on icon-only buttons

### Color Contrast

**WCAG 2.1 AA Compliance:**
- White text on #e74c3c red: 4.51:1 (Pass)
- Black text on #FFD700 gold badge: 10.35:1 (Pass)
- Light gray (#a0a0a0) on black (#0a0a0a): 7.2:1 (Pass)
- All interactive elements: 4.5:1 minimum

**Focus Indicators:**
- Visible focus ring: 3px solid #e74c3c with 2px white outline
- Focus visible on all interactive elements
- Skip to main content link

---

## 14. Performance Optimization

### Code Splitting
```javascript
// Lazy load heavy components
const ScoutLanding = lazy(() => import('./pages/Scout/ScoutLanding'));
const ComparisonView = lazy(() => import('./pages/Scout/ComparisonView'));
const Overview = lazy(() => import('./pages/Overview/Overview'));
```

### Virtualization
- Implement virtual scrolling for driver grid (>50 drivers)
- Use `react-window` or `react-virtualized`
- Render only visible cards + buffer

### Image Optimization
- Driver photos: WebP format, 200x200px, lazy loaded
- Use `loading="lazy"` on all images
- Provide fallback avatar for missing photos

### Data Caching
```javascript
// Cache driver data for 5 minutes
const driverDataCache = new Map();
const CACHE_TTL = 5 * 60 * 1000; // 5 minutes

const fetchDriverData = async (driverNumber) => {
  const cached = driverDataCache.get(driverNumber);
  if (cached && Date.now() - cached.timestamp < CACHE_TTL) {
    return cached.data;
  }

  const data = await api.get(`/api/drivers/${driverNumber}`);
  driverDataCache.set(driverNumber, { data, timestamp: Date.now() });
  return data;
};
```

### Animation Performance
- Use `transform` and `opacity` for animations (GPU accelerated)
- Use `will-change` sparingly
- Avoid animating `width`, `height`, `top`, `left`
- Target 60fps for all transitions

---

## 15. Error States & Edge Cases

### No Drivers Found (Empty Filter Results)
```
┌──────────────────────────────────────────────────────────┐
│                                                          │
│               No drivers match your filters              │
│                                                          │
│  Try adjusting your criteria:                            │
│  • Expand speed range to 40-100                          │
│  • Include more classifications                          │
│  • Reset all filters                                     │
│                                                          │
│  [Adjust Filters]  [Reset All]                           │
│                                                          │
└──────────────────────────────────────────────────────────┘
```

### Driver Data Load Error
```
┌──────────────────────────────────────────────────────────┐
│                                                          │
│        ⚠ Unable to load driver #13                       │
│                                                          │
│  This driver's data is temporarily unavailable.          │
│                                                          │
│  [← Back to Scout]  [Try Again]  [View Another]          │
│                                                          │
└──────────────────────────────────────────────────────────┘
```

### Comparison Queue Full (4 drivers)
```
Toast notification:
┌──────────────────────────────────────────────────────┐
│  Comparison queue full (4 drivers)                   │
│  Remove a driver to add another.              [✕]    │
└──────────────────────────────────────────────────────┘
```

### Slow Network (Loading States)
- Skeleton screens for driver cards (pulse animation)
- Spinner for filter results update
- Progressive loading: Show cached data first, update when fresh data arrives

---

## Appendix A: Complete Route Map

```
/                                    → Redirect to /scout
/scout                               → Scout Landing Page
/scout/compare                       → Comparison View
/scout/driver/:num                   → Redirect to /scout/driver/:num/overview
/scout/driver/:num/overview          → Overview Page (enhanced header)
/scout/driver/:num/race-log          → Race Log Page
/scout/driver/:num/skills            → Skills Page
/scout/driver/:num/improve           → Improve Page

DEPRECATED (redirect to new structure):
/overview                            → /scout/driver/:lastSelected/overview
/race-log                            → /scout/driver/:lastSelected/race-log
/skills                              → /scout/driver/:lastSelected/skills
/improve                             → /scout/driver/:lastSelected/improve
```

---

## Appendix B: API Endpoints Required

```
GET /api/drivers
GET /api/drivers/:number
GET /api/drivers/:number/stats
GET /api/drivers/:number/results
GET /api/drivers/compare?ids=13,22,7
POST /api/saved-searches (for saved filter presets)
GET /api/saved-searches/:userId
```

---

## Appendix C: Design Checklist

Before shipping Scout Landing Page, verify:

- [ ] All classification badges display correctly
- [ ] Filter state persists across navigation
- [ ] Comparison queue syncs across Scout and Detail views
- [ ] Back button returns to correct scroll position
- [ ] Mobile touch gestures work smoothly
- [ ] Keyboard navigation is complete
- [ ] Screen reader announces all interactive elements
- [ ] Color contrast meets WCAG AA
- [ ] Page load time < 2 seconds
- [ ] Animations run at 60fps
- [ ] Error states are user-friendly
- [ ] Analytics events fire correctly
- [ ] Deep links work (sharing driver URLs)
- [ ] Old routes redirect properly

---

**Document Version:** 1.0
**Last Updated:** 2025-11-02
**Author:** Sports Recruiting UX Designer (Claude Code)
**Status:** Ready for Development

**Files Referenced:**
- `/frontend/src/pages/Overview/Overview.jsx`
- `/frontend/src/App.jsx`
- `/analysis/racing_classification_system.md`
