# Vercel Deployment - Priority Fixes

**Status:** BLOCKING DEPLOYMENT
**Total Fixes:** 3 Critical, 2 Recommended
**Estimated Time:** 30-45 minutes

---

## 🚨 CRITICAL FIX #1: Add Missing BaseModel Import

**Priority:** HIGHEST - Will cause immediate 500 errors
**File:** `/backend/app/api/routes.py`
**Line:** 5 (after existing imports)

### Current Code (Lines 1-11):
```python
"""
API routes for Racing Analytics platform.
"""

from fastapi import APIRouter, HTTPException, Query
from typing import List, Optional, Dict
import pandas as pd
import logging

logger = logging.getLogger(__name__)
from models import (
```

### Fix Required:
```python
"""
API routes for Racing Analytics platform.
"""

from fastapi import APIRouter, HTTPException, Query
from typing import List, Optional, Dict
from pydantic import BaseModel, Field  # ✅ ADD THIS LINE
import pandas as pd
import logging

logger = logging.getLogger(__name__)
from models import (
```

**Why This Fails:**
- Line 145 defines `class PredictRequest(BaseModel)`
- BaseModel is never imported
- Python will raise `NameError: name 'BaseModel' is not defined`
- This crashes the entire API on startup

**Testing:**
```bash
cd backend
python -c "from app.api.routes import router; print('Success')"
```

---

## 🚨 CRITICAL FIX #2: Create API Requirements File

**Priority:** HIGHEST - Vercel won't install Python dependencies
**File:** `/api/requirements.txt` (CREATE NEW FILE)

### Create File:
```txt
# FastAPI and ASGI server
fastapi==0.115.6
uvicorn==0.34.0
mangum==0.17.0

# Data validation and settings
pydantic==2.10.6
python-dotenv==1.0.1

# AI and external services
anthropic==0.47.0
httpx==0.28.1

# Data processing
pandas==2.2.3
numpy==1.26.4
scipy==1.11.4

# Database and storage
snowflake-connector-python==3.6.0
cryptography==41.0.7

# HTTP requests
requests==2.32.3
python-multipart==0.0.20
```

**Why This Fails:**
- Vercel looks for dependencies in the same directory as the function
- Current `/backend/requirements.txt` is not accessible to `/api/index.py`
- Without dependencies, all imports fail

**Testing:**
```bash
# Verify file exists
ls -la api/requirements.txt

# Verify content
cat api/requirements.txt
```

---

## 🚨 CRITICAL FIX #3: Configure Vercel Environment Variables

**Priority:** HIGHEST - API features won't work
**Method:** Vercel Dashboard or CLI

### Required Variables:

```bash
# 1. Anthropic AI (REQUIRED for coaching features)
ANTHROPIC_API_KEY=sk-ant-api03-xxxxx

# 2. Snowflake Connection (PRIMARY data source)
SNOWFLAKE_ACCOUNT=EOEPNYL-PR46214
SNOWFLAKE_USER=hackthetrack_svc
SNOWFLAKE_WAREHOUSE=COMPUTE_WH
SNOWFLAKE_DATABASE=HACKTHETRACK
SNOWFLAKE_SCHEMA=TELEMETRY
SNOWFLAKE_ROLE=ACCOUNTADMIN
USE_SNOWFLAKE=true

# 3. Snowflake Private Key (BASE64 ENCODED)
# First, encode the key:
# base64 -i rsa_key.p8 | tr -d '\n'
SNOWFLAKE_PRIVATE_KEY=<paste-base64-output-here>

# 4. Frontend URL (for CORS)
FRONTEND_URL=https://your-app.vercel.app

# 5. Environment marker
ENVIRONMENT=production
```

### Step-by-Step Setup:

#### Option A: Vercel Dashboard (Recommended)
1. Go to https://vercel.com/dashboard
2. Select your project
3. Go to Settings → Environment Variables
4. Add each variable above
5. Set scope to "Production, Preview, Development"

#### Option B: Vercel CLI
```bash
# Install Vercel CLI if not already installed
npm i -g vercel

# Add each variable (interactive prompts)
vercel env add ANTHROPIC_API_KEY
# Paste your API key when prompted
# Select: Production, Preview, Development

vercel env add SNOWFLAKE_ACCOUNT
# Enter: EOEPNYL-PR46214

vercel env add SNOWFLAKE_USER
# Enter: hackthetrack_svc

# ... repeat for all variables
```

#### Encoding Private Key:
```bash
# On macOS/Linux
cd /Users/justingrosz/Documents/AI-Work/hackthetrack-master
base64 -i rsa_key.p8 | tr -d '\n' > rsa_key_base64.txt
cat rsa_key_base64.txt

# On Windows PowerShell
[Convert]::ToBase64String([IO.File]::ReadAllBytes("rsa_key.p8"))

# Copy the output and paste into SNOWFLAKE_PRIVATE_KEY variable
```

