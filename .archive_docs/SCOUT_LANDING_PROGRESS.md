# Scout Landing Page - Implementation Progress

## ✅ Completed (Foundation Layer)

### 1. **ScoutContext** (`/frontend/src/context/ScoutContext.jsx`)
State management for the entire scout experience:
- Filter state (classification, experience, attributes, ranges)
- View state (cards vs table, sort options)
- Comparison queue (max 4 drivers)
- Selected drivers for bulk actions
- **SessionStorage persistence** (filters, scroll position restored on return)
- Clean API with hooks: `useScout()`

### 2. **Classification Utilities** (`/frontend/src/utils/classification.js`)
Data-driven classification logic based on statistical analysis:
- **4-tier system**: FRONTRUNNER, CONTENDER, MID_PACK, DEVELOPMENT
- `classifyDriver(driver)` - Returns tier based on overall score, races, avg finish
- `getDriverTags(driver)` - Returns attribute tags (Speed Specialist, Veteran, etc.)
- `applyFilters(drivers, filters)` - Filter logic for all criteria
- `sortDrivers(drivers, sortBy, sortOrder)` - Sorting logic
- `getDataConfidence(races)` - Confidence warnings for low sample size

**Classification Rules (Data-Driven):**
- **FRONTRUNNER**: 65+ overall, 10+ races, <5 avg finish (Only 1 driver: #13)
- **CONTENDER**: 60-65 overall OR 70+ speed with <7 races (6-7 drivers)
- **MID-PACK**: 50-60 overall (12-15 drivers)
- **DEVELOPMENT**: <50 overall (15-20 drivers)

### 3. **ClassificationBadge Component** (`/frontend/src/components/ClassificationBadge/`)
Professional racing-themed badges:
- Gold (FRONTRUNNER), Silver (CONTENDER), Bronze (MID-PACK), Gray (DEVELOPMENT)
- Size variants: small, medium, large
- Optional description text
- No emojis (professional)
- Matches existing F1 design system

## 📋 Next Steps - Scout Landing Page Components

### 4. **DriverCard Component** (Next)
Grid card for each driver:
- Classification badge prominent
- Driver number and name
- Key metrics with horizontal bars
- Attribute tags (Speed Specialist, Rookie, etc.)
- Circuit fit summary
- Data confidence warning (if <5 races)
- Actions: View Details, Compare, Add to List

### 5. **FilterSidebar Component**
Left sidebar with all filters:
- Classification checkboxes (4 tiers)
- Experience checkboxes (Veteran, Developing, Rookie)
- Attribute checkboxes (Speed, Wheel-to-Wheel, Consistent)
- Range sliders (Overall, Speed, Races, Avg Finish)
- Reset button
- Live result count

### 6. **ScoutLanding Page**
Main page component:
- Dark theme matching Overview page
- 3-column layout: FilterSidebar | DriverGrid | QuickStats
- Grid controls: Search, Sort, View toggle (cards/table)
- Responsive grid (3-4 cards per row)
- Quick stats sidebar (field overview, comparison queue)

### 7. **ComparisonDrawer Component**
Bottom drawer for comparison queue:
- Shows up to 4 drivers in queue
- "Compare" button → opens ComparisonModal
- Remove drivers from queue
- Persists across navigation

### 8. **Routing Updates** (`/frontend/src/App.jsx`)
Add new routes:
- `/scout` - Scout Landing Page
- Make `/scout` the default entry point (scouts start here)
- Keep existing `/overview`, `/race-log`, `/skills`, `/improve` routes

## 🎨 Design System Alignment

### Colors (Consistent with Overview)
- Background: Dark (#1a1a1a or #000)
- Primary Accent: #e74c3c (Racing Red)
- Cards: White with 4px #e74c3c borders
- Typography: Inter, bold (700-900 weights)

### Classification Tier Colors
- **FRONTRUNNER**: #D4AF37 (Gold) on #FFF8DC background
- **CONTENDER**: #C0C0C0 (Silver) on #F5F5F5 background
- **MID-PACK**: #CD7F32 (Bronze) on #FFF5EE background
- **DEVELOPMENT**: #6B7280 (Gray) on #F9FAFB background

### Component Patterns (Match Overview)
- Bold red borders (4px solid)
- Rounded corners (16px)
- Drop shadows on hover
- Large bold numbers (36px+, weight 900)
- Uppercase labels with letter-spacing

## 📊 Data Integration

### Data Source: `/frontend/src/data/dashboardData.json`
- 34 drivers with full stats
- Classification applied at runtime (not stored in JSON)
- Filters applied client-side for fast UX

### Key Metrics Displayed:
1. **Overall Score** (0-100)
2. **Speed Percentile** (0-100)
3. **Consistency Percentile** (0-100)
4. **Racecraft Percentile** (0-100)
5. **Tire Management Percentile** (0-100)
6. **Races** (experience indicator)
7. **Avg Finish Position**

## 🚀 Implementation Order

**Phase 1** (Current - Foundation):
- ✅ ScoutContext
- ✅ Classification utilities
- ✅ ClassificationBadge component

**Phase 2** (Next - Core Components):
- ⏳ DriverCard component
- ⏳ FilterSidebar component
- ⏳ ScoutLanding page skeleton

**Phase 3** (After Core):
- QuickStatsSidebar component
- ComparisonDrawer component
- TableView component (alternative to cards)

**Phase 4** (Final):
- Routing updates (add /scout)
- Navigation enhancements
- Mobile responsive optimizations

## 🔗 User Journey Flow

```
1. Scout lands on /scout (Scout Landing Page)
   - Sees all 34 drivers in grid
   - Filters by classification, speed, experience
   - Adds drivers to comparison queue

2. Scout clicks "View Details" on Driver #13
   - Navigates to /scout/driver/13/overview
   - Sees enhanced Overview with classification badge
   - Tabs: Overview | Race Log | Skills | Improve

3. Scout clicks "← Scout Portal" breadcrumb
   - Returns to /scout
   - Filters RESTORED from SessionStorage
   - Comparison queue RESTORED
   - Scroll position RESTORED
```

## 📝 Notes & Decisions

1. **No Emojis**: Professional racing terminology only
2. **Data Honesty**: Classification based on actual statistical analysis
3. **Dark Theme**: Consistent F1-inspired aesthetic throughout
4. **State Persistence**: SessionStorage preserves scout workflow
5. **4-Tier System**: Simple, scannable, honest about driver levels

---

**Current Status**: Foundation complete, ready to build DriverCard component next.

**Files Created**:
- `/frontend/src/context/ScoutContext.jsx`
- `/frontend/src/utils/classification.js`
- `/frontend/src/components/ClassificationBadge/ClassificationBadge.jsx`
- `/frontend/src/components/ClassificationBadge/ClassificationBadge.css`
