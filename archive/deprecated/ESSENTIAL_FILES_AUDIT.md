# Essential Files Audit & Cleanup Plan

**Generated:** 2025-11-02
**Repository:** hackthetrack-master
**Total Size:** ~2.3GB
**Total Files:** 6,882

## Executive Summary

The repository contains **738MB of build artifacts** and **1.5GB of telemetry data**. This audit identifies:
- ✅ Essential files to KEEP
- ⚠️ Files to REVIEW/ARCHIVE
- ❌ Files to DELETE immediately

---

## 1. ESSENTIAL FILES (KEEP)

### 1.1 Core Application - Backend (15 files)
```
backend/
├── main.py                           # FastAPI entry point
├── requirements.txt                  # Python dependencies
├── api/
│   └── index.py                     # API index/routing
├── app/
│   ├── __init__.py
│   ├── models.py                    # Data models
│   ├── api/
│   │   ├── __init__.py
│   │   └── routes.py                # API endpoints
│   └── services/
│       ├── __init__.py
│       ├── ai_strategy.py           # AI strategy logic
│       ├── data_loader.py           # Data loading utilities
│       ├── factor_analyzer.py       # Factor analysis
│       ├── improve_predictor.py     # Performance predictions
│       ├── race_log_processor.py    # Race log processing
│       └── telemetry_processor.py   # Telemetry processing
└── database/
    ├── __init__.py
    ├── connection.py                # Database connection
    └── schema.sql                   # Database schema
```

### 1.2 Core Application - Frontend (30 files)
```
frontend/
├── package.json                     # Node dependencies
├── package-lock.json                # Locked dependencies
├── vite.config.js                   # Vite configuration
├── tailwind.config.js               # Tailwind CSS config
├── postcss.config.js                # PostCSS config
├── eslint.config.js                 # ESLint config
├── index.html                       # HTML entry point
├── README.md                        # Frontend documentation
├── public/
│   ├── vite.svg
│   └── track_maps/
│       ├── barber.png
│       └── cota.png
└── src/
    ├── main.jsx                     # React entry point
    ├── App.jsx                      # Main app component
    ├── App.css
    ├── index.css
    ├── context/
    │   └── SelectionContext.jsx    # React context
    ├── components/
    │   ├── Navigation.jsx
    │   ├── Navigation.css
    │   ├── SpeedTraceChart.jsx
    │   ├── SpeedTraceChart.css
    │   └── shared/
    │       ├── DriverSelector.jsx
    │       ├── PercentileBadge.jsx
    │       ├── StatCard.jsx
    │       └── StatGroup.jsx
    ├── pages/
    │   ├── Overview.jsx
    │   ├── Overview.css
    │   ├── Skills.jsx
    │   ├── Skills.css
    │   ├── Improve.jsx
    │   ├── Improve.css
    │   ├── RaceLog.jsx
    │   ├── RaceLog.css
    │   ├── TelemetryComparison.jsx
    │   ├── TelemetryComparison.css
    │   ├── TrackIntelligence.jsx
    │   ├── TrackIntelligence.css
    │   ├── StrategyChat.jsx
    │   └── StrategyChat.css
    ├── services/
    │   └── api.js                   # API client
    └── data/
        └── dashboardData.json       # Static dashboard data
```

### 1.3 Essential Data Files (~1.5GB)
```
data/
├── Telemetry/                       # 1.5GB - ESSENTIAL racing data
│   ├── barber_r1_wide.csv          (114MB)
│   ├── barber_r2_wide.csv          (116MB)
│   ├── cota_r1_wide.csv            (167MB) ✅
│   ├── cota_r2_wide.csv            (161MB)
│   ├── roadamerica_r1_wide.csv     (86MB)
│   ├── roadamerica_r2_wide.csv     (107MB)
│   ├── sonoma_r1_wide.csv          (258MB)
│   └── sonoma_r2_wide.csv          (129MB)
├── lap_timing/                      # 2.5MB - Lap time data
│   └── [various track lap data]
├── race_results/                    # 1.6MB - Race results
│   ├── best_10_laps/
│   ├── provisional_results/
│   └── analysis_endurance/
├── qualifying/                      # 60KB - Qualifying data
└── analysis_outputs/                # 1.2MB - Generated analysis
    └── [feature CSV files]
```

