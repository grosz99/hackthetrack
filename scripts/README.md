# Development Scripts

This directory contains Python scripts used for data processing, feature engineering, and analysis during development.

## Scripts

### Feature Engineering

**`build_features_tiered.py`**
- Builds tiered feature sets from raw racing data
- Generates features for factor analysis
- Outputs to `data/analysis_outputs/`
- Usage: `python scripts/build_features_tiered.py`

**`generate_dashboard_data.py`**
- Generates pre-calculated dashboard data
- Creates `frontend/src/data/dashboardData.json`
- Usage: `python scripts/generate_dashboard_data.py`

### Factor Analysis

**`run_tier1_efa.py`**
- Runs Exploratory Factor Analysis (EFA) on Tier 1 features
- Generates factor loadings and scores
- Outputs factor analysis results
- Usage: `python scripts/run_tier1_efa.py`

**`validate_tier1_for_product.py`**
- Validates Tier 1 features for production use
- Checks data quality and model performance
- Usage: `python scripts/validate_tier1_for_product.py`

### Demonstrations

**`demonstrate_factor_prediction.py`**
- Demonstrates factor-based finish position prediction
- Shows model performance metrics
- Usage: `python scripts/demonstrate_factor_prediction.py`

## Dependencies

All scripts require the Python dependencies listed in `backend/requirements.txt`:

```bash
cd backend
pip install -r requirements.txt
```

## Data Requirements

These scripts expect the following data structure:

```
data/
├── lap_timing/          # Lap timing data
├── race_results/        # Race results data
├── qualifying/          # Qualifying data
└── analysis_outputs/    # Generated feature files
```

## Running Scripts

From the project root:

```bash
# Build features
python scripts/build_features_tiered.py

# Generate dashboard data
python scripts/generate_dashboard_data.py

# Run factor analysis
python scripts/run_tier1_efa.py

# Validate for production
python scripts/validate_tier1_for_product.py
```

## Notes

- These scripts are for **development and data regeneration** only
- They are **not** part of the production application
- Output files are committed to the repository for production use
- Re-run these scripts when source data changes

---

*Last Updated: November 2, 2025*
