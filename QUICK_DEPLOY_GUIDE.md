# Quick Deployment Guide - Factor Mapping Fix

**READY TO DEPLOY** ✅ | **ESTIMATED TIME**: 10 minutes

---

## TL;DR - What You Need to Know

✅ **The code changes are SAFE**
✅ **No runtime errors will occur**
✅ **Overall score calculation remains mathematically valid**
🔄 **Data files MUST be regenerated** (3 files)

---

## One-Command Deploy (Run from repository root)

```bash
cd /Users/justingrosz/Documents/AI-Work/hackthetrack-master

# Step 1: Regenerate database (2-5 min)
python3 -m backend.app.services.factor_analyzer

# Step 2: Export to JSON (30 sec)
python3 export_db_to_json.py
python3 backend/scripts/export_factor_breakdowns.py

# Step 3: Verify (30 sec)
python3 backend/scripts/verify_data_completeness.py

# Step 4: Optional - Run validation (1 min)
python3 validate_4factor_model.py
```

---

## Expected Console Output

### Step 1: factor_analyzer.py
```
Reflected factor_2_score (multiplied by -1 due to negative loadings)
Reflected factor_3_score (multiplied by -1 due to negative loadings)
Processing driver #2...
Processing driver #3...
...
All factors calculated and stored with reflected scores!
```
✅ **Success**: "All factors calculated and stored"

### Step 2a: export_db_to_json.py
```
✅ Exported 34 drivers to backend/data/driver_factors.json
   Total factor records: 544
   File size: 204.0 KB
```
✅ **Success**: File size ~204 KB

### Step 2b: export_factor_breakdowns.py
```
✅ Exported REAL factor breakdowns: .../factor_breakdowns.json
   Drivers: 39
   Factors: 4
   Variables: 10
   Size: 116.0 KB
```
✅ **Success**: File size ~116 KB

### Step 3: verify_data_completeness.py
```
✓ driver_factors.json: 34 drivers
✓ factor_breakdowns.json: verified
```
✅ **Success**: All files present

---

## Files That Will Be Regenerated

| File | Location | Size | Generator |
|------|----------|------|-----------|
| **factor_breakdowns** (DB table) | `circuit-fit.db` | N/A | `factor_analyzer.py` |
| **driver_factors.json** | `backend/data/` | 204 KB | `export_db_to_json.py` |
| **factor_breakdowns.json** | `backend/data/` | 116 KB | `export_factor_breakdowns.py` |

---

## What Changed in factor_analyzer.py

```python
# OLD (INCORRECT):
FACTOR_MAPPING = {
    "factor_2": "racecraft",  # ❌ Wrong - factor_2 loads on speed
    "factor_3": "speed",      # ❌ Wrong - factor_3 loads on racecraft
}

FACTOR_VARIABLES = {
    "speed": {"factor_column": "factor_3_score"},      # ❌ Wrong column
    "racecraft": {"factor_column": "factor_2_score"},  # ❌ Wrong column
}

# NEW (CORRECT):
FACTOR_MAPPING = {
    "factor_2": "speed",      # ✅ Correct - factor_2 has 46.6% variance (speed)
    "factor_3": "racecraft",  # ✅ Correct - factor_3 has 14.9% variance (racecraft)
}

FACTOR_VARIABLES = {
    "speed": {"factor_column": "factor_2_score"},      # ✅ Correct column
    "racecraft": {"factor_column": "factor_3_score"},  # ✅ Correct column
}
```

---

## Why This Won't Break Anything

### The Math is Safe
```python
# data_loader.py uses VARIABLE NAMES (not factor numbers):
overall_score = (
    factor_scores["speed"]["score"] * 0.466 +        # Uses "speed" name
    factor_scores["racecraft"]["score"] * 0.149 +    # Uses "racecraft" name
    factor_scores["consistency"]["score"] * 0.291 +
    factor_scores["tire_management"]["score"] * 0.095
)
```

**Key Insight**: We only changed which factor column each variable name points to.
The overall score calculation uses variable names, so it remains valid.

---

## Troubleshooting

