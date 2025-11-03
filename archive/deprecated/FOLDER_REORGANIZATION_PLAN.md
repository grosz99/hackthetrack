# Folder Reorganization Plan

**Goal:** Clean, professional, organized folder structure that's easy to navigate

---

## PROPOSED NEW STRUCTURE

```
hackthetrack-master/
│
├── 📄 README.md                              # Main project documentation
├── 📄 .gitignore                             # Git ignore rules
├── 📄 vercel.json                            # Deployment configuration
│
├── 📁 backend/                               # Backend API application
│   ├── main.py                               # FastAPI entry point
│   ├── requirements.txt                      # Python dependencies
│   ├── circuit-fit.db                        # SQLite database
│   │
│   ├── api/                                  # API layer
│   │   ├── __init__.py
│   │   ├── index.py                          # API index
│   │   └── routes.py                         # API endpoints
│   │
│   ├── database/                             # Database layer
│   │   ├── __init__.py
│   │   ├── connection.py                     # DB connection
│   │   └── schema.sql                        # DB schema
│   │
│   ├── models/                               # Data models
│   │   ├── __init__.py
│   │   └── models.py                         # Pydantic models
│   │
│   └── services/                             # Business logic
│       ├── __init__.py
│       ├── ai_strategy.py                    # AI strategy service
│       ├── data_loader.py                    # Data loading
│       ├── factor_analyzer.py                # Factor analysis
│       ├── improve_predictor.py              # Performance predictions
│       ├── race_log_processor.py             # Race log processing
│       └── telemetry_processor.py            # Telemetry processing
│
├── 📁 frontend/                              # Frontend React application
│   ├── package.json                          # Node dependencies
│   ├── package-lock.json                     # Locked dependencies
│   ├── index.html                            # HTML entry point
│   ├── README.md                             # Frontend docs
│   │
│   ├── config/                               # Configuration files
│   │   ├── vite.config.js                    # Vite build config
│   │   ├── tailwind.config.js                # Tailwind CSS config
│   │   ├── postcss.config.js                 # PostCSS config
│   │   └── eslint.config.js                  # ESLint config
│   │
│   ├── public/                               # Static assets
│   │   ├── vite.svg
│   │   └── track_maps/                       # Track images for web
│   │       ├── barber.png
│   │       └── cota.png
│   │
│   └── src/                                  # Source code
│       ├── main.jsx                          # React entry point
│       ├── App.jsx                           # Main app component
│       ├── App.css                           # App styles
│       ├── index.css                         # Global styles
│       │
│       ├── components/                       # Reusable components
│       │   ├── navigation/
│       │   │   ├── Navigation.jsx
│       │   │   └── Navigation.css
│       │   │
│       │   ├── charts/
│       │   │   ├── SpeedTraceChart.jsx
│       │   │   └── SpeedTraceChart.css
│       │   │
│       │   └── shared/                       # Shared/common components
│       │       ├── DriverSelector.jsx
│       │       ├── PercentileBadge.jsx
│       │       ├── StatCard.jsx
│       │       └── StatGroup.jsx
│       │
│       ├── pages/                            # Page components
│       │   ├── Overview/
│       │   │   ├── Overview.jsx
│       │   │   └── Overview.css
│       │   ├── Skills/
│       │   │   ├── Skills.jsx
│       │   │   └── Skills.css
│       │   ├── Improve/
│       │   │   ├── Improve.jsx
│       │   │   └── Improve.css
│       │   ├── RaceLog/
│       │   │   ├── RaceLog.jsx
│       │   │   └── RaceLog.css
│       │   ├── TelemetryComparison/
│       │   │   ├── TelemetryComparison.jsx
│       │   │   └── TelemetryComparison.css
│       │   ├── TrackIntelligence/
│       │   │   ├── TrackIntelligence.jsx
│       │   │   └── TrackIntelligence.css
│       │   └── StrategyChat/
│       │       ├── StrategyChat.jsx
│       │       └── StrategyChat.css
│       │
│       ├── context/                          # React Context providers
│       │   └── SelectionContext.jsx
│       │
│       ├── services/                         # API client services
│       │   └── api.js
│       │
│       ├── data/                             # Static data
│       │   └── dashboardData.json
│       │
│       └── assets/                           # Images, fonts, etc.
│           └── react.svg
│
├── 📁 data/                                  # Race data (~1.5GB)
│   ├── README.md                             # Data documentation
│   │
│   ├── telemetry/                            # Raw telemetry data
│   │   ├── barber_r1_wide.csv               (114MB)
│   │   ├── barber_r2_wide.csv               (116MB)
│   │   ├── cota_r1_wide.csv                 (167MB)
│   │   ├── cota_r2_wide.csv                 (161MB)
│   │   ├── roadamerica_r1_wide.csv          (86MB)
│   │   ├── roadamerica_r2_wide.csv          (107MB)
│   │   ├── sonoma_r1_wide.csv               (258MB)
│   │   └── sonoma_r2_wide.csv               (129MB)
│   │
│   ├── lap_timing/                           # Lap time data
│   │   └── [track lap timing files]
│   │
│   ├── race_results/                         # Race results
│   │   ├── best_10_laps/
│   │   ├── provisional_results/
│   │   └── analysis_endurance/
│   │
│   ├── qualifying/                           # Qualifying session data
│   │   └── [qualifying files]
│   │
│   └── analysis_outputs/                     # Generated analysis
│       └── [feature CSV files]
│
├── 📁 assets/                                # Project assets
│   └── track_maps/                           # Track map resources
│       ├── images/                           # PNG images
│       │   ├── barber.png
│       │   ├── cota.png
│       │   ├── roadamerica.png
│       │   └── sonoma.png
│       │
│       └── documents/                        # PDF documents
│           ├── Barber_Circuit_Map.pdf
│           ├── COTA_Circuit_Map.pdf
│           ├── Road_America_Map.pdf
│           ├── Sebring_Track_Sector_Map.pdf
│           ├── Sonoma_Map.pdf
│           └── VIR_map.pdf
│
├── 📁 scripts/                               # Analysis scripts
│   ├── README.md                             # Scripts documentation
│   │
│   ├── analysis/                             # Analysis scripts
│   │   ├── analyze_score_distributions.py
│   │   ├── analyze_telemetry_factors.py
│   │   └── test_telemetry_model_improvement.py
│   │
│   ├── data_processing/                      # Data processing
│   │   ├── extract_telemetry_features.py
│   │   ├── generate_dashboard_data.py
│   │   └── load_data.py
│   │
│   ├── feature_engineering/                  # Feature engineering
│   │   ├── build_features_tiered.py
│   │   └── run_tier1_efa.py
│   │
│   ├── validation/                           # Validation scripts
│   │   ├── validate_lodo_cv.py
│   │   └── validate_tier1_for_product.py
│   │
│   └── utilities/                            # Utility scripts
│       ├── generate_sample_data.py
│       └── demonstrate_factor_prediction.py
│
├── 📁 docs/                                  # Documentation
│   ├── README.md                             # Docs index
│   │
│   ├── product/                              # Product documentation
│   │   ├── PRODUCT_REQUIREMENTS.md
│   │   └── PROJECT_ROADMAP.md
│   │
│   ├── technical/                            # Technical docs
│   │   ├── DATA_DICTIONARY.md
│   │   ├── FINAL_4_FACTOR_MODEL.md
│   │   └── database/
│   │       └── database_schema.md
│   │
│   ├── specifications/                       # Detailed specs
│   │   ├── dashboard_specification.md
│   │   ├── database_specification.md
│   │   └── improve_page_specification.md
│   │
│   └── design/                               # Design documents
│       ├── ui_components.md
│       ├── dashboard_design.md
│       └── coach_agent/
│           └── AI_COACHING_LIBRARY.md
│
└── 📁 archive/                               # Archived files
    ├── README.md                             # Archive index
    │
    ├── documentation/                        # Old docs
    │   ├── PROJECT_SUMMARY.md
    │   ├── RACE_LOG_BACKEND_STATUS.md
    │   ├── NEXT_STEPS10.27.md
    │   ├── RESEARCH_STATUS_AND_DECISION_POINTS.md
    │   ├── FILE_CLEANUP_PLAN.md
    │   ├── IMPLEMENTATION_PLAN.md
    │   └── DASHBOARD_DESIGN_BRIEF.md
    │
    └── deprecated/                           # Deprecated code/files
        └── [old implementations]
```

