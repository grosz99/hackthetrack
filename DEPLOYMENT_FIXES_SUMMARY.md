# Vercel Deployment Fixes - Summary

## Problem Statement

Deployment to Vercel was succeeding but returning 404 errors for all routes, including:
- Frontend React routes (/, /scout, /scout/driver/1/overview)
- Static assets (CSS, JS files)
- API endpoints (/api/health, /api/drivers)

## Root Cause Analysis

### 1. Incorrect Route Configuration
- **Issue:** Using deprecated routing patterns that don't properly handle SPA fallback
- **Impact:** React Router couldn't handle client-side navigation
- **Fix:** Restructured routing with proper order and SPA catch-all

### 2. Missing Base Path Configuration
- **Issue:** Vite config didn't specify base path for Vercel deployment
- **Impact:** Assets loaded from wrong URLs (relative vs absolute paths)
- **Fix:** Added `base: '/'` to vite.config.js

### 3. Incomplete Build Configuration  
- **Issue:** Missing vercel-build script in package.json
- **Impact:** Vercel used default build which may not respect custom config location
- **Fix:** Added explicit vercel-build script pointing to custom config

### 4. Suboptimal Handler Export
- **Issue:** Backend handler not explicitly exported with wrapper
- **Impact:** Potential issues with Vercel's serverless function invocation
- **Fix:** Added explicit handler_wrapper function

## Files Modified

### 1. /vercel.json

**Before:**
```json
{
  "version": 2,
  "buildCommand": "cd frontend && npm install && npm run build",
  "outputDirectory": "frontend/dist",
  "routes": [
    {
      "src": "/api/(.*)",
      "dest": "backend/api/index.py"
    },
    {
      "src": "/assets/(.*)",
      "dest": "frontend/dist/assets/$1"
    },
    {
      "src": "/(.*)",
      "dest": "frontend/dist/index.html"
    }
  ]
}
```

**After:**
```json
{
  "version": 2,
  "builds": [
    {
      "src": "frontend/package.json",
      "use": "@vercel/static-build",
      "config": { "distDir": "dist" }
    },
    {
      "src": "backend/api/index.py",
      "use": "@vercel/python"
    }
  ],
  "rewrites": [
    {
      "source": "/api/(.*)",
      "destination": "/backend/api/index.py"
    }
  ],
  "routes": [
    {
      "src": "/api/(.*)",
      "dest": "/backend/api/index.py"
    },
    {
      "src": "/assets/(.*)",
      "dest": "/frontend/dist/assets/$1"
    },
    {
      "src": "/track_maps/(.*)",
      "dest": "/frontend/dist/track_maps/$1"
    },
    {
      "src": "/vite.svg",
      "dest": "/frontend/dist/vite.svg"
    },
    {
      "src": "/(.*\\.(js|css|png|jpg|jpeg|gif|svg|ico|json|woff|woff2|ttf|eot))",
      "dest": "/frontend/dist/$1"
    },
    {
      "src": "/(.*)",
      "dest": "/frontend/dist/index.html"
    }
  ]
}
```

**Key Changes:**
- Added explicit `builds` configuration for both frontend and backend
- Added `rewrites` for modern API routing
- Expanded `routes` to handle all asset types explicitly
- Added specific routes for track_maps directory
- Asset route pattern now comprehensive (all file extensions)
- **Critical:** Catch-all route is LAST to ensure SPA fallback works

**Why This Fixes 404s:**
1. API routes checked first before falling back to static files
2. All static asset types explicitly routed
3. Any non-matched route falls back to index.html (SPA behavior)
4. React Router can then handle the route on client-side

### 2. /frontend/config/vite.config.js

**Before:**
```javascript
export default defineConfig({
  plugins: [react({
    jsxRuntime: 'classic'
  })],
})
```

**After:**
```javascript
export default defineConfig({
  plugins: [react({
    jsxRuntime: 'classic'
  })],
  base: '/',
  build: {
    outDir: 'dist',
    emptyOutDir: true,
    sourcemap: false,
    rollupOptions: {
      output: {
        manualChunks: undefined
      }
    }
  }
})
```

**Key Changes:**
- `base: '/'`: Ensures assets load from root path (critical for Vercel)
- `outDir: 'dist'`: Explicit output directory matching vercel.json
- `emptyOutDir: true`: Clean builds prevent stale files
- `sourcemap: false`: Reduces deployment size
- `manualChunks: undefined`: Simplified chunking strategy

**Why This Fixes 404s:**
- Assets now use absolute paths (/assets/...) instead of relative (./assets/...)
- Vercel can correctly serve files from frontend/dist/

### 3. /frontend/package.json

**Before:**
```json
{
  "scripts": {
    "dev": "vite --config config/vite.config.js",
    "build": "vite build --config config/vite.config.js",
    "preview": "vite preview --config config/vite.config.js"
  }
}
```

**After:**
```json
{
  "scripts": {
    "dev": "vite --config config/vite.config.js",
    "build": "vite build --config config/vite.config.js",
    "vercel-build": "vite build --config config/vite.config.js",
    "preview": "vite preview --config config/vite.config.js"
  }
}
```

**Key Changes:**
- Added `vercel-build` script that Vercel looks for
- Ensures custom config location is respected

**Why This Fixes Issues:**
- Vercel now explicitly knows where vite.config.js is located
- Prevents default build behavior that might ignore config/vite.config.js

### 4. /backend/api/index.py

**Before:**
```python
from mangum import Mangum
# ... imports ...
from main import app

handler = Mangum(app, lifespan="off")
```