**Why This Fails:**
- Anthropic API calls return 401 without valid key
- Snowflake connections fail without credentials
- Features that depend on external services won't work

**Testing:**
```bash
# After setting variables, verify in Vercel
vercel env ls
```

---

## ⚠️ RECOMMENDED FIX #1: Update Vercel Configuration

**Priority:** MEDIUM - Improves reliability
**File:** `/vercel.json`

### Current Configuration:
```json
{
  "buildCommand": "cd frontend && npm ci && npm run build",
  "outputDirectory": "frontend/dist",
  "installCommand": "cd frontend && npm ci",
  "framework": null,
  "rewrites": [
    {
      "source": "/api/:path*",
      "destination": "/api/index"
    },
    {
      "source": "/(.*)",
      "destination": "/index.html"
    }
  ]
}
```

### Recommended Configuration:
```json
{
  "version": 2,
  "buildCommand": "cd frontend && npm ci && npm run build",
  "outputDirectory": "frontend/dist",
  "installCommand": "cd frontend && npm ci",
  "framework": null,
  "functions": {
    "api/**/*.py": {
      "runtime": "python3.9",
      "memory": 1024,
      "maxDuration": 30
    }
  },
  "rewrites": [
    {
      "source": "/api/:path*",
      "destination": "/api/index"
    },
    {
      "source": "/(.*)",
      "destination": "/index.html"
    }
  ],
  "env": {
    "PYTHONPATH": "./backend"
  }
}
```

**Changes:**
1. Added `"version": 2` for latest Vercel config format
2. Added `functions` block to specify Python runtime
3. Added `PYTHONPATH` environment variable for imports
4. Specified memory (1024 MB) and timeout (30 seconds)

**Benefits:**
- Explicit runtime configuration
- Better cold start performance
- Proper Python path resolution

---

## ⚠️ RECOMMENDED FIX #2: Improve API Handler

**Priority:** MEDIUM - Better error handling
**File:** `/api/index.py`

### Current Code:
```python
"""
Vercel serverless function wrapper for FastAPI application.
This file adapts the FastAPI app to work with Vercel's serverless platform.
"""

import sys
from pathlib import Path

# Add parent directory to path so we can import from backend
backend_path = Path(__file__).parent.parent
sys.path.insert(0, str(backend_path))

# Import the main FastAPI app
from main import app

# Import Mangum after app to avoid circular imports
from mangum import Mangum

# Wrap the FastAPI app with Mangum for AWS Lambda/Vercel compatibility
handler = Mangum(app, lifespan="off")

# Vercel requires this export
def handler_wrapper(event, context):
    """Wrapper function for Vercel serverless deployment."""
    return handler(event, context)
```

### Recommended Code:
```python
"""
Vercel serverless function entry point for FastAPI backend.
"""
import sys
import os
from pathlib import Path

# Configure paths for serverless environment
backend_dir = Path(__file__).resolve().parent.parent / "backend"
sys.path.insert(0, str(backend_dir))

# Set environment markers
os.environ.setdefault("ENVIRONMENT", "production")
os.environ.setdefault("PYTHONUNBUFFERED", "1")

# Import FastAPI app
from main import app

# Import Mangum for ASGI->Lambda adapter
from mangum import Mangum

# Create serverless handler
handler = Mangum(app, lifespan="off", api_gateway_base_path="/api")

# Vercel entry point
def handler_wrapper(event, context):
    """Entry point for Vercel Python runtime."""
    try:
        return handler(event, context)
    except Exception as e:
        # Log error and return 500
        print(f"Handler error: {e}")
        return {
            "statusCode": 500,
            "body": {"error": "Internal server error"},
            "headers": {"Content-Type": "application/json"}
        }
```

**Improvements:**
1. Better path resolution with `.resolve()`
2. Environment variable configuration
3. Explicit base path for Mangum
4. Error handling wrapper
5. Proper logging for debugging

---

## Pre-Deployment Testing Checklist

### 1. Local Backend Test
```bash
cd /Users/justingrosz/Documents/AI-Work/hackthetrack-master/backend

# Activate virtual environment
source venv/bin/activate  # or venv\Scripts\activate on Windows

# Test imports
python -c "from app.api.routes import router; print('✅ Routes import successful')"

# Test API startup
python -c "from main import app; print('✅ App import successful')"

# Run server
python main.py
# Should see: INFO:     Uvicorn running on http://0.0.0.0:8000
```