### 1.4 Track Maps (4.3MB)
```
track_maps/
├── barber.png
├── cota.png
├── roadamerica.png (if exists)
├── sonoma.png (if exists)
├── Barber_Circuit_Map.pdf
├── COTA_Circuit_Map.pdf
├── Road_America_Map.pdf
├── Sebring_Track_Sector_Map.pdf
├── Sonoma_Map.pdf
└── VIR_map.pdf
```

### 1.5 Configuration & Scripts (13 files)
```
scripts/
├── README.md
├── analyze_score_distributions.py
├── analyze_telemetry_factors.py
├── build_features_tiered.py
├── demonstrate_factor_prediction.py
├── extract_telemetry_features.py
├── generate_dashboard_data.py
├── generate_sample_data.py
├── load_data.py
├── run_tier1_efa.py
├── test_telemetry_model_improvement.py
├── validate_lodo_cv.py
└── validate_tier1_for_product.py
```

### 1.6 Root Configuration Files
```
├── .gitignore                       # Git ignore rules
├── vercel.json                      # Vercel deployment config
├── circuit-fit.db                   # SQLite database (340MB)
└── README.md                        # Main documentation
```

### 1.7 Essential Documentation (Keep 5 files max)
```
├── README.md                        # Main project docs
├── PROJECT_ROADMAP.md               # Development roadmap
├── PRODUCT_REQUIREMENTS.md          # Product requirements
├── DATA_DICTIONARY.md               # Data definitions
└── FINAL_4_FACTOR_MODEL.md          # Statistical model docs
```

---

## 2. FILES TO DELETE IMMEDIATELY (❌)

### 2.1 Duplicate Files
```
❌ data/Telemetry/cota_r1_wide (1).csv    # 167MB - DUPLICATE of cota_r1_wide.csv
```

### 2.2 Build Artifacts (738MB total)
```
❌ backend/venv/                          # 405MB - Python virtual environment
❌ frontend/node_modules/                 # 333MB - Node dependencies
❌ frontend/dist/                         # Build output
❌ backend/__pycache__/                   # Python cache
❌ backend/app/__pycache__/
❌ backend/app/api/__pycache__/
❌ backend/app/services/__pycache__/
❌ backend/database/__pycache__/
```

### 2.3 System Files
```
❌ .DS_Store                              # macOS metadata
❌ **/.DS_Store                           # All DS_Store files
```

### 2.4 Duplicate/Nested Frontend Structure
```
❌ frontend/src/pages/frontend/           # Incorrectly nested structure
```

### 2.5 Log Files
```
❌ backend/backend.log                    # Application logs
❌ **/*.log                               # All log files
```

### 2.6 Old Documentation (Keep latest versions only)
```
❌ REPOSITORY_CLEANUP_ANALYSIS.md         # Old cleanup doc (replaced by this)
❌ STATISTICAL_FIXES_IMPLEMENTATION_GUIDE.md
❌ STATISTICAL_ISSUES_VISUAL.txt
❌ STATISTICAL_REVIEW_INDEX.md
❌ STATISTICAL_REVIEW_README.md
❌ STATISTICAL_REVIEW_SUMMARY.md
❌ STATISTICAL_VALIDATION_REPORT.md
❌ TIER1_VALIDATION_RESULTS.md
❌ SKILLS_INTEGRATION_FIX.md
❌ VERCEL_DEPLOYMENT.md
```

---

## 3. FILES TO REVIEW/ARCHIVE (⚠️)

### 3.1 Archive Directory (100KB)
```
⚠️ archive/                               # Already archived documentation
   └── documentation/
       ├── PROJECT_SUMMARY.md
       ├── RACE_LOG_BACKEND_STATUS.md
       ├── NEXT_STEPS10.27.md
       ├── RESEARCH_STATUS_AND_DECISION_POINTS.md
       ├── FILE_CLEANUP_PLAN.md
       ├── IMPLEMENTATION_PLAN.md
       └── DASHBOARD_DESIGN_BRIEF.md

RECOMMENDATION: Keep as-is (already archived)
```

### 3.2 Design Files (44KB)
```
⚠️ design/
   ├── racing-dashboard-design.skill
   ├── components.md
   └── coach_agent/
       └── AI_COACHING_LIBRARY.md

RECOMMENDATION: Keep - contains UI/UX specs
```