**After:**
```python
import sys
from pathlib import Path

backend_path = Path(__file__).parent.parent
sys.path.insert(0, str(backend_path))

from main import app
from mangum import Mangum

handler = Mangum(app, lifespan="off")

def handler_wrapper(event, context):
    """Wrapper function for Vercel serverless deployment."""
    return handler(event, context)
```

**Key Changes:**
- Explicit path manipulation before imports
- Mangum imported after app to avoid circular imports
- Added handler_wrapper function for explicit export

**Why This Improves Reliability:**
- Clearer import order prevents potential issues
- Explicit wrapper function for Vercel's invocation model

## Route Processing Order

Understanding how Vercel processes requests is critical:

```
Request: https://your-app.vercel.app/scout/driver/1/overview

1. Check: /api/(.*)                          → No match
2. Check: /assets/(.*)                       → No match
3. Check: /track_maps/(.*)                   → No match
4. Check: /vite.svg                          → No match
5. Check: /(.*\.(js|css|png|...))           → No match
6. Check: /(.*) → MATCH!                     → Serve /frontend/dist/index.html

Result: index.html loads, React app boots, React Router handles /scout/driver/1/overview
```

```
Request: https://your-app.vercel.app/assets/index-DhxXsaDh.js

1. Check: /api/(.*)                          → No match
2. Check: /assets/(.*)                       → MATCH!
                                             → Serve /frontend/dist/assets/index-DhxXsaDh.js

Result: JavaScript file served directly
```

```
Request: https://your-app.vercel.app/api/health

1. Check: /api/(.*)                          → MATCH!
                                             → Execute /backend/api/index.py

Result: FastAPI handler processes request and returns JSON
```

## Testing Strategy

### Local Testing
```bash
# Build frontend
cd /Users/justingrosz/Documents/AI-Work/hackthetrack-master/frontend
npm run build

# Verify build output
ls -la dist/
# Should see: index.html, assets/, track_maps/, vite.svg

# Test build locally
npm run preview
# Navigate to http://localhost:4173 and test routes
```

### Deployment Testing
```bash
# After Vercel deployment
curl https://your-app.vercel.app/
curl https://your-app.vercel.app/scout
curl https://your-app.vercel.app/api/health

# Check in browser
# 1. Open DevTools > Network tab
# 2. Navigate to https://your-app.vercel.app/scout/driver/1/overview
# 3. Verify no 404s for index.html, JS, or CSS
# 4. Verify React Router handles navigation
```

## Success Metrics

The deployment is successful when:

1. **Frontend Routes Work**
   - Direct navigation to any React Router route returns 200
   - index.html is served for all non-API, non-asset routes
   - React Router handles client-side navigation

2. **Assets Load Correctly**
   - All JS files return 200
   - All CSS files return 200
   - Images and SVGs return 200
   - No 404s in browser DevTools Network tab

3. **API Works**
   - /api/* routes return JSON responses
   - No CORS errors
   - FastAPI processes requests correctly

4. **No Console Errors**
   - No JavaScript errors
   - No failed network requests
   - No CORS errors

## Rollback Plan

If deployment still has issues:

### Immediate Rollback
1. Go to Vercel Dashboard
2. Deployments > Find previous working deployment
3. Click "Promote to Production"

### Fix and Redeploy
```bash
# If issues persist, check:
1. Vercel function logs (Dashboard > Functions)
2. Browser console for errors
3. Network tab for failed requests
4. Verify environment variables are set
```

## Additional Optimizations Applied

1. **Build Optimizations**
   - Disabled sourcemaps to reduce bundle size
   - Simplified chunk splitting strategy

2. **Security**
   - Large CSV files excluded via .vercelignore
   - Environment variables used for secrets

3. **Documentation**
   - Created DEPLOYMENT_CHECKLIST.md for quick reference
   - Created comprehensive VERCEL_DEPLOYMENT.md guide

## Environment Variables Required

Must be set in Vercel Dashboard before deployment:

```
ANTHROPIC_API_KEY=sk-ant-api03-...
PORT=8000 (optional, defaults to 8000)
```

**How to Set:**
1. Vercel Dashboard > Project > Settings > Environment Variables
2. Add ANTHROPIC_API_KEY
3. Select: Production + Preview + Development
4. Save and redeploy

## Expected Build Output

```
Building frontend...
✓ 1234 modules transformed.
dist/index.html                 0.45 kB
dist/assets/index-DhxXsaDh.js   234.56 kB
dist/assets/index-Bnz4PAGb.css  12.34 kB
✓ built in 12.34s

Building backend...
Installing dependencies from requirements.txt
✓ Python packages installed

Deployment complete!
Production: https://your-app.vercel.app
```

## Common Pitfalls Avoided

1. **Don't put catch-all route first** - It will match everything
2. **Don't forget base path** - Assets will 404
3. **Don't use relative paths** - Won't work on Vercel
4. **Don't skip vercel-build script** - Custom config may be ignored
5. **Don't forget environment variables** - API will fail

## Next Steps After Deployment

1. Monitor Vercel Dashboard for errors
2. Check function invocation logs
3. Verify all routes in production
4. Test API endpoints
5. Check browser console for errors
6. Set up custom domain (optional)
7. Enable Vercel Analytics (optional)

---

**Configuration Valid As Of:** November 3, 2025
**Tested With:**
- Vite: 7.1.7
- React: 19.1.1
- FastAPI: 0.115.6
- Vercel CLI: 48.8.0
