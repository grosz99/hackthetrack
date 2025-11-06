# Repository Cleanup Analysis

**Date**: November 2, 2025
**Total Tracked Files**: 217

## Executive Summary

After reviewing the repository, here's a breakdown of what's essential vs. what can be removed or archived to maintain a clean, production-ready codebase.

---

## ✅ KEEP - Essential Production Files

### Application Code (Core)
```
backend/
├── api/index.py              # Vercel serverless entry point
├── app/
│   ├── __init__.py
│   ├── api/routes.py         # API endpoints
│   ├── models.py             # Pydantic models
│   └── services/
│       ├── ai_strategy.py    # AI strategy agent
│       ├── data_loader.py    # Data loading service
│       ├── factor_analyzer.py # RepTrak normalization
│       └── race_log_processor.py # Race log processing
├── main.py                   # FastAPI app
└── requirements.txt          # Python dependencies

frontend/
├── src/
│   ├── components/           # React components
│   ├── pages/               # Page components
│   ├── services/api.js      # API client
│   └── data/dashboardData.json # Pre-calculated data
├── package.json
└── vite.config.js

circuit-fit.db                # RepTrak-normalized factor scores
vercel.json                   # Vercel deployment config
```

### Essential Documentation
```
README_APP.md                 # Main application README
PRODUCT_REQUIREMENTS.md       # Product specs
VERCEL_DEPLOYMENT.md         # Deployment guide
.gitignore                   # Git ignore rules
```

### Data Files (KEEP - Per User Request)
```
data/
├── analysis_outputs/        # All factor analysis results
├── lap_timing/             # Lap timing data
├── race_results/           # Race results
└── qualifying/             # Qualifying data
```

### Research Files (KEEP - Per User Request)
```
.claude/                     # All Claude research docs
FINAL_4_FACTOR_MODEL.md     # 4-factor model documentation
TIER1_VALIDATION_RESULTS.md # Validation results
DATA_DICTIONARY.md          # Data definitions
```

---

## 🗑️ REMOVE - Outdated/Redundant Files

### Outdated Status Documents
```
❌ NEXT_STEPS10.27.md          # Dated to Oct 27 - outdated
❌ RACE_LOG_BACKEND_STATUS.md  # Status doc from Nov 1 - outdated
❌ FILE_CLEANUP_PLAN.md        # Old cleanup plan - superseded
❌ IMPLEMENTATION_PLAN.md      # Old implementation plan
❌ frontend/src/data/plan_for_10_29.md # Dated planning doc
```

**Reason**: These are point-in-time status documents that are now obsolete. Current status should be in README or GitHub issues.

### Redundant/Overlapping Docs
```
❌ DASHBOARD_DESIGN_BRIEF.md   # Design details now in PRODUCT_REQUIREMENTS
❌ PROJECT_SUMMARY.md          # Redundant with README_APP.md
❌ RESEARCH_STATUS_AND_DECISION_POINTS.md # Historical - decisions made
```

**Reason**: Information is duplicated in other docs or decisions have been finalized.

### Development Scripts (Consider Archiving)
```
⚠️  build_features_tiered.py         # Data processing script
⚠️  demonstrate_factor_prediction.py  # Demo script
⚠️  generate_dashboard_data.py       # Data generation script
⚠️  run_tier1_efa.py                 # EFA analysis script
⚠️  validate_tier1_for_product.py    # Validation script
```

**Recommendation**: Move to `scripts/` directory or archive. These are development tools, not production code.

### Deployment Configs
```
⚠️  netlify.toml              # Netlify config (using Vercel now?)
```

**Reason**: If using Vercel exclusively, netlify.toml is unnecessary.

### Unused Root Files
```
❌ requirements.txt (root)     # Only has 'pandas' - use backend/requirements.txt
```

**Reason**: Backend has complete requirements.txt. Root file is incomplete.

---

## 📦 ARCHIVE - Move to `/archive` or `/docs/archive`

### Historical Documentation
```
DASHBOARD_DESIGN_BRIEF.md
RESEARCH_STATUS_AND_DECISION_POINTS.md
FILE_CLEANUP_PLAN.md
IMPLEMENTATION_PLAN.md
NEXT_STEPS10.27.md
RACE_LOG_BACKEND_STATUS.md
```

### Development Scripts
```
scripts/
├── build_features_tiered.py
├── demonstrate_factor_prediction.py
├── generate_dashboard_data.py
├── run_tier1_efa.py
└── validate_tier1_for_product.py
```

---

## 🔧 RECOMMENDED ACTIONS

### 1. Update .gitignore
Add the following to ignore unnecessary files:
```
# Development artifacts
*.log
.DS_Store
netlify.toml

# Build outputs
frontend/dist/
frontend/.npm-cache/
backend/database/

# Local development
circuit-fit.db.backup
*.db-journal
```

### 2. Create Archive Structure
```bash
mkdir -p archive/documentation
mkdir -p archive/scripts
mkdir -p scripts
```

### 3. Move Files
```bash
# Archive outdated docs
mv NEXT_STEPS10.27.md archive/documentation/
mv RACE_LOG_BACKEND_STATUS.md archive/documentation/
mv FILE_CLEANUP_PLAN.md archive/documentation/
mv IMPLEMENTATION_PLAN.md archive/documentation/
mv DASHBOARD_DESIGN_BRIEF.md archive/documentation/
mv PROJECT_SUMMARY.md archive/documentation/
mv RESEARCH_STATUS_AND_DECISION_POINTS.md archive/documentation/

# Move dev scripts
mv build_features_tiered.py scripts/
mv demonstrate_factor_prediction.py scripts/
mv generate_dashboard_data.py scripts/
mv run_tier1_efa.py scripts/
mv validate_tier1_for_product.py scripts/
```

### 4. Delete Unnecessary Files
```bash
# Remove root requirements.txt (use backend/requirements.txt)
rm requirements.txt

# Remove netlify.toml if not using Netlify
rm netlify.toml
```

### 5. Update README_APP.md
Rename to `README.md` and update with:
- Current deployment status
- Setup instructions
- Architecture overview
- Link to PRODUCT_REQUIREMENTS.md for detailed specs

---

## 📊 Before/After Summary

### Current State
- 217 tracked files
- Mix of code, docs, data, and historical artifacts
- Root directory cluttered with 15+ markdown files
- No clear separation between production and development

### After Cleanup
- ~195 tracked files (removing ~22 files)
- Clear separation: `/archive`, `/scripts`, clean root
- Production-ready structure
- Easy to navigate for new developers

---

## ⚠️ Important Notes

1. **DO NOT DELETE**:
   - Any files in `data/` directory (per user request)
   - Any files in `.claude/` directory (research docs)
   - `FINAL_4_FACTOR_MODEL.md` (core research)
   - `TIER1_VALIDATION_RESULTS.md` (validation evidence)
   - `DATA_DICTIONARY.md` (reference)

2. **Archive, Don't Delete**:
   - Historical docs may be useful for reference
   - Keep in `/archive` directory with README explaining context

3. **Scripts**:
   - Move to `/scripts` directory
   - Add README in scripts/ explaining each script's purpose
   - These are valuable for regenerating data if needed

---

## 🎯 Next Steps

1. Review this analysis
2. Confirm which files to archive vs. delete
3. Create archive structure
4. Execute file moves
5. Update .gitignore
6. Commit cleanup with descriptive message
7. Update main README.md
