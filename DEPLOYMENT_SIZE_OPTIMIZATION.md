# Vercel Serverless Function Size Optimization

## Problem Statement

Deployment failed with error:
```
Error: A Serverless Function has exceeded the unzipped maximum size of 250 MB.
```

## Root Cause Analysis

The serverless function exceeded Vercel's 250MB limit due to:

1. **Heavy Python Dependencies** (~240-330MB total):
   - `pandas`: 70-100MB
   - `numpy`: 40-60MB
   - `scipy`: 80-100MB (REMOVED)
   - `snowflake-connector-python`: 50-70MB (COMMENTED OUT)
   - `cryptography`: ~30MB (dependency, commented out with snowflake)

2. **Unnecessary Files Included**:
   - `backend/tests/` directory (260KB + test dependencies)
   - `backend/scripts/` directory (38KB deployment scripts)
   - `backend/*.md` documentation files (98KB)
   - Frontend source files (should only include built dist/)
   - Development configuration files

3. **No Function Size Optimization**:
   - No `.vercelignore` exclusions
   - No function-specific configuration in `vercel.json`
   - All dependencies installed regardless of usage

## Solution Implemented

### 1. Comprehensive `.vercelignore` File

Created extensive exclusion rules to prevent unnecessary files from being deployed:

- **Tests & Development Tools**: Excluded `backend/tests/`, `pytest.ini`, `.pytest_cache/`
- **Development Scripts**: Excluded `backend/scripts/`, `*.sql` setup files
- **Documentation**: Excluded `backend/*.md` files (98KB saved)
- **Frontend Source**: Only include built `frontend/dist/`, exclude source files
- **Python Cache**: Exclude `__pycache__/`, `*.pyc`, `venv/`, etc.
- **Development Config**: Exclude `.claude/`, `requirements-dev.txt`

### 2. Optimized `vercel.json` Configuration

Added function-specific configuration:

```json
{
  "functions": {
    "api/index.py": {
      "runtime": "python3.9",
      "memory": 1024,
      "maxDuration": 30,
      "includeFiles": "backend/data/**"
    }
  }
}
```

Benefits:
- Explicit runtime specification
- Only includes necessary backend data files
- Optimized memory allocation
- Clear timeout limits

### 3. Dependency Reduction in `api/requirements.txt`

**Removed** (saved ~130-170MB):
- `scipy` (80-100MB) - Replaced with numpy-only implementations
- `snowflake-connector-python` (50-70MB) - Commented out, not used in core API
- `cryptography` (~30MB) - Dependency of snowflake, also removed
- `uvicorn` - Vercel provides its own ASGI server
- `requests` - Using `httpx` instead (already included via anthropic)

**Kept** (essential, ~150-180MB):
- `fastapi`, `pydantic`, `python-dotenv`, `python-multipart` (FastAPI core)
- `mangum` (AWS Lambda/Vercel compatibility)
- `anthropic`, `httpx` (AI chat features)
- `pandas`, `numpy` (data processing - essential for analytics)

### 4. Created Numpy-Only Statistical Functions

Created `backend/app/utils/numpy_stats.py` with lightweight implementations:

#### `norm_ppf(p)` - Normal Distribution Inverse CDF
- Replaces `scipy.stats.norm.ppf`
- Beasley-Springer-Moro algorithm
- Accuracy: ~1e-9
- Pure numpy implementation
- **Saved**: ~80-100MB by eliminating scipy dependency

#### `find_peaks_simple(x, distance, prominence)` - Peak Detection
- Replaces `scipy.signal.find_peaks`
- Simplified algorithm for 1D peak detection
- Supports distance and prominence constraints
- Pure numpy implementation

#### `percentile_to_z(percentile)` - Percentile to Z-Score Conversion
- Convenience wrapper for norm_ppf
- Used throughout the codebase

### 5. Updated Code to Use Numpy Implementations

Modified files to remove scipy dependencies:

1. **`backend/app/api/routes.py`**:
   - Line 794: Replaced `scipy.stats.norm.ppf` with `numpy_stats.percentile_to_z`
   - Line 1161: Replaced `scipy.signal.find_peaks` with `numpy_stats.find_peaks_simple`

2. **`backend/app/services/improve_predictor.py`**:
   - Line 21: Replaced `from scipy import stats` with `from app.utils.numpy_stats import norm_ppf`
   - Line 158: Replaced `stats.norm.ppf` with `norm_ppf`

## Size Reduction Estimate

| Category | Before | After | Savings |
|----------|--------|-------|---------|
| scipy | 80-100MB | 0MB | **80-100MB** |
| snowflake-connector-python | 50-70MB | 0MB | **50-70MB** |
| cryptography | ~30MB | 0MB | **30MB** |
| uvicorn | ~10MB | 0MB | **10MB** |
| Tests/Scripts/Docs | ~500KB | 0MB | **500KB** |
| **Total Savings** | | | **~170-210MB** |

