# File Cleanup Plan

## ✅ KEEP - Core Product Files

### Working Scripts (Production)
- **build_features_tiered.py** - KEEP - Builds Tier 1 features (12 variables)
- **run_tier1_efa.py** - KEEP - Runs factor analysis
- **validate_tier1_for_product.py** - KEEP - Validation & track profiles
- **demonstrate_factor_prediction.py** - KEEP - Shows how prediction works

### Data Files (Output)
- **data/analysis_outputs/all_races_tier1_features.csv** - KEEP - Feature matrix
- **data/analysis_outputs/tier1_factor_scores.csv** - KEEP - Factor scores
- **data/analysis_outputs/tier1_factor_loadings.csv** - KEEP - Factor structure
- **data/analysis_outputs/track_demand_profiles_tier1.csv** - KEEP - Track profiles
- **data/analysis_outputs/driver_average_scores_tier1.csv** - KEEP - Driver averages
- **data/analysis_outputs/tier1_scree_plot.png** - KEEP - Visualization
- **data/analysis_outputs/tier1_loadings_heatmap.png** - KEEP - Visualization
- **data/analysis_outputs/track_demand_profiles.png** - KEEP - Visualization
- **data/analysis_outputs/prediction_diagnostics.png** - KEEP - Validation viz

### Documentation (Essential)
- **FINAL_4_FACTOR_MODEL.md** - KEEP - Complete model documentation
- **TIER1_VALIDATION_RESULTS.md** - KEEP - Validation results
- **RESEARCH_STATUS_AND_DECISION_POINTS.md** - KEEP - Decision rationale
- **NEXT_STEPS10.27.md** - KEEP - Implementation roadmap

### Reference Documentation
- **DATA_DICTIONARY.md** - KEEP - Data source reference
- **.claude/Analysis_Setup/TIER1_EFA_RESULTS.md** - KEEP - Detailed EFA results
- **.claude/Analysis_Setup/VARIABLE_DEF.md** - KEEP - Variable definitions
- **.claude/Analysis_Setup/circuit_fit_research_methodology.md** - KEEP - Methodology
- **.claude/Analysis_Setup/five_factor_racing_model.md** - KEEP - Original hypothesis

---

## 🗑️ DELETE - Outdated/Experimental Files

### Deprecated Scripts
- **build_telemetry_features.py** - DELETE - Failed due to data quality issues
- **build_simple_telemetry_features.py** - DELETE - Failed, not needed for MVP
- **build_feature_matrices.py** - DELETE - Replaced by build_features_tiered.py
- **01_discover_skills_eda.py** - DELETE - Early exploration, superseded
- **02_summarize_eda_results.py** - DELETE - Early exploration, superseded
- **test_metrics.py** - DELETE - Validation already done, no longer needed
- **test_corner_count.py** - DELETE - Exploration script
- **test_lap_sampling.py** - DELETE - Exploration script
- **verify_correlations.py** - DELETE - Validation already done
- **diagnose_metrics.py** - DELETE - Debugging script

### Outdated Documentation
- **TELEMETRY_VARIABLES_PLAN.md** - DELETE - Telemetry abandoned for MVP
- **EDA_PLAN.md** - DELETE - Early planning, no longer relevant
- **PROJECT_PLAN.md** - DELETE - Outdated
- **READY_FOR_EDA.md** - DELETE - Early phase doc
- **DATA_COVERAGE_SUMMARY.md** - DELETE - Replaced by DATA_DICTIONARY.md
- **DATA_STRUCTURE.md** - DELETE - Redundant with DATA_DICTIONARY.md
- **POSITION_CHANGES_CALCULATION.md** - DELETE - Implementation detail, now in code
- **README (1).md** - DELETE - Duplicate/unclear

### Failed Outputs
- **data/analysis_outputs/all_races_telemetry_features.csv** - DELETE - Empty/failed
- **data/analysis_outputs/metrics_validation_summary.csv** - DELETE - Old validation

---

## 📁 ARCHIVE - Historical Reference (Move to archive/ folder)