---

## REORGANIZATION STEPS

### Step 1: Create New Folder Structure

```bash
# Backend reorganization
mkdir -p backend/models

# Frontend reorganization
mkdir -p frontend/config
mkdir -p frontend/src/components/navigation
mkdir -p frontend/src/components/charts
mkdir -p frontend/src/components/shared
mkdir -p frontend/src/pages/Overview
mkdir -p frontend/src/pages/Skills
mkdir -p frontend/src/pages/Improve
mkdir -p frontend/src/pages/RaceLog
mkdir -p frontend/src/pages/TelemetryComparison
mkdir -p frontend/src/pages/TrackIntelligence
mkdir -p frontend/src/pages/StrategyChat
mkdir -p frontend/src/assets

# Data reorganization
mkdir -p data/telemetry
mkdir -p data/lap_timing
mkdir -p data/race_results
mkdir -p data/qualifying
mkdir -p data/analysis_outputs

# Assets reorganization
mkdir -p assets/track_maps/images
mkdir -p assets/track_maps/documents

# Scripts reorganization
mkdir -p scripts/analysis
mkdir -p scripts/data_processing
mkdir -p scripts/feature_engineering
mkdir -p scripts/validation
mkdir -p scripts/utilities

# Documentation reorganization
mkdir -p docs/product
mkdir -p docs/technical/database
mkdir -p docs/specifications
mkdir -p docs/design/coach_agent

# Archive (already exists, just add index)
mkdir -p archive/deprecated
```