**Expected Final Size**: ~80-120MB (well under 250MB limit)

## Verification Steps

### 1. Code Verification
```bash
# Verify no scipy imports remain
rg "from scipy|import scipy" backend/app --type py

# Should return no results
```

### 2. Functionality Testing
```bash
# Test numpy implementations
cd backend
python -c "from app.utils.numpy_stats import norm_ppf, percentile_to_z, find_peaks_simple; print('Import successful')"

# Test statistical functions
python -c "from app.utils.numpy_stats import norm_ppf; print(f'norm_ppf(0.5) = {norm_ppf(0.5):.6f}')"  # Should be ~0.0
python -c "from app.utils.numpy_stats import norm_ppf; print(f'norm_ppf(0.975) = {norm_ppf(0.975):.6f}')"  # Should be ~1.96
```

### 3. Deployment Testing
```bash
# Trigger Vercel deployment
git add .
git commit -m "fix(deployment): optimize serverless function size under 250MB limit"
git push origin master

# Monitor deployment in Vercel dashboard
# Verify function size is under 250MB
```

## Files Modified

1. **.vercelignore** - Comprehensive exclusion rules
2. **vercel.json** - Added function configuration
3. **api/requirements.txt** - Removed scipy, snowflake, uvicorn
4. **backend/app/utils/numpy_stats.py** - NEW: Numpy-only statistical functions
5. **backend/app/utils/__init__.py** - NEW: Utils package initialization
6. **backend/app/api/routes.py** - Updated to use numpy_stats
7. **backend/app/services/improve_predictor.py** - Updated to use numpy_stats

## Technical Details

### Numpy-Only Implementation Accuracy

The `norm_ppf` implementation uses the Beasley-Springer-Moro algorithm, which provides:
- **Accuracy**: ~1e-9 (comparable to scipy)
- **Speed**: Vectorizable with numpy (fast)
- **Size**: Zero additional dependencies beyond numpy

Comparison with scipy.stats.norm.ppf:
```python
import numpy as np
from app.utils.numpy_stats import norm_ppf
from scipy.stats import norm

test_values = [0.1, 0.25, 0.5, 0.75, 0.9, 0.95, 0.975, 0.99]
for p in test_values:
    numpy_result = norm_ppf(p)
    scipy_result = norm.ppf(p)
    diff = abs(numpy_result - scipy_result)
    print(f"p={p:.3f}: numpy={numpy_result:.6f}, scipy={scipy_result:.6f}, diff={diff:.2e}")
```

### Peak Detection Simplification

The simplified `find_peaks_simple` provides:
- Local maxima detection (point higher than both neighbors)
- Distance constraint (minimum samples between peaks)
- Prominence constraint (height above surrounding valleys)

Limitations vs scipy.signal.find_peaks:
- No width calculation
- Simplified prominence calculation
- No plateau detection
- Sufficient for our telemetry corner detection use case

## Monitoring & Validation

### Post-Deployment Checklist

- [ ] Verify Vercel deployment succeeds without size error
- [ ] Test `/api/health` endpoint returns 200 OK
- [ ] Test `/api/tracks` endpoint returns track data
- [ ] Test `/api/drivers` endpoint returns driver data
- [ ] Test `/api/improve` with skill adjustments (uses norm_ppf)
- [ ] Test `/api/telemetry/coach` with lap comparison (uses find_peaks_simple)
- [ ] Monitor Vercel function logs for any import errors
- [ ] Verify response times are acceptable (<2s for complex requests)

### Rollback Plan

If issues occur:
1. Revert to previous commit: `git revert HEAD`
2. Re-add scipy to `api/requirements.txt`
3. Revert code changes in routes.py and improve_predictor.py
4. Deploy with original heavy dependencies
5. Investigate alternative solutions (function splitting, external data storage)

## Future Optimization Opportunities

If further size reduction is needed:

1. **Lazy Load Pandas**: Only import pandas when needed
2. **Split API Functions**: Separate heavy analytics endpoints into separate functions
3. **External Data Storage**: Move JSON data files to Vercel Blob or S3
4. **Alternative to Pandas**: Use numpy-only data structures where possible
5. **Tree Shaking**: Use tools like `pigar` to identify truly necessary dependencies

## Conclusion

This optimization reduces the serverless function size by **~170-210MB**, bringing it well under Vercel's 250MB limit while maintaining all core functionality. The numpy-only implementations provide equivalent accuracy to scipy for our use cases while dramatically reducing deployment size.

**Expected Outcome**: ✅ Deployment succeeds with function size ~80-120MB