- **.claude/Analysis_Setup/FACTOR_THEMES_AND_FEATURES.md** - Historical brainstorming
- **.claude/Analysis_Setup/FIVE_STEP_IMPLEMENTATION_PLAN.md** - Historical plan
- **.claude/Analysis_Setup/REPTRAK_MODEL_FOR_RACING.md** - Methodology reference
- **data/analysis_outputs_OLD/** - Old outputs (already archived)

---

## 📋 Final Clean File Structure

```
gazoo_racing_files/
│
├── 📄 FINAL_4_FACTOR_MODEL.md              ← MAIN DOCUMENTATION
├── 📄 TIER1_VALIDATION_RESULTS.md          ← VALIDATION PROOF
├── 📄 RESEARCH_STATUS_AND_DECISION_POINTS.md
├── 📄 NEXT_STEPS10.27.md                   ← IMPLEMENTATION PLAN
├── 📄 DATA_DICTIONARY.md                   ← DATA REFERENCE
│
├── 🐍 build_features_tiered.py             ← BUILD FEATURES
├── 🐍 run_tier1_efa.py                     ← RUN EFA
├── 🐍 validate_tier1_for_product.py        ← VALIDATE & PROFILES
├── 🐍 demonstrate_factor_prediction.py     ← PREDICTION DEMO
│
├── data/
│   ├── analysis_outputs/
│   │   ├── all_races_tier1_features.csv         ← FEATURE MATRIX
│   │   ├── tier1_factor_scores.csv              ← FACTOR SCORES
│   │   ├── tier1_factor_loadings.csv            ← LOADINGS
│   │   ├── track_demand_profiles_tier1.csv      ← TRACK PROFILES
│   │   ├── driver_average_scores_tier1.csv      ← DRIVER AVGS
│   │   ├── *.png                                 ← VISUALIZATIONS
│   │   └── [cleaned up old files]
│   │
│   ├── qualifying/          ← SOURCE DATA
│   ├── race_results/        ← SOURCE DATA
│   └── lap_timing/          ← SOURCE DATA
│
└── .claude/
    └── Analysis_Setup/
        ├── TIER1_EFA_RESULTS.md              ← DETAILED RESULTS
        ├── VARIABLE_DEF.md                   ← VARIABLE REFERENCE
        ├── circuit_fit_research_methodology.md
        ├── five_factor_racing_model.md
        └── [archive old brainstorming docs]
```

---

## Cleanup Commands

```bash
# Delete failed telemetry scripts
rm build_telemetry_features.py
rm build_simple_telemetry_features.py

# Delete old/redundant scripts
rm build_feature_matrices.py
rm 01_discover_skills_eda.py
rm 02_summarize_eda_results.py
rm test_metrics.py
rm test_corner_count.py
rm test_lap_sampling.py
rm verify_correlations.py
rm diagnose_metrics.py

# Delete outdated docs
rm TELEMETRY_VARIABLES_PLAN.md
rm EDA_PLAN.md
rm PROJECT_PLAN.md
rm READY_FOR_EDA.md
rm DATA_COVERAGE_SUMMARY.md
rm DATA_STRUCTURE.md
rm POSITION_CHANGES_CALCULATION.md
rm "README (1).md"

# Delete failed outputs
rm data/analysis_outputs/all_races_telemetry_features.csv 2>/dev/null
rm data/analysis_outputs/metrics_validation_summary.csv 2>/dev/null

# Archive old brainstorming (optional)
mkdir -p .claude/Analysis_Setup/archive
mv .claude/Analysis_Setup/FACTOR_THEMES_AND_FEATURES.md .claude/Analysis_Setup/archive/
mv .claude/Analysis_Setup/FIVE_STEP_IMPLEMENTATION_PLAN.md .claude/Analysis_Setup/archive/
mv .claude/Analysis_Setup/REPTRAK_MODEL_FOR_RACING.md .claude/Analysis_Setup/archive/
```

---

## What Remains (Production Ready)

### Core Files: 8
1. FINAL_4_FACTOR_MODEL.md (main doc)
2. TIER1_VALIDATION_RESULTS.md (validation)
3. RESEARCH_STATUS_AND_DECISION_POINTS.md (rationale)
4. NEXT_STEPS10.27.md (roadmap)
5. DATA_DICTIONARY.md (data reference)
6. build_features_tiered.py (feature builder)
7. run_tier1_efa.py (EFA)
8. validate_tier1_for_product.py (validation)

### Data Files: 9 CSVs + 4 PNGs
- Feature matrix
- Factor scores
- Factor loadings
- Track profiles
- Driver averages
- Visualizations

### Supporting Docs: 4 (in .claude/Analysis_Setup/)
- TIER1_EFA_RESULTS.md
- VARIABLE_DEF.md
- circuit_fit_research_methodology.md
- five_factor_racing_model.md

**Total: ~25 essential files**

---

## Next: Product Requirements

After cleanup, create:
1. **PRODUCT_REQUIREMENTS.md** - What to build
2. **API_SPECIFICATION.md** - API endpoints
3. **DRIVER_REPORT_TEMPLATE.md** - Report format
4. **DEPLOYMENT_GUIDE.md** - How to deploy

Execute cleanup now?