### Step 2: Move Backend Files

```bash
# Move models
mv backend/app/models.py backend/models/models.py
touch backend/models/__init__.py
```

### Step 3: Move Frontend Files

```bash
# Move config files
mv frontend/vite.config.js frontend/config/vite.config.js
mv frontend/tailwind.config.js frontend/config/tailwind.config.js
mv frontend/postcss.config.js frontend/config/postcss.config.js
mv frontend/eslint.config.js frontend/config/eslint.config.js

# Move navigation component
mv frontend/src/components/Navigation.jsx frontend/src/components/navigation/Navigation.jsx
mv frontend/src/components/Navigation.css frontend/src/components/navigation/Navigation.css

# Move chart components
mv frontend/src/components/SpeedTraceChart.jsx frontend/src/components/charts/SpeedTraceChart.jsx
mv frontend/src/components/SpeedTraceChart.css frontend/src/components/charts/SpeedTraceChart.css

# Move shared components (already in shared/)
# No action needed

# Move pages to their own folders
mv frontend/src/pages/Overview.jsx frontend/src/pages/Overview/Overview.jsx
mv frontend/src/pages/Overview.css frontend/src/pages/Overview/Overview.css

mv frontend/src/pages/Skills.jsx frontend/src/pages/Skills/Skills.jsx
mv frontend/src/pages/Skills.css frontend/src/pages/Skills/Skills.css

mv frontend/src/pages/Improve.jsx frontend/src/pages/Improve/Improve.jsx
mv frontend/src/pages/Improve.css frontend/src/pages/Improve/Improve.css

mv frontend/src/pages/RaceLog.jsx frontend/src/pages/RaceLog/RaceLog.jsx
mv frontend/src/pages/RaceLog.css frontend/src/pages/RaceLog/RaceLog.css

mv frontend/src/pages/TelemetryComparison.jsx frontend/src/pages/TelemetryComparison/TelemetryComparison.jsx
mv frontend/src/pages/TelemetryComparison.css frontend/src/pages/TelemetryComparison/TelemetryComparison.css

mv frontend/src/pages/TrackIntelligence.jsx frontend/src/pages/TrackIntelligence/TrackIntelligence.jsx
mv frontend/src/pages/TrackIntelligence.css frontend/src/pages/TrackIntelligence/TrackIntelligence.css

mv frontend/src/pages/StrategyChat.jsx frontend/src/pages/StrategyChat/StrategyChat.jsx
mv frontend/src/pages/StrategyChat.css frontend/src/pages/StrategyChat/StrategyChat.css

# Move assets
mv frontend/src/assets/react.svg frontend/src/assets/react.svg

# Remove Rankings.css (orphaned file, no Rankings.jsx found)
rm frontend/src/pages/Rankings.css
```