### 2. Local Frontend Test
```bash
cd /Users/justingrosz/Documents/AI-Work/hackthetrack-master/frontend

# Clean install
rm -rf node_modules package-lock.json
npm install

# Test build
npm run build
# Should complete without errors

# Test dev server
npm run dev
# Should run on http://localhost:5173
```

### 3. Integration Test
```bash
# With both backend and frontend running:

# Test API health
curl http://localhost:8000/api/health

# Expected response:
# {
#   "status": "healthy",
#   "tracks_loaded": 18,
#   "drivers_loaded": 42,
#   ...
# }

# Test frontend API calls
# Open http://localhost:5173
# Check browser console for errors
# Navigate to different pages
```

### 4. Environment Variables Test
```bash
# Check .env file exists
ls -la backend/.env

# Verify required variables
cat backend/.env | grep -E "(ANTHROPIC|SNOWFLAKE)"

# Test Snowflake connection
cd backend
python -c "
from app.services.snowflake_service import SnowflakeService
sf = SnowflakeService()
print('✅ Snowflake connection successful' if sf.test_connection() else '❌ Connection failed')
"
```

---

## Deployment Steps

### Step 1: Apply Critical Fixes
```bash
cd /Users/justingrosz/Documents/AI-Work/hackthetrack-master

# Fix #1: Add BaseModel import
# Edit backend/app/api/routes.py
# Add: from pydantic import BaseModel, Field
# After line 5

# Fix #2: Create API requirements
cat backend/requirements.txt > api/requirements.txt

# Verify file created
ls -la api/requirements.txt
```

### Step 2: Configure Vercel
```bash
# Install Vercel CLI (if not installed)
npm i -g vercel

# Login
vercel login

# Link project (first time only)
vercel link

# Add environment variables
vercel env add ANTHROPIC_API_KEY
# ... add all variables from CRITICAL FIX #3
```

### Step 3: Test Deploy to Preview
```bash
# Deploy to preview environment
vercel

# Wait for deployment
# Vercel will provide a preview URL

# Test the preview deployment
curl https://your-preview-url.vercel.app/api/health

# Check frontend
open https://your-preview-url.vercel.app
```

### Step 4: Deploy to Production
```bash
# If preview works correctly
vercel --prod

# Monitor logs
vercel logs --follow
```

---

## Verification Checklist

After deployment, verify:

- [ ] Frontend loads without errors
- [ ] `/api/health` returns 200 status
- [ ] Driver list loads on Scout Landing page
- [ ] Navigation between pages works
- [ ] Telemetry data displays
- [ ] AI coaching responds (if ANTHROPIC_API_KEY is set)
- [ ] No CORS errors in browser console
- [ ] No 500 errors in Vercel logs

---

## Troubleshooting

### If Frontend Doesn't Load
1. Check Vercel build logs: `vercel logs --build`
2. Verify `frontend/dist` directory exists
3. Check `vercel.json` outputDirectory setting

### If API Returns 500
1. Check function logs: `vercel logs --function=/api/index`
2. Verify environment variables: `vercel env ls`
3. Check for import errors in backend code
4. Verify `api/requirements.txt` exists

### If Imports Fail
1. Verify PYTHONPATH in vercel.json
2. Check sys.path in `/api/index.py`
3. Verify relative import paths in backend code

### If Snowflake Connection Fails
1. Verify SNOWFLAKE_PRIVATE_KEY is base64 encoded
2. Check all Snowflake environment variables are set
3. Test connection locally first
4. Check if USE_SNOWFLAKE=true is set

---

## Rollback Procedure

If deployment fails critically:

```bash
# Immediate rollback to previous version
vercel rollback

# Or rollback to specific deployment
vercel rollback <deployment-url>

# Check current deployments
vercel ls
```

---

## Post-Deployment Monitoring

### First 24 Hours
1. Monitor error rate in Vercel dashboard
2. Check function execution time
3. Verify data source health
4. Watch for CORS errors

### Setup Alerts
```bash
# Configure Vercel monitoring
vercel env add SENTRY_DSN  # Optional: for error tracking
```

---

## Summary

**Total Time Required:** 30-45 minutes

**Critical Fixes (MUST DO):**
1. Add BaseModel import (2 minutes)
2. Create api/requirements.txt (2 minutes)
3. Configure environment variables (15-20 minutes)

**Recommended Fixes (SHOULD DO):**
1. Update vercel.json (5 minutes)
2. Improve API handler (5 minutes)

**Testing:**
1. Local testing (10 minutes)
2. Preview deployment (5 minutes)

**Once these fixes are applied, deployment should succeed.**

---

**Last Updated:** 2025-11-06
**Next Steps:** Apply Critical Fixes → Test → Deploy