### 3.3 Specs Directory (136KB)
```
⚠️ specs/
   ├── circuit-fit-dashboard-spec.md
   ├── circuit-fit-database-spec.md
   ├── IMPROVE_PAGE_QUICK_REFERENCE.md
   ├── IMPROVE_PAGE_SUMMARY.md
   ├── IMPROVE_PAGE_README.md
   ├── IMPROVE_PAGE_STATISTICAL_VALIDATION.md
   └── IMPROVE_PAGE_CORRECTED_IMPLEMENTATION.py

RECOMMENDATION: Consolidate into single spec document
```

### 3.4 Examples Directory (188KB)
```
⚠️ examples/
   └── [example files]

RECOMMENDATION: Review if still needed for demos
```

### 3.5 Mock Data Files
```
⚠️ frontend/src/data/mockData.js
⚠️ frontend/src/data/plan_for_10_29.md

RECOMMENDATION: Remove mockData.js (use real API), archive plan
```

### 3.6 Database Files
```
⚠️ circuit-fit.db                         # 340MB - Root level
⚠️ backend/circuit-fit.db                 # Duplicate?

RECOMMENDATION: Keep only ONE copy in backend/
```

---

## 4. CLEANUP COMMANDS

### Phase 1: Delete Build Artifacts (738MB savings)
```bash
# Remove Python virtual environment
rm -rf backend/venv/

# Remove Node modules
rm -rf frontend/node_modules/

# Remove frontend build output
rm -rf frontend/dist/

# Remove Python cache
find . -type d -name "__pycache__" -exec rm -rf {} +
find . -type f -name "*.pyc" -delete
find . -type f -name "*.pyo" -delete
```

### Phase 2: Delete System Files
```bash
# Remove macOS metadata
find . -name ".DS_Store" -delete

# Remove log files
find . -name "*.log" -delete
```

### Phase 3: Remove Duplicate Files (167MB savings)
```bash
# Remove duplicate telemetry file
rm "data/Telemetry/cota_r1_wide (1).csv"

# Remove duplicate database (if confirmed)
# Check which one is being used first!
# rm backend/circuit-fit.db  # OR rm circuit-fit.db
```

### Phase 4: Remove Nested Frontend Directory
```bash
rm -rf frontend/src/pages/frontend/
```

### Phase 5: Archive Old Documentation
```bash
mkdir -p archive/old_documentation
mv STATISTICAL_*.md archive/old_documentation/
mv TIER1_VALIDATION_RESULTS.md archive/old_documentation/
mv SKILLS_INTEGRATION_FIX.md archive/old_documentation/
mv VERCEL_DEPLOYMENT.md archive/old_documentation/
mv REPOSITORY_CLEANUP_ANALYSIS.md archive/old_documentation/
```

### Phase 6: Remove Mock/Test Data
```bash
rm frontend/src/data/mockData.js
mv frontend/src/data/plan_for_10_29.md archive/old_documentation/
```

---

## 5. UPDATE .gitignore

Add these entries to ensure build artifacts aren't committed:
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

# OS
.DS_Store
**/.DS_Store

# IDE
.vscode/
.idea/
```

---

## 6. FINAL FILE STRUCTURE (After Cleanup)

```
hackthetrack-master/
├── .gitignore
├── README.md
├── PROJECT_ROADMAP.md
├── PRODUCT_REQUIREMENTS.md
├── DATA_DICTIONARY.md
├── FINAL_4_FACTOR_MODEL.md
├── ESSENTIAL_FILES_AUDIT.md (this file)
├── vercel.json
│
├── backend/                         # ~50KB source code
│   ├── main.py
│   ├── requirements.txt
│   ├── circuit-fit.db              # 340MB - SQLite database
│   ├── api/
│   ├── app/
│   └── database/
│
├── frontend/                        # ~150KB source code
│   ├── package.json
│   ├── package-lock.json
│   ├── vite.config.js
│   ├── tailwind.config.js
│   ├── public/
│   └── src/
│
├── data/                            # ~1.5GB
│   ├── Telemetry/                  # Raw telemetry data
│   ├── lap_timing/
│   ├── race_results/
│   ├── qualifying/
│   └── analysis_outputs/
│
├── track_maps/                      # 4.3MB
│   └── [track images and PDFs]
│
├── scripts/                         # 192KB
│   └── [analysis scripts]
│
├── archive/                         # 100KB
│   ├── documentation/
│   └── old_documentation/
│
├── design/                          # 44KB
│   └── [design specs]
│
├── specs/                           # 136KB (to consolidate)
│   └── [technical specs]
│
└── examples/                        # 188KB (review needed)
    └── [example files]