### Step 4: Move Data Files

```bash
# Move telemetry data
mv data/Telemetry/* data/telemetry/
rmdir data/Telemetry

# lap_timing, race_results, qualifying, analysis_outputs already correctly named
```

### Step 5: Move Assets

```bash
# Move track map images
mv track_maps/*.png assets/track_maps/images/

# Move track map PDFs
mv track_maps/*.pdf assets/track_maps/documents/

# Remove old track_maps folder
rmdir track_maps
```

### Step 6: Reorganize Scripts

```bash
# Analysis scripts
mv scripts/analyze_score_distributions.py scripts/analysis/
mv scripts/analyze_telemetry_factors.py scripts/analysis/
mv scripts/test_telemetry_model_improvement.py scripts/analysis/

# Data processing
mv scripts/extract_telemetry_features.py scripts/data_processing/
mv scripts/generate_dashboard_data.py scripts/data_processing/
mv scripts/load_data.py scripts/data_processing/

# Feature engineering
mv scripts/build_features_tiered.py scripts/feature_engineering/
mv scripts/run_tier1_efa.py scripts/feature_engineering/

# Validation
mv scripts/validate_lodo_cv.py scripts/validation/
mv scripts/validate_tier1_for_product.py scripts/validation/

# Utilities
mv scripts/generate_sample_data.py scripts/utilities/
mv scripts/demonstrate_factor_prediction.py scripts/utilities/
```

### Step 7: Reorganize Documentation

```bash
# Product docs
mv PRODUCT_REQUIREMENTS.md docs/product/
mv PROJECT_ROADMAP.md docs/product/

# Technical docs
mv DATA_DICTIONARY.md docs/technical/
mv FINAL_4_FACTOR_MODEL.md docs/technical/

# Specifications
mv specs/circuit-fit-dashboard-spec.md docs/specifications/dashboard_specification.md
mv specs/circuit-fit-database-spec.md docs/specifications/database_specification.md

# Consolidate IMPROVE_PAGE docs into one
cat specs/IMPROVE_PAGE_*.md > docs/specifications/improve_page_specification.md
rm specs/IMPROVE_PAGE_*.md
rm specs/IMPROVE_PAGE_CORRECTED_IMPLEMENTATION.py

# Design docs
mv design/components.md docs/design/ui_components.md
mv design/racing-dashboard-design.skill docs/design/dashboard_design.md
mv design/coach_agent/AI_COACHING_LIBRARY.md docs/design/coach_agent/

# Remove empty directories
rmdir design/coach_agent design
rmdir specs
```

### Step 8: Archive Old Documentation

```bash
# Move statistical review docs to archive
mv STATISTICAL_*.md archive/deprecated/
mv TIER1_VALIDATION_RESULTS.md archive/deprecated/
mv SKILLS_INTEGRATION_FIX.md archive/deprecated/
mv VERCEL_DEPLOYMENT.md archive/deprecated/
mv REPOSITORY_CLEANUP_ANALYSIS.md archive/deprecated/
mv ESSENTIAL_FILES_AUDIT.md archive/deprecated/
mv PRODUCT_SPECIFICATION.md archive/deprecated/
```

### Step 9: Create README Files

```bash
# Create index files for each major directory
touch data/README.md
touch scripts/README.md
touch docs/README.md
touch archive/README.md
touch assets/track_maps/README.md
```

### Step 10: Update Configuration Files

```bash
# Update frontend/vite.config.js to reference new config location
# Update import statements in all files
```

---