### Error: "ModuleNotFoundError: No module named 'backend'"
```bash
# Solution: Run from repository root
cd /Users/justingrosz/Documents/AI-Work/hackthetrack-master
export PYTHONPATH="${PYTHONPATH}:$(pwd)/backend"
python3 backend/app/services/factor_analyzer.py
```

### Error: "Database locked"
```bash
# Solution: Close any SQLite browser connections
# Then retry the command
```

### Verification Failed
```bash
# Check file sizes:
ls -lh backend/data/driver_factors.json        # Should be ~204 KB
ls -lh backend/data/factor_breakdowns.json     # Should be ~116 KB

# Check driver count:
python3 -c "import json; data = json.load(open('backend/data/driver_factors.json')); print(f'Drivers: {data[\"driver_count\"]}')"
```

---

## After Deployment - What to Expect

### Driver Factor Scores Will Change
- **Speed scores** will now reflect actual speed metrics (qualifying_pace, best_race_lap)
- **Racecraft scores** will now reflect racing metrics (positions_gained, position_changes)
- **Overall scores** will be recalculated but remain mathematically valid

### Example Change (Hypothetical)
```
Before Fix (INCORRECT):
  Driver #2:
    Speed: 75.2 (was reading factor_3 - wrong!)
    Racecraft: 82.4 (was reading factor_2 - wrong!)
    Overall: 67.8

After Fix (CORRECT):
  Driver #2:
    Speed: 82.4 (now reading factor_2 - correct!)
    Racecraft: 75.2 (now reading factor_3 - correct!)
    Overall: 72.1  (recalculated correctly)
```

---

## Optional: Update Documentation Comments

```bash
# Edit this file to fix outdated comments:
nano /Users/justingrosz/Documents/AI-Work/hackthetrack-master/backend/scripts/export_factor_breakdowns.py

# Lines 6-8 should read:
# - Factor 2 (SPEED): best_race_lap, avg_top10_pace, qualifying_pace
# - Factor 3 (RACECRAFT): positions_gained, position_changes
```

---

## Critical Pre-Flight Checks

- [ ] Currently in repository root directory
- [ ] Python 3 installed (`python3 --version`)
- [ ] SQLite database exists (`ls -lh circuit-fit.db`)
- [ ] No SQLite browser connections open
- [ ] Backend environment activated (if using venv)

---

## Post-Deployment Validation

```bash
# Quick smoke test
cd /Users/justingrosz/Documents/AI-Work/hackthetrack-master/backend

# Test data loader import
python3 -c "from app.services.data_loader import data_loader; print(f'Loaded {len(data_loader.drivers)} drivers')"

# Test factor analyzer import
python3 -c "from app.services.factor_analyzer import FACTOR_MAPPING; print(FACTOR_MAPPING)"
```

**Expected Output**:
```
Loaded 34 drivers
{'factor_1': 'consistency', 'factor_2': 'speed', 'factor_3': 'racecraft', 'factor_4': 'tire_management'}
```

---

## Timeline Breakdown

| Task | Time | Command |
|------|------|---------|
| Regenerate DB | 2-5 min | `python3 -m backend.app.services.factor_analyzer` |
| Export driver_factors.json | 10 sec | `python3 export_db_to_json.py` |
| Export factor_breakdowns.json | 20 sec | `python3 backend/scripts/export_factor_breakdowns.py` |
| Verify completeness | 5 sec | `python3 backend/scripts/verify_data_completeness.py` |
| Smoke test | 5 sec | Manual verification |
| **TOTAL** | **~5-8 min** | |

---

## Git Commit Message (After Validation)

```bash
git add backend/app/services/factor_analyzer.py
git add backend/data/driver_factors.json
git add backend/data/factor_breakdowns.json

git commit -m "fix(analytics): correct factor mapping for speed and racecraft

- Swap factor_2 (racecraft → speed) and factor_3 (speed → racecraft)
- Align variable names with actual PCA factor loadings
- Regenerate driver_factors.json and factor_breakdowns.json
- No breaking changes - overall score calculation uses variable names

Refs: FACTOR_MAPPING_VERIFICATION_REPORT.md"
```

---

**Ready to deploy? Run the commands above and you're good to go!** 🚀

For detailed analysis, see: `FACTOR_MAPPING_VERIFICATION_REPORT.md`