```

---

## 7. SIZE COMPARISON

| Category | Before | After | Savings |
|----------|--------|-------|---------|
| Build artifacts | 738MB | 0MB | 738MB |
| Duplicate files | 167MB | 0MB | 167MB |
| System files | ~5MB | 0MB | 5MB |
| Old docs | ~200KB | 0KB | 200KB |
| **Total** | **~2.3GB** | **~1.5GB** | **~910MB** |

**Repository will be 40% smaller** after cleanup!

---

## 8. EXECUTION PLAN

### Step 1: Backup (Safety First)
```bash
# Create backup of entire repo
cd /Users/justingrosz/Documents/AI-Work/
tar -czf hackthetrack-backup-$(date +%Y%m%d).tar.gz hackthetrack-master/
```

### Step 2: Verify Database Location
```bash
# Check which database is being used
grep -r "circuit-fit.db" backend/
grep -r "circuit-fit.db" frontend/
```

### Step 3: Execute Cleanup (Run commands from Phase 1-6)

### Step 4: Rebuild Dependencies When Needed
```bash
# Backend: Recreate venv when needed
cd backend
python -m venv venv
source venv/bin/activate  # or venv/Scripts/activate on Windows
pip install -r requirements.txt

# Frontend: Reinstall when needed
cd frontend
npm install
```

### Step 5: Test Application
```bash
# Test backend
cd backend
source venv/bin/activate
python main.py

# Test frontend
cd frontend
npm run dev
```

### Step 6: Commit Clean State
```bash
git add .
git commit -m "refactor: cleanup repository structure and remove build artifacts

- Remove 738MB of build artifacts (venv, node_modules, dist)
- Remove 167MB duplicate telemetry file
- Archive old documentation
- Update .gitignore to prevent future commits of build artifacts
- Consolidate database to backend directory
- Remove system files (.DS_Store, logs)

Total size reduction: ~910MB (40% smaller)"
```

---

## 9. MAINTENANCE GUIDELINES

### Never Commit:
- ❌ `backend/venv/` or any virtual environment
- ❌ `frontend/node_modules/` or any dependencies
- ❌ `frontend/dist/` or any build output
- ❌ `__pycache__/` or `.pyc` files
- ❌ `.DS_Store` or system files
- ❌ `*.log` files
- ❌ Database files (except schema)

### Always Commit:
- ✅ Source code (`.py`, `.js`, `.jsx`, `.css`)
- ✅ Configuration files (`package.json`, `requirements.txt`, configs)
- ✅ Documentation (`.md` files)
- ✅ Database schema (`.sql` files)
- ✅ Essential data files (CSV files in `data/`)

### Before Committing:
```bash
# Check what you're about to commit
git status
git diff

# Ensure no large files
git add .
git status | grep -i "MB"

# If you see large files, investigate before committing
```

---

## 10. QUESTIONS TO RESOLVE

1. **Database Location**: Is `circuit-fit.db` in root or backend actively used?
   - Check: `backend/app/database/connection.py`
   - Decision: Keep ONE copy in `backend/`

2. **Examples Directory**: Are the files in `examples/` still needed?
   - Review: Check if referenced in documentation
   - Decision: Archive or delete

3. **Specs Consolidation**: Can all IMPROVE_PAGE_* docs be merged?
   - Review: Content overlap
   - Decision: Create single `IMPROVE_PAGE_SPECIFICATION.md`

4. **Mock Data**: Is `mockData.js` still used?
   - Check: `grep -r "mockData" frontend/src/`
   - Decision: Remove if using real API

---

## SUMMARY

**Total Files:** 6,882 → ~100 essential source files
**Total Size:** 2.3GB → 1.5GB (mostly essential telemetry data)
**Cleanup Savings:** ~910MB (40% reduction)

**Next Steps:**
1. Review questions in Section 10
2. Execute backup (Step 1)
3. Run cleanup commands (Phases 1-6)
4. Update .gitignore
5. Test application
6. Commit clean state