## FILES THAT NEED CODE UPDATES

### 1. Frontend Config References

**frontend/package.json**
```json
{
  "scripts": {
    "dev": "vite --config config/vite.config.js",
    "build": "vite build --config config/vite.config.js"
  }
}
```

**frontend/config/vite.config.js** (moved from root)
```javascript
// Update any relative paths if needed
```

**frontend/config/tailwind.config.js** (moved from root)
```javascript
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  // ... rest of config
}
```

### 2. Frontend Import Updates

**frontend/src/App.jsx**
```javascript
// Update page imports
import Overview from './pages/Overview/Overview'
import Skills from './pages/Skills/Skills'
import Improve from './pages/Improve/Improve'
import RaceLog from './pages/RaceLog/RaceLog'
import TelemetryComparison from './pages/TelemetryComparison/TelemetryComparison'
import TrackIntelligence from './pages/TrackIntelligence/TrackIntelligence'
import StrategyChat from './pages/StrategyChat/StrategyChat'
import Navigation from './components/navigation/Navigation'
```

**All Page Components**
```javascript
// Update chart imports
import SpeedTraceChart from '../../components/charts/SpeedTraceChart'

// Update shared component imports
import DriverSelector from '../../components/shared/DriverSelector'
import StatCard from '../../components/shared/StatCard'
// etc.
```

### 3. Backend Import Updates

**backend/api/routes.py**
```python
# Update model imports
from backend.models.models import Driver, Race, Session
# or
from ..models.models import Driver, Race, Session
```

**backend/services/*.py**
```python
# Update model imports if needed
from backend.models.models import Driver
# or
from ..models.models import Driver
```

### 4. Public Assets References

**frontend/public/track_maps** → No change needed (stays in public)

But update any references in components:
```javascript
// Already correct
<img src="/track_maps/barber.png" />
```

---

## UPDATED .gitignore

```gitignore
# Dependencies
backend/venv/
frontend/node_modules/

# Build outputs
frontend/dist/
backend/__pycache__/
**/__pycache__/
*.pyc
*.pyo

# Databases
*.db
circuit-fit.db
!backend/database/schema.sql

# Logs
*.log
backend/*.log

# OS
.DS_Store
**/.DS_Store
Thumbs.db

# IDE
.vscode/
.idea/
*.swp
*.swo

# Environment
.env
.env.local
.env.*.local

# Temporary
tmp/
temp/
*.tmp

# Generated data
data/analysis_outputs/*.csv
!data/analysis_outputs/README.md
```

---

## EXECUTION CHECKLIST

- [ ] 1. Create backup of repository
- [ ] 2. Create all new folders (Step 1)
- [ ] 3. Move backend files (Step 2)
- [ ] 4. Move frontend files (Step 3)
- [ ] 5. Move data files (Step 4)
- [ ] 6. Move assets (Step 5)
- [ ] 7. Reorganize scripts (Step 6)
- [ ] 8. Reorganize documentation (Step 7)
- [ ] 9. Archive old docs (Step 8)
- [ ] 10. Create README files (Step 9)
- [ ] 11. Update frontend config references
- [ ] 12. Update all import statements
- [ ] 13. Update .gitignore
- [ ] 14. Test backend API
- [ ] 15. Test frontend application
- [ ] 16. Update documentation links
- [ ] 17. Commit changes

---

## BENEFITS OF NEW STRUCTURE

✅ **Clear separation of concerns**
- Backend, frontend, data, scripts, docs all clearly separated

✅ **Scalable organization**
- Each page component in its own folder with CSS
- Scripts organized by purpose
- Documentation organized by type

✅ **Easy navigation**
- No more searching for files
- Related files grouped together
- Logical folder hierarchy

✅ **Professional appearance**
- Industry-standard structure
- Easy for new developers to understand
- Clear project organization

✅ **Better maintainability**
- Related files stay together
- Easier to find and update
- Clear ownership of folders

---

## NEXT STEPS

Would you like me to:
1. Execute the reorganization automatically?
2. Start with just backend/frontend first?
3. Generate the README files for each folder?
