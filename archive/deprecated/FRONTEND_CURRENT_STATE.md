# Frontend Current State

## Current Structure (Before Phase 2)

```
frontend/
├── 📄 Config files (ROOT LEVEL - needs organization)
│   ├── eslint.config.js
│   ├── postcss.config.js
│   ├── tailwind.config.js
│   └── vite.config.js
│
├── 📄 index.html
├── 📄 package.json
├── 📄 package-lock.json
│
├── 📁 public/
│   └── track_maps/
│       ├── barber.png
│       └── cota.png
│
└── 📁 src/
    ├── main.jsx
    ├── App.jsx
    ├── App.css
    ├── index.css
    │
    ├── 📁 assets/
    │   └── react.svg
    │
    ├── 📁 components/ (FLAT - needs organization)
    │   ├── Navigation.jsx
    │   ├── Navigation.css
    │   ├── SpeedTraceChart.jsx
    │   ├── SpeedTraceChart.css
    │   └── shared/
    │       ├── DriverSelector.jsx
    │       ├── PercentileBadge.jsx
    │       ├── StatCard.jsx
    │       └── StatGroup.jsx
    │
    ├── 📁 context/
    │   └── SelectionContext.jsx
    │
    ├── 📁 data/
    │   ├── dashboardData.json
    │   ├── mockData.js (SHOULD DELETE)
    │   └── plan_for_10_29.md (SHOULD ARCHIVE)
    │
    ├── 📁 pages/ (FLAT - needs folders per page)
    │   ├── Improve.jsx
    │   ├── Improve.css
    │   ├── Overview.jsx
    │   ├── Overview.css
    │   ├── RaceLog.jsx
    │   ├── RaceLog.css
    │   ├── Rankings.css (ORPHAN - no .jsx file!)
    │   ├── Skills.jsx
    │   ├── Skills.css
    │   ├── StrategyChat.jsx
    │   ├── StrategyChat.css
    │   ├── TelemetryComparison.jsx
    │   ├── TelemetryComparison.css
    │   ├── TrackIntelligence.jsx
    │   ├── TrackIntelligence.css
    │   └── frontend/ ⚠️ INCORRECTLY NESTED
    │       └── src/
    │           └── components/ (EMPTY)
    │
    └── 📁 services/
        └── api.js
```

## Issues to Fix in Phase 2:

### 🔴 CRITICAL ISSUES
1. **Nested frontend directory** `frontend/src/pages/frontend/` - Must be removed
2. **Orphaned CSS file** `Rankings.css` - No corresponding JSX file

### ⚠️ ORGANIZATION ISSUES
3. **Flat pages structure** - All pages and CSS in one folder
4. **Flat components structure** - Navigation and Charts not grouped
5. **Config files scattered** - All in root instead of config/ folder
6. **Mock data file** - Should be removed (using real API)
7. **Old plan file** - Should be archived

## Target Structure (After Phase 2)

```
frontend/
├── 📄 index.html
├── 📄 package.json
├── 📄 package-lock.json
├── 📄 README.md
│
├── 📁 config/                  ← NEW: All config files here
│   ├── eslint.config.js
│   ├── postcss.config.js
│   ├── tailwind.config.js
│   └── vite.config.js
│
├── 📁 public/
│   └── track_maps/
│
└── 📁 src/
    ├── main.jsx
    ├── App.jsx
    ├── App.css
    ├── index.css
    │
    ├── 📁 assets/
    │   └── react.svg
    │
    ├── 📁 components/
    │   ├── navigation/         ← NEW FOLDER
    │   │   ├── Navigation.jsx
    │   │   └── Navigation.css
    │   │
    │   ├── charts/             ← NEW FOLDER
    │   │   ├── SpeedTraceChart.jsx
    │   │   └── SpeedTraceChart.css
    │   │
    │   └── shared/            (stays as is)
    │       ├── DriverSelector.jsx
    │       ├── PercentileBadge.jsx
    │       ├── StatCard.jsx
    │       └── StatGroup.jsx
    │
    ├── 📁 context/
    │   └── SelectionContext.jsx
    │
    ├── 📁 data/
    │   └── dashboardData.json
    │
    ├── 📁 pages/
    │   ├── Overview/           ← NEW FOLDER per page
    │   │   ├── Overview.jsx
    │   │   └── Overview.css
    │   │
    │   ├── Skills/
    │   │   ├── Skills.jsx
    │   │   └── Skills.css
    │   │
    │   ├── Improve/
    │   │   ├── Improve.jsx
    │   │   └── Improve.css
    │   │
    │   ├── RaceLog/
    │   │   ├── RaceLog.jsx
    │   │   └── RaceLog.css
    │   │
    │   ├── TelemetryComparison/
    │   │   ├── TelemetryComparison.jsx
    │   │   └── TelemetryComparison.css
    │   │
    │   ├── TrackIntelligence/
    │   │   ├── TrackIntelligence.jsx
    │   │   └── TrackIntelligence.css
    │   │
    │   └── StrategyChat/
    │       ├── StrategyChat.jsx
    │       └── StrategyChat.css
    │
    └── 📁 services/
        └── api.js
```

## Changes Required:

### File Moves: ~40 files
### Import Updates: ~10 files
### Files to Delete: 3
### Config Updates: 2

## Phase 2 Steps:

1. ✅ Remove nested frontend directory
2. ✅ Remove orphaned Rankings.css
3. ✅ Remove mockData.js
4. ✅ Archive plan_for_10_29.md
5. ✅ Create folder structure
6. ✅ Move config files
7. ✅ Move component files
8. ✅ Move page files
9. ✅ Update imports in all files
10. ✅ Update vite.config.js reference
11. ✅ Test frontend build

---

**Ready to execute Phase 2?**
